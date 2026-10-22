# -*- coding: utf-8 -*-
# 04 — Bench topology (C3): robot computer + separate harness machine; fakes, stubs, synthetic
#      inputs, bag replay; dedicated low-latency control link vs bulk feed link; two network islands;
#      observers on their own core; clock-sync probe.
# Source: notes C3 (harness, fakes, stubs, synthetic input, bag replay, islands, second machine) and
#         B2 (cross-machine clock offset / SNTP), B0/B4 (observer core).

PAGE = dict(name="04-bench-topology", w=1340, h=860)

ROBOT = "#dae8fc"; ROBOT_S = "#6c8ebf"
HARN = "#ffe6cc"; HARN_S = "#d79b00"
FAKE = "#d5e8d4"; FAKE_S = "#82b366"
OBS = "#e1d5e7"; OBS_S = "#9673a6"
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"
HI = "#f8cecc"; HI_S = "#b85450"

BOXES = [
    dict(id="title", x=20, y=12, w=1300, h=30, rounded=False, align="center", valign="middle",
         bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="Two machines: only the real stack runs on the robot; everything that stands in for the world runs on a separate harness machine"),

    # ---- ROBOT COMPUTER (left) ----
    dict(id="robot", x=50, y=70, w=560, h=560, rounded=True, fill="#eef4fc", stroke=ROBOT_S,
         font=13, bold=True, align="left", valign="top",
         label="ROBOT COMPUTER  -  runs ONLY the real deployed stack (the system under test)"),
    dict(id="r_stack", x=80, y=120, w=300, h=150, rounded=True, fill=ROBOT, stroke=ROBOT_S,
         font=11, align="left", valign="top",
         label="Real services (A0-A7):\n- camera / depth / VIO\n- people perception\n- mapping + navigation\n- voice (VAD, wake-word)\n- VLA + cognition\n- middleware router, telemetry"),
    dict(id="r_ctrl", x=80, y=286, w=300, h=90, rounded=True, fill=HI, stroke=HI_S,
         font=11, bold=True, align="left", valign="top",
         label="Whole-body control loop (A4)\nMLP policy on ISOLATED cores\n50 Hz / 20 ms deadline\n(the island the bench tests)"),
    dict(id="r_obs", x=80, y=400, w=300, h=90, rounded=True, fill=OBS, stroke=OBS_S,
         font=11, align="left", valign="top",
         label="Observers / probes (B0, B2, B4)\non their OWN dedicated core,\noff the application cores,\nready + settled BEFORE t0"),
    dict(id="r_clk", x=80, y=512, w=300, h=72, rounded=True, fill=NOTE, stroke=NOTE_S,
         font=11, align="left", valign="top",
         label="Clock-sync probe (B2)\nSNTP, several times/sec\nreports a bounded offset\n(illustrative < 0.5 ms)"),
    dict(id="r_isl_a", x=410, y=130, w=170, h=200, rounded=True, fill="#eafaf1", stroke=FAKE_S,
         font=10, bold=True, align="center", valign="top",
         label="ISLAND A\n(control + sensor\nwire protocols)\n\nfast bus endpoints,\nmic stream,\ncamera topics"),
    dict(id="r_isl_b", x=410, y=400, w=170, h=185, rounded=True, fill="#fdf2f2", stroke=HI_S,
         font=10, bold=True, align="center", valign="top",
         label="ISLAND B\n(bulk feeds +\ncloud calls)\n\nsynthetic camera,\nbag replay,\ncloud-API calls"),

    # ---- HARNESS MACHINE (right) ----
    dict(id="harness", x=730, y=70, w=560, h=560, rounded=True, fill="#fff6ec", stroke=HARN_S,
         font=13, bold=True, align="left", valign="top",
         label="HARNESS MACHINE  -  stands in for the physical world; its CPU is measured HERE, never counted as stack load"),
    dict(id="h_motor", x=760, y=120, w=250, h=72, rounded=True, fill=FAKE, stroke=FAKE_S,
         font=11, align="left", valign="top",
         label="Fake motor boards (C3, A4)\nreal wire protocol + framing,\nreal rate (100-1000 Hz)"),
    dict(id="h_mic", x=760, y=204, w=250, h=72, rounded=True, fill=FAKE, stroke=FAKE_S,
         font=11, align="left", valign="top",
         label="Fake microphone board (C3, A5)\nmatch frames/pkt + packets/msg\n(wrong framing biases every consumer)"),
    dict(id="h_cam", x=760, y=288, w=250, h=72, rounded=True, fill=FAKE, stroke=FAKE_S,
         font=11, align="left", valign="top",
         label="Synthetic camera (C3, A2)\ngenerate frames with N people,\nor inject ground-truth detections"),
    dict(id="h_bag", x=760, y=372, w=250, h=64, rounded=True, fill=FAKE, stroke=FAKE_S,
         font=11, align="left", valign="top",
         label="Bag replay (C3, A3)\nrecorded motion drives bursty\nmapping; person-data stays local"),
    dict(id="h_stub", x=760, y=448, w=250, h=72, rounded=True, fill=FAKE, stroke=FAKE_S,
         font=11, align="left", valign="top",
         label="Cloud-API stubs (C3, A5/A6)\nfaithful schema + status codes,\nLABELLED latency assumption"),
    dict(id="h_obs", x=760, y=532, w=250, h=64, rounded=True, fill=OBS, stroke=OBS_S,
         font=11, align="left", valign="top",
         label="Harness CPU measured here\n(not counted as stack load)"),
    dict(id="h_clk", x=1040, y=532, w=220, h=64, rounded=True, fill=NOTE, stroke=NOTE_S,
         font=11, align="left", valign="top",
         label="Clock-sync peer (B2)\nSNTP responder for\nthe offset bound"),
]

