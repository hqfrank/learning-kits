# 02 — From a raw line to a count vector (A1, B1, B2, C2).
# Type: pipeline with an index-tree strip, a window timeline and a toy count matrix.
from _common import *

S = Src()
W = 1280
B, E, L = [], [], []
B.append(title("Parsing and windowing turn free text into a count matrix: every column is a "
               "template an engineer can read, and the order of events inside a window is lost", W))

# ---------- row A: line -> template + parameters ----------
YA = 80
B.append(text("ha", 20, YA, 600, 18, "**A. Parse one line** [A1, B1]", font=12))
B.append(box("raw", 20, YA + 22, 400, 70,
             "**raw line** (logcat threadtime layout)\n"
             "date time pid tid level tag: message\n"
             "... 812 845 I wpa_supplicant: CTRL-EVENT-DISCONNECTED "
             "bssid=aa:bb:cc:dd:ee:ff reason=3 locally_generated=1",
             GREY, GREY_S, align="left", valign="top", font=10.5))
B.append(box("tpl", 460, YA + 22, 400, 70,
             "**template** = constant words, parameters replaced by <*>\n"
             "CTRL-EVENT-DISCONNECTED bssid=<*> reason=<*> locally_generated=<*>\n"
             "-> one stable template ID (a vocabulary of a few hundred, e.g. %s)" %
             S.v("templates_per_component_set"),
             GREEN, GREEN_S, align="left", valign="top", font=10.5))
B.append(box("par", 900, YA + 22, 360, 70,
             "**parameters** = the run-time values, kept\n"
             "[aa:bb:cc:dd:ee:ff, 3, 1]\n"
             "reason %s = deauthenticated because leaving (IEEE 802.11); parameters often "
             "name the cause [B5]" % S.v("ieee80211_reason_deauth_leaving", u=""),
             AMBER, AMBER_S, align="left", valign="top", font=10.5))
E.append(dict(src="raw", dst="tpl", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))
E.append(dict(src="tpl", dst="par", sx=1, sy=0.5, dx=0, dy=0.5, color=INK, sw=2))

# ---------- row B: parse-tree matcher + template source ----------
YB = YA + 106
B.append(text("hb", 20, YB, 800, 18,
              "**B. Match it fast: a parse-tree matcher over a fixed template set** [B1]", font=12))
names = [("t1", "layer 1\ncomponent (tag)"), ("t2", "layer 2\ntoken count"),
         ("t3", "one layer per token\npartial-token wildcards keep event=<*> and error=<*> apart"),
         ("t4", "leaf\ntemplate ID")]
xs, ws = [20, 175, 330, 600], [130, 130, 245, 120]
for (i, lab), x, w in zip(names, xs, ws):
    B.append(box(i, x, YB + 24, w, 62, lab, BLUE, BLUE_S, font=10.5))
for a, b in [("t1", "t2"), ("t2", "t3"), ("t3", "t4")]:
    E.append(dict(src=a, dst=b, sx=1, sy=0.5, dx=0, dy=0.5, color=BLUE_S, sw=2))
B.append(box("unm", 175, YB + 104, 545, 40,
             "no template matches -> **unmatched bucket**: engineers review, add templates, "
             "rebuild the tree [C2]", RED, RED_S, font=10.5, dash="6,4"))
L.append(dict(pts=[(452, YB + 86), (452, YB + 104)], color=RED_S, sw=1.5, dash="4,3",
              arrow="end"))
B.append(panel("srcp", 740, YB + 24, 520, 120,
               "**Where templates come from** [B1]\n"
               "- mining (Drain, Spell) finds only what is in the sample. Example: a component with "
               "%s, about %s on error or warning paths; a miner on normal logs finds %s. "
               "The missing ones are the error paths detection needs.\n"
               "- source-code extraction: complete, but needs source access and upkeep.\n"
               "- Drain speed: %s faster than the best online parser of its time, on %s with more "
               "than %s." % (
                   S.v("component_print_statements"), S.v("component_error_warning_share", u="%"),
                   S.v("miner_templates_found"), S.v("drain_runtime_improvement"),
                   S.v("drain_eval_datasets"), S.v("drain_eval_messages_min")),
               font=10.5))

# ---------- row C: windows on a timeline ----------
YC = YB + 166
B.append(text("hc", 20, YC, 700, 18, "**C. Cut the parsed stream into windows** [B2]", font=12))
ax0, pxh = 120, 22.0          # 22 px per hour, 24 h = 528 px
day = raw("window_example", "day"); win = raw("window_example", "window")
step = raw("window_example", "step")
ty = YC + 150
L.append(hline(ax0, ax0 + day * pxh, ty, sw=1.2))
for h in range(0, int(day) + 1, 6):
    L.append(vline(ax0 + h * pxh, ty, ty + 5, sw=1.2))
    B.append(text("tk%d" % h, ax0 + h * pxh - 20, ty + 6, 40, 14, "%d h" % h, font=10,
                  align="center"))
