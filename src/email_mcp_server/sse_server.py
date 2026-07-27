import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from email_mcp_server.server import create_server

# 1. 生成带有真实工具的实例
mcp_obj = create_server()
fastmcp_app = mcp_obj.sse_app()

# 2. 探针兜底：专门应付 sullyOS 点击“测试连接”时的 Ping 测试，防止报 404/405
async def ping(request):
    return JSONResponse({"status": "ok", "message": "MCP Ready"})

# 3. 路由分发（绝对不篡改真实请求，全权交还给原生 FastMCP）
routes = [
    Route("/", endpoint=ping, methods=["GET", "POST"]),
    Route("/sse", endpoint=ping, methods=["POST"]),
    Mount("/", app=fastmcp_app)
]

app = Starlette(routes=routes)

# 4. 开启跨域许可 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    # proxy_headers=True 完美解决之前的 421 报错
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
