# Storyboard — "Measuring a robot's brain without fooling yourself"

Rung 4 (video) of the **robot-workload-benchmarking** public learning kit. One 3–5 minute explainer.
Built from the rung-1 notes (A0, B0, B2, C1–C7), the rung-2 diagrams (`diagrams/INDEX.md`), and the
rung-3 explorer params (`explorers/params.json`). Every number shown comes from this kit's
`constants.json` / `params.json` and is labelled **illustrative** on screen where its class is
`illustrative`; public values carry their source tag. No measured robot or campaign number appears.

**Public-safety:** generic subjects only ("a home robot", "the harness machine", "the control loop").
No codename, company, person, host, path, URL, commit, issue, or campaign number.

## Visual grammar
- Dark background `#0d1117`. One accent colour per concept, held across scenes:
  - sense/camera = teal `#2dd4bf`, perception = sky `#38bdf8`, control/hard-real-time = red `#f87171`,
    voice/audio = violet `#a78bfa`, mapping = amber `#fbbf24`, GPU = green `#4ade80`,
    CPU = blue `#60a5fa`, bench/harness = orange `#fb923c`, caveat/lie = rose `#fb7185`.
- Build incrementally; transform objects rather than cut. ≤12 words on screen at once.
- Every scene that shows a number carries a small source tag bottom-right
  (`illustrative · constants.json` or the public cite).
- Narration ≈ 140 wpm. Target total ≈ 4 min.

## Accent-colour legend (one per concept)
| concept | colour |
|---|---|
| camera / sense | teal |
| people perception | sky |
| control loop (hard real-time) | red |
| voice | violet |
| mapping | amber |
| GPU | green |
| CPU | blue |
| bench / harness | orange |
| how it lies / caveat | rose |

---

## Scene 01 — The crowded computer  (~26 s)
**On screen:** title fades to five stacked pipeline lanes on one "computer" slab. Lanes label and
light up one at a time: *camera depth 30 Hz* (teal), *people perception 10 Hz* (sky),
*mapping* (amber), *voice* (violet), *control 50 Hz · 20 ms, isolated cores* (red). A CPU chip and a
GPU chip sit under all lanes, shared.
**Numbers:** 30 Hz, 10 Hz, 50 Hz / 20 ms — all illustrative (constants.json).
**Narration:** "A home robot is not one program. It is a crowd of services on one small computer,
all at once. A camera makes depth at thirty hertz. People perception runs near ten. Mapping, voice,
and a control loop at fifty hertz on isolated cores. They share one C P U and one G P U."
**Source tag:** `rates illustrative · constants.json`

## Scene 02 — The question  (~20 s)
**On screen:** the five lanes shrink to the left; a large question appears right:
"Does it all fit?" then transforms into "What runs out first?". A resource bar trio (CPU, GPU,
memory) appears, none yet filled.
**Numbers:** none.
**Narration:** "The benchmark answers two questions for this stack on this computer. Does it all
fit at once? And when something gives, what runs out first — the C P U, the G P U, or memory?
A single average utilisation number cannot tell you whether the robot still walks while it thinks."
**Source tag:** none (method, note A0).

## Scene 03 — Predict first: the budget ledger  (~32 s)
**On screen:** the ledger equation builds term by term, as `Text` (no LaTeX):
`t = FLOP / R  +  bytes / B  +  CPU`. Each term highlights as named. Then a small van animation:
a van (the model) stops at a row of traffic lights (kernel launches) — moving little between lights.
Label: "small models are launch-bound".
**Numbers:** none (formula only; C1).
**Narration:** "Predict before you measure. Write a budget ledger: time equals arithmetic over the
compute rate, plus bytes over the bandwidth, plus C P U overhead. A prediction made before the data
cannot be tuned to fit it. And it warns you: a small batch-one model does little math per launch.
Like a van stuck at every traffic light, it spends its time between kernels, not computing. It is
launch-bound — far slower than its roofline."
**Source tag:** `ledger: note C1`

## Scene 04 — Measure each service alone, at three levels  (~34 s)
**On screen:** three nested rounded boxes grow outward: **L1 engine** (green) inside **L2 deployed
service** (blue) inside **L3 with upstream** (sky). Two gap brackets animate in:
`L2 − L1 = service glue`, `L3 − L2 = real-input cost`. A side panel contrasts a flat near-zero bar
"idle floor" vs a taller bar "driven working cost".
**Numbers:** none (method; C2).
**Narration:** "Measure each service alone first, at three levels. L one is the bare engine. L two is
the service as deployed, with its real glue. L three adds the real upstream feeding it. The gaps are
the finding: L two minus L one is the service's own C P U glue, and that glue usually costs more than
the network. And an event-driven service with no input shows an idle floor — near zero — not its
working cost. You must drive it."
**Source tag:** `levels: note C2`

