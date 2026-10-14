# Canonical Observability & Telemetry Standards

This reference specifies standards for distributed tracing, structured logging, latency profiling, and token metrics across LLM pipelines, microservices, and autonomous agents.

---

## 1. The 3 Pillars of Observability

```
┌────────────────────────────────────────────────────────────────────────┐
│ TRACES: Distributed context propagation (OTel spans, parent-child DAG) │
├────────────────────────────────────────────────────────────────────────┤
│ METRICS: Aggregations & counters (TTFT, tokens, error rates, p95 ms)   │
├────────────────────────────────────────────────────────────────────────┤
│ LOGS: Structured JSON events with trace_id correlation & PII redaction │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. OpenTelemetry GenAI Semantic Conventions

All LLM and agent invocations must emit OpenTelemetry-compliant spans following the GenAI semantic conventions:

```json
{
  "name": "gen_ai.chat",
  "attributes": {
    "gen_ai.system": "anthropic",
    "gen_ai.request.model": "claude-3-7-sonnet-20250219",
    "gen_ai.request.temperature": 0.2,
    "gen_ai.request.max_tokens": 4096,
    "gen_ai.response.id": "msg_01X...",
    "gen_ai.response.finish_reasons": ["end_turn"],
    "gen_ai.usage.input_tokens": 1240,
    "gen_ai.usage.output_tokens": 312,
    "gen_ai.usage.total_tokens": 1552,
    "session.id": "sess-849204",
    "user.id": "usr-1104"
  }
}
```

### Agent Tool Call Spans
When an agent invokes a tool, wrap the call in a child span:
- Span Name: `tool.<tool_name>` (e.g., `tool.execute_python`, `tool.read_file_safe`)
- Attributes:
  - `tool.name`: Exact tool identifier
  - `tool.parameters`: Serialized JSON parameters (with sensitive credentials redacted)
  - `tool.status`: `"success"` or `"error"`
  - `tool.execution_duration_ms`: Execution latency in milliseconds

---

## 3. Structured Logging Standard

All logs must be emitted as single-line JSON objects to standard out. Plain unstructured string logs are forbidden in production.

### Required Fields:
```json
{
  "timestamp": "2026-10-14T17:45:00.123Z",
  "level": "INFO",
  "message": "User session authenticated successfully",
  "service": "auth-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "environment": "production",
  "context": {
    "user_id": "usr-8492",
    "auth_method": "oauth2_pkce"
  }
}
```

### Logging Rules:
- **Correlate with Traces**: Always attach `trace_id` and `span_id` so logs can be filtered by a specific distributed request.
- **Redact Sensitive Information**: Automatically redact passwords, tokens, API keys, Social Security numbers, and credit card numbers before logging.
- **LogLevel Hygiene**:
  - `DEBUG`: High-volume diagnostic information (disabled in production).
  - `INFO`: Business milestones (session created, order submitted).
  - `WARN`: Recoverable degradation (cache miss fallback, transient retry).
  - `ERROR`: Unhandled exception or failed SLA (action required).

---

## 4. Latency & Token Burn Metrics Checklist

- [ ] **Time-to-First-Token (TTFT)**: Track duration from prompt dispatch to the first streaming chunk. Flag if p95 exceeds 1.5s.
- [ ] **Token Burn Rate**: Track cumulative prompt and completion tokens per session to prevent runaway context window consumption.
- [ ] **Tool Call Directness**: Compute Path Directness (minimum required tool calls / actual executed tool calls). Flag any trajectory with a ratio $< 0.7$ for review.
- [ ] **Error Rate Alerting**: Alert on $>1\%$ 5xx HTTP response rate or $>5\%$ tool failure rate over a 5-minute rolling window.
