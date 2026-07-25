import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

import email_mcp_server.server as server_module

# 1. 动态寻找真正包含工具的实例
mcp_obj = None
server_type = None

# 尝试 A：寻找 FastMCP 实例
try:
    from mcp.server.fastmcp import FastMCP
    for attr_name in dir(server_module):
        attr = getattr(server_module, attr_name)
        if isinstance(attr, FastMCP):
            mcp_obj = attr
            server_type = "fastmcp"
            break
except ImportError:
    pass

# 尝试 B：寻找底层标准 Server 实例（email_mcp_server 用的就是这个）
if not mcp_obj:
    try:
        from mcp.server import Server
        for attr_name in dir(server_module):
            attr = getattr(server_module, attr_name)
            if isinstance(attr, Server):
                mcp_obj = attr
                server_type = "standard"
                break
    except ImportError:
        pass

if not mcp_obj:
    raise RuntimeError("在源码中未能找到任何附带工具的 MCP Server 实例！")

# 2. 根据不同的 Server 类型，桥接到 Starlette Web 服务
routes = []

if server_type == "fastmcp":
    sse_app = mcp_obj.sse_app()
    async def handle_root(request):
        if request.method == "POST":
            return JSONResponse({"status": "ok", "message": "FastMCP Ready"})
        return await sse_app(request.scope, request.receive, request.send)

    routes = [
        Route("/", endpoint=handle_root, methods=["GET", "POST", "OPTIONS"]),
        Route("/sse", endpoint=handle_root, methods=["GET", "POST", "OPTIONS"]),
        Mount("/", app=sse_app),
    ]

elif server_type == "standard":
    from mcp.server.sse import SseServerTransport
    
    # 建立标准的 SSE 消息通道
    sse = SseServerTransport("/messages")

    async def handle_sse(request):
        # 兼容 sullyOS 初始测试时的探测
        if request.method == "POST":
            return JSONResponse({"status": "ok", "message": "Standard MCP Ready"})
        async with sse.connect_sse(request.scope, request.receive, request.send) as streams:
            await mcp_obj.run(streams[0], streams[1], mcp_obj.create_initialization_options())

    async def handle_messages(request):
        await sse.handle_post_message(request.scope, request.receive, request.send)

    routes = [
        Route("/", endpoint=handle_sse, methods=["GET", "POST", "OPTIONS"]),
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST", "OPTIONS"]),
        Route("/messages", endpoint=handle_messages, methods=["POST", "OPTIONS"]),
    ]

# 3. 开启跨域允许 (CORS) - sullyOS 网页端必备
app = Starlette(routes=routes)
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
