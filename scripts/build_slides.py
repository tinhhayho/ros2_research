#!/usr/bin/env python3
"""Assemble a Marp deck from a template by inlining slides/assets/<key>.svg
for each {{diagram:<key>}} placeholder. Inlining keeps the built HTML fully
self-contained (no external image files needed to open the deck).

Default: slides/deck.md -> slides/slides.md (the original teaching deck).
Pass --deck/--out for other decks, e.g. the research deck:
    build_slides.py --deck research-deck.md --out research.md
"""
import re, base64, pathlib, sys, argparse

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--deck", default="deck.md", help="template file inside slides/")
ap.add_argument("--out", default="slides.md", help="output file inside slides/")
args = ap.parse_args()
deck = (root / "slides" / args.deck).read_text()


def repl(m):
    key = m.group(1)
    f = root / "slides" / "assets" / f"{key}.svg"
    if not f.exists():
        sys.exit(f"missing diagram asset: {f}")
    # Embed as an SVG data-URI in an explicit <img> tag (needs Marp --html). This renders
    # crisply, keeps the HTML self-contained, and sidesteps both markdown-it's mangling of
    # raw multi-line <svg> and its refusal to parse a long data-URI in ![](...) syntax.
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    return f'<img alt="{key}" src="data:image/svg+xml;base64,{b64}" />'


def repl_png(m):
    key = m.group(1)
    f = root / "slides" / "assets" / f"{key}.png"
    if not f.exists():
        sys.exit(f"missing image asset: {f}")
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    return f'<img alt="{key}" src="data:image/png;base64,{b64}" />'


out = re.sub(r"\{\{diagram:([a-z0-9-]+)\}\}", repl, deck)
out = re.sub(r"\{\{image:([a-z0-9-]+)\}\}", repl_png, out)
missing = re.findall(r"\{\{(?:diagram|image):[a-z0-9-]+\}\}", out)
if missing:
    sys.exit(f"unresolved placeholders: {missing}")
(root / "slides" / args.out).write_text(out)
print(f"wrote slides/{args.out} ({len(out)} bytes, {out.count('<img alt=')} diagrams)")
