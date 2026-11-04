# 07 — The camera, one load at a time (note B1, "The camera is different"). Public kit.
# Every number via V() from ../constants.json, tagged by key.
from _charts import *

W, H = 1440, 800
PAGE = dict(name="07-camera-one-load-at-a-time", w=W, h=H)
T = Tags()

hz = V("camera_hz_alone")
gpu_loss = V("camera_gpu_only_loss_hz")
pool = V("camera_pool_loss_hz")
fan = V("camera_fanout_loss_hz")
full = V("camera_full_stack_loss_hz")
# x position of each pool arm = its camera CPU wait relative to the full stack's camera wait,
# read from the field NAME of camera_pool_loss_hz (half / twice the full stack's wait).
POS = {"half_full_wait": 0.5, "twice_full_wait": 2.0}
CUR, CUR_S = "#b9dfb0", "#3f7f33"
YR = (-1, 8)
yt = [0, 2, 4, 6, 8]

BOXES = [title("GPU load alone costs the depth camera service no frames; shared-pool CPU wait costs it frames (%s Hz "
               "at half the full stack's wait %s; the higher arm is void), so the pool verdict is \"undecided at "
               "dose\"" % (f(pool["half_full_wait"]), T("camera_pool_loss_hz", field="half_full_wait")), W, h=60,
               font=20)]
LINES, EDGES = [], []

# ---------------- GPU panel ----------------
BOXES.append(panel("gp", 20, 84, 480, 440, "", fill="none", stroke=GREY_S))
BOXES.append(text("gh", 30, 90, 460, 34, "**Factor 1: GPU compute co-tenant, idle CPU pool**", font=12))
ga = Axes(90, 150, 330, 250, (0, 1.3), YR)
b, l = ga.frame("g", [(0, "none"), (1, "max")], yt,
                "GPU dose; max = highest tested (no dose values here)",
                "camera loss vs alone (Hz)", zero=0)
BOXES += b; LINES += l
LINES.append(hline(ga.X(0), ga.X(1.3), ga.Y(full), GREY_S, 1.5, dash="6,4", top=True))
BOXES.append(text("gfl", ga.X(0) + 4, ga.Y(full) - 20, 320, 18,
                  "full stack, all loads together: %s Hz %s" % (f(full), T("camera_full_stack_loss_hz")),
                  font=9.5, color="#555555"))
LINES.append(dict(pts=[(ga.X(0), ga.Y(gpu_loss)), (ga.X(1), ga.Y(gpu_loss))], color=CUR_S, sw=3, top=True))
for i, x in enumerate((0.25, 0.5, 0.75, 1)):
    BOXES.append(dot("ga%d" % i, ga.X(x), ga.Y(gpu_loss), 6, CUR, CUR_S))
BOXES.append(text("gal", ga.X(0.1), ga.Y(gpu_loss) - 40, 300, 32,
                  "%s Hz at every GPU dose tested %s (dot count and spacing schematic)"
                  % (f(gpu_loss), T("camera_gpu_only_loss_hz")),
                  font=9.5, color=CUR_S))
LINES.append(dict(pts=[(ga.X(1.02), ga.Y(1.6)), (ga.X(1.28), ga.Y(1.6))], color=INK, sw=1.2, dash="3,3",
                  arrow="end", top=True))
BOXES.append(text("gbe", ga.X(0.62), ga.Y(3.4), 230, 30,
                  "full stack + VLA dose: beyond the highest GPU arm (not tested)", font=9.5, align="right"))
BOXES.append(dict(id="gv", x=60, y=456, w=400, h=56, fill=GPU, stroke=GPU_S, rounded=True, font=10.5,
                  label="**\"GPU minor\"**: no measurable loss at any GPU dose tested.\nA substantial GPU share "
                        "had been predicted: **the prediction was wrong.**"))

# ---------------- pool panel ----------------
PX = 515
BOXES.append(panel("pp", PX, 84, 480, 440, "", fill="none", stroke=GREY_S))
BOXES.append(text("ph", PX + 10, 90, 460, 34, "**Factor 2: shared-pool CPU load** %s" % T("camera_pool_loss_hz"),
                  font=12))
