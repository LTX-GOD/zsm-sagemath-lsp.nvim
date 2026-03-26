# CHANGELOG

## [0.2.0] - 2026-03-26

- 移除对外部 `sage-lsp` 的依赖
- 在仓库内新增自建 Python LSP 服务端
- 服务端运行方式改为 `uv` 项目环境
- 新增 shadow 转换层，用于把常见 `.sage` 语法改写为可静态分析的 Python
- 诊断后端切换为 `ruff + ty + shadow syntax`
- Neovim 侧新增 `:SageRun`、`:SageLspInfo`、`:SageLspRestart`
- 文档、安装说明和健康检查全部改为新的自托管方案
