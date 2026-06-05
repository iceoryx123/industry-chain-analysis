# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipelines
- Standard repository structure (docs/, theory/, cases/)
- Contributing guidelines
- **评分模型优化**: 多股加权平均（医药生物3股、食品饮料2股、国防军工2股等）
- **金融行业特殊处理**: 银行/非银金融使用代理毛利率（净息差/营业利润率）
- **标准模块体系 v1.0**: 新增理论文档 `theory/v10.x/standard-modules.md`
  - 模块A：商业模式分析（收入引擎/资产密度/客户结构/成本结构）
  - 模块B：护城河类型诊断（七种护城河分类体系）
  - 模块C：话语权地图（五力评估+利润池分布+行业四分类）
  - 模块D：现金流质量（CCC/FCF质量/CapEx/隐性负债）
  - 模块E：资本回报与增长定位（ROIC vs WACC/生命周期/政策敏感度）
- **模板升级**: v9.2 和 v10.x 模板均加入标准模块占位（原2-7节→2-10节）
- **数据时效标注系统**: 所有案例+仪表盘标注报告期和来源
- 交通运输深度分析（403行）
- 计算机 v10.x 双模分析（191行）

### Changed
- `scripts/fetch_real_data.py`: 支持多股平均 + parse_num + report_period 字段
- 评分分布从 1.0-3.4 扩展为 1.0-3.6（含趋势加减分）
- README 全面更新：32行业+准确目录+数据时效章节

## [10.5.1] - 2025-01-15

### Added
- Dual-mode analysis framework (Industry Chain + Value Network)
- 26 industry cases covering healthcare, finance, manufacturing, tech, etc.
- Theory library v10.x with dual-mode methodology
- Quick reference guide
- Cross-industry comparison framework

### Changed
- Migrated from v9.2 single-mode to v10 dual-mode architecture
- Restructured case library with industry categorization
- Enhanced value hub identification criteria

### Fixed
- Value network boundary detection for platform businesses
- Hub quality scoring edge cases

## [10.2.0] - 2024-10-20

### Added
- 8 new industry cases (AI, Robotics, Precision Instruments, etc.)
- Deep insights reference document
- Reverse assessment methodology
- Myth busting reference

### Changed
- Extended case library from 18 to 26 industries
- Improved version matrix documentation

## [10.0.0] - 2024-07-01

### Added
- **Breaking**: Dual-mode framework (Industry Chain + Value Network)
- Value network builder identification
- Ecosystem position mapping
- Network effects assessment

### Changed
- Complete architectural rewrite from v9 linear chain to dual-mode
- New output templates for dual-mode analysis
- Version selection guide updated

## [9.2.0] - 2024-03-15

### Added
- Traditional 4-layer industry chain framework (Upstream/Midstream/Downstream/Service)
- 18 foundational industry cases
- Version matrix for framework selection
- Case library index

### Changed
- Stabilized v9 analysis methodology
- Structured output templates

## [8.x] - 2023-2024

### Added
- Initial industry chain analysis framework
- Core concepts: value hub, profit pool, inflection point
- Early case studies

---

## Version Strategy

| Version Line | Status | Use Case |
|-------------|--------|----------|
| **v10.x** | 🟢 Active | Dual-mode (Chain + Network) — Internet, AI, Platform, Ecosystem businesses |
| **v9.2** | 🟡 Maintenance | Traditional 4-layer — Manufacturing, Consumer, Linear industries |
| **v8.x** | 🔴 Archived | Historical reference only |

See [Version Selection Guide](docs/guides/version-selection.md) for details.