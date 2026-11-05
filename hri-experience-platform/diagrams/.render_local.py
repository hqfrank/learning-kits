#!/usr/bin/env python3
"""Local draw.io renderer for the hri-experience-platform kit (rung 2).

Adapted from ../../agentic-device-control/diagrams/.render_local.py (edge waypoints), with
free LINES added: LINES = [dict(x1, y1, x2, y2, color, dashed=False, sw=1.5)] drawn ON TOP of
boxes (reference lines, axes, range bars). Each page is described once as a list of cells in a
sibling specNN.py module and rendered two ways from the SAME list:

  1. a .drawio file (editable, draw.io-compatible), and
  2. a standalone .svg (rect per box + <foreignObject> XHTML label, polyline edges),
     rasterised to .png via headless Chrome at 2x.

Spec module:
    PAGE  = dict(name, w, h)
    BOXES = [dict(id, x, y, w, h, label, fill, stroke, font=11, bold=False,
                  align='center', valign='middle', dashed=False, rounded=True,
                  rx=8, fontcolor='#000000', sw=1.5)]
    EDGES = [dict(src, dst, label='', color='#666666', dashed=False, bold=False,
                  sx, sy, dx, dy,          # exit/entry fractions on the box
                  points=[(x, y), ...],    # waypoints (absolute px)
                  lpos=(x, y), lw=160)]    # optional label centre / width
Usage: python3 .render_local.py spec01.py [spec02.py ...]
       python3 .render_local.py --combine   (writes hri-experience-platform.drawio)
"""
import glob
import html as _html
import importlib.util
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _esc_attr(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("\n", "&#10;"))


def write_drawio(path, page, boxes, edges, lines=()):
    o = ['<mxfile host="app.diagrams.net"><diagram id="p_%s" name="%s">'
         % (page["name"].replace("-", "_"), page["name"]),
         '<mxGraphModel dx="800" dy="600" grid="0" gridSize="10" guides="1" tooltips="1" '
         'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" '
         'pageHeight="%d" math="0" shadow="0"><root>' % (page["w"], page["h"]),
         '<mxCell id="0" /><mxCell id="1" parent="0" />']
    for b in boxes:
        if b.get("rounded", True):
            style = "rounded=1;whiteSpace=wrap;html=0;arcSize=%d;" % min(50, b.get("rx", 8) * 2)
        else:
            style = "text;html=0;whiteSpace=wrap;verticalAlign=%s;" % b.get("valign", "top")
        if b.get("rounded", True):
            style += "verticalAlign=%s;" % b.get("valign", "middle")
        style += "align=%s;fontSize=%d;" % (b.get("align", "center"), b.get("font", 11))
        if b.get("bold"):
            style += "fontStyle=1;"
        if b.get("dashed"):
            style += "dashed=1;"
        style += "fillColor=%s;strokeColor=%s;strokeWidth=%s;" % (
            b["fill"], b["stroke"], b.get("sw", 1.5))
        if b.get("fontcolor"):
            style += "fontColor=%s;" % b["fontcolor"]
        o.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                 '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" /></mxCell>'
                 % (b["id"], _esc_attr(b["label"]), style, b["x"], b["y"], b["w"], b["h"]))
    for i, e in enumerate(edges):
        style = "endArrow=classic;html=0;fontSize=%d;edgeStyle=none;" % e.get("font", 10)
        if e.get("bold"):
            style += "fontStyle=1;strokeWidth=2;"
        if e.get("dashed"):
            style += "dashed=1;"
        if e.get("sx") is not None:
            style += "exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % (e["sx"], e["sy"])
        if e.get("dx") is not None:
            style += "entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % (e["dx"], e["dy"])
        style += "strokeColor=%s;fontColor=%s;" % (e.get("color", "#666666"), e.get("color", "#666666"))
        pts = ""
        if e.get("points"):
            pts = '<Array as="points">%s</Array>' % "".join(
                '<mxPoint x="%d" y="%d" />' % p for p in e["points"])
        o.append('<mxCell id="edge%d" value="%s" style="%s" edge="1" parent="1" source="%s" '
                 'target="%s"><mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>'
                 % (i, _esc_attr(e.get("label", "")), style, e["src"], e["dst"], pts))
    for i, l in enumerate(lines):
        style = "endArrow=none;html=0;strokeColor=%s;strokeWidth=%s;" % (l.get("color", "#666666"), l.get("sw", 1.5))
        if l.get("dashed"):
            style += "dashed=1;"
        o.append('<mxCell id="line%d" value="" style="%s" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                 '<mxPoint x="%s" y="%s" as="sourcePoint" /><mxPoint x="%s" y="%s" as="targetPoint" />'
                 '</mxGeometry></mxCell>' % (i, style, l["x1"], l["y1"], l["x2"], l["y2"]))
    o.append('</root></mxGraphModel></diagram></mxfile>')
    open(path, "w").write("".join(o))


def _anchor(b, fx, fy):
    return (b["x"] + fx * b["w"], b["y"] + fy * b["h"])


def _edge_poly(src, dst, e):
    sp = _anchor(src, float(e["sx"]), float(e["sy"])) if e.get("sx") is not None \
        else (src["x"] + src["w"] / 2, src["y"] + src["h"])
    dp = _anchor(dst, float(e["dx"]), float(e["dy"])) if e.get("dx") is not None \
        else (dst["x"] + dst["w"] / 2, dst["y"])
    return [sp] + [tuple(p) for p in e.get("points", [])] + [dp]


