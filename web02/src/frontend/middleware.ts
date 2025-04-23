import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { authMiddleware, verifyToken } from "@/lib/auth"

export async function middleware(request: NextRequest) {
  // Protected routes
  if (request.nextUrl.pathname.startsWith("/dashboard")) {
    const redirectResponse = await authMiddleware(request)
    if (redirectResponse) {
      return redirectResponse
    }
  }

  // Redirect authenticated users away from login/register
  if (request.nextUrl.pathname.startsWith("/login") || request.nextUrl.pathname.startsWith("/register")) {
    const token = request.cookies.get("session")?.value
    if (token) {
      try {
        const payload = await verifyToken(token)
        if (payload) {
          return NextResponse.redirect(new URL("/dashboard", request.url))
        }
      } catch (error) {
        // Invalid token, continue to login page
      }
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
}