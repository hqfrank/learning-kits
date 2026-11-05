# -*- coding: utf-8 -*-
# 06 — Turn-taking: why the spectral barge-in guard was turned off (note B4).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="06-guard-blind-spot", w=W, h=0)

greet = V("proactive_greeting_illustrative"); t_greet = T("proactive_greeting_illustrative")
grace = V("guard_onset_grace_illustrative"); t_grace = T("guard_onset_grace_illustrative")
gap = V("turn_gap_typical") / 1000.0; t_gap = T("turn_gap_typical")
leak = V("self_hearing_leak_window_illustrative"); t_leak = T("self_hearing_leak_window_illustrative")
drop = V("self_hearing_suppressed_drop_illustrative"); t_drop = T("self_hearing_suppressed_drop_illustrative")
lift = V("self_hearing_lift_illustrative"); t_lift = T("self_hearing_lift_illustrative")
deb = V("barge_in_debounce_illustrative"); t_deb = T("barge_in_debounce_illustrative")
reply = greet + gap                       # my arithmetic
assert reply < grace, "the quick reply must land inside the onset grace for this lesson"

BOXES = [title("Why the clever guard was turned off: an onset grace of %s s %s cannot tell a %s s greeting %s followed by a "
               "%s ms human reply %s from the robot hearing itself, so the visitor's first word was rejected and one rejection ended the visit"
               % (num(grace), t_grace, num(greet), t_greet, V("turn_gap_typical"), t_gap), W, h=46)]
LINES = []
EDGES = []

# --- timeline -------------------------------------------------------------------------
BOXES.append(text("t_h", 30, 72, 1220, 20,
                  "A. THE NEW OPENING, to scale (one visit, time from the robot's speech onset). Positions of the visitor's reply follow the public turn gap.",
                  bold=True, font=12))
X0, PX, TMAX = 330, 220, 4.0
Y0, RH = 102, 46
lanes = [
    ("robot", "robot loudspeaker"),
    ("mic", "processed microphone channel (what the model hears)"),
    ("guard", "spectral barge-in guard"),
    ("visitor", "visitor"),
    ("model", "the reasoner (speech-to-speech model)"),
]
for i, (id_, lab) in enumerate(lanes):
    y = Y0 + i * RH
    BOXES.append(text("ln_" + id_, 30, y, X0 - 40, RH - 6, lab, font=10.5, align="right", valign="middle", bold=True))
    LINES.append(dict(x1=X0, y1=y + RH - 3, x2=X0 + TMAX * PX, y2=y + RH - 3, color="#dddddd", sw=1))


def X(t):
    return int(X0 + t * PX)


yR, yM, yG, yV, yD = [Y0 + i * RH + 6 for i in range(5)]
BH = RH - 16
BOXES.append(box("b_greet", X(0), yR, X(greet) - X(0), BH,
                 "perception-triggered greeting %s s %s" % (num(greet), t_greet), LLM, rounded=False, font=10))
BOXES.append(box("b_leak", X(leak[0]), yM, X(leak[1]) - X(leak[0]), BH,
                 "self-hearing leaks %s s %s" % (rng(leak), t_leak), BAD, rounded=False, font=9.5))
BOXES.append(box("b_supp", X(leak[1]), yM, X(greet) - X(leak[1]), BH,
                 "late suppression: -%s dB %s" % (drop, t_drop), NOTE, rounded=False, font=9.5))
BOXES.append(box("b_grace", X(0), yG, X(grace) - X(0), BH,
                 "ONSET GRACE %s s %s: VAD onsets here are rejected" % (num(grace), t_grace),
                 GATE, rounded=False, font=10, dashed=True))
BOXES.append(box("b_reply", X(reply), yV, X(reply + 1.3) - X(reply), BH,
                 "first reply starts at %s s [calc]" % num(round(reply, 2)), BODY, rounded=False, font=10))
BOXES.append(box("b_rej", X(reply) - 4, yG + 2, 92, BH - 4, "REJECTED", BAD, rounded=False, bold=True, font=10.5))
BOXES.append(box("b_idle", X(reply + 0.25), yD, X(TMAX) - X(reply + 0.25), BH,
                 "holds an unanswered greeting, stops listening -> the robot goes idle: the visit is over",
                 BAD, rounded=False, font=10))
