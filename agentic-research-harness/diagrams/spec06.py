# -*- coding: utf-8 -*-
# 06 — Calibration: give the topic something to find (notes C3, C2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="06-calibration-something-to-find", w=W, h=0)

f1 = V("sched_cal1_fifo_ms"); t_f1 = T("sched_cal1_fifo_ms")
fb = V("sched_cal1_fifo_binding"); t_fb = T("sched_cal1_fifo_binding")
e1 = V("sched_cal1_edf_ms"); t_e1 = T("sched_cal1_edf_ms")
fl1 = V("sched_cal1_floor_ms"); t_fl1 = T("sched_cal1_floor_ms")
u1 = V("sched_cal1_util"); t_u1 = T("sched_cal1_util")
gap1 = round(e1 - fl1, 1)  # my arithmetic
bl = V("sched_baseline"); t_bl = T("sched_baseline")
ed = V("sched_edf_gpu_first"); t_ed = T("sched_edf_gpu_first")
ll = V("sched_probe_least_laxity_ms"); t_ll = T("sched_probe_least_laxity_ms")
pr = V("sched_r1_eft_metric_first"); t_pr = T("sched_r1_eft_metric_first")
fl2 = V("sched_work_floor_ms"); t_fl2 = T("sched_work_floor_ms")
gb = V("sched_baseline_gpu_util"); t_gb = T("sched_baseline_gpu_util")
db = V("sched_baseline_dla_util"); t_db = T("sched_baseline_dla_util")
cb = V("sched_baseline_cpu_util"); t_cb = T("sched_baseline_cpu_util")
ga = V("sched_r1_gpu_util"); t_ga = T("sched_r1_gpu_util")
da = V("sched_r1_dla_util"); t_da = T("sched_r1_dla_util")
alpha = V("sched_alphabetical_perception_ms"); t_alpha = T("sched_alphabetical_perception_ms")
hb = V("sched_cal1_heldout_b"); t_hb = T("sched_cal1_heldout_b")
grasp = V("sched_heldout_b_grasp_ms"); t_grasp = T("sched_heldout_b_grasp_ms")
cdl = V("sched_control_deadline_ms"); t_cdl = T("sched_control_deadline_ms")

BOXES = [title("Calibration: on the first workload EDF came within %s ms [calc] of the work floor, so the owner densified it until placement "
               "(GPU %s %% %s, DLA %s %% %s) became the lever" % (gap1, gb, t_gb, db, t_db), W, h=40)]

PXMS = 8.0     # px per ms, both panels
PXPC = 3.0      # px per % utilization
LABW = 220
LINES = []

def panel(px, hdr, pal, lat_rows, util_rows, verdict, vpal):
    out = [box("h" + str(px), px, 66, 590, 36, hdr, pal, bold=True, font=13)]
    out.append(text("lh" + str(px), px, 108, 590, 18, "perception-chain metric, ms, as reported in note C3; densified rows are medians over seeds (%d px per ms)" % PXMS, bold=True, font=11))
    y = 130
    for i, (lab, ms, kind) in enumerate(lat_rows):
        out.append(text("ll%d_%d" % (px, i), px, y, LABW - 8, 26, lab, align="right", valign="middle", font=11))
        p = {"floor": BAD, "base": NOTE, "good": AGENT, "diag": DATA, "other": DATA}[kind]
        out.append(box("lb%d_%d" % (px, i), px + LABW, y + 4, int(ms * PXMS), 18, "", p, rounded=False, dashed=(kind == "diag")))
        out.append(text("lv%d_%d" % (px, i), px + LABW + int(ms * PXMS) + 4, y, 120, 26, "%s ms" % ms, valign="middle", font=11, bold=True))
        y += 30
    y += 6
    out.append(text("uh" + str(px), px, y, 590, 18, "utilization, %% (bars to scale, 100 %% = %d px)" % (100 * PXPC), bold=True, font=11))
    y += 22
    for i, (lab, pc, p) in enumerate(util_rows):
        out.append(text("ul%d_%d" % (px, i), px, y, LABW - 8, 24, lab, align="right", valign="middle", font=11))
        out.append(box("ub%d_%d" % (px, i), px + LABW, y + 4, int(100 * PXPC), 16, "", WHITE, rounded=False))
        if pc:
            out.append(box("uf%d_%d" % (px, i), px + LABW, y + 4, int(pc * PXPC), 16, "", p, rounded=False))
        out.append(text("uv%d_%d" % (px, i), px + LABW + int(100 * PXPC) + 4, y, 100, 24, "%s %%" % pc, valign="middle", font=11, bold=True))
        y += 26
    return out, y

