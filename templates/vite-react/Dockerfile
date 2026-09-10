# syntax=docker/dockerfile:1.6
# Vite/React static site served by nginx. Not needed on App Platform (use the
# static_sites component); use this for the Docker or Droplet fallback.
# Copy to frontend/Dockerfile. Pass the API base URL at build time:
#   docker build --build-arg VITE_API_BASE_URL=https://api.example.com .

FROM node:22-alpine AS builder
WORKDIR /app
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# SPA fallback: every unknown path serves index.html.
RUN printf 'server { listen 80; root /usr/share/nginx/html; location / { try_files $uri /index.html; } }\n' \
    > /etc/nginx/conf.d/default.conf
EXPOSE 80
