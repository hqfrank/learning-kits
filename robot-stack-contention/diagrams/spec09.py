# 09 — The ridge on two boards (note B4). Public kit.
# Board ceilings are sibling keys; the vision encoder and its forms are illustrative; ridges and Thor forms are
# my arithmetic from those keys. Roofs: rate = intensity x bandwidth up to the ridge, then the compute ceiling.
from _charts import *

W, H = 1440, 800
PAGE = dict(name="09-ridge-two-boards", w=W, h=H)
T = Tags()

oc = V("tensor_fp16_orin")
obw = V("dram_read_orin")
tc = V("tensor_fp16_thor")
tbw = V("pi05_sustained_bandwidth_thor")
s0, s1 = V("shape_rate_fraction")
enc = V("vision_encoder")
I = enc["intensity_flop_per_byte"]
tflop = enc["tflop"]
o_bw_ms = V("vision_pred_bandwidth_form_ms")
o_c0, o_c1 = V("vision_compute_form_ms")
o_meas = V("vision_measured_ms_orin")
tbw_rd = V("dram_read_thor")

# my arithmetic
ridge = lambda c, bw: c * 1000.0 / bw          # TFLOP/s / GB/s -> FLOP/B
o_r, t_r = ridge(oc, obw), ridge(tc, tbw)
o_rs = (ridge(oc * s0, obw), ridge(oc * s1, obw))
t_rs = (ridge(tc * s0, tbw), ridge(tc * s1, tbw))
weights_gb = tflop * 1000.0 / I                 # TFLOP / (FLOP/B) -> GB
t_bw_ms = weights_gb / tbw * 1000.0
t_c_roof_ms = tflop / tc * 1000.0
t_c_shape = (tflop / (tc * s1) * 1000.0, tflop / (tc * s0) * 1000.0)
r1 = lambda x: f(round(x, 1))
r2 = lambda x: f(round(x, 2))
n1 = lambda x: round(x, 1)
n2 = lambda x: round(x, 2)
VIS, VIS_S = "#eadcf2", "#7b4f9d"
DD = "8,3,2,3"  # dash-dot for Thor

BOXES = [title("The same vision encoder sits well above the Orin's ridge (compute-bound: the compute form is right) "
               "but near Thor's effective ridge, where neither form alone is safe (illustrative encoder, sibling "
               "ceilings)", W, h=60, font=20)]
LINES, EDGES = [], []

ax = Axes(110, 128, 700, 450, (30, 3000), (2, 300), xlog=True, ylog=True)
b, l = ax.frame("a", [30, 100, 300, 1000, 3000], [2, 5, 10, 20, 50, 100, 200],
                "arithmetic intensity (FLOP per byte of DRAM traffic), log scale",
                "attainable rate (TFLOP/s), log scale")
BOXES += b; LINES += l
g = lambda bw, i: bw * i / 1000.0  # TFLOP/s on a bandwidth roof (my arithmetic)

# shape-rate bands (where GEMMs at the model's own shapes run)
for nm, c, bw, col, fill, rs in [("o", oc, obw, ORIN, "#dbe7f5", o_rs), ("t", tc, tbw, THOR, "#fbe3cc", t_rs)]:
    BOXES.append(bar("band" + nm, ax.X(rs[0]), ax.Y(c * s1), ax.X(3000) - ax.X(rs[0]), ax.Y(c * s0) - ax.Y(c * s1),
                     fill, col, dash="2,2", sw=1))
# vision intensity line
LINES.append(vline(ax.X(I), ax.y, ax.y + ax.h, VIS_S, 2.2, dash="6,3", top=True))
BOXES.append(text("vl", ax.X(I) - 196, ax.y + 4, 190, 58, "**vision encoder**, weight side\n%s FLOP/B %s"
                  % (f(I), T("vision_encoder", field="intensity_flop_per_byte")), font=9.5, align="right",
                  color=VIS_S))


def roof(c, bw, ridge_x, color, dash):
    LINES.append(dict(pts=[(ax.X(30), ax.Y(g(bw, 30))), (ax.X(ridge_x), ax.Y(c))], color=color, sw=2.4,
                      dash=dash, top=True))
    LINES.append(dict(pts=[(ax.X(ridge_x), ax.Y(c)), (ax.X(3000), ax.Y(c))], color=color, sw=2.4, dash=dash,
                      top=True))


roof(oc, obw, o_r, ORIN, None)
roof(tc, tbw, t_r, THOR, DD)

