import { useState } from 'react'
import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { Btn, Card, Err, Input, LevelBadge, StatusBadge } from '../components/UI.jsx'

const TABS = [['', 'All'], ['open', 'Open'], ['escalated', 'Escalated'], ['acknowledged', 'Acknowledged']]

export default function Alerts() {
  const [tab, setTab] = useState('')
  const { data, reload, error } = useData(() => api('/api/alerts?limit=150' + (tab ? `&status=${tab}` : '')), [tab], 4000)
  const [notes, setNotes] = useState({})
  const [err, setErr] = useState('')
  const ack = async (id) => {
    try { await api(`/api/alerts/${id}/acknowledge`, { method: 'POST', body: { note: notes[id] || '' } }); reload() } catch (e) { setErr(e.message) }
  }
  return (
    <>
      <h1 className="text-2xl font-bold text-navy-900">Alert centre</h1>
      <div className="flex gap-2 flex-wrap">{TABS.map(([k, l]) => (
        <button key={k} onClick={() => setTab(k)} className={`px-3 py-1.5 rounded-full text-sm ${tab === k ? 'bg-navy-700 text-white' : 'bg-white border border-slate-200'}`}>{l}</button>))}</div>
      <Err msg={error || err} />
      <div className="space-y-3">
        {(data || []).map((a) => (
          <Card key={a.id} className={a.status === 'escalated' ? 'border-fuchsia-300' : a.status === 'open' && a.level === 'critical' ? 'border-red-300' : ''}>
            <div className="flex items-start justify-between gap-2 flex-wrap">
              <div className="flex items-center gap-2 flex-wrap"><LevelBadge level={a.level} /><StatusBadge status={a.status} />
                <span className="text-xs bg-slate-100 rounded-full px-2 py-1">{a.source}</span><b className="text-sm">{a.patient_name}</b></div>
              <span className="text-xs text-slate-400">{fmtDateTime(a.created_at)}</span>
            </div>
            <p className="text-sm mt-2">{a.message}</p>
            {a.source === 'fall' && <p className="text-xs text-purple-700">Experimental fall-event detection.</p>}
            {a.escalated_at && <p className="text-xs text-fuchsia-700 mt-1">Escalated (not acknowledged in time) at {fmtDateTime(a.escalated_at)}</p>}
            {a.acknowledgements.map((k, i) => <p key={i} className="text-xs text-emerald-700 mt-1">Acknowledged by {k.by} at {fmtDateTime(k.ts)}{k.note ? ` - “${k.note}”` : ''}</p>)}
            <details className="mt-2"><summary className="text-xs text-slate-500 cursor-pointer">Notifications ({a.notifications.length}, simulated)</summary>
              {a.notifications.map((n, i) => <div key={i} className="text-xs text-slate-500 mt-1">{fmtDateTime(n.ts)} · {n.channel} → user #{n.user_id} ({n.kind})</div>)}</details>
            {a.status !== 'acknowledged' && (
              <div className="flex gap-2 mt-3"><Input placeholder="Optional note" value={notes[a.id] || ''} onChange={(e) => setNotes({ ...notes, [a.id]: e.target.value })} />
                <Btn onClick={() => ack(a.id)}>Acknowledge</Btn></div>
            )}
          </Card>
        ))}
        {data?.length === 0 && <div className="text-sm text-slate-400">No alerts.</div>}
      </div>
    </>
  )
}
