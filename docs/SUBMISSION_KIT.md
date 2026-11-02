# project detiles
**Title:** WARD360 AI - An Intelligent IoT and AI-Powered Home Hospital Monitoring and Early Warning System
**Tagline:** Your Home. Your Health. One Intelligent Ward.

**Problem:** Hospitals detect deterioration through continuous monitoring and trained staff. At home, patients rely on family who have no early-warning tools, so changes are noticed late.

**Solution:** Turn a bedroom into a "ward". Sensors (simulated, ESP32-ready) stream HR, SpO2, temperature, respiration, activity and motion to a FastAPI backend. AI compares each patient with their *own* baseline, explains unusual patterns, estimates a transparent risk indicator, and alerts caregivers with escalation if nobody responds.

**Innovation:** (1) personal baselines instead of fixed thresholds; (2) explainable warnings with reasons and suggested action; (3) missing/disconnected sensors are treated as risk, never as "normal"; (4) alert escalation workflow; (5) emergency path independent of AI; (6) responsible framing - decision support, synthetic data, experimental features clearly labelled.

**Tech:** React + Vite + Tailwind + Recharts | FastAPI + SQLAlchemy + WebSockets | scikit-learn Isolation Forest, NumPy/Pandas | JWT + bcrypt + RBAC + audit logs | Docker.

**Slides outline (10):** 1 Title - 2 Problem - 3 Solution - 4 Architecture - 5 Workflow - 6 AI/ML - 7 Live demo screenshots - 8 Security & responsible AI - 9 Testing (10 scenarios) - 10 Future scope.

**Future scope:** real ESP32 + MAX30102 sensors over MQTT; PostgreSQL; clinically validated models with clinician partners; real SMS/WhatsApp/push; Hindi/regional-language voice; offline-first mobile app; FHIR export.
