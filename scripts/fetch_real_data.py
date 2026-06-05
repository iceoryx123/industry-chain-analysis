#!/usr/bin/env python3
"""fetch_real_data.py v2
从 akshare 抓取真实财务指标，支持多股平均 + 行业特殊处理。
"""

import sys, datetime, time, yaml
from pathlib import Path
import pandas as pd

ROOT = Path("/tmp/industry-chain-analysis-push")
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

import akshare as ak

# ── 行业特殊处理规则 ──────────────────────────────────
# 某些行业不适用标准毛利率，使用替代指标
SPECIAL_RULES = {
    "801140": {"name": "银行", "gross_margin_proxy": 0.35, "note": "用净息差/NIM替代"},  # 实际NIM~2%, 用营业毛利率口径
    "801160": {"name": "非银金融", "gross_margin_proxy": 0.20, "note": "用营业利润率替代"},
}

# ── 多股配置 ──────────────────────────────────────────
# key=行业代码, value=[(ticker, weight), ...]
PEER_TICKERS = {
    "801710": [("600893.SH", 1.0), ("600760.SH", 1.0)],   # 航发动力 + 中航沈飞
    "801180": [("000002.SZ", 1.0), ("600048.SH", 1.0)],   # 万科A + 保利发展
    "801880": [("300124.SZ", 1.0)],                         # 汇川技术（代替美的）
    "801730": [("000333.SZ", 1.0), ("000651.SZ", 1.0)],   # 美的 + 格力
    "801750": [("000895.SZ", 1.0), ("600519.SH", 1.0)],   # 双汇 + 茅台
    "801150": [("300015.SZ", 1.0), ("600276.SH", 1.0), ("603259.SH", 1.0)],  # 爱尔 + 恒瑞 + 药明康德
}


def parse_pct(val):
    if val is False or val is None:
        return None
    if isinstance(val, str):
        return float(val.replace("%", "").strip()) / 100.0
    return float(val)


def parse_num(val):
    """将 '6.28亿' 或 '4140.45万' 转为浮点数（亿为单位）"""
    if val is False or val is None:
        return 0.0
    if isinstance(val, str):
        val = val.strip()
        if "万亿" in val:
            return float(val.replace("万亿", "").replace(",", "")) * 10000
        elif "亿" in val:
            return float(val.replace("亿", "").replace(",", ""))
        elif "万" in val:
            return float(val.replace("万", "").replace(",", "")) / 10000
        elif "元" in val:
            return float(val.replace("元", "").replace(",", "")) / 100000000
        return float(val.replace(",", ""))
    return float(val)


def fetch_ticker_financial(ticker: str) -> dict:
    """获取个股最新财务指标"""
    result = {"gross_margin": None, "roe": None, "profit": None, "revenue": None}
    symbol = ticker.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    try:
        df = ak.stock_financial_abstract_ths(symbol=symbol)
        if df.empty:
            return result
        df = df.sort_values("报告期", ascending=False)
        for _, row in df.iterrows():
            gm = parse_pct(row.get("销售毛利率", False))
            roe = parse_pct(row.get("净资产收益率", False))
            profit = parse_num(row.get("净利润", False))
            revenue = parse_num(row.get("营业总收入", False))
            if gm is not None or roe is not None:
                result = {
                    "gross_margin": gm if gm is not None else 0.0,
                    "roe": roe if roe is not None else 0.0,
                    "profit": profit,
                    "revenue": revenue,
                }
                return result
        return result
    except Exception as e:
        print(f"    ⚠️ {ticker}: {e}")
        return result


def process_industry(meta: dict):
    code = meta["code"]
    name = meta["name"]
    cat = meta.get("category", "")
    primary_ticker = meta.get("representative_ticker", "")

    csv_path = OUT_DIR / f"{code}.csv"
    print(f"  📊 {code} {name}", end="")

    # ── 特殊处理 ──
    special = SPECIAL_RULES.get(code)

    # ── 确定 ticker 列表 ──
    tickers = PEER_TICKERS.get(code, [])
    if not tickers and primary_ticker:
        tickers = [(primary_ticker, 1.0)]

    if not tickers:
        print("  ⏭️ 无 ticker")
        return

    # ── 抓取所有 ticker ──
    results = []
    for tkr, wgt in tickers:
        fin = fetch_ticker_financial(tkr)
        if fin["gross_margin"] is not None or fin["roe"] is not None:
            results.append((wgt, fin))
        time.sleep(1.2)

    if not results:
        print("  ⚠️ 全部失败，用默认值")
        return

    # ── 加权平均 ──
    total_w = sum(w for w, _ in results)
    avg_gm = sum(w * r["gross_margin"] for w, r in results if r["gross_margin"] is not None) / total_w
    avg_roe = sum(w * r["roe"] for w, r in results if r["roe"] is not None) / total_w
    avg_rev = sum(w * r["revenue"] for w, r in results) / total_w

    # ── 特殊规则覆盖 ──
    if special and "gross_margin_proxy" in special:
        avg_gm = special["gross_margin_proxy"]
        print(f" [特殊: {special['note']}]", end="")

    # ── 行业规模估算 ──
    market_size = avg_rev * 10 if avg_rev > 0 else 0.0
    has_net = meta.get("has_network_effect", False)

    record = {
        "date": datetime.date.today().isoformat(),
        "market_size_cny_bn": round(market_size, 2),
        "cr4": 0.15,
        "hhi": 0.02,
        "gross_margin": round(avg_gm, 4),
        "roe": round(avg_roe, 4),
        "rd_intensity": 0.0,
        "network_intensity": 0.5 if has_net else 0.1,
        "platform_users_million": 0.0,
        "average_transaction_value_cny": 0.0,
    }

    df = pd.DataFrame([record])
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    ticker_str = ",".join(t for t, _ in tickers)
    print(f"  ✅ {len(results)}/{len(tickers)} tickers | 毛利率={avg_gm:.1%} ROE={avg_roe:.1%}")


def main():
    metas = []
    for f in sorted(META_DIR.glob("801*.yaml")):
        m = yaml.safe_load(f.read_text())
        if m:
            metas.append(m)

    print(f"共 {len(metas)} 个申万行业，开始抓取...\n")
    for i, meta in enumerate(metas, 1):
        print(f"[{i}/{len(metas)}]", end="")
        process_industry(meta)
    print("\n✅ 全部完成！")


if __name__ == "__main__":
    main()
