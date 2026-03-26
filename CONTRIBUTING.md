# 贡献指南

## 提交问题

请尽量附带以下信息：

1. Neovim 版本
2. `uv --version`
3. `sage --version`
4. `:checkhealth zsm-sagemath-lsp`
5. 最小复现 `.sage` 代码
6. `:LspLog` 中的相关日志

## 开发结构

```text
zsm-sagemath-lsp/
├── lua/                   # Neovim 客户端
├── src/zsm_sagemath_lsp/  # Python LSP 服务端
├── syntax/                # Vim 语法高亮
├── ftplugin/              # filetype 配置
├── ftdetect/              # 文件类型识别
└── tests/                 # Python 单元测试
```

## 本地检查

```bash
make test
python3 -m compileall src
```

## 约定

- Python 依赖统一放在 `pyproject.toml`
- Python 相关工作流统一走 `uv`
- 不要把 `.sage` 直接当成普通 Python 做破坏性格式化
