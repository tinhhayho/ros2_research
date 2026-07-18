# Info audit — citation coverage of the 30-minute compact deck (2026-07-18)

**Scope**: `autosar/slides/autosar-compact-deck.md` only (26 slides, 843 lines).
**Question**: which externally-sourced content has no source note on its own slide?

**How produced**: workflow `compact-deck-citation-audit` (run `wf_84ad57de-efa`) — 9 read-only
inventory agents over disjoint slide ranges, then one adversarial verifier per candidate
(47 candidates re-read the whole slide trying to refute "uncited"). 56 agents, 0 errors.
Result: **32 confirmed uncited**, 15 overturned (a source note was found), 1 say-note-only
citation. The orchestrator re-verified the MAJOR items by hand (lines 40–58, 246–266,
695–707). No files were changed.

**Context that frames everything below**: the deck front-matter (lines 33–34) says
"External claims are sourced from URLs. The full deck carries the references." So the
compact deck *deliberately* defers most citations to the 73-slide deck. The findings
below are the places where that deferral leaves a specific date, number, quote, or
market claim standing alone on a slide.

---

## Verdict

The four repo slides + four code slides (1/4–4/4) and every spec-figure slide are fully
sourced on-slide (repo@commit pins, GitHub permalinks with line ranges, figsrc captions,
requirement IDs). The gaps cluster on **six slides**: *Why AUTOSAR exists*, *Classic in
one slide*, *CP comms + diagnostics*, *Why Adaptive exists*, *AP runs only on a POSIX OS*
(right column of the kernel table), *CP vs AP*, and *Which stack on which silicon* —
plus two presenter-note mentions. Everything flagged already has a verified source in
`research/fact-check-2026-07-17.md` or the research notes; the fix is only to surface it.

---

## MAJOR — specific dates, numbers, quotes, superlatives with no on-slide source

1. **"First ASIL-D AUTOSAR impl certified 2016" — stated 3×, never sourced.**
   Lines 82 (*Classic in one slide*), 703 (*CP vs AP*), 823 (*Three takeaways*).
   ISO 26262 is named beside it, but that names the standard, not the certification
   event. Verified source on file: Vector MICROSAR Safe, exida certificate, 2016
   (fact-check 2026-07-17). One verifier passed line 823 on the "ISO 26262 is named"
   basis while two others confirmed 82/703 uncited — same fact, one fix.
2. **AUTOSAR partnership numbers** — founding talks **2002**, Development Agreement
   **July 2003**, **~360 partners today** (lines 44–45). The slide's only citation,
   (Heinecke et al., 2006), is attached to a different bullet. Source: autosar.org.
3. **Rivian skips AUTOSAR** — asserted on lines 52 (*Why AUTOSAR exists*), 767 and 773
   (*decision map*) with no source. The actual citation (Sonatus interview, with quote)
   exists only on line 811 (*decision tree* slide) — three slides earlier than none of
   these; each slide must stand alone per the deck's own design goal.
4. **AP safety market status** — "**ASIL-B shipping, ASIL-D underway**" (line 703) and
   the gloss hedge "no fully-certified end-to-end ASIL-D AP middleware ships as of
   mid-2026" (line 705). Load-bearing market claims, no source note.
5. **CAPI "the one complete official implementation … partner-gated"** (line 646).
   The gloss only expands the acronym. Needs the AUTOSAR partner-deliverable source.
6. **"DoIP the only standardized transport (custom permitted)"** for AP diagnostics
   (line 701) — a normative spec assertion with no AP Diagnostic Management doc/ID.

## MINOR — named-but-not-cited product/architecture facts

7. **Kernel table product rows** (lines 164–167): Linux/AGL, SAFERTOS, INTEGRITY,
   NuttX carry no per-product source (FreeRTOS's README quote has no permalink;
   Zephyr/PikeOS/VxWorks passed only because "POSIX" appears in the row text — same
   class). One table-level source line would cover all rows consistently.
8. **CP architecture facts asserted module-name-only**: COM/I-PDU/K-matrix
   (lines 110, 700), DEM/DCM split (line 112), CP-limits list (line 132), AP model row
   (line 699). No SWS document is ever named for them (the deck names doc IDs elsewhere,
   e.g. line 159, so the convention exists).
9. **Silicon/vendor tables** (lines 697, 767–771): AURIX/S32K/RH850,
   Orin/Thor/Qualcomm/S32G/R-Car, Vector/EB corbos/ETAS RTA-VRTE/Qorix, Thor FSI +
   lockstep R52. The gloss says these "repeat facts verified elsewhere" without saying
   where (the "elsewhere" is `autosar/research/` + full-deck References 4/4).
