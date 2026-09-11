---
name: agentic-ui-patterns
description: >-
  Use this skill when designing, building, or refining AI user interfaces, agentic chat applications,
  and human-in-the-loop frontend workflows. Covers token streaming components, unclosed markdown
  fence repair, collapsible reasoning accordions, generative UI component cards, and interactive diff
  review drawers.
---

# Agentic UI Patterns & Modern AI Frontend UX

Acts as a Principal AI Product Designer & Full-Stack Frontend Architect. Specializes in modern agentic human-computer interaction (HCI), token streaming pipelines, generative UI component hydration, and human-in-the-loop governance interfaces. Eliminates jarring UI glitches, minimizes cognitive overload during long reasoning runs, and designs interfaces that build trust between users and autonomous agents.

---

## When to Use This Skill

- When designing or building AI chat interfaces, copilots, or autonomous agent dashboards.
- When implementing token streaming (SSE / WebSockets) with smooth rendering and markdown stream repair.
- When rendering collapsible chain-of-thought (`<thought>`) reasoning accordions and live tool execution steppers.
- When building Generative UI cards (rendering dynamic interactive widgets from agent JSON payloads mid-chat).
- When implementing Human-in-the-loop Diff Review Drawers (side-by-side file diffs, approve/reject/modify actions).
- When designing optimistic UI updates and interruptible agent controls ("Stop Generating", "Rollback").
- Trigger phrases: `"design agent chat UI"`, `"streaming UI components"`, `"generative UI cards"`, `"diff review drawer"`, `"thought dropdown"`, `"agent tool execution ui"`, `"human approval drawer"`, `"agentic frontend"`.

---

## The 5 Core Agentic UI Patterns

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Agentic Frontend Interaction UX                   │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Token Stream & Fence Repair │ 2. Reasoning Accordion (<thought>)    │
│ (Glitch-Free Streaming Parser) │ (Auto-Collapsing Pulsing CoT Pill)    │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Generative UI Cards         │ 4. Diff Review & Approval Drawer      │
│ (Dynamic Interactive Widgets)  │ (Side-by-Side Unified Code Diffs)     │
├────────────────────────────────┴───────────────────────────────────────┤
│ 5. Tool Steppers & Optimistic Interruptibility (Cancel, Rollback)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Pattern 1: Token Streaming & Markdown Stream Repair

