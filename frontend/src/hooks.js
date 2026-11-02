import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth } from './auth.jsx'

/** Loads data; refreshes on WebSocket events (throttled) and on a slow poll as fallback. */
export function useData(loader, deps = [], pollMs = 8000) {
  const { subscribe } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const last = useRef(0)
  const ref = useRef(loader)
  ref.current = loader
  const reload = useCallback(() => {
    last.current = Date.now()
    return ref.current().then((d) => { setData(d); setError('') }).catch((e) => setError(e.message))
  }, [])
  useEffect(() => { setData(null); reload() }, deps) // eslint-disable-line
  useEffect(() => {
    const t = setInterval(reload, pollMs)
    const off = subscribe(() => { if (Date.now() - last.current > 1500) reload() })
    return () => { clearInterval(t); off() }
  }, [reload, subscribe, pollMs])
  return { data, error, reload }
}

export const fmtTime = (iso) => (iso ? new Date(iso).toLocaleTimeString() : '-')
export const fmtDateTime = (iso) => (iso ? new Date(iso).toLocaleString() : '-')
