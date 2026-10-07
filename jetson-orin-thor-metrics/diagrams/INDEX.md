# Diagrams — Jetson Orin (sm_87) vs Thor (sm_110), Rung 2 (learn-diagram)

Five diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. Every number is loaded
from `../constants.json` / the `../notes/` and carries its note tag on the canvas; nothing is retyped
into a diagram as a free constant. Measured values are coloured; datasheet values are dashed grey;
Orin counterparts of Thor roofs are dashed. Each canvas carries its own legend and sources footnote so
the exported image stands alone.

A rendering note: the PNGs were rasterised from the SVGs with cairosvg; cairo lacks a few Unicode glyphs
(the rightwards arrow `→`, `∥`, `∣`, `╲`), so those were replaced with ASCII (`->`, `||`, `|`, `vs`) in
the sources. The multiplication sign `×` and `π`/`µ` render fine. Every label now uses plain text
(`html=0` in the cell style, native `\n` line breaks) rather than HTML, so the exported SVGs contain
native `<text>` elements with no HTML foreignObject payload. draw.io still appends a trailing
`<switch>…Text is not SVG - cannot display…</switch>` fallback link to every SVG export; that banner is
stripped post-export by `.strip_and_raster.py` before rasterising, so neither the `.svg` nor the `.png`
shows it. (Note: a literal `<` inside a cell `value` — e.g. a `<->` arrow — is invalid XML and silently
blanks the whole page on load/export; use ASCII `-` or `->` instead.)

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-shared-soc` | Thor's CPU, GPU SMs (with SMSP sub-partitions), copy engines and the memset/blit path all funnel through ONE memory controller to one LPDDR pool — the single point of contention; Orin is the same topology at smaller numbers. | 00-platforms (Table 1); A.6 (L2-resident 3790, DRAM 259 GB/s); B.1 (memset blit 2.33→4.01×); B.6 (sustained 245 GB/s [M]); L4 (172 GB/s floor) |
| `02-roofline` | Hierarchical roofline Orin vs Thor; π0.5's phases (prefill AI≈731 compute-bound, action AI≈10 memory-bound) and WBC (AI≈0.4) sit far below every tensor ceiling — the model is bandwidth-bound, not TOPS-bound. | A.2 (CUDA FP32); A.3 (classic + tcgen05 FP16/INT8/FP8, datasheet 517); A.4 (NVFP4 dense 627.8, datasheet 1035); A.5 (L1 aggregate); A.6 (DRAM/L2 roofs); C.1 (π0.5 AI + sustained ~35 TFLOP/s); L4/B.8 (WBC AI) |
| `03-l2-cliff` | The L2 capacity cliff: a working set that fits L2 streams 12.4× (Orin) / 14.6× (Thor) faster than one that spills to DRAM; cliffs sit exactly at 4 MB / 32 MB; latency shelves show L2 did not get faster (~150 ns both), only bigger. | A.6 (B_L2, B_DRAM, ratio, read cliff = L2 size); A.7 (L1/L2/DRAM shelves, L2-hit saving, 190 vs 246 cyc) |
| `04-who-pays` | Who pays under co-tenancy: the memory-bound and tiny latency-critical victims absorb the slowdown; the compute-bound victim is nearly immune. One-sided asymmetry — compute starves memory (4.19×), memory barely touches compute (1.12×). | B.1 (copy/memset Table B.1.1); B.4 (controller peak, lockout onset 8/14%); B.5 (bandwidth cliff ~120/50 GB/s); B.6 (interference matrix S, L2-eviction bound 15.5); B.8 (WBC p99 Table B.8.1, overlap gate) |
| `05-qos-ladder` | The QoS ladder: context isolation + a 25–35% MPS SM cap returns a 100 Hz loop to 0 drops — but no step moves the ~172 GB/s CPU-memory floor ("no scheduler moves this"). Stream priority is not a lever; MIG is deferred. | L4 (shared-ctx 64×/51%, separate-ctx π0.5 17 ms/4.9% & GR00T 14.3 ms, plain MPS 61 ms/25%, cap-25/35 7.5/9.1/8.9 ms 0% drop, VLA rate 0.72–0.90, 172 GB/s floor, MIG deferred); B.8 (WBC solo p99 41.6 µs) |

---

## Per-diagram specs (as built)

### 01-shared-soc — block diagram
```
Teaches: everything on the SoC shares one memory controller and one LPDDR pool.
Type:    Block diagram (components + shared resources, edges labelled with measured rates).
Elements:
  CPU complex (14× Neoverse-V3AE @ 2.6 GHz) [00-platforms]
  GPU box: 20 SMs; one SM detail (128 FP32 cores, 4 tcgen05 tensor cores, 228 KB L1+shared)
           with 4 SMSP sub-partitions (1 inst/cycle each) [00-platforms]
  Copy engines (H2D/D2H/D2D); engine memset (blit path, bypasses queue arbitration)
  Shared L2 (32 MB Thor; 4 MB Orin) [00-platforms]
  ONE memory controller (highlighted as the single contention point)
  LPDDR5X 123 GB, ~273 GB/s spec [00-platforms]