# fixed: consecutive windows
B.append(text("lf", 20, YC + 28, 96, 16, "fixed", font=10.5, bold=True))
for i in range(int(day / win)):
    B.append(box("fx%d" % i, ax0 + i * win * pxh, YC + 28, win * pxh, 16, "", BLUE, BLUE_S,
                 rounded=False, sw=1))
# sliding: first few overlapping windows
B.append(text("ls", 20, YC + 56, 96, 30, "sliding\n(first 6 shown)", font=10.5, bold=True))
for i in range(6):
    x = ax0 + i * step * pxh
    B.append(box("sl%d" % i, x, YC + 54 + i * 7, win * pxh, 6, "", AMBER, AMBER_S,
                 rounded=False, sw=1))
B.append(text("ls2", ax0 + 6 * step * pxh + 30, YC + 60, 420, 30,
              "a device-day of %s, window %s, step %s -> %s (my arithmetic; overlapping rows are "
              "not independent)" % (
                  S.v("window_example", "day", u="h"), S.v("window_example", "window", u="h", tag=False),
                  S.v("window_example", "step", u="h", tag=False),
                  S.v("window_example", "windows", u="windows", tag=False)), font=10))
B.append(text("lss", 20, YC + 106, 96, 30, "session", font=10.5, bold=True))
for i, (a, b) in enumerate([(1.0, 3.5), (5.0, 6.2), (9.0, 13.0), (15.5, 16.5), (19.0, 22.5)]):
    B.append(box("ss%d" % i, ax0 + a * pxh, YC + 106, (b - a) * pxh, 16, "", GREEN, GREEN_S,
                 rounded=False, sw=1))
B.append(text("lss2", 20, ty + 22, 640, 30,
              "session = one execution path, needs an ID (HDFS block IDs; device logs rarely have "
              "one). Public defaults (BGL): fixed %s, sliding %s with step %s." % (
                  S.v("he2016_fixed_window_default"),
                  S.v("he2016_sliding_window_default", "window", u="h"),
                  S.v("he2016_sliding_window_default", "step", u="h", tag=False)), font=10))

# ---------- row C right: toy count matrix ----------
mx, my = 720, YC + 24
B.append(text("hm", mx, YC, 540, 18,
              "**D. Count templates per window: the event count matrix** [B2]", font=12))
cols = ["T1", "T2", "T3", "T4", "T5"]
rows = [("w1", [4, 0, 1, 0, 2]), ("w2", [5, 0, 1, 0, 1]), ("w3", [4, 3, 0, 6, 2]),
        ("w4", [1, 1, 1, 0, 0]), ("w5", [1, 1, 1, 0, 0])]
cw, ch = 46, 22
for j, c in enumerate(cols):
    B.append(box("mc%d" % j, mx + 60 + j * cw, my, cw, ch, c, GREEN, GREEN_S, rounded=False,
                 font=10.5, bold=True, sw=1))
for i, (r, vals) in enumerate(rows):
    hot = r == "w3"
    B.append(box("mr%d" % i, mx, my + (i + 1) * ch, 60, ch, r, BLUE, BLUE_S, rounded=False,
                 font=10.5, bold=True, sw=1))
    for j, v in enumerate(vals):
        B.append(box("m%d_%d" % (i, j), mx + 60 + j * cw, my + (i + 1) * ch, cw, ch, str(v),
                     RED if hot else "#ffffff", RED_S if hot else GREY_S, rounded=False,
                     font=10.5, sw=1))
B.append(text("mnote", mx, my + 6 * ch + 4, 290, 44,
              "toy counts, not data. w3 has unusual counts (red): the kind of row an isolation "
              "forest isolates fast [B3].", font=10))
B.append(box("ord", mx + 310, my, 230, 128,
             "**order is lost**\n"
             "w4 = T1 T2 T3\nw5 = T1 T3 T2\nsame vector [1, 1, 1, 0, 0]\n"
             "an order fault is invisible to counts -> transition edges [B5]",
             RED, RED_S, font=10.5, dash="6,4", align="left", valign="top"))

# trade-off strip
YT = YC + 210
B.append(panel("trade", 20, YT, 1240, 46,
               "**Window length is a design choice** [B2]: longer -> denser vector, frequency "
               "changes easier to see, but a short burst is diluted and the earliest alarm is later. "
               "Shorter -> faster, better time localisation, but mostly zeros and normal jitter "
               "looks large. Set it from the fault classes you care about.", fill=AMBER,
               stroke=AMBER_S, font=10.5))
B.append(panel("legend", 20, YT + 56, 1240, 30,
               "**Legend** — grey = raw text; green = templates / template columns; amber = "
               "parameters, sliding windows and design choices; blue = index layers, fixed windows "
               "and window rows; red dashed = where information is lost or left unmatched.",
               font=10.5))
n = S.footnote_lines()
sy = YT + 96
sh = int(12.5 * n + 22)
B.append(sources(S, 20, sy, 1240, sh))
PAGE = dict(name="02-line-to-count-vector", w=W, h=sy + sh + 14)
BOXES, EDGES, LINES = B, E, L
