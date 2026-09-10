# syntax=docker/dockerfile:1.6
# Go service: static binary built in a Go stage, copied into a tiny runtime.
# Copy to backend/Dockerfile.

FROM golang:1.24-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/server ./cmd/server

FROM alpine:3.20
RUN apk add --no-cache ca-certificates curl && adduser -D -u 1000 app
COPY --from=builder /out/server /server
COPY migrations /migrations
USER app
ENV PORT=8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/healthz" || exit 1
EXPOSE 8080
CMD ["/server"]