Edges (measured): SM->L2 L2-resident read 3790 GB/s [A.6]; MC<->DRAM read 259 GB/s, sustained 245 [A.6/B.6];
  blit->L2 slows a reader 2.33->4.01× [B.1]; CPU->MC 172 GB/s hog floor [L4].
Reference/threshold: 172 GB/s floor annotation.
Colour: red = measured rate; black = shared path; pink = the controller + blit violation; dashed = SoC die.
Left out: per-engine queue internals, cache coherence protocol.
```

### 02-roofline — hierarchical log-log roofline
```
Teaches: π0.5 is bandwidth-bound; it never approaches the tensor ceilings.
Type:    Roofline (log-log). Horizontal = compute ceilings; sloped = memory roofs; dots = workloads.
Ceilings (measured, TFLOP/s or TOP/s): NVFP4 dense 627.8 [A.4]; tcgen05 FP8 345.4 / INT8 324.5 / FP16 192.5 [A.3];
  classic Thor INT8 128.8 / FP16 64.4, Orin INT8 83.4 / FP16 42.5 [A.3]; CUDA FP32 Thor 7.82 / Orin 5.15 [A.2].
Datasheet (dashed grey): NVFP4 dense-equiv 1035 [A.4]; INT8/FP8 517 [A.3].
Memory roofs (sloped, slope = measured bandwidth): Thor/Orin DRAM 259/177, L2-resident 3790/2200,
  L1 aggregate 3038/2067 GB/s [A.5/A.6].
Workload dots: π0.5 prefill AI≈731 (compute-bound, delivers 52.8–110 TFLOP/s) [C.1];
  π0.5 action expert AI≈10 (memory-bound, on DRAM roof) [C.1]; WBC MLP AI≈0.4 (launch-bound) [L4/B.8].
Colour: green = Thor measured, blue = Orin measured, purple = Thor 5th-gen, grey dashed = datasheet,
  dashed coloured = Orin counterpart, red/black dot = workload.
Note: axes hand-placed on a log grid (approximate); the labelled values are exact.
Layout (fix pass 2): ceiling labels are staggered — alternating left-end and right-aligned right-end of
  each line — and shortened to "name value [src]" so the dense top cluster (NVFP4 / INT8-FP8 / tcgen05)
  no longer overprints. Left out: TF32 lines kept off to reduce clutter (values in A.3); vision phase (carried in prose).
```

### 03-l2-cliff — bandwidth-vs-footprint with latency inset
```
Teaches: fitting L2 is worth 12–15×; L2 got bigger between generations, not faster.
Type:    Annotated curves (two boards) + a small latency-shelf table inset.
Elements: Thor curve 3790->259 GB/s with cliff at 32 MB; Orin curve 2200->177 GB/s with cliff at 4 MB;
  double-arrow callouts 14.6× (Thor) and 12.4× (Orin) [A.6].
