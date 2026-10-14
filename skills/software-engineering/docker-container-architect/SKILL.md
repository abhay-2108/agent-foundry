---
name: docker-container-architect
description: >-
  Use this skill when authoring, optimizing, or debugging Dockerfiles and docker-compose setups.
  Enforces multi-stage build patterns, minimal base images (Alpine/Distroless), non-root execution,
  and layer caching optimizations.
---

# Docker Container Architect & Image Optimizer

## Overview

Authors, optimizes, and secures Dockerfiles and docker-compose architectures. Enforces multi-stage builds, non-root user execution, minimal base images (Alpine/Distroless), layer caching order, and vulnerability hardening.

## When to Use

- When containerizing a Python, Node.js, Go, or Rust application from scratch.
- When optimizing large Docker images (reducing gigabytes down to tens of megabytes).
- When resolving slow image build times by optimizing Docker layer caching.
- When configuring local multi-service environments (`docker-compose.yml` with databases, caches, and queues).
- Trigger phrases: `"dockerize this app"`, `"optimize Dockerfile"`, `"multi-stage build"`, `"docker-compose setup"`, `"reduce image size"`.

---
- **When NOT to use**: Managing Kubernetes cluster networking or Helm charts (use `sre-devops-guardian`).

## Core Process & Container Hardening Blueprint

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Running as `root` in the container doesn't matter because it's containerized."* | Root container escapes grant root access to the host kernel; running as a dedicated non-root user (`USER appuser`) is mandatory. |
| *"Using the `latest` tag is convenient for auto-updating."* | `latest` tags break build reproducibility, invalidate layer caches unpredictably, and introduce unvetted breaking changes. |
| *"Putting dependencies and source code in one `COPY . .` layer is fine."* | Copying source code before installing dependencies breaks layer caching, forcing full package reinstalls on every line edit. |
| *"Image size doesn't matter since bandwidth is fast."* | A 2GB image takes 5x longer to deploy, consumes cluster disk quotas, and contains an enormous attack surface of unneeded binaries. |

## Red Flags

- Containers executing as UID 0 (root) without an explicit `USER` directive.
- Hardcoded environment secrets or passwords baked into Dockerfile `ENV` instructions.
- Missing `.dockerignore` file, leading to `.git`, `node_modules`, or local `.env` files copied into the image.
- Single-stage builds containing compilers, build tools, and package managers in the production runtime image.

## Verification

After completing the workflow, confirm:
- [ ] Dockerfile utilizes multi-stage builds, copying only compiled artifacts to the minimal runtime stage.
- [ ] Container runs as a dedicated non-root user with minimal filesystem permissions.
- [ ] Layer ordering optimizes cache hit rates (package manifests copied before application source).
- [ ] Container build and healthcheck verify cleanly: `docker build -t app . && docker run --rm app healthcheck`.
