# Story spec — 01 · The GPU as a city of workshops

Rung 1.5 visual story for the **nvidia-gpu-anatomy** kit. Makes the CUDA execution model and
memory hierarchy *felt*: thread → warp of 32 → block → SM; latency hiding by switching warps; the
memory ladder (registers → L1/shared → L2 → DRAM) as travel distance; why reuse/tiling matters.

## The question

"A GPU has thousands of cores — why is my small kernel slow, and why does the same model run an
order of magnitude faster on one board than another with the same advertised TOPS?"

## The one-sentence answer (headline)

**A GPU hides waiting, not distance — it keeps thousands of workers busy by switching between them,
and it runs fast only while the parts it needs stay close.**

Hero picture: one city block = one SM. Four workshop bays (sub-partitions), benches of 32 workers
moving in lockstep (a warp), a foreman who always hands the next job to a bench that is ready
(the warp scheduler). A shelf in each bay (registers), a storeroom in the building (L1/shared), one
shared warehouse for the whole city (L2), and a port far across town (DRAM). Travel time grows with
distance; the headline is readable from the picture alone.

## Metaphor + cast

Family: **a city of workshops and warehouses.** Chosen for mechanism fidelity — the central idea
(latency = travel distance, reuse = keep parts on the bench) *is* a spatial fact, so the metaphor
carries the real mechanism rather than decorating it.

