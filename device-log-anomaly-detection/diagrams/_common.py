# Shared helpers for the device-log-anomaly-detection diagrams (rung 2).
# Every number on a canvas is LOADED from ../constants.json through Src.v(); nothing is retyped.
# Src numbers each constant on first use ([n] public, [n*] illustrative) and builds the
# on-canvas sources footnote from the same entries, so tag and footnote cannot drift apart.
import json
import math
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(_HERE, "..", "constants.json")))


def raw(key, *path):
    v = C[key]["value"]
    for p in path:
        v = v[p]
    return v


def fmt(x, nd=None):
    """Numbers as the notes write them: thin-space thousands, no trailing zeros."""
    if isinstance(x, (list, tuple)):
        return "–".join(fmt(i, nd) for i in x)
    if nd is not None:
        return ("%." + str(nd) + "f") % x
    if isinstance(x, int) or float(x).is_integer():
        n = int(x)
        return "{:,}".format(n).replace(",", " ") if abs(n) >= 10000 else str(n)
    return repr(float(x))


def _short(src):
    s = re.sub(r"https?://\S+", "", src)
    s = re.sub(r"\s+", " ", s).replace(" ,", ",").replace(" ;", ";").strip(" ,;")
    return s if len(s) <= 150 else s[:147].rstrip() + "..."


class Src:
    def __init__(self):
        self.order = []

    def tag(self, key):
        if key not in C:
            raise KeyError(key)
        if key not in self.order:
            self.order.append(key)
        n = self.order.index(key) + 1
        return "[%d%s]" % (n, "*" if C[key]["class"] == "illustrative" else "")

    def v(self, key, *path, u=None, nd=None, tag=True):
        """'value unit [n]' for a constant; u overrides the unit text ('' drops it)."""
        val = fmt(raw(key, *path), nd)
        unit = C[key]["unit"] if u is None else u
        txt = val + ((" " + unit) if unit else "")
        return txt + (" " + self.tag(key) if tag else "")

    def footnote(self, extra=""):
        lines = ["**Sources** — every number is loaded from ../constants.json. "
                 "[n] = public (real value, cited); [n*] = illustrative (an invented round number of "
                 "realistic order of magnitude; never a measurement)." + ((" " + extra) if extra else "")]
        for i, k in enumerate(self.order):
            e = C[k]
            star = "*" if e["class"] == "illustrative" else ""
            src = _short(e["source"])
            if src.startswith("illustrative"):
                src = src[len("illustrative"):].strip(" ;,")
            lines.append(("[%d%s] %s = %s %s — %s" + ("; %s" if src else "%s")) % (
                i + 1, star, k, fmt(e["value"]) if not isinstance(e["value"], dict) else
                ", ".join("%s %s" % (a, fmt(b)) for a, b in e["value"].items()),
                e["unit"], e["class"], src))
        return "\n".join(lines)

    def footnote_lines(self):
        return 1 + len(self.order)


# palette (colour is always doubled by dash / shape / a text tag)
BLUE, BLUE_S = "#dae8fc", "#6c8ebf"      # fleet-side cloud stages
GREEN, GREEN_S = "#d5e8d4", "#5f9e4f"    # normal / golden path / healthy
AMBER, AMBER_S = "#ffe6cc", "#d79b00"    # decision / threshold / caution
RED, RED_S = "#f8cecc", "#b85450"        # anomaly / false alarm / trap
PURPLE, PURPLE_S = "#e1d5e7", "#9673a6"  # device / on-device
GREY, GREY_S = "#eeeeee", "#888888"
NOTE, NOTE_S = "#f7f7f7", "#bbbbbb"
SRC, SRC_S = "#fff8dc", "#d6b656"
INK = "#333333"

log10 = math.log10


def title(text, w, h=56, font=20):
    return dict(id="title", x=20, y=10, w=w - 40, h=h, label=text, fill="none", stroke="none",
                font=font, bold=True, align="left", valign="middle", rounded=False)


def text(id, x, y, w, h, label, font=11, align="left", valign="top", bold=False, color="#000000"):
    return dict(id=id, x=x, y=y, w=w, h=h, label=label, fill="none", stroke="none", font=font,
                align=align, valign=valign, bold=bold, rounded=False, fontcolor=color, pad=2)


def box(id, x, y, w, h, label, fill, stroke, font=11, align="center", valign="middle",
        dash=None, bold=False, rounded=True, sw=1.5):
    return dict(id=id, x=x, y=y, w=w, h=h, label=label, fill=fill, stroke=stroke, font=font,
                align=align, valign=valign, dash=dash, bold=bold, rounded=rounded, sw=sw)


def panel(id, x, y, w, h, label, fill=NOTE, stroke=NOTE_S, font=11, dash=None):
    return box(id, x, y, w, h, label, fill, stroke, font=font, align="left", valign="top",
               dash=dash, rounded=False)


def sources(S, x, y, w, h, extra="", font=10):
    return panel("sources", x, y, w, h, S.footnote(extra), fill=SRC, stroke=SRC_S, font=font)


def hline(x0, x1, y, color=INK, sw=1.5, dash=None, top=False, arrow=None):
    return dict(pts=[(x0, y), (x1, y)], color=color, sw=sw, dash=dash, top=top, arrow=arrow)


def vline(x, y0, y1, color=INK, sw=1.5, dash=None, top=False, arrow=None):
    return dict(pts=[(x, y0), (x, y1)], color=color, sw=sw, dash=dash, top=top, arrow=arrow)


class Axes:
    """Maps data to pixels inside a plot rectangle (linear axes)."""

    def __init__(self, x, y, w, h, xr, yr):
        self.x, self.y, self.w, self.h, self.xr, self.yr = x, y, w, h, xr, yr

    def X(self, v):
        return self.x + (v - self.xr[0]) / float(self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / float(self.yr[1] - self.yr[0]) * self.h

    def frame(self, pid, xticks, yticks, xlabel, ylabel, font=10):
        B, L = [], []
        L.append(hline(self.x, self.x + self.w, self.y + self.h, sw=1.2))
        L.append(vline(self.x, self.y, self.y + self.h, sw=1.2))
        for i, t in enumerate(xticks):
            px = self.X(t)
            L.append(vline(px, self.y, self.y + self.h, color="#e6e6e6", sw=1))
            L.append(vline(px, self.y + self.h, self.y + self.h + 5, sw=1.2))
            B.append(text("%sxt%d" % (pid, i), px - 30, self.y + self.h + 6, 60, 15, fmt(t),
                          font=font, align="center"))
        for i, t in enumerate(yticks):
            py = self.Y(t)
            L.append(hline(self.x, self.x + self.w, py, color="#e6e6e6", sw=1))
            L.append(hline(self.x - 5, self.x, py, sw=1.2))
            B.append(text("%syt%d" % (pid, i), self.x - 50, py - 8, 44, 16, fmt(t), font=font,
                          align="right"))
        B.append(text("%sxl" % pid, self.x, self.y + self.h + 22, self.w, 18, xlabel,
                      font=font + 1, align="center"))
        B.append(text("%syl" % pid, self.x - 50, self.y - 24, self.w + 50, 18, ylabel,
                      font=font + 1))
        return B, L
