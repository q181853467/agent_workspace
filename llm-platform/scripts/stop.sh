#!/bin/bash

# 企业级大模型克隆平台停止脚本

set -e

echo "🛑 停止企业级大模型克隆平台..."

# 停止并移除容器
docker-compose down --remove-orphans

echo "✅ 平台已停止"
echo ""
echo "💡 提示:"
echo "   - 重新启动: ./scripts/start.sh"
echo "   - 完全清理: ./scripts/clean.sh"
echo ""
