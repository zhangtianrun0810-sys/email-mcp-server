"""FastMCP server factory and entry point."""

import sys
import logging

from mcp.server.fastmcp import FastMCP

from email_mcp_server.tools import register_tools
from email_mcp_server.resources import register_resources
from email_mcp_server.prompts import register_prompts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_server(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    """Create and configure a FastMCP email server instance."""
    mcp = FastMCP("email-server", host=host, port=port)
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp


def main() -> None:
    """Entry point for running the server from the command line."""
    if "--http" in sys.argv:
        logger.info("Starting Email MCP Server (Streamable HTTP on port 8000)...")
        server = create_server(host="0.0.0.0", port=8000)
        server.run(transport="streamable-http")
    else:
        logger.info("Starting Email MCP Server (stdio)...")
        server = create_server()
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
