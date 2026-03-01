# Naming Conventions Reference

Complete naming rules for the MongoDB DevRel platform. These conventions are enforced across all skills and should be followed consistently in new code.

## Models

### Interface Names

**Convention:** PascalCase with `I` prefix.

```typescript
IUser
IEvent
IPartner
IEmailTemplate
IAtlasCluster
IRagDocument
IFeedbackFormConfig
IRegistrationFormConfig
IParticipant
IScore
INotification
IAiUsageLog
IRagIngestionRun
IRagConversation
ISiteSettings
```

The `I` prefix distinguishes TypeScript interfaces from their Mongoose model counterparts. Every model file exports both the interface and the model.

### Model Export Names

**Convention:** PascalCase with `Model` suffix.

```typescript
UserModel
EventModel
PartnerModel
EmailTemplateModel
AtlasClusterModel
RagDocumentModel
FeedbackFormConfigModel
RegistrationFormConfigModel
ParticipantModel
ScoreModel
NotificationModel
AiUsageLogModel
RagIngestionRunModel
RagConversationModel
SiteSettingsModel
```

### Model Registration Guard

Every model uses the registration guard pattern to prevent `OverwriteModelError` during hot module reload:

```typescript
export const UserModel =
  mongoose.models.User || mongoose.model<IUser>("User", UserSchema);
```

The string passed to `mongoose.model()` is PascalCase without the `Model` suffix:
- `"User"` (not `"UserModel"`)
- `"EmailTemplate"` (not `"EmailTemplateModel"`)
- `"AtlasCluster"` (not `"AtlasClusterModel"`)

### Schema Variable Names

**Convention:** PascalCase with `Schema` suffix (Mongoose schemas, not Zod).

```typescript
const UserSchema = new Schema<IUser>({...});
const EventSchema = new Schema<IEvent>({...});
const PartnerSchema = new Schema<IPartner>({...});
```

### Model File Names

**Convention:** PascalCase, matching the model name.

```
src/lib/db/models/User.ts
src/lib/db/models/Event.ts
src/lib/db/models/Partner.ts
src/lib/db/models/EmailTemplate.ts
src/lib/db/models/AtlasCluster.ts
src/lib/db/models/RagDocument.ts
src/lib/db/models/FeedbackFormConfig.ts
src/lib/db/models/AiUsageLog.ts
```

---

## Zod Validation Schemas

### Schema Names

**Convention:** camelCase with `create` or `update` prefix and `Schema` suffix.

```typescript
createEventSchema
updateEventSchema          // = createEventSchema.partial()

createPartnerSchema
updatePartnerSchema

createEmailTemplateSchema
updateEmailTemplateSchema

submitScoreSchema
registrationSchema
```

### Paired Schemas

Every resource that supports both creation and updates has paired schemas:

```typescript
export const createEventSchema = z.object({
  name: z.string().min(3).max(200),
  description: z.string().min(10).max(5000),
  // ...all required fields
});

export const updateEventSchema = createEventSchema.partial();
```

### Schema File Location

All Zod schemas live in a single file:

```
src/lib/db/schemas.ts
```

---

## API Routes

### URL Path Convention

**Convention:** kebab-case for all URL segments.

```
/api/admin/events
/api/admin/events/[eventId]
/api/admin/email-templates
/api/admin/email-templates/[id]/test-send
/api/admin/feedback-forms
/api/admin/feedback-forms/[id]/clone
/api/admin/site-settings
/api/admin/users/[userId]/ban
/api/admin/users/[userId]/role
/api/admin/rag/status
/api/admin/rag/ingest
/api/admin/projects/[projectId]/featured
/api/events/[eventId]/register
/api/judging/[eventId]/score
/api/judging/[eventId]/projects
/api/settings/password
/api/settings/2fa
/api/settings/notifications
/api/gallery
/api/health
```

### Dynamic Segments

**Convention:** camelCase in square brackets.

```
[eventId]
[userId]
[projectId]
[id]         // generic, used when the resource name is clear from context
[runId]
```

### Route File Convention

All route handlers are in `route.ts` files:

```
src/app/api/admin/events/route.ts              # GET, POST
src/app/api/admin/events/[eventId]/route.ts    # GET, PATCH, DELETE
```

### HTTP Method Conventions

| Method | Purpose                    | Status Code (success) |
|--------|----------------------------|----------------------|
| GET    | Read resource(s)           | 200                  |
| POST   | Create resource or action  | 201 (create), 200 (action) |
| PATCH  | Partial update             | 200                  |
| DELETE | Remove resource            | 200 or 204           |

---

## Files and Directories

### Utility Files

**Convention:** kebab-case.

