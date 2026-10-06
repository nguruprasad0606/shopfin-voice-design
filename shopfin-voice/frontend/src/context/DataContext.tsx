import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { api } from '../lib/api'

// `version` goes up every time data changes (for example after a voice/text command),
// and every page that uses useApi re-fetches when it does.
const Ctx = createContext({ version: 0, refresh: () => {} })
export const useData = () => useContext(Ctx)

export function DataProvider({ children }: { children: ReactNode }) {
  const [version, setVersion] = useState(0)
  const refresh = useCallback(() => setVersion(v => v + 1), [])
  return <Ctx.Provider value={{ version, refresh }}>{children}</Ctx.Provider>
}

/** Fetches `path`. Pass `pollMs` to keep the numbers live (for example entries added from another device). */
export function useApi<T>(path: string, pollMs?: number) {
  const { version } = useData()
  const [tick, setTick] = useState(0)
  const [state, setState] = useState<{ data: T | null; error: string; loading: boolean; updatedAt: Date | null }>(
    { data: null, error: '', loading: true, updatedAt: null })

  useEffect(() => {
    if (!pollMs) return
    const id = window.setInterval(() => { if (!document.hidden) setTick(t => t + 1) }, pollMs)
    return () => window.clearInterval(id)
  }, [pollMs])

  useEffect(() => {
    let live = true
    api<T>(path)
      .then(data => live && setState({ data, error: '', loading: false, updatedAt: new Date() }))
      .catch(e => live && setState(s => ({ ...s, error: e.message, loading: false })))
    return () => { live = false }
  }, [path, version, tick])
  return state
}
