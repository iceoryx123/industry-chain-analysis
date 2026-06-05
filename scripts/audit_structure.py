#!/usr/bin/env python3
"""章节结构总览"""
import os, re

base = 'cases/by-industry'
sections_report = {}

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        with open(path) as fh:
            content = fh.read()
        
        h2s = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        sections = [h for h in h2s if '📑' not in h and '📋' not in h and '自动洞见' not in h]
        
        dirname = os.path.basename(os.path.dirname(path))
        parts = dirname.split('-', 1)
        code = parts[0]
        name = parts[1] if len(parts) > 1 else dirname
        sections_report[name] = (code, sections)

print("📋 32个行业章节结构总览")
print("=" * 70)
for name in sorted(sections_report.keys()):
    code, sections = sections_report[name]
    nums = []
    for s in sections:
        m = re.match(r'^([0-9]️⃣|1️⃣[0-9]️⃣)\s+', s)
        if m:
            nums.append(m.group(1))
    print("  {} {:<8s} | {}节 | {}".format(code, name, len(sections), ' '.join(nums)))

# Check for inconsistencies
print("\n⚠️ 异常检查:")
for name in sorted(sections_report.keys()):
    code, sections = sections_report[name]
    for s in sections:
        if s.startswith('1️⃣ '):
            print("  ❌ {} {}: H2 不应有 1️⃣ (找到: {})".format(code, name, s[:30]))
    
    if not any('2️⃣' in s for s in sections):
        print("  ❌ {} {}: 缺少 2️⃣ 产业全景".format(code, name))
    
    has_11 = any('1️⃣1️⃣' in s for s in sections)
    has_15 = any('1️⃣5️⃣' in s for s in sections)
    if has_11 and not has_15:
        print("  ⚠️ {} {}: 有 1️⃣1️⃣ 但无 1️⃣5️⃣ 结论".format(code, name))

print("\n✅ 检查完成")
