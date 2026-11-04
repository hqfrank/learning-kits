# -*- coding: utf-8 -*-
# 02 — The frozen evaluator and its binding ratio (notes B2, C2, C3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="02-frozen-evaluator-binding-ratio", w=W, h=0)

cap = V("harness_margin_cap_scheduling"); t_cap = T("harness_margin_cap_scheduling")
cap1 = V("harness_margin_cap_first_campaign"); t_cap1 = T("harness_margin_cap_first_campaign")
seeds = V("topic_visible_seeds"); t_seeds = T("topic_visible_seeds")
hz = V("topic_horizon_s"); t_hz = T("topic_horizon_s")
hseeds = V("topic_heldout_seeds"); t_hseeds = T("topic_heldout_seeds")
ha = V("sched_heldout_a"); t_ha = T("sched_heldout_a")
hb = V("sched_heldout_b_grasp_ms"); t_hb = T("sched_heldout_b_grasp_ms")
soft = V("topic_soft_miss_limit"); t_soft = T("topic_soft_miss_limit")
dec = V("topic_decision_time_limit_ms"); t_dec = T("topic_decision_time_limit_ms")

BOXES = [title("The evaluator reports how close a candidate came to failing: binding ratio = largest measured / limit; "
               "below 1 passes, promotion needs at most %s %s" % (cap, t_cap), W, h=40)]

BOXES += [
    box("cand", 31, 121, 150, 100, "CANDIDATE\ncandidates/<id>/\none idea, parent-linked, never modified (B5)", DATA, font=11),
    box("verify", 210, 120, 160, 100, "VERIFY\nfrozen tree hash = manifest?\nif not: refuse to evaluate\n(human-owned, versioned)", JUDGE, font=11),
    box("vis", 405, 70, 210, 60, "VISIBLE set\n%s seeds %s x %s s %s; agents may read it" % (seeds, t_seeds, hz, t_hz), DATA, font=11),
    box("hoa", 405, 140, 210, 60, "HELD-OUT a: %s cores, perception %s Hz %s; %s seeds %s" % (ha["cpu_cores"], ha["perception_hz"], t_ha, hseeds, t_hseeds), BAD, font=11, fill="#fff7f7"),
    box("hob", 405, 210, 210, 60, "HELD-OUT b: another robot, %s ms GPU grasp planner %s, no DLA; %s seeds %s" % (hb, t_hb, hseeds, t_hseeds), BAD, font=11, fill="#fff7f7"),
    box("gate", 650, 70, 260, 200,
        "GATE, per input set (limit -> ratio)\n"
        "- every chain instance due completes\n"
        "- hard chains: 0 deadline misses; worst e2e / deadline\n"
        "- soft chains: misses <= %s %% %s; p99 e2e / deadline, miss ratio / limit\n"
        "- mean decision time < %s ms %s; time / limit\n"
        "- order probe: reversed seeds give identical results\n"
        "- only ready jobs, allowed resources" % (soft, t_soft, dec, t_dec), JUDGE, font=11, align="left", valign="top"),
    box("bind", 940, 100, 140, 140, "BINDING RATIO\n= the LARGEST measured / limit over every check and every input set\n(also called the margin)", JUDGE, font=11, bold=False),
    box("verd", 1110, 70, 140, 200, "VERDICT\nACCEPTED: all checks pass (binding below 1)\nREJECTED: a check fails\nINVALID: cannot count by design (e.g. a quick development run)\n\npromotable only if binding <= %s %s" % (cap, t_cap), JUDGE, font=10),
    box("integ", 30, 293, 1220, 64,
        "INTEGRITY CHECKS (each closes one way a fast result can be fake):  model ran exactly once per call (no skipping or caching)  |  fixed noise consumed exactly once  |  "
        "output came from the device (no silent host fall-back)  |  order probe (no carried state)  |  provenance hashes of every file read  |  candidate tree hash before = after the run",
        JUDGE, font=11, align="left", fill="#fff8ee"),
]
EDGES = [
    dict(src="cand", dst="verify", sx=1, sy=0.5, dx=0, dy=0.5, bold=True),
    dict(src="verify", dst="vis", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="verify", dst="hoa", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="verify", dst="hob", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="vis", dst="gate", sx=1, sy=0.5, dx=0, dy=0.2),
    dict(src="hoa", dst="gate", sx=1, sy=0.5, dx=0, dy=0.55),
    dict(src="hob", dst="gate", sx=1, sy=0.5, dx=0, dy=0.9),
    dict(src="gate", dst="bind", sx=1, sy=0.5, dx=0, dy=0.5, bold=True),
    dict(src="bind", dst="verd", sx=1, sy=0.5, dx=0, dy=0.5, bold=True),
]

