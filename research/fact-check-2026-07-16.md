# Fact-check — 2026-07-16 — AUTOSAR deck: fleet walkthrough slides + linked references

**Context.** User request: review the AUTOSAR deck for how a fleet talks to a CP+AP
vehicle, add a concrete real example, and link every reference directly to its document.

## What changed in `autosar/slides/autosar-deck.md` (now 45 slides)

- New slide **"Fleet ↔ a CP+AP vehicle — one request, end to end"** (SOVD/TCU → central
  gateway → DM on AP / DoIP→DoCAN → DCM+DEM on CP; OTA via V-UCM + UDS 0x34–0x37) with two
  real anchors: Mercedes MB.OS (named CP+AP coexistence) and Rivian Gen 2 (shipped zonal
  topology, explicitly *not* an AUTOSAR deployment).
- New diagram slide reusing the already-verified `fleet-uds-flow.svg`.
- References 1/2 and 2/2: **61 of 63 sources converted to direct links**, every URL
  live-verified (curl range-request; autosar.org TLS workaround). Two dead links kept as
  plain text: embetronicx RTE tutorial (HTTP 401), qorix.ai press release (redirect loop).
- Review-driven fixes (independent Opus reviewer, 1 MAJOR + 2 MINOR + 2 NIT): split
  **TCU vs central gateway** into two named boxes (MAJOR — the slide previously collapsed
  them as "TCU/gateway"); narrowed the DoIP-only currency claim to the releases actually
  re-read (R24-11 + R25-11); gloss additions (MEB/PPE/CARIAD/ICAS/SSP, SIG/K8s/CI-CD);
  scoped font trim on the densest AP slide.

## Fact-check run on the NEW claims (`fact-check.js` claims mode, run `wf_c17a3d15-b4e`, 7 agents)

**6 claims — 5 ✅ correct · 1 ⚠️ partially-correct (fixed).**

