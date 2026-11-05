# -*- coding: utf-8 -*-
# 04 — Resource claims decide what may overlap (notes B3, B4; showcase order from C2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="04-resource-claims", w=W, h=0)

BOXES = [title("Resource claims decide what may overlap: one physical action, one gaze lease and one conversation "
               "turn can run together, but two physical actions never can, because each needs the one action slot", W, h=48)]

# claim matrix
X0, KW, CW, Y0, HH, RH = 30, 170, 118, 70, 40, 66
cols = ["action slot", "body", "head", "gaze", "audio out", "listening"]
BOXES.append(box("hk", X0, Y0, KW, HH, "contract kind  \\  resource", NOTE, bold=True, font=10.5))
for j, c in enumerate(cols):
    BOXES.append(box("h%d" % j, X0 + KW + j * CW, Y0, CW, HH, c, NOTE, bold=True, font=11))
rows = [
    ("PHYSICAL ACTION\nwave, expression, handshake, canned robot TTS, composites",
     [("ALWAYS\nexclusive", "solid"), ("optional", "opt"), ("optional;\nnever with gaze", "opt"),
      ("optional;\nnever with head", "opt"), ("optional", "opt")]),
    ("GAZE LEASE\nset / clear a gaze target; priority derived from the gaze mode",
     [("-", "no"), ("-", "no"), ("-", "no"), ("EXACTLY this,\nexclusive", "solid"), ("-", "no")]),
    ("SESSION SERVICE\nconversation turn, enrolment, gift offer, greeting, operator alert",
     [("-", "no"), ("-", "no"), ("-", "no"), ("-", "no"), ("nothing, or\nexclusive via an\noutput lease", "solid")]),
]
for i, (k, cells) in enumerate(rows):
    y = Y0 + HH + i * RH
    BOXES.append(box("k%d" % i, X0, y, KW, RH, k, WORLD, font=9.5, align="left"))
    for j, (lab, kind) in enumerate(cells):
        pal = {"solid": KERNEL, "opt": ("#fff7ee", "#d79b00"), "no": WHITE}[kind]
        BOXES.append(box("c%d%d" % (i, j), X0 + KW + j * CW, y, CW, RH, lab, pal, font=10,
                         bold=(kind == "solid"), dashed=(kind == "opt")))
BOXES.append(box("listen", X0 + KW + 5 * CW, Y0 + HH, CW, 3 * RH,
                 "NOT CLAIMABLE\nlistening is the kernel's visitor-audio permit, not a resource", BAD, font=10))
MX = X0 + KW + 6 * CW   # right edge of the matrix (= 908)

# rules panel
BOXES += [
    box("rules", MX + 20, Y0, W - 30 - MX - 20, HH + 3 * RH,
        "WHAT FOLLOWS (B3)\n"
        "- Every physical action claims the one action slot, so two physical actions never run at once.\n"
        "- Concurrency exists only BETWEEN kinds: one physical action + one gaze lease + one conversation turn.\n"
        "- Head and gaze drive the same actuators: no primitive claims both; an exclusive-head primitive is refused "
        "while a gaze lease is active.\n"
        "- Conversation speech (session service on an output lease) may overlap a wave; canned robot TTS cannot, it "
        "occupies the slot. A line + gesture is ONE composite primitive.",
        NOTE, font=10, align="left", valign="top"),
]

# conflict matrix row
YC = Y0 + HH + 3 * RH + 14
BOXES += [
    box("conf", 30, YC, 1220, 44,
        "CONFLICT MATRIX (closed; no primitive or experience may override it, B4):  action slot - an equal-or-lower "
        "priority request is deferred, a higher one preempts and waits for the old command's terminal cancellation  |  "
        "gaze - refuses lower priority, replaces at equal or higher after the prior clear succeeds  |  audio out - a "
        "conflict is refused  |  safety priority is reserved for the kernel", KERNEL, font=10, align="left"),
]

# showcase timeline (schematic order, not to scale)
YT = YC + 60
BOXES.append(text("tl_t", 30, YT, 1220, 34,
                  "THE SHOWCASE SCENARIO (C2), with the conservative first wave primitive (slot + body + head, all "
                  "exclusive, no audio). Order only: the notes give no durations, so bar lengths are a drawing choice.",
                  bold=True, font=11))
lanes = [("gaze", "gaze (gaze lease)"), ("slot", "action slot + body + head (wave)"), ("aud", "audio out (output lease per turn)")]
LX, LW, LH, LY0 = 30, 200, 40, YT + 70
for i, (id_, lab) in enumerate(lanes):
    BOXES.append(box("lane_" + id_, LX, LY0 + i * 54, LW, LH, lab, NOTE, font=10.5, bold=True))
    BOXES.append(box("track_" + id_, LX + LW + 8, LY0 + i * 54, 1012, LH, "", WHITE, fill="none", rounded=False, sw=0.8))
S = [270 + k * 150 for k in range(7)]   # step x positions (drawing choice)
bars = [
    ("g1", 0, S[0], S[2], "participant gaze", KERNEL),
    ("g2", 0, S[5], S[6], "gaze reacquired", KERNEL),
    ("w1", 1, S[3], S[4], "wave", EXPER),
    ("a1", 2, S[1] - 10, S[2] - 10, "speech turn", REASON),
    ("a2", 2, S[3] - 30, S[4] - 20, "speech turn", REASON),
]
for id_, lane, x1, x2, lab, pal in bars:
    BOXES.append(box(id_, x1, LY0 + lane * 54 + 6, x2 - x1, LH - 12, lab, pal, font=10, bold=True))
steps = ["1 participant gaze acquired", "2 brokered speech overlaps gaze", "3 positive gaze clear (ack)",
         "4 brokered speech overlaps the wave", "5 authoritative wave completion", "6 correlated gaze reacquisition",
         "7 cleanup: no retained claim"]
LINES = []
for k, (x, st) in enumerate(zip(S, steps)):
    LINES.append(dict(x1=x, y1=YT + 64, x2=x, y2=LY0 + 3 * 54 - 10, color="#666666", dashed=True, sw=1))
    BOXES.append(text("st%d" % k, x - 68, YT + 36, 136, 28, st, align="center", font=9.5, bold=True))
YN = LY0 + 3 * 54
BOXES += [
    box("gap", 30, YN, 600, 44,
        "Between 3 and 4 the gaze lease is cleared WITH acknowledgement before the wave starts: the wave claims the "
        "head exclusively. A lighter arm-only wave would be a later catalog revision with its own scenario (B3).",
        NOTE, font=10, align="left"),
    box("proof", 650, YN, 600, 44,
        "The video only illustrates the overlaps. The proof is the held intervals in the evidence (acquired -> "
        "released per invocation), read from evidence fields, never inferred from presentation events (C2).",
        NOTE, font=10, align="left"),
    box("legend", 30, YN + 56, 1220, 40,
        "Legend:  matrix - solid amber = claim always held (exclusive) | dashed light amber = optional claim | white "
        "'-' = never claimed | red = not a resource.  Timeline - amber = gaze lease, green = physical action, "
        "purple = conversation turn; dashed verticals = the seven showcase steps in order.", WHITE, font=10, align="left"),
]
EDGES = []

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B3-the-effect-vocabulary.md (contract kinds, resources and permitted claims, action slot, "
    "head vs gaze, speech vs canned TTS, composite primitives, conservative first wave claims); "
    "B4-kernel-interception-and-arbitration.md (closed conflict matrix); C2-the-conformance-ladder.md (showcase "
    "scenario order, held intervals, 'the video illustrates, the evidence proves'). This page carries no numeric "
    "design parameter."],
    30, YN + 110, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
