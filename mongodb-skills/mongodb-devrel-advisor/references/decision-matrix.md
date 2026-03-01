# Decision Matrix Reference

A guide for common technology and architecture decisions in MongoDB DevRel projects. Each decision includes the recommendation, rationale, alternatives, and when to deviate.

---

## Database Driver: Mongoose

### Recommendation

Use **Mongoose** as the database driver for all MongoDB DevRel projects.

### Rationale

- **Schema validation**: Mongoose schemas enforce structure at the application level, catching bugs before they reach the database.
- **Model registration guard**: The `mongoose.models.X || mongoose.model()` pattern prevents `OverwriteModelError` during hot module reload in Next.js development mode.
- **Middleware hooks**: Pre/post hooks on save, validate, and remove enable cross-cutting concerns (timestamps, audit logging, cascade deletes).
- **Population**: `populate()` simplifies joining across collections without manual `$lookup` pipelines.
- **TypeScript integration**: `Schema<IUser>` provides strong typing for document operations.
- **Singleton connection**: The global cache pattern (`global.mongoose`) prevents connection leaks in serverless environments.

### Alternatives

| Alternative          | When to Consider                                          |
|----------------------|-----------------------------------------------------------|
| **MongoDB Node.js Driver** | Heavy aggregation pipelines, raw performance needs, minimal schema enforcement. Use when the app is mostly analytics or data processing. |
| **Prisma with MongoDB** | Team is already using Prisma for another database and wants unified syntax. Note: Prisma's MongoDB support has limitations with nested documents and aggregations. |

### When to Deviate

- If the project is purely an aggregation/analytics dashboard with no CRUD operations, the native driver avoids Mongoose overhead.
- If the project needs multi-database transactions across different MongoDB instances, the native driver gives more control.

---

## Auth Library: NextAuth v5 + JWT

### Recommendation

Use **NextAuth v5** (next-auth@beta) with the **JWT session strategy**.

### Rationale

- **JWT is edge-compatible**: No database round-trip on every request. JWTs can be read in edge middleware via `getToken()`.
- **Built-in providers**: Credentials (email/password) and magic link providers are pre-built. OAuth providers can be added with minimal configuration.
- **Role in token**: The `jwt` callback embeds the user's role directly in the token, enabling role-based access control without database queries.
- **Impersonation support**: The `session` callback can swap the session identity by reading the `impersonate_user_id` cookie.
- **NextAuth v5 uses JWE**: Tokens are encrypted (A256CBC-HS512), not just signed. This prevents client-side token tampering.

### Alternatives

| Alternative       | When to Consider                                           |
|-------------------|------------------------------------------------------------|
| **Clerk**         | Need managed auth with pre-built UI components. Higher cost but less code to maintain. |
| **Auth0**         | Enterprise requirements, SSO with SAML/OIDC, compliance needs. |
| **Lucia Auth**    | Want lighter-weight auth without NextAuth's abstraction layer. Good for custom flows. |
| **Custom JWT**    | Already have an existing auth system and only need token verification. |

### When to Deviate

- If the project needs managed user management UI (signup pages, password reset flows), Clerk provides these out of the box.
- If the project requires multi-tenant SSO with SAML, Auth0 or a dedicated identity provider is better.
- If the project does not use Next.js, NextAuth is not applicable.

---

## UI Framework: MUI 7 + MongoDB Theme

### Recommendation

Use **Material-UI (MUI) 7** with the custom MongoDB brand theme defined in `src/styles/theme.ts`.

### Rationale

- **Accessibility**: MUI components follow WAI-ARIA patterns out of the box.
- **Dark mode**: `colorSchemes` configuration provides automatic light/dark mode support with MongoDB brand tokens.
- **Responsive**: MUI's breakpoint system and Grid component handle responsive layouts.
- **Consistent styling**: The theme overrides (Button borderRadius 8, Card borderRadius 12, no uppercase on buttons) enforce MongoDB brand guidelines across all components.
- **Emotion integration**: The `ThemeRegistry` component handles SSR with Emotion cache, preventing flash-of-wrong-theme.

### Alternatives

| Alternative       | When to Consider                                           |
|-------------------|------------------------------------------------------------|
| **Tailwind CSS**  | Utility-first styling preferred, smaller bundle size needed, team prefers Tailwind. Requires custom dark mode implementation. |
| **shadcn/ui**     | Want copy-paste components with Tailwind + Radix UI. More customizable but requires more manual styling work. |
| **Chakra UI**     | Similar component library to MUI with slightly different API. Personal preference. |

### When to Deviate

- If the project is a static marketing site, Tailwind CSS produces smaller bundles.
- If the project has unique design requirements that conflict with Material Design patterns.
- If the team has strong Tailwind expertise and no MUI experience.

---

## Embedding Model: Voyage AI voyage-4-large

### Recommendation

Use **Voyage AI `voyage-4-large`** for all embedding operations (document ingestion and query embedding).

### Rationale

- **Higher retrieval quality**: Voyage AI models are optimized for retrieval tasks and consistently outperform OpenAI embeddings in search benchmarks.
- **Document/query input types**: Voyage models produce different embeddings for documents vs queries, improving retrieval accuracy by 5-15%.
- **1024 dimensions**: Smaller vectors than OpenAI's text-embedding-3-large (3072 dims), reducing storage and improving search speed.
- **Model interchangeability**: All Voyage 4 models share the same embedding space. You can embed documents with voyage-4-large and queries with voyage-4-lite without re-indexing.
- **32,000 token context**: Longer context window than OpenAI (8,191 tokens), enabling larger chunks.

