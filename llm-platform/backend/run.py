#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的后端启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # 启动开发服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # 在生产环境中关闭reload
        log_level="info"
    )
