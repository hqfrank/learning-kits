# -*- coding: utf-8 -*-
# 05 — Gaze: layers, the ordered gates (when unsure, hold), the frame rule, glide not saccade, duty (note B3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="05-gaze-gates", w=W, h=0)

BOXES = [title("Gaze: aim the head only on trustworthy evidence, through gates in a fixed order where every failed gate means HOLD STILL, "
               "because a confident wrong turn tells a group the robot is talking to someone else", W, h=46)]
LINES = []
EDGES = []

# --- layers ---------------------------------------------------------------------------
ly = 70
layers = [
    ("L1", "ATTRIBUTION\nwho, and their bearing in ITS camera frame", VISIT),
    ("L2", "FACE SELECTOR\nhysteresis, dropout grace", VISIT),
    ("L3", "INTEREST LAYER\nwhat should the head do? one cell of the state matrix", LLM),
    ("L4", "GAZE POLICY\nmay I aim now? the ordered gates below", GATE),
    ("L5", "HEAD CONTROLLER\neased glide, nod overlay", BODY),
    ("L6", "ROBOT GATEWAY\nframe composition, limits, the only publisher", GREY),
]
lw_, gap = 186, 21
for i, (id_, lab, pal) in enumerate(layers):
    BOXES.append(box(id_, 30 + i * (lw_ + gap), ly, lw_, 56, lab, pal, font=10.5))
    if i:
        EDGES.append(dict(src=layers[i - 1][0], dst=id_, sx=1, sy=0.5, dx=0, dy=0.5, color=GREY_C))
BOXES.append(text("lay_n", 30, ly + 60, 1220, 18,
                  "The policy emits INTENT, never angles. Decision code is pure: driven by injected inputs and a clock, testable without a robot, camera or middleware. "
                  "Whom the speech is FOR comes from the reasoner's triage verdict, not from vision.",
                  font=10, fontcolor="#444444"))

# --- the gates --------------------------------------------------------------------------
gy = 168
BOXES.append(text("g_h", 30, gy, 620, 20, "THE GAZE POLICY: ordered gates (the order is the safety argument)", bold=True, font=12))
db = V("gaze_deadband_illustrative"); t_db = T("gaze_deadband_illustrative")
dw = V("gaze_dwell_illustrative"); t_dw = T("gaze_dwell_illustrative")
sgh = V("sector_glance_hold_illustrative"); t_sgh = T("sector_glance_hold_illustrative")
sgb = V("sector_glance_box_illustrative"); t_sgb = T("sector_glance_box_illustrative")
gates = [
    "1 STALENESS: never act on an old label",
    "2 EVIDENCE: lock-eligible (mouth-motion winner, bearing-matched face, accepted by triage) / attention-only (a glance at most) / refused",
    "3 SELF-SPEECH: while the robot speaks and for a tail, do not switch visitor (DoA may point at the robot); keep pursuing the locked face",
    "4 SLEW HOLD: bearings taken during a head pan are the least trustworthy",
    "5 DEADBAND: ignore changes under %s rad %s (about 3 deg)" % (num(db), t_db),
    "6 DWELL: no re-aim within %s s %s" % (num(dw), t_dw),
    "7 CONTESTED: labels alternate faster than the dwell -> hold; never average two speakers",
    "8 PURSUIT: follow the same locked face frame by frame; disengage on face loss",
    "9 SECTOR GLANCE: off-camera directed speech, bearing stable %s s %s, robot quiet -> one glance, time-boxed to %s s %s"
    % (num(sgh), t_sgh, num(sgb), t_sgb),
]
GH, GW = 40, 500
yy = gy + 24
for i, lab in enumerate(gates):
    BOXES.append(box("g%d" % i, 30, yy, GW, GH - 4, lab, GATE if i not in (2,) else BAD, font=10, align="left"))
    if i:
        EDGES.append(dict(src="g%d" % (i - 1), dst="g%d" % i, sx=0.06, sy=1, dx=0.06, dy=0, color=GREEN_C))
    yy += GH
BOXES.append(box("hold", 560, gy + 24, 90, 9 * GH - 4,
                 "HOLD\n\nkeep the current aim; log the suppressed decision with a reason\n\n(a gaze that does not happen is the interesting case)",
                 BAD, font=10.5, bold=False))
