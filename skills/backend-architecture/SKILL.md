---
name: backend-architecture
description: >-
  Use this skill when designing, implementing, or optimizing backend services,
  APIs, databases, and microservice architectures. Enforces clean API contract design,
  efficient database indexing, transaction safety, caching strategies, and resilient error handling.
---

# Backend Architecture & Systems Engineering

A comprehensive backend engineering skill guiding the design, implementation, and optimization of robust, scalable, and secure server-side applications, APIs, and data layers.

## When to Use This Skill
- When building or refactoring REST, GraphQL, or gRPC API services.
- When designing relational (PostgreSQL, MySQL, SQLite) or document (MongoDB) database schemas.
- When implementing authentication, role-based authorization (RBAC), and session management.
- When structuring background task workers, event queues (Redis, BullMQ, Celery), or pub/sub systems.
- Trigger phrases: `"build backend"`, `"design API"`, `"database schema"`, `"backend architecture"`, `"optimize query"`.

## Core Backend Tenets

```
┌────────────────────────────────────────────────────────┐
│               Backend Architecture Pillars             │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. API       │ 2. Data      │ 3. Caching  │ 4. Resilient│
│    Contracts │    Integrity │    & Queues │    Errors  │
└──────────────┴──────────────┴─────────────┴────────────┘
```

### 1. Robust API Contract Design
- **Consistent Envelopes**: Standardize API response structures across endpoints:
  ```json
  {
    "success": true,
    "data": { ... },
    "error": null,
    "meta": { "page": 1, "total": 45 }
  }
  ```
- **Idempotency**: Ensure state-mutating operations (`POST /payments`, `PUT /orders`) support idempotency keys to prevent duplicate actions on network retries.
- **Strict Input Validation**: Validate payloads at the boundary using schemas (e.g., Zod, Pydantic, Joi) before passing parameters to business logic.

### 2. Database Design & Transaction Safety
- **Normalized Schema**: Design schemas in 3rd Normal Form (3NF) to eliminate data redundancy; denormalize deliberately only when query benchmarks demonstrate the need.
- **Index Strategies**: Add composite indexes for frequently filtered, joined, or sorted columns (`CREATE INDEX idx_orders_user_status ON orders(user_id, status)`).
- **ACID Transactions**: Wrap multi-step mutations that must succeed or fail as a unit in database transactions (`BEGIN ... COMMIT`).
- **Connection Pooling**: Always configure connection pool limits to prevent connection exhaustion under high concurrency.

### 3. Caching & Asynchronous Tasks
- **Cache Invalidation**: Cache read-heavy, low-frequency mutation data with explicit TTLs (Time-To-Live). Implement cache-aside or write-through strategies.
- **Offload Heavy Work**: Offload slow tasks (PDF generation, email sending, video processing, bulk syncs) to asynchronous background job queues. Return a `202 Accepted` response with a job ID.

### 4. Error Handling & Observability Middleware
- Centralize error handling in top-level middleware.
- Never leak raw database stack traces or SQL syntax to public API consumers.
- Log errors with structured contextual metadata (request ID, user ID, endpoint, latency).

---

## Step-by-Step Implementation Workflow

### Step 1: Data Model & Schema Definition
Define database models with explicit constraints (foreign keys, nullability, unique indexes, and timestamps):
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
CREATE INDEX idx_users_email ON users(email);
```

### Step 2: Route & Controller Layer (with Validation)
```typescript
// Zod Schema Validation
const CreateUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

app.post('/api/v1/users', async (req, res, next) => {
  try {
    const validatedData = CreateUserSchema.parse(req.body);
    const user = await userService.createUser(validatedData);
    return res.status(201).json({ success: true, data: user });
  } catch (error) {
    next(error); // Forward to global error middleware
  }
});
```

## Anti-Patterns & Traps to Avoid

1. **The N+1 Query Disaster**: Iterating over an array of entities and issuing an individual `SELECT` query per row inside the loop. This converts a single operation into hundreds of database round-trips. Always use SQL joins, batch queries (`WHERE id IN (...)`), or DataLoader patterns.
2. **Bleeding Business Logic into Controllers**: Writing database queries, external API calls, and financial calculations directly inside route controller functions. Always enforce layered architecture: Controllers handle HTTP serialization, Services orchestrate business logic, and Repositories handle data access.
3. **Non-Transactional Multi-Write Operations**: Executing dependent mutations (e.g., deducting an inventory count and creating an invoice) across multiple independent queries without an explicit ACID transaction block. If step 2 fails, the database is permanently corrupted.
4. **Unbounded Connection Pools & Missing Query Timeouts**: Allowing queries to run indefinitely without a statement timeout. A single unindexed query under high traffic can lock table rows, saturate database connections, and bring down all microservices.

---

## Quality Checklist

- [ ] Route controllers strictly handle HTTP request validation and status response formatting.
- [ ] Business logic is decoupled into testable Service layers with typed dependency injection.
- [ ] Multi-table mutations are wrapped in atomic database transactions with rollback guarantees.
- [ ] Database queries are audited with `EXPLAIN ANALYZE` to eliminate sequential table scans.
- [ ] Sensitive secrets and credentials are read exclusively from environment variables.
- [ ] Structured logging emits standardized correlation IDs and excludes raw credentials or PII.
