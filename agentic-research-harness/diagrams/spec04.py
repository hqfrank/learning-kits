# -*- coding: utf-8 -*-
# 04 — One round of the loop: roles, the queue, the two memories (notes B7, B6, B4).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="04-one-round-of-the-loop", w=W, h=0)

ntask = V("topic_tasks_per_round"); t_ntask = T("topic_tasks_per_round")
nres = V("topic_researchers_parallel"); t_nres = T("topic_researchers_parallel")
nsub = V("topic_submissions_per_researcher"); t_nsub = T("topic_submissions_per_researcher")
steps = V("harness_plan_steps"); t_steps = T("harness_plan_steps")
hrs = V("harness_task_hours"); t_hrs = T("harness_task_hours")
age = V("topic_baseline_max_age_min"); t_age = T("topic_baseline_max_age_min")
lines = V("harness_lessons_max_lines"); t_lines = T("harness_lessons_max_lines")
pw = V("topic_planner_wall_min"); t_pw = T("topic_planner_wall_min")
pc = V("topic_planner_credits"); t_pc = T("topic_planner_credits")
rw = V("topic_researcher_wall_min"); t_rw = T("topic_researcher_wall_min")
rc = V("topic_researcher_credits"); t_rc = T("topic_researcher_credits")
r1s = V("sched_r1_submissions"); t_r1s = T("sched_r1_submissions")
r1w = V("sched_r1_wall_min"); t_r1w = T("sched_r1_wall_min")
shift = V("c1_host_shift_illustrative"); t_shift = T("c1_host_shift_illustrative")

BOXES = [title("One round: a read-only planner sets %s %s bounded tasks, %s %s researchers work in parallel, and only the harness's evaluation worker judges, promotes and writes memory"
               % (ntask, t_ntask, nres, t_nres), W, h=40)]

BOXES += [
    box("plan", 30, 80, 220, 140, "PLANNER (agent, read-only)\nreads champions + lessons + attempts digest; rewrites the lessons; assigns tasks.\nMay not: modify files, run evaluations, read held-out inputs", AGENT, font=11),
    box("tasks", 290, 80, 200, 140, "TASKS (x %s %s)\nid, title, parent candidate, hypothesis with numbers from memory, %s-%s steps %s, success criterion; about %s hour %s each; independent mechanisms" % (ntask, t_ntask, steps[0], steps[1], t_steps, hrs, t_hrs), NOTE, font=11),
    box("resA", 530, 70, 210, 76, "RESEARCHER A (agent)\nbuilds candidates, diagnostics, appends to the worklog; up to %s submissions %s" % (nsub, t_nsub), AGENT, font=11),
    box("resB", 530, 156, 210, 76, "RESEARCHER B (agent, in parallel)\nmay not edit the evaluator, an existing candidate, the topic config; may not read held-out", AGENT, font=11),
    box("queue", 780, 100, 140, 90, "EVALUATION QUEUE\nsubmit blocks until done; one official run at a time", JUDGE, font=11),
    box("work", 960, 64, 290, 176,
        "EVALUATION WORKER (harness code, not an agent)\n1. paired baseline in the same measurement context, younger than %s min %s; else run it first\n"
        "2. re-measure the track's champion if it has no record in this context\n3. run the frozen evaluator (diagram 02)\n4. apply the promotion policy (diagram 05)\n5. write the record and memory"
        % (age, t_age), JUDGE, font=11, align="left", valign="top"),
]
# memory row
MY = 300
BOXES += [
    box("lessons", 30, MY, 300, 86, "SLOW MEMORY: lessons.md\nshort (about %s lines %s), curated, every lesson cites a run id; rewritten by the planner each round; negative results KEPT ('X did not help (run id); do not repeat without a new idea')" % (lines, t_lines), DATA, font=11, align="left", valign="top"),
    box("attempts", 370, MY, 270, 86, "FAST MEMORY: attempts.jsonl\none row per official evaluation, append-only: candidate, parent, agent, verdict, metric, paired baseline, binding, note. Agents see a digest", DATA, font=11, align="left", valign="top"),
    box("champ", 680, MY, 250, 86, "champion.json\nper track: id, run id, metric, margin, since when, reason, previous champion. Written only by the promotion policy", DATA, font=11, align="left", valign="top"),
    box("evid", 970, MY, 280, 86, "evidence/<time>-<candidate>/\none directory per run: record, raw outputs, log. The directory name is the run id: 'cite or it did not happen' (B4)", DATA, font=11, align="left", valign="top"),
]
EDGES = [
    dict(src="plan", dst="tasks", sx=1, sy=0.5, dx=0, dy=0.5, bold=True),
    dict(src="tasks", dst="resA", sx=1, sy=0.4, dx=0, dy=0.5, bold=True),
    dict(src="tasks", dst="resB", sx=1, sy=0.6, dx=0, dy=0.5, bold=True),
    dict(src="resA", dst="queue", sx=1, sy=0.5, dx=0, dy=0.3, bold=True, label="submit", lpos=(760, 96), lw=50),
    dict(src="resB", dst="queue", sx=1, sy=0.5, dx=0, dy=0.7, bold=True),
    dict(src="queue", dst="work", sx=1, sy=0.5, dx=0, dy=0.47, bold=True),
    dict(src="work", dst="evid", sx=0.85, sy=1, dx=0.85, dy=0, color="#6c8ebf"),
    dict(src="work", dst="champ", sx=0.2, sy=1, dx=0.7, dy=0, color="#6c8ebf", points=[(1018, 270), (855, 270)]),
    dict(src="work", dst="attempts", sx=0.1, sy=1, dx=0.7, dy=0, color="#6c8ebf", points=[(989, 260), (559, 260)], label="write", lpos=(760, 260), lw=40),
    dict(src="attempts", dst="plan", sx=0.15, sy=0, dx=0.85, dy=1, color="#82b366", dashed=True, points=[(410, 240), (217, 240)], label="digest", lpos=(330, 240), lw=50),
    dict(src="plan", dst="lessons", sx=0.3, sy=1, dx=0.3, dy=0, color="#82b366", dashed=True, label="rewrite + read", lpos=(140, 262), lw=90),
]

