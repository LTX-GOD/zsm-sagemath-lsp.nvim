# 常见问题

## LSP 没启动

先检查：

```vim
:checkhealth zsm-sagemath-lsp
:LspInfo
:SageLspInfo
```

再确认：

```bash
uv --version
sage --version
```

## 第一次启动很慢

第一次通常是在让 `uv` 创建环境并安装依赖。建议提前在插件目录执行一次：

```bash
uv sync
```

## ruff 或 ty 没有诊断

默认服务端会尝试使用自身环境里的 `ruff` 和 `ty`。如果你手工改了 `cmd` 或 Python 环境，先确认对应环境里真的有这两个命令。

## 为什么没有默认格式化

`.sage` 不是纯 Python。直接把 Python formatter 套到原始 `.sage` 文件上，会把 Sage 语法破坏掉。当前版本故意不默认开放格式化，等后面补专门的 Sage formatter。

## 跳转定义为什么有时只能跳本地

当前版本优先保证本地符号分析稳定，Sage 内置对象的深层语义跳转还在继续补。

## 如何报告问题

提交 issue 时最好附带：

- Neovim 版本
- `uv --version`
- `sage --version`
- `:checkhealth zsm-sagemath-lsp` 输出
- 最小复现代码
