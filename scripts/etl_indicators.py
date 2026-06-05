#!/usr/bin/env python3
"""etl_indicators.py 合并去重"""
import pandas as pd
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis")
IND_DIR = ROOT / "data" / "indicators"

def main():
    for csv_path in sorted(IND_DIR.glob("*.csv")):
        df = pd.read_csv(csv_path)
        df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
        df.to_csv(csv_path, index=False)
        print(f"✅ 已去重: {csv_path}")

if __name__ == "__main__":
    main()
