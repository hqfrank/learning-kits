# Storyboard — The single-lane bridge: why a robot's control loop starves on a shared GPU

Rung 4 (learn-video) of the `jetson-orin-thor-metrics` kit. One video, target 3–5 minutes.
Every number is loaded from `../../explorers/params.json`; the key is cited in each scene's
source column. Nothing is retyped from prose. Measured values are coloured; datasheet values are
dashed grey. Accent colours are consistent across scenes:

- **CONTROL / WBC** — teal `#2DD4BF`
- **PERCEPTION / memory** — amber `#F59E0B`
- **VLA / compute aggressor** — magenta `#E879A9`
- **datasheet / ceiling (not reached)** — grey `#9CA3AF` (dashed)
- **deadline / floor / danger** — red `#EF4444`
- background: near-black `#0B0F14`

Narration budget ≈ 130–150 words/min. Seven scenes + a 1 s title card and a sources card.
Target total ≈ 4 min of narration. Each scene's animation is timed to its measured clip length
(ffprobe) + ≥ 0.5 s; audio is never stretched.

---

## Title card (1 s, no narration)
On screen: "The single-lane bridge" / subtitle "why a robot's control loop starves on a shared GPU"
/ small tag "Jetson Thor T5000 (sm_110) — measured". Teal + magenta accents on black.

---

## Scene 01 — Three jobs, one GPU (~30 s)
**On screen:** a single Jetson Thor SoC block. Three job boxes drop onto it one at a time:
CONTROL (teal, "100 Hz, 10 ms deadline"), PERCEPTION (amber), VLA (magenta, "π0.5, 5 Hz").
All three funnel through one arrow into one GPU → one memory controller → one LPDDR pool.
A thin teal "control loop" pulse ticks steadily at the start, then stutters as the other two land.

**Narration (≈72 words):**
"A modern robot runs three jobs on one Jetson Thor. A control loop — whole-body control — must
close at a hundred hertz, a ten-millisecond deadline, every tick. Perception runs the cameras.
And a vision-language-action model, π-zero-point-five, plans at about five hertz. One GPU. One
memory controller. One pool of memory. They do not get a lane each. They share a single-lane
bridge."

**Numbers / source:**
- 100 Hz, 10 ms deadline — `wbc_deadline` (10 ms)
- π0.5 ≈ 5 Hz — `mps_cap_vla_rate_retained.pi05_cap25` note ("pi0.5 5 -> 3.6 Hz" → solo 5 Hz)

---

## Scene 02 — The datasheet says there's room (~40 s)
**On screen:** two horizontal ceiling bars per precision. Grey dashed = datasheet; coloured =
measured `tcgen05`/NVFP4. Build top-down: NVFP4 dense datasheet 1035 (grey) → measured 627.8
(magenta), "60.7%". FP8/INT8 datasheet 517 (grey) → measured 324.5–345.4 (magenta), "~63–67%".
Then a tiny teal dot labelled "control loop" sits near the floor of the chart — it needs almost
none of this. Caption: "TOPS is not the constraint."

**Narration (≈86 words):**
"The datasheet promises enormous headroom. NVFP4 — the four-bit tensor format — advertises one
thousand thirty-five dense teraflops. In practice a tuned library reaches six hundred
twenty-seven point eight, about sixty-one percent of the sticker. INT8 and FP8 advertise five
hundred seventeen; measured, about two-thirds. Still: hundreds of teraflops. The control loop
needs a rounding error of that. By the datasheet, there is plenty of room. Hold that thought —
because room on paper is not room in practice."

**Numbers / source:**
- NVFP4 datasheet 1035, measured 627.8, 60.7% — `nvfp4_dense_ceiling.thor` (627.8; source string gives 1035 / 60.7%)
- INT8/FP8 datasheet 517 — A.3 (carried in `tensor_tcgen05_fp16` source neighbourhood; 517 cited in diagrams INDEX / A.3 note)
- tcgen05 FP16 measured 192.5 — `tensor_tcgen05_fp16.thor`

---

## Scene 03 — The cliff: SM co-scheduling lockout (~50 s)
**On screen:** an x-axis "GPU co-tenant occupancy (% warp slots)" 0→30%, y-axis "victim's first
completion". A flat teal line near zero (victim runs) that SNAPS up to a magenta plateau labelled
"= co-tenant lifetime" at x = 14% (Thor). A grey dashed companion snap at x = 8% (Orin). Big word
appears: "BISTABLE — no fair share." A faint grey line shows what *proportional* sharing would
look like (gentle slope) and is crossed out.

**Narration (≈103 words):**
"Here is the first reason. When two kernels share one GPU context, you might expect fair sharing:
a co-tenant on fourteen percent of the warp slots leaves you eighty-six percent. That is not what
the hardware does. Below a threshold the victim runs. Above it — just fourteen percent of the warp
slots on Thor, eight percent on Orin — the victim completes nothing until the co-tenant drains. It
snaps to the co-tenant's whole lifetime. It is bistable: two states, co-running or locked out, no
graded middle. A job on an eighth of the slots can lock you out while the rest of the GPU sits
idle. Scheduling is not fair."

**Numbers / source:**
- lockout onset Thor ≈ 14%, Orin ≈ 8% — `lockout_onset_occupancy.thor` / `.orin`
- bistable, snaps to co-tenant lifetime — B.4 note (mechanism)

