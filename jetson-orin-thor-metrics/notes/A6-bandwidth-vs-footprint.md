# A.6 Bandwidth vs footprint

**Source:** book.pdf §A.6 — `doc-a-capabilities/bandwidth-vs-footprint.tex`; tables A.6.1 (parameters), A.6.2 (predicted vs measured plateaus and cliffs)  ·  **Status in source:** D (drafted, awaiting review)

## In one sentence
Streaming read bandwidth is 2200 GB/s when the working set fits L2 and 177 GB/s when it does not on Orin (12.4×), and 3790 vs 259 GB/s on Thor (14.6×), with the cliff exactly at each board's L2 capacity (4 MB / 32 MB) — so a working set of a few to a few tens of megabytes runs an order of magnitude faster on the board whose L2 holds it, at identical advertised TOPS.

## What it measures
Sustained streaming bandwidth against working-set footprint, resolving the two bandwidth plateaus of the unified memory — the L2-resident rate B_L2 and the DRAM rate B_DRAM — and the capacity cliff between them. Three downstream quantities result: B_L2, B_DRAM, and their ratio. The ratio is the sharpest single expression of why capacity matters more than a rate figure. Unlike the per-SM L1 roof of §A.5, L2 and DRAM are shared across all SMs, so this is a device-wide sweep (§A.6 "Objective and metric").

## How
A streaming kernel reads, copies, or runs a triad (the STREAM pattern a_i = b_i + q·c_i: two reads and a write) over a buffer swept from 1 MB to 256 MB at four points per octave, with at least 8 GB of traffic per point. Bandwidth is effective bytes over wall time: 1 byte per element for read, 2 for copy, 3 for triad. The L2 plateau is the maximum on the flat run below the cliff; the DRAM plateau is the rate at ≥ 128 MB. Minimum wall time over 5 trials (§A.6 Table A.6.1).

## Predicted
The DRAM plateau should approach the datasheet (204.8 GB/s Orin, 273 GB/s Thor). The read cliff should fall at each board's L2 capacity (4 / 32 MB) and the copy cliff near half of it, because a copy holds two buffers.

The L2-resident bandwidth is not a datasheet quantity. A streaming read has no reuse, so every access misses L1 and is served from L2 at the SM's load-datapath width, 128 B/cycle/SM, summed over SMs at the clock (Eq. A.6.1): B_L2,est = 128 × n_SM × f = 2662 GB/s (Orin) / 4032 GB/s (Thor). This assumes the L2→SM return path is as wide as the L1 read datapath. A narrower 32–64 B/cycle/SM return, often quoted for other NVIDIA parts, would predict 666–1331 GB/s on Orin; the measurement discriminates between the two widths. The predicted L2:DRAM ratio is 13.0× (Orin) / 14.8× (Thor) (§A.6 "Prediction model").

## Measured
| Quantity | Predicted (Orin / Thor) | Orin | Thor |
|---|---|---|---|
| L2-resident read B_L2 (GB/s) | 2662 / 4032 (estimate) | 2200 | 3790 |
| DRAM read B_DRAM (GB/s) | 204.8 / 273 (datasheet) | 177 | 259 |
| L2:DRAM read ratio | 13.0 / 14.8× | 12.4× | 14.6× |
| Read cliff (MB) | 4 / 32 (= L2) | 4.0–4.8 | 32–38 |
| Copy cliff (MB) | 2 / 16 (= ½ L2) | ≈ 2 | ≈ 19–23 |

(§A.6 Table A.6.2.)

## The gap, and what it means
The read cliff falls at each board's L2 capacity and the copy cliff at about half of it, as predicted. The DRAM read plateau reaches 95% of spec on Thor and 86% on Orin; Orin's shortfall is a read-path effect, since its copy and triad recover to 88–95% of spec. The L2-resident plateau reaches 83% (Orin) and 94% (Thor) of the datapath estimate and far exceeds the 666–1331 GB/s a narrower return path would give, so L2-resident streaming is bound by SM consumption at the full 128 B/cycle/SM datapath, not by the L2 array or a narrow return.

The load-bearing result is the L2:DRAM ratio: 12.4× on Orin, 14.6× on Thor, within a few percent of the estimate. A working set of a few megabytes to a few tens of megabytes runs at 12–15× the bandwidth on the board whose L2 contains it, and at the DRAM rate on the board whose L2 does not. The two boards can differ by a factor of order ten in delivered memory bandwidth for the same workload while quoting the same TOPS (§A.6 "Comparison and discussion").

## So what
The source states it: this ratio and these two roofs are the memory ceilings the roofline is built on. Interpretation (mine): the first question to ask of a robotics kernel on these boards is not its FLOP count but whether its working set is under 4 MB, between 4 and 32 MB, or over 32 MB — the answer picks which of three bandwidth regimes it lives in.

## Terms introduced
- **working set / footprint** — the bytes a kernel touches per pass; swept here from 1 MB to 256 MB.
- **L2-resident bandwidth (B_L2)** — the streaming read plateau when the footprint fits L2.
- **DRAM bandwidth (B_DRAM)** — the streaming read plateau when the footprint far exceeds L2.
- **L2:DRAM ratio** — B_L2 / B_DRAM; 12.4× on Orin, 14.6× on Thor.
- **capacity cliff** — the footprint at which bandwidth collapses from one plateau to the next; at L2 capacity for reads.
- **triad** — the STREAM benchmark pattern a_i = b_i + q·c_i (two reads, one write).
- **STREAM** — the standard memory-bandwidth benchmark family (copy, scale, add, triad).
