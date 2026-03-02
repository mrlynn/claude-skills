---
name: mongodb-partner-portal
description: Add sponsor/partner management with 5-tier system, multiple contacts, engagement tracking, access request workflows, and partner-specific RBAC
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: partner-management
  updated: 2026-03-01
  python-tools: tier_report_generator.py
  tech-stack: mongoose, zod, rbac
---

# mongodb-partner-portal

## Trigger

Use this skill when adding sponsor/partner management to a platform: partner CRUD with tier system, contact management, engagement tracking, access request workflows, and partner-specific RBAC.

> *Sponsor management is the feature nobody thinks about until a VP asks "how many Gold partners renewed?" and you're querying raw JSON.* — ML

## Overview

Every hackathon, conference, and community program has sponsors. This skill provides a complete partner management system with 5-tier sponsorship levels, multiple contacts per organization, engagement tracking across events, and a partner portal with role-gated access. It integrates with the RBAC system (partner role) and email system (partner invite/approval/denial templates).

## How to Use

### Quick Start
Invoke with `/mongodb-partner-portal` or let Claude auto-activate when adding sponsor/partner management.

### Python Tools
- `scripts/tier_report_generator.py` — Generate partner engagement summary from JSON data

### Reference Docs
- `references/tier-system.md` — 5-tier sponsorship: perks, colors, sort order

### Templates & Samples
- `assets/sample_partner.json` — Example Partner document
- `assets/tier-badge-colors.json` — Tier-to-color mapping for UI

## Architecture Decisions

- **5-tier system (platinum → community)**: Tiers control visibility, placement, and perks. The tier name maps to UI styling (badge colors, sort order).
- **Multiple contacts per partner**: Organizations have multiple representatives. One is marked `isPrimary` for default communication.
- **Bidirectional engagement sync**: When an event adds a partner, `$addToSet` updates the partner's `engagement.eventsParticipated` array. This maintains a denormalized view for partner dashboards.
- **Access request workflow**: External users can request partner access. Admins approve/deny, triggering email notifications. Approved users get the `partner` role and `partnerId` on their user record.
- **Compound indexes**: `tier + status` is the most common query pattern (e.g., "show all active gold partners").

## Code Patterns

### Pattern 1: Partner Model

```typescript
// src/lib/db/models/Partner.ts
import mongoose, { Schema, Document, Types } from "mongoose";

export interface IPartner extends Document {
  name: string;
  description: string;
  logo?: string;
  website?: string;
  industry: string;
  tier: "platinum" | "gold" | "silver" | "bronze" | "community";
  status: "active" | "inactive" | "pending";
  companyInfo: {
    size?: "startup" | "small" | "medium" | "large" | "enterprise";
    headquarters?: string;
    foundedYear?: number;
    employeeCount?: string;
  };
  contacts: Array<{
    name: string;
    email: string;
    phone?: string;
    role: string;
    isPrimary: boolean;
  }>;
  engagement: {
    eventsParticipated: Types.ObjectId[];
    prizesOffered: Types.ObjectId[];
    totalContribution?: number;
    engagementLevel?: "low" | "medium" | "high";
    lastEngagementDate?: Date;
  };
  social?: { linkedin?: string; twitter?: string; github?: string; youtube?: string };
  tags: string[];
  notes?: string;
}

const PartnerSchema = new Schema<IPartner>({
  name: { type: String, required: true, unique: true },
  description: { type: String, required: true },
  logo: { type: String },
  website: { type: String },
  industry: { type: String, required: true },
  tier: { type: String, enum: ["platinum", "gold", "silver", "bronze", "community"], default: "bronze" },
  status: { type: String, enum: ["active", "inactive", "pending"], default: "pending" },
  companyInfo: {
    size: { type: String, enum: ["startup", "small", "medium", "large", "enterprise"] },
    headquarters: String, foundedYear: Number, employeeCount: String,
  },
  contacts: [{
    name: { type: String, required: true },
    email: { type: String, required: true },
    phone: String,
    role: { type: String, required: true },
    isPrimary: { type: Boolean, default: false },
  }],
  engagement: {
    eventsParticipated: [{ type: Schema.Types.ObjectId, ref: "Event" }],
    prizesOffered: [{ type: Schema.Types.ObjectId, ref: "Prize" }],
    totalContribution: Number,
    engagementLevel: { type: String, enum: ["low", "medium", "high"] },
    lastEngagementDate: Date,
  },
  social: { linkedin: String, twitter: String, github: String, youtube: String },
  tags: [{ type: String }],
  notes: { type: String },
}, { timestamps: true });

PartnerSchema.index({ tier: 1, status: 1 });
PartnerSchema.index({ industry: 1 });
PartnerSchema.index({ status: 1 });
PartnerSchema.index({ "engagement.engagementLevel": 1 });
PartnerSchema.index({ "contacts.email": 1 });
PartnerSchema.index({ tags: 1 });

export const PartnerModel = mongoose.models.Partner || mongoose.model<IPartner>("Partner", PartnerSchema);
```

