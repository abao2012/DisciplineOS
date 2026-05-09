const state = {
  month: new Date().toISOString().slice(0, 7),
  lang: localStorage.getItem("disciplineos.lang") || "en",
  cardTemplates: {},
  pathBrowser: {
    currentPath: "",
    parentPath: "",
    targetForm: "",
    targetName: "",
    mode: "directory",
    extensions: "",
  },
  latest: {
    settings: {},
    health: {},
    backups: [],
    dataSources: [],
    financialReports: [],
    infoAnalysisSummary: null,
    syncLogs: [],
    marketDataSummary: { by_type: [], top_symbols: [] },
    marketRecords: [],
    tradeReconciliation: { totals: {}, warnings: [], by_symbol: {} },
    evidenceItems: [],
    cards: {},
  },
};

const els = {
  languageSelect: document.querySelector("#languageSelect"),
  monthInput: document.querySelector("#monthInput"),
  seedButton: document.querySelector("#seedButton"),
  refreshButton: document.querySelector("#refreshButton"),
  templateSelect: document.querySelector("#templateSelect"),
  whyBuyOptions: document.querySelector("#whyBuyOptions"),
  positionPresetOptions: document.querySelector("#positionPresetOptions"),
  noBuyOptions: document.querySelector("#noBuyOptions"),
  addWhenOptions: document.querySelector("#addWhenOptions"),
  reduceWhenOptions: document.querySelector("#reduceWhenOptions"),
  raisePositionOptions: document.querySelector("#raisePositionOptions"),
  lowerPositionOptions: document.querySelector("#lowerPositionOptions"),
  invalidWhenOptions: document.querySelector("#invalidWhenOptions"),
  forbiddenOptions: document.querySelector("#forbiddenOptions"),
  generatorForm: document.querySelector("#generatorForm"),
  settingsForm: document.querySelector("#settingsForm"),
  backupForm: document.querySelector("#backupForm"),
  restoreForm: document.querySelector("#restoreForm"),
  backupSelect: document.querySelector("#backupSelect"),
  dataSourceForm: document.querySelector("#dataSourceForm"),
  capabilityForm: document.querySelector("#capabilityForm"),
  dataSyncForm: document.querySelector("#dataSyncForm"),
  importForm: document.querySelector("#importForm"),
  financialReportForm: document.querySelector("#financialReportForm"),
  evidenceForm: document.querySelector("#evidenceForm"),
  evidenceFilterForm: document.querySelector("#evidenceFilterForm"),
  evidenceSymbol: document.querySelector("#evidenceSymbol"),
  evidenceFilterSymbol: document.querySelector("#evidenceFilterSymbol"),
  reviewSnapshotForm: document.querySelector("#reviewSnapshotForm"),
  reviewCompareForm: document.querySelector("#reviewCompareForm"),
  decisionForm: document.querySelector("#decisionForm"),
  profileForm: document.querySelector("#profileForm"),
  styleAllocationHint: document.querySelector("#styleAllocationHint"),
  positionForm: document.querySelector("#positionForm"),
  decisionSymbol: document.querySelector("#decisionSymbol"),
  decisionEvidenceOptions: document.querySelector("#decisionEvidenceOptions"),
  score: document.querySelector("#score"),
  decisionCount: document.querySelector("#decisionCount"),
  statusCounts: document.querySelector("#statusCounts"),
  auditResult: document.querySelector("#auditResult"),
  settingsView: document.querySelector("#settingsView"),
  healthView: document.querySelector("#healthView"),
  backupView: document.querySelector("#backupView"),
  dataSourcesView: document.querySelector("#dataSourcesView"),
  dataSourceHint: document.querySelector("#dataSourceHint"),
  importResult: document.querySelector("#importResult"),
  financialReportResult: document.querySelector("#financialReportResult"),
  evidenceView: document.querySelector("#evidenceView"),
  cardsView: document.querySelector("#cardsView"),
  positionsView: document.querySelector("#positionsView"),
  positionGuardView: document.querySelector("#positionGuardView"),
  tradesView: document.querySelector("#tradesView"),
  financialReportsView: document.querySelector("#financialReportsView"),
  copilotView: document.querySelector("#copilotView"),
  violationsView: document.querySelector("#violationsView"),
  reviewView: document.querySelector("#reviewView"),
  reviewCompareView: document.querySelector("#reviewCompareView"),
  reviewSnapshotsView: document.querySelector("#reviewSnapshotsView"),
  reviewReportsView: document.querySelector("#reviewReportsView"),
  historyView: document.querySelector("#historyView"),
  pathBrowser: document.querySelector("#pathBrowser"),
  pathBrowserCurrent: document.querySelector("#pathBrowserCurrent"),
  pathBrowserList: document.querySelector("#pathBrowserList"),
  pathBrowserSelect: document.querySelector("#pathBrowserSelect"),
  systemStatusModal: document.querySelector("#systemStatusModal"),
  systemStatusView: document.querySelector("#systemStatusView"),
  syncLogsModal: document.querySelector("#syncLogsModal"),
  syncLogsView: document.querySelector("#syncLogsView"),
  marketDataModal: document.querySelector("#marketDataModal"),
  marketDataView: document.querySelector("#marketDataView"),
  infoAnalysisModal: document.querySelector("#infoAnalysisModal"),
  infoAnalysisView: document.querySelector("#infoAnalysisView"),
  evidenceModal: document.querySelector("#evidenceModal"),
  behaviorLibraryModal: document.querySelector("#behaviorLibraryModal"),
  behaviorLibraryView: document.querySelector("#behaviorLibraryView"),
  positionGuardModal: document.querySelector("#positionGuardModal"),
  monthlyReviewModal: document.querySelector("#monthlyReviewModal"),
  tradeLedgerModal: document.querySelector("#tradeLedgerModal"),
  copilotModal: document.querySelector("#copilotModal"),
  cardLibraryModal: document.querySelector("#cardLibraryModal"),
  violationLedgerModal: document.querySelector("#violationLedgerModal"),
  decisionHistoryModal: document.querySelector("#decisionHistoryModal"),
};

const BEHAVIOR_WEAKNESSES = [
  ["FOMO (Fear Of Missing Out)", "错失恐惧 / 踏空焦虑", "害怕错过上涨而追高"],
  ["Emotional Averaging Down", "情绪化补仓 / 情绪化摊平", "跌了后不断补仓不认错"],
  ["Panic Selling", "恐慌性卖出", "暴跌后情绪崩溃割肉"],
  ["Revenge Trading", "报复性交易", "亏损后急于翻本乱操作"],
  ["Greed", "贪婪", "永远嫌赚不够"],
  ["Fear", "恐惧", "不敢买、不敢持有"],
  ["Loss Aversion", "损失厌恶", "小赚即跑，大亏死扛"],
  ["Confirmation Bias", "确认偏误", "只看支持自己观点的信息"],
  ["Anchoring Bias", "锚定效应", "被历史价格锚定"],
  ["Overconfidence Bias", "过度自信", "连续盈利后膨胀"],
  ["Recency Bias", "近因偏差", "用近期走势外推未来"],
  ["Hindsight Bias", "事后偏差", "事后觉得“一切早知道”"],
  ["Survivorship Bias", "幸存者偏差", "只看成功案例"],
  ["Availability Bias", "可得性偏差", "被最容易获取的信息影响"],
  ["Narrative Bias", "叙事偏差", "沉迷宏大故事"],
  ["Halo Effect", "光环效应", "因喜欢公司/创始人忽视风险"],
  ["Authority Bias", "权威偏差", "迷信大V或机构"],
  ["Herd Mentality", "羊群效应", "跟风交易"],
  ["Action Bias", "行动偏执", "无法空仓、无法等待"],
  ["Overtrading", "过度交易", "高频操作"],
  ["Position Addiction", "仓位依赖", "满仓才安心"],
  ["Sunk Cost Fallacy", "沉没成本谬误", "因亏太多而不愿卖"],
  ["Disposition Effect", "处置效应", "赢的太早卖，亏的长期拿"],
  ["Lottery Bias", "彩票偏好", "迷恋暴富股、妖股"],
  ["Martingale Thinking", "马丁格尔思维", "越亏越加倍"],
  ["Chasing Strength", "追涨成瘾", "看见强势就追"],
  ["Selling Winners Too Early", "提前卖飞", "龙头拿不住"],
  ["Refusing To Rotate", "拒绝切换主线", "死守旧逻辑"],
  ["Theme Addiction", "赛道执念", "长期沉迷单一赛道"],
  ["Top Calling Addiction", "猜顶执念", "总想抄顶逃顶"],
  ["Value Trap Blindness", "价值陷阱失明", "低PE就觉得便宜"],
  ["Quality Illusion", "核心资产幻觉", "认为好公司永远不贵"],
  ["Permanent Bull Thesis", "永久牛市逻辑", "认为行业永远增长"],
  ["Dividend Obsession", "分红执念", "只看高股息"],
  ["Short-termism", "短视化", "过度关注短期波动"],
  ["Leverage Addiction", "杠杆成瘾", "习惯融资加杠杆"],
  ["Benchmark Envy", "基准嫉妒", "总和别人收益比较"],
  ["Information Addiction", "信息成瘾", "天天刷消息"],
  ["Prediction Addiction", "预测执念", "痴迷预测指数涨跌"],
  ["Complexity Bias", "复杂性偏好", "误以为复杂=高级"],
  ["Control Illusion", "控制幻觉", "误以为自己能控制市场"],
  ["Ego Investing", "自尊型投资", "不愿承认错误"],
  ["Bagholder Mentality", "套牢者思维", "永远等待回本"],
  ["Diamond Hands Delusion", "钻石手幻觉", "把死扛包装成信仰"],
  ["Doom Bias", "灾难偏见", "永远看空市场"],
  ["Euphoria Bias", "狂热偏见", "牛市后期极度乐观"],
  ["Home Bias", "本土偏好", "只投资熟悉地区"],
  ["Familiarity Bias", "熟悉偏好", "熟悉公司就觉得安全"],
  ["Endowment Effect", "禀赋效应", "持有后高估其价值"],
  ["Cognitive Dissonance", "认知失调", "用理由合理化错误"],
  ["Thesis Drift", "逻辑漂移", "买入逻辑不断变化"],
  ["Signal Confusion", "信号混乱", "短线长线逻辑混用"],
  ["Exit Paralysis", "离场瘫痪", "不知道什么时候卖"],
  ["Entry Impulsiveness", "冲动建仓", "没计划直接买入"],
  ["Volatility Intolerance", "波动不耐受", "扛不住正常波动"],
  ["Patience Deficit", "耐心缺失", "持有周期过短"],
  ["Conviction Fragility", "信念脆弱", "一跌就怀疑自己"],
  ["Alpha Illusion", "Alpha幻觉", "把β行情当自己能力"],
  ["Narrative Overfitting", "叙事过拟合", "用故事解释一切"],
  ["Strategy Hopping", "策略漂移", "不断换体系"],
  ["Emotional Positioning", "情绪化仓位管理", "仓位由情绪决定"],
  ["Timing Obsession", "择时执念", "痴迷精准抄底逃顶"],
  ["False Diversification", "虚假分散", "看似分散实则同风险"],
  ["Liquidity Neglect", "流动性忽视", "忽略退出难度"],
  ["Tail Risk Neglect", "尾部风险忽视", "忽略极端风险"],
  ["Black Swan Denial", "黑天鹅否认", "认为极端风险不会发生"],
];

function preparePageLayout() {
  const layout = document.querySelector(".layout");
  const summary = document.querySelector(".summary");
  if (!layout || !summary) return;

  document.querySelectorAll(".layout > .layer-heading").forEach((node) => node.remove());

  const generatorPanel = els.generatorForm?.closest(".panel");
  const settingsPanel = els.settingsForm?.closest(".panel");
  const dataSourcePanel = els.dataSourceForm?.closest(".panel");
  const infoPanel = els.financialReportForm?.closest(".panel");
  const evidencePanel = els.evidenceForm?.closest(".panel");
  const financialEvidencePanel = els.financialReportsView?.closest(".panel");
  const decisionPanel = els.decisionForm?.closest(".panel");
  const profilePanel = els.profileForm?.closest(".panel");
  const positionPanel = els.positionForm?.closest(".panel");
  const positionGuardPanel = document.querySelector("[data-action='show-position-guard']")?.closest(".panel");
  const positionsPanel = els.positionsView?.closest(".panel");
  const reviewPanel = els.reviewSnapshotForm?.closest(".panel");
  const tradePanel = document.querySelector("[data-action='show-trade-ledger']")?.closest(".panel");
  const copilotPanel = document.querySelector("[data-action='show-copilot']")?.closest(".panel");
  const cardLibraryPanel = document.querySelector("[data-action='show-card-library']")?.closest(".panel");
  const violationPanel = document.querySelector("[data-action='show-violation-ledger']")?.closest(".panel");
  const decisionHistoryPanel = document.querySelector("[data-action='show-decision-history']")?.closest(".panel");

  const layers = [
    {
      key: "rules",
      title: "Rule Layer",
      panels: [generatorPanel, cardLibraryPanel, profilePanel],
    },
    {
      key: "data",
      title: "Data And Information Layer",
      panels: [dataSourcePanel, infoPanel],
    },
    {
      key: "evidence",
      title: "Evidence And Analysis Layer",
      panels: [evidencePanel, financialEvidencePanel, copilotPanel],
    },
    {
      key: "decision",
      title: "Decision Execution Layer",
      panels: [decisionPanel],
    },
    {
      key: "risk",
      title: "Holding And Risk Layer",
      panels: [positionPanel, positionsPanel, positionGuardPanel],
    },
    {
      key: "audit",
      title: "Records And Review Layer",
      panels: [tradePanel, decisionHistoryPanel, violationPanel, reviewPanel],
    },
    {
      key: "support",
      title: "System Support Layer",
      panels: [settingsPanel],
    },
  ];

  let cursor = summary;
  layers.forEach((layer) => {
    const panels = layer.panels.filter(Boolean);
    if (!panels.length) return;
    const block = document.createElement("section");
    block.className = `layer-block layer-${layer.key}`;
    block.innerHTML = `
      <div class="layer-heading">
        <h2>${layer.title}</h2>
      </div>
      <div class="layer-body ${panels.length === 1 ? "single-panel" : ""}"></div>
    `;
    const body = block.querySelector(".layer-body");
    panels.forEach((panel) => {
      panel.classList.remove("grid-left-span", "grid-right", "compact-panel");
      body.appendChild(panel);
    });
    cursor.after(block);
    cursor = block;
  });

  document.querySelectorAll(".layout > .grid").forEach((node) => {
    if (!node.querySelector(".panel")) node.remove();
  });

  if (els.importResult && els.dataSourcesView) {
    els.dataSourcesView.before(els.importResult);
    els.importResult.textContent = "No sync preview yet.";
  }
}

preparePageLayout();

