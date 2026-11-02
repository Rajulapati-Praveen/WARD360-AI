import { useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { useData, fmtDateTime } from '../hooks.js'
import { Btn, Card, Err, Input, Select } from '../components/UI.jsx'

export default function Settings() {
  const { user } = useAuth()
  const isAdmin = user.role === 'admin'
  const { data: logs } = useData(() => (isAdmin ? api('/api/audit-logs?limit=40') : Promise.resolve([])), [], 10000)
  const { data: users, reload } = useData(() => (isAdmin ? api('/api/users') : Promise.resolve([])), [], 20000)
  const [f, setF] = useState({ name: '', email: '', password: '', role: 'caregiver' })
  const [err, setErr] = useState('')
  const add = async (e) => {
    e.preventDefault(); setErr('')
    try { await api('/api/users', { method: 'POST', body: f }); setF({ name: '', email: '', password: '', role: 'caregiver' }); reload() } catch (x) { setErr(x.message) }
  }
  return (
    <>
      <h1 className="text-2xl font-bold text-navy-900">Settings</h1>
      <div className="grid lg:grid-cols-2 gap-5">
        <Card title="My account"><div className="text-sm space-y-1"><div>Name: <b>{user.name}</b></div><div>Email: {user.email}</div><div>Role: <b className="capitalize">{user.role}</b></div></div></Card>
        <Card title="Privacy, safety & limitations"><ul className="text-sm text-slate-600 list-disc ml-5 space-y-1">
          <li>All patient data in this prototype is synthetic / simulated.</li>
          <li>Role-based access: caregivers and doctors see only assigned patients.</li>
          <li>Every login, patient view, acknowledgement and denied access is audit-logged.</li>
          <li>Decision support only - not a diagnosis. Risk scoring uses demo rules, not validated clinical thresholds.</li>
          <li>Forecasts and fall detection are experimental.</li>
          <li>Emergency requests are sent directly and never depend on AI.</li></ul></Card>
        {isAdmin && (
          <Card title="Create user">
            <form onSubmit={add} className="space-y-2">
              <Input placeholder="Name" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} required />
              <Input type="email" placeholder="Email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} required />
              <Input type="password" placeholder="Password (min 8 chars)" minLength={8} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} required />
              <Select value={f.role} onChange={(e) => setF({ ...f, role: e.target.value })}><option value="caregiver">Caregiver</option><option value="doctor">Doctor</option><option value="admin">Admin</option></Select>
              <Err msg={err} /><Btn>Create</Btn>
            </form>
            <div className="mt-3 text-xs text-slate-500">{(users || []).length} users registered.</div>
          </Card>
        )}
        {isAdmin && (
          <Card title="Audit log" className="max-h-96 overflow-y-auto">
            {(logs || []).map((l) => <div key={l.id} className="text-xs border-b border-slate-100 py-1"><span className="text-slate-400">{fmtDateTime(l.ts)}</span> · <b>{l.user}</b> · {l.action} {l.target}</div>)}
          </Card>
        )}
      </div>
    </>
  )
}
