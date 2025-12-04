#!/bin/bash

# GitHub Actions 工作流验证脚本
# 用于验证 mirror-to-gitlab.yml 工作流配置是否正确

set -e

echo "🔍 验证 GitHub Actions 工作流配置..."

# 检查工作流文件是否存在
WORKFLOW_FILE=".github/workflows/mirror-to-gitlab.yml"
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ 错误: 工作流文件 $WORKFLOW_FILE 不存在"
    exit 1
fi

echo "✅ 工作流文件存在"

# 检查 YAML 语法
if command -v yamllint &> /dev/null; then
    if yamllint -d relaxed "$WORKFLOW_FILE"; then
        echo "✅ YAML 语法正确"
    else
        echo "❌ YAML 语法错误"
        exit 1
    fi
else
    echo "⚠️  警告: yamllint 未安装，跳过 YAML 语法检查"
    echo "   可以通过 'pip install yamllint' 安装"
fi

# 检查必要的 GitHub Actions 语法元素
echo "🔍 检查工作流语法元素..."

# 检查触发条件
if grep -q "on:" "$WORKFLOW_FILE" && grep -q "push:" "$WORKFLOW_FILE"; then
    echo "✅ 包含 push 触发条件"
else
    echo "❌ 缺少 push 触发条件"
    exit 1
fi

# 检查必要的步骤
REQUIRED_STEPS=("Checkout GitHub repository" "Configure Git" "Add GitLab remote" "Push to GitLab")
for step in "${REQUIRED_STEPS[@]}"; do
    if grep -q "$step" "$WORKFLOW_FILE"; then
        echo "✅ 包含步骤: $step"
    else
        echo "❌ 缺少步骤: $step"
        exit 1
    fi
done

# 检查必要的 secrets
REQUIRED_SECRETS=("GITLAB_URL" "GITLAB_REPO" "GITLAB_TOKEN")
for secret in "${REQUIRED_SECRETS[@]}"; do
    if grep -q "\${{ secrets.$secret }}" "$WORKFLOW_FILE"; then
        echo "✅ 包含 secret: $secret"
    else
        echo "❌ 缺少 secret: $secret"
        exit 1
    fi
done

# 检查错误处理
if grep -q "if \[ \$? -ne 0 \]" "$WORKFLOW_FILE"; then
    echo "✅ 包含错误处理"
else
    echo "⚠️  警告: 缺少错误处理逻辑"
fi

echo ""
echo "🎉 工作流验证完成！"
echo ""
echo "📋 下一步操作："
echo "1. 在 GitHub 仓库设置中添加以下 Secrets："
echo "   - GITLAB_URL: GitLab 实例 URL（如 gitlab.example.com）"
echo "   - GITLAB_REPO: GitLab 仓库路径（如 group/project-name）"
echo "   - GITLAB_TOKEN: GitLab 访问令牌"
echo ""
echo "2. 确保 GitLab 令牌具有以下权限："
echo "   - api"
echo "   - read_repository"
echo "   - write_repository"
echo ""
echo "3. 推送代码到 GitHub 将自动触发镜像流程"
echo ""
echo "📖 详细配置指南请参考: docs/gitlab-mirror-setup.md"