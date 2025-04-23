import { type NextRequest, NextResponse } from "next/server"
import { createToken, setTokenCookie } from "@/lib/auth"
import { connectDB } from "@/lib/db"

export async function POST(request: NextRequest) {
  const bodyText = await request.text()
  const params = new URLSearchParams(bodyText)
  
  const username = params.get("username") || ""
  const password = params.get("password") || ""

  // Validate input
  if (!username || !password) {
    return NextResponse.json({ error: "Please fill in all fields" }, { status: 400 })
  }

  if (typeof username !== "string" || typeof password !== "string") {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 })
  }

  if (username.length > 20 || password.length > 20 || password.length < 8 || username.length < 8) {
    return NextResponse.json({ error: "Invalid input" }, { status: 400 })
  }

  try {
    const db = await connectDB()

    const query: Record<string, string> = {}
    if (username) query.username = username
    if (password) query.password = password
  
    const user = await db.collection("users").findOne(query)
    
    if (!user) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    const token = await createToken({ username: username, id: user._id.toHexString() })
    const res = NextResponse.json({ success: true })
    setTokenCookie(res, token)
    return res
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ error: "An error occurred, please try again" }, { status: 500 })
  }
}