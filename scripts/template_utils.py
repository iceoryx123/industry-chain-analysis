#!/usr/bin/env python3
"""template_utils.py — Jinja2 渲染工具，正确处理 indicator 占位符的转义"""

import re
from pathlib import Path
from jinja2 import Environment

def render_template(template_path: Path, context: dict) -> str:
    """
    用 Jinja2 渲染模板，并保留 {{ indicator.xxx }} 占位符供 render_cases.py 后续处理。

    原理：
      1. 将 {{ indicator.xxx }} 临时转义为 {% raw %}{{ indicator.xxx }}{% endraw %}
      2. Jinja2 渲染所有其他模板变量（{{ name }}、条件语句等）
      3. 恢复转义后的 indicator 占位符
    """
    template_text = template_path.read_text(encoding="utf-8")

    # 1. 提取并保护 indicator 占位符
    indicator_placeholders = {}
    def protect_indicator(m):
        key = f"__INDICATOR_{len(indicator_placeholders)}__"
        indicator_placeholders[key] = m.group(0)
        return key

    # 保护 {{ indicator.xxx }} 形式的占位符
    protected = re.sub(r'\{\{\s*indicator\.(\w+)\s*\}\}', protect_indicator, template_text)

    # 2. 用 Jinja2 渲染
    env = Environment()
    jinja_template = env.from_string(protected)
    rendered = jinja_template.render(**context)

    # 3. 恢复 indicator 占位符
    for key, original in indicator_placeholders.items():
        rendered = rendered.replace(key, original)

    return rendered


def get_meta_by_code(meta_dir: Path) -> dict:
    """加载 data/meta/*.yaml，返回 {code: meta} 字典"""
    import yaml
    result = {}
    for f in sorted(meta_dir.glob("*.yaml")):
        m = yaml.safe_load(f.read_text())
        if m and "code" in m:
            result[m["code"]] = m
    return result
