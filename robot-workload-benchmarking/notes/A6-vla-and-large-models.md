# A6 — VLA and large models

**Source:** GR00T N1 (arXiv:2503.14734), π0 / π0.5 (https://www.physicalintelligence.company/blog/pi05). Worked example and numbers from [[../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency|the sibling C1 note]]. · **Status:** concept primer; the only concrete numbers are sibling-kit values, cited as such.

## In one sentence
A vision-language-action (VLA) model is the robot's large neural tenant: it reads cameras and a goal, runs a big backbone and an action head to emit a chunk of future actions, and because it closes a loop with the robot, its inference latency becomes a hard cap on how often the robot can re-plan — which makes it a demanding and disruptive GPU co-tenant.

## What it is
A **vision-language-action (VLA)** model maps camera images and a language goal to robot actions. Two public families are **GR00T N1.x** (NVIDIA, arXiv:2503.14734) and **π0.5** (Physical Intelligence, https://www.physicalintelligence.company/blog/pi05). Their shape is:

- a **backbone** — a vision-language model that encodes the images and goal into a representation;
- an **action head** — a smaller network that turns that representation into actions, often by a diffusion or flow-matching process that runs several refinement steps.

The model emits an **action chunk**: several future timesteps at once (an illustrative horizon of 10), which the controller executes open-loop until the next chunk arrives.

## How it works
**Action chunks and re-planning rate.** One inference produces one chunk of H future actions. The robot executes the chunk, and the model re-plans when it finishes (or sooner). So the **re-planning rate** is the inverse of the inference latency: a 53 ms inference re-plans at about 19 Hz, a 90 ms inference at about 11 Hz (both from the worked example in [[../jetson-orin-thor-metrics/notes/C1-pi05-solo-latency|the sibling C1 note]]). Latency is a rate cap, not just a delay.

**Denoising / flow steps.** The action head refines its output over several steps, each re-reading the head's weights. More steps means more weight traffic, which on a small board is a memory-bandwidth cost (the sibling C1 note shows a VLA is a bandwidth problem, not a compute problem).

**TensorRT versus eager.** Running the model through a compiled inference engine (TensorRT) is far faster than running it step-by-step in the framework (eager). A VLA that just fits its deadline in compiled form will miss it in eager form, so the benchmark runs the deployed, compiled path.

**On-demand large language models.** Beyond the VLA, the stack may call a large language model on demand for reasoning. These calls are best-effort and often cloud-based; the benchmark stubs them (see [[C3-the-harness-and-fakes]]).

**Why a VLA is a closed-loop tenant.** Unlike a one-shot classifier, a VLA runs continuously at its re-planning rate, holding the GPU for a large fraction of each cycle. As a co-tenant it both takes GPU time from other services and is itself slowed when they take time back. The sibling kit shows that only a GPU sharing discipline — a separate process plus an SM cap (an illustrative 25–35% of the SMs) — lets a VLA and a hard control loop coexist ([[../jetson-orin-thor-metrics/notes/L4-scheduling-ladder|the L4 scheduling ladder]]).

## How it is measured or used in a benchmark
- **Measure observation-to-action latency and its inverse.** The deployable number is the time from a new observation entering the model to a new action chunk leaving it; its inverse is the re-planning rate. See the sibling C1 note for the full method.
- **Run the compiled path.** Measure the TensorRT engine as deployed, never the eager framework, because the deadline is set against the compiled latency.
- **Record the configuration.** Camera count, action horizon, and number of denoising steps all change the cost; record them.
- **Treat it as a co-tenant.** The important benchmark result is not the VLA's solo latency (the sibling kit has that) but what it does to the control loop and the camera when they share the GPU, and whether a sharing discipline fixes it.

## Common confusions
- **"Latency is just a delay."** For a VLA it is a rate cap: the robot cannot re-plan faster than the model runs.
- **"A VLA is compute-bound because it is big."** At batch 1 it re-reads its weights every inference, so it is bandwidth-bound; the sibling C1 note shows latency tracks bytes moved, not nominal compute.
- **"Eager and compiled are close enough."** Compiled (TensorRT) can be roughly twice as fast; a VLA that fits its deadline compiled will miss it eager.
- **"A VLA shares the GPU fine via CUDA streams."** Streams do not isolate it; without a separate process and an SM cap it starves the control loop (see [[../jetson-orin-thor-metrics/notes/07-sharing-the-gpu|the sibling sharing-the-GPU note]]).

## Why it matters for robotics workloads
A VLA is the single most disruptive GPU tenant a robot can run, because it holds the GPU almost continuously and its latency sets the robot's re-planning rate. Whether a robot can run a VLA on-board while keeping its control loop depends entirely on the GPU sharing discipline. The benchmark's role is to measure that interaction, using the sibling kit's solo latencies as the baseline the co-tenancy is compared against.

## Terms introduced
- **vision-language-action (VLA) model** — a model mapping camera images and a language goal to robot actions (GR00T N1.x, π0.5).
- **backbone** — the vision-language encoder inside a VLA.
- **action head** — the smaller network that turns the backbone's output into actions, often by diffusion/flow refinement.
- **action chunk / horizon (H)** — the several future timesteps one inference emits, executed open-loop until replaced. Also in [[../jetson-orin-thor-metrics/glossary|the sibling glossary]].
- **re-planning rate** — the inverse of observation-to-action latency; latency is a rate cap. Also in the sibling glossary.
- **denoising / flow steps** — the refinement iterations of the action head, each re-reading its weights.
- **TensorRT vs eager** — a compiled inference engine versus step-by-step framework execution; compiled is much faster.
- **closed-loop tenant** — a model that runs continuously at a rate set by its own latency, both taking and losing GPU time to co-tenants.
- **on-demand LLM** — a large language model called occasionally for reasoning, usually best-effort and often cloud-based.
