#!/usr/bin/env python3
"""
企业级大模型克隆平台功能验证脚本
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "backend"))

def test_backend_import():
    """测试后端模块导入"""
    try:
        from app.core.config import settings
        from app.services.mock_service import MockModelService
        print("✅ 后端模块导入正常")
        return True
    except ImportError as e:
        print(f"❌ 后端模块导入失败: {e}")
        return False

def test_mock_service():
    """测试Mock服务"""
    try:
        from app.services.mock_service import MockModelService
        
        mock_service = MockModelService()
        
        # 测试非流式响应
        response = mock_service.chat_completion({
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        })
        
        print("✅ Mock服务非流式响应正常")
        print(f"   响应内容: {response['choices'][0]['message']['content'][:50]}...")
        
        # 测试流式响应
        stream_response = mock_service.chat_completion({
            "model": "gpt-4o", 
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True
        })
        
        chunks = list(stream_response)
        print(f"✅ Mock服务流式响应正常 (共{len(chunks)}个块)")
        
        return True
    except Exception as e:
        print(f"❌ Mock服务测试失败: {e}")
        return False

def test_database_models():
    """测试数据库模型"""
    try:
        from app.models.user import User
        from app.models.api_key import APIKey
        from app.models.model import Model
        from app.models.access_log import AccessLog
        
        print("✅ 数据库模型导入正常")
        return True
    except ImportError as e:
        print(f"❌ 数据库模型导入失败: {e}")
        return False

def test_api_routes():
    """测试API路由"""
    try:
        from app.api.v1.api import api_router
        
        # 检查路由数量
        routes = api_router.routes
        print(f"✅ API路由配置正常 (共{len(routes)}个路由)")
        return True
    except Exception as e:
        print(f"❌ API路由测试失败: {e}")
        return False

def test_frontend_structure():
    """测试前端文件结构"""
    frontend_path = Path(__file__).parent / "frontend"
    
    required_files = [
        "package.json",
        "vite.config.ts", 
        "src/main.ts",
        "src/App.vue",
        "src/views/Login.vue",
        "src/views/Dashboard.vue",
        "src/store/auth.ts"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (frontend_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 前端文件缺失: {missing_files}")
        return False
    else:
        print("✅ 前端文件结构完整")
        return True

def test_docker_config():
    """测试Docker配置"""
    project_path = Path(__file__).parent
    
    required_files = [
        "docker-compose.yml",
        "backend/Dockerfile", 
        "frontend/Dockerfile"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Docker配置文件缺失: {missing_files}")
        return False
    else:
        print("✅ Docker配置文件完整")
        return True

def main():
    """主验证函数"""
    print("🚀 开始验证企业级大模型克隆平台...")
    print("=" * 50)
    
    tests = [
        ("后端模块导入", test_backend_import),
        ("Mock服务", test_mock_service),
        ("数据库模型", test_database_models),
        ("API路由", test_api_routes),
        ("前端文件结构", test_frontend_structure), 
        ("Docker配置", test_docker_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"📊 验证结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有验证通过！平台已准备就绪。")
        print("\n🚀 启动平台:")
        print("   cd llm-platform")
        print("   docker-compose up -d")
        print("\n🌐 访问地址:")
        print("   前端: http://localhost:3000")
        print("   后端: http://localhost:8000")
        print("   API文档: http://localhost:8000/docs")
        print("\n👤 默认账号: admin / admin123")
    else:
        print(f"⚠️  {total-passed} 项测试失败，需要进一步检查。")
    
    return passed == total

if __name__ == "__main__":
    main()
