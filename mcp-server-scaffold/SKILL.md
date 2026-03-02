---
name: mcp-server-scaffold
description: Generate Model Context Protocol (MCP) tool servers from API descriptions, enabling AI assistants to connect to external services
license: MIT
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: ai-tooling
  domain: mcp-protocol
  updated: 2026-03-01
  python-tools: openapi_parser.py, mcp_generator.py, server_tester.py
  tech-stack: python, typescript, mcp, openapi, json-rpc
---

# mcp-server-scaffold

## Trigger

Use this skill when building MCP servers to connect AI assistants to APIs, databases, or custom tools.

**Trigger phrases:**
- "Create MCP server for [API]"
- "Generate MCP tool server"
- "Build MCP connector for [service]"
- "Scaffold MCP server from OpenAPI"
- "Connect Claude to [API]"

## Overview

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to tools and data sources. This skill generates production-ready MCP servers from API descriptions (OpenAPI/Swagger), custom tool specs, or database schemas.

**What gets generated:**
- MCP server implementation (TypeScript or Python)
- Tool definitions with JSON schemas
- Error handling and validation
- Authentication/authorization logic
- Testing utilities
- Docker deployment config

**Not for:** Building APIs themselves - this assumes you have an API and want to expose it via MCP.

## How to Use

### Quick Start
1. **Parse API description:**
   ```bash
   python scripts/openapi_parser.py api-spec.yaml --output parsed.json
   ```

2. **Generate MCP server:**
   ```bash
   python scripts/mcp_generator.py parsed.json \
     --language typescript \
     --output mcp-server/
   ```

3. **Test the server:**
   ```bash
   python scripts/server_tester.py mcp-server/ --test-all
   ```

### Python Tools
- `scripts/openapi_parser.py` — Parse OpenAPI/Swagger specs and extract tool definitions
- `scripts/mcp_generator.py` — Generate MCP server code (TypeScript or Python)
- `scripts/server_tester.py` — Test MCP server tools and validate responses

### Reference Docs
- `references/mcp-protocol-guide.md` — MCP protocol overview and concepts
- `references/tool-design-patterns.md` — Best practices for MCP tool design

### Templates & Assets
- `assets/openapi-example.yaml` — Sample OpenAPI spec
- `assets/tool-definition-template.json` — Manual tool definition format
- `assets/docker-compose.yaml` — Deployment configuration

## Architecture Decisions

### Why OpenAPI as Input

OpenAPI specs already describe:
- Endpoints and methods
- Request/response schemas
- Authentication requirements
- Error responses

**Conversion:** OpenAPI endpoint → MCP tool
```yaml
# OpenAPI
/users/{id}:
  get:
    summary: Get user by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: string
```

**→ MCP Tool:**
```typescript
{
  name: "get_user",
  description: "Get user by ID",
  inputSchema: {
    type: "object",
    properties: {
      id: { type: "string" }
    },
    required: ["id"]
  }
}
```

### Tool Naming Convention

**OpenAPI:** `GET /api/v1/users/{id}/profile`
**MCP Tool:** `get_user_profile`

**Rules:**
1. Method + path segments
2. Snake_case
3. Remove version prefixes
4. Parameterized paths become tool inputs

### Error Handling Strategy

MCP servers should return structured errors:

```typescript
{
  error: {
    code: -32603,        // JSON-RPC error code
    message: "API error",
    data: {
      status: 404,
      body: "User not found"
    }
  }
}
```

**Categories:**
- `-32700` Parse error (malformed request)
- `-32600` Invalid request (missing required params)
- `-32601` Method not found (unknown tool)
- `-32603` Internal error (API failure, network error)

### Authentication Patterns

**Pattern 1: API Key (most common)**
```typescript
const apiKey = process.env.API_KEY;
headers['Authorization'] = `Bearer ${apiKey}`;
```

**Pattern 2: OAuth 2.0**
```typescript
const token = await refreshToken();
headers['Authorization'] = `Bearer ${token}`;
```

**Pattern 3: Custom Auth**
```typescript
headers['X-Custom-Auth'] = computeSignature(request);
```

**Best practice:** Store credentials in environment variables, never hardcode.

### Rate Limiting

MCP servers should handle rate limits gracefully:

```typescript
async function callWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (err.status === 429) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await sleep(delay);
        continue;
      }
      throw err;
    }
  }
}
```

## Generated MCP Server Structure

