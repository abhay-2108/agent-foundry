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

## Bug Hunter Investigation Report Template

When delivering a bug resolution to the user, format your explanation using this structure:

```markdown
### 🐞 Bug Hunter Investigation Report

**Issue Summary**: [Concise summary of the bug]
**Severity**: Critical / High / Medium / Low
**Root Cause File**: `path/to/file.ts:45`

#### 1. Root Cause Breakdown
- Explain exactly what went wrong and why.
- Detail the sequence of events leading from initial trigger to failure.

#### 2. Reproduction Evidence
```language
// Minimal reproduction code showing failure before fix
```

#### 3. Surgical Fix & Diff
```diff
- // Vulnerable / broken line
+ // Corrected implementation
```

#### 4. Verification Results
- [x] Minimal reproduction test passes.
- [x] Full regression test suite clean (X tests passing).
- [x] Edge cases verified (null, boundary, empty inputs).
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
