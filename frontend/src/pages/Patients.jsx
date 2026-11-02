import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { useData } from '../hooks.js'
import { useAuth } from '../auth.jsx'
import { Btn, Card, Err, Input, LevelBadge, Select } from '../components/UI.jsx'

export default function Patients() {
  const { user } = useAuth()
  const { data: patients, reload } = useData(() => api('/api/patients'), [], 8000)
  const [f, setF] = useState({ name: '', age: 70, gender: 'female', notes: '', hr: 75, spo2: 97, temp: 36.8, rr: 16 })
  const [err, setErr] = useState('')
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const add = async (e) => {
    e.preventDefault(); setErr('')
    try {
      await api('/api/patients', { method: 'POST', body: { name: f.name, age: Number(f.age), gender: f.gender, notes: f.notes,
        baseline: { heart_rate: +f.hr, spo2: +f.spo2, temperature: +f.temp, resp_rate: +f.rr } } })
      setF({ ...f, name: '', notes: '' }); reload()
    } catch (x) { setErr(x.message) }
  }
  return (
    <>
      <h1 className="text-2xl font-bold text-navy-900">Patients</h1>
      <div className="grid lg:grid-cols-3 gap-5">
        <Card title={`${patients?.length ?? 0} patient(s)`} className="lg:col-span-2 overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-xs text-slate-500"><th className="py-2">Name</th><th>Age</th><th>Baseline HR / SpO2</th><th>Risk</th><th>Alerts</th></tr></thead>
            <tbody>
              {(patients || []).map((p) => (
                <tr key={p.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="py-2.5"><Link className="text-navy-700 font-medium" to={`/patients/${p.id}`}>{p.name}</Link></td>
                  <td>{p.age}</td><td>{p.baseline.heart_rate} / {p.baseline.spo2}</td>
                  <td><LevelBadge level={p.risk?.level || 'unknown'} /></td><td>{p.open_alerts}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
        {user.role === 'admin' ? (
          <Card title="Register patient (synthetic only)">
            <form onSubmit={add} className="space-y-2">
              <Input placeholder="Full name (use a synthetic name)" value={f.name} onChange={set('name')} required minLength={2} />
              <div className="flex gap-2"><Input type="number" min="0" max="120" value={f.age} onChange={set('age')} />
                <Select value={f.gender} onChange={set('gender')}><option>female</option><option>male</option><option>other</option></Select></div>
              <Input placeholder="Notes" value={f.notes} onChange={set('notes')} />
              <div className="text-xs text-slate-500">Personal baseline</div>
              <div className="grid grid-cols-4 gap-2">
                {[['hr', 'HR'], ['spo2', 'SpO2'], ['temp', 'Temp'], ['rr', 'RR']].map(([k, l]) => (
                  <label key={k} className="text-[11px] text-slate-500">{l}<Input type="number" step="0.1" value={f[k]} onChange={set(k)} /></label>
                ))}
              </div>
              <Err msg={err} /><Btn className="w-full">Add patient + simulated device</Btn>
            </form>
          </Card>
        ) : <Card title="Registration"><p className="text-sm text-slate-500">Only administrators can register patients.</p></Card>}
      </div>
    </>
  )
}
