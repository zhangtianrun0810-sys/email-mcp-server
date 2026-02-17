"""Pydantic models for SMTP configuration and email messages."""

import base64
from pathlib import Path

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional, Union

MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class SMTPConfig(BaseModel):
    """SMTP server configuration with flattened auth fields."""

    host: str = Field(..., description="SMTP server hostname")
    port: int = Field(587, description="SMTP server port")
    secure: bool = Field(False, description="Use SSL/TLS (True for port 465, False for port 587)")
    username: str = Field(..., description="SMTP authentication username")
    password: str = Field(..., description="SMTP authentication password")
    from_email: EmailStr = Field(..., description="Sender email address")


class EmailAttachment(BaseModel):
    """Email attachment with validation."""

    filename: Optional[str] = Field(None, description="Attachment filename (auto-derived from path if omitted)")
    content: Optional[str] = Field(None, description="Base64-encoded attachment content")
    path: Optional[str] = Field(None, description="Local file path to attach")
    mime_type: Optional[str] = Field(None, description="MIME type override (auto-detected if omitted)")

    @model_validator(mode="after")
    def validate_attachment_source(self) -> "EmailAttachment":
        has_content = self.content is not None
        has_path = self.path is not None

        if has_content and has_path:
            raise ValueError("Provide either 'content' or 'path', not both")
        if not has_content and not has_path:
            raise ValueError("Either 'content' or 'path' must be provided")

        # Auto-derive filename from path when not explicitly set
        if has_path and not self.filename:
            self.filename = Path(self.path).name

        # Ensure filename is always set
        if not self.filename:
            raise ValueError("'filename' is required when using 'content'")

        # Validate content size when content is provided
        if has_content:
            raw_size = len(self.content) * 3 // 4  # approximate decoded size
            if raw_size > MAX_ATTACHMENT_SIZE_BYTES:
                raise ValueError(
                    f"Attachment content exceeds maximum size of "
                    f"{MAX_ATTACHMENT_SIZE_BYTES // (1024 * 1024)} MB"
                )

        return self

    def decode_content(self) -> bytes:
        """Decode base64 content, raising ValueError on invalid data."""
        try:
            return base64.b64decode(self.content, validate=True)
        except Exception as exc:
            raise ValueError(f"Invalid base64 content for '{self.filename}': {exc}") from exc

    def read_from_path(self) -> bytes:
        """Read file bytes from path, raising ValueError on failure."""
        file_path = Path(self.path)
        try:
            data = file_path.read_bytes()
        except FileNotFoundError:
            raise ValueError(f"File not found: {self.path}")
        except PermissionError:
            raise ValueError(f"Permission denied: {self.path}")
        except OSError as exc:
            raise ValueError(f"Cannot read file '{self.path}': {exc}") from exc

        if len(data) > MAX_ATTACHMENT_SIZE_BYTES:
            raise ValueError(
                f"File '{self.path}' exceeds maximum size of "
                f"{MAX_ATTACHMENT_SIZE_BYTES // (1024 * 1024)} MB"
            )
        return data


class EmailMessage(BaseModel):
    """Email message model."""

    to: Union[EmailStr, List[EmailStr]] = Field(..., description="Recipient email address(es)")
    cc: Optional[Union[EmailStr, List[EmailStr]]] = Field(None, description="CC email address(es)")
    bcc: Optional[Union[EmailStr, List[EmailStr]]] = Field(None, description="BCC email address(es)")
    subject: str = Field(..., description="Email subject")
    text: Optional[str] = Field(None, description="Plain text email body")
    html: Optional[str] = Field(None, description="HTML email body")
    attachments: Optional[List[EmailAttachment]] = Field(None, description="Email attachments")
