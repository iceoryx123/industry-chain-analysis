"""
🏭 产业链结构性分析 · CLI 入口
===============================

统一命令行接口，覆盖所有常用操作。

支持的指令：
    run            执行流水线（全部或部分）
    list           列出行业案例
    show           查看单个案例
    fetch          仅数据抓取
    insights       仅洞见生成
    dashboard      仅对比仪表盘
    validate       数据质量检查
    version        版本号

使用示例：
    industry-chain run all         # 完整链条
    industry-chain run fetch       # 仅抓取数据
    industry-chain list            # 列出所有行业
    industry-chain show 150000-01  # 查看儿科医院
    industry-chain validate        # 检查数据质量
"""

import sys
import click
from pathlib import Path
from datetime import datetime

from industry_chain.config import settings
from industry_chain import __version__


# =========================================
# 进度提示（易读性）
# =========================================
def _step(msg: str):
    """带 emoji 的步骤提示"""
    click.echo(f"\n  🔄 {msg}...")


def _done(msg: str = "✅ 完成"):
    click.echo(f"  {msg}")


def _error(msg: str):
    click.echo(f"  ❌ {msg}", err=True)


def _info(msg: str):
    click.echo(f"  ℹ️  {msg}")


# =========================================
# CLI 定义
# =========================================
@click.group()
@click.version_option(version=__version__, prog_name="industry-chain")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
def cli(verbose: bool):
    """🏭 产业链结构性分析工具

    \b
    专为申万一级行业分类设计的标准化分析框架。
    包含：数据抓取 → 指标ETL → 案例渲染 → 洞见生成 → 对比分析
    """
    if verbose or settings.VERBOSE:
        click.echo(f"📁 仓库目录: {settings.REPO_ROOT}")


# =========================================
# run 子命令
# =========================================
@cli.command()
@click.argument("stage", default="all",
                type=click.Choice(["all", "fetch", "etl", "render",
                                   "insights", "dashboard"]))
@click.option("--push", is_flag=True, help="完成后自动 git commit + push")
def run(stage: str, push: bool):
    """执行流水线（完整或部分）

    \b
    阶段说明：
    all       完整链条（fetch → etl → render → insights → dashboard）
    fetch     仅数据抓取（akshare / yfinance）
    etl       仅合并去重
    render    仅渲染 {{ indicator }} 占位符
    insights  仅生成洞见
    dashboard 仅生成对比仪表盘
    """
    if stage == "all":
        _step("数据抓取 (fetch)")
        _run_fetch()
        _step("指标合并 (etl)")
        _run_etl()
        _step("案例渲染 (render)")
        _run_render()
        _step("洞见生成 (insights)")
        _run_insights()
        _step("对比仪表盘 (dashboard)")
        _run_dashboard()
        _done("完整流水线执行完成！")
    elif stage == "fetch":
        _run_fetch()
    elif stage == "etl":
        _run_etl()
    elif stage == "render":
        _run_render()
    elif stage == "insights":
        _run_insights()
    elif stage == "dashboard":
        _run_dashboard()

    if push:
        _step("自动提交")
        import subprocess
        subprocess.run(["git", "add", "-A"], cwd=settings.REPO_ROOT)
        subprocess.run(["git", "commit", "-m", f"ci: auto pipeline {datetime.now():%Y-%m-%d %H:%M}"],
                       cwd=settings.REPO_ROOT)
        subprocess.run(["git", "push"], cwd=settings.REPO_ROOT)
        _done("已提交并推送")


