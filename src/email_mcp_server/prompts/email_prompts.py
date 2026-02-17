"""MCP prompt definitions for email composition assistance."""

from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all email prompts on the given FastMCP server."""

    @mcp.prompt()
    def compose_email(
        intent: str,
        recipient_name: str,
        tone: str = "professional",
    ) -> str:
        """Generate an email draft from intent, recipient name, and tone.

        Args:
            intent: What the email should communicate
            recipient_name: Name of the recipient
            tone: Desired tone (professional, casual, formal)
        """
        return (
            f"Compose an email to {recipient_name} with a {tone} tone.\n"
            f"The purpose of this email is: {intent}\n\n"
            "Please provide:\n"
            "1. A clear subject line\n"
            "2. The full email body\n"
            "3. Any suggested follow-up actions"
        )

    @mcp.prompt()
    def compose_reply(
        original_email: str,
        intent: str,
        tone: str = "professional",
    ) -> str:
        """Generate a reply to an existing email.

        Args:
            original_email: The email being replied to
            intent: What the reply should communicate
            tone: Desired tone (professional, casual, formal)
        """
        return (
            f"Write a {tone} reply to the following email:\n\n"
            f"--- Original Email ---\n{original_email}\n---\n\n"
            f"The reply should: {intent}\n\n"
            "Please provide the full reply body."
        )

    @mcp.prompt()
    def compose_followup(
        original_context: str,
        days_since: str = "a few days",
        tone: str = "professional",
    ) -> str:
        """Generate a follow-up email when no response has been received.

        Args:
            original_context: Context of the original message
            days_since: How long since the original was sent
            tone: Desired tone (professional, casual, formal)
        """
        return (
            f"Write a {tone} follow-up email. It has been {days_since} since "
            f"the original message with no response.\n\n"
            f"Original context: {original_context}\n\n"
            "The follow-up should be polite, reference the original message, "
            "and clearly restate the ask or next step."
        )
