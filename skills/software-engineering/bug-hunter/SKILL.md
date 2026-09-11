---
name: bug-hunter
description: >-
  Use this skill to diagnose, isolate, reproduce, and resolve tricky software bugs,
  runtime exceptions, regressions, race conditions, and logic errors. Employs a scientific
  root-cause analysis methodology with minimal reproduction test cases.
---

# Bug Hunter & Root Cause Debugger

A structured, hypothesis-driven debugging skill designed to track down, isolate, and eradicate elusive bugs, regressions, and silent failures without guessing or introducing secondary breaks.

## When to Use This Skill
- When receiving an error message, stack trace, or failing test.
- When an application behaves incorrectly, produces wrong calculations, or hangs.
- When investigating flaky, intermittent, or race condition issues.
- When tasked with fixing an issue where the root cause is unknown.
- Trigger phrases: `"debug this"`, `"find the bug"`, `"why is this failing?"`, `"fix this crash"`, `"investigate error"`.

## Core Debugging Principles
1. **Never Guess or Patch blindly**: Do not change code hoping the bug disappears. Understand *why* it failed before changing anything.
2. **Reproduction First**: Always create a minimal reproduction case (unit test, curl command, or isolated script) that reliably triggers the bug.
3. **Isolate State from Symptoms**: The error location in the stack trace is often just the *symptom*; the *root cause* is typically invalid state created earlier in execution.
4. **Zero-Regression Guarantee**: The fix must resolve the reproduction test while keeping 100% of preexisting tests passing.

---

## Step-by-Step Hunting Workflow

```
┌────────────────────────────────────────────────────────┐
│                   Bug Hunter Pipeline                  │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Symptom   │ 2. Minimal   │ 3. Root     │ 4. Verified│
│    Triage    │    Repro     │    Cause    │    Patch   │
└──────────────┴──────────────┴─────────────┴────────────┘
```

### Step 1: Symptom & Evidence Collection
1. Collect exact error output, stack trace, logs, and environmental context (OS, Node/Python version).
2. Deconstruct the stack trace:
   - Identify the earliest line of project code in the trace (not internal library code).
   - Inspect variable states and arguments passed into that function.
3. Identify what was *expected* versus what *actually* occurred.

### Step 2: Minimal Reproduction (Red Phase)
1. Write the smallest possible failing test or standalone reproduction script in a scratch file.
2. Eliminate irrelevant dependencies, mock external network calls, and reduce inputs to the simplest failing case.
3. Run the reproduction test and confirm it fails with the exact target error.

### Step 3: Hypothesis Formulation & Root Cause Isolation
Formulate and test hypotheses methodically:
- **Hypothesis Checklist**:
  - [ ] **Type / Null Coercion**: Is an object `null`, `undefined`, or `None` unexpectedly?
  - [ ] **Off-by-one / Boundaries**: Are loop indices, slice offsets, or pagination limits flawed?
  - [ ] **Async / Race Conditions**: Did a Promise resolve out of order? Was a shared variable mutated concurrently?
  - [ ] **Silent Swallowing**: Did a blanket `catch` block swallow an earlier critical exception?
  - [ ] **Stale State / Caching**: Is outdated cache or memoized data being served?
- Use temporary deterministic debug assertions or logs (`print`, `console.error`) to trace the lifecycle of variables leading up to the crash.

### Step 4: Surgical Fix & Verification (Green Phase)
1. Implement the minimal necessary fix addressing the root cause, not the symptom.
2. Run the reproduction test created in Step 2: verify that it now passes.
3. Run the entire project test suite: verify zero regressions.
4. Remove any temporary debug logs or scaffolding before submitting.

---

---

## Comprehensive Root Cause Analysis (RCA) Output Template

When publishing an RCA investigation, output findings in this structured post-mortem format:

