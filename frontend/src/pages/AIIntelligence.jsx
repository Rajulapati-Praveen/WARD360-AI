import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api.js'
import { useData, fmtDateTime } from '../hooks.js'
import { usePatients } from '../hooks2.js'
import { Card, Err, PatientSelect, SimBanner, VITALS } from '../components/UI.jsx'

const ARROW = { rising: '↗ Rising', falling: '↘ Falling', stable: '→ Stable', unknown: '? Not enough data' }

function TrendCard({ k, t }) {
  const v = VITALS[k]
  const hist = t.history.slice(-40).map((p) => ({ x: p.ts, value: p.value, ma: p.ma }))
  const fc = t.forecast.map((p) => ({ x: p.ts, forecast: p.value }))
  const data = [...hist, ...fc]
  const time = (s) => new Date(s * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  return (
    <Card title={v.label} right={<span className={`text-xs font-semibold ${t.abnormal ? 'text-red-600' : 'text-slate-500'}`}>{ARROW[t.direction]}{t.abnormal ? ' · abnormal trend' : ''}</span>}>
      <ResponsiveContainer width="100%" height={170}>
        <LineChart data={data} margin={{ left: -18, right: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="x" tickFormatter={time} tick={{ fontSize: 10 }} minTickGap={50} />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} />
          <Tooltip labelFormatter={time} />
          <Line dataKey="value" name="measured" stroke={v.color} dot={false} strokeWidth={1.5} isAnimationActive={false} connectNulls />
          <Line dataKey="ma" name="moving avg" stroke="#0b1f44" dot={false} strokeWidth={2} isAnimationActive={false} connectNulls />
          <Line dataKey="forecast" name="EXPERIMENTAL forecast" stroke="#a855f7" strokeDasharray="5 4" dot={false} strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
      <div className="text-xs text-slate-500">
        {t.enough_data ? `Deviation from baseline ${t.baseline}: ${t.baseline_deviation > 0 ? '+' : ''}${t.baseline_deviation} · change over window ${t.change_over_window}` : 'Collecting more data…'}
      </div>
    </Card>
  )
}

export default function AIIntelligence() {
  const { patients, pid, setPid } = usePatients()
  const { data, error } = useData(() => (pid ? api(`/api/patients/${pid}/analysis`) : Promise.resolve(null)), [pid], 5000)
  return (
    <>
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div><h1 className="text-2xl font-bold text-navy-900">AI Intelligence Centre</h1>
          <p className="text-sm text-slate-500">Personal-baseline statistics · Isolation Forest · trend analysis</p></div>
        <PatientSelect patients={patients} value={pid} onChange={setPid} />
      </div>
      <SimBanner /><Err msg={error} />
      {data && (
        <>
          <div className="text-xs bg-purple-50 text-purple-800 rounded-lg px-3 py-2"><b>EXPERIMENTAL:</b> purple dashed lines are simple linear forecasts, shown separately from measured history. They are not reliable medical predictions.</div>
          <div className="grid lg:grid-cols-2 gap-5">{Object.entries(data.trends).map(([k, t]) => <TrendCard key={k} k={k} t={t} />)}</div>
          <Card title="Anomaly events" className="overflow-x-auto">
            <p className="text-xs text-slate-500 mb-2">Model score = Isolation Forest score (lower = more unusual). It is <b>not</b> a clinical probability.</p>
            <table className="w-full text-sm"><thead><tr className="text-left text-xs text-slate-500"><th className="py-1">Time</th><th>Measurement</th><th>Model score</th><th>Explanation</th></tr></thead>
              <tbody>{data.anomalies.map((a) => (
                <tr key={a.id} className="border-t border-slate-100 align-top"><td className="py-2 whitespace-nowrap">{fmtDateTime(a.ts)}</td>
                  <td>{data.labels[a.feature] || a.feature}</td><td>{a.model_score}</td><td className="text-slate-600">{a.explanation}</td></tr>))}</tbody></table>
            {!data.anomalies.length && <div className="text-sm text-slate-400 py-3">No anomalies detected yet. Try the simulator scenarios.</div>}
          </Card>
        </>
      )}
    </>
  )
}
