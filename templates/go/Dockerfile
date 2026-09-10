# syntax=docker/dockerfile:1.6
# Go service. Copy to backend/Dockerfile and build from that folder.
# Stage 1 builds a static binary; stage 2 is a tiny non-root Alpine runtime.

FROM golang:1.25-alpine AS builder
# CHANGE: 1.25 -> the `go` directive in go.mod (older images auto-download newer toolchains)
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/server ./cmd/server
# CHANGE: ./cmd/server -> the package that holds main()

FROM alpine:3.22
RUN apk add --no-cache ca-certificates curl && adduser -D -u 1000 app
COPY --from=builder /out/server /server
# CHANGE: uncomment when SQL migrations ship with the binary
# COPY migrations /migrations
USER app
ENV PORT=8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/healthz" || exit 1
EXPOSE 8080
CMD ["/server"]
