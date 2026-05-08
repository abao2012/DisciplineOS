# DisciplineOS

DisciplineOS 是一个本地优先的个人投资纪律系统。它不荐股、不预测价格、不替用户交易，而是帮助投资者把“事前写下的纪律”落实到数据、证据、仓位、决策审查、记录和复盘流程里。

一句话概括：**DisciplineOS 不回答“这只股票会不会涨”，它回答“这次操作是否符合我事先定义的纪律”。**

## 当前定位

本项目目前是一个可运行的本地 Web 应用和 Python 后端原型，适合用于个人投资纪律管理、交易前自查、证据归档和月度复盘。

它不是：

- 投资顾问系统
- 荐股工具
- 自动交易系统
- 收益预测系统
- 目标价生成器

## 核心功能

- 本地 Web UI：默认运行在 `http://127.0.0.1:8765/`
- 中英文界面切换
- 纪律卡生成器
- 纪律卡库
- 投资者画像
- 数据源中心
- 信息解读中心
- 证据引擎
- 决策闸门
- 副驾驶
- 持仓簿
- 仓位护栏
- 交易流水
- 决策历史
- 违规台账
- 月度复盘
- 系统设置、AI 配置、备份与恢复、系统状态检查

## 七层结构

当前 UI 按以下七层组织：

1. 规则层
   - 纪律卡生成器
   - 纪律卡库
   - 投资者画像

2. 数据与信息层
   - 数据源中心
   - 信息解读中心

3. 证据与分析层
   - 证据引擎
   - 财报证据保存区
   - 副驾驶

4. 决策执行层
   - 决策闸门

5. 持仓与风控层
   - 持仓簿
   - 当前持仓
   - 仓位护栏

6. 记录与复盘层
   - 交易流水
   - 决策历史
   - 违规台账
   - 月度复盘

7. 系统支撑层
   - 系统设置
   - AI 配置
   - 本地备份与恢复
   - 系统状态

页面顶部的纪律评分、决策检查次数、本月状态是全局摘要，不属于某个单独业务层。

## 纪律卡生成器

纪律卡生成器当前不是 6 个问题，而是 **8 个编号问题 + 禁止行为**。

基础字段：

- 标的代码
- 标的名称
- 行业 / 主题
- 最大仓位比例
- 复盘周期

8 个编号问题：

1. 为什么买？
2. 我最多可以买多少？
3. 什么条件下不买？
4. 什么情况下可以加仓？
5. 什么情况下必须减仓？
6. 什么情况下可以提高仓位上限？
7. 什么情况下必须降低仓位上限？
8. 什么情况证明我错了？

额外纪律项：

- 禁止行为

生成后的纪律卡会保存到纪律卡库，并在决策闸门、证据引擎和复盘流程中被引用。

## 投资者画像

投资者画像用于定义全局约束：

- 名称
- 价值风格占比
- 成长风格占比
- 周期风格占比
- 红利风格占比
- 现金 / 防守仓位占比
- 单一标的仓位上限
- 行业仓位上限
- 最大回撤容忍
- 是否允许财报前加仓
- 行为弱点

风格占比不要求合计为 100%，但系统会阻止合计超过 100%。

## 数据源中心

当前支持的数据源类型：

- QMT
- TuShare
- AkShare
- CSV
- Excel
- 手动数据

可同步的数据类型：

- 日 K
- 5 分钟 K
- 成交量
- 财务指标
- 持仓
- 交易流水

实现状态：

- CSV / Excel：已实现本地文件导入和证据转换。
- TuShare：已接入可选连接器，需要安装 `tushare` 并配置 Token。
- AkShare：已接入可选连接器，需要安装 `akshare`。
- QMT：当前保存本地路径和状态，但真实 QMT / xtquant 连接器尚未完成。

为避免一次同步全市场数据，数据源同步支持填写个股代码后按标的同步。

## 信息解读中心

信息解读中心用于处理：

- 财报
- 研报
- 公告 / 新闻
- 市场事件

输入方式：

- 选择本地 PDF / Markdown / TXT 文件
- 粘贴原始文本
- 可选启用 AI 在线搜索意图

当前实现：

- PDF 文本提取依赖 `pypdf`
- Markdown / TXT 文本可直接读取
- DOC / DOCX 解析尚未完整实现
- 未启用 AI 时使用本地规则摘要
- 启用 AI 后调用 OpenAI-compatible API，并经过合规护栏处理

解读结果可以保存为证据，也可以生成纪律卡建议。

## 证据引擎

证据可以来自：

- 手动录入
- 信息解读中心
- 数据源同步

证据字段包括：

- 标的代码
- 证据类型
- 证据标题
- 证据内容
- 证据来源
- 来源日期

证据库通过弹窗查看，不在主页展开全部内容。

## 决策闸门

决策闸门用于交易前审查。

输入项：

- 标的代码
- 操作类型：买入、加仓、减仓、卖出
- 金额
- 当前情绪
- 操作理由
- 手动证据
- 已保存证据项
- 是否财报前
- 投资逻辑是否变化
- 是否自动计算操作前后仓位

审查输出包括：

