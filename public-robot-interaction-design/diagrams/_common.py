# -*- coding: utf-8 -*-
"""Shared palette and the constants.json loader for the public-robot-interaction-design diagrams.

Numbers are NEVER typed into a spec: they are read from ../constants.json with V(key[, sub]),
and every use registers a footnote tag via a per-page Tags() object:
    T = Tags();  "%s s %s" % (num(V("beat_greet_illustrative")), T("beat_greet_illustrative"))
Tag format: [Pn] = class public (a paper, standard or physics value, or arithmetic on one);
[In] = class illustrative (a round design value of the right order; never a measurement).
Derived values are tagged [calc] ("my arithmetic") and the formula is written in the footer.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "..", "constants.json")))

# palette (fill, stroke)
VISIT = ("#dae8fc", "#6c8ebf")    # visit / experience states, deterministic code
LLM = ("#e1d5e7", "#9673a6")      # the one language model, prompt-owned behaviour
BODY = ("#d5e8d4", "#82b366")     # body / motion / gaze output, success paths
GATE = ("#ffe6cc", "#d79b00")     # gates, timers, budgets
BAD = ("#f8cecc", "#b85450")      # failure, safety, refusals
NOTE = ("#f5f5f5", "#999999")
SRC = ("#fff2cc", "#d6b656")
WHITE = ("#ffffff", "#999999")
GREY = ("#eeeeee", "#666666")

BLUE_C = "#3d6aa3"
PURPLE_C = "#7b4f9e"
GREEN_C = "#2d7d2d"
AMBER_C = "#b37400"
RED_C = "#b85450"
GREY_C = "#666666"


def V(key, *sub):
    v = C[key]["value"]
    for s in sub:
        v = v[s]
    return v


def num(x):
    if isinstance(x, float):
        return repr(x) if not x.is_integer() else str(int(x))
    return str(x)


def rng(v, sep="-"):
    """A two-element range [a, b] printed as 'a-b'."""
    return "%s%s%s" % (num(v[0]), sep, num(v[1]))


def _fmt(v):
    if isinstance(v, (int, float)):
        return num(v)
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join("%s: %s" % (k, _fmt(x)) for k, x in v.items()) + "}"
    return str(v)


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
            src = e["source"]
            cls = "" if src.lower().startswith(e["class"]) else e["class"] + ": "
            out.append("[%s%d] %s = %s %s. %s%s" % (
                "P" if e["class"] == "public" else "I", i, k, _fmt(e["value"]), e["unit"],
                cls, src))
        return out


def footer_box(T, extra, x, y, w, font=10):
    """Sources footnote block on the canvas, height sized from the wrapped line count."""
    head = ("Sources. Every number is loaded from ../constants.json by the key shown. "
            "[Pn] = public (a paper, standard or physics value, or my arithmetic on one); "
            "[In] = illustrative (a round design value of the right order; never a measurement "
            "of a real robot or visitor); [calc] = my arithmetic on tagged values.")
    lines = [head] + list(extra) + T.lines()
    cpl = int(w / (font * 0.52))
    n = sum(max(1, math.ceil(len(l) / cpl)) for l in lines)
    h = int(n * (font * 1.17) + 16)
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


def frame(id, x, y, w, h, label, pal, **kw):
    """Container frame: no fill (edges are drawn under boxes), title at the top-left."""
    d = dict(id=id, x=x, y=y, w=w, h=h, label=label, fill="none", stroke=pal[1], dashed=True,
             sw=2, align="left", valign="top", bold=True, font=12, fontcolor=pal[1])
    d.update(kw)
    return d


def anchor(id, x, y):
    """Invisible 2x2 point used as an edge endpoint."""
    return dict(id=id, x=x - 1, y=y - 1, w=2, h=2, label="", fill="none", stroke="none",
                rounded=False)


def title(label, w, h=34):
    return dict(id="title", x=20, y=12, w=w - 40, h=h, rounded=False, align="center",
                valign="middle", bold=True, font=17, fill="none", stroke="none", label=label)
