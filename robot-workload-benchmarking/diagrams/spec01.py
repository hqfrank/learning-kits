# -*- coding: utf-8 -*-
# 01 — The stack as concurrent pipelines (sense -> perceive -> decide -> act)
# Source: notes A0, A1, A2, A3, A4, A5, A6, A7; rates from constants.json (all illustrative).
# Colour = timing class: red-ish = hard real-time, amber = soft real-time, grey-blue = best-effort.
# Each box names the resource it loads (CPU / GPU / both), its loop-rate class, and on-board vs cloud.

PAGE = dict(name="01-stack-as-pipelines", w=1280, h=880)

HARD = "#f8cecc"; HARD_S = "#b85450"      # hard real-time
SOFT = "#ffe6cc"; SOFT_S = "#d79b00"      # soft real-time
BEST = "#dae8fc"; BEST_S = "#6c8ebf"      # best-effort
SENSE = "#e1d5e7"; SENSE_S = "#9673a6"    # sense (raw I/O, mixed class)
FLOOR = "#d5e8d4"; FLOOR_S = "#82b366"    # core partition floor
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"

# column header band
COLX = [40, 350, 660, 970]   # x of the four stage columns
COLW = 290
HY = 70

BOXES = [
    dict(id="title", x=20, y=12, w=1240, h=30, rounded=False, align="center",
         valign="middle", bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="A home robot is not one program with one bottleneck: it is a crowd of pipelines with different deadlines sharing one CPU, one GPU, one memory pool"),

    # stage column headers
    dict(id="h_sense", x=COLX[0], y=HY, w=COLW, h=28, rounded=False, bold=True, font=12,
         fill=SENSE, stroke=SENSE_S, label="SENSE  (read hardware)"),
    dict(id="h_perc", x=COLX[1], y=HY, w=COLW, h=28, rounded=False, bold=True, font=12,
         fill=SOFT, stroke=SOFT_S, label="PERCEIVE  (raw data -> meaning)"),
    dict(id="h_dec", x=COLX[2], y=HY, w=COLW, h=28, rounded=False, bold=True, font=12,
         fill=BEST, stroke=BEST_S, label="DECIDE  (choose what to do)"),
    dict(id="h_act", x=COLX[3], y=HY, w=COLW, h=28, rounded=False, bold=True, font=12,
         fill=HARD, stroke=HARD_S, label="ACT  (command motors + speaker)"),

    # --- Row 1: camera / depth + odometry (A1) ---
    dict(id="cam", x=COLX[0], y=120, w=COLW, h=70, fill=SENSE, stroke=SENSE_S, font=11,
         label="Depth camera + IMU [A1]\nstereo pair, IMU at 100s Hz\nboth CPU+GPU | on-board"),
    dict(id="depth", x=COLX[1], y=120, w=COLW, h=70, fill=SOFT, stroke=SOFT_S, font=11,
         label="Depth map / point cloud / VIO [A1]\nneural depth = largest GPU cost\nboth CPU+GPU | soft ~30 Hz | on-board"),

    # --- Row 2: people perception (A2) ---
    dict(id="pp", x=COLX[1], y=204, w=COLW, h=78, fill=SOFT, stroke=SOFT_S, font=11,
         label="People perception [A2]\ndetect/face/re-ID/pose/speaker + track\nnetworks GPU, CPU glue dominates\nboth | soft ~10 Hz | on-board"),

    # --- Row 3: mapping + navigation (A3) ---
    dict(id="map", x=COLX[1], y=296, w=COLW, h=78, fill=SOFT, stroke=SOFT_S, font=11,
         label="Mapping + localization [A3]\nkeyframes, DISK/LightGlue/MixVPR,\nloop closure, iSAM2, TSDF  (BURSTY)\nboth | soft | on-board"),
    dict(id="nav", x=COLX[2], y=296, w=COLW, h=78, fill=BEST, stroke=BEST_S, font=11,
         label="Navigation / path planning [A3]\nsearch occupancy grid, replan\nmostly CPU | soft | on-board"),

    # --- Row 4: voice (A5) ---
    dict(id="mic", x=COLX[0], y=388, w=COLW, h=70, fill=SENSE, stroke=SENSE_S, font=11,
         label="Microphone array [A5]\npackets: 48 frames/pkt @ 16 kHz\nCPU | on-board"),
    dict(id="voice", x=COLX[1], y=388, w=COLW, h=70, fill=SOFT, stroke=SOFT_S, font=11,
         label="Voice: VAD + wake-word [A5]\nalways on-board, gate heavier models\nmostly CPU (per-msg overhead) | soft"),
    dict(id="asr", x=COLX[2], y=388, w=COLW, h=70, fill=BEST, stroke=BEST_S, font=11,
         label="ASR / TTS / speech-to-speech [A5]\nWhisper-class; often CLOUD (stubbed)\nCPU/GPU or cloud | best-effort"),

    # --- Row 5: cognition / LLM (A6) ---
    dict(id="cog", x=COLX[2], y=472, w=COLW, h=66, fill=BEST, stroke=BEST_S, font=11,
         label="Cognition / on-demand LLM [A6]\nreasoning, called occasionally\noften CLOUD (stubbed) | best-effort"),

    # --- Row 6: VLA (A6) ---
    dict(id="vla", x=COLX[2], y=552, w=COLW, h=78, fill=BEST, stroke=BEST_S, font=11,
         label="VLA (vision-language-action) [A6]\nbackbone + action head -> action chunk\nlatency caps re-plan rate (e.g. 53 ms -> ~19 Hz)\nGPU (bandwidth-bound) | best-effort | on-board"),

    # --- Row 7: whole-body control (A4) ---
    dict(id="wbc", x=COLX[3], y=552, w=COLW, h=78, fill=HARD, stroke=HARD_S, font=11, bold=False,
         label="Whole-body control [A4]\nMLP policy, fixed loop 50 Hz / 20 ms deadline\nmotor bus 100-1000 Hz\nCPU (isolated cores) | HARD real-time | on-board"),

    # platform layer note (A7)
    dict(id="act_lbl", x=905, y=530, w=120, h=18, rounded=False, align="center", valign="middle",
         font=9, bold=True, fill=NOTE, stroke=NOTE, fontcolor="#b85450",
         label="action chunk ->"),
    dict(id="plat", x=COLX[0], y=644, w=900, h=52, rounded=True, fill="#f0f0f0", stroke="#999999",
         font=11, align="left", valign="middle",
         label="Platform layer [A7]: ROS 2 pub/sub + QoS, router (zenoh), containers, CPU quotas (cgroup cpu.max), core pinning (cpusets/isolcpus). Near-zero CPU, decides correctness: who gets which core, which messages arrive, whether the control loop is protected."),
]