---

## Scene 04 — The real rehearsal: 41.6 µs → 5.9 ms (~45 s)
**On screen:** a 10 ms budget bar (red deadline line at the top). WBC solo p99 drawn as a sliver
near zero, labelled "41.6 µs (solo)". Then co-tenants are added cumulatively (perception, VLA,
+ CPU hog); the bar grows in steps and lands at 5.9 ms — a tall teal bar under, but close to, the
red 10 ms line. Big callout: "141× — most of the budget gone." A "predicted vs measured" style
arrow animates 41.6 µs → 5.9 ms.

**Narration (≈90 words):**
"Now the real rehearsal. The whole-body-control policy, measured alone, has a ninety-ninth-
percentile latency of forty-one point six microseconds — a speck. Put it under the full co-tenant
roster plus a CPU memory hog, and that tail inflates to five point nine milliseconds. A
hundred-and-forty-one-fold blow-up. It still fits inside the ten-millisecond budget — but only
just. Almost the entire deadline is now spent waiting, not computing. The solo number understated
the deployed tail by two orders of magnitude."

**Numbers / source:**
- WBC solo p99 41.6 µs (Thor) — `wbc_solo_p99.thor` (0.0416 ms)
- worst mix p99 5.9 ms, 141× — `wbc_worst_mix_p99.thor`
- deadline 10 ms — `wbc_deadline`

---

## Scene 05 — The ladder: what buys the loop back (~55 s)
**On screen:** a rising staircase of four steps against the red 10 ms line.
1. "Shared context" — p99 110.7 ms, 51% ticks dropped (red, far above line).
2. "Separate process" — ~17 ms, 4.9% dropped (amber, still above line) — "recovers ~90%".
3. "Plain MPS" — 61 ms (red) — "doesn't help".
4. "MPS + 25% SM cap" — 7.5 ms, 0% dropped (green, below line) — "THE FIX". Beside it a magenta
cost tag: "VLA 5 → 3.6 Hz".

**Narration (≈104 words):**
"Can scheduling buy the loop back? Climb the ladder. In a shared context the loop is destroyed —
p99 of a hundred-and-ten milliseconds, fifty-one percent of ticks dropped. Give the planner its
own process and you recover most of it: about seventeen milliseconds, under five percent dropped —
roughly ninety percent back, but still over budget. Plain MPS barely moves it. The fix is MPS with
the planner capped to twenty-five percent of the SMs: the control loop returns to zero dropped
ticks, comfortably under ten milliseconds. The bill is paid by the planner — its rate falls from
five hertz to three-point-six."

**Numbers / source:**
- shared context p99 110.7 ms, 51% dropped — `shared_context_wbc_p99` / `shared_context_wbc_penalty`
- separate process ~17 ms, 4.9% dropped — `separate_context_wbc_p99.pi05`
- plain MPS 61 ms — `plain_mps_wbc_p99`
- MPS + 25% cap 7.5 ms, 0% drop — `mps_cap_wbc_p99.pi05_cap25`
- VLA 5 → 3.6 Hz (0.72 retained) — `mps_cap_vla_rate_retained.pi05_cap25`

---

## Scene 06 — The wall: the 172 GB/s floor (~45 s)
**On screen:** all the ladder's green/amber steps redrawn small, then a thick red horizontal line
sweeps in at "~172 GB/s CPU memory load" and every step collapses to red below the 10 ms line
being crossed. Label: "245 GB/s sustained roof" (grey) with "~172 = 70% of it" bracket. Big words:
"Scheduling cannot fix a memory problem."

**Narration (≈92 words):**
"But there is a wall none of it moves. Drive CPU memory traffic up, and at about a hundred
seventy-two gigabytes per second — only seventy percent of Thor's sustained roof of two hundred
forty-five — every discipline collapses. Shared context, separate process, MPS, the SM cap: all of
them. The control loop breaks regardless of precision or scheduling. The bridge has a fixed total
capacity, and once the memory system is full, no scheduler conjures more. Scheduling decides who
pays. It cannot fix a memory problem."

**Numbers / source:**
- 172 GB/s floor, ~70% of 245 — `cpu_memory_load_floor`
- 245 GB/s sustained roof (Thor) — `dram_bandwidth_sustained_M.thor`

---

## Scene 07 — Sources card (~6 s, no narration or short tag)
On screen: "Sources — all numbers from book.pdf (Docs A, B) + L4 KEY-LEARNINGS, via
params.json". List: A.3/A.4 tensor & NVFP4 ceilings · B.4 SM co-scheduling lockout ·
B.8 WBC mix ladder · L4 scheduling ladder & 172 GB/s floor. Small line: "Jetson Thor T5000,
MAXN, clocks locked. A study aid — rough edges expected."

---

## Timing & assembly plan
- Render scene 01 at `-qm` first to validate the toolchain, then the rest at `-qm`.
- Narrate each scene with Kokoro (`tts.py`, voice `af_heart`); measure each clip with `ffprobe`;
  set each Manim scene's run time ≥ clip + 0.5 s.
- Assemble with ffmpeg: 1 s title card → scenes 01–06 muxed with their narration → scene 07
  sources card. Output `out/single-lane-bridge.mp4` + `out/single-lane-bridge.srt` built from the
  narration text and measured clip durations.
- Review: extract 4 frames, read them back for legibility and number-match; report total duration.
