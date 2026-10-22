#!/usr/bin/env python3
"""Local draw.io renderer for the robot-workload-benchmarking kit (rung 2).

The drawio MCP export pipeline is unreliable in this sandbox (see agent memory:
feature-179 "MCP export fully dead -> local renderer that works"). So each page is
described once as a list of cells in a sibling spec module and rendered two ways
from the SAME list:

  1. a .drawio file (editable, draw.io-compatible), and
  2. a standalone .svg (rect per box + <foreignObject> XHTML label, polyline edges),
     rasterised to .png via headless Chrome at 2x.

Chrome renders foreignObject HTML, so html=1 wrapping, <br>, bullets and the glyphs
cairo cannot draw all work. Any literal '<' inside a label MUST be written '&lt;'
or the raw-XHTML SVG breaks; we validate every SVG with ElementTree before raster.

A spec module defines:
    PAGE = dict(name=str, w=int, h=int)
    BOXES = [dict(id, x, y, w, h, label, fill, stroke, font=11, bold=False,
                  align='center', valign='middle', dashed=False, rounded=True,
                  fontcolor='#000000')]
    EDGES = [dict(src, dst, label='', color='#666666', dashed=False, bold=False,
                  sx=None, sy=None, dx=None, dy=None)]   # sx/sy/dx/dy = exit/entry fractions
Free-floating text boxes are just BOXES with rounded=False and a note fill.
"""
import html as _html
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


# ---------- draw.io emit ----------
def _esc_attr(s):
    # draw.io stores the label in an XML attribute; escape for XML attribute context.
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("\n", "&#10;"))


def write_drawio(path, page, boxes, edges):
    out = []
    out.append('<mxfile host="app.diagrams.net"><diagram id="p_%s" name="%s">' % (
        page["name"].replace("-", "_"), page["name"]))
    out.append('<mxGraphModel dx="800" dy="600" grid="0" gridSize="10" guides="1" '
               'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
               'pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root>' % (page["w"], page["h"]))
    out.append('<mxCell id="0" /><mxCell id="1" parent="0" />')
    for b in boxes:
        rounded = b.get("rounded", True)
        if rounded:
            style = "rounded=1;whiteSpace=wrap;html=0;"
        else:
            style = ("text;html=0;whiteSpace=wrap;verticalAlign=%s;"
                     % b.get("valign", "top"))
        style += "align=%s;" % b.get("align", "center")
        style += "fontSize=%d;" % b.get("font", 11)
        if b.get("bold"):
            style += "fontStyle=1;"
        if b.get("dashed"):
            style += "dashed=1;"
        style += "fillColor=%s;strokeColor=%s;" % (b["fill"], b["stroke"])
        if b.get("fontcolor"):
            style += "fontColor=%s;" % b["fontcolor"]
        out.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
                   % (b["id"], _esc_attr(b["label"]), style))
        out.append('<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry" />'
                   % (b["x"], b["y"], b["w"], b["h"]))
        out.append('</mxCell>')
    for i, e in enumerate(edges):
        style = "endArrow=%s;html=0;fontSize=%d;" % (
            e.get("arrow", "classic"), e.get("font", 10))
        if e.get("bold"):
            style += "fontStyle=1;"
        if e.get("dashed"):
            style += "dashed=1;"
        if e.get("sx") is not None:
            style += "exitX=%s;exitY=%s;" % (e["sx"], e["sy"])
        if e.get("dx") is not None:
            style += "entryX=%s;entryY=%s;" % (e["dx"], e["dy"])
        style += "strokeColor=%s;" % e.get("color", "#666666")
        out.append('<mxCell id="edge%d" value="%s" style="%s" edge="1" parent="1" '
                   'source="%s" target="%s"><mxGeometry relative="1" as="geometry" />'
                   '</mxCell>' % (i, _esc_attr(e.get("label", "")), style,
                                  e["src"], e["dst"]))
    out.append('</root></mxGraphModel></diagram></mxfile>')
    open(path, "w").write("".join(out))


# ---------- self-rendered SVG ----------
def _anchor(box, fx, fy):
    return (box["x"] + fx * box["w"], box["y"] + fy * box["h"])


def _edge_points(src, dst, e):
    # default: connect nearest horizontal or vertical sides
    if e.get("sx") is not None:
        sp = _anchor(src, float(e["sx"]), float(e["sy"]))
    else:
        sp = (src["x"] + src["w"] / 2, src["y"] + src["h"])
    if e.get("dx") is not None:
        dp = _anchor(dst, float(e["dx"]), float(e["dy"]))
    else:
        dp = (dst["x"] + dst["w"] / 2, dst["y"])
    return sp, dp


