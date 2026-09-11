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

---

## Production API Contract Specification & Templates

### Standardized Response Envelope Architecture
All HTTP APIs designed under this skill must adhere to unified response envelopes:

#### 1. Single Entity / Mutation Response Envelope
```json
{
  "success": true,
  "data": {
    "id": "usr_9b1deb4d3b7d",
    "email": "sarah.connor@example.com",
    "role": "admin",
    "created_at": "2026-09-11T14:30:00Z"
  },
  "meta": {
    "request_id": "req_8f1a2b3c4d5e",
    "timestamp_utc": "2026-09-11T14:30:00.102Z",
    "execution_time_ms": 14.2
  },
  "error": null
}
```

#### 2. Paginated Collection Response Envelope
```json
{
  "success": true,
  "data": [
    { "id": "ord_101", "total_cents": 4500, "status": "COMPLETED" },
    { "id": "ord_102", "total_cents": 1280, "status": "PENDING" }
  ],
  "meta": {
    "request_id": "req_1a2b3c4d5e6f",
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_records": 142,
      "total_pages": 8,
      "has_next": true,
      "has_previous": false
    }
  },
  "error": null
}
```

#### 3. Standardized Error Response Envelope (RFC 7807 Compliant)
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "User with email sarah.connor@example.com already exists.",
    "status_code": 409,
    "field_violations": [
      {
        "field": "email",
        "issue": "UNIQUE_CONSTRAINT_VIOLATION",
        "rejected_value": "sarah.connor@example.com"
      }
    ],
    "help_url": "https://docs.api.example.com/errors/RESOURCE_CONFLICT"
  },
  "meta": {
    "request_id": "req_bad9911ff0",
    "timestamp_utc": "2026-09-11T14:30:05.412Z"
  }
}
```

### Idempotency & Rate Limit Headers Contract
For all financial, order, or state-mutating endpoints (`POST`, `PUT`, `PATCH`), enforce idempotency:
```http
POST /api/v1/orders HTTP/1.1
Host: api.example.com
Authorization: Bearer <jwt_token>
Idempotency-Key: 7b568962-d419-4a92-9cb7-7ef862719602
Content-Type: application/json

Response Headers:
HTTP/1.1 201 Created
Idempotency-Replayed: false
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 994
X-RateLimit-Reset: 1726066800
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
