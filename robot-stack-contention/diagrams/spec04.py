# 04 — Same work, more cycles (note A2). Numbers via V() from ../constants.json; tags via Tags().
from _charts import *

W = 1440
PAGE = dict(name="04-same-work-more-cycles", w=W, h=820)
T = Tags()

ig = V("instr_growth")
cg0, cg1 = V("cycles_growth_range")
id0, id1 = V("ipc_drop_range")
l30, l31 = V("l3_refill_ratio_range")
fval = V("cluster_move_recovered")
line = V("cluster_move_class_line")

BOXES = [title("Same work, more cycles: in the full stack fixed-work threads run the same instructions with %s× to "
               "%s× the cycles %s; moving the motor-control services' cluster-mates removes about two thirds of "
               "the extra cycles (class \"most (or less board traffic)\")" % (f(1 + cg0), f(1 + cg1),
                                                                         T("cycles_growth_range")), W, h=60, font=20)]
LINES, EDGES = [], []

# ---------------- left: ratio to alone, per fixed work unit ----------------
BOXES.append(panel("lpan", 20, 84, 690, 520, "", fill="none", stroke=GREY_S))
BOXES.append(text("lhd", 30, 90, 670, 52,
                  "**Alone -> full stack, user-mode counts per fixed work unit** (one bus cycle / one audio "
                  "message / one detector frame), three fixed-work threads. Ratio to alone; the full-stack bar "
                  "spans the range over the threads. Pre-registered class: **X2 \"slower work\"** for all three.",
                  font=11))
ax = Axes(110, 180, 570, 300, (0, 4), (0, 3.2))
yt = [(v, "%s×" % f(v)) for v in (0, 0.5, 1, 1.5, 2, 2.5, 3)]
b, l = ax.frame("a", [], yt, "", "ratio to alone (alone = 1×)")
BOXES += b; LINES += l
LINES.append(hline(ax.X(0), ax.X(4), ax.Y(1), INK, 1.5, dash="6,4", top=True))
groups = [
    ("instructions per unit", 1 + ig, 1 + ig, "%s× (growth %s) %s" % (f(1 + ig), f(ig, 1), T("instr_growth")),
     GREY, GREY_S),
    ("cycles per unit", 1 + cg0, 1 + cg1, "%s×–%s× %s" % (f(1 + cg0), f(1 + cg1), T("cycles_growth_range")),
     CPU2, CPU_S),
    ("IPC", 1 - id1, 1 - id0, "%s×–%s× (drop %s–%s) %s" % (f(1 - id1, 1), f(1 - id0, 1), f(id0), f(id1),
                                                       T("ipc_drop_range")), "#ffffff", "#1f3f73"),
    ("L3 refills per instruction (a hint, not a cause)", l30, l31,
     "%s×–%s× %s" % (f(l30), f(l31), T("l3_refill_ratio_range")), "#f4f4f4", "#555555"),
]
BW = 40
for gi, (name, lo, hi, lab, fill, stroke) in enumerate(groups):
    cx = ax.X(gi + 0.5)
    # alone bar
    BOXES.append(bar("al%d" % gi, cx - BW - 4, ax.Y(1), BW, ax.Y(0) - ax.Y(1), "#e4e4e4", GREY_S, label="", font=9))
    # full-stack: solid to lo, dashed extension lo..hi
    sw = 3 if name == "IPC" else 1.5
    BOXES.append(bar("fl%d" % gi, cx + 4, ax.Y(lo), BW, ax.Y(0) - ax.Y(lo), fill, stroke, sw=sw))
    if hi > lo:
        BOXES.append(bar("fh%d" % gi, cx + 4, ax.Y(hi), BW, ax.Y(lo) - ax.Y(hi), "#ffffff", stroke, dash="4,3", sw=sw))
    BOXES.append(text("lab%d" % gi, cx - 68, ax.Y(max(hi, 1)) - 46, 136, 44, lab, font=9.5, align="center", valign="bottom"))
    BOXES.append(text("gn%d" % gi, cx - 68, ax.Y(0) + 6, 136, 44, "**%s**\nleft alone, right full stack" % name,
                      font=9.5, align="center"))
BOXES.append(text("clk", 30, 552, 670, 40,
                  "Clock unchanged (all cores locked). The motor loop is never preempted, so its slowdown is not "
                  "run-queue wait. Kernel-mode instructions do rise for some threads; message fan-out, interrupt and "
                  "scheduler work are not separated. My estimate: full-stack ratio = 1 + growth, IPC = 1 − drop.",
                  font=9.5, color="#444444"))

# ---------------- right: cluster move ----------------
RX = 730
BOXES.append(panel("rpan", RX, 84, 690, 520, "", fill="none", stroke=GREY_S))
BOXES.append(text("rhd", RX + 10, 90, 670, 52,
                  "**Cluster move: every service sharing the motor-control services' CPU cluster goes to the "
                  "pool.** X = the motor loop's user cycles per bus cycle; two arms, \"baseline\" (full stack) and "
                  "\"moved\", two windows each.", font=11))
