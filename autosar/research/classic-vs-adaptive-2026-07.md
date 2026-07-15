# AUTOSAR Classic vs Adaptive — one organization, two platforms, one vehicle (July 2026)

**What this is.** A single synthesis, for embedded/firmware engineers new to automotive
platforms, of how AUTOSAR's two platforms differ and how they coexist in a 2026 software-defined
vehicle. It merges two research notes — `autosar/research/notes/history-governance.md` (founding,
governance, releases, document landscape) and `autosar/research/notes/head-to-head-coexistence.md`
(the CP-vs-AP comparison, gateways, migration, ROS 2 positioning) — and cross-references the "Key
facts" tables of the eight sibling notes in `autosar/research/notes/`. Every external claim below
carries a source URL in the **Key claims** table; nothing is asserted without one. Where a note
hedged confidence or left something unverified, the hedge is preserved and pushed to **Open
questions** rather than upgraded to a bald fact. Two binding constraint files —
`notes/repo-constraints.md` and `notes/orchestrator-verification.md` — win over any research note
they conflict with, and their pinned facts (DDS-on-Classic in R25-11, the removed-spec list, the
Orin=AURIX / Thor=RH850 safety-MCU split, the "DoIP = only *standardized* transport" phrasing) are
carried through verbatim. Latest verified standard release: **AUTOSAR R25-11**, published
2025-11-27, internally R4.11.0.

A note on mental models before we start. If you come from MCU/RTOS/CAN work, the cleanest way in
is this: **AUTOSAR Classic is the world you already half-know** — a statically-configured RTOS
stack, everything fixed at build time, no heap in the safety paths, signals on a bus. **AUTOSAR
Adaptive is what happens when the "big chip" on the board runs Linux or QNX** and you want an
app-store deployment model with services discovered at runtime. They are not competitors; they are
the reflex spinal cord and the cortex of the same vehicle.

## 1. One organization, three standards

AUTOSAR (AUTomotive Open System ARchitecture) is a worldwide development partnership, not a
company and not a single document. Initial discussions on "the common challenge and objectives"
were held in **2002** by BMW, Bosch, Continental, DaimlerChrysler and Volkswagen (kick-off workshop
August 2002), "joined soon afterwards by Siemens VDO." The **Initial AUTOSAR Development Agreement**
was signed by the Core Partners in **July 2003**, and AUTOSAR was announced publicly in **September
2003 at the VDI Conference in Baden-Baden**. The founding circle then grew: **Ford** joined
November 2003; **Peugeot Citroën (PSA)** and **Toyota** in December 2003; **General Motors** in
November 2004. In February 2008 Siemens VDO was absorbed into Continental and ceased to be a
self-contained Core Partner. Registered address: Hörgertshausen, Germany.

**Governance** is layered, and Core Partners sit at the top of every layer: an **Executive Board**
(top governance), a **Steering Committee** (strategic management, reserved to Core Partners), a
**Project Leader Team** (technical steering, open to Core Partners plus Premium Partner Plus), and
the **Working Groups** where the actual standardization happens — R25-11 involved "more than 200
AUTOSAR partners across 20 working groups." For a firmware engineer the analogy is a large
open-source foundation with a paid steering committee: the specs are public, but who *decides* is a
small circle.

**Membership tiers and headcount.** The Introduction deck lists **eight partnership types** with
published fees and mandatory FTE contributions — Premium Partner Plus (€90,000/yr, 5 FTE + 1
project-leader FTE), Premium (€31,000, 1.5 FTE), Development (€10,000, 0.5 FTE), Associate
(€21,000), Associate [Light] (free), Attendee (free), Subscriber (€3,000), plus the **Core
Partner** governance tier (~10 companies that own and steer the partnership). The current deck sums
to **~360 total partners** (official Jan 2025 snapshot), and the striking shape is regional:
**Asia 174 > Europe 140** > North America 41 > Africa 5 — AUTOSAR is no longer Europe-centric by
headcount. (Consistent with AUTOSAR's own "350+ / more than 360 partners" site language; a
historical chart in the same deck peaks near 366 — see Open questions.)

**January 2026 core-partner refresh.** DENSO, Huawei Technologies and Vector Informatik were
promoted to **Core Partner** (announced 15 January 2026); DENSO had been a Premium Partner since
2004. Meanwhile "Continental" now appears in the core list as **AUMOVIO**, the spun-off automotive-
electronics business. Two founding-era OEMs, **Ford and PSA/Stellantis, are no longer shown as Core
Partners** — the core has tilted toward Tier-1 suppliers (Bosch, DENSO, Vector) and Asian players
(Toyota, Huawei). The current best-guess Core roster (10): AUMOVIO, BMW, Bosch, DENSO, GM, Huawei,
Mercedes-Benz, Toyota, Vector, VW.

**The FO / CP / AP structure.** AUTOSAR publishes one *standard set* with three members:

- **Foundation (FO)** — the cross-platform glue: common requirements, the meta-model and single XML
  schema, methodology, and shared wire protocols (SOME/IP, time-sync, DoIP, E2E, SecOC). Foundation
  is what "enforces interoperability between the AUTOSAR platforms" and lets a CP ECU and an AP
  machine live in one vehicle project.
