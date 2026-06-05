#!/usr/bin/env python3
"""
generate_sw_industry_meta.py
按申万一级行业（2024版）生成行业元数据 + 目录结构 + 案例占位
"""
import os, shutil, datetime, re
from pathlib import Path
import yaml

ROOT = Path("/tmp/industry-chain-analysis-push")
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry"
TEMPLATE_V9 = ROOT / "templates" / "case_template_v9.md"
TEMPLATE_V10 = ROOT / "templates" / "case_template_v10.md"
TEMPLATE_IND = ROOT / "templates" / "indicators_template.yaml"
TODAY = datetime.date.today().isoformat()

# ============================================================
# 申万一级行业（2024版）31个
# 字段：code, name, category, subsector, has_network_effect,
#       update_cycle, data_source, representative_ticker, official_website
# ============================================================
SW_INDUSTRIES = [
    # ── 01-Traditional ──────────────────────────────────
    ("801010", "农林牧渔", "01-Traditional", "Agriculture & Food", False, "quarterly",
     ["国家统计局", "Wind", "农业农村部"], "000998.SZ", ""),
    ("801020", "基础化工", "01-Traditional", "Chemicals & New Materials", False, "quarterly",
     ["Wind", "中国石油和化学工业联合会"], "600309.SH", ""),
    ("801030", "钢铁", "01-Traditional", "Steel & Metals", False, "quarterly",
     ["Wind", "中钢协"], "600019.SH", ""),
    ("801040", "有色金属", "01-Traditional", "Non-ferrous Metals", False, "quarterly",
     ["Wind", "安泰科"], "000831.SZ", ""),
    ("801050", "电子", "01-Traditional", "Electronics", False, "quarterly",
     ["Wind", "半导体行业协会"], "002371.SZ", ""),
    ("801080", "建筑装饰", "01-Traditional", "Construction & Decoration", False, "quarterly",
     ["Wind", "住建部"], "601668.SH", ""),
    ("801100", "建筑材料", "01-Traditional", "Building Materials", False, "quarterly",
     ["Wind", "中国建材协会"], "000786.SZ", ""),
    ("801110", "机械设备", "01-Traditional", "Machinery & Equipment", False, "quarterly",
     ["Wind", "中国机械工业联合会"], "601369.SH", ""),
    ("801120", "电力设备", "01-Traditional", "Electrical Equipment", False, "quarterly",
     ["Wind", "中电联"], "002531.SZ", ""),
    ("801150", "医药生物", "01-Traditional", "Healthcare", False, "quarterly",
     ["Wind", "国家药监局", "卫健委"], "300015.SZ", ""),
    ("801200", "纺织服饰", "01-Traditional", "Textile & Apparel", False, "quarterly",
     ["Wind", "中国纺织工业协会"], "002563.SZ", ""),
    ("801210", "轻工制造", "01-Traditional", "Light Manufacturing", False, "quarterly",
     ["Wind", "中国轻工联合会"], "002572.SZ", ""),
    ("801230", "交通运输", "01-Traditional", "Transportation", False, "quarterly",
     ["Wind", "交通运输部"], "600026.SH", ""),
    ("801780", "石油石化", "01-Traditional", "Petroleum & Petrochemical", False, "quarterly",
     ["Wind", "中国石油和化学工业联合会"], "600028.SH", ""),
    ("801890", "综合", "01-Traditional", "Conglomerate", False, "quarterly",
     ["Wind"], "600153.SH", ""),
    ("801070", "汽车", "01-Traditional", "Automotive", False, "quarterly",
     ["Wind", "中汽协"], "600104.SH", ""),

    # ── 02-Platform ─────────────────────────────────────
    ("801060", "计算机", "02-Platform", "Computing & Software", True, "monthly",
     ["Wind", "IDC", "信通院"], "000977.SZ", ""),
    ("801090", "传媒", "02-Platform", "Media & Internet", True, "monthly",
     ["Wind", "艾瑞", "QuestMobile"], "300058.SZ", ""),
    ("801130", "社会服务", "02-Platform", "Social Services & Platform", True, "monthly",
     ["Wind", "国家统计局"], "600138.SH", ""),
    ("801170", "通信", "02-Platform", "Telecom & Network", True, "monthly",
     ["Wind", "工信部", "三大运营商"], "600050.SH", ""),

    # ── 03-Regulated ────────────────────────────────────
    ("801140", "银行", "03-Regulated", "Banking", False, "quarterly",
     ["Wind", "央行", "银保监会"], "601398.SH", ""),
    ("801160", "非银金融", "03-Regulated", "Non-bank Finance", False, "quarterly",
     ["Wind", "证监会", "银保监会"], "601318.SH", ""),
    ("801180", "房地产", "03-Regulated", "Real Estate", False, "quarterly",
     ["Wind", "国家统计局", "住建部"], "000002.SZ", ""),
    ("801190", "公用事业", "03-Regulated", "Utilities", False, "quarterly",
     ["Wind", "国家能源局"], "600900.SH", ""),
    ("801220", "环保", "03-Regulated", "Environmental Protection", False, "quarterly",
     ["Wind", "生态环境部"], "002573.SZ", ""),

    # ── 04-Emerging ─────────────────────────────────────
    ("801710", "国防军工", "04-Emerging", "Defense & Aerospace", False, "quarterly",
     ["Wind", "国防科工局"], "600893.SH", ""),
    ("801720", "美容护理", "04-Emerging", "Beauty & Personal Care", False, "quarterly",
     ["Wind", "中国香料香精化妆品工业协会"], "603160.SH", ""),
    ("801730", "家用电器", "04-Emerging", "Home Appliances", False, "quarterly",
     ["Wind", "中国家电协会"], "000333.SZ", ""),
    ("801740", "商贸零售", "04-Emerging", "Retail & Commerce", False, "quarterly",
     ["Wind", "商务部"], "600827.SH", ""),
    ("801750", "食品饮料", "04-Emerging", "Food & Beverage", False, "quarterly",
     ["Wind", "中国食品工业协会"], "000895.SZ", ""),
    ("801760", "农林牧渔", "04-Emerging", "Agriculture Advanced", False, "quarterly",
     ["Wind", "农业农村部"], "000998.SZ", ""),
    ("801770", "电力设备", "04-Emerging", "New Energy Equipment", True, "monthly",
     ["Wind", "中电联", "中国光伏协会"], "601012.SH", ""),
    ("801790", "煤炭", "04-Emerging", "Coal & Energy Mining", False, "quarterly",
     ["Wind", "中国煤炭工业协会"], "601898.SH", ""),
    ("801880", "机器人", "04-Emerging", "Robotics & AI Hardware", True, "monthly",
     ["Wind", "IFR", "中国电子学会"], "000333.SZ", ""),
]


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def generate_meta_files():
    """生成 data/meta/*.yaml"""
    META_DIR.mkdir(parents=True, exist_ok=True)
    for row in SW_INDUSTRIES:
        code, name, cat, sub, net, cycle, sources, ticker, website = row
        meta = {
            "code": code,
            "name": name,
            "category": cat,
            "subsector": sub,
            "has_network_effect": net,
            "update_cycle": cycle,
            "data_source": sources,
            "representative_ticker": ticker,
            "official_website": website,
            "description": f"{name}（申万一级行业），隶属于 {cat} / {sub} 类别。",
        }
        fpath = META_DIR / f"{code}.yaml"
        fpath.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
        print(f"  ✅ meta: {fpath.name} → {name} ({cat})")


