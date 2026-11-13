# AI_DEV_LOG · StudyTask 个人学习任务管理系统

> 项目：StudyTask（个人学习任务管理系统）
> 记录日期：2026-11-13
> 协作方式：学生提出需求、确认口径与验收；AI 负责需求整理、设计、编码、测试与 UI 修复。
> 说明：本文件按附录D.2 的 AI 协作记录格式整理，保留关键指令、产出与决策，不逐字复制全部对话。

---

## 1. 项目目标与范围

- 需求依据：`C:\Users\18362\Desktop\软件工程\附录.docx` **附录A（A.1–A.6）StudyTask SRS**。
- 技术边界：Python 3 + Flask + Jinja2 + SQLite，单用户、本地浏览器访问。
- 范围：实现 FR-01～FR-10；不实现注册、多用户、共享、邮件/短信、日历同步、移动 App、云部署（SRS A.5）。
- 验收：可按 README 在本机运行；自动化测试覆盖核心功能；严重缺陷修复；源代码、依赖清单、测试结果、README 齐全。

## 2. 关键对话时间线

| 阶段/版本 | 学生关键指令 | AI 产出与问题 | 学生判断/验证 |
|-----------|--------------|----------------|----------------|
| v0.1 需求与设计 | “查看附录.docx，严格依据 StudyTask SRS 完成设计说明书；所有内容待确认后再执行。” | 读取附录A，确认附录B/C/D 属实验二/三，不纳入；提出设计结构、单表数据模型、路由、追踪矩阵 | 确认 Markdown 输出、drawio 图、T1—T10 不处理、今天～今天+3/整数完成率 |
| v0.2 设计定稿 | “不用生成图。” | 删除 `StudyTask-uml/*.drawio` 及正文图件引用；流程改为文字消息链、判定规则与表格 | 接受文字化设计说明书 |
| v0.3 编码实现 | “使用 python+flask+sqlit 开发，项目源代码输出到 实验\StudyTask。” | 生成 `app.py/models.py/dao.py/schema.sql/templates/static/tests/README`；`pytest -q` 18 passed | 验收项目结构与功能 |
| v1.0 UI 修复① | “必填 `*` 与输入框错位；下拉箭头错位；下拉框改轻圆弧；页脚只保留指定文字。” | 引入 `.label-text` 修复 `*` 布局；自定义 select 箭头；10px 圆角；页脚精简 | 18 passed |
| v1.1 UI 修复② | “下拉框的内容选择外框也需要优化。” | 新增自定义下拉面板（`static/app.js` + CSS），保留原生 select 负责提交；面板 12px 圆角、阴影、hover | 18 passed |
| v1.2 UI 修复③ | “描述框不可无限延伸；日期/优先级高度不一致；原生日历取消/今天 hover 错位；页面未居中。” | 描述框 120–260px 自动增高、超限滚动；控件统一 42px；自定义日期选择器；卡片居中 + 滚动条占位 | 18 passed，JS 语法检查通过 |
| v1.3 记忆点 | “增加记忆点：修改内容时，不要对数据库进行覆盖删除。” | 记录 nt 常驻规则 `Y3ERHP`（`rules/`）：只做增量 `UPDATE`，禁止覆盖/清空/删除数据库 | 已记录 |
| v1.4 文档 | “更新 README，确保有从零开始的运行步骤；将对话重要部分整理到 AI_DEV_LOG.md。” | 重写 README（环境、虚拟环境、安装、运行、测试、重置、排错）；生成本文件 | 待确认 |

## 3. 设计与实现决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 数据模型 | 单表 `task`，无用户表/课程表 | SRS 为单用户、课程为自由文本；200 条规模无需规范化 |
| 分层 | 界面层 → 控制层 → DAO → 实体/值对象 | 对应 ECB 设计，便于测试与追踪 FR |
| 数据访问 | `sqlite3` + 参数化 SQL，无 ORM | 依赖少、SQL 透明、便于课程评审 |
| ID | 整数自增 | SRS 允许“整数或 UUID”，整数更简单 |
| 日期 | `TEXT` 存 `YYYY-MM-DD`，应用层校验 | SQLite 无原生 DATE；字符串比较等价日期序 |
| 逾期/即将到期 | 未完成且 `<今天` / `今天～今天+3（含）` | 严格按 FR-07；已完成不提醒 |
| 完成率 | `completed/total` 四舍五入取整；0 任务为 0% | 符合 FR-08；避免小数显示歧义 |
| 删除 | 确认后硬删除 | FR-04 要求“从数据库删除” |
| 修改 | `UPDATE` 保留原记录 | 避免 `DELETE + INSERT` / 重建表；符合数据库安全规则 |
| 前端 | 服务端渲染 + 原生 JS 增强 | SRS 不强制前端框架；离线可用 |
| 下拉/日期 | 自定义面板，原生控件保留提交 | 原生 select/date 弹层由浏览器绘制，CSS 无法可靠修正 hover/圆角 |

