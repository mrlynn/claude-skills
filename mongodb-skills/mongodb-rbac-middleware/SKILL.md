---
name: mongodb-rbac-middleware
description: Add NextAuth v5 authentication with 8-role RBAC, edge-safe middleware, server-side guards, role hierarchy, and admin impersonation to a Next.js app
license: MIT
metadata:
  version: 1.0.0
  author: Michael Lynn [mlynn.org](https://mlynn.org)
  category: mongodb-devrel
  domain: authentication
  updated: 2026-03-01
  python-tools: role_matrix_generator.py
  tech-stack: next-auth, bcryptjs, jwt, edge-runtime
---

# mongodb-rbac-middleware

## Trigger

Use this skill when adding authentication, role-based access control, or route protection to a Next.js app. Covers NextAuth v5 with JWT strategy, edge middleware, server-side guards, role hierarchy, and admin impersonation.

> *8 roles sounds like overkill until you're building a hackathon platform with admins, organizers, judges, mentors, sponsors, and participants who all need different views of the same data.* — ML

## Overview

Getting auth middleware right in Next.js — especially edge middleware that can't import Mongoose — is a common stumbling block. This skill provides a battle-tested 8-role RBAC system with edge-safe JWT parsing, server-side guard functions, and an impersonation system for admin testing.

## How to Use

### Quick Start
Invoke with `/mongodb-rbac-middleware` or let Claude auto-activate when adding authentication or role-based access control.

### Python Tools
- `scripts/role_matrix_generator.py` — Generate role-to-route permission matrix from admin-guard config

### Reference Docs
- `references/role-hierarchy.md` — Full 8-role hierarchy with permissions per route
- `references/edge-runtime-constraints.md` — What can/cannot run in Edge (why getToken not auth())

### Templates & Samples
- `assets/role-permission-matrix.md` — Pre-built role-permission matrix template
- `assets/middleware-template.ts` — Starter middleware.ts for edge route protection

## Architecture Decisions

- **JWT strategy over database sessions**: JWTs are stateless and edge-compatible. No DB round-trip on every request.
- **`getToken()` in edge middleware, NOT `auth()`**: The `auth()` export from NextAuth pulls in bcryptjs, mongoose, and `cookies()` — all Node.js-only modules that crash the Edge runtime. `getToken()` from `next-auth/jwt` is Edge-safe.
- **NextAuth v5 uses JWE, not plain JWS**: Don't try to verify tokens with jose's `jwtVerify` — it won't work. NextAuth v5 encrypts tokens with A256CBC-HS512. Use `getToken()` which handles decryption.
- **Role groups, not individual role checks**: Define role groups (ADMIN_ROLES, ADMIN_PANEL_ROLES) and check membership. This makes adding new roles trivial.
- **Impersonation via httpOnly cookie**: Admins can test as other users by setting an `impersonate_user_id` cookie. The session callback swaps identity but preserves `realAdminRole` so guards still work.

## Code Patterns

### Pattern 1: NextAuth v5 Configuration

```typescript
// src/lib/auth.ts
import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import crypto from "crypto";
import { cookies } from "next/headers";
import { connectToDatabase } from "@/lib/db/connection";
import { UserModel } from "@/lib/db/models/User";
import { sendEmail } from "@/lib/email/email-service";
import { renderEmailTemplate } from "@/lib/email/template-renderer";

export const { handlers, signIn, signOut, auth } = NextAuth({
  secret: process.env.AUTH_SECRET,
  providers: [
    Credentials({
      id: "credentials",
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        await connectToDatabase();
        const user = await UserModel.findOne({
          email: (credentials.email as string).toLowerCase(),
        }).select("+twoFactorCode +twoFactorExpiry");

        if (!user || !user.passwordHash) return null;

        const isValid = await bcrypt.compare(credentials.password as string, user.passwordHash);
        if (!isValid) return null;

        // Check ban/soft-delete
        if (user.banned || user.deletedAt) {
          throw new Error(user.bannedReason || "Your account has been suspended.");
        }

        // 2FA flow: generate code, send email, return null to block sign-in
        if (user.twoFactorEnabled) {
          const code = Math.floor(100000 + Math.random() * 900000).toString();
          const hashedCode = crypto.createHash("sha256").update(code).digest("hex");
          user.twoFactorCode = hashedCode;
          user.twoFactorExpiry = new Date(Date.now() + 10 * 60 * 1000);
          await user.save();

          const template = await renderEmailTemplate("two_factor_code", { userName: user.name, code });
          sendEmail({ to: user.email, subject: template.subject, html: template.html, text: template.text }).catch(() => {});
          return null; // Client handles 2FA separately
        }

        return {
          id: user._id.toString(),
          email: user.email,
          name: user.name,
          role: user.role,
          partnerId: user.partnerId?.toString(),
        };
      },
    }),
    Credentials({
      id: "magic-link",
      name: "magic-link",
      credentials: {
        token: { type: "text" },
        email: { type: "email" },
      },
      async authorize(credentials) {
        if (!credentials?.token || !credentials?.email) return null;

        await connectToDatabase();
        const hashedToken = crypto.createHash("sha256").update(credentials.token as string).digest("hex");
        const user = await UserModel.findOne({
          email: (credentials.email as string).toLowerCase(),
        }).select("+magicLinkToken +magicLinkExpiry");

        if (!user?.magicLinkToken || !user?.magicLinkExpiry) return null;
        if (user.magicLinkToken !== hashedToken) return null;
        if (user.magicLinkExpiry < new Date()) return null;

        user.magicLinkToken = undefined;
        user.magicLinkExpiry = undefined;
        await user.save();

        return {
          id: user._id.toString(),
          email: user.email,
          name: user.name,
          role: user.role,
          partnerId: user.partnerId?.toString(),
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as { role: string }).role;
        token.id = user.id;
        token.partnerId = (user as { partnerId?: string }).partnerId;
        token.sub = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as unknown as { role: string }).role = token.role as string;
        (session.user as unknown as { id: string }).id = (token.id || token.sub) as string;
        (session.user as unknown as { partnerId?: string }).partnerId = token.partnerId as string | undefined;

        // Impersonation: swap session to impersonated user
        try {
          const cookieStore = await cookies();
          const impersonateUserId = cookieStore.get("impersonate_user_id")?.value;
          if (impersonateUserId && (token.role === "admin" || token.role === "super_admin")) {
            await connectToDatabase();
            const impersonatedUser = await UserModel.findById(impersonateUserId).select("-passwordHash").lean();
            if (impersonatedUser) {
              (session.user as unknown as { id: string }).id = impersonatedUser._id.toString();
              session.user.name = impersonatedUser.name;
              session.user.email = impersonatedUser.email;
              (session.user as unknown as { role: string }).role = impersonatedUser.role;
              (session.user as unknown as { isImpersonating: boolean }).isImpersonating = true;
              (session.user as unknown as { realAdminId: string }).realAdminId = token.id as string;
              (session.user as unknown as { realAdminRole: string }).realAdminRole = token.role as string;
            }
          }
        } catch {
          // cookies() may fail in non-request context — skip impersonation
        }
      }
      return session;
    },
  },
  pages: { signIn: "/login" },
  session: { strategy: "jwt" },
});
```

### Pattern 2: NextAuth Type Extensions

```typescript
// src/types/next-auth.d.ts
import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface User {
    role: string;
    partnerId?: string;
  }
  interface Session {
    user: {
      id: string;
      role: string;
      partnerId?: string;
      isImpersonating?: boolean;
      realAdminId?: string;
      realAdminRole?: string;
    } & DefaultSession["user"];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id: string;
    role: string;
    partnerId?: string;
  }
}
```

### Pattern 3: Role Groups and Server-Side Guards

```typescript
// src/lib/admin-guard.ts
import { auth } from "@/lib/auth";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export type UserRole =
  | "super_admin" | "admin" | "organizer" | "marketer"
  | "mentor" | "judge" | "participant" | "partner";

export const ADMIN_ROLES: UserRole[] = ["super_admin", "admin"];
export const ADMIN_PANEL_ROLES: UserRole[] = ["super_admin", "admin", "organizer", "marketer"];
export const EVENT_MANAGEMENT_ROLES: UserRole[] = ["super_admin", "admin", "organizer"];
export const PARTNER_PORTAL_ROLES: UserRole[] = ["super_admin", "admin", "partner"];

async function isImpersonationActive(): Promise<boolean> {
  try {
    const cookieStore = await cookies();
    return !!cookieStore.get("impersonate_user_id")?.value;
  } catch {
    return false;
  }
}

function effectiveRole(user: { role?: string; realAdminRole?: string; isImpersonating?: boolean }): UserRole {
  return ((user.isImpersonating ? user.realAdminRole : user.role) ?? user.role ?? "") as UserRole;
}

export async function requireAdmin() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  if (!ADMIN_ROLES.includes(role) && !(await isImpersonationActive())) redirect("/dashboard");
  return session;
}

export async function requireAdminPanel() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  if (!ADMIN_PANEL_ROLES.includes(role) && !(await isImpersonationActive())) redirect("/dashboard");
  return session;
}

export async function requireSuperAdmin() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  if (role !== "super_admin") redirect("/admin");
  return session;
}

export async function requirePartner() {
  const session = await auth();
  if (!session?.user) redirect("/login");
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  if (!PARTNER_PORTAL_ROLES.includes(role) && !(await isImpersonationActive())) redirect("/dashboard");
  return session;
}

export async function hasRole(...roles: UserRole[]): Promise<boolean> {
  const session = await auth();
  if (!session?.user) return false;
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  return roles.includes(role);
}

export async function isUserAdmin(): Promise<boolean> {
  const session = await auth();
  if (!session?.user) return false;
  const role = effectiveRole(session.user as { role?: string; realAdminRole?: string; isImpersonating?: boolean });
  if (ADMIN_ROLES.includes(role)) return true;
  return isImpersonationActive();
}
```

### Pattern 4: Edge Middleware (CRITICAL)

**This is the pattern most people get wrong.** You CANNOT import `auth` from `@/lib/auth` in middleware because it transitively imports bcryptjs, mongoose, and `cookies()` — all of which crash the Edge runtime.

```typescript
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

/**
 * CRITICAL: We use getToken(), NOT auth().
 * auth() imports bcryptjs + mongoose + cookies() = Edge crash.
 * getToken() is Edge-safe and handles NextAuth v5 JWE decryption.
 */

interface TokenPayload {
  role?: string;
  sub?: string;
}

async function getTokenPayload(req: NextRequest): Promise<TokenPayload | null> {
  try {
    const token = await getToken({ req, secret: process.env.AUTH_SECRET! });
    if (!token) return null;
    return { role: (token.role as string) || undefined, sub: token.sub || undefined };
  } catch {
    return null;
  }
}

export async function middleware(req: NextRequest) {
  const { pathname, searchParams } = req.nextUrl;

  // Admin route protection
  if (pathname.startsWith("/admin")) {
    const payload = await getTokenPayload(req);
    if (!payload) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("callbackUrl", req.url);
      return NextResponse.redirect(loginUrl);
    }
    const role = payload.role;
    if (role !== "admin" && role !== "super_admin" && role !== "organizer" && role !== "marketer") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
    return NextResponse.next();
  }

  // Judging route protection
  if (pathname.startsWith("/judging")) {
    const payload = await getTokenPayload(req);
    if (!payload) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("callbackUrl", req.url);
      return NextResponse.redirect(loginUrl);
    }
    const role = payload.role;
    if (role !== "judge" && role !== "admin" && role !== "super_admin" && role !== "organizer") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
    return NextResponse.next();
  }

  // Partner portal protection (exclude /partner/register)
  if (pathname.startsWith("/partner") && !pathname.startsWith("/partner/register")) {
    const payload = await getTokenPayload(req);
    if (!payload) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("callbackUrl", req.url);
      return NextResponse.redirect(loginUrl);
    }
    const role = payload.role;
    if (role !== "partner" && role !== "admin" && role !== "super_admin") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
    return NextResponse.next();
  }

  // Landing page preview mode guard
  if (searchParams.get("preview")) {
    const payload = await getTokenPayload(req);
    const role = payload?.role;
    if (role === "admin" || role === "super_admin" || role === "organizer" || role === "marketer") {
      return NextResponse.next();
    }
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("callbackUrl", req.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/judging/:path*",
    "/partner/:path*",
    "/((?!api|_next/static|_next/image|favicon\\.ico|login|register|admin|dashboard|events|judging|profile|projects|settings).*)",
  ],
};
```

### Pattern 5: Using Guards in API Routes

```typescript
// In route handlers that need admin access:
import { auth } from "@/lib/auth";
import { errorResponse } from "@/lib/utils";

export async function POST(request: NextRequest) {
  const session = await auth();
  const role = (session?.user as { role?: string })?.role;
  if (!role || !["admin", "super_admin"].includes(role)) {
    return errorResponse("Forbidden", 403);
  }
  // ... proceed
}

// In server components / layouts that need admin access:
import { requireAdminPanel } from "@/lib/admin-guard";
import type { UserRole } from "@/lib/admin-guard";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await requireAdminPanel(); // Redirects if unauthorized
  const userRole = ((session.user as { role?: string }).role ?? "participant") as UserRole;
  return <AdminShell userRole={userRole}>{children}</AdminShell>;
}
```

### Pattern 6: User Model with Auth Fields

```typescript
// Key auth-related fields on the User model (see mongodb-nextjs-scaffold for full model)
const UserSchema = new Schema({
  email: { type: String, required: true, unique: true, lowercase: true },
  passwordHash: { type: String },                    // bcrypt hash
  magicLinkToken: { type: String, select: false },   // SHA-256 hash (never return in queries)
  magicLinkExpiry: { type: Date, select: false },
  twoFactorEnabled: { type: Boolean, default: false },
  twoFactorCode: { type: String, select: false },    // SHA-256 hash
  twoFactorExpiry: { type: Date, select: false },
  role: {
    type: String,
    enum: ["super_admin", "admin", "organizer", "marketer", "mentor", "judge", "participant", "partner"],
    default: "participant",
  },
  banned: { type: Boolean, default: false },
  bannedAt: { type: Date },
  bannedReason: { type: String },
  deletedAt: { type: Date },                         // Soft delete
}, { timestamps: true });
```

## Environment Variables

```bash
AUTH_SECRET=your-random-secret-min-32-chars   # Required for JWT encryption
NEXTAUTH_URL=http://localhost:3000            # Required for callbacks
```

## Dependencies

```bash
npm install next-auth@beta bcryptjs
npm install -D @types/bcryptjs
```

## Common Pitfalls

- **NEVER import `@/lib/auth` in middleware.ts.** It pulls in bcryptjs/mongoose which crash Edge. Use `getToken` from `next-auth/jwt`.
- **NEVER use jose `jwtVerify` to decode NextAuth v5 tokens.** They're JWE-encrypted (A256CBC-HS512), not plain JWS. Only `getToken` handles this correctly.
- **Always hash tokens before storing.** Magic link tokens and 2FA codes are hashed with SHA-256 before saving to the database. Compare hashes, never raw values.
- **Use `select: false` for sensitive fields.** Password hashes, tokens, and 2FA codes should never be returned in normal queries. Use `.select("+fieldName")` when you explicitly need them.
- **Soft-delete users, don't hard-delete.** Set `deletedAt` and check for it in queries. This preserves audit trails.
- **Fire-and-forget for 2FA emails.** Use `.catch(() => {})` — don't let email failures block the auth flow.
