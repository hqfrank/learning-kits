# Learning kits

Study material generated with a four-rung learning method (notes → visual story → diagrams → interactive explorers → explainer video) plus a spaced-repetition quiz. Everything is a single-file, no-build artifact; every number cites its source.

**Quiz:** open `quiz/index.html` locally, or on GitHub Pages at `/quiz/`.

| Kit | What it covers |
|---|---|
| [`jetson-orin-thor-metrics/`](jetson-orin-thor-metrics/README.md) | Study notes on a measured reference for NVIDIA Jetson Orin and Thor under robotics workloads: compute and memory ceilings, interference and contention, real VLA models, GPU-sharing disciplines. |
| [`robot-workload-benchmarking/`](robot-workload-benchmarking/README.md) | How to benchmark a robot's on-board compute: what each part of a typical stack does (depth camera, people perception, mapping, control, voice, VLA), what each metric means and how it is collected (CPU quota and throttling, run-queue wait, GPU busy, latency and clocks, deadline statistics, profilers), and why such a campaign is designed the way it is (predict then measure, solo levels, off-board harness, validity gates, pre-registration, how the bench can lie). |
| [`robot-stack-contention/`](robot-stack-contention/README.md) | Why a robot software stack runs slower than its parts when they share one board, and how to find each service's own reason: CPU queueing on a shared pool, same work at more cycles, priorities in containers, costs that grow with history, where to put the observers, GPU time-slicing and the dose curve, why a low issue rate is not free room, MPS in practice, compute-bound or near the ridge, deployment fidelity and batch-1 latency. All measurements are illustrative. |
| [`nvidia-gpu-anatomy/`](nvidia-gpu-anatomy/README.md) | A concept primer for readers new to the terms: SMs and sub-partitions, warps/blocks/grids, occupancy and registers, CUDA vs tensor cores, the memory hierarchy, caches and working sets, sharing a GPU, measuring a GPU. |
| [`device-log-anomaly-detection/`](device-log-anomaly-detection/README.md) | Log parsing to templates, windows and count vectors, isolation forest, weighted-least-squares fleet trend tests, root-cause mining from log workflows, clustering and reporting, the ground-truth problem, template engineering, data quality, lessons learned. |
| [`wifi-csi-sensing/`](wifi-csi-sensing/README.md) | CSI vs RSSI and multipath, what the hardware gives you, preprocessing, time/subspace/frequency features, classifiers and windows, multi-device joint detection, room-level localisation by metric learning, KPIs, data campaigns, co-existence, endpoint architecture, limits. |
| [`agentic-device-control/`](agentic-device-control/README.md) | A cloud-initiated multi-agent loop: message path, the agent graph as a state machine, orchestrator, vision specialist, actuator, the ReAct loop, cost and latency with prompt caching, safety, evaluation. |
| [`agentic-research-harness/`](agentic-research-harness/README.md) | A frozen, human-owned evaluator with calibrated gates and held-out inputs; negative controls that must fail; evidence records behind every claim; small parent-linked candidates; a fast attempts log and a curated lessons file; planner, researchers and an evaluation queue with paired baselines and range-based promotion; a worked example on a simulated heterogeneous robot compute platform; the lessons and a 10-step checklist. |
| [`socks5-over-quic-phone-egress/`](socks5-over-quic-phone-egress/README.md) | Why a cloud agent needs the user's IP; SOCKS5 with remote DNS; QUIC streams, migration and idle timeouts; who dials whom through an anycast UDP front door; trust without a CA by fingerprint pinning over an authenticated control channel; the control stream; threat model and limits; the two phone client stacks; observability without user data; testing a tunnel; rollout; L3 vs L5 tunnelling; a platform-owned data plane. |

Each kit has `notes/`, `glossary.md`, `constants.json` (every constant with its source), `diagrams/` (draw.io + SVG/PNG), `explorers/` (interactive HTML), `videos/` (MP4 + captions) and `SOURCES.md`.

The quiz (`quiz/`) draws one question bank per note; wrong answers push the underlying knowledge point into more frequent review (Leitner boxes). Progress is stored in the browser only.

Study aids, not primary sources. Numbers are quoted from the listed sources or labelled as estimates.

## Contributing (humans and agents)

The repo is public. Before anything is committed:

1. **Quiz banks validate:** `node quiz/check-banks.js` must report 0 errors. New knowledge points go right after `knowledgePoints: {` and new questions right after `questions: [` in a bank file.
2. **Public-safety scan passes:** `tools/public-scan.sh` (staged files) or `tools/public-scan.sh --all`. It matches every line against a denylist of names that must not appear here; the denylist itself is kept outside the repo at `~/.config/learning-kits/denylist.txt` (override with `LEARNING_KITS_DENYLIST`). Fix the content rather than the list; a true false positive goes into `.public-scan-allow` with a comment.
3. Both run automatically from the pre-commit hook: `git config core.hooksPath .githooks` once per clone.

Every number carries its source or the tag *illustrative*; constants live in each kit's `constants.json` and are loaded, not retyped. Story pages (`<kit>/stories/`) use the shared runtime in `stories/` and are checked with `stories/tools/shoot.py` before publishing.

