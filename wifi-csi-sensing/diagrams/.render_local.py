#!/usr/bin/env python3
"""Local draw.io renderer for the wifi-csi-sensing kit (rung 2).

Adapted from learning/robot-workload-benchmarking/diagrams/.render_local.py. Each page
is described once as a list of cells in a sibling specNN.py module and rendered two
ways from the SAME list:

  1. an editable .drawio file (draw.io-compatible), and
  2. a standalone .svg (rect/ellipse per box + <foreignObject> XHTML label, line
     edges), rasterised to .png via headless Chrome at 2x.

Additions over the original: shape='ellipse' boxes, edges with arrow='none',
free LINES given by coordinates, and per-edge stroke width. Every SVG is validated
with ElementTree before rasterising. Labels are plain text; '<' is escaped.

Spec module:
    PAGE  = dict(name, w, h)
    BOXES = [dict(id, x, y, w, h, label, fill, stroke, font=11, bold=False,
                  align='center', valign='middle', dashed=False, rounded=True,
                  shape='rect'|'ellipse', fontcolor='#000000', sw=1.5)]
    EDGES = [dict(src, dst, label='', color, dashed, bold, arrow='classic'|'none',
                  sx, sy, dx, dy)]
    LINES = [dict(x1, y1, x2, y2, color, dashed, width, arrow='none'|'classic')]
Run: python3 .render_local.py specNN.py [...]
"""
import html as _html
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def _esc_attr(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("\n", "&#10;"))


def write_drawio(path, page, boxes, edges, lines):
    out = ['<mxfile host="app.diagrams.net"><diagram id="p_%s" name="%s">' % (
        page["name"].replace("-", "_"), page["name"])]
    out.append('<mxGraphModel dx="800" dy="600" grid="0" gridSize="10" guides="1" '
               'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
               'pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root>' % (page["w"], page["h"]))
    out.append('<mxCell id="0" /><mxCell id="1" parent="0" />')
    for i, l in enumerate([l for l in lines if l.get("under")]):
        style = "endArrow=%s;html=0;strokeColor=%s;strokeWidth=%s;" % (
            l.get("arrow", "none"), l.get("color", "#666666"), l.get("width", 1.5))
        if l.get("dashed"):
            style += "dashed=1;"
        out.append('<mxCell id="uline%d" value="" style="%s" edge="1" parent="1">'
                   '<mxGeometry relative="1" as="geometry">'
                   '<mxPoint x="%s" y="%s" as="sourcePoint" />'
                   '<mxPoint x="%s" y="%s" as="targetPoint" />'
                   '</mxGeometry></mxCell>' % (i, style, l["x1"], l["y1"], l["x2"], l["y2"]))
    for b in boxes:
        if b.get("shape") == "ellipse":
            style = "ellipse;whiteSpace=wrap;html=0;"
        elif b.get("rounded", True):
            style = "rounded=1;whiteSpace=wrap;html=0;"
        else:
            style = "text;html=0;whiteSpace=wrap;verticalAlign=%s;" % b.get("valign", "top")
        if b.get("shape") == "ellipse" or b.get("rounded", True):
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
        out.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                   % (b["id"], _esc_attr(b["label"]), style))
        out.append('<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" />'
                   % (b["x"], b["y"], b["w"], b["h"]))
        out.append('</mxCell>')
    # free lines after boxes so they sit on top, as in the SVG
    for i, l in enumerate([l for l in lines if not l.get("under")]):
        style = "endArrow=%s;html=0;strokeColor=%s;strokeWidth=%s;" % (
            l.get("arrow", "none"), l.get("color", "#666666"), l.get("width", 1.5))
        if l.get("dashed"):
            style += "dashed=1;"
        out.append('<mxCell id="line%d" value="" style="%s" edge="1" parent="1">'
                   '<mxGeometry relative="1" as="geometry">'
                   '<mxPoint x="%s" y="%s" as="sourcePoint" />'
                   '<mxPoint x="%s" y="%s" as="targetPoint" />'
                   '</mxGeometry></mxCell>' % (i, style, l["x1"], l["y1"], l["x2"], l["y2"]))
    for i, e in enumerate(edges):
        style = "endArrow=%s;html=0;fontSize=%d;" % (e.get("arrow", "classic"), e.get("font", 10))
        if e.get("bold"):
            style += "fontStyle=1;strokeWidth=2;"
        if e.get("dashed"):
            style += "dashed=1;"
        if e.get("sx") is not None:
            style += "exitX=%s;exitY=%s;" % (e["sx"], e["sy"])
        if e.get("dx") is not None:
            style += "entryX=%s;entryY=%s;" % (e["dx"], e["dy"])
        style += "strokeColor=%s;fontColor=%s;" % (e.get("color", "#666666"), e.get("color", "#666666"))
        out.append('<mxCell id="edge%d" value="%s" style="%s" edge="1" parent="1" '
                   'source="%s" target="%s"><mxGeometry relative="1" as="geometry" />'
                   '</mxCell>' % (i, _esc_attr(e.get("label", "")), style, e["src"], e["dst"]))
    out.append('</root></mxGraphModel></diagram></mxfile>')
    open(path, "w").write("".join(out))


def _anchor(box, fx, fy):
    return (box["x"] + fx * box["w"], box["y"] + fy * box["h"])


def _edge_points(src, dst, e):
    sp = _anchor(src, float(e["sx"]), float(e["sy"])) if e.get("sx") is not None \
        else (src["x"] + src["w"] / 2, src["y"] + src["h"])
    dp = _anchor(dst, float(e["dx"]), float(e["dy"])) if e.get("dx") is not None \
        else (dst["x"] + dst["w"] / 2, dst["y"])
    return sp, dp


