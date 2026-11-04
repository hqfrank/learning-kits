# C3 — Data quality: the input problems that become false alarms

**Source:** generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)); data-quality dimensions as commonly used in data-management practice (e.g. Wang & Strong, "Beyond Accuracy: What Data Quality Means to Data Consumers", J. Manag. Inf. Syst. 12(4):5–33, 1996). · **Status:** concept primer. All rates are illustrative.

## In one sentence
In a fleet pipeline the hardest problems are usually in the input data, not the model, so audit the metrics along four dimensions — availability, accuracy, timeliness, consistency — write each finding as check, rate, impact, and fix, and treat every unexplained anomaly as a possible data artefact first.

## What it is
**Data quality** is how fit the input data are for the analysis. A **data-quality report** is a structured audit that measures each problem, states which downstream result it corrupts, and proposes a fix. The four dimensions below are the ones that mattered for event-triggered fleet metrics ([[A2-fleet-metrics]]).

## How it works
**1. Availability — can you get the data at all?**

- Access may be limited to the pre-release population, to one product area's metrics, and to a short retention window (an illustrative 60 days).
- Consequences: many tickets refer to devices outside the population or outside the window, so their data cannot be fetched; and a population of a few hundred devices has little power for rare events. With an illustrative 100 devices in a family, three devices with a rare reason code move the share from about 0 % to 3 % ([[A2-fleet-metrics]]). A real defect and three unlucky households look the same.

**2. Accuracy — are the values right?**

- A typical check: the time a device recorded an event must precede the time the cloud received it. If an illustrative 3 % of records have the device time *after* the receive time, device clocks are wrong (unsynchronised, reset, or in the wrong time zone).
- Consequence: time-based detection relies on correct timestamps. Wrong ordering moves events between days and corrupts the series ([[B4-fleet-trend-detection]]).

**3. Timeliness — is the data there when expected?**

- Whole days can be missing for a cohort, or for every device, because of an ingestion fault.
- Consequence: a missing day looks like a drop to zero for an event-triggered metric, and a model flags it. A gap detector with an alarm, run *before* anomaly detection, is cheaper than explaining false tickets.

**4. Consistency — does each field mean one thing?**

- **Column content mismatch.** A field named "metadata 1" may hold, for most records, what the documentation calls "metadata 3" — shuffled columns in an illustrative few percent to most of the records, varying by device family.
- **Cross-device formats.** The same metric may store a band as a channel index on some families and as a text label on others.
- **Fragile parsing.** A serialisation step that adds or removes one space in a JSON field can make a fixed-position parser read `11a` instead of `11ac`. Parse with a real JSON parser and validate against the allowed values.
- **Documentation drift.** The documented schema may not match the data.

**Where the problems come from.** Each extra copy between the source store and the analysis — an export to object storage as JSON, a re-import — is a chance to reorder columns, change types, and break parsing. Consuming directly from the source store, with an explicit schema, removes a class of faults.

**General hygiene checks** (standard practice; not specific to the source):

- **duplicates** — the same event sent twice after a retry; de-duplicate on (device, time, metric, category);
- **schema changes** — a new category value or a renamed metric after a release; alert on unseen values;
- **outliers from test devices** — devices in automated stress tests emit far more events than any user; filter them by population membership.

**How to write the report.** One row per finding:

| Dimension | Check | Rate (illustrative) | Downstream impact | Fix |
|---|---|---|---|---|
| Availability | ticket devices with fetchable metrics | most, not all | some tickets cannot be enriched | wider access, longer retention |
| Accuracy | device time ≤ receive time | an illustrative 3 % fail | events land on the wrong day | flag or drop; fix device clock sync |
| Timeliness | every cohort has data every day | an illustrative few gap days per year | gap flagged as anomaly | gap detector and alarm before detection |
| Consistency | field content matches field name | varies by family | features mean different things on different families | per-family parser; schema validation; fix at source |

## How it is measured or used
- Run the checks as a daily job, before detection, and attach the day's quality status to every report.
- Use the root-cause label "data artefact" in ticket resolution ([[B6-clustering-and-reporting]]); its share is the false-alarm cost of poor data.
- Push fixes upstream to the owners of the source; patching downstream forever is the expensive path.

## Common confusions
- **"The model is producing false positives."** Often the data are. Rule out gaps, clock errors, and format changes before tuning the model.
- **"A small error rate is harmless."** An illustrative 3 % of mis-timed records is enough to create spurious day-to-day changes in a rare metric.
- **"The documentation describes the data."** Verify the schema against a sample of real records.

## Why it matters for fleet operations
Users judge the whole system by its false alarms. When tickets are opened on data artefacts and never fixed, people stop reading the tickets. Data-quality work is often a larger share of the effort than modelling, and it is the share that keeps the system trusted.

## Terms introduced
- **data quality** — how fit the input data are for the intended analysis.
- **availability** — whether the needed data can be accessed, for the needed devices and period.
- **accuracy** — whether values are correct (for example, timestamps in a possible order).
- **timeliness** — whether data arrive when expected, without gaps.
- **consistency** — whether each field means one thing across records, families, and time.
- **data-quality report** — an audit with one row per finding: dimension, check, rate, impact, fix.
- **gap detector** — a check that flags missing days or cohorts before anomaly detection runs.
- **data artefact** — an apparent anomaly caused by the data pipeline, not by device behaviour.
