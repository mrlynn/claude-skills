---
name: mongodb-event-platform
description: Build event/hackathon management with lifecycle states, multi-step registration, dynamic feedback forms, weighted judging rubrics, and landing pages with slug-based routing
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: event-management
  updated: 2026-03-01
  python-tools: feedback_form_generator.py
  tech-stack: nextjs, mongoose, zod, geospatial
---

# mongodb-event-platform

## Trigger

Use this skill when building event/hackathon/workshop/conference management features: event CRUD with lifecycle states, multi-step registration with capacity management, dynamic feedback forms, judging rubrics with weighted scoring, and landing pages with slug-based routing.

> *This is the big one. Lifecycle states, registration flows, judging rubrics, feedback forms — basically everything I learned running hackathons for 3 years, codified.* — ML

## Overview

MongoDB DevRel runs hackathons, .local conferences, community days, workshops, and meetups. This skill covers them all with a flexible Event model that supports the full lifecycle from draft to conclusion, customizable registration flows, dynamic feedback collection, judging with weighted rubrics, and a landing page builder with content sections.

## How to Use

### Quick Start
Invoke with `/mongodb-event-platform` or let Claude auto-activate when building event management features.

### Python Tools
- `scripts/feedback_form_generator.py` — Generate FeedbackFormConfig JSON from a simple YAML spec

### Reference Docs
- `references/event-lifecycle.md` — State machine: draft → open → in_progress → concluded
- `references/registration-flow.md` — 3-tier registration wizard flow + capacity checks

### Templates & Samples
- `assets/sample_event.json` — Example Event document with all fields
- `assets/sample_feedback_form.json` — Example FeedbackFormConfig
- `assets/sample_rubric.json` — Example judging rubric with weighted criteria

## Architecture Decisions

- **Lifecycle states (draft → open → in_progress → concluded)**: Events flow through defined states. Registration is only allowed when status is "open". Results are published when status is "concluded".
- **3-tier registration wizard**: Tier 1 is always shown (email, password, terms). Tier 2 is configurable (skills, github, bio). Tier 3 is fully custom questions per event. This balances simplicity for casual events with depth for competitive hackathons.
- **Session-persisted wizard progress**: Registration progress is stored in `sessionStorage` so users can navigate away and return without losing their input.
- **Dynamic feedback forms with 6 question types**: Forms are configured as JSON documents (sections → questions), not hardcoded. Admins can create forms with any combination of short_text, long_text, multiple_choice, checkbox, linear_scale, and rating questions.
- **Weighted judging rubrics**: Each rubric criterion has a weight and maxScore, enabling normalized scoring across different evaluation dimensions.
- **Landing page slug routing**: Events can have public landing pages at `/{slug}` with customizable hero, about, prizes, schedule, sponsors, and FAQ sections.
- **Geospatial indexing**: Events store coordinates with a 2dsphere index for map-based discovery.

## Code Patterns

### Pattern 1: Event Model

```typescript
// src/lib/db/models/Event.ts
import mongoose, { Schema, Document, Types } from "mongoose";

export interface IEvent extends Document {
  name: string;
  description: string;
  theme: string;
  startDate: Date;
  endDate: Date;
  registrationDeadline: Date;
  submissionDeadline?: Date;
  location: string;
  city?: string;
  country?: string;
  coordinates?: { type: "Point"; coordinates: [number, number] };
  venue?: string;
  capacity: number;
  isVirtual: boolean;
  tags: string[];
  rules: string;
  judging_criteria: string[];
  judgingRubric?: { name: string; description: string; weight: number; maxScore: number }[];
  organizers: Types.ObjectId[];
  partners: Types.ObjectId[];
  status: "draft" | "open" | "in_progress" | "concluded";
  resultsPublished: boolean;
  resultsPublishedAt?: Date;
  feedbackForms?: { participant?: Types.ObjectId; partner?: Types.ObjectId };
  atlasProvisioning?: {
    enabled: boolean;
    defaultProvider: 'AWS' | 'GCP' | 'AZURE';
    defaultRegion: string;
    openNetworkAccess: boolean;
    maxDbUsersPerCluster: number;
    autoCleanupOnEventEnd: boolean;
  };
  descriptionEmbedding?: number[];
  landingPage?: {
    template: string;
    slug: string;
    published: boolean;
    registrationFormConfig?: Types.ObjectId;
    customContent: {
      hero?: { headline?: string; subheadline?: string; ctaText?: string; backgroundImage?: string };
      about?: string;
      prizes?: Array<{ title: string; description: string; value?: string }>;
      schedule?: Array<{ time: string; title: string; description?: string }>;
      sponsors?: Array<{ name: string; logo: string; tier: string }>;
      faq?: Array<{ question: string; answer: string }>;
    };
  };
}

// Key indexes:
// EventSchema.index({ status: 1 });
// EventSchema.index({ startDate: 1 });
// EventSchema.index({ tags: 1 });
// EventSchema.index({ coordinates: "2dsphere" });
// EventSchema.index({ country: 1, city: 1 });
// EventSchema.index({ "landingPage.published": 1 });
// landingPage.slug has unique: true, sparse: true
```

