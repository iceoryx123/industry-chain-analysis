# ============================================================================
# 🏭 产业链结构性分析 — Makefile
# 使用便利性：一键完成所有常用操作
# ============================================================================

# 环境检测
SHELL := /bin/bash
PYTHON := python3
PIP := pip3
GIT := git

# 颜色输出（阅读友好）
GREEN := \033[0;32m
YELLOW := \033[1;33m
CYAN := \033[0;36m
NC := \033[0m

# 默认目标
.DEFAULT_GOAL := help

.PHONY: help install run test clean lint release

# ────────────────────────────────────────────────────────────────────
# 📖 帮助（默认）
# ────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(CYAN)🏭 产业链结构性分析 — 常用命令$(NC)"
	@echo ""
	@echo "  $(GREEN)安装与环境$(NC)"
	@echo "    make install        安装本包 + 全部依赖"
	@echo "    make install-dev    安装开发依赖（含测试）"
	@echo ""
	@echo "  $(GREEN)完整流水线$(NC)"
	@echo "    make all            完整链条（抓取→渲染→洞见→仪表盘）"
	@echo "    make fetch          仅数据抓取"
	@echo "    make etl            仅指标合并"
	@echo "    make render         仅占位符渲染"
	@echo "    make insights       仅洞见生成"
	@echo "    make dashboard      仅对比仪表盘"
	@echo ""
	@echo "  $(GREEN)查看与分析$(NC)"
	@echo "    make list           列出所有行业案例"
	@echo "    make show CODE=xxx  查看单个案例（如 CODE=150000-01）"
	@echo "    make insight CODE=xxx  生成单个洞见"
	@echo "    make validate       数据质量检查"
	@echo ""
	@echo "  $(GREEN)开发维护$(NC)"
	@echo "    make test           运行测试"
	@echo "    make lint           代码风格检查"
	@echo "    make clean          清理缓存"
	@echo "    make release TAG=v11.0.0  发布新版本"
	@echo ""
	@echo "  $(GREEN)快速开始$(NC)"
	@echo "    make install && make all"
	@echo ""

# ────────────────────────────────────────────────────────────────────
# 🔧 安装
# ────────────────────────────────────────────────────────────────────
install:
	@echo "$(YELLOW)▶ 安装 industry-chain-analysis$(NC)"
	$(PIP) install -e ".[full,api]"
	@echo "$(GREEN)✅ 安装完成！运行 'industry-chain --help' 查看用法$(NC)"

install-dev:
	@echo "$(YELLOW)▶ 安装开发依赖$(NC)"
	$(PIP) install -e ".[full,api,test]"
	$(PIP) install black pylint
	@echo "$(GREEN)✅ 开发环境就绪$(NC)"

# ────────────────────────────────────────────────────────────────────
# 🚀 流水线
# ────────────────────────────────────────────────────────────────────
all:
	@echo "$(YELLOW)▶ 完整流水线$(NC)"
	industry-chain run all

fetch:
	@echo "$(YELLOW)▶ 数据抓取$(NC)"
	industry-chain run fetch

etl:
	@echo "$(YELLOW)▶ 指标合并$(NC)"
	industry-chain run etl

render:
	@echo "$(YELLOW)▶ 案例渲染$(NC)"
	industry-chain run render

insights:
	@echo "$(YELLOW)▶ 洞见生成$(NC)"
	industry-chain run insights

dashboard:
	@echo "$(YELLOW)▶ 对比仪表盘$(NC)"
	industry-chain run dashboard

# ────────────────────────────────────────────────────────────────────
# 🔍 查看
# ────────────────────────────────────────────────────────────────────
list:
	industry-chain list

show:
ifndef CODE
	@echo "$(YELLOW)用法: make show CODE=150000-01$(NC)"
else
	industry-chain show $(CODE)
endif

insight:
ifndef CODE
	@echo "$(YELLOW)用法: make insight CODE=150000-01$(NC)"
else
	industry-chain insight $(CODE)
endif

validate:
	industry-chain validate

# ────────────────────────────────────────────────────────────────────
# 🔬 开发
# ────────────────────────────────────────────────────────────────────
test:
	@echo "$(YELLOW)▶ 运行测试$(NC)"
	cd industry_chain && python -m pytest tests/ -v --tb=short

lint:
	@echo "$(YELLOW)▶ 代码风格检查$(NC)"
	black --check industry_chain/ scripts/

clean:
	@echo "$(YELLOW)▶ 清理缓存$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf *.egg-info
	@echo "$(GREEN)✅ 已清理$(NC)"

release:
ifndef TAG
	@echo "$(YELLOW)用法: make release TAG=v11.0.0$(NC)"
else
	@echo "$(YELLOW)▶ 发布 $(TAG)$(NC)"
	$(GIT) tag -a $(TAG) -m "Release $(TAG)"
	$(GIT) push origin $(TAG)
	@echo "$(GREEN)✅ 已推送标签 $(TAG)，GitHub Actions 将自动创建 Release$(NC)"
endif
