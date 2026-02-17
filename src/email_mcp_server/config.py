"""Environment-based SMTP configuration loader."""

import os
import logging
from typing import Any

from dotenv import load_dotenv

from email_mcp_server.models import SMTPConfig
from email_mcp_server.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = ["SMTP_HOST", "SMTP_USER", "SMTP_FROM", "SMTP_PASS"]


def load_smtp_config() -> SMTPConfig:
    """Load SMTP configuration from environment variables.

    Raises ConfigurationError with a message listing all missing variables.
    """
    load_dotenv()

    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in your .env file or MCP client configuration."
        )

    port = int(os.getenv("SMTP_PORT", "587"))
    secure = os.getenv("SMTP_SECURE", "false").lower() == "true"

    return SMTPConfig(
        host=os.environ["SMTP_HOST"],
        port=port,
        secure=secure,
        username=os.environ["SMTP_USER"],
        password=os.environ["SMTP_PASS"],
        from_email=os.environ["SMTP_FROM"],
    )


def resolve_smtp_config(smtp_override: dict[str, Any] | None = None) -> SMTPConfig:
    """Return SMTPConfig from payload override, or fall back to environment."""
    if smtp_override:
        return SMTPConfig(**smtp_override)
    return load_smtp_config()


def get_smtp_config_safe() -> SMTPConfig | None:
    """Load SMTP config, returning None instead of raising on missing vars."""
    try:
        return load_smtp_config()
    except ConfigurationError:
        return None
