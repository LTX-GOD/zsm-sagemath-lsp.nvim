-- SageMath LSP 辅助函数
local M = {}

-- 检查 sage-lsp 是否安装
function M.check_sagelsp()
  local handle = io.popen("which sagelsp 2>/dev/null")
  local result = handle:read("*a")
  handle:close()
  return result ~= ""
end

-- 检查 SageMath 是否安装
function M.check_sage()
  local handle = io.popen("sage --version 2>/dev/null")
  local result = handle:read("*a")
  handle:close()
  return result ~= ""
end

-- 获取诊断信息
function M.get_diagnostics()
  local diagnostics = {}

  if not M.check_sagelsp() then
    table.insert(diagnostics, "❌ sage-lsp 未安装")
  else
    table.insert(diagnostics, "✅ sage-lsp 已安装")
  end

  if not M.check_sage() then
    table.insert(diagnostics, "❌ SageMath 未安装")
  else
    table.insert(diagnostics, "✅ SageMath 已安装")
  end

  return diagnostics
end

return M
