import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { cookies } from "next/headers"
import "@/styles/globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import Header from "@/components/header"
import Footer from "@/components/footer"
import { verifyToken } from "@/lib/auth"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "SecureBank - Your Trusted Banking Partner",
  description: "Secure and reliable banking services for all your financial needs"
}


export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const cookieStore = await cookies();
  const token = cookieStore.get("session")?.value;

  const user = token ? await verifyToken(token) : null;
  const isLogged = !!user;
  
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider attribute="class" enableSystem>
          <div className="flex min-h-screen flex-col">
            <Header isLogged={isLogged} />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
