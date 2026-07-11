#!/usr/bin/env python3
"""Bundle every diagram and captured image from slides/assets/ into one multi-page
draw.io file (slides/diagrams.drawio) — one page per figure, page named after the file.

Figures are embedded as image shapes (data URIs), so they render pixel-identical in
draw.io / Confluence and can be copied, resized, and annotated. Note: embedded SVGs are
single image shapes, not decomposed into editable draw.io shapes.
"""
import base64, pathlib, struct, xml.sax.saxutils as sx

root = pathlib.Path(__file__).resolve().parent.parent
assets = root / "slides" / "assets"
out = root / "slides" / "diagrams.drawio"

# SVG sources are the ground truth; PNGs listed here are real captures with no SVG source.
svgs = sorted(p.name for p in assets.glob("*.svg"))
capture_pngs = [
    "thor-official-block.png",
    "drive-devkit-photo.png",
    "groot-run-screenshot.png",
    "rqt-graph-real.png",
]


def png_size(data: bytes):
    w, h = struct.unpack(">II", data[16:24])
    return w, h


pages = []
for i, name in enumerate(svgs + capture_pngs):
    f = assets / name
    data = f.read_bytes()
    if name.endswith(".svg"):
        mime, (w, h) = "image/svg+xml", (960, 600)
    else:
        mime, (w, h) = "image/png", png_size(data)
    b64 = base64.b64encode(data).decode("ascii")
    style = (
        "shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
        f"aspect=fixed;imageAspect=0;image=data:{mime},{b64};"
    )
    title = sx.quoteattr(name.rsplit(".", 1)[0])
    pages.append(
        f'  <diagram id="page{i}" name={title}>\n'
        f'    <mxGraphModel dx="1000" dy="700" grid="0" gridSize="10" guides="1" tooltips="1" '
        f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" '
        f'pageHeight="{h}" math="0" shadow="0">\n'
        f"      <root>\n"
        f'        <mxCell id="0" />\n'
        f'        <mxCell id="1" parent="0" />\n'
        f'        <mxCell id="img{i}" value={title} style={sx.quoteattr(style)} vertex="1" parent="1">\n'
        f'          <mxGeometry x="0" y="0" width="{w}" height="{h}" as="geometry" />\n'
        f"        </mxCell>\n"
        f"      </root>\n"
        f"    </mxGraphModel>\n"
        f"  </diagram>\n"
    )

out.write_text(
    '<mxfile host="app.diagrams.net" agent="build_drawio.py" version="24.0.0">\n'
    + "".join(pages)
    + "</mxfile>\n"
)
print(f"wrote {out.relative_to(root)} ({out.stat().st_size} bytes, {len(pages)} pages)")
