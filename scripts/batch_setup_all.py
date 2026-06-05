#!/usr/bin/env python3
"""batch_setup_all.py
一次性完成：
1. 为 26 个行业创建 data/meta/*.yaml
2. 创建 data/indicators/*.csv（含占位数据）
3. 创建 cases/by-industry/<cat>/<subsector>/<code>-<name>/case.md
"""

import os, datetime, yaml, pandas as pd
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis")
LEARN = ROOT / "learn" / "cases"
META_DIR = ROOT / "data" / "meta"
IND_DIR = ROOT / "data" / "indicators"
CASE_ROOT = ROOT / "cases" / "by-industry"
META_DIR.mkdir(parents=True, exist_ok=True)
IND_DIR.mkdir(parents=True, exist_ok=True)

# ========== 行业分类映射 ==========
INDUSTRY_MAP = [
    # (序号, 名称, category, subsector, has_network, ticker)
    (1,  "儿科医院",           "01‑Traditional", "Healthcare",          False, "300015.SZ"),
    (2,  "口腔医院",           "01‑Traditional", "Healthcare",          False, "600763.SH"),
    (3,  "墓园",               "01‑Traditional", "RealEstate",          False, ""),
    (4,  "民航机场",           "01‑Traditional", "Transportation",      False, "600029.SH"),
    (5,  "医药",               "01‑Traditional", "Healthcare",          False, "600276.SH"),
    (6,  "金融",               "03‑Regulated",   "Banking",             False, "601398.SH"),
    (7,  "房地产",             "01‑Traditional", "RealEstate",          False, "000002.SZ"),
    (8,  "公用事业",           "01‑Traditional", "Utilities",           False, "600900.SH"),
    (9,  "消费",               "01‑Traditional", "Consumer",            False, "600887.SH"),
    (10, "能源",               "01‑Traditional", "Energy",              False, "601857.SH"),
    (11, "互联网",             "02‑Platform",    "Internet",            True,  "BABA"),
    (12, "制造业",             "01‑Traditional", "Manufacturing",       False, "000333.SZ"),
    (13, "科技硬件",           "01‑Traditional", "TechHardware",        False, "002415.SZ"),
    (14, "军工",               "01‑Traditional", "Defense",             False, "600760.SH"),
    (15, "农业与食品饮料",      "01‑Traditional", "Agriculture",         False, "002714.SZ"),
    (16, "交通运输",           "01‑Traditional", "Transportation",      False, "601006.SH"),
    (17, "传媒",               "02‑Platform",    "Media",               True,  "300413.SZ"),
    (18, "教育",               "01‑Traditional", "Education",           False, ""),
    (19, "科技行业",           "02‑Platform",    "Tech",                True,  "00700.HK"),
    (20, "AI行业",             "02‑Platform",    "AISector",            True,  "BIDU"),
    (21, "机器人",             "04‑Emerging",    "Robotics",            True,  "300124.SZ"),
    (22, "精密仪器",           "01‑Traditional", "PrecisionInstrument", False, "002236.SZ"),
    (23, "金融数据与交易所",    "03‑Regulated",   "FinData",             True,  ""),
    (24, "检验检测与认证(TIC)", "01‑Traditional", "TIC",                 False, "300012.SZ"),
    (25, "商业航天",           "04‑Emerging",    "Space",               True,  ""),
    (26, "化工新材料",          "01‑Traditional", "ChemMaterials",       False, "600309.SH"),
]

TODAY = datetime.date.today().isoformat()

# ========== 1️⃣ 创建 meta YAML ==========
for num, name, cat, sub, net, ticker in INDUSTRY_MAP:
    code = f"{num:04d}"
    meta = {
        "code": code,
        "name": name,
        "category": cat,
        "subsector": sub,
        "has_network_effect": net,
        "update_cycle": "monthly" if net else "quarterly",
        "data_source": ["Wind", "公司年报"],
        "representative_ticker": ticker,
        "official_website": "",
    }
    meta_path = META_DIR / f"{code}.yaml"
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"✅ meta/{code}.yaml — {name}")

# ========== 2️⃣ 创建指标 CSV ==========
FIELDS = ["date","market_size_cny_bn","cr4","hhi","gross_margin","roe","rd_intensity",
          "network_intensity","platform_users_million","average_transaction_value_cny"]

