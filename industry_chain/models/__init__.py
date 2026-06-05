"""
数据模型
========

定义行业、指标、案例等核心数据结构。
使用 dataclass 保持简单、可读、可序列化。
"""

from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional, List
import yaml
import pandas as pd
from pathlib import Path


# =========================================
# 行业元数据模型
# =========================================
@dataclass
class IndustryMeta:
    """行业元数据，对应 data/meta/*.yaml"""
    code: str                           # 唯一代码，如 "150000-01"
    name: str                           # 行业名，如 "儿科医院"
    shenwan_code: str = ""              # 申万一级代码，如 "150000"
    shenwan_industry: str = ""          # 申万一级名，如 "医药生物"
    subsector: str = ""                 # 子行业，如 "医疗服务"
    has_network_effect: bool = False    # 是否有网络效应
    update_cycle: str = "quarterly"     # 更新频率
    data_source: List[str] = field(default_factory=list)
    representative_ticker: str = ""
    official_website: str = ""

    @classmethod
    def load(cls, code: str, meta_dir: Optional[Path] = None) -> "IndustryMeta":
        """从 YAML 文件加载（忽略额外字段）"""
        from industry_chain.config import settings
        meta_dir = meta_dir or settings.META_DIR
        filepath = meta_dir / f"{code}.yaml"
        if not filepath.exists():
            raise FileNotFoundError(f"元数据不存在: {filepath}")
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
        # 只取模型定义的字段，忽略额外字段
        valid_fields = set(cls.__dataclass_fields__.keys())
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def save(self, meta_dir: Optional[Path] = None):
        """保存到 YAML 文件"""
        from industry_chain.config import settings
        meta_dir = meta_dir or settings.META_DIR
        filepath = meta_dir / f"{self.code}.yaml"
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, allow_unicode=True,
                           sort_keys=False, default_flow_style=False)

    @classmethod
    def list_all(cls, meta_dir: Optional[Path] = None) -> List["IndustryMeta"]:
        """列出所有行业（忽略额外字段）"""
        from industry_chain.config import settings
        meta_dir = meta_dir or settings.META_DIR
        result = []
        valid_fields = set(cls.__dataclass_fields__.keys())
        for f in sorted(meta_dir.glob("*.yaml")):
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            filtered = {k: v for k, v in data.items() if k in valid_fields}
            result.append(cls(**filtered))
        return result


# =========================================
# 指标数据模型
# =========================================
@dataclass
class IndicatorRow:
    """单行指标数据"""
    industry_code: str
    date: str
    market_size_cny_bn: float = 0.0
    cr4: float = 0.0
    hhi: float = 0.0
    gross_margin: float = 0.0
    roe: float = 0.0
    rd_intensity: float = 0.0
    network_intensity: float = 0.0
    platform_users_million: float = 0.0
    average_transaction_value_cny: float = 0.0

    @classmethod
    def load_latest(cls, code: str,
                    indicators_dir: Optional[Path] = None) -> "IndicatorRow":
        """从 CSV 读取最新一行指标"""
        from industry_chain.config import settings
        ind_dir = indicators_dir or settings.INDICATORS_DIR

        # 尝试完整代码，再试申万前缀
        for candidate in [f"{code}.csv", f"{code.split('-')[0]}.csv"]:
            csv_path = ind_dir / candidate
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                if not df.empty:
                    row = df.iloc[-1].to_dict()
                    return cls(industry_code=code, **row)

        # 无数据时返回全零
        return cls(industry_code=code, date=str(date.today()))


# =========================================
# 案例模型
# =========================================
@dataclass
class Case:
    """案例分析"""
    meta: IndustryMeta
    indicators: IndicatorRow
    content: str = ""          # case.md 完整内容
    insights: str = ""         # 自动生成的洞见

    @property
    def filepath(self) -> Path:
        """案例文件路径"""
        from industry_chain.config import settings
        return (settings.CASES_DIR /
                f"{self.meta.shenwan_code}-{self.meta.shenwan_industry}" /
                f"{self.meta.code}-{self.meta.name}" /
                "case.md")

    def render(self) -> str:
        """渲染 {{ indicator.xxx }} 占位符"""
        content = self.content
        for key, val in asdict(self.indicators).items():
            if key == "industry_code":
                continue
            placeholder = f"{{{{ indicator.{key} }}}}"
            if placeholder in content:
                # 数值格式化
                if isinstance(val, float):
                    if abs(val) >= 1e8:
                        formatted = f"{val:.0f}"
                    elif abs(val) >= 1:
                        formatted = f"{val:.2f}"
                    else:
                        formatted = f"{val:.4f}"
                else:
                    formatted = str(val)
                content = content.replace(placeholder, formatted)
        return content

    def save(self):
        """保存渲染后的案例"""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.filepath.write_text(self.content, encoding="utf-8")

    def __repr__(self) -> str:
        return f"Case({self.meta.code}-{self.meta.name})"