| Character (kitchen/city view) | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| City block / building | SM (streaming multiprocessor) | self-contained unit with its own workers, shelves, storeroom | a GPU is 16–20 blocks, not a sprawling city; blocks don't trade with each other |
| Workshop bay (4 per building) | sub-partition (SMSP) | each bay has one foreman and issues one job per tick | bays share the storeroom and warehouse access, not drawn as plumbing |
| Bench of 32 workers in lockstep | warp (32 threads) | one instruction drives all 32; they move as one | real lanes can diverge on branches (noted in breaks) |
| One worker at the bench | thread / lane | one instance of the job, own shelf slot | — |
| Foreman | warp scheduler | picks a ready bench each tick, one job issued | issues in order, no guessing ahead (that's the whole point) |
| A crew hired for one building | block | placed whole in one building, shares its storeroom | a building holds several crews at once |
| The work order for the whole city | grid / kernel launch | all crews from one launch | crews run in any order, can't wait on each other |
| Bench shelf | registers | fastest, right at hand, private to the worker | not a cache — assigned, never searched |
| Building storeroom | L1 / shared memory | per building, a short walk | L1 and shared are one array split by a carveout |
| City warehouse (one, shared) | L2 cache | every building sends runners here | shared → contention when the city is busy |
| The port across town | DRAM (global memory) | far, slow, holds everything | on these SoCs the port is shared with the CPU city too |
| Runner carrying a crate | a memory load in flight | takes a round trip; distance = latency | — |
| Keeping parts on the bench vs re-fetching | reuse / tiling | fetch once, use many times | — |

**Palette meaning (one hue = one concept, whole page):**
coral = compute/workers (SM, warps, workers) · sun = the foreman/issue (scheduler, dispatch) ·
sky = registers (bench shelf, nearest) · leaf = L1/shared (storeroom) · plum = L2 (warehouse) ·
stone = DRAM (the far port) · navy = ink/outline. Distance hue-codes the ladder: sky→leaf→plum→stone
goes near→far, and the same hues label the runners' routes.

## Scenes (claim · beat · figure · motion meaning · interaction · note · numbers)

**Hero** — answer as a picture; cast row; Kitchen/Engineer (City/Engineer) view switch; legend.

1. **One job, thirty-two workers, one instruction.** (concrete first)
   Beat: *this happens* — a warp is 32 threads driven by one instruction, moving in lockstep.
   Figure: scene player. Motion: a foreman hands one job card to a bench; all 32 workers raise the
   same tool together; one card = one instruction. A later step shows a branch where half the bench
   masks off (divergence). Interaction: step player. Note: 00, 02. Numbers: warp size 32 (illustrative
   label — architecture-fixed, not in constants.json), smsp_per_sm=4, fp32_cores_per_sm=128.

2. **Four foremen, one building — the first ceiling.** (therefore)
   Beat: *therefore* a building issues at most 4 jobs per tick (4 bays × 1), no matter how many
   workers. Figure: scene player. Motion: four bays each issue one card per tick; counter shows
   "4 jobs/tick" while 128 workers stand ready. Interaction: step. Note: 01. Numbers:
   smsp_per_sm=4, dispatch_bound_per_smsp=1, fp32_cores_per_sm=128, max_warps_per_sm=48.

3. **Waiting is hidden by switching, not by guessing.** (the core mechanism)
   Beat: *but* a bench that sent a runner to the warehouse would stall — so the foreman switches to
   another ready bench every tick. Predict-then-reveal: "the runner takes 20 ticks; how many other
   benches must the foreman have to never go idle?" Figure: predict + scene player. Motion: bench A
   sends a runner (greyed/waiting), foreman issues from B, C, D in the gap; when A's runner returns A
   is ready again. Interaction: predict, then step. Note: 00, 01, 03. Numbers: max_warps_per_sm=48
   (12 per bay), latency as travel (illustrative tick mapping, labelled).

4. **The memory ladder is a map — latency is travel time.** (climb the ladder of abstraction)
   Beat: *therefore* where a part lives decides the round trip: bench shelf (registers) → storeroom
   (L1/shared) → warehouse (L2) → port (DRAM). Figure: **live figure** — one slider "where the part
   lives" (or board toggle Orin/Thor) drives a runner animating the route, a round-trip-time readout,
   and a one-sentence verdict. Pure model from constants.json latencies. Interaction: slider over the
   four levels + Orin/Thor board toggle. Note: 05. Numbers (verbatim, class sibling/public from
   constants): latency_l1 (29.9/25.3 ns), latency_l2 (146/156 ns), latency_dram (675/510 ns),
   l1_shared_per_sm, l2_size. Bench-shelf (register) time has no measured latency → labelled
   illustrative "~1 tick, immediate".

5. **The cliff: when the working set outgrows the warehouse.** (the twist)
   Beat: *but* the warehouse (L2) is a fixed size. Predict-then-reveal: "a model's hot data is 30 MB.
   It fits Thor's warehouse but not Orin's. How much slower is the streaming read on Orin?" Options
   include "a little", "~2×", "~12×". Reveal: ~12.4× (Orin) — the L2 cliff. Figure: predict + bar/
   scene. Motion: footprint box grows; when it passes the warehouse outline, the supply route snaps
   from warehouse (plum, short) to port (stone, long) and the bandwidth bar collapses. Interaction:
   predict. Note: 05, 06. Numbers: l2_size (4/32 MB), l2_resident_read_bandwidth (2200/3790 GB/s),
   dram_bandwidth_read_measured (177/259 GB/s), l2_dram_bandwidth_ratio (12.4/14.6×).

6. **Reuse is keeping the part on the bench.** (therefore — the payoff)
   Beat: *therefore* the fix is to fetch a part once and use it many times before sending it back —
   tiling. Figure: scene player. Motion: naive = a runner goes to the warehouse for every single use
   (many long trips); tiled = one trip brings a crate to the storeroom, the whole crew reads it from
   there; the long routes shrink to short ones. A counter shows trips-to-warehouse falling. Interaction:
   step; optionally a two-state toggle naive/tiled. Note: 02 (tiled GEMM), 03 (reuse ladder), 06.
   Numbers: latency ratio as the payoff (latency_l2 vs latency_dram), reuse 32× (from note 02 tiled
   GEMM: 32×32 tile, each element crosses once instead of 32 times — illustrative-from-note label).

7. **Your turn** — links to the two explorers (launch-to-hardware, memory-ladder), the notes, the quiz.

Footer: "Where the city breaks" (3–5 items), numbers table rendered from the inlined JSON block.

## Truth plan

All board numbers inlined verbatim (value + source string) from `../constants.json` into
`<script id="params">`, rendered as the footer sources table. Classes: board numbers → `sibling`
(they come from the sibling metrics kit via constants.json); architecture-fixed facts not in
constants (warp size 32, 4 bays, 128 cores, D=1) → carry their constants.json key where one exists
(smsp_per_sm, dispatch_bound_per_smsp, fp32_cores_per_sm are in constants → sibling) and warp-size-32
→ `illustrative`/architecture label with CUDA PG citation text from the notes. Tick↔ns mappings used
in scenes 1–3 are labelled `illustrative`. Reuse factor 32× is labelled illustrative-from-note (02).
Hedges match the notes: "an order of magnitude", "12–15×", "usually". No new facts.