## Scene 05 — The bench: a second machine  (~30 s)
**On screen:** two machines side by side. Left (blue) = **robot**: real stack + isolated control loop.
Right (orange) = **harness machine**: fake motor boards, fake mic board, cloud stubs, synthetic
people. A dedicated red control link and a separate bulk-feed link connect them. Tag: "harness on a
SECOND machine — so it does not steal the robot's compute".
**Numbers:** none (C3).
**Narration:** "Now the bench. Everything that stands in for the world — fake motor boards, a fake
microphone, cloud stubs, synthetic people — runs on a second machine. If the harness ran on the robot,
it would steal the very cycles you are trying to measure. A dedicated link carries the control bus; a
separate link carries the bulk feeds."
**Source tag:** `harness: note C3`

## Scene 06 — How the bench can lie  (~36 s)
**On screen:** four rose-tinted cards flip in one at a time, each with a tiny icon:
(1) "Shared link slows the control bus" — two links merging, red bus dropping to 434 Hz vs 500 Hz
target; (2) "Interrupts pile on core 0"; (3) "Tracing perturbs — adds ~15 ms"; (4) "All-zero
benchmark data overstates speed". Each card gets a check-rule line beneath it.
**Numbers:** 434 Hz vs 500 Hz target (illustrative, C7); ~15 ms (illustrative, constants.json
nsys_perturbation_illustrative).
**Narration:** "The bench can lie in confident ways. A shared link lets bulk traffic slow the control
bus below its rate. Device interrupts all land on core zero and disturb the loop. Turning on tracing
can add milliseconds to the very latency it measures. And a benchmark fed all-zero data runs faster
than real data, because the datapath never toggles. A clean number can still be wrong."
**Source tag:** `434/500 Hz & 15 ms illustrative · constants.json / C7`

## Scene 07 — Windows, gates, pre-registration  (~30 s)
**On screen:** a timeline: `warm-up 120 s` → `window 300 s`. Below, five gate chips light green one
by one: alive · expected rates · crash scan · census · clocks. An ABBA interleave strip and a
"pre-register: hypotheses + thresholds frozen" lock icon appear. Tag: "no tuning after data".
**Numbers:** 120 s warm-up, 300 s window (illustrative, constants.json).
**Narration:** "To stop yourself tuning a result, freeze the rules first. Warm up, then measure a
fixed window. Before its numbers count, gates check the window: services alive, rates as expected,
no crash, no stray C P U, clocks locked at both ends. Conditions run interleaved, so slow drift
cancels. Hypotheses and thresholds are pre-registered — so a result cannot be tuned into passing."
**Source tag:** `120 s / 300 s illustrative · constants.json`

## Scene 08 — Combine and attribute the first limit  (~32 s)
**On screen:** the solo bars sum, then a taller "combined" bar appears; a bracket labels
`interference factor = combined / solo`. Three verdict bands PASS / UNRESOLVED / FAIL. A classifier
points to the winner: CPU quota bar fills to the top before the GPU bar. Tag:
"often C P U quota before G P U".
**Numbers:** interference factor definition (constants.json, no fixed value).
**Narration:** "Finally, run the whole stack together. The combined cost beats the sum of the solos,
because the services fight over C P U, G P U, and memory. That ratio is the interference factor. Each
timing promise is judged pass, unresolved, or fail, and a pre-set rule names the first resource to
give. On a small robot computer, it is often the C P U quota that fills before the G P U."
**Source tag:** `interference factor: note C6`

## Scene 09 — Sources card  (~10 s, static)
**On screen:** "Sources" title and a list: this kit's `constants.json` / `params.json` (illustrative
+ public values); notes A0, B0, B2, C1–C7; public docs — Linux cgroups/CFS, ROS 2, SNTP (RFC 4330),
NVIDIA Nsight. "No measured robot or campaign number appears." plus the four-rung ladder note.
**Narration:** none (silent card, held ~8 s).
**Source tag:** full list is the card.

---

## Timing plan
| scene | target s |
|---|---|
| 01 | 26 |
| 02 | 20 |
| 03 | 32 |
| 04 | 34 |
| 05 | 30 |
| 06 | 36 |
| 07 | 30 |
| 08 | 32 |
| 09 (sources) | 10 |
| title card | 2 |
| **total** | **≈ 282 s (4m42s)** |

Each animated scene holds to its measured narration clip length + ~0.6 s (Manim
`self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))`). Title + sources cards get silent tracks.
