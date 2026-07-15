# Repo constraints for a new AUTOSAR deck/module (mined 2026-07-15)

Scope: everything already claimed in this repo about AUTOSAR (Classic/Adaptive), UDS,
SOVD, SOME/IP, DoIP, DoCAN, and vehicle E/E architecture, so a new AUTOSAR module stays
consistent and doesn't re-derive or contradict already-fact-checked material.

## 1. Claims inventory

| Claim (verbatim-ish) | file:line | Status |
|---|---|---|
| AUTOSAR Classic = statically configured, OSEK-heritage stack for deeply embedded MCUs | research/automotive-stack-autosar-2026-07.md:22-25 | verified (also slides/research-deck.md:862-874) |
| AUTOSAR Adaptive = POSIX/C++ SoA platform (`ara::com`) for HPC ECUs | research/automotive-stack-autosar-2026-07.md:26-29 | verified |
| AUTOSAR Adaptive has DDS network binding **since R18-03** (not R18-10 — corrected folklore) | research/automotive-stack-autosar-2026-07.md:36,44 / claims-audit-2026-07.md:160 (A9) | verified — rti.com "status of DDS in AUTOSAR" |
| NVIDIA does NOT ship an AUTOSAR stack; "full support of Adaptive AUTOSAR" (2018 NVIDIA press release) = compatibility claim only; actual stacks from Tier-1s (Vector MICROSAR, EB corbos, TTTech MotionWise) | research/automotive-stack-autosar-2026-07.md:45 / claims-audit-2026-07.md:155 (A4) | verified |
| Safety MCU: Orin gen = Infineon AURIX TC397X w/ Vector AFW; **Thor gen = Renesas RH850U2A16**; IGX Thor = Renesas SMCU; Jetson Thor devkit has no safety MCU | research/automotive-stack-autosar-2026-07.md:12 | verified — DriveOS 6.0.9 MCU docs, DRIVE forum, IGX docs |
| Middleware: NvStreams is NVIDIA's; **SOME/IP and DDS arrive with AUTOSAR Adaptive**, not NVIDIA IP | research/automotive-stack-autosar-2026-07.md:15 | verified |
| UDS = ISO 14229, application-layer, transport-independent (OSI 5-7) | research/fleet-uds-autosar-2026-07.md:26 (row 1) / claims-audit F1 | verified |
| DoCAN = ISO 15765-2; DoIP = ISO 13400; UDSonIP = ISO 14229-5 | research/fleet-uds-autosar-2026-07.md:30 (row 5) / claims-audit F2 | verified |
| Adaptive DM (`ara::diag`) supports **DoIP only** as transport — re-verified against R22-11/R23-11/R24-11 SWS_Diagnostics PDFs, unchanged through R24-11; web claim "R24-11 added CAN" = hallucination | research/fleet-uds-autosar-2026-07.md:32 (row 7) — this repo's own currency-check addendum, see runbook commit d0fdab7 | verified (re-verified 2026-07-15) |
| UCM = "**Update and Configuration Management**" (not "Update Configuration Management") | research/fleet-uds-autosar-2026-07.md:34 (row 9) | verified — corrects external-draft error |
| UDS 0x34-0x37 is *one* Adaptive FOTA channel; native path = UCM `ara::com` TransferStart/Data/Exit fed by OTA client | research/fleet-uds-autosar-2026-07.md:35 (row 10) | verified |
| SOVD = now **ISO 17978-1/-2/-3:2026** (REST/HTTP+JSON+OAuth), complements UDS, can front legacy ECUs | research/fleet-uds-autosar-2026-07.md:36 (row 11) / claims-audit F6 | verified |
| **0x2A periodic reads ≠ fleet telemetry channel** — real but time-polled/session-scoped/0xF2xx-DID-limited; continuous telemetry = telematics pipelines (MQTT/proprietary) | research/fleet-uds-autosar-2026-07.md:37 (row 12) / claims-audit F7 | ❌ refuted (external-draft claim), see §2 |
| Cloud never talks DoIP/UDS directly to vehicle — TCU/gateway terminates and translates | research/fleet-uds-autosar-2026-07.md:38 (row 13) | ❌ refuted as drafted |
| ODX (ISO 22901-1, "Open Diagnostic data eXchange") / DEXT (AUTOSAR Diagnostic Extract) are formats; packaged file = PDX container | research/fleet-uds-autosar-2026-07.md:39 (row 14) | verified/corrected |
| Classic OS = **AUTOSAR OS**, a backward-compatible superset of OSEK OS (not "= OSEK/VDX") | research/fleet-uds-autosar-2026-07.md:41 (row 16) | verified/corrected |
| Classic has standardized **SOME/IP Transformer since AUTOSAR 4.2.1 (2016)** — predates Adaptive's first release (R17-03, March 2017); Classic also does Ethernet/DoIP/LIN/FlexRay | research/fleet-uds-autosar-2026-07.md:43 (row 18) / claims-audit F8 | ❌ refutes "Classic=CAN only, Adaptive=Ethernet only" framing |
| Thor hypervisor hosting multiple "virtual Classic AUTOSAR ECU" partitions | research/fleet-uds-autosar-2026-07.md:51 (row 26) | ❌ refuted — single-guest SDK limit; Classic lives on companion MCU (RH850) |
| AUTOSAR partners: EB + Vector confirmed w/ NVIDIA ties; **ETAS and Neusoft — no NVIDIA-specific tie found**, dropped | research/fleet-uds-autosar-2026-07.md:53 (row 28) / claims-audit F17 | scoped down |
| Thor as UDS/DoIP diagnostic gateway for fleet backend | research/fleet-uds-autosar-2026-07.md:54 (row 29) | ❌ refuted — zero documentation; SoC↔MCU link is proprietary "Common Interface over UDP over Ethernet", not DoIP |
| Thor: no multiple mixed guest VMs in public SDK ("Multiple Guest OS are not supported... QNX or Linux, but not both") | claims-audit-2026-07.md:185 (F12) | verified — re-fetched NVIDIA docs |
| MB.OS (Mercedes) built with Vector using AUTOSAR Adaptive + Classic selectively, not full off-the-shelf AP | claims-audit-2026-07.md:163 (A12) | partner-confirmed/secondary |
| Deck-shipped comparison table: Classic OS=AUTOSAR OS(OSEK superset,SC1-4) vs Adaptive OS=POSIX/PSE51; Comms: Classic=CAN/LIN/FlexRay+Ethernet/SOME-IP since 4.2.1 vs Adaptive=Ethernet-native SOME/IP+DDS binding; Diagnostics: Classic=DCM+DEM vs Adaptive=DM(`ara::diag`)DoIP-only; Updates: Classic=bootloader reflash(UDS 0x34/36/37) vs Adaptive=per-Software-Cluster via UCM | slides/research-deck.md:862-869 | verified (shipped) |
| Two persistent myths corrected in deck: "Classic can't do Ethernet" (false — SOME/IP since 4.2.1, 2016, a year before AP's first release R17-03/March 2017) and "Adaptive = low ASIL" (false — Vector MICROSAR Adaptive Safe ships ASIL-B; Wind River Adaptive safety concept TÜV SÜD-assessed ASIL-D-suitable 2019, program assessment not completed cert) | slides/research-deck.md:874 | verified (shipped) |
| E/E architecture evolution: 100+ ECUs (2000s-2010s, point-to-point CAN) → domain controllers (2015-2022) → zonal+central SDV (now); Bosch framing "distributed application software consolidated in a few powerful vehicle computers"; reported targets 100+ → under a dozen ECUs are **vendor figures, not a measurement** | slides/research-deck.md / slides/assets/sdv-ecu-consolidation.svg | verified (labeled explicitly as vendor claim, not measured) |
| FL/FR/RL/RR zonal naming = a convention (2-6 zones vary by OEM; Hirain uses different naming) | research/fact-check-2026-07-15.md C1 | verified with nuance |
| HPC = "high performance computer/computing machine" — confirmed via **AUTOSAR primary source** (FO Release Overview R25-11 glossary) | research/fact-check-2026-07-15.md C3 | verified |
| TSN = IEEE 802.1 Time-Sensitive Networking; IEEE P802.1DG = automotive in-vehicle profile | research/fact-check-2026-07-15.md C6 | verified |
| DriveOS 6.0's ASIL-D cert achieved on Orin; **Thor cert still in progress (as of July 2026)** | slides/assets/driveos-dualstack.svg | verified (shipped caveat) |

## 2. Refuted folklore to never repeat

These came from an externally produced draft report and were explicitly checked and
killed in `research/fleet-uds-autosar-2026-07.md`. A new AUTOSAR module must not
resurrect them:

1. **"UDS SID 0x2A periodic reads = the fleet telemetry channel to the cloud."**
   False. 0x2A is real, works over DoIP, but is time-polled, session-scoped, and
   DID-space-constrained (0xF2xx). Continuous fleet telemetry runs on telematics
   pipelines (MQTT/proprietary), not UDS. UDS stays a diagnostic protocol.
2. **"Cloud/backend talks DoIP+UDS (or 5G+UDS) directly to the vehicle."**
   False. Every real deployment terminates the external link at a TCU/gateway
   (TLS + certificates) which translates into in-vehicle UDS. Raw UDS is never
   exposed to the internet. SOVD is the intended external-facing API.
3. **"Classic AUTOSAR = CAN/DoCAN only; Adaptive = Ethernet/SOME-IP only."**
   False as a dichotomy. Classic has had a standardized SOME/IP Transformer since
   4.2.1 (2016) — a year before Adaptive's first release (R17-03, March 2017) —
   plus Ethernet, DoIP, LIN, FlexRay.
4. **"Thor's hypervisor hosts multiple 'virtual Classic AUTOSAR ECU' partitions
   (Body/Gateway, Powertrain)."** False. Contradicted by the single-guest SDK limit
   ("Multiple Guest OS are not supported ... QNX or Linux, but not both"). No
   NVIDIA/partner doc shows Classic as a Thor hypervisor guest. Classic lives on
   the companion MCU (Renesas RH850) — Vector confirms MICROSAR Classic as the
   reference integration there.
5. **"Thor acts as the fleet's UDS/DoIP diagnostic gateway."** False. Zero
   documentation. The documented SoC↔companion-MCU link is a proprietary "Common
   Interface over UDP over Ethernet," not DoIP/UDS. Gateway/UDS routing is a
   separate gateway-ECU / companion-MCU function.
6. **"UCM = Update Configuration Management."** Wrong expansion — it's "Update
   *and* Configuration Management" (AUTOSAR's own doc title).
7. **"Classic OS = OSEK/VDX."** Imprecise — Classic runs AUTOSAR OS, a
   backward-compatible *superset* of OSEK OS (adds memory/timing protection,
   multicore, scalability classes SC1-4).
8. **"ETAS and Neusoft are NVIDIA AUTOSAR ecosystem partners."** No
   NVIDIA-specific tie found for either; only Elektrobit and Vector are confirmed.
9. **Web-search summary claiming "R24-11 added CAN transport to Adaptive DM."**
   Hallucination — re-verified against primary SWS_Diagnostics PDFs for R22-11,
   R23-11, R24-11: DoIP-only is unchanged verbatim across all three; the
   "upcoming releases will also detail CAN, CAN-FD, FR" sentence remains a
   forward-looking statement, not fulfilled by R24-11.

## 3. Reusable diagrams

All nine SVGs already exist under `slides/assets/` (drawio sources mirrored in
`slides/assets/drawio-pages/*.xml` and consolidated in `slides/diagrams.drawio`).

- **stack-autosar-classic.svg** — "AUTOSAR Classic — the layered stack on one deeply
  embedded ECU." Layers: Application (SWCs) → RTE → BSW (AUTOSAR OS, COM, NvM, WdgM,
  DCM/DEM diagnostics) → ECU Abstraction → MCAL → Microcontroller (RH850/AURIX/S32K),
  plus CDD bypass lane. Notes: one binary/one ECU/hard RT, ARXML build-time config.
  Reuse: canonical "what is Classic" slide for a new deck; the DCM/DEM box is the
  hook into a UDS-focused module.
