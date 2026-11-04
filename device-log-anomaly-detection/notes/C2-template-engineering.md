# C2 — Template engineering: post-processing, versions, and retraining

**Source:** Drain (He et al., ICWS 2017) for the mining baseline; generalised from internal design documents of a device-health programme (see [`../SOURCES.md`](../SOURCES.md)). · **Status:** concept primer. All counts are illustrative.

## In one sentence
A template set is not built once: mined templates need post-processing to merge duplicates and mask variables, the set must be versioned per OS family and software release, and every change to it ripples through the feature space into a model retrain.

## What it is
**Template engineering** is the work of building, cleaning, validating, and maintaining the template set that the parser uses ([[B1-log-parsing-to-templates]]). It is unglamorous and decides the quality of everything downstream.

## How it works
**Post-process mined templates.** A data-driven miner's output needs four repairs:

1. **Merge values mistaken for constants.** If `pingTest target=GATEWAY`, `target=LOCALHOST`, and `target=NAMESERVER<*>` are separate templates, decide whether the target is a parameter (merge into `target=<*>`) or a meaningful constant (keep apart). Host names in an HTTP test are usually parameters; a state name usually is not.
2. **Mask variables the preprocessor missed.** IP addresses, MAC addresses, host names, and file paths should become `<*>` before mining, or they create one template per value.
3. **Check against the source.** Map each mined template to its print statement. Templates with no print statement are parsing errors. Print statements with no template are the gaps — usually the error and warning paths ([[B1-log-parsing-to-templates]]).
4. **Group by function.** Label each template by its role: connection status, ping test, HTTP test, recovery (network bounce), monitoring lifecycle, captive-portal check, and error paths. The labels make features and reports readable.

**Validate on known-different devices.** A simple check is to parse logs from an illustrative 10 devices believed healthy and an illustrative 5 with a known problem (for example, many disconnects despite a strong signal) over the same week. The healthy devices should show a regular, periodic pattern of status and test templates. The problem devices should show extra templates — recovery and error templates — that never appear on the healthy ones. If they do not, the template set cannot separate the two, and no model will.

A second lesson from such a check: one component can *separate* normal from abnormal and still not *explain* it. A diagnostics service may show that something is wrong while the cause lives in the supplicant, the DHCP client, or the kernel driver ([[C4-lessons]]).

**Versions and OS drift.**

- **Per OS family.** Two OS families running "the same" Wi-Fi stack have different components and print statements. Keep one template set per family (an illustrative few hundred templates each), and per component.
- **Per release.** Developers change print statements often. A changed statement makes old templates miss and new lines fall into the unmatched bucket. Rule-based tools break silently in the same situation; a template pipeline at least sees it.
- **Stable IDs.** Derive the template ID from a hash of the normalised template text, so the same template keeps its ID across rebuilds and across devices.

**The retraining cascade.** One template change triggers four steps:

1. rebuild the parse tree;
2. the feature space (one column per template) changes;
3. the anomaly model must be retrained on new count vectors;
4. the ground-truth set must be re-scored to confirm nothing regressed ([[C1-the-ground-truth-problem]]).

Set the cadence by the release train: rebuild when a release that changes the monitored components ships, not on a fixed calendar.

**Monitor coverage.** Track, per release and per component, the share of lines that match any template and the size of the unmatched bucket. A jump in unmatched lines after a release is the signal to update templates.

**Toward automation.** Three steps reduce the manual cost (internal roadmap, generalised):

- extract print statements from the source automatically (find logging calls, take the format string, replace format specifiers with `<*>`);
- treat the source-code set as the benchmark and add data-driven discoveries from the unmatched bucket;
- compare approaches on the same ground-truth set before switching.

## How it is measured or used
- **Coverage** — the share of lines matched, per component and release.
- **Duplicate rate** — the share of templates that map to the same print statement.
- **Gap list** — print statements with no template, sorted by severity (errors first).
- **Throughput** — lines parsed per second; an illustrative tens of millions of lines in a few minutes is the scale a weekly check across a few devices needs.

## Common confusions
- **"The template set is configuration."** It is a model artefact with versions, tests, and a release process.
- **"Unmatched lines are noise."** They are usually new code or a mis-masked variable. Review them.
- **"Retraining is only about the model."** A template change without a ground-truth re-run can lower detection silently.

## Why it matters for fleet operations
Fleets run several OS families and many releases at once. A pipeline whose templates lag behind the code loses exactly the new paths a new release introduces — which is where the regressions are.

## Terms introduced
- **template engineering** — building, cleaning, validating, and maintaining the template set.
- **post-processing (templates)** — merging duplicates, masking variables, and checking mined templates against source.
- **template coverage** — the share of log lines that match some template.
- **OS drift** — changes to print statements and components across OS families and releases.
- **stable template ID** — an ID derived from the normalised template text, unchanged across rebuilds.
- **retraining cascade** — the chain template change → tree rebuild → new feature space → model retrain → ground-truth re-run.
