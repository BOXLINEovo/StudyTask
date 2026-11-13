-- StudyTask 数据库建表脚本（单表 task）
-- 依据：附录A SRS A.2 数据项；设计说明书 第3部分

CREATE TABLE IF NOT EXISTS task (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100),
    course      TEXT NOT NULL CHECK(length(course) BETWEEN 1 AND 60),
    description TEXT NOT NULL DEFAULT '' CHECK(length(description) <= 1000),
    due_date    TEXT NOT NULL,
    priority    TEXT NOT NULL DEFAULT '中' CHECK(priority IN ('高','中','低')),
    status      TEXT NOT NULL DEFAULT '待完成' CHECK(status IN ('待完成','进行中','已完成')),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_task_course   ON task(course);
CREATE INDEX IF NOT EXISTS idx_task_status   ON task(status);
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);
CREATE INDEX IF NOT EXISTS idx_task_due_date ON task(due_date);
