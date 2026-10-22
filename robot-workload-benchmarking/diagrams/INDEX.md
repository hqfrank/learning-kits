# Diagrams — Benchmarking a robot's on-board compute workload (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: it turns the stack (Part A), the metrics (Part B), and the method
(Part C) into diagrams. Every number on every canvas is loaded from this kit's `constants.json` or
cited to a public source or a sibling kit, and is tagged on the canvas; **no measured number from any
specific robot or campaign appears.** Each canvas carries its own legend and a sources footnote so the
exported image stands alone. A combined 6-page source, `robot-workload-benchmarking.drawio`, is also
written so the browser shows all pages at once.

**Public-safety:** this kit is published on a public GitHub repo. These diagrams name only public
models/libraries/tools (YOLOX, SCRFD, ArcFace, OSNet, BlazePose, Light-ASD; DISK, LightGlue, MixVPR,
iSAM2, TSDF; VLA families; Whisper; ROS 2, zenoh, cgroups, tegrastats, nvidia-smi, Nsight, SNTP) and
generic subjects ("a home robot", "the harness machine", "the control loop"). No project codename,
company, person, hostname, internal URL/path, commit, issue, or campaign identifier is used. A
case-insensitive scan was run over every file in this folder before publishing (0 hits).

**Rendering notes (from `../../nvidia-gpu-anatomy/diagrams/INDEX.md` and the agent memory):**
The drawio MCP export pipeline was unavailable/unreliable in this environment, so each page is
described once as a list of cells in a `specNN.py` module and rendered two ways from the SAME list by
`.render_local.py`: (1) an editable `.drawio` (draw.io-compatible), and (2) a standalone `.svg` (a
`<rect>` per box plus a `<foreignObject>` XHTML label, polyline edges with a per-colour arrow marker),
rasterised to `.png` via headless Chrome at 2x. Chrome renders the foreignObject HTML, so wrapping,
`<br>`, bullets and glyphs like `->`, `|`, `x`, `c` all render without the cairo glyph/no-wrap issues
of the earlier pipeline. The exported SVGs contain **no** draw.io "Text is not SVG" banner (the local
renderer never emits one), so no strip step is needed. Rules still honoured: ASCII `->` for arrows and
`x` for the per-person multiplier; any literal `<` in a label is written in-prose as `-` or spelled out
(none remain); every SVG is validated with ElementTree before rasterising. To regenerate one page:
`python3 .render_local.py specNN.py`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-stack-as-pipelines` | A home robot is not one program with one bottleneck: it is a crowd of pipelines (sense -> perceive -> decide -> act) with different deadlines sharing one CPU, one GPU, one memory pool, on a floor of shared / service / isolated-control cores. | Notes A0-A7; rates from `constants.json` camera_frame_rate_illustrative, perception_output_rate_illustrative, wbc_control_rate_illustrative, wbc_deadline_illustrative, motor_bus_rate_illustrative, audio_packet_framing_illustrative, audio_sample_rate_illustrative; VLA example vla_latency_example_sibling |
| `02-people-perception-pipeline` | A short GPU network chain wrapped in CPU bookkeeping that grows with N: per-frame stages stay flat, per-person stages (and the CPU glue) scale with N, and the CPU glue usually exceeds the GPU inference. | Note A2 (YOLOX, SCRFD, ArcFace, OSNet, BlazePose, Light-ASD; NMS, Kalman, Hungarian, One Euro, 3D projection); `constants.json` perception_output_rate_illustrative, camera_frame_rate_illustrative |
| `03-solo-levels` | Three solo levels of realism, nested L1 within L2 within L3; the unit is the deployed service not the model; L2-L1 = service glue, L3-L2 = real-input cost; an un-driven event-driven service shows an idle floor, not its working cost. | Note C2 (L1/L2/L3, idle floor, driver, replaced pair; trtexec-style engine timing); interference factor denominator defined in C6 |
| `04-bench-topology` | Two machines: only the real stack runs on the robot, everything that stands in for the world runs on a separate harness machine; a dedicated low-latency control link vs a bulk feed link; two network islands; observers on their own core; an SNTP clock-sync probe. | Note C3 (harness, second machine, fake boards + framing, schema-faithful stubs, synthetic input, bag replay, islands); A4 control/isolation; A5 mic framing; A2 synthetic N; A3 bag replay; B2 SNTP offset; B0/B4 observer core; `constants.json` motor_bus_rate_illustrative, clock_offset_target_illustrative |
| `05-metric-collection-map` | Every metric has a source it is read from and a pitfall that misreads it; four groups (CPU / GPU+memory / rates+latency+stats / profilers) must all be read or the result lies. | Notes B0 (cgroup cpu.stat/cpu.max, /proc/stat, /proc/schedstat, loadavg, census), B1 (tegrastats GR3D/EMC/rails, nvidia-smi, MemAvailable, memory.current, nvmap, clock lock), B2 (topic rate/percentiles, receive vs stamp, SNTP offset, clock-free), B3 (Garwood Poisson, p99, sample-count, block bootstrap), B4 (tegrastats/Nsight Systems/Nsight Compute, union of kernel intervals, profiler safety); `constants.json` foreign_cpu_gate_illustrative, clock_offset_target_illustrative, nsys_perturbation_illustrative |
| `06-campaign-flow` | The campaign flow: predict (ledger) -> pre-register -> solo -> review -> combined tiers in seeded interleaved order -> validity gates per window (valid / flagged / void) -> carries verdict per KPI band -> first-limit attribution; loop back via addenda/supersede only for harness bugs, never for stack behaviour. | Notes C1 (ledger, bound class, launch-bound), C5 (pre-registration, interleaving, replicate blocks, paired, addenda/supersede, review), C2 (solo levels), C4 (windows, gates, valid/flagged/void), C6 (tiers, interference factor, PASS/UNRESOLVED/FAIL bands, first-limit attribution, saturated baseline) |

---

## Per-diagram specs (as built)

### 01-stack-as-pipelines
```
Teaches: a robot stack is concurrent pipelines (sense -> perceive -> decide -> act) with different
         deadlines sharing one CPU/GPU/memory; the floor is shared / service / isolated-control cores.
