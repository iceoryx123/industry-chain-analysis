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
- **机器人行业代表股修复**: 从美的（000333.SZ）改为汇川技术（300124.SZ）
- **食品饮料深度分析**: 426行行业结构性分析（白酒/调味品/乳制品/啤酒四象限）
- **README全面更新**: 完整目录结构、32行业覆盖、评分分布

### Changed
- `scripts/fetch_real_data.py`: 支持多股平均 + parse_num 兼容"万/亿/万亿元"格式
- 评分分布从 1.0-3.4 扩展为 1.0-3.9（食品饮料 3.9 成为最高分）
- README 从旧版（31行业/26案例）更新为当前准确状态

### Fixed
- akshare 数值解析错误（"4140.45万"→float 转换失败）
- 食品饮料案例从模板目录迁移为 subsector 深度分析目录

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