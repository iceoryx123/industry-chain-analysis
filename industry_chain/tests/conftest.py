"""
pytest 配置
"""

import os
import sys

# 确保测试能在仓库根目录运行
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, repo_root)

# 设置环境变量
os.environ.setdefault("REPO_ROOT", repo_root)
