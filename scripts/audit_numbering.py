#!/usr/bin/env python3
"""精确检查哪些 case 用了旧编号（3️⃣~6️⃣ 而非 1️⃣1️⃣~1️⃣5️⃣）"""
import os, re

base = 'cases/by-industry'

# 新编号预期映射
NEW_NUM = {
    '价值枢纽识别': '1️⃣1️⃣',
    '枢纽质量评估': '1️⃣2️⃣',
    '拐点判断': '1️⃣3️⃣',
    '结论与投资启示': '1️⃣5️⃣',
}
OLD_NUM = {
    '价值枢纽识别': '3️⃣',
    '枢纽质量评估': '4️⃣',
    '拐点判断': '5️⃣',
    '结论与投资启示': '6️⃣',
}

old_style = []
new_style = []
mixed = []

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        dirname = os.path.basename(os.path.dirname(path))
        with open(path) as fh:
            content = fh.read()
        
        # Check each section
        uses_old = False
        uses_new = False
        for section_name, new_emoji in NEW_NUM.items():
            old_emoji = OLD_NUM[section_name]
            if '## ' + old_emoji + ' ' + section_name in content:
                uses_old = True
            if '## ' + new_emoji + ' ' + section_name in content:
                uses_new = True
        
        if uses_old and not uses_new:
            old_style.append(dirname)
        elif uses_new and not uses_old:
            new_style.append(dirname)
        else:
            mixed.append(dirname)

print("📋 编号方案检查")
print("=" * 60)
print(f"\n✅ 新编号 (1️⃣1️⃣~1️⃣5️⃣): {len(new_style)} 个行业")
for n in sorted(new_style):
    print(f"   {n}")

print(f"\n❌ 旧编号 (3️⃣~6️⃣): {len(old_style)} 个行业（需要修复）")
for n in sorted(old_style):
    print(f"   {n}")

if mixed:
    print(f"\n⚠️ 混合：{len(mixed)} 个行业")
    for n in sorted(mixed):
        print(f"   {n}")

print(f"\n⚠️ 其他异常:")
for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        dirname = os.path.basename(os.path.dirname(path))
        with open(path) as fh:
            content = fh.read()
        
        # Check for 1️⃣4️⃣ (补充模块J)
        if '## 1️⃣4️⃣' in content:
            print(f"   {dirname}: 有 1️⃣4️⃣ 章节")

        # Check 计算机 (只有1节)
        h2s = re.findall(r'^##\s+\d+️⃣\s+', content, re.MULTILINE)
        if len(h2s) <= 2:
            print(f"   {dirname}: 仅 {len(h2s)} 节 (异常偏少)")
