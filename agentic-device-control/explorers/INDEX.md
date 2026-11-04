# Explorers — rung 3 (learn-explorer)

Two single-file, no-build HTML explorers for the *agentic-device-control* concept primer. Open them with a double-click, or
`open 01-steps-completion-and-cost.html`. They need no server, network or build step.

Each page inlines its parameters in a `<script type="application/json" id="params">` block, also shipped as `params.json`.
Every entry is copied verbatim (value, unit, class, source) from `../constants.json` by a generator. Nothing is retyped. The
pure model sits between `/*MODEL-START*/` and `/*MODEL-END*/` and runs unchanged under node. Its `selfTest(P, assert)` runs
`console.assert` on the page and in node, and the page writes the count into the sources section.

**This kit has no measurements.** Every number is `public` (cited vendor documentation or paper) or `illustrative` (a round
teaching number). The tasks, screens and tap coordinates in explorer 02 are invented on the page, except
`model_click_illustrative`. Sources used: notes 01–09, `glossary.md` and `constants.json` only.

---

## Spec — 01-steps-completion-and-cost.html  (notes 06, 07, 09)

```
Explorer: A 90 % step is a 59 % task — per-step reliability compounds, recovery breaks the product, caching sets the bill
Teaches:  With no recovery a task of n steps succeeds with p^n (note 09). The ReAct loop recovers wrong steps at the price
          of extra steps (note 06); the step limit cuts off the slow tail. Cost per run = expected steps × tokens per step
          priced by prompt caching (read 0.1×, write 1.25×) plus strong-tier orchestrator calls (note 07). An evaluation of
          N runs reports a Wilson interval, not a number (note 09).
Inputs:   p per-step success 0.5–1 (default 0.9, per_step_success_illustrative)
          n correct steps needed 1–15 (default 5, steps_without_recovery_illustrative)
          r share of wrong steps recovered 0–1 (0 = note 09's p^n, 1 = note 06's idealised loop; default 1)
          L step limit 1–40 (default 20, react_iteration_limit_illustrative)
          tokens per step 1 000–20 000 (default 7 000, vision_call_tokens_illustrative.total)
          caching on/off + cached share 0–1 (default 5 500/7 000, the note 07 split)
          orchestrator calls 0–10 (default 2, the 07 budget-table split)
          evaluation runs N 10–500 (default 50, eval_runs_illustrative)
Outputs:  completion probability, E[steps], expected input tokens, expected $ per run, $ per successful task
          — task_outcome_with_recovery (DP over successes so far), task_success_no_recovery_pn, cached_call_cost_07,
          task_cost_07 (fast tier for steps, strong tier for orchestrator, public $/M), wilson_interval_09.
Picture:  stacked bar chart of steps used per run by outcome (solid = finished, hatched = unrecovered wrong step,
          outlined = hit step limit) with an E[steps] marker; a 0–100 % strip with the predicted completion, the Wilson
          interval N runs would report, and the illustrative 40/50 evaluation of note 09 (diamond, labelled illustrative).
Cases:    no recovery (note 09) · recover every wrong step (note 06) · tight step limit (n + 1, chosen on the page) ·
          budget table caching off / on (note 07).
Overlays: none measured; the 40/50 evaluation is drawn as an illustrative point.
Out of scope: output tokens, the first call's full-prefix cache write, per-call token growth, cache expiry, latency.
```

Self-tests (13): p^n = 0.59 for 0.9, 5; the DP reproduces p^n when r = 0 and when L = n; with full recovery and a large
limit, completion is 1 and E[steps] = n/p; the outcome probabilities sum to 1; a cached call costs 2 425 units, about 35 %
of uncached; caching off costs 1×; the budget table gives 29 000 tokens (about the 30 000 constant), 5 calls and $0.045;
40/50 has a Wilson interval of 0.670–0.888; caching with nothing cached costs more than no caching.

## Spec — 02-agent-graph-stepper.html  (notes 01, 02, 04, 05, 06, 08)

```
Explorer: The planner never touches the screen — one task stepped hop by hop through the agent graph
Teaches:  START (message guards) → orchestrator → router (plain code) → vision or actuator → back to orchestrator → FINISH
          → END with exactly one result. Each vision iteration is one ReAct thought/action/observation, with the
          reference-frame → device-pixel scaling of note 04. Three limits (inner iteration limit, graph step limit,
          watchdog) and loop detection stop different bad runs. The allow-list refuses an off-list tool call.
Inputs:   case (5 buttons); inner iteration limit 1–30 (default 20); graph step limit 1–15 (default 10);
          loop-detection window 0–6 (0 = off, default 3, chosen on the page); watchdog 0.25–10 min (default 5).
          Prev/Next, a step slider, and ← → keys on the figure.
Outputs:  per step: active node, the frame's thought/action/result, the shared state (hops, iteration, calls by node,
          input tokens, elapsed s, last screen, reports, refused calls, status), and the audit log so far.
          — simulate_graph_02 (pure trace generator), scale_to_device_04.
Picture:  the agent graph with the active node and the edge just taken highlighted (colour + ▶ marker + dashed edge); a
          small model-frame inset with the tap point on vision steps.
Cases:    open the video app through the screen · through the OS · wrong tap then recovery (default) · stuck loop then the
          actuator · screen text tries to give an order (the planner is assumed fooled; the allow-list refuses).
Overlays: none.
Out of scope: real model behaviour (the orchestrator's choices are scripted), BUSY / de-duplication paths, confirmation gates.
```

Self-tests (20): the note 04 scaler maps (200, 560) to (375, 1120); the screen route makes 2 vision calls taking 10 s and the
OS route 1 call taking 2 s (`actuator_vs_screen_illustrative`); the screen route takes about the illustrative 20 s;
orchestrator calls = hops + 1 in every case; with loop detection off the stuck turn runs to the iteration limit, and at 3 it
stops after 3 taps; a step limit of 1 ends the stuck case with ERROR; an iteration limit of 3 forces a re-route and the run
still succeeds; the off-list call is refused and counted; a 0.25 min watchdog gives TIMEOUT; every run ends with exactly one
result.

---

## Verification

- `shoot.py` (desk 1280 px and phone 390 px). Each page exposes a small `window.Story` with one scene: the preloaded cases
  on 01, and the trace steps on 02. Result: no console errors, failed asserts or overflow.
- A Playwright sweep covered every case, each slider at min and max on its own, then all at min and all at max. On 01 it
  also ran with caching off; on 02 it also visited the trace steps. It found no NaN, Infinity or `undefined` in the visible
  text and no overflow.
- Node: both self-test suites pass. A NaN sweep checked 4 608 outputs on 01 and 160 limit combinations on 02, and confirmed
  that each inline params block equals `params.json`.

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-steps-completion-and-cost.html` | p^n compounding, recovery vs step limit, caching and tiers set cost, Wilson interval on an evaluation | p, n, r, L, tokens, cache share, orchestrator calls, N | notes 06/07/09; prompt-caching docs (public multipliers, prices); Wilson 1927 |
| `02-agent-graph-stepper.html` | hub-and-spoke graph, router as code, ReAct iterations, three limits + loop detection, allow-list refusal | case, iteration limit, step limit, loop window, watchdog | notes 01/02/04/05/06/08; computer-use docs (reference frame) |
| `params.json` | the constants both pages load | — | copied from `../constants.json` |
