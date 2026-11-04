# Finding faults in a device fleet from logs and metrics: parsing, anomaly detection, root-cause analysis — study notes

**Start here: the story →** [The night-shift mechanic](stories/01-the-night-shift-mechanic.html) — a picture-first, interactive tour of the pipeline in ten minutes ([all stories](stories/INDEX.md)).

## In one paragraph

A maker of connected consumer devices learns about most faults late, from customers who cannot describe them, after the logs that showed the fault have been overwritten. This kit teaches the pipeline that fixes that. **Part A** describes the problem and the data: why rule-based, on-demand tools fall short; what a device log really is (interleaved, semi-structured, in ring buffers that overwrite); and fleet metrics, where the key quantity — the share of devices that emitted a metric — has a variance that depends on how many devices were active. **Part B** describes the methods: parsing lines into templates and parameters, cutting windows and counting templates, isolation forests on count vectors (and small sequence models on the device), weighted least squares for fleet trends with a p-value turned into a score, transition edges and state machines for root cause, and clustering for one ticket per fault. **Part C** describes what makes the result trustworthy: a hand-built ground truth reported with its confidence interval and its false-alarm rate, template engineering across OS families and releases, a data-quality audit, the lessons (anomaly is not issue; the misses name the missing signals), and what changes when the pipeline becomes an interactive tool. The kit carries no internal numbers; every number is public with a citation or labelled illustrative (see [`SOURCES.md`](SOURCES.md)).

This is rung 1 of a four-rung learning kit (notes → diagram → explorer → video). Later rungs planned in the brief: explorers for isolation-forest intuition, the fleet trend test, and log windowing; a picture-first story; and quiz banks.

## How to read these notes

Read Part A → Part B → Part C. Part A gives you the data the methods consume; Part B gives you the methods; Part C tells you when to believe their output.

### Start here
- [`SOURCES.md`](SOURCES.md) — what this kit is, where the method comes from, the public sources, and the number classes.
- [`notes/A0-why-fleets-need-log-analysis.md`](notes/A0-why-fleets-need-log-analysis.md) — the whole pipeline on one page.

### Part A — the problem and the data
- [`notes/A0-why-fleets-need-log-analysis.md`](notes/A0-why-fleets-need-log-analysis.md) — support cost, lost evidence, reactive rule-based tools; the four-stage pipeline; on-device vs fleet-side.
- [`notes/A1-what-a-device-log-is.md`](notes/A1-what-a-device-log-is.md) — line format, severity, components, interleaving, timestamp ties, ring buffers and overwrite, collection constraints.
- [`notes/A2-fleet-metrics.md`](notes/A2-fleet-metrics.md) — event-triggered counters, pivoting to features, device-days, the share of devices and why its variance depends on n, proxy devices.

### Part B — the methods
- [`notes/B1-log-parsing-to-templates.md`](notes/B1-log-parsing-to-templates.md) — templates and parameters, mining (Drain, Spell) vs source-code extraction, one-to-many / many-to-one, the parse-tree matcher.
- [`notes/B2-windows-and-count-vectors.md`](notes/B2-windows-and-count-vectors.md) — fixed, sliding, session windows; log count vectors; window length vs sparsity vs delay; counts vs sequences.
- [`notes/B3-anomaly-detection-on-logs.md`](notes/B3-anomaly-detection-on-logs.md) — isolation forest (score, defaults, contamination); why unsupervised; rules vs classifier; DeepLog-style sequence models on the device.
- [`notes/B4-fleet-trend-detection.md`](notes/B4-fleet-trend-detection.md) — WLS on the share of devices, slope test against a practical threshold, p-value → score, direction filter, multiple testing; family vs device level.
- [`notes/B5-from-anomaly-to-root-cause.md`](notes/B5-from-anomaly-to-root-cause.md) — cascade vs parallel, transition-edge mining per thread, sequence and distribution anomalies, golden sequences, state-machine search.
- [`notes/B6-clustering-and-reporting.md`](notes/B6-clustering-and-reporting.md) — joining metric and log anomalies, hierarchical clustering, ranking, de-duplication, ticket contents, enrichment.

