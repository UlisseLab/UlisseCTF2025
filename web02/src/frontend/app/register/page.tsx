"use client"

import type React from "react"

import { useState } from "react"
import { setCookie } from "cookies-next";
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import AuthLayout from "@/components/auth-layout"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function RegisterPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    const formData = new FormData(e.currentTarget)
    const params = new URLSearchParams()
  
    for (const [key, value] of formData.entries()) {
      params.append(key, value.toString())
    }

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params.toString()
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || "Registration failed")
        setIsLoading(false)
        return
      }

      setCookie("username", formData.get("username") as string, { maxAge: 60 * 60 }) // Set cookie for 1 hour
      router.push("/login")
    } catch (err) {
      setError("An error occurred. Please try again.")
      setIsLoading(false)
    }
  }

  return (
    <AuthLayout title="Create an account" description="Enter your information to create an account">
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input id="username" name="username" placeholder="username" required minLength={8} maxLength={20} />
          <p className="text-xs text-muted-foreground">Username must be between 8 and 20 characters.</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              required
              minLength={8}
              maxLength={20}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4 text-muted-foreground" />
              ) : (
                <Eye className="h-4 w-4 text-muted-foreground" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">Password must be between 8 and 20 characters.</p>
        </div>
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? "Creating account..." : "Create Account"}
        </Button>
      </form>
      <div className="mt-4 text-center text-sm">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary underline-offset-4 hover:underline">
          Sign in
        </Link>
      </div>
    </AuthLayout>
  )
}