#!/usr/bin/env python3
"""generate_v9_cases.py
自动为所有 category 为 "01‑Traditional" 的行业生成案例占位文件（case.md + indicators.yaml）。
- 读取 data/meta/*.yaml
- 若对应目录不存在，则创建并复制模板
"""

import os, shutil, datetime
from pathlib import Path
import yaml

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis-push"))
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry" / "01-Traditional"
TEMPLATE_CASE = ROOT / "templates" / "case_template_v9.md"
TEMPLATE_IND = ROOT / "templates" / "indicators_template.yaml"

# 创建最小模板（若不存在）
if not TEMPLATE_CASE.exists():
    TEMPLATE_CASE.write_text("""---
title: "{{ name }}产业链分析"
industry_code: "{{ code }}"
version: "v9.2"
subsector: "{{ subsector }}"
date: "{{ today }}"
authors:
  - "自动生成占位"
tags: ["{{ name }}", "{{ subsector }}"]
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
""")

if not TEMPLATE_IND.exists():
    # 若模板不存在，使用已有模板复制（这里已经有）
    pass

def ensure_case(meta):
    code = meta["code"]
    name = meta["name"]
    subsector = meta["subsector"]
    today = datetime.date.today().isoformat()
    case_dir = CASE_ROOT / f"{code}-{name}"
    case_dir.mkdir(parents=True, exist_ok=True)
    case_md = case_dir / "case.md"
    ind_yaml = case_dir / "indicators.yaml"
    if not case_md.exists():
        content = TEMPLATE_CASE.read_text().replace("{{ name }}", name)\
                                 .replace("{{ code }}", code)\
                                 .replace("{{ subsector }}", subsector)\
                                 .replace("{{ today }}", today)
        case_md.write_text(content)
        print(f"✅ 创建案例占位: {case_md}")
    if not ind_yaml.exists():
        shutil.copy(TEMPLATE_IND, ind_yaml)
        print(f"✅ 创建指标模板: {ind_yaml}")

if __name__ == "__main__":
    for f in META_DIR.glob("*.yaml"):
        meta = yaml.safe_load(f.read_text())
        if meta.get("category") == "01‑Traditional":
            ensure_case(meta)
""