const I18N = {
  zh: {
    "Generate, enforce, audit, and review personal investment discipline.": "个人投资纪律生成、执行、审计与复盘。",
    "Load Demo": "载入示例",
    "Refresh": "刷新",
    "Discipline Score": "纪律评分",
    "Decision Checks": "审查次数",
    "Monthly Status": "本月状态",
    "Rule Layer": "规则层",
    "Define discipline boundaries before the system audits decisions.": "先定义纪律边界，再让系统执行决策审查。",
    "Data And Information Layer": "数据与信息层",
    "Manage QMT, TuShare, AkShare, and local data inputs.": "管理 QMT、TuShare、AkShare 和本地数据入口。",
    "Evidence And Analysis Layer": "证据与分析层",
    "Turn reports, research, news, and notes into traceable evidence.": "把财报、研报、新闻和手动记录转化为可追溯证据。",
    "Decision Execution Layer": "决策执行层",
    "Run pre-trade audits, reference evidence, and use the discipline copilot.": "集中处理交易前审查、证据引用和纪律副驾驶。",
    "Holding And Risk Layer": "持仓与风控层",
    "Review profile constraints, holdings, guardrails, and exposure together.": "把画像约束、持仓、仓位护栏和风险暴露放在同一层查看。",
    "Records And Review Layer": "记录与复盘层",
    "Archive trades, decision history, violations, and monthly reviews.": "统一归档交易流水、决策历史、违规台账和月度复盘。",
    "System Support Layer": "系统支撑层",
    "Configure database mode, AI settings, backup, restore, and system status.": "配置数据库模式、AI、备份恢复和系统状态。",
    "Settings": "设置",
    "Storage and guardrails": "存储与护栏",
    "Storage Mode": "存储模式",
    "SQLite Local Database": "SQLite 本地数据库",
    "JSON Legacy Export": "JSON 兼容导出",
    "PostgreSQL Optional": "PostgreSQL 可选",
    "Strict discipline mode": "严格纪律模式",
    "Enable optional AI layer": "启用可选 AI 层",
    "Save Settings": "保存设置",
    "Create Local Backup": "创建本地备份",
    "Backup Archives": "备份归档",
    "No backup archive yet.": "尚未创建备份。",
    "Restore": "恢复",
    "Data Health": "数据健康",
    "Health Checks": "健康检查",
    "Data Source Center": "数据源中心",
    "Provider and capability mapping": "Provider 与能力映射",
    "View Market Data": "查看行情数据",
    "Market Data": "行情数据",
    "Market Data Summary": "行情数据汇总",
    "Recent Market Records": "最近行情记录",
    "No market data saved yet.": "尚未保存行情数据。",
    "Market Records": "行情记录",
    "Position Price Updates": "持仓价格更新",
    "Data Type": "数据类型",
    "First": "最早",
    "Latest": "最新",
    "Top Symbols": "主要标的",
    "Provider": "Provider",
    "Manual": "手动",
    "Provider Name": "Provider 名称",
    "Priority": "优先级",
    "Local Path / API Base": "本地路径 / API Base",
    "Enabled": "启用",
    "Save Provider": "保存 Provider",
    "Capability": "数据能力",
    "Price Daily": "日线价格",
    "Volume": "成交量",
    "Financial Metrics": "财务指标",
    "Fallback Provider": "备用 Provider",
    "Save Mapping": "保存映射",
    "Discipline Card Generator": "纪律卡生成器",
    "Six-question wizard": "六问向导",
    "Template": "模板",
    "Symbol": "标的代码",
    "Name": "名称",
    "Sector / Theme": "行业 / 主题",
    "Max Position %": "最大仓位 %",
    "Review Cycle": "复盘周期",
    "1. Why do I buy?": "1. 我为什么买？",
    "2. How much can I buy at most?": "2. 我最多买多少？",
    "3. At what condition should I not buy?": "3. 什么情况下不买？",
    "4. When can I add?": "4. 什么情况下加仓？",
    "5. When must I reduce?": "5. 什么情况下减仓？",
    "6. What proves I was wrong?": "6. 什么情况说明我错了？",
    "Forbidden behaviors": "禁止行为",
    "Generate And Save Card": "生成并保存纪律卡",
    "Decision Gate": "决策闸门",
    "Pre-trade audit": "交易前审查",
    "Action": "操作",
    "Buy": "买入",
    "Add": "加仓",
    "Reduce": "减仓",
    "Sell": "清仓",
    "Amount": "金额",
    "Emotion": "情绪",
    "Calm": "平静",
    "Anxious": "焦虑",
    "Fearful": "恐惧",
    "Greedy": "贪婪",
    "Revenge": "报复交易",
    "Reason": "理由",
    "Evidence, one per line": "新增证据，每行一条",
    "Before earnings": "财报前",
    "Thesis changed": "投资逻辑变化",
    "Auto-calculate position before and after action": "自动计算操作前后仓位",
    "Run Audit": "提交审查",
    "No audit submitted yet.": "尚未提交审查。",
    "Data Import": "数据导入",
    "CSV / Excel adapter": "CSV / Excel 适配器",
    "Import Type": "导入类型",
    "Positions": "持仓",
    "Trades": "交易",
    "Local File Path": "本地文件路径",
    "Import File": "导入文件",
    "Preview Import File": "预检导入文件",
    "Preview Sync From Mapped Provider": "预检映射数据源同步",
    "Confirm Import": "确认导入",
    "Confirm Sync": "确认同步",
    "No import yet.": "尚未导入。",
    "Trade Ledger": "交易流水",
    "Imported trades": "已导入交易",
    "Trade Reconciliation": "交易归集",
    "Cash Flow": "现金流",
    "Realized PnL": "已实现盈亏",
    "Unrealized PnL": "未实现盈亏",
    "Open Positions": "开放持仓",
    "Fees": "费用",
    "No reconciliation warning.": "暂无归集警告。",
    "Financial Report Agent": "财报摘要助手",
    "Evidence summary only": "仅生成证据摘要",
    "Period": "周期",
    "Local Report Path": "本地财报路径",
    "Or Paste Report Text": "或粘贴财报文本",
    "Summarize Evidence": "生成证据摘要",
    "No report summarized yet.": "尚未生成财报摘要。",
    "Financial Evidence": "财报证据",
    "Saved summaries": "已保存摘要",
    "Investor Profile": "投资者画像",
  "Personal constraints": "个人约束",
  "Style": "风格",
  "Value Style %": "价值风格 %",
  "Growth Style %": "成长风格 %",
  "Cycle Style %": "周期风格 %",
  "Dividend Style %": "红利风格 %",
  "Cash / Defensive %": "现金 / 防守 %",
  "Style allocation total": "风格暴露合计",
  "Remaining unallocated": "未分配",
  "Style allocation total cannot exceed 100%.": "风格暴露合计不能超过 100%。",
  "Max Single Position %": "单标的上限 %",
    "Max Sector Position %": "行业上限 %",
    "Max Drawdown %": "最大回撤 %",
    "Allow pre-earnings add": "允许财报前加仓",
    "Behavior weaknesses": "行为弱点",
    "Behavior Weakness Library": "行为弱点词库",
    "Core manifestation": "核心表现",
    "Insert Weakness": "填入",
    "Save Profile": "保存画像",
    "Position Book": "持仓管理",
    "Manual holdings": "手动持仓",
    "Asset Type": "资产类型",
    "stock": "股票",
    "etf": "ETF",
    "fund": "基金",
    "bond": "债券",
    "cash": "现金",
    "Market": "市场",
    "Sector": "行业",
    "Theme": "主题",
    "Currency": "币种",
    "Quantity": "数量",
    "Cost Price": "成本价",
    "Current Price": "当前价",
    "Save Position": "保存持仓",
    "Position Guard": "仓位治理",
    "Exposure monitor": "暴露监控",
    "Monthly Review": "月度复盘",
    "Review engine": "复盘引擎",
    "Save Review Snapshot": "保存复盘快照",
    "Saved Review Snapshots": "已保存的复盘快照",
    "No review snapshot saved.": "尚未保存复盘快照。",
    "Snapshot": "快照",
    "Created": "创建时间",
    "Snapshot Drill-down": "快照明细",
    "Referenced Evidence": "引用证据",
    "Export Markdown": "导出 Markdown",
    "Report exported": "报告已导出",
    "Copilot": "副驾驶",
    "Discipline-only assistant": "仅限纪律一致性助手",
    "Discipline Card Library": "纪律卡库",
    "Generated and manual cards": "生成和手动纪律卡",
    "Current holdings": "当前持仓",
    "Violation Ledger": "违规账本",
    "Audit trail": "审计链路",
    "Decision History": "审查历史",
    "Recent checks": "最近审查",
  },
};

const EN_TEXT = new WeakMap();

const CN_STOCKS = {
  "300750": { name: "宁德时代", sector: "新能源" },
  "300308": { name: "中际旭创", sector: "通信设备" },
  "600519": { name: "贵州茅台", sector: "食品饮料" },
  "000001": { name: "平安银行", sector: "银行" },
  "000333": { name: "美的集团", sector: "家用电器" },
  "002594": { name: "比亚迪", sector: "汽车" },
  "601318": { name: "中国平安", sector: "非银金融" },
  "600036": { name: "招商银行", sector: "银行" },
  "300059": { name: "东方财富", sector: "证券" },
  "002475": { name: "立讯精密", sector: "电子" },
  "688981": { name: "中芯国际", sector: "半导体" },
  "603501": { name: "韦尔股份", sector: "半导体" },
  "600309": { name: "万华化学", sector: "化工" },
  "688041": { name: "海光信息", sector: "半导体" },
  "09988": { name: "阿里巴巴-W", sector: "互联网" },
  "00700": { name: "腾讯控股", sector: "互联网" },
  "601138": { name: "工业富联", sector: "电子制造" },
  "002342": { name: "巨力索具", sector: "机械设备" },
  "601899": { name: "紫金矿业", sector: "有色金属" },
  "002371": { name: "北方华创", sector: "半导体设备" },
  "688256": { name: "寒武纪", sector: "人工智能芯片" },
  "600900": { name: "长江电力", sector: "公用事业" },
  "600030": { name: "中信证券", sector: "证券" },
  "300124": { name: "汇川技术", sector: "自动化设备" },
  "603259": { name: "药明康德", sector: "医药服务" },
  "002415": { name: "海康威视", sector: "安防设备" },
  "601012": { name: "隆基绿能", sector: "光伏" },
  "01810": { name: "小米集团-W", sector: "消费电子" },
  "00981": { name: "中芯国际", sector: "半导体" },
};

Object.assign(I18N.zh, {
  "Generate, enforce, audit, and review personal investment discipline.": "\u751f\u6210\u3001\u6267\u884c\u3001\u5ba1\u8ba1\u548c\u590d\u76d8\u4e2a\u4eba\u6295\u8d44\u7eaa\u5f8b\u3002",
  "Storage and guardrails": "\u5b58\u50a8\u4e0e\u62a4\u680f",
  "Local Path / API Base": "\u672c\u5730\u8def\u5f84 / API \u5730\u5740",
  "Browse": "\u6d4f\u89c8",
  "Path Browser": "\u8def\u5f84\u6d4f\u89c8\u5668",
  "Close": "\u5173\u95ed",
  "Up": "\u4e0a\u4e00\u7ea7",
  "Select Current Path": "\u9009\u62e9\u5f53\u524d\u8def\u5f84",
  "Select This Folder": "\u9009\u62e9\u6b64\u6587\u4ef6\u5939",
  "Click a file to select it.": "\u70b9\u51fb\u6587\u4ef6\u5373\u53ef\u9009\u4e2d\u3002",
  "Folder": "\u6587\u4ef6\u5939",
  "File": "\u6587\u4ef6",
  "No entries.": "\u6ca1\u6709\u53ef\u663e\u793a\u7684\u9879\u3002",
  "When can I raise the position limit?": "\u4ec0\u4e48\u60c5\u51b5\u4e0b\u53ef\u4ee5\u63d0\u9ad8\u4ed3\u4f4d\u4e0a\u9650\uff1f",
  "When must I lower the position limit?": "\u4ec0\u4e48\u60c5\u51b5\u4e0b\u5fc5\u987b\u964d\u4f4e\u4ed3\u4f4d\u4e0a\u9650\uff1f",
  "6. When can I raise the position limit?": "6. \u4ec0\u4e48\u60c5\u51b5\u4e0b\u53ef\u4ee5\u63d0\u9ad8\u4ed3\u4f4d\u4e0a\u9650\uff1f",
  "7. When must I lower the position limit?": "7. \u4ec0\u4e48\u60c5\u51b5\u4e0b\u5fc5\u987b\u964d\u4f4e\u4ed3\u4f4d\u4e0a\u9650\uff1f",
  "8. What proves I was wrong?": "8. \u4ec0\u4e48\u60c5\u51b5\u8bc1\u660e\u6211\u9519\u4e86\uff1f",
  "Status Counts": "\u72b6\u6001\u7edf\u8ba1",
  "Violation Types": "\u8fdd\u89c4\u7c7b\u578b",
  "Rule Results": "\u89c4\u5219\u660e\u7ec6",
  "Referenced Evidence": "\u5f15\u7528\u8bc1\u636e",
  "Market value": "\u5e02\u503c",
  "Total market value": "\u603b\u5e02\u503c",
  "No exposure warning.": "\u6682\u65e0\u66b4\u9732\u9884\u8b66\u3002",
  "View Position Guard": "查看仓位护栏",
  "View Monthly Review": "查看月度复盘",
  "View Trade Ledger": "查看交易流水",
  "View Copilot": "查看副驾驶",
  "View Discipline Cards": "查看纪律卡",
  "View Violation Ledger": "查看违规台账",
  "View Decision History": "查看决策历史",
  "Copilot summarizes discipline risks, thesis drift, card draft suggestions, and next review actions. It does not make buy/sell recommendations.": "副驾驶用于汇总纪律风险、投资逻辑漂移、纪律卡草稿建议和下一步复盘动作；它不提供买入或卖出建议。",
  "No discipline issue found.": "\u672a\u53d1\u73b0\u7eaa\u5f8b\u95ee\u9898\u3002",
  "No exported report yet.": "\u5c1a\u672a\u5bfc\u51fa\u62a5\u544a\u3002",
  "Report Library": "\u62a5\u544a\u5e93",
  "Regenerate": "\u91cd\u65b0\u751f\u6210",
  "Snapshot Comparison": "\u5feb\u7167\u5bf9\u6bd4",
  "Trend": "\u8d8b\u52bf",
  "Repeated Symbols": "\u91cd\u590d\u95ee\u9898\u6807\u7684",
  "Rule Suggestion Changes": "\u89c4\u5219\u5efa\u8bae\u53d8\u5316",
  "Raise limit": "\u63d0\u9ad8\u4e0a\u9650",
  "Lower limit": "\u964d\u4f4e\u4e0a\u9650",
});

