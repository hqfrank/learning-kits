# A2 — The same work costs more cycles (IPC loss, shared cluster cache)

**Source:** per-thread hardware counters through `perf_event_open` (Linux `perf` subsystem); the cache-level interference mechanism in [B2 — cache-level interference](../../jetson-orin-thor-metrics/notes/B2-cache-level-interference.md); numbers from [`constants.json`](../constants.json) by key · **Status:** teaching note; every measured value is illustrative.

## In one sentence
In the full stack, fixed-work threads execute the same user instructions per unit of work as alone but need many more cycles for them, because instructions per cycle fall; for the motor-control services, moving their CPU-cluster neighbours away gives back about two thirds of the lost cycles (illustrative, `cluster_move_recovered`), but the path (cluster cache, board memory traffic, their own load) is not isolated.

## What it measures
- **Instructions per work unit** — how much work a thread does. If this rises, the thread does more work (more inputs, or spinning).
- **Cycles per work unit** — how long the work takes, in CPU cycles.
- **IPC (instructions per cycle)** — instructions ÷ cycles. If cycles rise at constant instructions, IPC falls: the same work runs slower per instruction.
- **L3 refills per instruction** — how often the core fetched a line into its view of L3. It is a hint about cache pressure, not a cause.

The measurement probe fixes the work units: one bus cycle for a motor-control loop, one message for an audio input service, one frame for the object detector's worker.

## How
A counter tool opens `perf_event_open` counters per thread, user-mode and all-mode, for a fixed interval in each window. Every event runs without multiplexing. The comparison is the thread alone versus the same thread in one plain full-stack window.

The pre-registered decomposition compares two growths: the growth in instructions per unit and the growth in cycles per unit. If instructions explain only a small share of the cycle growth, the class is X2, "slower work". If they explain a large share, the class is "more work".

The direct test then moves every service that shares the motor-control services' CPU cluster away. The motor-control services keep their own reserved cores; their cluster-mates get a pool cpuset instead. There are two windows per arm: baseline and moved. The pre-registered measure is the **removed fraction f = (X_base − X_moved) ÷ (X_base − X_alone)**, where X is the motor loop's user cycles per bus cycle. A pre-registered line at 0.5 (illustrative, `cluster_move_class_line`) separates "cluster-mates cause most" from "cluster-mates cause part".

Analogy: a cook follows the same recipe, but the shared spice rack is crowded, so each step takes longer to reach.

## Predicted
- Hypothesis X2: instructions per unit stay unchanged, and most of the cycle growth is IPC loss.
- The cluster move, written before the run: "part" (f below the line). An earlier cache A/B test had shown that a synthetic L3-footprint load on the neighbouring cores reproduces a slower motor loop, and that a load which fits in L1 reproduces nothing.

## Measured
Each value below is an illustrative measurement.

**Alone → full stack, user-mode counts per work unit, three fixed-work threads:**

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Instructions per unit, growth | 0.0 | `instr_growth` |
| Cycles per unit, growth | 0.4 to 1.0 (1.4× to 2× the cycles) | `cycles_growth_range` |
| IPC, drop | 0.3 to 0.5 (a third to a half) | `ipc_drop_range` |
| L3 refills per instruction, full stack ÷ alone | 2× to 3× | `l3_refill_ratio_range` |

The clock does not change; all cores are locked. The motor loop is never preempted, so its slowdown is not run-queue wait.

**Cluster move, the motor loop's user cycles per bus cycle:**

| Quantity | Value (illustrative) | Key |
|---|---|---|
| Removed fraction f | 0.65 | `cluster_move_recovered` |
| Pre-registered class line | 0.5 | `cluster_move_class_line` |
| Camera rate cost of the move | 4 to 6 Hz | `cluster_move_camera_cost_hz` |

In the moved arm, L3 refills per instruction fall, and board memory traffic also falls.

## The gap, and what it means
**Alone → full stack: the pre-registered class is X2 (slower work) for all three threads.** User instructions per unit are flat; the cycle growth is an IPC drop. In kernel mode, some of the threads execute more instructions per unit; the investigation does not separate message fan-out, interrupt work and scheduler work.

**Cluster move: f lands above the pre-registered line, and the class carries a traffic caveat.** The pre-registered class is "the cluster-mates cause most of the motor loop's slowdown (or less board traffic)". The prediction was "part", so the prediction failed. The result sits close to the line, so read it as "about two thirds", not as a clean "most". Three facts keep the path open:

1. The two moved windows differ from each other, and the spread between windows reaches toward the line. The class is therefore not robust to one more window.
2. Board memory traffic fell in the moved arm, outside the pre-registered matching limit. The class therefore carries "(or less board traffic)". The fall in L3 refills fits a cluster-cache cause, but lower DRAM latency also lowers the cycles per refill.
3. The motor-control services' own CPU load also fell in the moved arm, and f counts that too.

The remaining part, about a third (my estimate from `cluster_move_recovered`: 1 − 0.65 = 0.35), is not separated: the motor-control services' own load, the probe's heartbeat on a neighbouring reserved core, and board traffic.

**The move is not a free fix.** The moved services go to the pool, so the camera loses 4 to 6 Hz (illustrative, `cluster_move_camera_cost_hz`), and other pool services and message delay get worse.

**For the pool services the path is less clear than for the motor loop.** The audio input service and the detector worker are preempted in the full stack, so both neighbour cache traffic and cache refill after preemption are possible.

## So what
A thread with its own reserved core can still need 1.4× to 2× the cycles for the same work in the full stack (illustrative, `cycles_growth_range`), through shared cache and memory, without any run-queue wait (interpretation). Count instructions and cycles per unit of work before calling a slowdown "more work" or "less CPU".

## Terms introduced
- **IPC (instructions per cycle)** — retired instructions divided by CPU cycles for one thread.
- **PMU (performance monitoring unit)** — the per-core hardware counters, read through `perf_event_open`.
- **fixed-work thread** — a thread whose work per unit is fixed (bus cycle, message, frame), so its instructions per unit should not change.
- **X2 / "slower work"** — the class where cycles per unit rise at constant instructions per unit.
- **cluster-mate** — a service on another core of the same CPU cluster, sharing that cluster's L3 cache and interconnect.
- **removed fraction f** — (X_base − X_moved) ÷ (X_base − X_alone): the share of the motor loop's full-stack cycle growth that moving its cluster-mates removes.
- **cache A/B** — the earlier test that put a synthetic L3-footprint load or an L1-resident load on the neighbouring cores.