### TypeScript Server
```
mcp-server/
├── src/
│   ├── index.ts           # Server entry point
│   ├── tools/             # Tool implementations
│   │   ├── get_user.ts
│   │   ├── create_user.ts
│   │   └── ...
│   ├── client.ts          # API client wrapper
│   ├── types.ts           # TypeScript types
│   └── validation.ts      # Input validation
├── tests/
│   ├── tools.test.ts      # Tool tests
│   └── integration.test.ts
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

### Python Server
```
mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Server entry point
│   ├── tools/             # Tool implementations
│   │   ├── get_user.py
│   │   ├── create_user.py
│   │   └── ...
│   ├── client.py          # API client wrapper
│   └── validation.py      # Input validation
├── tests/
│   ├── test_tools.py
│   └── test_integration.py
├── requirements.txt
├── .env.example
└── README.md
```

## Python Tool Details

### 1. OpenAPI Parser

**Purpose:** Parse OpenAPI/Swagger specs and extract MCP tool definitions.

**Usage:**
```bash
python scripts/openapi_parser.py api-spec.yaml --output parsed.json
```

**Output:**
```json
{
  "info": {
    "title": "User API",
    "version": "1.0.0",
    "baseUrl": "https://api.example.com"
  },
  "auth": {
    "type": "bearer",
    "headerName": "Authorization"
  },
  "tools": [
    {
      "name": "get_user",
      "description": "Get user by ID",
      "method": "GET",
      "path": "/users/{id}",
      "parameters": {
        "path": ["id"],
        "query": [],
        "body": null
      },
      "inputSchema": { ... },
      "responseSchema": { ... }
    }
  ]
}
```

### 2. MCP Generator

**Purpose:** Generate MCP server code from parsed API spec.

**Usage:**
```bash
python scripts/mcp_generator.py parsed.json \
  --language typescript \
  --output mcp-server/ \
  --with-docker
```

**Options:**
- `--language` - typescript or python (default: typescript)
- `--output` - Output directory
- `--with-docker` - Generate Dockerfile and docker-compose.yaml
- `--auth-env-var` - Name of env var for auth (default: API_KEY)

**Generates:**
- Server entry point
- Tool implementations (one file per tool)
- API client wrapper
- Type definitions
- Tests
- Deployment config

### 3. Server Tester

**Purpose:** Test MCP server tools and validate responses.

**Usage:**
```bash
python scripts/server_tester.py mcp-server/ \
  --test-all \
  --mock-api \
  --output test-report.json
```

**Tests:**
- Tool schema validation
- Input validation (required fields, types)
- Error handling (missing params, invalid types)
- Response schema validation
- End-to-end with mock API

**Output:**
```json
{
  "summary": {
    "total_tools": 5,
    "passed": 4,
    "failed": 1
  },
  "results": [
    {
      "tool": "get_user",
      "tests": {
        "schema_valid": true,
        "input_validation": true,
        "response_validation": true,
        "error_handling": false
      },
      "errors": ["Missing 404 error handling"]
    }
  ]
}
```

## Workflow Example

**Scenario:** Create MCP server for GitHub API

**Step 1: Get OpenAPI spec**
```bash
# GitHub publishes OpenAPI specs
curl -o github-api.yaml https://github.com/github/rest-api-description/releases/latest/download/api.github.com.yaml
```

**Step 2: Parse spec**
```bash
python scripts/openapi_parser.py github-api.yaml \
  --filter "repos,issues" \
  --output github-parsed.json
```

Output: 50 tools extracted (filtered to repos and issues endpoints)

**Step 3: Generate MCP server**
```bash
python scripts/mcp_generator.py github-parsed.json \
  --language typescript \
  --output github-mcp-server/ \
  --auth-env-var GITHUB_TOKEN
```

Output: TypeScript MCP server with 50 tools

**Step 4: Configure authentication**
```bash
cd github-mcp-server/
cp .env.example .env
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
```

**Step 5: Test tools**
```bash
python scripts/server_tester.py github-mcp-server/ \
  --test-all \
  --output test-report.json
```

Output: 48/50 tools passing (2 require org access)

**Step 6: Deploy**
```bash
cd github-mcp-server/
npm install
npm run build
npm start
```

**Step 7: Connect to Claude Desktop**

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/github-mcp-server/dist/index.js"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

Now Claude can call GitHub tools: "Create an issue in my repo", "List my repositories", etc.

## Common Patterns

### Pattern 1: Pagination Handling

Many APIs return paginated results. MCP tools should handle this:

```typescript
async function listUsers(params: { limit?: number, cursor?: string }) {
  const response = await api.get('/users', {
    params: {
      limit: params.limit || 100,
      cursor: params.cursor
    }
  });
  
  return {
    users: response.data,
    nextCursor: response.nextCursor,
    hasMore: !!response.nextCursor
  };
}
```

**MCP Tool:**
```json
{
  "name": "list_users",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": { "type": "number", "default": 100 },
      "cursor": { "type": "string" }
    }
  }
}
```

### Pattern 2: Batch Operations

For efficiency, support batch operations:

```typescript
async function batchGetUsers(params: { ids: string[] }) {
  // Split into chunks of 50 (API limit)
  const chunks = chunkArray(params.ids, 50);
  const results = [];
  
  for (const chunk of chunks) {
    const response = await api.post('/users/batch', { ids: chunk });
    results.push(...response.data);
  }
  
  return results;
}
```

### Pattern 3: Webhook Integration

Some MCP servers can register webhooks:

```typescript
async function registerWebhook(params: { event: string, url: string }) {
  return await api.post('/webhooks', {
    event: params.event,
    url: params.url,
    secret: process.env.WEBHOOK_SECRET
  });
}
```

### Pattern 4: Caching

Cache frequently accessed data:

```typescript
const cache = new Map();