# bottom: coordinator, human, caps
BY = 410
BOXES += [
    box("caps", 30, BY, 560, 100,
        "CAPS AND COST (each agent is told its cap, so it reports before it is killed)\n- planner: %s min %s, %s credits %s; each researcher: %s min %s, %s credits %s\n"
        "- every tool call and credit is recorded; cost per accepted improvement is a campaign metric; a campaign budget pauses the loop\n"
        "- check the meter in round one: in the demonstration round the agent tool emitted no usage events, so credits read 0 and only the wall-time cap bounded the agents"
        % (pw, t_pw, pc, t_pc, rw, t_rw, rc, t_rc), NOTE, font=11, align="left", valign="top"),
    box("coord", 620, BY, 300, 100, "COORDINATOR (human-facing agent)\ncommits, writes the weekly report from the records (B8), raises the decisions the policy cannot take. May not: promote by judgement", HUMAN, font=11),
    box("human", 960, BY, 290, 100, "HUMAN OWNER\nowns the evaluator and the promotion rule; decides e.g. whether a near-tie blocked by the rule should change the rule", HUMAN, font=11, bold=False),
    box("pair", 30, BY + 112, 1220, 44,
        "WHY PAIRED: compare within one measurement context (host, boot, evaluator id), as in blocking in experimental design. In the first campaign absolute latency shifted by %s %% %s between two hosts of the same type; "
        "an unpaired comparison would have swamped real gains. Demonstration round 1: %s submissions %s, %s min %s of wall time." % (shift, t_shift, r1s, t_r1s, r1w, t_r1w),
        JUDGE, font=11, align="left", fill="#fff8ee"),
    box("legend", 30, BY + 168, 1220, 26,
        "Legend:  green = agent sessions  |  amber = harness code that judges  |  blue = files (memory and records)  |  purple = human-facing  |  grey = caps  |  bold arrows = the work path; blue = writes; dashed green = what agents read",
        WHITE, align="left", font=11),
]
EDGES += [
    dict(src="coord", dst="human", sx=1, sy=0.5, dx=0, dy=0.5, color="#9673a6", bold=True, label="decisions, asks", lpos=(940, BY + 34), lw=100),
    dict(src="champ", dst="coord", sx=0.5, sy=1, dx=0.6, dy=0, color="#6c8ebf", dashed=True),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B7-agents-and-the-loop.md (roles table, task shape, queue, paired baseline, champion re-measurement, caps, credit-meter caveat, machine-readable endings); "
    "notes/B6-the-two-memories.md (attempts log, lessons file, champions); notes/B4-evidence-records.md (one directory per run, run id); notes/B8-reporting.md (coordinator, weekly report, decisions)."],
    30, BY + 208, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
