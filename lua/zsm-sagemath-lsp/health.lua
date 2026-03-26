-- SageMath LSP 健康检查
local M = {}

function M.check()
  local utils = require("zsm-sagemath-lsp.utils")
  local health = vim.health or require("health")

  health.start("zsm-sagemath-lsp")

  if utils.check_uv() then
    health.ok("uv 已安装")
  else
    health.error("uv 未安装", {
      "访问 https://docs.astral.sh/uv/ 安装 uv",
    })
  end

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

  if utils.check_runtime_dependencies() then
    health.ok("内置 Python LSP 服务端可启动")
  else
    health.warn("内置 Python LSP 服务端依赖未准备好", {
      "在插件目录执行: uv sync",
      "或首次启动时让 uv 自动创建环境",
    })
  end
end

return M
