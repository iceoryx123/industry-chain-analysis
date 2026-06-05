#!/usr/bin/env python3
"""fetch_public_network.py
免费平台网络指标抓取
- pytrends: Google 搜索趋势（网络活跃度近似）
- requests+BeautifulSoup: Alexa 排名、新闻 GMV
"""

import os, re, datetime, pandas as pd, yaml, requests
from bs4 import BeautifulSoup
from pathlib import Path

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis"))
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AnalyticsBot/1.0)"}

# pytrends 可选
PTRENDS = None
try:
    from pytrends.request import TrendReq
    PTRENDS = TrendReq(hl='zh-CN', tz=480)
except Exception:
    PTRENDS = None

def fetch_google_trends(keyword: str) -> float:
    """Google Trends 兴趣指数（0‑1）"""
    if not PTRENDS:
        return 0.0
    try:
        PTRENDS.build_payload([keyword], timeframe='today 12-m')
        data = PTRENDS.interest_over_time()
        if not data.empty:
            return round(data[keyword].mean() / 100.0, 3)
    except Exception as e:
        print(f"  ⚠️ Google Trends 失败 ({keyword}): {e}")
    return 0.0

def fetch_alexa_rank(domain: str) -> int:
    """Alexa 网站排名（越低越好）"""
    if not domain:
        return 0
    try:
        url = f"https://www.alexa.com/siteinfo/{domain}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        tag = soup.select_one(".rank-global")
        if tag:
            return int(tag.get_text(strip=True).replace(",", ""))
    except Exception as e:
        print(f"  ⚠️ Alexa 失败 ({domain}): {e}")
    return 0

def fetch_news_gmv(domain: str) -> float:
    """Google 新闻搜索 GMV（亿元）"""
    if not domain:
        return 0.0
    try:
        q = f"{domain}+GMV+site:news.google.com"
        url = f"https://www.google.com/search?q={q}&tbm=nws"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        texts = " ".join(p.get_text() for p in soup.select("div.Slqrh"))
        matches = re.findall(r'([\d,.]+)\s*亿', texts)
        if matches:
            return max(float(m.replace(",", "")) for m in matches)
    except Exception as e:
        print(f"  ⚠️ 新闻 GMV 失败 ({domain}): {e}")
    return 0.0

def process_platform(meta: dict):
    code = meta["code"]
    name = meta["name"]
    domain = meta.get("official_website", "")
    if domain:
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

    print(f"\n🔍 [{code}] {name} (平台)")

    # 1. Google Trends
    trends = fetch_google_trends(name)

    # 2. Alexa 排名 → 归一化网络强度
    rank = fetch_alexa_rank(domain)
    net_intensity = round(max(0, min(1, (1000 - rank) / 1000)), 3) if rank else trends

    # 3. 新闻 GMV
    gmv = fetch_news_gmv(domain)

    # 4. 用户估计
    users = round(trends * 10 + net_intensity * 5, 3)

    record = {
        "date": datetime.date.today().isoformat(),
        "market_size_cny_bn": 0.0,
        "cr4": 0.0,
        "hhi": 0.0,
        "gross_margin": 0.0,
        "roe": 0.0,
        "rd_intensity": 0.0,
        "network_intensity": net_intensity,
        "platform_users_million": users,
        "average_transaction_value_cny": round(gmv * 1e8 / (users * 1e6 + 1), 2),
    }

    csv_path = OUT_DIR / f"{code}.csv"
    df = pd.DataFrame([record])
    if csv_path.exists():
        df.to_csv(csv_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_path, mode="w", header=True, index=False)
    print(f"  ✅ 网络 CSV 已更新: {csv_path}")

def main():
    for f in sorted(META_DIR.glob("*.yaml")):
        meta = yaml.safe_load(f.read_text(encoding="utf-8"))
        if meta.get("category") == "02‑Platform":
            process_platform(meta)

if __name__ == "__main__":
    main()