async function getUser(params: { id: string }) {
  const cacheKey = `user:${params.id}`;
  
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const user = await api.get(`/users/${params.id}`);
  cache.set(cacheKey, user, { ttl: 300 }); // 5 min TTL
  
  return user;
}
```

## Tool Design Best Practices

### 1. Clear Descriptions

**Bad:**
```json
{
  "name": "get_data",
  "description": "Gets data"
}
```

**Good:**
```json
{
  "name": "get_user_profile",
  "description": "Retrieves detailed user profile including name, email, created date, and account settings. Requires user ID."
}
```

### 2. Explicit Input Schemas

Always specify required fields and types:

```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": {
        "type": "string",
        "description": "Unique user identifier"
      },
      "includeSettings": {
        "type": "boolean",
        "description": "Whether to include account settings",
        "default": false
      }
    },
    "required": ["userId"]
  }
}
```

### 3. Structured Errors

Return actionable error messages:

```typescript
if (!params.userId) {
  throw {
    code: -32600,
    message: "Missing required parameter: userId",
    data: {
      parameter: "userId",
      type: "string",
      description: "Unique user identifier"
    }
  };
}
```

### 4. Response Normalization

Normalize API responses to consistent structure:

```typescript
async function getUser(params) {
  try {
    const response = await api.get(`/users/${params.id}`);
    
    return {
      success: true,
      data: response.data,
      metadata: {
        requestId: response.headers['x-request-id'],
        rateLimit: {
          remaining: response.headers['x-ratelimit-remaining'],
          reset: response.headers['x-ratelimit-reset']
        }
      }
    };
  } catch (err) {
    return {
      success: false,
      error: {
        message: err.message,
        status: err.status,
        code: err.code
      }
    };
  }
}
```

## Quality Checklist

Before deploying MCP server:
- [ ] All tools have clear descriptions
- [ ] Input schemas specify required fields
- [ ] Authentication configured via env vars
- [ ] Error handling for all API failures
- [ ] Rate limiting with exponential backoff
- [ ] Tests cover all tools
- [ ] Response schemas validated
- [ ] Logging enabled for debugging
- [ ] Docker deployment ready
- [ ] README with setup instructions

## When to Use vs. Direct API Calls

| Use MCP Server | Use Direct API |
|----------------|----------------|
| AI assistant integration | Simple scripts |
| Multiple tools from one API | One-off requests |
| Reusable across projects | Project-specific code |
| Need structured error handling | Quick prototypes |
| Authentication abstraction needed | Full control required |

## Deployment Options

### Option 1: Local (Development)
```bash
npm start
# Runs on localhost, accessible to Claude Desktop
```

### Option 2: Docker (Production)
```bash
docker-compose up -d
# Containerized, easy to deploy
```

### Option 3: Cloud (Serverless)
```typescript
// Deploy to AWS Lambda, Vercel, etc.
export const handler = mcpServer.handler;
```

## Monitoring

Track MCP server health:

```typescript
const metrics = {
  totalRequests: 0,
  successfulRequests: 0,
  failedRequests: 0,
  averageLatency: 0
};

function recordMetrics(tool: string, success: boolean, latency: number) {
  metrics.totalRequests++;
  if (success) metrics.successfulRequests++;
  else metrics.failedRequests++;
  
  // Update average latency
  metrics.averageLatency = 
    (metrics.averageLatency * (metrics.totalRequests - 1) + latency) / metrics.totalRequests;
  
  console.log(`[${tool}] ${success ? 'OK' : 'FAIL'} ${latency}ms`);
}
```

## References

- MCP Protocol Spec: `references/mcp-protocol-guide.md`
- Tool Design Patterns: `references/tool-design-patterns.md`
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- OpenAPI Specification: https://swagger.io/specification/

## Credits

**Michael Lynn** — [mlynn.org](https://mlynn.org) · [@mlynn](https://twitter.com/mlynn) · [LinkedIn](https://linkedIn.com/in/mlynn) · [GitHub](https://github.com/mrlynn)

---

**Next steps after generating server:**
1. Test tools with mock API
2. Configure authentication
3. Deploy and connect to Claude Desktop
4. Monitor usage and errors
5. Iterate on tool descriptions based on usage