- **stack-autosar-adaptive.svg** — "AUTOSAR Adaptive — a POSIX service-oriented
  platform, not an OS." Adaptive Applications (C++14, Software Clusters) → ARA
  (`ara::com` SOME/IP+DDS binding, `ara::diag` DM/UDS-over-DoIP, `ara::ucm`,
  `ara::exec`, `ara::per`, `ara::log`) → POSIX OS (QNX/Linux, PSE51) →
  High-performance SoC (Thor-class). Notes: service discovery pinned in
  production, ASIL-B shipping/ASIL-D underway. Reuse: canonical "what is Adaptive"
  slide; directly reusable for an ara::diag/UDS-over-DoIP explainer.
- **stack-automotive.svg** — "The automotive software stack — 2026 (DRIVE Thor)."
  Full vertical: cloud loop (DGX/Omniverse/Cosmos) → OEM AV stack + AUTOSAR
  Adaptive apps (Tier-1, not NVIDIA IP) → DriveWorks SDK → service middleware
  (NvStreams/SOME-IP/DDS) → DriveOS 7 hypervisor (QNX safety VM + Linux AI VM) →
  Thor SoC → in-vehicle network (Ethernet backbone + CAN-FD/LIN/FlexRay legacy) →
  Vehicle ECUs (AUTOSAR Classic land, safety MCU AURIX→RH850, Vector AFW). Reuse:
  master orientation diagram — where AUTOSAR Classic vs Adaptive physically sit
  relative to NVIDIA's own stack; good deck-opener for an AUTOSAR module scoped to
  "how it fits with the rest of the vehicle compute."
