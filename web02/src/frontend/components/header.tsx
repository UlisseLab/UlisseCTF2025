"use client"

import Link from "next/link"
import { useState } from "react"
import { Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export default function Header({ isLogged }: { isLogged: boolean }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center space-x-2">
            <div className="bg-primary text-primary-foreground font-bold text-xl px-2 py-1 rounded">SB</div>
            <span className="hidden font-bold sm:inline-block">SecureBank</span>
          </Link>
          <nav className="hidden md:flex gap-6 ml-10">
            <Link href="/" className="text-sm font-medium transition-colors hover:text-primary">
              Home
            </Link>
            <Link href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              Features
            </Link>
            <Link href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              About
            </Link>
            <Link href="#" className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              Contact
            </Link>
          </nav>
        </div>
        <div className="hidden md:flex items-center gap-4">
          {
            isLogged ? (
              <>
                <Link href="/dashboard">
                  <Button variant="ghost" size="sm">
                    Dashboard
                  </Button>
                </Link>
                <Link href="/logout">
                  <Button size="sm">Logout</Button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Register</Button>
                </Link>
              </>
            )
          }
        </div>
        <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)} aria-label="Toggle menu">
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      <div className={cn("md:hidden absolute w-full bg-background border-b", isMenuOpen ? "block" : "hidden")}>
        <div className="container py-4 flex flex-col gap-4">
          <nav className="flex flex-col gap-2">
            <Link
              href="/"
              className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              href="#"
              className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
              onClick={() => setIsMenuOpen(false)}
            >
              Features
            </Link>
            <Link
              href="#"
              className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
              onClick={() => setIsMenuOpen(false)}
            >
              About
            </Link>
            <Link
              href="#"
              className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
              onClick={() => setIsMenuOpen(false)}
            >
              Contact
            </Link>
          </nav>
          <div className="flex flex-col gap-2 pt-2 border-t">
            {
              isLogged ? (
                <>
                  <Link
                    href="/dashboard"
                    className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/logout"
                    className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Logout
                  </Link>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    href="/register"
                    className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-md"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Register
                  </Link>
                </>
              )
            }
          </div>
        </div>
      </div>
    </header>
  )
}

