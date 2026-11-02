import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, Activity, Brain, ShieldAlert, Bell, History, FileText, Cpu, Settings, LogOut, Menu, Wifi, WifiOff, X } from 'lucide-react'
import { useAuth } from '../auth.jsx'
import { useData } from '../hooks.js'
import { api } from '../api.js'

const NAV = [
  ['/', 'Dashboard', LayoutDashboard], ['/patients', 'Patients', Users], ['/live', 'Live Monitoring', Activity],
  ['/ai', 'AI Intelligence', Brain], ['/risk', 'Risk Assessment', ShieldAlert], ['/alerts', 'Alert Centre', Bell],
  ['/history', 'Health History', History], ['/reports', 'Reports', FileText], ['/devices', 'Devices', Cpu], ['/settings', 'Settings', Settings],
]

export default function Layout() {
  const { user, logout, connected } = useAuth()
  const nav = useNavigate()
  const [open, setOpen] = useState(false)
  const { data: alerts } = useData(() => api('/api/alerts?limit=50'), [], 6000)
  const active = (alerts || []).filter((a) => a.status !== 'acknowledged').length

  const side = (
    <aside className="w-64 bg-navy-900 text-slate-200 min-h-screen flex flex-col">
      <div className="px-5 py-5 border-b border-white/10">
        <div className="text-xl font-bold text-white tracking-tight">WARD<span className="text-sky-400">360</span> AI</div>
        <div className="text-[11px] text-slate-400 mt-0.5">Your Home. Your Health. One Intelligent Ward.</div>
      </div>
      <nav className="flex-1 py-3">
        {NAV.map(([to, label, Icon]) => (
          <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)}
            className={({ isActive }) => `flex items-center gap-3 px-5 py-2.5 text-sm transition ${isActive ? 'bg-white/10 text-white border-l-4 border-sky-400' : 'hover:bg-white/5 border-l-4 border-transparent'}`}>
            <Icon size={18} />{label}
            {label === 'Alert Centre' && active > 0 && <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-0.5">{active}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10 text-xs">
        <div className="text-white font-medium">{user.name}</div>
        <div className="capitalize text-slate-400 mb-2">{user.role}</div>
        <button onClick={() => { logout(); nav('/login') }} className="flex items-center gap-2 text-slate-300 hover:text-white"><LogOut size={14} />Sign out</button>
      </div>
    </aside>
  )

  return (
    <div className="flex">
      <div className="hidden lg:block sticky top-0 h-screen">{side}</div>
      {open && (
        <div className="fixed inset-0 z-40 flex lg:hidden">
          <div className="overflow-y-auto">{side}</div>
          <div className="flex-1 bg-black/40" onClick={() => setOpen(false)}><X className="m-4 text-white" /></div>
        </div>
      )}
      <div className="flex-1 min-w-0">
        <header className="sticky top-0 z-30 bg-white/90 backdrop-blur border-b border-slate-100 px-4 py-3 flex items-center gap-3">
          <button className="lg:hidden" onClick={() => setOpen(true)}><Menu /></button>
          <div className="font-semibold text-navy-900 lg:hidden">WARD360 AI</div>
          <div className="ml-auto flex items-center gap-2 text-xs">
            {connected ? <span className="flex items-center gap-1 text-emerald-600"><Wifi size={14} />Live</span>
              : <span className="flex items-center gap-1 text-slate-400"><WifiOff size={14} />Reconnecting</span>}
          </div>
        </header>
        <main className="p-4 sm:p-6 max-w-7xl mx-auto space-y-5"><Outlet /></main>
      </div>
    </div>
  )
}
