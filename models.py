# -*- coding: utf-8 -*-
"""领域模型：任务、任务视图、统计结果与校验规则。

对应设计说明书：第3部分（数据）、第4部分（业务规则）、第7部分（内部接口）。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Optional

PRIORITIES = ("高", "中", "低")
STATUSES = ("待完成", "进行中", "已完成")
DATE_FORMAT = "%Y-%m-%d"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def now_iso() -> str:
    """当前本地时间，ISO 8601（秒精度）。"""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


@dataclass
class Task:
    id: Optional[int] = None
    name: str = ""
    course: str = ""
    description: str = ""
    due_date: str = ""
    priority: str = "中"
    status: str = "待完成"
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row) -> "Task":
        return cls(
            id=row["id"],
            name=row["name"] or "",
            course=row["course"] or "",
            description=row["description"] or "",
            due_date=row["due_date"] or "",
            priority=row["priority"] or "中",
            status=row["status"] or "待完成",
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
        )

    def validate(self) -> List[str]:
        """返回中文错误列表；空列表表示校验通过。"""
        errors: List[str] = []
        name = (self.name or "").strip()
        course = (self.course or "").strip()
        description = self.description or ""

        if not name or len(name) > 100:
            errors.append("任务名称不能为空，且不超过 100 字")
        if not course or len(course) > 60:
            errors.append("所属课程不能为空，且不超过 60 字")
        if len(description) > 1000:
            errors.append("任务描述不能超过 1000 字")

        due = (self.due_date or "").strip()
        if not due:
            errors.append("请填写截止日期")
        elif not DATE_RE.fullmatch(due):
            errors.append("截止日期格式应为 YYYY-MM-DD")
        else:
            try:
                datetime.strptime(due, DATE_FORMAT)
            except ValueError:
                errors.append("截止日期格式应为 YYYY-MM-DD")

        if (self.priority or "") not in PRIORITIES:
            errors.append("优先级必须为高/中/低")
        if (self.status or "") not in STATUSES:
            errors.append("状态不合法")
        return errors


@dataclass
class TaskView:
    """任务 + 逾期/即将到期派生标记（值对象）。"""

    task: Task
    is_overdue: bool = False
    is_due_soon: bool = False

    @classmethod
    def from_task(cls, task: Task, today: Optional[date] = None) -> "TaskView":
        today = today or date.today()
        overdue = False
        soon = False
        if task.status != "已完成":
            try:
                due = datetime.strptime(task.due_date, DATE_FORMAT).date()
            except (ValueError, TypeError):
                return cls(task, False, False)
            if due < today:
                overdue = True
            elif today <= due <= today + timedelta(days=3):
                soon = True
        return cls(task, overdue, soon)


@dataclass
class Summary:
    total: int
    completed: int
    rate: int

    @classmethod
    def from_counts(cls, total: int, completed: int) -> "Summary":
        total = max(0, int(total))
        completed = max(0, min(int(completed), total))
        rate = 0 if total == 0 else int(completed * 100 / total + 0.5)
        return cls(total=total, completed=completed, rate=rate)
