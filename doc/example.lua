-- 示例配置文件

-- 基础配置
require("zsm-sagemath-lsp").setup()

-- 自定义配置
require("zsm-sagemath-lsp").setup({
  log_level = "DEBUG",
  init_options = {
    enable_ruff = true,
    enable_ty = true,
    max_completion_items = 200,
  },
  on_attach = function(client, bufnr)
    -- 自定义按键绑定
    local opts = { noremap=true, silent=true, buffer=bufnr }
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
    vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
    vim.keymap.set('n', '<leader>sr', '<cmd>SageRun<cr>', opts)
  end,
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
})