Object.assign(I18N.zh, {
  "Load Demo": "载入示例",
  "Refresh": "刷新",
  "Discipline Score": "纪律评分",
  "Decision Checks": "决策检查",
  "Monthly Status": "本月状态",
  "Settings": "设置",
  "Database Mode": "数据库模式",
  "Storage Mode": "存储模式",
  "SQLite Local Database": "SQLite 本地数据库",
  "JSON Legacy Export": "JSON 兼容导出",
  "PostgreSQL Optional": "PostgreSQL 可选",
  "Violation Handling": "违规处理方式",
  "Block invalid decisions": "拦截无效决策",
  "Warn only": "仅提示风险",
  "Strict discipline mode": "违规拦截",
  "Enable optional AI layer": "启用可选 AI 层",
  "Enable AI review analysis": "启用 AI 复盘分析",
  "AI API Token": "AI API Token",
  "AI API URL": "AI API URL",
  "AI Model": "AI 模型",
  "AI review analysis": "AI 复盘分析",
  "Save Settings": "保存设置",
  "Create Local Backup": "创建本地备份",
  "Restore From Backup": "从备份恢复",
  "Restore Selected Backup": "恢复选中的备份",
  "View System Status": "查看系统状态",
  "System Status": "系统状态",
  "View Sync Logs": "查看同步日志",
  "Sync Logs": "同步日志",
  "View Data Source Status": "查看数据源状态",
  "Data Source Status": "数据源状态",
  "Backup Archives": "备份归档",
  "No backup archive yet.": "尚无备份归档。",
  "Restore": "恢复",
  "Data Health": "数据健康",
  "Health Checks": "健康检查",
  "Data Source Center": "数据源中心",
  "Data Source": "数据源",
  "Choose one source, then preview and sync.": "选择一个数据来源，然后预览并同步。",
  "Save Data Source": "保存数据源",
  "Data Type": "数据类型",
  "Preview Sync": "预览同步",
  "Available Data": "可用数据",
  "Local Path": "本地路径",
  "Daily K": "日K",
  "5min K": "5分钟K",
  "Provider and capability mapping": "数据源与能力映射",
  "Provider": "数据源类型",
  "Provider Name": "数据源名称",
  "Manual": "手动",
  "CSV": "CSV",
  "Excel": "Excel",
  "QMT": "QMT",
  "TuShare": "TuShare",
  "AkShare": "AkShare",
  "Priority": "优先级",
  "API Token": "API 令牌",
  "API Base URL": "API 基础地址",
  "Enabled": "启用",
  "Save Provider": "保存数据源",
  "Capability": "数据能力",
  "Positions": "持仓",
  "Trades": "交易",
  "Price Daily": "日线价格",
  "Volume": "成交量",
  "Financial Metrics": "财务指标",
  "Fallback Provider": "备用数据源",
  "Save Mapping": "保存映射",
  "Sync Capability": "同步能力",
  "Preview Sync From Mapped Provider": "预览映射数据源同步",
  "Value": "价值",
  "Growth": "成长",
  "Cyclical": "周期",
  "Trend": "趋势",
  "ETF": "ETF",
  "Discipline Card Generator": "纪律卡生成器",
  "Six-question wizard": "八问式生成向导",
  "Template": "模板",
  "Symbol": "标的代码",
  "Name": "名称",
  "Sector / Theme": "行业 / 主题",
  "Max Position %": "最大仓位 %",
  "Review Cycle": "复盘周期",
  "1. Why do I buy?": "1. 我为什么买？",
  "2. How much can I buy at most?": "2. 我最多可以买多少？",
  "3. At what condition should I not buy?": "3. 什么情况下不买？",
  "4. When can I add?": "4. 什么情况下可以加仓？",
  "5. When must I reduce?": "5. 什么情况下必须减仓？",
  "Forbidden behaviors": "禁止行为",
  "Generate And Save Card": "生成并保存纪律卡",
  "Value Discipline": "价值纪律",
  "Growth Discipline": "成长纪律",
  "Cyclical Discipline": "周期纪律",
  "Trend Discipline": "趋势纪律",
  "ETF Allocation": "ETF 配置",
  "Decision Gate": "决策闸门",
  "Pre-trade audit": "交易前审查",
  "Action": "操作",
  "Buy": "买入",
  "Add": "加仓",
  "Reduce": "减仓",
  "Sell": "卖出",
  "Amount": "金额",
  "Emotion": "情绪",
  "Calm": "冷静",
  "Anxious": "焦虑",
  "Fearful": "恐惧",
  "Greedy": "贪婪",
  "FOMO": "错失恐惧",
  "Revenge": "报复交易",
  "Reason": "理由",
  "Evidence, one per line": "证据，每行一条",
  "Before earnings": "财报前",
  "Allow pre-earnings add": "允许财报前加仓",
  "Thesis changed": "投资逻辑变化",
  "Auto-calculate position before and after action": "自动计算操作前后仓位",
  "Run Audit": "运行审查",
  "No audit submitted yet.": "尚未提交审查。",
  "Data Import": "数据导入",
  "CSV / Excel adapter": "CSV / Excel 适配器",
  "Import Type": "导入类型",
  "Local File Path": "本地文件路径",
  "Preview Import File": "预览导入文件",
  "No import yet.": "尚无导入记录。",
  "No sync preview yet.": "尚无同步预览。",
  "Trade Ledger": "交易流水",
  "Imported trades": "已导入交易",
  "Financial Report Agent": "财报证据助手",
  "Information Analysis Center": "信息解读中心",
  "Reports, research, news, and events": "财报、研报、新闻与事件",
  "Material Type": "材料类型",
  "Financial Report": "财报",
  "Research Report": "机构研报",
  "Announcement / News": "公告 / 新闻",
  "Market Event": "市场事件",
  "Local PDF / Document Path": "本地 PDF / 文档路径",
  "AI online search": "AI 在线搜索",
  "Or Paste Material Text": "或粘贴材料文本",
  "Analyze Information": "解读信息",
  "View Analysis Results": "查看解读结果",
  "Information Analysis Results": "信息解读结果",
  "Card Suggestions": "纪律卡建议",
  "Analysis Mode": "解读模式",
  "AI analysis": "AI 解读",
  "Local rules": "本地规则",
  "AI failed, local rules used": "AI 调用失败，已使用本地规则",
  "Key Insights": "核心结论",
  "Positive Factors": "利好因素",
  "Negative Factors": "利空因素",
  "Risk Flags": "风险提示",
  "Discipline Suggestions": "纪律建议",
  "Apply to Discipline Card Draft": "应用到纪律卡草稿",
  "Evidence summary only": "仅生成证据摘要",
  "Period": "期间",
  "Local Report Path": "本地报告路径",
  "Or Paste Report Text": "或粘贴报告文本",
  "Summarize Evidence": "生成证据摘要",
  "Financial Result": "财报结果",
  "No report summarized yet.": "尚无报告摘要。",
  "Financial Evidence": "财报证据",
  "Saved summaries": "已保存摘要",
  "Investor Profile": "投资者画像",
  "Personal constraints": "个人约束",
  "Style": "风格",
  "Value Style %": "价值风格 %",
  "Growth Style %": "成长风格 %",
  "Cycle Style %": "周期风格 %",
  "Dividend Style %": "红利风格 %",
  "Cash / Defensive %": "现金 / 防守 %",
  "Style allocation total": "风格暴露合计",
  "Remaining unallocated": "未分配",
  "Style allocation total cannot exceed 100%.": "风格暴露合计不能超过 100%。",
  "Max Single Position %": "单一标的上限 %",
  "Max Sector Position %": "行业上限 %",
  "Max Drawdown %": "最大回撤 %",
  "Behavior weaknesses": "行为弱点",
  "Behavior Weakness Library": "行为弱点词库",
  "Core manifestation": "核心表现",
  "Insert Weakness": "填入",
  "Save Profile": "保存画像",
  "Position Book": "持仓簿",
  "Manual holdings": "手动持仓",
  "Asset Type": "资产类型",
  "stock": "股票",
  "etf": "ETF",
  "fund": "基金",
  "bond": "债券",
  "cash": "现金",
  "Market": "市场",
  "Sector": "行业",
  "Theme": "主题",
  "Currency": "币种",
  "Quantity": "数量",
  "Cost Price": "成本价",
  "Current Price": "当前价",
  "Save Position": "保存持仓",
  "Position Guard": "仓位护栏",
  "Exposure monitor": "暴露监控",
  "Monthly Review": "月度复盘",
  "Review engine": "复盘引擎",
  "Save Review Snapshot": "保存复盘快照",
  "Saved Review Snapshots": "已保存复盘快照",
  "No review snapshot saved.": "尚未保存复盘快照。",
  "Snapshot": "快照",
  "Created": "创建时间",
  "Snapshot Drill-down": "快照明细",
  "Export Markdown": "导出 Markdown",
  "Copilot": "副驾驶",
  "Discipline-only assistant": "仅限纪律一致性的助手",
  "Discipline Card Library": "纪律卡库",
  "Generated and manual cards": "生成卡与手工卡",
  "Current holdings": "当前持仓",
  "Violation Ledger": "违规台账",
  "Audit trail": "审计轨迹",
  "Decision History": "决策历史",
  "Recent checks": "最近检查",
  "Evidence Engine": "证据引擎",
  "Manual and extracted evidence": "手工与提取证据",
  "Filter Symbol": "筛选代码",
  "All Symbols": "全部标的",
  "Filter Type": "筛选类型",
  "All Types": "全部类型",
  "Evidence Type": "证据类型",
  "Title": "标题",
  "Content": "内容",
  "Source": "来源",
  "Source Date": "来源日期",
  "Save Evidence": "保存证据",
  "Filter Evidence": "筛选证据",
  "Evidence Items": "证据项",
  "Only symbols with saved discipline cards appear here.": "这里只显示已经保存纪律卡的标的；请先生成纪律卡。",
  "Evidence can be manual, extracted by Information Analysis, or synced from data sources.": "证据可以来自手动输入、信息解读中心提取，或数据源同步。",
  "View Evidence Library": "查看证据库",
  "Evidence Library": "证据库",
  "Announcement Event": "公告事件",
  "Price Condition": "价格条件",
  "Volume Signal": "成交量信号",
  "User Note": "用户笔记",
  "financial_result": "财报结果",
  "price_condition": "价格条件",
  "volume_signal": "成交量信号",
  "announcement_event": "公告事件",
  "user_note": "用户笔记",
  "research_report": "机构研报",
  "market_event": "市场事件",
  "buy": "买入",
  "add": "加仓",
  "reduce": "减仓",
  "sell": "卖出",
  "calm": "冷静",
  "anxious": "焦虑",
  "fearful": "恐惧",
  "greedy": "贪婪",
  "revenge": "报复交易",
  "fomo": "错失恐惧",
  "SAMPLE": "示例标的",
  "Sample Asset": "示例资产",
  "Backup Archives": "备份归档",
  "No capability mapping yet.": "尚无能力映射。",
  "No data source configured yet.": "尚未配置数据源。",
  "No sync log yet.": "尚无同步日志。",
  "No trades imported.": "尚无导入交易。",
  "No financial report summary saved.": "尚无财报摘要。",
  "No evidence item saved.": "尚无证据项。",
  "No position yet.": "尚无持仓。",
  "No violation recorded.": "尚无违规记录。",
  "No decision history.": "尚无决策历史。",
  "No copilot output yet.": "尚无副驾驶输出。",
  "No discipline card yet. Generate one above.": "尚无纪律卡，请先在上方生成。",
  "Need at least two snapshots to compare.": "至少需要两个快照才能对比。",
  "Card Draft Suggestions": "纪律卡草稿建议",
  "Monthly Review Draft": "月度复盘草稿",
  "Score Breakdown": "评分拆解",
  "Rule Revision Suggestions": "规则修订建议",
  "Next-month forbidden behaviors": "下月禁止行为",
  "Next Actions": "下一步行动",
  "Compliance Boundary": "合规边界",
  "Thesis Drift Alerts": "逻辑漂移提醒",
  "Edit As Draft": "作为草稿编辑",
  "Delete": "删除",
  "Review": "复盘",
  "Mark Resolved": "标记已解决",
  "None": "无",
  "Confirm Sync": "确认同步",
  "Confirm Import": "确认导入",
  "Add": "加仓",
  "Raise limit": "提高上限",
  "Lower limit": "降低上限",
  "Folder": "文件夹",
  "File": "文件",
  "No entries.": "没有可显示的项目。",
  "Edit": "编辑",
  "Score": "评分",
  "decisions": "决策",
  "enabled": "启用",
  "strict_mode": "严格模式",
  "ai_enabled": "AI 层",
  "allow_pre_earnings_add": "允许财报前加仓",
  "auto_position": "自动仓位计算",
  "is_before_earnings": "财报前",
  "thesis_changed": "逻辑变化",
  "No errors": "无错误",
  "PASS": "通过",
  "WARN": "警告",
  "ERROR": "错误",
  "HARD_BLOCK": "硬性拦截",
  "REVIEW_REQUIRED": "需要复盘",
  "EVIDENCE_REQUIRED": "需要证据",
  "max": "上限",
  "qty": "数量",
  "price": "价格",
  "fee": "费用",
  "PnL": "盈亏",

  "Valuation is below the long-term discipline range.": "估值低于长期纪律区间。",
  "Cash flow and profitability remain stable.": "现金流和盈利能力保持稳定。",
  "Dividend or shareholder return remains reliable.": "分红或股东回报仍然可靠。",
  "Valuation is outside the pre-defined discipline range.": "估值不在预设纪律区间内。",
  "Safety margin is not clear.": "安全边际不清晰。",
  "Fundamentals remain stable or improve.": "基本面保持稳定或改善。",
  "New evidence supports the original thesis.": "新证据支持原始投资逻辑。",
  "The original safety margin no longer exists.": "原有安全边际不复存在。",
  "Fundamentals weaken materially.": "基本面明显走弱。",
  "Valuation remains inside the discipline range.": "估值仍在纪律区间内。",
  "Core profitability or cash flow deteriorates for two review periods.": "核心盈利能力或现金流连续两个复盘期恶化。",
  "Do not buy only because the price has fallen.": "不要仅因价格下跌而买入。",
  "Do not add without new fundamental evidence.": "没有新的基本面证据时不得加仓。",
  "Revenue growth is accelerating.": "收入增长正在加速。",
  "Profit growth confirms operating leverage.": "利润增长验证经营杠杆。",
  "New product, order, or user data supports the second curve.": "新产品、订单或用户数据支持第二增长曲线。",
  "Growth rate no longer matches valuation.": "增长率已无法匹配估值。",
  "The second growth curve is unproven.": "第二增长曲线尚未被证实。",
  "Revenue or profit growth confirms the thesis.": "收入或利润增长验证投资逻辑。",
  "New product, order, or user data improves visibility.": "新产品、订单或用户数据提升可见度。",
  "Growth slows below the discipline threshold.": "增长放缓并低于纪律阈值。",
  "Position or theme exposure becomes concentrated.": "个股或主题暴露变得集中。",
  "Growth is confirmed by both revenue and profit quality.": "收入与利润质量共同验证增长。",
  "The second curve becomes measurable instead of narrative-only.": "第二曲线已从叙事变成可度量事实。",
  "Growth remains strong but valuation/risk becomes asymmetric.": "增长仍强，但估值和风险收益开始不对称。",
  "Customer, order, or margin evidence deteriorates.": "客户、订单或毛利率证据转弱。",
  "Core growth indicators miss expectations for two periods.": "核心成长指标连续两个周期低于预期。",
  "Management guidance weakens materially.": "管理层指引明显转弱。",
  "Do not chase a hot theme without evidence.": "不要在没有证据时追逐热门主题。",
  "Do not reinterpret a broken growth thesis as a value thesis.": "不要把破裂的成长逻辑重新解释成价值逻辑。",
  "Cycle data is improving from the trough.": "周期数据正在从低谷改善。",
  "Product price or inventory data supports recovery.": "产品价格或库存数据支持复苏。",
  "Supply expansion remains constrained while demand improves.": "需求改善的同时供给扩张仍受约束。",
  "Cycle position is unclear.": "周期位置不清晰。",
  "Industry supply growth weakens the expected recovery.": "行业供给增长削弱预期复苏。",
  "Cycle data improves and confirms the expected direction.": "周期数据改善并确认预期方向。",
  "Cash flow, profit, or order evidence improves materially.": "现金流、利润或订单证据明显改善。",
  "Cycle evidence becomes mixed or late-stage.": "周期证据变得混杂或进入后期。",
  "Position becomes too large for a cyclical asset.": "仓位对于周期资产而言过大。",
  "Inventory, price, and demand data all confirm cycle recovery.": "库存、价格和需求数据共同确认周期复苏。",
  "Capital expenditure discipline remains acceptable.": "资本开支纪律仍可接受。",
  "Inventory or product price data conflicts with the thesis.": "库存或产品价格数据与投资逻辑冲突。",
  "Supply expansion damages the original thesis.": "供给扩张破坏原始逻辑。",
  "Cycle recovery evidence fails to appear.": "周期复苏证据未出现。",
  "Do not average down without updated cycle evidence.": "没有更新后的周期证据时不得摊低成本。",
  "Do not treat cyclical profits as permanently stable.": "不要把周期利润当作永久稳定利润。",
  "Trend strength remains above the pre-defined threshold.": "趋势强度仍高于预设阈值。",
  "Volume confirms participation rather than only narrative heat.": "成交量确认参与度，而不只是叙事热度。",
  "Theme leadership remains intact.": "主题龙头地位仍保持。",
  "Trend strength has already weakened.": "趋势强度已经走弱。",
  "Entry is based only on social heat or price momentum.": "入场仅基于社交热度或价格动量。",
  "Trend strength and volume confirm continuation.": "趋势强度和成交量确认延续。",
  "Trend breaks the pre-defined exit signal.": "趋势触发预设退出信号。",
  "Theme exposure becomes concentrated.": "主题暴露变得集中。",
  "Trend, volume, and leadership all remain intact after review.": "复盘后趋势、成交量和龙头地位仍然完整。",
  "Theme crowding or single-name exposure becomes excessive.": "主题拥挤度或单一标的暴露过高。",
  "The main trend signal fails.": "主要趋势信号失效。",
  "Theme narrative changes without supporting data.": "主题叙事变化但缺少数据支持。",
  "Do not chase FOMO after a sharp rise.": "大涨后不要因错失恐惧追高。",
  "Do not convert a failed trend trade into a long-term thesis.": "不要把失败的趋势交易改口成长线逻辑。",
  "Portfolio allocation remains inside limits.": "组合配置仍在限制内。",
  "Purchase follows the pre-defined batch plan.": "买入遵守预设分批计划。",
  "Risk can still be reduced through a clear exit rule.": "仍可通过清晰退出规则降低风险。",
  "Allocation plan has not been defined.": "尚未定义配置计划。",
  "The purchase breaks the rebalance plan.": "买入破坏再平衡计划。",
  "Purchase follows the batch plan.": "买入遵守分批计划。",
  "Portfolio rebalance requires adding this exposure.": "组合再平衡要求增加该暴露。",
  "Rebalance rule is triggered.": "再平衡规则被触发。",
  "Allocation exceeds target range.": "配置超出目标区间。",
  "Portfolio rebalance plan explicitly raises the target allocation.": "组合再平衡计划明确提高目标配置。",
  "Drawdown has been pre-budgeted and batch rules remain intact.": "回撤已预先预算，分批规则仍然有效。",
  "Portfolio target allocation is lowered.": "组合目标配置被下调。",
  "Correlation with existing holdings becomes too high.": "与现有持仓相关性过高。",
  "Index exposure no longer matches the portfolio objective.": "指数暴露不再匹配组合目标。",
  "Allocation plan requires index exposure.": "配置计划要求指数暴露。",
  "Do not buy only because the index dropped today.": "不要仅因指数当天下跌而买入。",
  "Do not abandon the batch plan during volatility.": "不要在波动中放弃分批计划。"
});

