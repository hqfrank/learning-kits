# -*- coding: utf-8 -*-
# 03 — Solo levels: nested L1 c L2 c L3; what each answers; the gaps; idle floor vs working cost
# Source: note C2 (L1 engine / L2 deployed service / L3 service + upstream; idle floor; drivers).

PAGE = dict(name="03-solo-levels", w=1280, h=820)

L3F = "#e1d5e7"; L3S = "#9673a6"   # L3 outer
L2F = "#dae8fc"; L2S = "#6c8ebf"   # L2 middle
L1F = "#d5e8d4"; L1S = "#82b366"   # L1 inner
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"
GAP = "#ffe6cc"; GAP_S = "#d79b00"
HI = "#f8cecc"; HI_S = "#b85450"

BOXES = [
    dict(id="title", x=20, y=12, w=1240, h=30, rounded=False, align="center", valign="middle",
         bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="Three solo levels of realism: the unit is the DEPLOYED SERVICE, not the model - and the gaps between levels are the finding"),

    # L3 outer container
    dict(id="l3", x=60, y=70, w=740, h=470, rounded=True, fill=L3F, stroke=L3S,
         font=13, bold=True, align="left", valign="top",
         label="L3  -  service WITH its real upstream\nanswers: how fast is the service on REAL INPUT?\n(e.g. the camera service feeding mapping)"),
    # L2 middle container
    dict(id="l2", x=120, y=190, w=620, h=320, rounded=True, fill=L2F, stroke=L2S,
         font=13, bold=True, align="left", valign="top",
         label="L2  -  the service AS DEPLOYED\nanswers: how fast is the SERVICE?\nreal container + runtime + pre/post-processing, driven through its own interface"),
    # L1 inner container
    dict(id="l1", x=190, y=320, w=480, h=160, rounded=True, fill=L1F, stroke=L1S,
         font=13, bold=True, align="center", valign="middle",
         label="L1  -  the engine alone\nanswers: how fast is the NETWORK?\ncompiled inference engine timed in isolation\n(trtexec-style: no service wrapper, no middleware)\n= the floor"),

    # gap annotations (between the nested rings)
    dict(id="gap21", x=820, y=230, w=420, h=90, rounded=True, fill=GAP, stroke=GAP_S,
         font=12, align="left", valign="middle",
         label="GAP  L2 - L1 = the service's OWN overhead\n= the CPU 'glue' (pre/post-processing, container,\nruntime) around the bare network. On a small robot\nthis glue usually dominates (see A2)."),
    dict(id="gap32", x=820, y=110, w=420, h=90, rounded=True, fill=GAP, stroke=GAP_S,
         font=12, align="left", valign="middle",
         label="GAP  L3 - L2 = the cost of REAL UPSTREAM data\n= real input shape and timing from the upstream\nservice it consumes. Captures real-input cost, but\nadds the upstream's variability."),

    # idle floor vs working cost SIDE PANEL
    dict(id="side_hdr", x=820, y=340, w=420, h=26, rounded=False, bold=True, font=12,
         fill=HI, stroke=HI_S, label="SIDE PANEL: idle floor vs working cost"),
    dict(id="idle", x=820, y=372, w=200, h=120, rounded=True, fill=NOTE, stroke=NOTE_S,
         font=11, align="left", valign="top",
         label="IDLE FLOOR\nan event-driven service\nwith NO input does almost\nnothing (~0 cost).\nThis is NOT its working\ncost. Must be labelled\n'idle floor', never\nreported as the cost."),
    dict(id="work", x=1040, y=372, w=200, h=120, rounded=True, fill="#d5e8d4", stroke=L1S,
         font=11, align="left", valign="top",
         label="WORKING COST\nDRIVE the service through\nits own API:\n- speech plan -> voice\n- inject detections -> perception\n- replay motion -> mapping\n- command a mode -> control\nso it does REAL work."),

    # bottom guidance band
    dict(id="guide", x=60, y=560, w=1180, h=96, rounded=True, fill="#f0f0f0", stroke="#999999",
         font=11, align="left", valign="middle",
         label="HOW TO USE (C2):  Measure SOLO before combined - the clean per-service baseline is the DENOMINATOR for the interference factor the combined run reveals (C6); it is a result, not a rehearsal.  "
               "Pick the level that answers your question: L1 for the network floor, L2 for the deployable cost, L3 for real-input cost.  "
               "Measure the deployed service (L2), not the bare model (L1) - the network is only a fraction of the service's cost.  "
               "A 'replaced pair' (sized stand-in) is measured at its level and labelled with its basis, so the combined run adds a known, labelled quantity."),
]

# legend + sources
BOXES += [
    dict(id="legend", x=60, y=676, w=560, h=76, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\nNesting = increasing realism: L1 (engine) within L2 (deployed service) within L3 (+ real upstream)\ngreen = L1 engine   blue = L2 service   purple = L3 upstream\namber = the gap between two levels (what each gap measures)   red = the idle-floor caveat"),
    dict(id="src", x=640, y=676, w=600, h=76, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Source: note C2 (solo runs and levels). L1 = a trtexec-style engine timing (NVIDIA TensorRT, docs.nvidia.com/deeplearning/tensorrt/). "
               "'Idle floor', 'working cost', 'driver', and 'replaced pair' are C2 terms. The interference factor the baseline feeds is defined in C6. No measured robot numbers."),
]

EDGES = []
