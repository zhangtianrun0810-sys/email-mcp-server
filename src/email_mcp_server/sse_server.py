import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

# 1. 直接导入原作者暴露的创建函数
from email_mcp_server.server import create_server

# 2. 调用函数，真正生成带有所有邮件工具的 FastMCP 实例！
mcp_obj = create_server()

# 获取 FastMCP 内置的 SSE 应用
sse_app = mcp_obj.sse_app()

# 3. 兼容路由：防止 sullyOS 连通性测试时报 404 或 405
async def handle_root(request):
    if request.method == "POST":
        return JSONResponse({"status": "ok", "message": "FastMCP Email Server Ready"})
    return await sse_app(request.scope, request.receive, request.send)

routes = [
    Route("/", endpoint=handle_root, methods=["GET", "POST", "OPTIONS"]),
    Route("/sse", endpoint=handle_root, methods=["GET", "POST", "OPTIONS"]),
    Mount("/", app=sse_app),
]

# 4. 组装应用并开启跨域 (CORS)
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
