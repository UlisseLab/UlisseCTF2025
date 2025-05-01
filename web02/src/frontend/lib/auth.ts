import { type NextRequest, NextResponse } from "next/server"
import { SignJWT, jwtVerify } from "jose"

const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET || "secret")

export async function createToken(payload: any) {
  return await new SignJWT(payload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1 hour")
    .sign(JWT_SECRET);
}

export async function verifyToken(input: string) {
  try {
    const { payload, protectedHeader } = await jwtVerify(input, JWT_SECRET, {
      algorithms: ["HS256"],
    });
    return payload;
  } catch (error) {
    console.error("Token decryption error:", error)
    return null;
  }
}

export async function getUser(request: NextRequest) {
  const token = request.cookies.get("session")?.value
  if (!token) return null
  return await verifyToken(token)
}

export async function authMiddleware(request: NextRequest) {
  const user = await getUser(request)
  if (!user) {
    return NextResponse.redirect(new URL("/login", request.url))
  }
  return null
}

export function setTokenCookie(res: NextResponse, token: string) {
  res.cookies.set({
    name: 'session', 
    value: token,
    httpOnly: true,
    sameSite: 'strict',
    maxAge: 60 * 60, // 1 hour
    path: '/',
  });
}

export const clearTokenCookie = (res: NextResponse) => setTokenCookie(res, ""); 