# Sources — Benchmarking a robot's on-board compute workload

This kit teaches a general method and a general stack. It carries no measured numbers from any
specific robot or campaign.

## What this kit is

Study notes (rung 1 of a four-rung learning kit: notes → diagram → explorer → video) for one
question: **how do you benchmark the compute workload of a home robot that runs its whole software
stack on one small on-board computer?** The notes describe the stack (Part A), the metrics you
collect (Part B), and the experimental method that makes the result trustworthy (Part C).

The reader is assumed to have read the two sibling kits and will not be re-taught their content:

- [`../nvidia-gpu-anatomy/`](../nvidia-gpu-anatomy/) — what an SM, warp, L2 cache, CUDA context,
  and roofline are.
- [`../jetson-orin-thor-metrics/`](../jetson-orin-thor-metrics/) — how a shared integrated SoC
  behaves under load, the roofline, co-tenancy, GPU sharing discipline (MPS / SM cap), and the
  deployed-model latency numbers for two example boards.

Where a term is defined in a sibling kit, these notes link to it rather than re-defining it.

## Provenance of the method

The method described in Part C — predict-then-measure budgets, solo-before-combined runs, a
two-machine harness with faked hardware, pre-registration, interleaved A/B order, validity gates,
and a catalogue of bench artefacts — is abstracted from an internal benchmarking campaign the
author studied. **No internal material is reproduced here:** no measured number, no name, no path,
no hostname, no identifier of any kind from that campaign appears in this kit. The notes state the
generic idea only. Every number in this kit is one of:

1. **A public source** — a model paper, or official NVIDIA / Linux kernel / ROS / Stereolabs
   documentation — cited inline with a URL.
2. **A value already in a sibling kit**, cited by its `constants.json` key or note name.
3. **A clearly labelled "illustrative" round number**, invented to explain an idea, never a
   measurement.

See [`constants.json`](constants.json): every entry carries a `source` field that is one of these
three classes.

## Public sources cited

Models and libraries (what each does and how it works is taken from the paper or official docs):

- YOLOX — Ge et al., "YOLOX: Exceeding YOLO Series in 2021", arXiv:2107.08430,
  https://arxiv.org/abs/2107.08430
- SCRFD — Guo et al., "Sample and Computation Redistribution for Efficient Face Detection",
  arXiv:2105.04714, https://arxiv.org/abs/2105.04714
- ArcFace — Deng et al., "ArcFace: Additive Angular Margin Loss for Deep Face Recognition",
  arXiv:1801.07698, https://arxiv.org/abs/1801.07698
- OSNet — Zhou et al., "Omni-Scale Feature Learning for Person Re-Identification",
  arXiv:1905.00953, https://arxiv.org/abs/1905.00953
- BlazePose — Bazarevsky et al., "BlazePose: On-device Real-time Body Pose tracking",
  arXiv:2006.10204, https://arxiv.org/abs/2006.10204
- Light-ASD — Liao et al., "A Light Weight Model for Active Speaker Detection", CVPR 2023,
  https://arxiv.org/abs/2303.04439
- Silero VAD — Silero Team, https://github.com/snakers4/silero-vad
- openWakeWord — D. Scripka, https://github.com/dscripka/openWakeWord
- ECAPA-TDNN — Desplanques et al., "ECAPA-TDNN: Emphasized Channel Attention, Propagation and
  Aggregation in TDNN Based Speaker Verification", arXiv:2005.07143,
  https://arxiv.org/abs/2005.07143
- DISK — Tyszkiewicz et al., "DISK: Learning local features with policy gradient",
  arXiv:2006.13566, https://arxiv.org/abs/2006.13566
- LightGlue — Lindenberger et al., "LightGlue: Local Feature Matching at Light Speed", ICCV 2023,
  arXiv:2306.13643, https://arxiv.org/abs/2306.13643
- MixVPR — Ali-bey et al., "MixVPR: Feature Mixing for Visual Place Recognition", WACV 2023,
  https://arxiv.org/abs/2303.02190
- TSDF / VoxelBlockGrid — Open3D documentation, http://www.open3d.org/docs/release/
- iSAM2 — Kaess et al., "iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree",
  IJRR 2012; GTSAM documentation, https://gtsam.org/
- GR00T N1 — NVIDIA, "GR00T N1: An Open Foundation Model for Generalist Humanoid Robots",
  arXiv:2503.14734, https://arxiv.org/abs/2503.14734
- π0 / π0.5 — Physical Intelligence, "π0: A Vision-Language-Action Flow Model",
  https://www.physicalintelligence.company/blog/pi0 ; "π0.5",
  https://www.physicalintelligence.company/blog/pi05
- Whisper — Radford et al., "Robust Speech Recognition via Large-Scale Weak Supervision",
  arXiv:2212.04356, https://arxiv.org/abs/2212.04356

Platform, OS, and tooling documentation:

- ROS 2 concepts and QoS — https://docs.ros.org/en/rolling/Concepts.html and
  https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html
