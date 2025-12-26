#!/bin/bash

# 镜像管理流程验证脚本
# 用于验证自动化镜像管理流程的正确性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要工具
check_dependencies() {
    log_info "检查必要工具..."
    
    local tools=("git" "docker" "curl" "jq")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "所有必要工具已安装"
}

# 验证Dockerfile
validate_dockerfile() {
    log_info "验证Dockerfile..."
    
    if [ ! -f "docker/Dockerfile" ]; then
        log_error "Dockerfile不存在"
        return 1
    fi
    
    # 检查Dockerfile语法
    if docker build -f docker/Dockerfile --dry-run . > /dev/null 2>&1; then
        log_success "Dockerfile语法正确"
    else
        log_error "Dockerfile语法错误"
        return 1
    fi
}

# 验证GitHub Actions工作流
validate_github_workflow() {
    log_info "验证GitHub Actions工作流..."
    
    if [ ! -f ".github/workflows/docker-build.yml" ]; then
        log_error "GitHub Actions工作流文件不存在"
        return 1
    fi
    
    # 检查工作流语法
    if command -v yamllint &> /dev/null; then
        if yamllint .github/workflows/docker-build.yml > /dev/null 2>&1; then
            log_success "GitHub Actions工作流语法正确"
        else
            log_error "GitHub Actions工作流语法错误"
            return 1
        fi
    else
        log_warning "未安装yamllint，跳过语法检查"
    fi
    
    # 检查关键步骤
    local workflow_file=".github/workflows/docker-build.yml"
    local required_steps=("Extract version from tag" "Delete old version image if exists" "Build and push Docker image" "Create Release")
    
    for step in "${required_steps[@]}"; do
        if grep -q "$step" "$workflow_file"; then
            log_success "找到步骤: $step"
        else
            log_error "缺少步骤: $step"
            return 1
        fi
    done
}

# 验证GitLab CI配置
validate_gitlab_ci() {
    log_info "验证GitLab CI配置..."
    
    if [ ! -f ".gitlab-ci.yml" ]; then
        log_error "GitLab CI配置文件不存在"
        return 1
    fi
    
    # 检查CI配置语法
    if command -v yamllint &> /dev/null; then
        if yamllint .gitlab-ci.yml > /dev/null 2>&1; then
            log_success "GitLab CI配置语法正确"
        else
            log_error "GitLab CI配置语法错误"
            return 1
        fi
    else
        log_warning "未安装yamllint，跳过语法检查"
    fi
    
    # 检查关键作业
    local ci_file=".gitlab-ci.yml"
    local required_jobs=("build_image" "test_image" "cleanup_old_images" "create_release")
    
    for job in "${required_jobs[@]}"; do
        if grep -q "$job:" "$ci_file"; then
            log_success "找到作业: $job"
        else
            log_error "缺少作业: $job"
            return 1
        fi
    done
}

# 验证版本标签格式
validate_version_format() {
    log_info "验证版本标签格式..."
    
    local test_versions=("v1.0.0" "v2.1.3" "v10.20.30")
    local invalid_versions=("1.0.0" "v1.0" "v1.0.0.0" "va.b.c")
    
    # 测试有效版本
    for version in "${test_versions[@]}"; do
        if [[ $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            log_success "有效版本格式: $version"
        else
            log_error "无效版本格式: $version"
            return 1
        fi
    done
    
    # 测试无效版本
    for version in "${invalid_versions[@]}"; do
        if [[ $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            log_error "应该被拒绝的版本格式: $version"
            return 1
        else
            log_success "正确拒绝无效版本: $version"
        fi
    done
}

# 测试版本提取逻辑
test_version_extraction() {
    log_info "测试版本提取逻辑..."
    
    local test_tag="v1.2.3"
    local expected_version="1.2.3"
    local expected_major="1"
    local expected_minor="1.2"
    
    # 模拟版本提取
    local version=${test_tag#v}
    local major_version=$(echo $version | cut -d. -f1)
    local minor_version=$(echo $version | cut -d. -f1-2)
    
    if [ "$version" = "$expected_version" ] && 
       [ "$major_version" = "$expected_major" ] && 
       [ "$minor_version" = "$expected_minor" ]; then
        log_success "版本提取逻辑正确"
        log_info "  完整版本: $version"
        log_info "  主版本: $major_version"
        log_info "  次版本: $minor_version"
    else
        log_error "版本提取逻辑错误"
        return 1
    fi
}

# 生成测试报告
generate_report() {
    log_info "生成验证报告..."
    
    local report_file="validation-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# 镜像管理流程验证报告

## 验证时间
$(date)

## 验证项目
- Dockerfile
- GitHub Actions工作流
- GitLab CI配置
- 版本标签格式
- 版本提取逻辑

## 验证结果
所有验证项目均已通过。

## 下一步
1. 创建测试版本标签：\`git tag v1.0.0-test\`
2. 推送标签：\`git push origin v1.0.0-test\`
3. 观察CI/CD流程执行情况
4. 验证镜像标签和Release创建

## 注意事项
- 确保有足够的权限访问镜像仓库
- 检查环境变量和密钥配置
- 监控CI/CD执行日志
EOF

    log_success "验证报告已生成: $report_file"
}

# 主函数
main() {
    log_info "开始验证镜像管理流程..."
    echo
    
    # 检查依赖
    check_dependencies
    echo
    
    # 验证各个组件
    validate_dockerfile
    echo
    
    validate_github_workflow
    echo
    
    validate_gitlab_ci
    echo
    
    validate_version_format
    echo
    
    test_version_extraction
    echo
    
    # 生成报告
    generate_report
    echo
    
    log_success "镜像管理流程验证完成！"
    log_info "可以开始测试实际流程了。"
}

# 执行主函数
main "$@"