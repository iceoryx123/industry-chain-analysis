#!/usr/bin/env python3
"""render_cases.py 渲染案例中的 {{ indicator.xxx }} 占位"""
import re, pandas as pd
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
IND_DIR = ROOT / "data" / "indicators"

FIELDS = [
    "market_size_cny_bn", "cr4", "hhi", "gross_margin",
    "roe", "rd_intensity", "network_intensity",
    "platform_users_million", "average_transaction_value_cny",
]

def render_file(case_md: Path):
    txt = case_md.read_text(encoding="utf-8")
    # 从 case.md 头部提取 industry_code
    m = re.search(r'industry_code:\s*["\']?([\w-]+)', txt)
    if not m:
        print(f"  ⚠️ 未找到 industry_code: {case_md}")
        return
    code = m.group(1)
    csv_path = IND_DIR / f"{code}.csv"
    if not csv_path.exists():
        # 尝试只取申万代码
        sw_code = code.split("-")[0]
        csv_path = IND_DIR / f"{sw_code}.csv"
    if not csv_path.exists():
        print(f"  ⚠️ 无 CSV: {code}")
        return
    df = pd.read_csv(csv_path)
    latest = df.iloc[-1]
    # 替换所有 {{ indicator.xxx }}
    changed = False
    for col in FIELDS:
        val = latest.get(col, 0)
        # 按数值大小格式化
        if abs(val) >= 1e8:
            s = f"{val:.0f}"
        elif abs(val) >= 1:
            s = f"{val:.2f}"
        else:
            s = f"{val:.4f}"
        old = f"{{{{ indicator.{col} }}}}"
        if old in txt:
            txt = txt.replace(old, s)
            changed = True
    if changed:
        case_md.write_text(txt, encoding="utf-8")
        print(f"  ✅ 已渲染: {case_md}")
    else:
        print(f"  🔎 无需渲染: {case_md}")

def main():
    for f in sorted(ROOT.glob("cases/**/*/case.md")):
        render_file(f)

if __name__ == "__main__":
    main()
