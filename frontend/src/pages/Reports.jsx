import { useState } from 'react'
import { Download } from 'lucide-react'
import { api, downloadPdf } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Btn, Card, Err, PatientSelect, Select, SimBanner } from '../components/UI.jsx'

export default function Reports() {
  const { patients, pid, setPid } = usePatients()
  const [period, setPeriod] = useState('daily')
  const [err, setErr] = useState('')
  const { data: r, error } = useData(() => (pid ? api(`/api/reports/${pid}/summary?period=${period}`) : Promise.resolve(null)), [pid, period], 15000)
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold text-navy-900">Health reports</h1>
        <div className="flex gap-2 flex-wrap"><PatientSelect patients={patients} value={pid} onChange={setPid} />
          <Select value={period} onChange={(e) => setPeriod(e.target.value)}><option value="daily">Daily</option><option value="weekly">Weekly</option></Select>
          <Btn onClick={() => downloadPdf(pid, period).catch((e) => setErr(e.message))} className="flex items-center gap-1"><Download size={15} />Export PDF</Btn></div>
      </div>
      <SimBanner /><Err msg={error || err} />
      {r && (
        <>
          <Card title={`${period} summary - ${r.patient.name}`}>
            <table className="w-full text-sm"><thead><tr className="text-left text-xs text-slate-500"><th>Measurement</th><th>Min</th><th>Mean</th><th>Max</th><th>Readings</th></tr></thead>
              <tbody>{Object.entries(r.stats).map(([k, s]) => <tr key={k} className="border-t border-slate-100"><td className="py-2">{r.labels[k]}</td><td>{s.min}</td><td>{s.mean}</td><td>{s.max}</td><td>{s.count}</td></tr>)}</tbody></table>
            <div className="text-sm mt-3">Sensor availability: <b>{r.availability.good_pct}%</b> good-quality ({r.availability.total} readings, {r.availability.poor} poor, {r.availability.missing} missing)</div>
            <div className="text-sm">Risk observations: {Object.entries(r.risk_counts).map(([k, v]) => `${k}: ${v}`).join(' · ')}</div>
          </Card>
          <div className="grid lg:grid-cols-2 gap-5">
            <Card title={`Anomaly observations (${r.anomaly_count})`} className="max-h-80 overflow-y-auto">
              {r.anomalies.map((a) => <div key={a.id} className="text-xs border-b border-slate-100 py-1.5"><span className="text-slate-400">{fmtDateTime(a.ts)}</span> {a.explanation}</div>)}
              {!r.anomalies.length && <div className="text-sm text-slate-400">None in this period.</div>}
            </Card>
            <Card title={`Alerts & acknowledgements (${r.alert_count})`} className="max-h-80 overflow-y-auto">
              {r.alerts.map((a) => <div key={a.id} className="text-xs border-b border-slate-100 py-1.5"><b className="capitalize">{a.level}</b> · {a.source} · {a.status}
                <div className="text-slate-500">{a.message.slice(0, 100)}</div>{a.acknowledgements.map((k, i) => <div key={i} className="text-emerald-700">✓ {k.by} {fmtDateTime(k.ts)}</div>)}</div>)}
              {!r.alerts.length && <div className="text-sm text-slate-400">None in this period.</div>}
            </Card>
          </div>
        </>
      )}
    </>
  )
}
