# -*- coding: utf-8 -*-
# 04 — Who is speaking: coarse DoA gates and corroborates, ASD selects, abstain off camera (note B2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="04-who-is-speaking", w=W, h=0)

c = V("speed_of_sound_20c"); t_c = T("speed_of_sound_20c")
td10 = V("tdoa_max_10cm"); t_td10 = T("tdoa_max_10cm")
sp = V("sample_period_16k"); t_sp = T("sample_period_16k")
spath = V("sample_path_16k"); t_spath = T("sample_path_16k")
ang1 = V("one_sample_angle_10cm_16k"); t_ang1 = T("one_sample_angle_10cm_16k")
al5 = V("spatial_alias_5cm"); t_al5 = T("spatial_alias_5cm")
al10 = V("spatial_alias_10cm"); t_al10 = T("spatial_alias_10cm")
# my arithmetic checks against the loaded public values
assert abs(0.10 / c * 1e6 - td10) < 1
assert abs(math.degrees(math.asin(c * sp * 1e-6 / 0.10)) - ang1) < 0.1

binw = V("doa_bin_illustrative"); t_bin = T("doa_bin_illustrative")
gate = V("doa_face_gate_illustrative"); t_gate = T("doa_face_gate_illustrative")
win = V("doa_effective_window_illustrative"); t_win = T("doa_effective_window_illustrative")
assert abs(gate + binw / 2 - win) <= 2.5
fov = V("fov_true_illustrative"); t_fov = T("fov_true_illustrative")
tail = V("self_speech_tail_illustrative"); t_tail = T("self_speech_tail_illustrative")

BOXES = [title("Who is speaking: the face's moving mouth SELECTS, the coarse microphone bearing only gates and corroborates, "
               "and when the voice has no face the label is 'unidentified', because a confident wrong name costs more than no name", W, h=46)]
LINES = []

# --- left: top-down scene ------------------------------------------------------------
BOXES.append(text("sc_h", 30, 70, 570, 20, "A. TOP-DOWN SCENE AT THE STAND (positions are a drawing choice, not data)",
                  bold=True, font=12))
CX, CY, R = 315, 545, 330


def pt(deg, r):
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


# bin edges (every binw degrees, centred on 0) across the front half
k = 0.5
while k * binw <= 90:
    for s in (-1, 1):
        x, y = pt(s * k * binw, R)
        LINES.append(dict(x1=CX, y1=CY, x2=round(x), y2=round(y), color="#aaaaaa", dashed=True, sw=1))
    k += 1
# camera field of view
for s in (-1, 1):
    x, y = pt(s * fov / 2, R - 20)
    LINES.append(dict(x1=CX, y1=CY, x2=round(x), y2=round(y), color=GREEN_C, sw=2))
# the widened face-matching window around the bin at 0 deg
for s in (-1, 1):
    x, y = pt(s * win, 150)
    LINES.append(dict(x1=CX, y1=CY, x2=round(x), y2=round(y), color=AMBER_C, dashed=True, sw=2))
x, y = pt(-fov / 2, R - 14)
BOXES.append(text("fov_l", round(x) - 40, round(y) - 34, 170, 30,
                  "head-camera field of view %s deg %s" % (fov, t_fov), font=10, fontcolor=GREEN_C))
x, y = pt(win, 150)
BOXES.append(text("win_l", 30, 130, 300, 34,
                  "amber dashed = face window +-%s deg %s = gate %s deg %s + half a bin [calc]" % (win, t_win, gate, t_gate),
                  font=10, fontcolor=AMBER_C))
x, y = pt(-binw / 2 - 4, R + 2)
BOXES.append(text("bin_l", 30, 96, 260, 30,
                  "grey dashed = on-chip direction bins, %s deg each (8 directions) %s" % (binw, t_bin), font=10,
                  fontcolor="#666666"))

people = [
    ("v1", -8, 205, "visitor_1\nmouth moving", BODY),
    ("v2", 12, 245, "visitor_2\nsilent", VISIT),
    ("by", -58, 175, "bystander, outside\nthe window, silent", NOTE),
    ("ph", 66, 220, "a phone playing\nspeech, OFF camera", BAD),
]
for id_, deg, r, lab, pal in people:
    x, y = pt(deg, r)
    BOXES.append(box(id_, round(x) - 15, round(y) - 15, 30, 30, "", pal, rx=15))
    lx = round(x) + 18 if deg >= 0 else round(x) - 118
    BOXES.append(text(id_ + "_l", lx, round(y) - 14, 100, 30, lab, font=10, align="left" if deg >= 0 else "right"))
