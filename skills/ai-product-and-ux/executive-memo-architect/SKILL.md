---
name: executive-memo-architect
description: >-
  Use this skill when drafting, auditing, or structuring high-stakes executive documents, Amazon-style
  6-page narrative memos, startup investor update briefs, board meeting decks, and formal business
  case justifications. Enforces high metric density, active voice, elimination of corporate weasel words,
  and rigorous "So What?" financial framing.
---

# Executive Memo Architect & Strategic Business Communication

Acts as a Chief of Staff & Senior VP of Strategy. Transforms ambiguous ideas, technical architectures, and strategic proposals into clear, decision-ready narrative memos. Strictly adheres to the **Amazon 6-Page Narrative Methodology**, enforces uncompromising quantitative rigor, eliminates passive hand-waving, and prepares leadership teams to make multi-million dollar capital and engineering decisions in a single sitting.

---

## When to Use This Skill

- When drafting Amazon-style 6-Page Narrative Memos or 2-Page Executive Summaries.
- When authoring formal Business Cases, Capex/Opex justifications, and ROI analyses.
- When writing monthly/quarterly Investor Updates or Board Meeting briefings.
- When pitching new product initiatives, platform refactors, or infrastructure investments to C-level executives.
- When auditing draft proposals for vague hand-waving, low metric density, and corporate jargon.
- Trigger phrases: `"write 6-page memo"`, `"executive pitch deck"`, `"author business case"`, `"investor update memo"`, `"board briefing"`, `"amazon memo format"`, `"business case justification"`, `"strategy memo"`.

---

## The 6-Page Narrative Architecture (Amazon Methodology)

