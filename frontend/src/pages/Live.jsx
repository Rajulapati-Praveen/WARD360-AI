import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { useData } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Card, Err, LevelBadge, PatientSelect, SimBanner, Tile, VITALS } from '../components/UI.jsx'
import VitalsChart, { toChart } from '../components/VitalsChart.jsx'
import DigitalTwin from '../components/DigitalTwin.jsx'
import VoiceAssistant from '../components/VoiceAssistant.jsx'
import SimulatorPanel from '../components/SimulatorPanel.jsx'

export default function Live() {
  const { patients, pid, setPid } = usePatients()
  const { subscribe } = useAuth()
  const { data: live, error } = useData(() => (pid ? api(`/api/patients/${pid}/live`) : Promise.resolve(null)), [pid], 5000)
  const [rows, setRows] = useState([])
  useEffect(() => { if (live) setRows(live.series) }, [live?.reading?.id, pid]) // eslint-disable-line
  useEffect(() => subscribe((ev) => {
    if (ev.type === 'reading' && ev.patient_id === pid) setRows((r) => [...r.slice(-59), ev.reading])
  }), [pid, subscribe])
  const r = live?.reading
  const flagged = new Set((live?.contributions || []).map((c) => c.feature))
  const chart = toChart(rows)
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold text-navy-900">Live monitoring</h1>
        <PatientSelect patients={patients} value={pid} onChange={setPid} />
      </div>
      <SimBanner /><Err msg={error} />
      {live && (
        <>
          <Card title="Current readings" right={<LevelBadge level={live.risk?.level || 'unknown'} />}>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {Object.keys(VITALS).map((k) => <Tile key={k} k={k} value={r?.[k]} flagged={flagged.has(k)} />)}
              <div className="rounded-xl p-3 border border-slate-100 bg-slate-50"><div className="text-xs text-slate-500">Activity</div>
                <div className="text-lg font-bold capitalize text-navy-800">{r?.activity?.replace('_', ' ') || '--'}</div></div>
            </div>
            {r?.quality !== 'good' && r && <div className="mt-2 text-xs text-amber-700">Sensor data quality: {r.quality}. Some measurements are missing or invalid.</div>}
            {live.device?.status === 'offline' && <div className="mt-2 text-sm text-red-600 font-medium">Device disconnected - readings shown are the last received.</div>}
            {live.risk && (
              <div className="mt-3 text-sm bg-slate-50 rounded-lg p-3">
                <div className="font-medium mb-1">Why this status? (confidence: {live.confidence || '-'})</div>
                <ul className="list-disc ml-5 text-slate-600">{live.risk.reasons.map((x, i) => <li key={i}>{x}</li>)}</ul>
                <div className="mt-2"><b>Suggested caregiver action:</b> {live.risk.action}</div>
              </div>
            )}
          </Card>
          <div className="grid lg:grid-cols-2 gap-5">
            <Card title="Trends (last 60 readings)"><div className="grid sm:grid-cols-2 gap-3">
              {Object.keys(VITALS).map((k) => <VitalsChart key={k} k={k} data={chart} height={140} baseline={live.patient.baseline[k]} />)}</div></Card>
            <div className="space-y-5">
              <Card title="Digital twin"><DigitalTwin live={live} /></Card>
              <Card title="Emergency assistant (does not depend on AI)"><VoiceAssistant patientId={pid} live={live} /></Card>
            </div>
          </div>
          <SimulatorPanel patients={patients} patientId={pid} />
        </>
      )}
    </>
  )
}
