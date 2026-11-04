# -*- coding: utf-8 -*-
# 04 - Multi-device joint detection: AP side vs client side by cross-correlation; link graph; device-count result.
# Source: note B4 (softAP links, cross-correlation rule, sorted nodes/links, through-wall, device-count result).
from _common import *

t = Tags()
PAGE = dict(name="04-joint-detection", w=1280, h=814)

dev = V("devices_tpr_illustrative")
mot = V("motion_type_tpr_illustrative")
N = V("home_study_size_illustrative", "devices_per_home")
n_links_all = N * N  # N AP links + N(N-1) directed device-to-device links (note B4, my arithmetic)

AP = dict(id="ap", x=200, y=88, w=86, h=40, fill=BLUE, stroke=BLUE_S, font=11, bold=True, label="AP")
DEV = [
    dict(id="d1", x=48, y=96, w=74, h=34, label="device 1"),
    dict(id="d2", x=462, y=164, w=74, h=34, label="device 2"),
    dict(id="d3", x=48, y=414, w=74, h=34, label="device 3"),
    dict(id="d4", x=462, y=414, w=74, h=34, label="device 4"),
]
for d in DEV:
    d.update(fill=GREEN, stroke=GREEN_S, font=10.5, bold=True)

BOXES = [
    title("One link cannot tell AP-side from device-side motion; compare links across devices - and add "
          "device-to-device links, because links grow as N x N", 1280, 15),
    dict(id="home_lbl", x=30, y=50, w=530, h=10, rounded=False, fill="none", stroke="none", font=10, label=""),
]
for i, (x, y) in enumerate([(30, 64), (300, 64), (30, 272), (300, 272)]):
    BOXES.append(dict(id="room%d" % (i + 1), x=x, y=y, w=262, h=200, rounded=False, align="left", valign="top",
                      font=10, fill="none", stroke="#888888", label="room %d" % (i + 1)))
BOXES += [AP] + DEV
BOXES += [
    dict(id="pa", x=222, y=140, w=26, h=26, shape="ellipse", fill=RED, stroke=RED_S, font=9, bold=True, label="P"),
    dict(id="pa_l", x=150, y=170, w=150, h=34, rounded=False, fill="#ffffff", stroke="#ffffff", font=9.5,
         fontcolor=RED_S, label="motion near the AP:\nall AP links move together"),
    dict(id="pb", x=430, y=440, w=26, h=26, shape="ellipse", fill=RED, stroke=RED_S, font=9, bold=True, label="Q"),
    dict(id="pb_l", x=306, y=432, w=120, h=34, rounded=False, fill="#ffffff", stroke="#ffffff", font=9.5, align="right",
         fontcolor=RED_S, label="motion near device 4:\nonly its links move"),

    dict(id="links", x=30, y=482, w=532, h=72, fill="#ffffff", stroke=GREY_S, font=10.5, align="left", valign="top",
         label="Link graph [B4]: blue solid = AP-device links (N); green dashed = device-to-device links via a softAP "
               "on each device, same channel as the AP, MAC-filtered. With N = %d devices %s: %d AP links become "
               "%d directed links (N x N, my arithmetic) - and the new links cross rooms the AP links never cross."
               % (N, t("home_study_size_illustrative"), N, n_links_all)),
    dict(id="wall", x=30, y=564, w=532, h=72, fill=AMBER, stroke=AMBER_S, font=10.5, align="left", valign="top",
         label="Through-wall false positives: motion next door reaches the links through the wall, weakened. "
               "Mitigate with more endpoints (the right room responds much more strongly), per-home sensitivity "
               "for thin walls, and fusion with a sensor that does not see through walls [B4]."),

    # rule panel
    dict(id="rule_h", x=590, y=64, w=660, h=26, rounded=False, align="left", valign="middle", font=12, bold=True,
         fill="none", stroke="none", label="Decision rule: cross-correlate CSI variation across devices [B4]"),
    dict(id="r1", x=590, y=94, w=660, h=40, fill=BLUE, stroke=BLUE_S, font=10.5, align="left",
         label="HIGH correlation across all AP links  ->  motion near the AP (P): every AP link shares the AP end"),
    dict(id="r2", x=590, y=140, w=660, h=40, fill=GREEN, stroke=GREEN_S, font=10.5, align="left",
         label="LOW correlation, one device's links active  ->  motion near that device (Q)"),
    dict(id="r3", x=590, y=186, w=660, h=40, fill=PURPLE, stroke=PURPLE_S, font=10.5, align="left",
         label="Several devices active, LOW mutual correlation  ->  several people, each near a device"),
    dict(id="sn", x=590, y=238, w=660, h=118, fill="#ffffff", stroke=GREY_S, font=10.5, align="left", valign="top",
         label="Where: sorted nodes and sorted links [B4]. Node variation w_i = sum_j v_ij; the node with the largest w is "
               "probably closest. Take links in order of v; if one end's w is clearly larger (w_i > w_j + T, margin T "
               "found empirically), keep the half-plane on that side of the link's perpendicular bisector. The "
               "intersection of kept half-planes is the detected area; often the first two or three links decide the "
               "room. Equal w at three nodes -> answer \"near several nodes\". Needs rough device positions."),

    # staircase chart
    dict(id="ch_h", x=590, y=366, w=660, h=24, rounded=False, align="left", valign="middle", font=12, bold=True,
         fill="none", stroke="none",
         label="Home-level TPR at 1%% FPR (ILLUSTRATIVE) %s" % t("devices_tpr_illustrative")),
]

