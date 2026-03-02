# MCP Server Scaffold

Generate Model Context Protocol (MCP) servers from API descriptions.

## Quick Start

```bash
# 1. Parse OpenAPI spec
python scripts/openapi_parser.py api-spec.yaml --output parsed.json

# 2. Generate MCP server
python scripts/mcp_generator.py parsed.json \
  --language typescript \
  --output mcp-server/

# 3. Test tools
python scripts/server_tester.py mcp-server/ --test-all
```

## Python Tools

- `openapi_parser.py` - Parse OpenAPI specs
- `mcp_generator.py` - Generate server code
- `server_tester.py` - Test tools

## References

- `references/mcp-protocol-guide.md` - Protocol overview
- `references/tool-design-patterns.md` - Best practices

## Example

```bash
# Generate GitHub MCP server
python scripts/openapi_parser.py github-api.yaml --output github.json
python scripts/mcp_generator.py github.json --output github-mcp/
cd github-mcp && npm install && npm start
```

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)
