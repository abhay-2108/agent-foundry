---
name: workspace-researcher
description: >-
  Use this skill when tasked with gathering technical, market, competitive, or codebase intelligence.
  Executes structured search across documentation, web resources, and local repositories,
  cross-verifies claims across multiple sources, detects SEO spam, and synthesizes citation-backed briefs.
---

# Workspace Researcher & Technical Intelligence

A rigorous intelligence-gathering and synthesis skill designed to produce high-signal, zero-fluff research reports with traceable citations, cross-verified facts, and hallucination safeguards.

---

## When to Use This Skill

- When investigating external APIs, SDK libraries, dependencies, or open-source packages.
- When conducting competitor analysis, technical vendor evaluations, or architectural benchmarking.
- When surveying large or unfamiliar codebases before proposing significant architectural refactors.
- When cross-checking breaking changes, deprecation timelines, or CVE security advisories.
- Trigger phrases: `"research this library"`, `"compare frameworks"`, `"technical investigation"`, `"find documentation"`, `"evaluate alternatives"`.

---

## Core Principles: The Triangulation Protocol

1. **Source Hierarchy of Truth**:
   - Primary: Official source code (GitHub repo tags, release notes, test files).
   - Secondary: Official documentation & API references.
   - Tertiary: GitHub issues, community discussions, RFCs.
   - Discard: SEO scraper farms, AI-generated content hubs, and unattributed blog posts.
2. **Multi-Source Cross-Verification**: Never assert a performance benchmark, security claim, or API deprecation without corroboration from at least two independent primary sources.
3. **Signal over Volume**: Strip navigation bars, cookie banners, tracking scripts, and marketing filler; preserve only the semantic facts, type signatures, and data tables.

---

## Step-by-Step Execution Workflow

### Step 1: Scoped Query Formulation
- Formulate precise, scoped search queries using advanced operators:
  - Exact API definitions: `"FastAPI" "lifespan" "asynccontextmanager"`
  - Issue hunting: `site:github.com/org/repo in:issues "error message"`
  - Release compatibility: `"PackageA>=2.0" "Python 3.12" breaking changes`

### Step 2: Extraction & Deduplication Pipeline
1. Prefer raw Markdown or structured documentation APIs over rendered web pages.
2. Verify package existence and version directly against registries (PyPI, npm, crates.io).
3. For local codebases, use ripgrep patterns rather than reading unbounded files sequentially:
   ```bash
   rg --type py -n "class.*Strategy" src/
   ```

### Step 3: Synthesis & Report Structure
Format technical findings using this structured markdown brief:

```markdown
# Research Brief: [Topic]

**Date**: YYYY-MM-DD | **Confidence**: High / Medium / Low
**Executive Summary**: 1–2 sentence decisive verdict.

---

## 1. Key Findings & Trade-Off Matrix
| Dimension | Alternative A | Alternative B | Verification Source |
| :--- | :--- | :--- | :--- |
| **Throughput / Latency** | 12,000 req/s | 4,200 req/s | [Benchmark Repo](https://...) |
| **License & Compliance** | MIT | AGPL-3.0 | [LICENSE File](https://...) |
| **Active Maintenance** | 2 days ago | 9 months ago | [GitHub Commits](https://...) |

## 2. Breaking Changes & Deprecation Warnings
- Concrete API changes between major versions.
- Required migration path.

## 3. Real-World Failure Modes & Issue Tracker Insights
- Unresolved issues identified in production deployments:
  - Issue #412: Memory leak during high-concurrency websocket connections.

## 4. Traceable References
1. [Official Repository](https://github.com/org/repo) (Verified commit `3f8a12`)
2. [Official Documentation](https://docs.example.com)
3. Local Codebase Reference: `src/service.py:L45-L60`
```

---

## Anti-Patterns & Traps to Avoid

1. **The SEO Scraper Trap**: Relying on unverified aggregator blogs (e.g., GeeksForGeeks, Medium summaries) that recycle outdated code patterns. Always navigate to the official source repository or official docs.
2. **Anchoring on Stale Documentation**: Quoting code patterns from older library generations (e.g., Pydantic v1 syntax, LangChain 0.0.x chains, React class components) without checking the current major version.
3. **Vendor Benchmark Credulity**: Accepting vendor-published performance benchmarks uncritically. Vendors routinely tune benchmarks to favorable conditions; always look for third-party or reproducible harness results.
4. **Context Window Flooding**: Dumping thousands of lines of unparsed HTML into context. Always distill pages down to core code snippets, schema tables, and release notes before synthesizing.

---

## Quality Checklist

- [ ] Every non-trivial assertion includes a clickable, verified URL or local file path citation.
- [ ] Claims regarding library capabilities match the current major version (verified against registry/repo).
- [ ] Performance and security claims are cross-checked across at least two independent sources.
- [ ] Conflicting viewpoints between marketing claims and actual GitHub issue tracker bugs are explicitly noted.
- [ ] Code snippets extracted from research are syntactically valid and modern.
- [ ] Report includes a clear, decisive executive summary rather than open-ended ambiguity.
