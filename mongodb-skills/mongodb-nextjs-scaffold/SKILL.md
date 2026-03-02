---
name: mongodb-nextjs-scaffold
description: Bootstrap a Next.js + MongoDB + Auth + MUI project with MongoDB branding, singleton connection, Zod validation, and standard API route patterns
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: web-development
  updated: 2026-03-01
  python-tools: brand_color_checker.py, env_checker.py
  tech-stack: nextjs, mongodb, mongoose, mui, zod, next-auth
---

# mongodb-nextjs-scaffold

## Trigger

Use this skill when bootstrapping a new Next.js project with MongoDB, or when setting up the foundation layer (database connection, theme, response utilities, validation) for a MongoDB DevRel application.

> *This is where every project starts for me. I got tired of re-explaining "use a singleton connection" and "wrap your API responses" so now Claude just knows.* — ML

## Overview

Every MongoDB DevRel project starts the same way: Next.js App Router + Mongoose connection pooling + MUI theme with MongoDB branding + standard API route patterns. This skill generates that foundation so you never re-derive it.

## How to Use

### Quick Start
Invoke with `/mongodb-nextjs-scaffold` or let Claude auto-activate when bootstrapping a new Next.js + MongoDB project.

### Python Tools
- `scripts/brand_color_checker.py` — Validate CSS/theme files against MongoDB brand palette
- `scripts/env_checker.py` — Check .env has all required variables for selected skills

### Reference Docs
- `references/project-structure.md` — Full directory tree for a scaffolded project

### Templates & Samples
- `assets/sample.env` — Template .env with all variables documented
- `assets/api-route-template.ts` — Copy-paste starter for new API routes

## Architecture Decisions

- **Next.js App Router** (not Pages Router): All new projects use the App Router with `(app)` route groups for layout isolation.
- **Mongoose over native driver**: Mongoose provides schema validation, middleware hooks, and model registration patterns that prevent common bugs in serverless environments.
- **Singleton connection with global cache**: In serverless/edge environments, each function invocation could create a new connection. The global cache pattern prevents connection leaks by reusing connections across hot reloads and concurrent requests.
- **MUI with MongoDB branding**: Material-UI provides accessible, responsive components out of the box. The theme is configured with MongoDB Brand Book V4.0 tokens — not generic colors.
- **Zod for runtime validation**: TypeScript types disappear at runtime. Zod schemas validate API inputs and provide typed parse results.
- **JWT session strategy**: JWT sessions are stateless and edge-compatible. Database sessions require a DB round-trip on every request.

## File Structure

```
src/
├── app/
│   ├── (app)/
│   │   ├── layout.tsx          # Main app layout with ThemeRegistry + SessionProvider
│   │   ├── page.tsx            # Home page
│   │   └── admin/
│   │       └── layout.tsx      # Admin layout with guard
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts    # NextAuth route handler
│   └── layout.tsx              # Root layout (html, body, fonts)
├── components/
│   └── shared-ui/
│       └── ThemeRegistry.tsx   # SSR Emotion cache + ThemeProvider
├── lib/
│   ├── db/
│   │   ├── connection.ts       # Singleton Mongoose connection
│   │   ├── models/             # Mongoose models
│   │   │   └── User.ts
│   │   └── schemas.ts          # Zod validation schemas
│   ├── auth.ts                 # NextAuth configuration
│   └── utils.ts                # Response helpers
├── styles/
│   └── theme.ts                # MongoDB brand theme
└── types/
    └── next-auth.d.ts          # NextAuth type extensions
```

## Code Patterns

### Pattern 1: MongoDB Singleton Connection

This is the most critical pattern. Without it, you'll leak connections in serverless environments.

```typescript
// src/lib/db/connection.ts
import mongoose from "mongoose";

interface MongooseCache {
  conn: typeof mongoose | null;
  promise: Promise<typeof mongoose> | null;
}

declare global {
  // eslint-disable-next-line no-var
  var mongoose: MongooseCache | undefined;
}

const cached: MongooseCache = global.mongoose ?? { conn: null, promise: null };

if (!global.mongoose) {
  global.mongoose = cached;
}

export async function connectToDatabase(): Promise<typeof mongoose> {
  if (cached.conn) {
    return cached.conn;
  }

  const MONGODB_URI = process.env.MONGODB_URI;
  if (!MONGODB_URI) {
    throw new Error(
      "Please define the MONGODB_URI environment variable inside .env.local"
    );
  }

  if (!cached.promise) {
    cached.promise = mongoose
      .connect(MONGODB_URI, { bufferCommands: false })
      .then((m) => m);
  }

  cached.conn = await cached.promise;
  return cached.conn;
}
```

