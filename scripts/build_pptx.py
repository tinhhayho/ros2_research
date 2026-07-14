#!/usr/bin/env python3
"""Generate a TEXT-ONLY .pptx from a Marp deck — stdlib only, no python-pptx.

Mirrors the deck slide-for-slide (same count and order as the built HTML) so the
result can be fleshed out by hand: every {{diagram:...}} / {{image:...}} slide
becomes a placeholder page ("paste image here") — images are intentionally NOT
embedded. Tables become aligned text rows; glosses/footnotes shrink to small gray
text; code blocks go monospace.

Default: slides/research-deck.md -> slides/research.pptx. For the teaching deck:
    build_pptx.py --deck deck.md --out slides.pptx
"""
import argparse, html, pathlib, re, zipfile

root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--deck", default="research-deck.md", help="template inside slides/")
ap.add_argument("--out", default="research.pptx", help="output inside slides/")
args = ap.parse_args()

EMU_W, EMU_H = 12192000, 6858000  # 16:9

# ---------------------------------------------------------------- deck parsing
raw = (root / "slides" / args.deck).read_text()
parts = re.split(r"\n---\n", raw)
if parts and parts[0].lstrip().startswith("---"):  # YAML front matter
    parts = parts[1:]
slides_md = [p for p in parts if p.strip()]


def strip_inline(s: str) -> str:
    s = re.sub(r"<span[^>]*>|</span>", "", s)
    s = re.sub(r"<br\s*/?>", " · ", s)
    s = re.sub(r"</?(b|i|code|em|strong)>", "", s)
    s = re.sub(r"~~(.+?)~~", r"[refuted: \1]", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)  # any leftover tags
    return html.unescape(s).strip()


def parse_slide(md: str):
    """Return (title, [(kind, text)]) — kind in body/bullet/num/quote/code/gloss/table."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"<style[^>]*>.*?</style>", "", md, flags=re.S)

    ph = re.search(r"\{\{(diagram|image):([a-z0-9-]+)\}\}", md)
    if ph:
        kind, key = ph.group(1), ph.group(2)
        return (key, [("body", f"[{kind} slide — paste {key}.png here]"),
                      ("gloss", f"source: slides/assets/{key}." + ("png" if kind == "image" else "svg"))])

    title, body = "", []
    lines, i = md.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        if s.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(("code", lines[i].rstrip())); i += 1
            i += 1; continue
        m = re.match(r"^#{1,2}\s+(.*)$", s)
        if m and not title:
            title = strip_inline(m.group(1)); i += 1; continue
        gm = re.search(r'<div class="gloss">(.*?)</div>', s)
        if gm:
            body.append(("gloss", strip_inline(gm.group(1)))); i += 1; continue
        if s.startswith("|"):
            cells = [strip_inline(c) for c in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c or "--") for c in cells):
                body.append(("table", "   |   ".join(c for c in cells)))
            i += 1; continue
        if s.startswith(">"):
            body.append(("quote", strip_inline(s.lstrip("> ")))); i += 1; continue
        m = re.match(r"^(\s*)[-*]\s+(.*)$", ln)
        if m:
            # merge hanging continuation lines into the same bullet
            text, j = m.group(2), i + 1
            while j < len(lines) and lines[j].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s", lines[j]) \
                    and lines[j].strip() and not lines[j].lstrip().startswith(("|", ">", "#", "<", "```")):
                text += " " + lines[j].strip(); j += 1
            body.append(("bullet", strip_inline(text))); i = j; continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if m:
            body.append(("num", f"{m.group(1)}. " + strip_inline(m.group(2)))); i += 1; continue
        # plain paragraph (merge soft-wrapped lines)
        text, j = s, i + 1
        while j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith(("|", ">", "#", "-", "*", "<", "```")) \
                and not re.match(r"^\s*\d+\.\s", lines[j]):
            text += " " + lines[j].strip(); j += 1
        t = strip_inline(text)
        if t:
            body.append(("body", t))
        i = j
    return (title or "(untitled)", body)


# ---------------------------------------------------------------- pptx writing
def esc(s):  # XML escape
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def para(kind, text):
    sz, color, font, bullet, indent = 1400, "1B2B4A", None, False, 0
    if kind == "bullet": bullet = True
    if kind == "num": indent = 0
    if kind == "quote": color, sz = "2E5FAC", 1300
    if kind == "gloss": color, sz = "666677", 1000
    if kind == "code": font, sz, color = "Consolas", 1150, "11233F"
    if kind == "table": font, sz = "Consolas", 1150
    bu = '<a:buChar char="•"/>' if bullet else "<a:buNone/>"
    it = ' i="1"' if kind in ("quote", "gloss") else ""
    latin = f'<a:latin typeface="{font}"/>' if font else ""
    return (f'<a:p><a:pPr marL="{285750 if bullet else indent}" indent="{-285750 if bullet else 0}">{bu}</a:pPr>'
            f'<a:r><a:rPr lang="en-US" sz="{sz}"{it} dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{latin}</a:rPr>'
            f"<a:t>{esc(text)}</a:t></a:r></a:p>")


def slide_xml(title, body):
    body_ps = "".join(para(k, t) for k, t in body) or para("body", "")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="457200" y="274638"/><a:ext cx="{EMU_W - 914400}" cy="800000"/></a:xfrm></p:spPr>
<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="2600" b="1"><a:solidFill><a:srgbClr val="1B2B4A"/></a:solidFill></a:rPr><a:t>{esc(title)}</a:t></a:r></a:p></p:txBody></p:sp>
<p:sp><p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="457200" y="1200150"/><a:ext cx="{EMU_W - 914400}" cy="{EMU_H - 1600200}"/></a:xfrm></p:spPr>
<p:txBody><a:bodyPr><a:normAutofit fontScale="90000"/></a:bodyPr><a:lstStyle/>{body_ps}</p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:overrideClrMapping bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/></p:clrMapOvr></p:sld>"""


