# Diagrams — Running optimization research with AI agents (Rung 2, learn-diagram)

Six diagrams, one draw.io page each, exported to `.drawio` + `.svg` + `.png`. This is the picture
layer for the rung-1 notes: the order of construction (A1), the frozen evaluator and its binding ratio
(B2), negative controls (B3), the loop and its memories (B4, B6, B7), the promotion rule (B7, C3) and
calibration (C3). **Every number on every canvas is loaded from this kit's `constants.json` by key**
and tagged `[Pn]` (public: a cited paper, or my arithmetic on public mathematics) or `[In]`
(illustrative: a design parameter of the harness, a round value that keeps the shape of the first
campaign, or output of the demonstration scheduling simulator). Derived values are tagged `[calc]` with
the arithmetic in the canvas footnote. **No number on any canvas is a measurement of a real platform.**
Each canvas carries its own legend and a sources footnote (key = value unit, class, source) so the
exported image stands alone. `agentic-research-harness.drawio` is the combined 6-page document.

**Sources used:** only this kit's `notes/`, `glossary.md` and `constants.json`. No figure from any other
material was copied, traced or described; every diagram is drawn fresh from the mechanism in the notes.

**How these were built.** As in the sibling kits, each page is a list of cells in `specNN.py`,
rendered by `.render_local.py` into an editable `.drawio` and a self-rendered `.svg` (rect + XHTML
`foreignObject` labels, polyline edges, free reference lines), rasterised to `.png` with headless
Chrome at 2x. `_common.py` loads `../constants.json` (`V(key)`) and hands out the tags (`Tags()`), so
no number is typed into a spec. To regenerate: `python3 .render_local.py specNN.py`, then
`python3 .render_local.py --combine`.

| File | Teaches (the finding in the title) | Sources used |
|---|---|---|
| `01-order-of-construction` | Automate last: build reference and baseline, proposal, evaluator with controls, hand-run rounds, hardening, report, then the loop; in the illustrative shape of the first campaign, hand-run rounds took one call from 400 to 100 ms and automation found a further 12 % cheaply. | A1 (seven steps, phase table, three dependencies), C5; `c1_baseline_ms_illustrative`, `c1_after_handrun_ms_illustrative`, `c1_after_auto_ms_illustrative`, `c1_handrun_days_illustrative`, `c1_handrun_sessions_illustrative`, `c1_auto_rounds_illustrative`, `c1_auto_spend_usd_illustrative` |
| `02-frozen-evaluator-binding-ratio` | The evaluator reports how close a candidate came to failing: binding ratio = largest measured / limit over all checks and input sets; below 1 passes, promotion needs at most 0.9 (0.85 in the first campaign). Visible and held-out sets, gate, integrity checks, verdicts; the demonstration run's bindings on one scale. | B2, C2, C3; `harness_margin_cap_*`, `topic_visible_seeds`, `topic_horizon_s`, `topic_heldout_seeds`, `sched_heldout_a`, `sched_heldout_b_grasp_ms`, `topic_soft_miss_limit`, `topic_decision_time_limit_ms`, `sched_baseline`, `sched_edf_gpu_first`, `sched_r1_*` |
| `03-gate-tested-from-both-sides` | A gate is tested from both sides: the real baseline and legitimate-noise references must pass (not too tight), every negative control must fail (not too loose); a control can be wrong too; development vs evaluation host; Popper. | B3, B1, B2, C3, C4; `c1_control_scale_illustrative`, `sched_control_wallclock_ms`, `pub_popper_year`, `topic_quick_seeds`, `sched_baseline`, `harness_margin_cap_scheduling` |
| `04-one-round-of-the-loop` | One round: a read-only planner sets bounded tasks, researchers work in parallel and submit through a serialized queue, and only the harness's evaluation worker (paired baseline, champion re-measurement, frozen evaluator, promotion policy) judges and writes the fast memory, champions and evidence; the planner rewrites the slow memory; caps, the credit-meter caveat and why comparisons are paired. | B7, B6, B4, B8; `topic_*` round configuration and caps, `harness_plan_steps`, `harness_task_hours`, `harness_lessons_max_lines`, `sched_r1_submissions`, `sched_r1_wall_min`, `c1_host_shift_illustrative` |
| `05-promotion-by-disjoint-ranges` | A new champion must beat the old one on every seed: under no real difference a median rule promotes with probability 0.5, the disjoint-range rule with about 7.3e-12. Range bars of the calibration and round-1 candidates against the baseline's and the new champion's best seeds and the work floor; the near-floor case the rule blocks, left as a human decision. | B7, C3, C2; `pub_median_null_probability`, `pub_disjoint_null_probability_20v20`, `topic_visible_seeds`, `harness_timed_calls`, `sched_work_floor_ms`, `harness_margin_cap_scheduling`, `sched_baseline`, `sched_edf_gpu_first`, `sched_r1_*` |
| `06-calibration-something-to-find` | Calibration: on the first workload EDF came within 1.1 ms of the work floor (nothing to find), so the owner densified it until placement was the lever (GPU 91 %, DLA 0 % under the baseline; 65 % / 42 % after round 1); a fair baseline, not a strawman; GPU-greedy loses when a long job blocks the GPU (diagnostic). | C3, C2; `sched_cal1_*`, `sched_baseline*`, `sched_edf_gpu_first`, `sched_probe_least_laxity_ms`, `sched_r1_eft_metric_first`, `sched_work_floor_ms`, `sched_r1_gpu_util`, `sched_r1_dla_util`, `sched_alphabetical_perception_ms`, `sched_heldout_b_grasp_ms`, `sched_control_deadline_ms` |

## Per-diagram notes (as built)

- **01** Type: pipeline with phase bands, plus a to-scale bar trio. Left out: the proposal's contents (B8) and the checklist (C5). The 75 % and 12 % are my arithmetic on illustrative values.
- **02** Type: block flow plus a bar chart on one ratio scale. Baseline and EDF bars are the maximum of their three per-set bindings (my arithmetic); round-1 rows use each record's single binding. Left out: the plugin functions (C1).
- **03** Type: two-sided block diagram. The purpose of the second-core perturbation control is the notes' reading; the source names the control only.
- **04** Type: block / data-flow diagram. Left out: machine-readable prompt endings and the worklog (B4, B7 text).
- **05** Type: range chart (min-max over seeds, median tick) with reference lines. The notes do not give the order in which round-1 candidates were evaluated; the "not promotable" rows follow the round-1 table in C3, and the canvas says so.
- **06** Type: two side-by-side bar panels (latency to scale, utilization to scale). The first workload's DLA utilization is not in the notes and is not drawn. Least laxity and the held-out-b probe are diagnostics (dashed).

Colour semantics across pages: purple = human-owned / human decisions, amber = the frozen judge and its policy, green = agent work or the promoted / best candidate, blue = files, records, other candidates, red = rejections, controls and the work floor, grey = notes and baselines. Dashed outlines = diagnostics or phases, never only colour.
