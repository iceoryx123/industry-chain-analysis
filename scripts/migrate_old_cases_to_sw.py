#!/usr/bin/env python3
"""
migrate_old_cases_to_sw.py
将 learn/cases/ 下的旧案例迁移到 cases/by-industry/ 的新申万结构中
按行业名称模糊匹配 → 复制内容到对应新目录
"""
import re, shutil
from pathlib import Path
import yaml

ROOT = Path("/tmp/industry-chain-analysis-push")
OLD_CASES = ROOT / "learn" / "cases"
NEW_CASES = ROOT / "cases" / "by-industry"
META_DIR = ROOT / "data" / "meta"

# 旧文件名 → 申万行业名映射（模糊匹配）
OLD_TO_SW = {
    "儿科医院": "医药生物",
    "口腔医院": "医药生物",
    "医药": "医药生物",
    "墓园": "社会服务",
    "民航机场": "交通运输",
    "交通运输": "交通运输",
    "房地产": "房地产",
    "公用事业": "公用事业",
    "消费": "纺织服饰",
    "能源": "煤炭",
    "互联网": "计算机",
    "计算机": "计算机",
    "科技硬件": "电子",
    "电子": "电子",
    "军工": "国防军工",
    "商业航天": "国防军工",
    "精密仪器": "机械设备",
    "制造业": "机械设备",
    "机器人": "机器人",
    "金融": "银行",
    "金融数据与交易所": "非银金融",
    "传媒": "传媒",
    "教育": "社会服务",
    "检验检测与认证": "社会服务",
    "化工新材料": "基础化工",
    "农业与食品饮料": "农林牧渔",
}

def find_sw_code(sw_name: str) -> str:
    """根据申万行业名找到对应的 meta code"""
    for f in META_DIR.glob("*.yaml"):
        meta = yaml.safe_load(f.read_text())
        if meta.get("name") == sw_name:
            return meta["code"]
    return None

def find_sw_category(subsector: str) -> tuple:
    """根据细分名找 (category, sub_slug)"""
    for f in sorted(META_DIR.glob("*.yaml")):
        meta = yaml.safe_load(f.read_text())
        if meta.get("subsector", "").lower() in subsector.lower() or subsector.lower() in meta.get("subsector", "").lower():
            return meta["category"], meta["code"]
    return None, None

def migrate_one(old_file: Path):
    fname = old_file.stem  # e.g. "01-儿科医院"
    # 提取行业名
    match = re.search(r'\d+-(.+)', fname)
    if not match:
        return
    old_name = match.group(1).strip()
    # 映射到申万行业
    sw_name = OLD_TO_SW.get(old_name)
    if not sw_name:
        print(f"  ⚠️ 未匹配：{old_name}")
        return
    # 找对应的 code
    sw_code = find_sw_code(sw_name)
    if not sw_code:
        print(f"  ⚠️ 未找到 code：{sw_name}")
        return
    # 找目标目录
    target_dirs = list(NEW_CASES.glob(f"**/{sw_code}-{sw_name}/"))
    if not target_dirs:
        print(f"  ⚠️ 目标目录缺失：{sw_code}-{sw_name}")
        return
    target_dir = target_dirs[0]
    target_md = target_dir / "case.md"

    # 读取旧内容
    old_content = old_file.read_text(encoding="utf-8")
    # 读取新模板内容
    new_content = target_md.read_text(encoding="utf-8")

    # 把旧内容追加到新模式板的 "产业链全景" 之后
    merged = new_content.replace(
        "## 2️⃣ 产业链全景",
        f"## 2️⃣ 产业链全景\n\n{old_content}"
    )
    target_md.write_text(merged, encoding="utf-8")

    # 同时复制 indicators.yaml
    old_ind = old_file.parent.parent / "indicators" / f"{old_name}.yaml"
    if old_ind.exists():
        shutil.copy(old_ind, target_dir / "indicators.yaml")

    print(f"  ✅ {old_name} → {sw_name} ({sw_code})")

def main():
    print("=" * 60)
    print("🔄 旧案例迁移 → 申万结构")
    print("=" * 60)
    count = 0
    for f in sorted(OLD_CASES.glob("*.md")):
        migrate_one(f)
        count += 1
    print(f"\n✅ 共处理 {count} 个旧案例")

if __name__ == "__main__":
    main()
