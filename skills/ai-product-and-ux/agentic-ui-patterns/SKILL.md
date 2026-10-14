---
name: agentic-ui-patterns
description: >-
  Use this skill when designing, building, or refining AI user interfaces, agentic chat applications,
  and human-in-the-loop frontend workflows. Covers token streaming components, unclosed markdown
  fence repair, collapsible reasoning accordions, generative UI component cards, and interactive diff
  review drawers.
---

# Agentic UI Patterns & Modern AI Frontend UX

## Overview

Acts as a Principal AI Product Designer & Full-Stack Frontend Architect. Specializes in modern agentic human-computer interaction (HCI), token streaming pipelines, generative UI component hydration, and human-in-the-loop governance interfaces. Eliminates jarring UI glitches, minimizes cognitive overload during long reasoning runs, and designs interfaces that build trust between users and autonomous agents.

## When to Use

- When designing or building AI chat interfaces, copilots, or autonomous agent dashboards.
- When implementing token streaming (SSE / WebSockets) with smooth rendering and markdown stream repair.
- When rendering collapsible chain-of-thought (`<thought>`) reasoning accordions and live tool execution steppers.
- When building Generative UI cards (rendering dynamic interactive widgets from agent JSON payloads mid-chat).
- When implementing Human-in-the-loop Diff Review Drawers (side-by-side file diffs, approve/reject/modify actions).
- When designing optimistic UI updates and interruptible agent controls ("Stop Generating", "Rollback").
- Trigger phrases: `"stream markdown in UI"`, `"agent reasoning accordion"`, `"generative UI cards"`, `"diff review drawer"`, `"agent chat interface"`, `"token streaming smooth rendering"`.
- **When NOT to use**: Pure backend API contract design without UI (use `backend-architecture`), or generic design system tokens without agent/streaming state (use `frontend-design`).

## Core Process & UI Patterns

### The 5 Core Agentic UI Patterns

#### Pattern 1: Token Streaming & Markdown Stream Repair
Token streams arrive as partial chunks, frequently cutting off inside markdown delimiters (e.g. ` ```pyth `, ` **bold `). Naive markdown parsers glitch or corrupt layout until the fence closes.
- Maintain a stream repair buffer using `repairPartialMarkdown(chunk)`.
- Auto-close dangling code blocks, italic tags, and incomplete link brackets before handing chunks to React/DOM renderers.

#### Pattern 2: Collapsible Chain-of-Thought (Reasoning Accordions)
Deep reasoning models emit thousands of tokens of internal deliberation (`<thought>` tags).
- Parse `<thought>` blocks out of the primary message stream.
- Render reasoning in a collapsible accordion, collapsed by default with an elapsed execution timer.
- Display animated micro-indicators during generation and summary statistics on completion.

#### Pattern 3: Generative UI (Dynamic JSON Component Cards)
Instead of textual lists or raw JSON, hydrate structured agent responses into interactive UI widgets.
- Define a typed component registry matching agent tool payloads (`ArtifactCard`, `MetricComparison`, `ApprovalForm`).
- Hydrate components lazily with loading skeletons.

#### Pattern 4: Human-in-the-Loop Diff Review Drawers
When agents propose code, file, or configuration changes, present side-by-side unified diffs.
- Provide clear granular actions: "Accept Diff", "Reject", or "Edit Inline".
- Disallow state mutations until human approval is signaled.

#### Pattern 5: Live Tool Execution Stepper
Visualize multi-step agent DAGs with status indicators (RUNNING, COMPLETED, FAILED) and per-step duration badges.

```tsx
export function ToolExecutionStepper({ steps }: { steps: ToolExecution[] }) {
  return (
    <div className="flex flex-col gap-1.5 my-3 pl-2 border-l-2 border-neutral-700">
      {steps.map((step) => (
        <div key={step.id} className="flex items-center gap-2 font-mono text-xs text-neutral-400">
          {step.status === 'RUNNING' && <span className="animate-spin text-cyan-400">◐</span>}
          {step.status === 'COMPLETED' && <span className="text-emerald-400">✓</span>}
          {step.status === 'FAILED' && <span className="text-rose-400">✕</span>}
          <span className="text-neutral-200">{step.name}</span>
          {step.durationMs && <span className="text-neutral-500">({(step.durationMs / 1000).toFixed(2)}s)</span>}
        </div>
      ))}
    </div>
  );
}
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"We can just wait until the entire response finishes instead of streaming."* | For multi-step agent reasoning, waiting 15–30s with a dead spinner creates massive perceived latency and causes users to abandon sessions. |
| *"Unclosed markdown fences during streaming don't matter because it closes at the end."* | While streaming, an unclosed ` ``` ` turns the entire rest of the chat window into code block styling until completion. |
| *"Showing raw tool JSON is fine for technical users."* | Technical users experience cognitive fatigue parsing 200-line JSON dumps; interactive structured cards enable instant verification. |
| *"A 'Stop Generating' button isn't needed for quick queries."* | When an autonomous agent enters a runaway loop or hallucinates, the inability to cancel burns API tokens and erodes user trust. |

## Red Flags

- Re-rendering the entire chat transcript on every token chunk (causes 60fps DOM thrashing; only the active message node should update).
- Displaying raw, unstyled JSON payloads or stack traces directly in user-facing message bubbles.
- Blocking the chat input or UI thread during tool execution without an abort/cancel mechanism.
- Mutating external file or database state without routing through an explicit confirmation card or diff drawer.

## Verification

After completing the UI workflow, confirm:
- [ ] Markdown stream repair correctly closes trailing code blocks, bold text, and backticks without layout jitter.
- [ ] Reasoning chains (`<thought>` tags) are parsed into collapsible accordions with duration badges.
- [ ] Destructive actions present interactive diff drawers with Approve / Reject / Edit buttons.
- [ ] Companion test suite passes: `python skills/ai-product-and-ux/agentic-ui-patterns/scripts/agentic_ui_toolkit.py --test`.
