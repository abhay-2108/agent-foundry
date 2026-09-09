---
name: skill-creator
description: >-
  Use this skill when creating, editing, or evaluating AI agent skills.
  Provides guidance on structuring SKILL.md files, crafting precise triggers,
  applying progressive disclosure, writing executable workflows, and validating skill reliability.
---

# Skill Creator & Agent Capability Architect

The authoritative meta-skill for authoring, testing, and packaging production-grade Agent Skills compatible with Antigravity, Claude Code, Codex, and OpenCode.

## When to Use This Skill
- When tasked with creating a new skill for the agent skill library.
- When refactoring or updating an existing `SKILL.md` file.
- When defining new procedural workflows, tool runbooks, or domain cheatsheets.
- Trigger phrases: `"create a skill"`, `"write a new skill"`, `"skill creator"`, `"package this workflow as a skill"`.

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

## Verification & Quality Gates
- How the agent verifies that the task was completed successfully.

## Error Handling & Recovery
- Explicit instructions on what to do if a step fails.

## Output Templates / Examples
- Concrete templates for reports, diffs, or code.
```

### Step 3: Test & Validate the Skill
1. **Frontmatter Test**: Ensure the YAML header parses without syntax errors.
2. **Trigger Evaluation**: Test with a sample user query matching the description to ensure the agent activates the skill.
3. **Execution Run**: Have the agent follow the skill instructions end-to-end on a realistic test case.
4. **Refactor Loopholes**: If the agent hallucinates or takes shortcuts, add explicit negative constraints ("Do NOT do X").

### Step 4: Verification & Packaging
Ensure the skill folder follows the standard structure: `skills/<skill-name>/SKILL.md` with optional `scripts/` or `examples/` subfolders for heavy helper assets.

---

## Anti-Patterns & Traps to Avoid

1. **Monolithic Code Inlining in `SKILL.md`**: Embedding 300+ lines of raw Python or TypeScript directly into the instruction markdown. This wastes thousands of context tokens on every invocation. Use Progressive Disclosure: place large executable scripts in `scripts/` and keep `SKILL.md` high-signal.
2. **First-Person or Chatty Frontmatter**: Writing descriptions like *"I can help you build websites..."*. Agents route skills using semantic similarity over tool descriptions; always use imperative, third-person phrasing: *"Use this skill when designing, building, or styling responsive web frontends..."*
3. **Overly Broad / Greedy Trigger Descriptions**: Writing descriptions like *"Use this skill for any programming task"*. This triggers false-positive skill activations on unrelated prompts. Include explicit trigger phrases and boundary scenarios.
4. **Folder and Frontmatter Name Mismatch**: Assigning `name: my-cool-tool` in YAML while naming the folder `skills/helper-tool/`. In standard skill loaders (Antigravity/Claude Code), the frontmatter `name` must strictly match the directory name.

---

## Quality Checklist

- [ ] Frontmatter `name` strictly matches the parent directory kebab-case name.
- [ ] Description is written in third-person imperative voice with concrete trigger scenarios.
- [ ] Large runnable code blocks (>60 lines) are extracted into `scripts/` following progressive disclosure.
- [ ] Core instructions include explicit anti-patterns and common developer traps.
- [ ] A standardized pre-flight quality checklist is provided for agent verification.
- [ ] All code snippets within the skill are syntactically valid and tested.
