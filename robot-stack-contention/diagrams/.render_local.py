#!/usr/bin/env python3
"""Local draw.io renderer for the robot-stack-contention kit (rung 2).

Each page is one cell list in a sibling specNN.py module, rendered two ways from
the SAME list:

  1. an editable .drawio (draw.io-compatible, html=1 labels), and
  2. a standalone .svg (rect/ellipse per box + <foreignObject> XHTML label with the
     default XHTML namespace ON THE DIV, polylines for edges and chart lines),
     rasterised to .png by headless Chrome at 2x (--no-sandbox required).

Spec module:
    PAGE  = dict(name, w, h)
    BOXES = [dict(id, x, y, w, h, label, fill, stroke, font=11, bold=False,
                  align='center', valign='middle', dash=None, rounded=True,
                  shape='rect'|'ellipse', sw=1.5, fontcolor='#000')]
    EDGES = [dict(src, dst, sx, sy, dx, dy, pts=[(x,y)...], color, dash, sw, label)]
    LINES = [dict(pts=[(x,y),...], color, sw=1.5, dash=None, arrow='none'|'end')]
Label markup: '\n' = line break, '**text**' = bold. A literal '<' is escaped.
"""
import html as _html
import importlib.util
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.dirname(os.path.abspath(__file__))


def label_html(s):
    t = _html.escape(s, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    return t.replace("\n", "<br/>")


def _attr(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("\n", "&#10;"))


def _dash_style(d):
    if not d:
        return ""
    return "dashed=1;dashPattern=%s;" % d.replace(",", " ")


# ---------------- drawio ----------------
def write_drawio(path, page, boxes, edges, lines):
    o = ['<mxfile host="app.diagrams.net"><diagram id="p_%s" name="%s">'
         % (page["name"].replace("-", "_"), page["name"]),
         '<mxGraphModel dx="800" dy="600" grid="0" gridSize="10" guides="1" tooltips="1" '
         'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" '
         'pageHeight="%d" math="0" shadow="0"><root>' % (page["w"], page["h"]),
         '<mxCell id="0" /><mxCell id="1" parent="0" />']
    for b in boxes:
        if b.get("shape") == "ellipse":
            st = "ellipse;whiteSpace=wrap;html=1;"
        elif b.get("rounded", True):
            st = "rounded=1;arcSize=6;whiteSpace=wrap;html=1;"
        else:
            st = "rounded=0;whiteSpace=wrap;html=1;"
        st += "verticalAlign=%s;align=%s;fontSize=%d;spacing=6;" % (
            b.get("valign", "middle"), b.get("align", "center"), b.get("font", 11))
        if b.get("bold"):
            st += "fontStyle=1;"
        st += _dash_style(b.get("dash"))
        st += "fillColor=%s;strokeColor=%s;strokeWidth=%s;" % (
            b.get("fill", "none"), b.get("stroke", "none"), b.get("sw", 1.5))
        st += "fontColor=%s;" % b.get("fontcolor", "#000000")
        o.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                 '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry" /></mxCell>'
                 % (b["id"], _attr(label_html(b.get("label", ""))), st,
                    b["x"], b["y"], b["w"], b["h"]))
    for i, e in enumerate(edges):
        st = "endArrow=classic;html=1;fontSize=%d;" % e.get("font", 10)
        st += _dash_style(e.get("dash"))
        if e.get("sx") is not None:
            st += "exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % (e["sx"], e["sy"])
        if e.get("dx") is not None:
            st += "entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % (e["dx"], e["dy"])
        st += "strokeColor=%s;strokeWidth=%s;" % (e.get("color", "#666666"), e.get("sw", 1.5))
        pts = "".join('<mxPoint x="%s" y="%s" />' % p for p in e.get("pts", []))
        o.append('<mxCell id="e%d" value="%s" style="%s" edge="1" parent="1" source="%s" '
                 'target="%s"><mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>'
                 % (i, _attr(e.get("label", "")), st, e["src"], e["dst"],
                    ('<Array as="points">%s</Array>' % pts) if pts else ""))
    for i, l in enumerate(lines):
        p = l["pts"]
        st = "endArrow=%s;startArrow=none;html=1;" % (
            "classic" if l.get("arrow") == "end" else "none")
        st += _dash_style(l.get("dash"))
        st += "strokeColor=%s;strokeWidth=%s;" % (l.get("color", "#666666"), l.get("sw", 1.5))
        mid = "".join('<mxPoint x="%.1f" y="%.1f" />' % q for q in p[1:-1])
        o.append('<mxCell id="l%d" value="" style="%s" edge="1" parent="1">'
                 '<mxGeometry relative="1" as="geometry">'
                 '<mxPoint x="%.1f" y="%.1f" as="sourcePoint" />'
                 '<mxPoint x="%.1f" y="%.1f" as="targetPoint" />%s</mxGeometry></mxCell>'
                 % (i, st, p[0][0], p[0][1], p[-1][0], p[-1][1],
                    ('<Array as="points">%s</Array>' % mid) if mid else ""))
    o.append('</root></mxGraphModel></diagram></mxfile>')
    open(path, "w").write("".join(o))


