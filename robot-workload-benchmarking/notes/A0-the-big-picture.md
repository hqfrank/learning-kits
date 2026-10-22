# A0 — The big picture: a robot stack as concurrent pipelines

**Source:** general robotics-systems knowledge; ROS 2 concepts (https://docs.ros.org/en/rolling/Concepts.html). Platform behaviour links to [`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/). · **Status:** concept primer, no measured numbers.

## In one sentence
A home robot's software stack is many small programs that run at the same time, each on its own clock, passing messages to one another, and together they must keep a few hard timing promises while sharing one small computer's CPU cores, one GPU, and one pool of memory.

## What it is
The stack is a set of concurrent pipelines, grouped by purpose: **sense → perceive → decide → act**.

- **Sense** reads hardware: a depth camera, a microphone array, an inertial sensor, motor-control boards.
- **Perceive** turns raw sensor data into meaning: where people are, where the robot is, what was said.
- **Decide** chooses what to do: plan a path, pick a behaviour, generate an action.
- **Act** sends commands to the motors and the speaker.

Each stage is one or more *services* — separate operating-system processes, usually one per container. Services do not call each other directly. They publish messages on named *topics* and subscribe to the topics they need. This is the publish/subscribe (pub/sub) pattern, provided here by a robot middleware (ROS 2, see [[A7-middleware-containers-and-platform]]).

## How it works
Every pipeline runs at its own **rate** and has its own **deadline**. Three timing classes matter, and they set how much the benchmark must protect each service.

- **Hard real-time** — the control loop that drives the legs or wheels. It runs at a fixed rate (an illustrative 50 Hz) and must finish each cycle before the next one starts (a 20 ms deadline). A missed deadline is a real fault: the robot can stumble. See [[A4-locomotion-and-whole-body-control]].
- **Soft real-time** — perception. It should keep up with the camera (an illustrative 10 Hz), but a late frame degrades quality, it does not break the robot. See [[A1-depth-camera-and-odometry]] and [[A2-people-perception]].
- **Best-effort** — cognition and large models. They run when they can; a slow reply is acceptable. See [[A6-vla-and-large-models]].

The services load three shared resources differently, and the benchmark tracks each one separately (Part B):

- **CPU** — the per-service process work: message handling, Python post-processing, filtering, planning. On a small robot computer this is often the first resource to run out.
- **GPU** — neural-network inference: detection, depth, pose, the large models. One GPU is shared by every service that uses it; the sibling kit [[../jetson-orin-thor-metrics/notes/L4-scheduling-ladder|L4 scheduling ladder]] shows how the sharing discipline decides whether the control loop survives.
- **Memory** — on an integrated system-on-chip the CPU and GPU share one physical memory and one memory controller, so a memory-heavy service on one side can slow a service on the other (see [[../jetson-orin-thor-metrics/notes/00-platforms|the platforms note]]).

**On-board versus cloud.** Some work runs on the robot (on-board): everything with a deadline, and anything that must work without a network. Some work can run in the cloud: a large language model, a speech service. The benchmark measures the on-board stack; it replaces each cloud call with a stand-in that imitates the call's timing (see [[C3-the-harness-and-fakes]]).

## How it is measured or used in a benchmark
The benchmark's job is to answer two questions for this stack on this computer: **which resource runs out first, and by what mechanism?** To answer them it must:

1. Run each service the way it is actually deployed (same container, same core assignment, same rate).
2. Measure CPU, GPU, memory, and per-service output rate and latency at the same time.
3. Check that the hard-real-time loop keeps its deadline while every other service runs.

The rest of Part A describes each pipeline. Part B describes the metrics. Part C describes the method that keeps the answer honest.

## Common confusions
- **"The GPU is the bottleneck."** On a small robot computer the CPU usually runs out first, because much of the stack is per-message bookkeeping in a scripting language, not neural-network math (see [[B0-cpu-metrics]] and [[A2-people-perception]]).
- **"Services call each other."** They do not; they publish and subscribe. A service's cost therefore depends on how many messages it receives, not on who sent them (see [[A5-audio-and-voice]]).
- **"One rate fits all."** Each pipeline has its own rate and deadline; mixing them up hides which deadline is actually at risk.

## Why it matters for robotics workloads
A robot is not one program with one bottleneck. It is a crowd of programs with different deadlines sharing one small machine. The benchmark must respect that structure: it protects the hard loop, treats perception as soft, and treats cognition as best-effort. A measurement that ignores the structure — for example, one average GPU-utilisation number — cannot tell you whether the robot will still walk while it thinks.

## Terms introduced
- **service** — one operating-system process (usually one container) that runs part of the stack.
- **topic** — a named channel that carries messages of one type; services publish to it and subscribe from it.
- **publish/subscribe (pub/sub)** — the pattern where services communicate only through topics, never by direct calls.
- **rate** — how often a pipeline produces output, in Hz.
- **deadline** — the time by which one cycle of a pipeline must finish.
- **hard / soft real-time, best-effort** — the three timing classes: a missed hard deadline is a fault, a missed soft deadline degrades quality, best-effort work has no deadline.
- **integrated system-on-chip (SoC)** — a computer where CPU and GPU share one physical memory and one memory controller. Also defined in [[../jetson-orin-thor-metrics/glossary|the sibling glossary]].
- **on-board / cloud** — work that runs on the robot / work that runs on a remote server reached over a network.
