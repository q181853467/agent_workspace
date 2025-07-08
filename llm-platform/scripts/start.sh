#!/bin/bash

# 企业级大模型克隆平台启动脚本

set -e

echo "🚀 启动企业级大模型克隆平台..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装。请先安装 Docker。"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装。请先安装 Docker Compose。"
    exit 1
fi

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  警告: 端口 $port 已被占用"
        return 1
    fi
    return 0
}

echo "🔍 检查端口可用性..."
check_port 8000 || echo "   后端端口 8000 被占用，可能会冲突"
check_port 3000 || echo "   前端端口 3000 被占用，可能会冲突"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/data
mkdir -p backend/logs
mkdir -p frontend/dist

# 停止已运行的容器（如果存在）
echo "🛑 停止已运行的服务..."
docker-compose down --remove-orphans 2>/dev/null || true

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 初始化演示数据
echo "📊 初始化演示数据..."
docker-compose exec backend python -c "
import sys
sys.path.append('/app')
from scripts.init_demo_data import init_demo_data
init_demo_data()
print('演示数据初始化完成')
" 2>/dev/null || echo "   演示数据初始化失败，请稍后手动初始化"

# 检查服务状态
echo "🔍 检查服务状态..."
sleep 5

# 检查后端
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ 后端服务运行正常 (http://localhost:8000)"
else
    echo "❌ 后端服务启动失败"
fi

# 检查前端
if curl -f http://localhost:3000/health >/dev/null 2>&1; then
    echo "✅ 前端服务运行正常 (http://localhost:3000)"
else
    echo "❌ 前端服务启动失败"
fi

echo ""
echo "🎉 企业级大模型克隆平台启动完成！"
echo ""
echo "📖 访问方式:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo "👤 默认管理员账号:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📚 更多信息请查看 README.md 文档"
echo ""
echo "🛑 停止服务: ./scripts/stop.sh"
echo "📋 查看日志: docker-compose logs -f"
echo ""
