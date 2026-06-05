#!/usr/bin/env python3
"""查看混合编号案例的结构"""
import os

cases = ['801060-计算机', '801220-环保', '801880-机器人']
base = 'cases/by-industry'

for d in cases:
    for root, dirs, files in os.walk(base):
        for f in files:
            if f == 'case.md' and d in root:
                path = os.path.join(root, f)
                print(f"=== {d} ===")
                with open(path) as fh:
                    for l in fh:
                        if l.startswith('## '):
                            print(l.rstrip())
                print()
