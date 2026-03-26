local M = {}

M.config = {
  cmd = { "sagelsp" },
  log_level = "INFO",
  filetypes = { "sage" },
  root_dir = function(fname)
    local util = require("lspconfig.util")
    return util.find_git_ancestor(fname) or vim.fn.getcwd()
  end,
  settings = {
    sage = {
      maxNumberOfProblems = 100,
      enableDiagnostics = true,
      enableCompletion = true,
      enableHover = true,
    },
  },
}

function M.setup(opts)
  opts = opts or {}
  M.config = vim.tbl_deep_extend("force", M.config, opts)

  local lspconfig = require("lspconfig")
  local configs = require("lspconfig.configs")

  if not configs.sagelsp then
    configs.sagelsp = {
      default_config = {
        cmd = M.config.cmd,
        filetypes = M.config.filetypes,
        root_dir = M.config.root_dir,
        settings = M.config.settings,
        init_options = {
          logLevel = M.config.log_level,
        },
      },
    }
  end

  lspconfig.sagelsp.setup({
    on_attach = M.config.on_attach,
    capabilities = M.config.capabilities,
    settings = M.config.settings,
  })
end

return M
