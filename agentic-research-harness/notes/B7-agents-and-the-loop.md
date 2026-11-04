# B7 — Agents and the loop

**Source:** generalised from internal methodology notes, 2026 (§3.6); the harness supervisor (`supervisor.py`), evaluation queue (`evalq.py`), planner and researcher prompts; the demonstration topic's `topic.json` and worklog. Probabilities are my arithmetic (`pub_disjoint_null_probability_20v20`, `pub_median_null_probability`). · **Status:** concept note.

## In one sentence
Each round a read-only planner assigns a few bounded tasks, researchers work on them in parallel and submit through a queue, an evaluation worker runs the frozen evaluator with a paired baseline and a re-measured champion, and a mechanical rule promotes a candidate only when its whole range of samples beats the champion's whole range.

## What it is
The **loop** is the automated part of the method: plan → research in parallel → evaluate → remember → plan again. Roles are separated by what they may touch.

| Role | Does | May not |
|---|---|---|
| **Planner** | Rewrites the lessons; assigns N independent tasks | Modify files; run evaluations; read held-out inputs |
| **Researcher** (×N, in parallel) | Builds candidates, writes diagnostics, appends to the worklog, submits | Edit the evaluator, an existing candidate, or the topic config; read held-out inputs |
| **Evaluation worker** (harness code, not an agent) | Runs official evaluations one at a time; applies the promotion policy; writes memory | — |
| **Coordinator** (human-facing agent) | Commits, writes the weekly report, asks the human the decisions the policy cannot take | Promote by judgement |

A **task** from the planner has: an id, a one-line title, a parent candidate, a hypothesis with numbers from the memory, `harness_plan_steps` = 3–6 concrete steps, and a measurable success criterion. It is sized for about `harness_task_hours` = 1 hour of one researcher (design parameters, illustrative). The planner is told to make tasks independent (different mechanisms, different files), to diversify between refining the champion and exploring, and not to reassign a failed direction without a new idea.

## How it works
**The queue.** A researcher calls `submit candidates/<id>`. The request goes into a queue and the call blocks until the worker has finished. The worker serializes all official runs, so two timed runs never share a device.

**Paired baseline.** Before evaluating a submission, the worker makes sure a baseline record exists in the same measurement context and is younger than a maximum age (`topic_baseline_max_age_min` = 1440 min in the scheduling topic, because its simulator is deterministic; illustrative). If not, it runs the baseline first. Comparisons stay inside one context. This is **blocking** in the sense of experimental design: compare within a block where the shared noise is the same. In the first campaign, absolute latency shifted by an illustrative `c1_host_shift_illustrative` = 10 % between two hosts of the same type; an unpaired comparison would have swamped real gains.

**Champion re-measurement.** If the track's champion has no record in the current context, the worker re-measures it before comparing.

**The promotion policy** is mechanical. A candidate becomes champion of a track only if:

1. its verdict is ACCEPTED;
2. its binding ratio is at most the margin cap (else "accepted, low margin");
3. its whole range of repeated samples beats the champion's whole range, measured in the same context: for a lower-is-better metric, the candidate's worst sample is better than the champion's best sample.

In the first campaign the samples were `harness_timed_calls` = 20 timed calls; in the scheduling topic they are `topic_visible_seeds` = 20 seeds (design parameters, illustrative).

**Why disjoint ranges, not medians.** Suppose a candidate is no better than the champion, and both give 20 samples from the same distribution. Then the candidate's median is lower with probability `pub_median_null_probability` = 0.5: a median rule promotes a no-change candidate half the time. The disjoint-range rule promotes it with probability `pub_disjoint_null_probability_20v20` ≈ 7.3 × 10⁻¹² (my arithmetic: 1 / C(40, 20); assumes independent samples). The price is power: a real gain smaller than the spread of the samples is never promoted. The first campaign's researchers flagged a small real gain that the rule blocked because one slow first call widened the candidate's range; the scheduling topic hit the rule at the work floor (see [[C3-calibration]]). The rule is conservative by design; changing it is a human decision.

**Caps and cost.** Each agent has a wall-time cap and a credit cap (in the scheduling topic `topic_researcher_wall_min` = 60 min and `topic_researcher_credits` = 300 credits per researcher; `topic_planner_wall_min` = 30 min and `topic_planner_credits` = 100 credits for the planner; illustrative). The agent is told its cap, so it writes its report before it is killed. Every tool call and credit is recorded. Cost per accepted improvement is a campaign metric. A campaign-level budget pauses the loop when reached.

**Machine-readable endings.** Each prompt ends with a required JSON block: the planner returns the new lessons and the tasks; a researcher returns a report (status, submitted ids, best run id, summary, lessons, next ideas). The supervisor parses the block and does not need to read prose.

## How it is used in a campaign
In the scheduling topic's first automated round, `topic_researchers_parallel` = 2 researchers ran `topic_tasks_per_round` = 2 tasks with up to `topic_submissions_per_researcher` = 4 submissions each; the round made `sched_r1_submissions` = 4 submissions and took `sched_r1_wall_min` = 13 min of wall time (demonstration run of the local scheduling simulator; illustrative). See [[C3-calibration]].

## Common confusions
- **"The planner should evaluate too."** A planner that runs evaluations can tune toward the visible set. Read-only planning keeps planning and measuring apart.
- **"An agent can decide a near-tie."** The policy decides. An agent may argue in its report that the policy blocked a real gain; the coordinator raises it with a human.
- **"A credit cap bounds cost."** Only if credits are metered. In the scheduling topic's first round the agent tool emitted no usage events, so credits read 0 and the credit cap was inert; only the wall-time cap bounded the agents (source: demonstration topic worklog, harness observations). Check the meter in round one.

## Why it matters
Parallel agents produce candidates faster than a human can review them. A separation of roles, a single serialized judge, paired comparisons and a mechanical, conservative promotion rule let the loop run unattended without promoting noise.

## Terms introduced
- **loop** — plan → research in parallel → evaluate → remember, repeated per round.
- **round** — one planner session followed by its researcher sessions.
- **planner** — the read-only agent that rewrites the lessons and assigns tasks.
- **researcher** — an agent that answers one task by building and submitting candidates.
- **evaluation worker** — the harness component that runs official evaluations and applies the promotion policy.
- **coordinator** — the human-facing agent that commits, reports and raises decisions.
- **task** — one bounded question with parent, hypothesis, steps and success criterion.
- **evaluation queue** — the serialized list of submitted candidates awaiting official evaluation.
- **paired baseline** — a baseline record from the same measurement context as the candidate.
- **measurement context** — the environment id (host, boot, evaluator id) inside which comparisons are valid.
- **blocking** — comparing conditions within a block that shares its noise.
- **promotion policy** — the mechanical rule that makes a candidate champion.
- **disjoint-range rule** — promotion only if the candidate's whole sample range beats the champion's.
- **cost per accepted improvement** — total spend divided by the number of promotions.