### Pattern 2: Partner Zod Schema

```typescript
export const createPartnerSchema = z.object({
  name: z.string().min(2).max(200),
  description: z.string().min(10).max(2000),
  logo: z.string().url().optional(),
  website: z.string().url().optional(),
  industry: z.string().min(2).max(100),
  tier: z.enum(["platinum", "gold", "silver", "bronze", "community"]).default("bronze"),
  status: z.enum(["active", "inactive", "pending"]).default("pending"),
  companyInfo: z.object({
    size: z.enum(["startup", "small", "medium", "large", "enterprise"]).optional(),
    headquarters: z.string().max(200).optional(),
    foundedYear: z.number().int().min(1800).max(new Date().getFullYear()).optional(),
    employeeCount: z.string().max(50).optional(),
  }).optional(),
  contacts: z.array(z.object({
    name: z.string().min(2).max(100),
    email: z.string().email(),
    phone: z.string().max(30).optional(),
    role: z.string().min(2).max(100),
    isPrimary: z.boolean().default(false),
  })).min(1).max(10),
  social: z.object({
    linkedin: z.string().url().optional(),
    twitter: z.string().url().optional(),
    github: z.string().url().optional(),
    youtube: z.string().url().optional(),
  }).optional(),
  tags: z.array(z.string()).max(20).default([]),
  notes: z.string().max(5000).optional(),
});

export const updatePartnerSchema = createPartnerSchema.partial();
```

### Pattern 3: Partner RBAC Integration

From the `mongodb-rbac-middleware` skill:

```typescript
// Role group for partner portal access
export const PARTNER_PORTAL_ROLES: UserRole[] = ["super_admin", "admin", "partner"];

// Server-side guard
export async function requirePartner() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const role = effectiveRole(session.user);
  if (!PARTNER_PORTAL_ROLES.includes(role) && !(await isImpersonationActive())) redirect("/dashboard");
  return session;
}

// Edge middleware route protection
if (pathname.startsWith("/partner") && !pathname.startsWith("/partner/register")) {
  // Require partner, admin, or super_admin role
}
```

### Pattern 4: Partner Email Templates

Three built-in email templates for the partner workflow:

| Template Key | When Sent | Variables |
|-------------|-----------|-----------|
| `partner_invite` | Admin invites a new partner contact | userName, companyName, url |
| `partner_access_approved` | Admin approves a partner access request | userName, companyName, portalUrl |
| `partner_access_denied` | Admin denies a partner access request | userName, notes (optional reviewer feedback) |

### Pattern 5: Event-Partner Bidirectional Sync

```typescript
// When creating an event with partners:
if (eventData.partners?.length) {
  await PartnerModel.updateMany(
    { _id: { $in: eventData.partners } },
    {
      $addToSet: { "engagement.eventsParticipated": event._id },
      $set: { "engagement.lastEngagementDate": new Date() },
    }
  );
}
```

### Pattern 6: Tier Badge Colors

For UI rendering, map tiers to display colors:

```typescript
const TIER_COLORS: Record<string, string> = {
  platinum: "#B0B0B0",  // Silver-gray
  gold: "#FFD700",      // Gold
  silver: "#C0C0C0",    // Silver
  bronze: "#CD7F32",    // Bronze
  community: "#00ED64", // MongoDB Spring Green
};
```

## Dependencies

No additional dependencies beyond the scaffold.

## Common Pitfalls

- **Use `$addToSet` not `$push`** for engagement arrays to prevent duplicate entries.
- **Require at least 1 contact** in the Zod schema (`.min(1)`). A partner without a contact is useless.
- **Exclude `/partner/register` from auth middleware.** New partners need to access the registration page before they have an account.
- **Use `unique: true` on partner name** to prevent duplicate organizations. Handle the duplicate key error (E11000) gracefully.
- **Set `isPrimary: true` on exactly one contact.** The UI should enforce this, and the API should validate it.
