#!/usr/bin/env python3
"""etl_indicators.py

一个最小可行的 ETL 示例：
- 读取 data/meta/*.yaml 获取行业代码
- 对每个行业生成一个占位 CSV（如果不存在）
- CSV 列头统一，后续可以接入 Wind、同花顺、公开报告的抓取逻辑。

目前只做占位工作，CI 每月会运行此脚本并提交 CSV（若有变化则自动 PR）
"""

import csv
import os
from pathlib import Path
import yaml
import datetime

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis-push"))
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "data" / "indicators"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "date",
    "market_size_cny_bn",
    "cr4",
    "hhi",
    "gross_margin",
    "roe",
    "rd_intensity",
    "network_intensity",
    "platform_users_million",
    "average_transaction_value_cny",
]

def ensure_csv(code: str):
    csv_path = OUT_DIR / f"{code}.csv"
    if not csv_path.exists():
        today = datetime.date.today().isoformat()
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerow({k: 0 if k != "date" else today for k in FIELDS})
        print(f"✅ 创建占位 CSV: {csv_path}")
    else:
        print(f"🔎 已存在 CSV: {csv_path}")

for meta_file in META_DIR.glob("*.yaml"):
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
    ensure_csv(meta["code"])

print("✅ ETL 完成。所有行业均拥有占位 CSV。")