- **Classic Platform (CP)** — statically-configured, real-time, OSEK-heritage stack for deeply
  embedded microcontrollers. First released 1.0 in 2005.
- **Adaptive Platform (AP)** — POSIX-based, service-oriented, dynamically-deployed stack for
  high-performance compute. First released 17-03 (March 2017).

**Document types.** Every spec filename is `AUTOSAR_<PLATFORM>_<TYPE>_<Name>.pdf` and every
requirement ID is `[<TYPE>_<Module>_<nnnn>]`. The prefixes you will meet: **EXP** (Explanatory —
background/rationale), **TR** (Technical Report — methodology, release overviews), **RS**
(Requirements Specification — "Requirements on …"), **SRS** (older CP software requirements),
**SWS** (Software Specification — the detailed, testable module spec, e.g. `SWS_CanIf`), **TPS**
(Template Specification — the meta-model templates), **PRS** (Protocol Requirements Spec — wire
protocols). The spectrum runs from high-level (EXP, TR) down to fine-grained (SWS, TPS, PRS).

**Read-free, license-to-build.** Every AUTOSAR PDF is downloadable without a login (these notes
were built by fetching the CP/AP/FO PDFs directly). The legal line is in each disclaimer: the work
may be reproduced "for informational purposes only," but "the commercial exploitation of the
material … requires a license." Free to read and study; a partnership/license is required to build
and sell products.

**Release timeline.** The naming is a common source of confusion, so here is the whole arc:

| Era | Releases | Notes |
|---|---|---|
| CP standalone | 1.0 (May 2005) → 4.0 (Dec 2009) → 4.2.1 (Oct 2014) → **4.4.0 (Oct 2018)** | `4.2.1` is where the standardized SOME/IP Transformer landed — CP had Ethernet SOA years before AP existed |
| AP standalone | **17-03 (Mar 2017, first AP)** → 18-03 → **19-03 (Mar 2019, last standalone)** | DDS network binding arrived at **R18-03** (Apr 2018), not 18-10 |
| FO standalone | **R1.0.0 (Oct 2016, first Foundation)** → 1.5.1 (Mar 2019) | Foundation carries the shared meta-model |
| Unified `R{yy}-11` | R19-11 → R24-11 → **R25-11** (2025-11-27, internal **R4.11.0**, schema AUTOSAR_00054) | one release, one schema, all three standards, once a year in November |

The **R19-11 unification** (November 2019) changed three things at once: the *naming* (dropping CP's
`4.x.y` and AP's `yy-mm` for a common annual `R{yy}-11` label), the *cadence* (one synchronized
November release), and the *schema* (a single `AUTOSAR_000nn` meta-model usable across CP and AP).
Crucially, the **CP internal version line never reset** — R25-11 is internally R4.11.0, so
"AUTOSAR 4.x" is still alive under the marketing name. Anyone who thinks 4.4.0 was "the end of
Classic" has misread the naming change.

## 2. The head-to-head — twelve dimensions

Every row here is sourced in the Key claims table. The one-line summary: **CP is a static C RTOS
stack on an MCU; AP is a dynamic C++ service platform on a POSIX SoC.**

| Dimension | Classic Platform (CP) | Adaptive Platform (AP) |
|---|---|---|
| **OS / kernel model** | AUTOSAR OS — a backward-compatible *superset* of OSEK OS (fixed-priority tasks, scalability classes SC1–SC4, no MMU required) | Not a new OS: an **OS Interface** on POSIX **PSE51** (single-process profile, IEEE 1003.13) over Linux/QNX/PikeOS; the AP OS itself must provide multi-process POSIX |
| **Language & API** | C; RTE-generated `Rte_Read/Write/Call` APIs | C++14 (historical ARA baseline; C++17 via MISRA C++:2023 merge); `ara::*` runtime |
| **Configuration time** | Fully static: everything fixed pre-build via ECU config (ECUC), code-generated to one binary | Dynamic: manifests bound late; service discovery and app start/stop at **runtime** |
| **Communication paradigm** | **Signal**-oriented — COM packs signals into I-PDUs on CAN/LIN/FlexRay/Ethernet | **Service**-oriented — `ara::com` Proxy/Skeleton over **SOME/IP or DDS** |
| **Scheduling & determinism** | Static priority table; hard real-time by construction | POSIX `SCHED_FIFO`/`SCHED_RR` (standard), optional `SCHED_DEADLINE` (EDF); determinism is *engineered*, not free |
| **Memory model** | Static allocation; MPU-protected partitions; **no heap in safety paths** | **Dynamic allocation is allowed and assumed** (C++/STL); safety needs deterministic allocators |
| **Safety / certification** | Mature ISO 26262 up to **ASIL D**; decades of field use (first ASIL-D AUTOSAR impl certified 2016) | Documented "up to ASIL D," but harder in practice; **ASIL-B shipping/certified, ASIL-D programs underway** |
| **Update granularity** | Reflash the **whole ECU** via bootloader/UDS (0x34/0x36/0x37) | **UCM**: install/update/remove individual Software Clusters; functional-group granularity; OTA-native |
| **Diagnostics** | **DCM + DEM** implementing UDS (ISO 14229) over DoCAN/DoIP | **DM** (`ara::diag`) — a UDS server *and* SOVD server; UDS over **DoIP (only standardized transport; custom permitted)** |
| **Tooling & licence** | Vector MICROSAR / EB tresos / ETAS RTA-CAR; DaVinci Configurator; per-ECU seat + runtime licences | Vector MICROSAR Adaptive / EB corbos / ETAS RTA-VRTE / Qorix / Apex — HPC-class stacks |
| **Target silicon** | Microcontrollers: Infineon AURIX, NXP S32K, Renesas RH850 | Microprocessors/SoCs: NVIDIA Orin/Thor, Qualcomm, NXP S32G/S32N, Renesas R-Car |
| **Typical use** | Brakes, EPS, body, powertrain — ASIL B–D actuator/safety functions | ADAS/AD, HPC gateways, infotainment — QM–ASIL D compute, often mixed-criticality with a CP safety island |

