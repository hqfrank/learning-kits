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