# reply onset line and turn-gap bracket
LINES.append(dict(x1=X(reply), y1=yR, x2=X(reply), y2=yD + BH, color=GREEN_C, sw=2, dashed=True))
LINES.append(dict(x1=X(grace), y1=yR, x2=X(grace), y2=yG + BH, color=AMBER_C, sw=2, dashed=True))
BOXES.append(text("gap_l", X(0.1), yV, X(reply) - X(0.1) - 6, BH,
                  "greeting ends at %s s; the reply follows after the typical human gap of %s ms %s ->"
                  % (num(greet), V("turn_gap_typical"), t_gap), font=10, fontcolor=GREEN_C, valign="middle", align="right"))
yax = Y0 + 5 * RH + 4
LINES.append(dict(x1=X0, y1=Y0, x2=X0, y2=yax, color="#333333", sw=1.2))
LINES.append(dict(x1=X0, y1=yax, x2=X(TMAX), y2=yax, color="#333333", sw=1.2))
k = 0.0
while k <= TMAX + 1e-9:
    LINES.append(dict(x1=X(k), y1=yax, x2=X(k), y2=yax + 5, color="#333333", sw=1.2))
    BOXES.append(text("tk%d" % int(k * 10), X(k) - 20, yax + 6, 40, 14, "%s s" % num(k), font=10, align="center"))
    k += 0.5
BOXES.append(text("t_note", 30, yax + 24, 1220, 34,
                  "The guard's design argued 'a rejection costs at most one utterance'. Here that utterance was the first reply to the greeting, "
                  "so it cost the whole visit. The interaction design changed underneath the defence; the code, tests and promotion rule stayed, "
                  "only the default moved to OFF (with a boot-log line confirming the setting). A platform audio update had also removed most of the self-hearing it was built for.",
                  font=10.5))

# --- lower left: two sources of phantom barge-ins --------------------------------------------
yb = yax + 76
raw = V("actuator_lift_raw_illustrative"); t_raw = T("actuator_lift_raw_illustrative")
proc = V("actuator_lift_processed_illustrative"); t_proc = T("actuator_lift_processed_illustrative")
mos = V("motion_over_speech_processed_illustrative"); t_mos = T("motion_over_speech_processed_illustrative")
nt = V("noise_only_transcripts_illustrative"); t_nt = T("noise_only_transcripts_illustrative")
lowb = V("guard_low_band_illustrative"); t_lowb = T("guard_low_band_illustrative")
BOXES.append(text("s_h", 30, yb, 400, 20, "B. WHY PHANTOM BARGE-INS HAPPEN", bold=True, font=12))
BOXES.append(box("src_m", 30, yb + 24, 400, 100,
                 "(a) THE ROBOT'S OWN MOTORS: impulsive rumble, mostly %s Hz %s. Head moving vs holding: raw microphone +%s dB %s, "
                 "processed channel +%s dB %s (gain control winds up with no speech present); the motion was %s dB %s louder than a nearby talker. "
                 "Noise-only clips came back as words %s of %s times %s. Feedback cancellation cannot help: motors have no reference signal."
                 % (rng(lowb), t_lowb, raw, t_raw, proc, t_proc, mos, t_mos, nt[0], nt[1], t_nt),
                 BAD, font=10, align="left", valign="top"))
BOXES.append(box("src_v", 30, yb + 132, 400, 62,
                 "(b) THE ROBOT'S OWN VOICE: %s dB %s above the room floor during every robot speech window; suppression is late "
                 "and incomplete, likely because a clipped return is nonlinear and no linear canceller removes it."
                 % (lift, t_lift),
                 BAD, font=10, align="left", valign="top"))

# --- lower middle: the guard's score -------------------------------------------------------------
GX = 460
sub = V("guard_subwindow_illustrative"); t_sub = T("guard_subwindow_illustrative")
stride = V("guard_stride_illustrative"); t_stride = T("guard_stride_illustrative")
spb = V("guard_speech_band_illustrative"); t_spb = T("guard_speech_band_illustrative")
ph = V("guard_phantom_max_illustrative"); t_ph = T("guard_phantom_max_illustrative")
th = V("guard_threshold_illustrative"); t_th = T("guard_threshold_illustrative")
rl = V("guard_real_min_illustrative"); t_rl = T("guard_real_min_illustrative")
assert ph < th < rl
BOXES.append(text("g_h", GX, yb, 380, 20, "C. THE GUARD (what it does when it is on)", bold=True, font=12))
BOXES.append(box("g_txt", GX, yb + 24, 380, 74,
                 "Only when VAD would interrupt the robot: for each %s ms sub-window %s at a %s ms stride %s, score = 10 log10(E[%s Hz %s] / "
                 "E[rumble band]); keep the MAXIMUM, because one clear vowel is enough. Fail OPEN on any error: 'a deaf robot is a product failure'."
                 % (sub, t_sub, stride, t_stride, rng(spb), t_spb),
                 GATE, font=10, align="left", valign="top"))
