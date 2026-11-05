# -*- coding: utf-8 -*-
# 05 — Cancelling is not releasing: settle bounds to scale, and the path to recovery (notes B3, B2).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="05-cancellation-proof", w=W, h=0)

st = V("cancel_settle_target_ms_illustrative"); t_st = T("cancel_settle_target_ms_illustrative")
ce = V("cancel_settle_ceiling_ms_illustrative"); t_ce = T("cancel_settle_ceiling_ms_illustrative")
ck = V("cleanup_ack_timeout_ms_illustrative"); t_ck = T("cleanup_ack_timeout_ms_illustrative")
assert st <= ce < ck, "the design's relation: settle bound <= catalog ceiling < cleanup deadline"

BOXES = [title("Cancelling is not releasing: claims are kept until positive quiescence proof, and every settle bound "
               "(%s ms %s) sits inside the catalog ceiling and well inside the cleanup deadline (illustrative values)"
               % (num(st), t_st), W, h=48)]

# --- bars to scale ---
AX0, PX = 290, 0.094       # px per ms: the cleanup deadline spans ~980 px
YB = 96
BOXES.append(text("scale_t", 30, 66, 1220, 22,
                  "TO SCALE (one axis, %s px per second): the three bounds a cancellation lives inside" % num(round(PX * 1000)),
                  bold=True, font=11))
bars = [
    ("b_st", "target settle bound %s ms %s" % (num(st), t_st), st, EXPER),
    ("b_ce", "catalog-wide ceiling %s ms %s" % (num(ce), t_ce), ce, KERNEL),
    ("b_ck", "cleanup acknowledgement deadline %s ms %s" % (num(ck), t_ck), ck, BAD),
]
for i, (id_, lab, v, pal) in enumerate(bars):
    y = YB + i * 34
    BOXES.append(text(id_ + "_l", 30, y, 254, 26, lab, align="right", valign="middle", font=10, bold=True))
    BOXES.append(box(id_, AX0, y, int(round(v * PX)), 26, "", pal, rounded=False))
YA = YB + 3 * 34 + 4
LINES = [dict(x1=AX0, y1=YA, x2=AX0 + int(ck * PX), y2=YA, color="#333333", sw=1)]
for t_ms in range(0, ck + 1, 2000):
    x = AX0 + int(round(t_ms * PX))
    LINES.append(dict(x1=x, y1=YA, x2=x, y2=YA + 5, color="#333333", sw=1))
    BOXES.append(text("tk%d" % t_ms, x - 30, YA + 6, 60, 16, "%s s" % num(t_ms // 1000), align="center", font=9))
BOXES.append(text("rel", AX0 + int(ce * PX) + 20, YB + 2, 560, 50,
                  "Relation the design relies on: settle bound <= ceiling < cleanup deadline. Settle deadline = the "
                  "EARLIER of (request time + settle bound) and any active cleanup deadline, so a cancellation never "
                  "extends cleanup.", font=10))

# --- the decision path ---
YF = YA + 100
BOXES += [
    box("cancel", 30, YF, 190, 70, "CANCEL PRIMITIVE\ntargets the original invocation (no separate 'stop' primitive); idempotent",
        EXPER, font=10),
    box("settle", 250, YF, 220, 70, "SETTLING\nevery claim still held; the adapter must produce quiescence proof", KERNEL, font=10),
    box("q1", 500, YF, 200, 70, "positive proof before the settle deadline?", WHITE, font=10.5, bold=True),
    box("rel1", 740, YF - 50, 250, 50, "RELEASE ALL the invocation's claims, at once", EXPER, font=10.5, bold=True),
    box("forced", 740, YF + 50, 250, 70,
        "FORCED CLEANUP, reason 'cancellation stuck': keep every claim, refuse conflicting work", KERNEL, font=10, bold=True),
    box("q2", 1020, YF + 50, 230, 70, "quiescence proved before the cleanup deadline?", WHITE, font=10.5, bold=True),
    box("rel2", 1020, YF - 50, 230, 50, "release, normal cleanup completes", EXPER, font=10.5),
    box("recov", 1020, YF + 150, 230, 64,
        "RECOVERY (B2): claims stay in evidence, admission off, until operator recovery or a proven clean restart",
        BAD, font=10, bold=True),
]
EDGES = [
    dict(src="cancel", dst="settle", color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="settle", dst="q1", color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="q1", dst="rel1", label="yes", color="#82b366", bold=True, sx=0.5, sy=0, dx=0, dy=0.5,
         points=[(600, YF - 25)], lpos=(640, YF - 25), lw=40),
    dict(src="q1", dst="forced", label="no: the settle\ndeadline passed", color="#b85450", bold=True, sx=0.5, sy=1, dx=0, dy=0.5,
         points=[(600, YF + 85)], lpos=(660, YF + 100), lw=110, font=9),
    dict(src="forced", dst="q2", color="#666666", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="q2", dst="rel2", label="yes", color="#82b366", bold=True, sx=0.5, sy=0, dx=0.5, dy=1, lpos=(1150, YF + 25), lw=40),
    dict(src="q2", dst="recov", label="no", color="#b85450", bold=True, sx=0.5, sy=1, dx=0.5, dy=0, lpos=(1150, YF + 135), lw=40),
]

# --- what counts as proof ---
YP = YF + 150
BOXES += [
    box("proof", 30, YP, 470, 76,
        "WHAT COUNTS AS PROOF (each completion contract defines it)\n"
        "- physical action: terminal, and no longer holds the action slot\n"
        "- gaze lease: the gaze clear is acknowledged\n"
        "- speech stream: stopped or completed, AND its stop acknowledgement succeeded",
        EXPER, font=10, align="left", valign="top"),
    box("notproof", 520, YP, 470, 76,
        "WHAT IS NOT PROOF\nlease expiry | readiness loss | adapter removal | a transport disconnect.\n"
        "Lease expiry only stops further forwarding of audio; the claim stays held until the stream proves it "
        "stopped.", BAD, font=10, align="left", valign="top"),
    box("revoke", 30, YP + 88, 1220, 44,
        "KERNEL REVOCATIONS ARE UNCONDITIONAL: safety and reset, readiness loss, participant departure, cleanup and "
        "generation change cancel every primitive on every target. A catalog entry may add STRICTER revokers; it cannot "
        "remove or reorder these (B3).", KERNEL, font=10, align="left"),
    box("legend", 30, YP + 144, 1220, 40,
        "Legend:  bar lengths are to scale (one shared axis)  |  green = the experience's request and the clean exits  |  "
        "amber = kernel-held settlement  |  red = deadlines, non-proof, recovery  |  white = the kernel's checks.",
        WHITE, font=10, align="left"),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/B3-the-effect-vocabulary.md (cancellation proof, settle bound, ceiling, settle deadline, "
    "forced cleanup 'cancellation stuck', non-proof list, unconditional revocations); B2-state-ownership.md "
    "(cleanup failure enters recovery). Bars: length = value x %s px/ms (drawing scale)." % PX],
    30, YP + 198, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
