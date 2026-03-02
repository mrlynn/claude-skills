---
name: mongodb-email-system
description: Add transactional email with DB-backed templates, variable interpolation, hardcoded fallbacks, SMTP singleton transport, and admin template management to a Next.js + MongoDB app
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: email
  updated: 2026-03-01
  python-tools: template_variable_checker.py
  tech-stack: nodemailer, smtp, mongodb, handlebars-style
---

# mongodb-email-system

## Trigger

Use this skill when adding transactional email to a Next.js + MongoDB app. Covers SMTP transport, DB-backed templates with variable interpolation, hardcoded fallbacks, template seeding, admin CRUD, preview, and test-send.

> *Every app needs email eventually, and every time it's a mess. DB-backed templates with hardcoded fallbacks means the app never sends a blank email even if someone deletes a template.* — ML

## Overview

Every DevRel project that touches users needs transactional email: verification, magic links, event confirmations, feedback requests, partner invitations. This skill provides a complete email system with DB-backed templates that can be edited by admins, with hardcoded fallback templates for reliability.

## How to Use

### Quick Start
Invoke with `/mongodb-email-system` or let Claude auto-activate when adding transactional email.

### Python Tools
- `scripts/template_variable_checker.py` — Parse email templates and report missing/unused variables

### Reference Docs
- `references/template-catalog.md` — All 9 built-in templates with variables and previews

### Templates & Samples
- `assets/sample-email-template.html` — Starter HTML email with MongoDB branding
- `assets/expected_template_output.json` — Sample EmailTemplate document

## Architecture Decisions

- **DB-backed templates with hardcoded fallbacks**: Templates live in MongoDB for admin editing, but if the DB is down or a template hasn't been seeded yet, hardcoded functions take over. This makes email delivery resilient.
- **Lazy seeding**: Templates are seeded to the DB on first miss, not on app startup. This avoids migration scripts and works in serverless.
- **Singleton transporter**: Nodemailer's SMTP transporter is reused across requests to avoid reconnection overhead.
- **Fire-and-forget sends**: Non-critical emails (2FA codes, notifications) use `.catch(() => {})` so failures don't block the main flow.
- **Handlebars-style interpolation**: Templates use `{{variable}}` and `{{#if variable}}...{{/if}}` — simple enough to not need a full template engine dependency.

## File Structure

```
src/lib/
├── email/
│   ├── email-service.ts        # SMTP singleton + sendEmail()
│   ├── template-renderer.ts    # DB lookup + interpolation + fallback
│   ├── templates.ts            # Hardcoded fallback templates
│   └── seed-email-templates.ts # DB seeder (upsert)
└── db/models/
    └── EmailTemplate.ts        # Template model
```

## Code Patterns

### Pattern 1: SMTP Singleton Transport

```typescript
// src/lib/email/email-service.ts
import nodemailer from "nodemailer";
import type { Transporter } from "nodemailer";

interface EmailOptions {
  to: string;
  subject: string;
  html: string;
  text?: string;
}

let transporter: Transporter | null = null;

function getTransporter(): Transporter | null {
  if (transporter) return transporter;

  const host = process.env.SMTP_HOST;
  const port = parseInt(process.env.SMTP_PORT || "587", 10);
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;

  if (!host || !user || !pass) {
    console.warn("Email service: SMTP not configured. Emails will not be sent.");
    return null;
  }

  transporter = nodemailer.createTransport({
    host,
    port,
    secure: port === 465,
    auth: { user, pass },
  });

  return transporter;
}

export async function sendEmail(options: EmailOptions): Promise<boolean> {
  const transport = getTransporter();
  if (!transport) return false;

  const from = process.env.EMAIL_FROM || "App <noreply@example.com>";

  try {
    await transport.sendMail({
      from,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
    });
    return true;
  } catch (error) {
    console.error("Email service: Failed to send:", error);
    return false;
  }
}
```

### Pattern 2: Template Renderer with DB + Fallback

```typescript
// src/lib/email/template-renderer.ts
import { connectToDatabase } from "@/lib/db/connection";
import { EmailTemplateModel } from "@/lib/db/models/EmailTemplate";
import { seedEmailTemplates } from "./seed-email-templates";
import * as fallbackTemplates from "./templates";

let seeded = false;

function interpolate(template: string, variables: Record<string, string>): string {
  // Handle {{#if variable}}...{{/if}} blocks
  let result = template.replace(
    /\{\{#if (\w+)\}\}([\s\S]*?)\{\{\/if\}\}/g,
    (_match, varName, content) => (variables[varName] ? content : "")
  );
  // Replace {{variable}} placeholders
  result = result.replace(/\{\{(\w+)\}\}/g, (_match, varName) => variables[varName] ?? "");
  return result;
}

export async function renderEmailTemplate(
  key: string,
  variables: Record<string, string>
): Promise<{ subject: string; html: string; text: string }> {
  try {
    await connectToDatabase();
    let template = await EmailTemplateModel.findOne({ key }).lean();
    if (!template && !seeded) {
      await seedEmailTemplates();
      seeded = true;
      template = await EmailTemplateModel.findOne({ key }).lean();
    }
    if (template) {
      return {
        subject: interpolate(template.subject, variables),
        html: interpolate(template.htmlBody, variables),
        text: interpolate(template.textBody, variables),
      };
    }
  } catch (error) {
    console.error(`Template renderer: DB lookup failed for "${key}":`, error);
  }
  return renderFallback(key, variables);
}

function renderFallback(key: string, vars: Record<string, string>): { subject: string; html: string; text: string } {
  switch (key) {
    case "magic_link":
      return fallbackTemplates.magicLinkEmail(vars.userName || "there", vars.url || "");
    case "email_verification":
      return fallbackTemplates.emailVerificationEmail(vars.userName || "there", vars.verificationUrl || "");
    default:
      return {
        subject: "Notification",
        html: `<p>${vars.message || "You have a new notification."}</p>`,
        text: vars.message || "You have a new notification.",
      };
  }
}
```

