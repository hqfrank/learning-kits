# A3 — Priorities in containers: nice does nothing across cgroups, cpu.weight does, and the wait moves

**Source:** Linux cgroup v2 documentation, `cpu` controller and `cpu.weight` (https://docs.kernel.org/admin-guide/cgroup-v2.html); numbers from [`constants.json`](../constants.json) by key · **Status:** teaching note; every measured value is illustrative.

## In one sentence
Inside a container, `nice` cannot raise a service's CPU share against other containers, because each container is its own cgroup; writing the container's `cpu.weight` does raise it, but the camera still does not return to its alone rate, and the wait moves onto other services.

## What it measures
The question is whether CPU priority for the depth camera service removes its full-stack rate loss of 5 Hz (illustrative, `camera_full_stack_loss_hz`). If pool queueing (X1, see [[A1-cpu-queueing-on-a-shared-pool]]) is the main cause, protecting the camera on the pool should bring it back near its alone rate.

**Warning: first check that the manipulation happened.** An arm that does not change the target's wait tests nothing, whatever its outcome.

## How
**How CFS shares a CPU between containers.** A container runtime puts each container in its own cgroup v2 group with the `cpu` controller on. CFS first shares CPU time between sibling groups in proportion to their `cpu.weight`. The default weight is 100 (`cpu_weight_default`), and the allowed range is 1 to 10000 (`cpu_weight_range`). Only inside a group does a thread's nice value set its share against the other threads of the same group. So a uniform nice on every thread of one container leaves that container's share against other containers unchanged.

Analogy: two families share one car by a fixed rota. Changing who drives inside one family does not give that family more time with the car.

Two arms are run:

1. **Nice arm** — every thread of the depth camera service gets a negative nice value at the start of the window, and the value is read back.
2. **Weight arm** — the camera container's `cpu.weight` is written from 100 (`cpu_weight_default`) to 1000 (illustrative, `weight_raised`) at the start of the window, with the observers placed as in the full stack. One plain full-stack window from the same session is the control; there are two treatment windows.

The weight-arm gate is a manipulation check: the run-queue wait of the camera's frame-path candidate threads must fall to a small fraction of the control. The pre-registered outcomes, if the gate passes, are three bands: camera rate back near alone → X1 causal; part of the way back → partial; little change → X1 not the main cause. If a GPU client loses a large part of its rate at the same time, a camera gain is reported as "X1 or GPU relief".

## Predicted
If X1 dominates, the camera returns near its alone rate with the GPU load unchanged.

## Measured
Each value below is an illustrative measurement.

**Nice arm: not a valid test.** The camera's run-queue wait per camera CPU-second does not fall, so the manipulation is not achieved. The camera rate even falls slightly while the camera's own threads use more CPU. A spinning worker pool fits this, but it is not proven.

**Weight arm (`cpu.weight` 100 → 1000, `cpu_weight_default` → `weight_raised`):**

| Quantity | Control → treatment (illustrative) | Key |
|---|---|---|
| Camera wait per camera CPU-second | 3.0 → 0.75 s | `weight_wait_per_cpu_s` |
| Camera rate | 25 → 27.5 Hz (control → mean of two treatment windows) | `weight_camera_hz` |
| Other services' run-queue wait, rise | 0.25 to 0.5 (a quarter to a half) | `weight_others_wait_rise` |

The camera's own wait falls by three quarters (my estimate from `weight_wait_per_cpu_s`: 1 − 0.75 ÷ 3.0 = 0.75), so the gate passes. The object detector loses rate in the treatment windows.

## The gap, and what it means
**Verdict, as pre-registered: split.** One treatment window lands in "partial"; the other lands in "not the main cause". No pooling rule was pre-registered, so the two verdicts stand side by side. Neither window brings the camera back to its alone rate.

**The gain cannot be split.** The object detector loses rate, so it submits less GPU work. By the pre-registered rule the camera gain is "X1 or GPU relief". The robust result is negative: removing most of the camera's CPU queueing does not bring the camera back to its alone rate.

**Correction kept visible: the gate's unit.** The gate as first written counted timeslices per frame. The intended count was *activations* per frame (wake-ups, that is voluntary switches), taken from an earlier scheduler trace. The wrong unit was copied into the plan during the pre-run review. With the gate as written, the candidate threads cannot be identified. With the corrected unit, the control selects exactly the two candidate threads, and the gate is met. The causal reading is conditional on this corrected gate.

**Weight is a trade, not a fix.** At ten times the default weight (my estimate from `weight_raised` and `cpu_weight_default`: 1000 ÷ 100 = 10), one dose only, the camera gains rate. The object detector loses rate, and the waits of people perception, mapping, navigation, odometry, the dialogue engine and audio rise by a quarter to a half (illustrative, `weight_others_wait_rise`). The CPU time comes from somewhere.

A later batch splits the camera's full-stack loss into single factors; see the camera part of [[B1-gpu-time-slicing-and-the-dose-curve]].

## So what
In a containerised stack, priority is a property of the cgroup, not of the thread (interpretation). Set `cpu.weight` (or use a child cgroup) to change a service's share, and always gate the arm on a manipulation check: the target's wait must fall.

## Terms introduced
- **cgroup v2** — the Linux control-group hierarchy; each container is one group, and the `cpu` controller shares CPU time between sibling groups.
- **cpu.weight** — the cgroup v2 file that sets a group's CPU share against its siblings; the default is 100 (`cpu_weight_default`).
- **nice** — the per-thread priority value; it sets a thread's share only against threads in the same cgroup.
- **manipulation check** — a gate that confirms the factor was actually applied (here: the target's wait fell) before the outcome is read.
- **frame-path candidate threads** — the camera threads that an earlier scheduler trace identified as possible capture-loop stages.
- **activation** — one wake-up of a thread (counted as a voluntary switch); not the same as a timeslice.
- **"X1 or GPU relief"** — the pre-registered label for a camera gain when a GPU client also lost rate, so the CPU and GPU causes cannot be split.