BOXES.append(box("robot", CX - 46, CY - 8, 92, 34, "ROBOT\nmic array", GREY, font=10, bold=True))
BOXES.append(box("sc_n1", 30, 590, 270, 84,
                 "visitor_1 and visitor_2 share ONE bin and both sit inside the window: the bearing ABSTAINS and defers to "
                 "active-speaker detection, which picks visitor_1 by the moving mouth.",
                 NOTE, font=10.5, align="left", valign="top"))
BOXES.append(box("sc_n2", 315, 590, 285, 84,
                 "The phone's bearing has NO face: positive evidence for 'unidentified'. It must not be pinned on the silent "
                 "person in front. While the robot itself speaks, and for %s ms after %s, DoA evidence is ignored (the loudest "
                 "direction may be the robot)." % (tail, t_tail),
                 BAD, font=10.5, align="left", valign="top"))

# --- right: physics, fusion rule, tiers, ladder ----------------------------------------
RX = 630
BOXES.append(box("phys", RX, 70, 620, 86,
                 "WHY A SMALL ARRAY IS COARSE (public physics)\n"
                 "sound %s m/s %s -> largest delay across a 10 cm pair %s us %s\n"
                 "one sample at 16 kHz = %s us %s = %s cm of path %s -> an integer lag resolves only about %s deg near broadside %s\n"
                 "phase wraps above c / 2d: %s kHz for a 5 cm pair %s, %s kHz for 10 cm %s (spatial aliasing)\n"
                 "So estimators interpolate below one sample (GCC-PHAT, SRP-PHAT), and small chips often report only a bin."
                 % (c, t_c, td10, t_td10, num(sp), t_sp, num(spath), t_spath, num(ang1), t_ang1, num(al5), t_al5, num(al10), t_al10),
                 WHITE, font=10.5, align="left", valign="top"))
BOXES.append(box("rule", RX, 166, 620, 50,
                 "FUSION RULE (an invariant, not a tuning default): ASD selects among visible faces; DoA gates, breaks ties and "
                 "corroborates; the loudest direction never selects on its own. DoA binds to a visual track, never stands alone.",
                 GATE, font=10.5, align="left", valign="top", bold=False))

# tiered labels to scale
ty = 282
BOXES.append(text("tier_h", RX, ty, 620, 20, "TIERED LABELS after speech start (to scale): attach now, refine, repair before the NEXT turn",
                  bold=True, font=11))
TX0, TPX = RX + 10, 145
t0 = V("label_t0_illustrative") / 1000.0; t_t0 = T("label_t0_illustrative")
t1 = V("label_t1_illustrative"); t_t1 = T("label_t1_illustrative")
t2 = V("label_t2_illustrative"); t_t2 = T("label_t2_illustrative")
tiers = [
    ("T0", t0, "T0 %s ms %s: DoA x visible faces; never blocks a response" % (V("label_t0_illustrative"), t_t0), VISIT),
    ("T1", t1, "T1 by %s s %s: ASD picks the talker; re-evaluated every frame" % (num(t1), t_t1), BODY),
    ("T2", t2, "T2 up to %s s %s: voice and face embeddings confirm or repair" % (t2, t_t2), LLM),
]
yy = ty + 24
for id_, tt, lab, pal in tiers:
    BOXES.append(box("tb_" + id_, TX0, yy, max(4, int(tt * TPX)), 18, "", pal, rounded=False))
    lx = TX0 + int(tt * TPX) + 8
    if lx + 300 > RX + 620:
        lx = TX0 + 6
        BOXES.append(text("tl_" + id_, lx, yy, int(tt * TPX) - 10, 18, lab, font=10, valign="middle"))
    else:
        BOXES.append(text("tl_" + id_, lx, yy, RX + 620 - lx, 18, lab, font=10, valign="middle"))
    yy += 22