def generate_case_placeholders():
    """生成案例占位目录 + case.md + indicators.yaml"""
    for row in SW_INDUSTRIES:
        code, name, cat, sub, net, cycle, sources, ticker, website = row
        sub_slug = sub.lower().replace(" & ", "-").replace(" ", "-")
        case_dir = CASE_ROOT / cat / sub_slug / f"{code}-{name}"
        ensure_dir(case_dir)

        # 选择模板
        version = "v10.x" if net else "v9.2"
        tpl = TEMPLATE_V10 if net else TEMPLATE_V9

        case_md = case_dir / "case.md"
        if not case_md.exists():
            content = tpl.read_text().replace("{{ name }}", name) \
                                     .replace("{{ code }}", code) \
                                     .replace("{{ subsector }}", sub) \
                                     .replace("{{ version }}", version) \
                                     .replace("{{ today }}", TODAY)
            case_md.write_text(content)
            print(f"  ✅ case: {case_dir.relative_to(ROOT)}")

        ind_yaml = case_dir / "indicators.yaml"
        if not ind_yaml.exists():
            shutil.copy(TEMPLATE_IND, ind_yaml)


def main():
    print("=" * 60)
    print("申万一级行业分类生成器")
    print("=" * 60)
    print()

    print("📁 Step 1/2 — 生成行业元数据 (data/meta/*.yaml)")
    generate_meta_files()

    print()
    print("📁 Step 2/2 — 生成案例占位 (cases/by-industry/)")
    generate_case_placeholders()

    print()
    print("=" * 60)
    print(f"✅ 完成！共处理 {len(SW_INDUSTRIES)} 个申万一级行业")
    print("=" * 60)

    # 统计
    cats = {}
    for row in SW_INDUSTRIES:
        cat = row[2]
        cats[cat] = cats.get(cat, 0) + 1
    print("\n📊 分类统计：")
    for cat, cnt in sorted(cats.items()):
        print(f"  {cat}: {cnt} 个行业")


if __name__ == "__main__":
    main()
