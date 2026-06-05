#!/usr/bin/env python3
"""fix_case_formatting.py
统一修复32个案例的排版问题：
1. 删除多余 H1（非表情编号的 # 标题）
2. 将「第一部分/第二部分/第三部分」降级为 ### 子节
3. 旧编号映射：3️⃣→1️⃣1️⃣, 4️⃣→1️⃣2️⃣, 5️⃣→1️⃣3️⃣, 6️⃣→1️⃣4️⃣/1️⃣5️⃣
4. 保持自动洞见区块不变
"""
import re
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
CASE_ROOT = ROOT / "cases" / "by-industry"

# 旧→新编号映射
SECTION_MAP = {
    "3️⃣": "1️⃣1️⃣",
    "4️⃣": "1️⃣2️⃣",
}
# 5️⃣ 和 6️⃣ 需要智能判断——新版中 5️⃣=话语权, 6️⃣=现金流, 13️⃣=拐点, 14️⃣/15️⃣=结论
# 在旧版中 5️⃣=拐点, 6️⃣=结论
SECTION_MAP_SPECIAL = {
    "5️⃣ 拐点判断": "1️⃣3️⃣ 拐点判断",
    "5️⃣ 价值枢纽质量评估": "1️⃣2️⃣ 枢纽质量评估",
    "6️⃣ 结论与投资启示": "1️⃣5️⃣ 结论与投资启示",
}

# 需要重写的额外 H1 标题（这些标题内容会保留，但降级为 ## 或 ###）
# key=行业代码, value=list of (old_h1_prefix, replacement_prefix, new_level)
# 这些将作为子节插入到对应的模板 section 中

def fix_file(path: str) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original = lines[:]
    modified = False
    
    # ── 1. 识别并移除多余 H1 ──
    # 模板的合法 H1 模式：# N️⃣ ... (# 后跟数字+表情符号)
    # 非法 H1 模式：# 任何其他文本
    new_lines = []
    in_frontmatter = True
    skip_h1_text = []  # 被移除的多余 H1 标题文本
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 跳过 frontmatter
        if in_frontmatter:
            new_lines.append(line)
            if stripped == '---':
                in_frontmatter = False
            continue
        
        # 检查是否为多余 H1（非模板编号的 H1 标题）
        if stripped.startswith('# ') and not re.match(r'# \d', stripped) and '️⃣' not in stripped:
            # 多余 H1：如 "# 交通运输产业链结构性分析"
            skip_h1_text.append(stripped[2:])
            modified = True
            continue
        
        new_lines.append(line)
    
    lines = new_lines
    
    # ── 2. 将「第一部分/第二部分/第三部分」降级为 ### ──
    # 但如果它们后面没有属于模板的 ## 节，就保持 ## 但添加编号
    new_lines = []
    part_section_count = 0
    
    for line in lines:
        stripped = line.strip()
        # 匹配 "## 第一部分：" 或 "## 第二部分：" 等
        if re.match(r'^## 第[一二三四五六七八九十]部分', stripped):
            # 降级为 ###，保持原标题
            new_line = line.replace('## ', '### ', 1)
            new_lines.append(new_line)
            modified = True
        elif re.match(r'^## 分析前追问', stripped) or stripped == '## 分析前追问（总则·认知边界）':
            new_lines.append('### 分析前追问（总则·认知边界）\n')
            modified = True
        else:
            new_lines.append(line)
    
    lines = new_lines
    
    # ── 3. 更新旧编号 ──
    new_lines = []
    for line in lines:
        stripped = line.strip()
        
        # 特殊映射（优先匹配完整标题）
        for old, new in SECTION_MAP_SPECIAL.items():
            if old in stripped:
                new_lines.append(line.replace(old, new))
                modified = True
                break
        else:
            # 通用映射
            updated = False
            for old_num, new_num in SECTION_MAP.items():
                if old_num in stripped:
                    new_lines.append(line.replace(f'{old_num} ', f'{new_num} '))
                    modified = True
                    updated = True
                    break
            if not updated:
                new_lines.append(line)
    
    lines = new_lines
    
    # ── 4. 修复特殊问题 ──
    # 有些案例有分离的 auto-insights 区块标记
    new_lines = []
    for line in lines:
        # 修复 "---\n\n### 🔍 自动洞见" 中间的空行问题
        new_lines.append(line)
    
    lines = new_lines
    
    # 写回文件
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    return modified


def main():
    fixed = 0
    total = 0
    errors = []
    
    for f in sorted(CASE_ROOT.rglob("case.md")):
        total += 1
        try:
            # 检查行数
            txt = f.read_text(encoding='utf-8')
            lines_count = len(txt.splitlines())
            
            # 只有 >200 行的旧深度分析才需要修复
            if lines_count > 200:
                result = fix_file(str(f))
                if result:
                    code = f.parent.name.split('-')[0]
                    print(f"  ✅ {f.parent.name} (修复)")
                    fixed += 1
                else:
                    print(f"  ⏭️ {f.parent.name} (无需修复)")
            else:
                print(f"  ⚪ {f.parent.name} (模板)")
        except Exception as e:
            errors.append((str(f), str(e)))
            print(f"  ❌ {f.parent.name}: {e}")
    
    print(f"\n总计 {total} 个案例，修复 {fixed} 个")
    if errors:
        print(f"错误 {len(errors)} 个:")
        for path, err in errors:
            print(f"  {path}: {err}")


if __name__ == "__main__":
    main()