Type:    Swimlane / block diagram. Four stage columns; one box per subsystem; message-flow arrows.
Elements: camera/depth+VIO [A1]; people perception [A2]; mapping+nav [A3]; voice VAD/wake + ASR/TTS
         [A5]; VLA + cognition [A6]; whole-body control [A4]; platform layer [A7]. Each box tags
         resource (CPU / GPU / both), loop-rate class, and on-board vs cloud. Floor = three core pools.
Colour:  fill = timing class (red hard / amber soft / blue best-effort / purple sense / green floor).
Numbers (all illustrative, constants.json): camera 30 Hz; perception 10 Hz; control 50 Hz / 20 ms;
         motor bus 100-1000 Hz; audio 48 frames/pkt @ 16 kHz; VLA 53 ms -> ~19 Hz (SIBLING example).
Left out: per-metric detail (diagram 05); the harness (diagram 04).
```

### 02-people-perception-pipeline
```
Teaches: per-frame (fixed) vs per-person (scales with N) work; which stages run on GPU vs CPU; the
         CPU post-processing usually exceeds the GPU inference; where cost grows with N.
Type:    Two-band pipeline. Left band per-frame; right band per-person; GPU green, CPU blue.
Elements: decode, letterbox, YOLOX, NMS (per-frame); crop/warp, SCRFD, ArcFace, OSNet, BlazePose,
         Light-ASD, Kalman+Hungarian tracking, One Euro smoothing, 3D projection (per-person, 'xN').
Callouts: headline lesson (CPU glue exceeds GPU inference); the N-scaling rule (flat vs linear; measure
         N=1,2,5,10; report fixed cost + per-person slope; N = people in view not detected).
Colour:  green = GPU network; blue = CPU glue; purple band = the N-scaling rule.
Numbers: output ~10 Hz illustrative; camera 30 Hz illustrative; software rate cap is a ceiling (B2).
Left out: the depth/VIO internals (A1); roofline/bound-class (that is the explorer/video rung).
```

### 03-solo-levels
```
Teaches: L1 (engine) within L2 (deployed service) within L3 (+ real upstream); unit is the deployed
         service; L2-L1 = service glue, L3-L2 = real-input cost; idle floor vs working cost.
