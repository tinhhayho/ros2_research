# Info-audit — 2026-07-15 — automotive fleet management cluster

**Scope:** the "fleet management for automotive" cluster — deck slides from "Fleet
management — the same standards, one layer up" through "Two fleets, two standard
stacks" (`slides/research-deck.md`), blog section 6 (`docs/blog-robot-software-stacks-2026-07.md`),
transcript sections for those slides, `research/fleet-uds-autosar-2026-07.md` (F1–F17),
and the seven fleet-related diagram pairs (SVG + drawio mirror).

**Method:** three parallel read-only Sonnet auditors — (1) cross-document consistency,
(2) external freshness re-verification against primary sources, (3) diagram content +
SVG↔drawio mirror check. Orchestrator re-verified every MAJOR finding directly before
fixing. All fixes below were applied same-day (user pre-approved this run).

## Findings and resolutions

| # | Sev | Finding | Resolution |
|---|---|---|---|
| 1 | MAJOR | `uds-diag-stack` (SVG+drawio) listed `0x34/0x36/0x37 flash`, omitting `0x35` — the exact omission the audit had flagged in the source draft, self-contradicting the corrected table two slides later (deck:898) | Label now `0x34/0x35/0x36/0x37 transfer (flash)` in both SVG and drawio; PNG re-rendered |
| 2 | MAJOR | `fleet-standards-map` (SVG+drawio) same omission: `UDS flash (0x34/0x36/0x37)` | Now `0x34/0x35/0x36/0x37`; both files + PNG |
| 3 | MAJOR | The R17-03 first-release correction (commit 48fb76c, 2026-07-14) updated four docs but added **no citation** to the audit trail — row F8 still cited only the SOME/IP Transformer PDF | Sources added to `fleet-uds-autosar-2026-07.md` and claims-audit row F8: autosar.org R17-03 standards set (2017-03-31) + R17-10 announcement (2017-10-27), pointer to `research/fact-check-2026-07-14.md` where the verification lives |
| 4 | MINOR | "30 claims checked, **8 refuted**" (deck, blog ×2, transcript ×2) conflated 7 ❌ refuted + 1 ❓ zero-documentation — a distinction the verdict table's own legend insists on. Verified by symbol count: table rows 12,13,18,21,25,26,27 = ❌; row 29 = ❓ | All five spots now say 7 refuted + 1 with no public documentation |
| 5 | MINOR | Wind River "ASIL-D-suitable (TÜV SÜD)" is a **2019-10-15** press release (program-readiness assessment, not a completed cert) presented undated next to Vector's 2025/2026 status | Date + "program assessment, not completed cert" added in deck gloss, blog, transcript, research file |
| 6 | MINOR | "DM = DoIP-only" pinned to AP R22-11; R23-11/R24-11 never re-checked (autosar.org unreachable from sandbox); one unconfirmed web summary suggests R24-11 may add CAN to DM | **Resolved same day**: the actual R22-11/R23-11/R24-11 `SWS_Diagnostics` PDFs were fetched from autosar.org — DoIP-only **still true in R24-11** (§7.1 p.78: "only … Ethernet-based network technologies, which mandates support of DoIP"; the "upcoming releases will also detail CAN…" sentence unchanged verbatim since R22-11; only R24-11 transport change = DoIP amendment-2023 v4). The CAN suggestion was confirmed search-engine hallucination. Verdict-table row 7 updated with the full citation |
| 7 | NIT | Same-file drift: "Common Interface over UDP over Ethernet" (claim) vs "Common Interface over UDP" (sources section) | Sources line completed |
| 8 | NIT | AUTOSAR UCM spec title shifted R23-11 ("Vehicle Update and Configuration Management") then back in R24-11 per search-indexed titles — likely doc reorg | No action; watch on next AUTOSAR-touching audit |

## Freshness verdicts (agent 2, re-verified from primary sources where reachable)

CONFIRMED-STILL-CURRENT: SOVD = ISO 17978-1/-2/-3:2026 (REST/JSON, coexists with UDS) ·
ASAM SOVD v1.0 wording · UCM/UCM-Master roles · Vector MICROSAR Adaptive Safe ASIL-B
shipping with ASIL-D "planned for 2026" (Sept-2025 status) · DriveOS 7.0.3 quotes
re-fetched **verbatim** ("Multiple Guest OS are not supported… QNX or Linux, but not
both"; "Common Interface… UDP over Ethernet") · Thor companion MCU = RH850 / Orin =
AURIX TC397X + Vector AFW · MB.OS CLA SOP June 2025 (Rastatt) · Vector supplies the
MB.OS base layer · NVIDIA enhanced-L2 US rollout "by end of this year" (blog dated
2026-01-05, still live) · Uber 28 cities by 2028, 100k vehicles "starting 2027" · the
vECU-partitions-on-Thor refutation stands (nothing new public).

Carried forward unverified this pass: COQOS SoC list (opensynergy.com not re-fetched).
Known sandbox limits reproduced: iso.org / autosar.org / windriver.com TLS-blocked.

## Strengths (all three agents concur)

- Deck/blog/transcript/research are synchronized byte-for-byte on dozens of SIDs, ISO
  numbers, dates and verbatim quotes; gloss pointers (rows F5, F8–F10…) all resolve to
  the right rows.
- Six of seven diagram pairs fully accurate; all seven SVG↔drawio mirrors are faithful
  text-for-text (the two defects existed identically in both formats — content bugs,
  not drift).
- Struck claims (ETAS, Neusoft, "Classic on Adaptive", Thor-as-gateway) stayed excluded
  everywhere; hedged figures (ECU consolidation) remain properly caveated.
