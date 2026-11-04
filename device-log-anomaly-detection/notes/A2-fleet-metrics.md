# A2 — Fleet metrics: event counters, device-days, and the share of devices

**Source:** generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)); sample-proportion standard error from any introductory statistics text (e.g. NIST/SEMATECH e-Handbook of Statistical Methods, §7.2.4, https://www.itl.nist.gov/div898/handbook/prc/section2/prc24.htm). · **Status:** concept primer.

## In one sentence
Fleet metrics are event-triggered counters that devices send to the cloud; the most useful fleet-level quantity is the share of active devices that emitted a metric on a day, and its uncertainty depends on how many devices were active, so a day with few devices is a noisy day.

## What it is
A **fleet metric** is a structured record a device emits when a defined event occurs. A typical raw record holds:

- the device ID, device family, country, and software version;
- the time the device recorded the event;
- the metric name (for example, "number of Wi-Fi disconnects");
- one or more **category** fields that qualify it (for example, the band, the reason code, the signal-strength bar);
- a count of events and a sum of values (for duration metrics, the sum is seconds).

Metrics are **event-triggered**. A disconnect metric exists only when a disconnect happened. A healthy device emits nothing for that metric on most days.

## How it works
**Step 1 — pivot to features.** In the raw store the meaning of a category field depends on the metric name. A preprocessing query pivots the records into one row per device, day, and **feature**. A feature is the metric name joined to one category, for example `disconnects__reason-code` with category `3`. This gives every column one meaning.

**Step 2 — add attributes.** The same step attaches **attributes** that describe the device rather than its behaviour: software version, country, device family, and router vendor (derived from the router's MAC-address prefix, the organisationally unique identifier, OUI). Attributes are used later to slice the fleet ([[B6-clustering-and-reporting]]).

**Step 3 — aggregate to device-days.** Each device contributes at most one row per feature per day. This **device-day** is the unit of analysis.

**Step 4 — aggregate to the family level.** For each day, device family, and feature, compute two quantities:

- **share of devices** (also called the device ratio): *p̂* = (devices that emitted the feature) ÷ (devices that were active that day);
- **intensity**: (total events of the feature) ÷ (active devices).

**Why the share's variance depends on sample size.** If the active devices are a fair sample of the family, *p̂* is a **sample proportion**. Its standard error is

  SE(*p̂*) = √( *p̂* (1 − *p̂*) / *n* ),

where *n* is the number of active devices that day (NIST e-Handbook §7.2.4). Halve *n* and the standard error grows by √2.

Worked example (illustrative numbers, my arithmetic): a family has an illustrative 100 active devices. Three of them emit a rare disconnect reason. The share jumps from about 0 % to 3 %. Its standard error is about 1.7 percentage points. The same 3 % from an illustrative 10 000 devices would have a standard error of about 0.17 percentage points. The first jump could be three unlucky households; the second is a fleet change.

## How it is measured or used
- **Trend detection** fits a line to the daily share and weights each day by its precision ([[B4-fleet-trend-detection]]).
- **Per-device detection** uses each device's daily feature vector ([[B3-anomaly-detection-on-logs]]).
- **Population matters.** A small pre-release population gives low statistical power for rare events. A large production population gives power but usually no logs for the devices; a common workaround is to diagnose matching pre-release devices as **proxies** (same family, software version, and anomaly).

## Common confusions
- **"A higher share is always worse."** Direction matters per metric. Fewer disconnects, or more successful recoveries, is an improvement. A filter must drop "good" changes before ticketing ([[B4-fleet-trend-detection]]).
- **"Zero means healthy."** For an event-triggered metric, zero can mean healthy, or off, or not reporting. Missing days look like zeros unless they are detected ([[C3-data-quality]]).
- **"Percentiles are robust."** A tail percentile (p90, p99) over a small population is very noisy. Report the population size with the percentile.
- **"Device-level and family-level views agree."** A family-level trend can hide a few very bad devices, and a few very bad devices can look like a trend in a small family.

## Why it matters for fleet operations
Metrics are cheap, structured, and available for every device; logs are not. Metrics are therefore the trigger that chooses which logs to read. Getting the statistics of the share right decides whether the trigger fires on real changes or on small-sample noise.

## Terms introduced
- **fleet metric** — a structured, event-triggered record a device sends to the cloud.
- **event-triggered** — emitted only when the event happens; absence is the normal state.
- **feature** — one metric name joined to one category value, giving a column with one meaning.
- **attribute** — a descriptor of the device (software version, country, family, router vendor), used for slicing.
- **OUI (organisationally unique identifier)** — the vendor prefix of a MAC address; it identifies the router maker.
- **device-day** — one device's aggregated metrics for one day; the unit of analysis.
- **share of devices (device ratio)** — active devices that emitted a feature ÷ all active devices, per day.
- **intensity** — total events of a feature ÷ active devices, per day.
- **sample proportion** — a fraction estimated from a sample; its standard error is √(p(1−p)/n).
- **proxy device** — a device with logs that matches an anomalous group without logs, used for diagnosis.
