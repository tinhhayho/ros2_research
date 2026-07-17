# Fact-check — 2026-07-17 (stack-decision/fleet slides, repo-catalog + C++ code slides, coexistence redesign, figure glosses)

Run: packaged `fact-check` workflow (`.claude/workflows/fact-check.js`), 30 claims,
42 agents (30 verify + 12 adversarial refute), 0 errors. Scope: every NEW claim added
to the decks on 2026-07-17 — the compact deck's coexistence redesign, open-source-shelf
slide, C++-only code slide and "Choosing your stack" slide; the full deck's two
"skip AUTOSAR / fleet contracts" slides, References 4/4, and the 12 figure-gloss
additions. Research provenance: `autosar/research/{non-autosar-oem-fleet,
fleet-contracts-standards, sdv-fleet-oss-toolbox, autosar-vs-inhouse-decision}-2026-07.md`
(4 Opus researchers + 1 max-effort adversarial claim verifier, workflow wf_05bf2b75-181;
5 of 33 research claims rejected pre-drafting: broken Tesla-Toolbox citation, 2
unverifiable regulation-text links, 2 weakly-sourced OEM items).

## Verdicts: 19 correct · 11 partially-correct · 0 wrong · 0 unverifiable

All 11 partially-correct corrections were applied to the decks in place. One initial
verdict was overturned by the adversarial pass in the CLAIM's favor.