LINES.append(dict(x1=TX0, y1=yy + 2, x2=TX0 + 4 * TPX, y2=yy + 2, color="#333333", sw=1.2))
for s in range(0, 5):
    LINES.append(dict(x1=TX0 + s * TPX, y1=yy + 2, x2=TX0 + s * TPX, y2=yy + 7, color="#333333", sw=1.2))
    BOXES.append(text("tt%d" % s, TX0 + s * TPX - 15, yy + 8, 30, 14, "%d s" % s, font=9.5, align="center"))

# attribution ladder
ly = yy + 34
BOXES.append(text("lad_h", RX, ly, 620, 20, "ATTRIBUTION LADDER, per turn (first rung that succeeds wins)", bold=True, font=11))
vmin = V("voice_embedding_min_illustrative"); t_vmin = T("voice_embedding_min_illustrative")
cos_ = V("voice_match_cosine_illustrative"); t_cos = T("voice_match_cosine_illustrative")
mar = V("voice_match_margin_illustrative"); t_mar = T("voice_match_margin_illustrative")
asd = V("asd_min_face_illustrative"); t_asd = T("asd_min_face_illustrative")
ly += 22
BOXES.append(box("l1", RX, ly, 190, 92, "1  ASD among faces big enough to score (at least %s px wide %s)" % (asd, t_asd),
                 BODY, font=10.5))
BOXES.append(box("l2", RX + 215, ly, 200, 92,
                 "2  voice match: turn of %s s or more %s, cosine %s %s and margin %s %s; the only path that can name an off-camera voice"
                 % (num(vmin), t_vmin, num(cos_), t_cos, num(mar), t_mar), LLM, font=10))
BOXES.append(box("l3", RX + 440, ly, 180, 92,
                 "3  ABSTAIN: visitor_id null + a reason (off camera, contradicted, too short, blend). No sentinel id.",
                 BAD, font=10.5))
EDGES = [
    dict(src="l1", dst="l2", sx=1, sy=0.5, dx=0, dy=0.5, color=GREY_C, label="no", lw=24, lpos=(RX + 202, ly + 36)),
    dict(src="l2", dst="l3", sx=1, sy=0.5, dx=0, dy=0.5, color=GREY_C, label="no", lw=24, lpos=(RX + 427, ly + 36)),
]
ly += 100

# --- bottom: the asymmetry ---------------------------------------------------------------
yb = max(ly, 684) + 6
churn = V("id_churn_token_cost_illustrative"); t_churn = T("id_churn_token_cost_illustrative")
casc = V("cascade_turns_illustrative"); t_casc = T("cascade_turns_illustrative")
BOXES.append(box("resp", 30, yb, 600, 62,
                 "'SHOULD I RESPOND?' is about DIRECTEDNESS: under doubt, lean toward answering. An over-response is recoverable "
                 "('oh, were you asking me?'); silence toward an engaged visitor is not. Directedness ('someone off camera is "
                 "addressing you') ships in the same change as abstention.",
                 BODY, font=10.5, align="left", valign="top"))
BOXES.append(box("who", 650, yb, 600, 62,
                 "'WHO SAID IT?' is about IDENTITY: be strict. A churning id stream cost %s%% more input tokens per response %s, "
                 "and one wrong bind passed to the next %s turns %s through a 'last active speaker' fallback. "
                 "A missing label is far cheaper than a wrong one." % (int(round(churn * 100)), t_churn, casc, t_casc),
                 BAD, font=10.5, align="left", valign="top"))
ylg = yb + 76
BOXES.append(box("legend", 30, ylg, 1220, 26,
                 "Legend: circles = people or sound sources (green = talking, blue = silent visitor, grey = bystander, red = off-camera source) | "
                 "green lines = camera field of view | amber dashed = face-matching window | grey dashed = direction bins.",
                 WHITE, font=10.5, align="left"))
src_box, bottom = footer_box(T, [
    "Mechanism: notes/B2-who-is-speaking.md (DoA basics, the fusion rule, tiered labels, the robot's own voice, honest abstention, "
    "voices banked carefully, passing attribution to the model; 'check the input-size gate'). "
    "[calc]: window = %s + %s / 2, rounded to %s deg; checked 0.10 m / %s m/s = %s us and asin(%s m/s x %s us / 10 cm) = %s deg."
    % (gate, binw, win, c, td10, c, num(sp), num(ang1))],
    30, ylg + 40, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
