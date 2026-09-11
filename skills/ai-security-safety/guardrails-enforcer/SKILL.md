---
name: guardrails-enforcer
description: >-
  Use this skill when designing, implementing, or auditing runtime AI guardrails and safety filters.
  Enforces input sanitization, PII redaction, topic boundaries, toxicity filtering,
  and output hallucination checks using NeMo Guardrails, Llama Guard, or Guardrails AI.
---

# Guardrails Enforcer & Runtime Safety Controller

A production safety skill that installs programmable, deterministic guardrails around language models and autonomous agents. Acts as an active firewall intercepting unsafe inputs and sanitizing model outputs before they reach users.

## When to Use This Skill
- When building public-facing AI bots where toxic, biased, or harmful responses must be prevented.
- When preventing Personally Identifiable Information (PII) leakage (SSNs, credit cards, passwords).
- When enforcing strict topic boundaries (`"Only answer questions about our SaaS product; decline sports/politics"`).
- When implementing runtime safety frameworks (`NeMo Guardrails`, `Llama Guard`, `Guardrails AI`).
- Trigger phrases: `"set up guardrails"`, `"PII redaction"`, `"content filtering"`, `"NeMo Guardrails"`, `"Llama Guard integration"`.

---

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

## Anti-Patterns & Traps to Avoid

1. **ReDoS (Regular Expression Denial of Service)**: Writing vulnerable, catastrophic-backtracking regex patterns (e.g., `([\w\.-]+)+@[\w\.-]+`) for PII masking. A malicious user submitting repeated whitespace or special characters can freeze the server CPU for minutes. Always use atomic grouping, Google RE2, or dedicated libraries like Microsoft Presidio.
2. **Output-Only Guardrails Blindness**: Intercepting toxicity only on the generated output while letting raw, malicious user inputs reach downstream database tools and vector search retrieval. Guardrails must be enforced as a dual-layer sandwich (Input Rails $\rightarrow$ Agent $\rightarrow$ Output Rails).
3. **Heavyweight LLM Calls for Simple Filter Checks**: Calling a large 70B LLM to perform basic content moderation, adding 2+ seconds of latency to every interaction. Layer checks hierarchically: (1) Deterministic regex/heuristics (0ms), (2) Embedding cosine bounds (15ms), and (3) Small specialized classifiers like Llama-Guard-3-1B (<150ms).
4. **Preachy, Moralizing Fallback Refusals**: Emitting patronizing or apologetic AI lectures (*"As an AI, I am ethically prohibited from..."*). Refusals must be professional, neutral, and clear: *"I can only assist with account administration and billing queries."*

---

## Quality Checklist

- [ ] Dual-layer architecture: Input Rails screen user prompts and Output Rails verify generated responses.
- [ ] PII redaction patterns are ReDoS-safe and do not exhibit catastrophic backtracking on long strings.
- [ ] Guardrail execution overhead is benchmarked at $<150\text{ms}$ total latency.
- [ ] Topical bounds reliably deflect off-topic queries without breaking valid edge-case user questions.
- [ ] Blocked events emit structured security telemetry logs with trigger rules and redacted payloads.
- [ ] Safe fallback messages are concise, neutral, and professional without moralizing preambles.
