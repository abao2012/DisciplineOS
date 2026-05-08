# DisciplineOS 后端优化计划

## 当前后端完成度判断

后端已经具备可运行的本地应用骨架：CLI、Web API、SQLite/JSON 存储、纪律卡、规则引擎、证据、仓位护栏、复盘、备份恢复、AI 解读记录、CSV/Excel 导入和基础测试都已经存在。

当前主要问题不是“不能跑”，而是部分 UI 已经提供入口，但后端仍停留在原型或占位状态。最明显的是数据源中心：CSV/Excel 已经可以执行，QMT/TuShare/AkShare 仍主要是配置和状态提示。

## 后端未完成清单

1. 数据源连接器
   - QMT：只校验本地路径，未接入 xtquant/QMT 数据读取。
   - TuShare：只保存 Token，未拉取日 K、5 分钟 K、成交量、财务指标。
   - AkShare：只检查依赖，未拉取行情和财务数据。
   - 缺少 provider 级别的统一错误码、依赖缺失提示、空数据提示。

2. 文档解读
   - PDF 文本提取可用。
   - TXT/MD 可用。
   - DOC/DOCX 解析不完整，当前不应承诺稳定支持。

3. 存储与服务层
   - `services.py` 体量过大，长期需要拆分为 profile/card/decision/data-source/review/backup 等服务。
   - SQLite 与 JSON 兼容写入方便调试，但未来需要明确主存储策略。
   - 敏感配置如 AI Token、TuShare Token 目前明文存储在本地数据库。

4. 生产化能力
   - 无用户认证、权限、加密、多用户隔离。
   - 无 GitHub Actions、打包发布流程、安装器。
   - 无浏览器端 E2E 测试。
   - 日志、异常分类和错误提示还需要统一。

## 分阶段优化计划

### Phase B1：数据源连接器后端化

目标：让数据源中心从“配置 UI”变成真正可执行的数据入口。

- 为 TuShare/AkShare 增加可选连接器。
- 支持能力：日 K、5 分钟 K、成交量、财务指标。
- 支持按个股代码过滤，避免一次同步全市场。
- 依赖缺失、Token 缺失、空数据、API 异常都返回结构化错误。
- 保持 CSV/Excel 已有行为不变。
- 增加单元测试，用 fake module 模拟第三方库，避免测试依赖真实网络。

### Phase B2：信息解读后端增强

- 明确 PDF/TXT/MD/DOCX 的支持边界。
- 增加 DOCX 文本提取。
- 对超长材料做分段摘要。
- AI 输出继续经过合规护栏，禁止目标价、确定性收益、直接买卖建议。

### Phase B3：服务层拆分

- 从 `DisciplineService` 拆出 DataSourceService、DecisionService、ReviewService、BackupService。
- 保持 Web API 不变，降低后续维护成本。
- 增加边界测试。

### Phase B4：数据安全与发布工程

- Token 改为本地环境变量优先，数据库只保存是否启用和 provider 配置。
- 增加导出前隐私检查命令。
- 增加 GitHub Actions：pytest、compileall、node syntax check。
- 增加 release 打包说明。

## 当前执行批次

本批次执行 Phase B1：

- 新增 TuShare/AkShare 可选连接器。
- 更新数据源状态检测。
- 增加连接器测试。
- 验证现有 59 个测试不回退。
