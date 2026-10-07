# Explorers — rung 3 (learn-explorer)

Two single-file, no-build, double-click HTML explorers for the *nvidia-gpu-anatomy* concept primer.
Each inlines its parameters in a `<script type="application/json">` block (also written out as
`params.json`), every parameter copied from `../constants.json` with its `source` — nothing retyped.
Prediction functions are factored into a pure IIFE that also runs under node (used for the
`console.assert` self-tests and the NaN slider-extreme sweep). Both pass their self-tests and a NaN
sweep over every slider/selector extreme (512 and 20 combinations respectively; 0 bad). Open with a
double-click or `open 01-launch-to-hardware.html`. No server, no network, no build step.

The primer is a *concept* kit: these explorers teach the CUDA execution model (how a launch maps to
SM slots) and the memory hierarchy (where a working set sits), not the metrics kit's roofline/co-tenancy
measurements. They are the mechanism pictures behind Table 1 of `../../jetson-orin-thor-metrics`.

---

## Spec — 01-launch-to-hardware.html

```
Explorer: Launch → hardware (what actually fits on an SM)
Teaches:  A kernel launch does not "fill" an SM; the hardware packs whole blocks on until the first
          of five per-SM limits (resident warps / threads / blocks / register file / shared memory)
          runs out, and the resulting occupancy is the opportunity to hide latency — not the issue
          rate (notes 02, 03; CUDA PG §1.2.2/§3.2.2).
Inputs:
  - board (select): Thor T5000 (sm_110) | AGX Orin (sm_87) — picks SM count, clock, max-blocks/SM.
  - threads per block (slider): 32 … 1024, step 32. Why: one warp (32) to the 1024-thread cap used
      by the kit's B.3 kernels and A.5 sweep.
  - grid size (slider): 1 … 4096 blocks. Why: a single-block control launch to a grid of thousands,
      to show the "waves" number cross 1.
  - registers per thread (slider): 16 … 255. Why: 255 is the architectural max; crossing ~42 at
      1536 threads is where the register file starts to bind (note 03's worked limit).
  - shared memory per block (slider): 0 … 100 KB. Why: 0 (unused) up to a large tile that competes
      with the per-SM L1/shared array (164 Orin / 228 Thor KB).
Outputs:
  - warps per block = ceil(threads / 32).
  - blocks per SM admitted = min over the five limits (each limit shown; the binding one highlighted):
      warp floor(48/wpb); thread floor(1536/threads); block max_blocks_per_sm; register
      floor(65536/(regs·threads)) [note-03 teaching form]; shared-mem floor(l1_shared_KB/smem_KB).
  - achieved occupancy % = resident warps ÷ 48 (note 03 definition).
  - waves over the GPU = grid blocks / (blocks per SM × SM count).
  - SMSP view: resident warps ÷ 4 sub-partitions.
Picture: SVG grid of the board's SMs filling green in proportion to resident warps / 48, with a
         banner naming the binding limit.
Preloaded cases (from the notes):
  - A.1 probe — 512-thread block (16 warps, 4 warps/SMSP), Thor.
  - B.3 kernel — 1024-thread block (32 warps, 67% occupancy at 64 regs scale), Orin.
  - WBC — a single 32-thread warp, one block: a launch/latency-bound control kernel.
Measured overlays: none — this page is model-derived from the residency limits (CUDA PG + Table 1);
  the "measured" diamonds live on the memory-ladder page. The occupancy-vs-issue-rate caveat cites
  the kit's measured 4.24× runtime spread at flat occupancy (note 03 / B.3) in the why-panel.
Out of scope: warp-granularity register allocation (uses note-03 per-thread×threads form), the
  opt-in max-shared-per-block carveout rules, divergence, cluster/CGA scheduling, issue efficiency.
```

