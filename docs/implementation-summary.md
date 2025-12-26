# 自动化镜像管理流程实现总结

## 概述

本文档总结了为AnuNeko OpenAI API兼容服务器实现的完整自动化镜像管理流程。

## 已实现的功能

### 1. 版本提取与容器构建

- **GitHub Actions**：从Git标签自动提取版本号（如v1.0.0 → 1.0.0）
- **GitLab CI**：同样支持从标签提取版本号
- **容器构建**：基于当前源代码自动构建Docker镜像

### 2. 旧镜像清理（版本冲突处理）

- **GitHub Actions**：在推送新镜像前检查并删除同版本号的旧镜像
- **GitLab CI**：实现相同的清理逻辑
- **清理策略**：支持完整版本、主版本和次版本标签的清理

### 3. 多标签发布（Tagging）

实现了四种标签策略：

| 标签类型 | 示例 | 说明 |
|---------|------|------|
| 完整版本 | `1.0.0` | 对应特定的版本标签v1.0.0 |
| 主版本 | `1` | 始终指向最新的1.x.x版本 |
| 次版本 | `1.0` | 始终指向最新的1.0.x版本 |
| 最新 | `latest` | 始终指向最后一次成功构建的版本 |

### 4. 自动Release发布

- **GitHub Actions**：使用`softprops/action-gh-release@v1`自动创建Release
- **GitLab CI**：使用GitLab API创建Release
- **Release内容**：包含镜像信息、使用方法、变更日志和系统要求

## 文件修改

### 1. GitHub Actions工作流

**文件**：`.github/workflows/docker-build.yml`

**主要修改**：
- 添加版本提取步骤
- 实现旧镜像清理逻辑
- 配置多标签发布
- 添加自动Release创建
- 修复SBOM生成问题
- **分离成多个job**：提高构建效率和可维护性
  - `build`：构建和推送镜像
  - `sbom`：生成软件物料清单
  - `release`：创建Git Release
- **修复SBOM镜像引用**：使用正确的镜像digest格式

### 2. GitLab CI配置

**文件**：`.gitlab-ci.yml`

**主要修改**：
- 添加版本提取函数
- 实现多标签发布
- 添加清理旧镜像作业
- 创建Release作业
- 修复artifacts问题

### 3. Docker配置

**文件**：`docker/Dockerfile` 和 `docker/docker-compose.yml`

**主要修改**：
- 修复Dockerfile中的路径问题
- 更新docker-compose.yml的构建上下文

### 4. 文档和脚本

**新增文件**：
- `docs/automated-image-management.md` - 详细的自动化镜像管理文档
- `scripts/validate-image-management.sh` - 验证脚本
- `docs/implementation-summary.md` - 本实现总结

**修改文件**：
- `README.md` - 添加Docker部署和镜像管理说明

## 使用方法

### 1. 创建新版本

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0
```

### 2. 拉取镜像

```bash
# 拉取特定版本
docker pull ghcr.io/shidai567/anuneko-openai:1.0.0

# 拉取主版本最新
docker pull ghcr.io/shidai567/anuneko-openai:1

# 拉取次版本最新
docker pull ghcr.io/shidai567/anuneko-openai:1.0

# 拉取最新版本
docker pull ghcr.io/shidai567/anuneko-openai:latest
```

### 3. 验证流程

```bash
# 运行验证脚本
./scripts/validate-image-management.sh
```

## 技术细节

### 版本提取逻辑

```bash
# 从标签中提取版本号
VERSION=${CI_COMMIT_TAG#v}  # v1.0.0 -> 1.0.0
MAJOR_VERSION=$(echo $VERSION | cut -d. -f1)  # 1.0.0 -> 1
MINOR_VERSION=$(echo $VERSION | cut -d. -f1-2)  # 1.0.0 -> 1.0
```

### 镜像标签策略

```bash
# 标签推送时
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$VERSION      # 完整版本
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$MAJOR_VERSION  # 主版本
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$MINOR_VERSION # 次版本
docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest        # 最新版本
```

### 旧镜像清理

```bash
# 检查并删除旧的同版本镜像
if docker manifest inspect $IMAGE_NAME:$VERSION > /dev/null 2>&1; then
  docker buildx imagetools rm $IMAGE_NAME:$VERSION || true
fi
```

## 故障排除

### 常见问题

1. **GitLab CI 404错误**
   - 确保镜像仓库路径正确
   - 检查登录凭据
   - 验证权限设置

2. **版本提取失败**
   - 确保标签格式正确（v1.0.0）
   - 检查CI_COMMIT_TAG变量

3. **Release创建失败**
   - 检查API Token权限
   - 验证API端点URL

### 调试步骤

1. 检查CI/CD日志
2. 运行验证脚本
3. 手动测试版本提取
4. 验证镜像仓库状态

## 最佳实践

1. **版本控制**：使用语义化版本控制
2. **测试**：在推送标签前确保所有测试通过
3. **文档**：及时更新Release说明
4. **监控**：定期检查镜像仓库使用情况

## 未来改进

1. **自动化测试**：在发布前自动运行完整测试套件
2. **多架构支持**：支持ARM64等多架构镜像
3. **安全扫描**：集成容器安全扫描
4. **性能监控**：添加镜像大小和启动时间监控

## 总结

我们已经成功实现了一个完整的自动化镜像管理流程，包括：

- ✅ 版本提取与容器构建
- ✅ 旧镜像清理（版本冲突处理）
- ✅ 多标签发布（版本标签和latest标签）
- ✅ 自动Release发布
- ✅ GitHub Actions和GitLab CI双平台支持
- ✅ 完整的文档和验证脚本

这个流程大大简化了版本管理，确保了镜像标签的一致性，并提供了完整的发布自动化支持。