# Quiz Banks

One row per bank: topic, section, knowledge-point count, question count, date generated.

## nvidia-gpu-anatomy — Anatomy of an NVIDIA GPU

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| nvidia-gpu-anatomy | 00-the-big-picture | 7 | 23 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 01-sm-and-smsp | 9 | 36 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 02-threads-warps-blocks-grids | 11 | 51 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 03-occupancy-and-registers | 10 | 45 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 04-cuda-cores-vs-tensor-cores | 12 | 55 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 05-memory-hierarchy | 9 | 36 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 06-caches-and-working-sets | 8 | 32 | expanded 2026-10-07 |
| nvidia-gpu-anatomy | 07-sharing-the-gpu | 9 | 36 | expanded 2026-10-07 |
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

## robot-workload-benchmarking — Benchmarking a robot workload: stack, metrics, method

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| robot-workload-benchmarking | A0-the-big-picture | 7 | 30 | 2026-10-22 |
| robot-workload-benchmarking | A1-depth-camera-and-odometry | 7 | 29 | 2026-10-22 |
| robot-workload-benchmarking | A2-people-perception | 7 | 28 | 2026-10-22 |
| robot-workload-benchmarking | A3-mapping-localization-navigation | 6 | 25 | 2026-10-22 |
| robot-workload-benchmarking | A4-locomotion-and-whole-body-control | 7 | 28 | 2026-10-22 |
| robot-workload-benchmarking | A5-audio-and-voice | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | A6-vla-and-large-models | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | A7-middleware-containers-and-platform | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | B0-cpu-metrics | 7 | 28 | 2026-10-22 |
| robot-workload-benchmarking | B1-gpu-power-memory-metrics | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | B2-rates-periods-and-latency | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | B3-deadlines-tails-and-statistics | 7 | 28 | 2026-10-22 |
| robot-workload-benchmarking | B4-profilers-and-the-observer-effect | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C0-reference-not-replica | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C1-predict-then-measure | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C2-solo-runs-and-levels | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C3-the-harness-and-fakes | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C4-windows-gates-and-validity | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C5-experimental-design | 7 | 28 | 2026-10-22 |
| robot-workload-benchmarking | C6-tiers-combined-runs-and-attribution | 6 | 24 | 2026-10-22 |
| robot-workload-benchmarking | C7-how-the-bench-can-lie | 7 | 28 | 2026-10-22 |

**Totals:** 21 banks (one per note: A0–A7, B0–B4, C0–C7), 134 knowledge points, 540 questions.

Notes: one bank per note. Every knowledge point carries 4–5 questions from distinct angles
(definition, mechanism, contrast, scenario, numeric); distractors are drawn from each note's own
"Common confusions". Numeric questions use only values the note states (via `constants.json`):
the 50 Hz / 20 ms control deadline, the 30 Hz camera rate, the 48-frames/packet → 3 ms → ~55 msg/s
audio framing, Silero VAD ~1.8M parameters, the sibling π0.5 53.03 ms latency, the 25–35% SM cap,
the 0.5 ms clock-offset bound, 120 s warm-up / 300 s window, the 0.3-core foreign-CPU gate, and the
~15 ms Nsight timeline-trace perturbation; each is cited to its `constants.json` key. Derived
numbers (e.g. the audio message rate) are asked with their inputs shown in the prompt. This kit is
public: no internal names, hosts, URLs, paths, or identifiers appear in any bank
(verified by grep). Validated with `node quiz/check-banks.js` → 0 errors.

## agentic-device-control — Agentic control of a consumer device

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| agentic-device-control | 00-why-cloud-initiated-device-agents | 6 | 15 | 2026-11-04 |
| agentic-device-control | 01-the-message-path | 6 | 16 | 2026-11-04 |
| agentic-device-control | 02-the-agent-graph | 6 | 16 | 2026-11-04 |
| agentic-device-control | 03-the-orchestrator | 6 | 15 | 2026-11-04 |
| agentic-device-control | 04-the-vision-specialist | 7 | 21 | 2026-11-04 |
| agentic-device-control | 05-the-actuator | 6 | 15 | 2026-11-04 |
| agentic-device-control | 06-the-react-loop | 6 | 16 | 2026-11-04 |
| agentic-device-control | 07-cost-and-latency | 6 | 22 | 2026-11-04 |
| agentic-device-control | 08-safety | 6 | 16 | 2026-11-04 |
| agentic-device-control | 09-evaluation | 6 | 18 | 2026-11-04 |

