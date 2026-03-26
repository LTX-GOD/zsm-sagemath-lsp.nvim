# 常见问题 (FAQ)

## 安装问题

### Q: LSP 服务器无法启动？

**A:** 检查以下几点：

1. 确认 sage-lsp 已安装：
   ```bash
   which sagelsp
   sagelsp --sage
   ```

2. 查看 LSP 日志：
   ```vim
   :LspLog
   ```

3. 检查健康状态：
   ```vim
   :checkhealth zsm-sagemath-lsp
   ```

### Q: 提示 "sage-lsp not found"？

**A:** 安装 sage-lsp：
```bash
pip install sage-lsp
```

确保安装路径在 PATH 中。

## 功能问题

### Q: 代码补全不工作？

**A:** 确保：
1. LSP 服务器已启动 (`:LspInfo`)
2. 文件类型正确 (`:set filetype?` 应显示 `sage`)
3. SageMath 10.8+ 已安装（需要 .pyi 文件）

### Q: 跳转到定义不工作？

**A:** 某些 SageMath 内置函数可能无法跳转，这是正常的。对于用户定义的函数应该可以正常工作。

### Q: 如何自定义按键绑定？

**A:** 在 `on_attach` 中设置：
```lua
require("zsm-sagemath-lsp").setup({
  on_attach = function(client, bufnr)
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, {buffer=bufnr})
  end,
})
```

## 性能问题

### Q: LSP 响应很慢？

**A:** 尝试：
1. 减少诊断数量
2. 禁用某些功能
3. 升级到最新版本的 sage-lsp

## 其他问题

### Q: 支持哪些 SageMath 版本？

**A:** 建议使用 SageMath 10.8+，其他版本功能可能受限。

### Q: 如何报告 bug？

**A:** 在 GitHub Issues 提交，包含：
- Neovim 版本
- sage-lsp 版本
- 重现步骤
- 错误日志
