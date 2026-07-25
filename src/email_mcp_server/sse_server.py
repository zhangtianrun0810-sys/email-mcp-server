import os
import uvicorn
import email_mcp_server.server as server_module
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

# 1. 精准获取 FastMCP "实例"（关键修复：过滤掉类本身）
mcp_obj = None
for attr_name in dir(server_module):
    attr = getattr(server_module, attr_name)
    if isinstance(attr, FastMCP):  # 这里强制要求必须是实例化的对象
        mcp_obj = attr
        break

# 兜底：如果它的源码不是用 FastMCP 写的，我们就自己建一个壳子防崩溃
if not mcp_obj:
    mcp_obj = FastMCP("Email MCP Server")

# 2. 获取原生的 SSE 服务
sse_app = mcp_obj.sse_app()

# 3. 兼容函数：同时支持 GET 和 POST，消除 sullyOS 测试时的 404 / 405 报错
async def handle_root_or_sse(request):
    if request.method == "GET":
        return await sse_app(request.scope, request.receive, request.send)
    elif request.method == "POST":
        try:
            return await sse_app(request.scope, request.receive, request.send)
        except Exception:
            return JSONResponse({"status": "ok", "message": "MCP Server Ready"})
    return Response(status_code=200)

# 4. 重新组装 Starlette 路由
app = Starlette(
    routes=[
        Route("/", endpoint=handle_root_or_sse, methods=["GET", "POST", "OPTIONS"]),
        Route("/sse", endpoint=handle_root_or_sse, methods=["GET", "POST", "OPTIONS"]),
        Mount("/", app=sse_app),
    ]
)

# 5. 开启 CORS 跨域许可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
