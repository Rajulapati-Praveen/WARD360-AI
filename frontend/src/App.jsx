import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth.jsx'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Patients from './pages/Patients.jsx'
import PatientDetails from './pages/PatientDetails.jsx'
import Live from './pages/Live.jsx'
import AIIntelligence from './pages/AIIntelligence.jsx'
import Risk from './pages/Risk.jsx'
import Alerts from './pages/Alerts.jsx'
import History from './pages/History.jsx'
import Reports from './pages/Reports.jsx'
import Devices from './pages/Devices.jsx'
import Settings from './pages/Settings.jsx'

export default function App() {
  const { user, ready } = useAuth()
  if (!ready) return <div className="p-10 text-slate-500">Loading…</div>
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route element={user ? <Layout /> : <Navigate to="/login" />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/patients" element={<Patients />} />
        <Route path="/patients/:id" element={<PatientDetails />} />
        <Route path="/live" element={<Live />} />
        <Route path="/ai" element={<AIIntelligence />} />
        <Route path="/risk" element={<Risk />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/history" element={<History />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/devices" element={<Devices />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}