- `PASS`
- `WARN`
- `BLOCKED`
- `EVIDENCE_REQUIRED`
- `REVIEW_REQUIRED`

## 规则引擎

当前规则覆盖：

- 单一标的仓位上限
- 买入 / 加仓必须有证据
- 情绪化补仓
- 财报前无计划加仓
- FOMO
- 报复性交易
- 投资逻辑漂移
- 投资风格漂移
- 估值约束
- 重大操作后复盘要求

## 持仓与风控

持仓簿字段：

- 标的代码
- 名称
- 资产类型
- 市场
- 行业
- 主题
- 币种
- 数量
- 成本价
- 当前价

仓位护栏会计算：

- 单一标的暴露
- 行业暴露
- 主题暴露
- 市场暴露
- 币种暴露

当暴露接近或超过投资者画像中的上限时，系统会提示风险。

## 记录与复盘

系统会记录：

- 交易流水
- 决策历史
- 规则结果
- 违规台账
- 月度复盘快照
- 复盘报告

月度复盘包括：

- 纪律评分
- PASS 比例
- 违规类型统计
- 违规权重
- 归因分析
- 下月禁止行为
- 规则修订建议
- 快照对比
- Markdown 报告导出

## 副驾驶

副驾驶是纪律辅助层，不是荐股助手。

它可以帮助整理：

- 纪律一致性摘要
- 投资逻辑漂移提醒
- 纪律卡修订草稿
- 下次复盘动作

它不会输出：

- 买入建议
- 卖出建议
- 目标价
- 确定性收益判断

## 安装与运行

要求：

- Python 3.11+

创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

如果需要 TuShare / AkShare 数据源：

```powershell
python -m pip install -e ".[dev,data]"
```

启动 Web UI：

```powershell
disciplineos web --data-dir .\data
```

打开：

```text
http://127.0.0.1:8765/
```

如果没有安装入口命令，也可以直接运行源码：

```powershell
$env:PYTHONPATH = "src"
python -m disciplineos.cli web --data-dir .\data
```

## 常用命令

加载示例数据：

```powershell
disciplineos demo --data-dir .\data
```

审查一个决策 JSON：

```powershell
disciplineos check .\examples\sample_decision.json --data-dir .\data
```

生成月度复盘：

```powershell
disciplineos review --month 2026-05 --data-dir .\data
```

运行测试：

```powershell
.\.venv\Scripts\pytest.exe -q
```

源码编译检查：

```powershell
.\.venv\Scripts\python.exe -m compileall -q .\src
```

前端 JavaScript 语法检查：

```powershell
node --check .\src\disciplineos\static\app.js
```

## 数据目录

所有本地运行数据默认保存在启动时指定的 `--data-dir` 中，例如：

```text
data/
```

该目录可能包含：

- 本地数据库
- 纪律卡
- 持仓
- 交易流水
- 证据
- 决策历史
- 违规台账
- AI 配置
- 备份文件

因此 `data/` 已被 `.gitignore` 排除，不应上传到公开仓库。

## 示例文件

```text
examples/
  financial_report_sample.md
  positions.csv
  sample_decision.json
  trades.csv
```

持仓 CSV 字段：

```csv
symbol,name,asset_type,market,sector,theme,currency,quantity,cost_price,current_price
```

交易流水 CSV 字段：

```csv
symbol,action,quantity,price,amount,fee,traded_at,note
```

`action` 支持：

- `buy`
- `add`
- `reduce`
- `sell`

## 项目结构

```text
src/disciplineos/
  adapters.py              CSV / Excel 导入
  ai_analysis.py           可选 AI 信息解读
  ai_guardrails.py         AI 输出合规护栏
  card_generator.py        纪律卡生成器与模板
  cli.py                   命令行入口
  connectors.py            CSV / Excel / TuShare / AkShare 连接器
  copilot.py               纪律副驾驶
  financial_report.py      财报 / 研报 / 新闻材料解读
  models.py                数据模型
  position_guard.py        仓位护栏
  repositories.py          仓储封装
  review_engine.py         月度复盘
  rules.py                 规则引擎
  scoring.py               纪律评分
  services.py              应用服务层
  storage.py               SQLite + JSON 兼容存储
  violation_catalog.py     违规类型
  web.py                   本地 Web API
  static/
    index.html
    app.js
    styles.css
```

## 当前限制

- QMT 真实连接器尚未完成。
- DOC / DOCX 文档解析尚未完整实现。
- AI 在线搜索不是内置浏览器搜索，而是交给配置的 AI Provider 处理。
- 当前定位是本地单人使用，没有登录、多用户权限和加密存储。
- 真实交易系统、自动下单、收益预测不在当前范围内。

## 隐私与上传注意

以下内容不应上传到 GitHub：

- `data/`
- `.venv/`
- `.env`
- `*.db`
- `*.sqlite`
- 本地备份压缩包
- 私有白皮书或工程规格文档

本仓库的 `.gitignore` 已默认排除这些内容。

## 合规边界

DisciplineOS 的输出只能作为个人纪律检查和复盘参考，不构成投资建议。任何买入、卖出、加仓、减仓决定都应由用户自行负责。
