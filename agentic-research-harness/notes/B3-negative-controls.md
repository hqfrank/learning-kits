# B3 — Negative controls

**Source:** generalised from internal methodology notes, 2026 (§3.2, checklist step 4); the demonstration topic's README §2 and worklog "Calibration". · **Status:** concept note.

## In one sentence
A negative control is a deliberately wrong candidate that the evaluator must reject on every version; a gate that has never rejected a plausible cheat is untested.

## What it is
A **negative control** is a candidate built to be fast or plausible and wrong. Each control encodes one way the metric could be gamed. Controls live in their own directory, are never promoted, and are never shown to the agents as candidates.

The first campaign used four controls on a diffusion-model policy:

| Control | Why it is tempting | What must reject it |
|---|---|---|
| Fewer denoising steps | Fast and the output looks plausible | Correctness gate against the reference |
| Output scaled by an illustrative `c1_control_scale_illustrative` = 3 % | A small drift that a loose limit accepts | Calibrated per-dimension limits |
| Cached output | Very fast | Inputs that change per call; "model ran once" check |
| Perturbation on a second compute core | Tests that a wrong result from a two-core plan cannot pass (my reading; the source names the control only) | Correctness gate |

The scheduling topic used three:

| Control | What it does | What rejects it |
|---|---|---|
| `starve_soft` | Never runs soft chains | Completion gate: logging and telemetry never finish |
| `not_ready` | Returns a job it already started | Integrity: the scheduler returned a job that is not ready |
| `wallclock` | Breaks ties with an unseeded random choice | Order probe: reversed-seed results differ |

## How it works
Controls are built **at the same time as the gate**, not after. The evaluator is finished only when two things hold on every input set, held-out included:

1. the baseline is ACCEPTED with a margin clearly below 1;
2. every control is REJECTED.

**A control can be wrong too.** In the scheduling topic the `wallclock` control first salted its tie-break with the parity of a nanosecond clock. On the development machine that clock had microsecond resolution, so the parity was always even and the control was accidentally deterministic: the order probe could not see it. The fix used an unseeded random generator. (Source: demonstration topic worklog, "Calibration".) The lesson is general: run each control and confirm it fails for the reason it was built for.

**Development host and evaluation host.** The first campaign separated them.

- The **development host** has only the visible set. Its records are marked INVALID by design, so a development number can never be mistaken for an official one.
- The **evaluation host** has the visible and held-out sets and runs only official evaluations.
- A **device lock** on each host makes sure nothing else shares the device with a timed run.

## How it is used in a campaign
- Every evaluator version re-runs every control (checklist step 10, [[C5-the-checklist]]).
- The weekly report has an "evaluator integrity" section that lists the controls and their verdicts (see [[B8-reporting]]).
- A new failure mode seen on a real candidate becomes a new control and, usually, a new integrity check (see [[B2-the-frozen-evaluator]]).

## Common confusions
- **"The baseline passing proves the gate works."** It proves the gate is not too tight. Only a rejected control proves the gate is not too loose. A gate needs both.
- **"Controls are for adversarial agents."** Most fake results are accidents: a bug that skips work looks the same as a cheat. Controls catch both.
- **"One control per gate is enough."** One control per known way of gaming the metric. The list grows with the campaign.

## Why it matters
Popper (`pub_popper_year`) argued that a claim is scientific only if some observation could refute it. A gate that nothing has ever failed makes no claim. Negative controls are the observations that show the gate can refute.

## Terms introduced
- **negative control** — a deliberately wrong candidate the evaluator must reject on every version.
- **development host** — a machine with only the visible set; its records are INVALID by design.
- **evaluation host** — a machine with all input sets that runs official evaluations only.
- **device lock** — a lock that keeps other work off the device during a timed run.
- **falsifiable** — able to be refuted by some observation (Popper 1959).
