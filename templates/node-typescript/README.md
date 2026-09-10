# node-typescript

Node 22 + TypeScript backend in `backend/`, Fastify by default (Express is
the same shape). Listens on `PORT` (default 8080); health check is `GET /health`.

## Scaffold (from the repo root)

```
mkdir -p backend/src backend/test && cd backend
npm init -y && npm i fastify && npm i -D typescript tsx vitest @types/node eslint prettier
npx tsc --init --rootDir src --outDir dist --module nodenext --target es2022 --strict
cp <kit>/templates/node-typescript/{Dockerfile,.env.example} .
```

`package.json` scripts: `dev` = `tsx watch src/server.ts`, `build` = `tsc`,
`start` = `node dist/server.js`, `test` = `vitest run`, `lint` = `eslint .`,
`typecheck` = `tsc --noEmit`.

`src/app.ts` exports `build()` returning the Fastify app with `GET /health`;
`src/server.ts` calls `build().listen({ port: Number(process.env.PORT ?? 8080), host: "0.0.0.0" })`.
First test (`test/health.test.ts`): `build().inject({ url: "/health" })` returns 200
with a `status` field.

## Commands (run from `backend/`)

| Task | Command |
| --- | --- |
| run | `npm run dev` |
| test | `npm test` |
| lint | `npm run lint && npm run typecheck` |
| build | `npm run build` then `npm start` |
| image | `docker build -t api .` |

## Files in this folder

- `Dockerfile`: build stage compiles TS and prunes dev deps; slim non-root runtime with HEALTHCHECK. Copy to `backend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job (lint, typecheck, test, build). Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: every variable the app reads. Copy to `backend/.env.example`; `.env` is git-ignored.
- `app-component.yaml`: App Platform `services:` entry using the Node buildpack. Paste into `.do/app.yaml`.

## Conventions

- `src/config.ts` parses `process.env` once (zod or hand-written) and exports a typed object;
  a missing variable fails at startup with a clear message.
- `/health` reports the database check and returns 503 when it fails.
- Migrations (Drizzle `migrate()`, Prisma `migrate deploy`, or plain SQL) run before
  `node dist/server.js` in the container command.
- Fastify does not redirect on trailing slashes; pick one path form and use it everywhere.
- The App Platform Node buildpack works without the Dockerfile; use the Dockerfile when the
  runtime must be exact or the repo is a monorepo.
