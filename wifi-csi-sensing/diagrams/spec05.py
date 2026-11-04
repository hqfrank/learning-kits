# -*- coding: utf-8 -*-
# 05 - Room-level localisation by metric learning: train once on many homes, calibrate each home with one walk,
#      answer by nearest reference embedding (with an "unknown" distance threshold).
# Source: note B5 (metric learning, contrastive/triplet loss, Siamese, calibration walk, nearest neighbour,
#         network options); note B3 (room labelling rule); note C5 (drift). Number: triplet margin (public).
from _common import *

t = Tags()
PAGE = dict(name="05-room-metric-learning", w=1280, h=800)
margin = V("triplet_margin_facenet")

CW, X1, X2, X3 = 390, 30, 445, 860
BOXES = [
    title("Room localisation by metric learning: learn \"same room vs different room\" once from many homes - then a "
          "new home needs one calibration walk, not a new model", 1280, 15),
    dict(id="h1", x=X1, y=58, w=CW, h=30, fill=PURPLE, stroke=PURPLE_S, font=12, bold=True,
         label="1  TRAIN once, on many homes [B5]"),
    dict(id="h2", x=X2, y=58, w=CW, h=30, fill=BLUE, stroke=BLUE_S, font=12, bold=True,
         label="2  CALIBRATE once per new home [B5]"),
    dict(id="h3", x=X3, y=58, w=CW, h=30, fill=GREEN, stroke=GREEN_S, font=12, bold=True,
         label="3  INFER: nearest reference embedding [B5]"),

    # --- train ---
    dict(id="t_data", x=X1, y=100, w=CW, h=54, fill=GREY, stroke=GREY_S, font=10.5,
         label="CSI windows (subcarriers x time) from many homes, each labelled with the room the person was in "
               "(link labelling rule [B3])"),
    dict(id="t_a", x=X1, y=172, w=118, h=50, fill="#ffffff", stroke=PURPLE_S, font=10.5, bold=True,
         label="anchor\nroom K, home H"),
    dict(id="t_p", x=X1 + 136, y=172, w=118, h=50, fill="#ffffff", stroke=GREEN_S, font=10.5, bold=True,
         label="positive\nsame room K"),
    dict(id="t_n", x=X1 + 272, y=172, w=118, h=50, fill="#ffffff", stroke=RED_S, font=10.5, bold=True,
         label="negative\nother room, SAME home"),
    dict(id="t_net", x=X1, y=242, w=CW, h=70, fill=PURPLE, stroke=PURPLE_S, font=10.5,
         label="ONE shared network (Siamese) embeds all three. Options: 1-D conv over time + weighting over "
               "subcarriers; 1-D conv over time then over subcarriers; or 2-D conv on the window as an image."),
    dict(id="t_loss", x=X1, y=330, w=CW, h=96, fill="#ffffff", stroke=PURPLE_S, font=10.5, align="left",
         label="Triplet loss: require  d(anchor, negative) > d(anchor, positive) + margin.\nFaceNet uses a margin "
               "of %s on unit-length embeddings %s (public).\nContrastive loss (pairs) is the alternative: pull "
               "same-room pairs together, push other-room pairs a margin apart." % (fmt(margin),
                                                                                    t("triplet_margin_facenet"))),

    # --- calibrate ---
    dict(id="c_walk", x=X2, y=100, w=CW, h=54, fill=BLUE, stroke=BLUE_S, font=10.5,
         label="The user walks through each room once while the devices record CSI (the calibration walk)"),
    dict(id="c_emb", x=X2, y=172, w=CW, h=50, fill=BLUE, stroke=BLUE_S, font=10.5,
         label="Embed those windows with the trained network (no retraining)"),
    dict(id="c_ref", x=X2, y=242, w=CW, h=70, fill=BLUE, stroke=BLUE_S, font=10.5,
         label="Store one or a few REFERENCE embeddings per room of THIS home. Any number of rooms, any layout."),
    dict(id="c_age", x=X2, y=330, w=CW, h=96, fill=AMBER, stroke=AMBER_S, font=10.5, align="left",
         label="References age: furniture, doors and device moves change the CSI, so the walk must be refreshed "
               "[B5, C5]. Metric learning removes labels in the deployed home - it does NOT remove the need for "
               "many training homes."),

    # --- infer: embedding space ---
    dict(id="space", x=X3, y=100, w=CW, h=326, rounded=False, fill="#fbfbfb", stroke=GREEN_S, align="left",
         valign="top", font=10.5, label="Embedding space of one home (schematic, 2-D for drawing)"),
    dict(id="kA", x=X3 + 30, y=150, w=120, h=84, shape="ellipse", fill="#e8f0fa", stroke=BLUE_S, dashed=True,
         valign="top", font=10.5, bold=True, label="kitchen"),
    dict(id="kB", x=X3 + 210, y=140, w=130, h=90, shape="ellipse", fill="#ecf5e8", stroke=GREEN_S, dashed=True,
         valign="top", font=10.5, bold=True, label="living room"),
    dict(id="kC", x=X3 + 90, y=290, w=130, h=84, shape="ellipse", fill="#f4ecf7", stroke=PURPLE_S, dashed=True,
         valign="bottom", font=10.5, bold=True, label="bedroom"),
    dict(id="rA", x=X3 + 82, y=186, w=14, h=14, rounded=False, fill=BLUE_S, stroke=BLUE_S, label=""),
    dict(id="rB", x=X3 + 268, y=176, w=14, h=14, rounded=False, fill=GREEN_S, stroke=GREEN_S, label=""),
    dict(id="rC", x=X3 + 148, y=318, w=14, h=14, rounded=False, fill=PURPLE_S, stroke=PURPLE_S, label=""),
    dict(id="live", x=X3 + 238, y=244, w=18, h=18, shape="ellipse", fill=RED_S, stroke=RED_S, label=""),
    dict(id="live_l", x=X3 + 196, y=262, w=184, h=36, rounded=False, fill="none", stroke="none", font=10,
         fontcolor=RED_S, bold=True, label="live window -> nearest\nreference = living room"),
    dict(id="far", x=X3 + 330, y=330, w=18, h=18, shape="ellipse", fill="#ffffff", stroke=RED_S, dashed=True,
         label=""),
    dict(id="far_l", x=X3 + 236, y=350, w=150, h=50, rounded=False, fill="none", stroke="none", font=10,
         fontcolor=RED_S, align="right",
         label="farther than every reference\n-> answer \"unknown\": empty\nor the home has changed"),

    # --- why not a classifier + so what ---
    dict(id="why", x=X1, y=444, w=600, h=66, fill=RED, stroke=RED_S, font=11, align="left", valign="top",
         label="Why not a room classifier [B5]: a classifier has one output per class. A model trained on four-room "
               "homes has no meaning in a six-room home, and retraining per home needs a large labelled dataset. "
               "Metric learning turns per-home CLASSIFICATION (does not scale) into per-home CALIBRATION (one walk)."),
    dict(id="also", x=X1 + 620, y=444, w=600, h=66, fill=GREY, stroke=GREY_S, font=11, align="left", valign="top",
         label="Two side uses [B5]: (1) single-device tests can still TRAIN on device-to-device links labelled by the "
               "room rule, adding data without changing what is available at test time; (2) devices whose CSI changes "
               "look alike are probably in the same room - auto-assign smart-home devices to rooms."),
    legend_box("legend", 30, 522, 1220, 44,
               "Legend: purple = training (one network for all homes) | blue = per-home calibration | green = "
               "inference; dashed ellipses = rooms, squares = reference embeddings, red dot = live window, hollow red "
               "= unknown | amber = drift caveat | red panel = the reason for the design.  [B3], [B5], [C5] = kit notes."),
]

