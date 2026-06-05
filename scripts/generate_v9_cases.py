#!/usr/bin/env python3
"""generate_v9_cases.py
自动为 category 为 "01-Traditional" 的行业生成案例文件（case.md + indicators.yaml）。
使用 Jinja2 完整渲染模板（支持条件语句、变量插值），保留 {{ indicator.xxx }} 供后续处理。
"""

import os, re, sys, shutil, datetime
from pathlib import Path
import yaml

# 确保 scripts/ 在 Python 路径中（支持从 repo 根目录直接调用）
_SCRIPT_DIR = Path(__file__).parent.resolve()
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from template_utils import render_template, get_meta_by_code

ROOT = Path(os.getenv("WORKSPACE", str(_SCRIPT_DIR.parent)))
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry" / "01-Traditional"
TEMPLATE_CASE = ROOT / "templates" / "case_template_v9.md"
TEMPLATE_IND = ROOT / "templates" / "indicators_template.yaml"

def ensure_case(meta):
    code = meta["code"]
    name = meta["name"]
    subsector = meta["subsector"]
    today = datetime.date.today().isoformat()

    # 检查是否已有该行业的 case.md（可能在子目录中，如 {subsector}/{code}-{name}/）
    existing = list(CASE_ROOT.rglob(f"*/{code}-*/case.md")) + list(CASE_ROOT.rglob(f"{code}-*/case.md"))
    if existing:
        print(f"🔎 已存在 (跳过): {existing[0]}")
        return

    # 目录：{code}-{name}/
    case_dir = CASE_ROOT / f"{code}-{name}"
    case_dir.mkdir(parents=True, exist_ok=True)
    case_md = case_dir / "case.md"
    ind_yaml = case_dir / "indicators.yaml"

    if not case_md.exists():
        context = {
            "name": name,
            "code": code,
            "version": "v9.2",
            "subsector": subsector,
            "today": today,
        }
        content = render_template(TEMPLATE_CASE, context)
        case_md.write_text(content, encoding="utf-8")
        print(f"✅ 创建案例 (v9.2): {case_md}")
    else:
        print(f"🔎 已存在: {case_md}")

    if not ind_yaml.exists():
        shutil.copy(TEMPLATE_IND, ind_yaml)
        print(f"✅ 创建指标模板: {ind_yaml}")

if __name__ == "__main__":
    metas = get_meta_by_code(META_DIR)
    for code, meta in metas.items():
        if meta.get("category") == "01-Traditional":
            ensure_case(meta)
