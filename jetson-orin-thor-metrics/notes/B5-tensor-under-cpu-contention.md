# B.5 Tensor under CPU contention

**Source:** book.pdf §B.5 — `doc-b-proxy-workload/tensor-contention.tex`; tables B.5.1 (tile → arithmetic intensity), B.5.2 (fixed-shape family), B.5.3 (tcgen05 dense vs sparse under contention); Figures B.5.1–B.5.3  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
A CPU memory hog slows a tensor GEMM in proportion to the GEMM's own operand-byte demand on the shared controller — TF32 most (2.96× on Thor), INT4 least (1.31×) — the slowdown decays toward 1.0 as arithmetic intensity rises, and it bites on a cliff rather than a ramp: the victim stays within ≈ 1.1× until the CPU draws about half the bandwidth it can reach unthrottled (≈ 120 GB/s on Thor, ≈ 50 GB/s on Orin), then climbs steeply.

## What it measures
The slowdown S = R_solo / R_co (solo over contended rate, in FMA per clock per SM) of a tensor kernel under a CPU memory co-tenant, and what governs it. Three variables are swept: the victim's number format, the victim's arithmetic intensity, and the aggressor's memory bandwidth (§B.5 "Objective and metric").

## How
**Victims.** A fixed-shape 2:4-sparse tensor GEMM at five formats — INT4, INT8, FP16, TF32, and FP8 (Thor only) — isolates the datapath. A warp-tiled sparse GEMM with output tile swept 1×1 to 4×4 isolates arithmetic intensity; its 64 MiB operand pool exceeds L2, so the low-tile end is DRAM-fed. **Aggressor.** A sustained CPU write-hog held alive across the victim by a liveness gate (a victim outliving the hog is discarded). Full-tilt at the saturating thread count (12 on Thor, 10 on Orin) for the format and intensity sweeps; rate-limited (leaky bucket) with requested GB/s as the input for the bandwidth sweep. 5 trials per fixed-shape cell, 32 per tiled cell and bandwidth setpoint (§B.5 "Experiment setup").

A second sub-experiment (Thor only) runs the production `tcgen05` datapath — cuBLASLt dense and cuSPARSELt 2:4-sparse — over square GEMMs N = 512–8192 under the same hog.

## Predicted
Ordinal predictions along each axis. **Intensity:** more MACs per fetched byte lowers controller demand, so S decays toward 1 — until a register-blocked tile exhausts the 64K-register file (an M × N tile needs ≈ 4MN accumulator registers per thread), occupancy collapses, and S rebounds. **Format:** operand width × datapath rate sets each format's operand-byte demand; higher demand, more slowdown — TF32 most, narrow integer formats least. **Aggressor bandwidth:** contention should not grow linearly from zero; the victim stays robust until the CPU claims a large fraction of the controller, then degrades sharply (§B.5 "Prediction model").

## Measured
Arithmetic intensity of an M × N output tile in fetched-MACs per operand byte: I(M,N) = MN/(M+N) · ρ_fmt, with ρ = 114, 228, 410, 456 MAC/byte for TF32, FP16, INT8, FP8 (Eq. B.5.1). Operand-byte demand of a fixed-shape victim: D_solo = b_fmt · R_solo, with b = 0.5, 1, 1, 2, 4 bytes for INT4, INT8, FP8, FP16, TF32 (Eq. B.5.2).

Fixed-shape 2:4-sparse family under the saturating hog (§B.5 Table B.5.2):

| Format | Thor D_solo | Thor S | Orin D_solo | Orin S |
|---|---|---|---|---|
| INT4 | 21 | 1.31 | 59 | 1.13 |
| FP8 | 81 | 1.41 | — | — |
| INT8 | 100 | 2.06 | 119 | 1.13 |
| FP16 | 200 | 2.52 | 213 | 1.30 |
| TF32 | 518 | 2.96 | 515 | 1.37 |

Tiled sweep (Figure B.5.1, prose): Thor INT8 decays 2.58× → 1.30× as intensity rises; Orin shows the same shape, compressed. FP16 and TF32 rebound at the largest tiles (register wall).

Bandwidth setpoint (Figure B.5.2, prose): victims stay within ≈ 1.1× until the CPU draws roughly half its unthrottled bandwidth — about 120 GB/s on Thor, 50 GB/s on Orin — then climb steeply in the same order (TF32, FP16 lead; INT8, INT4, FP8 flattest). The dense control stays flat.

Thor `tcgen05` under the hog, delivered Top/s (§B.5 Table B.5.3):

| Format | | solo (N = 8192) | N = 1024 | 2048 | 4096 | 8192 |
|---|---|---|---|---|---|---|
| INT8 | sparse | 426 | 149 | 48 | 68 | 62 |
| INT8 | dense | 326 | 85 | 49 | 38 | 37 |
| FP8 | sparse | 366 | 192 | 98 | 120 | 85 |
| FP8 | dense | 297 | 114 | 100 | 46 | 44 |
| NVFP4 | sparse | 730 | 200 | 100 | 139 | 153 |
| NVFP4 | dense | 627 | 125 | 101 | 109 | 83 |

## The gap, and what it means
**Slowdown tracks operand-byte demand.** S rises with D_solo on both boards. TF32 (4 bytes per element) is most slowed; FP16 exceeds INT8 because it moves twice the bytes per MAC. Orin's weaker aggressor compresses the spread (INT8 pulled into the INT4 group), so the ordering, not the magnitude, carries across boards.

**Intensity buys robustness, to a point.** More MACs per fetched byte let the kernel hide contended memory latency. The decay ends at the register wall — a property of the register-blocked hand-tiled kernel, not of the datatype.

**Aggressor bandwidth bites on a cliff.** The degradation is a saturation cliff, not a linear tax: a GPU tensor workload can share LPDDR5 with substantial CPU traffic and stay robust until the CPU crosses about half its own ceiling.

**One lever, invisible to TOPS.** All three axes move the memory-demand rate at the shared controller; contention bites when the sum saturates it. Two kernels at equal nominal TOPS can differ by more than 2× in delivered rate under an identical co-tenant.

**Production datapath.** Dense and sparse are near-immune while L2-resident (N ≤ 1024, ≈ 1.1×) and rise steeply once DRAM-fed (N ≥ 2048). Once DRAM-fed, sparse's contended rate pulls above dense's (widest at N = 8192) because 2:4 compression streams half the operand. Every contended rate sits far below solo — the advertised number does not survive contention, and compression softens the penalty without removing it (§B.5 "Comparison and discussion").

## So what
Interpretation (mine, from the source): on a robot where the CPU streams sensor data, budget the CPU's DRAM traffic to stay under about half its ceiling, and prefer narrow formats and high-reuse tiles for the GPU tensor work that must hold its rate.

## Terms introduced
- **operand-byte demand (D_solo)** — bytes of operand traffic a victim places on the controller per unit time when solo; b_fmt × R_solo.
- **ρ_fmt** — a format's operand density in MACs per operand byte (TF32 114, FP16 228, INT8 410, FP8 456).
- **register wall** — the tile size at which accumulator registers exhaust the 64K-register file, collapsing occupancy.
- **liveness gate** — a check that the aggressor outlived the victim in a trial; trials failing it are discarded.
- **leaky bucket** — a rate limiter that releases work at a fixed requested rate; used to set the CPU hog's bandwidth.
- **saturation cliff** — a slowdown curve that is flat until the controller saturates, then steep.
- **DRAM-fed / L2-resident GEMM** — a GEMM whose operands stream from DRAM / fit in L2 (N ≥ 2048 / N ≤ 1024 here on Thor).