# ridge bars under the plot (shape range thin, roof ridge as a tick)
for k, (r, rs, col, nm) in enumerate([(o_r, o_rs, ORIN, "Orin"), (t_r, t_rs, THOR, "Thor")]):
    y = ax.y + ax.h - 16 - k * 30
    BOXES.append(bar("rb%d" % k, ax.X(rs[0]), y, ax.X(rs[1]) - ax.X(rs[0]), 10, col, col))
    LINES.append(vline(ax.X(r), y - 4, y + 14, col, 2.5, top=True))
BOXES.append(text("rl0", ax.X(30.5), ax.y + ax.h - 26, 170, 28,
                  "Orin ridge (FLOP/B):\nshapes %s, roof %s" % (rng(round(o_rs[0]), round(o_rs[1])), f(round(o_r))),
                  font=9, color=ORIN))
BOXES.append(text("rl1", ax.X(380) - 196, ax.y + ax.h - 56, 190, 28,
                  "Thor ridge (FLOP/B):\nshapes %s, roof %s" % (rng(round(t_rs[0]), round(t_rs[1])), f(round(t_r))),
                  font=9, color=THOR, align="right"))

# roof and band labels (right part of the chart)
BOXES += [
    text("tcl", ax.X(560), ax.Y(tc) - 36, 250, 32, "**Thor** tensor FP16\n%s TFLOP/s %s"
         % (f(tc), T("tensor_fp16_thor")), font=9.5, color=THOR),
    text("tsl", ax.X(1150), ax.Y(tc * s1) + 2, 260, 30, "Thor at shapes %s TFLOP/s\n(%s)"
         % (rng(n1(tc * s0), n1(tc * s1)), "x " + rng(s0, s1)), font=9, color=THOR),
    text("ocl", ax.X(800), ax.Y(oc) - 30, 300, 28, "**Orin** tensor FP16 %s TFLOP/s %s"
         % (f(oc), T("tensor_fp16_orin")), font=9.5, color=ORIN),
    text("osl", ax.X(1150), ax.Y(oc * s1) + 2, 260, 30, "Orin at shapes %s TFLOP/s\n%s"
         % (rng(n1(oc * s0), n1(oc * s1)), T("shape_rate_fraction")), font=9, color=ORIN),
    text("obl", ax.X(45), ax.Y(g(obw, 45)) + 10, 220, 30, "Orin DRAM read %s GB/s %s" % (f(obw), T("dram_read_orin")),
         font=9.5, color=ORIN),
    text("tbl", ax.X(31), 250, 200, 44, "Thor DRAM %s GB/s, sustained by a pi0.5-class VLA %s"
         % (f(tbw), T("pi05_sustained_bandwidth_thor")), font=9.5, color=THOR),
]

# ---------------- right: the two forms in ms ----------------
RX, RW = 850, 570
BOXES.append(panel("fp", RX, 84, RW, 318, "", fill="none", stroke=GREY_S))
BOXES.append(text("fh", RX + 10, 90, RW - 20, 34, "**Vision time: the two forms of the prediction vs an illustrative "
                  "measurement** (ms; %s TFLOP, weights about %s GB, %s)"
                  % (f(tflop), f(round(weights_gb, 2)), T.est("vision_encoder")), font=11))
fx = Axes(RX + 170, 140, 360, 200, (0, 32), (0, 1))
for i, t in enumerate(range(0, 33, 4)):
    LINES.append(vline(fx.X(t), 140, 350, "#e6e6e6", 1))
    BOXES.append(text("fxt%d" % i, fx.X(t) - 15, 352, 30, 14, str(t), font=9.5, align="center"))
BOXES.append(text("fxl", fx.X(32) + 8, 352, 24, 14, "ms", font=10))
rows = [
    ("Orin: bandwidth form\n(the first prediction)", (0, o_bw_ms), ORIN, "5,3", "#ffffff",
     "%s ms %s" % (f(o_bw_ms), T("vision_pred_bandwidth_form_ms"))),
    ("Orin: compute form", (o_c0, o_c1), ORIN, None, CPU, "%s ms %s" % (rng(o_c0, o_c1), T("vision_compute_form_ms"))),
    ("Thor: bandwidth form", (0, t_bw_ms), THOR, DD, "#fff3e8", "about %s ms" % r1(t_bw_ms)),
    ("Thor: compute, at roof", (0, t_c_roof_ms), THOR, None, "#fbd3ad", "about %s ms" % r1(t_c_roof_ms)),
    ("Thor: compute, at shapes", t_c_shape, THOR, None, "#fbd3ad", "about %s ms" % rng(n1(t_c_shape[0]), n1(t_c_shape[1]))),
]
for i, (nm, (a, bb), col, dash, fill, lab) in enumerate(rows):
    y = 144 + i * 40 + (20 if i >= 2 else 0)
    BOXES.append(text("fn%d" % i, RX + 6, y - 4, 158, 32, "**%s**" % nm, font=9.5, align="right", valign="middle"))
    BOXES.append(bar("fb%d" % i, fx.X(a), y + 2, fx.X(bb) - fx.X(a), 20, fill, col, dash=dash))
    if bb > 20:  # label to the left of a bar that ends near the right edge
        BOXES.append(text("fl%d" % i, fx.X(a) - 224, y + 4, 220, 30, lab, font=9, color=col, align="right"))
    else:
        BOXES.append(text("fl%d" % i, fx.X(bb) + 4, y - 2, 200, 30, lab, font=9, color=col))
