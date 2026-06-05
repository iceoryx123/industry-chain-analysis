# Industry Chain Analysis Framework

> **认知辅助工具** – 通过结构化的产业链 / 价值网框架，帮助分析师快速定位价值枢纽、评估枢纽质量、判断行业拐点。

## 📂 目录结构（已落地）
```
industry-chain-analysis/
├─ README.md                 # 本文件
├─ LICENSE
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ SKILL.md                  # 技能入口（兼容旧版）
├─ docs/                     # 设计文档 & 使用指南
│   ├─ design/architecture.md
│   └─ guides/version-selection.md   # **何时选 v9.2，何时选 v10.x**
├─ theory/                   # 框架、模型、评分规则（按版本）
│   ├─ v9.2/
│   └─ v10.x/
├─ data/                     # 结构化指标 & 行业元数据
│   ├─ meta/                 # 每个行业的 metadata.yaml
│   └─ indicators/           # 按行业 code 保存的 CSV（占位或真实数据）
├─ cases/                    # 案例库（已按照行业层级重构）
│   └─ by-industry/
│       ├─ 01‑Traditional/
│       │   └─ healthcare/0101‑儿科医院/case.md
│       ├─ 02‑Platform/…
│       ├─ 03‑Regulated/…
│       └─ 04‑Emerging/…
├─ templates/                # 案例/指标模板
│   └─ indicators_template.yaml
├─ scripts/                  # ETL / 数据生成脚本
│   └─ etl_indicators.py
└─ .github/workflows/ci.yml  # CI 包含元数据、版本、markdown lint 检查
```

## 🚀 快速上手
1. **克隆仓库**
   ```bash
   git clone https://github.com/iceoryx123/industry-chain-analysis.git
   cd industry-chain-analysis
   ```
2. **查看案例**
   ```bash
   # 例如打开儿科医院案例
   less cases/by-industry/01‑Traditional/healthcare/0101‑儿科医院/case.md
   ```
3. **使用脚本生成占位指标**（后续可自行替换为真实抓取）
   ```bash
   python3 scripts/etl_indicators.py
   ```
   程序会在 `data/indicators/` 下为每个行业生成一个基本 CSV。
4. **阅读设计文档**
   - `docs/design/architecture.md` – 框架全景与评分模型
   - `docs/guides/version-selection.md` – **何时选 v9.2 / v10.x**（决策树版）

## 📈 数据更新与对比
- **定期更新**：依据每个行业的 `update_cycle`（quarterly、monthly 等），自行运行 `etl_indicators.py` 或接入自定义抓取脚本。
- **对比仪表盘**：在 `cases/comparison/`（后续脚本生成）可查看横向（跨行业）与纵向（跨时间）指标对比。

## 🛠️ 贡献指南
请阅读 `CONTRIBUTING.md`，其中包括：
- 新增行业/案例的目录规范
- 统一的 `indicators.yaml`/`case.md` 头部格式
- CI 检查要求（metadata、version）

## 📦 Release & Versioning
- **语义化版本**：`v9.2.x`（传统框架） vs `v10.x.x`（双模框架）。
- 每次发布会自动生成 GitHub Release（含 CHANGELOG、核心文件 zip）。

---

© 2024‑2026 iceoryx123 – MIT License
