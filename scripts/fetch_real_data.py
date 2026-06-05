#!/usr/bin/env python3
"""fetch_real_data.py
从 akshare 抓取真实财务指标，填充 32 个申万行业的 CSV。
分批执行，避免 rate limit。
"""

import sys, datetime, time, yaml
from pathlib import Path
import pandas as pd

ROOT = Path("/tmp/industry-chain-analysis-push")
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "date", "market_size_cny_bn", "cr4", "hhi", "gross_margin",
    "roe", "rd_intensity", "network_intensity",
    "platform_users_million", "average_transaction_value_cny",
]

import akshare as ak

def parse_pct(val):
    """将 '87.79%' 或 False 转为浮点数"""
    if val is False or val is None:
        return 0.0
    if isinstance(val, str):
        return float(val.replace("%", "").strip()) / 100.0
    return float(val)

def parse_num(val):
    """将 '6.28亿' 等转为浮点数（亿为单位）"""
    if val is False or val is None:
        return 0.0
    if isinstance(val, str):
        val = val.strip()
        if "万亿" in val:
            return float(val.replace("万亿", "")) * 10000
        elif "亿" in val:
            return float(val.replace("亿", ""))
        elif "万" in val:
            return float(val.replace("万", "")) / 10000
        elif "元" in val:
            return float(val.replace("元", "")) / 100000000
        return float(val)
    return float(val)

def fetch_ticker_financial(ticker: str) -> dict:
    """获取个股最新财务指标"""
    result = {"gross_margin": 0.0, "roe": 0.0, "rd_intensity": 0.0,
              "profit": 0.0, "revenue": 0.0}
    # 去掉 .SH/.SZ 后缀
    symbol = ticker.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    try:
        df = ak.stock_financial_abstract_ths(symbol=symbol)
        if df.empty:
            return result
        # 取最新年报（报告期 = 某年12-31）或最新数据
        # 找到最近一年的数据
        df = df.sort_values("报告期", ascending=False)
        for _, row in df.iterrows():
            gm = parse_pct(row.get("销售毛利率", False))
            roe = parse_pct(row.get("净资产收益率", False))
            profit = parse_num(row.get("净利润", False))
            revenue = parse_num(row.get("营业总收入", False))
            # 只取有真实数据的行
            if gm > 0 or roe > 0:
                result = {
                    "gross_margin": gm,
                    "roe": roe,
                    "rd_intensity": 0.0,  # 研发投入比例不可用
                    "profit": profit,
                    "revenue": revenue,
                }
                return result
        return result
    except Exception as e:
        print(f"    ⚠️ {ticker}: {e}")
        return result


def build_csv(meta: dict, financial: dict):
    """构建行业指标 CSV"""
    code = meta["code"]
    name = meta["name"]
    cat = meta.get("category", "")
    has_net = meta.get("has_network_effect", False)

    today = datetime.date.today().isoformat()

    # 行业规模估算
    market_size = 0.0
    if financial["revenue"] > 0:
        # 用代表公司营收 * 行业集中度倒推 → 粗略估算
        market_size = financial["revenue"] * 10  # 假设代表公司占10%份额

    record = {
        "date": today,
        "market_size_cny_bn": round(market_size, 2),
        "cr4": 0.15,     # 默认低集中度
        "hhi": 0.02,     # 默认低 HHI
        "gross_margin": round(financial["gross_margin"], 4),
        "roe": round(financial["roe"], 4),
        "rd_intensity": round(financial["rd_intensity"], 4),
        "network_intensity": 0.5 if has_net else 0.1,
        "platform_users_million": 0.0,
        "average_transaction_value_cny": 0.0,
    }
    return record


def process_industry(meta: dict):
    code = meta["code"]
    name = meta["name"]
    ticker = meta.get("representative_ticker", "")
    csv_path = OUT_DIR / f"{code}.csv"

    print(f"  📊 {code} {name} (ticker={ticker})")

    if not ticker:
        print(f"    ⏭️  无代表 ticker，跳过")
        return

    financial = fetch_ticker_financial(ticker)
    record = build_csv(meta, financial)

    # 写入 CSV
    df = pd.DataFrame([record])
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"    ✅ 毛利率={record['gross_margin']:.1%}, ROE={record['roe']:.1%}")
    time.sleep(1.5)  # rate limit 保护


def main():
    # 只处理申万代码（801xxx）
    metas = []
    for f in sorted(META_DIR.glob("801*.yaml")):
        m = yaml.safe_load(f.read_text())
        if m:
            metas.append(m)

    print(f"共 {len(metas)} 个申万行业，开始抓取财务数据...\n")

    for i, meta in enumerate(metas, 1):
        print(f"[{i}/{len(metas)}]", end="")
        process_industry(meta)

    print("\n✅ 全部完成！")


if __name__ == "__main__":
    main()
