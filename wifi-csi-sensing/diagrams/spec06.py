# -*- coding: utf-8 -*-
# 06 - KPIs start from a false-alarm budget: the per-window FPR a product needs vs the research "1% FPR".
# Source: note C1 (four-stage KPI ladder, six KPIs, false-alarm arithmetic, time to detect/clear, per-scenario,
#         field shortfall). Arithmetic computed here from constants.json (labelled "my arithmetic", as in C1).
import math
from _common import *

t = Tags()
PAGE = dict(name="06-false-alarm-budget", w=1280, h=800)

S = V("seconds_per_30_days")
win = V("window_short_illustrative")
budget = V("false_alarm_budget_illustrative")
field = V("field_tpr_vs_target_illustrative")
research_fpr = 0.01                          # the usual research operating point "TPR at 1% FPR" [B3, C1]
windows = S / win                            # decisions per 30 days at one decision per window
fa_research = research_fpr * windows         # false windows per month at 1% FPR
fpr_budget = budget / windows                # per-window FPR the budget allows
orders = math.log10(research_fpr / fpr_budget)

SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
AX, TOP, DEC = 150, 112, 56                   # axis x, y of 10^-1, px per decade


def Y(f):
    return TOP + (-1 - math.log10(f)) * DEC


BOXES = [
    title("\"1%% FPR\" is about %s false alarms per home per month - a budget of %d needs a per-window FPR near "
          "%.1f x 10⁻⁶: fix the budget first" % (fmt(int(round(fa_research, -3))), budget, fpr_budget * 1e6), 1280, 15),
    dict(id="chart", x=30, y=58, w=620, h=470, rounded=False, align="left", valign="top", font=11, bold=True,
         fill="none", stroke=NOTE_S,
         label="Per-window false-positive rate (log scale) and what it means at one decision per %s s %s"
               % (fmt(win), t("window_short_illustrative"))),
    dict(id="ax_l", x=36, y=Y(1e-7) + 22, w=240, h=36, rounded=False, align="left", valign="top", font=9.5,
         fill="none", stroke="none", fontcolor="#555555",
         label="left: per-window FPR | right of axis: false\nalarms per 30 days %s (my arithmetic)" % t("seconds_per_30_days")),
]
for k in range(1, 8):
    f = 10.0 ** -k
    y = Y(f)
    BOXES.append(dict(id="tk%d" % k, x=AX - 64, y=int(y - 9), w=58, h=18, rounded=False, align="right",
                      valign="middle", font=10, fill="none", stroke="none", label="10" + ("-%d" % k).translate(SUP)))
    BOXES.append(dict(id="tm%d" % k, x=AX + 6, y=int(y + 2), w=90, h=16, rounded=False, align="left",
                      valign="middle", font=9, fill="none", stroke="none", fontcolor="#777777",
                      label="%s / month" % fmt(int(round(f * windows))) if f * windows >= 1 else
                      "%.2f / month" % (f * windows)))