**Why `bufferCommands: false`?** Mongoose buffers model operations until a connection is established. In serverless, this can cause operations to hang if the connection fails silently. Disabling it makes failures explicit.

**Why cache both `conn` and `promise`?** If two concurrent requests hit the server before the connection resolves, without caching the promise, both would call `mongoose.connect()` — creating duplicate connections.

### Pattern 2: Mongoose Model Registration Guard

Mongoose throws `OverwriteModelError` if you call `mongoose.model()` twice with the same name. In development with hot module reload, this happens on every save.

```typescript
// src/lib/db/models/User.ts
import mongoose, { Schema, Document, Types } from "mongoose";

export interface IUser extends Document {
  email: string;
  name: string;
  role: "super_admin" | "admin" | "organizer" | "marketer" | "mentor" | "judge" | "participant" | "partner";
  // ... additional fields
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema = new Schema<IUser>(
  {
    email: { type: String, required: true, unique: true, lowercase: true },
    name: { type: String, required: true },
    role: {
      type: String,
      enum: ["super_admin", "admin", "organizer", "marketer", "mentor", "judge", "participant", "partner"],
      default: "participant",
    },
    // ... additional fields
  },
  { timestamps: true }
);

// Indexes
UserSchema.index({ email: 1 }, { unique: true });

// THE GUARD: Check if model already exists before registering
export const UserModel =
  mongoose.models.User || mongoose.model<IUser>("User", UserSchema);
```

### Pattern 3: Response Utilities

Consistent API responses across all routes.

```typescript
// src/lib/utils.ts
import { NextResponse } from "next/server";

export function errorResponse(message: string, status: number = 400) {
  return NextResponse.json({ error: message }, { status });
}

export function successResponse<T>(data: T, status: number = 200) {
  return NextResponse.json(data, { status });
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(date));
}

export function formatDateRange(start: Date, end: Date): string {
  return `${formatDate(start)} - ${formatDate(end)}`;
}
```

### Pattern 4: MongoDB Brand Theme

The theme uses MongoDB Brand Book V4.0 tokens. Spring green is accent-only in dark mode — never use it as a background fill.

