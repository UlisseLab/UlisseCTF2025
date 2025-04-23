import Link from "next/link"
import { ArrowRight, Shield, CreditCard, PiggyBank } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-background to-muted">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 items-center">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
                  Banking Made Simple, Secure, and Smart
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl">
                  Experience the future of banking with SecureBank. Manage your finances with ease and confidence.
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Link href="/register">
                  <Button size="lg" className="w-full min-[400px]:w-auto">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/login">
                  <Button size="lg" variant="outline" className="w-full min-[400px]:w-auto">
                    Login
                  </Button>
                </Link>
              </div>
            </div>
            <div className="mx-auto lg:mx-0 relative w-full max-w-[500px] aspect-video rounded-xl overflow-hidden shadow-xl">
              <img
                src="/bank.jpg"
                alt="Banking dashboard preview"
                className="object-cover w-full h-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Features That Make Banking Better
              </h2>
              <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Discover why thousands of customers choose SecureBank for their financial needs.
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3 lg:gap-12 mt-12">
            <Card>
              <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <Shield className="h-8 w-8 text-primary" />
                <CardTitle className="text-xl">Secure Banking</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  State-of-the-art security measures to protect your financial information and transactions.
                </CardDescription>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <CreditCard className="h-8 w-8 text-primary" />
                <CardTitle className="text-xl">Smart Cards</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Advanced credit and debit cards with real-time notifications and spending insights.
                </CardDescription>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <PiggyBank className="h-8 w-8 text-primary" />
                <CardTitle className="text-xl">Savings Goals</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  Set and track your savings goals with automated tools to help you reach them faster.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-muted">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Ready to Start Banking Smarter?
              </h2>
              <p className="max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Join thousands of satisfied customers who trust SecureBank with their finances.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Link href="/register">
                <Button size="lg" className="w-full min-[400px]:w-auto">
                  Open an Account
                </Button>
              </Link>
              <Link href="#">
                <Button size="lg" variant="outline" className="w-full min-[400px]:w-auto">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}