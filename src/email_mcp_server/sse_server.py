import os
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount

from email_mcp_server.server import create_server
mcp_obj = create_server()
fastmcp_app = mcp_obj.sse_app()

async def rewrite_middleware(scope, receive, send):
    if scope["type"] == "http":
        if scope["method"] == "POST":
            scope["path"] = "/messages/"
        elif scope["method"] == "GET" and scope["path"] == "/":
            scope["path"] = "/sse"
    await fastmcp_app(scope, receive, send)

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
    # 关键修复：开启代理头信任，彻底消灭 421 错误
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
