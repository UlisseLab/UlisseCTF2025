import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-4 text-center">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tighter">404 - Not Found</h1>
        <p className="text-muted-foreground">The page you are looking for does not exist.</p>
      </div>
      <Link href="/">
        <Button>Go back home</Button>
      </Link>
    </div>
  )
}