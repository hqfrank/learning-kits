#!/usr/bin/env python3
"""Strip draw.io's trailing '<switch>...Text is not SVG...</switch>' banner from an
exported SVG, then rasterise to PNG with cairosvg. The banner is a fallback link
draw.io always appends; it is not diagram content."""
import re, sys, os
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")
import cairosvg

svg_path = sys.argv[1]
png_path = sys.argv[2] if len(sys.argv) > 2 else svg_path[:-4] + ".png"
s = open(svg_path).read()
# Remove the trailing <switch>...</switch> that carries the fallback banner.
s2 = re.sub(r'<switch>(?:(?!</switch>).)*Text is not SVG(?:(?!</switch>).)*</switch>',
            '', s, flags=re.DOTALL)
if s2 != s:
    open(svg_path, "w").write(s2)
    print("stripped banner from", os.path.basename(svg_path))
else:
    print("no banner found in", os.path.basename(svg_path))
cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2.0)
print("png written", os.path.basename(png_path))
assert "Text is not SVG" not in open(svg_path).read(), "banner still present!"
