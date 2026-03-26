# 快速开始

## 1. 安装插件

```lua
return {
  "zsm/zsm-sagemath-lsp",
  ft = "sage",
  dependencies = { "neovim/nvim-lspconfig" },
  config = function()
    require("zsm-sagemath-lsp").setup()
  end,
}
```

## 2. 准备环境

进入插件目录执行：

```bash
uv sync
```

确认系统里有 `sage`：

```bash
sage --version
```

## 3. 启动 Neovim

```bash
nvim test.sage
```

## 4. 检查状态

```vim
:checkhealth zsm-sagemath-lsp
:SageLspInfo
```

## 5. 试一段代码

```python
R.<x> = PolynomialRing(ZZ)
f(t) = t^2 + 1
M = matrix(QQ, [[1, 2], [3, 4]])
M.det()
```

现在应当可以得到基本补全、悬停、诊断和本地定义跳转。
