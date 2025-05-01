"use client"

import type React from "react"
import DOMPurify from "dompurify"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { getCookie } from "cookies-next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowDown, ArrowUp, CreditCard, DollarSign, PiggyBank, ArrowRightLeft, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ObjectId } from "mongodb";

interface Transaction {
  _id: ObjectId
  receiver: string
  sender: string
  amount: number
  note: string
  status: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [balance, setBalance] = useState(0)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("transactions")

  const [amount, setAmount] = useState("")
  const [receiver, setReceiver] = useState("")
  const [note, setNote] = useState("")
  const [isTransferLoading, setIsTransferLoading] = useState(false)
  const [transferError, setTransferError] = useState<string | null>(null)
  const [transferSuccess, setTransferSuccess] = useState<string | null>(null)

  const [adminParam, setAdminParam] = useState("")
  const [isAdminLoading, setIsAdminLoading] = useState(false)
  const [adminError, setAdminError] = useState<string | null>(null)
  const [adminSuccess, setAdminSuccess] = useState<string | null>(null)
  const [adminData, setAdminData] = useState<any>(null)
  
  const user = getCookie("username") as string

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("/api/dashboard")

      if (!response.ok) {
        if (response.status === 401) {
          router.push("/login")
          return
        }
        throw new Error("Failed to fetch dashboard data")
      }