**Totals:** 10 banks (one per note, 00–09), 61 knowledge points, 170 questions
(mcq 71, tf 60, multi 17, numeric 22).

Notes: every knowledge point has 2–5 questions; every question cites its note section. Numbers were
loaded from the kit's `constants.json` at generation time, not retyped. Each is either public (ReAct
gains of 34 / 10 pp, the vendor's computer-use reference frame, screenshot token range and history
defaults, prompt-caching breakpoints, lifetimes and price multipliers) or labelled illustrative (task
time, tokens, limits, temperatures, evaluation counts). Derived numbers (coordinate scaling, cached-call
cost, 0.9⁵, 40/50) are asked with their inputs in the prompt. tf runs at about 35 %, because this
kit's notes are built around "Common confusions" and each confusion gets a true/false item. Notes
08 and 02 have no numbers, so their banks have no numeric questions. Validated with
`node quiz/check-banks.js` (0 errors); `tools/public-scan.sh` is clean.

## wifi-csi-sensing — Wi-Fi sensing with channel state information

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| wifi-csi-sensing | A0-why-sense-with-wifi | 8 | 24 | 2026-11-04 |
| wifi-csi-sensing | A1-csi-and-multipath | 8 | 26 | 2026-11-04 |
| wifi-csi-sensing | A2-what-the-hardware-gives-you | 7 | 22 | 2026-11-04 |
| wifi-csi-sensing | B1-preprocessing | 7 | 25 | 2026-11-04 |
| wifi-csi-sensing | B2-features | 7 | 25 | 2026-11-04 |
| wifi-csi-sensing | B3-classifiers-and-windows | 6 | 23 | 2026-11-04 |
| wifi-csi-sensing | B4-multi-device-joint-detection | 7 | 22 | 2026-11-04 |
| wifi-csi-sensing | B5-room-localisation-by-metric-learning | 6 | 22 | 2026-11-04 |
| wifi-csi-sensing | C1-kpis | 6 | 23 | 2026-11-04 |
| wifi-csi-sensing | C2-data-collection-campaigns | 6 | 21 | 2026-11-04 |
| wifi-csi-sensing | C3-coexistence | 5 | 19 | 2026-11-04 |
| wifi-csi-sensing | C4-sensing-endpoint-architecture | 5 | 19 | 2026-11-04 |
| wifi-csi-sensing | C5-limits-and-open-problems | 6 | 21 | 2026-11-04 |

**Totals:** 13 banks, 84 knowledge points, 292 questions (mcq 135, tf 78, multi 37, numeric 42).

Notes: one bank per note; every knowledge point has at least 3 questions. Every question's `source`
names the note section, and every numeric answer comes from the kit's `constants.json` (key cited in the
source), as public values (802.11 subcarrier counts and spacing, beacon interval, delay resolution,
Hampel constants, FaceNet margin) or values labelled illustrative. Derived numbers (Doppler bound 2 ÷
0.055, field TPR 0.5 ÷ 0.9, N² links, the false-alarm budget arithmetic in C1, the beacon CSI traffic in
C4) are asked with their inputs in the prompt. Choices were rewritten to similar lengths so the longest
choice does not give the answer away. **Inconsistency in the source note, not fixed here:** B4 says
adding device-to-device links gave a larger gain than going from one to four devices, but its
illustrative `devices_tpr_illustrative` values give +0.20 against +0.25. The bank does not ask about
the size of the two gains. Validated with `node quiz/check-banks.js` (0 errors);
`tools/public-scan.sh` is clean.

## device-log-anomaly-detection — Finding faults in a device fleet from logs and metrics

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| device-log-anomaly-detection | A0-why-fleets-need-log-analysis | 6 | 16 | 2026-11-04 |
| device-log-anomaly-detection | A1-what-a-device-log-is | 7 | 17 | 2026-11-04 |
| device-log-anomaly-detection | A2-fleet-metrics | 6 | 17 | 2026-11-04 |
| device-log-anomaly-detection | B1-log-parsing-to-templates | 7 | 19 | 2026-11-04 |
| device-log-anomaly-detection | B2-windows-and-count-vectors | 7 | 18 | 2026-11-04 |
| device-log-anomaly-detection | B3-anomaly-detection-on-logs | 8 | 20 | 2026-11-04 |
| device-log-anomaly-detection | B4-fleet-trend-detection | 7 | 18 | 2026-11-04 |
| device-log-anomaly-detection | B5-from-anomaly-to-root-cause | 7 | 18 | 2026-11-04 |
| device-log-anomaly-detection | B6-clustering-and-reporting | 7 | 18 | 2026-11-04 |
| device-log-anomaly-detection | C1-the-ground-truth-problem | 6 | 17 | 2026-11-04 |
| device-log-anomaly-detection | C2-template-engineering | 6 | 18 | 2026-11-04 |
| device-log-anomaly-detection | C3-data-quality | 6 | 18 | 2026-11-04 |
| device-log-anomaly-detection | C4-lessons | 7 | 19 | 2026-11-04 |
| device-log-anomaly-detection | C5-from-service-to-tool | 7 | 18 | 2026-11-04 |

