# Adoption Guide: Greenfield vs. Brownfield Engineering

This guide outlines how to adopt Agent Foundry workflows depending on whether you are building a new application from scratch or integrating into an existing codebase.

---

## 1. Greenfield Projects: Full-Lifecycle Pipeline

When initiating a new repository or feature set, adopt the full sequential lifecycle:

```
┌────────────────────────────────────────────────────────────────────────┐
│ DEFINE       │ /brainstorm or /memo -> Solidify requirements & scope   │
├──────────────┼────────────────────────────────────────────────────────┤
│ PLAN         │ /spec or /gsd -> Produce DAG plan with STOP-after-spec │
├──────────────┼────────────────────────────────────────────────────────┤
│ BUILD        │ /build -> Vertical slices (<= 100-150 lines per slice) │
├──────────────┼────────────────────────────────────────────────────────┤
│ VERIFY       │ /test -> Prove-It test suite passing (exit code 0)     │
├──────────────┼────────────────────────────────────────────────────────┤
│ REVIEW       │ /review -> Senior 5-axis code review matrix            │
├──────────────┼────────────────────────────────────────────────────────┤
│ SHIP         │ /ship -> Parallel gate (code + security + SRE)         │
└────────────────────────────────────────────────────────────────────────┘
```

### Greenfield Rules:
1. **Never skip `/spec`**: Define explicit interfaces and schemas before generating source files.
2. **Commit after each slice**: Never bundle 10 tasks into a single unreviewed commit.

---

## 2. Brownfield Projects: Verification-First Fast Path

When working in an existing, large-scale production codebase:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. LOCALIZE  │ /debug -> Identify defect; isolate minimal repro       │
├──────────────┼────────────────────────────────────────────────────────┤
│ 2. PROVE-IT  │ Write standalone test -> Assert RED (must fail)        │
├──────────────┼────────────────────────────────────────────────────────┤
│ 3. MINIMAL   │ Apply surgical patch (diff <= 50 lines)                │
├──────────────┼────────────────────────────────────────────────────────┤
│ 4. GREEN     │ Assert GREEN (exit code 0) + full regression suite     │
├──────────────┼────────────────────────────────────────────────────────┤
│ 5. GATE      │ /review -> Ensure no drive-by refactoring outside bug  │
└────────────────────────────────────────────────────────────────────────┘
```

### Brownfield Rules:
1. **Respect Chesterton's Fence**: Never rewrite existing legacy code without understanding why it was originally written.
2. **Zero Drive-By Refactoring**: Do not reformat untouched files or alter code styling. Keep diffs strictly to the target fix.
3. **Always Prove-It First**: Never accept a bug fix without a failing test case that turns green after the patch.
