# Hosting InterviewX AI

## Render Frontend + Backend

This repo includes `render.yaml`, which creates:

- `interviewx-ai-web`: React frontend static site
- `interviewx-ai-api`: FastAPI backend service

The backend uses SQLite on Render to avoid the free-tier PostgreSQL database limit. This is suitable for a hosted demo. For production, move `DATABASE_URL` to PostgreSQL from Neon, Supabase, Render paid database, or another managed provider.

## Steps

1. Push this repo to GitHub.
2. Open Render.
3. Choose `New` -> `Blueprint`.
4. Connect the GitHub repo.
5. Select the repo and apply the blueprint.
6. Wait for both services to deploy.
7. Open the frontend URL Render gives you.

Expected URLs if the names are available:

- Frontend: `https://interviewx-ai-web.onrender.com`
- Backend health: `https://interviewx-ai-api.onrender.com/health`
- Backend docs: `https://interviewx-ai-api.onrender.com/docs`

If Render adds a suffix to either service name, update these environment variables:

- frontend `VITE_API_BASE_URL`
- backend `FRONTEND_ORIGIN`

## Production Database Later

For durable production data, create a managed PostgreSQL database and set backend `DATABASE_URL` to that connection string. SQLite on free Render can reset when the service is redeployed or restarted.

## GitHub Pages Option

GitHub Pages can host only the frontend. It cannot run FastAPI, PostgreSQL, ChromaDB, or Docker.

Frontend-only demo:

`https://aarjusingh10.github.io/InterviewX-AI/`

For full production behavior, use Render or another backend host.

## Important

Do not use `localhost` links for hosted apps. `localhost` only means your own computer.
