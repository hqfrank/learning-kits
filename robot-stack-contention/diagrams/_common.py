# Shared helpers for the robot-stack-contention diagrams (public kit).
# Every number on a canvas is loaded from ../constants.json through V(); nothing is retyped.
# Tags() hands out the on-canvas key tags: the first tag of an illustrative key on a page says
# "illustrative", so every illustrative number is called illustrative where it first appears.
import json
import math
import os
import textwrap

_HERE = os.path.dirname(os.path.abspath(__file__))
_C = json.load(open(os.path.join(_HERE, "..", "constants.json")))


def V(key, *path):
    """Value of a constants.json key, optionally indexed by path (int index or dict field)."""
    v = _C[key]["value"]
    for p in path:
        v = v[p]
    return v


def CLS(key):
    return _C[key]["class"]


def qnote(key):
    """The 'source' text stored with a constant (quoted, not retyped)."""
    return _C[key].get("source", "")


def f(x, nd=None):
    """Format a number: drop trailing zeros, keep given decimals. repr() keeps full precision."""
    if isinstance(x, bool):
        return str(x)
    if nd is not None:
        return ("%." + str(nd) + "f") % x
    if isinstance(x, int) or float(x).is_integer():
        return "%d" % x
    return repr(float(x))


def rng(a, b, unit="", nd=None, sep="–"):
    return "%s%s%s%s" % (f(a, nd), sep, f(b, nd), (" " + unit) if unit else "")


def pct(frac, nd=0, sign=True):
    """fraction -> percent string, e.g. 0.4 -> +40 %."""
    v = frac * 100
    return (("%+." if sign else "%.") + str(nd) + "f %%") % v


class Tags:
    """Per-page tag registry. T(key) -> '[key, illustrative]' the first time an illustrative key
    is tagged on this page, '[key]' afterwards; T(key, 'field') -> '[key: field]'."""

    def __init__(self):
        self.seen = []    # every key used on the page (drives the footnote)
        self.tagged = []  # keys already shown as an on-canvas [tag] (drives ", illustrative")

    def __call__(self, *keys, field=None):
        parts = []
        for k in keys:
            assert k in _C, k
            if k not in self.seen:
                self.seen.append(k)
            first = k not in self.tagged
            if first:
                self.tagged.append(k)
            s = k + ((": " + field) if field else "")
            if first and CLS(k) == "illustrative":
                s += ", illustrative"
            parts.append(s)
        return "[" + "; ".join(parts) + "]"

    def reg(self, *keys):
        """Register keys used only in derived text (my estimate from ...)."""
        for k in keys:
            assert k in _C, k
            if k not in self.seen:
                self.seen.append(k)

    def est(self, *keys):
        """'my estimate from `a` and `b`' text; registers the keys."""
        self.reg(*keys)
        ks = ["`%s`" % k for k in keys]
        return "my estimate from " + (", ".join(ks[:-1]) + " and " + ks[-1] if len(ks) > 1 else ks[0])

    def footnote(self):
        ill = [k for k in self.seen if CLS(k) == "illustrative"]
        sib = [k for k in self.seen if CLS(k) == "sibling"]
        pub = [k for k in self.seen if CLS(k) == "public"]
        out = []
        if ill:
            out.append("**Illustrative** (round teaching numbers that keep the shape of a finding; "
                       "not measurements): " + ", ".join(ill) + ".")
        if sib:
            out.append("**Sibling** (keys in a sibling public kit; paths relative to the kit folder): " +
                       "; ".join("%s = %s" % (k, qnote(k)) for k in sib) + ".")
        if pub:
            srcs = []
            for k in pub:
                srcs.append("%s = %s" % (k, qnote(k)))
            out.append("**Public**: " + "; ".join(srcs) + ".")
        return "\n".join(out)


def est_lines(s, w, font):
    """Rough wrapped line count for a label of width w px at a font size."""
    cpl = max(10, int((w - 12) / (font * 0.5)))
    n = 0
    for para in s.replace("**", "").split("\n"):
        n += max(1, len(textwrap.wrap(para, cpl)) if para else 1)
    return n


# palette (colour always doubled by dash / shape / text tag)
CPU, CPU_S = "#dae8fc", "#6c8ebf"
CPU2 = "#9fc0e8"
GPU, GPU_S = "#d5e8d4", "#5f9e4f"
BENCH, BENCH_S = "#ffe6cc", "#d79b00"
CORR, CORR_S = "#f3ecf7", "#9673a6"
GREY, GREY_S = "#eeeeee", "#888888"
NOTE, NOTE_S = "#f7f7f7", "#bbbbbb"
SRC, SRC_S = "#fff8dc", "#d6b656"
TITLE = "#222222"
ORIN = "#1f5fa8"
THOR = "#d9711c"
INK = "#333333"

log10 = math.log10


def title(text, w, h=56, font=21):
    return dict(id="title", x=20, y=12, w=w - 40, h=h, label=text, fill="none",
                stroke="none", font=font, bold=True, align="left", valign="middle",
                rounded=False)


def text(id, x, y, w, h, label, font=11, align="left", valign="top", bold=False,
         color="#000000"):
    return dict(id=id, x=x, y=y, w=w, h=h, label=label, fill="none", stroke="none",
                font=font, align=align, valign=valign, bold=bold, rounded=False,
                fontcolor=color, pad=2)


def panel(id, x, y, w, h, label, fill=NOTE, stroke=NOTE_S, font=11, align="left",
          valign="top", dash=None, bold=False):
    return dict(id=id, x=x, y=y, w=w, h=h, label=label, fill=fill, stroke=stroke,
                font=font, align=align, valign=valign, dash=dash, rounded=False, bold=bold)


def sources_panel(id, x, y, w, T, extra, font=10):
    """Sources footnote block built from the page's registered keys; height from line count."""
    lab = "**Sources.** " + extra + "\n" + T.footnote()
    h = int(est_lines(lab, w, font) * font * 1.25 + 18)
    return panel(id, x, y, w, h, lab, fill=SRC, stroke=SRC_S, font=font), h
