# MCP Protocol Guide

## Overview

Model Context Protocol (MCP) is an open protocol that standardizes how AI assistants connect to external data sources and tools.

**Key concepts:**
- **Servers** expose tools, resources, and prompts
- **Clients** (like Claude Desktop) connect to servers
- **JSON-RPC** transport layer
- **Stdio** or HTTP transport

## Protocol Basics

MCP uses JSON-RPC 2.0 for all communication. Requests and responses follow this format:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [...]
  }
}
```

## Tools

Tools are functions that clients can call.

**Tool definition:**
```json
{
  "name": "get_user",
  "description": "Get user by ID",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" }
    },
    "required": ["userId"]
  }
}
```

## Error Handling

JSON-RPC error codes:
- `-32700` Parse error
- `-32600` Invalid request
- `-32601` Method not found
- `-32603` Internal error

## Transport

**Stdio:** Server runs as subprocess, communicates via stdin/stdout
**HTTP:** Server runs as web service, communicates via HTTP

Most MCP servers use stdio for simplicity.

## References

- MCP Specification: https://spec.modelcontextprotocol.io
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