| # | Claim | Verdict | Note |
|---|---|---|---|
| F1 | Rivian Gen 2: 17→7 ECUs, 3 zonal (West/East/South) | ✅ high | Munro, PopSci, InsideEVs, Rivian's own pages |
| F2 | Dual DRIVE Orin, ~250 TOPS combined | ✅ high | NVIDIA partner page + Rivian announcement; still current config (custom RAP1 silicon announced Dec 2025 targets R2, not shipped in R1) |
| F3 | Rivian in-house stack, not AUTOSAR | ✅ high | On-record quote, Rivian SVP Vidya Rajagopalan: "We don't use any of the industry offerings such as AUTOSAR … built on top of FreeRTOS" |
| F4 | CP OTA reflash = UDS 0x34/0x36/0x37 via gateway; V-UCM coordinates | ✅ | ISO 14229-1 service IDs exact; KPIT/EDN Classic-via-AP flashing flow |
| F5 | MEB/PPE/SSP expansions | ⚠️ | **MEB = "Modular Electric Drive Matrix"** (VW's own English rendering), not "…platform" — fixed in the gloss; PPE and SSP correct |
| F6 | CARIAD = VW software subsidiary; ICAS = In-Car Application Server | ✅ | |

## Provenance

- Review + edit workflow: run `wf_d6cbea81-514` (2 Opus agents; reviewer report in the
  workflow journal). Claims run: `wf_c17a3d15-b4e` (~222k subagent tokens).
- Related: `research/fact-check-2026-07-15.md` (Run 3 — the original 97-claim deck check).

## Run 2 — open-source Adaptive AUTOSAR section (slides 33–36, References 3/3, research doc, blog)

**Context.** User request: colleagues want to see the *real shape* of Adaptive AUTOSAR code
from public repos (educational welcome). Added: slides 33–36 + References 3/3 (deck now
**50 slides**; the fleet walkthrough pair moved 36–37 → 40–41), research doc
`autosar/research/adaptive-open-source-2026-07.md`, and a text-only blog post
`autosar/blog/adaptive-autosar-open-source-2026-07.md` (per request, no images — figure
placeholders as HTML comments).

**Pipeline.** 3 research scouts (`wf_5b315d22-3eb`, 22 candidates, every repo fetched live)
→ orchestrator re-verified the two surprising finds first-hand (CAPI git 302→sign-in;
LoLa README wording) → draft + independent review (`wf_507d7bc7-433`, verdict ship;
1 MINOR + 1 NIT fixed: OpenSOVD "Incubating (proposed 2025-05-26)", graveyard date range)
→ claims-mode fact-check `wf_ecadf716-210`: 26 agents, 671 tool calls, ~1.25M subagent
tokens. Code snippets were byte-diffed against their pinned permalinks three separate
times (draft, review, blog).

**Result: 15 claims — 5 ✅ correct · 10 ⚠️ partially-correct · 0 ❌ wrong.**
All 10 corrected in place same day (fixer run `wf_83190c79-1af`) across deck, blog, doc,
plus correction banners on the three `ap-oss-*` notes files:

- **C1** langroodi is **C++14**, not C++17 (`CMakeLists.txt: set(CMAKE_CXX_STANDARD 14)`);
  post-2023 commits are *documentation*-only (one touches CONTRIBUTING.md), not README-only.
- **C2** its release baseline is **per-cluster R20-11–R22-11** (R21-11 most cited; R22-11
  only for com/E2E-Profile11 and phm) — not a headline "R22-11".
- **C3** ara-rs is **dual-licensed Apache-2.0 OR MIT** (not Apache-2.0 alone).
- **C6** S-CORE: no official statement about AP compatibility either way — community
  discussions (#759, #882) explore a mapping layer → phrased "makes no AP-compatibility claim".
- **C7** vsomeip: never mentions `ara::com`, but **does** mention AUTOSAR around E2E
  (changelog "AutoSAR E2E Profile 4", E2E test docs, two `AUTOSAR FO R22-11` citations).
- **C8** iceoryx "used by" table labels only **RTA-VRTE and AVIN AGNOSAR** as AP products;
  Apex.Ida appears without the AP label (safe/certified middleware).
- **C9** iceoryx2: safety wording also lives in README/FAQ ("designed to operate in
  safety-critical systems"), "automotive" is not in the roadmap — core point stands: **no
  AUTOSAR / ISO 26262 / ASIL certification claims**.
- **C10** `ara::com` standardizes **three** network bindings — SOME/IP · Signal-Based ·
  DDS — so DDS is "one of the three", not "the other".
- **C13** uProtocol is **Eclipse-governed** (GM-originated, pairs with COVESA VSS), not an
  "Eclipse/COVESA" joint project.
- **C15** insooth graveyard row: **64 spec PDFs + 17 spec ZIPs (88 files total)** + one
  `ara::per` header — not "~88 PDFs".
- Verified clean: CAPI partner-gating + wording, all LoLa README quotes, S-CORE
  dates/backers/dual-language, CommonAPI dormancy (2024-10-09), OpenSOVD (ISO 17978,
  proposed 2025-05-26), openAUTOSAR/classic-platform GPL-2.0 lineage.

The blog post carries the same claim set as the slides and inherited the same corrections
in the same fixer pass — no unshared claims shipped.

## Run 3 — official spec figures as companion slides (11 unmodified R25-11 excerpts)

**Context.** User request: reuse the figures already in the AUTOSAR specs so viewers
digest faster. Legal basis verified verbatim from the R25-11 PDFs (Disclaimer): *"This
work may be utilized or reproduced without any modification, in any form or by any
means, for informational purposes only."* → pixel-faithful crops, attribution captions,
one covering legal line on References 3/3. Website images were deliberately NOT used
(no such reuse grant).

**Pipeline.** Mining run `wf_e30dd92c-e1e` (inventory → 10 top-value specs → one miner
per spec with a view-crop-view loop → judge with vision over all 43 candidates):
**43 candidates → 11 adopted, 32 rejected** (mostly redundant with the repo's own
fact-checked diagrams). All 11 adoptions are *additions* ("— as the spec draws it"
companion slides); zero replacements. Orchestrator eyeballed the top 4 crops before
approving. Apply + independent review: `wf_fd016528-2ca`, verdict ship.

**Verification is mechanical, not claim-based** (no new textual claims beyond captions):
- sha256 parity ×11: deployed `autosar/slides/assets/spec-*.png` byte-identical to the
  mined originals — the unmodified-excerpt chain is provable.
- Captions rebuilt from miner metadata (doc + figure number extracted from each PDF) and
  diffed line-for-line; the LSA document has no numbered figure captions, so its caption
  cites the printed slide title and page ("Overview of Software Layers — detailed view",
  p. 24) instead of an invented number.
- Every new slide page viewed in the marp-rendered PDF: figure inside frame, caption
  present, legible.

Deck is now **61 slides**; the 11 spec slides sit at 11, 13, 19, 20, 24, 31, 34, 36, 37,
49, 51. Spec PDFs themselves are mirrored (35 files, SHA256SUMS) under `autosar/specs/`
per the same user request — commit `77c2b29`.

## Addendum — main research deck synced to previously-verified facts (2026-07-16)

Three edits to `slides/research-deck.md`, all restating claims already verified in the
07-15 runs (no new claims → no new fact-check run): (1) CP 4.2.1 dated **Oct 2014** (was
"2016") in the CP-vs-AP table and the myths gloss — the 07-15 finding finally propagated
to the main deck; (2) the DM row/glossary now say **DoIP = the only *standardized*
transport** (custom transports permitted) instead of bare "DoIP only"; (3) the CP comms
row + gloss note the **R25-11 DDS Transformer on Classic** (standard-level, no shipping
vendor implementation verified). Also: `spec-figures-manifest.md` added next to the spec
PNGs (sha256 ↔ doc/figure/page provenance table), and `slides/research.pdf` gitignored
per the keep-untracked decision.

## Addendum — draw.io mirrors for the two deck-local diagrams (2026-07-16)

`autosar/slides/assets/drawio-pages/autosar-timeline.xml` and `cp-signal-path.xml` added
as editable mirrors of the two already-fact-checked SVGs (module-local `drawio-pages/`
directory, same bare-mxGraphModel convention as the shared pool). **No new claims**: the
mirrors are required to carry every visible SVG string verbatim, enforced by an
independent parity verifier per diagram (workflow `wf_8c898ee6-4ba`, Opus authors +
verifiers, fix rounds until pass) — so no fact-check run was needed. The cp-signal-path
pinned strings from Run 3 ("CAN Transport Layer", "sign extension", the honest SWS
source line, no "§3.1") are asserted explicitly by the verifier.