pa = Axes(PX + 70, 150, 380, 250, (0, 2.5), YR)
BOXES.append(bar("above", pa.X(1), pa.y, pa.X(2.5) - pa.X(1), pa.h, "#f2f2f2", "none"))
b, l = pa.frame("p", [0, 0.5, 1, 1.5, 2, 2.5], yt,
                "camera's CPU wait ÷ the full stack's camera wait", "camera loss vs alone (Hz)", zero=0)
BOXES += b; LINES += l
LINES.append(vline(pa.X(1), pa.y, pa.y + pa.h, INK, 1.2, dash="4,3", top=True))
BOXES.append(text("abl", pa.X(1.05), pa.Y(1.5), 170, 30, "above the full stack's wait:\nno valid arm", font=9.5,
                  color="#555555"))
arms = [(0.0, 0.0, True, "alone (0 by definition)")] + \
       [(POS[k], pool[k], k == "half_full_wait", k) for k in ("half_full_wait", "twice_full_wait")]
# post-hoc dotted line through all arms, the void one included
LINES.append(dict(pts=[(pa.X(x), pa.Y(y)) for x, y, _, _ in arms], color=CPU_S, sw=1.8, dash="1,4", top=True))
for i, (x, y, ok, k) in enumerate(arms):
    BOXES.append(dot("pa%d" % i, pa.X(x), pa.Y(y), 7, CPU2 if (ok and i) else "#ffffff", CPU_S,
                     dash=None if ok else "3,2", sw=2))
BOXES.append(text("pal1", pa.X(0.03), pa.Y(2.0), 140, 30,
                  "**valid arm**, half the wait:\n%s Hz" % f(pool["half_full_wait"]), font=9.5, color=CPU_S))
BOXES.append(text("pal2", pa.X(2) - 172, pa.Y(pool["twice_full_wait"]) - 46, 180, 36,
                  "twice the wait: %s Hz\n**VOID** (failed the rate gate)" % f(pool["twice_full_wait"]),
                  font=9.5, align="right", color=CPU_S))
BOXES.append(dot("fs", pa.X(1), pa.Y(full), 7, INK, INK, square=True))
BOXES.append(text("fsl", pa.X(1) - 168, pa.Y(full) - 18, 160, 30, "**full stack**, all loads\ntogether: %s Hz"
                  % f(full), font=9.5, align="right"))
BOXES.append(dict(id="pv", x=PX + 40, y=456, w=400, h=56, fill=CPU, stroke=CPU_S, rounded=True, font=10.5,
                  label="**\"undecided at dose\"**: the one valid arm lies below the full stack's wait; the higher "
                        "arm is VOID, so it cannot decide the class."))

# ---------------- share strip: what explains the full stack's loss ----------------
SY = 540
BOXES.append(panel("sp", 20, SY, 975, 120, "", fill="none", stroke=GREY_S))
BOXES.append(text("sh", 30, SY + 6, 955, 34,
                  "**Factor 3: the full stack's extra topic subscribers (fan-out)** cost %s Hz %s. Each factor's "
                  "part of the full stack's %s Hz camera loss:" % (f(fan), T("camera_fanout_loss_hz"), f(full)),
                  font=11.5))
px = 820.0 / full
x0 = 140
BOXES.append(text("sl", 30, SY + 46, 104, 30, "loss, Hz", font=10.5, align="right", valign="middle"))
segs = [(fan, "fan-out %s Hz, share %s" % (f(fan), f(round(fan / float(full), 2))), "none", CPU_S, None),
        (gpu_loss, "", GPU, GPU_S, None),
        (full - fan - gpu_loss, "rest %s Hz: not attributed (pool share undecided; loads not tested together)"
         % f(full - fan - gpu_loss), "#ffffff", GREY_S, "4,3")]
