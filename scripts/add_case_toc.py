#!/usr/bin/env python3
"""
add_case_toc.py — 为所有案例添加目录(TOC) + 内容概要 + 内容排序分类

功能：
1. 在每个案例的 `# 1️⃣ 版本选择` 之后注入标准 TOC 区块
2. 自动解析章节结构生成可读目录
3. 根据章节分布自动生成内容概要
4. 统一章节排序逻辑
"""
import re
from pathlib import Path

REPO = Path("/tmp/industry-chain-analysis")
CASE_GLOB = "cases/by-industry/*/*/*/case.md"  # 三级：category/subsector/code-name/
# 实际上部分 case 在二级目录直接下，用 rglob 更可靠

# ── 标准章节定义（用于排序和分类） ──
SECTION_ORDER = {
    # 基础框架
    "2️⃣": ("产业链全景", "foundation"),
    "3️⃣": ("价值枢纽识别", "foundation"),
    "4️⃣": ("枢纽质量评估", "foundation"),
    "1️⃣1️⃣": ("商业模式分析", "module"),
    "1️⃣2️⃣": ("护城河类型诊断", "module"),
    "5️⃣": ("话语权地图", "module"),
    "6️⃣": ("现金流质量分析", "module"),
    # 老编号 → 新编号映射已在 fix_case_formatting 处理
    "7️⃣": ("资本回报与增长定位", "module"),
    "8️⃣": ("增长引擎分析", "supplement"),
    "9️⃣": ("周期定位", "supplement"),
    "1️⃣0️⃣": ("行业分化方向", "supplement"),
    "1️⃣3️⃣": ("颠覆风险", "supplement"),
    "1️⃣4️⃣": ("跨行业比较", "supplement"),
    "1️⃣5️⃣": ("结论与投资启示", "conclusion"),
    # 特殊
    "🔍": ("自动洞见", "auto"),
    "⏱️": ("数据时效", "meta"),
}

META_SECTIONS = {"---", "自动洞见", "数据时效", "数据来源", "免责声明"}


