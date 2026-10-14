# Canonical Performance & Latency Optimization Standards

This reference defines system performance benchmarks, database query optimization criteria, memory management standards, and frontend Core Web Vitals targets.

---

## 1. Latency Budgets & SLA Thresholds

Every engineering component must operate within its designated latency budget:

| Component / Layer | p50 Budget | p95 Budget | p99 Budget | Target Failure Mode |
|:---|:---|:---|:---|:---|
| **In-Memory Cache (Redis)** | $<1\text{ ms}$ | $<3\text{ ms}$ | $<5\text{ ms}$ | Return stale cache, background refresh |
| **Primary Database (OLTP Read)** | $<5\text{ ms}$ | $<15\text{ ms}$ | $<30\text{ ms}$ | Fallback to cache / degraded mode |
| **Primary Database (OLTP Write)** | $<10\text{ ms}$ | $<30\text{ ms}$ | $<50\text{ ms}$ | Async queue via Transactional Outbox |
| **Internal Microservice RPC** | $<15\text{ ms}$ | $<40\text{ ms}$ | $<80\text{ ms}$ | Circuit breaker trip after 3 failures |
| **Public API Response (p95)** | $<100\text{ ms}$ | $<250\text{ ms}$ | $<500\text{ ms}$ | HTTP 504 with structured error envelope |
| **LLM Time-to-First-Token (TTFT)** | $<800\text{ ms}$ | $<1500\text{ ms}$ | $<2500\text{ ms}$ | Token stream progress indicator |

---

## 2. Database Optimization & Anti-Patterns

### Anti-Pattern 1: The N+1 Query Problem
- **Smell**: Querying a parent table (`SELECT * FROM orders`) followed by a looped query per record (`SELECT * FROM order_items WHERE order_id = ?`).
- **Remedy**: Use joined queries (`JOIN order_items`) or eager bulk loading (`WHERE order_id IN (?, ?, ...)`).

### Anti-Pattern 2: Missing Index on Foreign Keys and Filter Predicates
- **Smell**: `EXPLAIN ANALYZE` shows a Sequential Scan (`Seq Scan`) across tables with $>10,000$ rows.
- **Remedy**: Create B-Tree or Hash indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses.

### Anti-Pattern 3: Unbounded SELECT Queries
- **Smell**: `SELECT * FROM audit_logs` without pagination.
- **Remedy**: Enforce strict cursor-based or keyset pagination with hard limits (e.g., `LIMIT 50`).

---

## 3. Resource Cleanup & Memory Leak Guards

- [ ] **Connection Pooling**: Database connections must be pooled (`max_connections`, `idle_timeout`). Connections must be acquired inside context managers (`async with pool.acquire()`) to guarantee release.
- [ ] **Stream Large Files / Payloads**: File uploads and downloads must stream in fixed-size chunks (e.g., 64KB) rather than buffering the entire file in RAM.
- [ ] **Explicit Event Listener Unbinding**: Frontend components and Node.js event emitters must remove listeners on teardown / unmount (`removeEventListener`, `emitter.off()`).
- [ ] **Bounded In-Memory Structures**: In-memory caches must declare a max item size with an LRU (Least Recently Used) eviction policy. Unbounded Maps or Dictionaries are forbidden.

---

## 4. Frontend Core Web Vitals Standards

Web applications must meet Google's Core Web Vitals thresholds on standard mobile and desktop devices:

| Metric | Full Name | Good Target | Poor Threshold | Measurement Strategy |
|:---|:---|:---|:---|:---|
| **LCP** | Largest Contentful Paint | $\le 2.5\text{ s}$ | $> 4.0\text{ s}$ | Preload critical hero images; inline critical CSS |
| **INP** | Interaction to Next Paint | $\le 200\text{ ms}$ | $> 500\text{ ms}$ | Break long JavaScript tasks ($>50\text{ ms}$) via `scheduler.yield()` |
| **CLS** | Cumulative Layout Shift | $\le 0.1$ | $> 0.25$ | Set explicit `width` and `height` attributes on all images and embeds |
| **FCP** | First Contentful Paint | $\le 1.8\text{ s}$ | $> 3.0\text{ s}$ | Serve pre-rendered HTML; defer non-critical JS bundles |
| **TTFB** | Time to First Byte | $\le 800\text{ ms}$ | $> 1800\text{ ms}$ | Edge CDN caching for static and SSR responses |

---

## 5. Performance Verification Commands

```bash
# Check SQL query execution plan for sequential scans
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

# Audit bundle size in frontend builds
npm run build -- --report
```
