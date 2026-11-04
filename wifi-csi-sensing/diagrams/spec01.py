# -*- coding: utf-8 -*-
# 01 - CSI vs RSSI: multipath, static vs dynamic paths, what one frame gives you.
# Source: note A1 (OFDM, CSI, RSSI, multipath, static/dynamic paths, Doppler, Nyquist caution),
#         note A2 (beacon-driven report rate). Numbers loaded from constants.json.
from _common import *

t = Tags()
PAGE = dict(name="01-csi-vs-rssi", w=1280, h=840)

sp = V("ofdm_subcarrier_spacing_11a_n_ac")
n_leg = V("used_subcarriers_legacy_20MHz")
n_ht = V("used_subcarriers_ht_20MHz")
pairs = V("mimo_2x2_streams")
l24, l5 = V("wavelength_2g4"), V("wavelength_5g")
dop = V("doppler_walk_example_5g")
rate = V("csi_rate_beacon_illustrative")
nyq = rate / 2  # Nyquist limit of the beacon-rate stream (my arithmetic, note A1 caution)

BOXES = [
    title("CSI keeps the per-subcarrier fingerprint that RSSI averages away - and a moving body changes only the dynamic paths", 1280, 16),

    # --- the room (schematic) ---
    dict(id="room", x=30, y=62, w=620, h=440, rounded=False, align="left", valign="top", font=11,
         fill="#fbfbfb", stroke=NOTE_S, label="A room, seen from above (schematic, not to scale) [A1]"),
    dict(id="wall", x=120, y=96, w=420, h=16, rounded=False, align="center", valign="middle", font=10,
         fill=GREY, stroke=GREY_S, label="wall / furniture = STATIC reflector"),
    dict(id="tx", x=50, y=250, w=120, h=62, fill=BLUE, stroke=BLUE_S, font=11, bold=True,
         label="Transmitter (AP)\nsends known\ntraining symbols"),
    dict(id="rx", x=500, y=250, w=130, h=62, fill=BLUE, stroke=BLUE_S, font=11, bold=True,
         label="Receiver (device)\nestimates H per\nsubcarrier"),
    dict(id="person", x=300, y=395, w=56, h=80, shape="ellipse", fill=RED, stroke=RED_S, font=10,
         bold=True, label="person\nmoves"),
    dict(id="los_lbl", x=250, y=258, w=150, h=20, rounded=False, align="center", valign="middle",
         font=10, fill="#fbfbfb", stroke="#fbfbfb", fontcolor="#333333", label="line of sight (static)"),
    dict(id="wall_lbl", x=458, y=126, w=150, h=34, rounded=False, align="left", valign="middle",
         font=10, fill="#fbfbfb", stroke="#fbfbfb", fontcolor="#333333", label="reflected path\n(static)"),
    dict(id="dyn_lbl", x=420, y=440, w=150, h=48, rounded=False, align="left", valign="middle",
         font=10, fill="#fbfbfb", stroke="#fbfbfb", fontcolor=RED_S, bold=True,
         label="reflected path\n(DYNAMIC: its length\nchanges as she moves)"),

    # --- the model ---
    dict(id="model", x=30, y=514, w=620, h=110, fill=PURPLE, stroke=PURPLE_S, font=12, align="left",
         label="The channel at subcarrier frequency f is the sum of all paths [A1; Ma et al. 2019]:\n"
               "      H(f) = Σᵢ aᵢ · exp(−j 2π f τᵢ)  =  H_static(f) + H_dynamic(f, t)\n"
               "Each path rotates by a different angle at each f, so paths add up differently per subcarrier "
               "(frequency-selective fading). Motion changes only H_dynamic: amplitude and phase fluctuate "
               "(CARM, Wang et al. 2015)."),

    # --- what the receiver hands to software ---
    dict(id="csi_panel", x=680, y=62, w=570, h=300, rounded=False, align="left", valign="top", font=12,
         bold=True, fill="#ffffff", stroke=GREEN_S,
         label="CSI: one complex value per subcarrier per antenna pair, every frame"),
    dict(id="csi_cap", x=690, y=300, w=550, h=58, rounded=False, align="left", valign="top", font=10.5,
         fill="#ffffff", stroke="#ffffff",
         label="Bars = |H| per subcarrier (schematic shape, no data). Grey = frame before, red dashed = frame after "
               "the person moved: the fingerprint changes shape. Subcarriers %s kHz apart %s; %d used at 20 MHz "
               "legacy %s, %d in 802.11n HT20 %s; a 2x2 link has %d antenna pairs %s, each with its own row."
               % (fmt(sp), t("ofdm_subcarrier_spacing_11a_n_ac"), n_leg, t("used_subcarriers_legacy_20MHz"),
                  n_ht, t("used_subcarriers_ht_20MHz"), pairs, t("mimo_2x2_streams"))),

    dict(id="rssi_panel", x=680, y=376, w=570, h=126, rounded=False, align="left", valign="top", font=12,
         bold=True, fill="#ffffff", stroke=AMBER_S, label="RSSI: one power number per frame"),
    dict(id="rssi_a", x=700, y=410, w=160, h=40, fill=AMBER, stroke=AMBER_S, font=11,
         label="frame before:\none number"),
    dict(id="rssi_b", x=880, y=410, w=160, h=40, fill=AMBER, stroke=AMBER_S, font=11, dashed=True,
         label="frame after:\nnearly the same"),
    dict(id="rssi_cap", x=1050, y=400, w=195, h=98, rounded=False, align="left", valign="top", font=10.5,
         fill="#ffffff", stroke="#ffffff",
         label="Power summed over the whole channel. Two different motions can give the same RSSI change and "
               "different CSI changes [A1]."),

    # --- timing numbers ---
    dict(id="timing", x=680, y=514, w=570, h=110, fill=AMBER, stroke=AMBER_S, font=11, align="left",
         label="How fast it fluctuates [A1]: one cycle per wavelength of path change; wavelength %s cm at 2.4 GHz %s, "
               "%s cm at 5 GHz %s. A reflected path changes at up to 2x body speed, so a 1 m/s walk gives up to "
               "~%s Hz at 5 GHz %s (Doppler).\nCAUTION: beacon-driven CSI at an illustrative %s Hz %s cannot "
               "represent anything above %s Hz (Nyquist, my arithmetic): you see aliased energy, not a clean "
               "Doppler spectrum."
               % (fmt(l24), t("wavelength_2g4"), fmt(l5), t("wavelength_5g"), fmt(dop),
                  t("doppler_walk_example_5g"), fmt(rate), t("csi_rate_beacon_illustrative"), fmt(nyq))),

    legend_box("legend", 30, 636, 1220, 46,
               "Legend:  blue = radios | red, red dashed = dynamic (motion-dependent) | grey = static | purple = model | "
               "green frame = CSI (PHY-layer detail) | amber = RSSI and timing caveat.\n"
               "[A1], [A2] = kit notes. [n] = constants.json entry listed below; ILLUSTRATIVE values are round "
               "teaching values, never measurements."),
]

