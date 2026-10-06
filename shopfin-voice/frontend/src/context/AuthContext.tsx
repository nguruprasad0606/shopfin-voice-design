import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import type { User } from '../types'
import { api, getToken, setToken } from '../lib/api'

export interface RegisterForm { name: string; email: string; password: string; shop: string; type: string }
interface AuthCtx {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<string | null>
  register: (f: RegisterForm) => Promise<string | null>
  logout: () => void
}
const Ctx = createContext<AuthCtx>({ user: null, loading: true, login: async () => null, register: async () => null, logout: () => {} })
export const useAuth = () => useContext(Ctx)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(!!getToken())

  const loadUser = async () => setUser(await api<User>('/auth/me'))
  const logout = () => { setToken(null); setUser(null) }

  useEffect(() => {
    if (getToken()) loadUser().catch(() => setToken(null)).finally(() => setLoading(false))
    const onExpired = () => logout()
    window.addEventListener('sfv-unauthorized', onExpired)
    return () => window.removeEventListener('sfv-unauthorized', onExpired)
  }, [])

  const start = async (path: string, body: unknown) => {
    try {
      const { access_token } = await api<{ access_token: string }>(path, { body })
      setToken(access_token)
      await loadUser()
      return null
    } catch (e) {
      return (e as Error).message
    }
  }
  const login = (email: string, password: string) => start('/auth/login', { email, password })
  const register = (f: RegisterForm) => start('/auth/register', f)

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>
}
