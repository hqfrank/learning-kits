"""Shared theme + measured constants for the single-lane-bridge video.

All numbers are loaded from ../../explorers/params.json (not retyped). The key
used for each value is recorded in SRC below so a reader can trace it. Colours
are consistent across scenes.
"""
import json
import os
from manim import ManimColor

BG = ManimColor("#0B0F14")       # near-black background
CONTROL = ManimColor("#2DD4BF")  # teal  — control / WBC
MEMORY = ManimColor("#F59E0B")   # amber — perception / memory
VLA = ManimColor("#E879A9")      # magenta — VLA / compute aggressor
GHOST = ManimColor("#9CA3AF")    # grey  — datasheet / unreached ceiling
DANGER = ManimColor("#EF4444")   # red   — deadline / floor / danger
INK = ManimColor("#E5E7EB")      # near-white text

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARAMS = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "explorers", "params.json"))

with open(_PARAMS) as _f:
    P = json.load(_f)

# Pull the exact values this video shows, each tied to its params.json key.
# (value, params-key path) — kept as plain floats for drawing.
WBC_DEADLINE = P["wbc_deadline"]["value"]                         # 10 ms
WBC_SOLO_P99_THOR = P["wbc_solo_p99"]["thor"]["value"]            # 0.0416 ms
WBC_WORST_MIX = P["wbc_worst_mix_p99"]["thor"]["value"]           # 5.9 ms
LOCKOUT_THOR = P["lockout_onset_occupancy"]["thor"]["value"]      # 14 %
LOCKOUT_ORIN = P["lockout_onset_occupancy"]["orin"]["value"]      # 8 %
NVFP4_MEAS = P["nvfp4_dense_ceiling"]["thor"]["value"]            # 627.8 TFLOP/s
TCGEN05_FP16 = P["tensor_tcgen05_fp16"]["thor"]["value"]          # 192.5 TFLOP/s
SHARED_CTX_P99 = P["shared_context_wbc_p99"]["value"]            # 110.7 ms
SHARED_CTX_X = P["shared_context_wbc_penalty"]["value"]          # 64 x
SEP_CTX_P99 = P["separate_context_wbc_p99"]["pi05"]["value"]     # 17 ms
PLAIN_MPS_P99 = P["plain_mps_wbc_p99"]["value"]                 # 61 ms
MPS_CAP25_P99 = P["mps_cap_wbc_p99"]["pi05_cap25"]["value"]     # 7.5 ms
VLA_RETAINED_25 = P["mps_cap_vla_rate_retained"]["pi05_cap25"]["value"]  # 0.72
FLOOR = P["cpu_memory_load_floor"]["value"]                     # 172 GB/s
DRAM_SUSTAINED_THOR = P["dram_bandwidth_sustained_M"]["thor"]["value"]   # 245 GB/s

# Datasheet figures the video names explicitly. 1035 and 517 are carried in the
# source strings of the measured keys (A.4 / A.3); labelled datasheet on screen.
NVFP4_DATASHEET = 1035   # params nvfp4_dense_ceiling.thor source: "60.7% of 1035"
INT8FP8_DATASHEET = 517  # A.3 note / diagrams INDEX: INT8=FP8 datasheet dense


def styled_axes_bg(scene):
    scene.camera.background_color = BG


def src_tag(text):
    """A small grey corner source tag used on every scene that shows a number."""
    from manim import Text
    return Text(text, font_size=14, color=GHOST)