PowerPoint slides hide shallow thinking behind bullet points. Narrative memos force deep clarity of thought:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Amazon 6-Page Narrative Memo Structure               │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Context & Business Problem  │ 2. Guiding Principles & Tenets        │
│ (Current State, Pain, Urgency) │ (Non-Negotiable Decision Heuristics)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Proposed Strategic Solution │ 4. Execution Plan & Milestones        │
│ (Architecture, UX, Capabilities│ (Phasing, Staffing, RACI, Timelines)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. Financials, ROI & KPIs      │ 6. Strategic FAQs & Counter-Arguments │
│ (Capex/Opex, Payback, Margins) │ (Addressing Top 10 Hard Objections)   │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## Core Tenets of Executive Writing

### 1. The "So What?" Rule & Metric Density
Every paragraph must answer the executive's unstated question: *"So what? Why does this matter to our customers, margins, or growth?"*
- ❌ **Vague**: *"We have experienced significant database downtime, which frustrated many users."*
- ✅ **Quantified**: *"Over the last 90 days, 14 unplanned database outages caused 218 minutes of downtime, resulting in 4,120 dropped checkout transactions and an estimated $86,400 in lost gross merchandise value (GMV)."*

### 2. Elimination of Corporate Weasel Words
Never use empty buzzwords that mask a lack of data. The companion toolkit will flag these terms:
- 🚫 *Seamlessly, revolutionary, game-changing, best-in-class, synergize, drive value, state-of-the-art, paradigm shift, holistic.*

### 3. Active Voice & Direct Accountability
Always specify **who** is doing **what**, by **when**:
- ❌ **Passive**: *"It was decided that the legacy cluster will be decommissioned in Q2."*
- ✅ **Active**: *"The Site Reliability Engineering team, led by Sarah Jenkins, will decommission the legacy Elasticsearch cluster by May 15, saving $14,200/month in cloud infrastructure spend."*

### 4. Tenets: Principles with Teeth
Tenets are not motherhood-and-apple-pie truisms like *"we value quality"*. Tenets are hard trade-offs that guide difficult decisions when two good values compete:
- *"Customer Trust over Short-Term Velocity: We will delay release dates rather than ship features without automated end-to-end regression tests."*
- *"Simplicity over Configurability: We offer 3 opinionated defaults rather than 40 dials."*

---

## Document Archetypes

### Archetype 1: The Amazon 6-Page Narrative Memo
Used for major product launches, platform migrations, or corporate strategy. Read in complete silence for 20 minutes at the start of the executive meeting before any discussion begins.
- Structure: Context $\rightarrow$ Tenets $\rightarrow$ Proposed State $\rightarrow$ Execution $\rightarrow$ Financials $\rightarrow$ FAQs.

---

## Canonical 6-Page Narrative Memo Template

Use this comprehensive markdown template when drafting formal 6-page decision memos:

```markdown
# [Project / Strategic Initiative Title]: 6-Page Narrative Memo

**Author(s)**: [Author Name & Title]  
**Date**: [YYYY-MM-DD]  
**Target Decision Date**: [YYYY-MM-DD]  
**Executive Sponsors**: [VP / Director Name]  
**Target Decision Requested**: [e.g., Approval of $420,000 Capex & 4 Full-Time Engineers for H2 Platform Refactor]

---

### Section 1: Context & Problem Statement
*Describe the current state, customer pain points, market headwinds, and why action is required now. Enforce high metric density.*

Over the past four quarters, our core analytics processing pipeline has experienced severe scaling bottlenecks as daily ingestion volume grew from 12M events/day to 84M events/day (+600%). In Q2 alone, these bottlenecks caused 18 customer-facing SLA breaches (P99 query latency exceeding 4,500ms vs. target 500ms), resulting in the churn of 3 enterprise accounts representing $185,000 in Annual Recurring Revenue (ARR). If unaddressed, projected customer growth in Q4 will cause catastrophic database connection saturation during peak trading hours (09:30–11:00 EST).

---

### Section 2: Guiding Tenets & Decision Principles
*Define 3 to 5 non-negotiable principles with teeth that resolve competing priorities.*

1. **Customer Latency over Infinite Flexibility**: We will reject features that compromise sub-500ms P99 query latency, regardless of customer request volume.
2. **Deterministic Reproducibility over Opaque Black Boxes**: Every data transformation must be 100% reproducible via idempotent DAG pipelines with automated lineage tracking.
3. **Decoupled Storage and Compute**: Compute resources must autoscale independently from persistent storage to prevent over-provisioning spend during off-peak hours.
4. **Automated Quality Gates over Manual Signoffs**: Code and schema migrations must pass automated regression and load testing before merging.

---

### Section 3: Proposed Strategic Solution
*Detail the architecture, system interactions, capabilities, and customer experience of the future state.*

We propose migrating from the monolithic PostgreSQL analytics instance to an event-driven Lakehouse architecture utilizing Apache Kafka for ingestion, ClickHouse for high-concurrency real-time OLAP querying, and Amazon S3 with Apache Iceberg for cold historical storage.

| Architecture Component | Current Monolithic State | Proposed Lakehouse Architecture | Expected Impact |
|:---|:---|:---|:---|
| **Ingestion Ingress** | Synchronous REST write to Postgres | Kafka partitioned event topics | Ingestion capacity: 84M $\rightarrow$ 500M events/day |
| **Analytical Query Engine** | Postgres B-tree index scans | ClickHouse columnar vector engine | P99 latency: 4,500ms $\rightarrow$ 180ms (-96%) |
| **Historical Storage Tier** | High-performance EBS volumes ($0.12/GB/mo) | S3 Glacier Flexible ($0.0036/GB/mo) | Storage cost reduction: 70% |

---

### Section 4: Execution Plan, Phasing & RACI
*Break execution into chronological phases with verifiable milestones, deliverables, and ownership.*

- **Phase 1: Foundation & Proof-of-Concept (Weeks 1–4)**
  - Milestone 1.1: Deploy 3-node ClickHouse test cluster via Terraform.
  - Milestone 1.2: Establish dual-writing pipeline from Kafka to Postgres & ClickHouse.
- **Phase 2: Shadow Ingestion & Verification (Weeks 5–8)**
  - Milestone 2.1: Execute 30-day data consistency reconciliation between Postgres and ClickHouse.
  - Milestone 2.2: Pass automated load test at $2\times$ projected peak load (20,000 writes/sec).
- **Phase 3: Production Cutover & Decommission (Weeks 9–12)**
  - Milestone 3.1: Route read-traffic from dashboard analytics to ClickHouse cluster.
  - Milestone 3.2: Decommission legacy Postgres read replicas; archive snapshot to S3.

**RACI Matrix**:
- **Responsible**: Platform Data Engineering Lead (`@fullstack-engineer`)
- **Accountable**: VP of Engineering
- **Consulted**: Security Lead (`@security-red-teamer`), SRE Lead (`@sre-devops-guardian`)
- **Informed**: Product Management & Customer Success

---

### Section 5: Financial Justification, ROI & Metrics Scorecard
*Detail Capex, Opex, headcount requirements, payback period, and business KPIs.*

```
Investment Breakdown:
- Infrastructure Capex (Staging & migration environments): $45,000
- 12-Month Cloud Opex (Kafka MSK + ClickHouse Cloud):      $185,000
- Engineering Resource Allocation (4 FTEs for 12 weeks):    $190,000
Total Investment:                                          $420,000

Financial Return & Savings:
- Legacy Database License & High-IOPS EBS Decommission:    -$160,000/year
- Reduced Enterprise Churn (Preserved ARR):                 +$240,000/year
- Net Annual Financial Benefit:                            +$240,000/year
- Payback Period:                                          14.2 months
```

---

### Section 6: Strategic FAQs & Hard Counter-Arguments
*Address the 5–10 hardest questions leadership will ask.*

**Q1: Why ClickHouse rather than Snowflake or Google BigQuery?**  
*Answer*: Snowflake and BigQuery charge on per-query scanned data. At our query volume (14M user queries/month), Snowflake estimated cost exceeds $38,000/month. ClickHouse fixed-instance clustering delivers sub-200ms latency at $11,500/month flat spend.

**Q2: What is the fallback plan if ClickHouse migration encounters data corruption during Week 7?**  
*Answer*: Dual-writing to PostgreSQL remains active throughout Phases 1 and 2. Cutover only occurs after 30 consecutive days of zero discrepancies verified by automated checksum audits. If corruption occurs, read-traffic remains anchored to PostgreSQL.

**Q3: Can current engineering staff maintain ClickHouse, or does this require new hiring?**  
*Answer*: Two senior backend engineers completed ClickHouse DBA certification in Q1. Furthermore, we are adopting managed ClickHouse Cloud for automated backups, HA failover, and OS patching.
```

---

### Archetype 2: The Investor & Board Update Memo
Used for monthly or quarterly updates to venture capitalists, board members, and executive committees:
1. **Executive Summary**: 3 sentences capturing macro performance.
2. **Core North Star KPIs**: MRR, Gross Margin, Net Retention Rate (NDR), Burn Multiple, Cash Runway (months).
3. **Highlights & Lowlights**: Honest transparency; lowlights must include root-cause analysis and corrective actions.
4. **The Asks**: Specific introductions, regulatory connections, or hiring assistance requested.

---

## Anti-Patterns & Hard Guardrails

- 🚫 **Never use bullet-point slides where narrative paragraphs are needed**: Bullet points allow writers to skate over logical gaps; full sentences expose flaws.
- 🚫 **Never bury bad news**: Executives respect honesty and despise surprises. Place lowlights and missed targets right after the KPI scorecard, paired with immediate remediation plans.
- 🚫 **Never omit the Financial Justification**: An engineering proposal without cost estimates (headcount, cloud spend, payback period) is incomplete.
- 🚫 **Never write soft FAQs**: FAQs must not be softball marketing questions. Address the hardest questions: *"Why not buy vendor X?", "What happens if adoption is only 10% of forecast?"*

---

## Verification & CLI Tooling

Use the companion script [`memo_audit_toolkit.py`](./scripts/memo_audit_toolkit.py) to audit draft memos for metric density, detect weasel words, and verify structural compliance:

```bash
# Run self-test suite
python skills/ai-product-and-ux/executive-memo-architect/scripts/memo_audit_toolkit.py --test

# Audit an executive memo markdown file
python skills/ai-product-and-ux/executive-memo-architect/scripts/memo_audit_toolkit.py audit --file memo.md
```