## 4. UI 问题与修复记录

| 问题 | 原因 | 修复 |
|------|------|------|
| 必填 `*` 与输入框错位 | `<label>` 为 flex column，`*` 成为独立 flex 项 | 用 `.label-text` 包裹标签文字与 `*`，`inline-flex; align-items: baseline` |
| 下拉箭头错位 | 原生 select 箭头由系统绘制 | `appearance: none` + SVG 箭头，`right 12px center` 固定居中 |
| 下拉矩形尖锐 | 原生 select 边框/圆角不可控 | 输入框/下拉统一 `border-radius: 10px`；自定义下拉面板 12px |
| 下拉内容面板外框 | 原生 option 列表无法定制 | 自定义 `.select-menu`：圆角、阴影、hover、选中高亮；固定定位避免表格裁切 |
| 描述框无限延伸 | `resize: vertical` 且无高度上限 | `resize: none`，120–260px 自动增高，超过后内部滚动 |
| 日期/优先级高度不一致 | 原生 date 与自定义 select 高度不同 | 统一 `--control-h: 42px` |
| 原生日历“取消/今天”hover 错位 | 浏览器原生日期弹层不可样式化 | 自定义日期选择器：日期网格 + `.date-action:hover`，布局用 flex |
| 页面偏移/未居中 | 表单卡片有 max-width 但无自动外边距；滚动条出现导致横向位移 | `.form-card/.detail-card { margin: 0 auto }`；`html { overflow-y: scroll }` |
| 页脚冗余 | 页脚包含额外说明 | 仅保留“StudyTask · 个人学习任务管理” |

## 5. 数据库安全记忆点

- **规则 ID**：`Y3ERHP`（nt `rules/`，每次会话自动注入）。
- **规则**：修改内容/代码时只做增量更新，禁止覆盖、清空或删除数据库。
  - 更新记录用 `UPDATE` 保留原行；禁止 `DELETE + INSERT` 或重建表来“修改”。
  - 禁止 `DROP TABLE`、清空表、删除 `studytask.db` 或用空库覆盖。
  - 重置/迁移前先备份 `studytask.db` 并征得确认。
  - 写操作使用事务；测试使用独立临时数据库。
- **代码现状**：`TaskDAO.update()` 使用 `UPDATE`；测试使用 `tmp_path` 独立库；`studytask.db` 仅首次运行自动生成。

## 6. 验证记录

| 检查 | 命令 | 结果 |
|------|------|------|
| 自动化测试 | `python -m pytest -q` | **18 passed** |
| JS 语法 | `node --check static/app.js` | 通过 |
| 路由注册 | `python -c "from app import app; ..."` | `/`、`/tasks`、`/tasks/<id>`、`/tasks/<id>/edit`、`/tasks/<id>/status`、`/tasks/<id>/delete` 等 |
| 核心覆盖 | pytest 用例 | 创建/校验、列表/详情、修改、删除、状态、组合筛选、逾期/即将到期、统计/0 任务、持久化、200 条任务、404 |

## 7. 问题与反思

1. **子代理模型不可用**：omo 预设的 `openai/gpt-6.1-sol` 在本机不存在，导致并行子代理无法启动。后续改为由主会话直接实现，避免在模型不可用时强行派发。
2. **原生控件弹层不可样式化**：`<select>` 与 `<input type="date">` 的弹出层由浏览器绘制，CSS 无法修正外框圆角与 hover。改用“隐藏原生控件 + 自定义面板”，保留原生控件负责表单提交与无 JS 回退。
3. **数据库清理与安全规则**：早期清理运行时曾删除 `studytask.db`；用户随后明确要求“修改内容时不要覆盖删除数据库”，已记录为常驻规则，后续重置必须先备份并确认。
4. **T1—T10 的处理**：附录A 的 A.6 提到 T1—T10，但未附具体用例；按用户要求不自行定义，设计文档只说明测试层次与追踪关系，具体测试集由课程/用户提供。
5. **设计图取舍**：初版设计生成了 7 张 drawio 图，用户明确“不用生成图”，已删除图件与引用，改为文字消息链、判定规则和表格描述。

## 8. 当前文件清单

```text
StudyTask/
  app.py                 # Flask 应用、路由、控制器、错误处理
  models.py              # Task / TaskView / Summary / 校验
  dao.py                 # TaskDAO（sqlite3，参数化 SQL）
  schema.sql             # task 单表建表脚本
  templates/             # base/index/task_form/task_detail/delete_confirm/404/500
  static/style.css       # 页面样式
  static/app.js          # 自定义下拉面板、日期选择器、描述框自动增高
  tests/test_app.py      # 18 条 pytest 用例
  requirements.txt
  README.md              # 从零运行步骤
  AI_DEV_LOG.md          # 本文件
  .gitignore
```

