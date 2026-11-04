# -*- coding: utf-8 -*-
# 01 — The order of construction: automation last (notes A1, C5).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="01-order-of-construction", w=W, h=0)

b0 = V("c1_baseline_ms_illustrative"); t_b0 = T("c1_baseline_ms_illustrative")
b1 = V("c1_after_handrun_ms_illustrative"); t_b1 = T("c1_after_handrun_ms_illustrative")
b2 = V("c1_after_auto_ms_illustrative"); t_b2 = T("c1_after_auto_ms_illustrative")
days = V("c1_handrun_days_illustrative"); t_days = T("c1_handrun_days_illustrative")
sess = V("c1_handrun_sessions_illustrative"); t_sess = T("c1_handrun_sessions_illustrative")
rounds = V("c1_auto_rounds_illustrative"); t_rounds = T("c1_auto_rounds_illustrative")
usd = V("c1_auto_spend_usd_illustrative"); t_usd = T("c1_auto_spend_usd_illustrative")
hand_pct = round(100.0 * (b0 - b1) / b0)          # my arithmetic
auto_pct = round(100.0 * (b1 - b2) / b1)          # my arithmetic

BOXES = [title("Automate last: by hand the policy call fell %s -> %s ms %s%s; the automated loop then found a further %d %% [calc] cheaply (all illustrative)"
               % (b0, b1, t_b0, t_b1, auto_pct), W, h=40)]

# phase bands
phases = [("CALIBRATE", 0, 3, HUMAN), ("HAND-RUN", 3, 6, AGENT), ("AUTOMATE", 6, 7, JUDGE)]
steps = [
    ("1  REFERENCE + BASELINE", "port, make it run, benchmark on frozen inputs on several devices (B1)", DATA),
    ("2  PROPOSAL", "one page: what is optimized, what 'equivalent' means, who owns the evaluator (B8)", HUMAN),
    ("3  FROZEN EVALUATOR + CONTROLS", "build the judge; baseline must pass, cheats must fail (B2, B3)", JUDGE),
    ("4  RESEARCH BY HAND", "a coordinating agent gives one bounded question per researcher session; a human watches every round", AGENT),
    ("5  EVALUATOR HARDENING", "each new check answers a failure seen the day before", JUDGE),
    ("6  FIRST REPORT", "rebuilt from the evidence records (B4, B8)", DATA),
    ("7  AUTOMATED LOOP", "planner, parallel researchers, queue, promotion policy, memory, cost meter (B7)", AGENT),
]
X0, SW, GAP, Y = 30, 160, 15, 128
for name, a, b, pal in phases:
    x = X0 + a * (SW + GAP)
    w = (b - a) * (SW + GAP) - GAP
    BOXES.append(box("ph_" + name, x, 72, w, 40, name, pal, bold=True, font=13, fill="none", dashed=True, sw=2))
for i, (h, d, pal) in enumerate(steps):
    BOXES.append(box("s%d" % i, X0 + i * (SW + GAP), Y, SW, 100, h + "\n\n" + d, pal, font=11, valign="top"))

# exit criteria under each phase (note A1 table)
crit = [
    (0, 3, "EXIT: the baseline passes every input set with margin clearly below 1, and every negative control is rejected"),
    (3, 6, "EXIT: the evaluator has survived several rounds of real candidates; the lessons file 'writes itself'"),
    (6, 7, "START: small caps, few parallel researchers, cost metered from round one"),
]
for a, b, t in crit:
    x = X0 + a * (SW + GAP)
    w = (b - a) * (SW + GAP) - GAP
    BOXES.append(box("ex%d" % a, x, 240, w, 50, t, WHITE, font=11, align="left"))

# why the order (three dependency callouts)
why = [
    ("w1", 30, "WHY 1 BEFORE 3\nA correctness gate compares the candidate with a trusted output. No reference -> nothing to compare -> the first fast-but-wrong result is accepted."),
    ("w2", 440, "WHY BASELINE BEFORE CANDIDATES\nIn the first campaign the first gate wrongly REJECTED the real baseline. It was found the day the evaluator was built, because the baseline ran before any candidate."),
    ("w3", 850, "WHY 4 BEFORE 7\nThe hand-run rounds showed which prompts, rules and checks the agents need. The loop then encodes a process that already works; automating earlier automates the wrong prompts."),
]
for id_, x, t in why:
    BOXES.append(box(id_, x, 306, 400, 70, t, NOTE, font=11, align="left", valign="top"))

# shape of the first campaign: bars to scale (px per ms)
PX = 2.2
YB = 426
BOXES.append(text("shape_h", 30, 394, 1220, 24,
                  "THE SHAPE OF THE FIRST CAMPAIGN (illustrative values that keep the shape, not the campaign's values). Bar length is to scale: latency of one policy call.",
                  bold=True, font=12))
bars = [
    ("bar0", "start: %s ms %s" % (b0, t_b0), b0, BAD, ""),
    ("bar1", "after hand-run rounds: %s ms %s" % (b1, t_b1), b1, AGENT,
     "-%d %% [calc] in %s days %s, about %s researcher sessions %s: people steering agents found the big gains" % (hand_pct, days, t_days, sess, t_sess)),
    ("bar2", "after automated loop: %s ms %s" % (b2, t_b2), b2, JUDGE,
     "a further -%d %% [calc] in %s rounds %s for about %s USD of model usage %s: the loop found smaller, harder gains cheaply" % (auto_pct, rounds, t_rounds, usd, t_usd)),
]
for i, (id_, lab, v, pal, note) in enumerate(bars):
    y = YB + i * 46
    BOXES.append(box(id_, 30, y, int(v * PX), 34, "", pal, rounded=False))
    BOXES.append(text(id_ + "_l", 30 + int(v * PX) + 10, y, 300, 34, lab, valign="middle", bold=True, font=12))
    if note:
        BOXES.append(text(id_ + "_n", 560, y, 690, 34, note, valign="middle", font=11))

BOXES.append(box("legend", 30, 572, 1220, 40,
                 "Legend:  dashed frames = phases (note A1 table)  |  purple = human-owned  |  amber = the judge  |  green = agent work  |  blue = records / data  |  "
                 "grey = why the order matters  |  bars: red = start, green = after hand-run, amber = after automation. Steps run left to right; each needs the one before it.",
                 WHITE, align="left", font=11))

EDGES = [dict(src="s%d" % i, dst="s%d" % (i + 1), color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5) for i in range(6)]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/A1-the-order-of-construction.md (seven steps, three dependencies, phase table, illustrative campaign shape); notes/C5-the-checklist.md; B1-B4, B7, B8 for each step. "
    "[calc]: -%d %% = (%s - %s) / %s; -%d %% = (%s - %s) / %s." % (hand_pct, b0, b1, b0, auto_pct, b1, b2, b1)],
    30, 626, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
