# Fact-check — 2026-07-15 — AUTOSAR module (run 3) + abbreviation keys (runs 1-2)

## Run 3 — the new AUTOSAR research module (autosar/)

**Scope:** the freshly drafted `autosar/slides/autosar-deck.md` (42 slides) plus the two
new diagrams `autosar/slides/assets/autosar-timeline.svg` and `cp-signal-path.svg` —
before first ship, per the standing rule. The three research docs under
`autosar/research/` inherited the same corrections.

**Method:** `fact-check` workflow (`.claude/workflows/fact-check.js`), files mode —
extract pass, then one Sonnet verify agent per claim against primary sources, then an
adversarial refute pass on every non-clean verdict. Run `wf_4748cedc-22d`:
121 agents, 1658 tool calls, ~4.6M subagent tokens.

**Result: 97 claims — 79 ✅ correct · 16 ⚠️ partially-correct · 2 ❌ wrong.**
All 18 corrected in place (deck + SVG + docs) the same day; full findings with sources in
`autosar/research/notes/fact-check-findings-2026-07-15.md`. Highlights:

- ❌ c17 — `cp-signal-path.svg` carried a bogus source line ("AUTOSAR CP CAN communication
  stack §3.1" — no such document; §3.1 was the research-note's own section number).
  Replaced with honest attribution to the COM/PduR/CanTp/CanIf SWS set.
- ❌ c30 — Raw Data Streaming removal + Communication Groups obsolescence were
  misattributed to R25-11; both actually happened at **R23-11** (and Communication Groups
  arrived R20-11, not R19-11). Also fixed in `notes/orchestrator-verification.md` §5.
- ⚠️ dates/numbers: partner count 339→**360** (Jan 2025 snapshot; Asia 174 > Europe 140 >
  NA 41) · CP 4.2.1 = **Oct 2014** (not 2016) · ETAS RTA-VRTE ASIL-B = **March 2025**
  (not Feb 2026) · Firewall cluster added **R22-11** · PHM Health Channels obsolete **R21-11**
- ⚠️ phrasing: CanTp = CAN Transport **Layer** · COM does **not** do scaling (only
  endianness + sign extension) · PSE51 **keeps** POSIX shared-memory objects · S-CORE is
  **dual-language C++/Rust** (not "Rust-first") · iceoryx "fully compatible" quote was
  2019-era marketing · QNX 35-38% = analyst estimate of the overall automotive-OS market ·
  EB AdaptiveCore "up to ASIL-D" is a 2017 press-release phrase, no longer current ·
  VW E³ 1.1/1.2 is **domain**-based (zonal arrives with SSP/E3 2.0) · OSEK OS = ISO 17356-**3**
- Verify pass note: the deck's load-bearing headline facts all survived clean — R25-11
  release + DDS-on-Classic (verified against the CP Release Overview PDF directly),
  Orin=AURIX/Thor=RH850 split, "DoIP = only standardized DM transport", ASIL-B-shipping
  hedge, DDS-binding-since-R18-03.
- **Addendum 2026-07-16 — "reading map" slide** (added on request): all 33 spec filenames
  on the slide verified live via HTTP range-requests against the R25-11 directories on
  autosar.org. Two R25-11 renames caught this way and reflected on the slide: the VFB
  document is now `CP_TR_VFB` (was `CP_EXP_VFB` in R24-11) and SecOC is
  `FO_PRS_SecOCProtocol` (was `…SecOcProtocol`).

---


## Run 2 — 7 new glossary expansions (deck-wide abbreviation sweep)

Context: user requested removing all audit-process narration from the slides and
annotating abbreviations instead. Expansions reused from the existing glossary slides
were not re-verified (already audited). Seven expansions had no glossary coverage —
all verified ✅ correct, high confidence, no refute pass triggered (run `wf_1788c4ee-207`,
7 Sonnet agents):

| Term | Shipped expansion | Key source |
|---|---|---|
| QP | Quadratic Programming (whole-body optimizer, solved each control cycle) | arXiv:2510.21773 ("WBC is inherently QP-based") |
| DRC | DARPA Robotics Challenge (trials 2013, finals 2015; Atlas lineage) | darpa.mil news pages 2013/2015 |
| POSIX | Portable Operating System Interface, IEEE Std 1003 family | IEEE 1003.1-2024 title; wikipedia |
| KV cache | attention keys/values stored per generated token; grows with context | HF Transformers "Caching" docs |
| OOM | out of memory | standard usage (Linux OOM killer, CUDA OOM) |
| PID | proportional–integral–derivative controller | standard control-engineering usage |
| PLC | programmable logic controller (IEC 61131) | standard industrial-automation usage |

(PID and PLC were verified but ultimately NOT added to slides — the embedded audience
knows them; recorded here so a future add needs no re-check.)

## Run 1 — E/E-consolidation diagram key (earlier same day)

**What shipped:** two abbreviation-key lines appended to `slides/assets/sdv-ecu-consolidation.svg`
(+ drawio mirror), deck slide 52 — expansions for DC, FL/FR/RL/RR, HPC, AV/AD, OTA, TSN.
User request 2026-07-15 ("thêm chú thích vào cuối slide, FL FR RR RL luôn").

**Method:** `fact-check` workflow (`.claude/workflows/fact-check.js`), one Sonnet verify
agent per claim against primary sources; adversarial refute pass triggers only on
non-clean verdicts (none triggered — all 6 verdicts `correct`, confidence high).
Run `wf_238b8bff-db7`, 6 agents, ~248k subagent tokens.

## Verdicts

| # | Claim (as shipped on the slide) | Verdict | Key evidence |
|---|---|---|---|
| C1 | FL/FR/RL/RR = front-left / front-right / rear-left / rear-right corner zones | ✅ correct | Häckel et al., IEEE Trans. Veh. Tech. 2022 (arXiv:2201.00589), verbatim: "grouped into four zones based on their placement in the vehicle (Front-Left (FL), -Right (FR), Rear-Left (RL), -Right (RR))". Nuance: a convention, not a rule — real OEM designs use 2–6 zones (McKinsey/GSA 2023); Hirain uses L/R/F/T naming instead |
| C2 | DC = domain controller (powertrain/body/chassis/infotainment DC) | ✅ correct | bosch-mobility.com E/E-architecture page; nxp.com Domain Control; industry usage incl. "Domain Controller (DC) ECUs" |
| C3 | HPC = high-performance computer (central vehicle computer) | ✅ correct | **AUTOSAR primary source**: FO Release Overview R25-11 glossary adds "HPC (High performance computer/computing machine)"; Bosch vehicle-computer pages; Aumovio "High-Performance Computer (HPC)" |
| C4 | AV/AD = autonomous vehicle / automated driving | ✅ correct | NVIDIA DRIVE AV ("autonomous vehicle (AV) software platform"); Renesas & AVL pair "ADAS and Automated Driving (AD)". Nuance: "AV/AD" as a joined token is informal shorthand — each half is separately well-attested, the pair as one term is not standardized |
| C5 | OTA = over-the-air update (remote, vs wired garage connection) | ✅ correct | Standard usage everywhere; automotive sources explicitly contrast with the wired dealer/garage model |
| C6 | TSN = Time-Sensitive Networking, IEEE 802.1 standards for bounded-latency automotive Ethernet | ✅ correct | 1.ieee802.org/tsn ("set of standards specified by IEEE 802", "bounded latency"); IEEE P802.1DG = "TSN Profile for Automotive In-Vehicle Ethernet Communications" |

## Notes

- No refute pass ran (nothing non-clean to attack).
- C1's nuance is worth remembering if the diagram is ever generalized: four corner
  zones is the *teaching* topology; production zonal counts vary (2–6+) and some
  vendors name zones L/R/F/T. The slide presents FL/FR/RL/RR as labels on one example
  layout, which the sources support.
- C4: if anyone ever asks for a citation of "AV/AD" as a single standardized term,
  there isn't one — cite the halves separately.

## Sources (selection, full URLs in workflow output)

- arxiv.org/pdf/2201.00589 · standards.ieee.org (Visteon zonal deck, 802.3 ISAAC 2019)
- bosch-mobility.com/en/mobility-topics/ee-architecture · nxp.com/applications/DOMAIN-CONTROL
- autosar.org R25-11 `AUTOSAR_FO_TR_ReleaseOverview.pdf` (HPC abbreviation)
- renesas.com ADAS/AD · avl.com ADAS-and-AD · nvidia.com DRIVE AV
- 1.ieee802.org/tsn · 1.ieee802.org/tsn/802-1dg
