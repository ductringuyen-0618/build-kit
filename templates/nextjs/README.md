# Frontend skeleton: Next.js (App Router)

Use when the prompt benefits from server rendering or route handlers, or
when the backend is small enough to live inside Next.js route handlers.
On App Platform it is a `services` component (a web service), not a
static site. Scaffold with the command in `playbook/stack-picker.md`.

## Layout

```
frontend/
  src/app/
    layout.tsx, page.tsx
    api/health/route.ts       GET returns {status:"ok"}; add a db ping if Next owns the data
    <feature>/page.tsx
  src/lib/api.ts              API base URL from NEXT_PUBLIC_API_BASE_URL, same-origin fallback
  next.config.ts              output: 'standalone' if using the Dockerfile
  package.json                scripts: dev, build, start (next start -p $PORT), lint, typecheck (tsc --noEmit)
  Dockerfile
```

## Rules

- `next start -p ${PORT:-3000}` in the `start` script so the buildpack's
  `PORT` is honoured.
- Public config only through `NEXT_PUBLIC_*`; server secrets stay in
  plain env and are read in route handlers or server components.
- If the API is a separate service, call it via the same-origin `/api`
  ingress rule in production and `NEXT_PUBLIC_API_BASE_URL` locally.
- `output: 'standalone'` makes the Docker image small; the buildpack path
  does not need it.

## Commands

```
npm ci
npm run dev
npm run lint && npx tsc --noEmit && npm run build
npm start
```
