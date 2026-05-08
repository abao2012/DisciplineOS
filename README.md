# DisciplineOS

DisciplineOS 是一个本地优先、数据源无关的个人投资纪律系统。它不荐股、不预测股价、不替用户交易，而是帮助投资者把模糊的投资判断转化为可执行、可审计、可复盘的纪律流程。

> Most investment tools track what you own. DisciplineOS governs how you decide.

## 当前实现状态

本项目已经从白皮书原型推进为一个可运行的本地 Web 工作台和 Python 服务。当前覆盖的核心闭环包括：

- 投资者纪律画像
- 纪律卡问答式生成器
- 价值、成长、周期、趋势、ETF 模板
- 持仓管理
- CSV / Excel 持仓导入
- CSV / Excel 交易流水导入
- 仓位治理 Position Guard
- 交易前决策审查 Decision Gate
- 规则引擎 Rule Engine
- 违规账本 Violation Ledger
- 加权纪律评分 Discipline Score
- 月度复盘 Review Engine
- 本地 Copilot 草稿层
- 财报证据摘要 Financial Report Agent
- 中英文 UI 切换

系统仍然坚持白皮书边界：它只审查“是否符合你事先定义的纪律”，不判断“会不会赚钱”。

## 快速开始

### 方式一：安装后运行

```powershell
cd D:\project\DisciplineOS_Architecture_Whitepaper
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
disciplineos web --data-dir .\data
```

然后打开：

```text
http://127.0.0.1:8765
```

### 方式二：不安装，直接运行源码

```powershell
cd D:\project\DisciplineOS_Architecture_Whitepaper
$env:PYTHONPATH = "src"
python -m disciplineos.cli web --data-dir .\data
```

如果 PowerShell 中文显示乱码，可以先执行：

```powershell
chcp 65001
```

## 常用命令

运行测试：

```powershell
.\.venv\Scripts\pytest.exe
```

启动 Web UI：

```powershell
.\.venv\Scripts\disciplineos.exe web --data-dir .\data
```

载入示例数据：

```powershell
.\.venv\Scripts\disciplineos.exe demo --data-dir .\data
```

审查一个决策 JSON：

```powershell
.\.venv\Scripts\disciplineos.exe check .\examples\sample_decision.json --data-dir .\data
```

生成月度复盘：

```powershell
.\.venv\Scripts\disciplineos.exe review --month 2026-04 --data-dir .\data
```

## Web UI 使用说明

### 1. 语言切换

页面右上角可以在 English / 中文之间切换。选择会保存在浏览器 `localStorage`，刷新后保持。

### 2. Discipline Card Generator

用于从六个核心问题生成纪律卡：

1. 为什么买？
2. 最多买多少？
3. 什么情况下不买？
4. 什么情况下加仓？
5. 什么情况下减仓？
6. 什么情况说明我错了？

支持模板：

- Value
- Growth
- Cyclical
- Trend
- ETF

生成后的纪律卡会保存到 Discipline Card Library，并可作为草稿再次编辑。

### 3. Decision Gate

交易前审查模块。选择已有标的后，填写：

- 操作类型：买入、加仓、减仓、清仓
- 操作金额
- 操作理由
- 新增证据
- 当前情绪状态
- 是否财报前
- 投资逻辑是否变化

默认会根据当前持仓自动计算操作前后仓位，并由规则引擎输出：

- `PASS`
- `WARN`
- `BLOCKED`

### 4. Data Import

支持从本地 CSV / Excel 导入：

- positions：持仓
- trades：交易流水

示例文件：

```text
examples/positions.csv
examples/trades.csv
```

UI 中填写本地绝对路径即可，例如：

```text
D:\project\DisciplineOS_Architecture_Whitepaper\examples\positions.csv
```

### 5. Financial Report Agent

本地财报证据摘要工具。可输入：

- 本地 Markdown / text 文件路径
- 直接粘贴财报文本

它会提取：

- 收入
- 利润
- 毛利率
- 现金流
- 管理层指引 / 展望

输出只作为“证据摘要”，不构成投资建议。

示例文件：

```text
examples/financial_report_sample.md
```

### 6. Investor Profile

维护投资者纪律画像：