# ---- binding-ratio chart: demonstration-run values on one scale ----
X0, PXU, YC = 440, 540, 396            # x of ratio 0, px per unit ratio, top of rows
def X(r): return X0 + r * PXU
rows = []
bl = V("sched_baseline"); t_bl = T("sched_baseline")
ed = V("sched_edf_gpu_first"); t_ed = T("sched_edf_gpu_first")
bl_max = max(bl["binding_visible"], bl["binding_a"], bl["binding_b"])   # my arithmetic
ed_max = max(ed["binding_visible"], ed["binding_a"], ed["binding_b"])   # my arithmetic
rows.append(("baseline (calibration) %s" % t_bl, bl_max, "accepted [calc]"))
rows.append(("EDF, same placement %s" % t_ed, ed_max, "accepted [calc]"))
for k, name, out in [("sched_r1_eft_placement", "R1 earliest-finish placement", "accepted"),
                     ("sched_r1_eft_metric_first", "R1 + perception-first dispatch", "promoted"),
                     ("sched_r1_eft_reserve", "R1 earliest-finish + reservation", "accepted, not promotable"),
                     ("sched_r1_metric_reserve", "R1 baseline placement + reservation", "accepted, not promotable")]:
    rows.append(("%s %s" % (name, T(k)), V(k, "binding"), out))

RH = 30
top = YC + 26
bot = top + len(rows) * RH
BOXES.append(text("ch_h", 30, YC - 14, 1220, 34,
                  "BINDING RATIOS OF THE DEMONSTRATION RUN on one scale (illustrative output of the local scheduling simulator, not a real platform). "
                  "Bars are to scale; zones are set by the margin cap and the pass limit.", bold=True, font=12))
# zones (behind the bars)
BOXES += [
    box("z_ok", int(X(0)), top, int(X(cap) - X(0)), bot - top, "", AGENT, rounded=False, fill="#f1f8ef", sw=0),
    box("z_low", int(X(cap)), top, int(X(1.0) - X(cap)), bot - top, "", JUDGE, rounded=False, fill="#fff3e0", sw=0),
    box("z_bad", int(X(1.0)), top, int(X(1.08) - X(1.0)), bot - top, "", BAD, rounded=False, fill="#fdecec", sw=0),
]
for i, (lab, r, out) in enumerate(rows):
    y = top + i * RH + 6
    BOXES.append(text("r%d_l" % i, 30, y - 3, 400, 24, "%s:  %s  %s" % (lab, r, out), align="right", valign="middle", font=11,
                      bold=(out == "promoted")))
    pal = AGENT if out == "promoted" else DATA
    BOXES.append(box("r%d_b" % i, int(X(0)), y, int(r * PXU), 18, "", pal, rounded=False, sw=1.5 if out != "promoted" else 2.5))
LINES = [
    dict(x1=X(0), y1=top, x2=X(0), y2=bot + 4, color="#333333"),
    dict(x1=X(0), y1=bot, x2=X(1.08), y2=bot, color="#333333"),
    dict(x1=X(cap1), y1=top, x2=X(cap1), y2=bot, color="#9673a6", dashed=True),
    dict(x1=X(cap), y1=top, x2=X(cap), y2=bot, color="#d79b00", sw=2),
    dict(x1=X(1.0), y1=top, x2=X(1.0), y2=bot, color="#b85450", sw=2),
]
for t in (0, 0.5):
    BOXES.append(text("tk%s" % t, int(X(t)) - 20, bot + 4, 40, 18, str(t), align="center", font=10))
BOXES += [
    text("tk_cap1", int(X(cap1)) - 124, bot + 4, 120, 32, "%s %s\nfirst-campaign cap" % (cap1, t_cap1), align="right", font=10, fontcolor="#9673a6"),
    text("tk_cap", int(X(cap)) - 4, bot + 4, 80, 32, "%s %s\ncap here" % (cap, t_cap), align="left", font=10, fontcolor="#d79b00", bold=True),
    text("tk_one", int(X(1.0)) + 4, bot + 4, 150, 32, "1.0 = a limit reached\n-> REJECTED", align="left", font=10, fontcolor="#b85450", bold=True),
    text("zl_ok", int(X(0)) + 4, bot + 40, int(X(cap) - X(0)), 18, "promotable zone (if the range rule also holds, diagram 04)", font=10, fontcolor="#4d7a3d"),
]
BOXES.append(box("why", 1070, top - 4, 180, bot - top + 2,
                 "WHY A MARGIN AND NOT JUST A PASS\nA pass close to 1 means the next small change breaks it, or the candidate exploits the edge of a limit: such a run is 'accepted, low margin' and never promoted.\n"
                 "Limits come from legitimate runs (B1), not a guess: a limit tighter than legitimate noise rejects correct work.",
                 NOTE, font=10, align="left", valign="top"))

yl = bot + 66
BOXES.append(box("legend", 30, yl, 1220, 40,
                 "Legend:  amber = the frozen judge  |  blue = inputs agents may read / candidate files  |  pale red = held-out inputs agents never read  |  "
                 "chart: bar = binding ratio (green, thick = promoted); purple dashed = first-campaign cap; amber = cap in the scheduling topic; red = pass limit 1.0",
                 WHITE, align="left", font=11))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B2-the-frozen-evaluator.md (frozen = human-owned, hash-pinned, versioned; four jobs; integrity table; verdicts); notes/C2-the-scheduling-topic.md (gate per input set, binding definition, held-out workloads); "
    "notes/C3-calibration.md (calibration and round-1 table). [calc]: baseline binding = max(visible %s, a %s, b %s); EDF binding = max(visible %s, a %s, b %s)." % (bl["binding_visible"], bl["binding_a"], bl["binding_b"], ed["binding_visible"], ed["binding_a"], ed["binding_b"]) + " The R1 rows use each record's single 'binding' value."],
    30, yl + 54, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 18
