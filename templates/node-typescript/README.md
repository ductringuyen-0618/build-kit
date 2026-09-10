# Backend skeleton: Node + TypeScript (Fastify or Express)

Fastify is the default here for its schema validation and built-in
logging; Express is the same shape with `express.json()` and a manual
error handler. The pnpm monorepo pattern from agent-os applies when the
frontend lives in the same repo as a workspace.

## Layout

```
backend/
  src/
    server.ts            listen on process.env.PORT
    app.ts               build() returns the app; tests import this
    config.ts            zod-parsed env; the only reader of process.env
    db.ts                pg Pool or Drizzle/Prisma client from config
    routes/health.ts     GET /health checks the db
    routes/<resource>.ts
  test/
    health.test.ts       vitest + app.inject() (Fastify) or supertest
  package.json           scripts: dev (tsx watch), build (tsc), start (node dist/server.js), test (vitest run), lint, typecheck
  tsconfig.json
  Dockerfile
```

## Rules

- `config.ts` parses the environment once with zod and exports a typed
  object. Missing variables fail at startup with a clear message.
- The health route reports the database check; a 503 with a status field
  beats a 200 that lies.
- Migrations: Drizzle `migrate()` or Prisma `migrate deploy` in the
  container CMD before `node dist/server.js`.
- Mount routes at exact paths and register them once; Fastify does not
  redirect on trailing slashes by default, so pick one form and use it in
  the frontend.

## Commands

```
npm ci
npm run dev
npm run lint && npm run typecheck && npm test && npm run build
node dist/server.js
```
