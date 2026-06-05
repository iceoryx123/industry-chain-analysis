#!/usr/bin/env python3
"""验证编号修复 + 检查混合案例细节"""
import os, re

base = 'cases/by-industry'

# 验证新编号
still_old = []
all_new = []
mixed = []

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        dirname = os.path.basename(os.path.dirname(path))
        with open(path) as fh:
            content = fh.read()
        
        uses_old_3 = '## 3️⃣ 价值枢纽识别' in content
        uses_old_4 = '## 4️⃣ 枢纽质量评估' in content
        uses_old_5 = '## 5️⃣ 拐点判断' in content
        uses_old_6 = '## 6️⃣ 结论与投资启示' in content
        
        uses_new_11 = '## 1️⃣1️⃣ 价值枢纽识别' in content
        uses_new_12 = '## 1️⃣2️⃣ 枢纽质量评估' in content
        uses_new_13 = '## 1️⃣3️⃣ 拐点判断' in content
        uses_new_15 = '## 1️⃣5️⃣ 结论与投资启示' in content
        
        # TOC consistency
        toc_old_3 = '- 3️⃣ 价值枢纽识别' in content
        toc_new_11 = '- 1️⃣1️⃣ 价值枢纽识别' in content
        
        has_old = uses_old_3 or uses_old_4 or uses_old_5 or uses_old_6
        has_new = uses_new_11 or uses_new_12 or uses_new_13 or uses_new_15
        
        if has_old and has_new:
            mixed.append(dirname)
            print(f"⚠️ 混合 {dirname}: 旧和新编号并存")
        elif has_old:
            still_old.append(dirname)
            print(f"❌ 仍旧 {dirname}")
        elif has_new:
            all_new.append(dirname)
        else:
            print(f"⚠️ 无匹配 {dirname}")

print(f"\n📊 统计:")
print(f"   新编号: {len(all_new)} 个")
print(f"   仍旧编号: {len(still_old)} 个")
print(f"   混合: {len(mixed)} 个")

# 检查 TOC 和标题一致性
print(f"\n🔍 TOC-H2 一致性检查:")
for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        dirname = os.path.basename(os.path.dirname(path))
        with open(path) as fh:
            content = fh.read()
        
        # 检查 TOC 中的 1️⃣1️⃣ 是否对应 H2 中的 1️⃣1️⃣
        if '- 1️⃣1️⃣ 价值枢纽识别' in content and '## 1️⃣1️⃣ 价值枢纽识别' not in content:
            print(f"   ❌ {dirname}: TOC 有 1️⃣1️⃣ 但 H2 没有")
        if '- 1️⃣2️⃣ 枢纽质量评估' in content and '## 1️⃣2️⃣ 枢纽质量评估' not in content:
            print(f"   ❌ {dirname}: TOC 有 1️⃣2️⃣ 但 H2 没有")
        if '- 1️⃣3️⃣ 拐点判断' in content and '## 1️⃣3️⃣ 拐点判断' not in content:
            print(f"   ❌ {dirname}: TOC 有 1️⃣3️⃣ 但 H2 没有")
        if '- 1️⃣5️⃣ 结论与投资启示' in content and '## 1️⃣5️⃣ 结论与投资启示' not in content:
            print(f"   ❌ {dirname}: TOC 有 1️⃣5️⃣ 但 H2 没有")

print("\n✅ 检查完成")
