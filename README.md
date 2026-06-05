# 🏭 产业链结构性分析

> **认知辅助工具** — 基于申万一级行业分类（2024版）的产业链分析框架
>
> 定位：帮助分析师快速定位价值枢纽、评估枢纽质量、判断行业拐点

---

## 📋 一览

| 项目 | 说明 |
|------|------|
| 📦 最新版本 | v10.5.1 |
| 🏭 行业覆盖 | **32个申万一级行业**（四大类别） |
| 📊 案例规模 | **32个案例**（11个深度分析 + 21个模板框架） |
| 🤖 自动化 | GitHub Actions 全链路 CI/CD，每日 UTC 03:00 自动更新 |
| 🔌 数据源 | akshare（A股财务）+ yfinance（全球）+ pytrends（可选，全免费） |
| 📄 许可证 | MIT |

---

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/iceoryx123/industry-chain-analysis.git
cd industry-chain-analysis

# 2. 安装依赖
pip install -r requirements.txt

# 3. 查看行业列表
python scripts/render_cases.py           # 渲染案例指标
python scripts/generate_insights_template.py  # 生成洞见
python scripts/generate_comparison.py   # 生成对比仪表盘

# 4. 打开仪表盘
open cases/comparison/overview.html
```

---

## 🏗️ 行业分类体系

四大类别，32个行业：

### 🏭 01-Traditional（传统线性产业链）— 20个

农林牧渔、基础化工、钢铁、有色金属、电子、汽车、建筑装饰、建筑材料、机械设备、电力设备、医药生物、轻工制造、纺织服饰、交通运输、石油石化、综合、**美容护理**、**家用电器**、**商贸零售**、**食品饮料**

### 🌐 02-Platform（网络效应平台）— 4个

计算机、传媒、社会服务、通信

### 🏛️ 03-Regulated（政策驱动）— 5个

银行、非银金融、房地产、公用事业、环保

### 🚀 04-Emerging（新兴跨界）— 3个

国防军工、煤炭、机器人

---

## 📂 目录结构

```
industry-chain-analysis/
│
├── cases/by-industry/           ← 📁 案例库（按四大类别分目录）
│   ├── 01-Traditional/          # 20个传统行业
│   │   ├── healthcare/801150-医药生物/   # 深度分析
│   │   ├── food-beverage/801750-食品饮料/ # 深度分析
│   │   ├── chemicals-new-materials/801020-基础化工/ # 深度分析
│   │   ├── agriculture-food/801010-农林牧渔/ # 深度分析
│   │   ├── electronics/801050-电子/      # 深度分析
│   │   ├── machinery-equipment/801110-机械设备/ # 深度分析
│   │   ├── textile-apparel/801200-纺织服饰/ # 深度分析
│   │   ├── transportation/801230-交通运输/ # 模板
│   │   └── ...（共12个深度分析 + 8个模板）
│   ├── 02-Platform/              # 4个平台型行业（全部模板）
│   │   ├── computing-software/801060-计算机/
│   │   ├── media-internet/801090-传媒/
│   │   ├── social-services-platform/801130-社会服务/
│   │   └── telecom-network/801170-通信/
│   ├── 03-Regulated/             # 5个监管型行业
│   │   ├── banking/801140-银行/         # 深度分析
│   │   ├── non-bank-finance/801160-非银金融/ # 深度分析
│   │   ├── real-estate/801180-房地产/     # 深度分析
│   │   ├── utilities/801190-公用事业/     # 深度分析
│   │   └── environmental-protection/801220-环保/ # 模板
│   └── 04-Emerging/              # 3个新兴行业
│       ├── defense-aviation/801710-国防军工/ # 深度分析
│       ├── coal-resource/801790-煤炭/     # 深度分析
│       └── robotics/801880-机器人/        # 模板
│   └── comparison/overview.html  # 对比仪表盘
│
├── data/                        ← 📊 结构化数据
│   ├── meta/*.yaml              #    32个行业元数据
│   └── indicators/*.csv         #    指标数据（毛利率/ROE等）
│
├── scripts/                     ← 🔄 自动化脚本
│   ├── fetch_real_data.py       #    akshare 多股平均抓取
│   ├── render_cases.py          #    渲染 {{ indicator.xxx }}
│   ├── generate_insights_template.py  # 规则式洞见
│   ├── generate_comparison.py   #    对比仪表盘
│   ├── generate_v9_cases.py     #    v9.2 案例生成（Jinja2）
│   ├── generate_v10_cases.py    #    v10.x 案例生成（Jinja2）
│   └── template_utils.py        #    Jinja2 渲染工具
│
├── theory/                      ← 📖 理论文档
│   ├── v9.2/                    #    传统四层链分析框架
│   └── v10.x/                   #    双模框架（价值链+价值网）
│
├── templates/                   ← 📋 案例模板（Jinja2）
├── .github/workflows/           # CI 配置
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE (MIT)
```

---

## 🧠 核心工作流

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  fetch      │ ──► │  render      │ ──► │  insights    │
│  (akshare)  │     │  (Jinja2)    │     │  (规则引擎)  │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
┌─────────────┐     ┌──────────────┐              │
│  CI/CD      │ ◄── │  dashboard   │ ◄────────────┘
│  (Actions)  │     │  (HTML)      │
└─────────────┘     └──────────────┘
```

### 数据源

| 数据 | 来源 | 费用 |
|------|------|:----:|
| A股财务指标（毛利率、ROE） | akshare | ✅ 免费 |
| 行业规模估算 | 代表股营收 × 倍数 | ✅ 免费 |
| 网络热度（可选） | pytrends | ✅ 免费 |
| 全球市场数据（可选） | yfinance | ✅ 免费 |

### 洞见评分模型

基于规则的四段式输出（无需 LLM，零成本）：

```
① 护城河（毛利率）→ 0-10分    权重30%
② 定价权（ROE）   → 0-10分    权重25%
③ 替代难度（研发） → 0-10分    权重25%
④ 生态位（网络效应）→ 0-10分   权重20%
```

> 银行/非银金融等特殊行业使用代理指标（净息差/营业利润率）

---

## 📊 当前评分分布（2026-06）

```
🏆 3.9  食品饮料    （双汇+茅台，毛利率54.7% ROE 8.2%）
   3.6  医药生物    （爱尔+恒瑞+药明，毛利率61.6% ROE 5.0%）
   3.4  公用事业    （长江电力，毛利率55.6%）
   3.1  交通运输    （中远海能，毛利率42.7%）
   3.0  机器人      （汇川技术，毛利率29.1%）
   ...
📉 1.0  国防军工    （低毛利行业特性）
   1.0  钢铁        （低毛利行业特性）
   1.0  建筑装饰    （低毛利行业特性）
   1.0  综合        （多元化折价）
```

---

## 🤖 CI/CD 自动化

| 工作流 | 触发 | 做的事 |
|--------|------|--------|
| **CI 全链路** | 每日 03:00 UTC + Push | 抓取 → 渲染 → 洞见 → 仪表盘 → 自动提交 |
| **Release** | 推送 tag | 自动创建 GitHub Release |

当前状态：[![CI](https://github.com/iceoryx123/industry-chain-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/iceoryx123/industry-chain-analysis/actions/workflows/ci.yml)

---

## 🧭 理论框架

- **v9.2** — 传统价值链分析（四层链：时间定位→空间定位→枢纽识别→价值评估）
- **v10.x** — 双模框架：价值链 + 价值网（适用于平台/网络效应行业）

详见 `theory/` 目录。

---

## 📝 贡献指南

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

添加新行业只需：
1. 在 `data/meta/` 下创建 `{行业代码}.yaml`（含代表股 ticker）
2. 运行 `python scripts/fetch_real_data.py` 抓取数据
3. 运行全流水线生成案例

---

## 📄 许可证

MIT © 2024-2026 iceoryx123
