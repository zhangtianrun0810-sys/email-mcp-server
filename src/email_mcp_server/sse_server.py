import os
import uvicorn
from mcp.server.fastmcp import FastMCP
from email_mcp_server.server import main

# 1. 创建一个自带 SSE 支持的 FastMCP 实例
mcp = FastMCP("Email MCP Server")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    # 2. 启动内置的 SSE Web 服务器
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
