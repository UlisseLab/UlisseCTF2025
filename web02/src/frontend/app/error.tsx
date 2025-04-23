"use client"

import { useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-4 text-center">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tighter">Something went wrong!</h1>
        <p className="text-muted-foreground">An error occurred while processing your request.</p>
      </div>
      <div className="flex gap-2">
        <Button onClick={reset}>Try again</Button>
        <Link href="/">
          <Button variant="outline">Go back home</Button>
        </Link>
      </div>
    </div>
  )
}