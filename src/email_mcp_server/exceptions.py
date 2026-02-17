"""Custom exception hierarchy for the Email MCP Server."""


class EmailServerError(Exception):
    """Base exception for all email server errors."""


class ConfigurationError(EmailServerError):
    """Raised when environment variables or configuration is missing/invalid."""


class AttachmentError(EmailServerError):
    """Raised for attachment issues (bad base64, file too large)."""


class SMTPConnectionError(EmailServerError):
    """Raised when all SMTP connection methods fail."""


class EmailSendError(EmailServerError):
    """Raised for email send failures not covered by other exceptions."""
