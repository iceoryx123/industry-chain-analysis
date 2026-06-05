#!/usr/bin/env python3
"""generate_comparison.py
生成跨行业对比仪表盘 HTML（Bootstrap + Chart.js）
支持按类别筛选、排序
v2.0 — 新增相对吸引力矩阵（补充模块J）
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

# ── 周期分类（与洞察引擎一致） ──
CYCLE_MAP = {
    "801010": "强周期", "801020": "强周期", "801030": "强周期",
    "801040": "强周期", "801050": "成长周期", "801060": "成长周期",
    "801070": "强周期", "801080": "弱周期", "801090": "弱周期",
    "801100": "强周期", "801110": "弱周期", "801120": "成长周期",
    "801130": "弱防御", "801140": "强防御", "801150": "弱防御",
    "801160": "弱周期", "801170": "强防御", "801180": "强周期",
    "801190": "强防御", "801200": "弱周期", "801210": "弱周期",
    "801220": "弱周期", "801230": "强周期", "801710": "弱防御",
    "801720": "弱防御", "801730": "弱周期", "801740": "弱周期",
    "801750": "弱防御", "801780": "强周期", "801790": "强周期",
    "801880": "成长周期", "801890": "弱周期",
}
CYCLE_ORDER = {"强周期": 0, "弱周期": 1, "成长周期": 2, "弱防御": 3, "强防御": 4}

# ── 颠覆风险分（1-4，用于数值化） ──
DISRUPT_SCORE = {
    "801010": 1, "801020": 2, "801030": 2, "801040": 1,
    "801050": 2, "801060": 3, "801070": 3, "801080": 1,
    "801090": 3, "801100": 1, "801110": 2, "801120": 2,
    "801130": 1, "801140": 2, "801150": 1, "801160": 2,
    "801170": 2, "801180": 1, "801190": 1, "801200": 2,
    "801210": 2, "801220": 1, "801230": 2, "801710": 1,
    "801720": 1, "801730": 2, "801740": 3, "801750": 1,
    "801780": 2, "801790": 2, "801880": 2, "801890": 1,
}

# ── 标准化分（0-100），用于相对吸引力矩阵 ──
def norm_score(val, higher_is_better=True):
    """将单个指标映射到 0-100，用于综合评分"""
    if val is None or val == 0:
        return 0
    v = float(val)
    # 中值转换：毛利率、ROE等 0-1 到 0-100
    if higher_is_better:
        return min(100, max(0, v * 100))
    else:
        return min(100, max(0, (1 - v) * 100))

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

        # ── 动态周期数据 ──
        row["cycle_position"] = str(latest.get("cycle_position", "中位"))
        row["cycle_score"] = float(latest.get("cycle_score", 50) or 50)

        # ── 模块F-J：计算相对吸引力评分 ──
        gm = float(latest.get("gross_margin", 0) or 0)
        roe = float(latest.get("roe", 0) or 0)
        rd = float(latest.get("rd_intensity", 0) or 0)
        net = float(latest.get("network_intensity", 0) or 0)
        cr4 = float(latest.get("cr4", 0) or 0)

        # 增长吸引力分（模块F）：ROE + 毛利率 + 研发强度 加权
        growth_score = (
            norm_score(roe) * 0.35 +
            norm_score(gm) * 0.35 +
            norm_score(rd) * 0.15 +
            norm_score(net) * 0.15
        )
        row["growth_score"] = round(growth_score, 1)

        # 质量吸引力分（模块B体系）：毛利率 + ROE + CR4
        quality_score = (
            norm_score(gm) * 0.4 +
            norm_score(roe) * 0.4 +
            norm_score(cr4) * 0.2
        )
        row["quality_score"] = round(quality_score, 1)

        # 周期定位
        row["cycle_type"] = CYCLE_MAP.get(code, "弱周期")
        row["cycle_order"] = CYCLE_ORDER.get(row["cycle_type"], 5)

        # 颠覆风险（逆向：低风险=高分）
        risk_score = DISRUPT_SCORE.get(code, 2)
        row["disrupt_score"] = max(0, 5 - risk_score)  # 5-1=4, 5-2=3, 5-3=2, 5-4=1

        # 综合相对吸引力
        row["attractiveness"] = round(
            row["growth_score"] * 0.3 +
            row["quality_score"] * 0.4 +
            row["disrupt_score"] * 0.15 +
            (100 - row["cycle_order"] * 15) * 0.15,  # 强周期低分（波动大）
            1
        )

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
    if col in ("score",):
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

    # 图表数据（含周期分类和评分）
    chart_data = df[["name", "gross_margin", "roe", "network_intensity", "rd_intensity",
                     "growth_score", "quality_score", "attractiveness",
                     "cycle_type", "cycle_order", "disrupt_score"]].to_json(orient="records")

    # 相对吸引力表
    attract_rows = df.sort_values("attractiveness", ascending=False)
    attract_html = ""
    for _, r in attract_rows.iterrows():
        cat_label = CAT_LABELS.get(r["category"], r["category"])
        # 周期徽标
        cyc_badge = {"强周期": "danger", "弱周期": "warning", "成长周期": "success", "弱防御": "info", "强防御": "primary"}
        cyc_class = cyc_badge.get(r.get("cycle_type", "弱周期"), "secondary")
        # 颠覆风险颜色
        dis_score = float(r.get("disrupt_score", 2))
        dis_tag = "🟢低风险" if dis_score >= 3 else "🟡中风险" if dis_score >= 2 else "🟠高风险"
        attract_html += f"""<tr>
            <td>{cat_label}</td>
            <td><strong>{r['name']}</strong></td>
            <td class="text-end">{fmt(r.get('growth_score', 0), 'score')}</td>
            <td class="text-end">{fmt(r.get('quality_score', 0), 'score')}</td>
            <td><span class="badge bg-{cyc_class}">{r.get('cycle_type', '弱周期')}</span></td>
            <td>{dis_tag}</td>
            <td class="text-end"><strong>{fmt(r.get('attractiveness', 0), 'score')}</strong></td>
        </tr>\n"""

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

<!-- 相对吸引力矩阵（补充模块J） -->
<div class="card mb-4">
    <div class="card-header bg-dark text-white">
        <h5 class="mb-0">📊 相对吸引力矩阵（模块J）— 跨行业比较排序</h5>
    </div>
    <div class="card-body">
        <p class="text-muted small">
            综合评分 = 增长吸引力(30%) + 质量吸引力(40%) + 颠覆防御力(15%) + 周期稳定性(15%)。<br>
            <strong>🔥 高分</strong> = 高增长+高质量+低颠覆风险+稳定周期 | 
            <strong>⚠️ 低分</strong> = 低增长+低质量+高颠覆风险+强周期波动
        </p>
        <div class="table-responsive">
            <table class="table table-sm table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>类别</th>
                        <th>行业</th>
                        <th class="text-end">📈 增长吸引力</th>
                        <th class="text-end">🛡️ 质量吸引力</th>
                        <th>🔄 周期类型</th>
                        <th>💥 颠覆风险</th>
                        <th class="text-end"><strong>★ 综合</strong></th>
                    </tr>
                </thead>
                <tbody>{attract_html}</tbody>
            </table>
        </div>
    </div>
</div>

<!-- 散点图：增长 vs 质量 -->
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body chart-container">
                <canvas id="chartAttractMatrix" height="400"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-body chart-container">
                <canvas id="chartCycleDistribution" height="400"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- 原有图表 -->
<div class="row">
    <div class="col-md-6 chart-container">
        <canvas id="chartProfit"></canvas>
    </div>
    <div class="col-md-6 chart-container">
        <canvas id="chartNetwork"></canvas>
    </div>
</div>

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

// 相对吸引力散点图（补充模块J）
new Chart(document.getElementById('chartAttractMatrix'), {{
    type: 'scatter',
    data: {{
        datasets: [{{
            label: '行业定位',
            data: data.map(d => ({{ x: d.quality_score||0, y: d.growth_score||0 }})),
            backgroundColor: data.map(d => {{
                if (d.attractiveness >= 50) return 'rgba(40,167,69,0.7)';   // 绿：高吸引力
                if (d.attractiveness >= 40) return 'rgba(255,193,7,0.7)';   // 黄：中吸引力
                return 'rgba(220,53,69,0.7)';                                 // 红：低吸引力
            }}),
            pointRadius: 8,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{
            title: {{ display: true, text: '行业相对吸引力矩阵 🔥增长 vs 🛡️质量' }},
            tooltip: {{
                callbacks: {{
                    label: function(ctx) {{
                        const idx = ctx.dataIndex;
                        const d = data[idx];
                        return d.name + ' | 增长:' + d.growth_score + ' 质量:' + d.quality_score + ' 综合:' + d.attractiveness;
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{ title: {{ display: true, text: '质量吸引力 (0-100)' }}, min: 0, max: 100 }},
            y: {{ title: {{ display: true, text: '增长吸引力 (0-100)' }}, min: 0, max: 100 }}
        }}
    }}
}});

// 周期分布图
new Chart(document.getElementById('chartCycleDistribution'), {{
    type: 'doughnut',
    data: {{
        labels: ['强周期', '弱周期', '成长周期', '弱防御', '强防御'],
        datasets: [{{
            data: [
                data.filter(d => d.cycle_type === '强周期').length,
                data.filter(d => d.cycle_type === '弱周期').length,
                data.filter(d => d.cycle_type === '成长周期').length,
                data.filter(d => d.cycle_type === '弱防御').length,
                data.filter(d => d.cycle_type === '强防御').length,
            ],
            backgroundColor: ['#dc3545', '#ffc107', '#28a745', '#17a2b8', '#007bff'],
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ title: {{ display: true, text: '行业周期类型分布' }} }}
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
