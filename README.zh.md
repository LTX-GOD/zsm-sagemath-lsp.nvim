# zsm-sagemath-lsp

适用于 Neovim 的 SageMath 语言服务器协议 (LSP) 插件

[English](README.md) | 简体中文

## 简介

这是一个为 Neovim 编辑器提供 SageMath 支持的 LSP 插件，基于 [sage-lsp](https://github.com/SeanDictionary/sage-lsp) 项目。

## 功能特性

- ✅ **代码补全** - 智能补全 SageMath 函数和对象
- ✅ **跳转定义** - 快速跳转到函数/类定义
- ✅ **悬停文档** - 显示函数签名和文档
- ✅ **代码诊断** - 实时错误检查 (pyflakes + pycodestyle)
- ✅ **代码格式化** - 自动格式化代码 (autopep8)
- ✅ **引用查找** - 查找符号引用
- ✅ **代码折叠** - 支持代码块折叠
- ✅ **语法高亮** - SageMath 特定语法高亮

## 安装

### 前置要求

- Neovim >= 0.8.0
- Python >= 3.10
- SageMath 已安装
- [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig)

### 1. 安装 sage-lsp

```bash
pip install sage-lsp
```

### 2. 安装插件

#### 使用 lazy.nvim (推荐)

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

## 配置

### 基础配置

```lua
require("zsm-sagemath-lsp").setup()
```

### 自定义配置

```lua
require("zsm-sagemath-lsp").setup({
  cmd = { "sagelsp", "-l", "DEBUG" },  -- 自定义命令
  on_attach = function(client, bufnr)
    -- 按键绑定
    local opts = { noremap=true, silent=true, buffer=bufnr }
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
    vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
    vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
    vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
    vim.keymap.set('n', '<leader>f', function()
      vim.lsp.buf.format({ async = true })
    end, opts)
  end,
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
})
```

## 使用示例

创建 `test.sage` 文件：

```python
# 定义多项式环
R = PolynomialRing(ZZ, 'x')
x = R.gen()

# 多项式运算
p = x^2 + 2*x + 1
print(p.factor())  # 输入 p. 后会显示补全列表

# 矩阵运算
M = matrix(QQ, [[1, 2], [3, 4]])
print(M.det())  # 悬停在 det 上显示文档
```

打开文件后，LSP 会自动启动并提供智能提示。

## 快捷键

默认 LSP 快捷键（需要在 `on_attach` 中配置）：

- `gd` - 跳转到定义
- `K` - 显示悬停文档
- `gr` - 查找引用
- `<leader>rn` - 重命名符号
- `<leader>ca` - 代码操作
- `<leader>f` - 格式化代码

## 故障排除

### LSP 未启动

检查 LSP 状态：
```vim
:LspInfo
```

查看日志：
```vim
:LspLog
```

### sage-lsp 未找到

验证安装：
```bash
which sagelsp
sagelsp --sage
```

### SageMath 未检测到

检查 SageMath：
```bash
sage --version
```

## 项目结构

```
zsm-sagemath-lsp/
├── doc/                    # 文档
│   ├── example.lua         # 配置示例
│   └── zsm-sagemath-lsp.txt # Vim 帮助文档
├── ftdetect/               # 文件类型检测
│   └── sage.vim
├── ftplugin/               # 文件类型插件
│   └── sage.lua
├── lua/                    # Lua 模块
│   └── zsm-sagemath-lsp/
│       └── init.lua        # 主模块
├── syntax/                 # 语法高亮
│   └── sage.vim
├── CHANGELOG.md
├── INSTALL.md
├── LICENSE
└── README.md
```

## 相关项目

- [sage-lsp](https://github.com/SeanDictionary/sage-lsp) - SageMath LSP 服务器
- [sagemath-vscode-enhanced](https://github.com/Lov3/sagemath-vscode-enhanced) - VSCode 扩展
- [sage-code](https://github.com/SeanDictionary/sage-code) - VSCode 语法支持

## 许可证

GPL-3.0 License

## 贡献

欢迎提交 Issue 和 Pull Request！