def write_svg(path, page, boxes, edges):
    W, H = page["w"], page["h"]
    s = []
    s.append('<svg xmlns="http://www.w3.org/2000/svg" '
             'width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
    s.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (W, H))
    # arrow markers (one per distinct colour)
    colours = sorted({e.get("color", "#666666") for e in edges})
    s.append('<defs>')
    for c in colours:
        mid = "arrow_" + c.lstrip("#")
        s.append('<marker id="%s" markerWidth="10" markerHeight="10" refX="8" refY="3" '
                 'orient="auto" markerUnits="strokeWidth">'
                 '<path d="M0,0 L8,3 L0,6 z" fill="%s"/></marker>' % (mid, c))
    s.append('</defs>')
    bid = {b["id"]: b for b in boxes}
    # edges first (under boxes)
    for e in edges:
        src, dst = bid[e["src"]], bid[e["dst"]]
        (x1, y1), (x2, y2) = _edge_points(src, dst, e)
        c = e.get("color", "#666666")
        mid = "arrow_" + c.lstrip("#")
        dash = ' stroke-dasharray="6,4"' if e.get("dashed") else ""
        sw = 2 if e.get("bold") else 1.5
        s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="%s"%s marker-end="url(#%s)"/>'
                 % (x1, y1, x2, y2, c, sw, dash, mid))
        if e.get("label"):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            lbl = _html.escape(e["label"])
            fw = "bold" if e.get("bold") else "normal"
            s.append('<foreignObject x="%.1f" y="%.1f" width="%d" height="34">'
                     '<div xmlns="http://www.w3.org/1999/xhtml" '
                     'style="font-family:Helvetica,Arial,sans-serif;'
                     'font-size:%dpx;font-weight:%s;color:%s;text-align:center;'
                     'background:rgba(255,255,255,0.85);line-height:1.1;">%s</div>'
                     '</foreignObject>'
                     % (mx - 80, my - 17, 160, e.get("font", 10), fw, c, lbl))
    # boxes
    for b in boxes:
        rounded = b.get("rounded", True)
        if rounded:
            rx = 8
            s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" '
                     'fill="%s" stroke="%s" stroke-width="1.5"%s/>'
                     % (b["x"], b["y"], b["w"], b["h"], rx, b["fill"], b["stroke"],
                        ' stroke-dasharray="6,4"' if b.get("dashed") else ""))
        else:
            s.append('<rect x="%d" y="%d" width="%d" height="%d" '
                     'fill="%s" stroke="%s" stroke-width="1"%s/>'
                     % (b["x"], b["y"], b["w"], b["h"], b["fill"], b["stroke"],
                        ' stroke-dasharray="6,4"' if b.get("dashed") else ""))
        # label via foreignObject (Chrome renders it)
        valign = {"top": "flex-start", "middle": "center",
                  "bottom": "flex-end"}.get(b.get("valign", "middle"), "center")
        halign = {"left": "flex-start", "center": "center",
                  "right": "flex-end"}.get(b.get("align", "center"), "center")
        talign = b.get("align", "center")
        fw = "bold" if b.get("bold") else "normal"
        fc = b.get("fontcolor", "#000000")
        label_html = _html.escape(b["label"]).replace("\n", "<br/>")
        pad = 6
        s.append('<foreignObject x="%d" y="%d" width="%d" height="%d">'
                 '<div xmlns="http://www.w3.org/1999/xhtml" '
                 'style="box-sizing:border-box;width:%dpx;height:%dpx;'
                 'display:flex;align-items:%s;justify-content:%s;'
                 'font-family:Helvetica,Arial,sans-serif;font-size:%dpx;'
                 'font-weight:%s;color:%s;padding:%dpx;line-height:1.18;'
                 'text-align:%s;overflow:hidden;">'
                 '<div style="width:100%%;">%s</div></div></foreignObject>'
                 % (b["x"], b["y"], b["w"], b["h"], b["w"], b["h"], valign, halign,
                    b.get("font", 11), fw, fc, pad, talign, label_html))
    s.append('</svg>')
    svg = "".join(s)
    # validate
    ET.fromstring(svg)
    open(path, "w").write(svg)


def raster_png(svg_path, png_path):
    # read viewBox for window size
    root = ET.fromstring(open(svg_path).read())
    w = int(float(root.get("width")))
    h = int(float(root.get("height")))
    tmp = "/tmp/chrome_render_rwb"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--user-data-dir=" + tmp,
                    "--force-device-scale-factor=2",
                    "--window-size=%d,%d" % (w, h),
                    "--screenshot=" + png_path,
                    "file://" + os.path.abspath(svg_path)],
                   check=True, capture_output=True)


def build(spec_module, outdir):
    name = spec_module.PAGE["name"]
    drawio = os.path.join(outdir, name + ".drawio")
    svg = os.path.join(outdir, name + ".svg")
    png = os.path.join(outdir, name + ".png")
    write_drawio(drawio, spec_module.PAGE, spec_module.BOXES, spec_module.EDGES)
    write_svg(svg, spec_module.PAGE, spec_module.BOXES, spec_module.EDGES)
    raster_png(svg, png)
    print("built", name, "->", os.path.basename(drawio), os.path.basename(svg),
          os.path.basename(png))


if __name__ == "__main__":
    import importlib.util
    outdir = os.path.dirname(os.path.abspath(__file__))
    for spec_path in sys.argv[1:]:
        spec_path = os.path.abspath(spec_path)
        mod_name = os.path.splitext(os.path.basename(spec_path))[0]
        sp = importlib.util.spec_from_file_location(mod_name, spec_path)
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        build(mod, outdir)