for i in range(9):
    EDGES.append(dict(src="g%d" % i, dst="hold", sx=1, sy=0.5, dx=0, dy=(i * GH + GH / 2 - 2) / (9 * GH - 4), color=RED_C,
                      dashed=True))
BOXES.append(box("aim", 30, yy + 4, GW, 34, "AIM: hand an eased glide to the head controller", BODY, bold=True, font=11))
EDGES.append(dict(src="g8", dst="aim", sx=0.06, sy=1, dx=0.06, dy=0, color=GREEN_C))
BOXES.append(text("g_leg", 30, yy + 42, 620, 30,
                  "green = pass, go to the next gate | red dashed = fail -> HOLD. When unsure, hold still; gaze loss degrades to the old nearest-visitor gaze, never to no gaze.",
                  font=10, fontcolor="#444444"))

# --- right column ---------------------------------------------------------------------------
RX, RW = 680, 570
# composition rule and field of view
fb = V("fov_example_bearing_true"); t_fb = T("fov_example_bearing_true")
ft = V("fov_true_illustrative"); t_ft = T("fov_true_illustrative")
fd = V("fov_default_illustrative"); t_fd = T("fov_default_illustrative")
fw = V("fov_example_linear_wrong_fov"); t_fw = T("fov_example_linear_wrong_fov")
fr = V("fov_example_linear_right_fov"); t_fr = T("fov_example_linear_right_fov")
le = V("linear_vs_pinhole_max_err_90"); t_le = T("linear_vs_pinhole_max_err_90")
u = math.tan(math.radians(fb)) / math.tan(math.radians(ft / 2)) / 2   # (x - 0.5) under a pinhole camera
assert abs(u * fd - fw) < 0.1 and abs(u * ft - fr) < 0.1
BOXES.append(box("frame", RX, gy, RW, 96,
                 "FRAMES. Composition rule: target yaw = MEASURED neck yaw + head-camera bearing, then clip. Using the COMMANDED yaw lets "
                 "error pile up and the head 'walks away'. A bearing travels with its frame name; null, never 0, means 'no bearing'.\n"
                 "Field of view: a face at a true %s deg %s on a %s deg camera %s, converted linearly with a leftover %s deg default %s, "
                 "reads %s deg %s [calc]: the head under-turns by %s deg [calc]. With the right FOV the linear formula still reads %s deg %s; "
                 "the pinhole form atan((x - cx) / fx) is exact (largest linear error about %s deg %s)."
                 % (fb, t_fb, ft, t_ft, fd, t_fd, num(fw), t_fw, num(round(fb - fw, 1)), num(fr), t_fr, num(le), t_le),
                 VISIT, font=10.5, align="left", valign="top"))

# motion quality
si = V("saccade_duration_intercept"); t_si = T("saccade_duration_intercept")
ss = V("saccade_duration_slope"); t_ss = T("saccade_duration_slope")
s40 = V("saccade_40deg_duration"); t_s40 = T("saccade_40deg_duration")
assert abs(si + ss * 40 - s40) < 1
slew = V("head_slew_cap_illustrative"); t_slew = T("head_slew_cap_illustrative")
a = V("head_ema_alpha_illustrative"); t_a = T("head_ema_alpha_illustrative")
t95 = V("head_ema_t95_illustrative"); t_t95 = T("head_ema_t95_illustrative")
assert abs(math.log(0.05) / math.log(1 - a) / 50 - t95) < 0.01
my = gy + 106
BOXES.append(box("motion", RX, my, RW, 84,
                 "GLIDE, NOT SACCADE. A human 40 deg saccade takes about %s ms %s (%s ms + %s ms per deg %s %s). The team chose not to imitate it: "
                 "every move is a smoothstep glide s = 3t^2 - 2t^3, duration growing with distance, peak speed capped at %s rad/s %s. "
                 "It arrives on both axes together, with zero speed at both ends and a clean completion event. "
                 "Exponential smoothing (alpha %s per 50 Hz tick %s) reaches 95 %% in about %s s %s but never finishes cleanly."
                 % (s40, t_s40, si, num(ss), t_si, t_ss, num(slew), t_slew, num(a), t_a, num(t95), t_t95),
                 BODY, font=10.5, align="left", valign="top"))

