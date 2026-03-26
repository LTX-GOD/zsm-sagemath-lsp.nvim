-- SageMath LSP 健康检查
local M = {}

function M.check()
  local utils = require("zsm-sagemath-lsp.utils")
  local health = vim.health or require("health")

  health.start("zsm-sagemath-lsp")

  -- 检查 sage-lsp
  if utils.check_sagelsp() then
    health.ok("sage-lsp 已安装")
  else
    health.error("sage-lsp 未安装", {
      "运行: pip install sage-lsp"
    })
  end

  -- 检查 SageMath
  if utils.check_sage() then
    health.ok("SageMath 已安装")
  else
    health.warn("SageMath 未安装", {
      "访问 https://www.sagemath.org/ 安装"
    })
  end

  -- 检查 nvim-lspconfig
  local ok, _ = pcall(require, "lspconfig")
  if ok then
    health.ok("nvim-lspconfig 已安装")
  else
    health.error("nvim-lspconfig 未安装", {
      "安装: https://github.com/neovim/nvim-lspconfig"
    })
  end
end

return M