- Zenoh (pub/sub router) — https://zenoh.io/docs/
- Linux control groups v2 (cpu.max, cpu.stat, memory.current) —
  https://docs.kernel.org/admin-guide/cgroup-v2.html
- CFS bandwidth control — https://docs.kernel.org/scheduler/sched-bwc.html
- /proc/stat, /proc/schedstat — https://docs.kernel.org/filesystems/proc.html
- isolcpus / cpusets — https://docs.kernel.org/admin-guide/kernel-parameters.html and
  https://docs.kernel.org/admin-guide/cgroup-v1/cpusets.html
- NVIDIA Nsight Systems — https://docs.nvidia.com/nsight-systems/
- NVIDIA Nsight Compute — https://docs.nvidia.com/nsight-compute/
- `nvidia-smi` utilization.gpu definition — NVIDIA System Management Interface documentation,
  https://developer.nvidia.com/system-management-interface
- `tegrastats` — NVIDIA Jetson Linux Developer Guide,
  https://docs.nvidia.com/jetson/archives/r36.4/DeveloperGuide/
- NVENC / H.264 hardware encode — NVIDIA Video Codec SDK,
  https://developer.nvidia.com/video-codec-sdk
- Stereolabs ZED SDK (stereo depth, neural depth, positional tracking/VIO) —
  https://www.stereolabs.com/docs/
- SNTP / NTP time synchronisation — RFC 4330, https://www.rfc-editor.org/rfc/rfc4330 ;
  RFC 5905, https://www.rfc-editor.org/rfc/rfc5905
- Garwood confidence interval for a Poisson rate — Garwood (1936), "Fiducial limits for the
  Poisson distribution", Biometrika 28; standard exact Poisson interval.
- Moving-block bootstrap — Künsch (1989), "The jackknife and the bootstrap for general stationary
  observations", Annals of Statistics 17.
- One Euro filter — Casiez et al., "1€ Filter: A Simple Speed-based Low-pass Filter for Noisy Input
  in Interactive Systems", CHI 2012, https://gery.casiez.net/1euro/

## How the material was read

- Public papers and docs were read from their official URLs (listed above).
- The sibling kits were read from this workspace: `../nvidia-gpu-anatomy/` and
  `../jetson-orin-thor-metrics/` (their `README.md`, `glossary.md`, `constants.json`, and notes).
- The method was learned from internal campaign documents, then abstracted. Those documents are
  not cited, quoted, or linked, by binding rule.

## Public-safety scan

A case-insensitive `grep -rniE` scan was run over the whole kit folder before publishing, using a
regex alternation of every forbidden project codename, company name, internal hostname prefix,
person alias, internal tool/registry name, two-digit issue marker (`#NN`), campaign/feature number,
and the two internal repository numbers. The regex itself is deliberately not reproduced here, so
that this file does not match its own scan.

**public-safety scan: 0 hits.**

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per
  concept, caveats before results, numbers with units.
- "The reference robot" / "a home robot's software stack" / "a benchmarking campaign" are the
  generic subjects; no specific product is named.
- Illustrative numbers are marked "illustrative" in the text and labelled `illustrative` in
  `constants.json`.
- Obsidian-style `[[wikilinks]]` connect notes inside this kit; relative Markdown links reach the
  sibling kits.

## Rung 2 — Diagrams (learn-diagram)

Six diagrams were built under [`diagrams/`](diagrams/), one draw.io page each, each exported to
`.drawio` + `.svg` + `.png`, with a per-diagram spec recorded in
[`diagrams/INDEX.md`](diagrams/INDEX.md):

1. `01-stack-as-pipelines` — the stack as concurrent sense/perceive/decide/act pipelines on a
   shared/service/isolated-control core floor (Notes A0–A7).
2. `02-people-perception-pipeline` — per-frame vs per-person stages, GPU vs CPU split, where cost
   grows with N (Note A2).
3. `03-solo-levels` — nested L1 within L2 within L3, the gaps, idle floor vs working cost (Note C2).
4. `04-bench-topology` — robot computer + separate harness machine, fakes/stubs/synthetic/bag,
   dedicated control link vs bulk link, two islands, observer core, SNTP probe (Note C3; A2–A5,
   B0/B2/B4).
5. `05-metric-collection-map` — each metric's source and pitfall, grouped CPU / GPU+memory /
   rates+latency+stats / profilers (Notes B0–B4).
6. `06-campaign-flow` — predict → pre-register → solo → review → combined tiers (seeded interleaved)
   → validity gates (valid/flagged/void) → carries verdict → first-limit attribution; addenda/
   supersede loop only for harness bugs (Notes C1, C4, C5, C6; C2).

Every number on every canvas is loaded from this kit's `constants.json` (with its `source` field) or
cited to a public source / sibling kit on the canvas itself; no measured robot or campaign number
appears. Each canvas has its own legend and sources footnote. The diagrams were authored as
`diagrams/specNN.py` cell lists and rendered by `diagrams/.render_local.py` (editable `.drawio`, a
self-rendered standalone `.svg`, and a headless-Chrome PNG at 2×) because the draw.io MCP export
pipeline was unavailable in this environment; the self-rendered SVGs carry no draw.io "Text is not
SVG" banner. A combined 6-page `diagrams/robot-workload-benchmarking.drawio` is provided for viewing
all pages at once.