10. **AUTOSAR licensing model** — "specs free to read, license to build" (line 46).
11. **Presenter-note-only external claims, uncited**: "the SOME/IP stack that BMW
    originated" (line 592); MICROSAR Safe and S-CORE named as options (line 815).
12. **Factual contradiction (leftover from the ~45→~40 board-count fix)**: body says
    "about 40 boards" (lines 246, 258) but the say-note still says "about forty-five
    boards" (line 266). Verified by hand.

## NIT / observations

- The SAFERTOS "carry the whole ISO 26262 safety case yourself" point is sourced only
  via the decision-tree diagram + say-note (fine, but note-only).
- "DDS present since R18-03" (line 199) is the weakest *cited* item — release named in
  the claim, no document/section.

## Strengths

- All 8 repo/code slides: repo@commit pins, full permalinks with line ranges, attributed
  README quotes — nothing uncited.
- Spec figures consistently carry figsrc captions (doc + release + figure number); the
  coexistence slide attributes its verbatim quote (AP_EXP_PlatformDesign §3.4).
- The POSIX slide cites requirement IDs with titles and doc numbers in the visible body.
- Tesla/Rivian claims on the decision-tree slide carry inline URLs.

---

## Proposed fixes (awaiting approval — nothing changed yet)

- **Option A (recommended, small)**: fix MAJOR 1–6 + MINOR 12. Add short gloss/source
  notes: "first cert = Vector MICROSAR Safe, exida, 2016"; "partner count: autosar.org,
  2026"; "(Sonatus interview)" beside Rivian on lines 52 and 773; source the ASIL hedge
  and CAPI lines; name the AP DM spec for the DoIP claim; say-note forty-five → forty.
  All wording comes from already-verified facts; run the fact-parity check after.
- **Option B (adds consistency)**: Option A + one-line table sources for the kernel
  table and the two silicon tables ("sources: full deck References 3/4–4/4 +
  autosar/research/"), covering MINOR 7–9 without per-cell citations.
- **Option C**: full per-item citation parity with the big deck — probably overkill for
  a 30-minute deck that already declares the full deck as its reference carrier.

---

## Resolution (2026-07-18) — Option A applied and verified

User approved **Option A**. Applied by workflow `compact-deck-optA-citations`
(run `wf_5acb0afc-824`: pin research → fixer with pre-edit snapshot → rebuild +
PDF overflow check → two max-effort verifiers, fact-parity and citation-correctness,
both PASS). Edits, by original line number:

- **MAJOR 1 resolved** — first-cert source added three times: gloss of *Classic in one
  slide* (l.84) and *CP vs AP* (l.705) and *Three takeaways* (l.828):
  "Vector MICROSAR Safe, certified by exida in 2016" (per fact-check 2026-07-17).
- **MAJOR 2 resolved** — *Why AUTOSAR exists* gloss (l.54): "founding dates and partner
  count: autosar.org".
- **MAJOR 3 resolved** — inline "[Sonatus interview](https://www.sonatus.com/resources/
  vidya-rajagopalan-of-rivian/)" added to the Rivian sentences on l.52 and l.773, same
  source as the existing decision-tree citation (l.811).
- **MAJOR 4 resolved (honest label)** — no single on-file primary source exists for
  "ASIL-B shipping, ASIL-D underway", so the gloss now says: "ASIL status is our reading
  as of mid-2026; sources are in the full deck references". No source invented.
- **MAJOR 5 resolved** — *The code 4/4* gloss (l.644): "CAPI partner-gated (AUTOSAR
  partners only): autosar.org/capi".
- **MAJOR 6 resolved** — DoIP transport rule traced to the local spec mirror:
  AP_SWS_Diagnostics (Doc ID 723) R25-11 §7.1 "UDS Transport Layer" (DoIP = ISO 13400-2
  the only network transport detailed; custom UDS transports permitted via the Transport
  Protocol API). Cited in the *CP vs AP* gloss. The fixer's original string carried an
  em-dash; the orchestrator tightened it post-verify (meaning preserved, dash removed).
- **MINOR 12 resolved** — say-note l.266: "about forty-five boards" → "about forty boards".

Render check: the *Why AUTOSAR exists* gloss initially overflowed; fixed with a scoped
per-slide style block (26px → 22px, gloss 15px), the deck's established idiom. All six
edited slides render clean in the rebuilt PDF. `autosar-compact.html` / `.md` rebuilt
via `./run.sh slides-autosar-compact`. MINOR 7–11 and the NITs remain open by design
(Option A scope). Not yet committed.