# duty cycle chart
dy0 = my + 96
bl = V("gaze_band_listening_illustrative"); t_bl = T("gaze_band_listening_illustrative")
bs = V("gaze_band_speaking_illustrative"); t_bs = T("gaze_band_speaking_illustrative")
ge = V("gaze_episode_mean_illustrative"); t_ge = T("gaze_episode_mean_illustrative")
lm = V("lookaway_mean_illustrative"); t_lm = T("lookaway_mean_illustrative")
duty = V("alternation_duty_illustrative"); t_duty = T("alternation_duty_illustrative")
assert abs(ge / (ge + lm) - duty) < 0.01
gl = V("gaze_listener_share"); t_gl = T("gaze_listener_share")
gs = V("gaze_speaker_share"); t_gs = T("gaze_speaker_share")
BOXES.append(text("duty_h", RX, dy0, RW, 34,
                  "DUTY CYCLE: share of time looking at the addressee. Plain alternation (%s s gaze %s, %s s away %s) gives %s %s [calc]: "
                  "inside the listening band, outside the speaking band." % (ge, t_ge, lm, t_lm, num(duty), t_duty),
                  font=10.5, bold=True))
CX0, CPX = RX + 175, 3.9     # px per percent
rows = [("listening", bl, gl, t_bl, t_gl), ("speaking", bs, gs, t_bs, t_gs)]
ry = dy0 + 42
for name, band, human, tb, th in rows:
    BOXES.append(text("dl_" + name, RX, ry - 4, 168, 30, "robot design band, %s: %s %s" % (name, rng(band), tb),
                      font=10, valign="middle", align="right"))
    BOXES.append(box("db_" + name, int(CX0 + band[0] * 100 * CPX), ry + 2, int((band[1] - band[0]) * 100 * CPX), 18,
                     "", GATE, rounded=False))
    hx = CX0 + human * 100 * CPX
    LINES.append(dict(x1=round(hx), y1=ry - 2, x2=round(hx), y2=ry + 24, color=PURPLE_C, sw=2.5))
    BOXES.append(text("dh_" + name, round(hx) + 3 if name == "speaking" else round(hx) - 113, ry + 22, 110, 14,
                      "human %s %s" % (num(human), th), font=9.5, fontcolor=PURPLE_C,
                      align="left" if name == "speaking" else "right"))
    ry += 40
dx = CX0 + duty * 100 * CPX
LINES.append(dict(x1=round(dx), y1=dy0 + 36, x2=round(dx), y2=ry - 4, color=RED_C, sw=2, dashed=True))
BOXES.append(text("dd", round(dx) + 4, ry - 16, 120, 14, "alternation %s" % num(duty), font=9.5, fontcolor=RED_C))
LINES.append(dict(x1=CX0, y1=ry, x2=CX0 + 100 * CPX, y2=ry, color="#333333", sw=1.2))
for p in range(0, 101, 25):
    LINES.append(dict(x1=CX0 + p * CPX, y1=ry, x2=CX0 + p * CPX, y2=ry + 5, color="#333333", sw=1.2))
    BOXES.append(text("dp%d" % p, CX0 + p * CPX - 20, ry + 6, 40, 14, "%d %%" % p, font=9.5, align="center"))
BOXES.append(text("duty_n", RX, ry + 24, RW, 44,
                  "So a seeded scheduler tracks the cumulative duty and draws randomised episode lengths (people notice periodicity). "
                  "Live use then moved the look-away to an eyebrow beat: a head look-away took the face out of frame and the head oscillated.",
                  font=10))
bottom_r = ry + 72

ylg = max(bottom_r, yy + 80) + 6
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: amber = gates and design bands | red = hold / self-speech | green = motion | blue = frames | purple ticks = public human gaze shares "
                 "(the bands bracket them) | red dashed = plain alternation.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B3-gaze.md (why nearest is wrong, layers, trust, frames, arbitration, gates, the state matrix and duty cycle, "
    "motion quality, 'how it is designed and tested'). "
    "[calc]: pinhole offset (x - 0.5) = tan(%s) / tan(%s / 2) / 2; linear reading = offset x FOV; under-turn = %s - %s; "
    "duty = %s / (%s + %s); asserted in the spec: %s + %s x 40 = %s ms and ln(0.05) / ln(1 - %s) / 50 = %s s."
    % (fb, ft, fb, num(fw), ge, ge, lm, si, num(ss), s40, num(a), num(t95))],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
