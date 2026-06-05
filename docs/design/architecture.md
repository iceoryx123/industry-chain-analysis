# 架构设计文档

## 1. 核心设计理念

### 1.1 认知辅助而非预测工具
- **定位**：帮助分析师**看清结构**、识别**价值枢纽**、评估**枢纽质量**、判断**拐点**
- **不做**：价格预测、买卖建议、宏观周期预判

### 1.2 双模并行架构（v10+）

```
┌─────────────────────────────────────────────────────────────┐
│                    Industry Chain Analysis                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────┐         ┌──────────────────────┐    │
│   │  Mode A: Chain   │         │  Mode B: Value Net   │    │
│   │  (v9 继承)       │◄───────►│  (v10 新增)          │    │
│   │                  │  映射    │                      │    │
│   │  线性：上/中/下/服│         │  网状：节点/连接/流   │    │
│   │  利润池集中单环节  │         │  价值共创/网络效应    │    │
│   └──────────────────┘         └──────────────────────┘    │
│         │                              │                    │
│         └──────────────┬───────────────┘                    │
│                        ▼                                    │
│              ┌──────────────────────┐                       │
│              │  Unified Output      │                       │
│              │  - Value Hubs        │                       │
│              │  - Quality Score     │                       │
│              │  - Inflection Signals│                       │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## 2. 数据模型

### 2.1 核心实体

| 实体 | 属性 | 说明 |
|------|------|------|
| **Industry** | id, name, version, category | 分析对象 |
| **ChainLayer** | position, key_players, profit_pool | 产业链层级 |
| **ValueHub** | entity, type(chain/net), score, evidence | 价值枢纽 |
| **NetworkNode** | entity, role(builder/participant), connections | 价值网节点 |
| **InflectionSignal** | indicator, threshold, direction, confidence | 拐点信号 |

### 2.2 版本兼容矩阵

| 版本 | Chain Mode | Network Mode | 适用场景 |
|------|-----------|-------------|----------|
| v9.2 | ✅ 完整 | ❌ | 传统制造/消费/线性行业 |
| v10.0 | ✅ 兼容 | ✅ 基础 | 过渡期双模并行 |
| v10.5+ | ✅ 兼容 | ✅ 完整 | 互联网/AI/平台/生态型 |

## 3. 分析流程设计

### 3.1 标准化 6 步法

```
Step 1: 版本选择     ──►  Step 2: 链/网全景绘制
                                           │
Step 6: 结论输出 ◄─── Step 5: 拐点监控 ◄─── Step 4: 质量评分 ◄─── Step 3: 枢纽识别
```

### 3.2 评分模型（可扩展）

```python
# 伪代码：枢纽质量评分
def hub_quality_score(hub):
    dimensions = {
        'moat': weight=0.30,      # 护城河
        'pricing_power': 0.25,    # 定价权
        'substitution_diff': 0.25,# 替代难度
        'ecosystem_position': 0.20# 生态位
    }
    return sum(score[d] * w for d, w in dimensions.items())
```

## 4. 扩展点设计

### 4.1 新增行业案例
- 遵循 `cases/by-industry/<category>/NN-名.md` 结构
- 自动纳入 `cases/README.md` 索引

### 4.2 新版本理论
- 在 `theory/v{X}.y/` 下新增版本文档
- 更新 `theory/comparison.md` 对比表
- CHANGELOG.md 记录破坏性变更

### 4.3 自定义评分维度
- 在 `references/scoring-rules.md` 定义（规划中）
- 支持行业特化权重覆盖

## 5. 部署与分发

| 形态 | 说明 |
|------|------|
| **GitHub Repo** | 源码、文档、案例库 |
| **GitHub Release** | 打包分发（SKILL.md + 核心理论 + 案例索引） |
| **Skill Package** | 供 QwenPaw 等平台直接加载 |

---

> **维护原则**：核心框架保持稳定，案例库持续扩充，版本演进有据可查。