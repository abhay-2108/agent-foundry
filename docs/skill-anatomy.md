# Canonical Skill Anatomy & Authoring Specification

Every skill in the **Agent Foundry** ecosystem follows a standardized anatomy designed for high autonomy, zero token waste, and uncompromising quality.

---

## 1. Core Philosophy: Process, Not Prose

Skills are **not passive documentation** that agents read for inspiration. Skills are **executable state-machine workflows** that agents must follow step-by-step.

### The 3 Non-Negotiables:
1. **Anti-Rationalization**: Agents naturally invent excuses to skip tests, create oversized diffs, or make assumptions. Every skill provides an anti-rationalization table pairing common excuses with strict rebuttals.
2. **Verification is Evidence**: "Code seems right" or "I believe this works" is forbidden. Verification demands fresh, empirical proof: test runner exit code 0, static typing passes, diff line counts, and captured runtime outputs.
3. **Progressive Disclosure**: Only skill names and descriptions are loaded into context at startup. Full `SKILL.md` runbooks are loaded on trigger, and `references/` checklists are loaded only when executing that phase. All `SKILL.md` files must strictly remain under **500 lines**.

---

## 2. Standard `SKILL.md` File Anatomy

Every `SKILL.md` file must be organized according to this exact section hierarchy:

```
┌────────────────────────────────────────────────────────┐
│ 1. YAML Frontmatter (name, description with trigger)   │
├────────────────────────────────────────────────────────┤
│ 2. # Title & Overview                                  │
├────────────────────────────────────────────────────────┤
│ 3. ## When to Use (& When NOT to Use)                  │
├────────────────────────────────────────────────────────┤
│ 4. ## Core Process / Step-by-Step Workflow SOP          │
├────────────────────────────────────────────────────────┤
│ 5. ## Common Rationalizations (Excuse vs Reality)      │
├────────────────────────────────────────────────────────┤
│ 6. ## Red Flags (Anti-patterns & failure modes)        │
├────────────────────────────────────────────────────────┤
│ 7. ## Verification (Evidence checklist)                │
└────────────────────────────────────────────────────────┘
```

---

## 3. Section-by-Section Specification

### 1. Frontmatter
```yaml
---
name: backend-architecture
description: >-
  Use this skill when designing, implementing, or optimizing backend services,
  REST/gRPC APIs, databases, connection pools, and error envelopes.
---
```
- **`name`**: Must match the containing directory name exactly.
- **`description`**: Must be under 1,024 characters and must begin with or include `"Use this skill when..."`.

### 2. Title & Overview
A concise 2–3 paragraph summary defining the domain scope, primary tenets, and architecture.

### 3. When to Use
- Bulleted list of concrete use cases.
- List of natural language trigger phrases (`"design endpoint"`, `"add database migration"`).
- Explicit **"When NOT to use"** clause pointing to companion skills (preventing skill overlap).

### 4. Core Process & Step-by-Step SOP
Numbered sequence of actionable steps. Must cite exact file patterns, command shapes, and state transitions.

### 5. Common Rationalizations
Markdown table contrasting typical agent excuses against engineering reality:

| Rationalization | Reality |
| :--- | :--- |
| *"I will write tests after the implementation works."* | Code without tests accumulates unverified edge cases. Apply Prove-It RED->GREEN first. |

### 6. Red Flags
Bulleted list of anti-patterns and warning signs that indicate the agent is cutting corners or deviating from standards.

### 7. Verification Checklist
Concrete checklist demanding empirical proof before the agent yields execution:
- [ ] Static type checker passes with zero errors (`mypy`, `tsc`).
- [ ] Diff line budget adheres to $\le 100\text{--}150$ lines.
- [ ] Unit test execution command produces exit code 0.
