# Learning kits

Study material generated with a four-rung learning method (notes → diagrams → interactive explorers → explainer video) plus a spaced-repetition quiz. Everything is a single-file, no-build artifact; every number cites its source.

**Quiz:** open `quiz/index.html` locally, or on GitHub Pages at `/quiz/`.

| Kit | What it covers |
|---|---|
| [`jetson-orin-thor-metrics/`](jetson-orin-thor-metrics/README.md) | Study notes on a measured reference for NVIDIA Jetson Orin and Thor under robotics workloads: compute and memory ceilings, interference and contention, real VLA models, GPU-sharing disciplines. |
| [`robot-workload-benchmarking/`](robot-workload-benchmarking/README.md) | How to benchmark a robot's on-board compute: what each part of a typical stack does (depth camera, people perception, mapping, control, voice, VLA), what each metric means and how it is collected (CPU quota and throttling, run-queue wait, GPU busy, latency and clocks, deadline statistics, profilers), and why such a campaign is designed the way it is (predict then measure, solo levels, off-board harness, validity gates, pre-registration, how the bench can lie). |
| [`nvidia-gpu-anatomy/`](nvidia-gpu-anatomy/README.md) | A concept primer for readers new to the terms: SMs and sub-partitions, warps/blocks/grids, occupancy and registers, CUDA vs tensor cores, the memory hierarchy, caches and working sets, sharing a GPU, measuring a GPU. |

Each kit has `notes/`, `glossary.md`, `constants.json` (every constant with its source), `diagrams/` (draw.io + SVG/PNG), `explorers/` (interactive HTML), `videos/` (MP4 + captions) and `SOURCES.md`.

The quiz (`quiz/`) draws one question bank per note; wrong answers push the underlying knowledge point into more frequent review (Leitner boxes). Progress is stored in the browser only.

Study aids, not primary sources. Numbers are quoted from the listed sources or labelled as estimates.
