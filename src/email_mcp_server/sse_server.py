import os
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from email_mcp_server.server import create_server

# 1. 直接创建原生带有完整邮件工具的 Server 实例
mcp_obj = create_server()

# 2. 提取原生应用（不加任何多余的路由和外壳，原汁原味）
app = mcp_obj.sse_app()

# 3. 仅添加网页端必备的 CORS 跨域许可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    # proxy_headers=True 完美适配 Render，保障安全校验和正确的路径解析
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
