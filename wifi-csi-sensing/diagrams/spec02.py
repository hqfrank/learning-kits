# -*- coding: utf-8 -*-
# 02 - Where one link is sensitive: Fresnel zones, ends vs middle, range off the LoS, walls.
# Source: note A1 (Fresnel zones, three single-link patterns, range, wall), note C5 (single-device homes).
from _common import *

t = Tags()
PAGE = dict(name="02-single-link-sensitivity", w=1280, h=768)

d = V("link_length_illustrative")
r5 = V("fresnel_first_zone_mid_radius_example", "5GHz_4m_link")
r24 = V("fresnel_first_zone_mid_radius_example", "2g4_4m_link")
walk = V("single_link_range_illustrative")
small = V("small_motion_range_illustrative")

CX, CY = 445, 290  # link midpoint on the canvas

BOXES = [
    title("One link sees motion best near its two radios, less mid-link, and almost nothing a few metres off the line of sight or behind a wall", 1280, 15),

    dict(id="scene", x=30, y=60, w=860, h=470, rounded=False, align="left", valign="top", font=11,
         fill="#fbfbfb", stroke=NOTE_S, label="One link, seen from above (schematic: zone widths exaggerated, not to scale) [A1]"),
    # detectable band for walking (drawn first, under the zones)
    dict(id="band", x=60, y=110, w=800, h=330, rounded=True, dashed=True, fill="#f3f7fc", stroke=BLUE_S,
         valign="top", align="left", font=10.5, fontcolor=BLUE_S,
         label="walking visible out to about %s m from the LoS %s (illustrative); hand-waving about %s m %s"
               % (fmt(walk), t("single_link_range_illustrative"), fmt(small), t("small_motion_range_illustrative"))),
    dict(id="z3", x=CX - 370, y=CY - 100, w=740, h=200, shape="ellipse", fill="none", stroke="#bbbbbb",
         label=""),
    dict(id="z2", x=CX - 350, y=CY - 68, w=700, h=136, shape="ellipse", fill="none", stroke="#999999",
         label=""),
    dict(id="z1", x=CX - 330, y=CY - 36, w=660, h=72, shape="ellipse", fill="#ece4f1", stroke=PURPLE_S,
         sw=2, label=""),
    dict(id="z3l", x=CX - 30, y=CY - 98, w=60, h=26, rounded=False, fill="none", stroke="none", font=10,
         fontcolor="#777777", label="zone 3"),
    dict(id="z2l", x=CX - 30, y=CY - 66, w=60, h=26, rounded=False, fill="none", stroke="none", font=10,
         fontcolor="#555555", label="zone 2"),
    dict(id="z1l", x=CX - 60, y=CY - 34, w=120, h=22, rounded=False, fill="none", stroke="none", font=10,
         bold=True, fontcolor=PURPLE_S, label="first Fresnel zone"),

    dict(id="tx", x=56, y=CY - 26, w=96, h=52, fill=BLUE, stroke=BLUE_S, font=11, bold=True, label="AP\n(transmitter)"),
    dict(id="rx", x=738, y=CY - 26, w=96, h=52, fill=BLUE, stroke=BLUE_S, font=11, bold=True, label="device\n(receiver)"),

    # example targets
    dict(id="pA", x=168, y=CY + 6, w=34, h=34, shape="ellipse", fill=RED, stroke=RED_S, font=10, bold=True, label="A"),
    dict(id="pB", x=CX - 17, y=CY + 2, w=34, h=34, shape="ellipse", fill=AMBER, stroke=AMBER_S, font=10, bold=True, label="B"),
    dict(id="pC", x=600, y=390, w=34, h=34, shape="ellipse", fill=GREY, stroke=GREY_S, font=10, bold=True, label="C"),
    dict(id="wall", x=60, y=452, w=800, h=14, rounded=False, fill="#bbbbbb", stroke="#666666", font=9,
         label="wall"),
    dict(id="pD", x=430, y=478, w=34, h=34, shape="ellipse", fill="#ffffff", stroke=GREY_S, dashed=True,
         font=10, bold=True, label="D"),
    dict(id="pD_l", x=470, y=476, w=380, h=40, rounded=False, align="left", valign="middle", font=10.5,
         fill="none", stroke="none", label="D: next room, behind the wall - most of the effect removed [A1]; "
                                           "but what remains is a through-wall false positive [B4]"),

    # right-hand panel: the three patterns + Fresnel numbers
    dict(id="pat", x=910, y=60, w=340, h=250, fill=GREY, stroke=GREY_S, align="left", valign="top", font=11,
         label="What one link sees - a power-fading simulation and single-link measurements agreed [A1]:\n\n"
               "A  motion close to EITHER radio changes the CSI most (red).\n\n"
               "B  on the LoS, motion mid-link changes it LESS than near the ends: the first zone is narrowest at "
               "the radios, so a body there fills more of it (amber).\n\n"
               "C  sensitivity falls steeply outside the first zone (grey).\n\n"
               "Also: motion ON the LoS drops power more than motion beside it."),
    dict(id="fz", x=910, y=322, w=340, h=208, fill=PURPLE, stroke=PURPLE_S, align="left", valign="top", font=11,
         label="Fresnel zones (Wang et al. UbiComp 2016): nested ellipses with the radios at the foci; zone n ends "
               "where a reflected path is n half-wavelengths longer than the LoS. First-zone radius at mid-link:\n"
               "      r1 = 0.5 x sqrt(lambda x d)\n"
               "For an illustrative d = %s m link %s:\n"
               "   %s m at 5 GHz, %s m at 2.4 GHz %s\n"
               "A body crossing zone boundaries makes one fluctuation per boundary."
               % (fmt(d), t("link_length_illustrative"), fmt(r5), fmt(r24),
                  t("fresnel_first_zone_mid_radius_example"))),

    dict(id="so", x=30, y=542, w=1220, h=52, fill=AMBER, stroke=AMBER_S, align="left", font=11.5, bold=True,
         label="So what: placement decides coverage. A room with no device is covered only weakly, through walls, "
               "and one link cannot tell motion near its AP end from motion near its device end - only a "
               "comparison across several links resolves that [B4, C5]."),
    legend_box("legend", 30, 604, 1220, 44,
               "Legend: blue = radios | purple fill = first Fresnel zone, grey rings = zones 2-3 | dashed blue = "
               "illustrative detectable band | target fill: red = large change, amber = smaller, grey = weak, "
               "dashed white = behind a wall.  [A1], [B4], [C5] = kit notes; [n] = constants.json entries below."),
]

LINES = [
    dict(x1=152, y1=CY, x2=738, y2=CY, color="#444444", width=2, arrow="classic"),
]
EDGES = []

BOXES.append(sources_box(30, 658, 1220, 96, t.foot(
    "Notes: [A1] CSI and multipath (Fresnel zones, single-link patterns, range, wall); [B4] multi-device joint "
    "detection; [C5] limits. Public ref: Wang et al., UbiComp 2016 (Fresnel-zone model)."), 9.5))
