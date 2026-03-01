# Architecture Pre-Flight Checklist

Use this checklist before submitting a PR or shipping a new feature. Every item reflects a convention validated in the MongoDB DevRel platform codebase.

## Database

- [ ] Called `connectToDatabase()` before any model operation in the API route?
- [ ] Using `.lean()` for read-only queries (returns plain objects, not Mongoose docs)?
- [ ] Added compound indexes for frequently queried field combinations?
- [ ] Using `{ timestamps: true }` on all schemas for automatic `createdAt`/`updatedAt`?
- [ ] Using `select: false` on sensitive fields (passwordHash, twoFactorCode)?
- [ ] Avoided `$where` and raw string queries (use typed Mongoose queries)?
- [ ] Used `$addToSet` instead of `$push` for arrays that should be unique?
- [ ] Checked for existing documents before creating (idempotent operations)?

## Authentication & Authorization

- [ ] Checked `session?.user` for authenticated routes?
- [ ] Checked role against role group (ADMIN_ROLES, EVENT_MANAGEMENT_ROLES) before mutations?
- [ ] Using `errorResponse("Unauthorized", 401)` for missing session?
- [ ] Using `errorResponse("Forbidden", 403)` for insufficient role?
- [ ] Using `getToken()` (not `auth()`) in edge middleware?
- [ ] NOT importing `@/lib/auth` in `middleware.ts` (crashes Edge runtime)?

## Validation

- [ ] Using Zod schema for all API request body validation?
- [ ] Calling `.safeParse()` (not `.parse()`) and returning 422 on failure?
- [ ] Validating ObjectId format before using in queries?
- [ ] Sanitizing user input before storing (trim, lowercase emails)?

## Security

- [ ] Hashing tokens/codes with SHA-256 (`crypto.createHash('sha256')`) before storing?
- [ ] Generating secure random values with `crypto.randomBytes()` or `crypto.randomUUID()`?
- [ ] Setting expiry on all temporary tokens (2FA codes, reset links)?
- [ ] NOT returning sensitive fields in API responses (passwords, tokens, 2FA codes)?
- [ ] Using `httpOnly` cookies for sensitive session data?

## Error Handling

- [ ] Wrapping route handler body in `try/catch`?
- [ ] Logging errors with `console.error("CONTEXT:", error)` before returning response?
- [ ] Returning `errorResponse("Internal server error", 500)` in catch blocks?
- [ ] NOT exposing internal error messages to the client?

## Email

- [ ] Using fire-and-forget (`.catch(() => {})`) for non-critical email sends?
- [ ] Using DB-backed template with hardcoded fallback?
- [ ] Including all required template variables in the render call?
- [ ] Using the singleton SMTP transporter (not creating new transporter per request)?

## API Response Patterns

- [ ] Using `successResponse(data)` and `successResponse(data, 201)` for success?
- [ ] Using `errorResponse(message, statusCode)` for errors?
- [ ] Returning 201 for POST creates, 200 for updates, 200 for deletes?
- [ ] Including meaningful error messages (not just "Error")?

## Naming Conventions

- [ ] Model interface uses `I` prefix (`IUser`, `IEvent`)?
- [ ] Model export uses `Model` suffix (`UserModel`, `EventModel`)?
- [ ] Zod schemas use camelCase with verb prefix (`createEventSchema`, `updateUserSchema`)?
- [ ] API route paths are kebab-case (`/api/admin/email-templates/[id]/test-send`)?
- [ ] Role values are snake_case (`super_admin`, `organizer`)?
- [ ] Utility files are kebab-case (`admin-guard.ts`, `email-service.ts`)?
- [ ] Components are PascalCase (`ThemeRegistry.tsx`, `EventCard.tsx`)?

## Branding

- [ ] Spring Green (`#00ED64`) used as accent only, never as background fill in dark mode?
- [ ] Using chip tint `rgba(0, 237, 100, 0.12)` not solid green for dark mode chips?
- [ ] Page background is Slate Blue (`#001E2B`) in dark mode?
- [ ] Buttons have `textTransform: "none"` (never uppercase)?
- [ ] Border radius: 12px for cards, 8px for buttons/inputs, 6px for chips?

## AI Features

- [ ] Using singleton pattern for OpenAI/Voyage clients?
- [ ] Logging AI usage with fire-and-forget `logAiUsage()` calls?
- [ ] Using `inputType: "document"` for storage embeddings, `inputType: "query"` for search?
- [ ] Content-hashing documents before re-ingestion to skip unchanged files?

## Atlas Provisioning

- [ ] Checking for existing project/cluster before creating (idempotent)?
- [ ] Implementing rollback (delete project) on provisioning failure?
- [ ] Including `appName=devrel-platform-*` in connection strings for attribution?
- [ ] Never storing database passwords (display once, then discard)?
