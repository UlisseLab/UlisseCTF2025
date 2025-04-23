import type { ReactNode } from "react"

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <div className="flex-1 p-6 md:p-8">{children}</div>
    </div>
  )
}