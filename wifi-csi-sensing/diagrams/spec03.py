# -*- coding: utf-8 -*-
# 03 - The per-link processing chain: preprocessing (B1) -> window + features (B2) -> classifier (B3).
# Source: notes B1, B2, B3. Numbers loaded from constants.json.
from _common import *

t = Tags()
PAGE = dict(name="03-processing-chain", w=1280, h=902)

mad = V("hampel_mad_scale"); thr = V("hampel_threshold_typical"); hw = V("hampel_halfwidth_illustrative")
w1, w4 = V("window_short_illustrative"), V("window_long_illustrative")
drop = V("fft_high_freq_drop_illustrative")
mlp = V("mlp_hidden_units_illustrative")
ng = V("beamforming_grouping_ng")
keep = V("subcarrier_keep_fraction_illustrative")
cost = V("subcarrier_selection_cost_illustrative")
gain = V("preprocessing_gain_illustrative")
acf = V("acf_vs_variance_illustrative")
sf = V("single_feature_tpr_illustrative")
rnd, day = V("split_random_accuracy_illustrative"), V("split_heldout_day_accuracy_illustrative")
hs = V("home_spread_illustrative")

STEPS = [
    ("raw", "Raw CSI report\none frame: |H| per\nsubcarrier, with a\nreal timestamp [A2]", GREY, GREY_S),
    ("s1", "1  Power-normalise\ndivide by L2 norm\n(removes AGC gain\njumps)", BLUE, BLUE_S),
    ("s2", "2  Drop bad\nsubcarriers\nguard-adjacent,\nvery low amplitude", BLUE, BLUE_S),
    ("s3", "3  Background\nmoving average per\nsubcarrier = static\nchannel", BLUE, BLUE_S),
    ("s4", "4  Dynamics\namplitude minus\nbackground = the\nmotion part [A1]", BLUE, BLUE_S),
    ("s5", "5  Energy series\nL2 norm of the\ndynamics: one\nnumber per report", BLUE, BLUE_S),
    ("s6", "6  Hampel filter\nflag if > %s x %s MAD\nfrom the median of\n+/-%s reports %s%s%s" % (
        fmt(thr), fmt(mad), fmt(hw), t("hampel_threshold_typical"), t("hampel_mad_scale"),
        t("hampel_halfwidth_illustrative")), BLUE, BLUE_S),
    ("s7", "7  Replace\nflagged reports\nwith the window\nmedian", BLUE, BLUE_S),
    ("s8", "8  Smooth\n(optional)\nexponential\nmoving average", BLUE, BLUE_S),
]

BOXES = [
    title("The signal chain moved the result more than the model did: cheap preprocessing, features whose scale "
          "does not depend on the room, then any small classifier", 1280, 15),
    dict(id="row1_lbl", x=31, y=54, w=900, h=20, rounded=False, align="left", valign="middle", font=11, bold=True,
         fill="none", stroke="none", fontcolor=BLUE_S,
         label="PREPROCESSING [B1] - every step is a median, a norm or a moving average"),
]
for i, (sid, lbl, f, s) in enumerate(STEPS):
    BOXES.append(dict(id=sid, x=30 + i * 136, y=78, w=124, h=96, fill=f, stroke=s, font=10.5, label=lbl,
                      bold=False))