# schematic CSI bars (shape only, no data)
before = [60, 95, 130, 105, 55, 30, 48, 100, 150, 160, 115, 72, 40]
after = [70, 80, 100, 125, 85, 40, 30, 70, 120, 165, 140, 95, 55]
base_y, x0 = 292, 712
for i, (hb, ha) in enumerate(zip(before, after)):
    hb, ha = hb * 1.25, ha * 1.25
    BOXES.append(dict(id="bb%d" % i, x=x0 + i * 40, y=int(base_y - hb), w=26, h=int(hb), rounded=False,
                      fill="#cccccc", stroke="#999999", label=""))
    BOXES.append(dict(id="ba%d" % i, x=x0 + i * 40 + 6, y=int(base_y - ha), w=26, h=int(ha), rounded=False,
                      fill="none", stroke=RED_S, dashed=True, sw=1.5, label=""))
BOXES.append(dict(id="axis_lbl", x=700, y=base_y - 1, w=540, h=2, rounded=False, fill="#333333",
                  stroke="#333333", label=""))

LINES = [
    # line of sight
    dict(x1=170, y1=281, x2=500, y2=281, color="#666666", width=2, arrow="classic"),
    # static reflection off the wall
    dict(x1=130, y1=250, x2=330, y2=112, color="#666666", width=1.5),
    dict(x1=330, y1=112, x2=545, y2=250, color="#666666", width=1.5, arrow="classic"),
    # dynamic reflection off the person
    dict(x1=150, y1=312, x2=300, y2=432, color=RED_S, width=2, dashed=True),
    dict(x1=356, y1=432, x2=520, y2=312, color=RED_S, width=2, dashed=True, arrow="classic"),
]

EDGES = []

BOXES.append(sources_box(30, 694, 1220, 132, t.foot(
    "Notes: [A1] CSI and multipath (OFDM, CSI vs RSSI, static/dynamic paths, Doppler, Nyquist caution); "
    "[A2] what the hardware gives you. Public refs: IEEE 802.11 OFDM PHY; Ma, Zhou, Wang, CSUR 2019; "
    "Wang et al. MobiCom 2015 (CARM); Qian et al. 2017 (Widar/WiDance Doppler)."), 9.5))
