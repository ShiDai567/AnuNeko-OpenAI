# 自动化镜像管理流程

本文档描述了AnuNeko OpenAI API兼容服务器的自动化镜像管理流程，包括版本提取、旧镜像清理、多标签发布和自动release发布功能。

## 流程概述

### 1. 版本提取与容器构建

- **版本提取**：根据Git上传的Tag标签（例如v1.0.0）自动提取版本号（例如1.0.0）
- **容器构建**：基于当前的源代码构建新的Docker容器镜像

### 2. 旧镜像清理（版本冲突处理）

- 在推送新镜像之前，系统会检查镜像仓库中是否已存在同名且同版本号的镜像
- 如果存在，先删除旧的同版本镜像，确保当前的版本标签指向的是最新构建的内容

### 3. 多标签发布（Tagging）

- **版本标签**：为新镜像打上对应的版本号标签，即`xxxx:1.0.0`
- **主版本标签**：同时打上主版本标签，即`xxxx:1`
- **次版本标签**：同时打上次版本标签，即`xxxx:1.0`
- **Latest标签**：同时将这个新构建的镜像标记为latest，即`xxxx:latest`

### 4. 自动Release发布

- 当推送版本标签时，自动创建Git Release
- Release包含镜像信息、使用方法、变更日志和系统要求

## GitHub Actions实现

### 触发条件

- 推送到main/master分支
- 推送版本标签（v*）
- 创建Pull Request到main/master分支

### 工作流程

1. **版本提取**：
   ```yaml
   - name: Extract version from tag
     id: version
     if: startsWith(github.ref, 'refs/tags/')
     run: |
       VERSION=${GITHUB_REF#refs/tags/v}
       echo "version=$VERSION" >> $GITHUB_OUTPUT
       echo "major_version=$(echo $VERSION | cut -d. -f1)" >> $GITHUB_OUTPUT
       echo "minor_version=$(echo $VERSION | cut -d. -f1-2)" >> $GITHUB_OUTPUT
   ```

2. **旧镜像清理**：
   ```yaml
   - name: Delete old version image if exists
     if: startsWith(github.ref, 'refs/tags/') && github.event_name != 'pull_request'
     run: |
       # 删除旧的同版本镜像
       if docker manifest inspect $FULL_IMAGE:$VERSION > /dev/null 2>&1; then
         docker buildx imagetools rm $FULL_IMAGE:$VERSION || true
       fi
   ```

3. **多标签发布**：
   ```yaml
   - name: Extract metadata
     id: meta
     uses: docker/metadata-action@v5
     with:
       images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
       tags: |
         type=semver,pattern={{version}}
         type=semver,pattern={{major}}.{{minor}}
         type=semver,pattern={{major}}
         type=raw,value=latest,enable={{is_default_branch}}
   ```

4. **自动Release发布**：
   ```yaml
   - name: Create Release
     uses: softprops/action-gh-release@v1
     with:
       name: Release ${{ steps.version.outputs.version }}
       body: |
         ## AnuNeko OpenAI API 兼容服务器 ${{ steps.version.outputs.version }}
         ...
   ```

## GitLab CI实现

### 触发条件

- 推送到main/master分支
- 推送版本标签（v*）

### 工作流程

1. **版本提取**：
   ```yaml
   .extract_version: &extract_version
     - |
       if [ "$CI_COMMIT_TAG" ]; then
         VERSION=${CI_COMMIT_TAG#v}
         MAJOR_VERSION=$(echo $VERSION | cut -d. -f1)
         MINOR_VERSION=$(echo $VERSION | cut -d. -f1-2)
         ...
       fi
   ```

2. **多标签发布**：
   ```yaml
   script:
     - |
       if [ "$CI_COMMIT_TAG" ]; then
         docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$VERSION
         docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$MAJOR_VERSION
         docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:$MINOR_VERSION
         docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
         ...
       fi
   ```

3. **自动Release发布**：
   ```yaml
   create_release:
     script:
       - |
         if [ "$CI_COMMIT_TAG" ]; then
           # 使用GitLab API创建Release
           curl --request POST \
             --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
             --data "{\"name\":\"Release $VERSION\",\"description\":\"$RELEASE_BODY\",\"tag_name\":\"$CI_COMMIT_TAG\"}" \
             "$CI_API_V4_URL/projects/$CI_PROJECT_ID/releases"
         fi
   ```

## 使用示例

### 1. 创建新版本

```bash
# 创建并推送版本标签
git tag v1.2.3
git push origin v1.2.3
```

这将触发：
- 构建新镜像
- 删除旧的v1.2.3、v1.2和v1标签
- 推送新镜像并打上v1.2.3、v1.2、v1和latest标签
- 创建包含完整信息的Release

### 2. 拉取和使用镜像

```bash
# 拉取特定版本
docker pull ghcr.io/shidai567/anuneko-openai:1.2.3

# 拉取主版本最新版本
docker pull ghcr.io/shidai567/anuneko-openai:1

# 拉取最新版本
docker pull ghcr.io/shidai567/anuneko-openai:latest

# 运行容器
docker run -d -p 8000:8000 \
  -e ANUNEKO_TOKEN=your_token_here \
  ghcr.io/shidai567/anuneko-openai:1.2.3
```

## 镜像标签策略

| 标签类型 | 示例 | 说明 |
|---------|------|------|
| 完整版本 | `1.2.3` | 对应特定的版本标签v1.2.3 |
| 主版本 | `1` | 始终指向最新的1.x.x版本 |
| 次版本 | `1.2` | 始终指向最新的1.2.x版本 |
| 最新 | `latest` | 始终指向最后一次成功构建的版本 |

## 清理策略

- GitHub Actions：自动删除同版本的旧镜像
- GitLab CI：手动触发清理，保留最新的10个镜像

## 注意事项

1. **版本格式**：必须遵循语义化版本控制（SemVer），例如v1.2.3
2. **权限要求**：需要仓库的写入权限和包管理权限
3. **环境变量**：确保设置了必要的环境变量和密钥
4. **镜像仓库**：确保有足够的镜像仓库存储空间

## 故障排除

### 常见问题

1. **镜像推送失败**：检查登录凭据和权限
2. **标签冲突**：确保版本号唯一性
3. **Release创建失败**：检查Git Token权限
4. **清理失败**：检查镜像仓库权限

### 调试步骤

1. 检查CI/CD日志
2. 验证镜像仓库状态
3. 确认标签格式正确
4. 检查权限配置

## 最佳实践

1. **版本控制**：使用语义化版本控制
2. **测试**：在推送标签前确保所有测试通过
3. **文档**：及时更新Release说明
4. **监控**：定期检查镜像仓库使用情况