# Role Hierarchy Reference

The platform uses an 8-role hierarchy. Roles are stored as snake_case strings on the User model and embedded in the JWT token for edge-safe access.

## Role Definitions

### super_admin

The highest-privilege role. Full platform control with no restrictions.

- **Description**: Platform owner with unrestricted access to all features, settings, and data.
- **Access**: Everything. All admin panels, all API routes, all data.
- **Unique capabilities**: Site settings, user role changes, impersonation, system configuration, template deletion of built-in templates.
- **Groups**: ADMIN_ROLES, ADMIN_PANEL_ROLES, EVENT_MANAGEMENT_ROLES, PARTNER_PORTAL_ROLES

### admin

Day-to-day platform administrator.

- **Description**: Manages events, users, partners, and content. Cannot modify system settings reserved for super_admin.
- **Access**: Admin panel, all event management, user management (ban, role change except to super_admin), partner management, email templates, RAG ingestion.
- **Unique capabilities**: Can impersonate other users via httpOnly cookie.
- **Groups**: ADMIN_ROLES, ADMIN_PANEL_ROLES, EVENT_MANAGEMENT_ROLES, PARTNER_PORTAL_ROLES

### organizer

Event-focused administrator.

- **Description**: Creates and manages events, assigns judges, publishes results. Cannot manage users or system settings.
- **Access**: Admin panel (events section only), event CRUD, judge assignments, feedback forms, landing pages, Atlas provisioning config.
- **Restrictions**: Cannot manage users, partners, email templates, RAG, or site settings.
- **Groups**: ADMIN_PANEL_ROLES, EVENT_MANAGEMENT_ROLES

### marketer

Content and communications role.

- **Description**: Manages landing pages, email templates, and event visibility. Read-only access to event data.
- **Access**: Admin panel (landing pages, email templates, event listing), preview mode for landing pages.
- **Restrictions**: Cannot create/edit events, manage users, assign judges, or publish results.
- **Groups**: ADMIN_PANEL_ROLES

### mentor

Event participant support role.

- **Description**: Guides teams during active events. Can view team details and projects but cannot score or judge.
- **Access**: Dashboard, event details, team rosters (for assigned events), project submissions.
- **Restrictions**: No admin panel access. Cannot score projects or manage events.
- **Groups**: None (checked individually)

### judge

Scoring and evaluation role.

- **Description**: Evaluates and scores project submissions using weighted rubrics during events.
- **Access**: Judging interface (`/judging/[eventId]`), assigned projects, score submission.
- **Restrictions**: Can only see projects assigned to them. No admin panel access.
- **Groups**: None (checked individually in middleware)

### participant

Default role for all registered users.

- **Description**: The base role assigned to every new user. Can register for events, join teams, submit projects.
- **Access**: Dashboard, event registration, team management, project submission, profile settings.
- **Restrictions**: No admin panel, no judging interface, no partner portal.
- **Groups**: None

### partner

Sponsor/partner organization representative.

- **Description**: Represents a sponsoring organization. Can access the partner portal to view event engagement and analytics.
- **Access**: Partner portal (`/partner`), partner dashboard, event engagement data for their organization.
- **Restrictions**: Can only see data for their own partner organization (filtered by `partnerId` on the user record).
- **Groups**: PARTNER_PORTAL_ROLES

## Role Groups

Role groups simplify permission checks. Instead of checking individual roles, guards check group membership.

```typescript
export const ADMIN_ROLES: UserRole[] = ["super_admin", "admin"];
export const ADMIN_PANEL_ROLES: UserRole[] = ["super_admin", "admin", "organizer", "marketer"];
export const EVENT_MANAGEMENT_ROLES: UserRole[] = ["super_admin", "admin", "organizer"];
export const PARTNER_PORTAL_ROLES: UserRole[] = ["super_admin", "admin", "partner"];
```

## Permissions Matrix