BOXES += [
    dict(id="row2_lbl", x=150, y=210, w=900, h=20, rounded=False, align="left", valign="middle", font=11, bold=True,
         fill="none", stroke="none", fontcolor=GREEN_S,
         label="FEATURES [B2] and CLASSIFIER [B3] - one window on one link at a time"),
    dict(id="win", x=30, y=240, w=190, h=150, fill=GREY, stroke=GREY_S, font=11,
         label="Window\nK subcarriers x L reports\non one link\n\nillustrative %s s or %s s %s%s"
               % (fmt(w1), fmt(w4), t("window_short_illustrative"), t("window_long_illustrative"))),
    dict(id="f_acf", x=270, y=240, w=330, h=46, fill=GREEN, stroke=GREEN_S, font=10.5, align="left",
         label="ACF (lag 1, averaged over subcarriers): ~1 when still, falls toward 0 with motion; lies in "
               "[-1, 1] in every room"),
    dict(id="f_pca", x=270, y=292, w=330, h=46, fill=GREEN, stroke=GREEN_S, font=10.5, align="left",
         label="PCA eigenvalues of the K x K covariance: still = one dominant eigenvalue; motion spreads energy "
               "to the 2nd and later"),
    dict(id="f_fft", x=270, y=344, w=330, h=46, fill=GREEN, stroke=GREEN_S, font=10.5, align="left",
         label="FFT per subcarrier, DC bin REMOVED (it encodes the room) and the top %s of bins dropped as noise %s"
               % ("third" if abs(drop - 1 / 3) < 0.01 else pct(drop), t("fft_high_freq_drop_illustrative"))),
    dict(id="clf", x=650, y=240, w=300, h=150, fill=PURPLE, stroke=PURPLE_S, font=10.5, align="left",
         label="Classifier ladder [B3]\n- threshold on one feature\n- SVM (RBF kernel)\n- small MLP on FFT features, "
               "illustrative %d + %d hidden units %s\n- (sequence / CNN models: too little data)\nScore -> threshold set "
               "by the false-alarm budget [C1]" % (mlp[0], mlp[1], t("mlp_hidden_units_illustrative"))),
    dict(id="out", x=1000, y=240, w=250, h=150, fill=AMBER, stroke=AMBER_S, font=11, bold=True,
         label="Per-link, per-window motion probability\n\n-> fused across all links of the home [B4]"),

    # design-choice cards
    dict(id="c_grp", x=30, y=406, w=295, h=66, fill="#ffffff", stroke=BLUE_S, font=10.5, align="left", valign="top",
         label="Group adjacent subcarriers (Ng = %d; 802.11 uses Ng in %s %s): NO loss, %dx less data. Adjacent "
               "subcarriers are strongly correlated [B1]." % (ng[2], "/".join(str(x) for x in ng),
                                                               t("beamforming_grouping_ng"), ng[2])),
    dict(id="c_sel", x=338, y=406, w=295, h=66, fill="#ffffff", stroke=BLUE_S, font=10.5, align="left", valign="top",
         label="Keep only the top %s of subcarriers %s by mean amplitude: about %d TPR points lost, about %s of "
               "feature compute saved %s (illustrative)." % (pct(keep), t("subcarrier_keep_fraction_illustrative"),
                                                             cost["tpr_drop_points"], pct(cost["compute_saved"]),
                                                             t("subcarrier_selection_cost_illustrative"))),
    dict(id="c_res", x=646, y=406, w=295, h=66, fill="#ffffff", stroke=RED_S, font=10.5, align="left", valign="top",
         label="DO NOT resample to a uniform time grid: interpolation manufactured smooth samples where reports "
               "were missing and clearly hurt detection. Use real timestamps [B1, A2]."),
    dict(id="c_ph", x=954, y=406, w=296, h=66, fill="#ffffff", stroke=RED_S, font=10.5, align="left", valign="top",
         label="Phase: random offsets per report. Sanitise only with 2+ receive antennas (linear fit, conjugate "
               "product, CSI ratio). A single-stream link uses amplitude only [A2, B1]."),

    # evidence
    dict(id="ev1", x=30, y=484, w=610, h=84, fill=GREEN, stroke=GREEN_S, font=11, align="left", valign="top",
         label="What the studies showed (ILLUSTRATIVE values, direction is the lesson):\n"
               "- preprocessing raised average TPR by about %d points, and by about %d points in the hardest "
               "scenarios (room with no device, small motion, near the AP) %s\n"
               "- single link, TPR at 1%% FPR: variance %s, ACF lag 1 %s %s; FFT + small net %s %s"
               % (gain["average_points"], gain["hardest_case_points"], t("preprocessing_gain_illustrative"),
                  fmt(acf["variance"]), fmt(acf["acf_tap1"]), t("acf_vs_variance_illustrative"),
                  fmt(sf["fft_plus_nn"]), t("single_feature_tpr_illustrative"))),
    dict(id="ev2", x=654, y=484, w=596, h=84, fill=RED, stroke=RED_S, font=11, align="left", valign="top",
         label="How the result must be tested (ILLUSTRATIVE):\n"
               "- same features and classifier: %s accuracy on a random split, %s on an unseen day %s%s - "
               "split by time and by home, never at random [B3]\n"
               "- leave-one-home-out: best home %s TPR, worst home %s %s - the home is the unit of generalisation"
               % (fmt(rnd), fmt(day), t("split_random_accuracy_illustrative"),
                  t("split_heldout_day_accuracy_illustrative"), fmt(hs["best_home_tpr"]), fmt(hs["worst_home_tpr"]),
                  t("home_spread_illustrative"))),
    legend_box("legend", 30, 580, 1220, 44,
               "Legend: grey = input / window | blue = preprocessing step (red-outlined cards = traps) | green = "
               "room-independent feature, green panel = evidence | purple = classifier | amber = output | red panel "
               "= evaluation trap.  [A1]-[C1] = kit notes; [n] = constants.json entries below."),
]

EDGES = [dict(src=STEPS[i][0], dst=STEPS[i + 1][0], color=BLUE_S, sx=1, sy=0.5, dx=0, dy=0.5)
         for i in range(len(STEPS) - 1)]
EDGES += [
    dict(src="win", dst="f_acf", color=GREEN_S, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="win", dst="f_pca", color=GREEN_S, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="win", dst="f_fft", color=GREEN_S, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="f_acf", dst="clf", color=PURPLE_S, sx=1, sy=0.5, dx=0, dy=0.3),
    dict(src="f_pca", dst="clf", color=PURPLE_S, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="f_fft", dst="clf", color=PURPLE_S, sx=1, sy=0.5, dx=0, dy=0.7),
    dict(src="clf", dst="out", color=AMBER_S, bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
]
# wrap from the end of row 1 down to the window
x8 = 30 + 8 * 136 + 62
LINES = [
    dict(x1=x8, y1=174, x2=x8, y2=200, color=GREY_S, width=1.5),
    dict(x1=x8, y1=200, x2=125, y2=200, color=GREY_S, width=1.5),
    dict(x1=125, y1=200, x2=125, y2=238, color=GREY_S, width=1.5, arrow="classic"),
]

BOXES.append(sources_box(30, 636, 1220, 250, t.foot(
    "Notes: [A1] multipath; [A2] hardware; [B1] preprocessing; [B2] features; [B3] classifiers and windows; [B4] joint "
    "detection; [C1] KPIs. Public refs: Hampel 1974, Pearson 2002 (Hampel/MAD); Zhang et al. 2018-2019 (ACF); Wang "
    "et al. 2015 (CARM, PCA); Kotaru et al. 2015, Li et al. 2017, Zeng et al. 2019 (phase); Cortes and Vapnik 1995 (SVM)."), 9.5))