# the core-partition FLOOR (drawn as a full-width base, 3 pools)
FLOOR_Y = 712
BOXES += [
    dict(id="floor_lbl", x=20, y=FLOOR_Y-24, w=360, h=20, rounded=False, align="left",
         valign="middle", bold=True, font=11, fill=NOTE, stroke=NOTE,
         label="THE FLOOR: one small on-board computer, cores partitioned ->"),
    dict(id="pool_shared", x=40, y=FLOOR_Y, w=400, h=58, fill=FLOOR, stroke=FLOOR_S, font=11,
         label="Shared pool cores\nperception, mapping, nav, voice,\nVLA, cognition compete here"),
    dict(id="pool_svc", x=460, y=FLOOR_Y, w=360, h=58, fill=FLOOR, stroke=FLOOR_S, font=11,
         label="Service cores\nmiddleware router, telemetry,\ncamera service threads"),
    dict(id="pool_iso", x=840, y=FLOOR_Y, w=380, h=58, fill="#d5e8d4", stroke=FLOOR_S, font=11, bold=True,
         label="Isolated control cores\nreserved (isolcpus): ONLY the\nhard control loop, IRQs moved off"),
]

# legend + sources
BOXES += [
    dict(id="legend", x=40, y=476, w=560, h=160, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\nFill = timing class:   red = hard real-time (miss = fault)   amber = soft real-time (miss degrades quality)   blue = best-effort (no deadline)\n   purple = sense / raw I/O     green = core-partition floor\nEach box tags: resource (CPU / GPU / both), rate class, and on-board vs cloud.\nArrows = message flow on pub/sub topics; services never call each other directly.\nLayers below are PROVIDERS; layers above CONSUME them (interference flows up, not down)."),
    dict(id="src", x=40, y=792, w=1180, h=70, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Sources: stack structure + timing classes A0; depth/VIO/NVENC A1; perception chain A2; mapping/nav A3; control loop + isolation A4; voice + framing A5; VLA + re-plan A6; platform/QoS/quotas/pinning A7.  "
               "All rates ILLUSTRATIVE from constants.json: camera 30 Hz [camera_frame_rate_illustrative]; perception 10 Hz [perception_output_rate_illustrative]; control 50 Hz / 20 ms [wbc_control_rate_illustrative, wbc_deadline_illustrative]; "
               "motor bus 100-1000 Hz [motor_bus_rate_illustrative]; audio 48 frames/pkt @ 16 kHz [audio_packet_framing_illustrative, audio_sample_rate_illustrative].  VLA 53 ms -> ~19 Hz is the SIBLING worked example [vla_latency_example_sibling]. No measured robot numbers."),
]

EDGES = [
    dict(src="cam", dst="depth", color="#9673a6", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="depth", dst="pp", color="#d79b00", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="depth", dst="map", color="#d79b00", sx=0.2, sy=1, dx=0.2, dy=0),
    dict(src="map", dst="nav", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="mic", dst="voice", color="#9673a6", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="voice", dst="asr", color="#d79b00", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="pp", dst="vla", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.2),
    dict(src="nav", dst="vla", color="#6c8ebf", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="vla", dst="wbc", color="#b85450", bold=True, sx=1, sy=0.5, dx=0, dy=0.5),
]
