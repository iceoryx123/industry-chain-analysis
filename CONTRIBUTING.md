# Contributing Guide

感谢你对 **产业链结构性分析框架** 的关注！欢迎贡献案例、修正错误、完善理论或改进文档。

---

## 🚀 快速开始

```bash
# 1. Fork 仓库
# 2. Clone 你的 Fork
git clone https://github.com/<your-username>/industry-chain-analysis.git
cd industry-chain-analysis

# 3. 创建分支
git checkout -b feat/add-new-case

# 4. 提交更改
git add .
git commit -m "feat(cases): add XX 行业分析案例"

# 5. 推送并发起 PR
git push origin feat/add-new-case
```

---

## 📋 贡献类型

| 类型 | 目录 | 示例 |
|------|------|------|
| **新增行业案例** | `cases/by-industry/<category>/` | `cases/by-industry/healthcare/01-儿科医院.md` |
| **理论修正/扩展** | `theory/v10.x/` 或 `theory/v9.2/` | `theory/v10.x/v10.5.1.md` |
| **文档改进** | `docs/guides/` / `docs/design/` | `docs/guides/best-practices.md` |
| **工具/模板** | `references/` | `references/output-template.md` |
| **Bug 修复** | 任意 | 修正公式、链接、错别字 |

---

## ✍️ 写作规范

### 案例文件命名
```
{cases/by-industry/}{category}/{NN-行业名}.md
```
- `NN`：两位数序号（按添加顺序）
- 行业名：中文，简洁明确

### 案例必含结构
```markdown
# {行业名}产业链分析

## 1. 版本选择
- 使用版本：v10.5 / v9.2
- 选择理由：...

## 2. 产业链全景
- 上游/中游/下游/服务层 关键环节
- 核心企业映射

## 3. 价值枢纽识别
- 候选枢纽列表
- 筛选逻辑与证据

## 4. 枢纽质量评估
- 护城河 / 定价权 / 替代难度 / 生态位

## 5. 拐点判断
- 量化指标 + 定性信号

## 6. 结论与投资启示
```

### 理论文档
- 版本号在文件名体现：`v10.5.1.md`
- 变更需在 CHANGELOG.md 同步记录
- 破坏性变更需在 PR 描述说明迁移路径

---

## 🔍 PR 检查清单

提交前自查：

- [ ] 文件命名符合规范
- [ ] Markdown 通过 `markdownlint` 检查
- [ ] 内部链接有效（相对路径）
- [ ] 新案例已在 `cases/README.md` 索引中登记
- [ ] 理论变更已更新 `CHANGELOG.md`
- [ ] 无敏感信息（内部数据、未公开研报等）

---

## 🏷️ 版本发布流程

仅维护者操作：

```bash
# 1. 更新版本号（CHANGELOG.md 已同步）
# 2. 打标签推送
git tag -a v10.5.2 -m "v10.5.2: patch description"
git push origin v10.5.2

# 3. GitHub Actions 自动创建 Release
```

---

## 📞 联系

- Issues: [GitHub Issues](https://github.com/iceoryx123/industry-chain-analysis/issues)
- Discussions: [GitHub Discussions](https://github.com/iceoryx123/industry-chain-analysis/discussions)

---

> **原则**：保持框架的**认知辅助**本质——不做预测，只做结构拆解与质量判断。