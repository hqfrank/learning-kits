# 07 — Sharing the GPU

**Sources:** CUDA Programming Guide §1.2.2.1 (A-PM); Ampere MIG material (B-AMPERE); metrics-kit `B4`, `B7`, `L4`, Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
Several programs share one GPU through CUDA contexts and streams, but ordinary streams do not isolate them — the hardware block scheduler, time-slicing, MPS, SM reservation and MIG are the real knobs, and each isolates a different thing, so the right choice decides whether a real-time loop meets its deadline.

## What it is
The mechanisms, from least to most isolating (C-KIT-NOTES L4 "sharing discipline"):

- **CUDA context** — a process's GPU state (its memory maps, module code). Work from one context does not automatically yield to another; the GPU time-slices between contexts (A-PM; C-KIT-NOTES L4).
- **Stream** — an ordered queue of work *within* one context. Different streams in one context may run concurrently, but they share the context and **do not isolate** tenants (C-KIT-NOTES B7, L4).
- **Block scheduler** — the hardware unit that places blocks on SMs, in no guaranteed order (A-PM §1.2.2.1). This is what actually decides co-residence.
- **MPS (Multi-Process Service)** — lets several *processes* share one GPU context so their kernels run concurrently, with an optional per-client SM cap (B-AMPERE; C-KIT-NOTES L4).
- **SM reservation / cap** — `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE`, limiting an MPS client to a fraction of the SMs (C-KIT-NOTES L4).
- **MIG (Multi-Instance GPU)** — partitions one GPU into isolated instances, each with dedicated compute, cache and memory paths (B-AMPERE; C-PLAT).

## How it works and what each isolates
- **Streams isolate ordering, not resources.** Two streams' kernels still land on the same SMs and share L2 and the controller. The kit's "shared context" rung puts every tenant on its own stream in one context and finds no isolation at all (C-KIT-NOTES L4).
- **The block scheduler is bistable, not fair.** When a GPU co-tenant occupies above a small warp-slot fraction, it does not take a proportional share — it *locks the victim out* entirely until it drains. The lockout onset is ≈8% of warp slots on Orin, ≈14% on Thor (`lockout_onset_occupancy`, C-KIT-NOTES B4). This is pure hardware scheduling, measured with both tenants in one context (C-KIT-NOTES B4).
- **The controller is a separate conflict.** A CPU memory hog that occupies no SMs still slows a GPU victim once the victim spills L2 — up to 1.53× (Orin) / 2.53× (Thor) (`controller_contention_peak`, C-KIT-NOTES B4). Controller contention and SM lockout are two mechanisms with two remedies: footprint control for the controller, occupancy/partition control for lockout (C-KIT-NOTES B4).
- **Separate context (time-slice)** stops the lockout by not co-executing, but the time-slice tail still costs latency (C-KIT-NOTES L4).
- **MPS + SM cap** reserves SMs for the real-time tenant so a greedy co-tenant cannot lock it out; it isolates *compute share* but not the memory controller (C-KIT-NOTES L4).
- **MIG** isolates compute, cache and memory paths together — the strongest option — but was tech-preview/deferred on Thor at the time of the kit (C-PLAT; C-KIT-NOTES L4).

A throughput view hides all of this: the kit shows two same-class tenants deliver one tenant's aggregate throughput under both streams and MPS, so the co-tenancy cost shows up only in per-kernel latency and its tail, not in throughput (C-KIT-NOTES B7).

## On Orin and Thor (numbers from constants.json)
- **SM-lockout onset:** ≈8% warp slots (Orin), ≈14% (Thor) — `lockout_onset_occupancy` (C-KIT-NOTES B4).
- **Controller-contention peak:** 1.53× (Orin), up to 2.53× (Thor) — `controller_contention_peak` (C-KIT-NOTES B4).
- **MIG:** none on Orin; tech-preview on Thor — C-PLAT Table 1.
- **MPS + SM cap, measured effect (Thor):** capping a π0.5 policy to 35% of SMs returns a 100 Hz loop to 0% dropped ticks while the policy keeps 0.90 of its rate; a 25% cap keeps 0.72 — `mps_cap_vla_rate_retained` (C-KIT-NOTES L4).
- **The floor nothing fixes:** at ≈172 GB/s of CPU memory load the loop collapses regardless of precision or MPS cap — `cpu_memory_load_floor` (C-KIT-NOTES L4).

## Common confusions
- **Streams are not isolation.** The single most common mistake the kit calls out: putting tenants on separate streams in one context gives concurrency, not protection (C-KIT-NOTES B7, L4).
- **MPS alone does not protect a deadline.** Plain MPS oversubscribes in the aggressor's favour; you need the SM cap (C-KIT-NOTES L4).
- **QoS does not add capacity.** The GPU is a fixed pie; a cap only decides *which* tenant absorbs the deficit (C-KIT-NOTES L4).
- **A light co-tenant can still lock you out.** 8–14% of warp slots is enough; "small" is not "harmless" (C-KIT-NOTES B4).

## Why it matters for robotics workloads
This note is the operational payoff of the whole metrics kit. A robot runs a 100 Hz control loop beside perception and a large policy on one shared GPU. Shared context makes the control loop pay (p99 blows up 64×); a separate process makes the policy pay but the loop's tail still misses; MPS with the policy capped to 25–35% of the SMs returns the loop to its deadline at a modest cost to policy rate (C-KIT-NOTES L4). The deployable recipe: own MPS client per policy, SM cap 25–35%, perception at FP16, and keep CPU DRAM traffic well under 172 GB/s (C-KIT-NOTES L4). None of this is visible on a throughput dashboard — only p99 latency shows it ([[08-measuring-a-gpu]]).

## Terms introduced
- **CUDA context** — a process's GPU state; the GPU time-slices between contexts (A-PM; C-KIT-NOTES L4).
- **stream** — an ordered work queue within a context; concurrent but not isolating (C-KIT-NOTES B7).
- **block scheduler** — the hardware unit assigning blocks to SMs; bistable under contention (A-PM §1.2.2.1; C-KIT-NOTES B4).
- **MPS** — Multi-Process Service; processes share one context, optional per-client SM cap. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-KIT-NOTES B4; B-AMPERE).
- **SM reservation / cap** — `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE`, an MPS SM-fraction limit. Reused from the metrics-kit glossary (C-KIT-NOTES L4).
- **MIG** — Multi-Instance GPU; spatial partition isolating compute, cache and memory. Reused from the metrics-kit glossary (C-PLAT; B-AMPERE).
- **SM co-scheduling** — the block scheduler placing two kernels' blocks on the same SMs. Reused from the metrics-kit glossary (C-KIT-NOTES B4).
- **lockout onset** — the co-tenant occupancy above which the victim completes nothing; ≈8% Orin, ≈14% Thor. Reused from the metrics-kit glossary (C-KIT-NOTES B4).
- **controller contention** — slowdown from sharing the memory controller; onsets when the victim spills L2. Reused from the metrics-kit glossary (C-KIT-NOTES B4).
