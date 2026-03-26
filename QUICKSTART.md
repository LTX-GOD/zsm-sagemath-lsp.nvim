# 快速开始

## 5 分钟上手指南

### 1. 安装 sage-lsp

```bash
pip install sage-lsp
```

### 2. 验证安装

```bash
sagelsp --sage
```

### 3. 配置 Neovim

在 `~/.config/nvim/lua/plugins/sage.lua` 添加：

```lua
return {
  "zsm/zsm-sagemath-lsp",
  ft = "sage",
  dependencies = { "neovim/nvim-lspconfig" },
  config = function()
    require("zsm-sagemath-lsp").setup()
  end
}
```

### 4. 重启 Neovim

```bash
nvim
```

### 5. 测试

创建 `test.sage`:

```python
R = PolynomialRing(ZZ, 'x')
x = R.gen()
p = x^2 + 2*x + 1
print(p.factor())
```

打开文件，输入 `p.` 应该看到补全提示。

## 完成！

现在你可以享受 SageMath 的智能编辑体验了。