EDGES = [
    dict(src="t_data", dst="t_a", color=PURPLE_S, sx=0.15, sy=1, dx=0.5, dy=0),
    dict(src="t_data", dst="t_p", color=PURPLE_S, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="t_data", dst="t_n", color=PURPLE_S, sx=0.85, sy=1, dx=0.5, dy=0),
    dict(src="t_a", dst="t_net", color=PURPLE_S, sx=0.5, sy=1, dx=0.15, dy=0),
    dict(src="t_p", dst="t_net", color=PURPLE_S, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="t_n", dst="t_net", color=PURPLE_S, sx=0.5, sy=1, dx=0.85, dy=0),
    dict(src="t_net", dst="t_loss", color=PURPLE_S, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="c_walk", dst="c_emb", color=BLUE_S, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="c_emb", dst="c_ref", color=BLUE_S, sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="t_net", dst="c_emb", color=PURPLE_S, dashed=True, sx=1, sy=0.3, dx=0, dy=0.7),
    dict(src="c_ref", dst="space", color=BLUE_S, dashed=True, sx=1, sy=0.5, dx=0, dy=0.65),
]
LINES = [
    dict(x1=X3 + 247, y1=244, x2=X3 + 276, y2=192, color=RED_S, width=1.8, arrow="classic"),
]

BOXES.append(sources_box(30, 578, 1220, 56, t.foot(
    "Notes: [B5] room localisation by metric learning (no result numbers - a proposed method); [B3] link labelling; "
    "[C5] drift. Public refs: Hadsell, Chopra, LeCun, CVPR 2006 (contrastive); Schroff, Kalenichenko, Philbin, "
    "CVPR 2015 (FaceNet, triplet)."), 9.5))
PAGE["h"] = 648
