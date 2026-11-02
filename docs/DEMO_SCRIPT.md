# Demo video script (about 4 minutes)
1. (0:00) Problem: hospitals watch patients continuously; at home families don't. Show login page + synthetic-data banner.
2. (0:25) Login as caregiver. Dashboard: 3 patients. Click **Start simulator**.
3. (0:50) Live Monitoring: readings update live over WebSocket; digital twin; baseline lines on charts.
4. (1:20) Inject **Low oxygen**. Show risk go Warning -> Critical, "Why this status?" reasons, suggested action.
5. (2:00) Alert Centre: new alert, simulated notification. Wait ~60s -> **escalated**. Then acknowledge with a note.
6. (2:30) AI Intelligence: anomaly explanation + model score, trend with experimental forecast. Run **Gradual upward trend** to show early warning.
7. (3:00) **Sensor disconnection** -> device offline alert. **Possible fall** -> experimental fall alert.
8. (3:20) Emergency assistant: type "I need help" / use mic. Stress: works without AI.
9. (3:35) Reports -> Export PDF. Login as another caregiver / show 403 + audit log (admin).
10. (3:55) Close: architecture, tests (11 passing), future scope (ESP32/MQTT, PostgreSQL, validated clinical models).
