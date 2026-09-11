---
name: agent-trajectory-evaluator
description: >-
  Use this skill when auditing, benchmarking, or optimizing autonomous agent execution trajectories.
  Analyzes tool call sequences, detects redundant loops, flags reasoning thrashing,
  and scores step-level efficiency rather than just the final conversational output.
---

# Agent Trajectory Evaluator & Step Auditor

An advanced diagnostic skill focused on evaluating the **path** an autonomous agent took to solve a problem—auditing intermediate tool calls, reasoning traces, parameter selections, and efficiency bottlenecks.

## When to Use This Skill
- When an agent arrives at the correct final answer, but took 15 tool calls when it only needed 2.
- When diagnosing agent thrashing (calling the same search tool repeatedly with minor query variations).
- When benchmarking autonomous coding agents, customer support bots, or research crawlers.
- When optimizing agent runtime latency and token costs across multi-step execution graphs.
- Trigger phrases: `"evaluate trajectory"`, `"audit tool calls"`, `"agent efficiency"`, `"step-level evaluation"`, `"debug agent loop"`.

---

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

---

## Anti-Patterns & Traps to Avoid

1. **End-State Blindness (Ignoring Trajectory Waste)**: Celebrating that an agent arrived at the correct answer while ignoring that it took 45 meandering tool steps (costing $2.50 in API tokens) when 3 steps were sufficient. Always audit path directness alongside final correctness.
2. **Repetitive Tool Invocations on Failure**: Permitting an agent to execute the identical failing tool call or query repeatedly without altering arguments or diagnosing the error. Consecutive identical tool failures must trigger an immediate circuit breaker.
3. **Unbounded Exploratory Thrashing**: Allowing an agent to list directory after directory aimlessly without formulating an explicit hypothesis. Subagents must establish a search plan before inspecting files.
4. **Over-Optimizing for Step Count over Safety**: Penalizing an agent for executing pre-flight verification checks (e.g., checking git status or running test suites before modifying code) in the pursuit of minimal step counts. Distinguish between defensive validation steps and redundant thrashing.

---

## Quality Checklist

- [ ] Every execution step is classified as Optimal, Necessary, Redundant, or Error.
- [ ] Path directness ratio is calculated: $\text{Directness} = \text{Optimal Steps} / \text{Actual Steps}$.
- [ ] Consecutive duplicate tool invocations are flagged as thrashing defects.
- [ ] Root causes for suboptimal branches are identified (prompt ambiguity, missing tool, bad schema).
- [ ] Concrete prompt remediations or few-shot examples are provided to eliminate identified detours.
- [ ] Trajectory evaluation checks whether intermediate state checkpoints were respected.
