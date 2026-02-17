"""Email sending use-case tests (simple, HTML, CC/BCC, attachments)."""

import base64
import os
import pytest


class TestSendSimpleEmail:
    async def test_send_text_email(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_simple_email",
                {"to": "recipient@example.com", "subject": "Test", "body": "Hello"},
            )
            text = result.content[0].text
            assert "successfully" in text.lower()
            mock_smtp.sendmail.assert_called_once()
            call_args = mock_smtp.sendmail.call_args
            assert "recipient@example.com" in call_args[0][1]

    async def test_send_html_email(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_simple_email",
                {
                    "to": "recipient@example.com",
                    "subject": "HTML Test",
                    "body": "<h1>Hello</h1>",
                    "is_html": True,
                },
            )
            text = result.content[0].text
            assert "successfully" in text.lower()
            raw_msg = mock_smtp.sendmail.call_args[0][2]
            assert "<h1>Hello</h1>" in raw_msg


class TestSendCustomEmail:
    async def test_send_with_cc_bcc(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "main@example.com",
                        "cc": "cc@example.com",
                        "bcc": "bcc@example.com",
                        "subject": "CC/BCC Test",
                        "text": "Testing CC and BCC",
                    },
                },
            )
            text = result.content[0].text
            assert "successfully" in text.lower()

            call_args = mock_smtp.sendmail.call_args
            recipients = call_args[0][1]
            assert "main@example.com" in recipients
            assert "cc@example.com" in recipients
            assert "bcc@example.com" in recipients

            # BCC should NOT appear in the message headers
            raw_msg = call_args[0][2]
            assert "Bcc" not in raw_msg

    async def test_send_with_attachment(self, client_factory, smtp_env, mock_smtp):
        async with client_factory() as client:
            content = base64.b64encode(b"file contents here").decode()
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "recipient@example.com",
                        "subject": "Attachment Test",
                        "text": "See attached",
                        "attachments": [
                            {"filename": "test.txt", "content": content},
                        ],
                    },
                },
            )
            text = result.content[0].text
            assert "successfully" in text.lower()
            raw_msg = mock_smtp.sendmail.call_args[0][2]
            assert 'filename="test.txt"' in raw_msg

    async def test_send_with_path_attachment(self, client_factory, smtp_env, mock_smtp, tmp_path):
        tmp_file = tmp_path / "report.pdf"
        tmp_file.write_bytes(b"%PDF-1.4 fake pdf content")

        async with client_factory() as client:
            result = await client.call_tool(
                "send_custom_email",
                {
                    "email": {
                        "to": "recipient@example.com",
                        "subject": "Path Attachment Test",
                        "text": "See attached",
                        "attachments": [
                            {"path": str(tmp_file)},
                        ],
                    },
                },
            )
            text = result.content[0].text
            assert "successfully" in text.lower()
            raw_msg = mock_smtp.sendmail.call_args[0][2]
            assert 'filename="report.pdf"' in raw_msg
