#!/usr/bin/env python3
"""
申万一级行业分类映射工具
将 26 个学习案例按申万一级行业（2021版）重新分类
并生成对应的 data/meta/ 元数据文件
"""

import os, datetime, yaml, shutil
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
META_DIR = ROOT / "data" / "meta"
META_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# 申万一级行业分类（2021版，31个）
# =========================================================
SHENWAN_LEVEL1 = {
    "110000": "农林牧渔",
    "120000": "食品饮料",
    "130000": "纺织服饰",
    "140000": "轻工制造",
    "150000": "医药生物",
    "160000": "公用事业",
    "170000": "交通运输",
    "180000": "房地产",
    "190000": "商贸零售",
    "200000": "社会服务",
    "210000": "综合",
    "220000": "建筑材料",
    "230000": "建筑装饰",
    "240000": "电力设备",
    "250000": "国防军工",
    "260000": "汽车",
    "270000": "家用电器",
    "280000": "电子",
    "290000": "计算机",
    "300000": "传媒",
    "310000": "通信",
    "320000": "银行",
    "330000": "非银金融",
    "340000": "钢铁",
    "350000": "有色金属",
    "360000": "煤炭",
    "370000": "石油石化",
    "380000": "基础化工",
    "390000": "机械设备",
    "400000": "环保",
    "410000": "美容护理",
}

# =========================================================
# 26个案例 → 申万一级行业 映射表
# =========================================================
# 格式: (序号, 案例名, 申万代码, 申万名, 子行业)
CASE_MAPPING = [
    ("01", "儿科医院",      "150000", "医药生物",     "医疗服务"),
    ("02", "口腔医院",      "150000", "医药生物",     "医疗服务"),
    ("03", "墓园",          "200000", "社会服务",     "殡葬服务"),
    ("04", "民航机场",      "170000", "交通运输",     "机场航空"),
    ("05", "医药",          "150000", "医药生物",     "医药商业"),
    ("06", "金融",          "320000", "银行",         "银行业"),
    ("07", "房地产",        "180000", "房地产",       "房地产开发"),
    ("08", "公用事业",      "160000", "公用事业",     "电力水务燃气"),
    ("09", "消费",          "120000", "食品饮料",     "消费综合"),
    ("10", "能源",          "370000", "石油石化",     "能源综合"),
    ("11", "互联网",        "290000", "计算机",       "互联网服务"),
    ("12", "制造业",        "390000", "机械设备",     "通用设备"),
    ("13", "科技硬件",      "280000", "电子",         "消费电子"),
    ("14", "军工",          "250000", "国防军工",     "军工装备"),
    ("15", "农业与食品饮料", "110000", "农林牧渔",    "农业综合"),
    ("16", "交通运输",      "170000", "交通运输",     "物流运输"),
    ("17", "传媒",          "300000", "传媒",         "文化传媒"),
    ("18", "教育",          "200000", "社会服务",     "教育"),
    ("19", "科技行业",      "290000", "计算机",       "IT服务"),
    ("20", "AI行业",        "290000", "计算机",       "人工智能"),
    ("21", "机器人",        "390000", "机械设备",     "自动化设备"),
    ("22", "精密仪器",      "280000", "电子",         "仪器仪表"),
    ("23", "金融数据与交易所", "330000", "非银金融",  "金融信息服务"),
    ("24", "检验检测与认证(TIC)", "200000", "社会服务", "专业服务"),
    ("25", "商业航天",      "250000", "国防军工",     "航天装备"),
    ("26", "化工新材料",    "380000", "基础化工",     "化工新材料"),
]

def generate_meta():
    """为每个案例生成元数据文件"""
    for seq, name, sw_code, sw_name, subsector in CASE_MAPPING:
        code = f"{sw_code}-{seq}"
        meta = {
            "code": code,
            "name": name,
            "shenwan_code": sw_code,
            "shenwan_industry": sw_name,
            "subsector": subsector,
            "category": "申万一级行业",
            "has_network_effect": False,
            "update_cycle": "quarterly",
            "data_source": ["Wind", "公司年报", "公开数据"],
            "representative_ticker": "",
            "official_website": "",
            "description": f"{name} — 申万{sw_name}行业下的{subsector}子行业",
        }

        # 为互联网、AI、平台类行业标记网络效应
        if name in ["互联网", "AI行业", "科技行业", "金融数据与交易所", "传媒", "教育"]:
            meta["has_network_effect"] = True
            meta["update_cycle"] = "monthly"

        # 写入 YAML
        filepath = META_DIR / f"{code}.yaml"
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(meta, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"✅ {code} {name} → {sw_name}/{subsector}")

def create_sample_case():
    """创建一个示例案例文件展示新结构"""
    case_dir = ROOT / "cases" / "by-industry" / "150000-医药生物"
    case_dir.mkdir(parents=True, exist_ok=True)
    case_md = case_dir / "150000-01-儿科医院" / "case.md"
    case_md.parent.mkdir(parents=True, exist_ok=True)
    if not case_md.exists():
        case_md.write_text(f"""---
title: "儿科医院产业链分析"
industry_code: "150000-01"
shenwan_industry: "医药生物"
version: "v9.2"
date: "{datetime.date.today().isoformat()}"
---

# 儿科医院产业链分析

## 产业链全景

（此处填写分析内容）

---
自动生成时间: {datetime.date.today().isoformat()}
""", encoding="utf-8")
        print(f"✅ 示例案例已生成: {case_md}")

def summary():
    """输出汇总表"""
    print("\n" + "="*70)
    print("📊 申万一级行业分类汇总")
    print("="*70)
    by_sw = {}
    for seq, name, sw_code, sw_name, subsector in CASE_MAPPING:
        by_sw.setdefault(sw_name, []).append(name)
    for sw_name, cases in sorted(by_sw.items()):
        print(f"\n📁 {sw_name} ({len(cases)}个案例)")
        for c in cases:
            print(f"   - {c}")

if __name__ == "__main__":
    generate_meta()
    create_sample_case()
    summary()