# =========================================
# list 子命令
# =========================================
@cli.command("list")
@click.option("--industry", "-i", help="按申万行业筛选，如 '医药生物'")
@click.option("--json", "-j", "json_out", is_flag=True, help="JSON 格式输出")
def list_cases(industry: str, json_out: bool):
    """列出所有行业案例"""
    from industry_chain.models import IndustryMeta

    # 只显示案例级（代码含"-"，如 150000-01），过滤掉行业级元数据（801xxx）
    metas = [m for m in IndustryMeta.list_all() if "-" in m.code]
    if industry:
        metas = [m for m in metas if m.shenwan_industry == industry]

    if not metas:
        _info("没有找到案例")
        return

    if json_out:
        import json
        click.echo(json.dumps([m.__dict__ for m in metas],
                              ensure_ascii=False, indent=2))
        return

    # 按申万行业分组显示
    from collections import defaultdict
    groups = defaultdict(list)
    for m in metas:
        groups[m.shenwan_industry].append(m)

    click.echo("\n  📋 行业案例列表\n")
    for sw_name in sorted(groups.keys()):
        click.echo(f"  📁 {sw_name}:")
        for m in groups[sw_name]:
            ticker_info = f" ({m.representative_ticker})" if m.representative_ticker else ""
            click.echo(f"      {m.code}  {m.name}{ticker_info}")
    click.echo(f"\n  ✅ 共 {len(metas)} 个案例，{len(groups)} 个申万一级行业\n")


# =========================================
# show 子命令
# =========================================
@cli.command()
@click.argument("code")
@click.option("--raw", is_flag=True, help="显示原始内容（不渲染）")
def show(code: str, raw: bool):
    """查看单个案例详情

    \b
    CODE 可以是：
    - 完整代码：150000-01
    - 申万代码：150000（列出该行业所有案例）
    """
    from industry_chain.models import IndustryMeta, IndicatorRow

    if "-" in code:
        # 单个案例
        try:
            meta = IndustryMeta.load(code)
        except FileNotFoundError:
            _error(f"未找到案例: {code}")
            return
        indicators = IndicatorRow.load_latest(code)

        click.echo(f"\n  📄 {meta.code} - {meta.name}")
        click.echo(f"  🏭 {meta.shenwan_industry}（{meta.shenwan_code}）")
        click.echo(f"  📊 代表代码: {meta.representative_ticker or '无'}")
        click.echo(f"\n  --- 核心指标 ---")
        for key, label in [
            ("market_size_cny_bn", "市场规模(十亿)"),
            ("gross_margin", "毛利率"),
            ("roe", "ROE"),
            ("rd_intensity", "研发强度"),
            ("network_intensity", "网络强度"),
            ("platform_users_million", "平台用户(百万)"),
        ]:
            val = getattr(indicators, key, 0)
            if isinstance(val, float):
                if key in ("gross_margin", "roe", "rd_intensity"):
                    click.echo(f"    {label}: {val:.1%}")
                else:
                    click.echo(f"    {label}: {val:.2f}")
            else:
                click.echo(f"    {label}: {val}")

        # 案例文件路径
        case_path = (settings.CASES_DIR /
                     f"{meta.shenwan_code}-{meta.shenwan_industry}" /
                     f"{meta.code}-{meta.name}" /
                     "case.md")
        if case_path.exists():
            click.echo(f"\n  📝 案例文件: {case_path}")
            if not raw:
                # 显示前 20 行摘要
                lines = case_path.read_text(encoding="utf-8").split("\n")
                for line in lines[:20]:
                    if line.strip():
                        click.echo(f"    {line[:120]}")
                if len(lines) > 20:
                    click.echo(f"    ...（共 {len(lines)} 行，使用 --raw 查看全部）")
    else:
        # 按申万代码列出
        metas = [m for m in IndustryMeta.list_all() if m.shenwan_code == code]
        if not metas:
            _error(f"未找到申万行业 {code} 下的案例")
            return
        click.echo(f"\n  🏭 {metas[0].shenwan_industry}（{code}）— {len(metas)} 个案例\n")
        for m in metas:
            click.echo(f"    {m.code}  {m.name}")


# =========================================
# validate 子命令
# =========================================
@cli.command()
def validate():
    """检查数据质量"""
    from industry_chain.processors import validate_data
    errors = validate_data()
    if not errors:
        _done("数据质量检查通过 ✅")
    else:
        for e in errors:
            _error(e)
        _info(f"共 {len(errors)} 个问题")