```typescript
// src/styles/theme.ts
"use client";

import { createTheme } from "@mui/material/styles";

export const mongoBrand = {
  springGreen: "#00ED64",    // Accent/CTA only
  slateBlue: "#001E2B",     // Dark backgrounds, text
  white: "#FFFFFF",
  forestGreen: "#00684A",   // Primary in light mode
  evergreen: "#023430",     // Primary dark
  mist: "#E3FCF7",         // Light tint
  lavender: "#F9EBFF",
  blue: "#006EFF",          // Secondary / interactive
  purple: "#B45AF2",        // Accent
  warningYellow: "#FFC010",
  errorRed: "#CF4520",
  gray: {
    50: "#F9FBFA",
    100: "#E7EEEC",
    200: "#C1CCC6",
    300: "#889397",
    400: "#5C6C75",
    500: "#3D4F58",
    600: "#1C2D38",
  },
};

export const hackathonTheme = createTheme({
  cssVariables: {
    colorSchemeSelector: "data-color-scheme",
  },
  colorSchemes: {
    light: {
      palette: {
        primary: {
          main: mongoBrand.forestGreen,
          light: mongoBrand.springGreen,
          dark: mongoBrand.evergreen,
          contrastText: mongoBrand.white,
        },
        secondary: { main: mongoBrand.blue, light: "#4A90FF", dark: "#0052C2", contrastText: mongoBrand.white },
        success: { main: mongoBrand.forestGreen, light: mongoBrand.springGreen, dark: mongoBrand.evergreen },
        info: { main: mongoBrand.blue },
        warning: { main: mongoBrand.warningYellow, dark: "#E6AC00" },
        error: { main: mongoBrand.errorRed, light: "#E8714D", dark: "#A33618" },
        background: { default: mongoBrand.white, paper: mongoBrand.white },
        text: { primary: mongoBrand.slateBlue, secondary: mongoBrand.gray[400] },
        divider: "rgba(0, 30, 43, 0.08)",
      },
    },
    dark: {
      palette: {
        primary: {
          main: mongoBrand.springGreen,   // Buttons, icons, links
          light: "#33F07F",
          dark: "#00C254",
          contrastText: mongoBrand.slateBlue,
        },
        secondary: { main: mongoBrand.blue, light: "#4A90FF", dark: "#0052C2", contrastText: mongoBrand.white },
        success: { main: "#00A854", light: "#33C270", dark: mongoBrand.forestGreen, contrastText: mongoBrand.white },
        info: { main: mongoBrand.blue },
        warning: { main: mongoBrand.warningYellow, dark: "#E6AC00" },
        error: { main: "#E8714D", light: "#F09A7D", dark: mongoBrand.errorRed },
        background: {
          default: mongoBrand.slateBlue,  // Page background
          paper: "#0F2235",               // Card surfaces (dark navy, not green-tinted)
        },
        text: { primary: "#E8EDEB", secondary: mongoBrand.gray[200] },
        divider: "rgba(255, 255, 255, 0.08)",
        action: {
          hover: "rgba(255, 255, 255, 0.12)",
          selected: "rgba(255, 255, 255, 0.20)",
          focus: "rgba(255, 255, 255, 0.16)",
        },
      },
    },
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
    fontWeightBold: 600,
    h1: { fontWeight: 600, letterSpacing: "-0.02em", fontSize: "clamp(2rem, 5vw, 3.5rem)", lineHeight: 1.2 },
    h2: { fontWeight: 600, letterSpacing: "-0.01em", fontSize: "clamp(1.75rem, 4vw, 3rem)", lineHeight: 1.25 },
    h3: { fontWeight: 600, fontSize: "clamp(1.5rem, 3vw, 2.5rem)", lineHeight: 1.3 },
    h4: { fontWeight: 600, fontSize: "clamp(1.25rem, 2.5vw, 2rem)", lineHeight: 1.35 },
    h5: { fontWeight: 500, fontSize: "clamp(1.125rem, 2vw, 1.5rem)", lineHeight: 1.4 },
    h6: { fontWeight: 500, fontSize: "clamp(1rem, 1.5vw, 1.25rem)", lineHeight: 1.45 },
    body1: { fontSize: "1rem", lineHeight: 1.6, fontWeight: 400 },
    body2: { fontSize: "0.875rem", lineHeight: 1.6, fontWeight: 400 },
    button: { fontWeight: 500, letterSpacing: "0.01em", textTransform: "none" },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: "none" as const, fontWeight: 500, padding: "10px 20px" },
        contained: { boxShadow: "none", "&:hover": { boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)" } },
        outlined: { borderWidth: 1.5, "&:hover": { borderWidth: 1.5 } },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: 12,
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 12px rgba(0, 0, 0, 0.04)",
          border: `1px solid ${theme.vars.palette.divider}`,
        }),
      },
    },
    MuiTextField: {
      defaultProps: { variant: "outlined" },
      styleOverrides: {
        root: { "& .MuiOutlinedInput-root": { borderRadius: 8 } },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6, fontWeight: 500 },
        colorPrimary: ({ theme }) => ({
          ...theme.applyStyles("dark", {
            backgroundColor: "rgba(0, 237, 100, 0.12)",
            color: mongoBrand.springGreen,
          }),
        }),
      },
    },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: "none" as const, fontWeight: 500, fontSize: "0.95rem" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundImage: "none",
          ...theme.applyStyles("dark", {
            backgroundColor: mongoBrand.slateBlue,
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          }),
        }),
      },
    },
  },
});
```

### Pattern 5: ThemeRegistry for SSR

Prevents flash-of-wrong-theme and hydration mismatches with Emotion + Next.js App Router.

```typescript
// src/components/shared-ui/ThemeRegistry.tsx
"use client";

import { useState } from "react";
import { useServerInsertedHTML } from "next/navigation";
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";
import { hackathonTheme } from "@/styles/theme";

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  const [{ cache, flush }] = useState(() => {
    const cache = createCache({ key: "mui" });
    cache.compat = true;
    const prevInsert = cache.insert;
    let inserted: string[] = [];
    cache.insert = (...args) => {
      const serialized = args[1];
      if (cache.inserted[serialized.name] === undefined) {
        inserted.push(serialized.name);
      }
      return prevInsert(...args);
    };
    const flush = () => {
      const prevInserted = inserted;
      inserted = [];
      return prevInserted;
    };
    return { cache, flush };
  });

  useServerInsertedHTML(() => {
    const names = flush();
    if (names.length === 0) return null;
    let styles = "";
    for (const name of names) {
      styles += cache.inserted[name];
    }
    return (
      <style
        key={cache.key}
        data-emotion={`${cache.key} ${names.join(" ")}`}
        dangerouslySetInnerHTML={{ __html: styles }}
      />
    );
  });

  return (
    <CacheProvider value={cache}>
      <InitColorSchemeScript attribute="data-color-scheme" />
      <ThemeProvider theme={hackathonTheme}>
        <CssBaseline enableColorScheme />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
```