lp, ly = panel(30, "FIRST VISIBLE WORKLOAD (superseded)", NOTE,
               [("FIFO baseline %s (binding %s %s)" % (t_f1, fb, t_fb), f1, "base"),
                ("EDF, GPU first %s" % t_e1, e1, "good"),
                ("work floor %s" % t_fl1, fl1, "floor")],
               [("CPU %s" % t_u1, u1["cpu"], DATA), ("GPU %s" % t_u1, u1["gpu"], JUDGE)], "", None)
rp, ry = panel(660, "DENSIFIED WORKLOAD (frozen v0.1)", JUDGE,
               [("baseline: FIFO, shortest-exec %s" % t_bl, bl["median"], "base"),
                ("EDF, same placement %s" % t_ed, ed["median"], "other"),
                ("least laxity, diagnostic %s" % t_ll, ll, "diag"),
                ("R1 promoted %s" % t_pr, pr["median"], "good"),
                ("work floor %s" % t_fl2, fl2, "floor")],
               [("GPU before %s" % t_gb, gb, JUDGE), ("GPU after R1 %s" % t_ga, ga, AGENT),
                ("DLA before %s" % t_db, db, JUDGE), ("DLA after R1 %s" % t_da, da, AGENT),
                ("CPU before %s" % t_cb, cb, DATA)], "", None)
BOXES += lp + rp

# verdict boxes under each panel
VY = max(ly, ry) + 8
BOXES += [
    box("v1", 30, VY, 590, 72,
        "NOTHING TO FIND. EDF sits %s ms [calc] above the floor and both units have slack (CPU %s %%, GPU %s %% %s). "
        "The baseline passes, the gate is calibrated, yet a campaign's ceiling is tiny: a passing baseline does not make a topic ready."
        % (gap1, u1["cpu"], u1["gpu"], t_u1), BAD, font=11, align="left", fill="#fff7f7"),
    box("v2", 660, VY, 590, 72,
        "THE LEVER IS PLACEMENT. Dispatch order alone (EDF, least laxity) stays inside the baseline's range; earliest-finish placement moves work off the saturated GPU onto the idle DLA "
        "and the promoted candidate's median drops to %s ms %s. Medians shown; promotion compares ranges (diagram 05)." % (pr["median"], t_pr),
        AGENT, font=11, align="left"),
]
LY = VY + 84
BOXES += [
    box("dens", 30, LY, 400, 100,
        "HOW IT WAS DENSIFIED (on purpose, documented)\n- a parallel segmenter in the perception chain\n- a new depth-mapping chain\n- several jobs made heavier\n- control deadline set to %s ms %s" % (cdl, t_cdl),
        NOTE, font=11, align="left", valign="top"),
    box("fair", 445, LY, 400, 100,
        "A FAIR BASELINE, NOT A STRAWMAN\nThe first baseline placed jobs alphabetically: every accelerator job went to the DLA, perception reached %s ms %s (off this scale) and the densified workload failed outright. "
        "It was replaced by shortest-execution placement: the default an engineer ships first." % (alpha, t_alpha),
        HUMAN, font=11, align="left", valign="top"),
    box("greedy", 860, LY, 390, 100,
        "GPU-GREEDY LOSES WHEN A LONG JOB BLOCKS THE GPU (diagnostic)\nHeld-out b, first calibration: GPU-greedy %s ms vs CPU placement %s ms %s. A %s ms %s grasp-planner job holds the single non-preemptive GPU and perception queues behind it."
        % (hb["gpu_greedy"], hb["cpu_placement"], t_hb, grasp, t_grasp),
        DATA, font=11, align="left", valign="top", dashed=True),
    box("legend", 30, LY + 112, 1220, 40,
        "Legend:  grey bar = baseline  |  green = best non-diagnostic policy  |  blue = other policy; dashed = diagnostic (did not pass through the frozen evaluator)  |  red = work floor (no scheduler beats it)  |  "
        "utilization: amber = before, green = after round 1, blue = CPU. Simulator output: illustrative, not a real platform.",
        WHITE, align="left", font=11),
]
EDGES = []
src_box, bottom = footer_box(T, [
    "Mechanism: notes/C3-calibration.md (two goals of calibration, work floor, densifying, baseline placement choice, GPU-greedy finding, round-1 result); notes/C2-the-scheduling-topic.md (platform, metric, held-out b). "
    "[calc]: %s = %s - %s. The first workload's DLA utilization is not in the notes and is not drawn." % (gap1, e1, fl1)],
    30, LY + 166, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
