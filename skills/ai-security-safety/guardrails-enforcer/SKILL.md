---
name: guardrails-enforcer
description: >-
  Use this skill when designing, implementing, or auditing runtime AI guardrails and safety filters.
  Enforces input sanitization, PII redaction, topic boundaries, toxicity filtering,
  and output hallucination checks using NeMo Guardrails, Llama Guard, or Guardrails AI.
---

# Guardrails Enforcer & Runtime Safety Controller

## Overview

Implements programmatic runtime AI safety filters, input sanitization, PII redaction, topic boundaries, toxicity filtering, and output hallucination verification across LLM applications and agent tool calls.

## When to Use

- When building public-facing AI bots where toxic, biased, or harmful responses must be prevented.
- When preventing Personally Identifiable Information (PII) leakage (SSNs, credit cards, passwords).
- When enforcing strict topic boundaries (`"Only answer questions about our SaaS product; decline sports/politics"`).
- When implementing runtime safety frameworks (`NeMo Guardrails`, `Llama Guard`, `Guardrails AI`).
- Trigger phrases: `"set up guardrails"`, `"PII redaction"`, `"content filtering"`, `"NeMo Guardrails"`, `"Llama Guard integration"`.

---
- **When NOT to use**: Static source-code vulnerability scanning (use `security-vulnerability-scanner`) or prompt injection adversarial red-teaming (use `prompt-injection-red-teamer`).

## Core Process & Guardrail Implementation

## The Dual-Layer Guardrail Architecture

```
User Input ──> [Input Guardrails: PII / Jailbreak / Topic] ──> [LLM / Agent]
                                                                     │
Client App <── [Output Guardrails: Grounding / Schema / Leakage] <──┘
```

1. **Input Guardrails**:
   - **PII Masking**: Replaces sensitive data with placeholders (`[EMAIL_REDACTED]`, `[SSN_REDACTED]`).
   - **Jailbreak Detection**: Classifies whether user prompt violates safety policies before the main model runs.
   - **Topic Bounds**: Rejects off-topic queries cheaply without calling expensive frontier models.
2. **Output Guardrails**:
   - **Schema Validation**: Ensures output strictly conforms to the expected JSON structure.
   - **Hallucination & Grounding Check**: Cross-checks generated answers against retrieved sources.
   - **Competitor / Policy Filter**: Blocks mentions of unauthorized competitors or legal liabilities.

---

## Step-by-Step Implementation Patterns

### 1. PII Redaction Pattern (Python Regex + Presidio)
```python
import re

def redact_pii(text: str) -> str:
    # Redact Emails
    text = re.sub(r'[\w.-]+@[\w.-]+\.\w+', '[EMAIL_REDACTED]', text)
    # Redact Phone Numbers (US & standard formats)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]', text)
    # Redact Social Security Numbers (SSN: 9 digits)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', text)
    # Redact Credit Cards (16 digits formatted or continuous)
    text = re.sub(r'\b(?:\d{4}[- ]?){3}\d{4}\b', '[CREDIT_CARD_REDACTED]', text)
    return text
```

### 2. NeMo Guardrails Colang Flow Pattern
Define safety flows using Colang (`config.co`):
```colang
define user ask off_topic
  "What is the capital of France?"
  "Who won the soccer match?"

define flow off_topic_control
  user ask off_topic
  bot inform off_topic

define bot inform off_topic
  "I am the Customer Support Assistant for CloudOps. I can only assist with our platform services and billing."
```

### 3. Llama Guard Output Verification
Before returning response to user, run a lightweight classification pass:
```python
def check_safety_with_llama_guard(model_output: str) -> bool:
    # Fast classification prompt to Llama-Guard-3-1B
    # Returns True if safe, False if violating safety policy
    ...
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"A strong system prompt is enough to prevent safety violations."* | System prompts are easily bypassed by prompt injection and jailbreaks; runtime programmatic guardrails (regex, Presidio, Llama Guard) are mandatory. |
| *"PII redaction adds too much latency to user queries."* | Fast regex and compiled NER tokenizers execute in sub-millisecond time and prevent catastrophic GDPR/HIPAA compliance breaches. |
| *"Output checks are redundant if the input was validated."* | Models can hallucinate toxic content, leak internalized training secrets, or hallucinate dangerous code even on benign inputs. |
| *"We can log raw prompts and outputs to debug guardrail false positives."* | Logging unredacted inputs and outputs persists user PII, API keys, and sensitive tokens into audit log indices. |

## Red Flags

- Relying solely on LLM self-moderation without deterministic programmatic filters.
- Unmasked credit card numbers, social security numbers, or API keys in application logs.
- Failing to implement timeout and fallback policies when an external guardrail service is unreachable.
- Directly streaming raw LLM tokens to the user before passing basic toxicity and safety gates.

## Verification

After completing the workflow, confirm:
- [ ] Input pipeline scrubs credit card numbers, SSNs, emails, and phone numbers before LLM ingestion.
- [ ] Colang / NeMo Guardrails or Llama Guard checks execute on input and output vectors.
- [ ] Safety fallbacks respond gracefully with neutral refusal messages without revealing system instructions.
- [ ] Automated guardrail test suite passes with zero false-negative leaks on benchmark test payloads.