**Totals:** 14 banks (one per note), 94 knowledge points, 251 questions
(mcq 136, tf 67, multi 23, numeric 25).

Notes: every knowledge point has 2–4 questions; every question cites its note section. Sources are
the kit's notes, glossary and `constants.json` only. Numbers were loaded from `constants.json` at
generation time, not retyped. They are either public (isolation-forest ψ = 256, t = 100, height
limit 8, c(256) ≈ 10.24, the 0.5 and 0.82 scores; DeepLog g = 9; Drain's 5 data sets; He et al.'s
HDFS 16,838 / 575,061 count vectors; IEEE 802.11 reason codes 2 and 15; the Phred factor 10 and
score examples) or labelled illustrative (lines per device-day, family sizes and standard errors,
ground-truth funnel and Wilson intervals, pilot tickets, flagged windows, time per case). Derived
numbers (√2 SE growth, 2.93 % HDFS anomaly share, 93 windows, 83 % time saved, 6× speed-up, 100
chance alarms) are asked with their inputs in the prompt. Two counts come from note text, not
constants: the four-step retraining cascade (C2) and √2 (A2). B6 has no numeric question because its
note states no number worth asking (its only number is an illustrative ticket volume). tf is about
27 %, because each "Common confusions" item gets a true/false question. Validated with
`node quiz/check-banks.js` (0 errors); `tools/public-scan.sh` is clean.

## robot-stack-contention — Robot stack contention: why every service slows in the full stack

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| robot-stack-contention | A0-the-big-picture | 7 | 31 | 2026-11-04 (QAE review) |
| robot-stack-contention | A1-cpu-queueing-on-a-shared-pool | 8 | 32 | 2026-11-04 |
| robot-stack-contention | A2-same-work-more-cycles | 8 | 34 | 2026-11-04 |
| robot-stack-contention | A3-priorities-in-containers | 8 | 32 | 2026-11-04 |
| robot-stack-contention | A4-costs-that-grow-with-history | 8 | 33 | 2026-11-04 |
| robot-stack-contention | A5-where-to-put-the-observers | 8 | 32 | 2026-11-04 |
| robot-stack-contention | B1-gpu-time-slicing-and-the-dose-curve | 9 | 39 | 2026-11-04 |
| robot-stack-contention | B2-low-issue-rate-is-not-free-room | 7 | 33 | 2026-11-04 |
| robot-stack-contention | B3-mps-in-practice | 9 | 36 | 2026-11-04 |
| robot-stack-contention | B4-compute-bound-or-near-the-ridge | 8 | 33 | 2026-11-04 (QAE review) |
| robot-stack-contention | C1-deployment-fidelity-and-batch-1-latency | 8 | 32 | 2026-11-04 |

**Totals:** 11 banks (one per note), 88 knowledge points, 367 questions
(mcq 162, tf 117, numeric 72, multi 16). Every knowledge point has 4–6 questions.

