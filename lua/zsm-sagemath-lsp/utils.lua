local M = {}

local function system_ok(command)
  return vim.fn.executable(command) == 1
end

function M.plugin_root()
  local source = debug.getinfo(1, "S").source:sub(2)
  local current = vim.fn.fnamemodify(source, ":p:h")
  return vim.fn.fnamemodify(current .. "/../..", ":p")
end

function M.default_cmd()
  local root = M.plugin_root()
  return {
    "uv",
    "run",
    "--project",
    root,
    "python",
    "-m",
    "zsm_sagemath_lsp",
  }
end

function M.check_uv()
  return system_ok("uv")
end

function M.check_sage()
  return system_ok("sage")
end

function M.check_python()
  return system_ok("python3") or system_ok("python")
end

function M.check_runtime_dependencies()
  if not M.check_uv() then
    return false
  end

  local cmd = vim.deepcopy(M.default_cmd())
  table.insert(cmd, "--version")
  local output = vim.fn.system(cmd)
  return vim.v.shell_error == 0 and output ~= ""
end

function M.load_snippets()
  local ok, vscode_loader = pcall(require, "luasnip.loaders.from_vscode")
  if not ok then
    return false
  end

  vscode_loader.lazy_load({
    paths = { M.plugin_root() .. "/snippets" },
  })
  return true
end

function M.get_diagnostics()
  local diagnostics = {}

  if M.check_uv() then
    table.insert(diagnostics, "✅ uv 可用")
  else
    table.insert(diagnostics, "❌ uv 不可用")
  end

  if M.check_sage() then
    table.insert(diagnostics, "✅ SageMath 可用")
  else
    table.insert(diagnostics, "❌ SageMath 不可用")
  end

  if M.check_runtime_dependencies() then
    table.insert(diagnostics, "✅ 内置 LSP 服务端可启动")
  else
    table.insert(diagnostics, "⚠️ 内置 LSP 服务端未完成依赖安装")
  end

  return diagnostics
end

return M
