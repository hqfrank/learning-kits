# -*- coding: utf-8 -*-
# 02 — People-perception pipeline: per-frame vs per-person, GPU vs CPU, where cost grows with N
# Source: note A2 (YOLOX, SCRFD, ArcFace, OSNet, BlazePose, Light-ASD; NMS, Kalman, Hungarian, One Euro).
# Colour: green = runs on GPU (neural net); blue = runs on CPU (post-processing glue).
#         The left band is per-frame work (fixed cost); the right band is per-person work (scales with N).

PAGE = dict(name="02-people-perception-pipeline", w=1320, h=770)

GPU = "#d5e8d4"; GPU_S = "#82b366"      # GPU stage
CPU = "#dae8fc"; CPU_S = "#6c8ebf"      # CPU stage
FRAME = "#fff2cc"; FRAME_S = "#d6b656"  # per-frame band
PERSON = "#ffe6cc"; PERSON_S = "#d79b00"  # per-person band
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"
HI = "#f8cecc"; HI_S = "#b85450"        # the headline-cost callout

BOXES = [
    dict(id="title", x=20, y=12, w=1280, h=30, rounded=False, align="center", valign="middle",
         bold=True, font=15, fill=NOTE, stroke=NOTE,
         label="People perception: a short GPU network chain wrapped in CPU bookkeeping that grows with the number of people N"),

    # band headers
    dict(id="band_frame", x=40, y=66, w=560, h=26, rounded=False, bold=True, font=12,
         fill=FRAME, stroke=FRAME_S,
         label="PER-FRAME work  (fixed cost, once per camera frame)"),
    dict(id="band_person", x=640, y=66, w=640, h=26, rounded=False, bold=True, font=12,
         fill=PERSON, stroke=PERSON_S,
         label="PER-PERSON work  (runs once per detected person -> scales ~linearly with N)"),

    # --- PER-FRAME lane ---
    dict(id="decode", x=40, y=110, w=175, h=62, fill=CPU, stroke=CPU_S, font=11,
         label="Decode frame\n(CPU)"),
    dict(id="letterbox", x=235, y=110, w=175, h=62, fill=CPU, stroke=CPU_S, font=11,
         label="Rectify / letterbox\nresize to net input (CPU)"),
    dict(id="detector", x=425, y=110, w=175, h=62, fill=GPU, stroke=GPU_S, font=11,
         label="Person detection\nYOLOX (GPU)"),
    dict(id="nms", x=425, y=192, w=175, h=58, fill=CPU, stroke=CPU_S, font=11,
         label="NMS\nde-dup boxes (CPU)"),

    # --- PER-PERSON lane (the N-scaling stages) ---
    dict(id="crop", x=640, y=110, w=200, h=58, fill=CPU, stroke=CPU_S, font=11,
         label="Crop / warp per person\n(CPU) - xN"),
    dict(id="facedet", x=860, y=110, w=200, h=58, fill=GPU, stroke=GPU_S, font=11,
         label="Face detect + landmarks\nSCRFD (GPU) - xN"),
    dict(id="facerec", x=1080, y=110, w=200, h=58, fill=GPU, stroke=GPU_S, font=11,
         label="Face recognition\nArcFace embedding (GPU) - xN"),
    dict(id="reid", x=640, y=180, w=200, h=58, fill=GPU, stroke=GPU_S, font=11,
         label="Body re-ID\nOSNet embedding (GPU) - xN"),
    dict(id="pose", x=860, y=180, w=200, h=58, fill=GPU, stroke=GPU_S, font=11,
         label="2D pose\nBlazePose (GPU) - xN"),
    dict(id="asd", x=1080, y=180, w=200, h=58, fill=GPU, stroke=GPU_S, font=11,
         label="Active-speaker\nLight-ASD (GPU) - xN"),

    # --- CPU post-processing band (the dominant cost) ---
    dict(id="track", x=640, y=300, w=200, h=72, fill=CPU, stroke=CPU_S, font=11,
         label="Tracking-by-detection\nKalman predict + Hungarian match\n(CPU) - per track per frame"),
    dict(id="smooth", x=860, y=300, w=200, h=72, fill=CPU, stroke=CPU_S, font=11,
         label="Smoothing\nOne Euro filter\n(CPU) - per tracked quantity"),
    dict(id="proj", x=1080, y=300, w=200, h=72, fill=CPU, stroke=CPU_S, font=11,
         label="3D projection\nsample depth map at pixels\n(CPU) - per person"),

    # output
    dict(id="out", x=1080, y=392, w=200, h=58, fill=PERSON, stroke=PERSON_S, font=11, bold=True,
         label="Publish tracks\n(illustrative ~10 Hz,\noften rate-capped)"),

    # headline-cost callout
    dict(id="headline", x=40, y=300, w=560, h=120, rounded=True, fill=HI, stroke=HI_S,
         font=12, align="left", valign="middle",
         label="HEADLINE LESSON (A2):\nThe neural networks run on the GPU and are individually small.\nBut NMS + Kalman + Hungarian + One Euro + depth-sampling + coordinate\ntransforms all run on the CPU, usually in a scripting language, once per\nperson per frame. On a small robot computer this CPU post-processing\nFREQUENTLY EXCEEDS the GPU inference time. A GPU-busy-only benchmark\nconcludes 'plenty of headroom' while the CPU cores are already full."),

    # where cost grows with N
    dict(id="ncost", x=40, y=472, w=1240, h=76, rounded=True, fill="#e1d5e7", stroke="#9673a6",
         font=11, align="left", valign="middle",
         label="WHERE COST GROWS WITH N (people in view):  per-frame stages (decode, letterbox, YOLOX, NMS) stay FLAT.  "
               "Per-person stages (crop/warp, SCRFD, ArcFace, OSNet, BlazePose, Light-ASD, Kalman+Hungarian, One Euro, 3D projection) grow ~LINEARLY with N.  "
               "Measure at N = 1, 2, 5, 10: report the fixed per-frame cost AND the per-person slope separately, not one average.  "
               "Note: occlusion means fewer than N may actually be detected, so N = people in view, not people detected."),
]

