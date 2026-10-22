# C4 — Windows, gates, and validity

**Source:** general measurement method, abstracted; sample-count/statistics in [[B3-deadlines-tails-and-statistics]]. · **Status:** concept primer, illustrative numbers only.

## In one sentence
A measurement is taken over a fixed window after a warm-up, and before its numbers count the benchmark runs a set of validity gates — clocks locked, services alive and at their expected rates, no crashes, no foreign CPU, enough samples — so that a window is either valid, flagged, or thrown out (void), and a known-bad window never pollutes the result.

## What it is
A **window** is the fixed span over which a cell's numbers are collected. Around it sit:

- a **warm-up** — a settling period before the window (an illustrative 120 s) so caches, clocks, and services reach steady state.
- a **fixed window length** — chosen from a sample-count rule (an illustrative 300 s), long enough to collect the samples the statistics need (see [[B3-deadlines-tails-and-statistics]]).
- **validity gates** — automated checks that decide whether the window counts.
- **void versus flagged** — the two ways a window can fail: thrown out entirely, or kept with a warning.

## How it works
**Warm-up then a fixed window.** Nothing is measured until the system settles. The warm-up lets clocks lock, services reach their steady rate, and bursty services reach a representative state. The window is then a fixed length, the same for comparable cells, so that counts and percentiles are comparable.

**Window length from a sample-count rule.** The length is not arbitrary: it is set so the window collects enough samples for the statistics (a stable p99 needs several thousand cycles; a tight Poisson bound on a rare miss needs many minutes — see [[B3-deadlines-tails-and-statistics]]). A window too short to meet the sample count is flagged, not trusted.

**Locked clocks, checked at both ends.** GPU and memory clocks are locked to a fixed regime so the compute and bandwidth metrics are comparable (see [[B1-gpu-power-memory-metrics]]). The lock is verified at the window's start *and* end; a window where a clock drifted is void.

**Observers pinned to a separate core; probes ready before t0.** The samplers and probes run on a dedicated core, off the application cores, so they do not steal from the services (see [[B0-cpu-metrics]] and [[B2-rates-periods-and-latency]]). They must be running and settled *before* the window starts; a probe that starts late reads every rate low (see [[C7-how-the-bench-can-lie]]).

**The validity gates.** Before a window counts, the benchmark checks:

- **alive** — every service is up and every probed topic produced at least one message in each time bin. A rate *drop* is an outcome, not a void; total silence is a void.
- **expected rates** — the inputs arrived at their configured rates (the feed is really at 30 Hz, the fake board at its rate).
- **crash scan** — no service (or child process inside a container) died and respawned during the window.
- **census** — no foreign process used more than a small CPU threshold (an illustrative 0.3 cores), so the machine was quiet (see [[B0-cpu-metrics]]).
- **clocks** — locked at both ends.

**Void versus flagged.** A window that fails a hard gate (clocks drifted, a service crashed, the islands bridged, foreign CPU over threshold) is **void** — thrown out. A window with a soft problem (a sample count a little below the rule) is **flagged** — kept, but reported with the caveat. The benchmark records a **void class** for every discarded window, so the pattern of failures is itself visible.

## How it is measured or used in a benchmark
- **Warm up, then measure a fixed window.** Same length for comparable cells.
- **Set the length from a sample-count rule.** Flag windows below it.
- **Lock clocks and verify at both ends.** Void on drift.
- **Ready the probes before t0; pin observers off the application cores.** Calibrate the probe's own delay (see [[B2-rates-periods-and-latency]]).
- **Run the gates every window.** Alive, expected rates, crash scan, census, clocks.
- **Record a void class for every discarded window.** Make the failure pattern visible.

## Common confusions
- **"A rate that dropped means void the window."** A rate drop is an outcome to report; only silence or a failed gate voids the window.
- **"Check the clocks once."** Verify at both ends; a mid-window drift invalidates the comparison.
- **"Any window length is fine."** The length must meet the sample-count rule for the statistics to hold.
- **"A quiet machine is automatic."** Foreign processes creep in; the census is what proves the machine was quiet.
- **"Discard bad windows silently."** Record the void class, because repeated voids of one kind are a finding about the bench.

## Why it matters for robotics workloads
Validity gates are what let a benchmark trust its own numbers. On a shared machine, over long windows, with a harness on a second clock, there are many ways a window can be quietly wrong — a drifted clock, a dead-and-respawned service, a late probe, a stray process. The gates catch each one before the number is used, and the void-class record turns the failures into evidence. Without them, the benchmark cannot tell a real result from a broken window.

## Terms introduced
- **window** — the fixed span over which a cell's numbers are collected.
- **warm-up** — the settling period before the window.
- **sample-count rule** — the requirement that sets the window length from the number of samples the statistics need.
- **validity gate** — an automated check (alive, expected rates, crash scan, census, clocks) that decides whether a window counts.
- **alive gate** — every service up and every topic producing; a rate drop is an outcome, silence is a void.
- **crash scan** — a check that no service or in-container child died and respawned during the window.
- **census (gate)** — a check that no foreign process exceeded a small CPU threshold.
- **void versus flagged** — a window thrown out entirely versus kept with a caveat.
- **void class** — the recorded reason a window was discarded, so the failure pattern is visible.
