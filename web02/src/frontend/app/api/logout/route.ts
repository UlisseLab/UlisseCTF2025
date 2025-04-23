import { NextResponse } from "next/server"
import { clearTokenCookie } from "@/lib/auth"

export async function GET() {
  const res = NextResponse.json({ success: true })
  clearTokenCookie(res)
  return res
}