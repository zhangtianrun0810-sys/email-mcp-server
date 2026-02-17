"""MCP tool definitions for email operations."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from email_mcp_server.config import resolve_smtp_config
from email_mcp_server.models import EmailMessage
from email_mcp_server.services.smtp import send_email, test_connection
from email_mcp_server.exceptions import EmailServerError

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register all email tools on the given FastMCP server."""

    @mcp.tool()
    async def send_simple_email(
        to: str,
        subject: str,
        body: str,
        is_html: bool = False,
        smtp_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Send a simple email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML (default: False)
            smtp_config: Optional SMTP configuration override with:
                - host: SMTP server hostname
                - port: SMTP server port
                - secure: Use SSL/TLS
                - username: Auth username
                - password: Auth password
                - from_email: Sender email address
                Falls back to environment variables if not provided.

        Returns:
            Success message or error message
        """
        try:
            smtp_cfg = resolve_smtp_config(smtp_config)
        except EmailServerError as exc:
            return f"Error: {exc}"

        email_data: Dict[str, Any] = {"to": to, "subject": subject}
        if is_html:
            email_data["html"] = body
        else:
            email_data["text"] = body

        try:
            email_msg = EmailMessage(**email_data)
            return await send_email(smtp_cfg, email_msg)
        except EmailServerError as exc:
            logger.error("Error sending email: %s", exc)
            return f"Error sending email: {exc}"

    @mcp.tool()
    async def send_custom_email(
        email: Dict[str, Any],
        smtp_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Send a custom email with full configuration options.

        Args:
            email: Email message details including:
                - to: Recipient email address(es) (string or list)
                - cc: CC email address(es) (optional, string or list)
                - bcc: BCC email address(es) (optional, string or list)
                - subject: Email subject
                - text: Plain text email body (optional)
                - html: HTML email body (optional)
                - attachments: List of attachments (optional), each with:
                    - path: Local file path to attach (preferred)
                    - content: Base64-encoded file content (alternative to path)
                    - filename: Override filename (auto-derived from path if omitted)
                    - mime_type: MIME type override (optional)
            smtp_config: Optional SMTP configuration override with:
                - host: SMTP server hostname
                - port: SMTP server port
                - secure: Use SSL/TLS
                - username: Auth username
                - password: Auth password
                - from_email: Sender email address

        Returns:
            Success message or error message
        """
        try:
            smtp_cfg = resolve_smtp_config(smtp_config)
        except EmailServerError as exc:
            return f"Error: {exc}"
        except Exception as exc:
            return f"Error: Invalid SMTP configuration: {exc}"

        try:
            email_msg = EmailMessage(**email)
            return await send_email(smtp_cfg, email_msg)
        except EmailServerError as exc:
            logger.error("Error sending custom email: %s", exc)
            return f"Error sending custom email: {exc}"

    @mcp.tool()
    async def test_smtp_connection(
        smtp_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Test SMTP connection.

        Args:
            smtp_config: Optional SMTP configuration override with:
                - host: SMTP server hostname
                - port: SMTP server port
                - secure: Use SSL/TLS
                - username: Auth username
                - password: Auth password
                - from_email: Sender email address
                Falls back to environment variables if not provided.

        Returns:
            Connection test result or error message
        """
        try:
            smtp_cfg = resolve_smtp_config(smtp_config)
            return await test_connection(smtp_cfg)
        except EmailServerError as exc:
            logger.error("Connection test failed: %s", exc)
            return f"Connection test failed: {exc}"