### Pattern 2: Dynamic Feedback Form Config

```typescript
// src/lib/db/models/FeedbackFormConfig.ts
export interface IScaleConfig {
  min: number; max: number; minLabel: string; maxLabel: string;
}

export interface IFeedbackQuestion {
  id: string;
  type: "short_text" | "long_text" | "multiple_choice" | "checkbox" | "linear_scale" | "rating";
  label: string;
  description: string;
  required: boolean;
  placeholder: string;
  options: string[];          // For multiple_choice and checkbox
  scaleConfig?: IScaleConfig; // For linear_scale and rating
}

export interface IFeedbackSection {
  id: string;
  title: string;
  description: string;
  questions: IFeedbackQuestion[];
}

export interface IFeedbackFormConfig extends Document {
  name: string;
  slug: string;               // Unique URL identifier
  description: string;
  isBuiltIn: boolean;
  createdBy?: Types.ObjectId;
  targetAudience: "participant" | "partner" | "both";
  sections: IFeedbackSection[];
}
```

### Pattern 3: 3-Tier Registration Form Config

```typescript
// src/lib/db/models/RegistrationFormConfig.ts
interface ICustomQuestion {
  id: string;
  label: string;
  type: "text" | "select" | "multiselect" | "checkbox";
  options: string[];
  required: boolean;
  placeholder: string;
}

export interface IRegistrationFormConfig extends Document {
  name: string;
  slug: string;
  description: string;
  isBuiltIn: boolean;

  tier1: {
    showExperienceLevel: boolean;
    customQuestions: ICustomQuestion[]; // Max 2
  };

  tier2: {
    enabled: boolean;
    prompt: string;          // "Help us match you with a great team"
    showSkills: boolean;
    showGithub: boolean;
    showBio: boolean;
    customQuestions: ICustomQuestion[];
  };

  tier3: {
    enabled: boolean;
    prompt: string;          // "A few more questions from organizers"
    customQuestions: ICustomQuestion[];
  };
}
```

### Pattern 4: Event CRUD API Route

```typescript
// src/app/api/admin/events/route.ts
import { NextRequest } from "next/server";
import { auth } from "@/lib/auth";
import { connectToDatabase } from "@/lib/db/connection";
import { EventModel } from "@/lib/db/models/Event";
import { PartnerModel } from "@/lib/db/models/Partner";
import { createEventSchema } from "@/lib/db/schemas";
import { errorResponse, successResponse } from "@/lib/utils";

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    const role = (session?.user as { role?: string })?.role;
    if (!role || !["admin", "super_admin", "organizer"].includes(role)) {
      return errorResponse("Forbidden", 403);
    }

    const body = await request.json();
    const parsed = createEventSchema.safeParse(body);
    if (!parsed.success) return errorResponse(parsed.error.errors[0].message, 422);

    await connectToDatabase();

    // Auto-add current user as organizer
    const userId = (session!.user as { id: string }).id;
    const eventData = { ...parsed.data, organizers: [userId] };

    const event = await EventModel.create(eventData);

    // Sync partner engagement (bidirectional)
    if (parsed.data.partners?.length) {
      await PartnerModel.updateMany(
        { _id: { $in: parsed.data.partners } },
        { $addToSet: { "engagement.eventsParticipated": event._id } }
      );
    }

    return successResponse(event, 201);
  } catch (error) {
    console.error("POST /api/admin/events error:", error);
    return errorResponse("Internal server error", 500);
  }
}
```