for k, (v, lab, fill, st, dash) in enumerate(segs):
    if k == 0 and v > 0:
        # light-blue hatch = CPU-side cost (drawn under the transparent bar, so the label stays on top)
        bx, by, bw, bh = x0, SY + 46, v * px, 30
        d = 0
        while d < bw + bh:
            x_a, y_a, x_b, y_b = bx + d - bh, by + bh, bx + d, by
            if x_a < bx:
                y_a -= bx - x_a; x_a = bx
            if x_b > bx + bw:
                y_b += x_b - (bx + bw); x_b = bx + bw
            if x_b > x_a:
                LINES.append(dict(pts=[(x_a, y_a), (x_b, y_b)], color=CPU2, sw=1.5))
            d += 9
    if v > 0:
        BOXES.append(bar("ss%d" % k, x0, SY + 46, v * px, 30, fill, st, dash=dash, label=lab, font=9.5))
    x0 += v * px
BOXES.append(text("sft", 140, SY + 82, 840, 32,
                  "GPU part %s Hz (no segment). Shares are %s; a post-hoc reading that keeps the VOID arm gives the "
                  "pool a larger part and does not replace the verdict."
                  % (f(gpu_loss), T.est("camera_fanout_loss_hz", "camera_full_stack_loss_hz",
                                        "camera_gpu_only_loss_hz")), font=9.5))

# ---------------- right column ----------------
RX, RW = 1010, 410
BOXES += [
    dict(id="ctx", x=RX, y=84, w=RW, h=72, fill=NOTE, stroke=NOTE_S, rounded=True, font=10.5, align="left",
         valign="top",
         label="**Setup.** The depth camera service keeps %s Hz alone %s. One factor per window, idle pool unless "
               "the factor is the pool. In the full stack it falls to %s Hz (%s)."
               % (f(hz), T("camera_hz_alone"), f(hz - full), T.est("camera_hz_alone", "camera_full_stack_loss_hz"))),
    dict(id="verd", x=RX, y=166, w=RW, h=90, fill="#ffffff", stroke=INK, rounded=True, font=10.5, align="left",
         valign="top",
         label="**Pre-registered verdicts**\n• GPU: **minor**. No loss at any GPU dose tested.\n• Shared pool: "
               "**\"undecided at dose\"**. The valid arm is below the full stack's wait.\n• Fan-out: **a minor "
               "share**, about one fifth of the full-stack loss."),
    dict(id="cav", x=RX, y=266, w=RW, h=124, fill="#ffffff", stroke="#333333", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Caveats.** **The three loads were not tested together.** The GPU arms ran with frame-time slack "
               "that the full stack does not leave, and the full stack + VLA dose lies beyond the highest GPU arm. "
               "The two panels use different x axes; the black square is the same full-stack reference on the pool "
               "axis. The dotted line joins all pool arms, the VOID one included (post-hoc reading). Values are an "
               "illustrative measurement."),
    dict(id="so", x=RX, y=400, w=RW, h=90, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Correction kept visible.** The camera's loss is CPU-side; GPU load alone costs it nothing. **Read "
               "with page 06**: the detector's GPU wait follows the others' GPU share, the camera's frame rate does "
               "not. Same GPU, different victims: the dose curve is per service, not per board (interpretation)."),
]

# ---------------- bottom ----------------
leg = ("**Legend**\ngreen line + circles = GPU arms (valid), no dose values given\nfilled blue circle = valid pool "
       "arm; hollow dashed blue circle = VOID window\nhollow solid blue circle = alone (zero loss by definition)\n"
       "black square = full-stack reference (all loads)\ngrey dashed line = full-stack loss level\ngrey shading = "
       "pool waits above the full stack's\ndotted = post-hoc reading; light-blue hatch = fan-out (CPU-side)")
BOXES.append(panel("legend", 20, 672, 470, 112, leg, font=10))
src, sh = sources_panel("src", 502, 672, 918, T,
                        "Note B1, \"The camera is different\". Pool-arm x positions come from the field names of "
                        "camera_pool_loss_hz (half / twice the full stack's wait). How to benchmark a robot stack: "
                        "../../robot-workload-benchmarking/.", font=9.5)
sh = int(sh * 0.8)  # the helper's line estimate runs high for this renderer
src["h"] = sh
BOXES.append(src)
PAGE["h"] = max(672 + 112, 672 + sh) + 12
