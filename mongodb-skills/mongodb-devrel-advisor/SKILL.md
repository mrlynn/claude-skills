---
name: mongodb-devrel-advisor
description: Always-on conventions advisor for MongoDB DevRel projects providing architecture guidance, branding rules, naming conventions, database patterns, and security best practices
license: MIT
disable-model-invocation: true
metadata:
  version: 1.0.0
  author: MongoDB Developer Relations
  category: mongodb-devrel
  domain: conventions
  updated: 2026-03-01
  tech-stack: nextjs, mongodb, mui, mongoose
---

# mongodb-devrel-advisor

## Trigger

Always active as background context. Use when making any architectural decision, choosing libraries, naming conventions, structuring code, or applying MongoDB branding in a DevRel project. This skill synthesizes the conventions from all other skills into a quick-reference guide.

## Overview

This is the meta-skill — a pattern-aware advisor grounded in the actual decisions made across the MongoDB Hackathon Platform. Instead of generic best practices, it provides specific conventions that the DevRel team has validated through production use.

## How to Use

This is a background context skill — it's always active and doesn't need to be explicitly invoked. Claude uses it automatically when making architectural decisions, choosing libraries, or applying MongoDB branding.

### Reference Docs
- `references/naming-conventions.md` — Complete naming rules for models, schemas, routes, files, roles
- `references/decision-matrix.md` — Which DB driver, auth lib, UI framework, LLM, embedding model

### Templates & Samples
- `assets/architecture-checklist.md` — Pre-flight checklist for new features

## Architecture Principles

### Project Structure
- **App Router** with `(app)` route group for layout isolation
- `src/lib/` for all server-side business logic
- `src/lib/db/models/` for Mongoose models
- `src/lib/db/schemas.ts` for Zod validation schemas
- `src/lib/db/connection.ts` for singleton DB connection
- `src/styles/` for theme files
- `src/components/shared-ui/` for reusable UI components
- `src/contexts/` for React context providers
- `src/types/` for TypeScript declarations

### Server vs Client Components
- **Server components by default.** Only add `"use client"` when the component uses hooks (useState, useEffect, useSession) or browser APIs.
- **Never import Mongoose in client components.** It will crash the build.
- **Never import `@/lib/auth` in `middleware.ts`.** It pulls in Node.js-only modules.

### Naming Conventions
- **Models**: PascalCase with `I` prefix for interface (`IUser`, `IEvent`), `Model` suffix for export (`UserModel`, `EventModel`)
- **Schemas**: camelCase with create/update prefix (`createEventSchema`, `updateEventSchema`)
- **API routes**: kebab-case paths (`/api/admin/email-templates/[id]/test-send`)
- **Files**: kebab-case for utilities (`admin-guard.ts`, `email-service.ts`), PascalCase for components (`ThemeRegistry.tsx`)
- **Role types**: snake_case (`super_admin`, `organizer`)

## MongoDB Branding

### Color Rules
| Token | Hex | Usage |
|-------|-----|-------|
| Spring Green | `#00ED64` | Accent/CTA only. NEVER as background fill in dark mode |
| Forest Green | `#00684A` | Primary in light mode |
| Evergreen | `#023430` | Primary dark variant |
| Slate Blue | `#001E2B` | Dark mode page background, light mode text |
| Blue | `#006EFF` | Secondary / interactive elements |
| Purple | `#B45AF2` | Accent (badges, highlights) |
| Warning Yellow | `#FFC010` | Warnings |
| Error Red | `#CF4520` | Errors |

### Dark Mode Rules
- Page background: `#001E2B` (Slate Blue)
- Card surfaces: `#0F2235` (dark navy, NOT green-tinted)
- Primary buttons: Spring Green with Slate Blue text
- Chips: Use `rgba(0, 237, 100, 0.12)` tint, not solid green
- AppBar: Slate Blue background with 1px border `rgba(255, 255, 255, 0.08)`

