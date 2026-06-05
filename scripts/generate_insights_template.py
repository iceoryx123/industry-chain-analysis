#!/usr/bin/env python3
"""generate_insights_template.py
基于规则的洞见生成（不调用任何 LLM，完全免费）
"""
import re, pandas as pd
from pathlib import Path

ROOT = Path("/tmp/industry-chain-analysis-push")
IND_DIR = ROOT / "data" / "indicators"

def generate_insights(code: str, row: dict) -> str:
    """根据指标行生成四段洞见"""
    gm = row.get("gross_margin", 0)
    roe = row.get("roe", 0)
    rd = row.get("rd_intensity", 0)
    net = row.get("network_intensity", 0)
    users = row.get("platform_users_million", 0)
    cr4 = row.get("cr4", 0)

    # 1. 价值枢纽
    if net > 0.5:
        hub = "平台/生态构建者（建网者）"
    elif gm > 0.4:
        hub = "品牌/技术驱动型企业（高毛利枢纽）"
    elif cr4 > 0.3:
        hub = "行业龙头企业（集中度优势）"
    else:
        hub = "产业链关键环节（待进一步识别）"

    # 2. 质量评分解释
    moat_score = min(10, int(gm * 20 + 2))
    pricing_score = min(10, int(roe * 30 + 2))
    subst_score = min(10, int(rd * 50 + 2))
    eco_score = min(10, int(net * 8 + users * 0.5 + 2))

    # 3. 拐点信号
    signals = []
    if net > 0.3 and net < 0.7:
        signals.append("网络效应处于上升期（中期拐点关注）")
    elif net >= 0.7:
        signals.append("网络效应趋于饱和（关注新增长曲线）")
    if gm < 0.2:
        signals.append("毛利率低位，警惕竞争加剧")
    elif gm > 0.6:
        signals.append("高毛利率但需关注可持续性")
    if roe < 0.05:
        signals.append("ROE 低于资金成本，价值毁灭风险")
    if rd > 0.1:
        signals.append("高强度研发投入，技术迭代风险")
    if not signals:
        signals.append("当前指标无明显拐点信号")

    # 4. 启示
    if net > 0.5:
        suggestion = "重点关注平台的生态扩展能力和用户粘性指标"
    elif gm > 0.4:
        suggestion = "关注高毛利企业的护城河可持续性，警惕新进入者"
    elif cr4 > 0.3:
        suggestion = "行业集中度较高，关注龙头企业的定价权变化"
    else:
        suggestion = "行业较为分散，需进一步细分识别潜在枢纽"

    return f"""
### 🔍 自动洞见（基于规则）

**价值枢纽识别**：{hub}

**质量评分**（维度 1‑10）：
- 护城河：{moat_score}/10 | 定价权：{pricing_score}/10 | 替代难度：{subst_score}/10 | 生态位：{eco_score}/10

**拐点信号**：
- {"；".join(signals)}

**业务启示**：
- {suggestion}
"""

def main():
    for csv_path in sorted(IND_DIR.glob("*.csv")):
        code = csv_path.stem
        df = pd.read_csv(csv_path)
        latest = df.iloc[-1].to_dict()
        insight = generate_insights(code, latest)

        # 查找对应案例
        for case_md in sorted(ROOT.glob(f"cases/**/{code}*/case.md")):
            txt = case_md.read_text(encoding="utf-8")
            # 检查是否已有自动洞见
            if "### 🔍 自动洞见（基于规则）" in txt:
                # 替换
                before = txt.split("### 🔍 自动洞见（基于规则）")[0]
                after = txt.split("### 🔍 自动洞见（基于规则）")[1]
                if "---" in after:
                    after = after.split("---", 1)[1] if "---" in after.split("---", 1)[1] else after
                txt = before + insight + "\n---\n" + after.strip()
            else:
                # 追加到文件末尾
                txt += "\n\n---\n" + insight
            case_md.write_text(txt, encoding="utf-8")
            print(f"  ✅ 洞见已写入: {case_md}")

if __name__ == "__main__":
    main()