Type:    Nested containment (three concentric rounded boxes) + gap annotations + a side panel.
Elements: L1/L2/L3 each with the question it answers; two gap boxes (L2-L1 glue, L3-L2 upstream);
         side panel: idle floor (un-driven ~0 cost, not the cost) vs working cost (drive via the API).
Colour:  green L1, blue L2, purple L3, amber gaps, red idle-floor caveat.
Numbers: none (method note); the baseline is the denominator for the C6 interference factor.
Left out: the combined-run interference itself (diagram 06, C6).
```

### 04-bench-topology
```
Teaches: two machines - only the real stack on the robot, the world-stand-ins on a separate harness;
         dedicated low-latency control link vs bulk feed link; two network islands; observers on
         their own core; an SNTP clock-sync probe.
Type:    Two-container network topology with two inter-machine links and two islands.
Elements (robot): real services; isolated control loop; observers/probes on a dedicated core; clock
         probe; island A (control+sensor protocols), island B (bulk feeds+cloud).
Elements (harness): fake motor boards; fake mic board; synthetic camera (N people); bag replay;
         cloud-API stubs; harness-CPU accounting; SNTP peer.
Colour:  blue robot, amber harness, green fakes/stubs, purple observers/accounting, red control+link.
Numbers (illustrative): motor bus 100-1000 Hz; clock offset < 0.5 ms.
Left out: the per-service pipelines (diagram 01); gate logic (diagram 06).
```

### 05-metric-collection-map
```
Teaches: each metric has a source it is read from and a pitfall that misreads it; four families must
         all be read or the result lies.
Type:    Grouped card matrix, four columns (CPU / GPU+memory / rates+latency+stats / profilers).
Elements: one card per metric with name / source / pitfall. CPU: cores, throttling, per-core busy,
         run-queue wait, loadavg, census. GPU+mem: GR3D, utilization.gpu, EMC, rails, MemAvailable/
         cgroup/nvmap, clock lock. Rates+stats: rate+percentiles, stamp vs receive, SNTP offset,
         clock-free latency, misses/min + p99, sample-count. Profilers: tegrastats, Nsight Systems,
         Nsight Compute, union of kernel intervals, profiler safety.
Colour:  blue CPU, green GPU+memory, amber rates+latency+stats, purple profilers.
Numbers (illustrative tags): foreign_cpu_gate 0.3 cores; clock offset 0.5 ms; nsys +~15 ms.
Left out: the full statistics derivations (B3 prose); roofline (explorer/video rung).
```

### 06-campaign-flow
```
Teaches: predict -> pre-register -> solo -> review -> combined tiers (seeded interleaved) -> validity
         gates per window (valid / flagged / void) -> carries verdict per KPI band -> first-limit
         attribution; loop back via addenda/supersede ONLY for harness bugs, never stack behaviour.
Type:    Flowchart, left-to-right then wrapping, with a backward dashed loop for the harness-bug path.
Elements: 8 steps; three window-outcome chips (valid/flagged/void); the PASS/UNRESOLVED/FAIL bands;
         the CPU/GPU/memory/none first-limit classifier with the saturated-baseline caveat; the
         addenda/supersede loop with 'no tuning after data'.
Colour:  blue steps, amber gates+flagged, green verdict steps, red void+saturated-baseline, purple loop.
Numbers: none (method note); the ledger formula t = FLOP/R + bytes/B + t_CPU is shown (C1).
Left out: the per-metric sources (diagram 05); the harness layout (diagram 04).
```

---

## Files

Each diagram has three files: `NN-slug.drawio` (editable single-page source), `NN-slug.svg` (vector,
self-rendered, no draw.io banner), `NN-slug.png` (raster, 2x via headless Chrome, read back and checked
for legibility). `robot-workload-benchmarking.drawio` is the combined 6-page document (concatenated
`<diagram>` blocks) for viewing all pages at once. `specNN.py` is the cell list each page is rendered
from; `.render_local.py` is the renderer (drawio + SVG + PNG from one list).
