"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    const logout = async () => {
      await fetch("/api/logout")
      router.push("/")
      router.refresh()
    }
    
    logout();
  }, [router])

  return <p>Logging out...</p>
}