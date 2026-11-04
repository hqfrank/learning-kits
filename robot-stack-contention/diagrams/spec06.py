# 06 — The dose curve (note B1). Public kit: every number via V() from ../constants.json, tagged by key.
from _charts import *

W, H = 1440, 750
PAGE = dict(name="06-dose-curve", w=W, h=H)
T = Tags()

pts = V("dose_curve_points")
vO, R = V("dose_vla_point")
slopes = V("dose_slopes")
dnull = V("dram_null_added_ms")
burst = V("burst_length_effect_ms")
ts0, ts1 = V("timeslice_ms")
blk, wait, run = V("detector_vla_added_blocked_wait_run")


def interp(o):
    """Straight line between neighbouring measured points (my arithmetic)."""
    for (o0, c0), (o1, c1) in zip(pts, pts[1:]):
        if o0 <= o <= o1:
            return c0 + (o - o0) * (c1 - c0) / float(o1 - o0)


cstar = interp(vO)
top_O, top_C = pts[-1]
low_O, low_C = pts[1]
CUR, CUR_S = "#b9dfb0", "#3f7f33"

BOXES = [title("The object detector's added GPU wait follows the other processes' share of GPU time on a convex "
               "curve; the VLA sits on the compute co-tenant's curve, and a memory copy at the same GPU time adds "
               "nothing (illustrative numbers)", W, h=60, font=20)]
LINES, EDGES = [], []

ax = Axes(110, 128, 760, 440, (0, 90), (0, 180))
b, l = ax.frame("a", list(range(0, 91, 10)), list(range(0, 181, 20)),
                "O = other processes' share of GPU-active time (percentage points)",
                "C = the detector's added blocked time (ms per frame, above the no-load window)")
BOXES += b; LINES += l

# prediction written before the run: at the highest dose C stays below R (dashed line at R)
LINES.append(hline(ax.X(70), ax.X(88), ax.Y(R), INK, 1.5, dash="5,3", top=True))
BOXES.append(text("predl", ax.X(70.5), ax.Y(R) + 4, ax.X(89) - ax.X(70.5), 44,
                  "dashed: predicted before the run, C at the high dose stays **below R**",
                  font=9.5, align="right"))

# measured compute curve
LINES.append(dict(pts=[(ax.X(o), ax.Y(c)) for o, c in pts], color=CUR_S, sw=2.5, top=True))
for i, (o, c) in enumerate(pts):
    BOXES.append(dot("p%d" % i, ax.X(o), ax.Y(c), 6, CUR if i else "#ffffff", CUR_S))
tag_pts = T("dose_curve_points")
names = ["no load", "compute, low dose", "compute, middle dose", "compute, high dose"]
offs = [(12, -44), (12, -2), (-178, -34), (-208, -16)]
for i, ((o, c), nm, (dx, dy)) in enumerate(zip(pts, names, offs)):
    lab = "**%s**\n(O %s, C %s ms)" % (nm, f(o), f(c))
    if i == 1:
        lab += "\n" + tag_pts
    BOXES.append(text("pl%d" % i, ax.X(o) + dx, ax.Y(c) + dy, 170 if i != 3 else 200, 46, lab,
                      font=9.5, align="right" if dx < 0 else "left"))
# slopes on the segments
for i, s in enumerate(slopes):
    (o0, c0), (o1, c1) = pts[i], pts[i + 1]
    mx, my = ax.X((o0 + o1) / 2.0), ax.Y((c0 + c1) / 2.0)
    sdx, sdy = [(-150, -34), (10, 6), (10, 6)][i]
    BOXES.append(text("sl%d" % i, mx + sdx, my + sdy, 190, 30, "slope %s ms per point %s" % (f(s), T("dose_slopes")),
                      font=9.5, bold=False, color=CUR_S))

# VLA point
BOXES.append(dot("vla", ax.X(vO), ax.Y(R), 7, INK, INK, square=True))
BOXES.append(text("vlal", ax.X(30), ax.Y(150), 300, 62,
                  "**VLA arm = R** (O %s, C %s ms) %s\nC* = curve at O %s = %s ms, so C*/R = %s (%s)"
                  % (f(vO), f(R), T("dose_vla_point"), f(vO), f(cstar), f(round(cstar / R, 2)),
                     T.est("dose_curve_points", "dose_vla_point")), font=9.5, align="left"))
LINES.append(dict(pts=[(ax.X(30) + 245, ax.Y(150) + 32), (ax.X(vO) - 8, ax.Y(R) - 6)], color=INK, sw=1.2,
                  dash="3,3", arrow="end", top=True))

# memory-copy null: same GPU time as the low-dose compute arm, adds nothing
BOXES.append(dot("cpy", ax.X(low_O), ax.Y(dnull) - 7, 7, "#ffffff", BENCH_S, dash="3,2", sw=2, square=True))
BOXES.append(text("cpyl", ax.X(low_O) + 12, ax.Y(dnull) - 40, 300, 32,
                  "**memory-copy co-tenant**, same GPU time as the low-dose arm: adds %s ms %s"
                  % (f(dnull), T("dram_null_added_ms")), font=9.5, color="#8a5a00"))

# correction callout near the low-dose point
BOXES.append(dict(id="corr", x=ax.X(3), y=ax.Y(118), w=250, h=92, fill=CORR, stroke=CORR_S, dash="6,4",
                  rounded=True, font=9.5, align="left", valign="top",
                  label="**Correction kept visible.** The first test's class \"neither alone\" (C about %d %% of R, "
                        "%s) came from a compute arm at about %s points against the VLA's %s: the low end of a convex "
                        "curve. The first class stands as recorded."
                        % (round(100.0 * low_C / R), T.est("dose_curve_points", "dose_vla_point"), f(low_O),
                           f(vO))))
