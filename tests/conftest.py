"""Shared test fixtures for the Email MCP Server test suite."""

import pytest
from unittest.mock import AsyncMock, patch

from mcp.shared.memory import create_connected_server_and_client_session

from email_mcp_server.server import create_server


@pytest.fixture
def smtp_env(monkeypatch):
    """Set all required SMTP environment variables."""
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_SECURE", "false")
    monkeypatch.setenv("SMTP_USER", "user@example.com")
    monkeypatch.setenv("SMTP_PASS", "secret")
    monkeypatch.setenv("SMTP_FROM", "user@example.com")


@pytest.fixture
def unconfigured_env(monkeypatch):
    """Ensure no SMTP environment variables are set."""
    for var in ("SMTP_HOST", "SMTP_PORT", "SMTP_SECURE", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_smtp():
    """Return a mocked aiosmtplib.SMTP instance and patch it into connection module."""
    mock_server = AsyncMock()
    mock_server.connect = AsyncMock()
    mock_server.starttls = AsyncMock()
    mock_server.login = AsyncMock()
    mock_server.sendmail = AsyncMock()
    mock_server.quit = AsyncMock()

    with patch("email_mcp_server.services.connection.aiosmtplib.SMTP", return_value=mock_server):
        yield mock_server


@pytest.fixture
def mcp_server():
    """Create a fresh FastMCP server instance for testing."""
    return create_server()


@pytest.fixture
def client_factory(mcp_server):
    """Provide the async context manager for creating MCP client sessions.

    Tests should use it as:
        async with client_factory() as client:
            ...
    This avoids the cancel-scope teardown issue with async yield fixtures.
    """

    def _factory():
        return create_connected_server_and_client_session(mcp_server)

    return _factory
