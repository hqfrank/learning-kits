# 06 — Evaluating with almost no labels: funnel, interval, confusion matrix, false alarms (C1, C4).
# Type: funnel + interval (range-bar) chart + 2x2 matrix + a pilot strip.
from _common import *

S = Src()
W = 1280
B, E, L = [], [], []
cand, use, det = raw("ground_truth_candidates"), raw("ground_truth_usable"), raw("ground_truth_detected")
rate = 100.0 * det / use  # my arithmetic
wil = raw("detection_rate_wilson95_6of10")
pt, pe = raw("pilot_tickets"), raw("pilot_environmental")
B.append(title("Catching %s of %s known faults says 'the method works', not 'it is better': the 95 %% "
               "interval is %s %%, and it must be reported next to %s of %s pilot flags that were "
               "environmental (illustrative counts)" % (fmt(det), fmt(use), fmt(wil), fmt(pe), fmt(pt)), W))

# ---------- A: funnel ----------
B.append(text("ha", 20, 80, 390, 18, "**A. Building ground truth by hand** [C1]", font=12))
fun = [("ground_truth_candidates", "candidate cases (lab faults + resolved user reports)", GREY, GREY_S),
       ("ground_truth_usable", "usable: production-format log, right time range, identified bug, "
        "closed ticket", BLUE, BLUE_S),
       ("ground_truth_detected", "detected by the pipeline (backward validation)", GREEN, GREEN_S)]
for i, (k, lab, f, s_) in enumerate(fun):
    wpx = 120 + 260 * raw(k) / float(cand)
    B.append(box("f%d" % i, 20 + (380 - wpx) / 2, 104 + i * 66, wpx, 30,
                 "**%s**" % S.v(k, u="cases"), f, s_, rounded=False, font=11))
    B.append(text("fl%d" % i, 20, 136 + i * 66, 380, 30, lab, font=10, align="center",
                  color="#444444"))

# ---------- B: intervals ----------
B.append(text("hb", 440, 80, 410, 18, "**B. Detection rate with its 95 % interval** [C1]", font=12))
ax = Axes(560, 120, 280, 150, (0, 100), (0, 3))
fb, fl = ax.frame("b", [0, 20, 40, 60, 80, 100], [], "detection rate (%)", "")
B += fb; L += fl
rws = [("detection_rate_wilson95_6of10", "Wilson, %s/%s" % (fmt(det), fmt(use)), GREEN_S, None, rate),
       ("detection_rate_wald95_6of10", "Wald, %s/%s" % (fmt(det), fmt(use)), GREY_S, "6,4", rate),
       ("detection_rate_wilson95_60of100", "Wilson, 60/100", BLUE_S, None, rate)]
for i, (k, lab, col, dash, p) in enumerate(rws):
    lo, hi = raw(k)
    y = ax.Y(2.5 - i)
    L += [hline(ax.X(lo), ax.X(hi), y, color=col, sw=4, dash=dash, top=True),
          vline(ax.X(lo), y - 7, y + 7, color=col, sw=2, top=True),
          vline(ax.X(hi), y - 7, y + 7, color=col, sw=2, top=True)]
    B.append(dict(id="pt%d" % i, x=ax.X(p) - 6, y=y - 6, w=12, h=12, label="", fill="#ffffff",
                  stroke=col, sw=2, shape="ellipse"))
    B.append(text("rl%d" % i, 440, y - 9, 116, 18, lab, font=10.5, align="right", color=col,
                  bold=True))
    B.append(text("rv%d" % i, ax.X(lo) - 10, y - 26, 200, 16, S.v(k), font=10, color=col))
B.append(text("bn", 440, 320, 410, 70,
              "point = %s %% (my arithmetic). Ten cases give about +/- 25 pp; 100 cases at the same rate "
              "narrow it. The Wald interval is too wide at the top and misbehaves near 0 and 1. "
              "Ten cases cannot rank this method against one that scored 50 %%." % fmt(rate),
              font=10.5))

# ---------- C: confusion matrix + pilot ----------
B.append(text("hc", 880, 80, 380, 18, "**C. Detection rate needs its false-alarm rate** [C1]",
              font=12))
