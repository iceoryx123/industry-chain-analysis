#!/usr/bin/env python3
"""修复环保(801220)严重编号错乱"""
import os

base = 'cases/by-industry'
target = None
for root, dirs, files in os.walk(base):
    for f in files:
        if f == 'case.md' and '801220' in root:
            target = os.path.join(root, f)
            break

if not target:
    print("❌ 未找到环保 case.md")
    exit(1)

print(f"📄 {target}")

with open(target) as fh:
    content = fh.read()

# 修复映射表：旧→新
fixes = {
    # 标题行修复
    '## 1️⃣1️⃣ 商业模式分析（标准模块A）': '## 3️⃣ 商业模式分析（标准模块A）',
    '## 1️⃣2️⃣ 护城河类型诊断（标准模块B）': '## 4️⃣ 护城河类型诊断（标准模块B）',
    '## 5️⃣ 话语权地图（标准模块C）':      '## 5️⃣ 话语权地图（标准模块C）',  # 正确
    '## 6️⃣ 现金流质量（标准模块D）':       '## 6️⃣ 现金流质量（标准模块D）',  # 正确
    '## 7️⃣ 增长引擎与天花板（补充模块F）':  '## 7️⃣ 增长引擎与天花板（补充模块F）',  # 正确
    '## 8️⃣ 周期定位（补充模块G）':         '## 8️⃣ 周期定位（补充模块G）',  # 正确
    '## 9️⃣ 技术颠覆敏感性（补充模块I）':   '## 9️⃣ 技术颠覆敏感性（补充模块I）',  # 正确
    '## 1️⃣0️⃣ 价值枢纽识别':               '## 1️⃣1️⃣ 价值枢纽识别',
    '## 1️⃣1️⃣ 枢纽质量评估':               '## 1️⃣2️⃣ 枢纽质量评估',
    '## 1️⃣2️⃣ 拐点判断':                  '## 1️⃣3️⃣ 拐点判断',
    '## 1️⃣4️⃣ 跨行业相对吸引力（补充模块J）': '## 1️⃣4️⃣ 跨行业相对吸引力（补充模块J）',  # 正确
    '## 1️⃣1️⃣2️⃣ 结论与投资启示':           '## 1️⃣5️⃣ 结论与投资启示',
    
    # TOC 行修复
    '- 1️⃣1️⃣ 商业模式分析（标准模块A）': '- 3️⃣ 商业模式分析（标准模块A）',
    '- 1️⃣2️⃣ 护城河类型诊断（标准模块B）': '- 4️⃣ 护城河类型诊断（标准模块B）',
    '- 1️⃣0️⃣ 价值枢纽识别': '- 1️⃣1️⃣ 价值枢纽识别',
    '- 1️⃣1️⃣ 枢纽质量评估': '- 1️⃣2️⃣ 枢纽质量评估',
    '- 1️⃣2️⃣ 拐点判断':    '- 1️⃣3️⃣ 拐点判断',
    '- 1️⃣1️⃣2️⃣ 结论与投资启示': '- 1️⃣5️⃣ 结论与投资启示',
}

applied = 0
for old, new in fixes.items():
    if old in content:
        content = content.replace(old, new)
        applied += 1
        print(f"  ✅ {old[:40]}... → {new[:40]}...")
    else:
        print(f"  ⚠️ 未找到: {old[:50]}...")

if applied > 0:
    with open(target, 'w') as fh:
        fh.write(content)
    print(f"\n📊 共修复 {applied} 处")
else:
    print("\n⚠️ 无需修复")
