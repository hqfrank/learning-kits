# 04 — CUDA cores vs tensor cores

**Sources:** CUDA Programming Guide §1.2.2 (A-PM); Ampere/Blackwell architecture material (B-AMPERE, B-BLACKWELL, B-FORUMS); metrics-kit `A2`, `A3`, `A4`, Table 1 (C-PLAT) and `constants.json`. See [[../SOURCES]].

## In one sentence
CUDA cores are scalar arithmetic lanes that do one multiply-add per lane per instruction (FP32, packed FP16, INT), while tensor cores are matrix units that multiply and accumulate a whole small matrix tile per instruction, and the tensor path is one to two orders of magnitude faster for the dense linear algebra that dominates neural networks.

## What it is
Inside each sub-partition are two kinds of math unit ([[01-sm-and-smsp]]):

- **CUDA cores** — the FP32/INT lanes. A warp instruction drives 32 lanes, each doing a scalar fused multiply-add. Precisions: FP32, packed FP16 (`half2`, two values per lane), and INT8 via the `dp4a` dot-product instruction (C-KIT-NOTES A2).
- **Tensor cores** — matrix-multiply-accumulate (MMA) units, one per sub-partition (4 per SM). One instruction multiplies two small matrix tiles and accumulates into a third, so it retires far more operations per issue than a scalar lane (B-FORUMS; B-BLACKWELL). Precisions depend on generation.

## How it works
A CUDA-core ceiling has one shape: issue rate × 32 lanes × ops-per-lane × 4 sub-partitions × clock × SM count (C-KIT-NOTES A2, Eq. A.2.1). You cannot beat the dispatch bound; you widen the work per instruction (FP16 packs 2, INT8 `dp4a` does 4 multiply-adds).

**Issue count versus instruction width.** The dispatch bound says one warp instruction per cycle per sub-partition; it says nothing about how much arithmetic that instruction does. A lane is 32 bits wide. `FFMA` uses the whole lane for one FP32 multiply-add (2 ops). `HFMA2` tells the lane to treat its register as two 16-bit halves and multiply-add both at once — `(a.lo·b.lo + c.lo, a.hi·b.hi + c.hi)` — so the same issue slot, the same 32 lanes and the same pass through the pipe retire 64 FP16 results (4 ops per lane). CUDA's `half2` type is that pair packed in one 32-bit register. `dp4a` goes further: four INT8 products summed into one INT32 accumulator, 8 ops per lane. That is the w in the kit's ceiling formula rate = θ × 32 × w × 4 × f × n_SM (C-KIT-NOTES A2, Eq. A.2.1): θ stays at 1, w is 2 / 4 / 8. You cannot issue more instructions; you can make each one do more. The Thor caveat below can now be stated in θ and w. Width w is a property of the instruction and is 4 on both boards (the SASS gate confirms Thor really executes `HFMA2`, two FP16 FMAs per lane). If `HFMA2` issued at θ = 1 like `FFMA`, FP16 would run at exactly 2× FP32; Orin's 1.87× is that case. Thor's 1.01× with w = 4 means θ_HFMA2 ≈ 0.5: the sub-partition accepts an `HFMA2` warp only every two cycles, so half the instruction rate × double the width nets out to the FP32 rate. The kit measures the net rate, not θ_HFMA2 directly; the half-rate explanation (one of the two 16-lane halves lost its FP16×2 capability on Blackwell CUDA cores, as IMAD uses one half in A1) is **my inference** from the formula (C-KIT-NOTES A1, A2).

A tensor core instead consumes matrix tiles. The portable path is the warp-level **`mma`** instruction (classic MMA), which any hand-written kernel can issue (C-KIT-NOTES A3). *Portable* means the programming model travels: `mma.sync` has had stable PTX semantics since Volta (register operands, fixed shapes such as `m16n8k16`), so one kernel source compiles and runs correctly on Orin, Thor, datacenter parts and desktop GPUs alike, with the compiler lowering it to each chip's tensor core. Portable does not mean equal speed — the same kernel gets 42.5 TFLOP/s FP16 on Orin and 64.4 on Thor, the clock × SM-count ratio — it means no rewrite. The price is that it reaches only what every generation can do (the *floor*). `tcgen05` is the opposite: it requires `sm_110a` compilation (the `a` suffix marks architecture-specific, non-forward-compatible features), tensor-memory allocation and a single-thread asynchronous issue model; it does not compile for Orin and carries no promise for the next generation, which is why it is reached through cuBLAS/CUTLASS rather than hand-written code. The gap between the two tiers is the kit's "programmability cost" (C-KIT-NOTES A3.6; PTX ISA target notes; **my explanation** of the term). Blackwell adds **`tcgen05`**, a fifth-generation datapath that stages operands in shared memory and **tensor memory (TMEM)** and accumulates in TMEM; it is reached only through tuned libraries (cuBLAS/CUTLASS) (B-BLACKWELL CUTLASS docs; C-KIT-NOTES A3). So on Blackwell there are two tensor ceilings per precision: the classic floor and the much higher tcgen05 ceiling.