LINES.append(hline(RX + 10, RX + RW - 10, 236, GREY_S, 1, dash="6,4"))
LINES.append(vline(fx.X(o_meas), 140, 224, INK, 2.5, top=True))
BOXES.append(text("om", fx.X(o_meas) - 304, 210, 300, 16,
                  "**measured %s ms** %s" % (f(o_meas), T("vision_measured_ms_orin")), font=9, align="right"))
BOXES.append(text("tnm", RX + 10, 370, RW - 20, 30,
                  "Thor rows: my estimates from `vision_encoder`, `pi05_sustained_bandwidth_thor`, `tensor_fp16_thor` "
                  "and `shape_rate_fraction`. No Thor vision time is given here.", font=9))
T.reg("pi05_sustained_bandwidth_thor", "tensor_fp16_thor", "shape_rate_fraction")

# ---------------- right: readings ----------------
BOXES += [
    dict(id="orin", x=RX, y=412, w=RW, h=80, fill=CPU, stroke=CPU_S, rounded=True, font=10.5, align="left",
         valign="top",
         label="**Orin: the form was what mattered.** Intensity ÷ ridge is about %s at the roof, %s at the "
               "shapes, so the encoder is compute-bound and the compute form brackets the measurement. The "
               "bandwidth form misses by about %s times (%s): the wrong form, not a slow encoder."
               % (r1(I / o_r), rng(n1(I / o_rs[1]), n1(I / o_rs[0])), r1(o_meas / float(o_bw_ms)),
                  T.est("vision_measured_ms_orin", "vision_pred_bandwidth_form_ms"))),
    dict(id="thor", x=RX, y=502, w=RW, h=80, fill="#fff3e8", stroke=THOR, dash=DD, rounded=True, font=10.5,
         align="left", valign="top",
         label="**Thor: the data do not decide.** Intensity ÷ ridge is about %s at the roof, %s at the shapes: the "
               "two forms give about the same time, so either roof could bind. Thor's compute roof is about %s× "
               "the Orin's, its bandwidth only about %s× (my estimate from the four sibling keys)."
               % (r2(I / t_r), rng(n2(I / t_rs[1]), n2(I / t_rs[0])), r1(tc / oc), r1(tbw / obw))),
]

# ---------------- bottom ----------------
BH = 118
BOXES += [
    dict(id="cav", x=20, y=630, w=470, h=BH, fill="#ffffff", stroke="#333333", rounded=True, font=10.5,
         align="left", valign="top",
         label="**Caveats.** The weight-side intensity is an upper bound for one pass; counting all DRAM traffic "
               "lowers it and moves the encoder toward the ridge on both boards. The shape-rate fraction is "
               "illustrative and **applied to Thor by assumption**. Thor's bandwidth is a sustained value from a "
               "VLA, not a read peak: with Thor's read peak (%s GB/s %s) the ridge is about %s FLOP/B (%s), about %s× "
               "the Orin's roof ridge rather than about %s×; the encoder stays near it. Axes are approximate; the "
               "labelled values are exact."
               % (f(tbw_rd), T("dram_read_thor"), f(round(ridge(tc, tbw_rd))),
                  T.est("tensor_fp16_thor", "dram_read_thor"), f(round(ridge(tc, tbw_rd) / o_r)),
                  f(round(t_r / o_r)))),
    panel("legend", 502, 630, 400, BH,
          "**Legend**\nblue solid = Orin roofs; orange dash-dot = Thor roofs\nshaded dotted bands = GEMM rate at "
          "the model's own shapes\npurple dashed = the encoder's weight-side intensity\nright: dashed outline = the first prediction; black line = measurement\nbars under the plot = ridge at shapes; tick = at the roof",
          font=10),
]
src, sh = sources_panel("src", 914, 630, 506, T,
                        "Note B4. Roofline and ridge: ../../jetson-orin-thor-metrics/ (glossary, note C1). Ridges, "
                        "weights and Thor times are my arithmetic.", font=9.5)
sh = int(sh * 0.8)  # the helper's line estimate runs high for this renderer
src["h"] = sh
BOXES.append(src)
PAGE["h"] = max(630 + BH, 630 + sh) + 12