Object.assign(I18N.zh, {
  "Position exceeds the limit.": "仓位超过纪律上限。",
  "Valuation becomes overheated.": "估值变得过热。",
  "Evidence quality weakens or becomes stale.": "证据质量转弱或已经过期。",
  "Volatility or drawdown exceeds the pre-defined tolerance.": "波动或回撤超过预设容忍度。",
  "Product price or inventory data turns against the thesis.": "产品价格或库存数据转向不利于投资逻辑。",
  "Product price or inventory data supports recovery.": "产品价格或库存数据支持复苏。",
  "Trend breaks the pre-defined exit signal.": "趋势触发预设退出信号。",
  "Theme exposure becomes concentrated.": "主题暴露变得集中。",
  "Trend remains but volume participation weakens.": "趋势仍在，但成交量参与度转弱。",
  "Theme crowding or single-name exposure becomes excessive.": "主题拥挤度或单一标的暴露过高。",
  "Trend, volume, and leadership all remain intact after review.": "复盘后趋势、成交量和龙头地位仍然完整。",
  "Risk can still be reduced through a clear exit rule.": "仍可通过清晰退出规则降低风险。",
  "Allocation exceeds target range.": "配置超过目标区间。",
  "Rebalance rule is triggered.": "再平衡规则被触发。",
  "Portfolio target allocation is lowered.": "组合目标配置被下调。",
  "Correlation with existing holdings becomes too high.": "与现有持仓相关性过高。",
  "Portfolio rebalance plan explicitly raises the target allocation.": "组合再平衡计划明确提高目标配置。",
  "Drawdown has been pre-budgeted and batch rules remain intact.": "回撤已预先预算，分批规则仍然有效。",
  "Two consecutive reviews confirm the thesis and risk remains controlled.": "连续两次复盘确认投资逻辑，且风险仍受控。",
  "Cash flow, profit, or order evidence improves materially.": "现金流、利润或订单证据明显改善。",
  "Growth remains strong but valuation/risk becomes asymmetric.": "增长仍强，但估值和风险收益已经不对称。",
  "Customer, order, or margin evidence deteriorates.": "客户、订单或毛利率证据恶化。",
  "Inventory, price, and demand data all confirm cycle recovery.": "库存、价格和需求数据共同确认周期复苏。",
  "Supply expansion remains constrained while demand improves.": "需求改善的同时供给扩张仍受约束。",
  "Cycle evidence becomes mixed or late-stage.": "周期证据变得混杂或进入后期。",
  "Industry supply growth weakens the expected recovery.": "行业供给增长削弱预期复苏。"
});

Object.assign(I18N.zh, {
  "All Types": "全部类型",
  "Announcement Event": "公告事件",
  "Baseline Snapshot": "基准快照",
  "Compare Snapshots": "对比快照",
  "Current holdings": "当前持仓",
  "Filter Evidence": "筛选证据",
  "Filter Symbol": "筛选代码",
  "Filter Type": "筛选类型",
  "Financial Result": "财报结果",
  "Import Type": "导入类型",
  "Manual and extracted evidence": "手工与提取证据",
  "Price Condition": "价格条件",
  "Price has fallen a lot and I want to reduce my average cost.": "价格跌了很多，我想降低平均成本。",
  "Saved summaries": "已保存摘要",
  "Target Snapshot": "目标快照",
  "User Note": "用户笔记",
  "Volume Signal": "成交量信号",
  "English": "英文",
  "Roots": "根目录",
  "ON": "开启",
  "OFF": "关闭",
  "AI": "AI",
  "block": "拦截",
  "warn": "提醒",
  "AI enabled": "AI 已启用",
  "AI disabled": "AI 已禁用",
  "AI on": "AI 开启",
  "AI off": "AI 关闭",
  "AI Audit Runs": "AI 审查运行记录",
  "Final status source": "最终状态来源",
  "Decision ID": "决策 ID",
  "Referenced Evidence": "引用证据",
  "Rule Results": "规则结果",
  "Violations": "违规记录",
  "Fix": "修复建议",
  "Params": "参数",
  "Rows": "行数",
  "valid": "有效",
  "skipped": "跳过",
  "commit": "提交",
  "yes": "是",
  "no": "否",
  "Missing columns": "缺失列",
  "Preview Rows": "预览行",
  "bytes": "字节",
  "files": "文件",
  "disabled": "停用",
  "untested": "未测试",
  "none": "无",
  "manual": "手动",
  "csv": "CSV",
  "excel": "Excel",
  "qmt": "QMT",
  "tushare": "TuShare",
  "akshare": "AkShare",
  "positions": "持仓",
  "trades": "交易",
  "price_daily": "日线价格",
  "price_5min": "5分钟K",
  "volume": "成交量",
  "financial_metrics": "财务指标",
  "import": "导入",
  "sync": "同步",
  "success": "成功",
  "failed": "失败",
  "pending": "待处理",
  "blocked": "已拦截",
  "resolved": "已解决",
  "open": "未解决",
  "pass": "通过",
  "Pass": "通过",
  "PASS": "通过",
  "warn": "警告",
  "Warn": "警告",
  "WARN": "警告",
  "error": "错误",
  "ERROR": "错误",
  "BLOCKED": "已拦截",
  "UNKNOWN": "未知",
  "INFO": "提示",
  "info": "提示",
  "HARD_BLOCK": "硬性拦截",
  "REVIEW_REQUIRED": "需要复盘",
  "EVIDENCE_REQUIRED": "需要证据",
  "general": "通用",
  "storage": "存储",
  "audit": "审计",
  "rules": "规则",
  "violations": "违规",
  "reviews": "复盘",
  "reports": "报告",
  "backups": "备份",
  "data_sources": "数据源",
  "market": "市场",
  "security": "标的",
  "portfolio": "组合",
  "behavior": "行为",
  "Single": "单一标的",
  "Sector": "行业",
  "Theme": "主题",
  "Market": "市场",
  "Currency": "币种",
  "storage_mode": "存储模式",
  "strict_mode": "严格模式",
  "ai_enabled": "AI 层",
  "allow_pre_earnings_add": "允许财报前加仓",
  "auto_position": "自动仓位计算",
  "is_before_earnings": "财报前",
  "thesis_changed": "逻辑变化",
  "pass rate": "通过率",
  "violation weight": "违规权重",
  "persistent": "持续存在",
  "added": "新增",
  "removed": "移除",
  "Added": "新增",
  "Removed": "移除",
  "after": "操作后仓位",
  "weight": "权重",
  "mixed": "混合",
  "improving": "改善",
  "deteriorating": "恶化",
  "flat": "持平",
  "rule_engine": "规则引擎",
  "no snapshot id": "无快照 ID",
  "Storage and guardrails": "存储与护栏",
  "Provider and capability mapping": "数据源与能力映射",
  "SQLite database": "SQLite 数据库",
  "Decision and audit linkage": "决策与审计关联",
  "Rule result linkage": "规则结果关联",
  "Orphan rule results": "孤立规则结果",
  "Violation linkage": "违规关联",
  "Review snapshots": "复盘快照",
  "Report snapshot references": "报告快照引用",
  "Local backup archive": "本地备份归档",
  "Capability mappings": "能力映射",
  "Enabled provider status": "启用数据源状态",
  "Manual source": "手动数据源",
  "No market attribution issue recorded.": "未记录市场归因问题。",
  "No security attribution issue recorded.": "未记录标的归因问题。",
  "No portfolio attribution issue recorded.": "未记录组合归因问题。",
  "No behavior attribution issue recorded.": "未记录行为归因问题。",
  "Review and document the decision.": "复盘并记录该决策。",
  "Request failed": "请求失败"
});

const ZH_MESSAGE_PATTERNS = [
  [/^(.+) financial evidence (\d+)$/, (_, period, index) => `${period} 财报证据 ${index}`],
  [/^(.+) evidence (\d+)$/, (_, period, index) => `${period} 证据 ${index}`],
  [/^(\d+) decisions have no audit record\.$/, "$1 条决策没有审计记录。"],
  [/^(\d+) audited decisions have no rule results\.$/, "$1 条已审计决策没有规则结果。"],
  [/^(\d+) rule result decision ids are missing from decision history\.$/, "$1 条规则结果的决策 ID 不在决策历史中。"],
  [/^(\d+) violation decision ids are missing from decision history\.$/, "$1 条违规记录的决策 ID 不在决策历史中。"],
  [/^(\d+) snapshots, (\d+) without drill-down\.$/, "$1 个快照，其中 $2 个缺少明细。"],
  [/^(\d+) reports, (\d+) reference missing snapshots\.$/, "$1 个报告，其中 $2 个引用了缺失快照。"],
  [/^(\d+) backup archives found\.$/, "找到 $1 个备份归档。"],
  [/^(\d+) enabled mappings point to missing providers\.$/, "$1 个启用映射指向缺失的数据源。"],
  [/^(\d+) enabled providers are blocked or errored\.$/, "$1 个启用数据源处于拦截或错误状态。"],
  [/^data\\disciplineos\.db$/, "data\\disciplineos.db"],
  [/^No (market|security|portfolio|behavior) attribution issue recorded\.$/, (_, bucket) => `未记录${t(bucket)}归因问题。`],
];

function t(text) {
  return state.lang === "zh" ? I18N.zh[text] || text : text;
}

function localizeText(value) {
  if (Array.isArray(value)) return value.map(localizeText);
  const raw = String(value ?? "");
  if (state.lang !== "zh") return raw;
  const exact = t(raw);
  if (exact !== raw) return exact;
  for (const [pattern, replacement] of ZH_MESSAGE_PATTERNS) {
    if (!pattern.test(raw)) continue;
    pattern.lastIndex = 0;
    return raw.replace(pattern, replacement);
  }
  return raw;
}

function localizeTokens(value) {
  if (state.lang !== "zh") return String(value ?? "");
  return String(value ?? "")
    .split(/(\s+|\/|->|:|,|\(|\)|;)/)
    .map((part) => localizeText(part))
    .join("");
}

function badgeText(value) {
  return escapeHtml(localizeText(value || "UNKNOWN"));
}

function localizeList(values, separator = "; ") {
  return (values || []).map(localizeText).map(escapeHtml).join(separator);
}

function applyLanguage() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  els.languageSelect.value = state.lang;
  const zhOption = els.languageSelect.querySelector('option[value="zh"]');
  if (zhOption) zhOption.textContent = "\u4e2d\u6587";
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (["SCRIPT", "STYLE", "TEXTAREA"].includes(parent.tagName)) {
          return NodeFilter.FILTER_REJECT;
        }
        return node.nodeValue.trim()
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      },
    }
  );
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);
  textNodes.forEach((node) => {
    const raw = node.nodeValue;
    const trimmed = raw.trim();
    if (!EN_TEXT.has(node)) EN_TEXT.set(node, trimmed);
    const translated = localizeText(EN_TEXT.get(node));
    node.nodeValue = raw.replace(trimmed, translated);
  });
  document.querySelectorAll("[placeholder], [aria-label], [title], input[type='submit']").forEach((node) => {
    ["placeholder", "aria-label", "title", "value"].forEach((attr) => {
      if (!node.hasAttribute(attr)) return;
      const originalAttr = `data-i18n-original-${attr}`;
      if (!node.hasAttribute(originalAttr)) {
        node.setAttribute(originalAttr, node.getAttribute(attr));
      }
      node.setAttribute(attr, localizeText(node.getAttribute(originalAttr)));
    });
  });
  syncSelectOptionText();
}

function syncSelectOptionText() {
  document.querySelectorAll("select option").forEach((option) => {
    const original = option.dataset.i18nOriginalText || option.textContent;
    option.dataset.i18nOriginalText = original;
    option.textContent = localizeText(original);
  });
}

els.monthInput.value = state.month;
els.languageSelect.value = state.lang;

els.languageSelect.addEventListener("change", () => {
  state.lang = els.languageSelect.value;
  localStorage.setItem("disciplineos.lang", state.lang);
  applyLanguage();
  loadDashboard();
});

els.monthInput.addEventListener("change", () => {
  state.month = els.monthInput.value || state.month;
  loadDashboard();
});

els.generatorForm.elements.max_position_pct.addEventListener("input", () => {
  els.generatorForm.elements.max_position_pct.dataset.touched = "true";
});

els.generatorForm.elements.name.addEventListener("input", () => {
  els.generatorForm.elements.name.dataset.touched = "true";
});

els.generatorForm.elements.sector.addEventListener("input", () => {
  els.generatorForm.elements.sector.dataset.touched = "true";
});

els.generatorForm.elements.symbol.addEventListener("input", () => {
  applyStockLookup(els.generatorForm.elements.symbol.value);
});

els.refreshButton.addEventListener("click", loadDashboard);

els.seedButton.addEventListener("click", async () => {
  await fetch("/api/demo", { method: "POST" });
  await loadDashboard();
});

els.templateSelect.addEventListener("change", () => {
  renderWizardOptions(state.cardTemplates);
});

els.decisionSymbol.addEventListener("change", () => {
  loadDecisionEvidenceOptions(els.decisionSymbol.value);
});

els.dataSourceForm.elements.provider_type.addEventListener("change", updateDataSourceMode);
els.dataSyncForm.elements.capability.addEventListener("change", updateDataSourceMode);
els.settingsForm.elements.ai_enabled.addEventListener("change", updateSettingsMode);
["style_value", "style_growth", "style_cycle", "style_dividend", "style_cash_defensive"].forEach((name) => {
  els.profileForm.elements[name]?.addEventListener("input", () => {
    updateStyleAllocationHint(readStyleAllocations(new FormData(els.profileForm)));
  });
});

els.settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.settingsForm);
  const disciplineMode = text(form, "discipline_mode") || "block";
  await postJson("/api/settings", {
    storage_mode: text(form, "storage_mode"),
    discipline_mode: disciplineMode,
    strict_mode: disciplineMode === "block",
    ai_enabled: form.get("ai_enabled") === "on",
    ai_api_token: text(form, "ai_api_token"),
    ai_api_base_url: text(form, "ai_api_base_url"),
    ai_model: text(form, "ai_model"),
  });
  await loadDashboard();
});

els.backupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await postJson("/api/backups", {});
  await loadDashboard();
});

els.restoreForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const filename = els.restoreForm.elements.filename.value;
  if (!filename) return;
  const ok = window.confirm(`${t("Restore")} ${filename}?`);
  if (!ok) return;
  await postJson("/api/backups/restore", { filename });
  await loadDashboard();
});

els.dataSourceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.dataSourceForm);
  const providerType = text(form, "provider_type") || "manual";
  await postJson("/api/data-sources", {
    provider_name: providerType,
    provider_type: providerType,
    priority: 1,
    enabled: form.get("enabled") === "on",
    config: {
      local_path: text(form, "local_path"),
      api_token: text(form, "api_token"),
      api_base_url: text(form, "api_base_url"),
    },
  });
  await saveAutomaticCapabilities(providerType);
  await loadDashboard();
});

if (els.capabilityForm) {
  els.capabilityForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(els.capabilityForm);
    const sourceForm = new FormData(els.dataSourceForm);
    await postJson("/api/data-capabilities", {
      capability: text(form, "capability"),
      provider_name: text(sourceForm, "provider_type") || "manual",
      fallback_provider: text(form, "fallback_provider"),
      priority: number(form, "priority"),
      enabled: true,
    });
    await loadDashboard();
  });
}

els.dataSyncForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.dataSyncForm);
  const sourceForm = new FormData(els.dataSourceForm);
  await saveAutomaticCapabilities(text(sourceForm, "provider_type") || "manual");
  const result = await postJson("/api/data-sync", {
    capability: text(form, "capability"),
    symbol: text(form, "symbol").toUpperCase(),
    confirm: false,
  });
  renderImportResult(result.result, {
    capability: text(form, "capability"),
    symbol: text(form, "symbol").toUpperCase(),
  });
  await loadDashboard();
});

async function saveAutomaticCapabilities(providerType) {
  const capabilities = capabilitiesForProvider(providerType);
  await Promise.all(
    capabilities.map((capability) =>
      postJson("/api/data-capabilities", {
        capability,
        provider_name: providerType,
        fallback_provider: "",
        priority: 1,
        enabled: true,
      })
    )
  );
}

function capabilitiesForProvider(providerType) {
  if (providerType === "qmt") {
    return ["positions", "trades", "price_daily", "price_5min", "volume", "financial_metrics"];
  }
  if (providerType === "tushare" || providerType === "akshare") {
    return ["price_daily", "price_5min", "volume", "financial_metrics"];
  }
  return ["positions", "trades", "price_daily", "price_5min", "volume", "financial_metrics"];
}

function updateDataSourceMode() {
  const providerType = els.dataSourceForm.elements.provider_type.value;
  const capabilityField = els.dataSyncForm.elements.capability;
  const capabilities = capabilitiesForProvider(providerType);
  Array.from(capabilityField.options).forEach((option) => {
    option.disabled = !capabilities.includes(option.value);
  });
  if (!capabilities.includes(capabilityField.value)) {
    capabilityField.value = capabilities[0] || "positions";
  }
  if (!els.dataSourceHint) return;
  els.dataSourceHint.textContent = "";
  const visibleFields = {
    qmt: ["local_path"],
    tushare: ["api_token"],
    akshare: [],
    csv: ["local_path"],
    excel: ["local_path"],
    manual: [],
  }[providerType] || [];
  document.querySelectorAll("[data-source-field]").forEach((field) => {
    field.classList.toggle(
      "hidden",
      !visibleFields.includes(field.dataset.sourceField)
    );
  });
}