# bar chart geometry: y = BASE - value * H
BASE, H, BX = 600, 190, 690
bars = [("1 device\nAP link only\n1 link", dev["1_device"], GREY, GREY_S),
        ("4 devices\nAP links only\n%d links" % N, dev["4_devices_ap_links_only"], BLUE, BLUE_S),
        ("4 devices\nAP + device-to-device\n%d links" % n_links_all, dev["4_devices_all_links"], GREEN, GREEN_S)]
for i, (lbl, v, f, s) in enumerate(bars):
    x = BX + i * 116
    h = int(round(v * H))
    BOXES.append(dict(id="bar%d" % i, x=x, y=BASE - h, w=90, h=h, rounded=False, fill=f, stroke=s,
                      font=13, bold=True, valign="top", label=fmt(v)))
    BOXES.append(dict(id="bl%d" % i, x=x - 12, y=BASE + 4, w=114, h=46, rounded=False, fill="none", stroke="none",
                      font=10, label=lbl))
for v in (0.0, 0.5, 1.0):
    BOXES.append(dict(id="tick%d" % int(v * 10), x=630, y=int(BASE - v * H) - 9, w=40, h=18, rounded=False,
                      fill="none", stroke="none", font=9.5, align="right", label=fmt(v)))
BOXES.append(dict(id="ch_note", x=1040, y=420, w=210, h=150, rounded=False, align="left", valign="top", font=10,
                  fill="#ffffff", stroke="#ffffff",
                  label="Same four devices: adding device-to-device links gained more than going from one device to "
                        "four on AP links. By scenario %s: near a device %s, room with no device %s, typing %s."
                        % (t("motion_type_tpr_illustrative"), fmt(mot["large_motion_near_device"]),
                           fmt(mot["room_without_device"]), fmt(mot["small_motion_typing"]))))

LINES = [dict(x1=672, y1=BASE, x2=1030, y2=BASE, color="#333333", width=1.5),
         dict(x1=672, y1=BASE, x2=672, y2=BASE - H, color="#333333", width=1.5),
         dict(x1=672, y1=BASE - H, x2=1022, y2=BASE - H, color="#bbbbbb", width=1, dashed=True)]


def _centre(b):
    return b["x"] + b["w"] / 2.0, b["y"] + b["h"] / 2.0


def _clip(a, b):
    """Segment between box centres, trimmed to the two box borders."""
    (x1, y1), (x2, y2) = _centre(a), _centre(b)
    dx, dy = x2 - x1, y2 - y1

    def frac(box):
        fx = (box["w"] / 2.0) / abs(dx) if dx else 1e9
        fy = (box["h"] / 2.0) / abs(dy) if dy else 1e9
        return min(fx, fy)
    fa, fb = frac(a) + 0.02, frac(b) + 0.02
    return x1 + dx * fa, y1 + dy * fa, x2 - dx * fb, y2 - dy * fb


for d in DEV:
    x1, y1, x2, y2 = _clip(AP, d)
    LINES.append(dict(x1=x1, y1=y1, x2=x2, y2=y2, color=BLUE_S, width=2.2, under=True))
for i in range(len(DEV)):
    for j in range(i + 1, len(DEV)):
        x1, y1, x2, y2 = _clip(DEV[i], DEV[j])
        LINES.append(dict(x1=x1, y1=y1, x2=x2, y2=y2, color=GREEN_S, width=1.6, dashed=True, under=True))

EDGES = []

BOXES += [
    legend_box("legend", 30, 662, 1220, 44,
               "Legend: blue = AP and AP-device links | green = devices, device-to-device links (dashed) | red P, Q = "
               "example motions | amber = through-wall caveat | bars: grey 1 device, blue 4 devices AP links, green 4 "
               "devices all links.  [B4] = kit note; [n] = constants.json entries below."),
]
BOXES.append(sources_box(30, 716, 1220, 84, t.foot(
    "Notes: [B4] multi-device joint detection (softAP links, cross-correlation rule, sorted nodes/links, through-wall "
    "false positives, device-count result); see also [C5] one-device homes. hostapd is open-source."), 9.5))