      const data = await response.json()
      setBalance(data.balance)
      setTransactions(data.transactions || [])
    } catch (err) {
      setError("Failed to load dashboard data")
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [router])

  const handleLogout = async () => {
    try {
      await fetch("/api/logout")
      router.push("/")
      router.refresh()
    } catch (err) {
      console.error("Logout error:", err)
    }
  }

  const handleTransferSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsTransferLoading(true)
    setTransferError(null)
    setTransferSuccess(null)

    const amountValue = Number.parseFloat(amount)
    if (isNaN(amountValue) || amountValue <= 0) {
      setTransferError("Please enter a valid amount greater than 0")
      setIsTransferLoading(false)
      return
    }

    if (!receiver.trim()) {
      setTransferError("Please enter a receiver username")
      setIsTransferLoading(false)
      return
    }

    try {
      const response = await fetch("/service/transaction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          amount: amountValue,
          receiver: receiver.trim(),
          note: note.trim() || "Transfer",
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setTransferError(data.error || "Transfer failed")
        setIsTransferLoading(false)
        return
      }

      setTransferSuccess("Transfer completed successfully!")
      setAmount("")
      setReceiver("")
      setNote("")

      await fetchDashboardData()

      setTimeout(() => {
        setActiveTab("transactions")
        setTransferSuccess(null)
      }, 3000)
    } catch (err) {
      setTransferError("An error occurred. Please try again.")
    } finally {
      setIsTransferLoading(false)
    }
  }

  const handleAdminRequest = async () => {
    setIsAdminLoading(true)
    setAdminError(null)
    setAdminSuccess(null)
    setAdminData(null)

    try {
      const response = await fetch(`/service/admin?auth=${encodeURIComponent(adminParam)}`, {
        method: "GET",
        credentials: "include",
      })

      const data = await response.json()

      if (!response.ok) {
        setAdminError(data.error || "Failed to become admin")
        setIsAdminLoading(false)
        return
      }

      setAdminSuccess("Successfully became admin!")
      setAdminData(data)
    } catch (err) {
      setAdminError("An error occurred. Please try again.")
    } finally {
      setIsAdminLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <div className="h-8 w-48 bg-muted animate-pulse rounded"></div>
        <div className="h-24 bg-muted animate-pulse rounded"></div>
        <div className="h-64 bg-muted animate-pulse rounded"></div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Welcome back! Here's an overview of your accounts.</p>
        </div>
        <Button variant="outline" onClick={handleLogout}>
          Logout
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${balance.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">Current account balance</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Savings</CardTitle>
            <PiggyBank className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$0.00</div>
            <p className="text-xs text-muted-foreground">Savings account balance</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Spending</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$0.00</div>
            <p className="text-xs text-muted-foreground">Monthly spending</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Admin Access</CardTitle>
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {adminSuccess ? (
              <div className="space-y-2">
                <div className="text-sm font-medium text-green-600">{adminSuccess}</div>
                {adminData && (
                  <div className="text-xs text-muted-foreground break-all">
                    {typeof adminData === "object" ? JSON.stringify(adminData) : adminData}
                  </div>
                )}
              </div>
            ) : adminError ? (
              <div className="space-y-2">
                <div className="text-sm font-medium text-red-600">{adminError}</div>
                <div className="flex gap-2 mt-2">
                  <Input
                    placeholder="Admin parameter"
                    value={adminParam}
                    onChange={(e) => setAdminParam(e.target.value)}
                    className="h-8 text-xs"
                    required={true}
                  />
                  <Button
                    size="sm"
                    onClick={handleAdminRequest}
                    disabled={isAdminLoading}
                    className="h-8 text-xs whitespace-nowrap"
                  >
                    {isAdminLoading ? "..." : "Try Again"}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <p className="text-xs text-muted-foreground">Request admin privileges</p>
                <div className="flex gap-2">
                  <Input
                    placeholder="Admin parameter"
                    value={adminParam}
                    onChange={(e) => setAdminParam(e.target.value)}
                    className="h-8 text-xs"
                    required={true}
                  />
                  <Button
                    size="sm"
                    onClick={handleAdminRequest}
                    disabled={isAdminLoading}
                    className="h-8 text-xs whitespace-nowrap"
                  >
                    {isAdminLoading ? "..." : "Become Admin"}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="transactions">Recent Transactions</TabsTrigger>
          <TabsTrigger value="transfer">Transfer Money</TabsTrigger>
        </TabsList>
        <TabsContent value="transactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Transactions</CardTitle>
              <CardDescription>Your recent transactions across all accounts.</CardDescription>
            </CardHeader>
            <CardContent>
              {transactions.length === 0 ? (
                <div className="text-center py-6 text-muted-foreground">No transactions found</div>
              ) : (
                <div className="space-y-4">
                  {transactions.map((transaction, index) => (
                    <div key={index} className="flex items-center justify-between border-b pb-4">
                      <div className="flex items-center gap-4">
                        <div
                          className={`rounded-full p-2 ${transaction.sender != user ? "bg-primary/10" : "bg-destructive/10"}`}
                        >
                          {transaction.sender != user ? (
                            <ArrowDown className="h-4 w-4 text-primary" />
                          ) : (
                            <ArrowUp className="h-4 w-4 text-destructive" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium">{transaction.sender == user ? `Sent to ${transaction.receiver}` : `Recieved from ${transaction.sender}`}</p>
                          <p 
                            className="text-sm text-muted-foreground"
                            dangerouslySetInnerHTML={{
                              __html: DOMPurify.sanitize(transaction.note.toString()),
                            }}
                          ></p>
                        </div>
                      </div>
                      {transaction.sender == user ? (
                        <div className="text-right">
                          <p className="font-medium text-red-600">
                            -{transaction.amount.toFixed(2)}
                          </p>
                          <p className="text-sm text-muted-foreground">{transaction.status}</p>
                        </div>
                      ) : (
                        <div className="text-right">
                          <p className="font-medium text-green-600">
                            +{transaction.amount.toFixed(2)}
                          </p>
                          <p className="text-sm text-muted-foreground">{transaction.status}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="transfer" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Transfer Money</CardTitle>
              <CardDescription>Send money to another user</CardDescription>
            </CardHeader>

            {transferError && (
              <CardContent className="pt-0 pb-0">
                <Alert variant="destructive">
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{transferError}</AlertDescription>
                </Alert>
              </CardContent>
            )}

            {transferSuccess && (
              <CardContent className="pt-0 pb-0">
                <Alert className="bg-green-50 border-green-500 text-green-700">
                  <AlertTitle>Success</AlertTitle>
                  <AlertDescription>{transferSuccess}</AlertDescription>
                </Alert>
              </CardContent>
            )}

            <form onSubmit={handleTransferSubmit}>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount ($)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="recipient">Recipient Username</Label>
                  <Input
                    id="recipient"
                    type="text"
                    placeholder="username"
                    value={receiver}
                    onChange={(e) => setReceiver(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="note">Note (Optional)</Label>
                  <Textarea
                    id="note"
                    placeholder="What's this transfer for?"
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    rows={3}
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit" className="w-full" disabled={isTransferLoading}>
                  {isTransferLoading ? "Processing..." : "Send Money"}
                  {!isTransferLoading && <ArrowRightLeft className="ml-2 h-4 w-4" />}
                </Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}