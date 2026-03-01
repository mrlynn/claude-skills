# Email Template Catalog

All 9 built-in email templates used by the platform. Each template is stored in MongoDB as an `EmailTemplate` document and has a hardcoded fallback function for resilience. Templates use `{{variable}}` for interpolation and `{{#if variable}}...{{/if}}` for conditional blocks.

## Template Index

| Key                       | Category     | When Sent                                      |
|---------------------------|-------------|-------------------------------------------------|
| `magic_link`              | auth         | User requests passwordless sign-in               |
| `two_factor_code`         | auth         | User with 2FA enabled signs in                   |
| `email_verification`      | auth         | New user registers or requests email verification |
| `feedback_request`        | event        | Admin triggers feedback collection for an event   |
| `notification`            | notification | System sends a general notification               |
| `registration_confirmation` | event      | User successfully registers for an event          |
| `partner_invite`          | partner      | Admin invites a contact to join a partner org     |
| `partner_access_approved` | partner      | Admin approves a partner access request           |
| `partner_access_denied`   | partner      | Admin denies a partner access request             |

---

## 1. magic_link

**Category:** auth
**When sent:** User clicks "Sign in with email link" on the login page. The system generates a SHA-256 hashed token, stores it on the user record with a 15-minute expiry, and emails the raw link.

**Example subject:** `Sign in to Your App`

### Required Variables

| Variable   | Type   | Description                                    |
|------------|--------|------------------------------------------------|
| `userName` | string | Recipient's display name (falls back to "there") |
| `url`      | string | Full magic link URL with token and email params  |

### Optional Variables

None.

### Notes

- The link expires in 15 minutes
- Tokens are single-use: cleared after successful authentication
- The URL includes both the token and email as query parameters

---

## 2. two_factor_code

**Category:** auth
**When sent:** During the credentials sign-in flow, after password validation succeeds but before the session is created. Only triggered when `user.twoFactorEnabled === true`. The authorize function generates a 6-digit code, hashes it with SHA-256, stores the hash, and sends the raw code via email.

**Example subject:** `Your verification code`

### Required Variables

| Variable   | Type   | Description                           |
|------------|--------|---------------------------------------|
| `userName` | string | Recipient's display name              |
| `code`     | string | 6-digit numeric verification code     |

### Optional Variables

None.

### Notes

- Code expires in 10 minutes
- The email is sent fire-and-forget (`.catch(() => {})`) so SMTP failures do not block the auth flow
- The `authorize()` function returns `null` after sending the code, signaling the client to show the 2FA input form

---

## 3. email_verification

**Category:** auth
**When sent:** After a new user registers or when an existing user requests to verify their email address. The system generates a verification token, hashes it, and stores the hash on the user record.

**Example subject:** `Verify your email address`

### Required Variables

| Variable          | Type   | Description                                  |
|-------------------|--------|----------------------------------------------|
| `userName`        | string | Recipient's display name                     |
| `verificationUrl` | string | Full URL to the email verification endpoint  |

### Optional Variables

None.

### Notes

- Verification tokens typically expire in 24 hours
- Part of the fire-and-forget post-registration processing pipeline

---

## 4. feedback_request

**Category:** event
**When sent:** Admin clicks "Send Feedback Requests" for an event. The system sends personalized emails to all participants (and optionally partners) with a link to the feedback form.

**Example subject:** `We'd love your feedback on {{eventName}}`

### Required Variables

| Variable        | Type   | Description                              |
|-----------------|--------|------------------------------------------|
| `recipientName` | string | Recipient's display name                 |
| `eventName`     | string | Name of the event requesting feedback    |
| `formUrl`       | string | Direct URL to the feedback form          |

### Optional Variables

| Variable    | Type   | Description                              |
|-------------|--------|------------------------------------------|
| `eventDate` | string | Formatted date range of the event        |
| `deadline`  | string | Feedback submission deadline             |

### Notes

- Sent in bulk but each email is personalized with the recipient's name
- The formUrl should include the participant's ID or a unique token for pre-authentication

---

## 5. notification

**Category:** notification
**When sent:** Generic notification template used for system-generated notifications such as team invitations, project status changes, event updates, and admin announcements.

**Example subject:** `{{title}}`

### Required Variables

| Variable   | Type   | Description                                |
|------------|--------|--------------------------------------------|
| `userName` | string | Recipient's display name                   |
| `title`    | string | Notification title (also used as subject)  |
| `message`  | string | Notification body text                     |

### Optional Variables

| Variable    | Type   | Description                                |
|-------------|--------|--------------------------------------------|
| `actionUrl` | string | CTA button URL (button hidden if missing)  |
| `actionText`| string | CTA button label (defaults to "View")      |