### Alternatives

| Alternative                    | When to Consider                              |
|--------------------------------|-----------------------------------------------|
| **voyage-4**                   | Same quality tier, 17% cheaper. Good for high-volume queries. |
| **voyage-4-lite**              | Development/testing, very high volume, tight budget. |
| **text-embedding-3-small**     | Want single-provider simplicity (OpenAI for everything). Much cheaper ($0.02/M vs $0.12/M). |
| **text-embedding-3-large**     | Need maximum OpenAI quality or broader multilingual support. |

### When to Deviate

- If the project cannot use a second API provider (policy/compliance reasons), use OpenAI embeddings.
- If the project is prototype/demo quality and cost must be minimized, use text-embedding-3-small.
- If the project requires multilingual embeddings in many languages, OpenAI may have broader coverage.

---

## LLM for Generation: OpenAI GPT-4-turbo / GPT-4o

### Recommendation

Use **OpenAI GPT-4-turbo** for structured outputs and **GPT-4o** for general chat/generation.

### Rationale

- **GPT-4-turbo**: Best for structured generation (JSON outputs, rubric scoring, project summaries). More consistent formatting than GPT-4o.
- **GPT-4o**: Better for conversational AI (RAG chat, assistant interfaces). Faster response times and lower cost than GPT-4-turbo.
- **Usage logging**: The AI usage logger tracks costs per model, enabling monitoring and budget control.
- **Singleton client**: The OpenAI client is lazily initialized and reused across requests.

### Alternatives

| Alternative          | When to Consider                                        |
|----------------------|---------------------------------------------------------|
| **Claude (Anthropic)** | Prefer Anthropic models for generation quality. Requires switching the API client. |
| **GPT-3.5-turbo**    | Cost-sensitive, simpler generation tasks, lower latency requirements. |
| **Llama / Mistral**  | Need self-hosted models for data privacy or cost at scale. |

### When to Deviate

- If the project generates large volumes of text where GPT-4 costs are prohibitive, use GPT-3.5-turbo.
- If the project handles sensitive data that cannot leave the organization, use a self-hosted model.

---

## Session Strategy: JWT vs Database

### Recommendation

Use **JWT sessions** (not database sessions).

### Rationale

- **Edge-compatible**: JWT tokens can be read in edge middleware without a database round-trip.
- **Stateless**: No session table to manage, clean up, or scale.
- **Performance**: No database query on every authenticated request.
- **Role embedded**: The user's role is stored in the JWT, enabling instant role checks.

### Trade-offs

| Aspect              | JWT Sessions                    | Database Sessions               |
|---------------------|----------------------------------|----------------------------------|
| Session revocation  | Cannot revoke until expiry       | Instant revocation              |
| Payload size        | Increases cookie size            | Minimal cookie (session ID)     |
| Database load       | None per request                 | 1 query per request             |
| Edge compatibility  | Yes (via getToken)               | No (requires DB connection)     |
| Role updates        | Requires re-login to pick up     | Reflects immediately            |

### When to Deviate

- If the project requires instant session revocation (e.g., compliance requirements), use database sessions.
- If the project needs to reflect role changes immediately without re-login, use database sessions.
- If the JWT payload becomes very large (many custom claims), consider database sessions to reduce cookie size.

---

## Adding a New Role

### Steps

1. **Add the role to the TypeScript type** in `src/lib/admin-guard.ts`:
   ```typescript
   export type UserRole = "super_admin" | "admin" | ... | "new_role";
   ```

2. **Add to the User model schema enum** in `src/lib/db/models/User.ts`:
   ```typescript
   role: {
     type: String,
     enum: [..., "new_role"],
     default: "participant",
   }
   ```

3. **Add to the appropriate role group(s)** in `src/lib/admin-guard.ts`:
   ```typescript
   export const SOME_ROLES: UserRole[] = [..., "new_role"];
   ```

4. **Add route protection** in `src/middleware.ts` if the role needs access to specific sections:
   ```typescript
   if (pathname.startsWith("/new-section")) {
     // Check for new_role
   }
   ```

5. **Create guard function** (if needed) in `src/lib/admin-guard.ts`:
   ```typescript
   export async function requireNewRole() {
     const session = await auth();
     if (!session?.user) redirect("/login");
     // ... role check
   }
   ```

6. **Update NextAuth type declarations** in `src/types/next-auth.d.ts` if the role carries additional JWT claims.

### What You Do NOT Need to Do

- **No database migration**: Existing users will not have the new role. The enum validation only applies to new writes.
- **No token format change**: The role is stored as a string in the JWT. Any string value works.
- **No re-deployment of existing sessions**: Existing JWTs continue to work. Users with the old roles are unaffected.

---

## Quick Reference Table

| Decision              | Recommendation           | Key Reason                         |
|----------------------|--------------------------|-------------------------------------|
| Database driver       | Mongoose                 | Schema validation, model guards     |
| Auth library          | NextAuth v5 + JWT        | Edge-compatible, role in token      |
| UI framework          | MUI 7 + MongoDB theme    | Accessible, dark mode, brand tokens |
| Embedding model       | Voyage AI voyage-4-large | Document/query types, retrieval quality |
| Generation LLM        | OpenAI GPT-4-turbo/4o   | Structured output + chat            |
| Session strategy      | JWT                      | Stateless, edge-safe                |
| Validation library    | Zod                      | Runtime type safety, .partial()     |
| Email transport       | Nodemailer (SMTP)        | Singleton transport, fire-and-forget |
| Atlas API auth        | HTTP Digest (digest-fetch)| Required by Atlas Admin API v2     |
