import { useState } from 'react'
import { Mic, Siren, Phone, HeartPulse } from 'lucide-react'
import { api } from '../api.js'
import { Btn, Input } from './UI.jsx'

/**
 * Emergency assistant. Commands are matched with plain keyword rules - NOT an AI chatbot - so an
 * emergency request never depends on an AI model. Text input is the fallback when speech is unavailable.
 */
export default function VoiceAssistant({ patientId, live }) {
  const [text, setText] = useState('')
  const [reply, setReply] = useState('')
  const [listening, setListening] = useState(false)
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition

  const run = async (raw, via = 'text') => {
    const t = raw.toLowerCase()
    try {
      if (/(help|emergency|ambulance|sos)/.test(t)) {
        await api(`/api/patients/${patientId}/emergency`, { method: 'POST', body: { message: raw.slice(0, 200), via } })
        setReply('Emergency alert sent to your caregivers.')
      } else if (/(call|caregiver|nurse)/.test(t)) {
        await api(`/api/patients/${patientId}/emergency`, { method: 'POST', body: { message: 'Caregiver call requested: ' + raw.slice(0, 150), via } })
        setReply('Caregiver has been notified and asked to call you (simulated).')
      } else if (/(status|health|how am i)/.test(t)) {
        const r = live?.reading
        setReply(r ? `Heart rate ${r.heart_rate ?? '--'}, SpO2 ${r.spo2 ?? '--'}, temperature ${r.temperature ?? '--'}, risk level: ${live.risk?.level || 'unknown'}. (Simulated data)` : 'No readings yet.')
      } else setReply('Command not recognised. Try: "I need help", "Show my health status", "Call my caregiver".')
    } catch (e) { setReply('Error: ' + e.message) }
    if ('speechSynthesis' in window) setTimeout(() => {}, 0)
  }
  const listen = () => {
    if (!SR) { setReply('Voice recognition is not available in this browser - please type your request.'); return }
    const rec = new SR()
    rec.lang = 'en-US'
    rec.onstart = () => setListening(true)
    rec.onend = () => setListening(false)
    rec.onerror = () => { setListening(false); setReply('Microphone unavailable or permission denied - please type your request.') }
    rec.onresult = (e) => { const v = e.results[0][0].transcript; setText(v); run(v, 'voice') }
    rec.start()
  }
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <Btn variant="danger" onClick={() => run('I need help', 'button')} className="flex items-center gap-1.5"><Siren size={16} />Emergency - I need help</Btn>
        <Btn variant="secondary" onClick={() => run('call my caregiver', 'button')} className="flex items-center gap-1.5"><Phone size={16} />Call caregiver</Btn>
        <Btn variant="secondary" onClick={() => run('show my health status', 'button')} className="flex items-center gap-1.5"><HeartPulse size={16} />Health status</Btn>
        <Btn variant="secondary" onClick={listen} className={`flex items-center gap-1.5 ${listening ? 'ring-2 ring-red-400' : ''}`}><Mic size={16} />{listening ? 'Listening…' : 'Speak'}</Btn>
      </div>
      <div className="flex gap-2">
        <Input value={text} onChange={(e) => setText(e.target.value)} placeholder='Type e.g. "I need help"' onKeyDown={(e) => e.key === 'Enter' && text && run(text)} />
        <Btn onClick={() => text && run(text)}>Send</Btn>
      </div>
      {reply && <div className="text-sm bg-navy-50 text-navy-900 rounded-lg px-3 py-2">{reply}</div>}
    </div>
  )
}
