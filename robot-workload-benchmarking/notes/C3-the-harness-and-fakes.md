# C3 — The harness and fakes

**Source:** general measurement method, abstracted; no internal material reproduced. · **Status:** concept primer, illustrative framing only.

## In one sentence
The harness is everything that stands in for the physical world so the robot's software can run on a bench — and the two rules that make it trustworthy are to put the harness on a *second machine* so it does not steal the robot's compute, and to make every fake faithful to the real thing's wire protocol, framing, and timing, because an unfaithful fake biases the result or hides a failure.

## What it is
The **harness** is the test apparatus around the real stack: fake hardware, cloud stubs, synthetic inputs, and recorded data. Its job is to drive the stack into realistic states without the physical robot. Its parts:

- **fake hardware boards** — programs that speak the real motor-board and microphone-board wire protocols.
- **cloud-API stubs** — local servers that imitate cloud services (speech, language) with realistic latency.
- **synthetic inputs** — generated camera frames with a chosen number of people, and detection injection.
- **bag replay** — recorded sensor data played back for mapping and other consumers.
- **network islands** — separated networks so two input sources do not collide.

## How it works
**Put the harness on a second machine.** The harness itself uses CPU — generating frames, serving stubs, timestamping. If it runs on the robot computer, it steals cycles from the services under test and corrupts their numbers. So the harness runs on a **separate machine**, connected to the robot by a link, and only the real stack runs on the robot. The harness's own CPU is then measured on the harness machine, not counted as stack load.

**Fake boards must speak the real wire protocol — and framing matters.** A fake motor board or microphone board must send the same message format, at the same rate, with the same **framing** as the real hardware. For audio, the frames-per-packet and packets-per-message set the message rate, which sets every downstream per-message cost (see [[A5-audio-and-voice]]). A fake that uses the wrong framing — for example, a different number of frames per packet — gives a different message rate and biases every consumer's CPU, even though the sample rate is unchanged. Framing fidelity is not a detail; it is the difference between measuring the robot and measuring a different workload (see [[C7-how-the-bench-can-lie]]).

**Cloud stubs need realistic latency and a faithful schema.** A stub for a cloud speech or language service must return the real API's response shape (its streaming format, its status codes) and imitate its latency. A schema-unfaithful stub can make a service report "working" when it is not actually exercising its real path — a false positive (see [[C7-how-the-bench-can-lie]]). The stub's latency parameters are assumptions and must be labelled as such, because the benchmark cannot measure the real cloud from the bench.

**Synthetic inputs and detection injection.** To test perception at a chosen N people, the harness generates frames containing N moving people, or injects ground-truth detections, so the pipeline does real downstream work at a controlled N (see [[A2-people-perception]]). The injected data is labelled, and the injection's own cost is accounted and subtracted.

**Bag replay drives bursty services.** Recorded sensor data (a bag) replays real motion so bursty services like mapping reach their working state (see [[A3-mapping-localization-navigation]]). Recorded data that holds a person's likeness stays local and is never shared.

**Network islands prevent collisions.** When two input sources would otherwise share a topic name (a live camera and a synthetic feed both publishing camera topics), the harness puts them on separate network islands so they do not interfere. The cut edges between islands are listed, so nothing is silently disconnected.

**Recording cut edges.** Whenever the harness cuts a connection the real robot would have (an island boundary, an unanswered stream), it records the cut. An un-recorded cut is a silent under-load.

## How it is measured or used in a benchmark
- **Run the harness on a second machine.** Measure its CPU there; do not count it as stack load.
- **Make fakes faithful.** Match the wire protocol, framing, and rate exactly; A/B the framing if unsure.
- **Make stubs schema-faithful with labelled latency.** Match the response shape and status codes; label latency as an assumption; fail the window on any unexpected call.
- **Inject synthetic input at a controlled N, and account its cost.** Subtract the injection overhead.
- **Replay bags to drive bursty services.** Keep person-identifying recordings local.
- **Separate colliding inputs into islands and list the cut edges.** No silent disconnections.

## Common confusions
- **"The harness can run on the robot."** It steals CPU from the services under test; put it on a second machine.
- **"Any fake board will do."** The wrong framing or rate changes the message rate and biases every consumer.
- **"A stub just needs to answer."** An unfaithful schema produces a false 'working'; match the real response shape and fail on surprises.
- **"Cut edges are obvious."** An unrecorded cut is a silent under-load; list every one.

## Why it matters for robotics workloads
The harness is where most bench artefacts are born (see [[C7-how-the-bench-can-lie]]): a shared link that slows a fast bus, a fake with the wrong packet size, a stub that fakes success, a synthetic feed colliding with a live one. Every one of these makes the result look fine while being wrong. Running the harness off the robot and making every fake faithful — in protocol, framing, timing, and schema — is what keeps the apparatus from quietly rewriting the workload it is supposed to measure.

## Terms introduced
- **harness** — the test apparatus that stands in for the physical world: fakes, stubs, synthetic inputs, bags, islands.
- **second machine** — the separate computer the harness runs on, so it does not steal the robot's compute.
- **fake hardware board** — a program that speaks a real device's wire protocol, framing, and rate.
- **framing fidelity** — matching the real device's frames-per-packet and packets-per-message, which set the message rate.
- **cloud-API stub** — a local server imitating a cloud service's response shape, status codes, and latency.
- **schema-faithful stub** — a stub matching the real API's response format, so it cannot produce a false 'working'.
- **detection injection / synthetic input** — generated frames or ground-truth detections at a controlled N, with their cost accounted.
- **bag replay** — recorded sensor data played back to drive bursty services.
- **network island** — a separated network keeping two input sources from colliding; its cut edges are listed.
- **cut edge** — a connection the real robot has that the bench severs; recorded, never silent.
