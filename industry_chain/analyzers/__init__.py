"""
分析与评分
========

价值枢纽识别、质量评分、洞见生成。

核心设计：评分模型可配置（通过 config/scoring_rules.yaml）
"""

from typing import Dict, List, Optional
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict

from industry_chain.config import settings
from industry_chain.models import IndustryMeta, IndicatorRow


# =========================================
# 评分配置
# =========================================
@dataclass
class Dimension:
    """评分维度"""
    name: str          # 维度名（英文）
    label: str         # 中文标签
    weight: float      # 权重（0-1）
    formula: str       # 评分公式，变量来自 IndicatorRow 字段

    def calculate(self, indicators: Dict[str, float]) -> float:
        """根据公式计算得分（0-10）"""
        try:
            # 安全 eval：仅允许数学函数和基本运算
            _safe_builtins = {"min": min, "max": max, "abs": abs, "round": round}
            return eval(self.formula, {"__builtins__": {}}, {**_safe_builtins, **indicators})
        except Exception as e:
            return 0.0


@dataclass
class ScoringConfig:
    """完整评分配置"""
    default_dimensions: List[Dimension]
    overrides: Dict[str, List[Dimension]]   # 行业类别覆盖

    @classmethod
    def load(cls) -> "ScoringConfig":
        config_path = settings.CONFIG_DIR / "scoring_rules.yaml"
        if not config_path.exists():
            return cls._default()

        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        default = [Dimension(**d) for d in raw.get("default", {}).get("dimensions", [])]
        overrides = {}
        for cat, cfg in raw.get("overrides", {}).items():
            overrides[cat] = [Dimension(**d) for d in cfg.get("dimensions", [])]
        return cls(default_dimensions=default, overrides=overrides)

    @classmethod
    def _default(cls) -> "ScoringConfig":
        return cls(
            default_dimensions=[
                Dimension("moat", "护城河", 0.30, "min(10, gross_margin * 20 + 2)"),
                Dimension("pricing_power", "定价权", 0.25, "min(10, roe * 30 + 2)"),
                Dimension("substitution", "替代难度", 0.25, "min(10, rd_intensity * 50 + 2)"),
                Dimension("ecosystem", "生态位", 0.20, "min(10, network_intensity * 8 + platform_users_million * 0.5 + 2)"),
            ],
            overrides={},
        )


# =========================================
# 评分卡
# =========================================
class ScoreCard:
    """评分卡：根据配置计算各维度得分"""

    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig.load()

    def score(self, industry_code: str, indicators: Dict[str, float]) -> Dict:
        """对单个行业进行评分"""
        # 确定使用哪套维度
        meta = IndustryMeta.load(industry_code)
        dimensions = self.config.overrides.get(meta.shenwan_industry,
                                                self.config.default_dimensions)

        results = []
        total = 0.0
        for dim in dimensions:
            s = dim.calculate(indicators)
            s = max(0, min(10, s))  # 限制 0-10
            results.append({
                "name": dim.name,
                "label": dim.label,
                "score": round(s, 1),
                "weight": dim.weight,
                "weighted": round(s * dim.weight, 2),
            })
            total += s * dim.weight

        return {
            "industry_code": industry_code,
            "dimensions": results,
            "total_score": round(total, 2),
        }


# =========================================
# 洞见生成（基于规则）
# =========================================
class InsightGenerator:
    """基于规则的洞见生成器（零成本，无需 LLM）"""

    def generate(self, meta: IndustryMeta, indicators: Dict[str, float]) -> str:
        """生成四段式洞见：枢纽 → 评分 → 信号 → 启示"""
        gm = indicators.get("gross_margin", 0)
        roe = indicators.get("roe", 0)
        rd = indicators.get("rd_intensity", 0)
        net = indicators.get("network_intensity", 0)
        users = indicators.get("platform_users_million", 0)
        cr4 = indicators.get("cr4", 0)

        # 1. 价值枢纽
        if net > 0.5:
            hub = "平台/生态构建者（建网者）"
        elif gm > 0.4:
            hub = "品牌/技术驱动型企业（高毛利枢纽）"
        elif cr4 > 0.3:
            hub = "行业龙头企业（集中度优势）"
        else:
            hub = "产业链关键环节（待进一步识别）"

        # 2. 评分
        card = ScoreCard()
        scoring = card.score(meta.code, indicators)
        dims = " | ".join(
            f"{d['label']}：{d['score']}/10"
            for d in scoring["dimensions"]
        )

        # 3. 拐点信号
        signals = []
        if net > 0.3 and net < 0.7:
            signals.append("网络效应处于上升期（中期拐点关注）")
        elif net >= 0.7:
            signals.append("网络效应趋于饱和（关注新增长曲线）")
        if gm < 0.2:
            signals.append("毛利率低位，警惕竞争加剧")
        elif gm > 0.6:
            signals.append("高毛利率但需关注可持续性")
        if roe < 0.05:
            signals.append("ROE 低于资金成本，价值毁灭风险")
        if rd > 0.1:
            signals.append("高强度研发投入，技术迭代风险")
        if not signals:
            signals.append("当前指标无明显拐点信号")

        # 4. 启示
        if net > 0.5:
            suggestion = "重点关注平台的生态扩展能力和用户粘性指标"
        elif gm > 0.4:
            suggestion = "关注高毛利企业的护城河可持续性，警惕新进入者"
        elif cr4 > 0.3:
            suggestion = "行业集中度较高，关注龙头企业的定价权变化"
        else:
            suggestion = "行业较为分散，需进一步细分识别潜在枢纽"

        return f"""
### 🔍 自动洞见（基于规则）

**价值枢纽识别**：{hub}

**质量评分**（维度 1‑10）：
- {dims}
- **综合评分**：{scoring['total_score']}/10

**拐点信号**：
- {"；".join(signals)}

**业务启示**：
- {suggestion}
"""