SX0, SPX = GX + 20, 30   # px per dB
sy = yb + 140
LINES.append(dict(x1=SX0, y1=sy, x2=SX0 + 11 * SPX, y2=sy, color="#333333", sw=1.2))
for d in range(0, 11, 2):
    LINES.append(dict(x1=SX0 + d * SPX, y1=sy, x2=SX0 + d * SPX, y2=sy + 5, color="#333333", sw=1.2))
    BOXES.append(text("sd%d" % d, SX0 + d * SPX - 18, sy + 6, 36, 14, "%d dB" % d, font=9.5, align="center"))
BOXES.append(box("s_ph", SX0, sy - 22, ph * SPX, 16, "", BAD, rounded=False))
BOXES.append(box("s_rl", SX0 + rl * SPX, sy - 22, 3 * SPX, 16, "", BODY, rounded=False))
LINES.append(dict(x1=SX0 + th * SPX, y1=sy - 34, x2=SX0 + th * SPX, y2=sy, color=AMBER_C, sw=2.2, dashed=True))
BOXES.append(text("s_phl", SX0, sy - 40, 170, 16, "motor onsets up to %s dB %s" % (ph, t_ph), font=9.5, fontcolor=RED_C))
BOXES.append(text("s_thl", SX0 + th * SPX - 40, sy + 20, 120, 16, "threshold %s dB %s" % (th, t_th), font=9.5, fontcolor=AMBER_C))
BOXES.append(text("s_rll", SX0 + rl * SPX - 50, sy - 40, 140, 16, "real onsets from %s dB %s" % (rl, t_rl), font=9.5, fontcolor=GREEN_C,
                  align="right"))
BOXES.append(text("s_n", GX, sy + 38, 380, 30,
                  "Perfect separation on one robot, one room and one talker is a FIT, not a generalisation.", font=10))

# --- lower right: the promotion rule and the method ------------------------------------------------
PX0 = 870
ev = V("guard_promo_evaluations_illustrative"); t_ev = T("guard_promo_evaluations_illustrative")
rb = V("guard_promo_real_bargeins_illustrative"); t_rb = T("guard_promo_real_bargeins_illustrative")
rr = V("guard_promo_reject_rate_illustrative"); t_rr = T("guard_promo_reject_rate_illustrative")
mg = V("guard_promo_margin_illustrative"); t_mg = T("guard_promo_margin_illustrative")
BOXES.append(text("p_h", PX0, yb, 380, 20, "D. SHIP A GUARD BY A WRITTEN RULE", bold=True, font=12))
BOXES.append(box("p_rule", PX0, yb + 24, 380, 66,
                 "Shadow mode first (log would-be decisions, change nothing). Default ON needs ALL of: %s in-scope evaluations %s; "
                 "%s scripted real barge-ins, none rejected %s; %s %% of motor onsets rejected %s; a %s dB worst-case margin %s."
                 % (ev, t_ev, rb, t_rb, int(round(rr * 100)), t_rr, mg, t_mg),
                 BODY, font=10, align="left", valign="top"))
BOXES.append(box("p_meas", PX0, yb + 100, 380, 94,
                 "Every turn-taking change gets TWO measurements, on the robot, moving and speaking, in venue noise: phantom turns caused "
                 "(false barge-ins, ghost wakes) and real turns lost (rejected barge-ins, missed starts), with sample sizes. "
                 "Barge-in itself stops the robot only after a %s s debounce %s." % (num(deb), t_deb),
                 VISIT, font=10, align="left", valign="top"))

ylg = yb + 222
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: purple = robot speech | red = self-hearing, rejection and failure | amber dashed = the onset grace and the guard threshold | "
                 "green = the visitor's real speech | grey = suppressed channel. Durations and dB are illustrative except the public turn gap.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B4-turn-taking-and-self-hearing.md (how a barge-in is handled, two sources of phantom barge-ins, the spectral "
    "barge-in guard, why the clever guard was turned off, 'how it is designed and tested'); Stivers et al. 2009 for the turn gap. "
    "[calc]: reply onset = greeting %s s + gap %s s = %s s, which is under the %s s grace. The reply's length on the canvas is a drawing choice."
    % (num(greet), num(gap), num(round(reply, 2)), num(grace))],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
