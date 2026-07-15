# Fact-check — 2026-07-15 — abbreviation keys (two runs) + deck-wide audit-text sweep

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
