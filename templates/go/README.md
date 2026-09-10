# Backend skeleton: Go (net/http or chi)

Standard library `net/http` with Go 1.22+ method routing is enough for a
prototype; chi adds middleware and route groups for the cost of one
dependency. The Dockerfile is preferred over the buildpack because it
makes the run command unambiguous.

## Layout

```
backend/
  go.mod
  cmd/server/main.go        reads config, opens db, mounts routes, listens on PORT
  internal/config/config.go  the only reader of os.Getenv
  internal/db/db.go          pgx pool or database/sql
  internal/http/health.go    GET /healthz pings the db
  internal/http/<resource>.go
  internal/http/health_test.go  httptest against the handler
  migrations/0001_init.sql   golang-migrate or goose
  Dockerfile
```

## Rules

- `PORT` env with default `8080`; App Platform sets it.
- Health handler returns `{"status":"ok","checks":{"db":"ok"}}` and 503
  when the ping fails.
- Structured logging with `log/slog`, one request id middleware.
- `go vet ./...` and `go test ./...` are the gate; add golangci-lint only
  if it is already installed on the machine.
- Migrations run in the container CMD before the server starts, or as a
  pre-deploy job.

## Commands

```
go mod tidy
go run ./cmd/server
go vet ./... && go test ./...
go build -o bin/server ./cmd/server
```
