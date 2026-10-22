# A4 — Locomotion and whole-body control

**Source:** general real-time control knowledge; Linux isolcpus/cpusets (https://docs.kernel.org/admin-guide/cgroup-v1/cpusets.html). Deadline statistics in [[B3-deadlines-tails-and-statistics]]. · **Status:** concept primer, illustrative rates only.

## In one sentence
The locomotion controller is the one piece of the stack with a hard deadline: a small neural policy on the CPU runs a fixed control loop (an illustrative 50 Hz, 20 ms per cycle), talks to motor-control boards over a fast bus at hundreds of Hz, and is pinned to its own CPU cores so that nothing else in the stack can make it miss a cycle.

## What it is
Whole-body control (WBC) turns a desired motion into torques for every joint. On a learned-policy robot the controller is a **multi-layer perceptron (MLP)** — a small feed-forward network — that takes the robot's current state (joint angles, velocities, body orientation, a command) and outputs target joint actions. It runs on the **CPU**, not the GPU, because it is tiny and must run on a strict schedule with no queueing behind other GPU work.

Around the policy sit:

- **the control loop** — reads state, runs the policy, sends actions, every cycle, at a fixed rate;
- **motor-control boards** — hardware that drives the actuators, talking to the computer over a fast serial bus at hundreds of Hz (faster than the control loop);
- **an IMU** — the inertial sensor that reports body orientation and motion, also at hundreds of Hz.

## How it works
**The loop and its deadline.** Each cycle must finish within its period (20 ms at 50 Hz). If the policy inference plus the surrounding read/send work does not finish in time, the cycle is a **deadline miss**, and the robot's motion degrades. The number of misses per minute is the control loop's primary health metric (see [[B3-deadlines-tails-and-statistics]]).

**Why it is isolated on dedicated cores.** On a shared computer, other services compete for CPU time and can delay the control loop. To prevent this the control loop's threads are **pinned** to dedicated CPU cores that no other service may use (via cpusets or `isolcpus`), and interrupts are moved off those cores. This gives the loop a protected island. A benchmark must reproduce this placement, because the whole point is to test whether the island holds under full load.

**The fast bus.** The motor boards exchange messages with the computer far faster than the control loop runs — hundreds of Hz — so the bus has its own timing that the benchmark checks separately from the control loop. A slow or jittery bus is a fault even if the control loop itself keeps its rate.

**Modes.** The controller has modes: a passive damping/standing mode (hold position, react gently) and an active walking mode (run the gait). Walking exercises the full policy and the fastest publishers; standing is lighter. The benchmark must say which mode it ran, because the cost differs.

## How it is measured or used in a benchmark
- **Count deadline misses, not averages.** The metric is misses per minute and the tail of the per-cycle time (p99), not the mean (see [[B3-deadlines-tails-and-statistics]]).
- **Reproduce the isolation exactly.** Run the real controller binary pinned to the same cores with interrupts moved, because the benchmark is testing that isolation.
- **Fake the boards faithfully.** No real motors are attached, so a fake motor board on the harness speaks the real wire protocol at the real rate (see [[C3-the-harness-and-fakes]]). If the fake's framing or rate is wrong, the bus timing is wrong.
- **Drive the real mode.** Command the controller into the mode under test (standing or walking) through its own interface, so the policy actually runs.
- **Test the island under siege.** The interesting result is the control loop's p99 and miss rate while every other service runs and the GPU and memory are loaded (the sibling kit [[../jetson-orin-thor-metrics/notes/L4-scheduling-ladder|L4 scheduling ladder]] shows the control loop surviving only under the right GPU sharing discipline).

## Common confusions
- **"The policy runs on the GPU."** The control policy usually runs on the CPU, because it is small and must not queue behind other GPU work.
- **"The average cycle time is fine, so the loop is healthy."** A deadline is about the worst cycle, not the average; report the tail and the miss count.
- **"Isolated cores cannot be disturbed."** CPU isolation stops CPU contention, but a memory-heavy co-tenant can still reach the isolated loop through the shared memory controller (the sibling B8/L4 notes show this).
- **"The bus rate equals the control rate."** The motor bus runs much faster than the control loop and has its own timing to check.

## Why it matters for robotics workloads
The control loop is the only service that can hurt the robot physically if it is late. Everything else in the benchmark exists to test whether the stack can run at full load without pushing the control loop past its deadline. That is why the loop gets its own cores, its own faithful fake hardware, and its own tail statistics — and why a benchmark that merges it into an average has measured the wrong thing.

## Terms introduced
- **whole-body control (WBC)** — computing joint torques/actions for the whole robot from its state and a command.
- **multi-layer perceptron (MLP)** — a small feed-forward neural network; here the control policy, run on the CPU.
- **control loop** — the fixed-rate cycle that reads state, runs the policy, and sends actions.
- **deadline miss** — a control cycle that does not finish within its period.
- **core pinning / isolation** — assigning threads to dedicated CPU cores (cpusets, `isolcpus`) that no other service uses.
- **motor-control board** — hardware that drives the actuators, talking to the computer over a fast bus.
- **fast bus** — the serial link to the motor boards, running at hundreds of Hz, faster than the control loop.
- **damping/standing vs walking mode** — a light passive mode versus the active gait; the cost differs and the benchmark states which ran.
