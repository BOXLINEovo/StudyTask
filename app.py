# -*- coding: utf-8 -*-
"""StudyTask 个人学习任务管理系统（Flask + SQLite）。

对应设计说明书：
- 第2部分 总体设计（ECB 分层）
- 第4部分 典型功能设计（FR-01～FR-10）
- 第5部分 页面模块设计
- 第7部分 接口设计
"""
from __future__ import annotations

import os
import sqlite3
from datetime import date
from typing import Dict, List, Optional, Tuple

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from dao import TaskDAO, init_db
from models import PRIORITIES, STATUSES, Summary, Task, TaskView, now_iso

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(BASE_DIR, "studytask.db")


class TaskController:
    """创建/修改/删除/状态调整（FR-01/03/04/05）。"""

    def __init__(self, dao: TaskDAO):
        self.dao = dao

    def _from_form(self, form) -> Task:
        return Task(
            name=(form.get("name") or "").strip(),
            course=(form.get("course") or "").strip(),
            description=form.get("description") or "",
            due_date=(form.get("due_date") or "").strip(),
            priority=(form.get("priority") or "中").strip(),
            status=(form.get("status") or "待完成").strip(),
        )

    def create(self, form) -> Tuple[bool, List[str], Optional[int]]:
        task = self._from_form(form)
        errors = task.validate()
        if errors:
            return False, errors, None
        task.created_at = now_iso()
        task.updated_at = task.created_at
        task_id = self.dao.insert(task)
        return True, [], task_id

    def update(self, task_id: int, form) -> Tuple[Optional[bool], List[str]]:
        task = self.dao.get_by_id(task_id)
        if task is None:
            return None, ["任务不存在"]
        task.name = (form.get("name") or "").strip()
        task.course = (form.get("course") or "").strip()
        task.description = form.get("description") or ""
        task.due_date = (form.get("due_date") or "").strip()
        task.priority = (form.get("priority") or "中").strip()
        task.status = (form.get("status") or "待完成").strip()
        errors = task.validate()
        if errors:
            return False, errors
        ok = self.dao.update(task)
        return ok, [] if ok else ["任务不存在"]

    def delete(self, task_id: int) -> bool:
        return self.dao.delete(task_id)

    def change_status(self, task_id: int, status: str) -> bool:
        status = (status or "").strip()
        if status not in STATUSES:
            return False
        return self.dao.update_status(task_id, status)


class QueryController:
    """列表/筛选/详情（FR-02/06/07）。"""

    def __init__(self, dao: TaskDAO):
        self.dao = dao

    def list(self, filters: Optional[Dict[str, str]] = None) -> List[TaskView]:
        today = date.today()
        return [TaskView.from_task(t, today) for t in self.dao.list(filters)]

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.dao.get_by_id(task_id)

    def get_detail(self, task_id: int) -> Optional[TaskView]:
        task = self.dao.get_by_id(task_id)
        return TaskView.from_task(task) if task else None


class StatsController:
    """首页统计（FR-08）。"""

    def __init__(self, dao: TaskDAO):
        self.dao = dao

    def summary(self) -> Summary:
        return Summary.from_counts(self.dao.count_total(), self.dao.count_completed())


def _task_values(task: Optional[Task] = None) -> Dict[str, str]:
    if task is None:
        return {
            "name": "",
            "course": "",
            "description": "",
            "due_date": "",
            "priority": "中",
            "status": "待完成",
        }
    return {
        "name": task.name,
        "course": task.course,
        "description": task.description,
        "due_date": task.due_date,
        "priority": task.priority,
        "status": task.status,
    }


def create_app(db_path: Optional[str] = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("STUDYTASK_SECRET_KEY", "studytask-local-secret")
    app.config["DB_PATH"] = db_path or os.environ.get("STUDYTASK_DB") or DEFAULT_DB

    init_db(app.config["DB_PATH"])
    dao = TaskDAO(app.config["DB_PATH"])
    app.extensions["task_dao"] = dao

    task_controller = TaskController(dao)
    query_controller = QueryController(dao)
    stats_controller = StatsController(dao)

    def render_form(mode: str, task: Optional[Task], values, errors):
        return render_template(
            "task_form.html",
            mode=mode,
            task=task,
            values=values,
            errors=errors,
            priorities=PRIORITIES,
            statuses=STATUSES,
        )

    @app.get("/")
    def index():
        filters = {
            key: (request.args.get(key) or "").strip()
            for key in ("course", "status", "priority")
        }
        tasks = query_controller.list(filters)
        summary = stats_controller.summary()
        courses = dao.distinct_courses()
        return render_template(
            "index.html",
            tasks=tasks,
            summary=summary,
            filters=filters,
            courses=courses,
            priorities=PRIORITIES,
            statuses=STATUSES,
        )

    @app.get("/tasks/new")
    def new_task():
        return render_form("create", None, _task_values(), [])

    @app.post("/tasks")
    def create_task():
        ok, errors, _ = task_controller.create(request.form)
        if not ok:
            return render_form("create", None, request.form, errors)
        flash("任务已创建", "success")
        return redirect(url_for("index"))

    @app.get("/tasks/<int:task_id>")
    def task_detail(task_id: int):
        view = query_controller.get_detail(task_id)
        if view is None:
            abort(404)
        return render_template("task_detail.html", item=view, statuses=STATUSES)

    @app.get("/tasks/<int:task_id>/edit")
    def edit_task(task_id: int):
        task = query_controller.get_task(task_id)
        if task is None:
            abort(404)
        return render_form("edit", task, _task_values(task), [])

    @app.post("/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = query_controller.get_task(task_id)
        if task is None:
            abort(404)
        ok, errors = task_controller.update(task_id, request.form)
        if ok is None:
            abort(404)
        if not ok:
            return render_form("edit", task, request.form, errors)
        flash("任务已更新", "success")
        return redirect(url_for("task_detail", task_id=task_id))

    @app.post("/tasks/<int:task_id>/status")
    def change_status(task_id: int):
        task = query_controller.get_task(task_id)
        if task is None:
            abort(404)
        status = (request.form.get("status") or "").strip()
        if not task_controller.change_status(task_id, status):
            flash("状态不合法", "error")
        else:
            flash("状态已更新", "success")
        if request.form.get("next") == "detail":
            return redirect(url_for("task_detail", task_id=task_id))
        return redirect(url_for("index"))

    @app.get("/tasks/<int:task_id>/delete")
    def delete_confirm(task_id: int):
        task = query_controller.get_task(task_id)
        if task is None:
            abort(404)
        return render_template("delete_confirm.html", task=task)

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id: int):
        task = query_controller.get_task(task_id)
        if task is None:
            abort(404)
        if task_controller.delete(task_id):
            flash("任务已删除", "success")
        else:
            flash("任务不存在", "error")
        return redirect(url_for("index"))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("500.html"), 500

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception("数据库异常: %s", error)
        return render_template("500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
