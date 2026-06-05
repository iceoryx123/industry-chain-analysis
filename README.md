# 🏭 产业链结构性分析

> **认知辅助工具** — 基于申万一级行业分类的产业链分析框架
>
> 定位：帮助分析师快速定位价值枢纽、评估枢纽质量、判断行业拐点

---

## 📋 一览

| 项目 | 说明 |
|------|------|
| 📦 版本 | v10.5.1 |
| 🏭 行业分类 | 申万一级行业（2021版，31个） |
| 📊 案例规模 | 26个案例，覆盖16个申万行业 |
| 🤖 自动化 | GitHub Actions 全链路 CI/CD |
| 🔌 数据源 | akshare + yfinance + 网页抓取（全免费） |
| 📄 许可证 | MIT |

---

## 🚀 30 秒上手

```bash
# 1. 克隆
git clone https://github.com/iceoryx123/industry-chain-analysis.git
cd industry-chain-analysis

# 2. 安装（推荐）
pip install -e ".[full]"

# 3. 查看行业一览
industry-chain list

# 4. 查看某个案例
industry-chain show 150000-01

# 5. 运行完整流水线（抓取→渲染→洞见→仪表盘）
make all
```

或者直接用 `Makefile`：

```
make install     # 安装依赖
make list        # 列出案例
make all         # 完整流水线
```

---

## 📂 新目录结构（重装版）

```
industry-chain-analysis/
│
├── industry_chain/              ← 📦 Python 包（统一入口）
│   ├── cli.py                   #    CLI：industry-chain run/list/show
│   ├── config.py                #    配置中心（环境变量 > YAML > 默认值）
│   ├── fetchers/                #    数据抓取器
│   ├── processors/              #    ETL / 渲染 / 验证
│   ├── analyzers/               #    评分模型 / 洞见生成
│   └── reporters/               #    对比仪表盘 / 报告
│
├── config/                      ← 🔧 可配置参数
│   └── scoring_rules.yaml       #     评分维度与权重（支持按行业覆盖）
│
├── cases/by-industry/           ← 📁 案例库（申万分类）
│   ├── 150000-医药生物/
│   │   ├── 150000-01-儿科医院/case.md
│   │   └── 150000-02-口腔医院/case.md
│   ├── 290000-计算机/
│   │   ├── 290000-11-互联网/case.md
│   │   └── ...
│   └── ...（共 16 个申万一级行业，26 个案例）
│
├── data/                        ← 📊 结构化数据
│   ├── meta/                    #    行业元数据 YAML
│   └── indicators/              #    指标 CSV（每日自动更新）
│
├── theory/                      ← 📖 理论文档
│   ├── v9.2/                    #    传统价值链框架
│   └── v10.x/                   #    双模框架（价值链+价值网）
│
├── scripts/                     ← 🔄 旧版脚本（向后兼容）
│
├── Makefile                     ← 🚀 一键命令（最推荐）
├── setup.py                     #  Python 包安装
├── SKILL.md                     #  技能入口
└── .github/workflows/           #  CI/CD 配置
    ├── ci.yml                   #   每日全链路自动化
    └── release.yml              #   标签自动 Release
```

---

## 🎮 CLI 使用指南

所有操作通过 `industry-chain` 命令或 `make` 完成。

### 查看

```bash
# 列出所有行业（按申万分组）
industry-chain list

# 查看单个案例详情（指标 + 摘要）
industry-chain show 150000-01

# 查看某个申万行业下的所有案例
industry-chain show 150000

# 列出某个行业
industry-chain list --industry 医药生物

# 质量检查
industry-chain validate
```

### 流水线

```bash
# 完整链条
industry-chain run all

# 分阶段执行
industry-chain run fetch      # 抓取数据（akshare/yfinance）
industry-chain run etl        # 合并去重
industry-chain run render     # 渲染 {{ indicator.xxx }}
industry-chain run insights   # 生成洞见
industry-chain run dashboard  # 对比仪表盘

# 流水线 + 自动 git push
industry-chain run all --push
```

### 开发

```bash
make install-dev   # 安装开发依赖
make test          # 运行测试
make lint          # 代码检查
make release TAG=v11.0.0  # 发版
```

---

## 🧠 核心架构设计

### 三条原则

1. **申万分类驱动** — 所有案例按申万一级行业代码组织，与金融数据源对齐
2. **配置>代码** — 评分规则、维度权重在 `config/scoring_rules.yaml` 中维护，无需改代码
3. **免费公开数据** — akshare + yfinance + 网页抓取，零 API 成本

### 评分模型

```
各维度（0-10） × 权重 → 综合评分（0-10）
      ↓
护城河（毛利率）   30%    ← 可配置
定价权（ROE）     25%
替代难度（研发）   25%
生态位（网络效应） 20%
```

权重可按申万行业覆盖：
- **290000-计算机** → 生态位权重提高到 35%
- **390000-机械设备** → 替代难度权重提高到 35%

### 洞见生成

基于规则的四段式输出（无需 LLM，零成本）：

```
① 价值枢纽识别    → 平台/品牌/龙头/关键环节
② 质量评分        → 各维度分数 + 综合分
③ 拐点信号        → 网络效应阶段 / 毛利率预警 / ROE警示
④ 业务启示        → 针对性建议
```

---

## 🤖 自动化 CI/CD

| 工作流 | 触发 | 做的事 |
|--------|------|--------|
| **CI 全链路** | 每日 03:00 UTC + Push | 抓取 → ETL → 渲染 → 洞见 → 仪表盘 |
| **Release** | 推送 tag | 自动创建 GitHub Release |
| **数据质量** | 每次 CI | 检查 CSV 完整性、案例文件存在性 |

---

## 📈 对比仪表盘

运行 `industry-chain run dashboard` 或 `make dashboard` 后：

```
cases/comparison/overview.html
```

在浏览器打开，即可查看：
- 所有行业核心指标对比柱状图
- 表格数据（带行业标签）
- 各维度最高/均值分布

---

## 🧭 理论框架

- **v9.2** — 传统价值链分析（波特的五力框架衍生）
- **v10.x** — 双模框架：价值链 + 价值网（平台/网络效应）

详见 `theory/` 目录。

---

## 📝 贡献指南

见 `CONTRIBUTING.md`。

新加案例只需：
1. 创建 `data/meta/{code}.yaml`（含申万分类）
2. 在 `cases/by-industry/` 下创建案例文件
3. CI 自动检测并渲染

---

## 📄 许可证

MIT © 2024-2026 iceoryx123