Notes: sources are the kit's notes, glossary and `constants.json` only. Every number was loaded from
`constants.json` by key at generation time; illustrative values are called illustrative in the
explanation, and derived values (wait share 0.5, probe share ≈ 0.92, C\* ≈ 100 ms, ridges ≈ 240 and
≈ 976 FLOP/B (≈ 743 FLOP/B at Thor's read peak, `dram_read_thor`), 0.75 / 0.6 s per s, ≈ 3.3 calls/s, 4 Hz) are asked with their inputs in the prompt and
labelled "my estimate". Each correction gets a tf or mcq on the confusion itself: GPU sharing alone
cost the camera nothing with an idle pool (GPU plus pool load not tested), nice inside a container is
not a priority test, the encoder's miss was the wrong prediction form, a low issue rate is not free room, more SMs help multi-wave kernels, no SM contention
without MPS, and most of the interaction service's rise was the measurement probe. Verdict wording is
kept as pre-registered ("undecided at dose", "about two thirds" on the class line). tf is about 32 %
because the kit is correction-heavy; multi is low (about 4 %) and A1 has none, because few notes have
select-all seams.

QAE review (2026-11-04): fixed a second-correct distractor (B4 q5), aligned wording with the revised
notes ("model version", baseline / moved arms and X_base / X_moved, B3's "suppose ... two Linux
users", C1's desktop-session advice), wave count as a ceiling, shared memory as the fourth residency
limit, units in numeric prompts; added two A0 correction questions and one B4 numeric (Thor ridge at
the read peak). All ids and KPs kept. Validated with `node quiz/check-banks.js` (0 errors); `tools/public-scan.sh` is clean.

## agentic-research-harness — Running optimization research with AI agents

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| agentic-research-harness | A0-why-research-needs-a-different-setup | 7 | 21 | 2026-11-04 |
| agentic-research-harness | A1-the-order-of-construction | 6 | 20 | 2026-11-04 |
| agentic-research-harness | B1-reference-and-baseline | 6 | 22 | 2026-11-04 |
| agentic-research-harness | B2-the-frozen-evaluator | 6 | 22 | 2026-11-04 |
| agentic-research-harness | B3-negative-controls | 7 | 23 | 2026-11-04 |
| agentic-research-harness | B4-evidence-records | 6 | 19 | 2026-11-04 |
| agentic-research-harness | B5-the-candidate-contract | 6 | 19 | 2026-11-04 |
| agentic-research-harness | B6-the-two-memories | 6 | 19 | 2026-11-04 |
| agentic-research-harness | B7-agents-and-the-loop | 7 | 26 | 2026-11-04 |
| agentic-research-harness | B8-reporting | 6 | 20 | 2026-11-04 |
| agentic-research-harness | C1-instantiating-a-topic | 6 | 20 | 2026-11-04 |
| agentic-research-harness | C2-the-scheduling-topic | 7 | 26 | 2026-11-04 |
| agentic-research-harness | C3-calibration | 8 | 27 | 2026-11-04 |
| agentic-research-harness | C4-lessons-about-the-method | 6 | 22 | 2026-11-04 |
| agentic-research-harness | C5-the-checklist | 6 | 20 | 2026-11-04 |

**Totals:** 15 banks (one per note), 96 knowledge points, 326 questions
(mcq 148, tf 92, multi 41, numeric 45). Every knowledge point has 3–5 questions.

Notes: sources are the kit's notes, glossary and `constants.json` only. Every number was loaded from
`constants.json` by key at generation time. First-campaign values (`c1_*`) and the scheduling simulator's
values (`sched_*`, `topic_*`, `harness_*`) are called illustrative (design parameter or demonstration run)
in the prompt or explanation; public values (Goodhart, Strathern, Popper, ReAct, Liu & Layland, HEFT,
Amdahl, the 0.5 and 1/C(40,20) null probabilities) keep their real values. Derived values (4× and 12 %
for the illustrative campaign shape, 1.1 ms headroom above the first floor, 6.9 ms from placement, 16×
launch understatement, overall binding = max of the per-set values) are asked with their inputs in the
prompt and labelled "my arithmetic". B5 has no numeric questions because the note has no numbers. tf is
about 28 % because each "Common confusions" entry gets a tf on the confusion itself. An mcq length-cue
lint (answer not clearly the longest choice) was applied to every bank. Validated with
`node quiz/check-banks.js` (0 errors); `tools/public-scan.sh learning/agentic-research-harness` and a scan
of the new banks, `manifest.js` and this file are clean.

## hri-experience-platform — A platform for many robot experiences

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| hri-experience-platform | A0-one-experience-versus-many | 8 | 26 | 2026-11-04 |
| hri-experience-platform | A1-the-reasoner-and-the-coordinator | 7 | 25 | 2026-11-04 |
| hri-experience-platform | B1-experiences-as-reducers | 8 | 27 | 2026-11-04 |
| hri-experience-platform | B2-state-ownership | 8 | 26 | 2026-11-04 |
| hri-experience-platform | B3-the-effect-vocabulary | 8 | 31 | 2026-11-04 |
| hri-experience-platform | B4-kernel-interception-and-arbitration | 8 | 26 | 2026-11-04 |
| hri-experience-platform | B5-registration-selection-switching | 8 | 26 | 2026-11-04 |
| hri-experience-platform | B6-conversation-and-model-boundaries | 8 | 26 | 2026-11-04 |
| hri-experience-platform | C1-simulation-first | 8 | 26 | 2026-11-04 |
| hri-experience-platform | C2-the-conformance-ladder | 8 | 27 | 2026-11-04 |
| hri-experience-platform | C3-regeneration-and-comparison | 8 | 25 | 2026-11-04 |
| hri-experience-platform | C4-the-observatory | 8 | 26 | 2026-11-04 |
| hri-experience-platform | C5-migrating-from-a-single-state-tracker | 8 | 28 | 2026-11-04 |

**Totals:** 13 banks (one per note), 103 knowledge points, 345 questions
(mcq 170, tf 111, multi 40, numeric 24). Every knowledge point has 3–5 questions; every bank has all four types.

Notes: sources are the kit's notes, glossary and `constants.json` only. Every number was loaded from
`constants.json` by key at generation time; all design limits are called illustrative in the prompt or
explanation, and the ROS 2 default history depth is public. Derived values (one profile-matrix cycle and the
serial total in B5, 3 turns × 8 s in B6, the settle-deadline clamp in C3) are asked with their inputs in the
prompt and labelled "my arithmetic". A1 and B4 have no constants, so their only numeric questions are counts
of items the note lists (three reasons, five priority levels); likewise the lifecycle-phase, contract-kind and
first-registry counts elsewhere. Numeric is lighter (~7 %) and tf heavier (~32 %) than the target because the
notes are design rules with few numbers and many "Common confusions". mcq choices are shuffled deterministically
at generation and passed a length-cue lint. Validated with `node quiz/check-banks.js` (0 errors);
`tools/public-scan.sh` over the kit, the new banks, `manifest.js` and this file is clean.

## public-robot-interaction-design

| Topic | Section | KPs | Questions | Date |
|---|---|---|---|---|
| public-robot-interaction-design | A0-why-strangers-are-the-hard-case | 7 | 28 | 2026-11-04 |
| public-robot-interaction-design | A1-the-experience-as-a-state-machine | 7 | 28 | 2026-11-04 |
| public-robot-interaction-design | A2-beats-and-dwell-budget | 7 | 30 | 2026-11-04 |
| public-robot-interaction-design | A3-consent-and-privacy-by-design | 8 | 34 | 2026-11-04 |
| public-robot-interaction-design | B1-the-voice-pipeline | 8 | 33 | 2026-11-04 |
| public-robot-interaction-design | B2-who-is-speaking | 8 | 40 | 2026-11-04 |
| public-robot-interaction-design | B3-gaze | 8 | 39 | 2026-11-04 |
| public-robot-interaction-design | B4-turn-taking-and-self-hearing | 8 | 37 | 2026-11-04 |
| public-robot-interaction-design | B5-behaviours-from-language | 9 | 39 | 2026-11-04 |
| public-robot-interaction-design | B6-ambient-awareness | 8 | 34 | 2026-11-04 |
| public-robot-interaction-design | C1-failure-and-degradation-ux | 8 | 37 | 2026-11-04 |
| public-robot-interaction-design | C2-the-validation-ladder | 8 | 35 | 2026-11-04 |
| public-robot-interaction-design | C3-lessons-from-a-live-show | 7 | 28 | 2026-11-04 |

**Totals:** 13 banks (one per note), 101 knowledge points, 442 questions
(mcq 224, tf 128, multi 31, numeric 59). Every knowledge point has 4–7 questions; every bank has all four types.

Notes: sources are the kit's notes, glossary and `constants.json` only. Every number was loaded from
`constants.json` by key at generation time. Public values (Stivers turn gap, Nielsen limits, Argyle/Vertegaal
gaze figures, Carpenter saccade, Hall proxemics, TDOA and aliasing arithmetic, GDPR ages, WCAG flash limit,
Landis & Koch κ, Fisher p-values) keep their citation; design values are called illustrative in the prompt or
explanation. Derived values (beat sum, cycle → throughput → visits per day, half of the scripted reach beat,
alternation duty, saccade at 40°, pre-roll bytes) are asked with their inputs in the prompt. Two numerics are
counts from the note (one reasoner-state publisher in B1, four conversation-ladder rungs in C1). tf is about
29 % because the notes carry many "Common confusions". mcq choices are shuffled deterministically and passed a
length-cue lint. Validated with `node quiz/check-banks.js` (0 errors).
