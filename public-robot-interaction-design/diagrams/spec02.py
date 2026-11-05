# -*- coding: utf-8 -*-
# 02 — Beats and the dwell budget: beats -> dwell -> cycle -> visitors per hour; the responsiveness budget (note A2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="02-dwell-budget", w=W, h=0)

beats = [
    ("beat_greet_illustrative", "greet: look up, wave, one short line", VISIT),
    ("beat_reply_window_illustrative", "reply window: listening armed after the line ends", GATE),
    ("beat_converse_illustrative", "converse: a few turns (largest, most variable)", LLM),
    ("beat_offer_illustrative", "offer: self-serve gift, includes the take timer", BODY),
    ("beat_celebrate_illustrative", "celebrate", BODY),
    ("beat_goodbye_illustrative", "goodbye", VISIT),
]
typ = V("interaction_typical_illustrative")
reset = V("reset_turnover_illustrative")
cycle = V("cycle_illustrative")
assert sum(V(k) for k, _, _ in beats) == typ, "beats must sum to the typical interaction"
assert typ + reset == cycle
thr = V("throughput_theoretical_illustrative")
assert 3600 // cycle == thr
fric = V("queue_friction_factor_illustrative")
real = V("throughput_realistic_illustrative")
assert round(thr * fric) == real
day = V("show_day_illustrative")
visits = V("visits_per_day_illustrative")
assert real * day == visits
gate = V("consecutive_cycles_gate_illustrative")
cap = V("interaction_cap_illustrative")

BOXES = [title("Beats add up to a dwell time, dwell plus reset is the cycle, and the cycle sets visitors per hour: "
               "%s s %s + %s s %s = %s s %s -> %s per hour %s in theory, about %s %s in a real queue (illustrative budget)"
               % (typ, T("interaction_typical_illustrative"), reset, T("reset_turnover_illustrative"), cycle, T("cycle_illustrative"),
                  thr, T("throughput_theoretical_illustrative"), real, T("throughput_realistic_illustrative")), W, h=46)]
LINES = []

# --- A: the beats as a waterfall, to scale ------------------------------------------
X0, PX = 380, 5.6
Y0, RH = 108, 24
BOXES.append(text("a_h", 30, 72, 1220, 20,
                  "A. ONE VISIT AS TIMED BEATS, to scale (%s px per second). Each bar starts where the previous beat ends." % num(PX),
                  bold=True, font=12))
t = 0
rows = []
for i, (k, lab, pal) in enumerate(beats):
    rows.append((k, "%s: %s s %s" % (lab, num(V(k)), T(k)), t, V(k), pal, False))
    t += V(k)
rows.append(("reset_turnover_illustrative", "reset and turnover (pure overhead): %s s %s" % (reset, T("reset_turnover_illustrative")),
             t, reset, NOTE, True))
y = Y0
for k, lab, start, dur, pal, dashed in rows:
    BOXES.append(text("l_" + k, 30, y, X0 - 40, RH - 2, lab, font=10.5, valign="middle", align="right"))
    BOXES.append(box("b_" + k, int(X0 + start * PX), y + 3, max(2, int(dur * PX)), RH - 6, "", pal,
                     rounded=False, dashed=dashed))
    y += RH
# take timer inside offer
off_start = sum(V(k) for k, _, _ in beats[:3])
tt = V("take_timer_illustrative")
BOXES.append(text("l_take", 30, y, X0 - 40, RH - 2,
                  "inside the offer: no-take timer %s s %s" % (tt, T("take_timer_illustrative")),
                  font=10.5, valign="middle", align="right", fontcolor="#555555"))
BOXES.append(box("b_take", int(X0 + off_start * PX), y + 6, int(tt * PX), RH - 12, "", BODY, rounded=False, dashed=True))
y += RH
# per-turn cap inside converse
conv_start = sum(V(k) for k, _, _ in beats[:2])
ptc = V("per_turn_cap_illustrative")
BOXES.append(text("l_turn", 30, y, X0 - 40, RH - 2,
                  "inside converse: one visitor turn is capped at %s s %s" % (ptc, T("per_turn_cap_illustrative")),
                  font=10.5, valign="middle", align="right", fontcolor="#555555"))
