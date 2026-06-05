# Hosting InterviewX AI

## Fastest Working Option: Render Static Site

This repo includes `render.yaml`, which creates:

- `interviewx-ai-web`: React frontend static site

The hosted frontend runs in demo mode if no backend URL is configured. This avoids Render free-tier database limits and gives you a public website immediately.

## Steps

1. Push this repo to GitHub.
2. Open Render.
3. Choose `New` -> `Blueprint`.
4. Connect the GitHub repo.
5. Select the repo and apply the blueprint.
6. Wait for both services to deploy.
7. Open the frontend URL Render gives you.

Expected URL if the name is available:

- Frontend: `https://interviewx-ai-web.onrender.com`

## Full Backend Later

For full backend APIs, create a separate paid or available PostgreSQL database and deploy the FastAPI backend as a separate Render web service. Render free accounts can fail Blueprint creation when there is already one active free database.

## GitHub Pages Option

GitHub Pages can host only the frontend. It cannot run FastAPI, PostgreSQL, ChromaDB, or Docker.

Frontend-only demo:

`https://aarjusingh10.github.io/InterviewX-AI/`

For full production behavior, use Render or another backend host.

## Important

Do not use `localhost` links for hosted apps. `localhost` only means your own computer.