### Pattern 3: EmailTemplate Model

```typescript
// src/lib/db/models/EmailTemplate.ts
import mongoose, { Schema, Document, Types } from "mongoose";

export interface IEmailTemplateVariable {
  name: string;
  required: boolean;
  description: string;
  example: string;
}

export interface IEmailTemplate extends Document {
  key: string;
  name: string;
  category: "auth" | "event" | "partner" | "notification";
  description: string;
  subject: string;
  htmlBody: string;
  textBody: string;
  variables: IEmailTemplateVariable[];
  isBuiltIn: boolean;
  updatedBy?: Types.ObjectId;
  createdAt: Date;
  updatedAt: Date;
}

const EmailTemplateSchema = new Schema<IEmailTemplate>(
  {
    key: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    category: { type: String, enum: ["auth", "event", "partner", "notification"], required: true },
    description: { type: String, default: "" },
    subject: { type: String, required: true },
    htmlBody: { type: String, required: true },
    textBody: { type: String, required: true },
    variables: [{
      name: { type: String, required: true },
      required: { type: Boolean, default: true },
      description: { type: String, default: "" },
      example: { type: String, default: "" },
    }],
    isBuiltIn: { type: Boolean, default: false },
    updatedBy: { type: Schema.Types.ObjectId, ref: "User" },
  },
  { timestamps: true }
);

EmailTemplateSchema.index({ key: 1 }, { unique: true });
EmailTemplateSchema.index({ category: 1 });

export const EmailTemplateModel =
  mongoose.models.EmailTemplate || mongoose.model<IEmailTemplate>("EmailTemplate", EmailTemplateSchema);
```

### Pattern 4: Hardcoded Email Templates with Brand Layout

```typescript
// src/lib/email/templates.ts
const brandColor = "#00684A"; // MongoDB Forest Green
const bgColor = "#f5f5f5";

function layout(content: string): string {
  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:${bgColor};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:${bgColor};padding:40px 20px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff;border-radius:8px;overflow:hidden;">
        <tr><td style="background:${brandColor};padding:24px 32px;">
          <span style="color:#fff;font-size:20px;font-weight:700;">Your App Name</span>
        </td></tr>
        <tr><td style="padding:32px;">${content}</td></tr>
        <tr><td style="padding:16px 32px;background:#fafafa;border-top:1px solid #eee;">
          <span style="color:#999;font-size:12px;">This is an automated message.</span>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>`;
}

export function magicLinkEmail(name: string, url: string) {
  return {
    subject: "Sign in to Your App",
    html: layout(`
      <h2 style="margin:0 0 16px;color:#333;font-size:22px;">Hi ${name},</h2>
      <p style="color:#555;font-size:15px;line-height:1.6;margin:0 0 24px;">
        Click below to sign in. This link expires in 15 minutes.
      </p>
      <a href="${url}" style="display:inline-block;background:${brandColor};color:#fff;padding:12px 32px;border-radius:6px;text-decoration:none;font-weight:600;">Sign In</a>
      <p style="color:#999;font-size:13px;margin:24px 0 0;">If you didn't request this, ignore this email.</p>
    `),
    text: `Hi ${name},\n\nSign in: ${url}\n\nExpires in 15 minutes.`,
  };
}

// Additional template functions follow the same pattern:
// twoFactorCodeEmail, emailVerificationEmail, feedbackRequestEmail,
// notificationEmail, registrationConfirmationEmail, partnerInviteEmail,
// partnerAccessApprovedEmail, partnerAccessDeniedEmail
```

### Pattern 5: Admin Template Routes

```
src/app/api/admin/email-templates/
├── route.ts                      # GET (list), POST (create)
└── [id]/
    ├── route.ts                  # GET, PATCH, DELETE
    ├── preview/route.ts          # POST — render without sending
    └── test-send/route.ts        # POST — send test email
```

**Preview route** renders the template with provided variables and returns `{ subject, html, text }` without sending.

**Test-send route** renders and sends to the admin's email (or a custom recipient), prepending `[TEST]` to the subject. Auto-fills missing variables with example values from the template's `variables` array.

## Built-in Template Keys

| Key | Category | Variables |
|-----|----------|-----------|
| `magic_link` | auth | userName, url |
| `two_factor_code` | auth | userName, code |
| `email_verification` | auth | userName, verificationUrl |
| `feedback_request` | event | recipientName, eventName, formUrl |
| `notification` | notification | userName, title, message, actionUrl |
| `registration_confirmation` | event | userName, eventName, eventDate, eventLocation, dashboardUrl |
| `partner_invite` | partner | userName, companyName, url |
| `partner_access_approved` | partner | userName, companyName, portalUrl |
| `partner_access_denied` | partner | userName, notes |

## Environment Variables

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-api-key
EMAIL_FROM="Your App <noreply@yourdomain.com>"
```

## Dependencies

```bash
npm install nodemailer
npm install -D @types/nodemailer
```

## Common Pitfalls

- **Don't block on non-critical email sends.** Use `sendEmail({...}).catch(() => {})` for 2FA codes, notifications, etc.
- **Don't hardcode brand colors in individual templates.** Use the `layout()` wrapper with `brandColor` constant so updates propagate.
- **Don't forget the text fallback.** Every template must provide both HTML and plain text for email clients that don't render HTML.
- **Don't edit built-in templates via the API** without the `isBuiltIn` guard. Admin CRUD should prevent deletion of built-in templates.
- **Use `select: false` pattern** for template variables with sensitive defaults (API keys, tokens).