Two nuances the firmware reader should not skip.

**The "up to ASIL D" trap.** The peer comparison paper (arXiv 2109.00099, Table 1) lists **both**
platforms as "Up to ASIL D." On paper, Adaptive is *not* a low-ASIL toy. In practice, AP ASIL-D is
achieved through mixed-criticality partitioning and a CP/lockstep safety companion, not by the
Linux/QNX host alone. Real-world evidence as of mid-2026: Vector MICROSAR Adaptive Safe ships
**ASIL-B** (first series projects), with ASIL-D "planned for 2026"; Qorix received TÜV SÜD **ASIL-B**
certification (Aug 2025); ETAS RTA-VRTE received TÜV SÜD **ASIL-B** (~March 2025). No fully-certified
ASIL-D AP *middleware* was found — hence "ASIL-B shipping, ASIL-D underway," not "AP is ASIL-D."

**The dynamic-memory reflex.** Every MISRA-C firmware engineer carries a "no `malloc` in safety
code" reflex. AUTOSAR's own architecture-decisions document says the *opposite* for AP: "the use of
dynamic memory allocation by Adaptive Applications and Functional Clusters is **allowed and
assumed**." It also names the cost — dynamic allocation "can cause non-deterministic behavior …
fragmentation and non-deterministic allocation/de-allocation processing time." AUTOSAR's answer is
not to ban the heap but to require **deterministic allocators** that replace `malloc/free` in
critical phases. This is one of the biggest culture-shocks moving from CP to AP.

## 3. Coexistence in one 2026 vehicle

A modern software-defined vehicle runs **both platforms at once**. The recurring pattern is: **CP
for the reflex nervous system, AP for the brain, Ethernet + gateways for the spine.** Zonal and
actuator ECUs run Classic, wired by CAN/LIN/FlexRay; central high-performance computers (HPCs) run
Adaptive on Linux/QNX, talking SOME/IP or DDS over automotive Ethernet.

**The signal↔service (S2S) gateway** is the single most important coexistence mechanism. A CP ECU
speaks *signals* (fixed byte layouts in PDUs); an AP node speaks *services* (typed events, methods
and fields discovered at runtime). An S2S gateway subscribes to Classic COM signals, repackages
them, and offers them as SOME/IP services (and vice-versa), "acting like a remote SOME/IP node" to
the daemon. Products that implement this in real vehicles: **Vector MICROSAR** (S2S add-on;
MICROSAR Classic and Adaptive interoperate over SOME/IP-SD), **Elektrobit** (EB tresos on CP + EB
corbos on AP), and **ETAS** (RTA-CAR + RTA-VRTE). For a firmware engineer: think of S2S as a
protocol-translating gateway ECU, except the translation is signal-frame ⇄ service-object rather
than CAN ⇄ LIN.

**Diagnostics routing across the split.** UDS (ISO 14229) is the one diagnostic language both
platforms speak. On Classic it runs through **DCM + DEM** over **DoCAN** (CanTp, ISO 15765-2) on
legacy CAN branches or **DoIP** (ISO 13400) on Ethernet. On Adaptive the **Diagnostic Manager**
(`ara::diag`) is "a diagnostic server implementation that realizes a UDS server instance according
to ISO 14229-1 and SOVD according to ASAM." Per the binding constraint file, the correct phrasing
for AP transport is: **DoIP (ISO 13400-2) is the only *standardized* UDS transport for the AP
Diagnostic Manager; the SWS explicitly permits a custom transport implementation** (unchanged
through R24-11 and R25-11). Do not write bare "DoIP-only" without the word "standardized" nearby,
and do not repeat the refuted web claim that "R24-11 added CAN transport to Adaptive DM" — that was
a hallucination; DoIP-only is verbatim-unchanged across R22-11/R23-11/R24-11. A central gateway
ECU routes DoIP from the Ethernet backbone down to DoCAN on the legacy CAN branches, and external
links terminate at a TCU/gateway (raw UDS is never exposed to the internet — SOVD is the intended
external-facing API).

