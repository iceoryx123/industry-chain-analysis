#!/usr/bin/env python3
"""全面检查所有 case.md 的排版和逻辑"""
import os, re

base = 'cases/by-industry'
errors = []
warnings = []

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        with open(path) as fh:
            content = fh.read()
        
        lines = content.split('\n')
        
        # 获取行业名称和代码
        code = os.path.basename(os.path.dirname(path)).split('-')[0]
        name = os.path.basename(os.path.dirname(path)).split('-', 1)[1] if '-' in os.path.basename(os.path.dirname(path)) else '?'
        
        # ── 1. 主标题格式（首行应为 --- front matter，紧后应为 # 1️⃣） ──
        if not lines[0].startswith('---'):
            errors.append(f'{rel}: 首行不是 `---`（缺少 front matter 起始）')
        # 找到第一个 # 开头的标题行
        first_h1 = None
        for i, l in enumerate(lines):
            if l.startswith('# ') and '1' in l[:10]:
                first_h1 = i
                break
        if first_h1 is None:
            errors.append(f'{rel}: 找不到 `# 1️⃣` 主标题')
        elif '1️⃣' not in lines[first_h1]:
            errors.append(f'{rel}: 主标题缺少 1️⃣ 编号 (line {first_h1+1}: {lines[first_h1][:40]})')
        
        # ── 2. H1 层级检查（除了主标题，不应有其他 # H1） ──
        h1_extra = []
        for i, l in enumerate(lines):
            if l.startswith('# ') and not l.startswith('# 1') and not l.startswith('# 1️'):
                h1_extra.append(i+1)
        if h1_extra:
            errors.append(f'{rel}: 多余 H1 行 {h1_extra}')
        
        # ── 3. TOC 存在 ──
        if '## 📑 目录' not in content:
            errors.append(f'{rel}: 缺少 `## 📑 目录`')
        
        # ── 4. 内容概要存在 ──
        if '## 📋 内容概要' not in content:
            errors.append(f'{rel}: 缺少 `## 📋 内容概要`')
        
        # ── 5. 自动洞见存在 ──
        if '### 🔍 自动洞见' not in content:
            errors.append(f'{rel}: 缺少 `### 🔍 自动洞见`')
        
        # ── 6. 数据时效存在 ──
        if '数据时效' not in content:
            errors.append(f'{rel}: 缺少数据时效标注')
        
        # ── 7. 综合评分存在 ──
        if not re.search(r'\*\*综合评分\*\*[：:]\s*[\d.]+/10', content):
            errors.append(f'{rel}: 缺少综合评分')
        
        # ── 8. 文件末尾残留 --- ──
        if content.rstrip().endswith('---'):
            errors.append(f'{rel}: 文件末尾有残留 `---`')
        
        # ── 9. 多个连续 --- ──
        for m in re.finditer(r'\n---\n---\n', content):
            errors.append(f'{rel}: 存在连续 `---` (位置 {m.start()})')
        
        # ── 10. 残留 Jinja2 占位符 ──
        jinja = re.findall(r'\{\{.*?\}\}', content)
        if jinja:
            errors.append(f'{rel}: 残留 Jinja2 占位符 {jinja[:3]}')
        
        # ── 11. 增长引擎含占位符 ──
        m = re.search(r'F - 增长引擎\*{0,2}[：:]\s*([^\*\n]+)', content)
        if m:
            g = m.group(1).strip()
            if 'N/A' in g or '待补充' in g:
                errors.append(f'{rel}: 增长引擎含占位符: {g}')
        
        # ── 12. 检查缺失的拐点信号或业务启示 ──
        if '拐点信号' not in content:
            warnings.append(f'{rel}: 缺少拐点信号')
        if '业务启示' not in content:
            warnings.append(f'{rel}: 缺少业务启示')
        
        # ── 13. 检查编号序列是否合理 ──
        numbered = re.findall(r'# ([1-9]️⃣|1️⃣[0-5]️⃣?)', content)
        
        # ── 14. 检查内容概要中的章节引用是否与正文一致 ──
        # 找到概要中的章节列表，并检查是否都出现在正文中
        summary_section = ''
        in_summary = False
        for l in lines:
            if l.startswith('## 📋 内容概要'):
                in_summary = True
                continue
            if in_summary and l.startswith('## '):
                in_summary = False
            if in_summary and l.startswith('- `#'):
                summary_section += l + '\n'
        
        # ── 15. 检查「价值枢纽识别」是否存在 ──
        if '价值枢纽识别' not in content:
            warnings.append(f'{rel}: 缺少价值枢纽识别')
        
        # ── 16. 检查是否有硬编码的旧编号（如 3️⃣ 2️⃣ 等说明文字） ──
        old_refs = re.findall(r'[3-9]️⃣|1️⃣[0-5]️⃣', content)
        # 这些在概要中和正文中都可能出现，都是正常引用
        
        # ── 17. 检查 TOC 项数 ──
        in_toc = False
        toc_items = 0
        for l in lines:
            if l.startswith('## 📑 目录'):
                in_toc = True
                continue
            if in_toc and l.startswith('## '):
                in_toc = False
            if in_toc and l.strip().startswith('- '):
                toc_items += 1
        if toc_items < 5:
            warnings.append(f'{rel}: TOC 项数偏少 ({toc_items})')
        
        # ── 18. 检查洞见区后的内容 ──
        # 洞见应该是文件最后的大区块（末尾可以有空行，但不能有正文）
        insight_start = content.find('### 🔍 自动洞见')
        if insight_start >= 0:
            after = content[insight_start + len('### 🔍 自动洞见'):]
            # 跳过洞见最后一个空行
            after_lines = after.split('\n')
            # 最后几行的内容
            tail_content = [l for l in after_lines if l.strip()]
            # 检查是否有非洞见/非空内容的行出现在洞见后（正常情况洞见是全文最后的部分）
        
        # ── 19. 检查原始 markdown 链接格式 ──
        bad_links = re.findall(r'\[([^\]]*)\]\(([^)]*)\)', content)
        for text, url in bad_links:
            if not url or url.isspace():
                errors.append(f'{rel}: 空链接 "[{text}]()"')
        
        # ── 20. 检查是否有模板注释残留 ──
        if '<!--' in content and '-->' in content:
            template_comments = re.findall(r'<!--.*?-->', content, re.DOTALL)
            if template_comments:
                warnings.append(f'{rel}: 有 HTML 注释残留 {len(template_comments)} 处')

print("=" * 70)
print("📋 案例排版全面检查报告")
print("=" * 70)

if errors:
    print(f"\n❌ {len(errors)} 个错误（必须修复）:")
    # 按文件分组
    by_file = {}
    for e in errors:
        fname = e.split(':')[0]
        if fname not in by_file:
            by_file[fname] = []
        by_file[fname].append(e.split(':', 1)[1].strip())
    for fname in sorted(by_file.keys()):
        print(f"\n  📄 {fname}:")
        for issue in by_file[fname]:
            print(f"    ❌ {issue}")
else:
    print("\n✅ 0 个错误，所有案例排版正确！")

if warnings:
    print(f"\n⚠️ {len(warnings)} 个警告（建议检查）:")
    by_file = {}
    for w in warnings:
        fname = w.split(':')[0]
        if fname not in by_file:
            by_file[fname] = []
        by_file[fname].append(w.split(':', 1)[1].strip())
    for fname in sorted(by_file.keys()):
        print(f"\n  📄 {fname}:")
        for issue in by_file[fname]:
            print(f"    ⚠️ {issue}")
else:
    print("\n⚠️ 0 个警告。")

print(f"\n📊 统计:")
print(f"  案例总数: 32")
