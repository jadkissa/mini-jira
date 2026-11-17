import { useEffect, useState, type ReactNode } from 'react'

import { api, clearTokens, hasTokens, saveTokens, setSessionExpiredHandler } from '../api/client'
import type { Tokens, User } from '../api/types'
import { AuthContext } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(hasTokens())

  useEffect(() => {
    setSessionExpiredHandler(() => setUser(null))
    if (!hasTokens()) return
    api<User>('/users/me')
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const tokens = await api<Tokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    saveTokens(tokens)
    setUser(await api<User>('/users/me'))
  }

  function logout() {
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>
  )
}
