# 01 — The pipeline on one page: metrics choose which logs to read (A0, A1, B1-B6, C1, C4).
# Type: block / pipeline diagram. Numbers: all loaded from constants.json via Src.
from _common import *

S = Src()
W, H = 1280, 0  # H set at the end

B, E, L = [], [], []
B.append(title("Metrics choose which logs to read: a four-stage cascade narrows a fleet's logs "
               "to a few flagged windows and one ticket per fault, and an engineer still decides", W))

# --- the device (source of both signals) ---
B.append(box("dev", 20, 88, 240, 130,
             "**A DEVICE** [A1]\n"
             "many components write one interleaved stream\n"
             "about %s per device-day\n"
             "ring buffer of %s overwrites old lines: only hours of history\n"
             "on-device retention %s\n"
             "sends metrics (all devices) and logs (on demand)" % (
                 S.v("lines_per_device_day"),
                 S.v("ring_buffer_size", u="MB"),
                 S.v("on_device_retention")),
             PURPLE, PURPLE_S, align="left", valign="top"))

X = [300, 545, 790, 1035]
SW, SY, SH = 225, 88, 130
B.append(box("s1", X[0], SY, SW, SH,
             "**1 DETECT a change** [B4, A2]\n"
             "family level: weighted-least-squares slope test on the daily share of devices\n"
             "device level: isolation forest on device-day metric vectors\n"
             "out: which metric, which devices, which days",
             BLUE, BLUE_S, align="left", valign="top"))
B.append(box("s2", X[1], SY, SW, SH,
             "**2 FETCH + PARSE** [B1, B2]\n"
             "fetch logs only of the devices that drive the change, only for that time range\n"
             "line -> template ID + parameters (a few hundred templates, e.g. %s)\n"
             "cut windows, count templates per window" % S.v("templates_per_component_set"),
             BLUE, BLUE_S, align="left", valign="top"))
B.append(box("s3", X[2], SY, SW, SH,
             "**3 SCORE + EXPLAIN** [B3, B5]\n"
             "isolation forest on count vectors -> one score per window\n"
             "per-thread transition edges -> where the sequence left the normal path\n"
             "reduction: %s flagged of %s" % (
                 S.v("flagged_windows"), S.v("windows_scanned")),
             BLUE, BLUE_S, align="left", valign="top"))
B.append(box("s4", X[3], SY, SW, SH,
             "**4 GROUP + REPORT** [B6]\n"
             "join metric + log anomaly per device-day\n"
             "hierarchical clustering: one cluster per symptom\n"
             "rank by devices hit and score; de-duplicate against open tickets; "
             "one ticket with the evidence attached",
             BLUE, BLUE_S, align="left", valign="top"))

# upload arrows device -> s1 (metrics) and device -> s2 (logs, on demand)
L.append(dict(pts=[(260, 130), (300, 130)], color=PURPLE_S, sw=2, arrow="end"))
L.append(dict(pts=[(140, 218), (140, 252), (657, 252), (657, 218)], color=PURPLE_S, sw=2,
              dash="6,4", arrow="end"))
B.append(text("up_l", 300, 256, 520, 20,
              "logs: uploaded on demand only (after the fault), kept %s [A1]" %
              S.v("uploaded_log_retention"), font=10, color=PURPLE_S))

# stage-to-stage
for a, b in [("s1", "s2"), ("s2", "s3"), ("s3", "s4")]:
    E.append(dict(src=a, dst=b, sx=1, sy=0.5, dx=0, dy=0.5, color=BLUE_S, sw=2))
B.append(text("ctx", X[0] + 4, SY + SH + 2, 230, 30,
              "pass context to stage 2: which metric fired + when (UTC vs device local time) [B5]",
              font=10, color=BLUE_S))

# engineer
B.append(box("eng", 1035, 262, 225, 90,
             "**ENGINEER decides** [C4]\n"
             "anomaly is not issue: confirm with a second signal before a ticket\n"
             "time per case %s -> %s" % (S.v("time_per_case_before", u=""),
                                         S.v("time_per_case_after")),
             AMBER, AMBER_S, align="left", valign="top"))
E.append(dict(src="s4", dst="eng", sx=0.5, sy=1, dx=0.5, dy=0, color=BLUE_S, sw=2))

# feedback loop (dashed) engineer -> stage 1
L.append(dict(pts=[(1035, 330), (282, 330), (282, 180), (300, 180)], color=GREEN_S, sw=2, dash="6,4",
              arrow="end"))
B.append(text("fb", 300, 334, 720, 20,
              "feedback: root-cause label (device defect / environmental / data artefact) "
              "-> ground truth [C1] + drop and direction rules [B4]", font=10, color=GREEN_S))

# on-device vs fleet-side
B.append(box("ond", 20, 372, 600, 74,
             "**ON-DEVICE alternative** [A0, B3]: a small sequence model (DeepLog-style LSTM, "
             "history h = %s, normal if next template in top g = %s) reads every line before "
             "the ring buffer overwrites it, works offline, and raw logs never leave the device. "
             "Cost: it must fit the device's memory and power budget." % (
                 S.v("deeplog_history_h", u=""), S.v("deeplog_top_g", u="")),
             PURPLE, PURPLE_S, align="left", valign="top", dash="6,4", font=10.5))
B.append(box("fls", 640, 372, 620, 74,
             "**FLEET-SIDE (this cascade)** [A0, B5]: ample compute, compares many devices, "
             "cheap and explainable forest. Sees only uploaded logs and kept time ranges; "
             "misses faults that never show in metrics. Started first: lower risk, a working "
             "result sooner, a path to a parallel (logs always analysed) form later.",
             BLUE, BLUE_S, align="left", valign="top", font=10.5))

B.append(panel("legend", 20, 458, 1240, 36,
               "**Legend** — purple = the device and on-device work; blue = fleet-side cloud stages; "
               "amber = the human decision; green dashed = the feedback loop. Solid arrow = data flow; "
               "dashed purple = logs, which arrive only on demand. [A0] etc. = the kit note that "
               "explains the box.", font=10.5))

n = S.footnote_lines()
sh = int(12.5 * n + 20)
B.append(sources(S, 20, 506, 1240, sh))
H = 506 + sh + 14
PAGE = dict(name="01-pipeline-cascade", w=W, h=H)
BOXES, EDGES, LINES = B, E, L
