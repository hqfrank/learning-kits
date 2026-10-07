# SOURCES — Jetson Orin (sm_87) and Thor (sm_110): a Measured Reference for Robotics Workloads

This folder is a learning kit (rung 1: notes) for the campaign metrics reference written by V (Varada).
Nothing here is a new measurement. Every number traces to one of the sources below.

## Primary source

**book.pdf** — "Jetson Orin (sm_87) and Thor (sm_110): a Measured Reference for Robotics Workloads.
Capabilities, behaviour under interference, and deployed models — the campaign metrics reference, Docs A–C
bound as one." 55 pages. Local copy: `/Users/qiahu/Documents/development/robotics/robotics_learning_notes/book.pdf`.

The PDF is built from `beyond-tops/metrics-report/book.tex` in the Brazil package **JetsonProfiling**
(branch `dev`). The LaTeX master says: "There is exactly one copy of every piece of prose." The book
`\input`s the same content fragments the standalone docs use.

### How it was read (and one caveat)

The shell tool was unavailable in the session that wrote these notes (`spawn EBADF` on every command), so
`pdftotext` could not run. The notes were therefore written from the **LaTeX sources the PDF is built
from**, read in full from `code.amazon.com` at branch `dev`:

| Book part | Source file (under `JetsonProfiling/beyond-tops/metrics-report/`) |
|---|---|
| Title, structure | `book.tex` |
| Platforms (Table 1) | `common/platforms.tex` |
| Doc A scope, inventory, references | `doc-a-capabilities/capabilities-content.tex` |
| A.1 FP/INT pipe interleaving | `doc-a-capabilities/fp-int-mix.tex` |
| A.2 CUDA-core ceilings | `doc-a-capabilities/cuda-core-ceilings.tex` |
| A.3 Tensor-core ceilings | `doc-a-capabilities/tensor-ceilings.tex` |
| A.4 NVFP4 ceiling | `doc-a-capabilities/nvfp4-ceiling.tex` |
| A.5 L1 bandwidth ceiling | `doc-a-capabilities/l1-bandwidth.tex` |
| A.6 Bandwidth vs footprint | `doc-a-capabilities/bandwidth-vs-footprint.tex` |
| A.7 Latency landmarks | `doc-a-capabilities/latency-landmarks.tex` |
| Doc B scope, inventory, references | `doc-b-proxy-workload/proxy-workload-content.tex` |
| B.1 Copy/exec-engine and DRAM-direction interference | `doc-b-proxy-workload/ce-interference.tex` |
| B.2 Cache-level interference | `doc-b-proxy-workload/cache-interference.tex` |
| B.3 matrix_profile stall decomposition | `doc-b-proxy-workload/matrix-profile.tex` |
| B.4 GEMM-victim interference | `doc-b-proxy-workload/gemm-victim.tex` |
| B.5 Tensor under CPU contention | `doc-b-proxy-workload/tensor-contention.tex` |
| B.6 Co-tenancy interference matrix | `doc-b-proxy-workload/cotenancy-heterogeneous.tex` |
| B.7 Aggregate throughput | `doc-b-proxy-workload/cotenancy-homogeneous.tex` |
| B.8 Co-tenancy with real-shape proxies (mix ladder) | `doc-b-proxy-workload/cotenancy-real-shape.tex` |
| Doc C scope and status | `doc-c-real-workload/real-workload-content.tex` |
| Doc C "Models used in this note" | `doc-c-real-workload/models.tex` |
| C.1 π0.5 solo latency | `doc-c-real-workload/c1-pi05-latency-body.tex` |
| C.2 Co-tenancy under GPU load (objective only) | `doc-c-real-workload/c2-cotenancy-gpu-load-body.tex` |
| Doc C references | `doc-c-real-workload/references.tex` |

Caveats that follow from this:

