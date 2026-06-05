#!/usr/bin/env python3
"""generate_insights_template.py — 重构版
基于规则的自动洞见生成（不调用任何 LLM）

=== v2 改进 ===
1. 修复 ROOT 路径（自适应）
2. 重写洞见替换逻辑（不再依赖 split('---')，改用正则精准定位）
3. 优化渗透率判断（使用毛利率+ROE+市场规模的组合逻辑）
4. 增长引擎判断动态化（基于指标变化趋势而非硬编码）
5. 清理多个 trailing ---
6. 洞见区块统一放置于文件末尾，以一个 --- 分隔
"""
import re
import pandas as pd
import yaml
from pathlib import Path

# ── 自适应 ROOT ──
ROOT = Path(__file__).resolve().parent.parent
IND_DIR = ROOT / "data" / "indicators"
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry"


def _pct(s) -> float:
    """安全解析百分比字符串或数值"""
    if isinstance(s, str):
        s = s.strip().rstrip("%").replace("亿元", "").replace("万元", "").replace("万亿元", "").replace("亿", "").replace("万", "").replace(",", "").replace("，", "").strip()
        try:
            return float(s) / 100 if s else 0.0
        except:
            return 0.0
    try:
        return float(s or 0)
    except:
        return 0.0


def generate_insights(code: str, row: dict, meta: dict) -> str:
    name = meta.get("name", code)
    cat = meta.get("category", "")
    sub = meta.get("subsector", "")
    has_net = meta.get("has_network_effect", False)

    gm = float(row.get("gross_margin", 0) or 0)
    roe = float(row.get("roe", 0) or 0)
    rd = float(row.get("rd_intensity", 0) or 0)
    net = float(row.get("network_intensity", 0) or 0)
    users = float(row.get("platform_users_million", 0) or 0)
    cr4 = float(row.get("cr4", 0) or 0)
    hhi = float(row.get("hhi", 0) or 0)
    mkt = float(row.get("market_size_cny_bn", 0) or 0)
    gm_trend = float(row.get("gross_margin_trend", 0) or 0)
    roe_trend = float(row.get("roe_trend", 0) or 0)
    cycle_score = float(row.get("cycle_score", 50) or 50)
    cycle_position = str(row.get("cycle_position", "中位") or "中位")
    fetch_date = str(row.get("date", ""))[:10]
    report_period = str(row.get("report_period", ""))[:10]

    # ── 周期分类 ──
    cycle_class_type = {
        "801010": "强周期", "801020": "强周期", "801030": "强周期",
        "801040": "强周期", "801050": "成长周期", "801060": "成长周期",
        "801070": "强周期", "801080": "弱周期", "801090": "弱周期",
        "801100": "强周期", "801110": "弱周期", "801120": "成长周期",
        "801130": "弱防御", "801150": "弱防御", "801200": "弱周期",
        "801210": "弱周期", "801230": "强周期", "801710": "弱防御",
        "801720": "弱防御", "801730": "弱周期", "801740": "弱周期",
        "801750": "弱防御", "801780": "强周期", "801790": "强周期",
        "801880": "成长周期", "801890": "弱周期",
        "801170": "强防御", "801140": "强防御", "801160": "弱周期",
        "801180": "强周期", "801190": "强防御", "801220": "弱周期",
    }
    cyc_type = cycle_class_type.get(code, "弱周期")
    cyc_pos = cycle_position if cycle_position != "unknown" else "中位"

    # ── 颠覆风险分类 ──
    disrupt_risk = {
        "801010": "🟢低风险", "801020": "🟡中风险", "801030": "🟡中风险",
        "801040": "🟢低风险", "801050": "🟡中风险", "801060": "🟠高风险",
        "801070": "🟠高风险", "801080": "🟢低风险", "801090": "🟠高风险",
        "801100": "🟢低风险", "801110": "🟡中风险", "801120": "🟡中风险",
        "801130": "🟢低风险", "801140": "🟡中风险", "801150": "🟢低风险",
        "801160": "🟡中风险", "801170": "🟡中风险", "801180": "🟢低风险",
        "801190": "🟢低风险", "801200": "🟡中风险", "801210": "🟡中风险",
        "801220": "🟢低风险", "801230": "🟡中风险", "801720": "🟢低风险",
        "801730": "🟡中风险", "801740": "🟠高风险", "801750": "🟢低风险",
        "801780": "🟡中风险", "801790": "🟡中风险", "801880": "🟠高风险",
        "801890": "🟢低风险", "801170": "🟡中风险",
    }
    risk_level = disrupt_risk.get(code, "🟡中风险")

    # ── 颠覆来源（差异化描述） ──
    disrupt_source_map = {
        "801010": "生物技术/基因编辑对传统种养殖的替代",
        "801020": "生物合成/碳约束对传统化工的替代",
        "801030": "碳约束+短流程电弧炉对长流程的替代",
        "801040": "资源不可替代，但回收技术影响供需格局",
        "801050": "半导体技术迭代+AI芯片架构变革",
        "801060": "AI重写SaaS/软件商业模式",
        "801070": "新能车+自动驾驶颠覆传统车企格局",
        "801080": "人工密集型，技术替代缓慢",
        "801090": "AI重构内容创作+分发，平台权力再分配",
        "801100": "区域性+运输成本提供天然保护",
        "801110": "自动化/机器人替代传统制造",
        "801120": "新能源技术迭代快速，固态电池等",
        "801130": "人际交互刚需，AI辅助非替代",
        "801140": "数字货币/去中心化金融对传统中介的替代",
        "801150": "刚需+监管壁垒提供稳定护城河",
        "801160": "数字化投顾/智能投顾替代传统中介",
        "801170": "基础设施壁垒高，Starlink等卫星通信构成远期威胁",
        "801180": "物理资产不可替代，但REITs改变定价模式",
        "801190": "自然垄断+政策刚需，颠覆概率极低",
        "801200": "3D打印/自动化对传统纺织的渐进替代",
        "801210": "自动化+AI设计对传统制造的替代",
        "801220": "政策刚需驱动，技术替代有限",
        "801230": "自动驾驶/新能源对传统运输模式的替代",
        "801720": "消费品牌忠诚度高，技术替代有限",
        "801730": "智能化+出海改变竞争格局",
        "801740": "电商对线下零售的持续替代",
        "801750": "消费防御性强，品牌壁垒稳固",
        "801780": "新能源替代对化石能源的长期压力",
        "801790": "碳约束+新能源对煤炭的长期替代",
        "801880": "AI大模型+通用机器人可能重塑行业",
        "801890": "缺乏主线，颠覆风险分散",
    }
    disrupt_source = disrupt_source_map.get(code, "碳约束/技术迭代")

    # ── 增长引擎判断（动态 + 行业特征 + 周期调整） ──
    growth_quality = "🟡稳定增长"
    penetration_stage = "成熟期"
    ceiling_judgment = "市场空间中等，关注细分增长"

    # 行业分类辅助判断
    is_cyclical_bottom = cyc_type == "强周期" and "底部" in cyc_pos
    is_cyclical_low = cyc_type == "强周期" and "低位" in cyc_pos
    is_cyclical_mid = cyc_type == "强周期" and "中位" in cyc_pos
    is_growth_sector = cyc_type == "成长周期"
    is_defensive = cyc_type in ("弱防御", "强防御")
    is_platform = cat.startswith("02-")
    is_regulated = cat.startswith("03-")

    # 成长周期行业优先高增长，不受低ROE影响
    if is_growth_sector and gm > 0.20:
        growth_quality = "🟢高增长"
        penetration_stage = "成长期"
        ceiling_judgment = "市场空间大，渗透率提升空间广阔" if mkt > 100 else "市场空间中等，关注细分增长"
    elif is_growth_sector:
        growth_quality = "🟢高增长（导入期）"
        penetration_stage = "导入期"
        ceiling_judgment = "市场偏小，需关注出海或品类扩展"
    # 平台型行业统一用成熟期/成长期，避免"衰退/困境"标签
    elif is_platform and gm > 0.15:
        growth_quality = "🟡稳定增长"
        penetration_stage = "成长期"
        ceiling_judgment = "市场空间大，渗透率提升空间广阔" if mkt > 100 else "市场空间中等，关注细分增长"
    elif is_platform:
        growth_quality = "🟠成熟期"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长"
    # 受监管行业有政策护城河，资产周转低但并非衰退
    elif is_regulated and gm > 0.10:
        growth_quality = "🟠成熟期"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长" if mkt > 200 else "市场偏小，关注集中度提升"
    elif is_regulated:
        growth_quality = "🟠成熟期（低利润模式）"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注集中度提升"
    # 防御型行业有稳定需求，即使用ROE低也不应标为"衰退"
    elif is_defensive and gm > 0.35:
        growth_quality = "🟡稳定增长"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间大，渗透率提升空间广阔" if mkt > 300 else "市场空间中等，关注细分增长"
    elif is_defensive and gm > 0.15:
        growth_quality = "🟠成熟期"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长"
    # 传统行业按财务指标判断
    elif gm > 0.50 and roe > 0.10 and cyc_type in ("弱防御", "弱周期"):
        growth_quality = "🟢高增长"
        penetration_stage = "导入期" if mkt < 200 else "成长期"
        ceiling_judgment = "市场空间大，渗透率提升空间广阔" if mkt > 50 else "市场偏小，需关注出海或品类扩展"
    elif gm > 0.30 and roe > 0.05:
        growth_quality = "🟡稳定增长"
        penetration_stage = "成长期" if cyc_type in ("弱周期",) else "成熟期"
        ceiling_judgment = "市场空间大，渗透率提升空间广阔" if mkt > 300 else "市场空间中等，关注细分增长"
    elif gm > 0.15 and roe > 0.03:
        growth_quality = "🟠成熟期"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长" if mkt > 200 else "市场偏小，关注集中度提升"
    elif is_cyclical_bottom:
        growth_quality = "🔄周期底部"
        penetration_stage = "成熟期" if gm > 0.15 else "饱和/衰落期"
        ceiling_judgment = "市场空间中等，关注细分增长"
    elif is_cyclical_low:
        growth_quality = "🔄周期低位"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长"
    elif is_cyclical_mid:
        growth_quality = "🔄周期中位"
        penetration_stage = "成熟期"
        ceiling_judgment = "市场空间中等，关注细分增长"
    else:
        growth_quality = "🔴衰退/困境"
        penetration_stage = "饱和/衰落期"
        ceiling_judgment = "存量博弈，关注龙头份额变化" if mkt > 100 else "市场偏小，需关注出海或品类扩展"

    # ── 1. 价值枢纽 ──
    if has_net:
        if net > 0.6:
            hub = f"{name}平台/生态构建者（强网络效应）"
        elif net > 0.3:
            hub = f"{name}平台运营商（中度网络效应）"
        else:
            hub = f"{name}产业链核心环节（网络效应待观察）"
    else:
        if gm > 0.5:
            hub = f"{name}高毛利环节（品牌/技术驱动）"
        elif gm > 0.3:
            hub = f"{name}中段制造/服务环节"
        elif cr4 > 0.4:
            hub = f"{name}龙头企业（集中度优势）"
        elif roe > 0.15:
            hub = f"{name}高效运营环节"
        else:
            hub = f"{name}产业链关键环节（需进一步识别）"

    # ── 2. 质量评分（行业类别调整） ──
    # 护城河：毛利率映射 + 行业调整
    moat = min(10, max(1, int(gm * 18 + 1)))
    pricing = min(10, max(1, int(roe * 25 + 1)))
    subst = min(10, max(1, int(rd * 40 + 1)))
    eco = min(10, max(1, int(net * 8 + users * 0.3 + 1)))

    # 集中度调整
    if hhi > 2500:
        moat = min(10, moat + 1)
    elif hhi < 1000:
        moat = max(1, moat - 1)

    # 行业类别调整
    if cat == "03-Regulated":
        moat = min(10, moat + 1)  # 政策护城河
    elif cat == "02-Platform":
        eco = min(10, eco + 1) if net > 0.3 else eco
    elif cat == "04-Emerging":
        subst = min(10, subst + 2)  # 新兴行业技术壁垒高

    # 趋势调整
    if gm_trend > 0.02:
        moat = min(10, moat + 1)
    elif gm_trend < -0.02:
        moat = max(1, moat - 1)
    if roe_trend > 0.02:
        pricing = min(10, pricing + 1)
    elif roe_trend < -0.02:
        pricing = max(1, pricing - 1)

    composite = round(moat * 0.30 + pricing * 0.25 + subst * 0.25 + eco * 0.20, 1)

    # ── 3. 拐点信号 ──
    signals = []
    if has_net and net > 0.5:
        signals.append("📈 网络效应强劲，关注生态扩张速度")
    if has_net and users > 500:
        signals.append("👥 用户规模超大，关注变现效率")
    if gm > 0.5:
        signals.append("💰 高毛利率，警惕新进入者压价")
    elif gm < 0.15:
        signals.append("⚠️ 毛利率偏低，行业竞争激烈")
    if roe > 0.20:
        signals.append("📊 ROE 优秀，关注可持续性")
    elif roe < 0.05:
        signals.append("⚠️ ROE 低于资金成本，价值毁灭风险")
    if gm_trend > 0.03:
        signals.append(f"📈 毛利率年化提升{gm_trend*100:.1f}%，盈利能力改善")
    elif gm_trend < -0.03:
        signals.append(f"📉 毛利率年化下降{gm_trend*100:.1f}%，需关注成本/竞争")
    if roe_trend > 0.03:
        signals.append(f"📈 ROE 年化提升{roe_trend*100:.1f}%，资本回报改善")
    elif roe_trend < -0.03:
        signals.append(f"📉 ROE 年化下降{roe_trend*100:.1f}%，效率恶化")
    if mkt > 500:
        signals.append("📦 市场规模巨大，关注增量 / 存量切换")
    if not signals:
        signals.append("📊 当前指标无明显拐点信号，持续观察")

    # ── 行业分化 ──
    if cr4 > 0.5:
        differentiation = "🏆寡头格局（CR4>0.5，龙头主导定价）"
    elif cr4 > 0.3:
        differentiation = "🏢集中度中（CR4 0.3-0.5，行业整合中）"
    elif gm > 0.4 and cr4 < 0.3:
        differentiation = "🔀百花齐放（毛利率高+集中度低，差异化竞争）"
    elif gm < 0.2 and cr4 < 0.3:
        differentiation = "⚔️内卷竞争（毛利率低+集中度低，价格战可能持续）"
    else:
        differentiation = "🔀分散市场（需进一步看细分赛道）"

    # ── 4. 业务启示 ──
    if has_net and net > 0.5:
        suggestion = f"重点关注{name}平台的生态扩展能力、用户粘性指标和网络密度变化"
    elif has_net:
        suggestion = f"关注{name}的网络效应构建进程，评估其平台化转型潜力"
    elif gm > 0.4:
        suggestion = f"关注{name}高毛利环节的护城河可持续性，警惕新进入者和技术替代"
    elif cr4 > 0.4:
        suggestion = f"{name}行业集中度高，关注龙头企业的定价权和市场份额变化"
    elif roe > 0.15:
        suggestion = f"{name}具备较好盈利能力，关注资本开支周期和产能变化"
    else:
        suggestion = f"行业较为分散，需进一步细分识别潜在价值枢纽"

    # ── 版本标签 ──
    version_tag = "双模(v10.x)" if has_net else "传统(v9.2)"

    return f"""### 🔍 自动洞见（基于规则引擎）

> ⏱️ **数据时效说明**
> - 毛利率/ROE 数据来源：**akshare（东方财富/同花顺）**
> - 财务报告期：**{report_period or "未知"}**
> - 数据拉取日期：**{fetch_date or "未知"}**
> - ⚠️ 评分和结论基于上述时效的数据，**数据过期后结论可能失效**

**行业**：{name} | **类别**：{cat} | **细分**：{sub} | **版本**：{version_tag}

**价值枢纽识别**：{hub}

**质量评分**（满分10）：
- 🛡️ 护城河：{moat}/10
- 💎 定价权：{pricing}/10
- 🔒 替代难度：{subst}/10
- 🌐 生态位：{eco}/10
- 📊 **综合评分**：{composite}/10

**补充模块（F-J）自动诊断**：

**F - 增长引擎**：{growth_quality}
- 渗透率阶段：{penetration_stage}
- 天花板判断：{ceiling_judgment}

**G - 周期定位**：{cyc_type} | 当前位置：{cyc_pos}（ROE历史百分位{cycle_score:.0f}%）
- 投资策略：{"顺周期配置，关注库存和产能指标" if cyc_type == "强周期" else "成长型配置，关注增长持续性" if cyc_type == "成长周期" else "防御型配置，关注股息和稳定性"}

**H - 行业分化**：{differentiation}

**I - 颠覆风险**：{risk_level}
- 风险来源：{disrupt_source}

**拐点信号**：
{chr(10).join("- " + s for s in signals) if signals else "- 暂无明显拐点信号"}

**业务启示**：
- {suggestion}
"""


