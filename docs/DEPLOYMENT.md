# Deployment
**Backend (Render / Railway):** root dir `backend`, build `pip install -r requirements.txt`, start `python seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
Env vars: `SECRET_KEY` (long random), `DEVICE_API_KEY`, `CORS_ORIGINS=https://<your-frontend-url>`.
SQLite resets on free tiers when the service restarts - `seed.py` recreates demo data on start. Use PostgreSQL (`DATABASE_URL`, add `psycopg2-binary`) for persistence.
**Frontend (Vercel / Netlify):** root dir `frontend`, build `npm run build`, output `dist`, env `VITE_API_URL=https://<your-backend-url>`. Add an SPA rewrite of all paths to `/index.html`.
**Docker:** `docker compose up --build` -> UI http://localhost:8080, API http://localhost:8000/docs.
Free tiers sleep when idle: open the backend `/api/health` URL a minute before your demo.
