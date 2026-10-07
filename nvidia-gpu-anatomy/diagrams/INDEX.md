# Diagrams — Anatomy of an NVIDIA GPU (Rung 2, learn-diagram)

Four diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is a concept
primer for a reader meeting SM / SMSP / warp / L2 / MPS for the first time; the diagrams explain the
mechanisms behind the sibling metrics kit's Table 1. Every board-specific number is loaded from
`../constants.json` (which copies the metrics kit's values with their source strings) and carries its
source tag on the canvas; nothing is retyped as a free constant. Each canvas has its own legend and a
sources footnote so the exported image stands alone. A combined 4-page source, `nvidia-gpu-anatomy.drawio`,
is also written so the browser shows all pages at once.

**Rendering notes (from `../../jetson-orin-thor-metrics/diagrams/INDEX.md` and the agent memory):**
Every label uses plain text (`html=0`, native `\n` line breaks), so the exported SVGs contain native
`<text>` with no HTML foreignObject payload. ASCII is used for glyphs cairo cannot render: `->` for the
arrow, `x` for the multiplier (`×` would also work but `x` is used in the measured ratios). draw.io
appends a trailing `<switch>...Text is not SVG - cannot display...</switch>` fallback to every SVG; it is
stripped post-export by `.strip_and_raster.py` before rasterising with cairosvg at scale 2.0
(`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`). One **new** quirk this pass: pages exported via a page
selector / `load_diagram` carried a background-rect fill of `fill: var(--ge-adaptive-bg, #ffffff)` — a CSS
variable cairosvg cannot parse (it chokes on "var", `ValueError: ... base 16: 'ar'`). Fix: `sed` the
`var(--ge-adaptive-bg, #ffffff)` down to its fallback `#ffffff` in the SVG before rasterising. Pages
exported straight from `create_new_diagram` in a fresh session did not have the CSS-var and rasterised
first try — so the `<` note still holds: author each page cleanly and avoid literal `<` in any `value`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-two-ladders` | The software ladder you write (thread -> warp -> block -> grid -> kernel) maps onto the hardware ladder that runs it (lane -> SMSP -> SM -> GPU): a warp runs on ONE SMSP, a block resides on ONE SM, a grid spreads over ALL SMs. | CUDA Prog. Guide 1.2.2 (A-PM: warp=32, block on one SM, grid any order); `constants.json` smsp_per_sm, sm_count, gpu_clock_maxn_locked [Platforms Table 1] |
| `02-inside-an-sm` | One SM is four sub-partitions, each issuing at most 1 instruction/cycle; the SM caps at 4 warp-instructions/cycle, and more FP32 cores do not raise issue rate — the dispatch port does. L1/shared and the 64K register file are shared across the four SMSPs. | `constants.json` smsp_per_sm=4, dispatch_bound_per_smsp=1, fp32_cores_per_sm=128, tensor_cores_per_sm=4, registers_per_sm=65536, max_warps_per_sm=48, max_threads_per_sm=1536, l1_shared_per_sm 164/228 KB, l1_read_datapath 128 B/cyc [all Platforms Table 1]; pipe inventory B-FORUMS; in-order SIMT issue 3.2.2 (A-HW) |
| `03-memory-hierarchy` | Registers -> L1/shared (per SM, private) -> L2 (shared by all SMs) -> memory controller -> LPDDR, also fed by the CPU cores and copy engines. Title finding: Thor grew L2 8x (4 -> 32 MB) but L2 latency did NOT change (146 -> 156 ns) — more data stays resident, not reached faster. | `constants.json` registers_per_sm, l1_shared_per_sm, l1_read_datapath, l2_size, l2_dram_capacity_ratio [Platforms Table 1]; l2_resident_read_bandwidth, dram_bandwidth_read_measured, l2_dram_bandwidth_ratio [A.6]; latency_l1/l2/dram [A.7]; hierarchy + unified memory 1.2.3 (A-PM) |
| `04-sharing-mechanisms` | A grid of what isolates what: columns = sharing mechanism (shared context+streams / separate processes time-slice / MPS / MPS+SM cap / MIG), rows = resource (SM slots, L2, memory controller), cells = isolated yes/partial/no with the citing note. Finding: streams give concurrency but no isolation; only MPS+SM cap protects compute share; only MIG isolates all three (deferred on Thor). | `constants.json` lockout_onset_occupancy 8/14% [B.4], controller_contention_peak 1.53/2.53x [B.4], mps_cap_vla_rate_retained [L4], cpu_memory_load_floor 172 GB/s [L4], MIG none/tech-preview [Platforms Table 1]; mechanisms + "streams are not isolation" note 07-sharing-the-gpu (B7, L4); 1.2.2.1 (A-PM); MIG B-AMPERE |

---

## Per-diagram specs (as built)

### 01-two-ladders — side-by-side ladder map
```
Teaches: the software terms you write map onto physical hardware units; a warp runs on one SMSP,
         a block resides on one SM, a grid spreads over all SMs.
Type:    Two parallel vertical ladders (software left, hardware right) with mapping arrows between.
Elements (software, blue):  thread; warp = 32 threads; block; grid; kernel (dashed - no single HW unit).
Elements (hardware, green): lane; SMSP (1 warp scheduler + 1 dispatch port, 4 per SM); SM (Orin 16 | Thor 20);
         GPU (all SMs behind one shared L2 + one memory controller).
Mapping arrows (red = the key ones): thread "runs in" lane (grey); warp -> SMSP "a warp runs on ONE SMSP";
         block -> SM "a block resides on ONE SM"; grid -> GPU "a grid spreads over ALL SMs".
Colour: blue = software you write; green = hardware that runs it; red arrow = the key mapping;
         dashed box = kernel.
Numbers on canvas (all from constants.json): SMSP per SM = 4 [smsp_per_sm]; SM count 16/20 [sm_count];
         clock 1.30/1.575 GHz, issue-bound speedup 1.51x [gpu_clock_maxn_locked].
Left out: the register/occupancy limits (diagram 02); warp-divergence detail (prose).
```

### 02-inside-an-sm — one SM exploded
```
Teaches: four SMSPs, each 1 inst/cycle; SM issues at most 4 warp-instructions/cycle; issue rate is
         bounded by the dispatch port, not the FP32 core count. L1/shared and the 64K register file
         are shared across the four SMSPs.
Type:    Containment / block diagram - an SM box holding four SMSP columns plus two shared bars.
Elements per SMSP: warp scheduler + dispatch port (1 inst/cycle, D=1 labelled on SMSP 0);
         32 FP32 lanes (CUDA cores); INT/ALU pipe; LD/ST + SFU; 1 tensor core (MMA; Orin 3rd-gen |
         Thor 5th-gen tcgen05 noted on SMSP 0); register-file slice.
Shared bars: L1/shared unified array (Orin 164 KB | Thor 228 KB; L1 read datapath 128 B/cyc);
         register file 65536 (64K) per SM; per-SM totals 128 FP32 cores, 4 tensor cores, 48 warps = 1536 threads.
Bound callout: 4 SMSP x 1 inst/cycle = at most 4 warp instructions per cycle; more FP32 cores do NOT
         raise issue rate - the dispatch port does.
Colour: orange = scheduler/issue (the bound); blue = CUDA-core/scalar pipes; purple = tensor core;
         red = register file; yellow = L1/shared.
Numbers: smsp_per_sm, dispatch_bound_per_smsp, fp32_cores_per_sm, tensor_cores_per_sm, registers_per_sm,
         max_warps_per_sm, max_threads_per_sm, l1_shared_per_sm, l1_read_datapath [all Platforms Table 1].
Left out: texture path, GPC/cluster level, per-pipe throughput (ceilings live in the metrics kit roofline).
```

### 03-memory-hierarchy — vertical stack with per-level numbers
```
Teaches: where a working set sits decides speed; Thor's L2 grew 8x but its latency did not change.
Type:    Vertical ladder of levels (fastest/smallest at top) with two measured columns (Orin, Thor)
         and "miss" arrows descending; CPU cores and copy engines also feed the controller.
Levels:  Registers (per thread); L1/shared (per SM, private); L2 (shared by all SMs); memory controller
         (one path, shared GPU+CPU); LPDDR DRAM (shared with CPU, integrated SoC).
Per-level numbers (Orin | Thor): L1 164/228 KB, datapath 128 B/cyc, latency 29.9/25.3 ns;
         L2 4/32 MB (8x), resident read 2200/3790 GB/s, latency 146/156 ns (unchanged!);
         DRAM read 177/259 GB/s measured, latency 675/510 ns.
Side feeds: CPU cores (14x on Thor) and copy engines (H2D/D2H/D2D) arrow into the one controller.
Finding box: L2-resident streaming is 12.4x (Orin) / 14.6x (Thor) faster than DRAM; L2 latency barely
         moved (146 -> 156 ns) while L2 capacity grew 8x.
Colour: blue = Orin measured; green = Thor measured.
Numbers: l1_shared_per_sm, l1_read_datapath, l2_size, l2_dram_capacity_ratio, registers_per_sm
         [Platforms Table 1]; l2_resident_read_bandwidth, dram_bandwidth_read_measured,
         l2_dram_bandwidth_ratio [A.6]; latency_l1/l2/dram [A.7].
Left out: the bandwidth-vs-footprint cliff curve (that is metrics-kit diagram 03-l2-cliff); L1 carveout detail.
```

### 04-sharing-mechanisms — isolation matrix
```
Teaches: streams give concurrency but no isolation; only MPS+SM cap protects compute share; only MIG
         isolates all three resources (and MIG is deferred on Thor).
Type:    Matrix. Columns = mechanism (least -> most isolating): shared context + streams; separate
         processes (time-slice); MPS plain; MPS + SM cap 25-35%; MIG. Rows = resource: SM slots
         (block-scheduler co-residence); L2 cache; memory controller (shared with CPU on the SoC).
Cells:   isolated? YES / PARTIAL / NO, each with the measured reason:
         SM slots: NO (lockout above ~8% Orin / ~14% Thor) | PARTIAL (time-slice tail) | NO (co-execute) |
                   YES-share (cap 35% returns a 100 Hz loop to 0 drops) | YES (dedicated compute slice).
         L2:       NO (shared, co-tenant evicts) across all but MIG (YES, dedicated cache path).
         Controller: NO across all but MIG; note the ~172 GB/s CPU-memory-hog floor the cap cannot fix.
Colour:  green = isolated (YES); yellow = partial; red = not isolated (NO).
Numbers: lockout_onset_occupancy 8/14% [B.4]; controller_contention_peak 1.53/2.53x [B.4];
         mps_cap_vla_rate_retained cap-35 0.87-0.90, cap-25 0.72 [L4]; cpu_memory_load_floor 172 GB/s [L4];
         MIG none/tech-preview [Platforms Table 1].
Left out: the full QoS staircase with p99 numbers (that is metrics-kit diagram 05-qos-ladder);
         stream-priority (not a built lever); CPU-bandwidth break-points per rung.
```

---

## Files

Each diagram has three files: `NN-slug.drawio` (editable single-page source), `NN-slug.svg` (vector,
banner stripped, CSS-var fill fixed), `NN-slug.png` (raster, 2x scale, read back and checked for
legibility). `nvidia-gpu-anatomy.drawio` is the combined 4-page document (concatenated `<diagram>`
blocks) for viewing all pages at once. To regenerate a PNG after editing a `.drawio`: load it in the
drawio MCP (`load_diagram`), `export_diagram` to `NN-slug.svg`, replace any
`fill: var(--ge-adaptive-bg, #ffffff)` with `fill: #ffffff`, then run
`python3 .strip_and_raster.py NN-slug.svg NN-slug.png`.
