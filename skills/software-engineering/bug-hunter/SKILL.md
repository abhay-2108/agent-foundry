---
name: bug-hunter
description: Use this skill when diagnosing, isolating, reproducing, and resolving
  tricky software bugs, runtime panics, regressions, and logic errors using minimal
  repro test cases.
---

# Bug Hunter & Root Cause Debugger

## Overview

Diagnoses, isolates, reproduces, and resolves tricky software bugs, runtime exceptions, race conditions, and regressions using a scientific hypothesis-driven methodology and minimal failing reproduction tests.

## When to Use

- When receiving an error message, stack trace, or failing test.
- When an application behaves incorrectly, produces wrong calculations, or hangs.
- When investigating flaky, intermittent, or race condition issues.
- When tasked with fixing an issue where the root cause is unknown.
- Trigger phrases: `"debug this"`, `"find the bug"`, `"why is this failing?"`, `"fix this crash"`, `"investigate error"`.
- **When NOT to use**: Reviewing greenfield PRs for general style and naming conventions (use `code-reviewer`).

## Core Process & Scientific Debugging Protocol

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"I can fix this bug immediately by tweaking this line without writing a test."* | Fixing code without a reproduction test frequently papers over the symptom while leaving the root cause intact, inviting future regressions. |
| *"The bug is intermittent, so it must be a transient hardware or network glitch."* | Intermittent bugs are almost always race conditions, unhandled promise rejections, or un-synchronized shared memory access. |
| *"Adding print statements is enough; we don't need a debugger or traces."* | Unstructured print debugging pollutes code, doesn't capture concurrent threads, and is stripped before committing. |
| *"The stack trace points to line 42, so the bug must be on line 42."* | Stack traces report where an exception was thrown, not where corrupted state originated; trace upstream state mutations. |

## Red Flags

- Applying 'shotgun fixes' (changing multiple lines at once hoping the bug disappears).
- Wrapping buggy code in generic `try...except: pass` blocks to suppress the error.
- Declaring a bug fixed without running the minimal reproduction test in an isolated environment.
- Failing to check for identical bug patterns across related modules in the codebase.

## Verification

After completing the workflow, confirm:
- [ ] A minimal failing reproduction test is written and confirmed failing before applying the fix.
- [ ] The root cause is identified and explained with causal evidence, not just symptom suppression.
- [ ] The fix is applied and verified: reproduction test passes and all existing test suites remain green.
- [ ] Edge cases (null inputs, boundary conditions, concurrent access) are covered by regression tests.
