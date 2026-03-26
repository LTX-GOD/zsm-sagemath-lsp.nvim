# 安装指南

## 前置要求

1. Neovim >= 0.8.0
2. Python >= 3.10
3. SageMath 安装
4. sage-lsp 包

## 安装步骤

### 1. 安装 sage-lsp

```bash
pip install sage-lsp
```

### 2. 验证安装

```bash
sagelsp --sage
```

应该显示 SageMath 版本信息。

### 3. 安装 Neovim 插件

#### 使用 lazy.nvim

在 `~/.config/nvim/lua/plugins/sage.lua` 中添加：

```lua
return {
  "zsm/zsm-sagemath-lsp",
  ft = "sage",
  dependencies = {
    "neovim/nvim-lspconfig",
  },
  config = function()
    require("zsm-sagemath-lsp").setup({
      on_attach = function(client, bufnr)
        local opts = { buffer = bufnr }
        vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
        vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
        vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
      end,
    })
  end
}
```

#### 使用 packer.nvim

```lua
use {
  "zsm/zsm-sagemath-lsp",
  ft = "sage",
  requires = { "neovim/nvim-lspconfig" },
  config = function()
    require("zsm-sagemath-lsp").setup()
  end
}
```

### 4. 测试

创建测试文件 `test.sage`:

```python
# test.sage
R = PolynomialRing(ZZ, 'x')
x = R.gen()
p = x^2 + 2*x + 1
print(p.factor())
```

打开文件，LSP 应该自动启动并提供补全、诊断等功能。

## 故障排除

### LSP 未启动

检查 LSP 日志：
```vim
:LspLog
```

### sage-lsp 未找到

确保 sage-lsp 在 PATH 中：
```bash
which sagelsp
```

### SageMath 未检测到

检查 SageMath 安装：
```bash
sage --version
```
