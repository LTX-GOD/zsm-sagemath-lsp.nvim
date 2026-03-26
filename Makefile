.PHONY: help install test clean

help:
	@echo "zsm-sagemath-lsp Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make install    - 安装插件到 ~/.local/share/nvim/site/pack/plugins/start/"
	@echo "  make test       - 运行测试"
	@echo "  make clean      - 清理临时文件"

install:
	@echo "安装 zsm-sagemath-lsp..."
	@mkdir -p ~/.local/share/nvim/site/pack/plugins/start/
	@cp -r . ~/.local/share/nvim/site/pack/plugins/start/zsm-sagemath-lsp
	@echo "安装完成！"

test:
	@echo "检查 uv..."
	@uv --version || echo "警告: uv 未安装"
	@echo "检查 SageMath..."
	@sage --version || echo "警告: SageMath 未安装"
	@echo "检查 Python 单元测试..."
	@PYTHONPATH=src python3 -m unittest tests/test_shadow.py

clean:
	@echo "清理临时文件..."
	@find . -name "*.swp" -delete
	@find . -name "*~" -delete
	@echo "清理完成！"
