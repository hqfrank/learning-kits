# A7 — Middleware, containers, and the platform

**Source:** ROS 2 concepts and QoS (https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html), Zenoh (https://zenoh.io/docs/), Linux cgroups v2 (https://docs.kernel.org/admin-guide/cgroup-v2.html), cpusets/isolcpus (https://docs.kernel.org/admin-guide/kernel-parameters.html). · **Status:** concept primer, no measured numbers.

## In one sentence
The platform layer is the plumbing that lets the services run and talk — a pub/sub middleware with quality-of-service settings, a router process, containers with CPU quotas and core pinning, and a few monitoring services — and although it uses little CPU, it decides correctness: which messages arrive, which cores a service may use, and whether the control loop is protected.

## What it is
This note covers the parts of the stack that are not a sensor, a model, or a controller, but make all of those work together:

- **The middleware** — ROS 2 provides the pub/sub system: typed topics, subscriptions, and quality-of-service (QoS) settings (https://docs.ros.org/).
- **A router / bridge** — a process (for example, a zenoh router) that carries messages between services and across machines.
- **Containers and compose files** — each service runs in its own container; a compose file declares the containers, their images, and their resource limits.
- **CPU quotas (cgroups)** — Linux control groups cap how much CPU a container may use (`cpu.max`) and account what it used (`cpu.stat`).
- **Core pinning (cpusets, isolcpus)** — assigning a container or thread to specific CPU cores, and reserving cores so only certain work runs on them.
- **Telemetry / monitoring services** — small services that collect metrics, logs, and health.

## How it works
**QoS shapes delivery.** ROS 2 topics have QoS settings — reliability (best-effort or reliable), history depth, durability — that decide whether a slow subscriber drops messages or blocks a publisher. The wrong QoS can silently change what a service receives, so it changes the workload, not just the transport.

**The router carries and bridges.** A router process moves messages within the machine and across machines. In a benchmark the router also appears as a small but real CPU cost, and its placement matters: a router sharing a core with a time-critical service steals from it.

**Quotas are deliberate.** A container's CPU quota (`cpu.max`) is a deployment choice: it stops one service from draining the whole CPU pool. When a service hits its quota, the kernel throttles it — it is parked until the next accounting period. This is intended behaviour, and the benchmark must keep the deployed quota as the baseline (see [[C7-how-the-bench-can-lie]] on reporting the uncapped case as a separate call-out).

**Pinning protects the control loop.** Core pinning (cpusets) and reserved cores (`isolcpus`) give the control loop its protected island (see [[A4-locomotion-and-whole-body-control]]). The platform layer is where that protection is configured; a benchmark must reproduce it exactly.

**Why platform services matter little in CPU but a lot in correctness.** Monitoring, the router, and the compose glue use little CPU on their own. But they decide which messages arrive (QoS), which cores each service uses (cpusets), and whether a service is throttled (quotas). A benchmark that gets the platform configuration wrong measures a different workload, even though the platform's own CPU cost is near zero.

## How it is measured or used in a benchmark
- **Reproduce the deployed configuration.** Same compose file, same QoS, same quotas, same core map. The platform is not something to simplify away.
- **Account the router and monitoring as real services.** Their small CPU cost is part of the stack; include them.
- **Keep quotas as the baseline.** Measure the service at its deployed quota; report an uncapped run only as a separate labelled call-out (see [[B0-cpu-metrics]] and [[C7-how-the-bench-can-lie]]).
- **Verify the isolation held.** Check at the start and end of each window that the control loop's cores carried only the control loop, and that services landed on the cores they were assigned (see [[C4-windows-gates-and-validity]]).

## Common confusions
- **"Platform services are negligible, so ignore them."** Their CPU is small, but their configuration decides the workload; ignoring the config changes what you measure.
- **"QoS is just transport tuning."** The wrong QoS silently drops or blocks messages, changing each service's effective input.
- **"A quota throttle means the service is broken."** A quota is a deliberate deployment choice; throttling at the quota is expected, and the deployed quota is the baseline.
- **"Pinning is optional detail."** Core pinning is what protects the control loop; reproducing it is the whole point of testing the loop under load.

## Why it matters for robotics workloads
The platform layer is where the deployment's intent lives: who gets which core, who may use how much CPU, and which messages are guaranteed. These choices decide whether the control loop survives a full stack. A benchmark that respects them measures the robot as it actually runs; one that simplifies them measures a robot that does not exist.

## Clarification: reading a boot-time core map
A robot computer's platform is often set at boot, on the kernel command line, plus a few system settings. A typical line for a 12-core board reads: `isolcpus=8-11`, swap off, `nospectre_bhb`, with cores 0–7 as the shared pool, 8–9 for pinned helper services and 10–11 for the control loop. Each part means one thing.

- **`isolcpus=8-11`** removes cores 8–11 from the scheduler's general pool. A thread runs there only if something pins it there (a container `cpuset`, `taskset`). Unpinned work lands on cores 0–7, which is why 0–7 is "the shared pool". Three limits matter in a benchmark:
  - Per-core kernel threads (workers, softirq, migration) still run on isolated cores.
  - `isolcpus` does not move device interrupts (that needs IRQ affinity or `irqaffinity=`) and does not stop the scheduler tick (that needs `nohz_full=`).
  - The scheduler does not load-balance inside an isolated set: if a container is pinned to 10–11, its threads stay on the core they first got, so two busy threads can share one core while the other is idle.
- **Swap off** means no memory page is ever moved out of RAM. Many embedded Linux images enable compressed swap in RAM (zram) by default. With swap off, a service never stalls on a swap-in, and no CPU is spent compressing pages. The cost: under memory pressure the kernel kills a process (the OOM killer) instead of slowing down. A benchmark must match the robot here, or memory behaviour differs.
- **`nospectre_bhb`** is an arm64 kernel flag. It turns off the mitigation for Spectre-BHB ("branch history injection"), a CPU side-channel attack in which user code steers the kernel's branch predictor. The mitigation clears the branch history each time the CPU enters the kernel from user space (a system call or an interrupt). That adds a small cost to every kernel entry. Turning it off makes kernel entries cheaper, and trades away that protection. A benchmark must match the robot, because a message-heavy stack makes many system calls.
- **The core map** is a deployment decision: a protected island for the control loop, a small pinned set for helpers that must not be starved or must not disturb the pool, and a shared pool for the rest. Cores are also grouped in clusters that share a cache, so "isolated" cores in one cluster still share that cache with each other. Isolation protects CPU time, not cache or memory bandwidth.

**The words underneath.**
- **cpuset vs. affinity.** A container's `cpuset` (`docker --cpuset-cpus`) is a cgroup setting. It applies to every thread of every process in the container. `taskset` (or `sched_setaffinity`) sets the allowed cores of one process or one thread. A thread may run only on cores allowed by both, so `taskset` can narrow a thread inside its container's cpuset but cannot leave it.
- **Per-core kernel threads** are kernel threads bound to one core, one set per core: `ksoftirqd/N` (deferred interrupt work), `kworker/N:*` (work queues), `migration/N` (moves tasks between cores), `cpuhp/N` (CPU hotplug). `ps` shows them in brackets, for example `[ksoftirqd/10]`. They run on isolated cores too.
- **An IRQ** (interrupt request) is a hardware signal that makes a core stop its current thread and run a driver's handler: a network card received a packet, a USB transfer finished, a timer fired. **IRQ affinity** is the set of cores that may take one interrupt (`/proc/irq/<n>/smp_affinity_list`). By default many interrupts land on core 0; a daemon such as `irqbalance` or a boot flag can move them.
- **The scheduler tick** is not a thread. It is a periodic timer interrupt on every core (typically 100–1000 times per second, set by the kernel's `CONFIG_HZ`). On each tick the kernel updates time accounting and checks whether the running thread's time slice is over. It interrupts the running thread for a few microseconds. Scheduling also happens at other moments: when a thread blocks, wakes or yields. `nohz_full=` stops the tick on a core that runs only one thread.
- **zram** is compressed swap in RAM. A page that would be swapped out is compressed and stored in RAM itself, trading CPU time for capacity. The configured size (often about half of RAM) is a ceiling: zram holds only the pages actually swapped, so it uses no RAM until there is memory pressure.
- **The OOM killer is not random.** It picks the process with the highest `oom_score`, which grows with the memory the process holds and is adjusted by `oom_score_adj` (−1000 = never kill). In a container with a memory limit, it kills inside that container only. On an integrated SoC some GPU allocations may not appear in a process's resident memory, so the kernel's view of "who holds memory" can be incomplete.
- **Spectre-BHB in one paragraph.** The CPU guesses where an indirect branch will go before it knows, and its guess uses the recent *branch history* (the pattern of the last branches taken) as part of the lookup key. Branches are normal user code, so a program can legally steer that history into a chosen state and then make a system call. The kernel's next indirect branch is then mispredicted on purpose, to a code fragment the attacker picked. The CPU later discards that wrong path, so nothing visible happens, but while it ran it loaded secret-dependent data into the cache, and cache timing leaks it. The attack does not stop prediction; it causes a chosen misprediction. Earlier fixes separated predictor entries between user and kernel, but history still crossed the boundary. The mitigation overwrites the history on every kernel entry. On a closed robot that runs only its own code, a team may judge the risk low and turn it off (`nospectre_bhb`) for speed.

Source: Linux kernel docs (https://docs.kernel.org/admin-guide/kernel-parameters.html, https://docs.kernel.org/admin-guide/cgroup-v2.html, https://docs.kernel.org/admin-guide/blockdev/zram.html, https://docs.kernel.org/timers/no_hz.html; `isolcpus`, `irqaffinity`, `nohz_full`, `nospectre_bhb`); Arm Spectre-BHB advisory (https://developer.arm.com/Arm%20Security%20Center/Spectre-BHB).

## Terms introduced
- **middleware** — the pub/sub system (ROS 2) that provides typed topics and subscriptions.
- **quality of service (QoS)** — ROS 2 settings (reliability, history, durability) that decide message delivery.
- **router / bridge** — a process that carries messages within and across machines (for example, zenoh).
- **container** — an isolated process environment; one service per container.
- **compose file** — the declaration of containers, images, and resource limits.
- **control group (cgroup)** — the Linux mechanism that caps and accounts a container's CPU and memory.
- **CPU quota (`cpu.max`)** — the cap on a container's CPU; hitting it throttles the container.
- **core pinning (cpusets) / reserved cores (`isolcpus`)** — assigning work to specific cores and reserving cores for specific work.
- **telemetry / monitoring service** — a small service collecting metrics, logs, and health.
- **swap off** — no page is moved out of RAM; memory pressure ends in an OOM kill rather than a slowdown.
- **`nospectre_bhb`** — arm64 kernel flag that disables the Spectre-BHB mitigation (branch-history clearing on every kernel entry from user space).