def _line(s, x1, y1, x2, y2, c, sw, dashed, arrow):
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    mk = ' marker-end="url(#arrow_%s)"' % c.lstrip("#") if arrow != "none" else ""
    s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s%s/>'
             % (x1, y1, x2, y2, c, sw, dash, mk))


def write_svg(path, page, boxes, edges, lines):
    W, H = page["w"], page["h"]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
         % (W, H, W, H), '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H)]
    colours = sorted({e.get("color", "#666666") for e in edges} |
                     {l.get("color", "#666666") for l in lines})
    s.append('<defs>')
    for c in colours:
        s.append('<marker id="arrow_%s" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3 L0,6 z" fill="%s"/>'
                 '</marker>' % (c.lstrip("#"), c))
    s.append('</defs>')
    for l in lines:  # under=True lines go beneath boxes (labels with a fill can mask them)
        if l.get("under"):
            _line(s, l["x1"], l["y1"], l["x2"], l["y2"], l.get("color", "#666666"),
                  l.get("width", 1.5), l.get("dashed"), l.get("arrow", "none"))
    bid = {b["id"]: b for b in boxes}
    labels = []
    for e in edges:
        (x1, y1), (x2, y2) = _edge_points(bid[e["src"]], bid[e["dst"]], e)
        c = e.get("color", "#666666")
        _line(s, x1, y1, x2, y2, c, 2 if e.get("bold") else 1.5, e.get("dashed"),
              e.get("arrow", "classic"))
        if e.get("label"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            lw = e.get("lw", 160)
            labels.append('<foreignObject x="%.1f" y="%.1f" width="%d" height="36">'
                          '<div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Helvetica,'
                          'Arial,sans-serif;font-size:%dpx;font-weight:%s;color:%s;text-align:center;'
                          'background:rgba(255,255,255,0.88);line-height:1.1;">%s</div></foreignObject>'
                          % (mx - lw / 2 + e.get("lox", 0), my - 18 + e.get("loy", 0), lw,
                             e.get("font", 10), "bold" if e.get("bold") else "normal", c,
                             _html.escape(e["label"]).replace("\n", "<br/>")))
    for b in boxes:
        dash = ' stroke-dasharray="6,4"' if b.get("dashed") else ""
        sw = b.get("sw", 1.5 if b.get("rounded", True) else 1)
        if b.get("shape") == "ellipse":
            s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
                     'stroke-width="%s"%s/>' % (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2,
                                               b["w"] / 2, b["h"] / 2, b["fill"], b["stroke"], sw, dash))
        else:
            rx = ' rx="8"' if b.get("rounded", True) else ""
            s.append('<rect x="%d" y="%d" width="%d" height="%d"%s fill="%s" stroke="%s" '
                     'stroke-width="%s"%s/>' % (b["x"], b["y"], b["w"], b["h"], rx, b["fill"],
                                               b["stroke"], sw, dash))
        if not b["label"]:
            continue
        valign = {"top": "flex-start", "middle": "center", "bottom": "flex-end"}[b.get("valign", "middle")]
        talign = b.get("align", "center")
        label_html = _html.escape(b["label"]).replace("\n", "<br/>")
        s.append('<foreignObject x="%d" y="%d" width="%d" height="%d">'
                 '<div xmlns="http://www.w3.org/1999/xhtml" style="box-sizing:border-box;width:%dpx;'
                 'height:%dpx;display:flex;align-items:%s;font-family:Helvetica,Arial,sans-serif;'
                 'font-size:%dpx;font-weight:%s;color:%s;padding:6px;line-height:1.2;text-align:%s;'
                 'overflow:hidden;"><div style="width:100%%;">%s</div></div></foreignObject>'
                 % (b["x"], b["y"], b["w"], b["h"], b["w"], b["h"], valign, b.get("font", 11),
                    "bold" if b.get("bold") else "normal", b.get("fontcolor", "#000000"),
                    talign, label_html))
    for l in [l for l in lines if not l.get("under")]:  # default: ON TOP of boxes
        _line(s, l["x1"], l["y1"], l["x2"], l["y2"], l.get("color", "#666666"),
              l.get("width", 1.5), l.get("dashed"), l.get("arrow", "none"))
    s += labels  # edge labels on top of everything
    s.append('</svg>')
    svg = "".join(s)
    ET.fromstring(svg)
    open(path, "w").write(svg)


def raster_png(svg_path, png_path):
    root = ET.fromstring(open(svg_path).read())
    w, h = int(float(root.get("width"))), int(float(root.get("height")))
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--user-data-dir=/tmp/chrome_render_wifi",
                    "--force-device-scale-factor=2", "--window-size=%d,%d" % (w, h),
                    "--screenshot=" + png_path, "file://" + os.path.abspath(svg_path)],
                   check=True, capture_output=True)


def build(mod, outdir):
    name = mod.PAGE["name"]
    lines = getattr(mod, "LINES", [])
    base = os.path.join(outdir, name)
    write_drawio(base + ".drawio", mod.PAGE, mod.BOXES, mod.EDGES, lines)
    write_svg(base + ".svg", mod.PAGE, mod.BOXES, mod.EDGES, lines)
    raster_png(base + ".svg", base + ".png")
    print("built", name)


if __name__ == "__main__":
    import importlib.util
    outdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, outdir)
    for spec_path in sys.argv[1:]:
        spec_path = os.path.abspath(spec_path)
        mod_name = os.path.splitext(os.path.basename(spec_path))[0]
        sp = importlib.util.spec_from_file_location(mod_name, spec_path)
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        build(mod, outdir)
