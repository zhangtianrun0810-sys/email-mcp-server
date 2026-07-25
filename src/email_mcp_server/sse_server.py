import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

# 1. 导入原作者的创建函数，生成带有真实工具的实例
from email_mcp_server.server import create_server
mcp_obj = create_server()
fastmcp_app = mcp_obj.sse_app()

# 2. 核心修复：智能路由重写器（拦截并纠正 sullyOS 的发件地址）
async def rewrite_middleware(scope, receive, send):
    if scope["type"] == "http":
        # 把所有的 POST 请求，强制导向 FastMCP 的真实数据处理接口
        if scope["method"] == "POST":
            scope["path"] = "/messages/"
        # 如果直接访问根目录，强制导向 /sse 建立订阅
        elif scope["method"] == "GET" and scope["path"] == "/":
            scope["path"] = "/sse"
            
    # 把修正好路径的真实请求，原封不动交给真正的 FastMCP 处理
    await fastmcp_app(scope, receive, send)

# 3. 组装应用并开启无死角跨域许可 (CORS)
app = Starlette(routes=[Mount("/", app=rewrite_middleware)])
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
