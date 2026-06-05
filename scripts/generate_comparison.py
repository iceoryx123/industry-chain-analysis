#!/usr/bin/env python3
"""generate_comparison.py
生成跨行业对比仪表盘 HTML（Bootstrap + Chart.js）
支持按类别筛选、排序
"""
import pandas as pd, yaml, datetime
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
IND_DIR = ROOT / "data" / "indicators"
META_DIR = ROOT / "data" / "meta"
OUT_DIR = ROOT / "cases" / "comparison"
OUT_DIR.mkdir(parents=True, exist_ok=True)

METRIC_COLS = [
    "market_size_cny_bn", "cr4", "hhi", "gross_margin",
    "roe", "rd_intensity", "network_intensity",
    "platform_users_million", "average_transaction_value_cny",
]

METRIC_LABELS = {
    "market_size_cny_bn": "市场规模(亿元)",
    "cr4": "CR4",
    "hhi": "HHI",
    "gross_margin": "毛利率",
    "roe": "ROE",
    "rd_intensity": "研发强度",
    "network_intensity": "网络强度",
    "platform_users_million": "平台用户(百万)",
    "average_transaction_value_cny": "平均交易额(元)",
}

CAT_LABELS = {
    "01-Traditional": "🏭 传统产业",
    "02-Platform": "🌐 平台型",
    "03-Regulated": "🏛️ 受监管",
    "04-Emerging": "🚀 新兴/跨界",
}

def load_all():
    rows = []
    min_period = ""
    max_period = ""
    for csv_path in sorted(IND_DIR.glob("*.csv")):
        code = csv_path.stem
        meta_file = META_DIR / f"{code}.yaml"
        if not meta_file.exists():
            continue
        meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
        df = pd.read_csv(csv_path)
        if df.empty:
            continue
        latest = df.iloc[-1].to_dict()
        row = {
            "code": code,
            "name": meta.get("name", code),
            "category": meta.get("category", ""),
            "subsector": meta.get("subsector", ""),
            "has_network": meta.get("has_network_effect", False),
        }
        for col in METRIC_COLS:
            row[col] = latest.get(col, 0)
        # 采集报告期
        rp = str(latest.get("report_period", ""))[:10] if latest.get("report_period") else ""
        row["report_period"] = rp
        if rp and (not min_period or rp < min_period):
            min_period = rp
        if rp and (not max_period or rp > max_period):
            max_period = rp
        rows.append(row)
    return pd.DataFrame(rows), min_period, max_period

def fmt(v, col):
    if v is None or v == 0:
        return "-"
    if col in ("cr4", "gross_margin", "roe", "rd_intensity", "network_intensity"):
        return f"{float(v):.2%}"
    if col in ("market_size_cny_bn",):
        return f"{float(v):.0f}"
    if col in ("hhi",):
        return f"{float(v):.0f}"
    if col in ("platform_users_million",):
        return f"{float(v):.1f}"
    return str(v)

