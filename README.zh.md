# zsm-sagemath-lsp

这是一个面向 Neovim 的 SageMath 插件，现在自带 Python LSP 服务端，不再依赖外部 `sage-lsp`。

仓库里同时包含两部分：

- Lua 写的 Neovim 客户端
- 用 `uv` 管理的 Python LSP 服务端

## 目标

原来的 `sage-lsp` 更偏向传统 Python 生态，和 `uv + ruff + ty` 的工作流不够贴合。这个项目现在的方向是：

- LSP 服务端由你自己维护
- 依赖与运行统一走 `uv`
- 诊断优先接 `ruff` 和 `ty`
- 不要求整个 LSP 进程运行在 Sage 自带 Python 里

## 当前功能

- 通过 `uv` 启动内置 LSP 服务端
- 本地符号补全
- 内置 SageMath 符号索引补全与悬停文档
- 常见对象方法的启发式补全
- 本地定义跳转与引用查找
- 诊断来源：
  - shadow 转换后的语法检查
  - `ruff`
  - `ty`
- `.sage` / `.sagews` 文件类型检测
- `:SageRun`、`:SageLspInfo`、`:SageLspRestart`
- 检测到 `LuaSnip` 时自动加载 snippets

## 架构

现在的核心思路是把 `.sage` 文件先转换成一份 shadow Python 代码，再把这份代码喂给静态工具：

- `ruff` 和 `ty` 跑在 shadow 代码上
- `.sage` 里的 `R.<x> = ...`、`f(x) = ...` 等常见语法会先被改写
- SageMath 的补全/文档基于仓库内置的符号索引

这套设计的重点不是复刻整个 Sage parser，而是先把 `uv + ruff + ty + Neovim` 这条链路打通。

## 安装

### 依赖

- Neovim >= 0.8
- `uv`
- `sage`
- `nvim-lspconfig`

### 插件配置

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

### 初始化 Python 环境

在插件目录执行：

```bash
uv sync
```

也可以首次启动时让 `uv` 自动建环境，但显式执行一次 `uv sync` 更稳。

## 配置示例

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

默认服务端启动命令：

```lua
{ "uv", "run", "--project", "<plugin-root>", "python", "-m", "zsm_sagemath_lsp" }
```

## 命令

- `:SageRun` 用 `sage` 执行当前文件
- `:SageLspInfo` 查看环境和服务端状态
- `:SageLspRestart` 重启 LSP

## 健康检查

```vim
:checkhealth zsm-sagemath-lsp
```

## 当前限制

- 还没有默认开启格式化，因为 `.sage` 的格式化不能直接粗暴套 Python formatter。
- 定义跳转和引用查找当前是“本地优先”。
- shadow 转换已经支持常见 Sage 语法，但还不是完整 Sage parser。

## 许可证

GPL-3.0
