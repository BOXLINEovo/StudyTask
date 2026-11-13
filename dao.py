# -*- coding: utf-8 -*-
"""数据访问层：TaskDAO（sqlite3，参数化 SQL）。

对应设计说明书：第3部分（数据库）、第6部分（DAO 设计）。
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, Iterable, List, Optional

from models import Task, now_iso

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """执行 schema.sql 建表（幂等）。"""
    parent = os.path.dirname(os.path.abspath(db_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = _connect(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
            conn.executescript(fh.read())
        conn.commit()
    finally:
        conn.close()


class TaskDAO:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def _conn(self):
        conn = _connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ---------- 写 ----------
    def insert(self, task: Task) -> int:
        ts = task.created_at or now_iso()
        task.created_at = ts
        task.updated_at = task.updated_at or ts
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO task(name, course, description, due_date,
                                    priority, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task.name, task.course, task.description, task.due_date,
                 task.priority, task.status, task.created_at, task.updated_at),
            )
            return int(cur.lastrowid or 0)

    def update(self, task: Task) -> bool:
        task.updated_at = now_iso()
        with self._conn() as conn:
            cur = conn.execute(
                """UPDATE task
                      SET name=?, course=?, description=?, due_date=?,
                          priority=?, status=?, updated_at=?
                    WHERE id=?""",
                (task.name, task.course, task.description, task.due_date,
                 task.priority, task.status, task.updated_at, task.id),
            )
            return cur.rowcount > 0

    def delete(self, task_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM task WHERE id=?", (task_id,))
            return cur.rowcount > 0

    def update_status(self, task_id: int, status: str) -> bool:
        with self._conn() as conn:
            cur = conn.execute(
                "UPDATE task SET status=?, updated_at=? WHERE id=?",
                (status, now_iso(), task_id),
            )
            return cur.rowcount > 0

    # ---------- 读 ----------
    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM task WHERE id=?", (task_id,)).fetchone()
        return Task.from_row(row) if row else None

    def list(self, filters: Optional[Dict[str, str]] = None) -> List[Task]:
        filters = filters or {}
        sql = "SELECT * FROM task"
        where: List[str] = []
        params: List[str] = []

        course = (filters.get("course") or "").strip()
        status = (filters.get("status") or "").strip()
        priority = (filters.get("priority") or "").strip()
        if course:
            where.append("course = ?")
            params.append(course)
        if status:
            where.append("status = ?")
            params.append(status)
        if priority:
            where.append("priority = ?")
            params.append(priority)

        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY due_date ASC, id DESC"

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [Task.from_row(r) for r in rows]

    def count_total(self) -> int:
        with self._conn() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM task").fetchone()[0])

    def count_completed(self) -> int:
        with self._conn() as conn:
            return int(
                conn.execute("SELECT COUNT(*) FROM task WHERE status='已完成'").fetchone()[0]
            )

    def distinct_courses(self) -> List[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT DISTINCT course FROM task ORDER BY course"
            ).fetchall()
        return [r[0] for r in rows if r[0]]
