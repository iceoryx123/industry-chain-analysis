from setuptools import setup, find_packages

setup(
    name="industry-chain-analysis",
    version="10.5.1",
    author="industry-chain team",
    description="产业链结构性分析 — 申万行业分类标准化 + 自动化流水线",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "pandas>=1.3",
        "pyyaml>=5.4",
        "requests>=2.28",
    ],
    extras_require={
        "full": [
            "akshare>=1.10",
            "yfinance>=0.2",
            "pytrends>=4.9",
            "beautifulsoup4>=4.11",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
        "api": [
            "fastapi>=0.100",
            "uvicorn>=0.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "industry-chain=industry_chain.cli:cli",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
