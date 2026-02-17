"""Protocol-level tests: tool/resource/prompt discovery and schema validation."""

import pytest


class TestToolDiscovery:
    async def test_lists_all_tools(self, client_factory):
        async with client_factory() as client:
            result = await client.list_tools()
            tool_names = {t.name for t in result.tools}
            assert tool_names == {"send_simple_email", "send_custom_email", "test_smtp_connection"}

    async def test_send_simple_email_schema(self, client_factory):
        async with client_factory() as client:
            result = await client.list_tools()
            tool = next(t for t in result.tools if t.name == "send_simple_email")
            required = tool.inputSchema.get("required", [])
            assert "to" in required
            assert "subject" in required
            assert "body" in required

    async def test_send_custom_email_schema(self, client_factory):
        async with client_factory() as client:
            result = await client.list_tools()
            tool = next(t for t in result.tools if t.name == "send_custom_email")
            required = tool.inputSchema.get("required", [])
            assert "email" in required


class TestResourceDiscovery:
    async def test_lists_all_resources(self, client_factory):
        async with client_factory() as client:
            result = await client.list_resources()
            uris = {str(r.uri) for r in result.resources}
            assert "email://config/status" in uris
            assert "email://providers" in uris


class TestPromptDiscovery:
    async def test_lists_all_prompts(self, client_factory):
        async with client_factory() as client:
            result = await client.list_prompts()
            prompt_names = {p.name for p in result.prompts}
            assert prompt_names == {"compose_email", "compose_reply", "compose_followup"}

    async def test_compose_email_arguments(self, client_factory):
        async with client_factory() as client:
            result = await client.list_prompts()
            prompt = next(p for p in result.prompts if p.name == "compose_email")
            arg_names = {a.name for a in prompt.arguments}
            assert "intent" in arg_names
            assert "recipient_name" in arg_names
            assert "tone" in arg_names
