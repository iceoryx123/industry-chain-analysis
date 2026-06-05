#!/usr/bin/env python3
"""generate_insights_template.py
基于规则的自动洞见生成（不调用任何 LLM）
为每个行业的 case.md 生成：价值枢纽、质量评分、拐点信号、业务启示
"""
import re, pandas as pd, yaml
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
IND_DIR = ROOT / "data" / "indicators"
META_DIR = ROOT / "data" / "meta"
CASE_ROOT = ROOT / "cases" / "by-industry"

def generate_insights(code: str, row: dict, meta: dict) -> str:
    """根据指标行 + 元数据生成四段洞见"""
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
    # ── 数据时效信息 ──
    fetch_date = str(row.get("date", ""))[:10]
    report_period = str(row.get("report_period", ""))[:10]

    # ── 补充模块 F-I：分类映射（基于行业特征） ──
    # 周期分类
    cycle_class = {
        # 强周期
        "801010": ("强周期", "底部回升"),  # 农林牧渔（猪周期）
        "801030": ("强周期", "底部"),       # 基础化工
        "801040": ("强周期", "底部"),       # 钢铁
        "801050": ("强周期", "中位"),       # 有色金属
        "801160": ("弱周期", "中位"),       # 建筑材料
        "801170": ("弱周期", "中低位"),     # 机械设备（→强周期）
        "801730": ("强周期", "中位"),       # 交通运输（航运强周期）
        "801750": ("强周期", "底部"),       # 房地产
        "801770": ("强周期", "中位"),       # 传媒（政策监管周期）
        "801790": ("强周期", "中位"),       # 石油石化
        "801800": ("强周期", "中位"),       # 煤炭
        "801880": ("强周期", "顶部回落"),   # 汽车
        # 成长周期
        "801080": ("成长周期", "中位AI驱动上行"),  # 电子
        "801100": ("成长周期", "成长期"),    # 计算机
        "801140": ("成长周期", "中位"),      # 电力设备
        "801170": ("成长周期", "中低位"),    # 机械设备（新质生产力部分）
        "801890": ("成长周期", "成长期"),    # 机器人
        # 弱防御
        "801120": ("弱防御", "低位集采出清中"),  # 医药生物
        "801150": ("弱防御", "中位"),        # 医药生物（二次映射）
        "801200": ("弱防御", "中位"),        # 食品饮料（消费降级压力）
        "801210": ("弱防御", "中位"),        # 食品饮料
        "801770": ("弱周期", "底部修复"),    # 传媒（游戏修复）
        # 强防御
        "801180": ("强防御", "稳定"),        # 银行
        "801190": ("弱周期", "低位"),        # 非银金融
        "801210": ("弱防御", "中位"),        # 美容护理
        "801780": ("强防御", "稳定"),        # 公用事业
        "801790": ("强周期", "中位"),        # 通信（弱防御）
    }
    cc = cycle_class.get(code, ("弱周期", "中位"))
    cyc_type, cyc_pos = cc[0], cc[1] if len(cc) > 1 else "中位"

    # 颠覆风险分类
    disrupt_risk = {
        "801010": "🟢低风险",     # 农林牧渔
        "801030": "🟡中风险",     # 基础化工（生物技术替代）
        "801040": "🟡中风险",     # 钢铁（碳约束）
        "801050": "🟢低风险",     # 有色金属
        "801080": "🟡中风险",     # 电子（技术迭代快）
        "801100": "🟠高风险",     # 计算机（AI重写SaaS）
        "801120": "🟢低风险",     # 医药生物（刚需防御）
        "801140": "🟡中风险",     # 电力设备（技术迭代）
        "801150": "🟢低风险",     # 食品饮料（习惯锁定）
        "801160": "🟢低风险",     # 建筑材料
        "801170": "🟡中风险",     # 机械设备（自动化替代）
        "801180": "🟡中风险",     # 银行（数字化去中心化）
        "801190": "🟡中风险",     # 非银金融
        "801200": "🟢低风险",     # 商贸零售
        "801210": "🟢低风险",     # 社会服务
        "801710": "🟢低风险",     # 纺织服饰
        "801720": "🟡中风险",     # 国防军工
        "801730": "🟡中风险",     # 交通运输
        "801740": "🟢低风险",     # 房地产
        "801750": "🟢低风险",     # 环保
        "801760": "🟠高风险",     # 美容护理（AIGC替代）
        "801770": "🟠高风险",     # 传媒（AI重构内容）
        "801780": "🟢低风险",     # 公用事业
        "801790": "🟢低风险",     # 石油石化
        "801800": "🟡中风险",     # 煤炭
        "801810": "🟢低风险",     # 通信（弱防御）
        "811100": "🟢低风险",     # 家用电器
        "801880": "🟠高风险",     # 汽车（新能车+自动驾驶颠覆）
        "801890": "🟡中风险",     # 机器人（技术迭代）
        "801120": "🟢低风险",     # 医药生物
        "000001": "🟢低风险",     # 综合
    }
    risk_level = disrupt_risk.get(code, "🟡中风险")

    # 增长质量评估
    if has_net:
        # 平台型：看用户增长和网络强度
        if users > 1000:
            growth_quality = "🟢自然增长（用户基数大，网络效应成熟）"
        elif users > 100:
            growth_quality = "🟡增长中（平台处于扩张期，关注转化率）"
        else:
            growth_quality = "🟠导入期（用户基数小，网络效应待验证）"
    else:
        # 传统型：看毛利率和ROE趋势
        if gm_trend > 0.03 and roe_trend > 0.03:
            growth_quality = "🟢高质量增长（毛利率和ROE双双改善）"
        elif gm_trend > 0.03:
            growth_quality = "🟢结构性改善（毛利率提升，定价环境改善）"
        elif roe_trend > 0.03:
            growth_quality = "🟡运营效率提升（ROE改善，关注是否可持续）"
        elif gm_trend < -0.03 and roe_trend < -0.03:
            growth_quality = "🔴内卷式增长（毛利率和ROE双降，以价换量）"
        elif gm_trend < -0.03:
            growth_quality = "🟡增长承压（毛利率下滑，竞争加剧或成本上升）"
        elif roe_trend < -0.03:
            growth_quality = "🟡增长质量下降（ROE走低，杠杆或效率恶化）"
        else:
            growth_quality = "🟡稳定增长（指标变化不大，存量博弈阶段）"

    # 行业分化方向
    if cr4 > 0.5:
        differentiation = "🏢寡头格局（CR4>0.5，龙头主导，新进入者难）"
    elif cr4 > 0.3:
        differentiation = "🏢集中度中（CR4 0.3-0.5，行业正在整合中）"
    elif gm > 0.4 and cr4 < 0.3:
        differentiation = "🔀百花齐放（毛利率高+集中度低，各细分差异化竞争）"
    elif gm < 0.2 and cr4 < 0.3:
        differentiation = "⚔️内卷竞争（毛利率低+集中度低，价格战可能持续）"
    else:
        differentiation = "🔀分散市场（CR4<0.3，需进一步看细分赛道）"

    # ── 1. 价值枢纽 ──
    if has_net:
        if net > 0.6:
            hub = f"{name}平台/生态构建者（强网络效应建网者）"
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

    # ── 2. 质量评分 ──
    # 护城河：毛利率越高护城河越深
    moat = min(10, max(1, int(gm * 18 + 1)))
    # 定价权：ROE越高定价权越强
    pricing = min(10, max(1, int(roe * 25 + 1)))
    # 替代难度：研发强度越高替代难度越大
    subst = min(10, max(1, int(rd * 40 + 1)))
    # 生态位：网络效应 + 用户规模
    eco = min(10, max(1, int(net * 8 + users * 0.3 + 1)))
    # 集中度加成
    if hhi > 2500:
        moat = min(10, moat + 1)
    elif hhi < 1000:
        moat = max(1, moat - 1)

    # ── 趋势加成（毛利率/ROE趋势方向） ──
    gm_trend_flag = ""
    roe_trend_flag = ""
    if gm_trend > 0.02:
        moat = min(10, moat + 1)
        gm_trend_flag = "↑"
    elif gm_trend < -0.02:
        moat = max(1, moat - 1)
        gm_trend_flag = "↓"
    else:
        gm_trend_flag = "→"

    if roe_trend > 0.02:
        pricing = min(10, pricing + 1)
        roe_trend_flag = "↑"
    elif roe_trend < -0.02:
        pricing = max(1, pricing - 1)
        roe_trend_flag = "↓"
    else:
        roe_trend_flag = "→"

    composite = round(moat * 0.30 + pricing * 0.25 + subst * 0.25 + eco * 0.20, 1)

    # ── 3. 拐点信号 ──
    signals = []
    if has_net:
        if net > 0.5:
            signals.append("📈 网络效应强劲，关注生态扩张速度")
        if users > 500:
            signals.append("👥 用户规模超大，关注变现效率")
    if gm > 0.5:
        signals.append("💰 高毛利率，警惕新进入者压价")
    elif gm < 0.15:
        signals.append("⚠️ 毛利率偏低，行业竞争激烈")
    if roe > 0.20:
        signals.append("📊 ROE 优秀，关注可持续性")
    elif roe < 0.05:
        signals.append("⚠️ ROE 低于资金成本，价值毁灭风险")
    if rd > 0.10:
        signals.append("🔬 高研发投入，技术迭代风险与机遇并存")
    if cr4 > 0.5:
        signals.append("🏢 集中度高，关注龙头定价权变化")
    if hhi > 2500:
        signals.append("🔒 市场高度集中，反垄断风险")
    # ── 趋势信号 ──
    if gm_trend > 0.03:
        signals.append(f"📈 毛利率趋势向好（↑{gm_trend:.1%}/年），定价环境改善")
    elif gm_trend < -0.03:
        signals.append(f"📉 毛利率持续下滑（↓{abs(gm_trend):.1%}/年），关注成本/竞争压力")
    if roe_trend > 0.03:
        signals.append(f"📊 ROE 趋势上行（↑{roe_trend:.1%}/年），运营效率改善")
    elif roe_trend < -0.03:
        signals.append(f"⚠️ ROE 趋势下行（↓{abs(roe_trend):.1%}/年），盈利能力恶化")
    if mkt > 500:
        signals.append("📦 市场规模巨大，关注增量 / 存量切换")
    if not signals:
        signals.append("📊 当前指标无明显拐点信号，持续观察")

    # ── 4. 业务启示 ──
    if has_net:
        if net > 0.5:
            suggestion = f"重点关注{name}平台的生态扩展能力、用户粘性指标和网络密度变化"
        else:
            suggestion = f"关注{name}的网络效应构建进程，评估其平台化转型潜力"
    else:
        if gm > 0.4:
            suggestion = f"关注{name}高毛利环节的护城河可持续性，警惕新进入者和技术替代"
        elif cr4 > 0.4:
            suggestion = f"{name}行业集中度高，关注龙头企业的定价权和市场份额变化"
        elif roe > 0.15:
            suggestion = f"{name}具备较好盈利能力，关注资本开支周期和产能变化"
        else:
            suggestion = f"行业较为分散，需进一步细分识别潜在价值枢纽"

    return f"""### 🔍 自动洞见（基于规则引擎）

> ⏱️ **数据时效说明**
> - 毛利率/ROE 数据来源：**akshare（东方财富/同花顺）**
> - 财务报告期：**{report_period or "未知"}**
> - 数据拉取日期：**{fetch_date or "未知"}**
> - ⚠️ 评分和结论基于上述时效的数据，**数据过期后结论可能失效**

**行业**：{name} | **类别**：{cat} | **细分**：{sub} | **版本**：{"双模(v10.x)" if has_net else "传统(v9.2)"}

**价值枢纽识别**：{hub}

**质量评分**（满分10）：
- 🛡️ 护城河：{moat}/10
- 💎 定价权：{pricing}/10
- 🔒 替代难度：{subst}/10
- 🌐 生态位：{eco}/10
- 📊 **综合评分**：{composite}/10

**补充模块（F-J）自动诊断**：

**F - 增长引擎**：{growth_quality}
- 渗透率阶段：{"导入期" if gm > 0.6 and mkt < 50 else "成长期" if gm > 0.4 else "成熟期" if gm > 0.2 else "饱和/衰落期"}
- 天花板判断：{"市场空间大，渗透率提升空间广阔" if mkt > 300 else "市场空间中等，关注细分增长" if mkt > 100 else "市场偏小，需关注出海或品类扩展"}

**G - 周期定位**：{cyc_type} | 当前位置：{cyc_pos}
- 对投资策略的影响：{"顺周期配置，关注库存和产能指标" if cyc_type == "强周期" else "成长型配置，关注增长持续性" if cyc_type == "成长周期" else "防御型配置，关注股息和稳定性"}

**H - 行业分化**：{differentiation}

**I - 颠覆风险**：{risk_level}
- 颠覆来源判断：{"AI/数字化替代" if risk_level in ("🟠高风险", "🔴极高风险") else "碳约束/技术迭代" if cyc_type == "强周期" else "稳定，颠覆概率低"}

**拐点信号**：
{signals and chr(10).join("- " + s for s in signals) or "- 暂无明显拐点信号"}

**业务启示**：
- {suggestion}
"""

