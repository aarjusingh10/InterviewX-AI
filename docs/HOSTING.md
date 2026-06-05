# Hosting InterviewX AI

## Best Simple Option: Render

This repo includes `render.yaml`, which creates:

- `interviewx-ai-web`: React frontend static site
- `interviewx-ai-api`: FastAPI backend
- `interviewx-ai-db`: PostgreSQL database

## Steps

1. Push this repo to GitHub.
2. Open Render.
3. Choose `New` -> `Blueprint`.
4. Connect the GitHub repo.
5. Select the repo and apply the blueprint.
6. Wait for both services to deploy.
7. Open the frontend URL Render gives you.

Expected URLs if names are available:

- Frontend: `https://interviewx-ai-web.onrender.com`
- Backend health: `https://interviewx-ai-api.onrender.com/health`
- Backend docs: `https://interviewx-ai-api.onrender.com/docs`

If Render changes the service URL, update:

- frontend service env var: `VITE_API_BASE_URL`
- backend service env var: `FRONTEND_ORIGIN`

## GitHub Pages Option

GitHub Pages can host only the frontend. It cannot run FastAPI, PostgreSQL, ChromaDB, or Docker.

Frontend-only demo:

`https://aarjusingh10.github.io/InterviewX-AI/`

For full production behavior, use Render or another backend host.

## Important

Do not use `localhost` links for hosted apps. `localhost` only means your own computer.

