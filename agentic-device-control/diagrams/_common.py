# -*- coding: utf-8 -*-
"""Shared palette and the constants.json loader for the agentic-device-control diagrams.

Numbers are NEVER typed into a spec: they are read from ../constants.json with V(key),
and every use registers a footnote tag via a per-page Tags() object:
    T = Tags();  label = "watchdog %s min %s" % (V("watchdog_timeout_illustrative"), T("watchdog_timeout_illustrative"))
Tag format: [Pn] = class public, [In] = class illustrative. Derived values are tagged [calc]
("my arithmetic") and the formula is written next to them.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "..", "constants.json")))

# palette (fill, stroke)
CLOUD = ("#e1d5e7", "#9673a6")    # cloud side / model calls go to the cloud
GUARD = ("#ffe6cc", "#d79b00")    # guards, limits, checks in device code
DEVICE = ("#dae8fc", "#6c8ebf")   # device-side code
MODEL = ("#d5e8d4", "#82b366")    # a model call (an agent node)
STOP = ("#f8cecc", "#b85450")     # failure / refusal / terminal status
NOTE = ("#f5f5f5", "#999999")
SRC = ("#fff2cc", "#d6b656")
WHITE = ("#ffffff", "#999999")


def V(key):
    return C[key]["value"]


def num(x):
    """Format a number with a thin-space-free thousands separator (ASCII space)."""
    if isinstance(x, float) and not x.is_integer():
        return ("%g" % x)
    x = int(x)
    return "{:,}".format(x).replace(",", " ")


class Tags:
    def __init__(self):
        self.order = []

    def __call__(self, key):
        if key not in C:
            raise KeyError("not in constants.json: " + key)
        if key not in self.order:
            self.order.append(key)
        cls = C[key]["class"]
        assert cls in ("public", "illustrative"), key
        return "[%s%d]" % ("P" if cls == "public" else "I", self.order.index(key) + 1)

    def lines(self):
        out = []
        for i, k in enumerate(self.order, 1):
            e = C[k]
            v = e["value"]
            vs = json.dumps(v, ensure_ascii=False).replace('"', "") if not isinstance(v, (int, float)) else num(v)
            src = e["source"]
            cls = "" if src.lower().startswith(e["class"]) else e["class"] + ": "
            out.append(("[%s%d] %s = %s %s" % ("P" if e["class"] == "public" else "I", i, k, vs,
                                               e["unit"])).rstrip() + ". " + cls + src)
        return out


def footer_box(T, extra, x, y, w, font=10, chars_per_line=None):
    """Sources footnote block on the canvas. Height is sized from the wrapped line count."""
    head = ("Sources. Numbers are loaded from ../constants.json by key (shown). "
            "P = public (cited doc/paper, value as published); I = illustrative (round value "
            "chosen to explain the idea, never a measurement); [calc] = my arithmetic on tagged values.")
    lines = [head] + list(extra) + T.lines()
    cpl = chars_per_line or int(w / (font * 0.47))
    n = sum(max(1, math.ceil(len(l) / cpl)) for l in lines)
    h = int(n * (font * 1.2) + 12)
    return dict(id="sources", x=x, y=y, w=w, h=h, rounded=False, align="left", valign="top",
                font=font, fill=SRC[0], stroke=SRC[1], label="\n".join(lines)), y + h


def box(id, x, y, w, h, label, pal, **kw):
    d = dict(id=id, x=x, y=y, w=w, h=h, label=label, fill=pal[0], stroke=pal[1])
    d.update(kw)
    return d


def text(id, x, y, w, h, label, **kw):
    d = dict(id=id, x=x, y=y, w=w, h=h, label=label, fill="none", stroke="none",
             rounded=False, align="left", valign="top")
    d.update(kw)
    return d


def title(label, w):
    return dict(id="title", x=20, y=12, w=w - 40, h=34, rounded=False, align="center",
                valign="middle", bold=True, font=17, fill="none", stroke="none", label=label)