def extract_sections(text: str) -> list[tuple[str, str, int]]:
    """从文本中提取所有标题行及其层级"""
    sections = []
    for line in text.splitlines():
        m = re.match(r'^(#{1,4})\s+(.+)$', line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            # 排除 frontmatter
            if title == "---":
                continue
            sections.append((title, level))
    return sections


def classify_section(title: str) -> str:
    """分类章节类型"""
    # 匹配 emoji 编号
    for emoji, (name, cat) in SECTION_ORDER.items():
        if title.startswith(emoji):
            return cat
    # 匹配关键词
    if "自动洞见" in title or "🔍" in title:
        return "auto"
    if "数据时效" in title or "⏱️" in title or "数据来源" in title:
        return "meta"
    if "总结" in title or "结论" in title or "💡" in title:
        return "conclusion"
    if "标准模块" in title:
        return "module"
    if "第一部分" in title or "第二部分" in title or "第零层" in title or "行业拆分" in title:
        return "foundation"
    if "子行业" in title:
        return "sub_industry"
    return "other"


def count_sub_industries(sections: list[tuple[str, int]]) -> list[str]:
    """提取子行业名称列表"""
    subs = []
    for title, level in sections:
        m = re.match(r'^(?:###\s+)?(?:子行业[一二三四五六七八九十]+[：:]|###?\s*[A-D][.．、]\s*)(.+?)(?:\s*$|（)', title)
        if m:
            subs.append(m.group(1).strip())
        # Also catch patterns like "A. 创新药" or "B. 运动鞋服"
        m2 = re.match(r'^[A-D][.．、]\s*(.+?)(?:\s*$|（)', title)
        if m2:
            name = m2.group(1).strip()
            if name not in subs and len(name) < 20:
                subs.append(name)
    return subs


def detect_framework(text: str) -> str:
    """检测框架版本"""
    if "v10" in text[:2000]:
        return "v10.x（价值网）"
    if "v9" in text[:2000]:
        return "v9.2（传统链）"
    return "自动检测"


def generate_toc_block(sections: list[tuple[str, int]]) -> str:
    """生成目录区块"""
    # 只取 ## 和 ### 级别的标题
    toc_lines = []
    toc_lines.append("## 📑 目录")
    toc_lines.append("")
    for title, level in sections:
        if level > 3:
            continue
        # 跳过 TOC/Summary 自身
        if title in ("📑 目录", "📋 内容概要"):
            continue
        # 跳过一级目录本身
        if title == "1️⃣ 版本选择":
            continue
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- {title}")
    toc_lines.append("")
    return "\n".join(toc_lines)


def generate_summary_block(
    sections: list[tuple[str, int]],
    industry_name: str,
    framework: str,
    report_period: str,
    subs: list[str],
) -> str:
    """生成内容概要区块"""
    lines = []
    lines.append("## 📋 内容概要")
    lines.append("")
    lines.append(f"| 维度 | 说明 |")
    lines.append(f"|------|------|")
    lines.append(f"| **行业** | {industry_name} |")
    lines.append(f"| **框架** | {framework} |")
    if subs:
        sub_str = "、".join(subs[:6])
        if len(subs) > 6:
            sub_str += f" 等{len(subs)}个细分领域"
        lines.append(f"| **分析范围** | {sub_str} |")
    lines.append(f"| **数据报告期** | {report_period} |")
    lines.append("")
    
    # 章节分布统计
    cat_counts = {}
    for title, level in sections:
        if level == 2 and not any(m in title for m in META_SECTIONS):
            cat = classify_section(title)
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    type_labels = {
        "foundation": "🏗️ 基础框架分析",
        "sub_industry": "🔹 子行业分析",
        "module": "📦 标准模块",
        "supplement": "🧩 补充模块",
        "auto": "🤖 自动洞见",
        "conclusion": "💡 总结",
        "meta": "⏱️ 数据信息",
    }
    
    if cat_counts:
        lines.append("**内容结构：**")
        for cat in ["foundation", "sub_industry", "module", "supplement", "auto", "conclusion"]:
            count = cat_counts.get(cat, 0)
            if count > 0:
                label = type_labels.get(cat, cat)
                lines.append(f"- {label}：{count} 节")
        lines.append("")
    
    lines.append("**章节速览：**")
    for title, level in sections:
        if level > 2:
            continue
        if title in ("📑 目录", "📋 内容概要"):
            continue
        if any(m in title for m in META_SECTIONS):
            continue
        cat = classify_section(title)
        icon = {"foundation": "🏗️", "module": "📦", "supplement": "🧩", 
                "sub_industry": "🔹", "auto": "🤖", "conclusion": "💡", 
                "meta": "⏱️"}.get(cat, "📄")
        lines.append(f"- {icon} {title}")
    
    lines.append("")
    return "\n".join(lines)


def inject_toc(text: str) -> tuple[str, bool]:
    """向案例文本中注入 TOC 和概要"""
    lines = text.splitlines()
    modified = False
    
    # 检查是否已有 TOC 或概要
    if any("📑 目录" in l for l in lines) and any("📋 内容概要" in l for l in lines):
        return text, False
    
    # 解析 sections
    sections = extract_sections(text)
    
    # 获取行业名称（从 frontmatter 或第一个 section）
    industry_name = ""
    for line in lines:
        m = re.match(r'^title:\s*"?(.+?)"?\s*$', line)
        if m:
            industry_name = m.group(1).replace("产业链分析", "").strip()
            break
    if not industry_name:
        industry_name = "未知行业"
    
    # 获取报告期
    report_period = ""
    for line in lines:
        m = re.match(r'.*报告期[：:]\s*(.+?)[\s）\)]', line)
        if m:
            report_period = m.group(1)
            break
    if not report_period:
        report_period = "2026-03-31"
    
    # 检测框架
    framework = detect_framework(text)
    
    # 提取子行业
    subs = count_sub_industries(sections)
    
    # 注入位置：# 1️⃣ 版本选择 之后
    inject_pos = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("# ") and "版本选择" in stripped:
            inject_pos = i + 1
            break
    
    if inject_pos < 0:
        return text, False
    
    # 找到 injection 位置后跳过空行
    while inject_pos < len(lines) and lines[inject_pos].strip() == "":
        inject_pos += 1
    
    # 生成 TOC + 概要
    toc_block = generate_toc_block(sections)
    summary_block = generate_summary_block(sections, industry_name, framework, report_period, subs)
    
    # 在 inject_pos 前插入分隔符
    sep = "\n---\n\n"
    new_block = sep + toc_block + "\n" + summary_block + "\n---\n"
    
    # 提取版本选择行的原有后续内容（以便知道要保留什么）
    # 找到第一个 ## 或 #（非版本选择）的位置
    first_section_after = inject_pos
    for i in range(inject_pos, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## ") or (stripped.startswith("# ") and "版本选择" not in stripped):
            first_section_after = i
            break
    
    # 构建新内容：版本选择行 → TOC → 摘要 → 后续内容
    new_lines = lines[:inject_pos]
    new_lines.append(new_block)
    new_lines.extend(lines[first_section_after:])
    
    modified = True
    return "\n".join(new_lines), modified


def main():
    cases = sorted(Path(REPO).rglob("case.md"))
    # 只处理 cases/by-industry/ 下的
    cases = [f for f in cases if "cases/by-industry" in str(f)]
    updated = 0
    skipped = 0
    errors = []
    
    print(f"🔍 发现 {len(cases)} 个案例文件\n")
    
    for f in cases:
        code = f.parent.name
        lines_count = 0
        try:
            text = f.read_text(encoding="utf-8")
            lines_count = len(text.splitlines())
            
            # 只处理深度案例（>200行）或已有框架占位的
            if lines_count < 170:
                skipped += 1
                continue
            
            new_text, changed = inject_toc(text)
            if changed:
                f.write_text(new_text, encoding="utf-8")
                updated += 1
                print(f"  ✅ {code} ({lines_count}行) → 已添加 TOC+概要")
            else:
                print(f"  ⏭️ {code} ({lines_count}行) → 已有 TOC/概要，跳过")
                skipped += 1
        except Exception as e:
            errors.append((str(f), str(e)))
            print(f"  ❌ {code}: {e}")
    
    print(f"\n📊 结果：{updated} 个已更新，{skipped} 个跳过，{len(errors)} 个错误")
    if errors:
        for path, err in errors:
            print(f"  ⚠️ {path}: {err}")


if __name__ == "__main__":
    main()
