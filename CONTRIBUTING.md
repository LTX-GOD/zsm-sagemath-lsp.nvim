# 贡献指南

感谢你对 zsm-sagemath-lsp 的关注！

## 如何贡献

### 报告 Bug

在 GitHub Issues 中提交 bug 报告，请包含：

1. Neovim 版本 (`:version`)
2. sage-lsp 版本 (`sagelsp --version`)
3. 重现步骤
4. 预期行为 vs 实际行为
5. 相关日志 (`:LspLog`)

### 提交功能请求

在 Issues 中描述：

1. 功能描述
2. 使用场景
3. 预期效果

### 提交代码

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开发指南

### 项目结构

```
zsm-sagemath-lsp/
├── lua/                    # Lua 模块
│   └── zsm-sagemath-lsp/
│       ├── init.lua        # 主模块
│       ├── utils.lua       # 工具函数
│       └── health.lua      # 健康检查
├── syntax/                 # 语法高亮
├── ftdetect/               # 文件类型检测
├── ftplugin/               # 文件类型插件
└── doc/                    # 文档
```

### 测试

```bash
# 检查依赖
make test

# 手动测试
nvim test.sage
```

## 代码规范

- Lua 代码使用 2 空格缩进
- Vim script 使用 2 空格缩进
- 提交信息遵循 Conventional Commits

## 许可证

贡献的代码将采用 GPL-3.0 许可证。