LINES.append(dict(pts=[(ax.X(3) + 250, ax.Y(118) + 70), (ax.X(low_O) + 4, ax.Y(low_C) - 8)], color=CORR_S,
                  sw=1.5, dash="4,3", arrow="end", top=True))

# ---------------- right column ----------------
RX, RW = 905, 515
BOXES += [
    dict(id="verd", x=RX, y=84, w=RW, h=64, fill=GPU, stroke=GPU_S, rounded=True, font=10.5, align="left",
         valign="top",
         label="**Verdict as pre-registered: \"dose explains\".** The VLA point lies on the compute co-tenant's "
               "curve (C*/R = %s, %s). Each extra point of O costs more than the last: slopes %s ms per point "
               "%s." % (f(round(cstar / R, 2)), T.est("dose_curve_points", "dose_vla_point"),
                        " / ".join(f(s) for s in slopes), T("dose_slopes"))),
    dict(id="null", x=RX, y=158, w=RW, h=84, fill="#ffffff", stroke=INK, rounded=True, font=10.5, align="left",
         valign="top",
         label="**What adds nothing measurable at the VLA's dose**\n• DRAM traffic: the memory copy adds %s ms "
               "%s.\n• SM issue rate: the compute co-tenant issues far more often than the VLA, yet costs the same "
               "at the same share.\n• Burst length: short vs long bursts at one share differ by %s ms %s."
               % (f(dnull), T("dram_null_added_ms"), f(burst), T("burst_length_effect_ms"))),
    dict(id="wrong", x=RX, y=252, w=RW, h=62, fill="#ffffff", stroke=INK, dash="5,3", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Two predictions were wrong** (written before the run)\n• high dose: predicted below R, measured "
               "%s R (%s).\n• burst length: predicted to matter, it did not. Bursts well below one time slice (under 1 ms) "
               "were not tested." % (f(round(top_C / float(R), 2)), T.est("dose_curve_points", "dose_vla_point"))),
    dict(id="mech", x=RX, y=324, w=RW, h=84, fill=NOTE, stroke=NOTE_S, rounded=True, font=10.5, align="left",
         valign="top",
         label="**Why share, not traffic (page 05).** \"%s\" %s Without MPS the contexts take turns of about "
               "%s ms %s, so the detector waits for the others' turns plus each switch. The split between slice "
               "waiting and switch cost was not measured."
               % (V("mps_no_concurrency_quote"), T("mps_no_concurrency_quote"), rng(ts0, ts1),
                  T("timeslice_ms"))),
]
# stacked bar: where the detector's rise next to the VLA goes
SY = 418
BOXES.append(panel("split", RX, SY, RW, 104, "", fill="#ffffff", stroke=GREY_S))
BOXES.append(text("splh", RX + 8, SY + 4, RW - 16, 34,
                  "**In the full stack, next to the VLA, most of the detector's rise is GPU wait** (ms per frame added) %s"
                  % T("detector_vla_added_blocked_wait_run"), font=10.5))
px = 4.0  # px per ms
x0 = RX + 14
for k, (v, nm, fill, st, dash) in enumerate([(blk, "blocked", GPU, GPU_S, None), (wait, "CPU wait", CPU, CPU_S, None),
                                             (run, "run", "#ffffff", CPU_S, "4,3")]):
    BOXES.append(bar("sb%d" % k, x0, SY + 44, v * px, 26, fill, st, dash=dash, label="%s %s" % (nm, f(v)),
                     font=9.5))
    x0 += v * px
BOXES.append(text("splt", RX + 14, SY + 74, RW - 28, 28,
                  "sum %s ms per frame, full stack -> full stack + VLA (a different row from the dose curve; %s)"
                  % (f(blk + wait + run), T.est("detector_vla_added_blocked_wait_run")),
                  font=9.5))

# ---------------- bottom ----------------
cav = ("**Caveats.** Measured in a reduced row (the depth camera service and the detector only), idle CPU pool, "
       "one window per arm. **In the full stack the mechanism is expected, not tested**; full-stack windows sit "
       "below the curve in a post-hoc reading, because the detector also waits for the CPU there and meets less GPU "
       "contention per frame (not separated from other causes). The victim metric is blocked time: neither running "
       "nor waiting for a CPU, mostly waiting for the GPU. O removes the detector's own GPU time; added GPU busy would "
       "include it and understate the dose. Straight segments join the points; the curve between them is not "
       "measured. All measured values are an illustrative measurement.")
leg = ("**Legend**\ngreen line + filled circles = compute co-tenant arms; hollow circle = no-load window\n"
       "black square = the VLA arm (R)\nhollow dashed orange square = memory-copy co-tenant\n"
       "dashed black line = prediction written before the run\npurple dashed box = a correction\n"
       "green box = the pre-registered verdict\nstacked bar: solid = illustrative measured share; dashed = slower run")
BOXES += [
    dict(id="cav", x=20, y=604, w=480, h=132, fill="#ffffff", stroke="#333333", rounded=True, font=10.5,
         align="left", valign="top", label=cav),
    panel("legend", 512, 604, 370, 132, leg, font=10.5),
]
src, sh = sources_panel("src", 894, 604, 526, T,
                        "Note B1. Contexts and time-slicing: ../../nvidia-gpu-anatomy/ (note 07). C* and the "
                        "ratios to R are straight-line arithmetic on the points.", font=9.5)
sh = int(sh * 0.8)  # the helper's line estimate runs high for this renderer
src["h"] = sh
BOXES.append(src)
PAGE["h"] = max(H, 604 + sh + 16)