**How small is "small"?** The classic warp-level `mma` fixes its tile shape in the instruction name, m×n×k: A is m×k, B is k×n, the accumulator C/D is m×n. The kit's A.3 shapes (C-KIT-NOTES A3 §Setup):

| Precision | Shape | A tile | B tile | C/D tile | MACs / instruction |
|---|---|---|---|---|---|
| FP16 | `m16n8k16` | 16×16 | 16×8 | 16×8 | 2048 |
| INT8, FP8 | `m16n8k32` | 16×32 | 32×8 | 16×8 | 4096 |
| TF32 | `m16n8k8` | 16×8 | 8×8 | 16×8 | 1024 |

MACs per instruction is m × n × k: each of the m × n output elements is a dot product along the shared dimension k (k multiplies and k accumulating adds), so `m16n8k16` is 16 × 8 × 16 = 2048 MACs = 4096 FLOPs, the "× 2" in the kit's rate formula (C-KIT-NOTES A3 Eq. A.3.2). It is not the product of the two input-tile sizes. The same rule gives the GEMM cost 2·M·N·K that C.1 uses to size π0.5's layers. The output tile is always 16×8 = 128 values (4 per thread across the warp), and k grows as the element narrows, so one instruction consumes the same operand *bytes* at every precision (A: 16×16×2 B = 16×32×1 B = 512 B). The reason is where the operands live: for classic `mma` every operand is a fragment in the warp's registers, and the instruction names a fixed number of 32-bit registers per thread for each — 4 for A (32 threads × 16 B = 512 B), 2 for B (256 B), 4 for the accumulator (512 B). A fixed register set is a fixed byte budget; FP16 fills A's 512 B with 256 elements (16×16), INT8 with 512 (16×32), so k doubles while m stays 16. The accumulator does *not* narrow: it is kept wide (FP32 for FP16/TF32/FP8 inputs, INT32 for INT8) so running sums do not overflow, and 16×8 × 4 B = 512 B at every precision. Narrow inputs therefore buy a longer dot product per instruction, never a bigger output tile — the same narrow-in, wide-accumulate rule that keeps the π0.5 fp8 engines on fp32 accumulators and softmax (C-KIT-NOTES C1). `tcgen05` escapes the register bound by taking A and B from shared memory and keeping C in tensor memory, which is how its tile reaches 128×256 (A-PM warp-matrix functions; PTX ISA mma fragment layouts; **my explanation** of the byte accounting). The 32×32 tile of the B3 tiled GEMM is a *block-level* unit staged in shared memory; the tensor core never sees it whole. A kernel carves it into fragments and issues one `mma` per fragment product — a 32×32×32 block step is 2×4×2 = 16 `m16n8k16` instructions. "Small" is relative to the matrices (thousands on a side) and to `tcgen05`, where a single Thor instruction can cover up to 128×256 in M×N with operands in shared/tensor memory — a large part of why that path reaches ~3× the classic rate (C-KIT-NOTES A3.6; B-BLACKWELL; **my explanation** of the byte-constancy and the 16-instruction count).

**Who holds the matrix when a warp issues `mma`?** All 32 threads, in **fragments**. For the kit's FP16 shape `m16n8k16` (C-KIT-NOTES A3): A is 16×16 = 256 fp16 values, 8 per thread (4 registers, two fp16 packed per 32-bit register); B is 16×8 = 128 values, 4 per thread (2 registers); the fp32 accumulator C/D is 16×8 = 128 values, 4 per thread (4 registers). The warp issues one `mma`; the sub-partition's tensor core reads every thread's fragments, computes the whole 16×8×16 product, and writes the 128 results back scattered over all 32 threads' accumulator registers (A-PM warp-matrix functions; **my explanation** of the per-thread counts from the shape). No thread owns the tensor core and no thread idles: the warp owns it. This is why the kit saturates tensor throughput by sweeping ILP and warps *per sub-partition* — one tensor core, fed by whichever resident warps have an `mma` ready (C-KIT-NOTES A3).

