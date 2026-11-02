export const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const getToken = () => localStorage.getItem('w360_token')

export async function api(path, { method = 'GET', body, raw } = {}) {
  const token = getToken()
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401 && token) {
    localStorage.removeItem('w360_token')
    window.location.href = `${import.meta.env.BASE_URL}login`
  }
  if (!res.ok) {
    const e = await res.json().catch(() => ({}))
    const d = e.detail
    throw new Error(typeof d === 'string' ? d : Array.isArray(d) ? d.map((x) => x.msg).join('; ') : res.statusText)
  }
  return raw ? res : res.json()
}

export const wsUrl = () => BASE.replace(/^http/, 'ws') + '/ws?token=' + encodeURIComponent(getToken() || '')

export async function downloadPdf(patientId, period) {
  const res = await api(`/api/reports/${patientId}/pdf?period=${period}`, { raw: true })
  const blob = await res.blob()
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `ward360-${period}-patient${patientId}.pdf`
  a.click()
}
