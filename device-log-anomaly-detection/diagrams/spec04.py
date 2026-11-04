# 04 — Fleet trend test: weight each day by n, test the slope against s, score the p-value (A2, B4).
# Type: error-bar comparison + a step flow + a p -> score ladder.
from _common import *

S = Src()
W = 1280
B, E, L = [], [], []
n_small, n_large = raw("small_family_devices"), raw("large_family_devices")
k = raw("rare_reason_devices")
share = 100.0 * k / n_small  # my arithmetic from illustrative inputs
se_s, se_l = raw("rare_share_small_family_se"), raw("rare_share_large_family_se")
B.append(title("The same %s %% jump can be noise in %s devices but is a fleet change in %s: the share's "
               "standard error shrinks with sqrt(n), so the trend test weights each day by n (illustrative counts)"
               % (fmt(share), fmt(n_small), fmt(n_large)), W))

# ---------- left: error bars ----------
B.append(panel("cp", 20, 80, 550, 400, "", fill="none", stroke=GREY_S))
B.append(text("cpt", 28, 84, 534, 34,
              "**Share of devices that emitted a rare disconnect reason, one day** [A2]\n"
              "dot = share; bar = +/- 1 standard error, SE = sqrt(p(1-p)/n)", font=10.5))
ax = Axes(110, 150, 420, 210, (0.5, 2.5), (0, 6))
fb, fl = ax.frame("a", [], [0, 1, 2, 3, 4, 5, 6], "", "share of devices (%)")
B += fb; L += fl
for i, (n, se, col, cs, lab) in enumerate([
        (n_small, se_s, RED, RED_S, "small family\n%s active,\n%s emit it\nSE = %s" % (
            S.v("small_family_devices", u=""), S.v("rare_reason_devices", u=""),
            S.v("rare_share_small_family_se", u="pp"))),
        (n_large, se_l, GREEN, GREEN_S, "large family\n%s active\nsame share\nSE = %s" % (
            S.v("large_family_devices", u=""), S.v("rare_share_large_family_se", u="pp")))]):
    x = ax.X(i + 1)
    L += [vline(x, ax.Y(share - se), ax.Y(share + se), color=cs, sw=3, top=True),
          hline(x - 10, x + 10, ax.Y(share - se), color=cs, sw=3, top=True),
          hline(x - 10, x + 10, ax.Y(share + se), color=cs, sw=3, top=True)]
    B.append(dict(id="dt%d" % i, x=x - 7, y=ax.Y(share) - 7, w=14, h=14, label="", fill=col,
                  stroke=cs, sw=2, shape="ellipse"))
    B.append(text("bl%d" % i, x - 95, ax.Y(0) + 6, 190, 66, lab, font=10.5, align="center",
                  color=cs, bold=True))
B.append(text("cpn", 28, 420, 534, 56,
              "Halve n and SE grows by sqrt 2. Three unlucky households can make the small-family "
              "jump; the large-family bar is ten times tighter (sqrt of 100x the devices). "
              "Share %s %% = %s / %s, my arithmetic." % (fmt(share), fmt(k), fmt(n_small)),
              font=10))
B[-1]["y"] = 438
B[-1]["h"] = 40

# ---------- right: the test, step by step ----------
steps = [
    ("1 one series per slice", "daily share p_t and active count n_t per (family, feature, "
     "category) over %s" % S.v("trend_series_length", "weeks", u="weeks")
     + " (%s daily points)" % fmt(raw("trend_series_length", "daily_points"))),
    ("2 not ordinary least squares", "Var(p_t) = p(1-p)/n_t changes day to day (weekends, outages, "
     "new cohorts): heteroscedastic; OLS gives a noisy day the same say and a wrong slope SE"),
    ("3 weighted least squares", "weight w_t = n_t / (p_t(1-p_t)); minimise sum w_t (p_t - a - b t)^2. "
     "Use a pooled p when p_t is 0 or 1 (infinite weight)"),
    ("4 test against a practical slope s", "H0: b = s (not b = 0: with enough devices every slope is "
     "significant). One-sided p = 1 - Phi((b_hat - s) / se(b_hat))"),
    ("5 p-value -> score", "score = -%s log10(p), capped at %s; see the ladder below" % (
        S.v("phred_factor", u=""), S.v("score_cap", u=""))),
    ("6 filter direction, control false discoveries", "drop good-direction changes; %s tested at "
     "p 0.01 give about %s by chance -> FDR control or rank and read the top" % (
         S.v("monitored_series", u="series/day"), S.v("multiple_testing_false_alarms", u="series/day"))),
]
y = 80
for i, (h, d) in enumerate(steps):
    B.append(box("st%d" % i, 590, y, 670, 56, "**%s** [B4]: %s" % (h, d),
                 AMBER if i in (3, 4) else BLUE, AMBER_S if i in (3, 4) else BLUE_S,
                 align="left", valign="middle", font=10.5))
    if i:
        E.append(dict(src="st%d" % (i - 1), dst="st%d" % i, sx=0.04, sy=1, dx=0.04, dy=0,
                      color=BLUE_S, sw=1.5))
    y += 66

# ---------- score ladder ----------
YS = 500
B.append(text("lh", 20, YS, 600, 18, "**p -> score ladder** (each 10 points = 10x smaller p) [B4]",
              font=12))
ex = raw("score_examples")
S.tag("score_examples")
labels = [("p_0.1", "0.1"), ("p_0.01", "0.01"), ("p_1e-5", "1e-5"), ("p_1e-10", "1e-10 (cap)")]
for i, (kk, pl) in enumerate(labels):
    sc = ex[kk]
    h = 34 + sc * 0.7
    B.append(box("sc%d" % i, 20 + i * 140, YS + 130 - h, 120, h,
                 "p = %s\nscore %s %s" % (pl, fmt(sc), S.tag("score_examples")),
                 AMBER, AMBER_S, rounded=False, font=10.5, valign="top"))

# ---------- family vs device level ----------
B.append(box("fam", 590, YS + 30, 330, 100,
             "**Family level** [B4]: WLS slope test on the share. Catches fleet-wide regressions "
             "(a release that raises disconnects). Few reports (e.g. %s per week), each high impact." %
             S.v("family_reports_per_week", u=""), BLUE, BLUE_S, align="left", valign="top",
             font=10.5))
B.append(box("devl", 930, YS + 30, 330, 100,
             "**Device level** [B3, B4]: isolation forest on device-day vectors. Catches one device "
             "or household behaving oddly. Many reports, each lower impact and often environmental.",
             PURPLE, PURPLE_S, align="left", valign="top", font=10.5))

YL = YS + 146
B.append(panel("conf", 20, YL, 1240, 32,
               "**Read it correctly** [B4]: the score is a confidence that the slope exceeds s, not a "
               "severity; a significant trend can be a router-firmware rollout, a holiday or a reporting "
               "change. Correlated daily residuals make se(b) too small: check with a weekly dummy.",
               fill=AMBER, stroke=AMBER_S, font=10.5))
B.append(panel("legend", 20, YL + 42, 1240, 30,
               "**Legend** — red = small population (noisy); green = large population (precise); blue = "
               "estimation steps; amber = the decision steps (threshold, score); purple = device-level "
               "detection. pp = percentage points.", font=10.5))
n = S.footnote_lines()
sy = YL + 82
sh = int(12.5 * n + 20)
B.append(sources(S, 20, sy, 1240, sh))
PAGE = dict(name="04-fleet-trend-test", w=W, h=sy + sh + 14)
BOXES, EDGES, LINES = B, E, L