### Notes

- The most flexible template -- used as a fallback when no specific template exists
- The `actionUrl` triggers a conditional block: `{{#if actionUrl}}...{{/if}}`

---

## 6. registration_confirmation

**Category:** event
**When sent:** Immediately after a user successfully registers for an event. Part of the fire-and-forget post-registration pipeline alongside embedding generation and notification creation.

**Example subject:** `You're registered for {{eventName}}!`

### Required Variables

| Variable        | Type   | Description                                   |
|-----------------|--------|-----------------------------------------------|
| `userName`      | string | Recipient's display name                      |
| `eventName`     | string | Name of the event                             |
| `eventDate`     | string | Formatted date/date range of the event        |
| `eventLocation` | string | Venue/location or "Virtual"                   |
| `dashboardUrl`  | string | URL to the user's event dashboard             |

### Optional Variables

| Variable      | Type   | Description                                    |
|---------------|--------|------------------------------------------------|
| `teamName`    | string | Team name if auto-assigned                     |
| `eventRules`  | string | Brief event rules or link to rules page        |

### Notes

- Sent fire-and-forget so registration is not blocked by email delivery
- The dashboardUrl typically points to `/events/[eventId]` with the user's view

---

## 7. partner_invite

**Category:** partner
**When sent:** Admin invites a new contact to join a partner organization. The invite includes a link to the partner registration page where the contact can create an account and request access.

**Example subject:** `You're invited to join {{companyName}} on our platform`

### Required Variables

| Variable      | Type   | Description                                    |
|---------------|--------|------------------------------------------------|
| `userName`    | string | Invited contact's name                         |
| `companyName` | string | Partner organization name                      |
| `url`         | string | Partner registration URL (may include invite token) |

### Optional Variables

| Variable    | Type   | Description                                     |
|-------------|--------|-------------------------------------------------|
| `inviterName` | string | Name of the admin who sent the invitation     |
| `message`   | string | Personal message from the inviter              |

### Notes

- The URL typically points to `/partner/register?invite=TOKEN&company=NAME`
- The invited user still needs to create an account and be approved

---

## 8. partner_access_approved

**Category:** partner
**When sent:** Admin approves a partner access request. The user's role is changed to `partner`, their `partnerId` is set, and this email is sent with a link to the partner portal.

**Example subject:** `Your partner access has been approved`

### Required Variables

| Variable      | Type   | Description                                  |
|---------------|--------|----------------------------------------------|
| `userName`    | string | Approved user's display name                 |
| `companyName` | string | Partner organization name                    |
| `portalUrl`   | string | Direct URL to the partner portal dashboard   |

### Optional Variables

None.

### Notes

- The portalUrl typically points to `/partner`
- At this point the user already has an account -- only their role and partnerId are updated

---

## 9. partner_access_denied

**Category:** partner
**When sent:** Admin denies a partner access request. The user is notified with an optional explanation.

**Example subject:** `Update on your partner access request`

### Required Variables

| Variable   | Type   | Description                           |
|------------|--------|---------------------------------------|
| `userName` | string | Denied user's display name            |

### Optional Variables

| Variable | Type   | Description                                     |
|----------|--------|-------------------------------------------------|
| `notes`  | string | Reviewer's feedback explaining the denial reason |

### Notes

- The `notes` variable uses a conditional block: only shown if the admin provides feedback
- The user's role remains unchanged (stays as participant or whatever it was)

---

## Admin Template Management

Templates are managed via API routes:

| Endpoint                                        | Method | Purpose                    |
|-------------------------------------------------|--------|----------------------------|
| `/api/admin/email-templates`                    | GET    | List all templates         |
| `/api/admin/email-templates`                    | POST   | Create custom template     |
| `/api/admin/email-templates/[id]`               | GET    | Get template by ID         |
| `/api/admin/email-templates/[id]`               | PATCH  | Update template            |
| `/api/admin/email-templates/[id]`               | DELETE | Delete (non-built-in only) |
| `/api/admin/email-templates/[id]/preview`       | POST   | Render preview with vars   |
| `/api/admin/email-templates/[id]/test-send`     | POST   | Send test to admin email   |

### Preview

POST body: `{ "variables": { "userName": "Alice", "url": "https://..." } }`
Response: `{ "subject": "...", "html": "...", "text": "..." }`

### Test Send

POST body: `{ "variables": {...}, "recipientEmail": "test@example.com" }` (optional recipientEmail, defaults to admin's email)
The subject is prefixed with `[TEST]`. Missing variables are auto-filled from the template's variable definitions using the `example` field.
