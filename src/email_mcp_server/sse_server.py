import os
import uvicorn
import email_mcp_server.server as server_module

# 自动寻找模块里的 FastMCP 实例（不管叫 mcp、app 还是 server）
mcp_obj = getattr(server_module, "mcp", None) or getattr(server_module, "app", None) or getattr(server_module, "server", None)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app = mcp_obj.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
