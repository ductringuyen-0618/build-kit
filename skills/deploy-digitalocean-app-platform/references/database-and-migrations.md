# Database binding and migrations on App Platform

Companion to step 5 of `SKILL.md`. Read this before the first write hits
the managed Postgres.

## What the platform gives you

A `databases:` entry with `production: false` provisions a dev Postgres
alongside the app: one size, no standby, PostgreSQL only, versions 15 to
18 (`version: "16"` pins it). `production: true` with `cluster_name`,
`db_name` and `db_user` attaches an existing managed cluster instead.

Every component can read these bindable variables, where `db` is the
database's `name`:

| Variable | Contents |
| --- | --- |
| `${db.DATABASE_URL}` | `postgresql://user:pass@host:port/dbname?sslmode=require` |
| `${db.DATABASE_PRIVATE_URL}` | same, over the private network |
| `${db.JDBC_DATABASE_URL}` | `jdbc:postgresql://host:port/dbname?sslmode=require` (no credentials) |
| `${db.HOSTNAME}`, `${db.PORT}`, `${db.USERNAME}`, `${db.PASSWORD}`, `${db.DATABASE}` | the parts |
| `${db.CA_CERT}` | the CA certificate, for clients that verify it |

## Per-stack wiring

| Stack | Env var(s) to set | Driver to install | Migration command |
| --- | --- | --- | --- |
| Python / SQLAlchemy | `DATABASE_URL=${db.DATABASE_URL}` | `psycopg[binary]` (psycopg 3) or `psycopg2-binary` | `alembic upgrade head` |
| Python / Django | `DATABASE_URL=${db.DATABASE_URL}` | `psycopg[binary]` plus `dj-database-url` | `python manage.py migrate` |
| Node / Prisma | `DATABASE_URL=${db.DATABASE_URL}` | `@prisma/client` | `npx prisma migrate deploy` |
| Node / Drizzle | `DATABASE_URL=${db.DATABASE_URL}` | `pg` | `npx drizzle-kit migrate` |
| Node / plain `pg` | `DATABASE_URL=${db.DATABASE_URL}` | `pg` | your own SQL runner |
| Go / pgx or database/sql | `DATABASE_URL=${db.DATABASE_URL}` | `github.com/jackc/pgx/v5` | `migrate -path migrations -database "$DATABASE_URL" up` (golang-migrate) or `goose up` |
| Spring Boot | `SPRING_DATASOURCE_URL=${db.JDBC_DATABASE_URL}`, `SPRING_DATASOURCE_USERNAME=${db.USERNAME}`, `SPRING_DATASOURCE_PASSWORD=${db.PASSWORD}` | `org.postgresql:postgresql` | Flyway or Liquibase run on boot; no job needed |

## Where to run migrations

Two options; pick one, not both.

1. At container start. The Dockerfile `CMD` runs the migration then the
   server (the kit's `templates/python-fastapi/Dockerfile` does
   `alembic upgrade head` when an `alembic/` folder exists; Spring Boot
   runs Flyway on boot). Simplest; the deploy fails visibly in the run
   logs if the migration fails.
2. A `PRE_DEPLOY` job in the spec (the `migrate` job in
   `templates/do-app.yaml`). Same source and Dockerfile as the service,
   with `run_command` set to the migration command. Runs once per deploy
   before the new service instance starts. Logs: `doctl apps logs <app-id> migrate --type run`.

For a prototype, `create_all` (SQLAlchemy) or `synchronize` (TypeORM) at
startup is acceptable. Say so in the README and name the migration tool
as the next step.

## SQLite to Postgres pitfalls, in the order they bite

- The URL scheme. SQLAlchemy needs `postgresql+psycopg://` for psycopg 3
  or `postgresql://` for psycopg2. The platform hands out `postgresql://`
  with `?sslmode=require`; keep the query string. Normalise the scheme in
  one settings module, never in a route.
- Missing driver. Shows up as a traceback in the run logs, not a build
  failure. Add the driver to the dependency file and redeploy.
- Types. SQLite accepts anything; Postgres does not. `Boolean` columns fed
  `0`/`1` strings, `DateTime` columns fed naive strings, and JSON fed as
  a Python dict or JS object into a text column fail on the first insert.
  If Docker is available, run the tests once against a local Postgres
  before deploying:

  ```
  docker run --rm -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:16
  DATABASE_URL=postgresql://postgres:x@localhost:5432/postgres <test command>
  ```

- Case-sensitive identifiers and reserved words (`user`, `order`) that
  SQLite tolerated.
- Connection limits. The dev database allows few connections; keep the
  pool small (`pool_size=5` or fewer) and one worker process.
- SSL. Most drivers honour `sslmode=require` in the URL. If a client
  insists on verifying the certificate, pass `${db.CA_CERT}` through an
  env var and write it to a file at startup.
