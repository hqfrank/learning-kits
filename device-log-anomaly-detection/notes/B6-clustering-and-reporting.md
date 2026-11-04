# B6 — Clustering similar anomalies, and automated reports

**Source:** agglomerative hierarchical clustering from any machine-learning text (e.g. scikit-learn `AgglomerativeClustering` documentation, https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering); Gower, "A general coefficient of similarity and some of its properties", Biometrics 27:857–871, 1971; generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer.

## In one sentence
One fault on many devices should become one ticket, not hundreds, so the pipeline joins each device's metric and log anomalies into one row, clusters similar rows bottom-up, ranks clusters by how many devices they hit and how strong the evidence is, and writes one evidence-rich ticket per cluster.

## What it is
**Anomaly clustering** groups anomalous device-days that look alike, so that each group is likely one underlying cause. **Automated reporting** turns each group into a ticket, or enriches an existing ticket, with the evidence an engineer needs to start.

## How it works
**Step 1 — join.** For each anomalous (device, date), join the metric anomaly and the log anomaly into one row with *m* + *n* + *p* columns:

- *m* attributes — family, software version, country, router vendor (OUI);
- *n* metric features — the device-day feature values ([[A2-fleet-metrics]]);
- *p* log features — the counts of the anomalous window's templates ([[B2-windows-and-count-vectors]]).

**Step 2 — distance.** Columns have different types and scales: categories, counts, durations. Scale the numeric columns, and use a mixed-type measure such as Gower's similarity (Gower 1971), or one-hot encode the categories with a weight per block of columns. The choice decides what "similar" means.

**Step 3 — cluster bottom-up.** **Agglomerative hierarchical clustering** starts with each row as its own cluster and repeatedly merges the two closest clusters. The **linkage** sets the distance between clusters: single, complete, average, or Ward. Cut the resulting tree (dendrogram) at a distance threshold, so the number of clusters follows from the data rather than being fixed in advance.

**Step 4 — rank.** For each cluster compute the number of affected devices, how often the log pattern recurs, and the mean anomaly score. Rank by a combination of these. Many devices, a recurring pattern, and high scores come first.

**Step 5 — de-duplicate against open tickets.** For each cluster, decide one of three actions: drop it (already known and closed as environmental), append it to an existing ticket (same pattern), or open a new ticket.

**Step 6 — write the ticket.** One ticket per cluster holds:

1. a table of affected devices: device ID, family, router vendor, country, software version, affected time range, release cohort, hardware build, and whether other devices in the same household on the same access point show the same behaviour;
2. the metric anomaly: one paragraph and a link to the trend;
3. the log anomaly: the parsed snippet that shows the pattern, its frequency, and the full raw logs for the affected range (main, kernel, system, radio buffers).

**Step 7 — close the loop.** When an engineer resolves the ticket, the root-cause label (device defect, environmental, data artefact) flows back. It feeds the direction and drop rules, and it becomes ground truth ([[C1-the-ground-truth-problem]]).

**Enrichment, not only detection.** The same components serve tickets that arrive from people:

- **user-reported bugs** from a pre-release programme — most arrive with a one-line description and no diagnosis, so most are never investigated (an illustrative majority of an illustrative 1 000 such tickets per year). Auto-attaching metric anomalies, log anomalies, similar-device matches, and release correlation lowers the cost of the first look;
- **support escalations** — the same enrichment, keyed by the device ID in the ticket.

Three checks give the enrichment its value: **similar devices** (do other devices with the same attributes show the pattern? one-off or fleet-wide?), **release correlation** (did the change start with a software update?), and **known-issue matching**.

**Meet people where they work.** For a recurring human process such as a weekly metrics review, put the ranked anomalies into the dashboard the reviewers already use, as a new tab, rather than in a new tool.

## How it is measured or used
- **Cluster purity** — the share of a cluster's devices that share the resolved root cause; measured from closed tickets.
- **Duplicate rate** — the share of new tickets later merged into another.
- **Time to first action** on enriched versus non-enriched tickets.

## Common confusions
- **"Clustering finds causes."** It finds similar *symptoms*. Two causes with the same symptoms land in one cluster; one cause with different symptoms on two device families lands in two.
- **"More information in the ticket is better."** In a user survey of the internal tool, columns the designers thought useful were judged confusing; statistical plots such as probability-mass charts were not understood by most users (generalised; see [[C5-from-service-to-tool]]). Fewer, clearer fields win.
- **"A ticket is the end."** The resolution label is the most valuable output for the next model iteration.

## Why it matters for fleet operations
Without clustering, a fleet-wide regression floods the tracker and nobody reads any of it. With clustering and ranking, an engineer reads a short list ordered by impact, and each item carries the evidence to start.

## Terms introduced
- **anomaly clustering** — grouping anomalous device-days with similar attributes, metrics, and log patterns.
- **agglomerative hierarchical clustering** — bottom-up clustering that repeatedly merges the two closest clusters.
- **linkage** — the rule for the distance between two clusters (single, complete, average, Ward).
- **dendrogram** — the merge tree of hierarchical clustering; cut at a threshold to get clusters.
- **Gower similarity** — a similarity measure for rows with mixed numeric and categorical columns.
- **ticket enrichment** — attaching automated evidence to a ticket that a person opened.
- **release correlation** — checking whether an anomaly started with a software update.
- **similar-device matching** — checking whether devices with the same attributes show the same pattern.
- **root-cause label** — the resolved category of a ticket (defect, environmental, data artefact), fed back to the pipeline.
