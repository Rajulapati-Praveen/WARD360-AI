import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { useAuth } from '../auth.jsx'
import { Btn, Card, Err, Input, LevelBadge, Select, SimBanner, StatusBadge } from '../components/UI.jsx'
import DigitalTwin from '../components/DigitalTwin.jsx'

export default function PatientDetails() {
  const { id } = useParams()
  const { user } = useAuth()
  const { data: p, error, reload } = useData(() => api(`/api/patients/${id}`), [id], 6000)
  const { data: live } = useData(() => api(`/api/patients/${id}/live`), [id], 3000)
  const { data: users } = useData(() => (user.role === 'admin' ? api('/api/users') : Promise.resolve([])), [id], 20000)
  const [edit, setEdit] = useState(null)
  const [pick, setPick] = useState('')
  const [msg, setMsg] = useState('')
  if (error) return <Err msg={error} />
  if (!p) return <div className="text-slate-500">Loading…</div>
  const isAdmin = user.role === 'admin'
  const save = async () => {
    try { await api(`/api/patients/${id}`, { method: 'PUT', body: { name: edit.name, age: +edit.age, gender: edit.gender, notes: edit.notes,
      baseline: { heart_rate: +edit.hr, spo2: +edit.spo2, temperature: +edit.temp, resp_rate: +edit.rr } } }); setEdit(null); reload() } catch (e) { setMsg(e.message) }
  }
  const startEdit = () => setEdit({ ...p, hr: p.baseline.heart_rate, spo2: p.baseline.spo2, temp: p.baseline.temperature, rr: p.baseline.resp_rate })
  const assign = async () => { if (pick) { await api(`/api/patients/${id}/assign`, { method: 'POST', body: { user_id: +pick } }); reload() } }
  const unassign = async (uid) => { await api(`/api/patients/${id}/assign/${uid}`, { method: 'DELETE' }); reload() }
  const candidates = (users || []).filter((u) => u.role !== 'admin' && !p.team.find((t) => t.id === u.id))
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div><h1 className="text-2xl font-bold text-navy-900">{p.name}</h1><div className="text-sm text-slate-500">{p.age} years · {p.gender} · synthetic patient</div></div>
        <LevelBadge level={p.risk?.level || 'unknown'} />
      </div>
      <SimBanner />
      <div className="grid lg:grid-cols-2 gap-5">
        <Card title="Patient digital twin"><DigitalTwin live={live} /></Card>
        <Card title="Profile & baseline" right={isAdmin && !edit && <Btn variant="secondary" onClick={startEdit}>Edit</Btn>}>
          {edit ? (
            <div className="space-y-2">
              <Input value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} />
              <div className="flex gap-2"><Input type="number" value={edit.age} onChange={(e) => setEdit({ ...edit, age: e.target.value })} />
                <Select value={edit.gender} onChange={(e) => setEdit({ ...edit, gender: e.target.value })}><option>female</option><option>male</option><option>other</option></Select></div>
              <Input value={edit.notes} onChange={(e) => setEdit({ ...edit, notes: e.target.value })} />
              <div className="grid grid-cols-4 gap-2">{[['hr', 'HR'], ['spo2', 'SpO2'], ['temp', 'Temp'], ['rr', 'RR']].map(([k, l]) => (
                <label key={k} className="text-[11px] text-slate-500">{l}<Input type="number" step="0.1" value={edit[k]} onChange={(e) => setEdit({ ...edit, [k]: e.target.value })} /></label>))}</div>
              <div className="flex gap-2"><Btn onClick={save}>Save</Btn><Btn variant="secondary" onClick={() => setEdit(null)}>Cancel</Btn></div>
            </div>
          ) : (
            <div className="text-sm space-y-1">
              <div>Notes: {p.notes || '-'}</div>
              <div>Baseline: HR {p.baseline.heart_rate} bpm · SpO2 {p.baseline.spo2}% · Temp {p.baseline.temperature}°C · RR {p.baseline.resp_rate}/min</div>
              <div className="text-xs text-slate-500">Personal baselines let the AI compare this patient with themselves, not with a population average.</div>
            </div>
          )}
          <Err msg={msg} />
        </Card>
        <Card title="Care team (access)">
          <div className="space-y-1.5 text-sm">
            {p.team.map((t) => (
              <div key={t.id} className="flex justify-between items-center">
                <span>{t.name} <span className="text-xs text-slate-400 capitalize">({t.role})</span></span>
                {isAdmin && <button className="text-xs text-red-600" onClick={() => unassign(t.id)}>remove</button>}
              </div>
            ))}
            {!p.team.length && <div className="text-slate-400">No one assigned</div>}
          </div>
          {isAdmin && (
            <div className="flex gap-2 mt-3">
              <Select value={pick} onChange={(e) => setPick(e.target.value)}><option value="">Assign caregiver / doctor…</option>
                {candidates.map((u) => <option key={u.id} value={u.id}>{u.name} ({u.role})</option>)}</Select>
              <Btn onClick={assign}>Assign</Btn>
            </div>
          )}
        </Card>
        <Card title="Devices">
          {p.devices.map((d) => (
            <div key={d.id} className="flex items-center justify-between text-sm py-1">
              <span>{d.name} <span className="text-xs text-slate-400">({d.kind})</span></span>
              <span className="flex items-center gap-2"><StatusBadge status={d.status} /><span className="text-xs">🔋{d.battery}%</span><span className="text-xs text-slate-400">{fmtDateTime(d.last_seen)}</span></span>
            </div>
          ))}
        </Card>
      </div>
    </>
  )
}
