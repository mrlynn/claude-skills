import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";

// Role groups — adjust to match your app's roles
const ADMIN_PANEL_ROLES = ["super_admin", "admin", "organizer", "marketer"];
const AUTHENTICATED_ROUTES = ["/dashboard", "/settings", "/projects"];
const ADMIN_ROUTES = ["/admin"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip static assets and API routes (API routes handle their own auth)
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Get JWT token (edge-safe — does NOT import Mongoose or bcrypt)
  const token = await getToken({
    req: request,
    secret: process.env.AUTH_SECRET,
  });

  // --- Admin routes: require admin panel role ---
  if (ADMIN_ROUTES.some((route) => pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }

    const role = token.role as string | undefined;
    if (!role || !ADMIN_PANEL_ROLES.includes(role)) {
      return NextResponse.redirect(new URL("/", request.url));
    }

    return NextResponse.next();
  }

  // --- Authenticated routes: require any valid session ---
  if (AUTHENTICATED_ROUTES.some((route) => pathname.startsWith(route))) {
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("callbackUrl", pathname);
      return NextResponse.redirect(loginUrl);
    }

    return NextResponse.next();
  }

  // --- Public routes: allow through ---
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     * - public folder files
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
