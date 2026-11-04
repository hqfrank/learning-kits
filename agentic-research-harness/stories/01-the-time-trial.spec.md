# Story 1 spec — The time trial

**Question (the learner's words):** If I let AI agents optimize my system all day, how do I know a
faster number they report is real, and not a shortcut, a lucky run or a story they told each other?

**Headline:** A faster lap counts only if a sealed judge times it, the decoy cars get caught, every
claim cites its timing slip, and the new car beats the champion on every lap.
(Engineer view: a faster result counts only if a frozen evaluator measures it, its negative controls
fail, every number cites an evidence record, and the candidate's whole range beats the champion's.)
Hedges follow A0 and B7: the method makes results checkable; the rule is conservative by design and
pays in power.

**Hero picture:** a race course seen from the side. Left: a workshop where two builders modify cars.
Centre: a timing hut with a wax-sealed rulebook, checkpoint gates on the course, and a sealed envelope
(the secret course). One honest car laps the whole course; a decoy car cuts the chicane and a marshal's
flag catches it. Right: a timing slip prints a run number, and a champion board shows two lap-time
ranges that do not overlap. A row of four tickets under the picture names the four safeguards with
their notes (B2, B3, B4, B7).

## Why this metaphor (the brief's idea, moved to a race)

The notes (A0) use a sealed-envelope contest, and the brief proposes it. It fits the judge, the
held-out papers, the decoys and the logbook. It does not fit three mechanisms the scenes rely on:
the metric is a **speed**, the evaluator takes **repeated samples** (20 timed calls or 20 seeds), and
the fastest way to a better number is to **do less work**. A time trial has all three built in: lap
times, many laps per car, and cutting the course. The race keeps every part of the contest (a sealed
rulebook, a secret course in a sealed envelope, decoy cars, a logbook with numbered slips) and adds
weather (measurement context, hence paired baselines) and the track's physical limit (the work
floor). B6's own analogy, a coach who rewrites the one-page notes after every match, joins the cast
unchanged.

I considered a bakery contest (correctness by tasting; no repeated samples) and an exam hall (no
speed). Neither carries "beat every lap".

## Cast

| Metaphor | Real term | Why it fits | Where it breaks |
|---|---|---|---|
| builders in the workshop | researcher agents | build a modified car, then hand it in | they build code, nobody drives; most "cut corners" are bugs, not cheats |
| a car with a plate "built from #n" | candidate (parent-linked, immutable) | one change per car; a timed car is never rebuilt | — |
| the coach with one-page notes | planner + slow memory (lessons file) | read-only; hands out drills; rewrites the notes each round, failed plays kept | — |
| the logbook of every run | fast memory (attempts log) | one line per timed run, never erased | — |
| the sealed timing hut | frozen evaluator (hash-pinned, human-owned) | builders may read the rules and complain, never change them; a broken seal and the hut refuses to time | the evaluator is a program, versioned and re-frozen |
| checkpoint gates with marshals | correctness gate, limits calibrated from legitimate runs | a car that misses a checkpoint is out, however fast | real limits are numeric distances, not physical gates |
| the closest call at any gate | binding ratio | how near the car came to the limit | — |
| the secret course in a sealed envelope | held-out inputs | builders never see it; tuning to the practice course must still generalize | — |
| decoy cars | negative controls | built to cut corners on purpose; they must lose | — |
| the timing slip with a run number | evidence record + run id | every claimed time cites a slip | — |
| the starter (one car on the course at a time) | evaluation worker + queue | serial, same conditions, applies the rule mechanically | it is harness code, not a person or an agent |
| today's weather | measurement context | the champion is re-timed today, not quoted from last week | in the simulator the "weather" is the seed list and the host |
| the track's physical limit | work floor | no car can lap faster | — |
| the team owner | the human owner | takes the decisions that change what counts | — |
| race classes | champion tracks | a different fuel races in its own class | — |

## Scenes