BOXES.append(box("b_turn", int(X0 + conv_start * PX), y + 6, int(ptc * PX), RH - 12, "", LLM, rounded=False, dashed=True))
y += RH + 6
# bounds from zero
ina = V("inactivity_timeout_illustrative")
bounds = [
    ("typ", "typical interaction = sum of the six beats: %s s %s [calc]" % (typ, T("interaction_typical_illustrative")), typ, VISIT, False),
    ("cyc", "cycle = interaction + reset: %s s %s [calc]" % (cycle, T("cycle_illustrative")), cycle, GREY, False),
    ("ina", "global inactivity timeout (any beat -> goodbye): %s s %s" % (ina, T("inactivity_timeout_illustrative")), ina, GATE, True),
    ("cap", "'chatty visitor' cap and session-lease maximum: %s s %s" % (cap, T("interaction_cap_illustrative")), cap, BAD, True),
]
for id_, lab, dur, pal, dashed in bounds:
    BOXES.append(text("l_" + id_, 30, y, X0 - 40, RH - 2, lab, font=10.5, valign="middle", align="right",
                      bold=(id_ in ("typ", "cyc"))))
    BOXES.append(box("b_" + id_, X0, y + 3, int(dur * PX), RH - 6, "", pal, rounded=False, dashed=dashed))
    y += RH
yax = y + 4
LINES.append(dict(x1=X0, y1=Y0 - 4, x2=X0, y2=yax, color="#333333", sw=1.2))
LINES.append(dict(x1=X0, y1=yax, x2=X0 + cap * PX, y2=yax, color="#333333", sw=1.2))
for s in range(0, cap + 1, 25):
    LINES.append(dict(x1=X0 + s * PX, y1=yax, x2=X0 + s * PX, y2=yax + 5, color="#333333", sw=1.2))
    BOXES.append(text("tk%d" % s, X0 + s * PX - 20, yax + 6, 40, 16, "%d s" % s, font=10, align="center"))
for s, c in ((typ, BLUE_C), (cycle, GREY_C)):
    LINES.append(dict(x1=X0 + s * PX, y1=Y0 - 4, x2=X0 + s * PX, y2=yax, color=c, dashed=True, sw=1.2))
BOXES.append(box("note_a", int(X0 + cycle * PX) + 30, Y0, int(1250 - X0 - cycle * PX - 30), 96,
                 "Timeouts are failsafes set ABOVE the intended length, not targets.\n\n"
                 "The greet line is short on purpose: the reply window opens only when it ends, so a longer greeting delays the visitor's natural reply.",
                 NOTE, font=10.5, align="left", valign="top"))

# --- B: from cycle to the show day ----------------------------------------------------
yb = yax + 34
BOXES.append(text("b_h", 30, yb, 1220, 20,
                  "B. THE ARITHMETIC RUNS BOTH WAYS: the cycle sets the queue, and the queue sets how long any beat may be.",
                  bold=True, font=12))
yb += 26
chain = [
    ("c1", "cycle\n%s s %s" % (cycle, T("cycle_illustrative")), GREY),
    ("c2", "3600 s / cycle\n= %s visitors per hour %s [calc]" % (thr, T("throughput_theoretical_illustrative")), VISIT),
    ("c3", "x queue friction %s %s\n= about %s per hour %s [calc]" % (num(fric), T("queue_friction_factor_illustrative"),
                                                                       real, T("throughput_realistic_illustrative")), VISIT),
    ("c4", "x show day %s h %s\n= about %s visits per day %s [calc]" % (day, T("show_day_illustrative"),
                                                                        visits, T("visits_per_day_illustrative")), VISIT),
    ("c5", "feeds other gates: endurance gate %s cycles without intervention %s; gift tray and refill cadence must keep up"
     % (gate, T("consecutive_cycles_gate_illustrative")), GATE),
]
cx = 30
cw = [150, 200, 250, 250, 300]
EDGES = []
for i, (id_, lab, pal) in enumerate(chain):
    BOXES.append(box(id_, cx, yb, cw[i], 58, lab, pal, font=10.5, bold=(i < 4)))
    if i:
        EDGES.append(dict(src=chain[i - 1][0], dst=id_, sx=1, sy=0.5, dx=0, dy=0.5, color=BLUE_C))
    cx += cw[i] + 17
