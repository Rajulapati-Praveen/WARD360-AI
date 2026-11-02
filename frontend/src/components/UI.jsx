import { AlertTriangle, ShieldCheck, HelpCircle, Flame } from 'lucide-react'

export const Card = ({ title, right, children, className = '' }) => (
  <section className={`bg-white rounded-2xl shadow-sm border border-slate-100 p-4 sm:p-5 ${className}`}>
    {(title || right) && (
      <div className="flex items-center justify-between mb-3 gap-2">
        <h2 className="font-semibold text-navy-900">{title}</h2>{right}
      </div>
    )}
    {children}
  </section>
)

const LEVELS = {
  normal: ['bg-emerald-100 text-emerald-700', ShieldCheck, 'Normal'],
  warning: ['bg-amber-100 text-amber-700', AlertTriangle, 'Warning'],
  critical: ['bg-red-100 text-red-700', Flame, 'Critical'],
  unknown: ['bg-slate-100 text-slate-600', HelpCircle, 'No data'],
}
export const LevelBadge = ({ level }) => {
  const [cls, Icon, label] = LEVELS[level] || LEVELS.unknown
  return <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${cls}`}><Icon size={13} />{label}</span>
}

export const StatusBadge = ({ status }) => {
  const c = { online: 'bg-emerald-100 text-emerald-700', offline: 'bg-slate-200 text-slate-600', open: 'bg-red-100 text-red-700',
    escalated: 'bg-fuchsia-100 text-fuchsia-700', acknowledged: 'bg-emerald-100 text-emerald-700' }[status] || 'bg-slate-100 text-slate-600'
  return <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${c}`}>{status}</span>
}

export const SimBanner = () => (
  <div className="text-xs bg-navy-50 text-navy-800 border border-navy-100 rounded-lg px-3 py-2">
    <b>Synthetic / simulated data</b> - not a real measurement. WARD360 AI is a decision-support prototype, not a medical device and not a diagnosis.
  </div>
)

export const Err = ({ msg }) => msg ? <div className="bg-red-50 text-red-700 text-sm rounded-lg px-3 py-2">{msg}</div> : null
export const Btn = ({ children, className = '', variant = 'primary', ...p }) => (
  <button {...p} className={`px-3.5 py-2 rounded-lg text-sm font-medium transition disabled:opacity-50 ${
    variant === 'primary' ? 'bg-navy-700 text-white hover:bg-navy-800' : variant === 'danger' ? 'bg-red-600 text-white hover:bg-red-700'
    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'} ${className}`}>{children}</button>
)
export const Input = (p) => <input {...p} className={`w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-navy-600 ${p.className || ''}`} />
export const Select = (p) => <select {...p} className="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-navy-600" />

export const VITALS = {
  heart_rate: { label: 'Heart rate', unit: 'bpm', color: '#dc2626' },
  spo2: { label: 'SpO2', unit: '%', color: '#2563eb' },
  temperature: { label: 'Temperature', unit: '°C', color: '#d97706' },
  resp_rate: { label: 'Resp. rate', unit: '/min', color: '#059669' },
}
export const Tile = ({ k, value, flagged }) => (
  <div className={`rounded-xl p-3 border ${flagged ? 'border-red-300 bg-red-50' : 'border-slate-100 bg-slate-50'}`}>
    <div className="text-xs text-slate-500">{VITALS[k].label}</div>
    <div className="text-2xl font-bold" style={{ color: VITALS[k].color }}>{value ?? '--'}<span className="text-xs text-slate-400 ml-1">{VITALS[k].unit}</span></div>
  </div>
)

export function PatientSelect({ patients, value, onChange }) {
  return (
    <Select value={value || ''} onChange={(e) => onChange(Number(e.target.value))}>
      {(patients || []).map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
    </Select>
  )
}