1. The `dev` branch may have moved since the PDF was built (the master is dated "V 2026-09-11, built
   2026-09-30"). If a number in these notes disagrees with the PDF, the PDF is the artifact the user named;
   check the LaTeX history for the change.
2. **Table numbers.** The book numbers tables per section (A.6.1, A.6.2, …). The notes cite tables by
   section plus the order in which the tables appear in the LaTeX source, plus the caption subject in
   parentheses, for example "§A.6 Table A.6.2 (predicted vs measured plateaus)". The caption subject is the
   reliable locator; the ordinal was inferred from the source, not read off the PDF.
3. Numbers that exist only in a figure (not in a table or in prose) are marked "figure only; not read" in
   the notes. This applies to the measured pointer-chase eviction plateau in B.2 and to the per-tile curves
   in B.5.

### Verification pass against the PDF (2026-10-02)

The notes were first drafted from the LaTeX sources (shell unavailable, see above). In a later
session `pdftotext -layout book.pdf /tmp/book.txt` ran successfully (2802 lines) and every note was
read back against the extracted PDF text. All numeric tables matched the PDF exactly (Tables A.1.3,
A.2.2, A.3.2, A.3.3, A.4.2, A.5.1, A.6.2, A.7.2, B.1.1, B.2.1, B.3.1–B.3.2, B.4.1, B.5.1–B.5.3,
B.6.1–B.6.3, B.7.1, B.8.1, C.0.1–C.0.2, C.1.1–C.1.8). The one soft spot flagged above — the inferred
table ordinals (A.6.1, A.6.2, …) — remains inferred, because the PDF numbers tables by caption only
in the text; the caption subject carried in each note's Source line is the reliable locator. No note
number required correction after the verification pass.

## Supplementary source

**KEY-LEARNINGS.md** — `JetsonProfiling/robot-kernels/L4-realmodel-cotenancy/KEY-LEARNINGS.md` (branch
`dev`). The synthesized findings of the L4 real-model co-tenancy campaign on one Thor GPU. Doc C says its
later sections (queueing decomposition, precision as a co-tenancy fix, MPS reservation) are "drafted from
committed data but not yet written up"; this file is the committed summary those sections will draw on.
Used for the note `L4-scheduling-ladder.md` only. It is a working document with a less formal register than
the book; where it gives a number as a range or a tilde, the note keeps the range or tilde.

## Secondary material consulted (not cited for numbers)

- `JetsonProfiling/beyond-tops/metrics-report/briefs/brief-memory-hierarchy.md` — extraction brief for
  A.5–A.7; used only to confirm the reading of the LaTeX tables.
- `JetsonProfiling/common/measured_constants.md` — the campaign's own constants index ([M] in the book). The
  book cites it for the sustained DRAM bandwidth (190 / 245 GB/s) and the retained-bandwidth fractions used in
  B.6; those two values are carried in the notes with the [M] label the book gives them.

## Reading conventions used in the notes

- "Orin" = NVIDIA Jetson AGX Orin, Ampere, sm_87. "Thor" = NVIDIA Jetson Thor T5000, Blackwell, sm_110.
- All numbers are at MAXN with GPU clocks locked and devfreq-verified, as the book states for every
  experiment, unless a note says otherwise.
- Where the book gives a range ("1.07–1.14"), the notes keep the range. Where the book marks a value with
  "≈" or "~", the notes keep the mark.
- `constants.json` holds every measured constant the notes cite, each with its section and table.

## Files written by this rung (learn-notes)

- `README.md` — reading order and a one-paragraph summary of the book.
- `glossary.md` — one line per term.
- `constants.json` — machine-readable constants with sources.
- `notes/` — one note per experiment section (00-platforms, A1–A7, B1–B8, C1, C2) plus
  `L4-scheduling-ladder.md`.

Later rungs (diagrams, explorers, video) extend this file.

## Files written by Rung 2 (learn-diagram)

Five diagrams under `diagrams/`, one draw.io page each, exported as `.drawio` + `.svg` + `.png`, with a
`diagrams/INDEX.md` carrying the per-diagram spec and the sources each used. Every number on every canvas
is taken from `constants.json` / the `notes/` and tagged with its note on the canvas; no constant was
retyped as a free value. Measured values are coloured, datasheet values dashed grey, Orin counterparts of
Thor roofs dashed.

| Diagram | Finding (title) | Notes/constants used |
|---|---|---|
| `01-shared-soc` | Thor's CPU, GPU SMs (+SMSPs), copy engines and the memset/blit path all funnel through ONE memory controller to one LPDDR pool. | 00-platforms; A.6; B.1; B.6 [M]; L4 |
| `02-roofline` | Hierarchical roofline Orin vs Thor; π0.5 phases and WBC sit far below every tensor ceiling — bandwidth-bound, not TOPS-bound. | A.2; A.3; A.4; A.5; A.6; C.1; L4/B.8 |
| `03-l2-cliff` | L2 capacity cliff: fitting L2 is 12.4×/14.6× faster than spilling to DRAM; cliffs at 4/32 MB; L2 latency unchanged (~150 ns). | A.6; A.7 |
| `04-who-pays` | Co-tenancy is one-sided: compute starves memory (4.19×), memory barely touches compute (1.12×); tiny latency-critical victims pay in the tail. | B.1; B.4; B.5; B.6; B.8 |
| `05-qos-ladder` | Context isolation + a 25–35% MPS SM cap returns the 100 Hz loop to 0 drops, but no step moves the ~172 GB/s CPU-memory floor. | L4; B.8 |

How the images were produced: diagrams authored via the draw.io MCP; `.svg` exported from the MCP;
`.png` rasterised from the `.svg` with cairosvg at 2× (the MCP's PNG/projection export was unreliable in
this session). cairo lacks a few Unicode glyphs (`→`, `∥`, `∣`, `╲`), replaced with ASCII (`->`, `||`,
`|`, `vs`) in the diagram text; `×`, `π`, `µ` render correctly. Each PNG was read back and checked for
legibility before completion.

## Files written by rung 3 (learn-explorer)

Two single-file, no-build HTML explorers under `explorers/`, built from the notes and `constants.json`
(no new measurement; every number carries its source):

- `explorers/params.json` — the constants both pages load, each entry copied verbatim (value + unit +
  source) from `constants.json`. Where an explorer needed a value `constants.json` carries only per
  datapath (a compute roof, an engine size, an action-expert param count), the `source` string names
  the note/table it was lifted from; the two teaching derivations (action-expert FLOP estimate, the
  topology scaling factors in explorer 02) are labelled as teaching models in the page footers.
- `explorers/01-roofline-explorer.html` — the roofline: arithmetic intensity decides which roof binds;
  shows π0.5 predicted vs measured latency as the labelled gap (64.1→90.06 ms, 37.4→53.03 ms, §C.1
  Tables C.1.5/C.1.6), the WBC MLP, the π0.5 action expert, and a 1024² FP32 GEMM. Sources: §A.2, §A.3,
  §A.4, §A.6, §C.1.
- `explorers/02-who-pays-explorer.html` — co-tenancy: names the governing mechanism (SM fair-share,
  DRAM share, L2 eviction, SM-co-schedule lockout, the CPU-hog cliff, the 172 GB/s floor) and shows the
  WBC p99 against the 10 ms deadline, with measured overlays from §B.6 Table B.6.3, §B.8 Table B.8.1 and
  the L4 scheduling ladder. Sources: §B.4, §B.5, §B.6, §B.8, L4 `KEY-LEARNINGS.md`.
- `explorers/INDEX.md` — the written spec for each explorer (teaches / inputs / outputs / picture /
  preloaded cases / measured overlays / out-of-scope) plus the self-test list.

Verification: prediction functions are factored into a pure IIFE that also runs under node. Each page's
`console.assert` self-tests reproduce at least three of the source's own predicted/measured numbers
(ridge, GEMM latency, arithmetic intensity, SM fair-share, DRAM share, CPU-hog floor), and a node NaN
sweep over every slider/selector extreme (64 combinations for explorer 01, 300 for explorer 02) found
zero NaN/Infinity/negative outputs. Both were rendered headless (Chrome) and the screenshots read back:
the log-log roofline and the deadline bar-chart both draw and move, and both pages log "self-tests done"
with no assertion failures.

Later rung (video) extends this file.

## Files written by Rung 4 (learn-video)

One explainer video under `videos/01-single-lane-bridge/`, built from the notes and
`explorers/params.json` (no new measurement; every on-screen number is loaded from `params.json`
and its key is cited in the scene's source tag and in the storyboard):

- `videos/01-single-lane-bridge/storyboard.md` — the written spec: seven scenes with duration
  targets, on-screen elements, the narration sentences, and the `params.json` key for every number
  shown. Written before rendering.
- `videos/01-single-lane-bridge/scenes/` — `theme.py` (shared colours + constants loaded from
  `../../explorers/params.json`), `scene_00_cards.py` (title + sources cards), `scene_01.py` …
  `scene_06.py` (one Manim `Scene` per storyboard scene). `Text` is used throughout, not `MathTex`
  (no LaTeX on the machine); `Axes` tick labels are drawn as `Text` for the same reason.
- `videos/01-single-lane-bridge/audio/scene_01.wav` … `scene_06.wav` — Kokoro-82M narration
  (`af_heart`, 24 kHz mono).
- `videos/01-single-lane-bridge/out/single-lane-bridge.mp4` — the final cut, 3 min 29 s (209 s):
  1 s title card → scenes 01–06 muxed with their narration → a sources card.
- `videos/01-single-lane-bridge/out/single-lane-bridge.srt` — captions, timed to the measured
  narration clip lengths (built by `build_srt.py` from the storyboard text + per-part durations).
- `videos/INDEX.md` — the per-video spec (teaches / duration / sources) and the scene arc.

The video — "The single-lane bridge: why a robot's control loop starves on a shared GPU" — carries
the campaign's thesis as a seven-beat arc: three jobs on one Thor GPU; the datasheet TOPS looks
ample (A.3 tcgen05, A.4 NVFP4); the bistable SM co-scheduling lockout at ~8% / ~14% occupancy
(B.4); the real-shape WBC p99 inflated 141× to 5.9 ms under the 10 ms deadline (B.8); the L4 QoS
ladder that recovers the loop at the cost of VLA Hz; and the ~172 GB/s shared-controller floor that
no discipline moves (L4). Sources used: A.3, A.4, B.4, B.8, and the L4 `KEY-LEARNINGS.md`.

How the narration toolchain was fixed: Kokoro's g2p step (misaki) auto-downloads the spaCy model
`en_core_web_sm` via a pip resolver that lands on `uv` and fails in this environment; installing the
model wheel once into the shared venv (`uv pip install --python
~/.local/share/learn-kit/venv/bin/python …en_core_web_sm-3.8.0-py3-none-any.whl`) resolves it. Noted
in the learn-video memory file.