```
src/lib/admin-guard.ts
src/lib/auth.ts
src/lib/utils.ts
src/lib/logger.ts
src/lib/rubric-templates.ts
src/lib/email/email-service.ts
src/lib/email/template-renderer.ts
src/lib/email/seed-email-templates.ts
src/lib/atlas/atlas-client.ts
src/lib/atlas/provisioning-service.ts
src/lib/atlas/status-service.ts
src/lib/atlas/auth-guard.ts
src/lib/ai/usage-logger.ts
src/lib/ai/summary-service.ts
src/lib/ai/feedback-service.ts
src/lib/ai/embedding-service.ts
src/lib/rag/embeddings.ts
src/lib/rag/ingestion.ts
src/lib/rag/retrieval.ts
src/lib/rag/chunker.ts
src/lib/rag/chat.ts
src/lib/rag/rate-limit.ts
src/lib/rag/types.ts
```

### React Components

**Convention:** PascalCase with `.tsx` extension.

```
src/components/shared-ui/ThemeRegistry.tsx
src/components/shared-ui/AdminShell.tsx
src/components/shared-ui/LoadingSpinner.tsx
src/components/events/EventCard.tsx
src/components/judging/ScoreForm.tsx
```

### Page Files

**Convention:** `page.tsx` (Next.js App Router convention).

```
src/app/(app)/page.tsx
src/app/(app)/admin/page.tsx
src/app/(app)/events/[eventId]/page.tsx
```

### Layout Files

**Convention:** `layout.tsx` (Next.js App Router convention).

```
src/app/layout.tsx
src/app/(app)/layout.tsx
src/app/(app)/admin/layout.tsx
```

### Style Files

**Convention:** kebab-case.

```
src/styles/theme.ts
src/app/globals.css
```

### Type Declaration Files

**Convention:** kebab-case with `.d.ts` extension.

```
src/types/next-auth.d.ts
```

---

## Role Types

**Convention:** snake_case strings.

```typescript
type UserRole =
  | "super_admin"
  | "admin"
  | "organizer"
  | "marketer"
  | "mentor"
  | "judge"
  | "participant"
  | "partner";
```

These are stored as plain strings in MongoDB (not numeric codes) for readability in queries and debugging.

---

## Status Values

**Convention:** snake_case strings.

### Event Status

```typescript
"draft" | "open" | "in_progress" | "concluded"
```

### Partner Status

```typescript
"active" | "inactive" | "pending"
```

### Atlas Cluster Status

```typescript
"creating" | "idle" | "active" | "deleting" | "deleted" | "error"
```

### Participant Status

```typescript
"registered" | "checked_in" | "cancelled"
```

### RAG Ingestion Run Status

```typescript
"running" | "completed" | "failed" | "cancelled"
```

---

## Environment Variables

**Convention:** UPPER_SNAKE_CASE.

```bash
MONGODB_URI
AUTH_SECRET
NEXTAUTH_URL
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASS
EMAIL_FROM
ATLAS_PUBLIC_KEY
ATLAS_PRIVATE_KEY
ATLAS_ORG_ID
ATLAS_BASE_URL
OPENAI_API_KEY
VOYAGE_API_KEY
```

---

## Database Collection Names

Mongoose automatically pluralizes and lowercases model names for collection names:

| Model Name           | Collection Name          |
|----------------------|--------------------------|
| User                 | users                    |
| Event                | events                   |
| Partner              | partners                 |
| EmailTemplate        | emailtemplates           |
| AtlasCluster         | atlasclusters            |
| RagDocument          | ragdocuments             |
| FeedbackFormConfig   | feedbackformconfigs      |
| Participant          | participants             |
| Score                | scores                   |
| AiUsageLog           | aiusagelogs              |

---

## Summary Table

| Thing               | Convention     | Example                         |
|---------------------|---------------|---------------------------------|
| Interface           | `I` + PascalCase | `IUser`, `IEvent`             |
| Model export        | PascalCase + `Model` | `UserModel`, `EventModel` |
| Mongoose schema var | PascalCase + `Schema` | `UserSchema`              |
| Model file          | PascalCase     | `User.ts`, `EmailTemplate.ts`  |
| Zod schema          | camelCase + `Schema` | `createEventSchema`       |
| API route path      | kebab-case     | `/api/admin/email-templates`    |
| Dynamic segment     | camelCase      | `[eventId]`, `[userId]`         |
| Utility file        | kebab-case     | `admin-guard.ts`                |
| Component file      | PascalCase     | `ThemeRegistry.tsx`             |
| Role type           | snake_case     | `super_admin`, `organizer`      |
| Status value        | snake_case     | `in_progress`, `concluded`      |
| Env variable        | UPPER_SNAKE_CASE | `MONGODB_URI`                |
