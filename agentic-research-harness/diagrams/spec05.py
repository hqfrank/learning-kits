# -*- coding: utf-8 -*-
# 05 — Promotion by disjoint ranges, not medians (notes B7, C3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="05-promotion-by-disjoint-ranges", w=W, h=0)

pmed = V("pub_median_null_probability"); t_pmed = T("pub_median_null_probability")
pdis = V("pub_disjoint_null_probability_20v20"); t_pdis = T("pub_disjoint_null_probability_20v20")
seeds = V("topic_visible_seeds"); t_seeds = T("topic_visible_seeds")
calls = V("harness_timed_calls"); t_calls = T("harness_timed_calls")
floor = V("sched_work_floor_ms"); t_floor = T("sched_work_floor_ms")
cap = V("harness_margin_cap_scheduling"); t_cap = T("harness_margin_cap_scheduling")

BOXES = [title("A new champion must beat the old one on EVERY seed, not on average: a median rule promotes a no-change candidate with probability %s %s, the range rule with about %.1e %s"
               % (pmed, t_pmed, pdis, t_pdis), W, h=40)]

# rows (key, label, outcome)
rows = [("sched_baseline", "baseline (paired): champion before round 1", "champion before"),
        ("sched_edf_gpu_first", "calibration: EDF, same placement", "accepted; ranges overlap"),
        ("sched_r1_eft_placement", "R1: earliest-finish placement", "accepted; range overlaps the baseline's"),
        ("sched_r1_eft_metric_first", "R1: earliest-finish + perception-first", "PROMOTED"),
        ("sched_r1_metric_reserve", "R1: baseline placement + GPU reservation", "accepted; not promotable"),
        ("sched_r1_eft_reserve", "R1: earliest-finish + reservation", "accepted; not promotable")]

LO, HI = 20, 48
X0, X1 = 430, 1000
def X(ms): return X0 + (ms - LO) * (X1 - X0) / float(HI - LO)
TOP, RH = 116, 46
BOXES.append(text("ch_h", 30, 63, 1000, 44,
                  "Range of the per-seed p95 end-to-end latency of the perception chain (min to max over %s seeds %s; tick = median), lower is better. "
                  "Demonstration run of the local scheduling simulator: illustrative, not a real platform." % (seeds, t_seeds), bold=True, font=12))
LINES = []
vals = {}
for i, (k, lab, out) in enumerate(rows):
    v = V(k); tg = T(k); vals[k] = v
    y = TOP + i * RH
    prom = out == "PROMOTED"
    BOXES.append(text("l%d" % i, 30, y, 395, 34, "%s %s\nmedian %s (%s-%s) ms; %s" % (lab, tg, v["median"], v["min"], v["max"], out),
                      align="right", valign="middle", font=11, bold=prom))
    pal = AGENT if prom else (NOTE if k == "sched_baseline" else DATA)
    BOXES.append(box("b%d" % i, int(X(v["min"])), y + 9, max(3, int(X(v["max"]) - X(v["min"]))), 16, "", pal, rounded=False, sw=2.5 if prom else 1.5))
    LINES.append(dict(x1=X(v["median"]), y1=y + 4, x2=X(v["median"]), y2=y + 30, color="#333333", sw=2.5))
BOT = TOP + len(rows) * RH
bl = vals["sched_baseline"]; ch = vals["sched_r1_eft_metric_first"]; er = vals["sched_r1_eft_reserve"]
LINES += [
    dict(x1=X0, y1=BOT, x2=X1, y2=BOT, color="#333333"),
    dict(x1=X(bl["min"]), y1=TOP - 4, x2=X(bl["min"]), y2=BOT, color="#9673a6", dashed=True, sw=2),
    dict(x1=X(ch["min"]), y1=TOP - 4, x2=X(ch["min"]), y2=BOT, color="#82b366", dashed=True, sw=2),
    dict(x1=X(floor), y1=TOP - 4, x2=X(floor), y2=BOT, color="#b85450", sw=2),
]
for t in range(LO, HI + 1, 4):
    LINES.append(dict(x1=X(t), y1=BOT, x2=X(t), y2=BOT + 5, color="#333333"))
    BOXES.append(text("t%d" % t, int(X(t)) - 15, BOT + 6, 30, 16, str(t), align="center", font=10))
