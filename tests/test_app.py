# -*- coding: utf-8 -*-
"""StudyTask 自动化测试（pytest）。

覆盖 SRS FR-01～FR-10 的核心路径与边界；测试数量 > 10。
运行：在 StudyTask 目录执行 `pytest -q`
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from models import Summary, Task, TaskView  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    application = create_app(str(tmp_path / "test.db"))
    application.config.update(TESTING=True, SECRET_KEY="test-secret")
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def get_dao(app):
    return app.extensions["task_dao"]


def new_task(client, **overrides):
    data = {
        "name": "数据结构作业",
        "course": "数据结构",
        "description": "链表实验报告",
        "due_date": (date.today() + timedelta(days=7)).isoformat(),
        "priority": "高",
        "status": "待完成",
    }
    data.update(overrides)
    return client.post("/tasks", data=data, follow_redirects=True)


# ---------- FR-01 创建与校验 ----------
def test_create_task_and_list(client, app):
    resp = new_task(client)
    assert resp.status_code == 200
    assert "数据结构作业" in resp.get_data(as_text=True)
    tasks = get_dao(app).list()
    assert len(tasks) == 1
    assert tasks[0].name == "数据结构作业"
    assert tasks[0].priority == "高"
    assert tasks[0].status == "待完成"


def test_create_rejects_empty_name(client, app):
    resp = new_task(client, name="   ")
    text = resp.get_data(as_text=True)
    assert "任务名称不能为空" in text
    assert get_dao(app).count_total() == 0


def test_create_rejects_invalid_due_date(client, app):
    resp = new_task(client, due_date="2026/01/01")
    text = resp.get_data(as_text=True)
    assert "截止日期格式应为 YYYY-MM-DD" in text
    assert get_dao(app).count_total() == 0


def test_create_rejects_overlong_course(client, app):
    resp = new_task(client, course="课" * 61)
    assert "所属课程不能为空" in resp.get_data(as_text=True)
    assert get_dao(app).count_total() == 0


# ---------- FR-02 列表与详情 ----------
def test_detail_and_404(client, app):
    new_task(client)
    task = get_dao(app).list()[0]
    resp = client.get(f"/tasks/{task.id}")
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "数据结构作业" in text
    assert "数据结构" in text

    missing = client.get("/tasks/99999")
    assert missing.status_code == 404
    assert "任务不存在" in missing.get_data(as_text=True)


# ---------- FR-03 修改 ----------
def test_update_task(client, app):
    new_task(client)
    task = get_dao(app).list()[0]
    resp = client.post(
        f"/tasks/{task.id}",
        data={
            "name": "更新后的任务",
            "course": "数据库原理",
            "description": "SQL 练习",
            "due_date": "2026-12-01",
            "priority": "中",
            "status": "进行中",
        },
        follow_redirects=True,
    )
    text = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "更新后的任务" in text
    updated = get_dao(app).get_by_id(task.id)
    assert updated.name == "更新后的任务"
    assert updated.course == "数据库原理"
    assert updated.status == "进行中"


def test_update_rejects_invalid_data(client, app):
    new_task(client)
    task = get_dao(app).list()[0]
    resp = client.post(
        f"/tasks/{task.id}",
        data={
            "name": "",
            "course": "数据结构",
            "description": "",
            "due_date": "2026-12-01",
            "priority": "中",
            "status": "待完成",
        },
        follow_redirects=True,
    )
    assert "任务名称不能为空" in resp.get_data(as_text=True)
    assert get_dao(app).get_by_id(task.id).name == "数据结构作业"


# ---------- FR-04 删除 ----------
def test_delete_confirm_and_delete(client, app):
    new_task(client)
    task = get_dao(app).list()[0]

    confirm = client.get(f"/tasks/{task.id}/delete")
    assert confirm.status_code == 200
    assert "确认删除" in confirm.get_data(as_text=True)

    resp = client.post(f"/tasks/{task.id}/delete", follow_redirects=True)
    assert resp.status_code == 200
    assert get_dao(app).count_total() == 0
    assert "暂无任务" in resp.get_data(as_text=True)


def test_delete_missing_task_404(client):
    assert client.get("/tasks/99999/delete").status_code == 404
    assert client.post("/tasks/99999/delete").status_code == 404


# ---------- FR-05 状态调整 ----------
def test_change_status_and_reject_invalid(client, app):
    new_task(client)
    task = get_dao(app).list()[0]

    client.post(f"/tasks/{task.id}/status", data={"status": "进行中"}, follow_redirects=True)
    assert get_dao(app).get_by_id(task.id).status == "进行中"

    client.post(f"/tasks/{task.id}/status", data={"status": "未知"}, follow_redirects=True)
    assert get_dao(app).get_by_id(task.id).status == "进行中"


# ---------- FR-06 组合筛选 ----------
def test_filter_combination(client, app):
    new_task(client, name="A-数据结构-待完成", course="数据结构", status="待完成", priority="高")
    new_task(client, name="B-数据库-进行中", course="数据库原理", status="进行中", priority="中")
    new_task(client, name="C-数据结构-已完成", course="数据结构", status="已完成", priority="高")

    resp = client.get("/?course=数据结构&status=待完成&priority=高")
    text = resp.get_data(as_text=True)
    assert "A-数据结构-待完成" in text
    assert "B-数据库-进行中" not in text
    assert "C-数据结构-已完成" not in text


# ---------- FR-07 逾期/即将到期 ----------
def test_task_view_boundaries():
    today = date.today()

    def view(due, status="待完成"):
        return TaskView.from_task(
            Task(name="t", course="c", due_date=due.isoformat(), status=status),
            today=today,
        )

    assert view(today - timedelta(days=1)).is_overdue is True
    assert view(today).is_due_soon is True
    assert view(today + timedelta(days=3)).is_due_soon is True
    assert view(today + timedelta(days=4)).is_due_soon is False
    completed = view(today - timedelta(days=5), status="已完成")
    assert completed.is_overdue is False and completed.is_due_soon is False


def test_index_shows_badges(client):
    today = date.today()
    new_task(client, name="逾期任务", due_date=(today - timedelta(days=1)).isoformat())
    new_task(client, name="今日到期", due_date=today.isoformat())
    text = client.get("/").get_data(as_text=True)
    assert "badge-overdue" in text
    assert "badge-soon" in text


# ---------- FR-08 统计 ----------
def test_summary_zero_and_rate(client, app):
    text = client.get("/").get_data(as_text=True)
    assert "0%" in text

    new_task(client, name="T1", status="已完成")
    new_task(client, name="T2", status="待完成")
    text = client.get("/").get_data(as_text=True)
    assert "50%" in text


def test_summary_from_counts():
    assert Summary.from_counts(0, 0).rate == 0
    assert Summary.from_counts(3, 1).rate == 33
    assert Summary.from_counts(3, 2).rate == 67
    assert Summary.from_counts(5, 0).rate == 0


# ---------- FR-09 持久化 ----------
def test_persistence_across_app_instances(tmp_path):
    db = str(tmp_path / "persist.db")
    app1 = create_app(db)
    app1.config.update(TESTING=True, SECRET_KEY="t")
    client1 = app1.test_client()
    new_task(client1, name="持久化任务")

    app2 = create_app(db)
    app2.config.update(TESTING=True, SECRET_KEY="t")
    text = app2.test_client().get("/").get_data(as_text=True)
    assert "持久化任务" in text


# ---------- NFR：200 条任务 ----------
def test_two_hundred_tasks(client, app):
    dao = get_dao(app)
    for i in range(200):
        dao.insert(
            Task(
                name=f"批量任务-{i:03d}",
                course="批量课程",
                description="",
                due_date="2026-12-31",
                priority="中",
                status="待完成",
            )
        )
    resp = client.get("/")
    assert resp.status_code == 200
    assert "批量任务-000" in resp.get_data(as_text=True)


# ---------- 错误处理 ----------
def test_edit_missing_task_404(client):
    assert client.get("/tasks/99999/edit").status_code == 404
    assert client.post("/tasks/99999", data={}).status_code == 404