- 投资风格
- 单标的仓位上限
- 行业仓位上限
- 最大回撤容忍
- 是否允许财报前加仓
- 行为弱点

画像会约束纪律卡和决策审查。

### 7. Position Book

维护当前持仓：

- 代码
- 名称
- 资产类型
- 市场
- 行业
- 主题
- 币种
- 数量
- 成本价
- 当前价

### 8. Position Guard

仓位治理模块会自动计算：

- 单标的暴露
- 行业暴露
- 主题暴露
- 市场暴露
- 币种暴露

当单标的或行业接近 / 超过画像上限时，会产生警告。

### 9. Monthly Review

月度复盘包含：

- 加权纪律评分
- PASS 率
- 违规类型统计
- 下月禁止行为
- 分项评分
- 四类归因：
  - market
  - security
  - portfolio
  - behavior
- 规则修订建议

### 10. Copilot

Copilot 是本地纪律助手，不调用外部 AI API。它基于系统已有数据生成：

- 纪律一致性复盘草稿
- 逻辑漂移提示
- 纪律卡修订草稿
- 下一步动作

Copilot 不输出：

- 买卖建议
- 目标价
- 收益预测
- 确定性判断

### 11. Violation Ledger

违规账本记录每次审查触发的问题。每条违规包含：

- 类型
- 分类
- 严重程度
- 权重
- 规则 ID
- 修正建议
- open / resolved 状态

可以在 UI 中将违规标记为 resolved。

## 数据目录

所有数据默认保存在你启动时指定的 `--data-dir` 中，例如：

```text
data/
  profile.json
  cards.json
  positions.json
  trades.json
  decisions.json
  audits.json
  violations.json
  financial_reports.json
```

这是本地优先项目，不需要数据库。

## CSV 字段格式

### positions.csv

```csv
symbol,name,asset_type,market,sector,theme,currency,quantity,cost_price,current_price
SAMPLE,Sample Asset,stock,HK,technology,AI,HKD,1000,10,10
```

### trades.csv

```csv
symbol,action,quantity,price,amount,fee,traded_at,note
SAMPLE,buy,1000,10,10000,5,2026-04-10T10:00:00+00:00,Initial position
```

`action` 支持：

- `buy`
- `add`
- `reduce`
- `sell`

## 项目结构

```text
src/disciplineos/
  adapters.py              CSV / Excel 导入适配器
  card_generator.py        纪律卡生成器和模板库
  cli.py                   命令行入口
  copilot.py               本地 Copilot 草稿层
  financial_report.py      财报证据摘要
  models.py                统一数据模型
  position_guard.py        仓位治理
  review_engine.py         月度复盘归因与规则修订建议
  rules.py                 规则引擎
  scoring.py               加权纪律评分
  services.py              应用服务层
  storage.py               本地 JSON 存储
  violation_catalog.py     违规类型库
  static/
    index.html
    app.js
    styles.css
docs/
  00-development-plan.md
  01-product-positioning.md
  02-system-architecture.md
  03-rule-engine-design.md
examples/
  positions.csv
  trades.csv
  financial_report_sample.md
  sample_decision.json
tests/
```

## 合规边界

DisciplineOS 必须避免被误解为荐股、投资顾问或自动交易系统。

本项目遵守以下原则：

- 不提供确定性收益承诺
- 不输出“必涨 / 必买 / 目标价”等表述
- 不主动推荐标的
- 不替用户交易
- 不把 Copilot 作为最终裁判
- 示例仅用于展示系统结构，不构成投资建议

## 当前路线图

已完成：

- Phase 1：MVP 手动闭环、持仓管理、仓位治理
- Phase 2：纪律卡问答生成器和模板库
- Phase 3：规则引擎、违规类型库、违规账本生命周期
- Phase 4：加权纪律评分、复盘归因、规则修订建议
- Phase 5：CSV / Excel 数据导入
- Phase 6：本地 Copilot 和财报证据摘要

后续可继续增强：

- 更严格的数据校验和字段映射 UI
- 更完整的交易流水到持仓自动归集
- 报告导出
- 画像问卷
- 真实 AI API 接入，但必须继续遵守合规边界
