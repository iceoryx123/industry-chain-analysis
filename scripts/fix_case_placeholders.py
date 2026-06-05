#!/usr/bin/env python3
"""fix_case_placeholders.py - 为所有 case.md 添加 {{ indicator.xxx }} 占位符"""
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
FIELDS = [
    ("market_size_cny_bn", "市场规模（亿元）"),
    ("cr4", "CR4"),
    ("hhi", "HHI"),
    ("gross_margin", "毛利率"),
    ("roe", "ROE"),
    ("rd_intensity", "研发强度"),
    ("network_intensity", "网络强度"),
    ("platform_users_million", "平台用户（百万人）"),
    ("average_transaction_value_cny", "平均交易额（元）"),
]

for case_md in sorted(ROOT.glob("cases/**/case.md")):
    txt = case_md.read_text(encoding="utf-8")
    if "{{ indicator." in txt:
        continue
    # Append indicator table
    lines = ["\n---\n", "> **关键指标**"]
    for field, label in FIELDS:
        lines.append(f"> - {label}：{{{{ indicator.{field} }}}}")
    txt += "\n".join(lines)
    case_md.write_text(txt, encoding="utf-8")
    print(f"✅ 修复: {case_md.relative_to(ROOT)}")
