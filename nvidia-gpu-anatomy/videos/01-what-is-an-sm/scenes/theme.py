"""Shared colours and helpers for the SM explainer video.

Accent legend (held across scenes):
  SOFTWARE (you write) = blue;  HARDWARE (runs it) = green;
  SCHEDULER / issue bound = orange;  TENSOR core = purple;
  REGISTER / limit bite = red.  Orin = blue, Thor = green in the memory ladder.
All constants come from explorers/params.json; the key is shown as a corner source tag.
"""
from manim import *

BG = "#0d1117"
SOFTWARE = "#4F9DFF"   # blue
HARDWARE = "#49C17A"   # green
SCHED = "#F0A030"      # orange
TENSOR = "#B080F0"     # purple
LIMIT = "#E5484D"      # red
MUTE = "#6E7681"       # grey
INK = "#E6EDF3"        # near-white text

ORIN = "#4F9DFF"       # blue
THOR = "#49C17A"       # green


def source_tag(key: str):
    """A small source tag for a scene corner (params.json key or note ref)."""
    t = Text(key, font_size=16, color=MUTE)
    t.to_corner(DR, buff=0.25)
    return t


def rung(label: str, color, w=3.4, h=0.72, fs=26):
    box = RoundedRectangle(corner_radius=0.1, width=w, height=h,
                           stroke_color=color, stroke_width=3, fill_color=color,
                           fill_opacity=0.14)
    txt = Text(label, font_size=fs, color=INK)
    txt.move_to(box.get_center())
    return VGroup(box, txt)
