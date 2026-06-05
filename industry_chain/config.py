"""
配置管理
========

集中管理所有配置，避免硬编码。
优先级：环境变量 > 配置文件 > 默认值

使用示例：
    from industry_chain.config import settings
    print(settings.REPO_ROOT)
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """全局配置

    所有路径默认从环境变量 REPO_ROOT 获取，
    未设置则自动向上查找包含 SKILL.md 的目录。
    """

    def __init__(self):
        # ---------- 路径 ----------
        self.REPO_ROOT: Path = self._find_repo_root()
        self.DATA_DIR = self.REPO_ROOT / "data"
        self.META_DIR = self.DATA_DIR / "meta"
        self.INDICATORS_DIR = self.DATA_DIR / "indicators"
        self.CASES_DIR = self.REPO_ROOT / "cases" / "by-industry"
        self.CONFIG_DIR = self.REPO_ROOT / "config"
        self.OUTPUT_DIR = self.REPO_ROOT / "cases" / "comparison"

        # 确保目录存在
        for d in [self.DATA_DIR, self.META_DIR, self.INDICATORS_DIR,
                  self.CASES_DIR, self.CONFIG_DIR, self.OUTPUT_DIR]:
            d.mkdir(parents=True, exist_ok=True)

        # ---------- 数据源（可被环境变量覆盖） ----------
        self.WIND_API_KEY: Optional[str] = os.getenv("WIND_API_KEY")
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

        # ---------- 运行模式 ----------
        self.VERBOSE: bool = os.getenv("INDUSTRY_CHAIN_VERBOSE", "1") == "1"
        self.OFFLINE: bool = os.getenv("INDUSTRY_CHAIN_OFFLINE", "0") == "1"

    @staticmethod
    def _find_repo_root() -> Path:
        """智能查找仓库根目录"""
        # 1. 环境变量优先
        env_root = os.getenv("REPO_ROOT")
        if env_root:
            return Path(env_root).resolve()

        # 2. 当前目录向上查找 SKILL.md
        cwd = Path.cwd().resolve()
        for parent in [cwd] + list(cwd.parents):
            if (parent / "SKILL.md").exists():
                return parent

        # 3. 回退到当前目录
        return cwd

    def __repr__(self) -> str:
        return f"Settings(REPO_ROOT={self.REPO_ROOT})"


# 全局单例
settings = Settings()
