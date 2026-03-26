# zsm-sagemath-lsp

SageMath Language Server Protocol (LSP) plugin for Neovim

English | [简体中文](README.zh.md)

## Features

- ✅ **Code Completion** - Intelligent completion for SageMath functions and objects
- ✅ **Go to Definition** - Jump to function/class definitions
- ✅ **Hover Documentation** - Display function signatures and docs
- ✅ **Diagnostics** - Real-time error checking (pyflakes + pycodestyle)
- ✅ **Code Formatting** - Auto-format code (autopep8)
- ✅ **Find References** - Find symbol references
- ✅ **Code Folding** - Support code block folding
- ✅ **Syntax Highlighting** - SageMath-specific syntax highlighting

## Installation

### Prerequisites

- Neovim >= 0.8.0
- Python >= 3.10
- SageMath installed
- [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig)

### 1. Install sage-lsp

```bash
pip install sage-lsp
```

### 2. Install Plugin

#### Using lazy.nvim (Recommended)

```lua
{
  "zsm/zsm-sagemath-lsp",
  ft = "sage",
  dependencies = {
    "neovim/nvim-lspconfig",
  },
  config = function()
    require("zsm-sagemath-lsp").setup()
  end
}
```

#### Using packer.nvim

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

## Configuration

### Basic Setup

```lua
require("zsm-sagemath-lsp").setup()
```

### Custom Configuration

```lua
require("zsm-sagemath-lsp").setup({
  cmd = { "sagelsp", "-l", "DEBUG" },
  on_attach = function(client, bufnr)
    local opts = { noremap=true, silent=true, buffer=bufnr }
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
    vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
  end,
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
})
```

## Usage

Create a `test.sage` file and the LSP will start automatically.

## Related Projects

- [sage-lsp](https://github.com/SeanDictionary/sage-lsp) - SageMath LSP server
- [sagemath-vscode-enhanced](https://github.com/Lov3/sagemath-vscode-enhanced) - VSCode extension

## License

GPL-3.0