def write_svg(path, page, boxes, edges, lines=()):
    W, H = page["w"], page["h"]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
         % (W, H, W, H),
         '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H), '<defs>']
    for c in sorted({e.get("color", "#666666") for e in edges}):
        s.append('<marker id="arrow_%s" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 z" fill="%s"/>'
                 '</marker>' % (c.lstrip("#"), c))
    s.append('</defs>')
    bid = {b["id"]: b for b in boxes}

    def label_fo(cx, cy, w, text, font, colour, bold, h=None):
        h = h or (font + 6) * (text.count("\n") + 1) + 4
        return ('<foreignObject x="%.1f" y="%.1f" width="%d" height="%d">'
                '<div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Helvetica,Arial,'
                'sans-serif;font-size:%dpx;font-weight:%s;color:%s;text-align:center;'
                'line-height:1.15;"><span style="background:rgba(255,255,255,0.92);">%s</span>'
                '</div></foreignObject>'
                % (cx - w / 2, cy - h / 2, w, h, font, "bold" if bold else "normal", colour,
                   _html.escape(text).replace("\n", "<br/>")))

    edge_labels = []
    for e in edges:
        pts = _edge_poly(bid[e["src"]], bid[e["dst"]], e)
        c = e.get("color", "#666666")
        dash = ' stroke-dasharray="6,4"' if e.get("dashed") else ""
        s.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%s"%s '
                 'marker-end="url(#arrow_%s)"/>'
                 % (" ".join("%.1f,%.1f" % p for p in pts), c, 2.2 if e.get("bold") else 1.5,
                    dash, c.lstrip("#")))
        if e.get("label"):
            if e.get("lpos"):
                cx, cy = e["lpos"]
            else:  # midpoint of the longest segment
                segs = list(zip(pts, pts[1:]))
                a, b = max(segs, key=lambda ab: abs(ab[0][0] - ab[1][0]) + abs(ab[0][1] - ab[1][1]))
                cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            edge_labels.append(label_fo(cx, cy, e.get("lw", 160), e["label"], e.get("font", 10),
                                        c, e.get("bold")))
    for b in boxes:
        dash = ' stroke-dasharray="6,4"' if b.get("dashed") else ""
        rx = b.get("rx", 8) if b.get("rounded", True) else 0
        s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" '
                 'stroke-width="%s"%s/>' % (b["x"], b["y"], b["w"], b["h"], rx, b["fill"],
                                             b["stroke"], b.get("sw", 1.5), dash))
        if not b["label"]:
            continue
        valign = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}[
            b.get("valign", "middle")]
        s.append('<foreignObject x="%d" y="%d" width="%d" height="%d">'
                 '<div xmlns="http://www.w3.org/1999/xhtml" style="box-sizing:border-box;'
                 'width:%dpx;height:%dpx;display:flex;align-items:%s;'
                 'font-family:Helvetica,Arial,sans-serif;font-size:%dpx;font-weight:%s;'
                 'color:%s;padding:%dpx;line-height:1.2;text-align:%s;overflow:hidden;">'
                 '<div style="width:100%%;">%s</div></div></foreignObject>'
                 % (b["x"], b["y"], b["w"], b["h"], b["w"], b["h"], valign, b.get("font", 11),
                    "bold" if b.get("bold") else "normal", b.get("fontcolor", "#000000"),
                    b.get("pad", 6), b.get("align", "center"),
                    _html.escape(b["label"]).replace("\n", "<br/>")))
    for l in lines:  # free lines on top of boxes
        s.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s/>'
                 % (l["x1"], l["y1"], l["x2"], l["y2"], l.get("color", "#666666"), l.get("sw", 1.5),
                    ' stroke-dasharray="6,4"' if l.get("dashed") else ""))
    s.extend(edge_labels)  # labels on top of everything
    s.append('</svg>')
    svg = "".join(s)
    ET.fromstring(svg)  # validate
    open(path, "w").write(svg)


def raster_png(svg_path, png_path):
    root = ET.fromstring(open(svg_path).read())
    w, h = int(float(root.get("width"))), int(float(root.get("height")))
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--user-data-dir=/tmp/chrome_render_hep_%d" % os.getpid(),
                    "--force-device-scale-factor=2", "--window-size=%d,%d" % (w, h),
                    "--screenshot=" + png_path, "file://" + os.path.abspath(svg_path)],
                   check=True, capture_output=True)


def build(mod):
    n = mod.PAGE["name"]
    p = lambda ext: os.path.join(HERE, n + ext)
    lines = getattr(mod, "LINES", [])
    write_drawio(p(".drawio"), mod.PAGE, mod.BOXES, mod.EDGES, lines)
    write_svg(p(".svg"), mod.PAGE, mod.BOXES, mod.EDGES, lines)
    raster_png(p(".svg"), p(".png"))
    print("built", n)


def combine():
    blocks = []
    for f in sorted(glob.glob(os.path.join(HERE, "[0-9][0-9]-*.drawio"))):
        blocks += re.findall(r"<diagram .*?</diagram>", open(f).read(), flags=re.S)
    out = os.path.join(HERE, "hri-experience-platform.drawio")
    open(out, "w").write('<mxfile host="app.diagrams.net">%s</mxfile>' % "".join(blocks))
    ET.parse(out)
    print("combined", len(blocks), "pages ->", os.path.basename(out))


if __name__ == "__main__":
    if sys.argv[1:] == ["--combine"]:
        combine()
        sys.exit(0)
    for sp_path in sys.argv[1:]:
        sp_path = os.path.abspath(sp_path)
        spec = importlib.util.spec_from_file_location(
            os.path.splitext(os.path.basename(sp_path))[0], sp_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        build(mod)