# =========================================
# insight 子命令（单案例）
# =========================================
@cli.command()
@click.argument("code")
@click.option("--save", is_flag=True, help="保存到案例文件")
def insight(code: str, save: bool):
    """生成单个案例的洞见"""
    from industry_chain.models import IndustryMeta, IndicatorRow
    from industry_chain.analyzers import InsightGenerator

    try:
        meta = IndustryMeta.load(code)
    except FileNotFoundError:
        _error(f"未找到案例: {code}")
        return

    indicators = IndicatorRow.load_latest(code)
    gen = InsightGenerator()
    result = gen.generate(meta, indicators.__dict__)

    click.echo(result)

    if save:
        case_path = (settings.CASES_DIR /
                     f"{meta.shenwan_code}-{meta.shenwan_industry}" /
                     f"{meta.code}-{meta.name}" /
                     "case.md")
        if case_path.exists():
            content = case_path.read_text(encoding="utf-8")
            content += f"\n\n{result}"
            case_path.write_text(content, encoding="utf-8")
            _done(f"洞见已追加到 {case_path}")
        else:
            _error("案例文件不存在")


# =========================================
# 内部函数
# =========================================
def _run_fetch():
    """数据抓取（仅处理案例级代码）"""
    from industry_chain.fetchers import AKSharesFetcher, WebFetcher
    from industry_chain.models import IndustryMeta
    import pandas as pd

    metas = [m for m in IndustryMeta.list_all() if "-" in m.code]
    for meta in metas:
        _info(f"{meta.code} {meta.name}")
        # 使用 akshare 抓取财务数据
        fetcher = AKSharesFetcher()
        result = fetcher.fetch(meta.code, ticker=meta.representative_ticker)
        if any(v != 0 for v in result.values()):
            # 写入 CSV
            csv_path = settings.INDICATORS_DIR / f"{meta.code}.csv"
            result["date"] = datetime.now().strftime("%Y-%m-%d")
            df = pd.DataFrame([result])
            if csv_path.exists():
                old = pd.read_csv(csv_path)
                df = pd.concat([old, df], ignore_index=True)
            df.to_csv(csv_path, index=False)
            _done(f"  ✅ 已写入 {len(df)} 行")
        else:
            _info(f"  ⏭️ 无新数据")

    _done("数据抓取完成")


def _run_etl():
    from industry_chain.processors import run_etl
    count = run_etl()
    _done(f"已处理 {count} 个 CSV 文件")


def _run_render():
    from industry_chain.processors import render_all_cases
    count = render_all_cases()
    _done(f"已渲染 {count} 个案例文件")


def _run_insights():
    from industry_chain.models import IndustryMeta, IndicatorRow
    from industry_chain.analyzers import InsightGenerator
    gen = InsightGenerator()
    count = 0
    for meta in IndustryMeta.list_all():
        if "-" not in meta.code:
            continue
        indicators = IndicatorRow.load_latest(meta.code)
        result = gen.generate(meta, indicators.__dict__)
        # 追加到案例文件
        case_path = (settings.CASES_DIR /
                     f"{meta.shenwan_code}-{meta.shenwan_industry}" /
                     f"{meta.code}-{meta.name}" /
                     "case.md")
        if case_path.exists():
            content = case_path.read_text(encoding="utf-8")
            # 如果已有洞见则跳过
            if "### 🔍 自动洞见（基于规则）" not in content:
                content += f"\n\n{result}"
                case_path.write_text(content, encoding="utf-8")
                count += 1
    _done(f"已生成 {count} 个洞见")


def _run_dashboard():
    from industry_chain.reporters import save_comparison
    path = save_comparison()
    _done(f"对比仪表盘 -> {path}")


# =========================================
# 固定入口
# =========================================
if __name__ == "__main__":
    cli()