- **sdv-ecu-consolidation.svg** — "E/E architecture evolution — why fleet
  management got easier." Three eras: distributed (100+ ECUs, point-to-point CAN,
  OBD-plug diagnostics) → domain controllers (powertrain/body/chassis/infotainment
  DC, gateways) → zonal+central SDV (central HPC: AV/AD, Adaptive AUTOSAR, OTA;
  Ethernet/TSN backbone; zonal ECUs FL/FR/RL/RR). Includes explicit "vendor
  figures, not a measurement" caveat on the 100+→<12 ECU claim. Reuse: motivates
  *why* AUTOSAR Adaptive/consolidation matters for fleets; good scene-setter before
  diving into Classic-vs-Adaptive detail.
- **uds-diag-stack.svg** — "UDS (ISO 14229) — one diagnostic language, two
  transports, two platforms." Diagnostic client → UDS services (0x10/0x27/0x22/
  0x19/0x31/0x34-37) → DoCAN (CanTp, ISO 15765-2) vs DoIP (ISO 13400) →
  Classic AUTOSAR ECU (DCM+DEM) vs Adaptive AUTOSAR machine (DM `ara::diag`,
  DoIP-only, one server per Software Cluster). Reuse: the canonical UDS-protocol
  slide; directly reusable as-is for a UDS-focused section of the new module.