### The Streaming Glitch Problem
When an LLM streams tokens word-by-word via Server-Sent Events (SSE), markdown formatters crash or flicker when parsing unclosed elements (e.g. ```` ```python \n def foo(): ```` before the closing triple backticks arrive).

### The Solution: Partial Stream Buffer & Auto-Closure
Before passing the streamed buffer into a markdown renderer, run a lightweight repair regex that temporarily appends missing closing tags:
1. Count unclosed code fences (```` ``` ````): if odd, append `\n```\n`.
2. Count unclosed asterisks (`**` or `*`): balance odd counts.
3. Suppress raw HTML tags until matching closing brackets arrive.

```typescript
export function repairStreamingMarkdown(rawBuffer: string): string {
  let repaired = rawBuffer;
  
  // Count occurrences of triple backticks
  const codeFences = (repaired.match(/```/g) || []).length;
  if (codeFences % 2 !== 0) {
    repaired += "\n```";
  }
  
  // Balance unclosed bold delimiters
  const boldMarkers = (repaired.match(/\*\*/g) || []).length;
  if (boldMarkers % 2 !== 0) {
    repaired += "**";
  }
  
  return repaired;
}
```

---

## Pattern 2: Collapsible Chain-of-Thought (Reasoning Accordions)

Long reasoning outputs (e.g., deep thinking models, plan generation) overwhelm the user if rendered as plain text.

### Implementation Blueprint
1. Extract `<thought>...</thought>` or `<reasoning>...</reasoning>` blocks from the streaming token stream.
2. Render as a compact status element:
   - **While thinking**: Display a subtle pulsing indicator: `✦ Thinking (3.2s)...`
   - **Upon completion**: Auto-collapse into an accordion pill: `✦ Thought process (18 lines) ▼`
3. The user can expand the accordion at any time to inspect the chain-of-thought, but the primary view focuses cleanly on the agent's final answer.

---

## Pattern 3: Generative UI (Dynamic JSON Component Cards)

Rather than forcing the user to read raw text tables or markdown, the agent emits structured JSON tool calls that hydrate into interactive React/Vue/vanilla widgets:

### Component Payload Contract
```json
{
  "ui_component": "kpi_metric_card",
  "props": {
    "title": "Monthly Recurring Revenue",
    "value": "$142,500",
    "change_percentage": 18.4,
    "trend": "up",
    "cta_label": "View Cohort Breakdown",
    "action_id": "open_mrr_cohorts"
  }
}
```

### Dynamic Dispatcher
The frontend maps `ui_component` to a registered component registry:
```javascript
const COMPONENT_REGISTRY = {
  kpi_metric_card: RenderMetricCard,
  sql_result_table: RenderInteractiveGrid,
  confirmation_dialog: RenderActionForm,
  diff_viewer: RenderDiffDrawer
};
```

---

## Pattern 4: Human-in-the-Loop Diff Review Drawer

When an agent proposes file modifications, database mutations, or config edits, never apply them silently. Present a slide-out drawer with side-by-side or unified diffs:

### UX Requirements
1. **File Selector Tabs**: Navigate multi-file diffs cleanly.
2. **Syntax Highlighting & Color Coding**: Green for additions (`+`), red for deletions (`-`).
3. **Granular Controls**:
   - `[Approve All]`: Executes file writes immediately.
   - `[Reject]`: Dismisses suggestions with optional feedback comment.
   - `[Approve Selected Lines]`: Selectively cherry-picks chunks.
4. **Optimistic Feedback**: Display reversible undo toasts (`"3 files modified. Undo (10s)"`).

---

## Pattern 5: Tool Steppers & Execution Indicators

Provide visual transparency while the agent runs background workflows:
- Display an animated vertical stepper for active tool calls:
  - `✓ Search codebase for 'auth_service' (0.4s)`
  - `✓ Read file 'src/auth/jwt.py' (0.1s)`
  - `● Running test suite: pytest tests/ (running...)`
---

## Production Streaming Component Recipes

### Recipe 1: High-Performance Token Streaming Hook (React / TypeScript)
Prevents DOM thrashing by throttling token re-renders using `requestAnimationFrame`:

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { repairStreamingMarkdown } from './markdownUtils';

export function useThrottledTokenStream(streamUrl: string) {
  const [content, setContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const bufferRef = useRef('');
  const rafIdRef = useRef<number | null>(null);

  const startStreaming = async (prompt: string) => {
    setIsStreaming(true);
    bufferRef.current = '';
    const abortController = new AbortController();

    const response = await fetch(streamUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
      signal: abortController.signal
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    const flushBuffer = () => {
      setContent(repairStreamingMarkdown(bufferRef.current));
      rafIdRef.current = null;
    };

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      bufferRef.current += decoder.decode(value, { stream: true });
      if (!rafIdRef.current) {
        rafIdRef.current = requestAnimationFrame(flushBuffer);
      }
    }
    flushBuffer();
    setIsStreaming(false);
  };

  return { content, isStreaming, startStreaming };
}
```

### Recipe 2: Collapsible Thought Process Component (`<ThoughtAccordion />`)
```tsx
export function ThoughtAccordion({ thoughts, isThinking }: { thoughts: string; isThinking: boolean }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!thoughts && !isThinking) return null;

  return (
    <div className="thought-container border-l-2 border-indigo-500/40 bg-indigo-950/20 rounded-r-lg my-2 text-xs">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 w-full text-left text-indigo-300 hover:text-indigo-100 transition-colors"
      >
        <span className={`inline-block w-2 h-2 rounded-full ${isThinking ? 'bg-indigo-400 animate-pulse' : 'bg-emerald-400'}`} />
        <span className="font-mono font-medium">
          {isThinking ? 'Thinking in progress...' : `Thought process (${thoughts.split('\\n').length} lines)`}
        </span>
        <span className="ml-auto font-mono text-neutral-400">{isOpen ? '▲ Hide' : '▼ View'}</span>
      </button>
      {isOpen && (
        <div className="px-3 pb-2 text-neutral-300 font-mono text-xs whitespace-pre-wrap border-t border-indigo-900/30 pt-2">
          {thoughts}
        </div>
      )}
    </div>
  );
}
```

### Recipe 3: Live Tool Execution Stepper Component
```tsx
interface ToolExecution {
  id: string;
  name: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  durationMs?: number;
}

export function ToolExecutionStepper({ steps }: { steps: ToolExecution[] }) {
  return (
    <div className="flex flex-col gap-1.5 my-3 pl-2 border-l-2 border-neutral-700">
      {steps.map((step) => (
        <div key={step.id} className="flex items-center gap-2 font-mono text-xs text-neutral-400">
          {step.status === 'RUNNING' && <span className="animate-spin text-cyan-400">◌</span>}
          {step.status === 'COMPLETED' && <span className="text-emerald-400">✓</span>}
          {step.status === 'FAILED' && <span className="text-rose-400">✗</span>}
          <span className="text-neutral-200">{step.name}</span>
          {step.durationMs && <span className="text-neutral-500">({(step.durationMs / 1000).toFixed(2)}s)</span>}
        </div>
      ))}
    </div>
  );
}
```

---

## Anti-Patterns & Hard Guardrails

- 🚫 **Never re-render the entire chat transcript on every token**: Token streams emit 30–80 times per second. Re-rendering the full message list causes severe DOM thrashing and lag. Only update the active message node.
- 🚫 **Never display raw unparsed JSON payloads in chat bubbles**: If the model emits structured tool arguments, render a styled component or collapsible disclosure.
- 🚫 **Never block the chat input during streaming without a stop button**: Users frequently notice mistakes early; always allow immediate cancellation.
- 🚫 **Never mutate external state without a human checkpoint**: Destructive actions (deletes, writes, external API calls) must route through an explicit confirmation card or diff drawer.

---

## Verification & CLI Tooling

Use the companion script [`agentic_ui_toolkit.py`](./scripts/agentic_ui_toolkit.py) to test stream fence repairs, validate Generative UI schemas, and extract thought blocks:

```bash
# Run self-test suite
python skills/ai-product-and-ux/agentic-ui-patterns/scripts/agentic_ui_toolkit.py --test

# Repair partial streaming markdown
python skills/ai-product-and-ux/agentic-ui-patterns/scripts/agentic_ui_toolkit.py repair-stream --text "Here is the code:\n\`\`\`python\ndef add(a, b):\n    return a + b"
```