### Part C — making it trustworthy
- [`notes/C1-the-ground-truth-problem.md`](notes/C1-the-ground-truth-problem.md) — lab faults and resolved reports, backward vs forward validation, confusion matrix, Wilson interval, false-alarm rate, time-ordered validation.
- [`notes/C2-template-engineering.md`](notes/C2-template-engineering.md) — post-processing mined templates, validation on known-different devices, per-OS-family versions, the retraining cascade, coverage monitoring.
- [`notes/C3-data-quality.md`](notes/C3-data-quality.md) — availability, accuracy, timeliness, consistency; how to write a data-quality report.
- [`notes/C4-lessons.md`](notes/C4-lessons.md) — anomaly ≠ issue, the human in fault localisation, scope too narrow, collection limits, hybrid analysers, release-health checks.
- [`notes/C5-from-service-to-tool.md`](notes/C5-from-service-to-tool.md) — the stand-alone analyzer: linked views, local parsing, transparency, privacy by design, survey-driven redesign, success metrics.

### Reference files
- [`glossary.md`](glossary.md) — one definition per term, alphabetical.
- [`constants.json`](constants.json) — every number this kit cites, each labelled public or illustrative, with its source.

## Question a reader asks → note that answers it

| Question | Note |
|---|---|
| Why can't support and rule-based tools find these faults? | [[notes/A0-why-fleets-need-log-analysis]] |
| Should the analysis run on the device or in the cloud? | [[notes/A0-why-fleets-need-log-analysis]] |
| Why is the log evidence usually gone when I look? | [[notes/A1-what-a-device-log-is]] |
| Why can't I trust the order of lines in a log? | [[notes/A1-what-a-device-log-is]] |
| Why is a jump in a small device family often noise? | [[notes/A2-fleet-metrics]] |
| What is a template, and should I mine it or read it from the code? | [[notes/B1-log-parsing-to-templates]] |
| How do I turn a log into something a model can read? | [[notes/B2-windows-and-count-vectors]] |
| How long should a window be? | [[notes/B2-windows-and-count-vectors]] |
| How does an isolation forest score a window, and what does 0.8 mean? | [[notes/B3-anomaly-detection-on-logs]] |
| Why not train a classifier? | [[notes/B3-anomaly-detection-on-logs]] |
| Why weighted least squares and not ordinary regression for fleet trends? | [[notes/B4-fleet-trend-detection]] |
| How many false alarms will 10 000 daily tests give me? | [[notes/B4-fleet-trend-detection]] |
| The window is anomalous — now what? | [[notes/B5-from-anomaly-to-root-cause]] |
| How do I recover event order from interleaved threads? | [[notes/B5-from-anomaly-to-root-cause]] |
| How do I avoid one ticket per device for a fleet-wide fault? | [[notes/B6-clustering-and-reporting]] |
| How do I evaluate a detector when nobody labelled anything? | [[notes/C1-the-ground-truth-problem]] |
| Is "60 % detection" on ten cases a meaningful number? | [[notes/C1-the-ground-truth-problem]] |
| What breaks when developers change their print statements? | [[notes/C2-template-engineering]] |
| Is it the model or the data that is producing false alarms? | [[notes/C3-data-quality]] |
| Why are so many flags the customer's router? | [[notes/C4-lessons]] |
| Why did the detector miss a "connectivity" fault? | [[notes/C4-lessons]] |
| What should an interactive log tool show, and how do I keep it private? | [[notes/C5-from-service-to-tool]] |

## Conventions

- Notes use the ASD-STE100-at-80% style: one fact per sentence, active voice, one term per concept, caveats before results, numbers with units.
- The subject is generic: "a maker of connected consumer devices", "the fleet", "a fleet health-monitoring service", "a stand-alone health analyzer".
- Every number is public with a citation or labelled illustrative (see [`SOURCES.md`](SOURCES.md) and [`constants.json`](constants.json)); nothing is a measurement from any specific fleet.
- "my arithmetic", "my interpretation", and "generalised" label derived values, the author's own claims, and ideas restated from internal material.
- `[[wikilinks]]` connect notes inside this kit.