els.generatorForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.generatorForm);
  await postJson("/api/generate-card", {
    template: text(form, "template"),
    symbol: text(form, "symbol").toUpperCase(),
    name: text(form, "name"),
    sector: text(form, "sector"),
    max_position_pct: number(form, "max_position_pct"),
    review_cycle: text(form, "review_cycle") || "monthly",
    why_buy: wizardLines(form, "why_buy"),
    no_buy: wizardLines(form, "no_buy"),
    add_when: wizardLines(form, "add_when"),
    reduce_when: wizardLines(form, "reduce_when"),
    invalid_when: wizardLines(form, "invalid_when"),
    forbidden_behaviors: wizardLines(form, "forbidden_behaviors"),
    raise_position: wizardLines(form, "raise_position"),
    lower_position: wizardLines(form, "lower_position"),
  });
  await loadDashboard();
});

if (els.importForm) {
  els.importForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(els.importForm);
    const result = await postJson("/api/import-preview", {
      kind: text(form, "kind"),
      path: text(form, "path"),
    });
    renderImportResult(result.result);
  });
}

els.financialReportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.financialReportForm);
  const result = await postJson("/api/financial-report", {
    symbol: text(form, "symbol"),
    period: text(form, "period"),
    material_type: text(form, "material_type"),
    ai_online_search: form.get("ai_online_search") === "on",
    path: text(form, "path"),
    text: text(form, "text"),
  });
  renderFinancialReportResult(result.summary);
  await loadDashboard();
});

els.evidenceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.evidenceForm);
  await postJson("/api/evidence", {
    symbol: text(form, "symbol").toUpperCase(),
    evidence_type: text(form, "evidence_type"),
    title: text(form, "title"),
    content: text(form, "content"),
    source: text(form, "source") || "manual",
    source_date: text(form, "source_date"),
  });
  els.evidenceForm.reset();
  syncEvidenceSymbolSelects(state.latest.cards || {});
  els.evidenceForm.elements.source.value = "manual";
  await loadDashboard();
});

els.evidenceFilterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.evidenceFilterForm);
  const params = new URLSearchParams();
  if (text(form, "symbol")) params.set("symbol", text(form, "symbol").toUpperCase());
  if (text(form, "evidence_type")) params.set("evidence_type", text(form, "evidence_type"));
  const response = await fetch(`/api/evidence?${params.toString()}`);
  const result = await response.json();
  renderEvidence(result.evidence_items || []);
  els.evidenceModal.classList.remove("hidden");
  applyLanguage();
});

els.reviewSnapshotForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await postJson("/api/reviews", { month: state.month });
  await loadDashboard();
});

els.reviewCompareForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.reviewCompareForm);
  const left = text(form, "left_snapshot_id");
  const right = text(form, "right_snapshot_id");
  if (!left || !right || left === right) return;
  const result = await postJson("/api/reviews/compare", {
    left_snapshot_id: left,
    right_snapshot_id: right,
  });
  renderReviewComparison(result.comparison);
});

els.decisionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.decisionForm);
  const payload = {
    symbol: text(form, "symbol"),
    action: text(form, "action"),
    amount: number(form, "amount"),
    reason: text(form, "reason"),
    evidence: lines(form, "evidence"),
    evidence_item_ids: form.getAll("evidence_item_ids"),
    emotion: text(form, "emotion"),
    is_before_earnings: form.get("is_before_earnings") === "on",
    thesis_changed: form.get("thesis_changed") === "on",
    auto_position: form.get("auto_position") === "on",
  };
  const result = await postJson("/api/check", payload);
  renderAuditResult(result);
  await loadDashboard();
});

els.profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.profileForm);
  const styleAllocations = readStyleAllocations(form);
  const totalAllocation = sumStyleAllocations(styleAllocations);
  if (totalAllocation > 100) {
    window.alert(t("Style allocation total cannot exceed 100%."));
    updateStyleAllocationHint(styleAllocations);
    return;
  }
  await postJson("/api/profile", {
    name: text(form, "name"),
    style: dominantStyle(styleAllocations),
    style_allocations: styleAllocations,
    max_single_position_pct: number(form, "max_single_position_pct"),
    max_sector_position_pct: number(form, "max_sector_position_pct"),
    max_drawdown_pct: number(form, "max_drawdown_pct"),
    allow_pre_earnings_add: form.get("allow_pre_earnings_add") === "on",
    behavioral_weaknesses: lines(form, "behavioral_weaknesses"),
  });
  await loadDashboard();
});

els.positionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(els.positionForm);
  await postJson("/api/positions", {
    symbol: text(form, "symbol").toUpperCase(),
    name: text(form, "name"),
    asset_type: text(form, "asset_type"),
    market: text(form, "market"),
    sector: text(form, "sector"),
    theme: text(form, "theme"),
    currency: text(form, "currency"),
    quantity: number(form, "quantity"),
    cost_price: number(form, "cost_price"),
    current_price: number(form, "current_price"),
  });
  await loadDashboard();
});

document.addEventListener("click", async (event) => {
  const positionButton = event.target.closest("[data-position-pct]");
  if (!positionButton) return;
  els.generatorForm.elements.max_position_pct.value = positionButton.dataset.positionPct;
  els.generatorForm.elements.max_position_pct.dataset.touched = "true";
  document.querySelectorAll("[data-position-pct]").forEach((item) => {
    item.classList.toggle("selected", item === positionButton);
  });
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const symbol = button.dataset.symbol;

  if (button.dataset.action === "edit-card") {
    fillGeneratorForm(JSON.parse(button.dataset.card));
  }
  if (button.dataset.action === "delete-card") {
    await fetch(`/api/cards?symbol=${encodeURIComponent(symbol)}`, { method: "DELETE" });
    await loadDashboard();
  }
  if (button.dataset.action === "edit-position") {
    fillForm(els.positionForm, JSON.parse(button.dataset.position));
  }
  if (button.dataset.action === "delete-position") {
    await fetch(`/api/positions?symbol=${encodeURIComponent(symbol)}`, { method: "DELETE" });
    await loadDashboard();
  }
  if (button.dataset.action === "resolve-violation") {
    await postJson("/api/violations/resolve", {
      id: button.dataset.id,
      note: "Resolved from local UI",
    });
    await loadDashboard();
  }
  if (button.dataset.action === "export-review") {
    const result = await postJson("/api/reviews/export", {
      snapshot_id: button.dataset.id,
      format: "markdown",
    });
    window.alert(`${t("Report exported")}: ${result.report.path}`);
  }
  if (button.dataset.action === "restore-backup") {
    const ok = window.confirm(`Restore backup ${button.dataset.filename}?`);
    if (!ok) return;
    await postJson("/api/backups/restore", {
      filename: button.dataset.filename,
    });
    await loadDashboard();
  }
  if (button.dataset.action === "confirm-import") {
    const result = await postJson("/api/import", {
      kind: button.dataset.kind,
      path: button.dataset.path,
      confirm: true,
    });
    renderImportResult(result.result);
    await loadDashboard();
  }
  if (button.dataset.action === "confirm-sync") {
    const result = await postJson("/api/data-sync", {
      capability: button.dataset.capability,
      symbol: button.dataset.symbol || "",
      confirm: true,
    });
    renderImportResult(result.result);
    await loadDashboard();
  }
  if (button.dataset.action === "show-system-status") {
    showSystemStatus();
  }
  if (button.dataset.action === "show-sync-logs") {
    showSyncLogs();
  }
  if (button.dataset.action === "show-market-data") {
    await showMarketData();
  }
  if (button.dataset.action === "show-info-analysis") {
    showInfoAnalysis();
  }
  if (button.dataset.action === "show-evidence-library") {
    showEvidenceLibrary();
  }
  if (button.dataset.action === "show-behavior-library") {
    showBehaviorLibrary();
  }
  if (button.dataset.action === "show-position-guard") {
    showModal(els.positionGuardModal);
  }
  if (button.dataset.action === "show-monthly-review") {
    showModal(els.monthlyReviewModal);
  }
  if (button.dataset.action === "show-trade-ledger") {
    showModal(els.tradeLedgerModal);
  }
  if (button.dataset.action === "show-copilot") {
    showModal(els.copilotModal);
  }
  if (button.dataset.action === "show-card-library") {
    showModal(els.cardLibraryModal);
  }
  if (button.dataset.action === "show-violation-ledger") {
    showModal(els.violationLedgerModal);
  }
  if (button.dataset.action === "show-decision-history") {
    showModal(els.decisionHistoryModal);
  }
  if (button.dataset.action === "add-behavior-weakness") {
    addBehaviorWeakness(button.dataset.behaviorValue || "");
  }
  if (button.dataset.action === "apply-info-suggestions") {
    applyInfoSuggestionsToGenerator(JSON.parse(button.dataset.summary));
  }
  if (button.dataset.pathPicker !== undefined) {
    await openPathBrowser(
      button.dataset.targetForm,
      button.dataset.targetName
    );
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-system-status-action]");
  if (!button) return;
  if (button.dataset.systemStatusAction === "close") {
    els.systemStatusModal.classList.add("hidden");
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-info-analysis-action]");
  if (!button) return;
  if (button.dataset.infoAnalysisAction === "close") {
    els.infoAnalysisModal.classList.add("hidden");
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-sync-logs-action]");
  if (!button) return;
  if (button.dataset.syncLogsAction === "close") {
    els.syncLogsModal.classList.add("hidden");
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-evidence-action]");
  if (!button) return;
  if (button.dataset.evidenceAction === "close") {
    els.evidenceModal.classList.add("hidden");
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-behavior-library-action]");
  if (!button) return;
  if (button.dataset.behaviorLibraryAction === "close") {
    els.behaviorLibraryModal.classList.add("hidden");
  }
});

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-modal-close]");
  if (!button) return;
  document.querySelector(`#${button.dataset.modalClose}`)?.classList.add("hidden");
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-path-picker]");
  if (!button) return;
  await openPathBrowser(
    button.dataset.targetForm,
    button.dataset.targetName,
    {
      mode: button.dataset.pathMode || "directory",
      extensions: button.dataset.pathExtensions || "",
    }
  );
});

document.addEventListener("click", async (event) => {
  const item = event.target.closest("[data-path-entry]");
  if (!item) return;
  if (state.pathBrowser.mode === "file" && item.dataset.pathIsDir !== "true") {
    setPickedPath(item.dataset.pathEntry);
    return;
  }
  await loadPathBrowser(item.dataset.pathEntry);
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-path-action]");
  if (!button) return;
  if (button.dataset.pathAction === "close") {
    els.pathBrowser.classList.add("hidden");
  }
  if (button.dataset.pathAction === "up") {
    await loadPathBrowser(state.pathBrowser.parentPath);
  }
  if (button.dataset.pathAction === "select") {
    setPickedPath(state.pathBrowser.currentPath);
  }
});

async function loadDashboard() {
  const response = await fetch(`/api/dashboard?month=${encodeURIComponent(state.month)}`);
  const data = await response.json();
  renderDashboard(data);
}

async function openPathBrowser(targetForm, targetName, options = {}) {
  state.pathBrowser.targetForm = targetForm;
  state.pathBrowser.targetName = targetName;
  state.pathBrowser.mode = options.mode || "directory";
  state.pathBrowser.extensions = options.extensions || "";
  const current = els[targetForm]?.elements?.[targetName]?.value || "";
  els.pathBrowser.classList.remove("hidden");
  await loadPathBrowser(current);
}

async function loadPathBrowser(path = "") {
  const params = new URLSearchParams({ path: path || "" });
  if (state.pathBrowser.extensions) {
    params.set("extensions", state.pathBrowser.extensions);
  }
  const response = await fetch(`/api/path-browser?${params.toString()}`);
  const data = await response.json();
  state.pathBrowser.currentPath = data.current_path || "";
  state.pathBrowser.parentPath = data.parent_path || "";
  els.pathBrowserCurrent.textContent = state.pathBrowser.mode === "file"
    ? `${data.current_path || t("Roots")} · ${t("Click a file to select it.")}`
    : data.current_path || t("Roots");
  if (els.pathBrowserSelect) {
    els.pathBrowserSelect.textContent = state.pathBrowser.mode === "file"
      ? t("Select This Folder")
      : t("Select Current Path");
  }
  els.pathBrowserList.innerHTML = (data.entries || [])
    .map((entry) => `
      <button type="button" class="path-entry" data-path-entry="${escapeHtml(entry.path)}" data-path-is-dir="${entry.is_dir ? "true" : "false"}">
        <span>${entry.is_dir ? "\u25b6" : "\u25cf"}</span>
        <strong>${escapeHtml(entry.name)}</strong>
        <small>${entry.is_dir ? t("Folder") : t("File")}</small>
      </button>
    `)
    .join("") || `<div class="empty">${t("No entries.")}</div>`;
}

function setPickedPath(path) {
  const form = els[state.pathBrowser.targetForm];
  if (form?.elements?.[state.pathBrowser.targetName]) {
    form.elements[state.pathBrowser.targetName].value = path || "";
  }
  els.pathBrowser.classList.add("hidden");
}

function showModal(modal) {
  if (!modal) return;
  modal.classList.remove("hidden");
  applyLanguage();
}

function renderDashboard(data) {
  const review = data.review || {};
  els.score.textContent = `${review.discipline_score ?? "--"}`;
  els.decisionCount.textContent = review.decision_count ?? "--";
  els.statusCounts.textContent =
    Object.entries(review.status_counts || {})
      .map(([key, value]) => `${localizeText(key)} ${value}`)
      .join(" / ") || "--";

  renderSettings(data.settings || {});
  renderHealth(data.data_health || {});
  renderBackups(data.backup_archives || []);
  renderDataSources(
    data.data_sources || [],
    data.data_capabilities || [],
    data.data_sync_logs || [],
    data.market_data_summary || { by_type: [], top_symbols: [] }
  );
  renderTemplates(data.card_templates || {});
  renderProfile(data.profile || {});
  renderCards(data.cards || {});
  renderPositions(data.positions || {});
  renderTrades(data.trades || [], data.trade_reconciliation || {});
  renderFinancialReports(data.financial_reports || []);
  state.latest.evidenceItems = data.evidence_items || [];
  renderEvidence([]);
  renderPositionGuard(data.position_guard || {});
  renderViolations(data.violations || []);
  renderReview(review);
  renderScoreBreakdown(review.score_report || {});
  renderAttribution(review.attribution || {});
  renderRuleSuggestions(review.rule_revision_suggestions || []);
  renderReviewCompareOptions(data.review_snapshots || []);
  renderReviewSnapshots(data.review_snapshots || []);
  renderReviewReports(data.review_reports || []);
  renderCopilot(data.copilot || {});
  renderAIRuns(data.ai_runs || []);
  renderHistory(data.decisions || [], data.audits || [], data.rule_results || []);
  renderSymbolOptions(data.cards || {});
  syncEvidenceSymbolSelects(data.cards || {});
  renderDecisionEvidenceOptions(data.evidence_items || [], els.decisionSymbol.value);
  renderStockSuggestions();
  updateDataSourceMode();
  applyLanguage();
}

function renderSettings(settings) {
  state.latest.settings = settings;
  fillForm(els.settingsForm, {
    ...settings,
    discipline_mode:
      settings.discipline_mode || (settings.strict_mode ? "block" : "warn"),
  });
  els.settingsView.innerHTML = "";
  updateSettingsMode();
}

function updateSettingsMode() {
  const enabled = els.settingsForm.elements.ai_enabled.checked;
  document.querySelectorAll("[data-ai-field]").forEach((field) => {
    field.classList.toggle("hidden", !enabled);
  });
}

function renderHealth(health) {
  state.latest.health = health;
  const checks = health.checks || [];
  els.healthView.innerHTML = renderHealthDetails(health, checks);
}

function renderHealthDetails(health, checks = health.checks || []) {
  return `
    <div class="item">
      <strong>${t("Data Health")} <span class="badge ${health.status || "WARN"}">${badgeText(health.status || "UNKNOWN")}</span></strong>
      <div class="muted">${health.check_count || 0} ${t("Health Checks")} / ${t("PASS")} ${health.summary?.PASS || 0} / ${t("WARN")} ${health.summary?.WARN || 0} / ${t("BLOCKED")} ${health.summary?.BLOCKED || 0}</div>
    </div>
    ${checks.map((item) => `
      <div class="item">
        <strong>${escapeHtml(localizeText(item.title || ""))} <span class="badge ${escapeHtml(item.status || "WARN")}">${badgeText(item.status || "WARN")}</span></strong>
        <div class="muted">${escapeHtml(localizeText(item.category || ""))}</div>
        <div>${escapeHtml(localizeText(item.message || ""))}</div>
      </div>
    `).join("")}
  `;
}