**The OEM "wrap" pattern.** OEMs increasingly adopt AUTOSAR *selectively* inside a proprietary base
layer rather than shipping an off-the-shelf platform. The canonical case is **Mercedes-Benz MB.OS**,
whose Base Layer middleware was co-developed with **Vector** and is "based on AUTOSAR Adaptive and
Classic and the AUTOSAR Runtime Environment." AUTOSAR here is an *ingredient*, not the platform.
Volkswagen Group's **E³** architecture (E3 1.1 on MEB EVs, E3 1.2 on PPE) with CARIAD software is
**domain-controller-based today** (E3 1.1 = three domain controllers ICAS1–3; E3 1.2 = five
function-organized HPCs) — Classic on the domain/safety ECUs, Adaptive/Linux on the compute
domains. VW Group's **zonal + central-AP** shape is reserved for the next-generation **SSP / E3 2.0**
and a *separate* China-specific zonal program (the CEA, co-developed with XPeng) — both still
upcoming, not the shipping E3 1.1/1.2 generation. BMW publicly runs an HPC+zonal split with
Adaptive on the compute cluster, but the precise CP/AP/vendor breakdown is not clearly documented
(Open questions).

**Where Classic vs Adaptive physically live — the NVIDIA example.** On an NVIDIA DRIVE board the
split is concrete and repo-verified. Classic lives on the **companion/safety MCU**, and the two
generations use *different* silicon: **Orin generation → Infineon AURIX TC397X** (Vector AUTOSAR
firmware, "AFW"); **Thor generation → Renesas RH850U2A16** (DriveOS 7.0.3 flash artifact
`…AFW-RH850-U2A16-…hex`, Vector MICROSAR Classic as the reference integration). Never say Thor uses
AURIX — that is a refuted guess. Adaptive runs on the Thor SoC *beside* the OEM AV apps, as a
Tier-1 layer (Vector/EB), not NVIDIA IP — NVIDIA's "full support of Adaptive AUTOSAR" is a
compatibility claim, not a shipped stack. The SoC↔MCU link is a proprietary "Common Interface over
UDP over Ethernet," not DoIP, and the Thor hypervisor does **not** host "virtual Classic AUTOSAR
ECU" partitions (single-guest SDK limit).

## 4. Convergence signals — the two worlds are moving toward each other

The old dichotomy "signals = Classic, services = Adaptive; CAN = Classic, Ethernet = Adaptive" is
now outdated *at the standard level*. Several R25-11-era moves close the gap:

**DDS on the Classic Platform (new in R25-11).** This is the headline. The CP Release Overview
§2.1.1.5 "DDS Support on Classic Platform" states: "Management functionalities for Events, Methods,
and Fields, previously available through SOME/IP, are now extended to DDS, offering increased
flexibility thanks to its native capability of defining Quality of Service (QoS) parameters at
various levels." It ships a "new BSW module **DDS Transformer**," "full support of
ClientServerInterface," and "integration of the OMG **SPDP** and **SEDP** discovery protocols, along
with the Service Discovery protocol already defined in the AUTOSAR Adaptive Platform, thus ensuring
cross-solution compatibility." **Hedge to preserve:** this is a *standard-level concept new in
R25-11*; no shipping vendor implementation was verified, and adoption timelines by Vector/EB/ETAS
are unconfirmed. It means a CP ECU can, in principle, join the same DDS databus that AP and ROS 2
already use.

**Dynamic memory, blessed on purpose.** AUTOSAR's own FO Explanation of SW Architectural Decisions
frames dynamic allocation as an intentional AP design choice (§2 above) — the standard is telling
firmware engineers that the heap is permitted on the compute side, provided determinism is
engineered back in. This is a philosophical convergence with the C++ application world, not the
embedded-C world.

**MISRA C++:2023 merge.** The standalone "AUTOSAR C++14 Guidelines" document was removed from the
standard set (404 since R23-11; last present in R22-11) and merged into **MISRA C++:2023**, which
targets **C++17** — "MISRA merging the AUTOSAR guidelines with its own established best practice"
into a single language subset. C++14 remains the historical ARA API baseline; **whether R25-11
formally moves the ARA APIs to C++17 is an open question**, kept as one.

**SOVD as the external-facing diagnostic API.** ASAM's Service-Oriented Vehicle Diagnostics — now
**ISO 17978-3** (HTTP/REST + JSON + OAuth) — has been adopted into AP as `AP_EXP_SOVD`, and the DM
"also aims on natively supporting SOVD and therefore acts as an SOVD server." SOVD is
self-describing ("no need for ODX-based interpretation," "UDS as a subset") and can front legacy
ECUs via ODX-based SOVD→UDS translation. R25-11 cites ISO 17978-3:2026 / ASAM SOVD 1.1 but notes
1.1 "is not yet (fully) supported."

**Eclipse S-CORE and the open-source SDV stack.** Launched 2025-06-12 as "the automotive industry's
first open-source core stack," S-CORE has a founding roster spanning BMW, Mercedes, Bosch, ETAS,
Vector, VW, ZF, Qualcomm, QNX and Red Hat, aims at certifiable ISO 26262 / ISO 21434 middleware, is
dual-language (C++ and Rust), and is cooperating with AUTOSAR on a reference implementation — while AUTOSAR AP is
"still debating Rust." This is a signal that even AUTOSAR's own core partners are hedging into open
source.

