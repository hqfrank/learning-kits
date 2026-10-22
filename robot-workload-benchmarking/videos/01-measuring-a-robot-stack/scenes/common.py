"""Shared palette and helpers for the robot-workload-benchmarking video."""
from manim import *

BG = "#0d1117"
TEAL = "#2dd4bf"    # camera / sense
SKY = "#38bdf8"     # people perception
RED = "#f87171"     # control loop (hard real-time)
VIOLET = "#a78bfa"  # voice
AMBER = "#fbbf24"   # mapping
GREEN = "#4ade80"   # GPU
BLUE = "#60a5fa"    # CPU
ORANGE = "#fb923c"  # bench / harness
ROSE = "#fb7185"    # caveat / lie
FG = "#e6edf3"
MUTED = "#8b949e"

config.background_color = BG


def source_tag(text):
    t = Text(text, font_size=16, color=MUTED)
    t.to_corner(DR, buff=0.25)
    return t


def scene_title(text, color=FG):
    t = Text(text, font_size=38, color=color, weight=BOLD)
    t.to_edge(UP, buff=0.5)
    return t


def hold(scene, clip, started=None):
    """Hold to clip length + 0.6s regardless of prior animation time."""
    scene.wait(max(0.5, clip + 0.6 - scene.renderer.time))
