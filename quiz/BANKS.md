# Quiz Banks

One row per bank: topic, section, knowledge-point count, question count, date generated.

## nvidia-gpu-anatomy — Anatomy of an NVIDIA GPU

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| nvidia-gpu-anatomy | 00-the-big-picture | 7 | 23 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 01-sm-and-smsp | 9 | 36 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 02-threads-warps-blocks-grids | 10 | 45 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 03-occupancy-and-registers | 10 | 42 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 04-cuda-cores-vs-tensor-cores | 12 | 55 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 05-memory-hierarchy | 9 | 36 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 06-caches-and-working-sets | 8 | 32 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 07-sharing-the-gpu | 8 | 31 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 08-measuring-a-gpu | 8 | 32 | expanded 2026-10-07 |

**Totals:** 9 banks, 72 knowledge points, 284 authored questions (294 after board-template expansion).

Notes: every question is sourced to its note section and, where numeric, to a value in
`../nvidia-gpu-anatomy/constants.json` (via the note's citation). Distractors are drawn from each
note's own "Common confusions". **Expanded 2026-10-07:** every knowledge point now carries 4–5
questions spanning distinct angles (definition / mechanism / contrast / scenario / numeric). All
existing question ids and knowledge points were preserved. Single-board numerics were converted to
board templates (`template.vars.board` + `values{orin,thor}` + `answerFrom`/`answerByBoard`) so the
same point is asked on both boards from `constants.json`: max blocks per SM (16/24), register-file
size (4/5 MB), CUDA FP16 multiple (1.87/1.01×), L2:DRAM ratio (12.4/14.6×), DRAM & L1 latency
(675/510, 29.9/25.3 ns), eviction penalty (4.6/3.3×), lockout onset (8/14%), controller-contention
peak (1.53/2.53×). Derived-number questions (the 1.51× clock × SM-count rule, the 63% and 60.7%
datasheet fractions) now show their inputs in the prompt or ask which kernel class the rule applies
to, rather than asking for a memorised product.

## jetson-orin-thor-metrics — Jetson Orin/Thor: a Measured Reference for Robotics Workloads

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| jetson-orin-thor-metrics | 00-platforms | 6 | 24 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A1-fp-int-pipe-interleaving | 7 | 28 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A2-cuda-core-ceilings | 6 | 25 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A3-tensor-core-ceilings | 7 | 28 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A4-nvfp4-ceiling | 7 | 28 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A5-l1-bandwidth-ceiling | 5 | 21 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A6-bandwidth-vs-footprint | 6 | 24 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | A7-latency-landmarks | 6 | 24 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B1-copy-engine-dram-direction | 6 | 25 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B2-cache-level-interference | 6 | 24 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B3-matrix-profile-stall-decomposition | 6 | 25 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B4-gemm-victim-interference | 6 | 24 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B5-tensor-under-cpu-contention | 6 | 25 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B6-cotenancy-interference-matrix | 7 | 28 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B7-aggregate-throughput | 6 | 25 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | B8-cotenancy-real-shape-mix-ladder | 7 | 28 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | C1-pi05-solo-latency | 7 | 30 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | C2-cotenancy-under-gpu-load | 5 | 20 | expanded 2026-10-07 |
| jetson-orin-thor-metrics | L4-scheduling-ladder | 8 | 32 | expanded 2026-10-07 |

**Totals:** 19 banks, 120 knowledge points, 488 authored questions (505 after board-template
expansion). Every knowledge point now carries 4-5 questions from distinct angles (definition,
mechanism, contrast, scenario, numeric).

**Expanded 2026-10-07 (EXPAND MODE):** every existing question id and knowledge point was kept
unchanged. Each KP was raised to 4-5 questions. Single-board numerics with both-board values in
`constants.json` were converted to board templates (`{Board}`/`{name}`, one variant per board):
00 L2 size; A3 classic FP16; A5 per-SM/aggregate L1; A6 L2:DRAM ratio, L2 and DRAM plateaus; A7
L1/L2/DRAM latency (ns and cycles); B2 chase plateau; B4 lockout onset, controller peak; B5
bandwidth cliff; B6 one-sided slowdown; B8 WBC solo p99. Derived-number questions were rewritten
to show their inputs rather than ask for the memorised product: the 1.51x clock x SM-count scaling
(00 q9 now gives 1.575x20 and 1.30x16), the tcgen05-vs-classic 3.0x (A3 q4 gives 192.5 and 64.4),
and the L1 clock-ratio 1.2x (A5 q7 gives 1.575 and 1.30 GHz). Fraction-of-datasheet questions
already carried their numerator and denominator in the prompt and were left as measured-value
questions.

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
