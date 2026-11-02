import { useEffect, useState } from 'react'
import { api } from './api.js'
import { useData } from './hooks.js'

/** Patient list + selected patient id. */
export function usePatients() {
  const { data: patients, reload } = useData(() => api('/api/patients'), [], 6000)
  const [pid, setPid] = useState(null)
  useEffect(() => { if (patients?.length && !patients.find((p) => p.id === pid)) setPid(patients[0].id) }, [patients]) // eslint-disable-line
  return { patients, pid, setPid, reload }
}
