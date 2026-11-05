# Explorers — rung 3 (learn-explorer)

Four single-file, no-build HTML explorers for the *hri-experience-platform* concept primer. Open one with a double-click
(or `open 01-reducer-sandbox.html`). No server, no network, no build step.

Each page inlines its parameters in a `<script type="application/json" id="params">` block (also shipped as
[`params.json`](params.json)). Every entry that exists in [`../constants.json`](../constants.json) is copied verbatim with its
`class` and `source`; nothing is retyped. Values the page needs that are not in `constants.json` (primitive run times, the
dispatcher's timings, the size of the rule matrix) are separate `page_*` entries, class `illustrative`, source "page model
choice (not in constants.json)". Prose numbers on the pages are filled from the params block (`data-p`), so they cannot
drift. The model of each page sits between `/*MODEL-START*/` and `/*MODEL-END*/`. It is pure and has a `selfTest(P, assert)`
that runs on the page through `console.assert` and runs the same way under node.

This kit carries **no measured numbers**. Every number is a labelled illustrative design parameter or page choice; there is no
measured overlay on any page, and each banner says so. The only sources are this kit's `notes/`, `glossary.md` and
`constants.json`.

| File | Teaches | Inputs | Notes and constants |
|---|---|---|---|
| [`01-reducer-sandbox.html`](01-reducer-sandbox.html) | A safety input stops the robot only because the kernel sees it before the story: one ordered queue, admission, interception, a pure reducer, validate-then-commit. | 7 preloaded input streams; append any input (arrive, speak, wave, leave, operator stop, safety, staff reset) with a track and a gap; step through every processed event; toggles for interception and the participant-track check | B1, B2, B3, B4; `gesture_wait_timeout_s_illustrative`, `cleanup_ack_timeout_ms_illustrative`, `cancel_settle_target_ms_illustrative`, `cancel_settle_ceiling_ms_illustrative`, `page_timing_01` |
| [`02-switching-experiences.html`](02-switching-experiences.html) | Whether an experience can run is decided at start-up from per-target catalogs; switching is stop–clean–restart, never a hot swap. | target; cross-target milestone; health of 3 input producers and 4 primitive adapters; from/to experience; visit in progress; cleanup, retire and cold-start times; matrix run time and profile count | B2, B3, B5, C1, C2; `sim_cold_start_s_illustrative`, `sim_launch_timeout_s_illustrative`, `sim_retire_timeout_s_illustrative`, `matrix_profiles_illustrative`, `matrix_run_s_illustrative`, `cleanup_ack_timeout_ms_illustrative`, `page_switch_02` |
| [`03-effect-dispatch.html`](03-effect-dispatch.html) | Commit first, then dispatch with deterministic IDs: a lossy link costs retries and pauses, not double actions, half events or orphaned completions. | round trip (1–2 000 ms); failure rate; invalid-effect rate; retries; effects per event; settle bound (target or ceiling); time left on the cleanup deadline | B3, C3; `cancel_settle_target_ms_illustrative`, `cancel_settle_ceiling_ms_illustrative`, `cleanup_ack_timeout_ms_illustrative`, `page_dispatch_03` |
| [`04-conformance-coverage.html`](04-conformance-coverage.html) | A green simulation run proves the kernel rules, not the robot; "done" must name its milestone, and invariants need negative tests. | scope (simulation, or both targets); 6 rungs on/off; negative tests present; cloud reachable | B4, C1, C2, C3; `page_rules_04` (32 rules × 6 rungs; each row cites its note) |

## Specs

### 01 — Reducer sandbox
```
Explorer: A safety input stops the robot only because the kernel sees it before the story does
Teaches:  Every input enters one ordered queue (safety, reset, operator, outcomes and timers, observations), is admitted or
          rejected, is handled by the kernel if it belongs to an intercepted class, and only then reaches the experience's
          pure reducer, whose effects are validated and committed as one snapshot before dispatch (B1-B4).
Inputs:   7 preloaded streams; append-an-input builder (type, track A/B, gap 0.5-15 s); event stepper;
          toggle "kernel intercepts safety, operator stop, reset and departure first"; toggle "admission checks the track".
Outputs:  per step: kernel decision, reducer rule (transition / update / reject), validation, committed effects;
          kernel envelope (phase, session, participant track, claims, commands, timers, cleanup); local state
          (schema, state_name, heard); hazards (only when a toggle is off).
Picture:  timeline lanes: kernel phase; action slot, body, head, audio out (a bar per claim, invoke to completion or
          quiescence proof); story timer; input markers (delegated, intercepted, rejected, hazard); cursor at the step.
Cases:    happy path; timer expires; bystander waves; visitor leaves mid-wave; safety mid-wave then reset;
          talking over the greeting (audio-out conflict); operator stop during a reply.
Model:    the wave experience of B1 (greet → await_wave → wave; timer → gesture_not_observed; completion cleanup).
          The speech → reply-turn rule is a page addition so that "visitor speaks" has an effect.
Out of scope: forced cleanup and recovery (the page's quiescence time is inside the settle target; see 03), gaze.
```

### 02 — Switching experiences
```
Explorer: Eligibility is derived from per-target catalogs; switching is a full restart
Teaches:  Required capabilities are derived from declared inputs and primitives; readiness fails unless each has a healthy
          producer or adapter on this target; optional inputs only select a declared degraded branch; a simulation producer
          says nothing about the robot; switching = stop admission, cleanup, clean-store proof, stop, start, readiness (B5).
Inputs:   target; cross-target milestone; 7 health checkboxes; from/to; visit in progress; cleanup 0.5-15 s;
          retire 30-600 s; cold start 60-1800 s; matrix run 60-600 s; profiles 1-8.
Outputs:  eligible / degraded / not eligible per experience with reasons; switch steps with bounds and the failing step;
          downtime; serial profile-matrix time = n × (cold start + run + retire) (B5, my arithmetic); state table
          (before, after, what a rejected hot swap would have to prove).
Cases:    simulation all healthy; switch during a visit; browser microphone down; physical before / after the milestone;
          stuck cleanup blocks the switch; slow cold start.
Model:    the experiences' declared inputs and primitives are page choices following B3 and B5 (the gesture input and its
          physical deferred record are from B5). The notes give no physical restart time, so the timeline uses the
          simulation host lifecycle (C1).
```

### 03 — Effect dispatch
```
Explorer: Commit first, then dispatch with deterministic IDs
Teaches:  Atomic preparation and dispatch plus idempotent re-dispatch remove second actions, half-dispatched events and
          orphaned completions; they do not remove the retries and pauses a lossy or slow link costs; when retries run out
          the kernel cancels, and the settle deadline min(request + settle bound, cleanup deadline) decides whether
          quiescence proof can arrive before forced cleanup (B3, C3).
Inputs:   round trip 1-2000 ms; failure rate 0-60 %; invalid-effect events 0-30 %; retries 0-5; effects per event 1-4;
          settle bound (target / ceiling); time left on the cleanup deadline 0-10000 ms.
Outputs:  expected visible seams per 100 events, naive vs kernel, by type; extra dispatches; deduplicated re-dispatches;
          forced cleanups; a strip of 24 seeded events.
Equations: attempts = Σ_{i=0..R} f^i; executions = (1 - f(1-a)) × attempts; extra executions = executions - (1 - (f(1-a))^{R+1});
          exhausted = f^{R+1}; cancel attempts in the settle window = floor((D - L)/T) + 1, stuck = f^n.
Cases:    default; healthy link; lossy link; very fast adapter; an effect fails validation; slow adapter;
          cancel near the cleanup deadline; round trip past the settle bound.
"Seam" is the page's word; the notes do not count seams.
```

### 04 — Conformance coverage
```
Explorer: A green simulation run proves the kernel rules, not the robot
Teaches:  The ladder (kernel conformance, experience suite, simulation acceptance, live-chat gate, physical acceptance,
          representative acceptance) and which rung proves which rule; milestones (simulation, cross-target) and the
          live-chat gate; negative tests; the rules simulation cannot prove; two rules outside every rung (C1, C2, B4).
Inputs:   scope; 6 rungs on/off; negative tests present; cloud reachable.
Outputs:  rules proven; the milestone you may name; live-chat gate; gaps by kind (needs the robot, not exercised,
          positive only, outside the ladder); per-rule table with its note.
Cases:    simulation milestone; positive tests only; cloud outage; skip the kernel suite; simulation and physical;
          robot runs without the simulation rungs.
Judgement rows: rule 27 (contact force) is my reading: the notes name physical acceptance as the robot gate but do not
          list this check; rule 29 (conversation quality, social timing) is counted as provable by a live human in the
          browser in simulation scope, my reading of C1.
```

## Self-tests (reproduce the notes' own numbers and rules)

- 01 (16 asserts): settle target ≤ ceiling < cleanup deadline (B3); gesture_not_observed at 1 + 3 + 10 s; a reply turn overlaps the wave (B3 concurrency between kinds); a bystander's wave is rejected at admission (B2); departure enters common cleanup (C2); claims are released only on quiescence proof (B3); interception off lets the wave run through a safety input; an audio-out conflict commits nothing (B3); byte-identical replay.
- 02 (12 asserts): one profile cycle = 600 + 300 + 300 = 1 200 s and 5 profiles = 100 min (B5); launch bound > cold start (C1); the wave is not eligible on the physical target because the gesture input is deferred (B5); physical execution disabled before the cross-target milestone (C2); cleanup past the deadline → recovery (B2).
- 03 (15 asserts): the settle deadline of a cancel 600 ms before cleanup's deadline is clamped to 600 ms (C3 worked example); expected attempts; 0.1875 extra executions per effect at f = 0.5, one retry (my arithmetic); the closed form agrees with a 20 000-event seeded simulation on three cases; over every slider extreme the kernel never shows more seams than the naive dispatcher.
- 04 (11 asserts): the simulation milestone holds with all rungs and fails without negative tests (C2); a cloud outage blocks only the live-chat gate (C2); physical acceptance alone gives no cross-target milestone; every rule cites a note.

## Verification

- node: all 54 self-tests pass; slider-extreme sweeps of 28, 1 024, 128 and 512 combinations give no non-finite output; every inline params block equals `params.json` and the `constants.json` entry.
- `learning/stories/tools/shoot.py` on each page (desk 1280 px and phone 390 px, every preloaded case): no console errors, no failed asserts, no overflow. Shots read back.
- Playwright sweep at 1280 and 390 px: every range at min and max, singly and all together, × every select option × each checkbox flipped, plus every append type and every step on page 01 (2 420 states): no NaN, Infinity or undefined in the page text, no overflow, no console errors.
- `learning/tools/public-scan.sh learning/hri-experience-platform`: clean.
