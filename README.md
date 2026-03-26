# zsm-sagemath-lsp

SageMath support for Neovim with a bundled Python LSP server.

This project no longer depends on `sage-lsp`. The repository now contains:

- A Neovim plugin written in Lua
- A Python LSP server managed by `uv`
- A bundled SageMath symbol index reused for completion and hover

## Features

- Local LSP server started through `uv`
- Completion from local symbols, bundled SageMath symbols, and common member heuristics
- Hover for local definitions and bundled SageMath documentation
- Local definition and reference lookup
- Diagnostics from:
  - Shadow-transformed Sage source syntax checks
  - `ruff`
  - `ty`
- `.sage` and `.sagews` filetype support
- `:SageRun`, `:SageLspInfo`, `:SageLspRestart`
- Optional snippet loading through `LuaSnip`

## Architecture

The server runs in its own Python environment and does not require the whole LSP process to live
inside Sage's Python runtime.

- `uv` manages the server environment
- `ruff` and `ty` run on a shadow Python representation of `.sage` files
- Sage-specific completion and hover data come from the bundled symbol index

This keeps the workflow aligned with `uv + ruff + ty`, which was the main goal of this rewrite.

## Installation

### Requirements

- Neovim >= 0.8
- `uv`
- `sage`
- `nvim-lspconfig`

### Plugin

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

### Prepare the Python environment

Inside the plugin directory:

```bash
uv sync
```

You can also let `uv` create the environment on first start, but running `uv sync` explicitly is
more predictable.

## Configuration

```lua
require("zsm-sagemath-lsp").setup({
  log_level = "INFO",
  init_options = {
    enable_ruff = true,
    enable_ty = true,
    max_completion_items = 200,
  },
  on_attach = function(_, bufnr)
    local opts = { buffer = bufnr, silent = true }
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
    vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
    vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
  end,
})
```

Default server command:

```lua
{ "uv", "run", "--project", "<plugin-root>", "python", "-m", "zsm_sagemath_lsp" }
```

## Commands

- `:SageRun` run current `.sage` file with `sage`
- `:SageLspInfo` show environment diagnostics
- `:SageLspRestart` restart the LSP client

## Health Check

```vim
:checkhealth zsm-sagemath-lsp
```

## Current Limits

- Formatting is intentionally not enabled yet. Reformatting `.sage` while preserving Sage-specific
  syntax needs a dedicated formatter instead of blindly reusing Python formatters.
- Definition and reference lookup are local-first right now.
- The shadow transformation already handles common Sage syntax such as `R.<x> = ...` and
  `f(x) = ...`, but it is not a full Sage parser yet.

## License

GPL-3.0