Reference lines: vertical dashed at each board's L2 capacity (the cliff).
Inset table [A.7]: L1 29.9/25.3 ns; L2 ~146/~156 ns (unchanged!); L2 cliff 4.0/32 MB; DRAM ~675/~510 ns;
  L2 save ~530ns 4.6× / ~355ns 3.3×; note that L2 latency is fixed in time not cycles (190 vs 246).
Colour: solid green = Thor measured, dashed blue = Orin measured, vertical dashed = cliff.
Note: bandwidth axis is log; curve shapes schematic, plateaus/cliffs at exact source values.
Left out: copy/triad cliffs (≈ half L2) mentioned in A.6 but not drawn.
```

### 04-who-pays — interference matrix
```
Teaches: compute-bound victims are immune; memory-bound and tiny latency-critical victims pay.
Type:    Matrix / heat map. Rows = victim class, columns = aggressor class, cell = measured slowdown + mechanism.
Rows:    compute-bound L2-resident GEMM; memory-bound streaming (GEMV / stream read); tiny latency-critical WBC (p99).
Cols:    copy engine (+memset blit); CPU memory hog; GPU compute co-tenant (same context, SM-saturating); L2-evicting co-tenant.
Cells (measured, Thor; Orin in parens): see table above — key cells IM|IC 4.19 (Orin 2.66), IC||IC 1.97,
  memset 2.33->4.01×, WBC INT8-compute p99 1.70 ms, WBC worst mix 5.9 ms = 141×, L2-eviction bound 15.5×.
Lower-bound marking: ‡ on cells below the 0.90 co-execution overlap gate [B.8].
Colour: cell fill = severity (green≈1 / orange~2× / red≥2.5× or tail blow-up / yellow = capacity-dependent).
Left out: the full 4×4 synthetic+real matrix of B.6 (only the governing cells shown).
```

### 05-qos-ladder — staircase of sharing disciplines
```
Teaches: isolation + an SM cap fixes the loop, but nothing beats the 172 GB/s floor.
Type:    Ladder / staircase (rising step height = QoS delivered to the WBC loop).
Steps:   1 shared context (p99 110.7 ms, 64×, 51% dropped); [stream priority = not a built lever];
  2 separate process (π0.5 p99 17 ms / 4.9% dropped, GR00T 14.3 ms / 98% held; shared-ctx 64× was ~90% topology);
  3 plain MPS (61 ms / 25%); 4 MPS + SM cap 25/35% = THE FIX (cap-25 7.5 ms, cap-35 9.1 ms / GR00T 8.9 ms, 0% drop;
  VLA cost cap-35 ~0.87–0.90, cap-25 ~0.72); 5 MIG deferred.  [all L4]
Reference line: horizontal thick red dashed = ~172 GB/s CPU-memory floor labelled "no scheduler moves this" [L4];
  10 ms deadline annotation (only step 4 clears it).
Colour: red = loop broken, green = meets deadline, grey dashed = deferred/not-a-lever, red dashed = the floor.
Layout (fix pass 2): each step's numbers now sit as a compact 2–3 line label directly above its own box
  (the fix box stays a filled green callout), instead of floating high with lead lines; the lead lines were
  removed. The "increasing isolation / QoS ->" arrow was shortened into the open wedge left of the staircase.
  The 10 ms deadline note moved to the clear top band and the 172 GB/s floor label sits just below the floor
  line, both kept clear of the step boxes.
Left out: the CPU-bandwidth break-points per rung (37–186 GB/s band) summarised in the note, not drawn.
```

---

## Files

Each diagram has three files: `NN-slug.drawio` (editable source), `NN-slug.svg` (vector), `NN-slug.png`
(raster, 2× scale, read back and checked for legibility). To regenerate a PNG after editing a `.drawio`:
load it in the drawio MCP (`load_diagram`), `export_diagram` to `NN-slug.svg`, then run
`python3 .strip_and_raster.py NN-slug.svg NN-slug.png` — the helper strips draw.io's trailing
"Text is not SVG" fallback `<switch>` from the SVG and rasterises with cairosvg at scale 2.0
(`DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` is set inside it).