**Public-safety scan (rung 2):** the same case-insensitive scan was re-run over every file written
under `diagrams/`. **public-safety scan: 0 hits.**

## Rung 3 — explorers (learn-explorer)

Three single-file, no-build, double-click HTML explorers live in [`explorers/`](explorers/), each
with its spec at the top of [`explorers/INDEX.md`](explorers/INDEX.md):

- `01-cpu-quota-and-throttling.html` (notes A7, B0) — a CFS bandwidth quota (`cpu.max` =
  quota/period) caps delivered cores against demand; `throttled_usec` is summed over per-core
  run-queues and is **not** unmet demand; the honest reading is the fraction of periods exhausted,
  with the deployed quota as the baseline.
- `02-deadline-misses-and-sample-size.html` (notes B3, C4, C6) — the exact two-sided **Garwood**
  Poisson 95% interval on a miss rate, computed in-page (chi-square quantile via an inverse
  regularized incomplete-gamma); PASS/UNRESOLVED/FAIL against user-set bands; and a sample-size
  panel showing a stable p99 needs several thousand samples (~3000 → ~30 tail points).
- `03-perception-scaling-with-people.html` (notes A2, C1) — per-frame latency on GPU and on CPU as
  N people grow, which side binds, the crossover N where CPU post-processing overtakes the GPU, and
  how a software rate cap hides the real compute limit. All per-frame / per-person times are
  slider inputs, labelled illustrative.

Parameters are copied from [`constants.json`](constants.json) into
[`explorers/params.json`](explorers/params.json) (and inlined in each page) with their original
`class` and `source`; nothing is retyped. Every page renders the sources table from that block.

Verification: each page's prediction functions are factored into a pure IIFE that also runs under
node. All three pass their `console.assert` self-tests — including the standard Garwood bounds
(0 misses in 30 min → upper ≈ 0.123/min; 12 misses in 30 min → [0.207, 0.699]/min) — and a NaN
sweep over every slider/selector extreme (964 outputs checked, 0 non-finite). Each page was rendered
headlessly and the screenshot read back. Accessibility: labelled controls, a live region for the
headline, colour-plus-text labels, `prefers-reduced-motion` honoured, contrast ≥ 4.5:1.

**public-safety scan (rung 3):** the `grep -rniE` scan of the forbidden-term alternation was re-run
over every file written in this rung (`explorers/*.html`, `explorers/params.json`,
`explorers/INDEX.md`, this section) — **0 hits**.

## Rung 4 — video (learn-video)

One short explainer video lives under [`videos/`](videos/), with its spec at the top of
[`videos/INDEX.md`](videos/INDEX.md):

- `01-measuring-a-robot-stack/out/measuring-a-robot-stack.mp4` (~3m16s, 720p30) — **"Measuring a
  robot's brain without fooling yourself."** Nine scenes: (1) the stack as concurrent pipelines on
  one computer; (2) the two questions — does it fit, what runs out first; (3) predict-then-measure
  with the budget ledger `t = FLOP/R + bytes/B + CPU` and why batch-1 models are launch-bound (the
  van stuck at traffic lights); (4) the three solo levels L1/L2/L3, the gaps, idle floor vs driven
  working cost; (5) the two-machine harness with fake boards, cloud stubs, synthetic people; (6) how
  the bench can lie (shared-link bus slip, interrupts on core 0, tracing perturbation, all-zero
  data); (7) windows, gates, interleaving and pre-registration; (8) combine and attribute the first
  limit, often CPU quota before GPU; (9) a sources card.

Every number shown is loaded from this kit's `constants.json` / `explorers/params.json` with its
class, and is tagged **illustrative** on screen where its class is `illustrative` (camera 30 Hz,
perception 10 Hz, control 50 Hz / 20 ms; warm-up 120 s, window 300 s; the `nsys` ~15 ms
perturbation; the 434 Hz-vs-500 Hz shared-link example from C7). Public values carry their source.
**No measured robot or campaign number appears.** The narration was produced by the Kokoro helper
(voice `af_heart`), the animation by Manim Community 0.21 from the shared venv using `Text` (no
LaTeX), and the assembly by `ffmpeg`; the title card is a Manim scene because `ffmpeg`'s `drawtext`
was unavailable in this environment. Four frames of the final video were extracted and read back for
legibility, overlap, and number-correctness before finishing; the total duration is ~196 s.

**public-safety scan (rung 4):** the `grep -rniE` scan of the forbidden-term alternation was re-run
over every file written in this rung (`videos/INDEX.md`, `videos/01-measuring-a-robot-stack/`
storyboard, narration, scene sources, scripts, and the `.srt`, plus this section) — **0 hits**.
