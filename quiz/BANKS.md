# Quiz Banks

One row per bank: topic, section, knowledge-point count, question count, date generated.

## nvidia-gpu-anatomy — Anatomy of an NVIDIA GPU

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| nvidia-gpu-anatomy | 00-the-big-picture | 7 | 15 | 2026-10-07 |
| nvidia-gpu-anatomy | 01-sm-and-smsp | 9 | 24 | 2026-10-07 |
| nvidia-gpu-anatomy | 02-threads-warps-blocks-grids | 8 | 23 | 2026-10-07 |
| nvidia-gpu-anatomy | 03-occupancy-and-registers | 8 | 24 | 2026-10-07 |
| nvidia-gpu-anatomy | 04-cuda-cores-vs-tensor-cores | 8 | 21 | 2026-10-07 |
| nvidia-gpu-anatomy | 05-memory-hierarchy | 8 | 21 | 2026-10-07 |
| nvidia-gpu-anatomy | 06-caches-and-working-sets | 8 | 22 | 2026-10-07 |
| nvidia-gpu-anatomy | 07-sharing-the-gpu | 8 | 21 | 2026-10-07 |
| nvidia-gpu-anatomy | 08-measuring-a-gpu | 8 | 21 | 2026-10-07 |

**Totals:** 9 banks, 72 knowledge points, 192 questions.

Notes: every question is sourced to its note section and, where numeric, to a value in
`../nvidia-gpu-anatomy/constants.json` (via the note's citation). Distractors are drawn from each
note's own "Common confusions". The recently expanded sections were covered with dedicated
knowledge points: note 01 (warp instruction, issue-vs-latency, pipelining, CPU-vs-GPU latency
hiding, register-file banks), note 02 (shared memory + barrier, scope/ordering table), note 03
(what registers hold, registers vs L1/shared, spills), note 05 (registers are not a cache level),
note 06 (streaming vs dependent pointer chase).

## jetson-orin-thor-metrics — Jetson Orin/Thor: a Measured Reference for Robotics Workloads

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| jetson-orin-thor-metrics | 00-platforms | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | A1-fp-int-pipe-interleaving | 7 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | A2-cuda-core-ceilings | 6 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | A3-tensor-core-ceilings | 7 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | A4-nvfp4-ceiling | 7 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | A5-l1-bandwidth-ceiling | 5 | 11 | 2026-10-07 |
| jetson-orin-thor-metrics | A6-bandwidth-vs-footprint | 6 | 14 | 2026-10-07 |
| jetson-orin-thor-metrics | A7-latency-landmarks | 6 | 14 | 2026-10-07 |
| jetson-orin-thor-metrics | B1-copy-engine-dram-direction | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | B2-cache-level-interference | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | B3-matrix-profile-stall-decomposition | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | B4-gemm-victim-interference | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | B5-tensor-under-cpu-contention | 6 | 14 | 2026-10-07 |
| jetson-orin-thor-metrics | B6-cotenancy-interference-matrix | 7 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | B7-aggregate-throughput | 6 | 13 | 2026-10-07 |
| jetson-orin-thor-metrics | B8-cotenancy-real-shape-mix-ladder | 7 | 15 | 2026-10-07 |
| jetson-orin-thor-metrics | C1-pi05-solo-latency | 7 | 16 | 2026-10-07 |
| jetson-orin-thor-metrics | C2-cotenancy-under-gpu-load | 5 | 10 | 2026-10-07 |
| jetson-orin-thor-metrics | L4-scheduling-ladder | 8 | 16 | 2026-10-07 |

**Totals:** 19 banks, 120 knowledge points, 263 questions.

Notes: every numeric question draws its value and tolerance from `../jetson-orin-thor-metrics/constants.json`
via the note's citation (e.g. L2:DRAM ratio 12.4x/14.6x, lockout onset 8%/14%, 172 GB/s CPU floor,
pi0.5 90.06/53.03 ms, 1.40-1.50x prediction optimism). Questions favour mechanism, prediction-vs-
measurement gaps, and what-it-means-for-a-robot over raw recall; distractors are drawn from the
notes' own confusions (per-SM vs aggregate, controller contention vs SM lockout, same-direction vs
opposed streams, aggregate throughput vs tail latency, bytes vs TOPS).

**C2 is short (5 KPs, 10 questions):** its source section is unfinished — it carries only the
objective and metric, with no prediction/measurement/gap written yet — so the bank tests the stated
objective, the bimodal-median reasoning, the fixed-sharing-discipline design, and that the committed
answer lives in the L4 note. It is intentionally lighter than the other sections.
