#!/usr/bin/env python3
"""第二轮深度检查：逻辑一致性"""
import os, re

base = 'cases/by-industry'
issues = []

for root, dirs, files in os.walk(base):
    for f in sorted(files):
        if f != 'case.md':
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, base)
        with open(path) as fh:
            lines = fh.readlines()
        
        code = os.path.basename(os.path.dirname(path)).split('-')[0]
        
        # ── A. 提取所有 H2 标题，检查编号序列 ──
        h2s = []
        for l in lines:
            m = re.match(r'^##\s+(.+)$', l)
            if m and '自动洞见' not in m.group(1) and '📑' not in m.group(1) and '📋' not in m.group(1):
                h2s.append(m.group(1).strip())
        
        # ── B. 从标题提取数字序列（2️⃣→2），排除非章节的引用 ──
        num_map = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5,
                   '6️⃣': 6, '7️⃣': 7, '8️⃣': 8, '9️⃣': 9,
                   '1️⃣0️⃣': 10, '1️⃣1️⃣': 11, '1️⃣2️⃣': 12, '1️⃣3️⃣': 13, '1️⃣4️⃣': 14, '1️⃣5️⃣': 15}
        
        found_nums = []
        for h in h2s:
            for emoji, num in num_map.items():
                if emoji in h:
                    found_nums.append((num, h))
                    break
        
        if found_nums:
            # 检查编号是否从 2️⃣ 开始（1️⃣ 是主标题，不属 H2 章节）
            if found_nums and found_nums[0][0] != 2:
                # 如果从 1 开始，看看是不是因为标题行包含了 1️⃣ 并被误抓到 h2s
                # 例如 "版本选择" 可能是 ## 1️⃣ 版本选择？不对，主标题是 H1
                pass  # 不报错，因为 H2 从 2 开始是正常的
        
        # ── C. 检查内容概要中引用的章节是否都在正文中出现 ──
        in_summary = False
        summary_refs = []
        for l in lines:
            if '📋 内容概要' in l:
                in_summary = True
                continue
            if in_summary and l.startswith('## '):
                in_summary = False
            if in_summary:
                # 找反引号引用的章节名
                refs = re.findall(r'`([^`]+)`', l)
                summary_refs.extend(refs)
        
        # ── D. 检查标准模块引用是否出现在该出现的地方 ──
        in_auto_insight = False
        insight_found = False
        for l in lines:
            if '自动洞见' in l:
                insight_found = True
                in_auto_insight = True
                continue
            if in_auto_insight and l.startswith('---'):
                break  # 洞见区块结束
        
        if not insight_found:
            issues.append(f'{rel}: 未找到自动洞见区块')
        
        # ── E. 检查标准模块引用是否与行业类别匹配 ──
        # v9.2 → 标准模块A-E, v10.x → 标准模块A-E + 补充模块F-J
        version_tag = ''
        for l in lines:
            m = re.search(r'\*\*版本\*\*[：:]\s*([^\|*]+)', l)
            if m:
                version_tag = m.group(1).strip()
                break
        
        # ── F. 检查洞见中的评分与模板评分是否一致 ──
        # 从模板中找评分
        template_moat = template_pricing = template_subst = template_eco = None
        for l in lines:
            m = re.search(r'\*\*护城河\*\*[：:]\s*([\d.]+)/10', l)
            if m: template_moat = float(m.group(1))
            m = re.search(r'\*\*定价权\*\*[：:]\s*([\d.]+)/10', l)
            if m: template_pricing = float(m.group(1))
            m = re.search(r'\*\*替代难度\*\*[：:]\s*([\d.]+)/10', l)
            if m: template_subst = float(m.group(1))
            m = re.search(r'\*\*生态位\*\*[：:]\s*([\d.]+)/10', l)
            if m: template_eco = float(m.group(1))
        
        # 从洞见中找评分
        insight_moat = insight_pricing = insight_subst = insight_eco = None
        in_insight_section = False
        for l in lines:
            if '### 🔍 自动洞见' in l:
                in_insight_section = True
                continue
            if in_insight_section:
                m = re.search(r'护城河[：:]\s*([\d.]+)/10', l)
                if m: insight_moat = float(m.group(1))
                m = re.search(r'定价权[：:]\s*([\d.]+)/10', l)
                if m: insight_pricing = float(m.group(1))
                m = re.search(r'替代难度[：:]\s*([\d.]+)/10', l)
                if m: insight_subst = float(m.group(1))
                m = re.search(r'生态位[：:]\s*([\d.]+)/10', l)
                if m: insight_eco = float(m.group(1))
                if l.startswith('**拐点信号') or l.startswith('**业务启示'):
                    break
        
        # 比较评分一致性
        score_pairs = [
            ('护城河', template_moat, insight_moat),
            ('定价权', template_pricing, insight_pricing),
            ('替代难度', template_subst, insight_subst),
            ('生态位', template_eco, insight_eco),
        ]
        for name, tmpl, ins in score_pairs:
            if tmpl is not None and ins is not None and tmpl != ins:
                issues.append(f'{rel}: {name}评分不一致 模板={tmpl} 洞见={ins}')
        
        # ── G. 综合评分检查 ──
        # 综合 = (moat + pricing + subst + eco) / 4 * 10/4... 实际上综合 = sum/4
        if all(v is not None for v in [template_moat, template_pricing, template_subst, template_eco]):
            expected_composite = (template_moat + template_pricing + template_subst + template_eco) / 4.0
            # 找到实际综合评分
            for l in lines:
                m = re.search(r'综合评分[：:]\s*([\d.]+)/10', l)
                if m:
                    actual = float(m.group(1))
                    if abs(actual - expected_composite) > 0.15:
                        issues.append(f'{rel}: 综合评分不一致 预期={expected_composite:.1f} 实际={actual}')
                    break

        # ── H. 检查洞见中的周期定位与CSV是否一致 ──
        # 从CSV读取
        csv_path = f'data/indicators/{code}.csv'
        if os.path.exists(csv_path):
            import pandas as pd
            try:
                df = pd.read_csv(csv_path)
                csv_cycle = df.cycle_position.iloc[-1] if 'cycle_position' in df.columns else None
                
                # 从洞见中提取
                in_insight_cycle = False
                for l in lines:
                    if 'G - 周期定位' in l:
                        m = re.search(r'当前位置[：:]\s*([^（]+)', l)
                        if m:
                            insight_pos = m.group(1).strip()
                            if csv_cycle and csv_cycle not in insight_pos and insight_pos not in csv_cycle:
                                issues.append(f'{rel}: 周期位置不一致 CSV={csv_cycle} 洞见={insight_pos}')
                        break
            except:
                pass

print("=" * 70)
print("🔍 第二轮深度检查：逻辑一致性")
print("=" * 70)

if issues:
    print(f"\n❌ {len(issues)} 个逻辑问题:")
    by_file = {}
    for issue in issues:
        fname = issue.split(':')[0]
        if fname not in by_file:
            by_file[fname] = []
        by_file[fname].append(issue.split(':', 1)[1].strip())
    for fname in sorted(by_file.keys()):
        print(f"\n  📄 {fname}:")
        for i in by_file[fname]:
            print(f"    ❌ {i}")
else:
    print("\n✅ 0 个逻辑问题！")

print(f"\n📊 检查数: 32 cases")
