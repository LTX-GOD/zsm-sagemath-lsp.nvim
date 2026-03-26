-- 示例配置文件

-- 基础配置
require("zsm-sagemath-lsp").setup()

-- 自定义配置
require("zsm-sagemath-lsp").setup({
  cmd = { "sagelsp", "-l", "DEBUG" },
  on_attach = function(client, bufnr)
    -- 自定义按键绑定
    local opts = { noremap=true, silent=true, buffer=bufnr }
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
    vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
    vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
    vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
    vim.keymap.set('n', '<leader>f', vim.lsp.buf.format, opts)
  end,
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
})
