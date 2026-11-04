# -*- coding: utf-8 -*-
"""Shared helpers for the wifi-csi-sensing diagram specs.

Every number on a canvas is loaded from ../constants.json via V(); nothing is retyped.
Tags() hands out short on-canvas tags [1], [2], ... and builds the footnote block that
maps each tag to its constants.json key and class (public / illustrative).
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(_HERE, "..", "constants.json")))


def V(key, *sub):
    """Value of a constants.json entry, optionally indexed into dicts/lists."""
    v = C[key]["value"]
    for s in sub:
        v = v[s]
    return v


def fmt(x, nd=None):
    """Plain number formatting with thin grouping for big ints (ASCII only)."""
    if isinstance(x, float) and nd is not None:
        return ("%." + str(nd) + "f") % x
    if isinstance(x, int) and abs(x) >= 10000:
        return "{:,}".format(x).replace(",", " ")
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def pct(x):
    return "%g%%" % (x * 100)


class Tags:
    """t('key') -> '[n]'. Same key reuses the same n. t.foot() -> footnote text."""

    def __init__(self):
        self.order = []

    def __call__(self, key, note=None):
        assert key in C, key
        if key not in self.order:
            self.order.append(key)
        return "[%d]" % (self.order.index(key) + 1)

    def foot(self, extra=""):
        lines = []
        for i, k in enumerate(self.order, 1):
            e = C[k]
            cls = e["class"].upper() if e["class"] == "illustrative" else e["class"]
            lines.append("[%d] %s - %s; %s" % (i, k, cls, e["source"]))
        txt = "Numbers (all loaded from constants.json):\n" + "\n".join(lines)
        if extra:
            txt += "\n" + extra
        return txt


# palette (shared with the robot-workload-benchmarking diagrams)
NOTE = "#f5f5f5"; NOTE_S = "#999999"
SRC = "#fff2cc"; SRC_S = "#d6b656"
BLUE = "#dae8fc"; BLUE_S = "#6c8ebf"
GREEN = "#d5e8d4"; GREEN_S = "#82b366"
AMBER = "#ffe6cc"; AMBER_S = "#d79b00"
RED = "#f8cecc"; RED_S = "#b85450"
PURPLE = "#e1d5e7"; PURPLE_S = "#9673a6"
GREY = "#eeeeee"; GREY_S = "#666666"


def title(text, w, font=17):
    return dict(id="title", x=20, y=12, w=w - 40, h=34, rounded=False, align="center",
                valign="middle", bold=True, font=font, fill="#ffffff", stroke="#ffffff",
                label=text)


def legend_box(id, x, y, w, h, text, font=11):
    return dict(id=id, x=x, y=y, w=w, h=h, rounded=False, align="left", valign="top",
                font=font, fill=NOTE, stroke=NOTE_S, label=text)


def sources_box(x, y, w, h, text, font=10):
    return dict(id="src", x=x, y=y, w=w, h=h, rounded=False, align="left", valign="top",
                font=font, fill=SRC, stroke=SRC_S, label=text)
