import { LevelBadge, StatusBadge } from './UI.jsx'

/** Visual representation of RECORDED monitoring information - not a physiological simulation. */
export default function DigitalTwin({ live }) {
  const r = live?.reading
  const flagged = new Set((live?.contributions || []).map((c) => c.feature))
  const level = live?.risk?.level || 'unknown'
  const col = (f) => (flagged.has(f) ? '#dc2626' : r?.[f] == null ? '#94a3b8' : '#10b981')
  const dev = live?.device
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-center">
      <svg viewBox="0 0 160 260" className="w-40 shrink-0">
        <circle cx="80" cy="28" r="20" fill="#e2e8f0" stroke={col('temperature')} strokeWidth="4" />
        <rect x="52" y="52" width="56" height="90" rx="22" fill="#e2e8f0" />
        <rect x="26" y="56" width="20" height="80" rx="10" fill="#e2e8f0" />
        <rect x="114" y="56" width="20" height="80" rx="10" fill="#e2e8f0" />
        <rect x="58" y="140" width="20" height="100" rx="10" fill="#e2e8f0" />
        <rect x="82" y="140" width="20" height="100" rx="10" fill="#e2e8f0" />
        <ellipse cx="68" cy="82" rx="10" ry="15" fill={col('spo2')} opacity=".85" />
        <ellipse cx="92" cy="82" rx="10" ry="15" fill={col('resp_rate')} opacity=".85" />
        <circle cx="76" cy="104" r="9" fill={col('heart_rate')} className={flagged.has('heart_rate') ? 'pulse' : ''} />
        <rect x="26" y="128" width="20" height="9" rx="4" fill={dev?.status === 'online' ? '#0ea5e9' : '#94a3b8'} />
      </svg>
      <div className="text-sm space-y-2 w-full">
        <div className="flex items-center gap-2"><span className="text-slate-500">Monitoring status</span><LevelBadge level={level} /></div>
        <div className="flex items-center gap-2"><span className="text-slate-500">Device</span>{dev ? <><StatusBadge status={dev.status} /><span className="text-xs text-slate-500">battery {dev.battery}%</span></> : '-'}</div>
        <div><span className="text-slate-500">Activity: </span><b className="capitalize">{r?.activity?.replace('_', ' ') || '-'}</b></div>
        <div className="text-xs text-slate-500">Legend: green = within personal baseline, red = flagged, grey = no data. Head = temperature, lungs = SpO2 / respiration, heart = heart rate.</div>
        <div>
          <div className="text-xs text-slate-500 mb-1">Recent warnings</div>
          {(live?.recent_alerts || []).slice(0, 3).map((a) => <div key={a.id} className="text-xs truncate">• {a.message}</div>)}
          {!(live?.recent_alerts || []).length && <div className="text-xs text-slate-400">None</div>}
        </div>
      </div>
    </div>
  )
}
