#!/usr/bin/env python3
"""fetch_public_financial.py
免费财务指标抓取 - 适配申万一级行业
- akshare: 中国宏观、行业数据、A股上市公司财务
- yfinance: 全球上市公司财务数据
- World Bank: 宏观行业规模
"""

import os, datetime, pandas as pd, yaml
import yfinance as yf
import requests
from pathlib import Path

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis-push"))
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

try:
    import akshare as ak
except ImportError:
    ak = None

FIELDS = [
    "date", "market_size_cny_bn", "cr4", "hhi", "gross_margin",
    "roe", "rd_intensity", "network_intensity",
    "platform_users_million", "average_transaction_value_cny",
]

def fetch_cn_financial(ticker: str) -> dict:
    """中国 A股：通过 akshare 获取毛利率、ROE、研发强度"""
    result = {"gross_margin": 0.0, "roe": 0.0, "rd_intensity": 0.0}
    if not ak:
        return result
    try:
        # 尝试获取个股财务摘要
        df = ak.stock_financial_abstract_ths(symbol=ticker)
        if not df.empty:
            latest = df.iloc[0]
            gm = latest.get("销售毛利率", 0)
            roe = latest.get("净资产收益率", 0)
            rd = latest.get("研发投入比例", 0)
            result = {
                "gross_margin": float(gm) / 100 if gm else 0,
                "roe": float(roe) / 100 if roe else 0,
                "rd_intensity": float(rd) / 100 if rd else 0,
            }
    except Exception as e:
        print(f"    ⚠️ akshare {ticker}: {e}")
    return result

def fetch_yf_financial(ticker: str) -> dict:
    """全球股票：通过 yfinance 获取毛利率、ROE、研发强度"""
    result = {"gross_margin": 0.0, "roe": 0.0, "rd_intensity": 0.0}
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        gm = info.get("grossMargins", 0)
        roe = info.get("returnOnEquity", 0)
        rd = info.get("researchDevelopment", 0)
        rev = info.get("totalRevenue", 0)
        result = {
            "gross_margin": float(gm) if gm else 0,
            "roe": float(roe) if roe else 0,
            "rd_intensity": float(rd) / float(rev) if (rd and rev) else 0,
        }
    except Exception as e:
        print(f"    ⚠️ yfinance {ticker}: {e}")
    return result

def fetch_macro_size() -> float:
    """World Bank 宏观指标（行业规模近似）"""
    try:
        url = "https://api.worldbank.org/v2/country/CHN/indicator/NV.IND.TOTL.CD?format=json&per_page=1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if len(data) >= 2 and data[1]:
            val = data[1][0].get("value")
            return float(val) / 1e8 if val else 0.0
    except Exception:
        pass
    return 0.0

def process_industry(meta: dict):
    code = meta["code"]
    name = meta["name"]
    cat = meta.get("category", "")
    ticker = meta.get("representative_ticker", "")
    has_net = meta.get("has_network_effect", False)

    print(f"  🔍 [{code}] {name} ({cat})")

    record = {f: 0.0 for f in FIELDS}
    record["date"] = datetime.date.today().isoformat()

    # 传统行业 + 受监管行业 + 新兴行业（非平台）：抓财务指标
    if not has_net:
        # 宏观规模
        record["market_size_cny_bn"] = fetch_macro_size()

        # 上市公司财务
        if ticker:
            fin = fetch_cn_financial(ticker)
            if not any(fin.values()):
                fin = fetch_yf_financial(ticker)
            record.update(fin)

    # 平台行业：网络指标由 fetch_public_network.py 覆盖
    # 这里写基本结构

    # 写入 CSV
    csv_path = OUT_DIR / f"{code}.csv"
    df = pd.DataFrame([record])
    if csv_path.exists():
        # 去重：如果今天已有则跳过
        existing = pd.read_csv(csv_path)
        if record["date"] in existing["date"].values:
            print(f"    ↩️ 今日已存在，跳过: {csv_path}")
            return
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, mode="w", header=True, index=False)
    print(f"    ✅ CSV 已写入: {csv_path.name}")

def main():
    print("=" * 60)
    print("📊 财务指标抓取（申万一级行业）")
    print("=" * 60)
    count = 0
    for f in sorted(META_DIR.glob("*.yaml")):
        meta = yaml.safe_load(f.read_text(encoding="utf-8"))
        process_industry(meta)
        count += 1
    print(f"\n✅ 完成！共处理 {count} 个行业")

if __name__ == "__main__":
    main()
