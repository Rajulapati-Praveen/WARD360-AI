# WARD360 AI - Architecture

```mermaid
flowchart LR
  S[Simulated sensors<br/>iot/simulator.py or built-in] -- HTTP POST /api/ingest + device key --> API
  ESP[ESP32 optional] -.-> API
  subgraph Backend [FastAPI backend]
    API[REST API + JWT/RBAC] --> V[Validation]
    V --> DB[(SQLite / PostgreSQL)]
    V --> ML[ML engine<br/>anomaly - risk - trend - fall]
    ML --> AL[Alert service<br/>dedupe - notify - escalate]
    AL --> DB
    MON[Monitor loop<br/>device offline + escalation] --> AL
    API --> WS[WebSocket hub]
    AL --> WS
  end
  WS --> UI[React dashboard]
  UI -- REST --> API
  AL -- simulated push/SMS --> CG[Caregiver]
```

## Data flow
1. Sensor posts a reading. 2. Values validated (impossible values rejected, quality flagged). 3. Stored with timestamp.
4. Anomaly engine: personal-baseline z-scores + per-patient Isolation Forest. 5. Interpretable risk engine (reasons, persistence, sensor quality).
6. Fall check + trend check. 7. Alerts created (deduplicated), caregivers notified (simulated). 8. WebSocket pushes to dashboard.
9. Unacknowledged alerts are escalated after `ESCALATION_SECONDS`; silent devices are marked offline after `DEVICE_TIMEOUT_SECONDS`.

## ER diagram
```mermaid
erDiagram
  users ||--o{ caregiver_assignments : has
  patients ||--o{ caregiver_assignments : has
  patients ||--o{ devices : owns
  patients ||--o{ vital_readings : has
  devices ||--o{ vital_readings : sends
  patients ||--o{ risk_assessments : has
  patients ||--o{ anomaly_events : has
  vital_readings ||--o{ anomaly_events : triggers
  patients ||--o{ alerts : has
  alerts ||--o{ alert_acknowledgements : has
  users ||--o{ alert_acknowledgements : makes
  alerts ||--o{ notifications : sends
  users ||--o{ notifications : receives
  patients ||--o{ health_reports : has
  users ||--o{ audit_logs : writes
```
Indexes: `vital_readings(patient_id, ts)`, `risk_assessments(patient_id, ts)`, `alerts(patient_id, status)`, unique `users.email`, unique `(user_id, patient_id)` assignment.

## AI / ML explained (for judges)
- **Personal baseline** per patient; spread (SD) learned from history, bounded to sensible limits.
- **Statistical anomaly**: |z| >= 3 from personal baseline.
- **Isolation Forest** (scikit-learn) trained per patient on that patient's history; flags unusual *combinations*; counted only when also >= 2 SD off baseline to limit false alarms. `model_score` is NOT a clinical probability.
- **Risk engine**: transparent points by deviation size, +1 for persistence (>= 3 of last 5 readings), SpO2 only when low, raised HR/RR ignored during activity, confidence reduced by missing data. Demo values, not clinically validated.
- **Trend engine**: moving average, linear slope + R^2, abnormal-trend flag, 10-step EXPERIMENTAL forecast shown separately.
- **Fall**: accelerometer spike >= 2.5 g (experimental).
- Emergency button/voice path is plain keyword rules + direct API: it never depends on AI.
