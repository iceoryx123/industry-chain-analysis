#!/usr/bin/env python3
"""generate_comparison.py 生成跨行业对比仪表盘 HTML"""
import pandas as pd, yaml, datetime
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
IND_DIR = ROOT / "data" / "indicators"
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "cases" / "comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIELDS = [
    "date", "market_size_cny_bn", "cr4", "hhi", "gross_margin",
    "roe", "rd_intensity", "network_intensity",
    "platform_users_million", "average_transaction_value_cny",
]

def build_table():
    rows = []
    for csv_path in sorted(IND_DIR.glob("*.csv")):
        code = csv_path.stem
        meta_file = META_DIR / f"{code}.yaml"
        if not meta_file.exists():
            continue
        meta = yaml.safe_load(meta_file.read_text())
        df = pd.read_csv(csv_path)
        if df.empty:
            continue
        latest = df.iloc[-1].to_dict()
        row = {
            "code": code,
            "name": meta.get("name", code),
            "category": meta.get("category", ""),
            "subsector": meta.get("subsector", ""),
        }
        for f in FIELDS:
            row[f] = latest.get(f, 0)
        rows.append(row)
    return pd.DataFrame(rows)

def fmt_val(v):
    if isinstance(v, float):
        if abs(v) >= 1e8:
            return f"{v:.0f}"
        elif abs(v) >= 1:
            return f"{v:.2f}"
        else:
            return f"{v:.4f}"
    return str(v)

def main():
    df = build_table()
    if df.empty:
        print("⚠️ 无数据，跳过对比仪表盘")
        return

    rows_html = ""
    for _, r in df.iterrows():
        vals = "".join(f"<td>{fmt_val(r.get(f, ''))}</td>" for f in FIELDS)
        rows_html += f"<tr><td>{r['code']}</td><td>{r['name']}</td><td>{r['category']}</td>{vals}</tr>\n"

    today = datetime.date.today().isoformat()
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>产业链指标对比仪表盘</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>body{{margin:20px}}.table{{font-size:14px}}</style>
</head>
<body>
<div class="container">
<h1>📊 产业链指标对比仪表盘</h1>
<p>更新日期：{today} | 数据来源：akshare / yfinance / pytrends / 公开网页</p>
<hr>
<div class="table-responsive">
<table class="table table-striped table-bordered" id="compTable">
<thead class="table-dark">
<tr><th>代码</th><th>行业</th><th>类别</th>
{"".join(f'<th>{f}</th>' for f in FIELDS)}
</tr></thead>
<tbody>{rows_html}</tbody>
</table>
</div>
<hr>
<h2>📈 行业对比趋势</h2>
<canvas id="chart" width="800" height="400"></canvas>
<script>
const ctx = document.getElementById('chart').getContext('2d');
const data = {df.to_json(orient='records')};
const labels = data.map(d => d.name);
const datasets = ['gross_margin','network_intensity','roe'].map(key => ({{
    label: key,
    data: data.map(d => d[key] || 0),
    borderWidth: 1
}}));
new Chart(ctx, {{
    type: 'bar',
    data: {{ labels, datasets }},
    options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
}});
</script>
</div>
</body>
</html>"""
    out_path = OUT_DIR / "overview.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"✅ 仪表盘已生成: {out_path}")

if __name__ == "__main__":
    main()
