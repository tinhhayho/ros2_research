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

## Addendum — draw.io mirrors for the two deck-local diagrams (2026-07-16)

`autosar/slides/assets/drawio-pages/autosar-timeline.xml` and `cp-signal-path.xml` added
as editable mirrors of the two already-fact-checked SVGs (module-local `drawio-pages/`
directory, same bare-mxGraphModel convention as the shared pool). **No new claims**: the
mirrors are required to carry every visible SVG string verbatim, enforced by an
independent parity verifier per diagram (workflow `wf_8c898ee6-4ba`, Opus authors +
verifiers, fix rounds until pass) — so no fact-check run was needed. The cp-signal-path
pinned strings from Run 3 ("CAN Transport Layer", "sign extension", the honest SWS
source line, no "§3.1") are asserted explicitly by the verifier.
