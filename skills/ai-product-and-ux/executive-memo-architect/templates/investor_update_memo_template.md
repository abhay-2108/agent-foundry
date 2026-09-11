# Monthly / Quarterly Investor & Board Update Memo

**Company**: [Company Name]  
**Period**: [e.g. Q2 2026 / August 2026]  
**Prepared By**: [Founder / CEO Name]  
**Date**: [Date]  

---

## 1. Executive Summary (The TL;DR)
*3-4 sentences summarizing macro business performance, milestone delivery, and current trajectory.*

In [Quarter/Month], [Company] reached **$[MRR]k MRR** (+[X]% MoM), driven by strong expansion within our enterprise cohort. We successfully closed our SOC 2 Type II audit, enabling us to sign 3 Fortune 500 contracts. Cash runway stands at **[X] months**, with a net burn of **$[Amount]k/month**.

---

## 2. Core Scorecard & Financial KPIs

| Metric | Current Value | Previous Period | MoM / QoQ Delta | Target Goal |
| :--- | :--- | :--- | :--- | :--- |
| **Monthly Recurring Revenue (MRR)** | $[Value]k | $[Value]k | +[X]% | $[Target]k |
| **Annual Recurring Revenue (ARR)** | $[Value]M | $[Value]M | +[X]% | $[Target]M |
| **Gross Margin** | [X]% | [X]% | +[X] bps | > 80% |
| **Net Revenue Retention (NRR)** | [X]% | [X]% | +[X]% | > 120% |
| **Customer Acquisition Cost (CAC)** | $[Value] | $[Value] | -[X]% | < $[Target] |
| **Gross Cash Burn (Monthly)** | $[Value]k | $[Value]k | -$[X]k | < $[Target]k |
| **Cash in Bank** | $[Value]M | $[Value]M | -$[X]k | N/A |
| **Runway (Months)** | [X] months | [X] months | -[X] mo | > 18 months |

---

## 3. Key Highlights (What Went Well)
- **Revenue & Pipeline**: [Specific contract wins, ACV expansion, closed deals with names and contract values].
- **Product & Engineering**: [Shipped major capabilities, latency reductions, infrastructure optimizations].
- **Team & Recruiting**: [Key leadership hires: VP of Engineering, Head of Sales].

---

## 4. Lowlights & Headwinds (Where We Missed & Corrective Actions)
*Be candid and transparent. Every lowlight must include root-cause analysis and immediate remedy.*

- **Lowlight 1: Missed Self-Serve Conversion Target (1.2% vs. 2.0% Goal)**:
  - *Root Cause*: Onboarding drop-off occurred at the API key generation step due to complex OAuth permission scopes.
  - *Remediation*: Deployed simplified 1-click GitHub auth flow on August 12; early cohort data shows conversion rebounding to 1.85%.
- **Lowlight 2: Churn of Mid-Market Account ($2,400 MRR)**:
  - *Root Cause*: Customer experienced database migration timeout during peak business hours.
  - *Remediation*: Implemented zero-downtime blue/green migration pipelines with automated health check rollbacks.

---

## 5. Strategic Priorities for Next Period
1. **Priority 1 (Revenue)**: Close 4 late-stage enterprise POCs representing $180k in incremental ARR.
2. **Priority 2 (Product)**: Launch self-serve vector database indexing and SOC 2 automated audit dashboards.
3. **Priority 3 (Hiring)**: Hire 2 Senior Distributed Systems Engineers and 1 Account Executive.

---

## 6. The Asks (How Investors & Advisors Can Help)
- **Enterprise Introductions**: We are seeking introductions to Heads of Data / VP of Infrastructure at companies scaling beyond 10M events/day.
- **Talent Referrals**: Looking for a Staff Kafka / Distributed Systems Engineer. Job description link: `[URL]`.
- **Customer Feedback**: If any portfolio company is currently adopting pgvector or Qdrant, we'd love 15 minutes to demo our automated index tuning toolkit.