def _clean_trailing_seps(text: str) -> str:
    """清理尾部多余的 --- 分隔符"""
    # 移除文件末尾连续多个 --- 行（保留一个）
    lines = text.rstrip().splitlines()
    # 从后往前找非空行
    new_lines = []
    in_tail_seps = True
    for line in reversed(lines):
        if in_tail_seps and line.strip() == "---" or line.strip() == "":
            continue
        else:
            in_tail_seps = False
        new_lines.append(line)
    new_lines.reverse()
    return "\n".join(new_lines) + "\n"


def main():
    print("=" * 60)
    print("🧠 自动生成行业洞见（v2 重构版）")
    print(f"📂 仓库根目录: {ROOT}")
    print("=" * 60)

    all_case_files = sorted(CASE_ROOT.rglob("case.md"))
    total = len(all_case_files)

    # ── 清理旧的洞见区块（精准正则替换） ──
    old_pattern = re.compile(
        r'\n*---\s*\n*### 🔍 自动洞见（基于规则引擎）\n.*?(?=\n*$|$)',
        re.DOTALL
    )
    old_pattern2 = re.compile(
        r'### 🔍 自动洞见（基于规则引擎）\n.*?(?=\n*$|$)',
        re.DOTALL
    )

    cleaned_count = 0
    for cf in all_case_files:
        txt = cf.read_text(encoding="utf-8")
        new_txt = old_pattern.sub("", txt)
        new_txt = old_pattern2.sub("", new_txt)
        new_txt = _clean_trailing_seps(new_txt)
        if new_txt != txt:
            cf.write_text(new_txt, encoding="utf-8")
            cleaned_count += 1
    print(f"  🧹 清理旧洞见区块：{cleaned_count}/{total} 个案例")

    # ── 生成新洞见 ──
    count = 0
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
        insight = generate_insights(code, latest, meta)

        case_files = list(CASE_ROOT.glob(f"**/{code}*/case.md"))
        if not case_files:
            print(f"  ⚠️ {code}: 未找到案例文件")
            continue

        for case_md in case_files:
            txt = case_md.read_text(encoding="utf-8")
            # 追加洞见到文件末尾（以 --- 分隔）
            txt = txt.rstrip() + "\n\n---\n\n" + insight + "\n"
            # 清理多余 trailing separators
            txt = _clean_trailing_seps(txt)
            case_md.write_text(txt, encoding="utf-8")

            # 提取评分
            score_match = re.search(r'综合评分\*{0,2}[：:]\s*([\d.]+)/10', insight)
            score_str = score_match.group(1) if score_match else "N/A"
            print(f"  ✅ {meta['name']} ({code}): {score_str}/10")
            count += 1

    print(f"\n✅ 完成！共为 {count} 个行业生成/更新洞见")


if __name__ == "__main__":
    main()