cx, cy, cw, ch = 990, 126, 130, 44
B.append(text("ch1", cx, cy - 22, cw, 18, "fault present", font=10.5, align="center", bold=True))
B.append(text("ch2", cx + cw, cy - 22, cw, 18, "no fault", font=10.5, align="center", bold=True))
B.append(text("rh1", 880, cy + 12, 106, 18, "flagged", font=10.5, align="right", bold=True))
B.append(text("rh2", 880, cy + ch + 12, 106, 18, "not flagged", font=10.5, align="right", bold=True))
for (lab, r, c, f, s_) in [("TP", 0, 0, GREEN, GREEN_S), ("FP\nfalse alarm", 0, 1, RED, RED_S),
                          ("FN\nmiss", 1, 0, AMBER, AMBER_S), ("TN", 1, 1, GREY, GREY_S)]:
    B.append(box("cm%d%d" % (r, c), cx + c * cw, cy + r * ch, cw, ch, lab, f, s_, rounded=False,
                 font=11, bold=True, sw=1.5))
B.append(text("cmf", 880, cy + 2 * ch + 6, 380, 48,
              "detection rate (recall) = TP / (TP + FN); precision = TP / (TP + FP); "
              "false-alarm share of flags = 1 - precision. Flag everything and recall is 100 %.",
              font=10.5))
B.append(text("pil", 880, 286, 380, 18, "forward pilot: %s, of which %s environmental" % (
    S.v("pilot_tickets"), S.v("pilot_environmental", u="")), font=10.5, bold=True))
for i in range(int(pt)):
    env = i >= pt - pe
    B.append(box("tk%d" % i, 880 + i * 36, 308, 30, 30, "env" if env else "", RED if env else BLUE,
                 RED_S if env else BLUE_S, rounded=False, font=9, dash="4,3" if env else None, sw=1.5))
B.append(text("pil2", 880, 342, 380, 46,
              "environmental = the customer's access point or internet, not the device [C4]. "
              "Confirm with a second signal before a ticket.", font=10.5))

# ---------- D: the method around the numbers ----------
YD = 400
B.append(box("bw", 20, YD, 400, 86,
             "**Backward validation** [C1]: start from a known fault, find the snippet, check the "
             "detector flags the same device and window. Record: what, when, caught?, if not why and "
             "is it fixable. Necessary, not sufficient.", BLUE, BLUE_S, align="left", valign="top",
             font=10.5))
B.append(box("fw", 440, YD, 400, 86,
             "**Forward pilot** [C1]: a few cases a week to domain experts with no prior answer. Ask in "
             "order: is the output enough to start? what is missing? was the right anomaly flagged? "
             "Speed the cycle with a historical set and time-ordered cross-validation (train early, "
             "validate later, roll forward).", GREEN, GREEN_S, align="left", valign="top", font=10.5))
B.append(box("ms", 860, YD, 400, 86,
             "**The misses name the missing signals** [C1, C4]: Wi-Fi disconnects caused by the DHCP "
             "client; 'cannot register' caused by failed time sync; reboots from a kernel-driver "
             "assertion (kernel buffer); a log that ends at the crash; stateful order-dependent faults "
             "(need sequences). Fixable misses become the roadmap.", AMBER, AMBER_S, align="left",
             valign="top", font=10.5))
E.append(dict(src="bw", dst="fw", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))
E.append(dict(src="fw", dst="ms", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))

B.append(panel("legend", 20, YD + 98, 1240, 30,
               "**Legend** — green = caught / Wilson interval / forward step; grey dashed = Wald interval; "
               "blue = usable cases, the 100-case interval and device-fault tickets; red dashed = false "
               "alarms (environmental); amber = misses. Circle = point estimate.", font=10.5))
n = S.footnote_lines()
sy = YD + 138
sh = int(12.5 * n + 22)
B.append(sources(S, 20, sy, 1240, sh, extra="Wilson interval: Wilson, JASA 1927; NIST e-Handbook §7.2.4.1. "
                 "Precision/recall as in Du et al., DeepLog, CCS 2017, §5.1."))
PAGE = dict(name="06-evaluating-without-labels", w=W, h=sy + sh + 14)
BOXES, EDGES, LINES = B, E, L
