---
name: skill-creator
description: >-
  Use this skill when creating, editing, or evaluating AI agent skills.
  Provides guidance on structuring SKILL.md files, crafting precise triggers,
  applying progressive disclosure, writing executable workflows, and validating skill reliability.
---

# Skill Creator & Agent Capability Architect

## Overview

Authors, evaluates, refines, and packages reusable AI agent skills conforming to the Agent Skills standard. Enforces progressive disclosure, anti-rationalization tables, triggering descriptions, and concrete verification gates.

## When to Use

- When tasked with creating a new skill for the agent skill library.
- When refactoring or updating an existing `SKILL.md` file.
- When defining new procedural workflows, tool runbooks, or domain cheatsheets.
- Trigger phrases: `"create a skill"`, `"write a new skill"`, `"skill creator"`, `"package this workflow as a skill"`.
- **When NOT to use**: Writing application business logic or backend APIs (use `backend-architecture`).

## Core Process & Skill Authoring Methodology

## The Anatomy of an Agent Skill

An agent skill is a self-contained directory with a mandatory `SKILL.md` entrypoint:

```text
skills/<skill-name>/
├── SKILL.md              # REQUIRED: Frontmatter + instructions + workflow
├── scripts/              # OPTIONAL: Deterministic helper scripts (bash, python)
├── examples/             # OPTIONAL: Input/output pairs and reference samples
├── resources/            # OPTIONAL: Static assets, schemas, templates
└── references/           # OPTIONAL: Deep documentation (loaded on-demand)
```

---

## Core Principles of Great Skill Design

### 1. Progressive Disclosure
- The agent's context window is precious. Do not stuff entire manuals into `SKILL.md`.
- **Level 1 (Catalog View)**: Only the YAML `name` and `description` are loaded at startup.
- **Level 2 (Execution View)**: The full `SKILL.md` is loaded only when the skill is triggered.
- **Level 3 (Deep Reference View)**: Auxiliary documentation belongs in `references/` and is viewed by the agent only if needed.

### 2. High-Precision YAML Frontmatter
The `description` is the **sole decision factor** the orchestrator uses to activate the skill:
- **Write in the third person**: Use *"Use this skill when..."* rather than *"I can..."* or *"You should..."*.
- **Include explicit triggers**: List exact user intentions, file extensions, or lifecycle phases.
- **Set boundaries**: State what the skill does *and* what it does not do.

### 3. Procedural SOPs, Not Generic Advice
- Avoid vague advice like "write clean code" or "be careful".
- Provide concrete, numbered steps: inspect file X, execute command Y, assert output Z.
- Include executable command line snippets and code templates.

---

## Step-by-Step Skill Authoring Workflow

### Step 1: Define Scope & Triggers
1. Determine the exact user problem or repetitive task the skill solves.
2. Formulate 4–6 representative user prompts that should trigger the skill.
3. Formulate 2–3 boundary prompts that should *not* trigger the skill (to prevent false activations).

### Step 2: Draft the `SKILL.md` Template
Use this standard blueprint:

```markdown
---
name: my-skill-name
description: >-
  Use this skill when [condition/user prompt]. Enforces [key standard],
  automates [workflow], and produces [output artifact].
---

# Skill Title

Short overview of the skill's purpose.

## When to Use This Skill
- Bulleted list of triggers, phrases, and scenarios.

## Prerequisites & Tool Dependencies
- CLI tools, packages, or API keys needed.

## Step-by-Step Execution Workflow
1. Step 1: Context inspection
2. Step 2: Action / Script execution
3. Step 3: Verification

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"A skill is just a markdown prompt; it doesn't need a strict structure."* | Unstructured prompt dumps lead to agent hallucinations and missed steps; structured workflows with exit gates guarantee deterministic execution. |
| *"The skill description can just say 'Helps with coding'."* | Vague descriptions cause the agent's router to misfire or fail to trigger when needed; explicit 'Use when' criteria are mandatory. |
| *"Anti-rationalization tables are unnecessary extra tokens."* | Anti-rationalization tables are the single most effective barrier against agent corner-cutting and vibe-coding. |
| *"We can put all helper scripts inline in SKILL.md."* | Inlining 500-line scripts blows up token context; progressive disclosure with external `scripts/` keeps skills token-efficient. |

## Red Flags

- Frontmatter missing required `name` or `description` with explicit triggering keywords.
- Skills lacking verification checklists or allowing 'seems right' as exit criteria.
- Process steps written as vague suggestions ('consider writing tests') instead of actionable imperatives.
- Skills exceeding 500 lines without breaking deep checklists into `references/`.

## Verification

After completing the workflow, confirm:
- [ ] Frontmatter adheres strictly to the Agent Skills specification (`name`, `description`).
- [ ] Includes Overview, When to Use (with negative exclusions), Core Process, Common Rationalizations, Red Flags, and Verification.
- [ ] Companion helper scripts in `scripts/` execute without errors and pass `--test` flags.
- [ ] Skill triggers correctly under automated routing benchmark evaluation.
