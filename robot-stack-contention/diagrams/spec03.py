# 03 — Where the object detector's frame goes (notes A1, B1). Numbers via V() from ../constants.json.
from _common import *

W = 1460
PAGE = dict(name="03-where-the-detectors-frame-goes", w=W, h=760)
T = Tags()

solo, full = V("detector_frame_ms_solo_full")
aw, ar, ab = V("detector_added_wait_run_blocked")
vb, vw, vr = V("detector_vla_added_blocked_wait_run")
vla_tot = full + vb + vw + vr          # my estimate
assert solo + aw + ar + ab == full     # the illustrative split sums to the full-stack frame

X0 = 230; S = 2.8  # px per ms (to scale)
xs = lambda ms: X0 + ms * S
BH = 64
BLK, BLK_S = "#b9dfb0", "#3f7f33"   # blocked (mostly GPU) — green, solid border
WAI, WAI_S = "#9fc0e8", "#2f5d9a"   # run-queue wait (CPU) — mid blue, solid border
RUN, RUN_S = "#dae8fc", "#6c8ebf"   # run (CPU) — light blue, dashed border
BASE, BASE_S = "#e4e4e4", "#888888"

BOXES = [title("The object detector's frame: from alone to the full stack it grows mostly by CPU terms (run-queue "
               "wait + slower run); from the full stack to full stack + VLA it grows mostly by GPU-blocked time",
               W, h=60, font=20)]
LINES = []


def seg(id, y, a, b, label, fill, stroke, dash=None, font=11):
    BOXES.append(dict(id=id, x=round(xs(a), 1), y=y, w=round((b - a) * S, 1), h=BH, label=label, fill=fill,
                      stroke=stroke, dash=dash, rounded=False, font=font, sw=1.5))


Y = [84, 194, 304]
names = ["**Alone**\n%s" % T("detector_frame_ms_solo_full"),
         "**Full stack**\n%s" % T("detector_added_wait_run_blocked"),
         "**Full stack + VLA**\n%s" % T("detector_vla_added_blocked_wait_run")]
for i, n in enumerate(names):
    BOXES.append(text("n%d" % i, 14, Y[i], X0 - 24, BH, n, font=10.5, align="right", valign="middle"))

seg("solo", Y[0], 0, solo, "alone frame %s ms\n(alone frame not split)" % f(solo), BASE, BASE_S)
seg("fb", Y[1], 0, solo, "alone frame %s ms" % f(solo), BASE, BASE_S)
seg("fw", Y[1], solo, solo + aw, "+%s\nwait" % f(aw), WAI, WAI_S)
seg("fr", Y[1], solo + aw, solo + aw + ar, "+%s\nrun" % f(ar), RUN, RUN_S, dash="5,3")
seg("fk", Y[1], solo + aw + ar, full, "+%s\nblocked" % f(ab), BLK, BLK_S, font=10)
BOXES.append(text("ftot", xs(full) + 6, Y[1] + 20, 120, 24, "= **%s ms**" % f(full), font=12))
seg("vb0", Y[2], 0, full, "full-stack frame %s ms" % f(full), BASE, BASE_S)
seg("vk", Y[2], full, full + vb, "+%s\nblocked" % f(vb), BLK, BLK_S)
seg("vw", Y[2], full + vb, full + vb + vw, "+%s\nwait" % f(vw), WAI, WAI_S, font=10)
seg("vr", Y[2], full + vb + vw, vla_tot, "+%s\nrun" % f(vr), RUN, RUN_S, dash="5,3", font=10)
BOXES.append(text("vtot", xs(vla_tot) - 600, Y[2] + BH + 6, 606, 36,
                  "= about **%s ms** (%s)" % (f(vla_tot), T.est("detector_frame_ms_solo_full",
                                                               "detector_vla_added_blocked_wait_run")),
                  font=10.5, align="right"))

