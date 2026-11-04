# -*- coding: utf-8 -*-
# 03 — Negative controls: a gate is tested from both sides (notes B3, B1, C3, C4).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="03-gate-tested-from-both-sides", w=W, h=0)

scale = V("c1_control_scale_illustrative"); t_scale = T("c1_control_scale_illustrative")
wc = V("sched_control_wallclock_ms"); t_wc = T("sched_control_wallclock_ms")
pop = V("pub_popper_year"); t_pop = T("pub_popper_year")
quick = V("topic_quick_seeds"); t_quick = T("topic_quick_seeds")
bl = V("sched_baseline"); t_bl = T("sched_baseline")
cap = V("harness_margin_cap_scheduling"); t_cap = T("harness_margin_cap_scheduling")

BOXES = [title("A gate is tested from both sides: the real baseline must PASS (the gate is not too tight) and every negative control must FAIL (the gate is not too loose)", W, h=40)]

# left: legitimate side
BOXES += [
    box("legit_h", 30, 70, 330, 34, "MUST BE ACCEPTED", AGENT, bold=True, font=13),
    box("bl", 30, 112, 330, 74, "THE REAL BASELINE\nscheduling topic: accepted at binding %s %s on the visible set, clearly below the cap %s %s" % (bl["binding_visible"], t_bl, cap, t_cap), AGENT, font=11),
    box("noise", 30, 196, 330, 74, "LEGITIMATE-NOISE REFERENCES\nlegitimate runs (e.g. reduced precision, another device) that set each limit, per input set (B1)", AGENT, font=11),
    box("tight", 30, 282, 330, 92, "IF ONE IS REJECTED: the gate is too tight.\nIn the first campaign the first gate rejected the real baseline; found the day the evaluator was built, because the baseline ran before any candidate.",
        BAD, font=11, fill="#fff7f7", align="left"),
]
# centre: the gate
BOXES += [
    box("gate", 450, 150, 380, 150,
        "THE FROZEN GATE (B2)\nis finished only when, on EVERY input set, held-out included:\n1. the baseline is ACCEPTED with margin clearly below 1\n2. every control is REJECTED\n\nre-run both on every evaluator version",
        JUDGE, font=12, bold=False),
]
# right: controls
BOXES += [
    box("ctrl_h", 920, 70, 330, 34, "MUST BE REJECTED (negative controls)", BAD, bold=True, font=13),
    box("c1", 920, 112, 330, 128,
        "FIRST CAMPAIGN (diffusion-model policy)\n"
        "- fewer denoising steps -> correctness gate vs reference\n"
        "- output scaled by %s %% %s -> calibrated per-dimension limits\n"
        "- cached output -> inputs change per call; 'model ran once'\n"
        "- perturbation on a second compute core -> correctness gate" % (scale, t_scale),
        BAD, font=11, align="left", valign="top", fill="#fff7f7"),
    box("c2", 920, 250, 330, 124,
        "SCHEDULING TOPIC\n"
        "- starve_soft: never runs soft chains -> completion check (logging, telemetry never finish)\n"
        "- not_ready: returns a job already started -> integrity check\n"
        "- wallclock: unseeded random tie-break -> order probe (REJECTED at %s ms %s)" % (wc, t_wc),
        BAD, font=11, align="left", valign="top", fill="#fff7f7"),
]
EDGES = [
    dict(src="bl", dst="gate", sx=1, sy=0.5, dx=0, dy=0.3, color="#82b366", bold=True, label="pass", lpos=(405, 165), lw=40),
    dict(src="noise", dst="gate", sx=1, sy=0.5, dx=0, dy=0.6, color="#82b366", bold=True, label="pass", lpos=(405, 225), lw=40),
    dict(src="c1", dst="gate", sx=0, sy=0.5, dx=1, dy=0.3, color="#b85450", bold=True, label="fail", lpos=(875, 180), lw=40),
    dict(src="c2", dst="gate", sx=0, sy=0.5, dx=1, dy=0.7, color="#b85450", bold=True, label="fail", lpos=(875, 270), lw=40),
]

# bottom: two lessons
BOXES += [
    box("wrong", 30, 400, 600, 92,
        "A CONTROL CAN BE WRONG TOO\nThe wallclock control first salted its tie-break with the parity of a nanosecond clock. On the development machine that clock had microsecond resolution, so the parity was always even: the control was accidentally deterministic and the order probe could not see it. "
        "Fix: an unseeded random generator. Rule: run each control and confirm it fails for the reason it was built for.",
        NOTE, font=11, align="left", valign="top"),
    box("hosts", 650, 400, 600, 92,
        "DEVELOPMENT HOST vs EVALUATION HOST\n- development host: visible set only; its records are INVALID by design (scheduling topic quick mode: %s seeds %s), so a development number is never taken for an official one\n"
        "- evaluation host: visible + held-out sets, official runs only\n- a device lock on each host keeps other work off the device during a timed run" % (quick, t_quick),
        DATA, font=11, align="left", valign="top"),
    box("popper", 30, 504, 1220, 44,
        "WHY: a claim is scientific only if some observation could refute it (Popper %s %s). A gate that has never rejected a plausible cheat makes no claim; the rejected controls are the observations that show it can refute. "
        "Most fake results are accidents (a bug that skips work looks like a cheat); controls catch both." % (pop, t_pop),
        HUMAN, font=11, align="left"),
    box("legend", 30, 560, 1220, 26,
        "Legend:  green = legitimate runs that must pass  |  red = controls that must fail, and the too-tight failure  |  amber = the frozen gate  |  blue = hosts  |  purple = the principle  |  arrow label = required verdict",
        WHITE, align="left", font=11),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B3-negative-controls.md (both control tables, 'a control can be wrong too', development vs evaluation host, device lock, Popper); notes/B2-the-frozen-evaluator.md; notes/B1-reference-and-baseline.md (legitimate-noise references); "
    "notes/C3-calibration.md (baseline binding, wallclock control rejected); notes/C4-lessons-about-the-method.md (gates fail both ways). The second-core perturbation's purpose is the notes' reading; the source names the control only."],
    30, 598, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