BOXES += [
    text("ax", X0, BOT + 22, X1 - X0, 16, "ms (scale is linear)", align="center", font=10),
    text("fl", int(X(floor)) - 150, BOT + 40, 148, 46, "work floor %s ms %s:\nno scheduler beats it" % (floor, t_floor), align="right", font=10, fontcolor="#b85450", bold=True),
    text("chb", int(X(ch["min"])) + 4, BOT + 40, 170, 46, "new champion's BEST seed %s ms: already near the floor plus jitter" % ch["min"], align="left", font=10, fontcolor="#4d7a3d", bold=True),
    text("blb", int(X(bl["min"])) + 4, BOT + 40, 240, 46, "baseline's BEST seed %s ms: the promoted candidate's WORST seed %s ms is below it" % (bl["min"], ch["max"]), align="left", font=10, fontcolor="#9673a6", bold=True),
]

# right panel: the rule and the arithmetic
BOXES += [
    box("rule", 1030, 62, 220, 140,
        "THE PROMOTION POLICY (mechanical)\n1. verdict ACCEPTED\n2. binding <= %s %s, else 'accepted, low margin'\n3. lower-is-better: the candidate's WORST sample beats the champion's BEST sample, same measurement context\n"
        "samples: %s seeds %s here; %s timed calls %s in the first campaign" % (cap, t_cap, seeds, t_seeds, calls, t_calls),
        JUDGE, font=10, align="left", valign="top"),
    box("null", 1030, 214, 220, 140,
        "WHY NOT MEDIANS\nIf the candidate is no better, both give 20 i.i.d. samples of one distribution:\n- median lower with probability %s %s\n- all 20 below all 20 with probability 1 / C(40, 20) = %.2e %s\n"
        "Price: power. A real gain smaller than the sample spread is never promoted." % (pmed, t_pmed, pdis, t_pdis),
        HUMAN, font=10, align="left", valign="top"),
]
BY = BOT + 98
BOXES += [
    box("floorcase", 30, BY, 1220, 62,
        "THE RULE MEETS THE FLOOR. Earliest-finish + reservation has a better median (%s vs %s ms) and a far better worst seed (%s vs %s ms) than the new champion, yet it cannot be promoted: its worst seed must beat %s ms, "
        "which sits %.1f ms [calc] above the %s ms floor. The researcher raised it as a decision (promote by median and maximum together, or by a paired per-seed comparison); the coordinator recorded it and did NOT change the rule: changing it is a human decision."
        % (er["median"], ch["median"], er["max"], ch["max"], ch["min"], ch["min"] - floor, floor),
        HUMAN, font=11, align="left", fill="#f7f0fa"),
    box("legend", 30, BY + 75, 1220, 40,
        "Legend:  bar = min-max range over seeds, black tick = median  |  green thick bar = promoted  |  grey = baseline champion  |  dashed purple = baseline's best seed  |  dashed green = new champion's best seed  |  red = work floor. "
        "Which champion each 'not promotable' row was compared with follows the round-1 table in note C3; the notes do not give the evaluation order.",
        WHITE, align="left", font=11),
]
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B7-agents-and-the-loop.md (promotion policy, disjoint-range rule, null probabilities, price in power); notes/C3-calibration.md (calibration result, round-1 table, 'the rule meets the floor'); notes/C2-the-scheduling-topic.md (metric). "
    "[calc]: %.1f = %s - %s." % (ch["min"] - floor, ch["min"], floor)],
    30, BY + 128, 1220)
BOXES.append(src_box)
EDGES = []
PAGE["h"] = bottom + 18
