"""Email MCP Server - An MCP server for sending emails via SMTP."""

__version__ = "2.0.0"

from email_mcp_server.server import create_server

__all__ = ["create_server", "__version__"]