# legend + sources
BOXES += [
    dict(id="legend", x=40, y=566, w=600, h=92, rounded=False, align="left", valign="top",
         font=11, fill=NOTE, stroke=NOTE_S,
         label="Legend\ngreen = runs on the GPU (a neural network)\nblue = runs on the CPU (post-processing 'glue')\n'xN' = stage runs once per detected person (scales with N)\npurple band = the N-scaling rule itself"),
    dict(id="src", x=40, y=674, w=1240, h=70, rounded=False, align="left", valign="top",
         font=9, fill=SRC, stroke=SRC_S,
         label="Source: note A2. Models: YOLOX (arXiv:2107.08430), SCRFD (arXiv:2105.04714), ArcFace (arXiv:1801.07698), OSNet (arXiv:1905.00953), BlazePose (arXiv:2006.10204), Light-ASD (CVPR 2023). "
               "CPU post-processing: NMS; Kalman filter + Hungarian algorithm (tracking-by-detection); One Euro filter (Casiez et al., CHI 2012); 3D projection by sampling the depth map from A1.  "
               "Output rate ~10 Hz is ILLUSTRATIVE [perception_output_rate_illustrative]; camera 30 Hz [camera_frame_rate_illustrative]. A software rate cap is a ceiling, not a compute signal (B2). No measured robot numbers."),
]

EDGES = [
    dict(src="decode", dst="letterbox", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="letterbox", dst="detector", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="detector", dst="nms", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="nms", dst="crop", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="crop", dst="facedet", color="#6c8ebf", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="facedet", dst="facerec", color="#82b366", sx=1, sy=0.5, dx=0, dy=0.5),
    dict(src="crop", dst="reid", color="#6c8ebf", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="reid", dst="track", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="pose", dst="smooth", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="asd", dst="proj", color="#82b366", sx=0.5, sy=1, dx=0.5, dy=0),
    dict(src="proj", dst="out", color="#6c8ebf", sx=0.5, sy=1, dx=0.5, dy=0),
]
