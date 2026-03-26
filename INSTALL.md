# 安装指南

## 1. 前置条件

- Neovim >= 0.8
- `uv`
- `sage`
- `nvim-lspconfig`

## 2. 安装插件

```lua
{
  "zsm/zsm-sagemath-lsp",
  ft = { "sage" },
  dependencies = {
    "neovim/nvim-lspconfig",
  },
  config = function()
    require("zsm-sagemath-lsp").setup()
  end,
}
```

## 3. 初始化 Python 依赖

进入插件目录执行：

```bash
uv sync
```

## 4. 验证

```vim
:checkhealth zsm-sagemath-lsp
```

查看状态：

```vim
:SageLspInfo
```

## 5. 运行 Sage 文件

```vim
:SageRun
```
