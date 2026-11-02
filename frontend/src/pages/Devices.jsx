import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Card, SimBanner, StatusBadge } from '../components/UI.jsx'
import SimulatorPanel from '../components/SimulatorPanel.jsx'

export default function Devices() {
  const { data } = useData(() => api('/api/devices'), [], 4000)
  const { patients } = usePatients()
  return (
    <>
      <h1 className="text-2xl font-bold text-navy-900">Device management</h1>
      <SimBanner />
      <Card title="Connected devices" className="overflow-x-auto">
        <table className="w-full text-sm"><thead><tr className="text-left text-xs text-slate-500"><th className="py-1">Device</th><th>Patient</th><th>Type</th><th>Status</th><th>Battery</th><th>Last seen</th></tr></thead>
          <tbody>{(data || []).map((d) => (
            <tr key={d.id} className="border-t border-slate-100"><td className="py-2.5 font-medium">{d.name}</td><td>{d.patient_name}</td><td>{d.kind}</td>
              <td><StatusBadge status={d.status} /></td>
              <td><div className="w-24 h-2 bg-slate-100 rounded-full inline-block align-middle mr-2"><div className={`h-2 rounded-full ${d.battery <= 15 ? 'bg-red-500' : 'bg-emerald-500'}`} style={{ width: `${d.battery}%` }} /></div>{d.battery}%</td>
              <td className="text-xs text-slate-500">{fmtDateTime(d.last_seen)}</td></tr>))}</tbody></table>
        <p className="text-xs text-slate-500 mt-3">Devices are marked offline automatically when no data arrives for ~20 seconds, and a caregiver alert is raised. Real hardware (e.g. ESP32) can POST to <code>/api/ingest</code> with the device key.</p>
      </Card>
      <SimulatorPanel patients={patients} />
    </>
  )
}
