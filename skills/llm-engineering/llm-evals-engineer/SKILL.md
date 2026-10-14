---
name: llm-evals-engineer
description: >-
  Use this skill when designing, building, or executing automated evaluation (evals) suites
  for LLMs, RAG systems, and AI agents. Implements LLM-as-a-judge rubrics, regression test
  fixtures, and quantitative scoring metrics (faithfulness, hallucination, context precision) using Promptfoo, DeepEval, or RAGAS.
---

# LLM Evals Engineer & Benchmarking Specialist

## Overview

Designs, implements, and runs automated quantitative evaluation (evals) suites for LLMs, RAG pipelines, and agentic tool workflows. Measures context precision, recall, faithfulness, hallucination rates, and LLM-as-a-judge alignment using Promptfoo, DeepEval, or RAGAS.

## When to Use

- Before deploying a new prompt, model version, or RAG pipeline to production.
- When measuring hallucination rates, answer relevancy, and factual faithfulness.
- When configuring automated testing tools (`Promptfoo`, `DeepEval`, `RAGAS`, `TruLens`).
- When defining quantitative grading rubrics for **LLM-as-a-judge** evaluations.
- Trigger phrases: `"set up evals"`, `"evaluate prompt"`, `"Promptfoo test"`, `"RAGAS evaluation"`, `"measure hallucinations"`.

---
- **When NOT to use**: Traditional unit testing of deterministic python functions (use `code-reviewer`) or exploratory agent trajectory debugging (use `agent-trajectory-evaluator`).

## Core Process & Evaluation Architecture

## The Core Evaluation Triad

```
┌────────────────────────────────────────────────────────┐
│                   Evaluation Dimensions                │
├───────────────────┬───────────────────┬────────────────┤
│ 1. Faithfulness   │ 2. Context        │ 3. Answer      │
│    (Groundedness) │    Precision      │    Relevancy   │
├───────────────────┼───────────────────┼────────────────┤
│ • Are claims in   │ • Did the search  │ • Does answer  │
│   the answer fully│   engine fetch    │   directly     │
│   supported by the│   relevant context│   address user │
│   retrieved chunks│   without clutter?│   question?    │
└───────────────────┴───────────────────┴────────────────┘
```

---

## Step-by-Step Evals Implementation (Promptfoo Pattern)

### Step 1: Create Golden Evaluation Dataset (`eval_dataset.yaml`)
Curate a diverse benchmark suite representing typical queries, edge cases, and adversarial attempts:
```yaml
# promptfooconfig.yaml
description: "RAG Answer Quality & Hallucination Benchmark"

prompts:
  - "file://prompts/rag_system_prompt.txt"

providers:
  - id: "openai:gpt-4o"
  - id: "google:gemini-1.5-pro"

tests:
  - vars:
      query: "What is our company refund window for enterprise tiers?"
      context: "Enterprise contracts have a 45-day refund window upon written notice."
    assert:
      - type: contains
        value: "45"
      - type: llm-rubric
        value: "The answer must state that the refund window is 45 days and requires written notice. It must not invent exceptions."
      - type: latency
        threshold: 2500 # Max 2.5 seconds
```

---

## Programmatic DeepEval Implementation (Python)

```python
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

# Construct Test Case
test_case = LLMTestCase(
    input="How do I reset my API key?",
    actual_output=agent_response,
    retrieval_context=[doc_snippet_1, doc_snippet_2]
)

# 1. Hallucination Metric (Detect unsupported statements)
hallucination_metric = HallucinationMetric(threshold=0.1)
hallucination_metric.measure(test_case)

# 2. Answer Relevancy Metric
relevancy_metric = AnswerRelevancyMetric(threshold=0.8)
relevancy_metric.measure(test_case)

print(f"Hallucination Score: {hallucination_metric.score} (Passed: {hallucination_metric.is_successful()})")
print(f"Relevancy Score: {relevancy_metric.score}")
```

---

## Evals Report Template

```markdown
### 📊 Evaluation Run Summary: [Benchmark Suite Name]

**Total Test Cases**: 50 | **Passed**: 48 (96%) | **Failed**: 2 (4%)
**Average Latency**: 1.42s | **Estimated Token Cost**: $0.18

#### Metric Breakdown:
- **Faithfulness / Grounding**: 98.2%
- **Answer Relevancy**: 94.5%
- **Hallucination Rate**: 1.8% (Target < 2.0%)

#### Failed Test Regressions:
1. **Case #14 (Boundary Condition)**:
   - *Query*: "Can a trial user invite 10 team members?"
   - *Failure*: Model answered "Yes" when documentation specified maximum of 5 trial members.
   - *Remediation*: Update system prompt negative constraints on trial limits.
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Eyeballing 5-10 prompt responses in the playground is enough testing."* | Manual spot-checking hides regression bugs, distribution shift, and edge-case hallucinations; automated benchmark suites with quantitative metrics are required. |
| *"LLM-as-a-judge is completely objective and doesn't need calibration."* | Judge models exhibit verbosity bias, self-preference, and position bias; judges must be calibrated against human ground-truth rubrics. |
| *"Running evals on every commit is too slow and expensive."* | Tiered evaluation (fast unit assert tests on PRs, deep multi-turn LLM-as-a-judge on nightly runs) balances latency and evaluation rigor. |
| *"We don't need synthetic test data if we have no user logs yet."* | Synthetic golden datasets generated via multi-perspective edge cases bootstrap evals before production traffic exists. |

## Red Flags

- Prompt or model changes merged to main without running automated evaluation benchmark suites.
- Evaluation rubrics that score on arbitrary 1-10 scales without unambiguous anchor criteria.
- High test pass rates masking zero-diversity test fixtures (all tests using identical simple sentence structures).
- Evaluating RAG systems solely on generation output without evaluating retrieval context precision.

## Verification

After completing the workflow, confirm:
- [ ] Benchmark dataset includes golden inputs, reference truths, and edge-case failure probes.
- [ ] Quantitative metrics (Faithfulness > 0.90, Answer Relevance > 0.85, Context Recall > 0.85) are measured.
- [ ] LLM judge outputs include structured reasoning and numerical confidence scores.
- [ ] Regression test suite is integrated into CI/CD pre-merge workflows.
