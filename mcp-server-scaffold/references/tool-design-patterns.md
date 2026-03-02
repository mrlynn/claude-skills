# MCP Tool Design Patterns

## Pattern 1: Clear Descriptions

**Bad:** "Gets data"
**Good:** "Retrieves user profile including name, email, created date. Requires user ID."

## Pattern 2: Explicit Schemas

Always specify types and required fields:

```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": {
        "type": "string",
        "description": "Unique user identifier"
      }
    },
    "required": ["userId"]
  }
}
```

## Pattern 3: Structured Errors

Return actionable error messages:

```typescript
throw {
  code: -32600,
  message: "Missing required parameter: userId"
};
```

## Pattern 4: Pagination

Support pagination for large result sets:

```typescript
{
  name: "list_users",
  inputSchema: {
    properties: {
      limit: { type: "number", default: 100 },
      cursor: { type: "string" }
    }
  }
}
```

## Pattern 5: Caching

Cache frequently accessed data with TTL.

## References

- MCP Best Practices: https://modelcontextprotocol.io/docs/best-practices