function renderBackups(backups) {
  state.latest.backups = backups;
  renderBackupSelect(backups);
  if (!backups.length) {
    els.backupView.innerHTML = `<div class="empty">${t("No backup archive yet.")}</div>`;
    return;
  }
  els.backupView.innerHTML = `
    <div class="item">
      <strong>${t("Backup Archives")}</strong>
      <div class="muted">${backups.length}</div>
    </div>
    ${backups.map((backup) => `
      <div class="item">
        <strong>${escapeHtml(backup.filename || "")}</strong>
        <div class="muted">${escapeHtml(backup.path || "")}</div>
        <div class="muted">${escapeHtml(backup.created_at || "")} / ${backup.bytes || 0} ${t("bytes")} / ${backup.file_count || 0} ${t("files")}</div>
        <div class="item-actions">
          <button type="button" data-action="restore-backup" data-filename="${escapeHtml(backup.filename || "")}">${t("Restore")}</button>
        </div>
      </div>
    `).join("")}
  `;
}

function renderBackupSelect(backups) {
  if (!els.backupSelect) return;
  els.backupSelect.innerHTML = backups.length
    ? backups
        .map((backup) => `<option value="${escapeHtml(backup.filename || "")}">${escapeHtml(backup.filename || "")}</option>`)
        .join("")
    : `<option value="">${t("No backup archive yet.")}</option>`;
  els.restoreForm.querySelector("button").disabled = !backups.length;
}

function showSystemStatus() {
  const settings = state.latest.settings || {};
  const backups = state.latest.backups || [];
  els.systemStatusView.innerHTML = `
    <div class="item">
      <strong>${t("Database Mode")}: ${escapeHtml(settings.storage_mode || "sqlite")}</strong>
      <div class="muted">${t("Violation Handling")}: ${escapeHtml(localizeText(settings.discipline_mode || (settings.strict_mode ? "block" : "warn")))} / ${t("AI review analysis")}: ${t(settings.ai_enabled ? "ON" : "OFF")}</div>
    </div>
    ${renderHealthDetails(state.latest.health || {})}
    <div class="item">
      <strong>${t("Backup Archives")}</strong>
      <div class="muted">${backups.length}</div>
    </div>
    ${
      backups.length
        ? backups.map((backup) => `
          <div class="item">
            <strong>${escapeHtml(backup.filename || "")}</strong>
            <div class="muted">${escapeHtml(backup.path || "")}</div>
            <div class="muted">${escapeHtml(backup.created_at || "")} / ${backup.bytes || 0} ${t("bytes")} / ${backup.file_count || 0} ${t("files")}</div>
          </div>
        `).join("")
        : `<div class="empty">${t("No backup archive yet.")}</div>`
    }
  `;
  els.systemStatusModal.classList.remove("hidden");
  applyLanguage();
}

function renderDataSources(sources, capabilities, syncLogs, marketDataSummary = { by_type: [], top_symbols: [] }) {
  state.latest.dataSources = sources;
  state.latest.syncLogs = syncLogs;
  state.latest.marketDataSummary = marketDataSummary;
  els.dataSourcesView.innerHTML = "";
}

function renderDataSourceStatus(sources) {
  return sources.length
    ? sources
        .map(
          (source) => `
            <div class="item">
              <strong>${escapeHtml(localizeText(source.provider_type))}</strong>
              <div class="muted">${t(source.enabled ? "enabled" : "disabled")} / ${escapeHtml(localizeText(source.test_status || "untested"))}</div>
              <div class="muted">${escapeHtml(localizeText(source.test_message || ""))}</div>
            </div>
          `
        )
        .join("")
    : `<div class="empty">${t("No data source configured yet.")}</div>`;
}

function renderSyncLogs(syncLogs) {
  return syncLogs.length
    ? syncLogs
        .map(
          (item) => `
            <div class="item">
              <strong>${escapeHtml(localizeText(item.sync_type))} / ${escapeHtml(item.provider_name)} / ${escapeHtml(localizeText(item.status))}</strong>
              <div class="muted">${escapeHtml(localizeText(item.message || ""))}</div>
              <div class="muted">${escapeHtml(item.started_at || "")} -> ${escapeHtml(item.finished_at || "")}</div>
            </div>
          `
        )
        .join("")
    : `<div class="empty">${t("No sync log yet.")}</div>`;
}

function showSyncLogs() {
  els.syncLogsView.innerHTML = `
    ${renderDataSourceStatus(state.latest.dataSources || [])}
    <div class="item">
      <strong>${t("Sync Logs")}</strong>
    </div>
    ${renderSyncLogs(state.latest.syncLogs || [])}
  `;
  els.syncLogsModal.classList.remove("hidden");
  applyLanguage();
}

async function showMarketData() {
  const response = await fetch("/api/market-data?limit=30");
  const data = await response.json();
  if (!response.ok) throw new Error(localizeText(data.error || "Request failed"));
  state.latest.marketRecords = data.market_records || [];
  state.latest.marketDataSummary =
    data.market_data_summary || state.latest.marketDataSummary || { by_type: [], top_symbols: [] };
  els.marketDataView.innerHTML = `
    ${renderMarketDataSummary(state.latest.marketDataSummary)}
    <div class="item">
      <strong>${t("Recent Market Records")}</strong>
    </div>
    ${renderMarketRecords(state.latest.marketRecords)}
  `;
  showModal(els.marketDataModal);
}

function renderMarketDataSummary(summary) {
  const byType = summary.by_type || [];
  const topSymbols = summary.top_symbols || [];
  if (!byType.length && !topSymbols.length) {
    return `<div class="empty">${t("No market data saved yet.")}</div>`;
  }
  return `
    <div class="item">
      <strong>${t("Market Data Summary")}</strong>
      ${
        byType.length
          ? byType
              .map(
                (item) => `
                  <div class="muted">
                    ${escapeHtml(localizeText(item.data_type))}: ${t("Rows")} ${item.row_count}
                    / ${t("First")} ${escapeHtml(item.first_timestamp || "")}
                    / ${t("Latest")} ${escapeHtml(item.last_timestamp || "")}
                  </div>
                `
              )
              .join("")
          : ""
      }
      ${
        topSymbols.length
          ? `<div class="muted">${t("Top Symbols")}: ${topSymbols
              .map((item) => `${escapeHtml(item.symbol)}(${item.row_count})`)
              .join(" / ")}</div>`
          : ""
      }
    </div>
  `;
}

function renderMarketRecords(records) {
  return records.length
    ? records
        .map(
          (item) => `
            <div class="item">
              <strong>${escapeHtml(item.symbol)} / ${escapeHtml(localizeText(item.data_type))} / ${escapeHtml(item.timestamp)}</strong>
              <div class="muted">${escapeHtml(item.provider_name)} / ${escapeHtml(item.source || "")}</div>
              <div class="muted">${escapeHtml(JSON.stringify(item.fields || {}))}</div>
            </div>
          `
        )
        .join("")
    : `<div class="empty">${t("No market data saved yet.")}</div>`;
}

function renderFinancialReportResult(summary) {
  state.latest.infoAnalysisSummary = summary;
  els.financialReportResult.innerHTML = renderInfoAnalysisSummary(summary);
  showInfoAnalysis();
}

function renderInfoAnalysisSummary(summary) {
  const mode = summary.analysis_mode === "ai"
    ? t("AI analysis")
    : summary.ai_status === "failed"
      ? t("AI failed, local rules used")
      : t("Local rules");
  return `
    <div class="item">
      <strong>${escapeHtml(summary.symbol)} ${escapeHtml(summary.period)}</strong>
      <div class="muted">${t("Analysis Mode")}: ${mode} / ${escapeHtml(localizeText(summary.material_type || ""))}</div>
      <div class="muted">${escapeHtml(summary.source)}</div>
      ${summary.ai_error ? `<div class="muted">${escapeHtml(summary.ai_error)}</div>` : ""}
      ${renderInfoList(t("Key Insights"), summary.key_insights || summary.evidence_summary || [])}
      ${renderInfoList(t("Positive Factors"), summary.positive_factors || [])}
      ${renderInfoList(t("Negative Factors"), summary.negative_factors || [])}
      ${renderInfoList(t("Risk Flags"), summary.risk_flags || [])}
      ${renderInfoList(t("Discipline Suggestions"), summary.discipline_suggestions || [])}
      <div class="muted">${t("Card Suggestions")}: ${renderCardSuggestionText(summary)}</div>
      <div class="item-actions">
        <button type="button" data-action="apply-info-suggestions" data-summary="${escapeHtml(JSON.stringify(summary))}">${t("Apply to Discipline Card Draft")}</button>
      </div>
    </div>
  `;
}

function renderCardSuggestionText(summary) {
  const suggestions = summary.card_suggestions || {};
  const lines = Object.values(suggestions).flat().filter(Boolean);
  if (lines.length) {
    return lines.slice(0, 4).map(escapeHtml).join(" / ");
  }
  const fallbackLines = summary.evidence_summary || [];
  if (!fallbackLines.length) return t("None");
  return fallbackLines
    .slice(0, 3)
    .map((line) => `${escapeHtml(summary.symbol)}: ${escapeHtml(line)}`)
    .join(" / ");
}

function renderInfoList(title, items) {
  const values = (items || []).filter(Boolean);
  if (!values.length) return "";
  return `
    <div>
      <strong>${title}</strong>
      <ul>${values.map((item) => `<li>${escapeHtml(localizeText(item))}</li>`).join("")}</ul>
    </div>
  `;
}

