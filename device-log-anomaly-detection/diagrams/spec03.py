# 03 — Isolation-forest score as an annotated curve (B3).
# Type: threshold curve s(E[h]) for psi = 256, plus a 2-D isolation sketch and a defaults panel.
from _common import *

S = Src()
W = 1280
B, E, L = [], [], []
c = raw("iforest_c_256")
hl = raw("iforest_height_limit_psi256")
B.append(title("An isolation-forest score is a normalised path length, not a probability: a window "
               "isolated in 3 random splits scores %s; one at the average path scores %s"
               % (fmt(raw("iforest_score_3_splits_psi256")), fmt(raw("iforest_score_at_average_path"))), W))

# ---------- chart ----------
ax = Axes(90, 110, 600, 360, (0, 16), (0, 1))
fb, fl = ax.frame("a", [0, 2, 4, 6, 8, 10, 12, 14, 16], [0, 0.2, 0.4, 0.6, 0.8, 1.0],
                  "E(h(x)) = mean splits needed to isolate the window, over the forest",
                  "anomaly score s(x)")
B += fb; L += fl
# shaded regions (drawn first; lines that must show set top=True)
B.append(box("zA", ax.X(0), ax.Y(1.0), ax.X(3) - ax.X(0), ax.Y(0.8) - ax.Y(1.0),
             "", RED, RED_S, rounded=False, dash="4,3", sw=1))
B.append(text("zAl", ax.X(3) + 4, ax.Y(1.0) + 2, 220, 30,
              "near 1: few, different -> anomalous", font=10.5, color=RED_S, bold=True))
pts = [(ax.X(e / 10.0), ax.Y(2 ** (-(e / 10.0) / c))) for e in range(0, 161)]
L.append(dict(pts=pts, color=BLUE_S, sw=3, top=True))
B.append(text("curve", ax.X(0.6), ax.Y(0.34), 230, 34,
              "s = 2^(-E(h) / c(psi)), psi = %s, c(256) = %s" % (
                  S.v("iforest_subsample_size_default", u=""), S.v("iforest_c_256", u="")),
              font=10.5, color=BLUE_S, bold=True))
# reference lines
L.append(hline(ax.X(0), ax.X(16), ax.Y(0.5), color=AMBER_S, sw=1.5, dash="6,4", top=True))
B.append(text("l05", ax.X(0.2), ax.Y(0.5) + 2, 250, 30,
              "s = 0.5: E(h) equals c(psi); if all windows sit here, no distinct anomaly",
              font=10, color=AMBER_S))
L.append(vline(ax.X(hl), ax.Y(1.0), ax.Y(0), color=GREY_S, sw=1.5, dash="3,3", top=True))
B.append(text("lhl", ax.X(hl) + 4, ax.Y(0.12), 150, 30,
              "height limit ceil(log2 256) = %s" % S.v("iforest_height_limit_psi256", u=""),
              font=10, color="#555555"))
L.append(vline(ax.X(c), ax.Y(0.5), ax.Y(0), color=AMBER_S, sw=1, dash="2,3", top=True))
# marked points
p3 = raw("iforest_score_3_splits_psi256")
B.append(box("p3", ax.X(3) - 6, ax.Y(p3) - 6, 12, 12, "", RED, RED_S, rounded=False, sw=2))
B.append(text("p3l", ax.X(3) + 10, ax.Y(p3) - 4, 210, 30,
              "3 splits -> s = %s" % S.v("iforest_score_3_splits_psi256", u=""),
              font=11, bold=True, color=RED_S))
B.append(dict(id="pc", x=ax.X(c) - 6, y=ax.Y(0.5) - 6, w=12, h=12, label="", fill=AMBER,
              stroke=AMBER_S, sw=2, shape="ellipse"))
B.append(text("pcl", ax.X(c) + 6, ax.Y(0.5) - 34, 200, 30,
              "%s splits -> s = %s" % (S.v("iforest_c_256", u="", tag=False),
                                       S.v("iforest_score_at_average_path", u="")),
              font=11, bold=True, color=AMBER_S))
