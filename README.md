# mcp-wm

### configure with Claude Desktop
1. open `%APPDATA%\Claude\claude_desktop_config.json` (on Windows)
1. add configuration for this MCP server
```
{
    "mcpServers": {
        "wealth_management": {
            "command": "C:\\Users\\dafi\\.local\\bin\\uv",
            "args": [
                "--directory",
                "C:\\Users\\dafi\\workspace\\mcp-wm",
                "run",
                "wealth_management_server.py"
            ]
        }
    }
}
```