## 9. 后续可做

- 增加浏览器截图与人工视觉验收记录。
- 为自定义下拉/日期选择器补充前端交互测试（当前以人工/浏览器验证为主）。
- 如课程要求，补充测试记录表（T1—T10 实际结果）与实验报告截图。
- 继续保持“只 `UPDATE`、不覆盖删除数据库”的数据安全规则。

---

## 10. 对话过程记录（按时间顺序）

> 说明：用户消息保留原话；AI 回复因包含大量工具输出与长文，以下保留关键结论、操作与验证结果，工具输出从略。

### 10.1 安装 omo-slim 插件

**用户**：
> 安装omo-slim插件

**AI 处理与结果**：
- 在 npm 检索到 `oh-my-opencode-slim`（omo-slim）；本机为 OpenCode 桌面版 1.17.11、没有 `opencode` CLI，安装器误判“未安装”。
- 用临时版本 shim 绕过检测，执行 `npx -y oh-my-opencode-slim@latest install --no-tui`。
- 结果：`~/.config/opencode/opencode.jsonc` 增加 `"oh-my-opencode-slim"`；生成 `oh-my-opencode-slim.json`（openai/opencode-go 预设，默认 openai）；加入 TUI badge；预热插件缓存。
- 后续发现 omo 子代理模型 `openai/gpt-6.1-sol` 在本机不可用，StudyTask 实现改为主会话直接完成。

### 10.2 安装 draw.io 插件

**用户**：
> 安装draw.io插件

**AI 处理与结果**：
- 说明 npm 上有两个候选，询问后用户选择 `opencode-drawio`。
- 将 `"opencode-drawio"` 加入 `opencode.json` 的 `plugin` 数组；该包 postinstall 依赖 `bun`，本机无 bun，改用 npm 安装依赖并跳过脚本，预置插件缓存。

### 10.3 安装 nt（蒸馏插件）

**用户**：
> 安装蒸馏插件“nt”

**AI 处理与结果**：
- npm/GitHub 未找到名为 `nt` 的蒸馏插件，询问后用户给出 `https://github.com/navbytes/nt/releases/tag/v0.31.0`。
- 通过 gh-proxy 下载 `nt_0.31.0_windows_amd64.zip`，校验 SHA256 通过；安装到 `%LOCALAPPDATA%\Programs\nt\nt.exe` 并加入用户 PATH。
- 执行 `nt opencode install`：注册 MCP、安装 `nt-memory` 插件、`nt` skill、`/learn`、`/recall`、`/distill`、AGENTS.md、`permission.skill.nt`、`nt-rules.md`。
- 为避免 `opencode.json` 与 `opencode.jsonc` 双配置，将原配置合并/重命名为 `opencode.json`。

### 10.4 蒸馏资料库

**用户**：
> 我要蒸馏该文件夹下 “资料库”文件夹内的所有文档资料，告诉我如何做的步骤，待我确认后再执行。

**AI 处理与结果**：
- 扫描 `实验\资料库\资料库`，共 83 份文档；说明 nt 的 `/distill` 是整理已有笔记，不是导入外部文档。
- 提出“抽取文本 → 摘要 → `nt_note`”的步骤；询问粒度、范围、特殊 PDF 处理。
- 用户确认：每份文档一条、文档 + 源码、Java 扫描件跳过、BABOK 按章。
- 执行：用 PyMuPDF / python-pptx / PowerPoint COM / Word COM 抽取文本；创建 104 条内容笔记（81 份文档 + BABOK 16 章 + 源码 7 条）和 8 条索引；修复标题、合并旧索引、移动到 `kb/软件工程`；常驻层压缩到 10 条。

### 10.5 撰写 StudyTask 设计说明书

**用户**：
> 请查看该目录下的附录.docx。请严格依据附件《StudyTask需求规格说明书》完成撰写设计说明书。所有内容待我确认后再执行。

**AI 处理与结果**：
- 读取 `附录.docx`，确认本次依据 **附录A（A.1–A.6）**；附录B/C/D 属实验二/三，不纳入。
- 提出 10 部分结构、单表 `task` 数据模型、Flask + SQLite 技术口径、FR-01～FR-10 追踪矩阵。
- 询问输出格式、图件、T1—T10、边界口径；用户选择 Markdown、使用 drawio、T1—T10 不处理、今天～今天+3（含）与整数完成率。
- 生成 `StudyTask软件设计说明书.md` 与 7 张 drawio；用户随后明确“不用生成图”，删除图件与正文引用，保留文字消息链、判定规则和表格。

### 10.6 开发 StudyTask 项目

