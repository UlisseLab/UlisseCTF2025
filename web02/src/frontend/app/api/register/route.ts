import { type NextRequest, NextResponse } from "next/server"
import { createUser } from "@/lib/funcs"

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
    await createUser({ username, password })
    return NextResponse.json({ success: true })
  } catch (error: any) {
    if (error.message === "User already exists") {
      return NextResponse.json({ error: "User already exists" }, { status: 400 })
    }

    console.error("Registration error:", error)
    return NextResponse.json({ error: "An error occurred, please try again" }, { status: 500 })
  }
}