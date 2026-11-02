import { useState } from 'react'
import { Play, Square } from 'lucide-react'
import { api } from '../api.js'
import { useData } from '../hooks.js'
import { useAuth } from '../auth.jsx'
import { Btn, Card, Err, Select } from './UI.jsx'

const DESC = { normal: 'Normal readings', tachycardia: 'Unusual heart rate', hypoxia: 'Low oxygen (SpO2)', rising_trend: 'Gradual upward trend',
  missing: 'Missing / poor data', disconnect: 'Sensor disconnection', fall: 'Possible fall' }

export default function SimulatorPanel({ patients, patientId }) {
  const { user } = useAuth()
  const { data, reload } = useData(() => api('/api/simulator/status'), [], 4000)
  const [pid, setPid] = useState(patientId || patients?.[0]?.id)
  const [err, setErr] = useState('')
  if (user.role === 'doctor') return null
  const target = patientId || pid
  const call = (path, body) => api(path, { method: 'POST', body }).then(reload).catch((e) => setErr(e.message))
  return (
    <Card title="Sensor simulator (synthetic data)" right={data && <span className={`text-xs font-semibold ${data.running ? 'text-emerald-600' : 'text-slate-400'}`}>{data.running ? '● running' : '○ stopped'}</span>}>
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {data?.running ? <Btn variant="secondary" onClick={() => call('/api/simulator/stop')} className="flex items-center gap-1"><Square size={14} />Stop</Btn>
          : <Btn onClick={() => call('/api/simulator/start')} className="flex items-center gap-1"><Play size={14} />Start simulator</Btn>}
        {!patientId && (
          <Select value={pid || ''} onChange={(e) => setPid(Number(e.target.value))}>
            {(patients || []).map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </Select>
        )}
      </div>
      <div className="text-xs text-slate-500 mb-2">Inject a scenario for the selected patient{data?.active?.[target] ? ` (current: ${data.active[target]})` : ''}:</div>
      <div className="flex flex-wrap gap-2">
        {(data?.scenarios || []).map((s) => (
          <Btn key={s} variant="secondary" disabled={!target} onClick={() => call('/api/simulator/scenario', { patient_id: target, scenario: s })}>{DESC[s] || s}</Btn>
        ))}
      </div>
      <div className="mt-2"><Err msg={err} /></div>
    </Card>
  )
}
