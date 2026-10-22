# C7 — How the bench can lie

**Source:** general measurement method, abstracted; no internal material reproduced. Metric traps in [[B0-cpu-metrics]], [[B1-gpu-power-memory-metrics]], [[B2-rates-periods-and-latency]], [[B4-profilers-and-the-observer-effect]]. · **Status:** concept primer; all examples are generic, numbers illustrative.

## In one sentence
A robot benchmark can produce a confident, wrong answer in many ways — the apparatus steals compute, the fakes are not faithful, the observer is biased, a benchmark operand is degenerate, or a metric is misread — and this note is the catalogue of those bench artefacts, how each was detected, and the rule that catches it, because knowing them is the main defence against a plausible-looking fiction.

## What it is
A **bench artefact** is a result caused by the measurement apparatus rather than the robot. Each entry below is a real class of artefact, the mechanism, how it shows up, and the rule that catches it. They cluster into: the harness stealing or disturbing timing, unfaithful fakes, biased observers, degenerate benchmark inputs, and misread metrics.

## How it works (the catalogue)

**1. A shared harness link slows a fast bus.** When the motor board's link and bulk data (camera frames, a replayed bag) share one physical cable or one receive path, the bulk traffic delays the motor messages, so the fast bus runs below its rate. *Shows up as:* a motor bus running below its target rate (an illustrative example: 434 Hz against a 500 Hz target), only when bulk traffic flows. *Caught by:* isolating the control-bus link onto its own physical path; treating motor-bus timing as a KPI only in windows with no bulk traffic on the shared link.

**2. All device interrupts land on one core.** By default a system routes many device interrupts to CPU core 0. A high-rate input's interrupt load on core 0 then delays a time-critical loop whose work also touches core 0. *Shows up as:* the fast bus slipping even after the link is separated. *Caught by:* moving the interrupt to a free core — but note this can itself bias an observer on that core (see entry 4), so the move is tested, not assumed.

**3. NIC interrupt coalescing adds latency.** A network card may hold received frames for a short interval (coalescing) before interrupting, to reduce interrupt load. That hold adds latency to every cross-machine measurement. *Shows up as:* a cross-machine clock-offset bound larger than the smallest latency being measured. *Caught by:* measuring the offset bound and, when it is too large, falling back to clock-free latency (see [[B2-rates-periods-and-latency]]).

**4. A probe that starts late reads rates low.** If the probe begins a few seconds after the window opens, it misses early messages and reports a rate below the truth. A starved probe likewise reads arrivals late and inflates latency. *Shows up as:* a rate a few percent low, or a latency biased high, with no other cause. *Caught by:* readying every probe before t0, pinning observers to a quiet core, and calibrating the probe's own delay — gating the window on that delay (see [[C4-windows-gates-and-validity]]).

**5. Zero-valued benchmark operands overstate speed and understate power.** A compute benchmark that multiplies all-zero matrices keeps the datapath and the memory bus from toggling, so it draws less power and, under a power or current limit, can run *faster* than real data. *Shows up as:* a GEMM rate higher with zeros than with random data, at lower power. *Caught by:* using random operands, long samples, many repeats, and recording the kernel names and power; reporting the real-data rate and labelling the zero-operand figure separately (see [[C1-predict-then-measure]]).

**6. Harness cost on the measured machine.** If any harness component runs on the robot computer, its CPU is charged to the stack and inflates the result. *Shows up as:* a CPU total higher than the sum of the real services. *Caught by:* running the harness on a second machine and measuring its cost there (see [[C3-the-harness-and-fakes]]).

**7. Editing a running script.** A shell reads a script as it executes, so editing the script of a window that is in progress can make the running copy hit a syntax error partway through and lose that window's data. *Shows up as:* one window's outputs missing, with a mid-run error. *Caught by:* running each window from an immutable snapshot of the scripts; never deploying to the machine during a window.