**How the instruction finds 512 B spread over 32 threads.** The same way any warp instruction does ([[01-sm-and-smsp]]): it names one register per operand and every lane supplies its own slot of that name. `HMMA.16816.F32 R8, R0, R4, R8` (SASS, schematically) names A as the quad R0–R3, B as the pair R4–R5, C/D as the quad R8–R11 — three base names, not 32 × 10. Which matrix element each lane's register holds is fixed by the instruction, not the programmer: the PTX ISA publishes a fragment layout per shape. For the FP16 A operand of `m16n8k16`, thread *t* holds rows *t/4* and *t/4 + 8* at columns (*t* mod 4)·2, +1, and the same +8, two halves per register; the 32 lanes' 8 elements each tile the 16×16 exactly once. The tensor core is wired to that table, so it reads R0–R3 from all lanes through the register datapath and knows by lane and register which element it has — no addresses, no gather. The matrix in memory is still ordinary row-major; the kernel's job before the `mma` is to move each element into the lane and register the layout demands. Hand-written code does that with per-thread loads from shared memory; the dedicated `ldmatrix` instruction reads 8×8 blocks from shared memory and deposits them straight into fragment layout across the warp, and shuffles ([[02-threads-warps-blocks-grids]]) fix up values that land in the wrong lane. Production kernels run global → shared (wide loads) → fragments (`ldmatrix`) → `mma` → C fragments written back by the inverse map. This choreography is the price of register-resident operands; `tcgen05`'s descriptors (an address plus layout for operands left in shared memory) remove it, at the cost of portability (PTX ISA, warp-level matrix fragment layouts and `ldmatrix`; **my explanation** of the SASS sketch and the pipeline).

**`tcgen05` breaks that picture.** On Thor the fifth-generation MMA is issued by a single thread, its operands live in shared memory and tensor memory rather than in the warp's registers, and it runs asynchronously while the warp continues (B-BLACKWELL; C-KIT-NOTES A3). The other 31 threads are not idle because nobody is waiting on registers; the tensor core works from memory. The matrix per instruction is far larger and the rate far higher (192.5 vs 64.4 TFLOP/s FP16, `tensor_tcgen05_fp16` vs `tensor_classic_fp16`), but a kernel written with plain `mma` never touches it — the "programmability cost" of A.3.6.

**Generations:** Orin (Ampere, sm_87) carries **3rd-generation** tensor cores supporting FP16, TF32 and INT8 (B-AMPERE lists the Ampere datatypes; C-PLAT). Thor (Blackwell, sm_110) carries **5th-generation** tensor cores that add FP8 and **NVFP4**, a 4-bit float with micro-block (two-level) scaling (B-BLACKWELL; C-PLAT).

## On Orin and Thor (numbers from constants.json)
CUDA-core ceilings (`cuda_*_ceiling`, C-KIT-NOTES A2):

| CUDA-core path | Orin | Thor |
|---|---|---|
| FP32 | 5.15 TFLOP/s | 7.82 TFLOP/s |
| FP16 (`half2`) | 9.64 TFLOP/s (1.87× FP32) | 7.86 TFLOP/s (1.01× FP32) |
| INT8 (`dp4a`) | 10.63 TOP/s | 16.10 TOP/s |

Caveat first: **Thor's CUDA cores have no double-rate FP16** — packed FP16 runs at the FP32 rate (C-KIT-NOTES A2). On Thor, FP16 pays off only on the tensor path.

Tensor-core ceilings (`tensor_*`, `nvfp4_*`, C-KIT-NOTES A3/A4):

| Tensor path | Orin (3rd-gen) | Thor (5th-gen) |
|---|---|---|
| classic `mma` FP16 | 42.5 TFLOP/s | 64.4 TFLOP/s |
| classic `mma` INT8 | 83.4 TOP/s | 128.8 TOP/s |
| tcgen05 FP16 | — | 192.5 TFLOP/s |
| tcgen05 INT8 | — | 324.5 TOP/s |
| tcgen05 FP8 | — | 345.4 TFLOP/s |
| NVFP4 dense | — | 627.8 TFLOP/s |
| NVFP4 2:4-sparse | — | 878.3 TFLOP/s |