# ---- the two inter-machine links ----
BOXES += [
    dict(id="link1", x=620, y=210, w=100, h=56, rounded=True, fill=HI, stroke=HI_S,
         font=10, bold=True, align="center", valign="middle",
         label="DEDICATED\nlow-latency\nCONTROL link"),
    dict(id="link2", x=620, y=460, w=100, h=56, rounded=True, fill=ROBOT, stroke=ROBOT_S,
         font=10, bold=True, align="center", valign="middle",
         label="BULK link\n(feeds,\nreplay)"),
]

# legend + sources
BOXES += [
    dict(id="legend", x=50, y=660, w=620, h=100, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\nblue = robot (system under test)   amber = harness machine\ngreen = a faithful fake / stub / synthetic input   purple = observers & harness-CPU accounting\nred = the hard control loop + its dedicated link (the thing most at risk)\nTwo links: a DEDICATED low-latency link for control (so its timing is not stolen) and a BULK link for\nfeeds; TWO network ISLANDS so a live and a synthetic source sharing a topic name do not collide."),
    dict(id="src", x=690, y=660, w=600, h=100, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Source: note C3 (harness, second machine, fake boards + framing fidelity, schema-faithful stubs, synthetic input / detection injection, bag replay, network islands + cut edges). "
               "Control loop + isolation: A4. Fake-mic framing + per-message cost: A5. Synthetic N people: A2. Bursty mapping bag replay: A3. "
               "Cross-machine clock offset by SNTP, bound < smallest latency: B2 (RFC 4330). Observer core: B0, B4. "
               "Rates ILLUSTRATIVE: motor bus 100-1000 Hz [motor_bus_rate_illustrative]; offset < 0.5 ms [clock_offset_target_illustrative]. No measured robot numbers."),
]

EDGES = [
    # robot islands <-> links
    dict(src="r_isl_a", dst="link1", color="#b85450", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="link1", dst="h_motor", color="#b85450", bold=True, sx=1, sy=0.3, dx=0, dy=0.5),
    dict(src="r_isl_b", dst="link2", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="link2", dst="h_cam", color="#6c8ebf", sx=1, sy=0.3, dx=0, dy=0.5),
    # clock probe <-> peer
    dict(src="r_clk", dst="h_clk", color="#999999", dashed=True, sx=1, sy=0.5, dx=0, dy=0.5),
]
