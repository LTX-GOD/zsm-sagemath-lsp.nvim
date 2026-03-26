-- 完整配置示例

-- 1. 基础配置
require("zsm-sagemath-lsp").setup()

-- 2. 带自定义按键的配置
require("zsm-sagemath-lsp").setup({
  on_attach = function(client, bufnr)
    local opts = { noremap=true, silent=true, buffer=bufnr }

    -- 导航
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, opts)
    vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, opts)
    vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)

    -- 文档
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
    vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, opts)

    -- 编辑
    vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
    vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
    vim.keymap.set('n', '<leader>f', function()
      vim.lsp.buf.format({ async = true })
    end, opts)

    -- 诊断
    vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, opts)
    vim.keymap.set('n', ']d', vim.diagnostic.goto_next, opts)
    vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, opts)
  end,
})

-- 3. 带补全的配置
local capabilities = require('cmp_nvim_lsp').default_capabilities()
require("zsm-sagemath-lsp").setup({
  capabilities = capabilities,
})

-- 4. 调试模式
require("zsm-sagemath-lsp").setup({
  log_level = "DEBUG",
  init_options = {
    enable_ruff = true,
    enable_ty = true,
  },
})
