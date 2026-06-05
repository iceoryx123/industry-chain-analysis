#!/usr/bin/env python3
"""
修复案例文件中遗留的 Jinja2 占位符和过时的类别标签。
- 替换 {{ "..." if version == "v10.x" else "..." }} → else 分支结果
- 读取 meta/*.yaml 更新洞察段落的「类别」字段
- 清理其他零散模板残留
"""
import re, yaml
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")

# 加载所有 meta
meta_by_code = {}
for f in (ROOT / "data" / "meta").glob("*.yaml"):
    m = yaml.safe_load(f.read_text())
    if m and "code" in m:
        meta_by_code[m["code"]] = m

def fix_case(case_md: Path):
    txt = case_md.read_text(encoding="utf-8")
    changed = False

    # 提取 industry_code
    code_m = re.search(r'industry_code:\s*["\']?([\w-]+)', txt)
    code = code_m.group(1) if code_m else None
    sw_code = code.split("-")[0] if code and "-" in code else code

    # 1. 修复 Jinja2 条件语句 → 取 else 分支
    pattern = r'\{\{\s*"([^"]*)"\s+if\s+version\s*==\s*"v10\.x"\s+else\s+"([^"]*)"\s*\}\}'
    new_txt = re.sub(pattern, r'\2', txt)
    if new_txt != txt:
        changed = True
        txt = new_txt
        print(f"  ✅ Jinja2 条件已修复")

    # 2. 从 meta 获取正确类别，更新洞察段
    meta = None
    if sw_code and sw_code in meta_by_code:
        meta = meta_by_code[sw_code]
    elif code and code in meta_by_code:
        meta = meta_by_code[code]

    if meta:
        correct_category = meta["category"]
        # 修复 "**类别**：04-Emerging" → 正确类别
        cat_search = f"**类别**："
        for old_cat in ["04-Emerging", "01-Traditional", "02-Platform", "03-Regulated"]:
            old_str = f"{cat_search}{old_cat}"
            new_str = f"{cat_search}{correct_category}"
            if old_str in txt and old_cat != correct_category:
                txt = txt.replace(old_str, new_str)
                changed = True
                print(f"  ✅ 类别已更新: {old_cat} → {correct_category}")
                break

    # 3. 替换 {{ name }} 等残留（如果还没被替换的话）
    for placeholder in ["{{ name }}", "{{ code }}", "{{ version }}", "{{ subsector }}", "{{ today }}"]:
        if placeholder in txt:
            txt = txt.replace(placeholder, "")
            changed = True
            print(f"  ⚠️ 清理残留占位符: {placeholder}")

    if changed:
        case_md.write_text(txt, encoding="utf-8")
        print(f"  💾 已保存: {case_md.relative_to(ROOT)}")
    else:
        print(f"  🔎 无需修改: {case_md.relative_to(ROOT)}")

def main():
    cases = sorted(ROOT.glob("cases/**/*/case.md"))
    print(f"共发现 {len(cases)} 个案例文件")
    for f in cases:
        rel = f.relative_to(ROOT)
        fix_case(f)

if __name__ == "__main__":
    main()
