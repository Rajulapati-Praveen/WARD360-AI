import { useState } from 'react'
import { HeartPulse } from 'lucide-react'
import { useAuth } from '../auth.jsx'
import { Btn, Err, Input, SimBanner } from '../components/UI.jsx'

const DEMO = [['Admin', 'admin@ward360.test', 'Admin@123'], ['Caregiver', 'caregiver@ward360.test', 'Care@123'], ['Doctor', 'doctor@ward360.test', 'Doctor@123']]

export default function Login() {
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    try { await login(email, password) } catch (x) { setErr(x.message) } finally { setBusy(false) }
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-sky-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-7 space-y-5">
        <div className="text-center">
          <div className="mx-auto w-12 h-12 rounded-xl bg-navy-900 text-sky-400 flex items-center justify-center mb-2"><HeartPulse /></div>
          <h1 className="text-2xl font-bold text-navy-900">WARD360 AI</h1>
          <p className="text-sm text-slate-500">Your Home. Your Health. One Intelligent Ward.</p>
        </div>
        <form onSubmit={submit} className="space-y-3">
          <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Err msg={err} />
          <Btn className="w-full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</Btn>
        </form>
        <div>
          <div className="text-xs text-slate-500 mb-1">Demo accounts (synthetic) - tap to fill:</div>
          <div className="flex gap-2 flex-wrap">
            {DEMO.map(([n, e, p]) => <button key={n} type="button" onClick={() => { setEmail(e); setPassword(p) }} className="text-xs px-3 py-1.5 rounded-full bg-navy-50 text-navy-800 hover:bg-navy-100">{n}</button>)}
          </div>
        </div>
        <SimBanner />
      </div>
    </div>
  )
}
