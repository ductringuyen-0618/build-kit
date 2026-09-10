# vite-react

Vite + React + TypeScript single-page frontend in `frontend/`. Dev server on
port 5173; production is static files in `dist/` (no port, no health path).
On App Platform it is a `static_sites` component, so the Dockerfile is only
for Docker-based hosts.

## Scaffold (from the repo root)

```
npm create vite@latest frontend -- --template react-ts && cd frontend && npm i
npm i -D prettier && cp <kit>/templates/vite-react/{Dockerfile,.env.example} .
```

Add these scripts to `package.json` (Vite's scaffold gives `dev`, `build`, `lint`, `preview`):

```json
"typecheck": "tsc --noEmit",
"format:check": "prettier --check src",
"verify": "npm run typecheck && npm run lint && npm run format:check && npm run build"
```

`src/config/api.ts` resolves the API base once:

```ts
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? window.location.origin;
```

First check: `npm run verify` passes and `dist/index.html` exists.

## Commands (run from `frontend/`)

| Task | Command |
| --- | --- |
| run | `npm run dev` (http://localhost:5173) |
| test | `npm run verify` (typecheck + lint + format + build; add Playwright specs if time allows) |
| lint | `npm run lint && npm run typecheck` |
| build | `npm run build` (writes `dist/`) |
| image | `docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t web .` |

## Files in this folder

- `Dockerfile`: Node build stage, unprivileged nginx serving `dist/` on 8080 with SPA fallback. Copy to `frontend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job running `npm run verify`. Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: the one variable the browser bundle reads. Copy to `frontend/.env.example`; `.env.local` is git-ignored.
- `app-component.yaml`: App Platform `static_sites:` entry. Paste into `.do/app.yaml` and route `/` to it.

## Conventions

- Only `VITE_`-prefixed variables reach the browser, and they are baked in at build time.
- Leave `VITE_API_BASE_URL` unset in production so calls go same-origin through the
  ingress rule that sends `/api` to the backend; set it to the backend's local URL in dev.
- Call the backend's exact path form (with or without trailing slash) to avoid redirects
  that drop CORS headers.
- One page, one `App.tsx`; add a router only when the brief names more than one screen.
- Select elements in tests by ARIA role and accessible name.