```markdown
# 🔬 Root Cause Analysis (RCA): [Bug Title / Incident Name]

## 1. Incident Metadata
- **RCA Identifier**: RCA-2026-0911-01
- **Severity**: P1 (Critical Outage) / P2 (Degraded Performance) / P3 (Minor Glitch)
- **Component / Service**: `auth-service` -> `jwt_validator.py`
- **First Observed**: 2026-09-11 14:10:02 UTC
- **Root Cause Isolated**: 2026-09-11 14:18:30 UTC
- **Resolution Verified**: 2026-09-11 14:24:12 UTC
- **Time to Detect (TTD)**: 4m 12s | **Time to Resolve (TTR)**: 14m 10s
- **Lead Investigator**: `@bug-hunter`

---

## 2. Executive Summary & Impact Radius
A race condition during token refresh allowed concurrent identical refresh requests to invalidate active user sessions prematurely. Affected ~3.4% of active mobile users between 14:00 and 14:25 UTC. No customer data compromised or leaked.

---

## 3. The "5 Whys" Root Cause Chain
1. **Why did user sessions disconnect?** The backend returned HTTP 401 on valid API calls.
2. **Why was 401 returned?** The stored refresh token secret did not match the incoming token hash.
3. **Why was the hash mismatched?** A concurrent request rotated the secret 12ms before the second request arrived.
4. **Why was secret rotation allowed concurrently?** The token rotation endpoint lacked distributed locking or idempotency keys.
5. **Why was locking omitted?** The rotation handler assumed a single-replica environment and did not account for multi-pod Kubernetes deployment.

---

## 4. Deterministic Reproduction Harness
```python
# tests/repro/test_rca_concurrent_refresh.py
import asyncio
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_concurrent_refresh_race_condition():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        token = "valid_refresh_token_xyz"
        # Fire 5 concurrent refresh requests with identical token
        responses = await asyncio.gather(*[
            client.post("/auth/refresh", json={"refresh_token": token})
            for _ in range(5)
        ])
        status_codes = [r.status_code for r in responses]
        # Failure mode before fix: 4 out of 5 returned 401 or 500
        assert status_codes.count(200) >= 1
        assert 500 not in status_codes
```

---

## 5. Surgical Fix & Code Diff
```diff
--- a/src/services/auth_service.py
+++ b/src/services/auth_service.py
@@ -88,6 +88,8 @@ async def rotate_refresh_token(user_id: str, old_token: str) -> TokenPair:
-    # Non-atomic check and rotate
-    if not verify_token(user_id, old_token):
-        raise InvalidTokenError()
-    return await generate_new_tokens(user_id)
+    # Atomic Redis distributed lock with 5-second lease
+    async with redis_lock(f"lock:refresh:{user_id}", timeout=5):
+        if not verify_token(user_id, old_token):
+            raise InvalidTokenError()
+        return await generate_new_tokens(user_id)
```

---

## 6. Preventive Action Items & Regression Guards
- [ ] **Regression Test**: Integrated `test_concurrent_refresh_race_condition` into primary CI test suite.
- [ ] **Static Code Lint**: Add architectural rule banning un-locked state mutations in multi-replica endpoints.
- [ ] **Telemetry Alert**: Set alert threshold if 401 refresh spikes $> 2\%$ over 5-minute rolling window.
```

### Machine-Parseable RCA JSON Contract
```json
{
  "$schema": "agent-rca-report/v1",
  "rca_id": "RCA-2026-0911-01",
  "bug_title": "Concurrent refresh token race condition invalidating active sessions",
  "severity": "P2",
  "root_cause_file": "src/services/auth_service.py:88",
  "root_cause_category": "CONCURRENCY_RACE_CONDITION",
  "reproduction_test_path": "tests/repro/test_rca_concurrent_refresh.py",
  "reproduction_status": "REPRODUCED_AND_VERIFIED",
  "regression_tests_passing": true,
  "action_items_count": 3
}
```

---

## Anti-Patterns & Traps to Avoid

1. **Symptom Band-Aiding (Defensive Whack-a-Mole)**: Wrapping crashing lines in blanket `try...catch { return null; }` or blind optional chaining (`user?.profile?.settings?.id`). This suppresses the crash but converts an explicit failure into a silent data corruption bug downstream. Fix the root cause, not the symptom.
2. **"Shotgun Debugging" (Guess-and-Check)**: Making multiple random code edits across multiple files simultaneously hoping the error resolves. If you don't know *why* a change fixed the bug, you haven't fixed it. Formulate a hypothesis and test one variable at a time.
3. **Skipping the Reproduction Test Case**: Modifying source code before producing a reliable, automated failing test case. Without a repro test, you cannot prove the bug was resolved or prevent future regressions.
4. **Leaving Debug Scaffolding in Production**: Submitting PRs containing leftover `print("DEBUG HERE")` statements, commented-out dead code blocks, or temporary mock hardcoding.

---

## Quality Checklist

- [ ] A minimal, deterministic reproduction test case was created and failed reliably before any fix.
- [ ] Root cause is isolated to the exact line and state transition, not just masked with defensive null checks.
- [ ] Surgical fix modifies the minimal necessary code surface without side-effect regressions.
- [ ] The reproduction test passes after applying the patch.
- [ ] The broader project test suite runs completely green.
- [ ] All temporary debug logs, print statements, and scratch files are cleaned up.
