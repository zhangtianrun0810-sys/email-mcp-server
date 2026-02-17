"""Shared SMTP connection primitive with TLS fallback."""

import ssl
import logging
from typing import List, Tuple

import aiosmtplib

from email_mcp_server.models import SMTPConfig
from email_mcp_server.exceptions import SMTPConnectionError

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 30


def get_connection_methods(config: SMTPConfig) -> List[Tuple[str, bool, bool]]:
    """Return ordered list of (name, use_tls, start_tls) to try.

    Never includes plain (unencrypted) connections.
    """
    if config.port == 465 or config.secure:
        return [("implicit TLS", True, False)]
    return [
        ("STARTTLS", False, True),
        ("implicit TLS fallback", True, False),
    ]


async def connect_and_authenticate(config: SMTPConfig) -> aiosmtplib.SMTP:
    """Connect and authenticate to SMTP server, trying TLS methods in order.

    Returns an authenticated SMTP client on success.
    Raises SMTPConnectionError if all methods fail.
    """
    methods = get_connection_methods(config)
    last_error: Exception | None = None

    for method_name, use_tls, start_tls in methods:
        try:
            logger.info("Trying connection method: %s", method_name)
            tls_context = ssl.create_default_context() if use_tls else None

            server = aiosmtplib.SMTP(
                hostname=config.host,
                port=config.port,
                use_tls=use_tls,
                tls_context=tls_context,
                timeout=SMTP_TIMEOUT_SECONDS,
            )

            await server.connect()

            if start_tls:
                await server.starttls(tls_context=ssl.create_default_context())

            await server.login(config.username, config.password)
            logger.info("Connected successfully using %s", method_name)
            return server

        except Exception as exc:
            last_error = exc
            logger.warning("Connection method '%s' failed: %s", method_name, exc)
            continue

    raise SMTPConnectionError(
        f"All connection methods failed for {config.host}:{config.port}. "
        f"Last error: {last_error}"
    )
