"""
数据抓取器
==========

从各类公开数据源抓取行业指标。
所有抓取器统一继承 BaseFetcher，返回统一格式 dict。

当前实现：
- AKSharesFetcher  — akshare（中国 A 股、宏观）
- YFinanceFetcher  — yfinance（全球股票）
- WebFetcher       — 网页抓取（Alexa、新闻）
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import date
from industry_chain.config import settings


# =========================================
# 基础抓取器
# =========================================
class BaseFetcher(ABC):
    """所有抓取器的抽象基类"""

    def __init__(self):
        self.today = str(date.today())

    @abstractmethod
    def fetch(self, industry_code: str, ticker: str = "",
              domain: str = "") -> Dict[str, float]:
        """抓取指标，返回统一格式的 dict

        返回字段：
            market_size_cny_bn, cr4, hhi, gross_margin,
            roe, rd_intensity, network_intensity,
            platform_users_million, average_transaction_value_cny
        """
        ...

    def _empty_result(self) -> Dict[str, float]:
        """返回全等到零"""
        return {
            "market_size_cny_bn": 0.0,
            "cr4": 0.0,
            "hhi": 0.0,
            "gross_margin": 0.0,
            "roe": 0.0,
            "rd_intensity": 0.0,
            "network_intensity": 0.0,
            "platform_users_million": 0.0,
            "average_transaction_value_cny": 0.0,
        }


# =========================================
# akshare 实现
# =========================================
class AKSharesFetcher(BaseFetcher):
    """使用 akshare 抓取中国公司财务数据"""

    def fetch(self, industry_code: str, ticker: str = "",
              domain: str = "") -> Dict[str, float]:
        try:
            import akshare as ak
        except ImportError:
            return self._empty_result()

        if not ticker or not ticker.endswith(("SZ", "SH", "BJ")):
            return self._empty_result()

        try:
            df = ak.stock_financial_abstract_ths(symbol=ticker)
            if df.empty:
                return self._empty_result()

            row = df.iloc[0]
            result = self._empty_result()
            result["gross_margin"] = float(row.get("销售毛利率", 0)) / 100
            result["roe"] = float(row.get("净资产收益率", 0)) / 100
            result["rd_intensity"] = float(row.get("研发投入比例", 0)) / 100
            return result
        except Exception as e:
            if settings.VERBOSE:
                print(f"  ⚠️ akshare {ticker}: {e}")
            return self._empty_result()


# =========================================
# yfinance 实现
# =========================================
class YFinanceFetcher(BaseFetcher):
    """使用 yfinance 抓取全球股票财务数据"""

    def fetch(self, industry_code: str, ticker: str = "",
              domain: str = "") -> Dict[str, float]:
        try:
            import yfinance as yf
        except ImportError:
            return self._empty_result()

        if not ticker:
            return self._empty_result()

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            result = self._empty_result()
            result["gross_margin"] = info.get("grossMargins", 0)
            result["roe"] = info.get("returnOnEquity", 0)
            rd = info.get("researchDevelopment", 0)
            rev = info.get("totalRevenue", 0)
            result["rd_intensity"] = rd / rev if rev else 0
            return result
        except Exception as e:
            if settings.VERBOSE:
                print(f"  ⚠️ yfinance {ticker}: {e}")
            return self._empty_result()


# =========================================
# 网页抓取器
# =========================================
class WebFetcher(BaseFetcher):
    """从公开网页抓取网络效应指标"""

    def fetch(self, industry_code: str, ticker: str = "",
              domain: str = "") -> Dict[str, float]:
        result = self._empty_result()
        if not domain:
            return result

        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

        # Google Trends
        try:
            from pytrends.request import TrendReq
            pytrends = TrendReq(hl='zh-CN', tz=480)
            pytrends.build_payload([domain.split(".")[0]], timeframe='today 12-m')
            trends = pytrends.interest_over_time()
            if not trends.empty:
                result["network_intensity"] = round(
                    trends[domain.split(".")[0]].mean() / 100.0, 3)
        except Exception as e:
            if settings.VERBOSE:
                print(f"  ⚠️ trends {domain}: {e}")

        return result


# =========================================
# 自动选择器
# =========================================
def get_fetcher(ticker: str = "") -> BaseFetcher:
    """根据 ticker 自动选择合适的抓取器"""
    if ticker.endswith(("SZ", "SH", "BJ")):
        return AKSharesFetcher()
    else:
        return YFinanceFetcher()
