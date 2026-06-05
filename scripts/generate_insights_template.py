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

**行业**：{name} | **类别**：{cat} | **细分**：{sub} | **版本**：{"双模(v10.x)" if has_net else "传统(v9.2)"}

**价值枢纽识别**：{hub}

**质量评分**（满分10）：
- 🛡️ 护城河：{moat}/10
- 💎 定价权：{pricing}/10
- 🔒 替代难度：{subst}/10
- 🌐 生态位：{eco}/10
- 📊 **综合评分**：{composite}/10

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
