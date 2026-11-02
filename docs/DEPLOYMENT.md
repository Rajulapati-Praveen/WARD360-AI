# Deployment

## GitHub Pages frontend-only deployment

The `.github/workflows/pages.yml` workflow builds and publishes the frontend whenever frontend files are pushed to `main`. In the repository's **Settings → Pages**, set the build and deployment source to **GitHub Actions**. The first workflow run will publish the site at `https://rajulapati-praveen.github.io/WARD360-AI/`.

This publishes only the static frontend. GitHub Pages cannot run the Python API, so login, live monitoring, and other API-backed features will not work until a backend is deployed and configured with `VITE_API_URL` and matching backend CORS settings.

## Render backend + Vercel frontend

1. In Render, create a **Blueprint** from this GitHub repository. It reads `render.yaml` and creates the `ward360-api` web service. The secret keys are generated automatically.
2. Wait for the backend deploy, then copy its URL (for example, `https://ward360-api.onrender.com`).
3. In Vercel, import the same GitHub repository and set the project **Root Directory** to `frontend`. Add the environment variable `VITE_API_URL` with the backend URL (no trailing slash), then deploy. `frontend/vercel.json` configures the Vite build and SPA routes.
4. Copy the Vercel production URL. In Render, open the backend service's environment settings and set `CORS_ORIGINS` to that exact URL (for example, `https://ward360-ai.vercel.app`), then redeploy the backend. The Blueprint's localhost value is only a placeholder until the frontend URL is known.
5. Verify the backend at `<backend-url>/api/health`, then open the Vercel URL and sign in with the seeded demo account.

The backend seeds synthetic demo data at startup. Free Render services use ephemeral local storage, so SQLite data can be lost when the service restarts. For persistence, provision PostgreSQL and set `DATABASE_URL` to its connection URL; the PostgreSQL driver is already in `backend/requirements.txt`.

## Docker

Run `docker compose up --build` -> UI http://localhost:8080, API http://localhost:8000/docs.

Free-tier services may sleep when idle; open the backend `/api/health` URL a minute before your demo.