### Pattern 5: Registration Flow

```typescript
// Key registration logic from src/app/api/events/[eventId]/register/route.ts
// 1. Validate event exists, status === "open", deadline not passed, capacity not reached
// 2. Resolve user: find by email or create new (atomic transaction for new users)
// 3. Create/update Participant record with event-specific customResponses
// 4. Fire-and-forget post-processing:
//    - Generate skills embedding for vector team matching
//    - Send registration confirmation notification
//    - Send confirmation email
//    - Send email verification (if needed)

const registrationSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  password: z.string().min(8).optional(),
  skills: z.array(z.string()).min(1).max(10),
  experienceLevel: z.enum(["beginner", "intermediate", "advanced"]).optional(),
  github: z.string().optional(),
  bio: z.string().max(1000).optional(),
  customAnswers: z.record(z.string(), z.unknown()).optional(),
});
```

### Pattern 6: Judging Rubric and Score Submission

```typescript
// Rubric definition on the Event model:
judgingRubric: [{
  name: "Innovation",         // Criterion name
  description: "How novel...", // What judges should evaluate
  weight: 2,                  // Multiplier for weighted scoring
  maxScore: 10,               // Maximum score for this criterion
}]

// Score submission schema:
const submitScoreSchema = z.object({
  projectId: z.string(),
  rubricId: z.string(),
  scores: z.array(z.object({
    criteriaId: z.string(),
    score: z.number().min(0),
    feedback: z.string().max(2000),
  })),
  overallComments: z.string().max(5000),
});
```

### Pattern 7: Zod Schemas

```typescript
export const createEventSchema = z.object({
  name: z.string().min(3).max(200),
  description: z.string().min(10).max(5000),
  theme: z.string().min(2).max(200),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  registrationDeadline: z.string().datetime(),
  location: z.string().min(2).max(500),
  capacity: z.number().int().positive().max(10000),
  isVirtual: z.boolean(),
  tags: z.array(z.string()).max(20),
  rules: z.string().max(10000).optional(),
  judging_criteria: z.array(z.string()).max(20).optional(),
});

export const updateEventSchema = createEventSchema.partial();
```

## Related API Routes

```
src/app/api/admin/events/
├── route.ts                              # GET (list), POST (create)
└── [eventId]/
    ├── route.ts                          # GET, PATCH, DELETE
    ├── assignments/route.ts              # Judge-to-project assignments
    ├── atlas-provisioning/route.ts       # Cluster provisioning config
    ├── feedback-forms/route.ts           # Link feedback forms to event
    ├── feedback-responses/route.ts       # Get feedback submissions
    ├── results/route.ts                  # Publish final rankings
    ├── send-feedback/route.ts            # Trigger email feedback requests
    ├── generate-all-feedback/route.ts    # AI feedback synthesis
    ├── landing-page/route.ts             # Landing page CRUD
    └── publish-results/route.ts          # Finalize results
```

## Dependencies

No additional dependencies beyond the scaffold (mongoose, zod, next-auth).

## Common Pitfalls

- **Check event status before allowing registration.** Only `"open"` events accept new registrations.
- **Use atomic transactions for new user creation** during registration to prevent orphaned records.
- **Store custom answers keyed by eventId** (`customResponses[eventId]`) so multiple event registrations don't conflict.
- **Use `$addToSet` for partner engagement sync** — not `$push` — to prevent duplicate entries.
- **Use `sparse: true` on `landingPage.slug`** index because not all events have landing pages.
- **Validate capacity at registration time**, not just on the frontend. Race conditions can cause over-registration.