| Capability                    | super_admin | admin | organizer | marketer | mentor | judge | participant | partner |
|-------------------------------|:-----------:|:-----:|:---------:|:--------:|:------:|:-----:|:-----------:|:-------:|
| **Admin Panel Access**        |      Y      |   Y   |     Y     |    Y     |        |       |             |         |
| **Site Settings**             |      Y      |       |           |          |        |       |             |         |
| **User Management**           |      Y      |   Y   |           |          |        |       |             |         |
| **User Ban/Unban**            |      Y      |   Y   |           |          |        |       |             |         |
| **Change User Role**          |      Y      |   Y   |           |          |        |       |             |         |
| **Impersonate User**          |      Y      |   Y   |           |          |        |       |             |         |
| **Create Event**              |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Edit Event**                |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Delete Event**              |      Y      |   Y   |           |          |        |       |             |         |
| **Assign Judges**             |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Publish Results**           |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Manage Feedback Forms**     |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Configure Atlas Prov.**     |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Manage Landing Pages**      |      Y      |   Y   |     Y     |    Y     |        |       |             |         |
| **Preview Landing Pages**     |      Y      |   Y   |     Y     |    Y     |        |       |             |         |
| **Manage Email Templates**    |      Y      |   Y   |           |    Y     |        |       |             |         |
| **Send Test Emails**          |      Y      |   Y   |           |    Y     |        |       |             |         |
| **Manage Partners**           |      Y      |   Y   |           |          |        |       |             |         |
| **RAG Ingestion**             |      Y      |   Y   |           |          |        |       |             |         |
| **Manage Rubric Templates**   |      Y      |   Y   |     Y     |          |        |       |             |         |
| **Score Projects**            |      Y      |   Y   |     Y     |          |        |   Y   |             |         |
| **View Assigned Projects**    |      Y      |   Y   |     Y     |          |   Y    |   Y   |             |         |
| **Register for Events**       |      Y      |   Y   |     Y     |    Y     |   Y    |   Y   |      Y      |    Y    |
| **Submit Projects**           |      Y      |   Y   |     Y     |    Y     |   Y    |   Y   |      Y      |    Y    |
| **Partner Portal Access**     |      Y      |   Y   |           |          |        |       |             |    Y    |
| **Partner Portal (own data)** |             |       |           |          |        |       |             |    Y    |

## Server-Side Guard Functions

| Guard Function          | Allowed Roles                            | Redirect Target |
|-------------------------|------------------------------------------|-----------------|
| `requireSuperAdmin()`   | super_admin                              | /admin          |
| `requireAdmin()`        | super_admin, admin                       | /dashboard      |
| `requireAdminPanel()`   | super_admin, admin, organizer, marketer  | /dashboard      |
| `requirePartner()`      | super_admin, admin, partner              | /dashboard      |
| `hasRole(...roles)`     | Any specified roles (returns boolean)    | N/A             |
| `isUserAdmin()`         | super_admin, admin (returns boolean)     | N/A             |

## Edge Middleware Route Protection

| Route Pattern          | Allowed Roles                               |
|------------------------|---------------------------------------------|
| `/admin/*`             | super_admin, admin, organizer, marketer     |
| `/judging/*`           | super_admin, admin, organizer, judge        |
| `/partner/*`           | super_admin, admin, partner                 |
| `/partner/register`    | Anyone (excluded from partner auth check)   |
| `?preview` query param | super_admin, admin, organizer, marketer     |

## Impersonation

Admins (admin, super_admin) can impersonate other users by setting the `impersonate_user_id` httpOnly cookie. During impersonation:

- The session swaps to the impersonated user's identity
- `session.user.isImpersonating` is set to `true`
- `session.user.realAdminId` preserves the admin's user ID
- `session.user.realAdminRole` preserves the admin's actual role
- Guard functions use `effectiveRole()` which checks `realAdminRole` when impersonating, so admin access is never lost during impersonation

## Adding a New Role

1. Add the role string to the `UserRole` type in `src/lib/admin-guard.ts`
2. Add it to the `role` enum in the User model schema
3. Add it to the appropriate role group(s) in `admin-guard.ts`
4. Add route protection in `src/middleware.ts` if the role needs its own section
5. Update the NextAuth type declarations in `src/types/next-auth.d.ts` if needed
6. No database migration is required -- existing users will not have the new role
