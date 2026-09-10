# go

Go backend in `backend/` on `net/http` (Go 1.22+ method routing) or chi.
Listens on `PORT` (default 8080); health check is `GET /healthz`.
The App Platform Go buildpack detects `go.mod`, but the Dockerfile keeps the
run command unambiguous, so it is the default here.

## Scaffold (from the repo root)

```
mkdir -p backend/cmd/server backend/internal && cd backend
go mod init example.com/app          # CHANGE: module path
go get github.com/go-chi/chi/v5      # optional; skip for plain net/http
cp <kit>/templates/go/{Dockerfile,.env.example} .
```

`cmd/server/main.go` reads `PORT`, registers `GET /healthz` and calls
`http.ListenAndServe(":"+port, mux)`. The handler writes
`{"status":"ok","checks":{"db":"ok"}}` and 503 when the database ping fails.
First test (`internal/http/health_test.go`): `httptest.NewRecorder()` against the
handler expects 200 and a JSON body with `status`.

## Commands (run from `backend/`)

| Task | Command |
| --- | --- |
| run | `go run ./cmd/server` |
| test | `go test ./...` |
| lint | `gofmt -l . && go vet ./...` (golangci-lint only if already installed) |
| build | `go build -o bin/server ./cmd/server` |
| image | `docker build -t api .` |

## Files in this folder

- `Dockerfile`: static binary built in a Go stage, copied into Alpine, non-root, HEALTHCHECK. Copy to `backend/Dockerfile`.
- `ci-job.yml`: GitHub Actions job (gofmt, vet, test, build). Paste under `jobs:` in `.github/workflows/ci.yml`.
- `.env.example`: every variable the app reads. Copy to `backend/.env.example`; `.env` is git-ignored.
- `app-component.yaml`: App Platform `services:` entry with the Dockerfile build. Paste into `.do/app.yaml`.

## Layout

```
backend/
  cmd/server/main.go           config, db, routes, listen
  internal/config/config.go    the only caller of os.Getenv
  internal/db/db.go            pgx pool or database/sql
  internal/http/               one file per resource plus health.go
  migrations/0001_init.sql     golang-migrate or goose; run before serving
```

## Conventions

- Structured logs with `log/slog` and one request-id middleware.
- Migrations run in the container command before the server starts, or as a pre-deploy job.
- `CGO_ENABLED=0` so the binary is static and the runtime image stays tiny.
