# Email MCP Server

An MCP (Model Context Protocol) server that lets your AI assistant send emails via SMTP.

## Features

- **`send_simple_email`** — Send a quick email (text or HTML); accepts optional `smtp_config`
- **`send_custom_email`** — Full control: CC/BCC, attachments; accepts optional `smtp_config`
- **`test_smtp_connection`** — Verify your SMTP settings before sending; accepts optional `smtp_config`

## Quick Start

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

cd email-mcp-server
uv sync --extra dev
```

Configure SMTP (see next section), then run:

```bash
# stdio transport (for MCP clients)
uv run python -m email_mcp_server.server

# Streamable HTTP transport (port 8000)
uv run python -m email_mcp_server.server --http
```

Run tests:

```bash
uv run pytest
```

## SMTP Configuration

You can configure SMTP credentials in two ways — use one or both.

### Option A: Environment variables

Copy the example and fill in your credentials:

```bash
cp env.example .env
```

```env
# Required
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=your-email@gmail.com

# Optional (defaults shown)
# SMTP_PORT=587
# SMTP_SECURE=false
```

Alternatively, pass them via the client's `env` block (see Client Configuration below).

### Option B: Per-call payload

Pass `smtp_config` directly in any tool call — environment variables are ignored for that call:

```json
{
  "smtp_config": {
    "host": "smtp.gmail.com",
    "port": 587,
    "secure": false,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from_email": "your-email@gmail.com"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `host` | string | SMTP server hostname |
| `port` | integer | SMTP server port (usually `587`) |
| `secure` | boolean | Use SSL/TLS (`false` for STARTTLS) |
| `username` | string | Auth username |
| `password` | string | Auth password |
| `from_email` | string | Sender email address |

## Client Configuration

### Claude Code

```bash
# stdio
claude mcp add email-server -- uv --directory /absolute/path/to/email-mcp-server run python -m email_mcp_server.server

# streamable HTTP (start the server first with --http)
claude mcp add --transport http email-server http://localhost:8000/mcp
```

### JSON-based clients (Claude Desktop, Cursor, VS Code, Windsurf, Zed)

Use the generic example below and adjust the top-level key and config file path for your client:

```json
{
  "<top-level-key>": {
    "email-server": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/email-mcp-server", "run", "python", "-m", "email_mcp_server.server"],
      "env": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_SECURE": "false",
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_FROM": "your-email@gmail.com",
        "SMTP_PASS": "your-app-password"
      }
    }
  }
}
```

| Client | Config file path | Top-level key | Notes |
|--------|-----------------|---------------|-------|
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` | `mcpServers` | Windows: `%APPDATA%\Claude\...` |
| Cursor | `~/.cursor/mcp.json` | `mcpServers` | Or `.cursor/mcp.json` (project) |
| VS Code | `.vscode/mcp.json` | `servers` | Add `"type": "stdio"` inside the server entry |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | `mcpServers` | |
| Zed | `~/.config/zed/settings.json` | `context_servers` | |

### Streamable HTTP (any client)

Start the server with `uv run python -m email_mcp_server.server --http`, then:

| Client | Config |
|--------|--------|
| Claude Code | `claude mcp add --transport http email-server http://localhost:8000/mcp` |
| Claude Desktop | `{ "type": "http", "url": "http://localhost:8000/mcp" }` |
| Cursor | `{ "url": "http://localhost:8000/mcp" }` |
| VS Code | `{ "type": "http", "url": "http://localhost:8000/mcp" }` |
| Windsurf | `{ "serverUrl": "http://localhost:8000/mcp" }` |
| Zed | `{ "url": "http://localhost:8000/mcp" }` |

## Provider Settings

| Provider | Host | Notes |
|----------|------|-------|
| Gmail | `smtp.gmail.com` | Requires [app password](https://myaccount.google.com/apppasswords) with 2FA enabled |
| Outlook | `smtp-mail.outlook.com` | Regular password or app password |
| Yahoo | `smtp.mail.yahoo.com` | Requires app password with 2FA enabled |
| iCloud | `smtp.mail.me.com` | Requires app password with 2FA enabled |

All providers use port `587` with `SMTP_SECURE=false` (STARTTLS).

## License

MIT License
