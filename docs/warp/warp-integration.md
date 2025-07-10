# Warp Terminal Integration

This guide summarizes how to use the Agent Memory Server with Warp's Agent Mode.

## Agent Mode Overview

Warp Agent Mode interprets natural language commands and requests approval before executing shell commands. It maintains context, can read command output for self‑correction, and uses rules stored in `~/.warp/` to guide interactions. This collaborative workflow expands terminal capabilities while ensuring the user stays in control.

## MCP Configuration Examples

Warp's preview releases allow connecting external MCP servers that expose tools and resources. Configure servers under **Settings → AI → Manage MCP servers** or via the Warp Drive panel.

### Perplexity Web Search
```bash
# Server Name: Perplexity
# Command: git clone https://github.com/ppl-ai/modelcontextprotocol.git && cd modelcontextprotocol/perplexity-ask && npm install && node server.js
# Environment: PERPLEXITY_API_KEY=your_api_key_here
# Start on launch: ✓
```

### Filesystem Operations
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/one", "/path/two"],
  "start_on_launch": true
}
```

## Workflow Best Practices

- Keep workflows interactive and require user approval for any command execution.
- Store credentials in a secrets manager; avoid plain‑text tokens in configuration files.
- Use version control for workflow definitions and test servers before enabling “start on launch”.

## Security Notes

Warp automatically redacts secrets from terminal output and encrypts stored data with AES‑256. Local processing minimizes cloud exposure. Review server code and only enable trusted endpoints.
