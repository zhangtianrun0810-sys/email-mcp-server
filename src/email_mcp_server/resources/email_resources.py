"""MCP resource definitions for email server status and provider info."""

import json

from mcp.server.fastmcp import FastMCP

from email_mcp_server.config import get_smtp_config_safe

PROVIDERS = [
    {
        "name": "Gmail",
        "host": "smtp.gmail.com",
        "port": 587,
        "secure": False,
        "notes": "Requires App Password with 2FA enabled.",
    },
    {
        "name": "Outlook",
        "host": "smtp-mail.outlook.com",
        "port": 587,
        "secure": False,
        "notes": "Use regular password or app password.",
    },
    {
        "name": "Yahoo",
        "host": "smtp.mail.yahoo.com",
        "port": 587,
        "secure": False,
        "notes": "Requires App Password with 2FA enabled.",
    },
    {
        "name": "iCloud",
        "host": "smtp.mail.me.com",
        "port": 587,
        "secure": False,
        "notes": "Requires App Password with 2FA enabled.",
    },
]


def register_resources(mcp: FastMCP) -> None:
    """Register all email resources on the given FastMCP server."""

    @mcp.resource("email://config/status")
    def config_status() -> str:
        """Current SMTP configuration status (never exposes passwords)."""
        config = get_smtp_config_safe()
        if config is None:
            return json.dumps({"configured": False})
        return json.dumps({
            "configured": True,
            "host": config.host,
            "port": config.port,
            "from_email": str(config.from_email),
        })

    @mcp.resource("email://providers")
    def providers() -> str:
        """List of supported email providers with configuration details."""
        return json.dumps(PROVIDERS)