## 5. AUTOSAR vs ROS 2 for this repo's team

ROS 2 sits **next to**, not inside, the AUTOSAR world. The two share the **DDS wire family** (ROS
2's default RMW is DDS — Fast DDS / Cyclone DDS; AP supports DDS as an `ara::com` binding since
R18-03) but they are **not plug-compatible**: integration goes through **bridges**, not naive
DDS-to-DDS.

**Positioning: prototyping/R&D vs production platform.** Apex.AI frames it cleanly — "ROS 2 has
taken a code-first approach to make it as easy as possible to develop new applications," while
"AUTOSAR has a strong focus and successful history in creating interoperability between suppliers
and OEMs." Peer sources converge: ROS 2 excels in research and prototyping; AP dominates certified
production. A 2026 arXiv comparison (Hegerath et al.) finds ROS 2 "lacks hard real-time guarantees
needed for safety-critical systems" and "lacks several concepts essential for series-production
automotive systems" (operation modes, allocation control, watchdog supervision), while AP is
production-oriented. A Nov-2025 arXiv paper proposes an explicit **AP↔ROS 2 collaboration
framework** with DDS as the common layer and gateway solutions for message routing.

**Why bridges, not direct interop.** Even though both speak DDS/RTPS on the wire, the type systems,
service semantics and discovery differ, so practical interop uses **SOME/IP-DDS bridges** or
ROS2-SOME/IP bridges. Apex.AI ships "connectors for communication protocols, including SOME/IP,
CAN, and MQTT," letting ROS 2 data reach "AUTOSAR Adaptive applications using `ara::com` or in
AUTOSAR Classic RTE." One genuinely shared building block is **iceoryx** — a low-level zero-copy
shared-memory IPC ("plumbing") that higher layers wrap: it sits *under* both ROS 2 (via the
`rmw_iceoryx` binding) and some `ara::com` implementations, rather than being either API itself.
(A 2020-era FOSDEM talk called it "fully compatible with the ROS 2 and Adaptive AUTOSAR APIs," but
iceoryx's own current docs use a narrower framing.) It is the same local transport under both stacks.

**The safe-C++ playbook converges.** The production-hardened ROS 2 derivative is **Apex.Grace**
(formerly Apex.OS), "certified by TÜV Nord as a Safety Element out of Context (SEooC) up to ASIL D
according to the ISO 26262 standard," with **Apex.Ida** as its DDS-based communication layer.
Apex.Grace enforces static memory pools and eliminates runtime dynamic allocation — mirroring
exactly the deterministic-allocator discipline AP prescribes for C++. The flagship open AD stack on
ROS 2 is **Autoware** (Tier IV / Autoware Foundation).

**What an embedded team should take from each.** From CP: the static-config, no-heap, MPU-partition,
E2E/SecOC discipline is the same functional-safety mindset you already use on MCUs — AUTOSAR just
formalizes it. From AP: the service-oriented, manifest-driven, OTA-updatable model is where the
"big chip" is going, and its DDS binding is the bridge to the ROS 2 knowledge this repo already
teaches. Learn CP to understand *why* automotive safety code looks the way it does; learn AP (and
ROS 2) to understand where the compute side is heading.

## 6. Migration reality — moving one function CP → AP

Moving a function (say body-comfort logic or ADAS pre-processing) from a Classic ECU to an Adaptive
HPC is **not a recompile — it is a re-architecting**:

1. **Re-express the interface** from signals/PDUs to a **service interface** (events/methods/fields)
   — new ARXML `ServiceInterface` and manifests instead of COM signal definitions.
2. **Rewrite the code** from C/RTE calls (`Rte_Read/Write`) to C++ `ara::com` proxies/skeletons.
3. **Add manifests** (Execution, Service Instance, Machine) for late binding, plus **UCM Software
   Cluster** packaging for OTA deployment instead of a full-ECU flash.
4. **Insert an S2S gateway** so the migrated service still reaches the CP ECUs that expected the old
   signals.
5. **Re-do the safety case** — dynamic memory, POSIX scheduling and mixed-criticality partitioning
   must be argued afresh; deterministic allocators replace `malloc/free` in critical phases.

**No public artifact-level OEM case study was located.** Vendor whitepapers describe the pattern
(e.g. "Transitioning from AUTOSAR Classic to Adaptive for Service-Based Architectures"), but a
public case study listing concrete ARXML/manifest artifacts and engineering effort was not found —
this stays an open question.

**Folklore discipline.** The claim "**Tesla uses no AUTOSAR**" is common folklore with **no primary
source**; Tesla's stack is largely proprietary Linux-based, but a categorical "zero AUTOSAR" claim
is unverified and stays folklore, not fact. Likewise the refuted items from `repo-constraints.md`
§2 — "UDS 0x2A periodic reads = the fleet telemetry channel," "cloud talks DoIP+UDS directly to the
vehicle," "Classic = CAN-only / Adaptive = Ethernet-only," "Thor hypervisor hosts virtual Classic
ECU partitions," "Thor is the fleet's UDS/DoIP gateway," "UCM = Update Configuration Management,"
"Classic OS = OSEK/VDX" — must never be resurrected in any new module.

## Key claims

| # | Claim | Source URL | Confidence |
|---|---|---|---|
| 1 | AUTOSAR founding discussions 2002 (BMW, Bosch, Continental, DaimlerChrysler, VW; + Siemens VDO soon after); Development Agreement July 2003; public debut Sept 2003 Baden-Baden | https://www.autosar.org/about/history | high |
| 2 | Ford joined Nov 2003; PSA + Toyota Dec 2003; GM Nov 2004 | https://www.autosar.org/about/history + https://www.wardsauto.com/general-motors/gm-to-join-autosar | high |
| 3 | ~360 total partners (official Jan 2025 snapshot); Asia 174 > Europe 140 > NA 41 > Africa 5; eight membership tiers with published fees | https://www.autosar.org/fileadmin/user_upload/AUTOSAR_Introduction_PDF/AUTOSAR_EXP_Introduction_Part1.pdf | high |
| 4 | DENSO, Huawei, Vector promoted to Core Partner (announced 15.01.2026); Continental now shown as AUMOVIO; Ford/PSA no longer Core | https://www.autosar.org/news-events/detail/welcome-our-three-new-core-partners + https://www.autosar.org/about/partners/core-partner | high / med |
| 5 | AUTOSAR = FO + CP + AP; Foundation carries shared meta-model/schema to enforce cross-platform interoperability | https://en.wikipedia.org/wiki/AUTOSAR | high |
| 6 | Document types: EXP, TR, RS, SRS, SWS, TPS, PRS; filename `AUTOSAR_<PLATFORM>_<TYPE>_<Name>.pdf` | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_TPS_StandardizationTemplate.pdf | high |
| 7 | Specs free to read; commercial exploitation requires a license | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high |
| 8 | Latest release R25-11, published 2025-11-27, internally R4.11.0, schema AUTOSAR_00054, a minor release | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high |
| 9 | R19-11 unified naming + cadence + schema (separate until CP R4.4.0 / AP R19-03); CP internal version never reset | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high |
| 10 | First AP release = 17-03 (Mar 2017); first Foundation = R1.0.0 (Oct 2016); CP 1.0 = 2005 | https://www.autosar.org/about/history | high |
| 11 | CP OS = AUTOSAR OS, a superset of OSEK OS; scalability classes SC1–SC4 | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf (OSEK descent) | high / med |
| 12 | AP is not a new OS; defines an OS Interface on POSIX; AAs restricted to PSE51 single-process, AP OS provides multi-process POSIX | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf | high |
| 13 | AP scheduling: standard policies SCHED_FIFO/SCHED_RR, optional SCHED_DEADLINE (EDF) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf | high |
| 14 | CP = OSEK/C/signal/whole-ECU-update/up-to-ASIL-D; AP = POSIX/C++/service/per-app-update/up-to-ASIL-D | https://arxiv.org/pdf/2109.00099 | med |
| 15 | CP communication is signal-oriented (COM packs signals→I-PDU→PduR→CanIf); AP is service-oriented `ara::com` Proxy/Skeleton over SOME/IP or DDS | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 16 | AP dynamic memory allocation is "allowed and assumed"; non-determinism managed via deterministic allocators | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf | high |
| 17 | CP is fully static: no dynamic memory, no runtime task creation, single build-time binary | (teaching/vendor, per classic-safety-limits note) | med-high |
| 18 | CP first AUTOSAR impl certified ISO 26262 ASIL D (Vector MICROSAR Classic Safe, 2016) | https://www.vector.com/ (MICROSAR Classic Safe) | high |
| 19 | AP ASIL reality mid-2026: ASIL-B shipping/certified (Vector Adaptive Safe; Qorix TÜV SÜD Aug 2025; ETAS RTA-VRTE TÜV SÜD ~March 2025); no fully-certified ASIL-D AP middleware found | https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ + https://www.qorix.ai/press-release/ + https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ | high |
| 20 | CP diagnostics = DCM + DEM implementing UDS (ISO 14229) over DoCAN/DoIP | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf | high |
| 21 | AP DM realizes a UDS server (ISO 14229-1) and SOVD server (ASAM); DoIP is the only *standardized* UDS transport, custom transport permitted (R24-11 & R25-11) | https://www.autosar.org/fileadmin/standards/R25-11/AP/ (AP DM SWS) | high |
| 22 | AP UCM updates individual Software Clusters at functional-group granularity, OTA-native; UCM Master is now V-UCM (own SWS since R23-11) | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf | high |
| 23 | R25-11 adds DDS to Classic (DDS Transformer BSW module, OMG SPDP/SEDP + AP Service Discovery); standard-level concept, no shipping vendor impl verified | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high (standard) / adoption unverified |
| 24 | AUTOSAR C++14 Guidelines merged into MISRA C++:2023 (targets C++17); standalone doc gone (404 since R23-11) | https://en.wikipedia.org/wiki/AUTOSAR (news) | high |
| 25 | SOVD = ISO 17978-3 (HTTP/REST + JSON + OAuth), adopted into AP as AP_EXP_SOVD; DM acts as SOVD server; can front legacy ECUs via ODX-based SOVD→UDS | https://www.asam.net/standards/detail/sovd/ + https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf | high |
| 26 | AP DDS binding first appeared in R18-03 (Apr 2018); DDS is the same OMG family ROS 2 uses | https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds | high |
| 27 | Signal-to-service (S2S) gateways: Vector MICROSAR, EB tresos+corbos, ETAS RTA; gateway acts "like a remote SOME/IP node" | https://cdn.vector.com/cms/content/products/Adaptive_MICROSAR/Docs/MICROSAR_Adaptive_ProductCatalogue_EN.pdf | med |
| 28 | Mercedes MB.OS Base Layer co-developed with Vector, based on AUTOSAR Adaptive + Classic + RTE (selective adoption) | https://www.vector.com/us/en/news/news/mercedes-benz-mbos-base-layer/ | high |
| 29 | VW E3 1.1 (MEB) = domain controllers ICAS1–3 / E3 1.2 (PPE) = five function-organized HPCs (domain-based today), CARIAD software; zonal + central-AP is the next-gen SSP/E3 2.0 plus a separate China CEA (co-developed with XPeng) | https://www.volkswagen-group.com/en/articles/smart-vehicles-at-china-speed | med |
| 30 | NVIDIA safety-MCU split: Orin = Infineon AURIX TC397X (Vector AFW); Thor = Renesas RH850U2A16 (Vector MICROSAR Classic ref) | repo: research/automotive-stack-autosar-2026-07.md (DriveOS docs, repo-verified) | high |
| 31 | ROS 2 ↔ AP interop via bridges (SOME/IP-DDS), not naive DDS-to-DDS; iceoryx is a low-level zero-copy IPC that sits under both AP and ROS 2 via separate bindings, not directly either API | https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 | med-high |
| 32 | Apex.Grace certified by TÜV Nord as SEooC up to ASIL D (ISO 26262); ROS 2 API compatible; static memory pools | https://www.apex.ai/apexgrace + https://www.apex.ai/post/autosar-and-ros-2-for-software-defined-vehicle | high |
| 33 | 2026 arXiv: ROS 2 lacks hard real-time/determinism for safety-critical automotive; AP production-oriented | https://arxiv.org/pdf/2604.22576 | med |
| 34 | Nov-2025 arXiv proposes AP↔ROS 2 collaboration framework with DDS common layer + gateways | https://arxiv.org/pdf/2511.17540 | med |
| 35 | Eclipse S-CORE launched 2025-06-12 as first open-source SDV core stack; dual-language (C++ and Rust); cooperating with AUTOSAR | https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open | high |

## Sources

1. https://www.autosar.org/about/history — History of AUTOSAR (founding timeline, first releases) — AUTOSAR — primary
2. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf — Classic Platform Release Overview R25-11 (schema/release table, DDS on CP, disclaimer) — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf — Adaptive Platform Release Overview R25-11 (functional clusters, OSEK descent) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/user_upload/AUTOSAR_Introduction_PDF/AUTOSAR_EXP_Introduction_Part1.pdf — AUTOSAR Introduction Part 1 (tiers, fees, governance, ~360 partners) — AUTOSAR — primary
6. https://www.autosar.org/about/partners/core-partner — Core Partners page (current logos) — AUTOSAR — primary
7. https://www.autosar.org/news-events/detail/welcome-our-three-new-core-partners — Welcome our three new Core Partners! (2026-01-15) — AUTOSAR — primary
8. https://www.wardsauto.com/general-motors/gm-to-join-autosar — GM to Join Autosar — WardsAuto — secondary
9. https://www.autosar.org/fileadmin/user_upload/2025_12_18_AUTOSAR-PR_Release_Event.pdf — R25-11 Release Event PR (participation stats) — AUTOSAR — primary
10. https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf — Explanation of AP/CP SW Architectural Decisions R25-11 (dynamic memory) — AUTOSAR — primary
11. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf — AP SWS Operating System Interface R25-11 (PSE51, scheduling) — AUTOSAR — primary
12. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf — AP SWS Communication Management R25-11 (ara::com, SOME/IP, DDS) — AUTOSAR — primary
13. https://arxiv.org/pdf/2109.00099 — Comparison between AUTOSAR Platforms (Table 1) — arXiv — secondary/peer
14. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf — AP SWS Update and Configuration Management (UCM) — AUTOSAR — primary
15. https://www.elektrobit.com/products/ecu/eb-tresos/operating-systems/ — EB tresos OsekCore / Safety OS — Elektrobit — vendor
16. https://cdn.vector.com/cms/content/products/Adaptive_MICROSAR/Docs/MICROSAR_Adaptive_ProductCatalogue_EN.pdf — MICROSAR Adaptive (S2S) — Vector — vendor
17. https://www.vector.com/us/en/news/news/mercedes-benz-mbos-base-layer/ — Mercedes MB.OS Base Layer teamup — Vector — vendor
18. https://www.apex.ai/post/autosar-and-ros-2-for-software-defined-vehicle — AUTOSAR and ROS 2 for SDV — Apex.AI — vendor
19. https://www.apex.ai/apexgrace — Apex.Grace (ASIL-D SEooC) — Apex.AI — vendor
20. https://www.volkswagen-group.com/en/articles/smart-vehicles-at-china-speed — VW/XPENG CEA E/E architecture — Volkswagen Group — vendor/OEM
21. https://arxiv.org/pdf/2604.22576 — Comparison of ROS 2 and AP against automotive middleware requirements (Hegerath et al., 2026) — arXiv — secondary/peer
22. https://arxiv.org/pdf/2511.17540 — AUTOSAR AP and ROS 2 Collaboration Framework (Iwakami et al., 2025-11) — arXiv — secondary/peer
23. https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds — AUTOSAR AP 18.03 now with DDS — RTI — vendor
24. https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ — MICROSAR Adaptive Safe ASIL-B available, ASIL-D planned 2026 — Vector — vendor
25. https://www.qorix.ai/press-release/tuv-certified-qorix-is-one-of-the-few-providers-with-a-certified-adaptive-autosar-stack/ — Qorix TÜV SÜD ASIL-B Adaptive stack (Aug 2025) — Qorix — vendor
26. https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ — ETAS RTA-VRTE ISO 26262 ASIL-B TÜV SÜD (~March 2025) — ETAS — vendor
27. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf — CP SWS DCM (UDS/ISO 14229) — AUTOSAR — primary
28. https://www.asam.net/standards/detail/sovd/ — ASAM SOVD standard page — ASAM — primary
29. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf — Explanation of Service-Oriented Vehicle Diagnostics (AP) — AUTOSAR — primary
30. https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open — Eclipse S-CORE launch — Eclipse Foundation — primary/secondary
31. https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 — iceoryx as low-level zero-copy IPC under AP and ROS 2 — Apex.AI — vendor
32. https://en.wikipedia.org/wiki/AUTOSAR — AUTOSAR overview (Foundation purpose, OSEK, C++14/MISRA merge) — Wikipedia — secondary
33. repo: research/automotive-stack-autosar-2026-07.md — safety-MCU generations (Orin=AURIX, Thor=RH850), repo-verified against DriveOS docs — internal/primary-derived

## Open questions

- **Exact AP ASIL-D field evidence.** Sources state "up to ASIL D" as a design target; no specific
  production ECU was verified where the AP *host itself* (not a CP/lockstep companion) carries the
  ASIL-D claim. *Best guess (labelled): ASIL-D-relevant paths in production AP deployments are
  partitioned onto a safety island/hypervisor, with the Linux/QNX AP host at ASIL-B or QM.*
- **Whether R25-11 CP "DDS Transformer" is production-shipping or concept-stage.** The Release
  Overview describes it as an introduced concept; adoption timelines by Vector/EB/ETAS unverified.
- **Whether R25-11 formally moves the ARA APIs to C++17.** C++14 is the historical baseline; the
  guidelines merged into MISRA C++:2023 (C++17), but a formal ARA C++17 move is not confirmed.
- **Published, artifact-level CP→AP migration case study.** Vendor whitepapers describe the pattern;
  a public OEM case study listing concrete ARXML/manifest artifacts and effort was not located.
- **"Tesla uses no AUTOSAR."** Common folklore, no primary source. Tesla's stack is largely
  proprietary Linux-based, but a categorical "zero AUTOSAR" claim is unverified — folklore, not fact.
- **BMW stack attribution.** BMW publicly runs HPC+zonal; the precise CP/AP/vendor breakdown is not
  clearly documented in accessible primary sources.
- **Exact current Core Partner count and full roster.** Logo alt-tags gave 9–10 names; a clean text
  roster could not be loaded. *Best guess (labelled): 10 — AUMOVIO, BMW, Bosch, DENSO, GM, Huawei,
  Mercedes-Benz, Toyota, Vector, VW.*
- **The ~360 partner total is AUTOSAR's official Jan 2025 snapshot** (Asia 174 > Europe 140 > NA 41 >
  Africa 5), consistent with AUTOSAR's own "350+ / more than 360 partners" site language; a historical
  chart in the same deck peaks near 366. The R25-11 PR's "more than 200 partners" is a
  working-group participation metric, not total membership.
- **Whether the 2022 opening-strategy "university/startup" non-partner license actually launched**,
  and its terms. Status unverified. *Guess: still limited/experimental.*
- **AP Communication Management DDS binding maturity.** The R25-11 CM SWS confirms DDS is a binding,
  but the exact clause enumerating supported DDS QoS vs SOME/IP parity was not fetched.
- **Precise meaning of the `ASWS` prefix** seen in some CP filenames (likely "Auxiliary/Abstract
  Software Specification") — not confirmed from a primary definition.

*Fact-checked 2026-07-15 (workflow run wf_4748cedc-22d, 97 claims: 79 correct / 16 partially correct / 2 wrong — all corrected in place; full findings in autosar/research/notes/fact-check-findings-2026-07-15.md).*
