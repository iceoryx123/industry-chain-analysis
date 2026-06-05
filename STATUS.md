# 项目状态看板

> 最后更新：2026-06-05

## 仓库信息

- **远程仓库**：https://github.com/iceoryx123/industry-chain-analysis
- **最新 commit**：`dc40f27` — feat: 申万一级行业分类(34行业) + 完整自动化流水线 + 洞见生成 + 对比仪表盘
- **文件总数**：307（不含 .git）
- **Git Tags**：`v9.2.0`、`v10.0.0`、`v10.2.0`、`v10.5.1`

---

## 行业覆盖（申万一级 2024 版，34 个）

| 类别 | 数量 | 行业代码范围 |
|------|:---:|------|
| 01-Traditional（传统线性产业链） | 16 | 801010–801230 |
| 02-Platform（网络效应平台） | 4 | 801060, 801090, 801130, 801170 |
| 03-Regulated（政策驱动） | 5 | 801140–801220 |
| 04-Emerging（新兴跨界） | 9 | 801710–801880+ |

所有 34 个行业均有 `cases/by-industry/{类别}/{子行业名}/{code}-行业名/case.md`。

---

## 目录结构总览

```
.
├── .github/workflows/ci.yml          # CI: 抓取→渲染→洞见→对比→自动提交
├── .github/workflows/release.yml     # Release 流程
├── cases/
│   ├── by-industry/                  # 34 行业案例（按四大类分目录）
│   └── comparison/overview.html      # 60 行业对比仪表盘（Bootstrap+Chart.js）
├── config/
├── data/
│   ├── indicators/                   # CSV 指标数据（待真实数据填充）
│   └── meta/*.yaml                   # 34 行业元数据
├── docs/
│   ├── design/architecture.md
│   └── guides/version-selection.md
├── industry_chain/                   # Python 分析库（fetchers/analyzers/models）
├── learn/cases/                      # 案例学习参考（原始 26 个旧案例）
├── scripts/
│   ├── fetch_public_financial.py     # akshare 财务数据抓取
│   ├── fetch_public_network.py       # pytrends 网络热度抓取
│   ├── etl_indicators.py             # 指标 ETL
│   ├── render_cases.py               # 案例渲染入口
│   ├── generate_insights_template.py # 洞见生成
│   ├── generate_comparison.py        # 对比仪表盘生成
│   ├── generate_sw_industry_meta.py  # 申万元数据生成
│   ├── migrate_old_cases_to_sw.py    # 旧案例迁移工具
│   ├── generate_v9_cases.py          # v9 案例生成
│   └── generate_v10_cases.py         # v10 案例生成
├── templates/
│   ├── case_template_v9.md
│   ├── case_template_v10.md
│   └── indicators_template.yaml
├── theory/
│   ├── v9.2/framework.md
│   ├── v9.2/revisions.md
│   └── v10.x/v10.5.1.md
│   └── v10.x/dual-mode.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE (MIT)
├── README.md
├── requirements.txt
└── setup.py
```

---

## 自动化流水线（scripts/）

| 脚本 | 功能 | 状态 |
|------|------|------|
| `fetch_public_financial.py` | akshare 抓取 A 股财务数据 | ✅ 完成 |
| `fetch_public_network.py` | pytrends 网络热度（优雅降级） | ✅ 完成 |
| `etl_indicators.py` | 标准化指标计算 | ✅ 完成 |
| `render_cases.py` | Jinja2 案例渲染 | ✅ 完成 |
| `generate_insights_template.py` | 规则式洞见生成 | ✅ 完成（需真实数据） |
| `generate_comparison.py` | HTML 对比仪表盘生成 | ✅ 完成 |
| `migrate_old_cases_to_sw.py` | 旧案例 → 申万结构迁移 | ✅ 完成 |

---

## 待办（优先级排序）

### 🔴 高优先级
1. **填充真实指标数据** — 当前 34 个行业的 CSV 数据为占位值（全 0），洞见评分全部为 1.0
   - 解除 akshare rate limit 或分批抓取
   - 目标：每个行业有毛利率/ROE/CR4/HHI 等真实指标

2. **CI 端到端验证** — 确认 GitHub Actions 能完整跑通
   - 推送一个小的指标数据变更，观察 Actions 状态

### 🟡 中优先级
3. **丰富 v9.2 案例库** — 传统行业案例需 ≥30 条有洞见的内容
   - 目前多数案例是自动生成模板，需要人工补充深度分析

4. **丰富 v10.x 案例库** — 平台/网络型案例需 ≥20 条
5. **跨行业类比分析模块** — 在案例中加入行业间类比

### 🟢 低优先级
6. **README 补全** — 快速开始、示例、贡献指南
7. **理论文档迭代** — v9.3/v10.6 深度补充
8. **行业覆盖审计** — 确认申万 2024 版 34 个行业无遗漏

---

## 关键技术决策

| 决策 | 说明 |
|------|------|
| 行业分类 | 申万一级 2024 版（34 个） |
| 行业代码 | 申万代码（801010–801890）作为 industry_code |
| 四大类别 | 01-Traditional / 02-Platform / 03-Regulated / 04-Emerging |
| 数据源 | akshare + yfinance + pytrends + web scraping（全免费） |
| 洞见生成 | 规则式（毛利率/ROE/CR4 阈值），不调用 LLM |
| 案例版本 | v9.2 用于线性产业链，v10.x 用于网络效应平台型 |
| 仪表盘 | Bootstrap + Chart.js，静态 HTML |

---

## 已知限制

- **洞见评分全为 1.0**：因 CSV 指标为占位值 0，规则式模块默认兜底评分
- **pytrends 本机不可用**：受限网络环境，CI 环境可用
- **yfinance rate limit**：akshare 部分 ticker 需容错处理
- **部分行业分类重叠**：如 "电力设备" 同时出现在 01-Traditional 和 04-Emerging（可接受，因分析视角不同）