**用户**：
> 请根据 StudyTask软件设计说明书.md ，使用python+flask+sqlit开发项目，项目源代码输出到“实验\StudyTask”

**AI 处理与结果**：
- 生成 `app.py`、`models.py`、`dao.py`、`schema.sql`、`templates/`、`static/style.css`、`tests/test_app.py`、`README.md`、`requirements.txt`、`.gitignore`。
- 实现 FR-01～FR-10：创建/校验、列表/详情、修改、删除确认、状态调整、组合筛选、逾期/即将到期、统计、SQLite 持久化、中文错误处理。
- `python -m pytest -q` → **18 passed**；清理 `__pycache__`、`.pytest_cache` 与运行时数据库。

### 10.7 UI 修复①：必填提示、下拉箭头、圆角、页脚

**用户**：
> 现在修复问题1：界面美观性问题。
> 1.错位问题。必填提示*与输入框错位；下拉框箭头错位
> 2.外观问题。下拉矩形框可以换成轻圆弧框，减少尖锐感
> 3.内容问题。底部内容仅保留“StudyTask · 个人学习任务管理”

**AI 处理与结果**：
- 用 `.label-text` 包裹标签文字与 `*`，避免 flex column 把 `*` 挤成独立行。
- `select` 使用 `appearance: none` + 内嵌 SVG 箭头，固定 `right 12px center`。
- 输入框/下拉框统一 `border-radius: 10px`。
- 页脚改为仅保留“StudyTask · 个人学习任务管理”。
- 验证：18 passed。

### 10.8 UI 修复②：下拉框内容选择外框

**用户**：
> 下拉框的内容选择外框也需要进行优化

**AI 处理与结果**：
- 说明原生 `<select>` 弹出层由浏览器绘制，CSS 无法可靠调整外框。
- 新增 `static/app.js`：把每个 `<select>` 增强为“圆角触发按钮 + 圆角选项面板”，保留原生 select 负责表单提交；面板 12px 圆角、阴影、hover/选中高亮，固定定位避免被表格裁切。
- 验证：18 passed；`node --check static/app.js` 通过。

### 10.9 UI 修复③：描述框、控件高度、日历、页面居中

**用户**：
> 现在修复问题2：实际操作、美观问题。
> 1.不可控因素。任务描述的框不可以无限延申，可以适当增加框架高度限制，当超出框架高度之后，可以自动延申。
> 2.框架问题。截止日期和优先级的输入框高度不一致，影响观感；日历选择页面，取消按钮和今天按钮的hover有错位问题。
> 3.界面问题。大部分页面没有居中效果，页面偏移。

**AI 处理与结果**：
- 描述框：`resize: none`，最小 120px、最大 260px；JS 自动增高，超过 260px 后内部滚动。
- 统一控件高度 `--control-h: 42px`：文本/日期输入、下拉触发按钮、筛选按钮对齐。
- 原生日历弹层的“取消/今天”无法用 CSS 修正，改为自定义日期选择器：圆角面板、日期网格、今天/取消按钮使用 `.date-action:hover` 对齐。
- 页面居中：`.form-card`/`.detail-card` 增加 `margin: 0 auto`；`html { overflow-y: scroll; }` 固定滚动条占位。
- 验证：18 passed；JS 语法检查通过。

### 10.10 数据库安全记忆点

**用户**：
> 增加记忆点：修改内容时，不要对数据库进行覆盖删除

**AI 处理与结果**：
- 在 nt 中记录常驻规则 `Y3ERHP`（`rules/`，每次会话注入）。
- 规则：更新用 `UPDATE` 保留原行；禁止 `DELETE + INSERT`、重建表、`DROP TABLE`、清空表、删除 `studytask.db` 或用空库覆盖；重置/迁移前先备份并确认；写操作使用事务；测试使用临时数据库。
- 代码现状：`TaskDAO.update()` 使用 `UPDATE`，测试使用 `tmp_path` 独立库，符合规则。

### 10.11 README 与 AI_DEV_LOG

**用户**：
> 更新README.md，确保有从零开始的运行步骤。另外，将我们之间对话的重要部分整理成md文件，导出到AI_DEV_LOG.md。

**AI 处理与结果**：
- 重写 `README.md`：环境要求、Windows/macOS/Linux 从零步骤（venv、激活、安装、运行、访问、停止）、测试、数据库备份/重置、常见问题。
- 生成 `AI_DEV_LOG.md`：项目目标、时间线、设计决策、UI 修复、数据库规则、验证、问题与反思。
- 验证：18 passed。

### 10.12 本轮：保留对话过程

**用户**：
> AI_DEV_LOG.md需要保留我们之间的对话过程

**AI 处理与结果**：
- 在 `AI_DEV_LOG.md` 末尾新增本节，按时间顺序保留用户原话与 AI 的关键处理/结果，形成可追溯的对话过程记录。