def main():
    print("=" * 60)
    print("🧠 自动生成行业洞见")
    print("=" * 60)

    # 先清理旧的自动洞见
    all_case_files = list(CASE_ROOT.rglob("case.md"))
    cleaned = 0
    for cf in all_case_files:
        txt = cf.read_text(encoding="utf-8")
        if "### 🔍 自动洞见（基于规则引擎）" in txt:
            # 移除旧的自动洞见区块
            parts = txt.split("### 🔍 自动洞见（基于规则引擎）")
            if len(parts) >= 2:
                before = parts[0]
                after_parts = "### 🔍 自动洞见（基于规则引擎）".join(parts[1:]).split("\n---", 1)
                if len(after_parts) >= 2:
                    after = after_parts[1]
                else:
                    after = ""
                cf.write_text(before + "\n---\n" + after.strip(), encoding="utf-8")
                cleaned += 1
    print(f"  🧹 已清理 {cleaned} 个旧洞见区块")

    # 生成新洞见
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

        # 查找对应案例文件
        case_files = list(CASE_ROOT.glob(f"**/{code}*/case.md"))
        if not case_files:
            continue

        for case_md in case_files:
            txt = case_md.read_text(encoding="utf-8")
            # 追加洞见到文件末尾
            if "### 🔍 自动洞见（基于规则引擎）" in txt:
                # 替换已有洞见
                before = txt.split("### 🔍 自动洞见（基于规则引擎）")[0]
                after_parts = txt.split("### 🔍 自动洞见（基于规则引擎）")[1].split("\n---", 1)
                after = "\n---" + after_parts[1] if len(after_parts) >= 2 else ""
                txt = before + insight + after
            else:
                txt = txt.rstrip() + "\n\n" + insight + "\n"
            case_md.write_text(txt, encoding="utf-8")
            print(f"  ✅ {meta['name']} ({code}): 综合评分 {insight.split('综合评分')[1].split('/10')[0].strip() if '综合评分' in insight else 'N/A'}/10")
            count += 1

    print(f"\n✅ 完成！共为 {count} 个行业生成洞见")

if __name__ == "__main__":
    main()
