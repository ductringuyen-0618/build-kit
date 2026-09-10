# syntax=docker/dockerfile:1.6
# Node/TypeScript service: deps and build in one stage, slim runtime, non-root.
# Copy to backend/Dockerfile. The App Platform Node buildpack also works;
# use this when the runtime needs to be exact or the repo is a monorepo.

FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
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
CMD ["node", "dist/server.js"]
