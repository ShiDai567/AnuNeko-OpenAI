# GitHub Actions 到 GitLab 镜像配置指南

本指南将帮助您配置 GitHub Actions 工作流，实现将代码自动镜像到本地部署的 GitLab 仓库。

## 前提条件

1. 您有 GitHub 仓库的管理员权限
2. 您有 GitLab 实例的管理员权限或至少有创建项目的权限
3. 您的 GitLab 实例支持 API 访问

## 配置步骤

### 1. 在 GitLab 创建访问令牌

1. 登录您的 GitLab 实例
2. 转到 **用户设置** > **访问令牌**
3. 创建一个新的个人访问令牌，具有以下权限：
   - `api` - 访问 API
   - `read_repository` - 读取仓库
   - `write_repository` - 写入仓库

4. 复制生成的令牌（注意：令牌只显示一次，请妥善保存）

### 2. 在 GitHub 设置 Secrets

1. 在您的 GitHub 仓库中，转到 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**，添加以下三个 secrets：

#### a. GITLAB_URL
您的 GitLab 实例的基础 URL（不包含协议）
```
例如: gitlab.example.com
```

#### b. GITLAB_REPO
GitLab 仓库的完整路径（包含用户/组名和项目名）
```
例如: group/project-name 或 username/project-name
```

#### c. GITLAB_TOKEN
在步骤 1 中创建的 GitLab 访问令牌

### 3. 工作流触发条件

工作流将在以下情况下自动触发：
- 推送到 `main` 或 `master` 分支
- 创建针对 `main` 或 `master` 分支的 Pull Request
- 手动触发（workflow_dispatch）

### 4. 工作流功能

- **代码镜像**: 将 GitHub 代码完整推送到 GitLab
- **分支同步**: 支持多分支同步
- **标签同步**: 主分支推送时同步所有标签
- **自动 MR**: 对于非主分支，自动在 GitLab 创建合并请求
- **错误处理**: 包含连接验证和错误提示

## 高级配置

### 自定义目标分支

如果您的主分支不是 `main`，可以修改工作流文件中的目标分支：

```yaml
# 在 .github/workflows/mirror-to-gitlab.yml 中
"target_branch": "your-main-branch-name"
```

### 限制同步的分支

如果您只想同步特定分支，可以修改触发条件：

```yaml
on:
  push:
    branches: [ main, develop, release/* ]  # 只同步这些分支
```

### 排除某些文件或目录

如果您想排除某些文件不被镜像，可以在 GitLab 仓库中创建 `.gitignore` 文件。

## 故障排除

### 常见错误

1. **"无法连接到GitLab仓库"**
   - 检查 `GITLAB_URL` 是否正确（不应包含协议前缀）
   - 确认 `GITLAB_REPO` 路径格式正确
   - 验证 `GITLAB_TOKEN` 是否有效且具有足够权限

2. **"权限被拒绝"**
   - 确认 GitLab 令牌具有 `write_repository` 权限
   - 检查用户是否有目标仓库的写入权限

3. **"合并请求创建失败"**
   - 确认 GitLab 令牌具有 `api` 权限
   - 检查目标分支是否存在

### 调试技巧

1. 查看 GitHub Actions 的详细日志
2. 在本地手动测试 Git 连接：
   ```bash
   git ls-remote https://oauth2:YOUR_TOKEN@gitlab.example.com/group/project.git
   ```

## 安全注意事项

1. **令牌安全**: GitLab 访问令牌具有仓库写入权限，请妥善保管
2. **最小权限原则**: 只授予必要的权限
3. **定期轮换**: 定期更新访问令牌
4. **审计日志**: 定期检查 GitHub Actions 的运行日志

## 替代方案

如果您的 GitLab 实例不支持 OAuth2 或遇到其他问题，可以考虑以下替代方案：

1. **使用 SSH 密钥**: 配置 SSH 密钥进行镜像
2. **使用 GitLab CI/CD**: 在 GitLab 端设置从 GitHub 拉取
3. **使用第三方服务**: 如 GitLab 的 GitHub 集成功能

## 相关资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitLab API 文档](https://docs.gitlab.com/ee/api/)
- [GitLab 个人访问令牌文档](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)