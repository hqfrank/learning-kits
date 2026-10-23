# Story 1 spec — The robot's kitchen

**Question:** My robot's GPU looks half idle — so why is the stack falling behind, and how would I prove it?

**Headline:** A small robot computer usually runs out of cooks (CPU) before it runs out of oven (GPU).

**Hero:** orders pile up at the window, every cook's busy meter is full, most oven trays are dark, one pantry door is shared, the pass bell beats.

## Cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| kitchen | on-board computer | one place, shared stations | — |
| cooks | CPU cores | do the per-order bookkeeping | real schedulers do not bind orders to named cooks |
| oven, trays | GPU, SMs | bakes the batched heavy work | a GPU is thousands of threads in warps of 32 |
| pantry door | shared memory (integrated SoC) | cooks and oven queue at one door | not true for a discrete GPU |
| orders | sensor messages | arrive on their own beat | — |
| pass bell | control-loop deadline | a plate must leave on every ring | — |
| guests | people in view (N) | per-guest plating | — |
| time card | container CPU quota | budget per period, spent by all its burners | belongs to a container, not one cook |
| inspector | profiler / probe | watching takes kitchen time | — |

## Scenes

| # | Claim | Beat | Figure | Note | Numbers |
|---|---|---|---|---|---|
| 1 | Three timing classes share one kitchen | setup | scene player, 4 steps, 200 ms timeline | A0, A4 | wbc 50 Hz / 20 ms, perception 10 Hz (ill.) |
| 2 | Per-guest CPU work outgrows GPU work | therefore | predict + live figure (N slider) | A2 | explorer 03 "CPU-heavy" case (ill.) |
| 3 | throttled_usec is a sum over run-queues, not demand | but | predict + scene player, 4 steps | B0 | 2 cores, 100 ms, 4 threads (ill.) |
| 4 | Zero misses in a short window proves little | but | predict + live figure (T, k sliders) | B3 | Garwood 95 % (public) |
| 5 | The observer changes what it measures | therefore | scene player, 4 steps | B4, C4 | 7 of 10 (ill.) |
| 6 | Six artefacts that give clean wrong numbers | catalogue | flip cards | C7 | — |
| 7 | The method exists to block those lies | therefore | scene player, 8 steps | C0–C6 | — |

Palette: coral = CPU · sun = GPU · sky = memory/perception · leaf = deadline · plum = large model · stone = observer.