The tensor path is ~8× the CUDA-core path for FP16 on Orin (42.5 vs 5.15) and, through tcgen05, ~25× on Thor (192.5 vs 7.82) **(my explanation, ratios of the constants above)**.

## Common confusions
- **TOPS is not achievable rate.** The datasheet peaks assume tcgen05 at the best shape; a tuned library reaches 55–75% of them, and a portable `mma` kernel far less (C-KIT-NOTES A3). The classic FP8 floor is only 26% of the 517 datasheet figure (C-KIT-NOTES A3).
- **The sparsity 2× is advertised, not delivered.** NVFP4 2:4-sparse delivers 1.40× over dense cross-vehicle, not 2× (`nvfp4_sparsity_multiplier_delivered`, C-KIT-NOTES A4).
- **FP16 kernels tuned on Orin lose their speedup on Thor's CUDA cores.** Orin's packed-half runs at 1.87× FP32; Thor's at 1.01× (C-KIT-NOTES A2). Move the work to tensor cores on Thor.
- **"Tensor core" is not a separate chip.** It is a unit inside each sub-partition, one per SMSP, sharing the SM's operand paths (B-FORUMS).

## Why it matters for robotics workloads
A vision-language-action policy is almost all matmul, so it lives on the tensor cores; its deployable precision (FP16 vs FP8 vs NVFP4) sets both its speed and its memory traffic (C-KIT-NOTES L4, [[05-memory-hierarchy]]). But the metrics kit's blunt finding is that for the co-tenancy that governs a robot, the tensor peak is almost irrelevant: real workloads sit 2–3 orders of magnitude below the advertised NVFP4/INT8/FP16 numbers, bound by memory and scheduling instead (C-KIT-NOTES L4). Knowing which datapath a kernel uses tells you which ceiling to draw — and the kit shows the ceiling is rarely the binding one ([[08-measuring-a-gpu]]).

## Terms introduced
- **CUDA core** — a scalar FP32/INT arithmetic lane; 128 per SM. See [[01-sm-and-smsp]] (B-FORUMS; C-PLAT).
- **tensor core** — a matrix-multiply-accumulate unit, one per sub-partition; retires a tile per instruction (B-FORUMS; C-PLAT).
- **classic mma** — the portable warp-level MMA instruction; the floor tensor tier. Reused from `../jetson-orin-thor-metrics/glossary.md` (C-KIT-NOTES A3).
- **tcgen05** — Blackwell's 5th-generation tensor datapath with tensor memory; the datasheet-peak path. Reused from the metrics-kit glossary (C-PLAT; B-BLACKWELL).
- **tensor memory (TMEM)** — Blackwell on-chip memory that stages tcgen05 operands and holds the accumulator (B-BLACKWELL CUTLASS docs).
- **NVFP4** — block-scaled 4-bit float (E2M1 + per-block scale); Thor only. Reused from the metrics-kit glossary (C-KIT-NOTES A4; B-BLACKWELL).
- **dp4a / half2** — the INT8 dot-product and packed-FP16 CUDA-core instructions. Reused from the metrics-kit glossary (C-KIT-NOTES A2).
- **TF32 / FP8 / FP16 / INT8** — tensor-core precisions; Orin has FP16/TF32/INT8, Thor adds FP8 and NVFP4 (C-PLAT).
- **fragment** — the slice of a matrix tile (A, B or accumulator) that one thread of the warp holds in its registers for a warp-level `mma`; the 32 fragments together are the whole tile (A-PM warp-matrix functions).
- **instruction width (w)** — the arithmetic operations one lane retires per instruction: 2 for FFMA, 4 for packed-FP16 HFMA2, 8 for dp4a; independent of the issue rate θ (C-KIT-NOTES A2).
- **mma shape (m×n×k)** — the fixed tile a warp-level `mma` multiplies: A m×k times B k×n into C m×n; e.g. `m16n8k16` for FP16 (C-KIT-NOTES A3).
- **portable path** — code using instructions with stable cross-generation semantics (classic `mma.sync`) so one source runs on every tensor-core GPU; reaches the floor, not the datasheet peak (C-KIT-NOTES A3).
- **fragment layout** — the per-shape table (PTX ISA) that fixes which matrix element each lane holds in which register for a warp-level `mma`; the tensor core is wired to it (PTX ISA warp-level matrix instructions).
- **`ldmatrix`** — a warp instruction that loads 8×8 blocks from shared memory directly into fragment layout across the warp (PTX ISA).
