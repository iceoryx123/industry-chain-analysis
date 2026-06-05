#!/usr/bin/env python3
"""
迁移案例到申万行业目录结构
"""

import os, shutil, datetime, yaml
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis")
LEARN_DIR = ROOT / "learn" / "cases"
CASE_ROOT = ROOT / "cases" / "by-industry"
META_DIR = ROOT / "data" / "meta"

# 与 assign_shenwan_classification.py 保持一致的映射
CASE_MAPPING = [
    ("01", "儿科医院",      "150000", "医药生物"),
    ("02", "口腔医院",      "150000", "医药生物"),
    ("03", "墓园",          "200000", "社会服务"),
    ("04", "民航机场",      "170000", "交通运输"),
    ("05", "医药",          "150000", "医药生物"),
    ("06", "金融",          "320000", "银行"),
    ("07", "房地产",        "180000", "房地产"),
    ("08", "公用事业",      "160000", "公用事业"),
    ("09", "消费",          "120000", "食品饮料"),
    ("10", "能源",          "370000", "石油石化"),
    ("11", "互联网",        "290000", "计算机"),
    ("12", "制造业",        "390000", "机械设备"),
    ("13", "科技硬件",      "280000", "电子"),
    ("14", "军工",          "250000", "国防军工"),
    ("15", "农业与食品饮料", "110000", "农林牧渔"),
    ("16", "交通运输",      "170000", "交通运输"),
    ("17", "传媒",          "300000", "传媒"),
    ("18", "教育",          "200000", "社会服务"),
    ("19", "科技行业",      "290000", "计算机"),
    ("20", "AI行业",        "290000", "计算机"),
    ("21", "机器人",        "390000", "机械设备"),
    ("22", "精密仪器",      "280000", "电子"),
    ("23", "金融数据与交易所", "330000", "非银金融"),
    ("24", "检验检测与认证(TIC)", "200000", "社会服务"),
    ("25", "商业航天",      "250000", "国防军工"),
    ("26", "化工新材料",    "380000", "基础化工"),
]

def migrate_case(seq, name, sw_code, sw_name):
    """迁移单个案例文件"""
    src = LEARN_DIR / f"{seq}-{name}.md"
    if not src.exists():
        print(f"  ⚠️ 源文件不存在: {src}")
        return None

    # 目标目录: cases/by-industry/{sw_code}-{sw_name}/{sw_code}-{seq}-{name}/
    sw_dir_name = f"{sw_code}-{sw_name}"
    case_dir_name = f"{sw_code}-{seq}-{name}"
    dst_dir = CASE_ROOT / sw_dir_name / case_dir_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_md = dst_dir / "case.md"

    # 读取内容，添加 YAML 头
    content = src.read_text(encoding="utf-8")

    header = f"""---
title: "{name}产业链分析"
industry_code: "{sw_code}-{seq}"
shenwan_industry: "{sw_name}"
version: "v9.2"
date: "{datetime.date.today().isoformat()}"
---

"""
    dst_md.write_text(header + content, encoding="utf-8")
    print(f"  ✅ {seq} {name} → {sw_name}/{case_dir_name}")

    # 也创建指标 CSV（如果还没有）
    ind_dir = ROOT / "data" / "indicators"
    ind_dir.mkdir(parents=True, exist_ok=True)
    csv_path = ind_dir / f"{sw_code}-{seq}.csv"
    if not csv_path.exists():
        today = datetime.date.today().isoformat()
        csv_content = f"""date,market_size_cny_bn,cr4,hhi,gross_margin,roe,rd_intensity,network_intensity,platform_users_million,average_transaction_value_cny
{today},0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
"""
        csv_path.write_text(csv_content, encoding="utf-8")
        print(f"  ✅ CSV 创建: {csv_path.name}")

    return dst_md

def main():
    print("="*60)
    print("🔄 开始迁移案例到申万行业目录")
    print("="*60)

    for seq, name, sw_code, sw_name in CASE_MAPPING:
        migrate_case(seq, name, sw_code, sw_name)

    # 清理旧的 meta 文件（保持只有新格式）
    old_metas = list(META_DIR.glob("*.yaml"))
    for f in old_metas:
        code = f.stem
        # 旧格式如 0101, 0102 没有 - 分隔，新格式有 -
        if "-" not in code:
            f.unlink()
            print(f"  🗑️ 删除旧 meta: {f.name}")

    print("\n✅ 迁移完成！")
    print(f"\n📁 案例新位置: {CASE_ROOT}/")
    for d in sorted(CASE_ROOT.iterdir()):
        if d.is_dir():
            n = len(list(d.glob("*/case.md")))
            print(f"   📂 {d.name} ({n}个案例)")

if __name__ == "__main__":
    main()
