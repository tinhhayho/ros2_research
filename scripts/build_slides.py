#!/usr/bin/env python3
"""Assemble a Marp deck from a template by inlining slides/assets/<key>.svg
for each {{diagram:<key>}} placeholder. Inlining keeps the built HTML fully
self-contained (no external image files needed to open the deck).

Default: slides/deck.md -> slides/slides.md (the original teaching deck).
Pass --deck/--out for other decks, e.g. the research deck:
    build_slides.py --deck research-deck.md --out research.md
Pass --dir for decks living outside slides/, e.g. the AUTOSAR deck:
    build_slides.py --dir autosar/slides --deck autosar-deck.md --out autosar.md
Assets resolve from <dir>/assets/ first, then slides/assets/ (the shared pool).
"""
import re, base64, pathlib, sys, argparse

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--dir", default="slides", help="deck directory relative to the repo root")
ap.add_argument("--deck", default="deck.md", help="template file inside --dir")
ap.add_argument("--out", default="slides.md", help="output file inside --dir")
args = ap.parse_args()
base = root / args.dir
deck = (base / args.deck).read_text()


def find_asset(key, ext):
    # deck-local assets first, then the shared slides/assets pool, so decks outside
    # slides/ can reuse shared diagrams without keeping a second copy in sync
    for d in (base / "assets", root / "slides" / "assets"):
        f = d / f"{key}.{ext}"
        if f.exists():
            return f
    sys.exit(f"missing diagram asset: {key}.{ext} (looked in {base / 'assets'} and slides/assets)")


def repl(m):
    key = m.group(1)
    f = find_asset(key, "svg")
    # Embed as an SVG data-URI in an explicit <img> tag (needs Marp --html). This renders
    # crisply, keeps the HTML self-contained, and sidesteps both markdown-it's mangling of
    # raw multi-line <svg> and its refusal to parse a long data-URI in ![](...) syntax.
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    return f'<img alt="{key}" src="data:image/svg+xml;base64,{b64}" />'


def repl_png(m):
    key = m.group(1)
    f = find_asset(key, "png")
    b64 = base64.b64encode(f.read_bytes()).decode("ascii")
    return f'<img alt="{key}" src="data:image/png;base64,{b64}" />'


out = re.sub(r"\{\{diagram:([a-z0-9-]+)\}\}", repl, deck)
out = re.sub(r"\{\{image:([a-z0-9-]+)\}\}", repl_png, out)
missing = re.findall(r"\{\{(?:diagram|image):[a-z0-9-]+\}\}", out)
if missing:
    sys.exit(f"unresolved placeholders: {missing}")
(base / args.out).write_text(out)
print(f"wrote {args.dir}/{args.out} ({len(out)} bytes, {out.count('<img alt=')} diagrams)")
