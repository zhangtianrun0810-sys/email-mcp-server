"""Edge-case and error scenario tests."""

import pytest
from unittest.mock import AsyncMock, patch
from pydantic import AnyUrl

import aiosmtplib


class TestInvalidAttachment:
    async def test_bad_base64_returns_error(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "x@example.com",
                        "subject": "Bad Attach",
                        "text": "See attached",
                        "attachments": [
                            {"filename": "bad.txt", "content": "not!valid!base64!!!"},
                        ],
                    },
                },
            )
            text = result.content[0].text
            assert "error" in text.lower()


    async def test_nonexistent_file_path_returns_error(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "x@example.com",
                        "subject": "Bad Path",
                        "text": "See attached",
                        "attachments": [
                            {"path": "/tmp/nonexistent_file_12345.txt"},
                        ],
                    },
                },
            )
            text = result.content[0].text
            assert "error" in text.lower()

    async def test_both_content_and_path_returns_error(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "x@example.com",
                        "subject": "Both Fields",
                        "text": "See attached",
                        "attachments": [
                            {
                                "filename": "test.txt",
                                "content": "aGVsbG8=",
                                "path": "/tmp/test.txt",
                            },
                        ],
                    },
                },
            )
            text = result.content[0].text
            assert "error" in text.lower()


class TestSMTPFailures:
    async def test_connection_refused(self, client_factory, smtp_env):
        with patch(
            "email_mcp_server.services.connection.aiosmtplib.SMTP",
        ) as mock_cls:
            mock_server = AsyncMock()
            mock_server.connect = AsyncMock(side_effect=OSError("Connection refused"))
            mock_cls.return_value = mock_server

            async with client_factory() as client:
                result = await client.call_tool(
                    "send_simple_email",
                    {"to": "x@example.com", "subject": "Test", "body": "Hello"},
                )
                text = result.content[0].text
                assert "error" in text.lower() or "failed" in text.lower()

    async def test_auth_failure(self, client_factory, smtp_env):
        with patch(
            "email_mcp_server.services.connection.aiosmtplib.SMTP",
        ) as mock_cls:
            mock_server = AsyncMock()
            mock_server.connect = AsyncMock()
            mock_server.starttls = AsyncMock()
            mock_server.login = AsyncMock(
                side_effect=aiosmtplib.SMTPAuthenticationError(535, "Auth failed")
            )
            mock_cls.return_value = mock_server

            async with client_factory() as client:
                result = await client.call_tool("test_smtp_connection", {})
                text = result.content[0].text
                assert "failed" in text.lower()


class TestPromptRendering:
    async def test_compose_email_includes_args(self, client_factory):
        async with client_factory() as client:
            result = await client.get_prompt(
                "compose_email",
                {"intent": "schedule meeting", "recipient_name": "Alice", "tone": "casual"},
            )
            text = result.messages[0].content.text
            assert "Alice" in text
            assert "casual" in text
            assert "schedule meeting" in text

    async def test_compose_reply_includes_original(self, client_factory):
        async with client_factory() as client:
            result = await client.get_prompt(
                "compose_reply",
                {
                    "original_email": "Please send the report.",
                    "intent": "confirm receipt",
                    "tone": "formal",
                },
            )
            text = result.messages[0].content.text
            assert "Please send the report." in text
            assert "formal" in text

    async def test_compose_followup_includes_context(self, client_factory):
        async with client_factory() as client:
            result = await client.get_prompt(
                "compose_followup",
                {"original_context": "Budget approval request", "days_since": "5 days"},
            )
            text = result.messages[0].content.text
            assert "Budget approval request" in text
            assert "5 days" in text
