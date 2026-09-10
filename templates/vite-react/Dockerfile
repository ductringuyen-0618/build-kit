# syntax=docker/dockerfile:1.6
# Vite/React static site served by unprivileged nginx on port 8080.
# Not needed on App Platform (use the static_sites component); use it for
# Docker-based hosts. Copy to frontend/Dockerfile and build from that folder:
#   docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t web .

FROM node:22-alpine AS builder
WORKDIR /app
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runs as the nginx user (uid 101) and listens on 8080.
FROM nginxinc/nginx-unprivileged:1.27-alpine
# CHANGE: /app/dist -> vite.config.ts build.outDir if changed
COPY --from=builder /app/dist /usr/share/nginx/html
# SPA fallback: every unknown path serves index.html.
COPY <<'CONF' /etc/nginx/conf.d/default.conf
server {
    listen 8080;
    root /usr/share/nginx/html;
    location / { try_files $uri /index.html; }
}
CONF
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ > /dev/null || exit 1
EXPOSE 8080
