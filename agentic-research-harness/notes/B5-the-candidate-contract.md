# B5 — The candidate contract

**Source:** generalised from internal methodology notes, 2026 (§3.4); the harness README (topic directory, classes and tracks); the demonstration topic's AGENTS.md rule 3 and README §4. · **Status:** concept note.

## In one sentence
A candidate is a small, immutable directory that names its parent and patches the system at runtime, so every result can be reproduced by walking the parent chain and nothing an agent does can change a candidate someone else already relies on.

## What it is
A **candidate** is one proposed change, stored as `candidates/<id>/`. It holds:

- `candidate.json`: `id`, `parent` (the candidate it starts from), a **class** field, flags and a description;
- the code the evaluator consumes. In the first campaign this was a Python file with two hooks, one called before the model loads and one after, that patch the model at runtime. In the scheduling topic it is a `scheduler.py` with a `Scheduler` class (see [[C2-the-scheduling-topic]]).

The **candidate contract** is the set of rules every candidate obeys.

1. **Small units.** One idea per candidate.
2. **Parent-linked.** A change to an existing idea is a new id with `parent` set. The chain from the baseline to any candidate is reproducible by walking parents.
3. **Runtime patching, not upstream edits.** Upstream sources (the model library, the framework) are never edited. A candidate applies its change when it runs.
4. **Immutable.** An existing candidate directory is never modified. Other agents and the evidence records rely on it. The evaluator hashes the candidate tree before and after the run; a change during the run makes the result non-promotable.

## How it works
**Why immutability.** If an agent could edit a candidate after its evaluation, the record would describe code that no longer exists. Another agent that copied the candidate as a parent would inherit an untested change. An immutable directory keeps "this record" and "this code" the same thing.

**Why runtime patching.** Edits to upstream code spread across many files, collide between parallel agents, and are hard to undo. A runtime patch is one file in one directory. Removing the candidate removes the change.

**Classes and tracks.** The **class** field labels what kind of change a candidate is. In the first campaign it was a **numerics tag**: `exact` (the computation is unchanged up to legitimate noise) or `reduced` (a precision trade, such as a lower-precision weight format). A **champion track** is a separate leaderboard with its own champion; each track accepts some classes. Two tracks — exact, and any class — let a precision trade coexist with exact rewrites without being mistaken for one. In the scheduling topic every candidate is `exact` and there is one track; the field stays for later use (for example preemptive versus non-preemptive schedulers).

## How it is used in a campaign
- Researchers copy what they need from the parent's files into a new directory.
- The harness lists candidates to the planner, which names a parent for each task ([[B7-agents-and-the-loop]]).
- A candidate competes in every track whose accepted classes include its class.

## Common confusions
- **"A branch per candidate is the same thing."** A branch can be rewritten. A directory that the harness hashes and the records cite cannot silently change.
- **"Reduced precision is cheating."** It is a legitimate trade if it passes the gate. It is a different claim, so it lives on its own track; whether it counts as a headline result is a human decision ([[B8-reporting]]).
- **"Parent means the best candidate."** Parent means the code this candidate started from. A task can start from a non-champion to explore a different direction.

## Why it matters
Parallel agents produce many candidates quickly. The contract keeps each one small, reproducible and frozen once evaluated, so the campaign's history is a tree of tested changes rather than a pile of edits.

## Terms introduced
- **candidate** — one proposed change, stored as an immutable directory with `candidate.json`.
- **parent** — the candidate a new candidate starts from.
- **candidate contract** — small, parent-linked, runtime-patching, immutable.
- **runtime patching** — applying a change when the system loads or runs, instead of editing its sources.
- **class** — the label of the kind of change a candidate makes.
- **numerics tag** — the class used for precision: `exact` or `reduced`.
- **champion track** — a leaderboard with its own champion, accepting some classes.
- **champion** — the current best promoted candidate of a track.