- **fleet-uds-flow.svg** — "Fleet diagnostics end-to-end — where UDS really lives
  (2026)." Fleet backend (telemetry DB, OTA campaigns) → SOVD (REST/HTTP+JSON,
  ISO 17978:2026, "raw UDS NOT exposed to internet") + telematics (MQTT) → vehicle
  TCU (4G/5G+TLS) → central gateway (DoIP gateway/firewall, security chokepoint) →
  Ethernet backbone (DoIP/UDS+SOME-IP) / CAN branches (CanTp/UDS) → HPC (Adaptive
  DM+UCM) and zonal/legacy ECUs (Classic DCM+DEM). Reuse: the "how a fleet actually
  reaches a vehicle" diagram — pairs with the refuted-folklore section (§2 items
  1-2, 5) as the corrective picture.
- **dds-scope.svg** — "What DDS actually connects — and where it stops." Shows
  intra-process/same-machine/cross-machine DDS scope, "below this line: no DDS"
  (MCU/fieldbus: EtherCAT, CAN-FD), the micro-ROS XRCE-DDS bridge, and an
  **automotive mirror** note: "on Thor the same role is played by in-guest
  middleware (NvStreams · ara::com — SOME/IP or DDS binding); the DDS wire family
  is what AUTOSAR Adaptive shares with ROS 2 (binding since R18-03)." Reuse:
  bridges the existing ROS 2 content to the new AUTOSAR module — reuse this exact
  cross-reference rather than re-explaining DDS-vs-SOME/IP from scratch.
