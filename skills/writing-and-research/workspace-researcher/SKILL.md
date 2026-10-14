---
name: workspace-researcher
description: >-
  Use this skill when tasked with gathering technical, market, competitive, or codebase intelligence.
  Executes structured search across documentation, web resources, and local repositories,
  cross-verifies claims across multiple sources, detects SEO spam, and synthesizes citation-backed briefs.
---

# Workspace Researcher & Technical Intelligence

## Overview

Conducts structured codebase and multi-source web intelligence gathering. Cross-verifies technical claims across official documentation, GitHub repositories, and package registries, detects SEO spam, and synthesizes citation-backed research briefs.

## When to Use

- When investigating external APIs, SDK libraries, dependencies, or open-source packages.
- When conducting competitor analysis, technical vendor evaluations, or architectural benchmarking.
- When surveying large or unfamiliar codebases before proposing significant architectural refactors.
- When cross-checking breaking changes, deprecation timelines, or CVE security advisories.
- Trigger phrases: `"research this library"`, `"compare frameworks"`, `"technical investigation"`, `"find documentation"`, `"evaluate alternatives"`.

---
- **When NOT to use**: Writing code implementation PRs (use `fullstack-engineer`) or formal Amazon-style 6-page strategy memos (use `executive-memo-architect`).

## Core Process & Research Triangulation

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"The first search result snippet is accurate enough for technical facts."* | First-page SEO spam blogs frequently copy outdated or hallucinated code; always verify against primary source repositories or official docs. |
| *"We can cite secondary Medium articles instead of official documentation."* | Secondary blog posts go stale; technical briefs must cite official API specs, changelogs, or verified commit hashes. |
| *"One source is sufficient if it comes from an established website."* | Critical architectural trade-offs require triangulation across at least two independent sources or active benchmarks. |
| *"Code search across the local repo isn't needed if we remember the file."* | Memory is lossy; ripgrep or semantic search ensures all call sites and edge-case usages are accounted for. |

## Red Flags

- Citing deprecated API methods or abandoned repositories (last commit > 2 years ago).
- Presenting performance claims without citing reproducible benchmark environments and metrics.
- Research summaries lacking clickable markdown file links (`[file.py](file:///path)`) to local evidence.
- Uncritical acceptance of vendor marketing claims without independent engineering evaluation.

## Verification

After completing the workflow, confirm:
- [ ] All external claims are grounded in official documentation or GitHub source repositories.
- [ ] Local codebase claims include verified line references (`file://...#L10-L25`).
- [ ] Technical comparisons contrast at least two alternative approaches with explicit trade-off matrices.
- [ ] Research brief is structured with Executive Summary, Findings, Trade-off Matrix, and Recommendations.
