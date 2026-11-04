# C5 — From service to tool: what changes when the pipeline becomes a stand-alone analyzer

**Source:** generalised from internal design documents of a device-health programme, including its user survey and tool design (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer. All times and counts are illustrative.

## In one sentence
A background service that files tickets serves one workflow; engineers also want to point the same parsing and detection at any log they hold, see the intermediate steps, and search for their own event patterns — so the stand-alone tool keeps the models and rebuilds everything around them for interaction, transparency, and access control.

## What it is
A **stand-alone health analyzer** is an interactive tool that takes one device ID (or an uploaded log file), fetches and parses the logs, runs the same detectors as the fleet service, and presents the results as linked views. It is a back end of the fleet service and also a client of it.

## How it works
**Why the service was not enough.** Pilot users asked for two things (generalised):

1. **Use it without a metric trigger.** Not every fault shows in metrics. Lab devices are not in the monitored population. Developers want to check that a new feature "looks normal". Support engineers already hold a log and want help reading it. Triage engineers receive many user-reported tickets with no diagnosis.
2. **Make the output interactive and explainable.** A static report did not show how the anomaly was found.

**The manual workflow it replaces.** Download compressed logs for the device (an illustrative 15 minutes or more), unzip them into many folders, open each file in a text editor, search for words like "error", "fail", and "disconnect", then go back and forth to the source code to check that the sequence of events is the expected one. An illustrative 90 minutes or more per case.

**The tool's views.** One input; four linked views:

1. **Log output** — device summary (type, software version); every template that occurred, as a time-series scatter (one dot per occurrence, hover for the line); detected anomalous windows overlaid, with the templates that drove each one and a "false alarm" feedback link; and a plot of any chosen template parameter over time (for example, HTTP-test latency).
2. **Log search** — the raw lines with filters by time, component, process ID, thread ID, severity, and a regular expression.
3. **State machine** — pick a pre-defined pattern or define an ordered list of expected events and a time span; the tool lists every match, each expandable to its raw lines with the matched events highlighted ([[B5-from-anomaly-to-root-cause]]).
4. **Metrics** — the device's metric series, its software-version timeline (to see whether a change started with an update), and a comparison of this device with the rest of its family.

**Local parsing.** For an uploaded file, the tool runs the same parse tree and templates locally on the file ([[B1-log-parsing-to-templates]]). Detection is limited to the components that have templates; search and state-machine views work on every component.

**Design tenets** (generalised):

- **used daily, not shelf-ware** — design with users throughout;
- **modular** — new views, components, and teams can be added;
- **evolvable** — templates and models are retrained as code changes ([[C2-template-engineering]]);
- **transparent, not a black box** — show the intermediate layers (templates, counts, contributing events, raw lines), so each engineer chooses how much automation to trust.

**One back end, two interfaces.** A user interface for engineers and an API for other tools (for example, a bot that enriches newly filed tickets) share the same back end ([[B6-clustering-and-reporting]]).

**Privacy and access.** A device ID is personal data. The design rules were:

- the device ID is an *input* from the user, never an output of the tool, so the tool reveals no new identities;
- results are visible only to the user who asked;
- the tool analyses only logs already uploaded, and only for users who already have access to those logs through the existing log service; access requires membership of both the tool's access group and the log service's group;
- logs stay in the cloud, so no copy lands on a laptop — less exposure than the manual workflow.

**A deliberately small first version.** One device per request, one OS family, the main log buffer only, and templates for two Wi-Fi components. The roadmap adds many devices per request, more OS families, more buffers, streaming, and a programming interface.

**What the survey changed.** A survey of the service's users (an illustrative 10 respondents) found that the output was hard to understand and too dense (generalised):

| Finding | Response in the tool |
|---|---|
| most users could not read the probability-mass plots | replaced with time-series scatter plots with hover detail |
| users used the anomaly score but did not know what it meant | show the contributing templates and raw lines next to the score; add false-alarm feedback |
| too many columns | split into four focused views |
| filters were hard to use | structured filters by component, process, thread, severity, expression |
| feature codes were cryptic | map each feature ID to a readable description |
| false alarms from metrics | confirm metric anomalies with log evidence ([[C4-lessons]]) |

## How it is measured or used
Three success metrics, collected inside the tool:

- **weekly requests** — logged per request, sliceable by team and device type (engagement);
- **self-reported time saving** — "how much time did this save you, in %?" in the output panel (the north-star metric, since the goal is faster troubleshooting);
- **weekly utility** — "did this help narrow down the root cause?" yes/no.

Users of the first version reported analysis falling from an illustrative 90 minutes to an illustrative 15 minutes per case.

## Common confusions
- **"The tool is a new model."** The models are the same as in the service. The change is input, presentation, and access.
- **"Full automation is the goal."** Transparency is the goal; experienced engineers drive manually with better tools, new engineers lean on the golden sequence and the anomaly overlay.
- **"An interactive tool is a privacy risk."** Designed as above, it reduces exposure compared with downloading logs by hand.

## Why it matters for fleet operations
Adoption decides value. A correct pipeline that only files tickets reaches one team; the same pipeline as a daily tool, with the evidence on screen, becomes how engineers read logs at all — and every "false alarm" click improves the next model.

## Terms introduced
- **stand-alone health analyzer** — an interactive tool that runs the fleet pipeline's parsing and detection on one device or one uploaded log.
- **linked views** — separate displays (output, search, state machine, metrics) of the same log and time range.
- **parameter plot** — a time series of one template parameter across all its occurrences.
- **false-alarm feedback** — a user action that marks a flagged window as not a fault; future training data.
- **transparent design** — showing intermediate pipeline results so users can verify and choose the level of automation.
- **north-star metric** — the single measure that best states the product's goal (here, time saved).
