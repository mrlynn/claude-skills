# Edge Runtime Constraints Reference

This document explains why `auth()` from NextAuth cannot be used in Next.js edge middleware, what alternatives exist, and the exact errors developers encounter when they get this wrong.

## What Is the Edge Runtime?

Next.js middleware runs in the Edge Runtime, a lightweight JavaScript environment designed for low-latency execution at CDN edge nodes. It is NOT Node.js. It supports a subset of Web APIs but lacks many Node.js built-in modules and APIs.

### What the Edge Runtime Supports

- Web standard APIs: `fetch`, `Request`, `Response`, `URL`, `URLSearchParams`
- `TextEncoder` / `TextDecoder`
- `crypto.subtle` (Web Crypto API)
- `structuredClone`
- `atob` / `btoa`
- `setTimeout` / `setInterval` (limited)
- ES modules and dynamic `import()`

### What the Edge Runtime Does NOT Support

- Node.js built-in modules: `fs`, `path`, `crypto` (Node version), `buffer`, `stream`, `os`
- Native addons or C++ bindings
- `process.env` (available but limited -- no `process.cwd()`, `process.exit()`)
- `require()` (CommonJS)
- Any npm package that depends on Node.js built-ins

## Why `auth()` Crashes in Edge Middleware

The `auth()` export from NextAuth v5 (`@/lib/auth.ts`) transitively imports three things that are incompatible with the Edge Runtime:

### 1. bcryptjs

The NextAuth credentials provider imports `bcryptjs` for password hashing. While `bcryptjs` is a pure-JavaScript implementation (no native bindings), it relies on Node.js-specific patterns that can cause issues in edge environments. More importantly, the entire auth configuration file is pulled in, including the `authorize()` function that calls `bcrypt.compare()`.

**Error message:**
```
Module not found: Can't resolve 'crypto' in '/node_modules/bcryptjs/...'
```

### 2. mongoose

The `authorize()` callback calls `connectToDatabase()` and uses `UserModel.findOne()`. Mongoose depends on the MongoDB Node.js driver, which uses TCP sockets, DNS resolution, and other Node.js networking primitives unavailable in Edge.

**Error message:**
```
Module not found: Can't resolve 'dns' in '/node_modules/mongodb/...'
```
or:
```
Module not found: Can't resolve 'net' in '/node_modules/mongodb/...'
```

### 3. cookies() from next/headers

The `session` callback in the auth config calls `cookies()` from `next/headers` to check for the impersonation cookie. The `cookies()` function is a server-only API that requires the Node.js runtime's request context.

**Error message:**
```
Error: `cookies` was called outside a request scope.
```

### The Import Chain

```
middleware.ts
  -> import { auth } from "@/lib/auth"
    -> import bcrypt from "bcryptjs"           // CRASH: Node.js crypto
    -> import { connectToDatabase } from "..."  // CRASH: mongoose -> mongodb -> dns/net
    -> import { cookies } from "next/headers"   // CRASH: server-only API
```

Even if you only call `auth()` to read the session (not to authenticate), the entire module is imported and parsed, triggering the crashes.

## The Solution: getToken() from next-auth/jwt

The `getToken()` function from `next-auth/jwt` is Edge-safe because it:

1. Has no transitive dependencies on Node.js modules
2. Only needs the request object and the `AUTH_SECRET` environment variable
3. Handles NextAuth v5's JWE decryption internally
4. Returns the decoded JWT payload directly

```typescript
import { getToken } from "next-auth/jwt";

// In middleware:
const token = await getToken({ req, secret: process.env.AUTH_SECRET! });
if (token) {
  const role = token.role as string;
  const userId = token.sub;
}
```

## NextAuth v5 JWE vs JWS

This is a common source of confusion. Developers who have worked with older versions of NextAuth or other JWT libraries often try to verify the token using `jose`'s `jwtVerify()`. This will not work with NextAuth v5.

### NextAuth v4 (JWS - JSON Web Signature)

- Tokens are **signed** with HS256 or RS256
- The payload is base64-encoded and readable
- Can be verified with `jose.jwtVerify(token, secret)`
- Structure: `header.payload.signature`

### NextAuth v5 (JWE - JSON Web Encryption)

- Tokens are **encrypted** with A256CBC-HS512 (AES-256 in CBC mode with HMAC-SHA-512)
- The payload is encrypted and NOT readable without the key
- Cannot be verified with `jwtVerify()` -- it must be **decrypted**
- Structure: `header.encryptedKey.iv.ciphertext.tag` (5 parts, not 3)
- `getToken()` handles the decryption using the `AUTH_SECRET`

### Common Error When Using jose Directly

```typescript
// THIS WILL NOT WORK with NextAuth v5
import { jwtVerify } from "jose";
const { payload } = await jwtVerify(token, secret); // throws JWSInvalid
```

**Error message:**
```
JWSInvalid: Invalid Compact JWS
```

This happens because the token has 5 dot-separated parts (JWE format) instead of the 3 parts that `jwtVerify` expects (JWS format).

## Correct Middleware Pattern

```typescript
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";

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
  const { pathname } = req.nextUrl;

  if (pathname.startsWith("/admin")) {
    const payload = await getTokenPayload(req);
    if (!payload) {
      return NextResponse.redirect(new URL("/login", req.url));
    }
    // Check role from JWT payload
    const role = payload.role;
    if (!["admin", "super_admin", "organizer", "marketer"].includes(role || "")) {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
  }

  return NextResponse.next();
}
```

## What You CAN Do in Edge Middleware

- Read and decode JWT tokens via `getToken()`
- Redirect based on token claims (role, userId)
- Set/read cookies on the response
- Rewrite URLs
- Add headers
- Return early responses (403, 404)

## What You CANNOT Do in Edge Middleware

- Query the database (no Mongoose, no MongoDB driver)
- Hash or compare passwords (no bcryptjs)
- Call `auth()` from NextAuth
- Call `cookies()` from `next/headers` (use `req.cookies` instead)
- Use `fs` to read files
- Perform complex server-side logic that depends on Node.js APIs

## Debugging Checklist

If your middleware crashes at build or runtime, check for these import chains:

1. **Are you importing `@/lib/auth`?** Replace with `getToken` from `next-auth/jwt`.
2. **Are you importing any Mongoose model?** Remove it. Middleware cannot access the database.
3. **Are you importing `cookies` from `next/headers`?** Use `req.cookies.get()` instead.
4. **Are you importing any package that uses Node.js `crypto`?** Check with `npm ls crypto` or inspect the error trace.
5. **Are you trying to decode the JWT manually?** Use `getToken()` -- it handles JWE decryption.

## Summary

| Approach                    | Edge-Safe | Why                                      |
|-----------------------------|:---------:|------------------------------------------|
| `auth()` from NextAuth      |    No     | Imports bcryptjs, mongoose, cookies()    |
| `getToken()` from next-auth/jwt |  Yes  | Pure JS, handles JWE, no Node.js deps   |
| `jwtVerify()` from jose     |    No     | Expects JWS format, NextAuth v5 uses JWE |
| `req.cookies.get()`         |    Yes    | Web standard API                         |
| `cookies()` from next/headers |  No     | Server-only, requires Node.js runtime    |
