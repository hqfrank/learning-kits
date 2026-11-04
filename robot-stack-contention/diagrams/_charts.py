# Chart helpers for the chart pages. Pure geometry: no numbers here, all data comes via V().
from _common import *


class Axes:
    """Maps data to pixels inside a plot rectangle; linear or log10 per axis."""

    def __init__(self, x, y, w, h, xr, yr, xlog=False, ylog=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog

    def _n(self, v, r, lg):
        if lg:
            return (log10(v) - log10(r[0])) / (log10(r[1]) - log10(r[0]))
        return (v - r[0]) / float(r[1] - r[0])

    def X(self, v):
        return self.x + self._n(v, self.xr, self.xlog) * self.w

    def Y(self, v):
        return self.y + self.h - self._n(v, self.yr, self.ylog) * self.h

    def frame(self, pid, xticks, yticks, xlabel, ylabel, font=10, grid=True, zero=None):
        B, L = [], []
        L.append(dict(pts=[(self.x, self.y + self.h), (self.x + self.w, self.y + self.h)], color=INK, sw=1.2))
        L.append(dict(pts=[(self.x, self.y), (self.x, self.y + self.h)], color=INK, sw=1.2))
        for i, t in enumerate(xticks):
            tv, tl = (t if isinstance(t, tuple) else (t, f(t)))
            px = self.X(tv)
            if grid:
                L.append(dict(pts=[(px, self.y), (px, self.y + self.h)], color="#e6e6e6", sw=1))
            L.append(dict(pts=[(px, self.y + self.h), (px, self.y + self.h + 5)], color=INK, sw=1.2))
            B.append(text("%sxt%d" % (pid, i), px - 30, self.y + self.h + 6, 60, 15, tl, font=font, align="center"))
        for i, t in enumerate(yticks):
            tv, tl = (t if isinstance(t, tuple) else (t, f(t)))
            py = self.Y(tv)
            if grid:
                L.append(dict(pts=[(self.x, py), (self.x + self.w, py)], color="#e6e6e6", sw=1))
            L.append(dict(pts=[(self.x - 5, py), (self.x, py)], color=INK, sw=1.2))
            B.append(text("%syt%d" % (pid, i), self.x - 50, py - 8, 44, 16, tl, font=font, align="right"))
        if zero is not None:
            L.append(dict(pts=[(self.x, self.Y(zero)), (self.x + self.w, self.Y(zero))], color=INK, sw=1.2))
        B.append(text("%sxl" % pid, self.x, self.y + self.h + 22, self.w, 18, xlabel, font=font + 0.5,
                      align="center"))
        B.append(text("%syl" % pid, self.x - 50, self.y - 24, self.w + 50, 18, ylabel, font=font + 0.5))
        return B, L


def dot(id, cx, cy, r, fill, stroke, dash=None, sw=1.8, square=False):
    return dict(id=id, x=round(cx - r, 1), y=round(cy - r, 1), w=2 * r, h=2 * r, label="", fill=fill,
                stroke=stroke, dash=dash, sw=sw, rounded=False, shape=None if square else "ellipse")


def bar(id, x, y, w, h, fill, stroke, label="", dash=None, font=10, sw=1.5, fontcolor="#000000"):
    # normalise negative heights/widths
    if w < 0:
        x, w = x + w, -w
    if h < 0:
        y, h = y + h, -h
    return dict(id=id, x=round(x, 1), y=round(y, 1), w=round(w, 1), h=round(h, 1), label=label, fill=fill,
                stroke=stroke, dash=dash, rounded=False, font=font, sw=sw, fontcolor=fontcolor, pad=1)


def hline(x0, x1, y, color=INK, sw=1.5, dash=None, top=False):
    return dict(pts=[(x0, y), (x1, y)], color=color, sw=sw, dash=dash, top=top)


def vline(x, y0, y1, color=INK, sw=1.5, dash=None, top=False):
    return dict(pts=[(x, y0), (x, y1)], color=color, sw=sw, dash=dash, top=top)


def whisker_h(x0, x1, y, color=INK, sw=2, cap=5):
    return [hline(x0, x1, y, color, sw, top=True), vline(x0, y - cap, y + cap, color, sw, top=True),
            vline(x1, y - cap, y + cap, color, sw, top=True)]


def whisker_v(x, y0, y1, color=INK, sw=2, cap=5):
    return [vline(x, y0, y1, color, sw, top=True), hline(x - cap, x + cap, y0, color, sw, top=True),
            hline(x - cap, x + cap, y1, color, sw, top=True)]
