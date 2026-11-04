# C1 — Instantiating a topic

**Source:** the reusable harness README (topic directory, evaluator plugin contract, commands); the demonstration topic's `topic.json`. Values are configuration of the demonstration topic (`topic_*` keys; illustrative). · **Status:** concept note.

## In one sentence
The harness is topic-independent: a new research question is one directory with a `topic.json` that names the metric, margin, tracks, baseline, roles and budgets, and an `evaluator.py` plugin with four functions — verify, context, run, summarize.

## What it is
The **harness** is the reusable machinery: campaign state on disk, the agent runner, the memory, the evaluation queue, the promotion policy, the round loop, a cost meter and a local read-only dashboard. A **topic** is everything specific to one research question. The harness never looks inside the evaluator; it only calls the plugin.

A topic directory holds:

| Path | What |
|---|---|
| `topic.json` | the configuration (below) |
| `evaluator.py` | the plugin (below) |
| `evaluator/` | the frozen evaluator proper, hash-pinned by the topic's freeze script |
| `AGENTS.md` | working rules for the agents, loaded because agents run in the topic directory |
| `prompts/` | the planner and researcher prompt templates |
| `seed_lessons.md` | the initial slow memory |
| `candidates/<id>/` and `candidates/controls/` | candidates and negative controls |
| `evidence/<run_id>/` | evidence records |
| `runs/<campaign>/` | harness state (not version-controlled) |

## How it works
**`topic.json`** declares, in data, everything the loop needs:

- `metric`: name, label, unit, direction (lower or higher is better);
- `margin`: label and the promotion cap (`harness_margin_cap_scheduling` = 0.9 in the scheduling topic; a design parameter, illustrative);
- `class_field` and `tracks`: which candidate field is the class, and which classes each track accepts;
- `baseline_candidate` and `baseline_max_age_min`;
- `promotion`: whether disjoint ranges are required, or a minimum relative gain;
- `roles`: the planner and researcher agent profiles, with credit and wall-time caps;
- `max_parallel_researchers`, `tasks_per_round`, `max_rounds`, `max_submissions_per_researcher`;
- cost: an illustrative `topic_usd_per_credit` = 0.04 USD per credit, an optional campaign budget, and an optional resource-cost plugin for cloud machines;
- `seed_champions`: which candidate starts as champion of each track.

**The evaluator plugin** has four required functions and three optional ones.

```python
def verify() -> list[str]                        # [] when the frozen evaluator is intact; else refuse to run
def context(log) -> str | None                   # measurement environment id; paired comparisons stay inside one
def run(candidate_dir, opts, log) -> dict | None # evaluate; return the evidence record
def summarize(record) -> dict                    # run_id, candidate, parent, verdict, reasons, metric,
                                                 # metric_min, metric_max, margin, context, evaluator, created_utc
# optional: describe(record) -> str, evaluator_id() -> str, list_records() -> list[dict]
```

`metric_min` and `metric_max` are the range over the repeated samples; the disjoint-range rule compares them ([[B7-agents-and-the-loop]]). `margin` is the binding ratio ([[B2-the-frozen-evaluator]]).

**Commands.** A human verifies the evaluator, evaluates the baseline and the controls directly (no queue, no promotion), prints a report, and then starts a named campaign in the background with a dashboard. Researchers call `submit` from inside the campaign. A stopped campaign restarted with the same name continues with the same champions, lessons, attempts and round counter. A fresh campaign seeds the lessons from `seed_lessons.md` and the champions from the newest ACCEPTED record of each `seed_champions` id.

## How it is used in a campaign
The evaluator can be anything: a local simulator, a remote device, a benchmark farm. The harness needs only the plugin. The demonstration topic's evaluator is a discrete-event simulator that runs in about `sched_eval_seconds` = 1 s per candidate (demonstration run of the local scheduling simulator; illustrative), so a whole campaign runs on one workstation ([[C2-the-scheduling-topic]]). The first campaign's evaluator ran on a remote accelerator host.

The harness ships with its own tests that use a fake agent and a fake evaluator, so its loop and promotion policy are tested without any network, agent or device.

## Common confusions
- **"The harness knows the metric."** It knows only the metric's name, unit, direction, and the range in each record. Everything else is the plugin's business.
- **"`context` is cosmetic."** It defines where a paired comparison is valid. A plugin that returns the same context for two different hosts makes paired baselines meaningless.
- **"Humans submit through the queue too."** Humans evaluate directly to calibrate. Only agents in a campaign submit, and only submissions can be promoted.

## Why it matters
Separating the harness from the topic means the hard parts — the queue, the pairing, the promotion rule, the memory — are written and tested once. A new research question then costs one evaluator, one config and one set of rules, and inherits every safeguard.

## Terms introduced
- **harness** — the topic-independent machinery: state, agent runner, memory, queue, promotion, loop, cost, dashboard.
- **topic** — one research question's directory: config, evaluator, rules, prompts, seed lessons, candidates, evidence.
- **evaluator plugin** — the topic's `evaluator.py`, with `verify`, `context`, `run`, `summarize`.
- **seed champion** — the candidate that starts as champion of a track in a fresh campaign.
- **dashboard** — a local, read-only web view of the campaign files.
