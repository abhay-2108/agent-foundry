---
name: knowledge-capture
description: Use this skill when converting raw meeting transcripts, chat threads,
  and messy notes into structured, searchable knowledge artifacts and ADR decisions.
---

# Knowledge Capture & Meeting Intelligence

## Overview

Extracts structured decisions, Architecture Decision Records (ADRs), action items with assigned owners, and consensus rationale from messy meeting transcripts, Slack discussions, and brainstorm notes.

## When to Use

- When provided with an audio transcription, Zoom/Teams transcript, or raw meeting notes.
- When summarizing multi-turn chat threads or Slack discussions into a definitive decision document.
- When drafting Architectural Decision Records (ADRs), executive readouts, or technical specs from meetings.
- When tasked with extracting concrete action items, assignees, and deadlines from unstructured dialogue.
- Trigger phrases: `"capture meeting notes"`, `"extract action items"`, `"summarize transcript"`, `"document decision"`, `"meeting intelligence"`.

---
- **When NOT to use**: Executing code refactoring or running automated benchmarks.

## Core Process & Knowledge Synthesis Architecture

## Core Transformation Principles

1. **Differentiate Discussion from Decision**: Brainstorming explores possibilities; decisions establish commitments. Never confuse hypothetical ideas with agreed outcomes.
2. **Strict Action Item Accountability**: Every action item must answer: *Who owns it?*, *What is the exact deliverable?*, and *When is it due?* (No collective or anonymous assignments).
3. **Preserve the "Why" (Decision Rationale)**: Record rejected alternatives and the explicit reason a path was chosen to prevent teams from relitigating settled questions in future meetings.
4. **Document Dissent and Consensus**: If consensus was not reached, document the dissenting perspective and whether the team agreed to "disagree and commit".

---

## Structured Extraction Schema (Python / Pydantic)

When parsing high-volume transcripts programmatically, validate extracted artifacts against this schema:

```python
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    task: str = Field(description="Concrete verb-led deliverable description")
    owner: str = Field(description="Single individual responsible for execution")
    due_date: Optional[date] = Field(None, description="Agreed deadline")
    priority: Literal["P0", "P1", "P2"] = Field("P1", description="Urgency rating")
    status: Literal["Not Started", "In Progress", "Blocked"] = "Not Started"

class DecisionRecord(BaseModel):
    decision: str = Field(description="The agreed, binding decision")
    rationale: str = Field(description="Why this decision was chosen over alternatives")
    alternatives_considered: List[str] = Field(default_factory=list)
    dissenting_opinions: Optional[str] = Field(None, description="Unresolved objections or trade-offs")

class MeetingRecord(BaseModel):
    title: str
    date: date
    participants: List[str]
    executive_summary: str
    decisions: List[DecisionRecord]
    action_items: List[ActionItem]
    parking_lot_items: List[str]
```

---

## Standardized Markdown Output Template

```markdown
# Meeting Intelligence Record: [Meeting Title]

**Date & Time**: YYYY-MM-DD HH:MM | **Participants**: [Name 1], [Name 2]
**Executive Verdict**: 1–2 sentence summary of key outcomes.

---

## 1. Key Decisions & Rationale (ADR Format)
- **Decision 1**: Team approved migrating API endpoints from REST to gRPC.
  - **Rationale**: Eliminates JSON serialization overhead and generates typed client SDKs.
  - **Alternatives Rejected**: GraphQL (overkill for internal microservices), REST with OpenAPI (didn't solve latency).
  - **Dissent**: @Dave expressed concern regarding browser client compatibility; mitigated via grpc-web gateway.

## 2. Action Items & Next Steps
| Task Deliverable | Assignee | Due Date | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| Benchmark gRPC vs REST latency under 10k RPS | @Alex | 2026-09-15 | P0 | Not Started |
| Draft core proto schema for User Service | @Sarah | 2026-09-18 | P1 | In Progress |

## 3. Topic Digest & Trade-off Analysis
### Topic A: Database Scaling vs Caching
- **Context**: Read volume increased 4x over last quarter.
- **Discussion**: Evaluated Redis cluster vs Aurora read replicas.
- **Outcome**: Decided on Redis due to lower cost ($400/mo vs $1,800/mo) and sub-millisecond response.

## 4. Parking Lot & Unresolved Questions
- [ ] Need legal review of third-party model data retention policy by next Friday (@Jordan).
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"A verbatim chronological summary is more complete than an ADR."* | Nobody reads 10-page meeting transcripts; busy stakeholders need explicit decisions, trade-offs rejected, and assigned action owners. |
| *"Action items don't need deadlines if the owner is mentioned."* | Action items without concrete deadlines or measurable exit criteria turn into indefinite project debt. |
| *"Minor dissenting opinions can be omitted for brevity."* | Omitting rejected alternatives hides the context of why a decision was made, leading future teams to re-litigate the same issue. |
| *"We can infer consensus even if the transcript ends abruptly."* | Assuming agreement when discussion was unresolved causes misaligned execution; unconfirmed decisions must be flagged as open questions. |

## Red Flags

- Summaries listing general discussion topics without extracting firm decisions.
- Action items assigned to 'the team' instead of an individual named owner.
- ADRs missing the 'Consequences / Trade-offs' section.
- Glossing over unresolved conflicts or technical disagreements without documenting open items.

## Verification

After completing the workflow, confirm:
- [ ] All extracted decisions follow standard ADR format (Context, Decision, Consequences, Alternatives Considered).
- [ ] Every action item has an individual owner, concrete deliverable, and explicit deadline.
- [ ] Unresolved questions are segregated into a distinct 'Open Items & Blockers' section.
- [ ] Extracted JSON schema validates cleanly against Pydantic models.