### Pattern 6: Zod Validation Schemas

Always create paired schemas: `createXSchema` for creation and `updateXSchema = createXSchema.partial()` for updates.

```typescript
// src/lib/db/schemas.ts
import { z } from "zod";

export const createEventSchema = z.object({
  name: z.string().min(3).max(200),
  description: z.string().min(10).max(5000),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  location: z.string().min(2).max(500),
  capacity: z.number().int().positive().max(10000),
  isVirtual: z.boolean(),
  tags: z.array(z.string()).max(20),
});

export const updateEventSchema = createEventSchema.partial();
```

### Pattern 7: Standard API Route

Every API route follows this exact pattern.

```typescript
// src/app/api/admin/events/route.ts
import { NextRequest } from "next/server";
import { auth } from "@/lib/auth";
import { connectToDatabase } from "@/lib/db/connection";
import { EventModel } from "@/lib/db/models/Event";
import { createEventSchema } from "@/lib/db/schemas";
import { errorResponse, successResponse } from "@/lib/utils";

export async function GET() {
  try {
    const session = await auth();
    if (!session?.user) {
      return errorResponse("Unauthorized", 401);
    }

    await connectToDatabase();
    const events = await EventModel.find()
      .sort({ startDate: -1 })
      .lean();

    return successResponse(events);
  } catch (error) {
    console.error("GET /api/admin/events error:", error);
    return errorResponse("Internal server error", 500);
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    const role = (session?.user as { role?: string })?.role;
    if (!role || !["admin", "super_admin"].includes(role)) {
      return errorResponse("Forbidden", 403);
    }

    const body = await request.json();
    const parsed = createEventSchema.safeParse(body);
    if (!parsed.success) {
      return errorResponse(parsed.error.errors[0].message, 422);
    }

    await connectToDatabase();
    const event = await EventModel.create(parsed.data);
    return successResponse(event, 201);
  } catch (error) {
    console.error("POST /api/admin/events error:", error);
    return errorResponse("Internal server error", 500);
  }
}
```

## Environment Variables

```bash
# Required
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
AUTH_SECRET=your-random-secret-min-32-chars
NEXTAUTH_URL=http://localhost:3000

# Optional (for email — see mongodb-email-system skill)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-smtp-password
EMAIL_FROM="Your App <noreply@example.com>"
```

## Dependencies

```bash
npm install next react react-dom mongoose next-auth@beta zod
npm install @mui/material @emotion/react @emotion/cache @emotion/styled
npm install -D typescript @types/react @types/node
```

## Generation Instructions

When this skill is invoked:

1. Create the directory structure shown above
2. Write `src/lib/db/connection.ts` (singleton pattern — copy exactly)
3. Write `src/lib/utils.ts` (response helpers)
4. Write `src/styles/theme.ts` (MongoDB brand theme — copy the `mongoBrand` object and `hackathonTheme` exactly)
5. Write `src/components/shared-ui/ThemeRegistry.tsx` (SSR Emotion cache)
6. Write `src/lib/db/schemas.ts` (Zod schemas for the project's domain)
7. Write a User model following Pattern 2 (with registration guard)
8. Write the root layout importing ThemeRegistry
9. Create `.env.local` with required variables
10. Install dependencies

## Common Pitfalls

- **Don't import `mongoose` in client components.** Mongoose is server-only. Keep all DB code in `src/lib/`.
- **Don't forget `bufferCommands: false`** in the connection options. Without it, operations hang silently on connection failure.
- **Don't use `mongoose.model()` without the guard.** Always use `mongoose.models.X || mongoose.model()` to prevent `OverwriteModelError` in dev.
- **Don't use spring green (#00ED64) as a background fill in dark mode.** It's accent-only (buttons, icons, links). Use `#0F2235` for card surfaces and `#001E2B` for page backgrounds.
- **Don't use `"use client"` on files that import Mongoose.** This crashes the build. Only client components need the directive.
- **Always call `connectToDatabase()` before any model operation** in API routes. Models don't auto-connect.
