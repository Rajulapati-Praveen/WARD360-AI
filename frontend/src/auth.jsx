import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { api, getToken, wsUrl } from './api.js'

const Ctx = createContext(null)
export const useAuth = () => useContext(Ctx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)
  const [connected, setConnected] = useState(false)
  const subs = useRef(new Set())

  useEffect(() => {
    if (!getToken()) { setReady(true); return }
    api('/api/auth/me').then(setUser).catch(() => localStorage.removeItem('w360_token')).finally(() => setReady(true))
  }, [])

  // live WebSocket feed (auto-reconnect)
  useEffect(() => {
    if (!user) return
    let ws, timer, stop = false
    const open = () => {
      ws = new WebSocket(wsUrl())
      ws.onopen = () => setConnected(true)
      ws.onmessage = (m) => { try { const ev = JSON.parse(m.data); subs.current.forEach((f) => f(ev)) } catch {} }
      ws.onclose = () => { setConnected(false); if (!stop) timer = setTimeout(open, 3000) }
    }
    open()
    return () => { stop = true; clearTimeout(timer); ws && ws.close() }
  }, [user])

  const subscribe = useCallback((fn) => { subs.current.add(fn); return () => subs.current.delete(fn) }, [])
  const login = async (email, password) => {
    const r = await api('/api/auth/login', { method: 'POST', body: { email, password } })
    localStorage.setItem('w360_token', r.token)
    setUser(r.user)
  }
  const logout = () => { localStorage.removeItem('w360_token'); setUser(null) }
  return <Ctx.Provider value={{ user, ready, login, logout, connected, subscribe }}>{children}</Ctx.Provider>
}
