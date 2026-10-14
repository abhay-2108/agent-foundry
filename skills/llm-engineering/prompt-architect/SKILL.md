---
name: prompt-architect
description: >-
  Use this skill when authoring, refining, or debugging system prompts, few-shot templates,
  and structured output schemas. Enforces deterministic, machine-parseable outputs (JSON/Pydantic/Instructor),
  eliminates markdown leakage, and applies battle-tested prompt engineering patterns.
---

# Prompt Architect & Structured Output Engineer

## Overview

Authors, refines, and optimizes structured system prompts, few-shot templates, and deterministic output schemas. Uses XML boundary tags, Pydantic validation, negative constraint enforcement, and chain-of-thought scratchpads to guarantee machine-parseable outputs.

## When to Use

- When designing system prompts for new agents, subagents, or LLM pipelines.
- When an LLM leaks conversational filler ("Sure, here is your JSON:") instead of raw, valid JSON.
- When crafting few-shot examples that steer model reasoning without introducing bias.
- When formulating negative constraints ("Never do X") that models reliably respect.
- Trigger phrases: `"write a system prompt"`, `"prompt engineering"`, `"structured output"`, `"Pydantic JSON schema"`, `"fix prompt"`.

---
- **When NOT to use**: Creative copywriting or persuasive human marketing prose (use `human-writer`).

## Core Process & Prompt Engineering Patterns

## The 6-Block System Prompt Architecture

```
┌────────────────────────────────────────────────────────┐
│               Standard System Prompt Anatomy           │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Identity  │ 2. Context   │ 3. Core     │ 4. Output  │
│    & Role    │    & Domain  │    Rules    │    Schema  │
├──────────────┴──────────────┼─────────────┴────────────┤
│ 5. Negative Constraints     │ 6. Few-Shot Examples     │
└─────────────────────────────┴──────────────────────────┘
```

1. **Identity & Role**: Precise domain identity, operational stance, and tone.
2. **Context & Domain**: Workspace background, available tools, and runtime environment.
3. **Core Rules / Workflow**: Step-by-step reasoning instructions (Chain-of-Thought or Plan-Execute).
4. **Output Schema & Contract**: Strictly typed structure (JSON Schema, TypeScript interface, or XML tags).
5. **Negative Constraints**: Explicit prohibitions detailing common failure modes to avoid.
6. **Few-Shot Examples**: 2–3 paired input-output demonstrations representing standard and edge cases.

---

## Structured Output Enforcement (Instructor / Pydantic Pattern)

Never ask for JSON using raw string prompts like `"Return JSON"`. Use constrained decoding or schema enforcement:

```python
from pydantic import BaseModel, Field
from typing import List, Literal
import instructor
from openai import OpenAI

# Define Strict Output Schema
class RiskAssessment(BaseModel):
    risk_level: Literal["low", "medium", "high", "critical"]
    affected_components: List[str] = Field(description="Names of impacted software services")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Model confidence between 0 and 1")
    remediation_steps: List[str]

# Patch client with Instructor for guaranteed schema conformity
client = instructor.from_openai(OpenAI())

response: RiskAssessment = client.chat.completions.create(
    model="gpt-4o",
    response_model=RiskAssessment,
    messages=[{"role": "user", "content": "Analyze vulnerability CVE-2024-1234"}]
)
```

---

## Battle-Tested Prompt Patterns

### 1. XML Tag Delimitation
Use XML tags to clearly separate instructions from untrusted user inputs:
```text
You are a senior data validator. You will evaluate the user payload below.
<user_input>
{{USER_INPUT}}
</user_input>

Analyze the content inside <user_input> against the rules in <validation_rules>.
```

### 2. Guarding Negative Constraints
Models struggle with passive negatives ("Don't be verbose"). Rephrase as active imperatives:
- ❌ *Weak*: "Don't write long answers."
- ✅ *Strong*: "Limit all output strictly to a 3-bullet executive summary. Each bullet must be under 20 words."

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Telling the model 'Be accurate and do not make mistakes' ensures good outputs."* | Vague emotional pleas fail to constrain model behavior; explicit negative constraints and schema contracts are required. |
| *"JSON schemas in prompt instructions are enough; we don't need Pydantic validation."* | LLMs occasionally emit trailing commas, markdown fences, or markdown commentary that break raw JSON parsers. |
| *"More prompt text is always better for accuracy."* | Prompt bloat degrades attention, dilutes critical instructions (the 'lost in the middle' phenomenon), and inflates inference costs. |
| *"One-shot examples aren't necessary if the instructions are clear."* | Exemplars (few-shot inputs and expected outputs) demonstrate edge cases and formatting nuances far more reliably than abstract instructions. |

## Red Flags

- Prompts relying on informal natural language formatting without XML delimiters (`<context>`, `<instructions>`, `<input>`).
- Permitting markdown fences (```json ... ```) when the downstream consumer expects pure machine-parseable JSON.
- Prompts lacking negative constraints (e.g. failing to specify what NOT to include).
- Ambiguous prompt instructions that allow the model to guess missing parameters silently.

## Verification

After completing the workflow, confirm:
- [ ] Prompt uses explicit XML boundary tags for context, inputs, and instructions.
- [ ] Structured outputs are validated against strict Pydantic / Zod schemas with fallback recovery.
- [ ] Few-shot examples demonstrate target formatting and at least one complex edge case.
- [ ] Prompt eliminates markdown leakage and produces deterministic parsing across multiple test runs.