ya = 434
LINES.append(dict(pts=[(X0, ya), (xs(vla_tot), ya)], color="#444444", sw=1.2))
for t in range(0, int(vla_tot) + 1, 50):
    LINES.append(dict(pts=[(xs(t), ya), (xs(t), ya + 6)], color="#444444", sw=1.2))
    BOXES.append(text("tk%d" % t, xs(t) - 20, ya + 7, 40, 16, "%d" % t, font=10, align="center"))
BOXES.append(text("axl", X0, ya + 24, xs(vla_tot) - X0, 18,
                  "ms per frame (the detector's own per-frame log, split by the inventory script)", font=10.5,
                  align="center"))

add1 = aw + ar + ab
add2 = vb + vw + vr
BOXES += [
    dict(id="ann1", x=1110, y=Y[1] - 8, w=330, h=BH + 16, fill=CPU, stroke=CPU_S, rounded=True, font=10.5,
         align="left", valign="middle",
         label="**alone -> full stack: mostly CPU.** Wait + run = %s of +%s ms added; wait alone = %s of it "
               "(%s). Clocks locked, so not frequency."
               % (f(aw + ar), f(add1), f(aw / float(add1), 1), T.est("detector_added_wait_run_blocked"))),
    dict(id="ann2", x=1110, y=Y[2] - 8, w=330, h=BH + 16, fill=GPU, stroke=GPU_S, rounded=True, font=10.5,
         align="left", valign="middle",
         label="**full stack -> + VLA: mostly GPU.** Blocked +%s of +%s ms added = %s (%s): GPU time-slicing "
               "between CUDA contexts (page 05)."
               % (f(vb), f(add2), f(vb / float(add2), 1), T.est("detector_vla_added_blocked_wait_run"))),
]

py = 492
BOXES += [
    dict(id="corr", x=30, y=py, w=450, h=74, fill=CORR, stroke=CORR_S, dash="6,4", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Correction kept visible.** Step 1 first said the pool changes from the full stack to full "
               "stack + VLA were \"within round-to-round spread\". Withdrawn: one full stack + VLA round had no "
               "speech in its window. With voice on in both, pool wait rises. The GPU step is still the larger "
               "change."),
    dict(id="cav", x=495, y=py, w=480, h=74, fill="#ffffff", stroke="#333333", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Caveats.** \"Blocked\" = neither running nor waiting for a CPU (mostly GPU sync; also locks, "
               "I/O). The GPU mechanism was tested in a camera-plus-detector row with an idle pool; in the full "
               "stack it is expected, not tested (note B1). The + VLA total is my sum of the added terms."),
    dict(id="rate", x=990, y=py, w=450, h=74, fill="#ffffff", stroke=GREY_S, rounded=True, font=10.5,
         align="left", valign="top",
         label="**What each term means.** Wait = runnable, no free pool core (note A1, page 02). Added run = "
               "the same instructions needing more cycles (note A2, page 04). Blocked next to the VLA = waiting "
               "for other contexts' GPU turns (note B1, page 05)."),
]
ly = py + 86
legend = ("**Legend** grey = the previous level's frame; mid-blue, solid border = added run-queue wait (CPU); "
          "light blue, dashed border = added run time (CPU); green, solid border = added blocked time (mostly "
          "GPU sync); every term is also named in its bar. Bar lengths to scale (%s px per ms)." % f(S))
src, hs = sources_panel("src", 645, ly, 795, T,
                        "Numbers loaded from ../constants.json by spec03.py; key in brackets. Notes A1 "
                        "(per-frame decomposition, correction), B1 (the rise next to the VLA).", font=9.5)
hl = int(est_lines(legend, 600, 10.5) * 13.2 + 16)
BOXES.append(panel("legend", 30, ly, 600, max(hs, hl), legend, font=10.5))
BOXES.append(src)
PAGE["h"] = ly + max(hs, hl) + 16
EDGES = []
