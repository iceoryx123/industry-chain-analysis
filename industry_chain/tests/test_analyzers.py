"""
评分测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from industry_chain.analyzers import ScoreCard, InsightGenerator, ScoringConfig, Dimension


def test_score_default_dimensions():
    """默认评分维度应返回合理分数"""
    card = ScoreCard()
    indicators = {
        "gross_margin": 0.4,
        "roe": 0.15,
        "rd_intensity": 0.08,
        "network_intensity": 0.5,
        "platform_users_million": 10,
    }
    result = card.score("150000-01", indicators)
    assert "total_score" in result
    assert 0 <= result["total_score"] <= 10
    assert len(result["dimensions"]) == 4


def test_score_high_moat():
    """高毛利率应打分高"""
    card = ScoreCard()
    indicators = {
        "gross_margin": 0.9,  # 90% 毛利率
        "roe": 0.10,
        "rd_intensity": 0.02,
        "network_intensity": 0.1,
        "platform_users_million": 1,
    }
    result = card.score("150000-01", indicators)
    moat = [d for d in result["dimensions"] if d["name"] == "moat"][0]
    # 公式: min(10, 0.9 * 20 + 2) = min(10, 20) = 10
    assert moat["score"] == 10


def test_score_low_all():
    """所有指标很低时应接近 0"""
    card = ScoreCard()
    indicators = {
        "gross_margin": 0.01,
        "roe": 0.01,
        "rd_intensity": 0.001,
        "network_intensity": 0.0,
        "platform_users_million": 0,
    }
    result = card.score("150000-01", indicators)
    assert result["total_score"] < 4


def test_insight_generation():
    """洞见生成不应报错"""
    from industry_chain.models import IndustryMeta
    gen = InsightGenerator()

    # 模拟一个元数据
    meta = IndustryMeta(code="150000-01", name="测试行业",
                         shenwan_code="150000", shenwan_industry="医药生物")
    indicators = {
        "gross_margin": 0.4,
        "roe": 0.15,
        "rd_intensity": 0.08,
        "network_intensity": 0.5,
        "platform_users_million": 10,
        "cr4": 0.3,
        "market_size_cny_bn": 100,
        "hhi": 0.1,
        "average_transaction_value_cny": 100,
    }
    result = gen.generate(meta, indicators)
    assert "价值枢纽识别" in result
    assert "质量评分" in result
    assert "拐点信号" in result
    assert "业务启示" in result
