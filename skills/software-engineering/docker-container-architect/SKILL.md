---
name: docker-container-architect
description: >-
  Use this skill when authoring, optimizing, or debugging Dockerfiles and docker-compose setups.
  Enforces multi-stage build patterns, minimal base images (Alpine/Distroless), non-root execution,
  and layer caching optimizations.
---

# Docker Container Architect & Image Optimizer

A container engineering skill for creating secure, minimal, and fast-building Docker images and multi-container `docker-compose` orchestration environments.

## When to Use This Skill
- When containerizing a Python, Node.js, Go, or Rust application from scratch.
- When optimizing large Docker images (reducing gigabytes down to tens of megabytes).
- When resolving slow image build times by optimizing Docker layer caching.
- When configuring local multi-service environments (`docker-compose.yml` with databases, caches, and queues).
- Trigger phrases: `"dockerize this app"`, `"optimize Dockerfile"`, `"multi-stage build"`, `"docker-compose setup"`, `"reduce image size"`.

---

## The 4 Golden Rules of Production Dockerfiles

1. **Multi-Stage Builds**: Build dependencies and compile binaries in an SDK stage; copy only the compiled artifacts into a lightweight runtime image.
2. **Order by Change Frequency**: Place static system dependencies and lockfiles (`package.json`, `requirements.txt`) *before* source code (`COPY . .`) to maximize layer cache reuse.
3. **Run as Non-Root User**: Never run production containers as `root`. Create and switch to an unprivileged system user.
4. **Specific Base Image Tags**: Pin exact major/minor versions (e.g. `node:20.11-alpine3.19`), never mutable `latest`.

---

## Step-by-Step Multi-Stage Dockerfile (Node.js / Next.js)

```dockerfile
# Stage 1: Build Dependencies
FROM node:20-alpine AS builder
WORKDIR /app

# Install build tools needed for native bindings
RUN apk add --no-cache libc6-compat

# Copy lockfiles first to leverage Docker layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build production bundle
COPY . .
RUN npm run build

# Stage 2: Minimal Production Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Security: Run as non-privileged user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

# Copy only compiled build output and minimal production node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

USER appuser
EXPOSE 3000
CMD ["node_modules/.bin/next", "start"]
```

---

## Production Multi-Service `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://app_user:secret_pass@db:5432/app_db
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: secret_pass
      POSTGRES_DB: app_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

## Anti-Patterns & Traps to Avoid

1. **Running Production Containers as Root**: Leaving the default root user active inside the container. If an attacker discovers an application-level vulnerability (e.g., RCE or command injection), they inherit root privileges over container namespaces. Always create and switch to an unprivileged system user (`USER appuser`).
2. **Invalidating the Build Layer Cache Early**: Placing `COPY . .` *before* package manager installation steps (`RUN npm install` or `pip install`). Any trivial edit to a README or comment invalidates the dependency cache, forcing a multi-minute dependency reinstall on every build. Copy dependency manifests first, install, then copy source code.
3. **Bloating Production Images with Build Tools**: Shipping `gcc`, `g++`, `cmake`, and header packages in the final deployment image. Use multi-stage builds to compile binaries in an SDK builder stage and copy only the compiled artifacts into a lightweight Distroless or Alpine runtime.
4. **Missing `.dockerignore` (Secret Leakage)**: Neglecting to include a `.dockerignore` file. This routinely bundles local `.git` directories, development `.env` credentials, and local build artifacts directly into publicly accessible container image layers.

---

## Quality Checklist

- [ ] Multi-stage build separates compiler toolchains from minimal runtime environments.
- [ ] Application processes execute under a dedicated non-root user (`USER appuser`).
- [ ] `.dockerignore` is present, excluding `.git`, `.env`, test files, and local build caches.
- [ ] Dependency manifests are copied and installed *before* application source code to maximize caching.
- [ ] Base images pin specific minor/patch tags (e.g. `node:20.11-alpine`) rather than floating `latest`.
- [ ] Container includes automated `HEALTHCHECK` commands to enable orchestrator restarts.
