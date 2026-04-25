# TradingAgent AI Skill

这是一个 AI Skill——安装后，你的 AI 助手就能像一个专业的交易分析团队一样，对任意美股进行多维度分析：技术面、基本面、新闻舆情、市场情绪，最终输出明确的 Buy / Hold / Sell 交易决策。

一个完整的华尔街分析团队，现在跑在你的 IDE 里。

## 关于 TradingAgent

本 Skill 的构建参考了 [TradingAgents](https://github.com/TauricResearch/TradingAgents) —— 一个基于 LangGraph 的多智能体股票交易框架。TradingAgents 模拟真实交易公司的运作模式，部署专门的 LLM 驱动智能体团队（基本面分析师、情绪分析师、技术分析师、交易员、风险管理团队等）协同评估市场状况并做出交易决策。

本 Skill 将该框架的完整 6 阶段分析流水线封装为自包含的 Skill 指令，无需依赖原始代码库即可运行。

| 项目 | 内容 |
|------|------|
| 分析框架 | 6 阶段多智能体流水线 |
| 数据来源 | Yahoo Finance (yfinance) |
| 技术指标 | stockstats (RSI, MACD, Bollinger Bands, ATR 等) |
| 评级体系 | Buy / Overweight / Hold / Underweight / Sell |

## 能力概览

TradingAgent 包含 **4 项数据获取能力** + **6 阶段分析流水线**：

| 能力 | 你可以问 | 数据来源 |
|------|----------|----------|
| 股价行情 | "帮我看看 NVDA 最近半年的走势" | get_stock_data.py |
| 技术指标 | "AAPL 的 RSI 和 MACD 是多少？" | get_indicators.py |
| 公司基本面 | "TSLA 的财报数据怎么样？" | get_fundamentals.py |
| 新闻舆情 | "最近有什么关于 MSFT 的新闻？" | get_news.py |
| **完整交易分析** | **"帮我分析下英特尔，评估是否值得投资"** | **全部 4 个脚本 + 6 阶段流水线** |

## 6 阶段分析流水线

本 Skill 的核心是一套完整的多智能体分析流程，严格按顺序执行：

| 阶段 | 角色 | 说明 |
|------|------|------|
| Stage 1 | 分析师团队 (4 位) | 市场分析师、情绪分析师、新闻分析师、基本面分析师各出一份报告 |
| Stage 2 | 投研辩论 | 多头研究员 vs 空头研究员，基于 4 份报告进行结构化辩论 |
| Stage 3 | 研究总监 | 评估多空辩论，给出明确方向和投资计划 |
| Stage 4 | 交易员 | 将投资计划转化为具体交易提案（含仓位和入场点） |
| Stage 5 | 风控辩论 (3 方) | 激进派 vs 保守派 vs 中立派，三方评估交易风险 |
| Stage 6 | 投资组合经理 | 综合所有分析，给出最终评级和执行摘要 |

```
分析师团队 → 多空辩论 → 研究总监 → 交易员 → 风控辩论 → 投资组合经理
 (4份报告)    (Bull vs Bear)   (决策)    (交易提案)  (3方风控)   (最终评级)
```

## 数据脚本

`scripts/` 文件夹包含 4 个独立的 Python 数据获取脚本和 1 个共享模块：

| 脚本 | 功能 | 示例 |
|------|------|------|
| `get_stock_data.py` | OHLCV 价格数据 | `python get_stock_data.py NVDA 2025-07-01 2026-01-15` |
| `get_indicators.py` | 技术指标计算 (RSI, MACD, SMA 等) | `python get_indicators.py NVDA rsi,macd 2026-01-15 30` |
| `get_fundamentals.py` | 公司基本面 (财报、内部交易等) | `python get_fundamentals.py NVDA all --date 2026-01-15` |
| `get_news.py` | 股票新闻 & 全球宏观新闻 | `python get_news.py NVDA 2026-01-08 2026-01-15` |
| `_shared.py` | 共享模块 (缓存、重试、Ticker 复用) | 被其他脚本自动引用 |

脚本之间通过 `_shared.py` 共享 OHLCV 数据缓存和 `yf.Ticker` 对象缓存，避免重复下载相同数据。

## 使用方式

直接告诉你的 AI 助手：

> 帮我分析下英伟达最近的股价，评估是否值得投资

AI 助手会自动调用 TradingAgent Skill，运行完整的 6 阶段分析流程，最终输出类似这样的结论：

```
============================================
FINAL TRADING DECISION: NVDA
Date: 2026-04-25
Rating: **OVERWEIGHT**
============================================
Executive Summary: ...
Key Catalysts: ...
Key Risks: ...
============================================
```

## 安装

### 最简单的方式：告诉你的 AI 助手

直接拷贝下面这句话发给你的 AI 助手：

> 帮我安装 TradingAgent Skill，仓库地址：https://github.com/your-repo/trading-agent-skill

Agent 会自动克隆仓库并安装到对应的 Skill 目录。

### 手动安装

将本仓库克隆到你项目下的 Skill 目录，不同 IDE 对应的路径：

| IDE | Skill 目录 |
|-----|-----------|
| Trae | `.trae/skills/trading-agent/` |
| Cursor | `.cursor/skills/trading-agent/` |
| Windsurf | `.windsurf/skills/trading-agent/` |
| Claude Code | `.claude/skills/trading-agent/` |
| 通用 | `.agents/skills/trading-agent/` |

```bash
# 示例：安装到 Trae
git clone https://github.com/your-repo/trading-agent-skill.git \
  .trae/skills/trading-agent
```

只要目录下有 `SKILL.md`，Agent 下次启动就会自动加载这个 Skill。

### 安装 Python 依赖

数据脚本需要以下 Python 包：

```bash
pip install yfinance stockstats pandas python-dateutil
```

## 目录结构

```
trading-agent/
├── SKILL.md                 # 核心文件：元数据 + 6 阶段 Agent 指令
├── scripts/                 # 数据获取脚本
│   ├── _shared.py           #   共享模块（缓存、重试、Ticker 复用）
│   ├── get_stock_data.py    #   OHLCV 价格数据
│   ├── get_indicators.py    #   技术指标计算
│   ├── get_fundamentals.py  #   公司基本面数据
│   └── get_news.py          #   新闻与舆情数据
└── README.md
```

## 支持的技术指标

| 类型 | 指标 |
|------|------|
| 移动平均线 | `close_50_sma`, `close_200_sma`, `close_10_ema` |
| MACD | `macd`, `macds`, `macdh` |
| 动量 | `rsi`, `mfi` |
| 波动率 | `boll`, `boll_ub`, `boll_lb`, `atr` |
| 成交量 | `vwma` |

## 致谢

- [TradingAgents](https://github.com/TauricResearch/TradingAgents) — 本 Skill 的架构参考来源，一个优秀的多智能体 LLM 金融交易框架
- [yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance 数据接口
- [stockstats](https://github.com/jealous/stockstats) — 技术指标计算库

## License

MIT