# ---------------- SVG ----------------
def _anchor(b, fx, fy):
    return (b["x"] + fx * b["w"], b["y"] + fy * b["h"])


def write_svg(path, page, boxes, edges, lines):
    W, H = page["w"], page["h"]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
         % (W, H, W, H), '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)]
    cols = sorted({e.get("color", "#666666") for e in edges} |
                  {l.get("color", "#666666") for l in lines if l.get("arrow") == "end"})
    s.append("<defs>")
    for c in cols:
        s.append('<marker id="a%s" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 z" '
                 'fill="%s"/></marker>' % (c.lstrip("#"), c))
    s.append("</defs>")

    def poly(pts, color, sw, dash, arrow):
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        m = ' marker-end="url(#a%s)"' % color.lstrip("#") if arrow else ""
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s%s/>'
                 % (" ".join("%.1f,%.1f" % p for p in pts), color, sw, d, m))

    bid = {b["id"]: b for b in boxes}
    for l in [l for l in lines if not l.get("top")]:  # chart lines under boxes
        poly(l["pts"], l.get("color", "#666666"), l.get("sw", 1.5), l.get("dash"),
             l.get("arrow") == "end")
    def draw_edge(e):
        a, b = bid[e["src"]], bid[e["dst"]]
        sp = _anchor(a, e.get("sx", 0.5), e.get("sy", 1)) if e.get("sx") is not None else \
            (a["x"] + a["w"] / 2, a["y"] + a["h"])
        dp = _anchor(b, e.get("dx", 0.5), e.get("dy", 0)) if e.get("dx") is not None else \
            (b["x"] + b["w"] / 2, b["y"])
        poly([sp] + list(e.get("pts", [])) + [dp], e.get("color", "#666666"),
             e.get("sw", 1.5), e.get("dash"), True)
    for e in edges:
        if not e.get("top"):
            draw_edge(e)
    for b in boxes:
        fill, stroke = b.get("fill", "none"), b.get("stroke", "none")
        d = ' stroke-dasharray="%s"' % b["dash"] if b.get("dash") else ""
        sw = b.get("sw", 1.5)
        if b.get("shape") == "ellipse":
            s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                     'stroke-width="%s"%s/>' % (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2,
                                                b["w"] / 2, b["h"] / 2, fill, stroke, sw, d))
        else:
            rx = 6 if b.get("rounded", True) else 0
            s.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%d" fill="%s" stroke="%s" '
                     'stroke-width="%s"%s/>' % (b["x"], b["y"], b["w"], b["h"], rx, fill,
                                                stroke, sw, d))
        lab = b.get("label", "")
        if not lab:
            continue
        va = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}[b.get("valign", "middle")]
        pad = b.get("pad", 6)
        s.append('<foreignObject x="%s" y="%s" width="%s" height="%s">'
                 '<div xmlns="http://www.w3.org/1999/xhtml" style="box-sizing:border-box;'
                 'width:%spx;height:%spx;display:flex;align-items:%s;'
                 'font-family:Helvetica,Arial,sans-serif;font-size:%dpx;font-weight:%s;'
                 'color:%s;padding:%dpx;line-height:1.2;text-align:%s;overflow:hidden;">'
                 '<div style="width:100%%;">%s</div></div></foreignObject>'
                 % (b["x"], b["y"], b["w"], b["h"], b["w"], b["h"], va, b.get("font", 11),
                    "bold" if b.get("bold") else "normal", b.get("fontcolor", "#000000"),
                    pad, b.get("align", "center"), label_html(lab)))
    for e in edges:
        if e.get("top"):
            draw_edge(e)
    for l in lines:
        if l.get("top"):
            poly(l["pts"], l.get("color", "#666666"), l.get("sw", 1.5), l.get("dash"),
                 l.get("arrow") == "end")
    s.append("</svg>")
    svg = "".join(s)
    ET.fromstring(svg)  # validate
    open(path, "w").write(svg)


def raster(svg, png, w, h):
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--user-data-dir=/tmp/chrome_render_rsc_%d" % os.getpid(),
                    "--force-device-scale-factor=2", "--window-size=%d,%d" % (w, h),
                    "--screenshot=" + png, "file://" + svg], check=True, capture_output=True)


def build(mod):
    p = mod.PAGE
    base = os.path.join(OUT, p["name"])
    lines = getattr(mod, "LINES", [])
    write_drawio(base + ".drawio", p, mod.BOXES, mod.EDGES, lines)
    write_svg(base + ".svg", p, mod.BOXES, mod.EDGES, lines)
    raster(base + ".svg", base + ".png", p["w"], p["h"])
    print("built", p["name"])


if __name__ == "__main__":
    sys.path.insert(0, OUT)
    for sp in sys.argv[1:]:
        sp = os.path.abspath(sp)
        spec = importlib.util.spec_from_file_location(os.path.basename(sp)[:-3], sp)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        build(m)
