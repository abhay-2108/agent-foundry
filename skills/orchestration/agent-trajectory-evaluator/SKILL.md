---
name: agent-trajectory-evaluator
description: >-
  Use this skill when auditing, benchmarking, or optimizing autonomous agent execution trajectories.
  Analyzes tool call sequences, detects redundant loops, flags reasoning thrashing,
  and scores step-level efficiency rather than just the final conversational output.
---

# Agent Trajectory Evaluator & Step Auditor

## Overview

Audits, benchmarks, and optimizes autonomous agent tool execution trajectories. Analyzes tool call sequences, detects redundant loops, flags reasoning thrashing, and scores step-level efficiency rather than just the final conversational output.

## When to Use

- When an agent arrives at the correct final answer, but took 15 tool calls when it only needed 2.
- When diagnosing agent thrashing (calling the same search tool repeatedly with minor query variations).
- When benchmarking autonomous coding agents, customer support bots, or research crawlers.
- When optimizing agent runtime latency and token costs across multi-step execution graphs.
- Trigger phrases: `"evaluate trajectory"`, `"audit tool calls"`, `"agent efficiency"`, `"step-level evaluation"`, `"debug agent loop"`.

---
- **When NOT to use**: Evaluating single-turn prompt output text quality (use `llm-evals-engineer`).

## Core Process & Trajectory Audit Methodology

## The Trajectory Diagnostic Matrix

```
┌────────────────────────────────────────────────────────┐
│               Trajectory Evaluation Dimensions         │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Path      │ 2. Tool Call │ 3. Argument │ 4. Loop    │
│    Directness│    Precision │    Accuracy │    Defense │
└──────────────┴──────────────┴─────────────┴────────────┘
```

1. **Path Directness**: Ratio of essential steps vs. superfluous exploration steps ($E = \frac{\text{Optimal Steps}}{\text{Actual Steps}}$).
2. **Tool Call Precision**: Did the agent select the most specific tool available, or did it fumble with generic fallback tools?
3. **Argument Accuracy**: Were tool call arguments well-formed on the first attempt, or did the agent trigger multiple error-retry cycles?
4. **Loop & Thrashing Defense**: Did the agent recognize when a strategy wasn't working and pivot, or did it get trapped in repetitive retry loops?

---

## Step-by-Step Trajectory Audit Workflow

### Step 1: Ingest the Execution Trace
Extract the sequence of events from the agent trajectory log:
```json
[
  {"step": 1, "thought": "Need to check open ports", "tool": "run_command", "args": "netstat -ano", "status": "success"},
  {"step": 2, "thought": "Let me run it again", "tool": "run_command", "args": "netstat -ano", "status": "redundant"},
  {"step": 3, "thought": "Kill process", "tool": "kill_process", "args": "pid=8080", "status": "success"}
]
```

### Step 2: Calculate Trajectory Efficiency Metrics
- **Step Count**: Total steps executed ($N$).
- **Redundancy Rate**: Percentage of tool calls that returned identical data or duplicate queries.
- **Error-Recovery Rate**: Steps required to recover from a failed tool call.

### Step 3: Trajectory Scoring Rubric
Score the execution trace on a 1–5 scale:
- **5 (Optimal)**: Minimal direct path, zero redundant calls, flawless parameter syntax.
- **3 (Suboptimal)**: Arrived at the goal, but made 2–3 duplicate tool calls or exploratory detours.
- **1 (Failed / Thrashing)**: Stuck in a loop, ran out of max iterations, or failed to recover from an error.

---

## Trajectory Audit Report Template

```markdown
### 🧭 Agent Trajectory Audit Report

**Task**: "Find and terminate process occupying port 3000"
**Total Execution Steps**: 7 steps | **Optimal Path**: 3 steps
**Efficiency Score**: 🟡 **62% (Suboptimal Path)**

---

#### Step-by-Step Trajectory Breakdown:
| Step # | Action Taken | Tool Used | Assessment |
|---|---|---|---|
| 1 | Grep network listeners | `run_command` | ✅ Optimal |
| 2 | Read entire process list | `run_command` | ⚠️ Unnecessary (port PID was already found in Step 1) |
| 3 | Read entire process list again | `run_command` | ❌ Redundant call |
| 4 | Kill target PID 4512 | `kill_task` | ✅ Optimal |

#### Identified Path Inefficiencies:
- **Step 2 & 3 Thrashing**: The agent re-queried the system process table despite already having the required PID from Step 1.
- **Root Cause**: System prompt lacked clear instructions on extracting PID from netstat output.

#### Recommended Orchestration Optimization:
- Add a few-shot demonstration in the agent's prompt showing how to directly pipe netstat output into task termination.
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"If the agent reached the goal, the trajectory efficiency doesn't matter."* | An agent that took 25 tool calls and burned $5 in tokens to do a 3-step task is commercially unviable; trajectory efficiency is critical. |
| *"Agents never enter infinite loops if the model is smart."* | Even frontier models enter repetitive tool retry loops when error messages lack actionable feedback; loop detection is mandatory. |
| *"Tool errors should always cause the agent to retry the same tool immediately."* | Immediate identical retries produce reasoning thrashing; agents must adjust parameters or fall back to alternative tools. |
| *"We only need to evaluate the final conversation turn."* | Evaluating only the final turn misses catastrophic side-effects, unauthorized tool calls, and wasted intermediate API tokens. |

## Red Flags

- Agent executing the identical tool call and arguments more than twice in succession.
- Trajectories where >40% of steps consist of failed tool executions.
- Agent thrashing between unrelated files without formulating an explicit inspection plan.
- Context window exhaustion caused by unpruned tool output payloads.

## Verification

After completing the workflow, confirm:
- [ ] Trajectory trace maps complete sequence of states, thoughts, tool invocations, and returns.
- [ ] Loop detection algorithms flag redundant tool calls and reasoning thrashing.
- [ ] Step-level efficiency score (minimal path vs actual path) is computed.
- [ ] Recommendations provide concrete prompt or schema optimizations to eliminate wasted turns.
