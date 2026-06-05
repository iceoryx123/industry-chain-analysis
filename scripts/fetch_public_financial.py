#!/usr/bin/env python3
"""fetch_public_financial.py
免费财务指标抓取
- akshare: 中国宏观、行业数据、A股上市公司财务
- yfinance: 全球上市公司财务数据
"""

import os, datetime, pandas as pd, yaml
import yfinance as yf
from pathlib import Path

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis-push"))
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    import akshare as ak
except ImportError:
    ak = None

def fetch_cn_ticker_financial(ticker: str) -> dict:
    """中国 A股：通过 akshare 获取毛利率、ROE"""
    try:
        if ak is None:
            return {}
        df = ak.stock_financial_abstract_ths(symbol=ticker)
        if df.empty:
            return {}
        latest = df.iloc[0]
        gross_margin = float(latest.get("销售毛利率", 0))
        roe = float(latest.get("净资产收益率", 0))
        rd = float(latest.get("研发投入比例", 0))
        return {"gross_margin": gross_margin/100, "roe": roe/100, "rd_intensity": rd/100}
    except Exception as e:
        print(f"  ⚠️ akshare 获取 {ticker} 失败：{e}")
        return {}

def fetch_yfinance_financial(ticker: str) -> dict:
    """全球股票：通过 yfinance 获取毛利率、ROE、研发强度"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        gm = info.get("grossMargins", 0)
        roe = info.get("returnOnEquity", 0)
        rd = info.get("researchDevelopment", 0)
        rev = info.get("totalRevenue", 0)
        rd_intensity = rd / rev if rev else 0
        return {"gross_margin": gm, "roe": roe, "rd_intensity": rd_intensity}
    except Exception as e:
        print(f"  ⚠️ yfinance {ticker} 失败：{e}")
        return {}

def fetch_macro_size(indicator: str = "NV.IND.TOTL.CD") -> float:
    """World Bank 宏观指标（行业规模近似）"""
    import requests
    try:
        url = f"https://api.worldbank.org/v2/country/CHN/indicator/{indicator}?format=json&per_page=1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if len(data) >= 2 and data[1]:
            val = data[1][0].get("value")
            return float(val) / 1e8 if val else 0.0
    except Exception as e:
        print(f"  ⚠️ WorldBank 失败：{e}")
    return 0.0

def process_industry(meta: dict):
    code = meta["code"]
    name = meta["name"]
    cat = meta.get("category", "")
    print(f"\n🔍 [{code}] {name} ({cat})")

    record = {
        "date": datetime.date.today().isoformat(),
        "market_size_cny_bn": 0.0,
        "cr4": 0.0,
        "hhi": 0.0,
        "gross_margin": 0.0,
        "roe": 0.0,
        "rd_intensity": 0.0,
        "network_intensity": 0.0,
        "platform_users_million": 0.0,
        "average_transaction_value_cny": 0.0,
    }

    # 传统行业：抓财务指标
    if cat == "01‑Traditional":
        # 1. 宏观规模
        record["market_size_cny_bn"] = fetch_macro_size()

        # 2. 上市公司财务
        ticker = meta.get("representative_ticker", "")
        if ticker:
            fin = {}
            if ticker.endswith(("SS", "SH", "BJ")):
                fin = fetch_cn_ticker_financial(ticker)
            if not fin:
                fin = fetch_yfinance_financial(ticker)
            record.update(fin)

    # 平台行业：网络指标由 fetch_public_network.py 覆盖
    # 这里只写基本结构

    csv_path = OUT_DIR / f"{code}.csv"
    df = pd.DataFrame([record])
    if csv_path.exists():
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, mode="w", header=True, index=False)
    print(f"  ✅ CSV 已更新: {csv_path}")

def main():
    for f in sorted(META_DIR.glob("*.yaml")):
        meta = yaml.safe_load(f.read_text(encoding="utf-8"))
        process_industry(meta)

if __name__ == "__main__":
    main()
