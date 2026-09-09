---
name: knowledge-capture
description: >-
  Use this skill to convert raw meeting transcripts, messy chat threads, brainstorming discussions,
  and ad-hoc notes into structured, searchable knowledge artifacts. Extracts clear decisions,
  assigned action items with deadlines, resolves conflicting viewpoints, and documents ADR rationale.
---

# Knowledge Capture & Meeting Intelligence

Transforms messy, conversational transcripts, Slack/Teams chat threads, and multi-party discussions into actionable, schema-validated knowledge records suitable for Notion, markdown wikis, or project issue trackers.

---

## When to Use This Skill

- When provided with an audio transcription, Zoom/Teams transcript, or raw meeting notes.
- When summarizing multi-turn chat threads or Slack discussions into a definitive decision document.
- When drafting Architectural Decision Records (ADRs), executive readouts, or technical specs from meetings.
- When tasked with extracting concrete action items, assignees, and deadlines from unstructured dialogue.
- Trigger phrases: `"capture meeting notes"`, `"extract action items"`, `"summarize transcript"`, `"document decision"`, `"meeting intelligence"`.

---

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

---

## Anti-Patterns & Traps to Avoid

1. **Passive Voice Assignments**: Writing *"Tests should be implemented by end of week"* without a named individual owner. If everyone is responsible, no one is responsible.
2. **Hallucinating Consensus**: Treating casual comments (*"We could perhaps try Rust"*) as binding team decisions. Only extract decisions that had explicit agreement from decision-makers.
3. **Omitting the Rationale**: Recording *what* was chosen without *why*. Without the rationale, teams inevitably repeat the same debate 3 months later when context fades.
4. **Vague Numerical Generalization**: Replacing concrete metrics mentioned in speech with vague adjectives (e.g., changing *"reduce latency from 450ms to under 100ms"* into *"improve system speed"*). Always capture exact figures.

---

## Quality Checklist

- [ ] Every action item has a single named owner (no anonymous or shared tasks).
- [ ] Action items specify a concrete deliverable and an explicit deadline where discussed.
- [ ] Rationale and rejected alternatives are preserved for every major decision.
- [ ] Numerical targets, dates, and technical identifiers are recorded verbatim.
- [ ] Unresolved disputes and parking lot items are explicitly distinguished from binding agreements.
- [ ] Output conforms to clean, copy-pasteable markdown ready for team wikis or tickets.