for num, name, cat, sub, net, ticker in INDUSTRY_MAP:
    code = f"{num:04d}"
    csv_path = IND_DIR / f"{code}.csv"
    if csv_path.exists():
        print(f"  ⏭  CSV 已存在: {code}")
        continue
    # 生成两期占位数据
    rows = []
    for i, offset in enumerate([-90, -60, -30]):
        d = (datetime.date.today() + datetime.timedelta(days=offset)).isoformat()
        if net:  # 平台行业
            rows.append({
                "date": d, "market_size_cny_bn": 0, "cr4": 0, "hhi": 0,
                "gross_margin": 0, "roe": 0, "rd_intensity": 0,
                "network_intensity": round(0.5 + i*0.05, 3),
                "platform_users_million": round(300 + i*20, 0),
                "average_transaction_value_cny": round(30 + i*3, 1),
            })
        else:  # 传统行业
            rows.append({
                "date": d, "market_size_cny_bn": round(80 + i*5, 0),
                "cr4": round(0.15 + i*0.02, 3),
                "hhi": round(700 + i*30, 0),
                "gross_margin": round(0.35 + i*0.02, 3),
                "roe": round(0.15 + i*0.01, 3),
                "rd_intensity": round(0.03, 3),
                "network_intensity": 0, "platform_users_million": 0, "average_transaction_value_cny": 0,
            })
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV/{code}.csv — {name}")

# ========== 3️⃣ 创建案例文件 ==========
TEMPLATE_V9 = """---
title: "{name}产业链分析"
industry_code: "{code}"
version: "v9.2"
subsector: "{sub}"
date: "{today}"
authors:
  - "自动生成占位"
tags: ["{name}", "{sub}"]
---

# 1️⃣ 版本选择
> 本案例使用 **v9.2**（传统四层链）框架。

## 2️⃣ 产业链全景
（请自行补充）

## 3️⃣ 价值枢纽识别
（请自行补充）

## 4️⃣ 枢纽质量评估
（请自行补充）

## 5️⃣ 拐点判断
（请自行补充）

## 6️⃣ 结论与启示
（请自行补充）

---

> **关键指标**
> - 市场规模：{{ indicator.market_size_cny_bn }} 亿元
> - CR4：{{ indicator.cr4 }}
> - HHI：{{ indicator.hhi }}
> - 毛利率：{{ indicator.gross_margin }}
> - ROE：{{ indicator.roe }}
> - 研发强度：{{ indicator.rd_intensity }}
"""

TEMPLATE_V10 = """---
title: "{name}产业链分析"
industry_code: "{code}"
version: "v10.x"
subsector: "{sub}"
date: "{today}"
authors:
  - "自动生成占位"
tags: ["{name}", "{sub}"]
---

# 1️⃣ 版本选择
> 本案例使用 **v10.x**（双模链 + 价值网）框架。

## 2️⃣ 产业链 & 价值网全景
（请自行补充）

## 3️⃣ 价值枢纽识别
（请自行补充）

## 4️⃣ 枢纽质量评估
（请自行补充）

## 5️⃣ 网络效应指标
（请自行补充）

## 6️⃣ 拐点判断
（请自行补充）

## 7️⃣ 结论与启示
（请自行补充）

---

> **关键指标**
> - 网络强度：{{ indicator.network_intensity }}
> - 平台用户：{{ indicator.platform_users_million }} 百万人
> - 平均交易额：{{ indicator.average_transaction_value_cny }} 元
> - 市场规模：{{ indicator.market_size_cny_bn }} 亿元
"""

for num, name, cat, sub, net, ticker in INDUSTRY_MAP:
    code = f"{num:04d}"
    template = TEMPLATE_V10 if net else TEMPLATE_V9
    content = template.format(code=code, name=name, sub=sub, today=TODAY)

    case_dir = CASE_ROOT / cat / sub.lower().replace(" ", "-") / f"{code}-{name}"
    case_dir.mkdir(parents=True, exist_ok=True)
    case_path = case_dir / "case.md"
    if not case_path.exists():
        case_path.write_text(content, encoding="utf-8")
        print(f"✅ case/{code}-{name}/case.md")
    else:
        print(f"  ⏭  案例已存在: {code}-{name}")

print("\n🎉 全部完成！")
