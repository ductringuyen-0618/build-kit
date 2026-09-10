# syntax=docker/dockerfile:1.6
# Node/TypeScript service. Copy to backend/Dockerfile and build from that folder.
# Stage 1 installs deps, compiles to dist/ and prunes dev deps; stage 2 is a
# slim non-root runtime.

FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
# CHANGE: pnpm-lock.yaml + `corepack enable && pnpm i --frozen-lockfile` for pnpm
RUN npm ci
COPY tsconfig.json ./
COPY src src
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=8080
RUN apk add --no-cache curl
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/dist dist
USER node
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1
EXPOSE 8080
# CHANGE: run migrations first if needed, e.g. sh -c "npx prisma migrate deploy && node dist/server.js"
CMD ["node", "dist/server.js"]
