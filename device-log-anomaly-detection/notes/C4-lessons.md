# C4 — Lessons: anomaly is not issue, and what the misses teach

**Source:** generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)); TKIP deprecation in IEEE Std 802.11-2012 and Wi-Fi Alliance guidance (public); He et al., ISSRE 2016 (public benchmarks, for contrast). · **Status:** concept primer; lessons are generalised, counts are illustrative.

## In one sentence
An anomaly detector narrows thousands of lines to a handful of windows, but a flagged window is not a device defect until a second signal and an engineer agree, and nearly every missed fault traces back to a component, log type, or time range the pipeline did not look at.

## What it is
These are the recurring lessons from building and piloting a fleet log-and-metric pipeline. They are design rules, not results.

## How it works
**Lesson 1 — anomaly ≠ issue (the confidence gap).** The detector finds behaviour that differs from normal. Customer environments differ from normal all the time:

- an old router that still uses a deprecated security mode (TKIP, deprecated in IEEE 802.11-2012);
- an access point that drops clients when it runs out of capacity;
- an internet-provider outage, a captive portal, a household with many devices on one access point.

Each of these produces anomalous logs on a healthy device. In an illustrative pilot of 10 tickets, 4 were environmental. **Rule:** confirm with an independent second signal before opening a ticket — a metric anomaly *and* a log anomaly, or a log anomaly *and* similar devices on other access points ([[B6-clustering-and-reporting]]).

**Lesson 2 — fault localisation needs a human.** The detector's value is the size of the reduction: from a day of logs to an illustrative 20 flagged windows out of an illustrative 50 000. Deciding what the windows mean, and what to fix, still needs domain expertise. **Rule:** design the output as a focused report for an engineer, not as an automated verdict ([[C5-from-service-to-tool]]).

**Lesson 3 — the scope is too narrow until proven otherwise.** Lab ground-truth cases ([[C1-the-ground-truth-problem]]) showed one pattern repeatedly: the cause sat outside the monitored components.

| What the case looked like | Where the cause actually was | What the pipeline needed |
|---|---|---|
| repeated Wi-Fi disconnects | the DHCP client rejected packets (bad checksum) | DHCP client logs |
| "cannot register after connecting" | network time sync failed, so secure server access failed | time-sync and TLS components |
| device reboots during a connection | an assertion in the Wi-Fi kernel driver | the kernel log buffer, processed separately from the main buffer |
| reboot, then nothing | the log ended at the crash | a longer collection window |
| failure only after a specific earlier test | stale state from the previous step (stateful, order-dependent) | sequence or transition features, not counts ([[B5-from-anomaly-to-root-cause]]) |

"Connectivity" problems are often not Wi-Fi problems. They live in the layers that depend on Wi-Fi: addressing, time, name resolution, security. **Rule:** for each missed case, name the missing signal and add it; the miss list is the roadmap.

**Lesson 4 — know which logs you have.** Some lab logs were in a test-framework format; some lacked a whole component. **Rule:** scope the analyser explicitly (for example, production main-buffer logs only), say so in the output, and fall back gracefully when a component is absent.

**Lesson 5 — collection limits shape everything.** Central storage covers only devices that are allowed to upload. Production devices upload on demand, after the fault. Buffers overwrite ([[A1-what-a-device-log-is]]). **Rule:** this is the argument for on-device analysis, which reads the lines before they are lost ([[A0-why-fleets-need-log-analysis]]).

**Lesson 6 — rules and models are partners.** Rules give precision and a named cause for known faults. Models find unknown ones. A **hybrid analyser** extracts known signals by rule (ping result and latency, connect and disconnect events, reason codes) and feeds them to the model as extra features next to the count vectors.

**Lesson 7 — "no anomaly" is information.** After each software release, compare the release's fleet behaviour with the previous releases. Consistent behaviour is a green flag; a change is a red flag. This turns a bug finder into a **release-health check**.

**Lesson 8 — a correct output that nobody understands has no value.** In a user survey of the internal tool, users relied on the anomaly score without understanding it, and most could not read the statistical plots (generalised). **Rule:** show the evidence (the lines, the templates, the trend) next to the score, and remove fields that users do not use ([[C5-from-service-to-tool]]).

## How it is measured or used
- Keep a **miss log**: every ground-truth case not caught, with the missing signal and the planned fix.
- Track the **environmental share** of resolved tickets over time; it should fall as second-signal confirmation improves.

## Common confusions
- **"High false alarms mean a bad model."** They often mean a missing second signal or a data artefact ([[C3-data-quality]]).
- **"More components means more noise."** More components with good templates means fewer misses; filter by component per question, not globally.
- **"Automation removes the engineer."** It removes the search, not the judgement.

## Why it matters for fleet operations
These lessons decide whether a pipeline is trusted. A team that opens tickets on environmental anomalies and misses faults in neighbouring components loses its users within months. A team that confirms with two signals, reads the right buffers, and publishes its miss list keeps them.

## Terms introduced
- **confidence gap** — the distance between "anomalous" and "a real device defect".
- **second-signal confirmation** — requiring an independent signal before opening a ticket.
- **scope (of an analyser)** — the components, log buffers, formats, and time ranges it reads.
- **stateful (order-dependent) fault** — a fault that appears only after a specific earlier sequence of events.
- **hybrid analyser** — a model that uses rule-extracted known signals as extra features.
- **release-health check** — comparing a new release's fleet behaviour with earlier releases.
- **miss log** — the list of missed ground-truth cases, each with its missing signal.
