# StudyTask · 个人学习任务管理系统

基于《StudyTask 个人学习任务管理系统 SRS》（附录A）与《StudyTask 软件设计说明书》实现的单用户本地 Web 应用：**Python 3 + Flask + Jinja2 + SQLite**。

---

## 1. 功能

- 创建任务：名称、课程、描述、截止日期、优先级、状态，带服务端校验（FR-01）
- 任务列表与详情：列表展示名称/课程/截止日期/状态/优先级（FR-02）
- 修改任务：修改后列表与详情一致（FR-03）
- 删除任务：确认后从数据库删除（FR-04）
- 状态调整：待完成 / 进行中 / 已完成（FR-05）
- 组合筛选：课程 + 状态 + 优先级（AND）（FR-06）
- 逾期/即将到期标记：未完成且截止日 < 今天 → 逾期；今天 ≤ 截止日 ≤ 今天+3 → 即将到期；已完成不提醒（FR-07）
- 首页统计：任务总数、已完成数、完成率（四舍五入整数；0 任务显示 0%）（FR-08）
- 数据持久化：SQLite 文件，重启不丢失（FR-09）
- 中文界面与友好错误提示（FR-10）

## 2. 技术栈

| 项 | 选型 |
|----|------|
| 语言 | Python 3.10+ |
| Web 框架 | Flask 3.x |
| 模板 | Jinja2 |
| 数据库 | SQLite 3（文件 `studytask.db`） |
| 测试 | pytest |
| 前端 | 原生 HTML/CSS/JavaScript（自定义下拉面板与日期选择器） |

## 3. 目录结构

```text
StudyTask/
  app.py                 # Flask 应用、路由、控制器、错误处理
  models.py              # Task / TaskView / Summary / 校验
  dao.py                 # TaskDAO（sqlite3，参数化 SQL）
  schema.sql             # 建表脚本
  templates/             # 页面模板（base/index/form/detail/delete/404/500）
  static/
    style.css            # 页面样式
    app.js               # 自定义下拉面板、日期选择器、描述框自动增高
  tests/test_app.py      # 自动化测试（18 条）
  requirements.txt
  README.md
  AI_DEV_LOG.md          # AI 协作过程记录
  studytask.db           # 首次运行自动生成（已 gitignore）
```

## 4. 环境要求

- Windows 10/11、macOS 或 Linux
- Python **3.10 或更高版本**
- pip（随 Python 安装）
- 无需安装数据库服务，无需联网（依赖安装完成后）

检查 Python：

```powershell
python --version
# 或 Windows 上的：
py --version
```

应看到 `Python 3.10.x` 或更高版本。

---

## 5. 从零开始运行（Windows PowerShell）

> 以下命令均在 **`StudyTask` 项目根目录**执行（包含 `app.py` 的目录）。

### 第 1 步：进入项目目录

```powershell
cd C:\Users\18362\Desktop\软件工程\实验\StudyTask
```

### 第 2 步：创建虚拟环境

```powershell
python -m venv .venv
```

如果 `python` 不可用，可改用：

```powershell
py -3 -m venv .venv
```

### 第 3 步：激活虚拟环境

PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果提示“禁止运行脚本”，先执行（仅对当前窗口生效）：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

命令提示符（cmd）：

```bat
.venv\Scripts\activate.bat
```

激活成功后，命令行前面会出现 `(.venv)`。

### 第 4 步：安装依赖

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 第 5 步：启动应用

```powershell
python app.py
```

看到类似输出即启动成功：

```text
* Running on http://127.0.0.1:5000
```

### 第 6 步：浏览器访问

打开浏览器访问：

```text
http://127.0.0.1:5000
```

首次进入首页显示“暂无任务”，点击“新建任务”即可开始使用。

### 第 7 步：停止应用

在运行 `python app.py` 的终端按：

```text
Ctrl + C
```

下次运行只需重新进入项目目录、激活虚拟环境，再执行 `python app.py`。

---

## 6. macOS / Linux 运行步骤

```bash
cd /path/to/StudyTask
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

浏览器访问 `http://127.0.0.1:5000`，按 `Ctrl+C` 停止。

---

## 7. 数据库说明

- 首次启动自动执行 `schema.sql`，在项目根目录生成 `studytask.db`。
- 数据库为单表 `task`，字段与 SRS A.2 一致；无需安装 MySQL/SQL Server。
- 可通过环境变量指定数据库路径：

  ```powershell
  $env:STUDYTASK_DB = "D:\data\studytask.db"
  python app.py
  ```

- **重置数据前请先备份**：复制 `studytask.db` 到安全位置，再删除原文件；重新启动会生成空库。
- 修改/更新任务时使用 `UPDATE` 保留原记录；**不要用删除后重建、清空表或删除数据库文件的方式覆盖数据**。

## 8. 运行测试

```powershell
python -m pytest -q
```

预期结果：

```text
18 passed
```

测试覆盖：创建与校验、列表/详情、修改、删除确认、状态调整、组合筛选、逾期/即将到期边界、统计与 0 任务、重启持久化、200 条任务、错误处理等。

## 9. 常见问题

| 问题 | 处理 |
|------|------|
| `python` 不是内部或外部命令 | 安装 Python 3.10+，安装时勾选 “Add Python to PATH”，或使用 `py` 启动 |
| PowerShell 禁止运行 `Activate.ps1` | 执行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 后重新激活 |
| `ModuleNotFoundError: No module named 'flask'` | 确认已激活 `.venv`，再执行 `python -m pip install -r requirements.txt` |
| 端口 5000 被占用 | 使用 `flask --app app run --port 5001`，浏览器访问 5001 端口 |
| 页面样式/交互未更新 | 按 `Ctrl+F5` 强制刷新浏览器缓存 |
| 数据库损坏或需要重置 | 先备份 `studytask.db`，再删除文件并重启应用 |

## 10. 设计依据与相关文档

- 需求：`C:\Users\18362\Desktop\软件工程\附录.docx` 附录A（A.1–A.6）
- 设计：`C:\Users\18362\Desktop\软件工程\StudyTask软件设计说明书.md`
- AI 协作记录：`AI_DEV_LOG.md`

## 11. 范围说明

按 SRS A.5，不实现用户注册、多用户权限、共享任务、邮件/短信、第三方日历同步、移动 App 和云部署。
