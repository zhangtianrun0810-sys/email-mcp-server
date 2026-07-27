import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from email_mcp_server.server import create_server

# 1. 正常创建带有所有邮件工具的实例
mcp_obj = create_server()
fastmcp_app = mcp_obj.sse_app()

# 2. 专门对付 sullyOS 的 GET/POST 探测，完美放行并返回握手成功
async def sse_probe_endpoint(request):
    return JSONResponse({"status": "ok", "message": "MCP Server Ready"})

# 3. 混合路由：既有原生的真实工具挂载，又用 Route 优雅接管 /sse 的 POST 探测，彻底消灭 405
app = Starlette(
    routes=[
        Route("/sse", endpoint=sse_probe_endpoint, methods=["GET", "POST", "OPTIONS"]),
        Mount("/", app=fastmcp_app),
    ]
)

# 4. 跨域许可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
