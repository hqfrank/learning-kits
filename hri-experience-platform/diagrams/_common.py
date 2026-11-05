# -*- coding: utf-8 -*-
"""Shared palette and the constants.json loader for the hri-experience-platform diagrams.

Numbers are NEVER typed into a spec: they are read from ../constants.json with V(key), and every
use registers a footnote tag via a per-page Tags() object:
    T = Tags();  "%s ms %s" % (V("cleanup_ack_timeout_ms_illustrative"), T("cleanup_ack_timeout_ms_illustrative"))
Tag format: [Pn] = class public, [In] = class illustrative (a design parameter, never a measurement).
Derived values are tagged [calc] ("my arithmetic") and the formula is written in the sources block.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(HERE, "..", "constants.json")))

# palette (fill, stroke)
KERNEL = ("#ffe6cc", "#d79b00")     # the coordinator kernel: authority, admission, cleanup
EXPER = ("#d5e8d4", "#82b366")      # an experience: reducer, local story, chapters
REASON = ("#e1d5e7", "#9673a6")     # the reasoner (speech-to-speech LLM session)
WORLD = ("#dae8fc", "#6c8ebf")      # catalogs, adapters, producers, targets, the world
BAD = ("#f8cecc", "#b85450")        # rejected / forbidden / recovery
NOTE = ("#f5f5f5", "#999999")
SRC = ("#fff2cc", "#d6b656")
WHITE = ("#ffffff", "#999999")


def V(key, *sub):
    v = C[key]["value"]
    for s in sub:
        v = v[s]
    return v


def num(x):
    if isinstance(x, float):
        return repr(x) if not x.is_integer() else str(int(x))
    if isinstance(x, int):
        return "{:,}".format(x).replace(",", " ") if x >= 10000 else str(x)
    return str(x)


def _fmt(v):
    if isinstance(v, (int, float)):
        return num(v)
    if isinstance(v, list):
        return "[" + ", ".join(num(x) for x in v) + "]"
    return str(v)


class Tags:
    def __init__(self):
        self.order = []

    def __call__(self, key):
        if key not in C or not isinstance(C[key], dict):
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
    head = ("Sources. Mechanisms: this kit's notes/ (named per line below) and glossary.md. "
            "Every number is loaded from ../constants.json by the key shown: [Pn] = public (cited); "
            "[In] = illustrative (a round design parameter that keeps the design's relations; never a "
            "measurement of any system); [calc] = my arithmetic on tagged values.")
    lines = [head] + list(extra) + T.lines()
    cpl = int(w / (font * 0.5))
    n = sum(max(1, math.ceil(len(l) / cpl)) for l in lines)
    h = int(n * (font * 1.22) + 14)
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


def title(label, w, h=34):
    return dict(id="title", x=20, y=12, w=w - 40, h=h, rounded=False, align="center",
                valign="middle", bold=True, font=17, fill="none", stroke="none", label=label)
