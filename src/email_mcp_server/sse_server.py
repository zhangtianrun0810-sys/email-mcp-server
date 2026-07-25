import os
import uvicorn
from email_mcp_server.server import mcp

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # 使用 FastMCP 内置的 sse app 启动 uvicorn
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
