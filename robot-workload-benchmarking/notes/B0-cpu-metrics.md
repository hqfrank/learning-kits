# B0 — CPU metrics

**Source:** Linux cgroups v2 (https://docs.kernel.org/admin-guide/cgroup-v2.html), CFS bandwidth control (https://docs.kernel.org/scheduler/sched-bwc.html), /proc/stat and /proc/schedstat (https://docs.kernel.org/filesystems/proc.html). · **Status:** concept primer, illustrative numbers only.

## In one sentence
CPU metrics on a robot measure how much processor each service uses, whether it is being throttled by its quota, and whether it is waiting in the run queue for a core — and the most common mistake is to read a throttling counter as "unmet demand" when it is nothing of the sort.

## What it is
Several numbers together describe the CPU load, each from a specific kernel source:

- **cgroup CPU usage** — total CPU time a container used, from `cpu.stat`, converted to **cores** (one core fully used for the whole window = 1.0 cores).
- **per-thread CPU** — the same, broken down by thread, to see which thread inside a service is busy.
- **CFS quota and throttling** — `cpu.max` sets the quota; `cpu.stat` reports `nr_throttled` (how many accounting periods the container was throttled in) and `throttled_usec` (microseconds of throttling).
- **per-core busy** — the fraction of time each physical core was busy, from `/proc/stat`.
- **run-queue wait** — how long runnable threads waited for a core, from `/proc/schedstat`.
- **load average** — the kernel's smoothed count of runnable-plus-waiting threads.
- **a foreign-CPU census** — a list of processes using CPU that are *not* part of the experiment, to catch contamination.

## How it works
**Usage in cores.** A container's `cpu.stat` reports cumulative CPU time; dividing the increase over a window by the window length gives cores used. This is the primary per-service cost.

**Quota and throttling — and the common misreading.** When a container reaches its `cpu.max` quota, the scheduler throttles it until the next period. `throttled_usec` counts throttled time **summed across all per-core run-queues**, so it is not "milliseconds of unmet demand" — a container throttled on four queues at once accrues four times the wall-clock throttled time. The honest reading is **the fraction of accounting periods in which the quota was exhausted** (`nr_throttled` over the number of periods), not a demand figure. To learn actual demand you must remove the quota and measure again (see [[C7-how-the-bench-can-lie]] on quota caps as a deliberate choice).

**Per-core busy and run-queue wait.** `/proc/stat` gives each core's busy fraction; a pool of cores near 100% busy means the CPU pool is the limit. `/proc/schedstat` gives run-queue wait: when threads are runnable but no core is free, this rises. Rising run-queue wait, not GPU-busy, is the signature of a CPU-bound stack (the sibling kit's scheduling note shows the control loop's tail inflating under exactly this pressure).

**The foreign-CPU census.** A benchmark machine often carries processes that are not part of the experiment: leftover services, the operator's shell, monitoring agents. A census lists every process using CPU and flags any that are not known experiment members. If foreign CPU exceeds a small threshold (an illustrative 0.3 cores), the window is suspect (see [[C4-windows-gates-and-validity]]).

## How it is measured or used in a benchmark
- **Report cores per service, from cgroup `cpu.stat`.** This is the main cost number.
- **Report quota exhaustion as a fraction of periods, never as a demand.** Add an uncapped run as a separate call-out if you want the real demand.
- **Report per-core busy and run-queue wait for the CPU pool.** These show whether the pool is the first limit.
- **Run a foreign-CPU census every window.** Void or flag the window if contamination exceeds the threshold.
- **Pin observers off the application cores.** The sampler and probes themselves use CPU; put them on a dedicated core so they do not steal from the services (see [[B4-profilers-and-the-observer-effect]]).

## Common confusions
- **"`throttled_usec` is unmet demand."** It is a sum over per-core run-queues, not wall-clock demand; report the fraction of throttled periods instead.
- **"High load average means overload."** Load average counts runnable-plus-waiting threads and includes short spikes; pair it with per-core busy and run-queue wait.
- **"Usage in percent is enough."** Convert to cores so the number is comparable across machines with different core counts.
- **"The observer's CPU does not matter."** A sampler on an application core steals from the service it measures; pin it away.

## Why it matters for robotics workloads
On a small robot computer the CPU pool usually runs out before the GPU, because the stack is full of per-message and per-person bookkeeping (see [[A2-people-perception]] and [[A5-audio-and-voice]]). The metrics that reveal this are per-core busy and run-queue wait, not GPU-busy. And the quota-throttling counter is the single easiest number to misread, so the benchmark must report it correctly — as a fraction of exhausted periods — or it will claim a demand it never measured.

## Terms introduced
- **cores (as a unit)** — CPU time used divided by wall-clock time; 1.0 cores = one core fully busy for the window.
- **CFS quota (`cpu.max`)** — the Completely Fair Scheduler bandwidth cap on a container.
- **`nr_throttled` / `throttled_usec`** — the count of throttled periods / the summed throttled time (summed over run-queues, not wall-clock demand).
- **per-core busy** — each physical core's busy fraction, from `/proc/stat`.
- **run-queue wait** — time runnable threads spent waiting for a core, from `/proc/schedstat`; the signature of a CPU-bound stack.
- **load average** — the kernel's smoothed count of runnable-plus-waiting threads.
- **foreign-CPU census** — a per-window list of processes using CPU that are not part of the experiment.
- **observer core** — a dedicated core for samplers and probes, so they do not steal from the services.