# schematic bars: lengths show f only
L0, G = 230, 260
bx0 = RX + 170
sch = [("alone", "alone", L0, GREY, GREY_S, None),
       ("moved", "moved: cluster-mates moved", L0 + G * (1 - fval), CPU, CPU_S, "5,3"),
       ("base", "baseline: full stack", L0 + G, CPU2, CPU_S, None)]
for i, (rid, rname, Lx, fill, stroke, dash) in enumerate(sch):
    y = 156 + i * 46
    BOXES.append(text("rn%s" % rid, RX + 8, y, 156, 34, "**%s**" % rname, font=10, align="right", valign="middle"))
    BOXES.append(bar("rb%s" % rid, bx0, y + 2, Lx, 30, fill, stroke, dash=dash, label="X_%s" % rid, font=10.5))
for x0, x1, yy, lab, col in [(L0, L0 + G, 302, "full-stack growth X_base − X_alone", INK),
                             (L0 + G * (1 - fval), L0 + G, 324, "removed X_base − X_moved", CPU_S)]:
    LINES += whisker_h(bx0 + x0, bx0 + x1, yy, col)
    BOXES.append(text("br%d" % yy, bx0 + x0 - 236, yy - 8, 230, 16, lab, font=10, align="right", color=col))
BOXES.append(text("schn", RX + 10, 340, 670, 16, "schematic: bar lengths show only the ratio f, not cycle counts",
                  font=9.5, align="center", color="#555555"))

# f-scale strip
fx = Axes(RX + 70, 400, 590, 60, (0, 1), (0, 1))
BOXES.append(bar("fz1", fx.X(0), 410, fx.X(line) - fx.X(0), 40, "#ffffff", INK, dash="6,4",
                 label="\"part\" = predicted before the run", font=10))
BOXES.append(bar("fz2", fx.X(line), 410, fx.X(1) - fx.X(line), 40, CPU, CPU_S,
                 label="\"most (or less board traffic)\"", font=10))
LINES.append(vline(fx.X(line), 398, 460, INK, 2, dash="4,3", top=True))
for i, t in enumerate([0, line, 1]):
    BOXES.append(text("fxt%d" % i, fx.X(t) - 20, 462, 40, 14, f(t), font=9.5, align="center"))
BOXES.append(dot("fdot", fx.X(fval), 394, 6, "#1f3f73", "#1f3f73"))
BOXES.append(text("fval", fx.X(fval) - 250, 366, 500, 18,
                  "**f = %s** %s, close to the line" % (f(fval), T("cluster_move_recovered")), font=10.5, align="center"))
BOXES.append(text("fdef", RX + 10, 478, 670, 18,
                  "removed fraction f = (X_base − X_moved) ÷ (X_base − X_alone); dashed line = pre-registered class line %s %s"
                  % (f(line), T("cluster_move_class_line")), font=10, align="center"))
c0, c1 = V("cluster_move_camera_cost_hz")
BOXES += [
    dict(id="whyopen", x=RX + 10, y=500, w=330, h=96, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True,
         font=10, align="left", valign="top",
         label="**Prediction failed; the path stays open.** Predicted \"part\"; f lands above the line, so read "
               "it as \"about two thirds\", not a clean \"most\". (1) The two moved windows differ, and the spread "
               "reaches toward the line. (2) Board memory traffic fell in the moved arm, so the class carries \"(or less "
               "board traffic)\". (3) The motor-control services' own load also fell. The other ~%s is not "
               "separated (%s: 1 − %s)." % (f(1 - fval, 2), T.est("cluster_move_recovered"), f(fval))),
    dict(id="cost", x=RX + 350, y=500, w=330, h=96, fill=BENCH, stroke=BENCH_S, rounded=True, font=10,
         align="left", valign="top",
         label="**The move is not a free fix.** The moved services land on the pool: the camera loses %s to %s "
               "Hz %s; other pool services and message delay get worse.\nEarlier cache A/B: a synthetic "
               "L3-footprint load on the neighbouring cores reproduced a slower motor loop; an L1-resident load "
               "reproduced nothing." % (f(c0), f(c1), T("cluster_move_camera_cost_hz"))),
]

ly = 618
legend = ("**Legend**\nleft: grey bar = alone (1×); coloured bar = full stack, solid to the low end of the range "
          "and dashed outline to the high end; thick dark-blue border = IPC; dashed horizontal line = alone level.\n"
          "right: grey = alone, mid-blue = baseline, light blue dashed = moved; dot = f; dashed outline / dashed line = the "
          "prediction and the pre-registered class line.\npurple dashed box = why the result is not a clean cause; "
          "amber = the cost of the fix.")
src, hs = sources_panel("src", 470, ly, 950, T,
                        "Numbers loaded from ../constants.json by spec04.py; key in brackets. Note A2 (counters, "
                        "cluster move, cache A/B). The cache mechanism is taught in "
                        "../../jetson-orin-thor-metrics/notes/B2-cache-level-interference.md.", font=9.5)
hl = int(est_lines(legend, 436, 10.5) * 13.2 + 16)
BOXES.append(panel("legend", 20, ly, 436, max(hs, hl), legend, font=10.5))
BOXES.append(src)
PAGE["h"] = ly + max(hs, hl) + 16
