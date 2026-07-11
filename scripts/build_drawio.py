#!/usr/bin/env python3
"""Assemble slides/diagrams.drawio — one page per figure.

Diagram pages are NATIVE draw.io shapes (editable boxes/edges/text), sourced from the
per-diagram <mxGraphModel> fragments in slides/assets/drawio-pages/*.xml. The captured
images (official NVIDIA figures, real screenshots) have no vector source, so they are
appended as image pages.
"""
import base64, pathlib, struct
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parent.parent
assets = root / "slides" / "assets"
pages_dir = assets / "drawio-pages"
out = root / "slides" / "diagrams.drawio"

capture_pngs = [
    "thor-official-block.png",
    "drive-devkit-photo.png",
    "groot-run-screenshot.png",
    "rqt-graph-real.png",
]


def png_size(data: bytes):
    w, h = struct.unpack(">II", data[16:24])
    return w, h


pages, native = [], sorted(pages_dir.glob("*.xml"))
for i, f in enumerate(native):
    ET.parse(f)  # fail loudly on malformed XML
    model = f.read_text().strip()
    pages.append(f'  <diagram id="page{i}" name="{f.stem}">\n{model}\n  </diagram>\n')

for j, name in enumerate(capture_pngs):
    f = assets / name
    data = f.read_bytes()
    w, h = png_size(data)
    b64 = base64.b64encode(data).decode("ascii")
    style = (
        "shape=image;verticalLabelPosition=bottom;verticalAlign=top;"
        f"aspect=fixed;imageAspect=0;image=data:image/png,{b64};"
    )
    pages.append(
        f'  <diagram id="capture{j}" name="{name.rsplit(".", 1)[0]}">\n'
        f'    <mxGraphModel dx="1000" dy="700" grid="0" page="1" pageScale="1" '
        f'pageWidth="{w}" pageHeight="{h}" math="0" shadow="0">\n'
        f'      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n'
        f'        <mxCell id="cimg{j}" value="{name.rsplit(".", 1)[0]}" style="{style}" '
        f'vertex="1" parent="1">\n'
        f'          <mxGeometry x="0" y="0" width="{w}" height="{h}" as="geometry" />\n'
        f"        </mxCell>\n      </root>\n    </mxGraphModel>\n  </diagram>\n"
    )

out.write_text(
    '<mxfile host="app.diagrams.net" agent="build_drawio.py" version="24.0.0">\n'
    + "".join(pages)
    + "</mxfile>\n"
)
print(
    f"wrote {out.relative_to(root)} ({out.stat().st_size} bytes, "
    f"{len(native)} native + {len(capture_pngs)} image pages)"
)