THEME = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="plain"><a:themeElements>
<a:clrScheme name="plain"><a:dk1><a:srgbClr val="1B2B4A"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="2E5FAC"/></a:dk2><a:lt2><a:srgbClr val="EEF2F8"/></a:lt2><a:accent1><a:srgbClr val="2E5FAC"/></a:accent1><a:accent2><a:srgbClr val="E0A96D"/></a:accent2><a:accent3><a:srgbClr val="8FBF8F"/></a:accent3><a:accent4><a:srgbClr val="9BBCE0"/></a:accent4><a:accent5><a:srgbClr val="B0B0B0"/></a:accent5><a:accent6><a:srgbClr val="6B4A2B"/></a:accent6><a:hlink><a:srgbClr val="2E5FAC"/></a:hlink><a:folHlink><a:srgbClr val="5B7BB0"/></a:folHlink></a:clrScheme>
<a:fontScheme name="plain"><a:majorFont><a:latin typeface="Helvetica"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Helvetica"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="plain"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements></a:theme>"""

MASTER = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>"""

LAYOUT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="titleAndBody"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"""


def build(out_path, slides):
    n = len(slides)
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>']
    ct += [f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, n + 1)]
    ct.append("</Types>")

    pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                 '<Relationship Id="rIdM" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
                 '<Relationship Id="rIdT" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>']
    pres_rels += [f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>' for i in range(1, n + 1)]
    pres_rels.append("</Relationships>")

    sld_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, n + 1))
    pres = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdM"/></p:sldMasterIdLst>
<p:sldIdLst>{sld_ids}</p:sldIdLst>
<p:sldSz cx="{EMU_W}" cy="{EMU_H}"/><p:notesSz cx="{EMU_H}" cy="{EMU_W}"/></p:presentation>"""

    rel_layout_master = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>'
    rel_master = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>'
    rel_slide = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>'

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "\n".join(ct))
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", "\n".join(pres_rels))
        z.writestr("ppt/theme/theme1.xml", THEME)
        z.writestr("ppt/slideMasters/slideMaster1.xml", MASTER)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", rel_master)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", LAYOUT)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rel_layout_master)
        for i, (title, body) in enumerate(slides, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(title, body))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", rel_slide)


slides = [parse_slide(s) for s in slides_md]
out = root / "slides" / args.out
build(out, slides)
print(f"wrote slides/{args.out} ({out.stat().st_size} bytes, {len(slides)} text-only slides; "
      f"{sum(1 for t, b in slides if b and 'paste' in b[0][1])} image-placeholder pages)")