BOXES += [
    dict(id="res", x=300, y=int(Y(research_fpr) - 26), w=330, h=52, fill=RED, stroke=RED_S, font=10.5,
         align="left", label="Research operating point: TPR at 1%% FPR [B3]\n= about %s false windows per month "
                             "(my arithmetic)" % fmt(int(round(fa_research, -3)))),
    dict(id="bud", x=300, y=int(Y(fpr_budget) - 26), w=330, h=52, fill=GREEN, stroke=GREEN_S, font=10.5,
         align="left", label="Product budget: an illustrative %d false alarms per home per month %s\n-> per-window "
                             "FPR near %.1f x 10⁻⁶ if every false window counts" % (budget,
                             t("false_alarm_budget_illustrative"), fpr_budget * 1e6)),
    dict(id="gap", x=330, y=int(Y(research_fpr) + 40), w=290, h=96, rounded=False, align="left", valign="middle",
         font=11, bold=True, fill="none", stroke="none", fontcolor=RED_S,
         label="gap: about %.1f orders of magnitude\n(3 to 4, my arithmetic)\nPartly closed by: merging touching "
               "false windows into one EVENT; requiring several positive windows in a row - both cost latency [C1]"
               % orders),

    # right: the KPI ladder
    dict(id="lad_h", x=670, y=58, w=580, h=24, rounded=False, align="left", valign="middle", font=12, bold=True,
         fill="none", stroke="none", label="The KPI ladder: four stages, same six KPIs at each [C1]"),
    dict(id="col_home", x=790, y=86, w=225, h=24, rounded=False, fill="none", stroke="none", font=10.5, bold=True,
         label="home level"),
    dict(id="col_room", x=1025, y=86, w=225, h=24, rounded=False, fill="none", stroke="none", font=10.5, bold=True,
         label="room level"),
    dict(id="row_m", x=670, y=114, w=110, h=70, rounded=False, fill="none", stroke="none", font=10.5, bold=True,
         align="right", label="motion\n(person moves)"),
    dict(id="row_p", x=670, y=192, w=110, h=70, rounded=False, fill="none", stroke="none", font=10.5, bold=True,
         align="right", label="presence\n(moving or still)"),
    dict(id="st1", x=790, y=114, w=225, h=70, fill=GREEN, stroke=GREEN_S, font=10.5,
         label="1  motion anywhere in the home?\nhard part: non-human change"),
    dict(id="st2", x=1025, y=114, w=225, h=70, fill=BLUE, stroke=BLUE_S, font=10.5,
         label="2  which room has motion?\nhard part: adjacent rooms through walls"),
    dict(id="st3", x=790, y=192, w=225, h=70, fill=AMBER, stroke=AMBER_S, font=10.5,
         label="3  anyone home, moving or still?\nhard part: a still person barely changes the CSI"),
    dict(id="st4", x=1025, y=192, w=225, h=70, fill=RED, stroke=RED_S, font=10.5,
         label="4  which room is a person in?\nhard part: both of the above"),
    dict(id="six", x=670, y=274, w=580, h=96, fill="#ffffff", stroke=GREY_S, font=10.5, align="left", valign="top",
         label="Six KPIs per stage: TPR, FPR, TNR, FNR (wrong room counts as a miss), BLIND-SPOT ratio (area or rooms "
               "where errors exceed a threshold), EFFECTIVE-COVERAGE ratio (area or rooms where TPR and TNR both pass). "
               "The last two turn an average into a map: a good average can still fail one room every day."),
    dict(id="time", x=670, y=380, w=580, h=66, fill="#ffffff", stroke=GREY_S, font=10.5, align="left", valign="top",
         label="Time to detect (start of motion -> first positive) and time to clear (exit -> \"empty\"): report both as "
               "distributions with a high percentile, not a mean. State window-level vs event-level for every number."),
    dict(id="fld", x=670, y=456, w=580, h=72, fill=RED, stroke=RED_S, font=10.5, align="left", valign="top",
         label="Why it matters (ILLUSTRATIVE): a lab demo looked near-perfect before false-positive cases were tested; "
               "the later field study at the product budget reached about %s TPR against a target of %s %s. Causes: CSI "
               "outliers, drift over time, chip CSI quality [C1]." % (fmt(field["achieved"]), fmt(field["target"]),
                                                                      t("field_tpr_vs_target_illustrative"))),
    legend_box("legend", 30, 540, 1220, 44,
               "Legend: red = research operating point / field shortfall | green = product budget, stage 1 | blue, "
               "amber, red stages = increasing difficulty | grey ticks = false alarms per 30 days at that FPR. Report "
               "every KPI per scenario (near a device, near the AP, door, far, room with no device, small motion, still, "
               "empty) [C1, C2]."),
]

LINES = [dict(x1=AX, y1=Y(1e-1), x2=AX, y2=Y(1e-7), color="#333333", width=1.5)]
for k in range(1, 8):
    LINES.append(dict(x1=AX - 5, y1=Y(10.0 ** -k), x2=620, y2=Y(10.0 ** -k), color="#e2e2e2", width=1, under=True))
LINES += [
    dict(x1=AX, y1=Y(research_fpr), x2=300, y2=Y(research_fpr), color=RED_S, width=2.5),
    dict(x1=AX, y1=Y(fpr_budget), x2=300, y2=Y(fpr_budget), color=GREEN_S, width=2.5),
    dict(x1=315, y1=Y(research_fpr) + 28, x2=315, y2=Y(fpr_budget) - 30, color=RED_S, width=2, arrow="classic"),
]
EDGES = []

BOXES.append(sources_box(30, 596, 1220, 92, t.foot(
    "Arithmetic (my arithmetic, as in [C1]): decisions per 30 days = seconds_per_30_days / window; false windows at "
    "1% FPR = 0.01 x that; budget FPR = budget / decisions. Notes: [B3] TPR at fixed FPR; [C1] KPIs; [C2] scenario "
    "taxonomy. Public ref: Fawcett 2006 (ROC)."), 9.5))
PAGE["h"] = 702