### Overturned by the refute pass (no deck change needed)
- **coex-fig-regions** — initial verifier said the bottom `trajectory control /
  safety function` box sits in a third, untagged dashed region, not region C. The
  refuter re-rendered PlatformDesign p.18 at 600 dpi and ran pixel band-scans: no
  closing bottom edge exists for a "tight" C rectangle and no left edge exists for a
  separate third region (control test on the genuinely-separate A boundary confirmed
  the method detects real gaps). The C outline is one continuous Γ-shaped boundary
  wrapping the sensor boxes AND the trajectory-control/safety-function box. Slide
  wording ("Region C … groups the sensor-input boxes … and the bottom
  trajectory-control + safety-function box") stands as written.

### Corrections applied (deck edits, 2026-07-17)
1. **UDS "no law mandates them" was too absolute (US)** — CARB (13 CCR §§1968.2/1971.1,
   rule in force since 2022-11-22) mandates the UDS-based **SAE J1979-2 "OBDonUDS"**
   for **all MY2027+** vehicles. Both decks' UDS/DoIP bullets now read "de-facto,
   tilting legal in the US" with the CARB mandate named; DoIP stays unmandated;
   EU 2017/1151 names ISO 14229 only as an allowed option. Compact say-note updated.
2. **CARB OBD-II 1996 scoped** — gasoline vehicles MY1996; diesel followed MY1997.
3. **MICROSAR Safe date** — first exida ASIL-D certification was **2016** (world's
   first AUTOSAR impl at ASIL D); the 2020 certificate is the follow-up covering
   29+19 modules. Both decks' cells now say "since 2016; 2020 cert: 29+19 modules".
4. **S-CORE / #759** — discussion #759 never says "complementary"; it proposes AUTOSAR
   reuse S-CORE's processes/tooling. Slide sentence and References 4/4 annotation
   reworded; "no official AP-compatibility statement either way" retained.
5. **CARIAD cumulative losses** — the cited article says "over **$7.5 billion**" (USD);
   euro cumulative ≈ €6.9 bn (2.1 + 2.392 + 2.431). Slide now quotes the dollar figure
   with the euro approximation; FY2024 €2.431 bn stands.
6. **Li Auto Halo OS** — 2025-03-27 was the open-sourcing *announcement*; code shipped
   in phases (v0.1.0 2025-04-23 → v1.0.0 2025-06-30, Gitee, Apache-2.0). References
   annotation expanded; "challenging AUTOSAR" framing confirmed as press-accurate.
7. **SOME/IP Message Type gloss was wrong** — per [PRS_SOMEIP_00055]: 0x00 = REQUEST,
   0x01 = REQUEST_NO_RETURN, 0x02 = NOTIFICATION, 0x80 = RESPONSE, 0x81 = ERROR.
   Bonus finding: the deck's Fig 5.11 crop is specifically the **Magic Cookie Message**
   (§5.2.1.2) — its 0x01/0x02 are the sentinel's reserved constants. Gloss now carries
   the correct enumeration + a note identifying the crop.
8. **SecOC field order** — per [PRS_SecOc_00211]: Authentic I-PDU → Freshness Value →
   Authenticator (Freshness before Authenticator; optional, truncated; truncation
   disallowed for signature-based authenticators). Gloss reordered + qualified.
9. **OS-Application ownership** — Resources are *granted* to OS-Applications, not owned
   (SWS_OS §7.6). Fixed in the new partitioning-figure gloss AND in the pre-existing
   functional-safety slide gloss which carried the same error; "trusted **may** run
   in supervisor mode".
10. **E2E gloss overclaim** — detection is high-probability with a bounded residual
    risk, not an absolute "cannot corrupt"; protect/check happen at the SW-Cs. Reworded.
11. **Layered-architecture gloss** — the BSW has **four** layers (Services, ECU
    Abstraction, Microcontroller Abstraction, Complex Drivers); Complex Drivers is a
    BSW layer drawn spanning hardware→RTE, not an add-on outside the BSW. Reworded.

### Confirmed clean (highlights)
Fig 3.2 region-A contents and the direct sensor→safety-function arrows (verified at
600 dpi against the local PDF, asset pixel-identical); §3.4 "AP will not replace CP …
interact … to form an integrated system" verbatim; OfferService()/StopOfferService()
= [SWS_CM_00101]/[SWS_CM_00111] on ServiceSkeleton; V-UCM Backend↔OTA-Client protocol
"out of scope for this specification document"; R155 CSMS / R156 SUMS = management
systems for type approval; eCall M1/N1 since 2018-03-31; SOVD = ISO 17978 parts 1–3
published; AWS IoT FleetWise closed to new customers (2026); Tesla fleet-telemetry
README quote + WebSocket/mTLS/protobuf/Kafka path; Rivian quote; S-CORE charter
quotes; ETAS both-and; teslamotors/linux; ISO 24089 optional; ISO 15118 + AFIR
framing; langroodi restatement; all OSS versions/dates; UML stereotype/multiplicity
gloss.

Both decks rebuilt after the fixes (`./run.sh slides-autosar`,
`./run.sh slides-autosar-compact`).

## Addendum — stack-decision-tree diagram (2026-07-17)

`autosar/slides/assets/stack-decision-tree.svg` (+ drawio mirror
`drawio-pages/stack-decision-tree.xml`) added and swapped into the compact deck's
"Choosing your stack" slide, replacing the 3-column table with a two-question /
five-landing decision tree (per-leaf HW/SW requirement lines). **No new claims**: every
string restates facts verified in this file or the 2026-07-16 runs ([SWS_OSI_01010],
[RS_OSI_00100], first ASIL-D cert 2016, CARB OBDonUDS MY2027+, S-CORE not-an-AP-impl,
Rivian FreeRTOS zonals, fleet-contract labels). Enforced by the workflow's max-effort
adversarial verifier (wf_5e69d51e-162): frozen-string spec compliance byte-identical
(2390 == 2390 chars, both directions), 6-fact repo-traceability spot-check clean,
SVG↔mirror string parity clean, layout overlap checks clean.

## Addendum — blog article for the compact deck (2026-07-17)

`autosar/blog/autosar-in-20-minutes-2026-07.md` added (~2950 words, 15 sections, 8
`<!-- suggested figure: ... -->` placeholders, no images per blog convention).
**Restatement-only by construction**: the drafter was constrained to facts in the two
fact-checked decks; a max-effort adversarial reviewer then traced the article line by
line against them (C++ snippet byte-diffed, permalink char-identical, every
date/version/requirement-ID/quote checked). It caught and the fixer corrected 2 MAJOR
drafter additions — a wrong "(PSE52 is the multi-process IEEE 1003.13 profile)"
parenthetical (PSE52 is single-process; deleted to match the deck cell) and DoCAN
mis-attributed as an AP DM transport (reworded: CP runs UDS over DoCAN/DoIP; AP DM
standardizes DoIP only, custom permitted) — plus 1 MINOR (PDU expanded at first use).
Workflow wf_c170a7ae-1f1.

## Addendum — plain-language rewrite of the compact deck + blog (2026-07-17)

Per the owner's style instruction (readers include Vietnamese ESL engineers), the
compact deck and the 20-minute blog article were rewritten into plain everyday
English: full sentences, one idea per sentence, body-prose em-dashes 171→0 (deck)
and 71→0 (blog; the one survivor is inside the byte-frozen langroodi permalink
label), idioms replaced ("street name", "kills the anxiety", "shelf", "brain/
reflexes", "tilting legal" and similar). **Style-only by construction and by proof**:
two max-effort fact-parity verifiers diffed the rewrites against pre-rewrite
snapshots — URLs, code blocks (md5-identical), requirement IDs, the full
digit-bearing-token multiset, verbatim quotes, figure macros/comments and gloss
meanings all identical both directions; deck must_fix = 0; blog had 3 MINOR
non-fact dropped transition sentences, restored by the fixer. Workflow
wf_86958ec4-12d (rewrites cached on resume after a session-limit interruption;
verify+fix ran clean). Compact deck rebuilt.

## Addendum — decision tree v2 (safety-first) + three per-repo deep-dive slides (2026-07-17)

Owner feedback drove two structural changes, both implemented in workflow
wf_1e27333e-cac and verified by two max-effort adversarial verifiers:

**Decision tree v2.** `stack-decision-tree.svg` (+ drawio mirror) redrawn: safety is
now the MCU-side question ("What safety level (ASIL) must this ECU carry, and who is
the customer?") with six outcomes — forced buy-Classic when selling to an OEM
(RFQ + MICROSAR Safe exida ASIL D since 2016); for in-house ASIL products the two
honest options (buy Classic anyway, or a certified non-AUTOSAR RTOS: SAFERTOS,
TÜV SÜD, ISO 26262 ASIL D, with the whole safety case carried in-house, the Rivian
path); QM = free choice; HPC side annotated "the HPC's ASIL story lives outside the
middleware … that companion MCU runs CP". This replaces the v1 framing in which
"vertically integrated" implied skipping AUTOSAR — the owner correctly objected that
a vertically integrated company can still buy AUTOSAR. Verifier A: 42/42 frozen
strings verbatim both directions (SVG and mirror normalize to identical 3163-char
word-multisets), 7/7 fact-traceability checks clean, layout overlap checks clean;
one cosmetic fork-arrowhead mismatch fixed. Compact slide say-note (~95s) and the
blog's "The decision tree" section rewritten to match (295 words, no em-dashes,
Rivian quote byte-identical).

**Per-repo deep-dive slides.** The compact deck's 7-row "open-source shelf" table
slide was replaced by three "Inside the repo" slides (langroodi/Adaptive-AUTOSAR @
866d158 · Eclipse S-CORE LoLa @ 6acba35 · COVESA vsomeip @ v3.7.4), each showing the
real trimmed directory tree, start-reading entry points, build/run, limits, and one
verbatim README quote; the same three slides were inserted into the full deck after
the landscape slide (deck counts: compact 21 slides ≈ 24.2 min, full 68 slides).
CAPI was demoted from a table row to the single boundary line on slide 3/3;
iceoryx/Fast DDS/CommonAPI rows left the compact deck (they remain in the full
deck's building-blocks slides). Verifier B independently re-fetched all three pinned
git trees from the GitHub API: every path on the slides exists verbatim, all README
quotes verbatim, licenses match, no invented numbers; two minor wording fixes
applied (a LoLa types.h description tightened to what the header actually contains;
a dangling star-symbol gloss entry removed). Style contract held: no em-dashes in
new prose/say-notes.

## Addendum — per-repo CODE slides, Classic added, deck retitled to 30 minutes (2026-07-17)

Owner direction: every repo gets a structure slide AND a real-code slide, Classic must
be represented, and the meeting budget is now 30 minutes. Workflow wf_e6e217dd-167:

- **openAUTOSAR/classic-platform joins as the Classic representative** (pinned @
  0943377, master HEAD; miner finding recorded on-slide: master unchanged since
  2020-04-02, "Remove GPLv2 violating files"; no examples/ directory at this ref —
  the structure slide's limits say so). Structure slide "Inside the repo 1/4" +
  code slide with Com_SendSignal (Com_Com.c L44-52) and Dem_ReportErrorStatus
  (Dem.c L7458-7465).
- **Code slides for all four repos** (8 repo slides total, structure + code each):
  langroodi @ 866d158 (RpcClient class shape rpc_client.h L19-29 + ExecutionManagement
  cluster composition execution_management.cpp L146-156), S-CORE LoLa @ 6acba35
  (tutorial provider OfferService + consumer typed-proxy Subscribe,
  score/mw/com/doc/tutorial/chapter_1), vsomeip @ 3.7.4 = 7bcc1e0 (response-sample
  init/register_message_handler + request-sample client side). Every snippet
  byte-verbatim with commit-pinned #L-range permalinks.
- **Verification**: verifier A re-fetched every file from raw.githubusercontent at the
  pinned refs and byte-diffed all 8 snippets (only CRLF→LF normalization on the two
  classic-platform files — their sources are CRLF); all refs/paths/README quote/
  license confirmed; 2 gloss issues fixed (an invented SocketRpcServer subclass claim
  corrected to SocketRpcClient; board count ~45→~40 per the actual tree's 41
  top-level board dirs). Verifier B proved parity (only mandated edits in both decks;
  blog untouched), then a render check caught the Inside-1/4 gloss clipping —
  fixed by tightening that slide's scoped CSS, re-render clean. Stale say-note
  ordinals ("first of three") renumbered for the 4-repo structure in both decks.
- **Deck retitle**: compact deck is now "AUTOSAR in 30 minutes" (title, lead say-note,
  run.sh echo + usage line); Q&A cross-reference updated to the full deck's new count.

## Addendum — blog synced to the 30-minute deck (2026-07-17)

Blog renamed `autosar-in-20-minutes-` → `autosar-in-30-minutes-2026-07.md`; title
updated; the open-source section rewritten from the seven-project list into the
deck's four-repository story (classic-platform · langroodi · LoLa · vsomeip, with
the Com_SendSignal code block and permalink byte-identical to the deck, the CAPI
boundary line, and a pointer to the full deck for iceoryx / Fast DDS / CommonAPI).
Workflow wf_dad84cb6-b9a: max-effort verifier proved parity vs the pre-edit
snapshot (only the title and the sanctioned section changed), traced every SHA /
license / date to the deck slides, and byte-diffed the code block + permalink;
3 style fixes applied (CAPI, GPL-2.0, MPL-2.0 expanded at first use). Drawio
mirrors needed no changes this round (tree-v2 parity already verified; no SVG
changed afterwards).
