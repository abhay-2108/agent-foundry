# Agent Autonomy & Trajectory Benchmarking Gym

A standardized benchmarking suite to evaluate autonomous AI agents on path directness, loop resilience, and tool schema accuracy.

---

## 1. Evaluation Axes

| Benchmark Code | Evaluation Axis | Metric & Formula | Pass Threshold |
| :--- | :--- | :--- | :--- |
| **`TRAJ-01`** | **Trajectory Directness** | Path Efficiency: $S_{direct} = \frac{\text{optimal\_steps}}{\text{actual\_steps}}$ | $\ge 75\%$ |
| **`LOOP-01`** | **Loop & Thrashing Resilience** | Max Retry Bounds: Halts retry loop on simulated tool failure | $\le 3$ retries |
| **`SCHEMA-01`** | **Tool Parameter Accuracy** | Type & Required Field Compliance | $100\%$ schema match |

---

## 2. Running Benchmarks

```bash
# Run the complete agent autonomy benchmark gym
python benchmarks/benchmark_runner.py
```
