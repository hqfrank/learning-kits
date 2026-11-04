# -*- coding: utf-8 -*-
# 03 — The vision specialist's action cycle and the coordinate scaler (note 04).
# Frames are drawn to one common scale so the reader sees the aspect-ratio mismatch.
from math import gcd
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="03-vision-cycle-and-scaling", w=W, h=0)

rw, rh = V("cu_reference_frame_recommended"); t_ref = T("cu_reference_frame_recommended")
mw, mh = V("cu_max_resolution_advised"); t_max = T("cu_max_resolution_advised")
nw, nh = V("device_native_resolution_illustrative"); t_nat = T("device_native_resolution_illustrative")
cx, cy = V("model_click_illustrative"); t_clk = T("model_click_illustrative")
settle = "%s s %s" % (V("settle_delay_illustrative"), T("settle_delay_illustrative"))
tk = V("cu_tokens_per_screenshot"); t_tk = T("cu_tokens_per_screenshot")
keep = "%s %s" % (V("cu_screenshots_kept"), T("cu_screenshots_kept"))

# my arithmetic
sx, sy = rw / nw, rh / nh
dxp, dyp = round(cx / sx), round(cy / sy)
su = min(sx, sy)
uw, uh = round(nw * su), round(nh * su)
g1, g2 = gcd(nw, nh), gcd(rw, rh)
asp_n = "%d:%d" % (nw // g1, nh // g1)
asp_r = "%d:%d" % (rw // g2, rh // g2)
if (rh // g2) * 2 == 10:
    asp_r += " (= %d:10)" % (2 * rw // g2)

WH = lambda a, b: "%d×%d" % (a, b)

BOXES = [title("The model taps in its %s %s reference frame, the device taps in its own pixels: a consistent offset means the scaler is wrong, not the model" % (WH(rw, rh), t_ref), W)]

steps = [
    ("cap", "1  CAPTURE\nthe OS screen-capture API\n(MediaProjection); the user\nconsents before capture", DEVICE),
    ("down", "2  SCALE DOWN\nto the reference frame\n%s %s\n(advice: not above %s %s)" % (WH(rw, rh), t_ref, WH(mw, mh), t_max), GUARD),
    ("dec", "3  DECIDE  (model call)\nreturns left_click at\n(%d, %d) %s\nin reference px" % (cx, cy, t_clk), MODEL),
    ("up", "4  SCALE UP\nthe coordinate scaler maps it\nto (%d, %d) [calc]\nin device px" % (dxp, dyp), GUARD),
    ("act", "5  ACT\nthe accessibility service\ninjects the tap\n(dispatchGesture)", DEVICE),
    ("set", "6  SETTLE\nwait %s so the UI\nstops moving, then\ncapture again" % settle, DEVICE),
]
x = 30
for i, (sid, lab, pal) in enumerate(steps):
    BOXES.append(box(sid, x, 66, 190, 96, lab, pal, font=11, bold=False))
    x += 203

# frames drawn to one scale
S = 0.18
RX, RY = 60, 268
DX, DY = 400, 268
BOXES += [
    text("frames_t", 40, 214, 820, 40, "Both frames drawn to the SAME scale. Different aspect ratios (%s vs %s) mean the x and y scale factors differ." % (asp_n, asp_r), font=12, bold=True),
    box("ref", RX, RY, round(rw * S), round(rh * S), "REFERENCE FRAME\n(what the model sees)\n%s %s" % (WH(rw, rh), t_ref), MODEL, rounded=False, valign="top", font=11, fill="#eef8ec"),
    box("dev", DX, DY, round(nw * S), round(nh * S), "DEVICE NATIVE SCREEN\n(where the tap happens)\n%s %s" % (WH(nw, nh), t_nat), DEVICE, rounded=False, valign="top", font=11, fill="#eef4fc"),
]
rdx, rdy = RX + cx * S, RY + cy * S
ddx, ddy = DX + dxp * S, DY + dyp * S
BOXES += [
    box("rdot", round(rdx - 7), round(rdy - 7), 14, 14, "", MODEL, rx=7, fill="#82b366", stroke="#3d6b2a"),
    text("rdot_l", round(rdx + 10), round(rdy - 10), 120, 20, "(%d, %d) %s" % (cx, cy, t_clk), font=11, bold=True, fontcolor="#3d6b2a"),
    box("ddot", round(ddx - 7), round(ddy - 7), 14, 14, "", DEVICE, rx=7, fill="#6c8ebf", stroke="#2c4a7a"),
    text("ddot_l", round(ddx + 10), round(ddy - 10), 160, 20, "(%d, %d) [calc]" % (dxp, dyp), font=11, bold=True, fontcolor="#2c4a7a"),
]

BOXES.append(box("math", 880, 214, 370, 270,
    "THE SCALER ARITHMETIC  [calc]\n"
    "x scale = reference ÷ native = %d ÷ %d = %.3f\n"
    "y scale = %d ÷ %d = %.3g\n"
    "device tap = (%d ÷ %.3f, %d ÷ %.3g) = (%d, %d)\n\n"
    "The two scales differ because %s ≠ %s. A plain resize therefore STRETCHES the image. "
    "Vendor advice: preserve the aspect ratio when resizing.\n\n"
    "Uniform alternative: one scale = min(%.3f, %.3g) = %.3g, giving a %s image padded to %s.\n\n"
    "Either way: keep the factors, and apply their inverse to EVERY coordinate the model returns."
    % (rw, nw, sx, rh, nh, sy, cx, sx, cy, sy, dxp, dyp, asp_n, asp_r, sx, sy, su, WH(uw, uh), WH(rw, rh)),
    GUARD, align="left", valign="top", font=12))

BOXES += [
    box("diag", 30, 572, 610, 100,
        "DIAGNOSE A WRONG TAP\n"
        "- Consistent offset in one direction: almost always a scaling bug (coordinates applied to a display of a different size). Check the scaler before the prompt.\n"
        "- Near-miss on a small target: detail lost in down-scaling. Use the zoom action, or crop; not more prompt text.\n"
        "- Similar-looking wrong element: a more specific instruction, placed BEFORE the image in the message.",
        STOP, fill="#fff7f7", align="left", valign="top", font=11),
    box("knobs", 655, 572, 595, 100,
        "KNOBS AND THEIR TRADE\n"
        "- Reference frame size: smaller = fewer image tokens and a faster reply; larger = small text stays readable. zoom inspects one region at full resolution.\n"
        "- Settle delay %s: too short = a half-drawn screen and a repeated action; too long = every step pays the wait.\n"
        "- Screenshot history: %s-%s input tokens per screenshot %s; keep the last %s (diagram 05)." % (settle, num(tk[0]), num(tk[1]), t_tk, keep),
        NOTE, align="left", valign="top", font=11),
    box("legend", 30, 687, 1220, 36,
        "Legend:  blue = device code  |  amber = the scaler, where most tap bugs live  |  green = the model call  |  green dot = point the model asked for (reference px)  |  "
        "blue dot = where the device taps (native px)  |  arrows: one action cycle; the dashed return is the next observation (diagram 04)",
        WHITE, align="left", font=11),
]

EDGES = [dict(src=a, dst=b, color="#666666", sx=1, sy=0.5, dx=0, dy=0.5)
         for a, b in zip(["cap", "down", "dec", "up", "act"], ["down", "dec", "up", "act", "set"])]
EDGES += [
    dict(src="set", dst="cap", label="next observation", color="#666666", dashed=True, sx=0.5, sy=1, dx=0.5, dy=1,
         points=[(1140, 188), (125, 188)], lpos=(630, 188), lw=120),
    dict(src="ref", dst="dev", label="scaler\nx ÷ %.3f\ny ÷ %.3g" % (sx, sy), color="#d79b00", bold=True,
         sx=1, sy=0.6, dx=0, dy=0.3, lpos=(342, 330), lw=70),
]

src_box, bottom = footer_box(T, [
    "Mechanism: notes/04-the-vision-specialist.md (five-step cycle, worked scaling example, grounding errors, knobs). Public docs: computer-use tool documentation, sections "
    "'Available actions', 'Size screenshots to fit image limits', 'Diagnose click issues', 'Manage screenshot history', 'Optimize model performance with prompting'; "
    "Android MediaProjection guide and AccessibilityService.dispatchGesture reference (see ../SOURCES.md)."],
    30, 736, 1220)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
