# Role-Permission Matrix

## Role Hierarchy (highest to lowest)

1. `super_admin` — Full platform control
2. `admin` — Event and user management
3. `organizer` — Event operations
4. `marketer` — Content and communications
5. `mentor` — Participant guidance
6. `judge` — Project evaluation
7. `participant` — Event participation
8. `partner` — Sponsor portal access

## Route Permissions

| Route / Action | super_admin | admin | organizer | marketer | mentor | judge | participant | partner |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Admin Panel** | | | | | | | | |
| `/admin` (access panel) | Y | Y | Y | Y | - | - | - | - |
| `/admin/users` (list/search) | Y | Y | - | - | - | - | - | - |
| `/admin/users` (ban/role change) | Y | Y | - | - | - | - | - | - |
| `/admin/users` (delete) | Y | - | - | - | - | - | - | - |
| **Event Management** | | | | | | | | |
| `/admin/events` (list all) | Y | Y | Y | Y | - | - | - | - |
| `/admin/events` (create) | Y | Y | Y | - | - | - | - | - |
| `/admin/events` (edit) | Y | Y | Y | - | - | - | - | - |
| `/admin/events` (delete) | Y | Y | - | - | - | - | - | - |
| `/admin/events/[id]/assignments` | Y | Y | Y | - | - | - | - | - |
| `/admin/events/[id]/results` | Y | Y | Y | - | - | - | - | - |
| **Atlas Provisioning** | | | | | | | | |
| `/admin/events/[id]/atlas` (config) | Y | Y | - | - | - | - | - | - |
| `/api/atlas/provision` (trigger) | Y | Y | Y | - | - | - | - | - |
| `/api/atlas/status` (view) | Y | Y | Y | - | - | Y | Y | - |
| **Feedback & Judging** | | | | | | | | |
| `/admin/feedback-forms` (CRUD) | Y | Y | Y | - | - | - | - | - |
| `/admin/events/[id]/send-feedback` | Y | Y | Y | Y | - | - | - | - |
| `/judging/[eventId]/projects` | Y | Y | Y | - | - | Y | - | - |
| `/judging/[eventId]/score` | Y | Y | - | - | - | Y | - | - |
| **Email & Templates** | | | | | | | | |
| `/admin/email-templates` (list) | Y | Y | - | Y | - | - | - | - |
| `/admin/email-templates` (CRUD) | Y | Y | - | - | - | - | - | - |
| `/admin/email-templates/preview` | Y | Y | - | Y | - | - | - | - |
| `/admin/email-templates/test-send` | Y | Y | - | - | - | - | - | - |
| **RAG / AI Admin** | | | | | | | | |
| `/admin/rag` (full access) | Y | Y | - | - | - | - | - | - |
| `/admin/rag/status` (view only) | Y | Y | Y | Y | - | - | - | - |
| **Partners** | | | | | | | | |
| `/admin/partners` (CRUD) | Y | Y | - | Y | - | - | - | - |
| `/partners/portal` (own data) | Y | Y | - | - | - | - | - | Y |
| **Content & Templates** | | | | | | | | |
| `/admin/templates` (rubrics) | Y | Y | Y | - | - | - | - | - |
| `/admin/site-settings` | Y | - | - | - | - | - | - | - |
| **Gallery / Public** | | | | | | | | |
| `/gallery` (view) | Y | Y | Y | Y | Y | Y | Y | Y |
| `/gallery` (feature project) | Y | Y | - | - | - | - | - | - |
| **User Self-Service** | | | | | | | | |
| `/settings/profile` | Y | Y | Y | Y | Y | Y | Y | Y |
| `/settings/password` | Y | Y | Y | Y | Y | Y | Y | Y |
| `/settings/2fa` | Y | Y | Y | Y | Y | Y | Y | Y |
| `/settings/notifications` | Y | Y | Y | Y | Y | Y | Y | Y |

## Role Groups (used in code)

```typescript
const SUPER_ADMIN_ROLES = ["super_admin"];
const ADMIN_ROLES = ["super_admin", "admin"];
const ADMIN_PANEL_ROLES = ["super_admin", "admin", "organizer", "marketer"];
const EVENT_MANAGEMENT_ROLES = ["super_admin", "admin", "organizer"];
const ALL_ROLES = ["super_admin", "admin", "organizer", "marketer", "mentor", "judge", "participant", "partner"];
```

## Notes

- `super_admin` can do everything. There is no route that blocks super_admin.
- `admin` can do almost everything except delete users and modify site settings.
- `organizer` is scoped to event operations (CRUD, assignments, results, provisioning).
- `marketer` can view events and manage email templates/partners but cannot create events.
- `judge` can only access judging routes for events they are assigned to.
- `participant` has no admin panel access; they interact through public routes.
- `partner` accesses a dedicated partner portal showing their organization data.