**8. A fake board with the wrong packet size.** A fake microphone or motor board that uses the wrong framing (frames per packet, packets per message) produces the wrong message rate, which biases every consumer's per-message cost even though the sample rate is right. *Shows up as:* an audio-topic rate that does not match the real device (an illustrative example: 83 Hz where the real device would give about 55 Hz). *Caught by:* matching the real device's framing exactly and A/B-testing the framing to size the bias (see [[A5-audio-and-voice]] and [[C3-the-harness-and-fakes]]).

**9. A stub that is not schema-faithful produces a false "working".** A cloud stub that does not match the real API's response shape or boot probe can let a service *appear* to start and run its path when it is actually taking a degraded fallback — a false positive. *Shows up as:* a service reporting success while an unexpected-endpoint counter is non-zero. *Caught by:* making the stub match the real response schema and status codes, and voiding the window on any unexpected or un-stubbed call (see [[C3-the-harness-and-fakes]]).

**10. A software rate cap hides a compute limit.** A service that holds a minimum interval between outputs publishes at a fixed rate regardless of spare compute, so its rate cannot show a compute limit. *Shows up as:* a flat output rate that does not move with load. *Caught by:* reading the limit from CPU and latency, not the capped rate, and labelling the rate as throttled (see [[B2-rates-periods-and-latency]]).

**11. Quota caps as deliberate deployment choices.** A container's CPU quota is set on purpose to stop one service draining the pool. Removing it to "see the real cost" measures a different deployment, not the robot. *Shows up as:* a tempting uncapped number that is faster but not representative. *Caught by:* keeping the deployed quota as the baseline and reporting the uncapped run only as a separate, labelled call-out (see [[A7-middleware-containers-and-platform]] and [[B0-cpu-metrics]]).

## How it is measured or used in a benchmark
- **Keep this catalogue as a checklist.** Before trusting a surprising result, ask which of these it could be.
- **Each artefact has a rule; the rules live in the gates and the harness design.** Faithful fakes (3, 8, 9), the second machine (6), snapshots (7), probe readiness and pinning (4), clock-free latency (3), locked clocks and random operands (5), quota-as-baseline (11).
- **When an artefact is found mid-campaign, record it as an addendum and supersede the affected windows.** Never silently fix (see [[C5-experimental-design]]).

## Common confusions
- **"A clean-looking number is a correct number."** Several of these artefacts produce clean, confident, wrong numbers.
- **"The uncapped run is the real cost."** The capped run is the deployment; the uncapped run is a call-out.
- **"Zeros are a harmless benchmark input."** Degenerate operands overstate speed and understate power.
- **"The harness is outside the measurement."** Only if it is on a second machine; on the robot it is counted as load.
- **"A service that started is a service that is working."** An unfaithful stub can fake a working path.

## Why it matters for robotics workloads
Every other note in Part C is, in the end, a defence against this one. The budget (C1), the solo levels (C2), the faithful harness (C3), the validity gates (C4), the pre-registration (C5), and the attribution bands (C6) each exist because the bench can lie in a specific way. A benchmarker who knows this catalogue reads a surprising result first as a possible artefact, finds the mechanism, and only then — once the apparatus is cleared — reads it as a finding about the robot. That habit is the difference between a trustworthy result and a plausible fiction.

## Terms introduced
- **bench artefact** — a result caused by the measurement apparatus rather than the system under test.
- **shared-link bus slip** — a fast control bus slowed by bulk traffic on a shared link.
- **interrupt placement** — which CPU core a device's interrupts land on; the default (core 0) can disturb a time-critical loop.
- **interrupt coalescing** — a NIC holding frames before interrupting, adding latency to cross-machine measurements.
- **late/starved probe** — an observer that starts late (rates low) or is CPU-starved (latency high).
- **degenerate operand** — a benchmark input (all zeros) that overstates compute speed and understates power.
- **script-edit-in-flight** — corrupting a running window by editing its script; avoided by immutable snapshots.
- **framing mismatch** — a fake board's wrong packet framing, biasing per-message cost.
- **false 'working'** — a service appearing to run while on a degraded fallback, caused by an unfaithful stub.
- **throttled rate / quota cap** — a software rate ceiling / a deliberate CPU quota; neither is a compute limit, and the quota is the baseline.
