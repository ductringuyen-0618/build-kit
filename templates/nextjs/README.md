# nextjs

Next.js (App Router) + TypeScript in `frontend/`. Listens on `PORT`
(default 3000); health check is `GET /api/health`. On App Platform it is a
`services:` component (a Node web service), not a static site.

## Scaffold (from the repo root)

```
npx create-next-app@latest frontend --ts --eslint --app --src-dir --no-tailwind --import-alias "@/*"
cd frontend && cp <kit>/templates/nextjs/{Dockerfile,.env.example} .
```

Add `"typecheck": "tsc --noEmit"` to `package.json` scripts, and set
`output: 'standalone'` in `next.config.ts` when using the Dockerfile.

Health route, `src/app/api/health/route.ts` (add a database ping if Next owns the data):

```ts
export function GET() {
  return Response.json({ status: "ok", checks: {} });
}
```

First check: `npm run lint && npm run typecheck && npm run build` passes and
`curl localhost:3000/api/health` returns the JSON above after `npm start`.

## Commands (run from `frontend/`)

| Task | Command |
| --- | --- |
| run | `npm run dev` (http://localhost:3000) |
| test | `npm run build` (add vitest or Playwright if time allows) |
| lint | `npm run lint && npm run typecheck` |
| build | `npm run build` then `npm start` (`next start` honours `PORT`) |
| image | `docker build -t web .` |

## Files in this folder

- `Dockerfile`: builds with `output: 'standalone'`, slim non-root runtime with HEALTHCHECK. Copy to `frontend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job (lint, typecheck, build). Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: every variable the app reads. Copy to `frontend/.env.example`; `.env.local` is git-ignored.
- `app-component.yaml`: App Platform `services:` entry using the Node buildpack. Paste into `.do/app.yaml`.

## Conventions

- Browser-visible config only through `NEXT_PUBLIC_*`, baked in at build time; server
  secrets stay in plain env and are read in route handlers or server components.
- With a separate backend, call it same-origin via the `/api` ingress rule in production
  and via `NEXT_PUBLIC_API_BASE_URL` locally. If Next.js owns the data, keep the API
  inside route handlers and skip the second service.
- `output: 'standalone'` keeps the image small; the buildpack path does not need it.