def build_html(df: pd.DataFrame, min_period: str = "", max_period: str = "") -> str:
    today = datetime.date.today().isoformat()

    # 构建表格行
    rows_html = ""
    for _, r in df.iterrows():
        cat_label = CAT_LABELS.get(r["category"], r["category"])
        net_badge = "🌐" if r["has_network"] else ""
        cells = "".join(f'<td class="text-end">{fmt(r.get(c, 0), c)}</td>' for c in METRIC_COLS)
        rows_html += f"""<tr data-category="{r['category']}">
            <td><span class="badge bg-secondary">{cat_label}</span></td>
            <td><strong>{r['name']}</strong>{net_badge}</td>
            <td><small class="text-muted">{r['code']}</small></td>
            <td><small>{r['subsector']}</small></td>
            {cells}
        </tr>\n"""

    # 图表数据
    chart_data = df[["name", "gross_margin", "roe", "network_intensity", "rd_intensity"]].to_json(orient="records")

    metric_headers = "".join(f'<th class="text-end">{METRIC_LABELS.get(c, c)}</th>' for c in METRIC_COLS)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>产业链指标对比仪表盘 - 申万一级行业 - 数据至{max_period or today}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
    body {{ padding: 20px; background: #f8f9fa; }}
    .table {{ font-size: 13px; white-space: nowrap; }}
    .sticky-col {{ position: sticky; left: 0; background: white; z-index: 1; }}
    .chart-container {{ margin: 20px 0; }}
    .filter-btn {{ margin: 2px; }}
</style>
</head>
<body>
<div class="container-fluid">
<div class="alert alert-info py-2 mb-3 small">
    ⏱️ <strong>数据时效</strong>：
    财务报告期 <strong>{max_period or "未知"}</strong>（{min_period or ""} 至 {max_period or "未知"}）｜
    生成日期 {today} ｜
    来源 <strong>akshare</strong>（东方财富/同花顺）｜
    ⚠️ 数据过期后以下图表和结论可能失效
</div>
<h1 class="mb-3">📊 产业链指标对比仪表盘</h1>
<p class="text-muted">基于申万一级行业分类 | 报告期：{max_period or today} | 生成：{today} | 来源：akshare</p>

<!-- 类别筛选 -->
<div class="mb-3">
    <button class="btn btn-sm btn-outline-primary filter-btn active" onclick="filterCat('all')">全部</button>
    <button class="btn btn-sm btn-outline-secondary filter-btn" onclick="filterCat('01-Traditional')">🏭 传统</button>
    <button class="btn btn-sm btn-outline-success filter-btn" onclick="filterCat('02-Platform')">🌐 平台</button>
    <button class="btn btn-sm btn-outline-warning filter-btn" onclick="filterCat('03-Regulated')">🏛️ 受监管</button>
    <button class="btn btn-sm btn-outline-danger filter-btn" onclick="filterCat('04-Emerging')">🚀 新兴</button>
</div>

<!-- 对比表格 -->
<div class="table-responsive mb-4">
<table class="table table-striped table-hover table-sm" id="compTable">
<thead class="table-dark sticky-top">
<tr>
    <th>类别</th>
    <th>行业</th>
    <th>代码</th>
    <th>细分</th>
    {metric_headers}
</tr>
</thead>
<tbody>{rows_html}</tbody>
</table>
</div>

<!-- 图表：毛利率 & ROE 对比 -->
<div class="row">
    <div class="col-md-6 chart-container">
        <canvas id="chartProfit"></canvas>
    </div>
    <div class="col-md-6 chart-container">
        <canvas id="chartNetwork"></canvas>
    </div>
</div>

<!-- 图表：研发强度 & 网络强度 -->
<div class="row">
    <div class="col-md-6 chart-container">
        <canvas id="chartRD"></canvas>
    </div>
    <div class="col-md-6 chart-container">
        <canvas id="chartHHI"></canvas>
    </div>
</div>

<script>
const data = {chart_data};

function filterCat(cat) {{
    const rows = document.querySelectorAll('#compTable tbody tr');
    rows.forEach(r => {{
        if (cat === 'all' || r.dataset.category === cat) {{
            r.style.display = '';
        }} else {{
            r.style.display = 'none';
        }}
    }});
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
}}

// 利润率对比图
new Chart(document.getElementById('chartProfit'), {{
    type: 'bar',
    data: {{
        labels: data.map(d => d.name),
        datasets: [
            {{ label: '毛利率', data: data.map(d => (d.gross_margin||0)*100), backgroundColor: 'rgba(54,162,235,0.7)' }},
            {{ label: 'ROE', data: data.map(d => (d.roe||0)*100), backgroundColor: 'rgba(255,99,132,0.7)' }},
        ]
    }},
    options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '盈利能力对比 (%)' }} }} }} 
}});

// 网络强度图
new Chart(document.getElementById('chartNetwork'), {{
    type: 'bar',
    data: {{
        labels: data.map(d => d.name),
        datasets: [
            {{ label: '网络强度', data: data.map(d => (d.network_intensity||0)*100), backgroundColor: 'rgba(75,192,192,0.7)' }},
        ]
    }},
    options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '网络效应强度 (%)' }} }} }} 
}});

// 研发强度图
new Chart(document.getElementById('chartRD'), {{
    type: 'bar',
    data: {{
        labels: data.map(d => d.name),
        datasets: [
            {{ label: '研发强度', data: data.map(d => (d.rd_intensity||0)*100), backgroundColor: 'rgba(153,102,255,0.7)' }},
        ]
    }},
    options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '研发投入强度 (%)' }} }} }} 
}});

// HHI 散点图
new Chart(document.getElementById('chartHHI'), {{
    type: 'scatter',
    data: {{
        datasets: [{{
            label: 'HHI vs 毛利率',
            data: data.map(d => ({{ x: d.hhi||0, y: (d.gross_margin||0)*100 }})),
            backgroundColor: 'rgba(255,159,64,0.7)'
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ title: {{ display: true, text: '市场集中度 vs 毛利率' }} }},
        scales: {{
            x: {{ title: {{ display: true, text: 'HHI' }} }},
            y: {{ title: {{ display: true, text: '毛利率 (%)' }} }}
        }}
    }}
}});
</script>
</div>
</body>
</html>"""
    return html

def main():
    print("=" * 60)
    print("📊 生成跨行业对比仪表盘")
    print("=" * 60)

    df, min_period, max_period = load_all()
    if df.empty:
        print("⚠️ 无数据，请先生成指标 CSV")
        return

    html = build_html(df, min_period, max_period)
    out_path = OUT_DIR / "overview.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"  ✅ 仪表盘已生成: {out_path}")
    print(f"  📊 包含 {len(df)} 个行业 × {len(METRIC_COLS)} 个指标")
    print(f"  📁 文件大小: {out_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
