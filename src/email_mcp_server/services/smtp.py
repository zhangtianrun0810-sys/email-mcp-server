"""MIME message building and email send/test orchestration."""

import logging
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Tuple

from email_mcp_server.models import SMTPConfig, EmailMessage, EmailAttachment
from email_mcp_server.exceptions import AttachmentError, EmailSendError
from email_mcp_server.services.connection import connect_and_authenticate

logger = logging.getLogger(__name__)


def _attach_file(msg: MIMEMultipart, attachment: EmailAttachment) -> None:
    """Decode, detect MIME type, and attach a file to the message."""
    if attachment.path:
        try:
            content = attachment.read_from_path()
        except ValueError as exc:
            raise AttachmentError(str(exc)) from exc
    else:
        try:
            content = attachment.decode_content()
        except ValueError as exc:
            raise AttachmentError(str(exc)) from exc

    if attachment.mime_type:
        maintype, _, subtype = attachment.mime_type.partition("/")
        if not subtype:
            maintype, subtype = "application", "octet-stream"
    else:
        guessed, _ = mimetypes.guess_type(attachment.filename)
        if guessed:
            maintype, subtype = guessed.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"

    part = MIMEBase(maintype, subtype)
    part.set_payload(content)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=attachment.filename)
    msg.attach(part)


def build_mime_message(
    config: SMTPConfig, email_msg: EmailMessage
) -> Tuple[MIMEMultipart, List[str]]:
    """Build a MIME message and return (message, all_recipients)."""
    msg = MIMEMultipart()
    msg["From"] = config.from_email
    msg["Subject"] = email_msg.subject

    recipients: List[str] = []

    # TO
    to_list = email_msg.to if isinstance(email_msg.to, list) else [email_msg.to]
    msg["To"] = ", ".join(str(e) for e in to_list)
    recipients.extend(str(e) for e in to_list)

    # CC
    if email_msg.cc:
        cc_list = email_msg.cc if isinstance(email_msg.cc, list) else [email_msg.cc]
        msg["Cc"] = ", ".join(str(e) for e in cc_list)
        recipients.extend(str(e) for e in cc_list)

    # BCC — added to recipients only, never to headers
    if email_msg.bcc:
        bcc_list = email_msg.bcc if isinstance(email_msg.bcc, list) else [email_msg.bcc]
        recipients.extend(str(e) for e in bcc_list)

    # Body
    if email_msg.text:
        msg.attach(MIMEText(email_msg.text, "plain"))
    if email_msg.html:
        msg.attach(MIMEText(email_msg.html, "html"))

    # Attachments
    if email_msg.attachments:
        for attachment in email_msg.attachments:
            _attach_file(msg, attachment)

    return msg, recipients


async def send_email(config: SMTPConfig, email_msg: EmailMessage) -> str:
    """Build and send an email, returning a success summary."""
    try:
        msg, recipients = build_mime_message(config, email_msg)
    except AttachmentError:
        raise
    except Exception as exc:
        raise EmailSendError(f"Failed to build email message: {exc}") from exc

    try:
        server = await connect_and_authenticate(config)
        try:
            await server.sendmail(
                config.from_email,
                recipients,
                msg.as_string(),
            )
        finally:
            await server.quit()
    except AttachmentError:
        raise
    except Exception as exc:
        raise EmailSendError(f"Failed to send email: {exc}") from exc

    return f"Email sent successfully! Recipients: {', '.join(recipients)}"


async def test_connection(config: SMTPConfig) -> str:
    """Test SMTP connection and authentication, then disconnect."""
    server = await connect_and_authenticate(config)
    await server.quit()
    return (
        f"SMTP connection successful to {config.host}:{config.port} "
        f"with user {config.username}"
    )
