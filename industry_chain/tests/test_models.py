"""
模型测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from industry_chain.models import IndustryMeta, IndicatorRow


def test_indicator_row_defaults():
    """指标行应该具有合理的默认值"""
    row = IndicatorRow(industry_code="150000-01", date="2026-01-01")
    assert row.gross_margin == 0.0
    assert row.roe == 0.0
    assert row.rd_intensity == 0.0
    assert row.network_intensity == 0.0
    assert row.platform_users_million == 0.0


def test_indicator_load_latest_nonexistent():
    """不存在的代码应返回空指标"""
    row = IndicatorRow.load_latest("999999-99")
    assert row.industry_code == "999999-99"
    assert row.gross_margin == 0.0
    assert row.date  # 应该有日期的字符串


def test_industry_meta_list():
    """列出所有行业元数据（不抛异常）"""
    metas = IndustryMeta.list_all()
    assert isinstance(metas, list)
    # meta 文件可能不存在于测试环境中，但不应抛异常
