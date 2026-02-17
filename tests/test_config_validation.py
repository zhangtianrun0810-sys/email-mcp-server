"""Configuration resource and missing-config handling tests."""

import json
import pytest
from pydantic import AnyUrl


class TestConfigStatusResource:
    async def test_configured_returns_host_and_port(self, client_factory, smtp_env):
        async with client_factory() as client:
            result = await client.read_resource(AnyUrl("email://config/status"))
            data = json.loads(result.contents[0].text)
            assert data["configured"] is True
            assert data["host"] == "smtp.example.com"
            assert data["port"] == 587
            assert data["from_email"] == "user@example.com"
            assert "password" not in data

    async def test_unconfigured_returns_false(self, client_factory, unconfigured_env):
        async with client_factory() as client:
            result = await client.read_resource(AnyUrl("email://config/status"))
            data = json.loads(result.contents[0].text)
            assert data["configured"] is False


class TestProvidersResource:
    async def test_returns_provider_list(self, client_factory):
        async with client_factory() as client:
            result = await client.read_resource(AnyUrl("email://providers"))
            providers = json.loads(result.contents[0].text)
            assert isinstance(providers, list)
            assert len(providers) >= 4
            names = {p["name"] for p in providers}
            assert names == {"Gmail", "Outlook", "Yahoo", "iCloud"}


class TestMissingConfigToolError:
    async def test_send_without_config_returns_error(self, client_factory, unconfigured_env):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_simple_email",
                {"to": "x@example.com", "subject": "Test", "body": "Hello"},
            )
            text = result.content[0].text
            assert "SMTP_HOST" in text

    async def test_test_connection_without_config_returns_error(self, client_factory, unconfigured_env):
        async with client_factory() as client:
            result = await client.call_tool("test_smtp_connection", {})
            text = result.content[0].text
            assert "SMTP_HOST" in text
