# B2 — Rates, periods, and latency

**Source:** ROS 2 concepts (https://docs.ros.org/), SNTP/NTP (RFC 4330, https://www.rfc-editor.org/rfc/rfc4330). · **Status:** concept primer, illustrative numbers only.

## In one sentence
Rate and latency metrics describe how fast a service produces output and how long a result takes to travel the pipeline — and the traps are mistaking a software-throttled rate for a compute limit, confusing a message's send-time stamp with its arrival time, and letting a busy or clock-skewed observer bias the very latency it measures.

## What it is
For each topic the benchmark reports:

- **topic rate** — messages per second.
- **period percentiles** — the per-message gap at p50, p95, p99 (the median and the tails), not just the mean.
- **gaps above a threshold** — how often the period exceeded a chosen bound (for example, a control-loop period over twice its target).
- **receive time versus header stamp** — when a message arrived versus when its sender stamped it.
- **end-to-end latency** — the time from an input (a camera frame) to the output it caused (a detection).

And across machines:

- **a cross-machine clock offset** with a bound, measured by SNTP probing.
- **clock-free latency** — a latency computed from two arrivals on the same machine, needing no clock correction.

## How it works
**Rate versus period.** The rate is the average; the period percentiles show the shape. A service can hold a steady 10 Hz average while occasionally stalling for 200 ms — the mean hides it, the p99 period and the gap count reveal it.

**Receive time versus header stamp.** A message carries a header stamp set by its sender and arrives at a receive time set by the reader's clock. End-to-end latency measured from the header stamp needs the two clocks to agree; latency measured from receive times needs only one clock. Mixing them silently adds the clock offset to every number.

**Cross-machine clocks and the offset bound.** When the harness is on a second machine (see [[C3-the-harness-and-fakes]]), its clock and the robot's differ and drift. The benchmark probes the offset continuously (SNTP, several times a second) and reports a **bound** on it. Any latency that crosses the two machines is only trustworthy to within that bound, so the bound must be smaller than the smallest latency being measured (an illustrative sub-millisecond bound against millisecond latencies).

**Clock-free latency.** The way to avoid the offset entirely is to measure a latency as the gap between two events that both arrive on the same machine — for example, the same frame's two arrivals at two stages — so no cross-machine clock enters. This is the primary latency when the offset bound is too large to trust.

**The busy-observer bias.** The probe that timestamps arrivals is itself a process. If it is starved of CPU, or pinned to a core that is also handling interrupts, it reads arrivals late, and reports latency that is too high (or, if it starts late, rates that are too low). A busy observer biases the measurement. The probe must be ready before the window starts, pinned to a quiet core, and its own delay must be calibrated (see [[B4-profilers-and-the-observer-effect]] and [[C4-windows-gates-and-validity]]).

**A throttled rate is not a compute KPI.** Many services hold a software minimum interval between outputs (see [[A2-people-perception]]). Their published rate is then a fixed ceiling, independent of spare compute. A rate held by a throttle tells you nothing about the compute limit; you must look at CPU, latency, and the uncapped case instead.

## How it is measured or used in a benchmark
- **Report period percentiles and gap counts, not just the rate.** The tail is where deadlines live.
- **Choose one clock basis per latency and state it.** Prefer clock-free latency; use header-stamp latency only when the offset bound is small enough.
- **Bound and verify the cross-machine offset.** Probe it continuously; void a cross-machine latency when the bound exceeds what is being measured.
- **Calibrate the probe's own delay.** A late or starved observer invalidates the latency; measure its delay and gate on it.
- **Never treat a throttled rate as a compute limit.** Flag throttled rates and read the limit from CPU and latency.

## Common confusions
- **"The mean latency is the latency."** Deadlines are about tails; report p95/p99 and gap counts.
- **"Header-stamp and receive-time latency are interchangeable."** They differ by the clock offset; pick one basis and state it.
- **"The clock offset is negligible."** Across machines it drifts by milliseconds; bound it and compare to what you measure.
- **"A steady 10 Hz means 10 Hz of compute headroom."** If the rate is software-throttled, it is a ceiling, not a compute measurement.
- **"The observer is free."** A starved or late observer biases latency and rate; it must be ready early, pinned, and calibrated.

## Why it matters for robotics workloads
Rates and latencies are how a benchmark decides whether each pipeline keeps its promise (see [[A0-the-big-picture]]). But they are the metrics most easily corrupted by the measurement apparatus itself — by clock skew between two machines, by a busy probe, or by a service's own rate cap. Getting the clock basis, the observer, and the throttle interpretation right is what separates a real timing result from an artefact (the catalogue in [[C7-how-the-bench-can-lie]] is largely about these).

## Terms introduced
- **topic rate** — messages per second on a topic.
- **period percentiles (p50/p95/p99)** — the per-message gap at the median and the tails.
- **gap above threshold** — a count of periods exceeding a chosen bound.
- **receive time vs header stamp** — a message's arrival time (reader's clock) versus its sender's stamp (sender's clock).
- **end-to-end latency** — time from an input to the output it caused.
- **cross-machine clock offset** — the difference between two machines' clocks, bounded by SNTP probing.
- **clock-free latency** — a latency from two same-machine arrivals, needing no clock correction.
- **busy-observer bias** — the error a starved or late probe adds to the latency and rate it measures.
- **software rate cap** — a minimum interval a service enforces, making its rate a ceiling rather than a compute measurement.
