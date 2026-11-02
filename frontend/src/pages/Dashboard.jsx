import { Link } from 'react-router-dom'
import { AlertTriangle, Cpu, ShieldAlert, Users } from 'lucide-react'
import { api } from '../api.js'
import { useData, fmtTime } from '../hooks.js'
import { Card, LevelBadge, SimBanner, StatusBadge } from '../components/UI.jsx'
import SimulatorPanel from '../components/SimulatorPanel.jsx'

const Stat = ({ icon: Icon, label, value, tone }) => (
  <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-3">
    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${tone}`}><Icon size={20} /></div>
    <div><div className="text-2xl font-bold text-navy-900">{value}</div><div className="text-xs text-slate-500">{label}</div></div>
  </div>
)

export default function Dashboard() {
  const { data: patients } = useData(() => api('/api/patients'), [], 4000)
  const { data: alerts } = useData(() => api('/api/alerts?limit=8'), [], 4000)
  const open = (alerts || []).filter((a) => a.status !== 'acknowledged')
  return (
    <>
      <div><h1 className="text-2xl font-bold text-navy-900">Ward overview</h1><p className="text-sm text-slate-500">All monitored patients at a glance</p></div>
      <SimBanner />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Stat icon={Users} label="Patients" value={patients?.length ?? '-'} tone="bg-navy-50 text-navy-700" />
        <Stat icon={AlertTriangle} label="Active alerts" value={open.length} tone="bg-amber-100 text-amber-700" />
        <Stat icon={ShieldAlert} label="Critical patients" value={(patients || []).filter((p) => p.has_critical).length} tone="bg-red-100 text-red-700" />
        <Stat icon={Cpu} label="Devices online" value={(patients || []).filter((p) => p.device?.status === 'online').length} tone="bg-emerald-100 text-emerald-700" />
      </div>
      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 grid sm:grid-cols-2 gap-4">
          {(patients || []).map((p) => (
            <Link key={p.id} to={`/patients/${p.id}`} className={`bg-white rounded-2xl border shadow-sm p-4 hover:shadow-md transition ${p.has_critical ? 'border-red-300' : 'border-slate-100'}`}>
              <div className="flex justify-between items-start">
                <div><div className="font-semibold text-navy-900">{p.name}</div><div className="text-xs text-slate-500">{p.age} y · {p.gender}</div></div>
                <LevelBadge level={p.risk?.level || 'unknown'} />
              </div>
              <div className="grid grid-cols-3 gap-2 my-3 text-center">
                {[['HR', p.latest?.heart_rate, 'text-red-600'], ['SpO2', p.latest?.spo2, 'text-blue-600'], ['Temp', p.latest?.temperature, 'text-amber-600']].map(([l, v, c]) => (
                  <div key={l} className="bg-slate-50 rounded-lg py-2"><div className={`text-lg font-bold ${c}`}>{v ?? '--'}</div><div className="text-[11px] text-slate-500">{l}</div></div>
                ))}
              </div>
              <div className="flex items-center justify-between text-xs">
                {p.device ? <StatusBadge status={p.device.status} /> : <span />}
                <span className="text-slate-500">{p.open_alerts} open alert(s)</span>
              </div>
            </Link>
          ))}
          {patients?.length === 0 && <div className="text-sm text-slate-500">No patients assigned to you yet.</div>}
        </div>
        <div className="space-y-5">
          <Card title="Recent alerts" right={<Link to="/alerts" className="text-xs text-navy-700">View all</Link>}>
            <div className="space-y-2">
              {(alerts || []).slice(0, 6).map((a) => (
                <div key={a.id} className="text-xs border-b border-slate-100 pb-2">
                  <div className="flex justify-between"><LevelBadge level={a.level} /><span className="text-slate-400">{fmtTime(a.created_at)}</span></div>
                  <div className="mt-1 text-slate-600">{a.patient_name}: {a.message.slice(0, 90)}</div>
                </div>
              ))}
              {alerts?.length === 0 && <div className="text-sm text-slate-400">No alerts yet.</div>}
            </div>
          </Card>
          <SimulatorPanel patients={patients} />
        </div>
      </div>
    </>
  )
}