| # | Claim | Beat | Figure / motion (what moving means) | Interaction | Note | Numbers (key, class) |
|---|---|---|---|---|---|---|
| 1 | The quickest way to a faster lap is to cut the course | setup | scene player, 4 steps: honest car laps the full course (token = one lap); a builder's car cuts the chicane; the stopwatch alone cheers its time; a checkpoint flag catches it. Then "when the time is the target, cars learn to cut" (Goodhart) | step | A0 | `pub_goodhart_year`, `pub_strathern_year` public |
| 2 | The judge is sealed, its gates are set from honest laps, and it reports the closest call | therefore | scene player, 5 steps: sealed rulebook; a builder's edit breaks the seal → hut refuses; honest laps set the gate width; secret course; closest call over gates and courses (baseline 0.49 / 0.34 / 0.44 → 0.49) | step + predict (binding is the max, not the average) + live figure (two checks → binding → verdict) | B1, B2 | `topic_soft_miss_limit`, `topic_decision_time_limit_ms`, `harness_margin_cap_scheduling`, `sched_baseline` ill.; `story_binding_predict` ill. |
| 3 | A gate is tested from both sides: the honest car passes, every decoy loses | therefore / but (a decoy can be broken too) | scene player, 4 steps: baseline passes with room; `starve_soft` decoy caught; `wallclock` decoy slips through (clock parity bug); fixed, the order probe (run the course backwards) catches it. Flip cards: four decoys of the first campaign | step + flip | B3, C4 | `sched_baseline`, `sched_control_wallclock_ms`, `c1_control_scale_illustrative` ill.; `pub_popper_year` public |
| 4 | No slip, no claim; the coach keeps the failed plays | therefore | scene player, 5 steps: each timed run prints a slip; a claim without a slip is stamped "did not happen"; a builder's own stopwatch is a diagnostic; the logbook gets a line per run; the coach rewrites one page (≤ 70 lines) and keeps "X did not help" | step | B4, B6 | `harness_lessons_max_lines`, `topic_quick_seeds` ill. |
| 5 | One round: the coach plans, builders work in parallel, the starter times one car at a time in today's weather | therefore / but (the credit meter read zero) | scene player, 5 steps: coach hands out 2 drills; 2 builders in parallel; queue to one starter; champion re-timed today (10 % weather shift); caps: wall time and credits, and the credit meter that read 0 | step | B7, C4 | `topic_researchers_parallel`, `topic_tasks_per_round`, `topic_submissions_per_researcher`, `topic_researcher_wall_min`, `topic_researcher_credits`, `topic_planner_wall_min`, `topic_planner_credits`, `c1_host_shift_illustrative`, `sched_r1_submissions`, `sched_r1_wall_min` ill. |
| 6 | Crown a new champion only if every lap beats the old champion's best | therefore | predict (equal cars, median rule: how often crowned?), then live figure: 20 laps each, sliders for true gain and spread, two verdicts and their redraw rates | predict + live | B7 | `harness_timed_calls`, `topic_visible_seeds` ill.; `pub_median_null_probability`, `pub_disjoint_null_probability_20v20` public; `e1_metric_mean`, `e1_default_gain_pct`, `e1_default_spread_pct` assumption (explorer params) |
| 7 | Near the track's limit the rule cannot fire, and that is the owner's call | but (twist) | predict (better median and worst lap, crowned?), then gated scene player, 3 steps: round-1 range bars vs the paired baseline; the promoted car becomes the bar; the faster-median car still overlaps, both pressed against the 22.5 ms floor; a "decision needed" card for the owner | predict + step | C3, B8 | `sched_baseline`, `sched_r1_eft_placement`, `sched_r1_eft_metric_first`, `sched_r1_metric_reserve`, `sched_r1_eft_reserve`, `sched_work_floor_ms` ill. |
| 8 | Build the judge first, run by hand, automate last | ending | scene player, 5 steps: signposts light in order; the lap-time bar drops a lot in the hand-run phase and a little in the automated phase, for a modest spend | step | A1, C4 | `c1_baseline_ms_illustrative`, `c1_after_handrun_ms_illustrative`, `c1_handrun_days_illustrative`, `c1_handrun_sessions_illustrative`, `c1_after_auto_ms_illustrative`, `c1_auto_rounds_illustrative`, `c1_auto_spend_usd_illustrative` ill. |

Ending: "Your turn" cards to explorers 01 (range-based promotion), 02 (binding ratio and limits),
03 (placement under contention), 04 (cost of a campaign), the quiz (`../../quiz/`) and the notes.
Open question: which shortcut could your metric reward that no gate of yours would catch?

## Palette meaning (one hue = one concept, whole page)

- **sun** — the clock and lap times (the metric)
- **leaf** — honest / accepted / champion
- **coral** — a shortcut, a decoy, rejected
- **plum** — sealed: the rulebook seal, the secret course
- **sky** — the course and the inputs (the practice course, the slips' paper rows)
- **stone** — people (builders, coach, owner, starter)

## Where the metaphor breaks (footer)

1. Nobody drives. A "lap" is one timed call or one seed of a deterministic simulation; in the
   scheduling topic laps differ by workload seed, not by a driver.
2. Builders are not cheats. Most fast-but-wrong results are accidents (a bug that skips work), and
   decoys catch both.
3. A real race crowns the fastest lap. Here a single fast lap never counts; the whole range does.
4. The "weather" is the measurement context: the host, its boot and the evaluator version.
5. Gates are numeric limits (output distance, deadline misses, decision time), not posts on a course.

## Number rules

Every number is loaded verbatim from `../constants.json` or `../explorers/params.json` into the
`#params` block. Story-only picture values are `story_*` entries in `#params-story`, class
illustrative, with their scene as the source. Nothing is retyped in prose: captions use `{{key}}`
placeholders. The first campaign's results appear only as the kit's illustrative shape values (`c1_*`).
