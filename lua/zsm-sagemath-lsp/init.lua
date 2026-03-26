local M = {}
local utils = require("zsm-sagemath-lsp.utils")

M.config = {
  cmd = nil,
  log_level = "INFO",
  filetypes = { "sage" },
  root_dir = function(fname)
    local util = require("lspconfig.util")
    return util.root_pattern("pyproject.toml", "uv.lock", ".venv", ".git", ".zsm-sagemath-lsp")(fname) or vim.fn.getcwd()
  end,
  init_options = {
    enable_diagnostics = true,
    enable_completion = true,
    enable_hover = true,
    enable_definition = true,
    enable_references = true,
    enable_document_symbols = true,
    enable_jedi = true,
    enable_sage_bridge = true,
    enable_ruff = true,
    enable_ty = true,
    max_completion_items = 120,
    log_level = "INFO",
  },
  load_snippets = true,
  auto_delete_generated_file = false,
  terminal = {
    position = "botright",
    size = 12,
  },
}

local function create_user_commands()
  if M._commands_created then
    return
  end

  vim.api.nvim_create_user_command("SageRun", function()
    local file = vim.api.nvim_buf_get_name(0)
    if file == "" then
      vim.notify("当前缓冲区没有文件路径", vim.log.levels.WARN)
      return
    end

    vim.cmd(M.config.terminal.position .. " " .. M.config.terminal.size .. "split")
    local term_cmd = { "sage", file }
    if M.config.auto_delete_generated_file then
      local generated = file .. ".py"
      local shell_cmd = string.format(
        "sage %s && rm -f %s",
        vim.fn.shellescape(file),
        vim.fn.shellescape(generated)
      )
      vim.fn.termopen(shell_cmd)
    else
      vim.fn.termopen(term_cmd)
    end
  end, {
    desc = "运行当前 SageMath 文件",
  })

  vim.api.nvim_create_user_command("SageLspInfo", function()
    vim.notify(table.concat(utils.get_diagnostics(), "\n"), vim.log.levels.INFO)
  end, {
    desc = "显示 zsm-sagemath-lsp 运行状态",
  })

  vim.api.nvim_create_user_command("SageLspRestart", function()
    vim.cmd("LspRestart")
  end, {
    desc = "重启 SageMath LSP",
  })

  M._commands_created = true
end

function M.setup(opts)
  opts = opts or {}
  M.config = vim.tbl_deep_extend("force", M.config, opts)
  M.config.cmd = M.config.cmd or utils.default_cmd()
  M.config.init_options.log_level = M.config.log_level

  create_user_commands()

  if M.config.load_snippets then
    utils.load_snippets()
  end

  local lspconfig = require("lspconfig")
  local configs = require("lspconfig.configs")

  if not configs.zsm_sagemath_lsp then
    configs.zsm_sagemath_lsp = {
      default_config = {
        cmd = M.config.cmd,
        filetypes = M.config.filetypes,
        root_dir = M.config.root_dir,
        init_options = {
          enable_diagnostics = M.config.init_options.enable_diagnostics,
          enable_completion = M.config.init_options.enable_completion,
          enable_hover = M.config.init_options.enable_hover,
          enable_definition = M.config.init_options.enable_definition,
          enable_references = M.config.init_options.enable_references,
          enable_document_symbols = M.config.init_options.enable_document_symbols,
          enable_jedi = M.config.init_options.enable_jedi,
          enable_sage_bridge = M.config.init_options.enable_sage_bridge,
          enable_ruff = M.config.init_options.enable_ruff,
          enable_ty = M.config.init_options.enable_ty,
          max_completion_items = M.config.init_options.max_completion_items,
          log_level = M.config.init_options.log_level,
        },
      },
    }
  end

  lspconfig.zsm_sagemath_lsp.setup({
    on_attach = M.config.on_attach,
    capabilities = M.config.capabilities,
    cmd = M.config.cmd,
    filetypes = M.config.filetypes,
    root_dir = M.config.root_dir,
    init_options = M.config.init_options,
  })
end

return M