Self-tests (reproduce the source's own numbers):
1. 512-thread A.1 probe → 16 warps, 16/4 = 4 warps per SMSP (note 02).
2. 1024-thread B.3 kernel → 32 warps; 32/48 = **67%** occupancy (note 03).
3. 64 registers/thread on a 512-thread block → floor(65536/(64·512)) = 2 blocks by registers = 32
   resident warps (note 03's "a kernel at 64 registers/thread fits only 1024 threads = 32 warps = 67%").
4. Waves formula: 256 blocks of 512 thr on Thor → 3 blocks/SM → 256/(3·20) waves (self-consistency).

---

## Spec — 02-memory-ladder.html

```
Explorer: The memory ladder (where a working set sits decides its speed)
Teaches:  A GPU's memory is a capacity ladder (registers → L1/shared → L2 → DRAM); a kernel runs at
          the bandwidth/latency of the level its footprint fits, and because the L2:DRAM gap is
          12.4× (Orin) / 14.6× (Thor) and the cliff is sharp, capacity decides speed more than the
          datasheet rate (notes 05, 06; metrics-kit A.6/A.7).
Inputs:
  - board (select): Thor T5000 (32 MB L2) | AGX Orin (4 MB L2).
  - working-set footprint (log slider): 1 KB … 1 GB. Why: straddles both L2 sizes (4 / 32 MB) to put
      the cliff under the thumb, from a register-sized set to a weights-sized one.
  - access pattern (select): streaming (bandwidth-bound) | dependent pointer-chase (latency-bound).
Outputs:
  - level that holds it = registers (≤256 KB reg file, teaching bound) / L1-shared (≤ per-SM KB) /
      L2 (≤ board L2 MB) / DRAM, by capacity.
  - bandwidth seen (streaming) = measured plateau of that level (A.5/A.6); latency seen
      (pointer-chase) = measured landmark of that level (A.7).
  - time to touch footprint once = bytes/bandwidth (stream) or (bytes/128 B)·latency (chase).
Picture: SVG four-rung ladder; the resident level is lit; the 4/32 MB L2 cliff is drawn as a dashed
         line labelled with the board's L2:DRAM ratio; each rung carries its measured plateau/latency
         as a diamond (A.6/A.7), visually distinct from the lit level.
Preloaded cases (from the notes):
  - WBC weights ≈ 0.5 MB (roofline INDEX / B.8; WBC INT8 MLP) — fits L2 on both boards.
  - π0.5 KV cache ≈ 13 MB (C.1: "~13 MB of KV at S≈712") — fits Thor L2, spills Orin L2.
  - GR00T-scale ≈ 27.5 MB (RM fp16 decode-GEMM weight footprint, B.6 Table B.6.1) — fits Thor L2,
      spills Orin L2; the cleanest demonstration of the cliff.
  - 64 MB stream — spills both boards' L2 to the DRAM roof.
Measured overlays: the A.6 bandwidth plateaus (L2-resident & DRAM) and A.5 L1 plateau, and the A.7
  latency landmarks (L1/L2/DRAM), as diamonds on each rung — distinct from the model-lit level.
Out of scope: write-bandwidth asymmetry, the L1/shared runtime carveout split, cache-line replacement
  policy, co-tenant eviction (that is the metrics kit's B.2/B.7 territory), unified-memory page faults.
```

Self-tests (reproduce the source's own numbers):
1. L2:DRAM bandwidth ratio from the two measured plateaus — Orin 2200/177 ≈ **12.4×** (A.6).
2. Thor 3790/259 ≈ **14.6×** (A.6).
3. 27.5 MB is L2-resident on Thor but spills to DRAM on Orin, and the Thor-L2↔Orin-DRAM streaming
   time ratio is > 10× — the L2 cliff (A.6).
4. A 64 MB stream spills **both** boards' L2 to DRAM.

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-launch-to-hardware.html` | which per-SM limit binds a launch, and the occupancy it yields (≠ issue rate) | board, block, grid, registers, shared memory | notes 01/02/03; CUDA PG §1.2.2/§3.2.2; Platforms Table 1 |
| `02-memory-ladder.html` | which memory level holds a footprint, and the 12–15× L2 cliff | board, footprint, access pattern | notes 05/06; A.5, A.6, A.7; Platforms Table 1 |
| `params.json` | the constants both pages load | — | copied from `../constants.json` |

Open with a double-click, or `open 01-launch-to-hardware.html`. No server, no network, no build step.
