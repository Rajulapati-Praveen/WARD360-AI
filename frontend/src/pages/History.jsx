import { useState } from 'react'
import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Card, Err, PatientSelect, Select, SimBanner, VITALS } from '../components/UI.jsx'
import VitalsChart, { toChart } from '../components/VitalsChart.jsx'

export default function History() {
  const { patients, pid, setPid } = usePatients()
  const [hours, setHours] = useState(1)
  const { data, error } = useData(() => (pid ? api(`/api/patients/${pid}/vitals?hours=${hours}&limit=800`) : Promise.resolve([])), [pid, hours], 10000)
  const rows = data || []
  const p = (patients || []).find((x) => x.id === pid)
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold text-navy-900">Health history</h1>
        <div className="flex gap-2"><PatientSelect patients={patients} value={pid} onChange={setPid} />
          <Select value={hours} onChange={(e) => setHours(+e.target.value)}><option value={1}>Last hour</option><option value={6}>6 hours</option><option value={24}>24 hours</option><option value={168}>7 days</option></Select></div>
      </div>
      <SimBanner /><Err msg={error} />
      <Card title={`${rows.length} readings`}>
        <div className="grid sm:grid-cols-2 gap-4">{Object.keys(VITALS).map((k) => <VitalsChart key={k} k={k} data={toChart(rows)} baseline={p?.baseline?.[k]} />)}</div>
      </Card>
      <Card title="Latest readings" className="overflow-x-auto">
        <table className="w-full text-xs"><thead><tr className="text-left text-slate-500"><th className="py-1">Time</th><th>HR</th><th>SpO2</th><th>Temp</th><th>RR</th><th>Activity</th><th>Quality</th></tr></thead>
          <tbody>{[...rows].reverse().slice(0, 60).map((r) => (
            <tr key={r.id} className="border-t border-slate-100"><td className="py-1">{fmtDateTime(r.ts)}</td><td>{r.heart_rate ?? '-'}</td><td>{r.spo2 ?? '-'}</td>
              <td>{r.temperature ?? '-'}</td><td>{r.resp_rate ?? '-'}</td><td>{r.activity}</td><td>{r.quality}</td></tr>))}</tbody></table>
      </Card>
    </>
  )
}
