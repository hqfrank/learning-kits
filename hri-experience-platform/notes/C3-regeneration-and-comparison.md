# C3 — Regeneration and comparison: re-deriving an old experience, and comparing evidence across targets

**Source:** generalised from internal design documents (see [`../SOURCES.md`](../SOURCES.md)); Fowler, "Strangler fig application" (https://martinfowler.com/bliki/StranglerFigApplication.html) for the parallel-line idea. · **Status:** concept primer. Every number is labelled illustrative.

## In one sentence
The richest existing experience is regenerated through the platform's own authoring flow as an *experiment* whose mismatches become platform improvements or explicit "unsupported" records, never special cases in the kernel; and "the same scenario on simulation and on the robot" is measured by a comparator that canonicalises IDs, compares declared fields exactly or within declared tolerances, and lists the only differences it permits.

## What it is
Two comparators serve two questions.

1. **The regeneration experiment.** Is the platform complete enough to express the experience we already have? The old experience, a story of an illustrative 12 local states (`baseline_local_states_illustrative`) from selection through handshake, enrolment, conversation, gift and farewell, keeps running unchanged on a frozen image as a **parallel line**. Separately, its requirements are fed into the authoring flow ([[B1-experiences-as-reducers]]) as a new description.
2. **The cross-target comparator.** Does an experience behave the same on the simulation target and on the robot?

## How it works
**The regeneration experiment ends in one of two artifacts.**

- **Parity** against the old experience's own scenarios, under a *semantic* comparator; or
- a **capability-gap report** that lists each mismatch as a platform improvement (catalog, chapter, classifier, or kernel and wire extension) or an explicit unsupported-feature record with owner and rationale.

The semantic comparator normalises both runs to: the ordered adapter command sequence per scenario (command kind, primitive or behaviour ID, target, deadline class); the ordered participant decisions; cleanup results and terminal outcomes; operator-visible alerts and recovery entries; and the set of authorities exercised. A *superset* of authorities on the regenerated side is a failure, not a gap. Byte identity of records, snapshots, timestamps or digests is neither required nor measured.

Two rules keep the experiment honest.

- **It never bends the platform.** A comparator failure must not be resolved by adding experience-specific behaviour to the kernel or the effect vocabulary.
- **A gap report closes the experiment and authorises nothing.** Retiring the frozen line needs a replacement that has independently passed the experience suite, simulation acceptance and, for the robot, physical acceptance. An accepted gap report cannot be used to deploy an incomplete regeneration.

The old line is retired only when such a replacement exists for each target — the strangler-fig pattern: the new system grows beside the old one, and the old one is removed only when the new one carries the load on its own merits.

**The cross-target comparator** normalises each run's evidence and requires equality on:

- ordered kernel phase transitions and local state-name transitions;
- ordered primitive invocations: ID, contract kind, authority class, claimed resources, head–gaze coordination, speech semantics, outcome class (completed, cancelled, failed, timed out), and normalised parameters;
- ordered authority lifecycle events, with still-held claims and reason class;
- the visitor-audio permit lifecycle;
- **overlap structure**: for every pair of invocations and resources, whether their held intervals overlap, are strictly ordered, or meet at a preemption hand-off. A target that serialises what the other overlaps fails, even if order and outcomes match;
- participant decisions, input admission decisions and admitted payload fields;
- correlation structure: which invocation each outcome, cancellation, timer expiry and progress event belongs to;
- cleanup result, terminal outcome, and the set of authorities exercised (a superset on either side fails).

**IDs are canonicalised, not stripped.** Raw command, lease, timer, stream, session and generation IDs differ between targets by construction, but the relationships between them are semantics. The comparator rewrites every ID to a label in first-appearance order (`cmd#1`, `timer#3`, `session#1`) and compares structure. An outcome attached to `cmd#2` on one target and `cmd#3` on the other is a failure.

**Comparison schemas.** Every primitive and normalised input used by a landed experience declares, per field: `exact` (enums, frames, target IDs, behaviour IDs, the text of a scripted line), `tolerance(abs|rel, value)` (positions, angles, confidences, requested durations), or `ignore` (honestly target-specific, with a reason). Frames and units are exact; a gaze target in a different frame is a failure. A field missing from the schema is compared exactly; `ignore` is never the default. Requested timeouts are compared; elapsed time is not.

**Derived deadlines are checked first.** Each run must prove from its own records that its settle deadline equals the earlier of "request time + settle bound" and any active cleanup deadline ([[B3-the-effect-vocabulary]]). With an illustrative settle bound of 1 500 ms (`cancel_settle_target_ms_illustrative`), a cancel requested 600 ms before cleanup's deadline is clamped to that deadline, and the clamp state must match on both targets even though the raw bounds may differ (my arithmetic). Then raw timestamps and target-specific bounds are stripped.

**Permitted differences** are listed and closed: raw ID values (after canonicalisation); all timestamps, elapsed durations and latencies; implementation artifact, adapter and producer contract IDs; target-specific speech bindings and settle values (each still validated against its own pinned contract); capability health for capabilities declared target-specific; and fields a schema marks `tolerance` or `ignore`. Anything else that differs fails, with a report naming the field and the canonical IDs. Widening a schema or the permitted list needs a design review.

**Live model output is not an oracle.** For the chat experience, both targets get the same deterministic reasoner result and audio fixture, and the full authority structure is compared. Each target also runs the live model separately to prove bounded turns, correlation, interruption, cleanup and fallback. Generated wording and audio bytes are never compared.

## Design choices and trade-offs
- **Semantic, not byte, comparison.** An earlier revision made byte-identical replay of the old experience a gate. It froze the state and effect vocabularies to that experience's and made every kernel change a governed re-baseline, and it bought nothing an owner cared about. It was removed.
- **Overlap structure is the hard part.** Matching order and outcomes is easy; matching *which authorities held at the same time* is what catches a target that silently serialises or parallelises.

## Common confusions
- **"Parity is required for the platform to be done."** It is not; regeneration is required but non-blocking.
- **"Different IDs on two targets are noise."** Values are noise; relationships are signal.
- **"Ignore is a safe default for awkward fields."** Exact is the default; ignore needs a reason.

## Why it matters for robot experiences
Simulation is only worth trusting if a difference from the robot is caught by a machine, not by someone noticing a video looks odd. The comparator turns "it looked the same" into a list of fields that were equal.

## Terms introduced
- **regeneration experiment** — re-deriving an existing experience through the authoring flow to test the catalogs, chapters and classifier.
- **parallel line** — the old experience kept running on a frozen image until an independently validated replacement exists.
- **capability-gap report** — the outcome of a failed regeneration: each mismatch classified as a platform improvement or an unsupported-feature record.
- **semantic comparator** — the tool that compares normalised command, decision, outcome and authority sequences rather than bytes.
- **cross-target comparator** — the tool that requires equal normalised evidence from the simulation and physical targets.
- **canonical ID** — an identifier rewritten to a first-appearance label so that structure can be compared across runs.
- **comparison schema** — the per-field rule (exact, tolerance, ignore) for comparing parameters and payloads.
- **overlap structure** — for each pair of held intervals, whether they overlap, are ordered, or meet at a preemption hand-off.
