"""
报告生成
========

对比仪表盘 HTML、Markdown 报告输出。
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from industry_chain.config import settings
from industry_chain.models import IndustryMeta, IndicatorRow


# =========================================
# 对比仪表盘 HTML
# =========================================
def generate_comparison_html() -> str:
    """生成跨行业对比仪表盘 HTML"""
    metas = IndustryMeta.list_all()
    rows = []
    for meta in metas:
        ind = IndicatorRow.load_latest(meta.code)
        rows.append({
            "code": meta.code,
            "name": meta.name,
            "industry": meta.shenwan_industry,
            "gross_margin": ind.gross_margin,
            "roe": ind.roe,
            "rd_intensity": ind.rd_intensity,
            "network_intensity": ind.network_intensity,
            "platform_users_million": ind.platform_users_million,
        })

    chart_data = json.dumps(rows, ensure_ascii=False, indent=2)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>产业链结构性分析 · 对比仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: -apple-system, 'Segoe UI', sans-serif; background: #f5f7fa; color: #333; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 24px; margin-bottom: 8px; }}
  .subtitle {{ color: #666; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
  .card {{ background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
  .card h2 {{ font-size: 16px; margin-bottom: 16px; color: #1a73e8; }}
  canvas {{ max-height: 280px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #eee; }}
  th {{ background: #f8f9fa; font-weight: 600; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 12px; background: #e8f0fe; color: #1a73e8; }}
  .dim-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }}
  .dim-item {{ text-align: center; padding: 8px; background: #f8f9fa; border-radius: 6px; font-size: 12px; }}
  .dim-value {{ font-size: 18px; font-weight: 700; color: #1a73e8; }}
  .footer {{ margin-top: 24px; color: #999; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <h1>🏭 产业链结构性分析 · 对比仪表盘</h1>
  <p class="subtitle">数据更新时间：{now} | 共 {len(rows)} 个行业案例</p>

  <div class="card">
    <h2>📊 核心指标对比</h2>
    <canvas id="mainChart"></canvas>
  </div>

  <div class="card">
    <h2>📋 全部行业数据</h2>
    <div style="overflow-x:auto;">
    <table>
      <thead><tr>
        <th>行业代码</th><th>行业名称</th><th>申万分类</th>
        <th>毛利率</th><th>ROE</th><th>研发强度</th>
        <th>网络强度</th><th>平台用户(百万)</th>
      </tr></thead>
      <tbody>
      {"".join(
        f"<tr>"
        f"<td><span class='badge'>{r['code']}</span></td>"
        f"<td>{r['name']}</td><td>{r['industry']}</td>"
        f"<td>{r['gross_margin']:.1%}</td>"
        f"<td>{r['roe']:.1%}</td>"
        f"<td>{r['rd_intensity']:.1%}</td>"
        f"<td>{r['network_intensity']:.2f}</td>"
        f"<td>{r['platform_users_million']:.0f}</td>"
        f"</tr>"
        for r in rows
      )}
      </tbody>
    </table>
    </div>
  </div>

  <div class="card">
    <h2>📈 按行业维度分布</h2>
    <div class="dim-grid" id="dimGrid"></div>
  </div>

  <div class="footer">
    自动生成于 {now} · <a href="https://github.com/iceoryx123/industry-chain-analysis" target="_blank">industry-chain-analysis</a>
  </div>
</div>

<script>
const data = {chart_data};
const labels = data.map(d => d.name);
const datasets = [
  {{ label: '毛利率', data: data.map(d => (d.gross_margin*100).toFixed(1)), backgroundColor: '#4285f4' }},
  {{ label: 'ROE', data: data.map(d => (d.roe*100).toFixed(1)), backgroundColor: '#ea4335' }},
  {{ label: '研发强度', data: data.map(d => (d.rd_intensity*100).toFixed(1)), backgroundColor: '#fbbc05' }},
  {{ label: '网络强度', data: data.map(d => (d.network_intensity*10).toFixed(1)), backgroundColor: '#34a853' }},
];

new Chart(document.getElementById('mainChart'), {{
  type: 'bar',
  data: {{ labels, datasets }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ position: 'top' }} }},
    scales: {{ y: {{ beginAtZero: true }} }}
  }}
}});

// 维度最大值分布
const dimGrid = document.getElementById('dimGrid');
const keys = ['gross_margin','roe','rd_intensity','network_intensity','platform_users_million'];
const names = ['毛利率','ROE','研发强度','网络强度','平台用户'];
keys.forEach((key, i) => {{
  const vals = data.map(d => d[key]).filter(v => v > 0);
  const max = vals.length > 0 ? Math.max(...vals) : 0;
  const avg = vals.length > 0 ? (vals.reduce((a,b) => a+b, 0) / vals.length) : 0;
  dimGrid.innerHTML += `<div class="dim-item"><div class="dim-value">${{max.toFixed(2)}}</div><div>${{names[i]}} (最高)</div><div style="font-size:11px;color:#999;">均值 ${{avg.toFixed(2)}}</div></div>`;
}});
</script>
</body>
</html>"""
    return html


def save_comparison() -> Path:
    """生成并保存对比仪表盘"""
    html = generate_comparison_html()
    output_path = settings.OUTPUT_DIR / "overview.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
