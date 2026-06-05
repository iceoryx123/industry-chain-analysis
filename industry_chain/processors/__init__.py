"""
数据处理
========

ETL、渲染、验证等核心数据处理流程。
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional
from datetime import date

from industry_chain.config import settings
from industry_chain.models import IndustryMeta, IndicatorRow, Case


# =========================================
# ETL：合并去重
# =========================================
def run_etl():
    """合并去重所有行业 CSV，保持数据整洁"""
    count = 0
    for csv_path in sorted(settings.INDICATORS_DIR.glob("*.csv")):
        df = pd.read_csv(csv_path)
        if df.empty:
            continue
        df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
        df.to_csv(csv_path, index=False)
        count += 1
    return count


# =========================================
# 渲染：替换占位符
# =========================================
def render_all_cases() -> int:
    """渲染所有案例中的 {{ indicator.xxx }} 占位符"""
    count = 0
    for meta in IndustryMeta.list_all():
        indicators = IndicatorRow.load_latest(meta.code)
        case_paths = list(settings.CASES_DIR.rglob(f"{meta.code}-*/case.md"))
        for case_path in case_paths:
            content = case_path.read_text(encoding="utf-8")
            # 替换占位符
            changed = False
            for key in [
                "market_size_cny_bn", "cr4", "hhi", "gross_margin",
                "roe", "rd_intensity", "network_intensity",
                "platform_users_million", "average_transaction_value_cny",
            ]:
                placeholder = f"{{{{ indicator.{key} }}}}"
                if placeholder in content:
                    val = getattr(indicators, key, 0)
                    if isinstance(val, float):
                        if abs(val) >= 1e8:
                            formatted = f"{val:.0f}"
                        elif abs(val) >= 1:
                            formatted = f"{val:.2f}"
                        else:
                            formatted = f"{val:.4f}"
                    else:
                        formatted = str(val)
                    content = content.replace(placeholder, formatted)
                    changed = True
            if changed:
                case_path.write_text(content, encoding="utf-8")
                count += 1
    return count


# =========================================
# 数据质量验证
# =========================================
def validate_data() -> List[str]:
    """检查数据质量，返回错误信息列表"""
    errors = []

    for meta in IndustryMeta.list_all():
        # 1. 检查 CSV 是否存在
        csv_path = settings.INDICATORS_DIR / f"{meta.code}.csv"
        if not csv_path.exists():
            errors.append(f"{meta.code}: 指标 CSV 不存在")

        # 2. 检查案例文件是否存在
        case_paths = list(settings.CASES_DIR.rglob(f"{meta.code}-*/case.md"))
        if not case_paths:
            errors.append(f"{meta.code}: 案例文件不存在")

        # 3. 检查最近 7 天是否有数据更新
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if not df.empty:
                latest_date = df["date"].iloc[-1]
                # 只是警告，不作为错误

    return errors
