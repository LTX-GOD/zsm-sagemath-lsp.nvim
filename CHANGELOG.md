# CHANGELOG

## [1.0.0] - 2026-03-26

### 新增功能

#### LSP 集成
- ✅ 完整的 LSP 服务器集成（基于 sage-lsp）
- ✅ 代码补全（支持 SageMath 特定符号）
- ✅ 跳转到定义
- ✅ 悬停文档显示
- ✅ 查找引用
- ✅ 代码诊断（pyflakes + pycodestyle）
- ✅ 代码格式化（autopep8）
- ✅ 代码折叠

#### 语法支持
- ✅ SageMath 特定语法高亮
- ✅ 环和域关键字（ZZ, QQ, RR, CC, GF 等）
- ✅ 核心函数（var, solve, factor 等）
- ✅ 特殊操作符（^^, **, .. 等）
- ✅ 环生成器语法（R.<x,y> = ...）

#### 文件类型
- ✅ .sage 文件自动检测
- ✅ .sagews 文件支持
- ✅ Python 兼容的缩进和注释

#### 工具和辅助
- ✅ 健康检查命令（:checkhealth zsm-sagemath-lsp）
- ✅ 代码片段支持
- ✅ 工具函数模块
- ✅ 详细文档和示例

### 依赖
- sage-lsp >= 1.0.0
- neovim >= 0.8.0
- nvim-lspconfig
- SageMath（推荐 10.8+）

### 文档
- 📖 中英文 README
- 📖 安装指南
- 📖 快速开始指南
- 📖 FAQ 文档
- 📖 贡献指南
- 📖 配置示例
