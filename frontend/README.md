# Mini Jira frontend

React + TypeScript + Vite client for the Mini Jira API.

```bash
npm install
npm run dev      # http://localhost:5173
npm run lint
npm run build
```

The API must be running on `http://localhost:8000`. To use another address, copy `.env.example` to `.env.local` and change `VITE_API_URL`. The backend only accepts browser requests from origins listed in its `CORS_ORIGINS` setting.

## Docker

From the repo root, `docker compose up --build` builds this image and serves it at http://localhost:5173. `VITE_API_URL` is baked in at build time (default `http://localhost:8000`); changing it needs a rebuild. Compose sets `CORS_ORIGINS` from `FRONTEND_PORT`, so changing the published port still lets the browser call the API.

## Layout

- `src/api/client.ts`: `api()` calls `/api/v1`, sends the access token, and refreshes it once on a 401.
- `src/api/types.ts`: response types that mirror `backend/app/schemas`.
- `src/auth/`: `AuthProvider` keeps the logged-in user; `useAuth()` reads it.
- `src/pages/`: log on, sign up, and the main window. From the window you can create teams, projects, and tasks, invite members, and open a task to edit it, comment, and label it.