function applyInfoSuggestionsToGenerator(summary) {
  const stock = CN_STOCKS[String(summary.symbol || "").replace(/\D/g, "").slice(0, 6)] || {};
  els.generatorForm.elements.symbol.value = summary.symbol || "";
  els.generatorForm.elements.name.value = els.generatorForm.elements.name.value || stock.name || "";
  els.generatorForm.elements.sector.value = els.generatorForm.elements.sector.value || stock.sector || "";
  const suggestions = summary.card_suggestions || {};
  appendLinesToField("why_buy", suggestions.why_buy || summary.key_insights || []);
  appendLinesToField("no_buy", suggestions.no_buy || summary.negative_factors || []);
  appendLinesToField("add_when", suggestions.add_when || []);
  appendLinesToField("reduce_when", suggestions.reduce_when || []);
  appendLinesToField("raise_position", suggestions.raise_position || []);
  appendLinesToField("lower_position", suggestions.lower_position || summary.risk_flags || []);
  appendLinesToField("invalid_when", suggestions.invalid_when || []);
  appendLinesToField("forbidden_behaviors", suggestions.forbidden_behaviors || []);
  els.infoAnalysisModal.classList.add("hidden");
  els.generatorForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

function appendLinesToField(fieldName, values) {
  const field = els.generatorForm.elements[fieldName];
  if (!field) return;
  const existing = linesFromText(field.value);
  const next = [...existing];
  (values || []).forEach((value) => {
    const line = String(value || "").trim();
    if (line && !next.includes(line)) next.push(line);
  });
  field.value = next.join("\n");
}

function linesFromText(value) {
  return String(value || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function renderLegacyCardSuggestionText(summary) {
  const lines = summary.evidence_summary || [];
  if (!lines.length) return t("None");
  return lines
    .slice(0, 3)
    .map((line) => `${summary.symbol}: ${line}`)
    .join(" / ");
}

function renderImportResult(result, options = {}) {
  const errors = result.errors || [];
  const samples = result.sample_items || [];
  const marketSamples = result.sample_market_records || [];
  const priceUpdate = result.position_price_update || {};
  const canImport = result.can_import && !result.commit;
  const confirmAction = options.capability ? "confirm-sync" : "confirm-import";
  const confirmAttrs = options.capability
    ? `data-capability="${escapeHtml(options.capability)}" data-symbol="${escapeHtml(options.symbol || "")}"`
    : `data-kind="${escapeHtml(result.kind || "")}" data-path="${escapeHtml(result.source || "")}"`;
  els.importResult.innerHTML = `
    <div class="item">
      <strong>${escapeHtml(localizeText(result.kind))} ${t("import")}</strong>
      <div class="muted">${t("Rows")} ${result.row_count ?? 0} / ${t("valid")} ${result.imported ?? 0} / ${t("skipped")} ${result.skipped ?? 0} / ${t("commit")} ${t(result.commit ? "yes" : "no")}</div>
      <div class="muted">${t("Market Records")}: ${result.market_record_count ?? (result.market_records || marketSamples).length ?? 0}</div>
      ${
        result.position_price_update
          ? `<div class="muted">${t("Position Price Updates")}: ${priceUpdate.updated_count || 0}</div>`
          : ""
      }
      <div class="muted">${t("Missing columns")}: ${(result.missing_columns || []).map(escapeHtml).join(", ") || t("None")}</div>
      <div class="muted">${errors.map(escapeHtml).join("<br />") || t("No errors")}</div>
      ${
        samples.length
          ? `<details class="rule-results"><summary>${t("Preview Rows")} (${samples.length})</summary><div class="muted">${samples.map((item) => escapeHtml(JSON.stringify(item))).join("<br />")}</div></details>`
          : ""
      }
      ${
        marketSamples.length
          ? `<details class="rule-results"><summary>${t("Market Records")} (${marketSamples.length})</summary><div class="muted">${marketSamples.map((item) => escapeHtml(JSON.stringify(item))).join("<br />")}</div></details>`
          : ""
      }
      ${
        canImport
          ? `<div class="item-actions"><button type="button" data-action="${confirmAction}" ${confirmAttrs}>${options.capability ? t("Confirm Sync") : t("Confirm Import")}</button></div>`
          : ""
      }
    </div>
  `;
}

function renderFinancialReports(reports) {
  state.latest.financialReports = reports;
  if (!reports.length) {
    els.financialReportsView.innerHTML = `<div class="empty">${t("No financial report summary saved.")}</div>`;
    return;
  }
  els.financialReportsView.innerHTML = reports
    .slice(-6)
    .reverse()
    .map((report) => `
      <div class="item">
        <strong>${escapeHtml(report.symbol)} ${escapeHtml(report.period)}</strong>
        <div class="muted">${escapeHtml(report.source || "")}</div>
        <div>${(report.evidence_summary || []).map(escapeHtml).join("<br />")}</div>
      </div>
    `)
    .join("");
}

function showInfoAnalysis() {
  const current = state.latest.infoAnalysisSummary;
  const reports = state.latest.financialReports || [];
  els.infoAnalysisView.innerHTML = `
    ${
      current
        ? renderInfoAnalysisSummary(current)
        : `<div class="empty">${t("No report summarized yet.")}</div>`
    }
    ${
      reports.length
        ? reports
            .slice(-8)
            .reverse()
            .map(renderInfoAnalysisSummary)
            .join("")
        : ""
    }
  `;
  els.infoAnalysisModal.classList.remove("hidden");
  applyLanguage();
}

function renderEvidence(items) {
  if (!items.length) {
    els.evidenceView.innerHTML = `<div class="empty">${t("No evidence item saved.")}</div>`;
    return;
  }
  els.evidenceView.innerHTML = items
    .slice(0, 10)
    .map((item) => `
      <div class="item">
        <strong>${escapeHtml(item.symbol)} / ${escapeHtml(localizeText(item.evidence_type))} / ${escapeHtml(localizeText(item.title))}</strong>
        <div>${escapeHtml(localizeText(item.content))}</div>
        <div class="muted">${escapeHtml(item.source || "manual")} ${escapeHtml(item.source_date || "")}</div>
      </div>
    `)
    .join("");
}

function showEvidenceLibrary() {
  renderEvidence(state.latest.evidenceItems || []);
  els.evidenceModal.classList.remove("hidden");
  applyLanguage();
}

async function loadDecisionEvidenceOptions(symbol) {
  if (!symbol) {
    renderDecisionEvidenceOptions([], "");
    return;
  }
  const params = new URLSearchParams({ symbol });
  const response = await fetch(`/api/evidence?${params.toString()}`);
  const result = await response.json();
  renderDecisionEvidenceOptions(result.evidence_items || [], symbol);
}

function renderDecisionEvidenceOptions(items, symbol) {
  const filtered = (items || [])
    .filter((item) => !symbol || item.symbol === symbol)
    .slice(0, 8);
  if (!filtered.length) {
    els.decisionEvidenceOptions.innerHTML = `<div class="empty">${t("No evidence item saved.")}</div>`;
    return;
  }
  els.decisionEvidenceOptions.innerHTML = filtered
    .map((item) => `
      <label class="option-pill">
        <input type="checkbox" name="evidence_item_ids" value="${escapeHtml(item.id)}" />
        <span>${formatEvidenceLabel(item)}</span>
      </label>
    `)
    .join("");
}

function formatEvidenceLabel(item) {
  const title = localizeText(item.title || "");
  const content = localizeText(item.content || "");
  const preview = content ? ` · ${content.slice(0, 48)}${content.length > 48 ? "..." : ""}` : "";
  return `${escapeHtml(localizeText(item.evidence_type))} / ${escapeHtml(title)}${escapeHtml(preview)}`;
}

function renderCopilot(copilot) {
  if (!copilot.notice) {
    els.copilotView.innerHTML = `<div class="empty">${t("No copilot output yet.")}</div>`;
    return;
  }
  const drift = copilot.thesis_drift_alerts || [];
  const drafts = copilot.card_draft_suggestions || [];
  const next = copilot.next_actions || [];
  els.copilotView.innerHTML = `
    <div class="item">
      <strong>${t(copilot.ai_enabled ? "AI enabled" : "AI disabled")} / ${escapeHtml(localizeText(copilot.compliance_status || "pass"))}</strong>
      <div class="muted">${t("Final status source")}: ${escapeHtml(localizeText(copilot.final_status_source || "rule_engine"))}</div>
    </div>
    <div class="item">
      <strong>${t("Compliance Boundary")}</strong>
      <div class="muted">${escapeHtml(localizeText(copilot.notice))}</div>
    </div>
    <div class="item">
      <strong>${t("Monthly Review Draft")}</strong>
      <div>${escapeHtml(localizeText(copilot.monthly_review_draft || ""))}</div>
    </div>
    <div class="item">
      <strong>${t("Thesis Drift Alerts")}</strong>
      <div class="muted">${drift.map((item) => `${escapeHtml(item.symbol)}: ${escapeHtml(localizeText(item.message))} ${escapeHtml(localizeText(item.suggestion))}`).join("<br />") || t("None")}</div>
    </div>
    <div class="item">
      <strong>${t("Card Draft Suggestions")}</strong>
      <div class="muted">${drafts.map((item) => `${escapeHtml(item.symbol)} / ${escapeHtml(localizeText(item.focus))}: ${escapeHtml(localizeText(item.draft))}`).join("<br />") || t("None")}</div>
    </div>
    <div class="item">
      <strong>${t("Next Actions")}</strong>
      <div class="muted">${next.map(localizeText).map(escapeHtml).join("<br />") || t("None")}</div>
    </div>
  `;
}

function renderAIRuns(runs) {
  if (!runs.length) return;
  els.copilotView.innerHTML += `
    <div class="item">
      <strong>${t("AI Audit Runs")}</strong>
      <div class="muted">
        ${runs
          .map((run) => `${escapeHtml(run.created_at)} / ${escapeHtml(localizeText(run.agent_type))} / ${escapeHtml(localizeText(run.compliance_status))} / ${t(run.ai_enabled ? "AI on" : "AI off")}`)
          .join("<br />")}
      </div>
    </div>
  `;
}

function renderTemplates(templates) {
  state.cardTemplates = templates;
  const current = els.templateSelect.value;
  els.templateSelect.innerHTML = Object.entries(templates)
    .map(([key, template]) => `<option value="${escapeHtml(key)}">${escapeHtml(t(template.label))}</option>`)
    .join("");
  if (templates[current]) els.templateSelect.value = current;
  renderWizardOptions(templates);
}

function renderWizardOptions(templates) {
  const template = templates[els.templateSelect.value] || Object.values(templates)[0];
  if (!template) return;
  const fields = [
    [els.whyBuyOptions, "why_buy", template.thesis_options || []],
    [els.noBuyOptions, "no_buy", template.no_buy_conditions || []],
    [els.addWhenOptions, "add_when", template.add_conditions || []],
    [els.reduceWhenOptions, "reduce_when", template.reduce_conditions || []],
    [els.raisePositionOptions, "raise_position", template.raise_position_conditions || []],
    [els.lowerPositionOptions, "lower_position", template.lower_position_conditions || []],
    [els.invalidWhenOptions, "invalid_when", template.invalid_conditions || []],
    [els.forbiddenOptions, "forbidden_behaviors", template.forbidden_behaviors || []],
  ];
  fields.forEach(([container, name, values]) => {
    renderOptionGroup(container, name, values);
  });
  renderPositionPresets(Number(template.default_max_position_pct || 15));
  const maxField = els.generatorForm.elements.max_position_pct;
  if (!maxField.dataset.touched) maxField.value = template.default_max_position_pct || maxField.value;
}

function renderOptionGroup(container, name, values) {
  if (!container) return;
  container.innerHTML = values
    .map((value, index) => `
      <label class="option-pill">
        <input type="checkbox" name="${escapeHtml(name)}__option" value="${escapeHtml(value)}" ${index === 0 ? "checked" : ""} />
        <span>${escapeHtml(localizeText(value))}</span>
      </label>
    `)
    .join("");
}

function renderStockSuggestions() {
  const datalist = document.querySelector("#stockSuggestions");
  if (!datalist) return;
  datalist.innerHTML = Object.entries(CN_STOCKS)
    .map(([symbol, item]) => `<option value="${symbol}">${symbol} ${item.name}</option>`)
    .join("");
}

function applyStockLookup(rawSymbol) {
  const normalized = String(rawSymbol || "").replace(/\D/g, "").slice(0, 6);
  const stock = CN_STOCKS[normalized];
  if (!stock) return;
  const nameField = els.generatorForm.elements.name;
  const sectorField = els.generatorForm.elements.sector;
  if (!nameField.dataset.touched || !nameField.value || nameField.value === "Sample Asset") {
    nameField.value = stock.name;
  }
  if (!sectorField.dataset.touched || !sectorField.value || sectorField.value === "technology") {
    sectorField.value = stock.sector;
  }
}

function renderPositionPresets(defaultPct) {
  const values = Array.from(new Set([5, 10, 15, 20, defaultPct, 25, 30]))
    .filter((value) => Number.isFinite(value) && value > 0)
    .sort((a, b) => a - b);
  els.positionPresetOptions.innerHTML = values
    .map((value) => `
      <button type="button" class="option-button ${value === defaultPct ? "selected" : ""}" data-position-pct="${value}">
        ${value}%
      </button>
    `)
    .join("");
}

function renderProfile(profile) {
  const allocations = profile.style_allocations || legacyStyleAllocation(profile.style);
  fillForm(els.profileForm, {
    ...profile,
    style_value: allocations.value || "",
    style_growth: allocations.growth || "",
    style_cycle: allocations.cycle || "",
    style_dividend: allocations.dividend || "",
    style_cash_defensive: allocations.cash_defensive || "",
    behavioral_weaknesses: (profile.behavioral_weaknesses || []).join("\n"),
  });
  updateStyleAllocationHint(allocations);
}

function readStyleAllocations(form) {
  return {
    value: number(form, "style_value"),
    growth: number(form, "style_growth"),
    cycle: number(form, "style_cycle"),
    dividend: number(form, "style_dividend"),
    cash_defensive: number(form, "style_cash_defensive"),
  };
}

function sumStyleAllocations(allocations) {
  return Object.values(allocations || {}).reduce((total, value) => total + Number(value || 0), 0);
}

function dominantStyle(allocations) {
  const entries = Object.entries(allocations || {}).filter(([, value]) => Number(value || 0) > 0);
  if (!entries.length) return "balanced";
  return entries.sort((a, b) => Number(b[1]) - Number(a[1]))[0][0];
}

function legacyStyleAllocation(style) {
  return style ? { [style]: 100 } : {};
}

function updateStyleAllocationHint(allocations) {
  if (!els.styleAllocationHint) return;
  const total = sumStyleAllocations(allocations);
  const remaining = Math.max(0, 100 - total);
  els.styleAllocationHint.textContent =
    `${t("Style allocation total")}: ${total.toFixed(1)}% / ${t("Remaining unallocated")}: ${remaining.toFixed(1)}%`;
  els.styleAllocationHint.classList.toggle("danger-text", total > 100);
}

function showBehaviorLibrary() {
  els.behaviorLibraryView.innerHTML = BEHAVIOR_WEAKNESSES
    .map(([en, zh, manifestation]) => {
      const value = `${en} ${zh}：${manifestation}`;
      return `
        <div class="item behavior-item">
          <strong>${escapeHtml(en)} / ${escapeHtml(zh)}</strong>
          <div>${t("Core manifestation")}: ${escapeHtml(manifestation)}</div>
          <div class="item-actions">
            <button type="button" data-action="add-behavior-weakness" data-behavior-value="${escapeHtml(value)}">${t("Insert Weakness")}</button>
          </div>
        </div>
      `;
    })
    .join("");
  els.behaviorLibraryModal.classList.remove("hidden");
  applyLanguage();
}

function addBehaviorWeakness(value) {
  const field = els.profileForm.elements.behavioral_weaknesses;
  if (!field || !value) return;
  const values = linesFromText(field.value);
  if (!values.includes(value)) {
    values.push(value);
    field.value = values.join("\n");
  }
}

function renderCards(cards) {
  const values = Object.values(cards);
  if (!values.length) {
    els.cardsView.innerHTML = `<div class="empty">${t("No discipline card yet. Generate one above.")}</div>`;
    return;
  }
  els.cardsView.innerHTML = values
    .map((card) => `
      <div class="item">
        <strong>${escapeHtml(card.symbol)} - ${escapeHtml(card.name)}</strong>
        <div class="muted">${escapeHtml(localizeText(card.asset_type))} / ${escapeHtml(card.sector)} / ${t("max")} ${card.max_position_pct}%</div>
        <p>${(card.thesis || []).map(localizeText).map(escapeHtml).join("; ")}</p>
        <div class="muted">${t("Add")}: ${(card.add_conditions || []).map(localizeText).map(escapeHtml).join("; ")}</div>
        <div class="muted">${t("Raise limit")}: ${(card.raise_position_conditions || []).map(localizeText).map(escapeHtml).join("; ") || t("None")}</div>
        <div class="muted">${t("Lower limit")}: ${(card.lower_position_conditions || []).map(localizeText).map(escapeHtml).join("; ") || t("None")}</div>
        <div class="item-actions">
          <button type="button" data-action="edit-card" data-card="${escapeHtml(JSON.stringify(card))}">${t("Edit As Draft")}</button>
          <button type="button" class="danger" data-action="delete-card" data-symbol="${escapeHtml(card.symbol)}">${t("Delete")}</button>
        </div>
      </div>
    `)
    .join("");
}

function renderTrades(trades, reconciliation = {}) {
  state.latest.tradeReconciliation = reconciliation;
  const summary = renderTradeReconciliation(reconciliation);
  if (!trades.length) {
    els.tradesView.innerHTML = `${summary}<div class="empty">${t("No trades imported.")}</div>`;
    return;
  }
  els.tradesView.innerHTML = summary + trades
    .slice(-8)
    .reverse()
    .map((trade) => `
      <div class="item">
        <strong>${escapeHtml(trade.symbol)} - ${escapeHtml(localizeText(trade.action))} - ${Number(trade.amount || 0).toFixed(2)}</strong>
        <div class="muted">${escapeHtml(trade.traded_at || "")} / ${t("qty")} ${trade.quantity} / ${t("price")} ${trade.price} / ${t("fee")} ${trade.fee}</div>
        <div>${escapeHtml(trade.note || "")}</div>
      </div>
    `)
    .join("");
}

function renderTradeReconciliation(reconciliation = {}) {
  const totals = reconciliation.totals || {};
  const warnings = reconciliation.warnings || [];
  return `
    <div class="item">
      <strong>${t("Trade Reconciliation")}</strong>
      <div class="muted">
        ${t("Cash Flow")} ${Number(totals.cash_flow || 0).toFixed(2)}
        / ${t("Realized PnL")} ${Number(totals.realized_pnl || 0).toFixed(2)}
        / ${t("Unrealized PnL")} ${Number(totals.unrealized_pnl || 0).toFixed(2)}
      </div>
      <div class="muted">
        ${t("Open Positions")} ${totals.open_position_count || 0}
        / ${t("Fees")} ${Number(totals.fees || 0).toFixed(2)}
        / ${t("Trades")} ${totals.trade_count || 0}
      </div>
      <div class="muted">${warnings.length ? warnings.map(localizeText).map(escapeHtml).join("<br />") : t("No reconciliation warning.")}</div>
    </div>
  `;
}

function renderPositions(positions) {
  const values = Object.values(positions);
  if (!values.length) {
    els.positionsView.innerHTML = `<div class="empty">${t("No position yet.")}</div>`;
    return;
  }
  els.positionsView.innerHTML = values
    .map((position) => {
      const marketValue = Number(position.quantity || 0) * Number(position.current_price || 0);
      const pnl = marketValue - Number(position.quantity || 0) * Number(position.cost_price || 0);
      return `
        <div class="item">
          <strong>${escapeHtml(position.symbol)} - ${escapeHtml(position.name)}</strong>
          <div class="muted">${escapeHtml(localizeText(position.asset_type || ""))} / ${escapeHtml(position.market)} / ${escapeHtml(position.sector)} / ${escapeHtml(position.theme)} / ${escapeHtml(position.currency)}</div>
          <div>${t("Market value")} ${marketValue.toFixed(2)}, ${t("PnL")} ${pnl.toFixed(2)}</div>
          <div class="item-actions">
            <button type="button" data-action="edit-position" data-position="${escapeHtml(JSON.stringify(position))}">${t("Edit")}</button>
            <button type="button" class="danger" data-action="delete-position" data-symbol="${escapeHtml(position.symbol)}">${t("Delete")}</button>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderPositionGuard(report) {
  const sections = [
    [t("Single"), report.positions || []],
    [t("Sector"), report.sectors || []],
    [t("Theme"), report.themes || []],
    [t("Market"), report.markets || []],
    [t("Currency"), report.currencies || []],
  ];
  const warnings = report.warnings || [];
  els.positionGuardView.innerHTML = `
    <div class="item">
      <strong>${t("Total market value")} ${Number(report.total_market_value || 0).toFixed(2)}</strong>
      <div class="muted">${warnings.length ? warnings.map(localizeText).map(escapeHtml).join("; ") : t("No exposure warning.")}</div>
    </div>
    ${sections
      .map(([title, items]) => `
        <div class="item">
          <strong>${title}</strong>
          <div class="muted">${items.map((item) => `${escapeHtml(item.key)} ${item.percent}% ${escapeHtml(localizeText(item.status))}`).join(" / ") || t("None")}</div>
        </div>
      `)
      .join("")}
  `;
}

function renderAuditResult(result) {
  const all = [...(result.violations || []), ...(result.warnings || [])];
  els.auditResult.innerHTML = `
    <div class="item">
      <span class="badge ${result.status}">${badgeText(result.status)}</span>
      <p class="muted">${t("Decision ID")}: ${escapeHtml(result.decision_id)}</p>
    </div>
    ${renderReferencedEvidence(result.referenced_evidence_items || [])}
    ${all.map(renderFinding).join("") || `<div class="item">${t("No discipline issue found.")}</div>`}
    ${renderRuleResults(result.rule_results || [])}
  `;
}

function renderReferencedEvidence(items) {
  if (!items.length) return "";
  return `
    <details class="rule-results" open>
      <summary>${t("Referenced Evidence")} (${items.length})</summary>
      ${items
        .map((item) => `
          <div class="item">
            <strong>${escapeHtml(item.symbol)} / ${escapeHtml(localizeText(item.evidence_type))} / ${escapeHtml(item.title)}</strong>
            <div>${escapeHtml(item.content)}</div>
            <div class="muted">${escapeHtml(item.source || "")} ${escapeHtml(item.source_date || "")}</div>
          </div>
        `)
        .join("")}
    </details>
  `;
}

function renderViolations(violations) {
  if (!violations.length) {
    els.violationsView.innerHTML = `<div class="empty">${t("No violation recorded.")}</div>`;
    return;
  }
  els.violationsView.innerHTML = violations
    .slice(-8)
    .reverse()
    .map((item) => renderFinding(item, true))
    .join("");
}

function renderReview(review) {
  const forbidden = review.next_month_forbidden_behaviors || [];
  const types = Object.entries(review.violation_types || {});
  els.reviewView.innerHTML = `
    <div class="item">
      <strong>${escapeHtml(review.month || state.month)} ${t("Review")}</strong>
      <div class="muted">${t("Score")} ${review.discipline_score ?? "--"}, ${t("pass rate")} ${review.pass_rate ?? "--"}%, ${t("decisions")} ${review.decision_count ?? 0}</div>
    </div>
    <div class="item">
      <strong>${t("Violation Types")}</strong>
      <div class="muted">${types.map(([key, value]) => `${escapeHtml(localizeText(key))}: ${value}`).join(" / ") || t("None")}</div>
    </div>
    <div class="item">
      <strong>${t("Next-month forbidden behaviors")}</strong>
      <div class="muted">${localizeList(forbidden) || t("None")}</div>
    </div>
  `;
}

function renderScoreBreakdown(scoreReport) {
  const dimensions = scoreReport.dimensions || {};
  const items = Object.entries(dimensions);
  if (!items.length) return;
  els.reviewView.innerHTML += `
    <div class="item">
      <strong>${t("Score Breakdown")}</strong>
      <div class="muted">
        ${items
          .map(([key, value]) => `${escapeHtml(localizeText(key))} ${value.score}/${value.weight}`)
          .join(" / ")}
      </div>
    </div>
  `;
}

function renderAttribution(attribution) {
  const buckets = ["market", "security", "portfolio", "behavior"];
  if (!buckets.some((bucket) => attribution[bucket])) return;
  els.reviewView.innerHTML += `
    <div class="item">
      <strong>${t("Attribution")}</strong>
      <div class="muted">
        ${buckets
          .map((bucket) => escapeHtml(localizeText(attribution[bucket]?.summary || `No ${bucket} attribution issue recorded.`)))
          .join("<br />")}
      </div>
    </div>
  `;
}

function renderRuleSuggestions(suggestions) {
  if (!suggestions.length) return;
  els.reviewView.innerHTML += `
    <div class="item">
      <strong>${t("Rule Revision Suggestions")}</strong>
      <div class="muted">
        ${suggestions
          .map((item) => `${escapeHtml(localizeText(item.scope))} / ${escapeHtml(localizeText(item.trigger))}: ${escapeHtml(localizeText(item.suggestion))}`)
          .join("<br />")}
      </div>
    </div>
  `;
}

function renderReviewSnapshots(snapshots) {
  if (!snapshots.length) {
    els.reviewSnapshotsView.innerHTML = `<div class="empty">${t("No review snapshot saved.")}</div>`;
    return;
  }
  els.reviewSnapshotsView.innerHTML = `
    <div class="item">
      <strong>${t("Saved Review Snapshots")}</strong>
      <div class="muted">${snapshots.length}</div>
    </div>
    ${snapshots
      .map((snapshot) => {
        const statusText =
          Object.entries(snapshot.status_summary || {})
            .map(([key, value]) => `${escapeHtml(localizeText(key))} ${value}`)
            .join(" / ") || t("None");
        return `
          <div class="item">
            <strong>${t("Snapshot")} ${escapeHtml(snapshot.period || state.month)} / ${snapshot.discipline_score}</strong>
            <div class="muted">${t("Created")}: ${escapeHtml(snapshot.created_at || "")}</div>
            <div class="muted">${t("decisions")} ${snapshot.decision_count ?? 0} / ${statusText}</div>
            <div class="item-actions">
              <button type="button" data-action="export-review" data-id="${escapeHtml(snapshot.id)}">${t("Export Markdown")}</button>
            </div>
            ${renderSnapshotDrilldown(snapshot.review?.drilldown)}
          </div>
        `;
      })
      .join("")}
  `;
}

function renderReviewReports(reports) {
  if (!reports.length) {
    els.reviewReportsView.innerHTML = `<div class="empty">${t("No exported report yet.")}</div>`;
    return;
  }
  els.reviewReportsView.innerHTML = `
    <div class="item">
      <strong>${t("Report Library")}</strong>
      <div class="muted">${reports.length}</div>
    </div>
    ${reports.map((report) => `
      <div class="item">
        <strong>${escapeHtml(report.title || report.filename)}</strong>
        <div class="muted">${escapeHtml(report.path || "")}</div>
        <div class="muted">${escapeHtml(report.modified_at || "")} / ${report.bytes || 0} ${t("bytes")} / ${escapeHtml(localizeText(report.snapshot_id || "no snapshot id"))}</div>
        ${
          report.snapshot_id
            ? `<div class="item-actions"><button type="button" data-action="export-review" data-id="${escapeHtml(report.snapshot_id)}">${t("Regenerate")}</button></div>`
            : ""
        }
      </div>
    `).join("")}
  `;
}

function renderReviewCompareOptions(snapshots) {
  const options = snapshots
    .map((snapshot) => {
      const label = `${snapshot.period} / ${snapshot.discipline_score} / ${snapshot.id.slice(0, 8)}`;
      return `<option value="${escapeHtml(snapshot.id)}">${escapeHtml(label)}</option>`;
    })
    .join("");
  els.reviewCompareForm.elements.left_snapshot_id.innerHTML = options;
  els.reviewCompareForm.elements.right_snapshot_id.innerHTML = options;
  els.reviewCompareForm.querySelector("button").disabled = snapshots.length < 2;
  if (snapshots.length >= 2) {
    els.reviewCompareForm.elements.left_snapshot_id.value = snapshots[1].id;
    els.reviewCompareForm.elements.right_snapshot_id.value = snapshots[0].id;
  }
  if (snapshots.length < 2) {
    els.reviewCompareView.innerHTML = `<div class="empty">${t("Need at least two snapshots to compare.")}</div>`;
  }
}

function renderReviewComparison(comparison) {
  const delta = comparison.delta || {};
  const ruleSuggestions = comparison.rule_suggestions || {};
  els.reviewCompareView.innerHTML = `
    <div class="item">
      <strong>${t("Snapshot Comparison")}: ${escapeHtml(comparison.left.period)} -> ${escapeHtml(comparison.right.period)}</strong>
      <div class="muted">${t("Trend")}: ${escapeHtml(localizeText(comparison.interpretation || "mixed"))}</div>
      <div class="muted">${t("Score")} ${formatDelta(delta.discipline_score)} / ${t("pass rate")} ${formatDelta(delta.pass_rate)} / ${t("decisions")} ${formatDelta(delta.decision_count)} / ${t("violation weight")} ${formatDelta(delta.violation_weight)}</div>
    </div>
    <div class="item">
      <strong>${t("Status Counts")}</strong>
      <div class="muted">${formatDeltaMap(delta.status_counts || {})}</div>
    </div>
    <div class="item">
      <strong>${t("Violation Types")}</strong>
      <div class="muted">${formatDeltaMap(delta.violation_types || {})}</div>
    </div>
    <div class="item">
      <strong>${t("Repeated Symbols")}</strong>
      <div class="muted">${formatRepeatedSymbols(comparison.repeated_symbols || [])}</div>
    </div>
    <div class="item">
      <strong>${t("Rule Suggestion Changes")}</strong>
      <div class="muted">${t("persistent")} ${ruleSuggestions.persistent?.length || 0} / ${t("added")} ${ruleSuggestions.added?.length || 0} / ${t("removed")} ${ruleSuggestions.removed?.length || 0}</div>
      ${renderSuggestionList("Added", ruleSuggestions.added || [])}
      ${renderSuggestionList("Removed", ruleSuggestions.removed || [])}
    </div>
  `;
}

function formatDelta(value) {
  const numberValue = Number(value || 0);
  if (numberValue > 0) return `+${numberValue}`;
  return `${numberValue}`;
}

function formatDeltaMap(items) {
  const entries = Object.entries(items || {});
  if (!entries.length) return t("None");
  return entries.map(([key, value]) => `${escapeHtml(localizeText(key))} ${formatDelta(value)}`).join(" / ");
}

function formatRepeatedSymbols(items) {
  if (!items.length) return t("None");
  return items
    .map((item) => `${escapeHtml(item.symbol)} ${item.left_violations}->${item.right_violations} (${formatDelta(item.delta)})`)
    .join(" / ");
}

function renderSuggestionList(label, items) {
  if (!items.length) return "";
  return `
    <details class="rule-results">
      <summary>${t(label)} (${items.length})</summary>
      ${items.map((item) => `
        <div class="item">
          <strong>${escapeHtml(localizeText(item.scope || ""))} / ${escapeHtml(localizeText(item.trigger || ""))}</strong>
          <div>${escapeHtml(localizeText(item.suggestion || ""))}</div>
        </div>
      `).join("")}
    </details>
  `;
}

function renderSnapshotDrilldown(drilldown) {
  if (!drilldown) return "";
  const decisions = drilldown.decisions || [];
  const auditsByDecision = Object.fromEntries(
    (drilldown.audits || []).map((audit) => [audit.decision_id, audit])
  );
  const rulesByDecision = groupBy(drilldown.rule_results || [], "decision_id");
  const violationsByDecision = groupBy(drilldown.violations || [], "decision_id");
  const evidenceById = Object.fromEntries(
    (drilldown.evidence_items || []).map((item) => [item.id, item])
  );
  return `
    <details class="rule-results">
      <summary>${t("Snapshot Drill-down")} (${decisions.length})</summary>
      ${decisions.length ? decisions.map((decision) => {
        const audit = auditsByDecision[decision.id] || {};
        const evidenceItems = (decision.referenced_evidence_ids || [])
          .map((id) => evidenceById[id])
          .filter(Boolean);
        return `
          <div class="item">
            <strong>${escapeHtml(decision.symbol)} - ${escapeHtml(localizeText(decision.action))} - <span class="badge ${audit.status || "WARN"}">${badgeText(audit.status || "UNKNOWN")}</span></strong>
            <div class="muted">${escapeHtml(decision.created_at || "")} / ${escapeHtml(localizeText(decision.emotion || ""))} / ${t("after")} ${decision.position_after_pct ?? "--"}%</div>
            <div>${escapeHtml(decision.reason || "")}</div>
            ${renderSnapshotEvidence(evidenceItems)}
            ${renderSnapshotViolations(violationsByDecision[decision.id] || [])}
            ${renderRuleResults(rulesByDecision[decision.id] || [])}
          </div>
        `;
      }).join("") : `<div class="empty">${t("No decision history.")}</div>`}
    </details>
  `;
}

function renderSnapshotEvidence(items) {
  if (!items.length) return "";
  return `
    <details class="rule-results">
      <summary>${t("Referenced Evidence")} (${items.length})</summary>
      ${items.map((item) => `
        <div class="item">
          <strong>${escapeHtml(item.symbol)} / ${escapeHtml(localizeText(item.evidence_type))} / ${escapeHtml(item.title)}</strong>
          <div>${escapeHtml(item.content || "")}</div>
          <div class="muted">${escapeHtml(item.source || "")} ${escapeHtml(item.source_date || "")}</div>
        </div>
      `).join("")}
    </details>
  `;
}

function renderSnapshotViolations(items) {
  if (!items.length) return "";
  return `
    <details class="rule-results">
      <summary>${t("Violations")} (${items.length})</summary>
      ${items.map((item) => renderFinding(item, false)).join("")}
    </details>
  `;
}

function renderHistory(decisions, audits, ruleResults) {
  const auditById = Object.fromEntries(audits.map((audit) => [audit.decision_id, audit]));
  const ruleResultsByDecision = groupBy(ruleResults, "decision_id");
  if (!decisions.length) {
    els.historyView.innerHTML = `<div class="empty">${t("No decision history.")}</div>`;
    return;
  }
  els.historyView.innerHTML = decisions
    .slice(-10)
    .reverse()
    .map((decision) => {
      const audit = auditById[decision.id] || {};
      return `
        <div class="item">
          <strong>${escapeHtml(decision.symbol)} - ${escapeHtml(localizeText(decision.action))} - <span class="badge ${audit.status || "WARN"}">${badgeText(audit.status || "UNKNOWN")}</span></strong>
          <div class="muted">${escapeHtml(decision.created_at)} / ${t("after")} ${decision.position_after_pct}% / ${escapeHtml(localizeText(decision.emotion))}</div>
          <div>${escapeHtml(decision.reason)}</div>
          ${renderRuleResults(ruleResultsByDecision[decision.id] || [])}
        </div>
      `;
    })
    .join("");
}

function renderRuleResults(items) {
  if (!items.length) return "";
  return `
    <details class="rule-results">
      <summary>${t("Rule Results")} (${items.length})</summary>
      ${items
        .slice()
        .sort((a, b) => String(a.rule_code).localeCompare(String(b.rule_code)))
        .map((item) => `
          <div class="item">
            <strong>${escapeHtml(item.rule_code)} <span class="badge ${escapeHtml(item.status)}">${badgeText(item.status)}</span></strong>
            <div class="muted">${escapeHtml(localizeText(item.rule_name || ""))} / ${escapeHtml(localizeText(item.category || "general"))} / ${escapeHtml(localizeText(item.severity || "info"))}</div>
            <div>${escapeHtml(localizeText(item.message || ""))}</div>
            <div class="muted">${t("Params")}: ${escapeHtml(JSON.stringify(item.params || {}))}</div>
          </div>
        `)
        .join("")}
    </details>
  `;
}

function groupBy(items, key) {
  return items.reduce((acc, item) => {
    const value = item[key];
    if (!acc[value]) acc[value] = [];
    acc[value].push(item);
    return acc;
  }, {});
}

function renderSymbolOptions(cards) {
  state.latest.cards = cards || {};
  const symbols = Object.keys(cards);
  if (!symbols.length) {
    els.decisionSymbol.innerHTML = `<option value="SAMPLE">SAMPLE</option>`;
    return;
  }
  const current = els.decisionSymbol.value;
  els.decisionSymbol.innerHTML = symbols
    .map((symbol) => `<option value="${escapeHtml(symbol)}">${escapeHtml(symbol)} · ${escapeHtml(cards[symbol].name)}</option>`)
    .join("");
  if (symbols.includes(current)) els.decisionSymbol.value = current;
}

function syncEvidenceSymbolSelects(cards) {
  const symbols = Object.keys(cards || {});
  const optionHtml = symbols.length
    ? symbols
        .map((symbol) => `<option value="${escapeHtml(symbol)}">${escapeHtml(symbol)} · ${escapeHtml(localizeText(cards[symbol].name || ""))}</option>`)
        .join("")
    : `<option value="SAMPLE">${t("SAMPLE")}</option>`;
  [els.evidenceSymbol, els.evidenceFilterSymbol].forEach((select) => {
    if (!select) return;
    const current = select.value;
    select.innerHTML = select === els.evidenceFilterSymbol
      ? `<option value="">${t("All Symbols")}</option>${optionHtml}`
      : optionHtml;
    if (symbols.includes(current) || (select === els.evidenceFilterSymbol && current === "")) {
      select.value = current;
    }
  });
}

function renderFinding(item, withActions = false) {
  return `
    <div class="item">
      <strong>${escapeHtml(localizeText(item.type))} <span class="muted">(${escapeHtml(localizeText(item.severity))} / ${escapeHtml(localizeText(item.category || "general"))} / ${t("weight")} ${item.weight || 0})</span></strong>
      <div>${escapeHtml(localizeText(item.message))}</div>
      <div class="muted">${t("Fix")}: ${escapeHtml(localizeText(item.remediation || "Review and document the decision."))}</div>
      <div class="muted">${escapeHtml(item.rule_id || "")}${item.status ? ` / ${escapeHtml(localizeText(item.status))}` : ""}</div>
      ${
        withActions && item.id && item.status !== "resolved"
          ? `<div class="item-actions"><button type="button" data-action="resolve-violation" data-id="${escapeHtml(item.id)}">${t("Mark Resolved")}</button></div>`
          : ""
      }
    </div>
  `;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(localizeText(result.error || "Request failed"));
  return result;
}

function fillGeneratorForm(card) {
  fillForm(els.generatorForm, {
    template: "value",
    symbol: card.symbol,
    name: card.name,
    sector: card.sector,
    max_position_pct: card.max_position_pct,
    review_cycle: card.review_cycle,
    why_buy: (card.thesis || []).join("\n"),
    no_buy: (card.no_buy_conditions || []).join("\n"),
    add_when: (card.add_conditions || []).join("\n"),
    reduce_when: (card.reduce_conditions || []).join("\n"),
    invalid_when: (card.invalid_conditions || []).join("\n"),
    raise_position: (card.raise_position_conditions || []).join("\n"),
    lower_position: (card.lower_position_conditions || []).join("\n"),
    forbidden_behaviors: (card.forbidden_behaviors || []).join("\n"),
  });
}

function fillForm(form, values) {
  Object.entries(values).forEach(([key, value]) => {
    const field = form.elements[key];
    if (!field) return;
    if (field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = value ?? "";
    }
  });
}

function text(form, key) {
  return String(form.get(key) || "").trim();
}

function number(form, key) {
  return Number(form.get(key) || 0);
}

function lines(form, key) {
  return String(form.get(key) || "")
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function wizardLines(form, key) {
  const selected = form
    .getAll(`${key}__option`)
    .map((item) => String(item).trim())
    .filter(Boolean);
  return uniqueLines([...selected, ...lines(form, key)]);
}

function uniqueLines(values) {
  const seen = new Set();
  return values.filter((value) => {
    const key = value.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

applyLanguage();
loadDashboard();