yb += 58 + 10
BOXES.append(text("b_note", 30, yb, 1220, 36,
                  "Throughput is 3600 divided by the CYCLE, not by the dwell: the reset counts. Need more visitors per hour? "
                  "Cap the converse beat (largest, most variable) or shorten the reset; every second removed from the reset returns to visitors. "
                  "Report the dwell distribution (median and a high percentile), not only the mean: the cap exists for the tail.",
                  font=10.5))

# --- C: the responsiveness budget, in milliseconds --------------------------------------
yc = yb + 50
BOXES.append(text("c_h", 30, yc, 1220, 20,
                  "C. THE RESPONSIVENESS BUDGET: from the visitor's consent action to a VISIBLE listening signal, every stage named (to scale, ms).",
                  bold=True, font=12))
MX0, MPX = 380, 0.82
lim = V("response_limit_flow") * 1000
det = V("listening_indicator_detect_illustrative")
sig = V("listening_indicator_signal_illustrative")
bud = V("listening_indicator_budget_illustrative")
assert det + sig == bud and bud < lim
ry = yc + 66
BOXES.append(text("l_det", 30, ry, MX0 - 40, 28,
                  "budget %s ms %s = detection %s ms %s + permit, audio gate, indicator %s ms %s"
                  % (bud, T("listening_indicator_budget_illustrative"), det, T("listening_indicator_detect_illustrative"),
                     sig, T("listening_indicator_signal_illustrative")),
                  font=10.5, align="right", valign="middle"))
BOXES.append(box("m_det", MX0, ry + 4, int(det * MPX), 22, "detect", GATE, rounded=False, font=10))
BOXES.append(box("m_sig", MX0 + int(det * MPX), ry + 4, int(sig * MPX), 22, "permit + gate + light", BODY, rounded=False, font=10))
may = ry + 40
LINES.append(dict(x1=MX0, y1=ry - 4, x2=MX0, y2=may, color="#333333", sw=1.2))
LINES.append(dict(x1=MX0, y1=may, x2=MX0 + 1050 * MPX, y2=may, color="#333333", sw=1.2))
for s in range(0, 1001, 200):
    LINES.append(dict(x1=MX0 + s * MPX, y1=may, x2=MX0 + s * MPX, y2=may + 5, color="#333333", sw=1.2))
    BOXES.append(text("mt%d" % s, MX0 + s * MPX - 30, may + 6, 60, 16, "%d ms" % s, font=10, align="center"))
refs = [
    (V("response_limit_instant") * 1000, "%s s feels instant %s" % (num(V("response_limit_instant")), T("response_limit_instant")), GREY_C, -36),
    (V("turn_gap_typical"), "typical human turn gap %s ms %s" % (V("turn_gap_typical"), T("turn_gap_typical")), PURPLE_C, -20),
    (lim, "%s s flow-of-thought limit %s" % (num(V("response_limit_flow")), T("response_limit_flow")), RED_C, -20),
]
for i, (ms, lab, c, dy) in enumerate(refs):
    x = MX0 + ms * MPX
    LINES.append(dict(x1=x, y1=ry + dy + 14, x2=x, y2=may, color=c, dashed=True, sw=1.4))
    if i == 2:
        BOXES.append(text("rf%d" % int(ms), x - 234, ry + dy, 230, 16, lab, font=10, fontcolor=c, align="right"))
    else:
        BOXES.append(text("rf%d" % int(ms), x + 4, ry + dy, 230, 16, lab, font=10, fontcolor=c))
BOXES.append(text("c_note", MX0 + 520 * MPX, ry + 2, 1000 * MPX - 530 * MPX, 30,
                  "The robot need not match humans, but each stage is measured on the real robot and network.",
                  font=10, fontcolor="#444444"))

ylg = may + 35
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: solid bars = planned beat lengths | dashed bars = timers and caps (failsafes) | dashed vertical lines = totals (A) or public reference limits (C). "
                 "All robot durations are illustrative design values, not measurements.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/A2-beats-and-dwell-budget.md (budget table, from beats to throughput, short beats that start early, the responsiveness budget, "
    "'throughput is 3600 divided by the cycle'); C2 for the endurance gate. "
    "[calc]: %s = sum of six beats; %s + %s = %s s; 3600 / %s = %s per hour; %s x %s = %s (rounded); %s x %s h = %s visits; %s + %s = %s ms."
    % (typ, typ, reset, cycle, cycle, thr, thr, num(fric), real, real, day, visits, det, sig, bud)],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
