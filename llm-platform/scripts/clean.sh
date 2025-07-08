#!/bin/bash

# 企业级大模型克隆平台清理脚本

set -e

echo "🧹 清理企业级大模型克隆平台..."
echo "⚠️  这将删除所有数据和镜像，请确认操作！"
read -p "确定要继续吗？(y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 操作已取消"
    exit 1
fi

# 停止并移除容器
echo "🛑 停止并移除容器..."
docker-compose down --remove-orphans --volumes

# 移除镜像
echo "🗑️  移除相关镜像..."
docker image rm llm-platform_backend llm-platform_frontend 2>/dev/null || true

# 清理未使用的资源
echo "🧹 清理未使用的Docker资源..."
docker system prune -f

# 清理数据目录
echo "📁 清理数据目录..."
rm -rf backend/data/* backend/logs/* 2>/dev/null || true

echo "✅ 清理完成"
echo ""
echo "💡 提示:"
echo "   - 重新启动: ./scripts/start.sh"
echo ""
