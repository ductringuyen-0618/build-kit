---
name: codebase-map
description: Use when you land in an unfamiliar repository and need a working mental map in about ten minutes before changing anything; writes the map to docs/CODEBASE.md.
---

# codebase-map

Before touching an unfamiliar repo, spend ten minutes building a map of it
and write that map down. The written map is for the next agent or session
as much as for you: a fresh context can read `docs/CODEBASE.md` in one
minute instead of re-deriving it.

No tools beyond file listing, search and reading are needed. Do not run
the app or install anything in this pass.

## The ten-minute pass

Work through the questions in order. Spend at most the time shown on each.
Record answers as you go. Do not read whole files: read the top of files
and grep for names.

1. **What is it? (1 min)** Read the README and any top-level `AGENTS.md`,
   `CLAUDE.md` or `CONTRIBUTING.md`. If they contradict the code, trust
   the code and note the contradiction.
2. **Stack and layout (1 min)** List the top two directory levels. Read the
   manifest files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
   `Gemfile`, `pom.xml`, or similar). Note the language, framework, package
   manager, and whether it is a monorepo.
3. **Entry points (1 min)** Find where the process starts: `main`, `app`,
   `server`, `index`, `cmd/`. Note the exact file and the command that
   runs it, from the manifest scripts or the Dockerfile.
4. **Routes and surface (2 min)** Grep for route decorators or registrations
   (`@app.get`, `router.`, `app.use`, `Route`, `urlpatterns`, `HandleFunc`).
   List the public endpoints or pages with a one-line purpose each.
5. **Data models (2 min)** Find the schema: ORM models, migrations,
   `schema.prisma`, SQL files, or type definitions used by storage. List
   the main entities and how they relate. Note which database is used and
   where the connection string comes from.
6. **Tests (1 min)** Find the test directory and runner. Note the command
   to run one test and all tests, and roughly how many there are.
7. **CI and deploy (1 min)** Read `.github/workflows/`, `Dockerfile`,
   `Procfile`, `fly.toml`, `app.yaml`, `vercel.json` or equivalents. Note
   what CI checks and where the app is deployed.
8. **Config and secrets (1 min)** Find `.env.example` or the settings
   module. List the environment variables the app needs and which ones
   have no default.

If a question has no answer, write "none found" rather than guessing.

## Write docs/CODEBASE.md

Use this shape. Keep it under 120 lines. It is a map, not documentation.

```markdown
# Codebase map

Last mapped: <YYYY-MM-DD> by <agent or person>

## What it is
<Two sentences.>

## Stack
- Language / framework:
- Package manager and install command:
- Run locally:
- Monorepo: yes/no (list packages if yes)

## Entry points
- `<path>`: <what starts here>

## Routes / surface
| Path | Method | Purpose | Handler file |
| --- | --- | --- | --- |

## Data
- Database: <engine>, configured by <env var or file>
- Entities: <A has many B; B belongs to C>
- Models live in `<path>`; migrations in `<path>`

## Tests
- Runner: `<command>`; single test: `<command>`
- Location and rough count:

## CI / deploy
- CI: <what runs on push or PR>
- Deploy target: <where>, configured by `<file>`

## Config
| Variable | Required | Default | Used by |
| --- | --- | --- | --- |

## Gotchas
- <Anything that surprised you: stale README, two config paths, legacy
  directories to ignore, non-default formatter settings.>
```

## After writing

State the three files you would open first for the task at hand and why.
If the repo already has a `docs/CODEBASE.md`, read it first, then verify
the entry points and routes still match before trusting the rest. Update
the date and any drift you found.

## Rules

- Read-only apart from creating or updating `docs/CODEBASE.md`.
- Prefer facts you saw in files over what the README claims.
- Stop at ten minutes. A partial map with "none found" entries is more
  useful than a complete one that took an hour.
