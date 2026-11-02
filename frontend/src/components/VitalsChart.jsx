import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { VITALS } from './UI.jsx'

export default function VitalsChart({ data, k, height = 180, baseline }) {
  const v = VITALS[k]
  return (
    <div>
      <div className="text-xs font-medium text-slate-500 mb-1">{v.label} ({v.unit})</div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ left: -18, right: 8, top: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="t" tick={{ fontSize: 10 }} minTickGap={40} />
          <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} />
          <Tooltip />
          {baseline != null && <ReferenceLine y={baseline} stroke="#94a3b8" strokeDasharray="4 4" label={{ value: 'baseline', fontSize: 10, fill: '#94a3b8' }} />}
          <Line type="monotone" dataKey={k} stroke={v.color} strokeWidth={2} dot={false} connectNulls isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export const toChart = (rows) => rows.map((r) => ({ ...r, t: new Date(r.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) }))
