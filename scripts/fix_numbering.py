#!/usr/bin/env python3
"""修复 13 个旧编号案例为新编号 (3️⃣→1️⃣1️⃣, 4️⃣→1️⃣2️⃣, 5️⃣→1️⃣3️⃣, 6️⃣→1️⃣5️⃣)"""
import os, re

base = 'cases/by-industry'

# 旧→新编号映射
REPLACEMENTS = [
    ('## 3️⃣ 价值枢纽识别', '## 1️⃣1️⃣ 价值枢纽识别'),
    ('## 4️⃣ 枢纽质量评估',   '## 1️⃣2️⃣ 枢纽质量评估'),
    ('## 5️⃣ 拐点判断',       '## 1️⃣3️⃣ 拐点判断'),
    ('## 6️⃣ 结论与投资启示',  '## 1️⃣5️⃣ 结论与投资启示'),
]

# 同时修复 TOC 和正文中的引用
TOC_REPLACEMENTS = [
    ('- 3️⃣ 价值枢纽识别', '- 1️⃣1️⃣ 价值枢纽识别'),
    ('- 4️⃣ 枢纽质量评估',   '- 1️⃣2️⃣ 枢纽质量评估'),
    ('- 5️⃣ 拐点判断',       '- 1️⃣3️⃣ 拐点判断'),
    ('- 6️⃣ 结论与投资启示',  '- 1️⃣5️⃣ 结论与投资启示'),
]

fixed_count = 0
fixed_files = []

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        
        with open(path) as fh:
            content = fh.read()
        
        original = content
        has_old = any(old in content for old, _ in REPLACEMENTS)
        
        if not has_old:
            continue
        
        # Fix H2 titles
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        
        # Fix TOC references
        for old, new in TOC_REPLACEMENTS:
            content = content.replace(old, new)
        
        if content != original:
            with open(path, 'w') as fh:
                fh.write(content)
            fixed_count += 1
            dirname = os.path.basename(os.path.dirname(path))
            fixed_files.append(dirname)
            print(f"  ✅ {rel}")

print(f"\n📊 共修复 {fixed_count} 个案例:")
for f in sorted(fixed_files):
    print(f"   {f}")
