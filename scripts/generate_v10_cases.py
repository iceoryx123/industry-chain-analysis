#!/usr/bin/env python3
"""generate_v10_cases.py
自动为所有 category 为 "02‑Platform" 的行业生成案例占位文件（case.md + indicators.yaml）。
与 v9.2 类似，只是 version 为 v10.x，并在模板里留出网络效应占位。
"""

import os, shutil, datetime
from pathlib import Path
import yaml

ROOT = Path(os.getenv("WORKSPACE", "/tmp/industry-chain-analysis-push"))
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry" / "02-Platform"
TEMPLATE_CASE = ROOT / "templates" / "case_template_v10.md"
TEMPLATE_IND = ROOT / "templates" / "indicators_template.yaml"

if not TEMPLATE_CASE.exists():
    TEMPLATE_CASE.write_text("""---
title: "{{ name }}产业链分析"
industry_code: "{{ code }}"
version: "v10.x"
subsector: "{{ subsector }}"
date: "{{ today }}"
authors:
  - "自动生成占位"
tags: ["{{ name }}", "{{ subsector }}"]
---

# 1️⃣ 版本选择
> 本案例使用 **v10.x**（双模链 + 价值网）框架。

## 2️⃣ 产业链 & 价值网全景
（请自行补充链和网两层结构）

## 3️⃣ 价值枢纽识别
- **链枢纽**（如核心供应商）
- **网枢纽**（如平台建网者）
（请自行补充）

## 4️⃣ 枢纽质量评估
（请自行补充）

## 5️⃣ 网络效应指标（示例）
- **平台活跃用户**：{{ indicator.platform_users_million }} 万
- **网络强度指数**：{{ indicator.network_intensity }}
（请自行补充）

## 6️⃣ 拐点判断
（请自行补充）

## 7️⃣ 结论与启示
（请自行补充）
""")

if not TEMPLATE_IND.exists():
    # 已经有通用模板，直接使用
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
        print(f"✅ 创建平台案例占位: {case_md}")
    if not ind_yaml.exists():
        shutil.copy(TEMPLATE_IND, ind_yaml)
        print(f"✅ 创建指标模板: {ind_yaml}")

if __name__ == "__main__":
    for f in META_DIR.glob("*.yaml"):
        meta = yaml.safe_load(f.read_text())
        if meta.get("category") == "02‑Platform":
            ensure_case(meta)
""