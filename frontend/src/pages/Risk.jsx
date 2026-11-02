import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Card, Err, LevelBadge, PatientSelect, SimBanner } from '../components/UI.jsx'

export default function Risk() {
  const { patients, pid, setPid } = usePatients()
  const { data: live, error } = useData(() => (pid ? api(`/api/patients/${pid}/live`) : Promise.resolve(null)), [pid], 4000)
  const { data: hist } = useData(() => (pid ? api(`/api/patients/${pid}/risk`) : Promise.resolve([])), [pid], 6000)
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold text-navy-900">Risk assessment</h1>
        <PatientSelect patients={patients} value={pid} onChange={setPid} />
      </div>
      <SimBanner /><Err msg={error} />
      <div className="text-xs bg-amber-50 text-amber-800 rounded-lg px-3 py-2">The risk indicator compares readings with this patient's own baseline using transparent rules. Point values are demo settings, <b>not medically validated thresholds</b>. It does not diagnose any condition.</div>
      {live && (
        <div className="grid lg:grid-cols-2 gap-5">
          <Card title="Current indicator" right={<LevelBadge level={live.risk?.level || 'unknown'} />}>
            <div className="text-sm mb-2">Assessment confidence: <b>{live.confidence || '-'}</b> (based on sensor quality and missing data)</div>
            <div className="space-y-2">
              {(live.contributions || []).map((c) => (
                <div key={c.feature} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2 text-sm">
                  <span>{c.text}</span><span className="text-xs font-semibold text-red-600 whitespace-nowrap ml-2">+{c.points} pt</span>
                </div>
              ))}
              {!(live.contributions || []).length && <div className="text-sm text-slate-500">No measurements are contributing to a warning.</div>}
            </div>
            <div className="mt-3 text-sm bg-navy-50 rounded-lg p-3"><b>Suggested caregiver action:</b> {live.risk?.action || '-'}</div>
          </Card>
          <Card title="Assessment history" className="max-h-[480px] overflow-y-auto">
            {(hist || []).map((h) => (
              <div key={h.id} className="border-b border-slate-100 py-2 text-xs">
                <div className="flex justify-between"><LevelBadge level={h.level} /><span className="text-slate-400">{fmtDateTime(h.ts)}</span></div>
                <div className="text-slate-600 mt-1">{h.reasons.join('; ')}</div>
              </div>
            ))}
          </Card>
        </div>
      )}
    </>
  )
}