B.append(text("lowl", ax.X(11), ax.Y(0.3), 190, 30,
              "well below 0.5: deep in the crowd -> normal", font=10.5, color=GREEN_S, bold=True))

# ---------- right: 2-D isolation sketch ----------
sx, sy, sw_, sh_ = 760, 100, 500, 220
B.append(panel("sk", sx, sy, sw_, sh_, "", fill="#ffffff", stroke=GREY_S))
B.append(text("skt", sx + 6, sy + 4, sw_ - 12, 34,
              "**Why short paths mean anomalous** (sketch, two template counts per window): random "
              "cuts isolate the odd window (red) in 3 cuts; a window inside the crowd needs many.",
              font=10.5))
import random
random.seed(7)
for i in range(26):
    px = sx + 250 + random.gauss(0, 34)
    py = sy + 150 + random.gauss(0, 22)
    B.append(dict(id="d%d" % i, x=round(px, 1), y=round(py, 1), w=8, h=8, label="", fill=GREEN,
                  stroke=GREEN_S, sw=1.2, shape="ellipse"))
ox, oy = sx + 440, sy + 70
B.append(box("out", ox, oy, 10, 10, "", RED, RED_S, rounded=False, sw=2))
L.append(vline(sx + 380, sy + 42, sy + sh_, color=AMBER_S, sw=1.5, dash="5,3", top=True))
L.append(hline(sx + 380, sx + sw_, sy + 110, color=AMBER_S, sw=1.5, dash="5,3", top=True))
L.append(vline(sx + 420, sy + 42, sy + 110, color=AMBER_S, sw=1.5, dash="5,3", top=True))
for k, (tx, ty) in enumerate([(sx + 383, sy + 196), (sx + 466, sy + 112), (sx + 404, sy + 46)]):
    B.append(text("cut%d" % k, tx, ty, 30, 16, "cut %d" % (k + 1), font=10, color=AMBER_S,
                  bold=True))

# ---------- right: defaults + threshold ----------
B.append(panel("defs", 760, 334, 500, 100,
               "**Defaults and the threshold** [B3]\n"
               "- each tree is built on a sub-sample of psi = %s; the forest has t = %s\n"
               "- c(n) = 2H(n-1) - 2(n-1)/n with H(i) = ln(i) + %s\n"
               "- scikit-learn contamination='auto' uses offset %s on the shifted score; a numeric "
               "contamination flags that share of the training data. It is your alarm budget, "
               "not a property of the data." % (
                   S.v("iforest_subsample_size_default", tag=False),
                   S.v("iforest_trees_default"), S.v("euler_mascheroni", u=""),
                   S.v("sklearn_iforest_offset_auto", u="")), font=10.5))

YL = 520
B.append(panel("conf", 20, YL, 1240, 32,
               "**Read the score correctly** [B3]: %s means 'easy to isolate', not '%d %% likely to be "
               "a bug'. Train on windows from devices believed healthy, or the forest learns faults as "
               "normal. It flags environmental anomalies too, so a second signal decides [C4]." %
               (fmt(p3), round(p3 * 100)), fill=AMBER, stroke=AMBER_S, font=10.5))
B.append(panel("legend", 20, YL + 42, 1240, 30,
               "**Legend** — blue line = the score formula (exact); red square = the worked anomalous "
               "window; amber circle + dashed = the s = 0.5 reference; grey dotted = tree height limit; "
               "green dots = normal windows. Curve computed from c(256) loaded from constants.json.",
               font=10.5))
n = S.footnote_lines()
sy2 = YL + 82
sh = int(12.5 * n + 22)
B.append(sources(S, 20, sy2, 1240, sh))
PAGE = dict(name="03-isolation-forest-score", w=W, h=sy2 + sh + 14)
BOXES, EDGES, LINES = B, E, L