### Typography
- Font: Inter (similar to MongoDB's Euclid Circular A)
- Headings: weight 600, negative letter-spacing for h1/h2
- Buttons: weight 500, `textTransform: "none"` (never uppercase)
- Use `clamp()` for responsive heading sizes

### Component Styling
- Card: borderRadius 12, subtle shadow, 1px divider border
- Button: borderRadius 8, no box-shadow on contained, 10px 20px padding
- Chip: borderRadius 6, weight 500
- TextField: borderRadius 8, focus border = primary
- Tab: no textTransform, weight 500

## Database Patterns

### Connection
- **Always call `connectToDatabase()` before any model operation** in API routes
- Use the singleton pattern with global cache (conn + promise)
- Set `bufferCommands: false` to make connection failures explicit

### Querying
- Use `.lean()` for read-only queries (returns plain objects, 3-5x faster)
- Use `.select("+fieldName")` to include fields marked `select: false`
- Use `.select("-fieldName")` to exclude large fields (embeddings, long text)
- Use `.sort({ createdAt: -1 })` for reverse chronological by default

### Writing
- Use `$addToSet` for array additions (prevents duplicates)
- Use `$pull` for array removals
- Use `.partial()` on Zod schemas for update operations
- Use `{ timestamps: true }` on all schemas for automatic createdAt/updatedAt

### Indexes
- Always create indexes for frequently queried fields
- Use compound indexes for common query patterns (`{ tier: 1, status: 1 }`)
- Use `sparse: true` for optional unique fields (`landingPage.slug`)
- Use `select: false` + sparse indexes for security tokens
- Use `2dsphere` for geospatial coordinates

## Security Patterns

### Password & Token Security
- Hash passwords with bcrypt (`bcryptjs` for Node.js compatibility)
- Hash tokens (magic link, 2FA, email verification) with SHA-256 before storing
- Mark sensitive fields with `select: false` in schema definitions
- Use `crypto.randomInt()` for secure random generation (not `Math.random()`)

### Account Safety
- Soft-delete users with `deletedAt` (never hard-delete)
- Ban system with `banned`, `bannedAt`, `bannedReason` fields
- Check ban/delete status during authentication
- Rate-limit sensitive operations (login, 2FA, API endpoints)

### API Security
- Validate all inputs with Zod schemas
- Check role before any mutation
- Use `errorResponse("Forbidden", 403)` for unauthorized role
- Use `errorResponse("Unauthorized", 401)` for missing session
- Never expose internal error details to clients

## Singleton Patterns

All expensive-to-create resources follow the same lazy initialization:

```typescript
let instance: Type | null = null;
function getInstance(): Type {
  if (!instance) {
    instance = new Type(config);
  }
  return instance;
}
```

Applied to: Mongoose connection, Nodemailer transporter, OpenAI client, DigestFetch client.

## Error Handling

### API Routes
```typescript
try {
  // auth check → connect → validate → operate → respond
} catch (error) {
  console.error("METHOD /api/path error:", error);
  return errorResponse("Internal server error", 500);
}
```

### Fire-and-Forget
For non-critical operations (email, logging, embeddings):
```typescript
sendEmail({...}).catch(() => {});
logAiUsage({...}); // Already never-throws internally
```

### Rollback
For multi-step operations (Atlas provisioning):
```typescript
try {
  // step 1, 2, 3...
} catch (error) {
  // rollback: delete created resources
  if (createdResource) {
    try { await deleteResource(createdResource.id); } catch { /* log only */ }
  }
  throw error;
}
```

## Cross-References

| Need | Use Skill |
|------|-----------|
| New project from scratch | `mongodb-nextjs-scaffold` |
| Authentication & roles | `mongodb-rbac-middleware` |
| Sending emails | `mongodb-email-system` |
| Atlas cluster management | `mongodb-atlas-provisioning` |
| AI summarization, RAG | `mongodb-ai-features` |
| Event/hackathon features | `mongodb-event-platform` |
| Sponsor management | `mongodb-partner-portal` |

## Decision Guide

**"Which database driver?"** → Mongoose. It provides schema validation, model guards for hot reload, middleware hooks, and population. The native driver is only better for raw aggregation-heavy workloads.

**"Which auth library?"** → NextAuth v5 (beta). JWT strategy for edge compatibility. Credential + magic link providers. Role embedded in JWT token.

**"Which UI framework?"** → MUI 7 with the MongoDB brand theme. Provides accessible components, dark mode via `colorSchemes`, and responsive breakpoints out of the box.

**"Which embedding model?"** → Voyage AI `voyage-4-large` for documents, same model (or `voyage-4-lite`) for queries. Same embedding space, different cost/quality tradeoffs.

**"Which LLM for generation?"** → OpenAI GPT-4-turbo for structured outputs. GPT-4o for general chat. Use the usage logger to track costs.

**"How do I add a new role?"** → Add to the UserRole type and schema enum in User model. Add to the appropriate role group in admin-guard.ts. Add route protection in middleware.ts. No migration needed — existing users won't have the new role.