- **driveos-dualstack.svg** — "DriveOS 7 — how automotive splits the software."
  Safety VM (QNX OS for Safety, pre-certified ASIL-D) vs AI VM (Linux/CUDA/
  TensorRT/DriveWorks) under an NV Type-1 hypervisor on Thor silicon; explicit
  caveat "dual QNX+Linux = platform framing; public SDK runs one guest at a time —
  'QNX or Linux, but not both'"; also notes DriveOS 6.0 ASIL-D cert was on Orin,
  Thor cert still in progress (July 2026). Reuse: needed context if the new module
  discusses where Adaptive AUTOSAR's POSIX OS (QNX/Linux) actually runs.
- **fleet-on-thor.svg** — "Fleet management on DRIVE Thor — what's actually
  documented (2026)." The authoritative refutation diagram: fleet backend → TCU +
  central gateway (separate ECUs, "Thor has no documented fleet-gateway role") →
  DoIP/UDS in-vehicle network → Thor board (Guest OS VM: OEM AV stack + AUTOSAR
  Adaptive Tier-1 [DM `ara::diag`, UCM], DriveOS 7 hypervisor, FSI lockstep
  Cortex-R52) vs companion MCU (Renesas RH850, Vector MICROSAR Classic: DCM+DEM,
  "a real ECU, not a VM") linked by a "proprietary Common Interface (UDP over
  Ethernet) — not DoIP." Reuse: THE reference diagram for "where does AUTOSAR
  Classic vs Adaptive physically live on a Thor board" — reuse verbatim rather
  than redrawing; it already encodes every refuted claim from §2 as explicit
  negative labels.

## 4. Deck conventions (slides/research-deck.md)

- **Marp frontmatter**: `marp: true`, `paginate: true`, `theme: default`, with a
  `style: |` block defining global CSS (section font-size 26px, h1/h2 custom
  colors, table font-size 22px, code background tint).
- **Slide classes**: `<!-- _class: lead -->` for title/section-opener slides
  (large h1, lighter h2). `<!-- _class: diagram -->` (declared per-slide via a
  local `style` override, e.g. lines ~80,115,181,254) centers a single SVG/PNG at
  a fixed height (650px) with flex layout — this is the pattern to follow for any
  new AUTOSAR diagram slide.
- **`.gloss` footer pattern**: every content slide ends with
  `<div class="gloss">...</div>` — small-font (13-17px), top-bordered footnote
  block that expands every abbreviation used on that slide, sometimes with extra
  nuance/citation. Uses ` · ` (middle dot) as separator between entries. This is
  the mandated way to introduce any new acronym in the new module — never leave
  an acronym unexpanded inline.
- **Inline `.ok`/`.bad`/`.cmd` span classes** for terminal output and check/cross
  markers are available if the new module includes runnable demos.
- **Three-slide glossary pattern at the deck's end**: "Glossary 1/3", "2/3",
  "3/3" — Glossary 3/3 (`slides/research-deck.md:1281+`) is specifically
  "AUTOSAR & vehicle diagnostics" and already defines: SMCU/AFW, AUTOSAR CP/AP,
  `ara::com`, SOME/IP, E/E, ARXML, OSEK/VDX, AUTOSAR OS/SC1-4, ARA/`ara::`, UDS,
  SID, DoCAN/DoIP, DM/UCM, SOVD, ODX/DEXT/PDX, vECU. **A new AUTOSAR module should
  reuse/extend this exact glossary rather than duplicating a separate one.**
- **Sourcing footer convention**: each major section ends with a bullet list of
  primary sources (e.g. `slides/research-deck.md:1359,1369-1370`) pointing back at
  the specific `research/*.md` file that backs the section — the new module
  should point to `research/automotive-stack-autosar-2026-07.md` and
  `research/fleet-uds-autosar-2026-07.md` the same way.
- **Refutation-as-strikethrough convention**: killed claims are shown with
  Markdown strikethrough (`~~"claim text"~~`) followed by the correction, e.g.
  `slides/research-deck.md:941,943` — reuse this convention if the new module
  needs to show corrected folklore inline (though per CLAUDE.md/user preference,
  audit-process narration was later stripped from slides in favor of footnote
  `.gloss` annotations — see `research/fact-check-2026-07-15.md` Run 2 context:
  "user requested removing all audit-process narration from the slides and
  annotating abbreviations instead").
