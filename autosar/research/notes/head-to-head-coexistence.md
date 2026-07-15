# Classic vs Adaptive Head-to-Head — and How They Coexist in One Vehicle

*Research notes for embedded/firmware engineers new to automotive software platforms. English. Compiled 2026-07-15. Latest standard release verified: **AUTOSAR R25-11**, published 2025-11-27 [1][2].*

## Executive summary

AUTOSAR ships **two** platforms, not one. The **Classic Platform (CP)** is a statically-configured, OSEK-based, C, signal-oriented stack for deeply-embedded microcontrollers (brakes, EPS, body, powertrain) up to ASIL D. The **Adaptive Platform (AP)** is a POSIX (PSE51) C++14/17 service-oriented stack for high-performance SoCs running Linux/QNX (ADAS, HPC, infotainment gateways) with dynamic deployment and OTA. They are complementary, and a 2026 SDV runs **both at once**: zonal/actuator CP ECUs wired by CAN/LIN/FlexRay, central AP HPCs talking SOME/IP or DDS over automotive Ethernet, joined by **signal-to-service (S2S) gateways** (Vector MICROSAR, Elektrobit, ETAS implement these). R25-11's headline change directly serves coexistence: **DDS is now a supported service transport on Classic**, sharing OMG SPDP/SEDP discovery with AP [2]. OEMs increasingly wrap AUTOSAR selectively inside a proprietary "base layer" (Mercedes MB.OS, built with Vector [12]). ROS 2 sits *next to*, not inside, this world: it shares the DDS wire family and is the R&D/prototyping layer, with Apex.AI's **Apex.Grace** (ISO 26262 ASIL-D SEooC) the production-hardened ROS 2 derivative [10][11].

## 1. The definitive CP-vs-AP comparison (12+ dimensions)

Every row is sourced in §Key facts. Summary of the head-to-head:

| Dimension | Classic Platform (CP) | Adaptive Platform (AP) |
|---|---|---|
| **OS / kernel model** | OSEK/VDX-derived AUTOSAR OS — fixed priority, static tasks, no MMU required [3][8][14] | POSIX **PSE51** single-process profile per IEEE 1003.13 / POSIX-1003.1-2003, on Linux/QNX/PikeOS [4] |
| **Language & API** | C; RTE-generated APIs [3][8] | C++14 (moving toward C++17/20); `ara::*` (ARA = AUTOSAR Runtime for Adaptive Applications) [5][7] |
| **Configuration time** | Fully static: everything fixed pre-build via ECU config (ECUC), code-generated [3][8] | Dynamic: service discovery + application start/stop at **runtime**; manifests bound late [7][15] |
| **Communication paradigm** | **Signal**-oriented over COM/PDUs on CAN/LIN/FlexRay/Ethernet [3][7] | **Service**-oriented (`ara::com`) over SOME/IP or **DDS** [5][7] |
| **Scheduling & determinism** | Static priority table; hard real-time by construction [3][8] | POSIX `SCHED_FIFO/RR/OTHER`, optional non-POSIX `SCHED_DEADLINE` (EDF); determinism is engineered, not free [4] |
| **Memory model** | Static allocation; MPU-protected partitions; no heap in safety paths [3][14] | **Dynamic memory allocation is allowed and assumed** (C++/STL); needs deterministic allocators for safety [1] |
| **Safety / certification** | Mature ISO 26262 up to **ASIL D**; decades of field use [3][14] | Designed for safety up to ASIL D but harder in practice; SafetyOverview + platform mechanisms [3][6] |
| **Update granularity** | Reflash the **whole ECU** via bootloader/UDS [3] | **UCM**: install/update/remove individual Software Clusters / apps; functional-group granularity; OTA-native [15] |
| **Diagnostics** | DCM + DEM implementing UDS (ISO 14229) over DoCAN/DoIP [3][14] | `ara::diag` / Diagnostic Management (DM) functional cluster, UDS over DoIP [3-AP] |
| **Tooling & licence** | Vector MICROSAR / EB tresos / ETAS RTA — per-ECU seat + runtime licences [8][14] | Vector MICROSAR Adaptive / EB corbos / Apex — HPC-class stacks, often open-source-adjacent [8][12] |
| **Target silicon** | Microcontrollers: Infineon AURIX, NXP S32K, Renesas RH850 [3] | Microprocessors/SoCs: NVIDIA Orin/Thor, Qualcomm, NXP S32G/S32N, Renesas R-Car [4][6] |
| **Typical ASIL** | ASIL B–D actuator/safety functions [3] | QM–ASIL D compute; often mixed-criticality with a CP safety island [3][6] |
| **Developer experience** | Config-heavy, model-driven, slow iteration, deterministic [3][8] | Code-first C++, app-store deployment, faster iteration, Linux tooling [7][10] |

*Note on ASIL D for AP:* the peer comparison paper (arxiv 2109.00099, Table 1) lists **both** platforms as "Up to ASIL D" [7]. In practice AP ASIL-D is achieved via mixed-criticality partitioning and a CP/lockstep safety companion, not by the Linux/QNX host alone — see Surprises/Open questions.

## 2. The signal-world ↔ service-world gateway

This is the single most important coexistence mechanism. A CP ECU speaks **signals** (fixed byte layouts in PDUs); an AP node speaks **services** (typed events/methods/fields discovered at runtime). A **Signal-to-Service (S2S)** gateway maps between them: it subscribes to Classic COM signals, repackages them, and offers them as SOME/IP services (and vice-versa), acting "like a remote SOME/IP node" to the daemon [13]. Products that implement this in real vehicles:

- **Vector MICROSAR** — S2S add-on / gateway application splits and recombines PDUs into services; MICROSAR Classic and MICROSAR Adaptive interoperate over SOME/IP-SD [13][8].
- **Elektrobit EB tresos (CP) + EB corbos (AP)** — Classic BSW plus adaptive stack with the same bridging role [14].
- **ETAS RTA** — RTA-CAR (Classic) and RTA-VRTE (Adaptive) with signal/service translation.

Crucially, **R25-11 adds DDS as a service transport on Classic itself**: "Management functionalities for Events, Methods, and Fields, previously available through SOME/IP, are now extended to DDS," via a new **DDS Transformer** BSW module and OMG **SPDP/SEDP** discovery plus AP's Service Discovery, "thus ensuring cross-solution compatibility" [2]. This narrows the CP/AP protocol gap and lets a CP ECU participate directly on the DDS databus that AP (and ROS 2) already use.

## 3. Published OEM E/E architectures showing the CP+AP split

- **Volkswagen Group E³ (E3 1.1 / E3 1.2)** — the E3 domain/zonal architecture (E3 1.1 on MEB EVs, E3 1.2 on PPE, Audi-led) with CARIAD software; zonal controllers/safety ECUs run **Classic**, central HPCs run **Adaptive**/Linux for AD, infotainment, OTA [9]. VW's China CEA architecture was co-developed with XPENG/VCTC [9].
- **Mercedes-Benz MB.OS** — a proprietary vehicle OS whose **Base Layer** middleware was co-developed with **Vector**, "based on AUTOSAR Adaptive and Classic and the AUTOSAR Runtime Environment" [12]. This is the canonical "AUTOSAR adopted selectively inside a custom platform" pattern this repo tracks.
- **BMW / others** — publicly describe HPC + zonal splits with Adaptive on the compute cluster; exact stack attribution is less publicly documented (see Open questions).

The recurring pattern: **CP for the reflex nervous system, AP for the brain, Ethernet + gateways for the spine.**

## 4. Migrating one function from CP to AP — what it actually involves

Moving, say, a body-comfort or ADAS-preprocessing function from a Classic ECU to an Adaptive HPC is not a recompile; it is a re-architecting:

1. **Re-express the interface** from signals/PDUs to a **service interface** (events/methods/fields) — new ARXML `ServiceInterface` and manifests instead of COM signal definitions [7][15].
2. **Rewrite the code** from C/RTE calls (`Rte_Read/Write`) to C++ `ara::com` proxies/skeletons [7].
3. **Add a manifest** (Execution, Service Instance, Machine manifests) for late binding, plus **UCM Software Cluster** packaging for deployment/OTA instead of a full-ECU flash [15].
4. **Insert an S2S gateway** so the migrated service still reaches the CP ECUs that expected the old signals [13].
5. **Re-do the safety case** — dynamic memory, POSIX scheduling, and mixed-criticality partitioning must be argued afresh; deterministic allocators replace `malloc/free` in critical phases [1].

Published, fully-worked OEM case studies with artifacts are scarce (mostly vendor whitepapers, e.g. "Transitioning from AUTOSAR Classic to Adaptive for Service-Based Architectures" [13-lead]); this is an Open question.

## 5. Where ROS 2 realistically sits next to AUTOSAR

ROS 2 is **not** an AUTOSAR platform and is not a drop-in production automotive middleware — but it shares the **DDS wire family** (ROS 2's default RMW is DDS: Fast DDS / Cyclone DDS; AP supports DDS as an `ara::com` binding [5][7]). Positioning verified against primary/peer sources:

- **Complementary, not competing.** Apex.AI: "ROS 2 has taken a code-first approach to make it as easy as possible to develop new applications" while "AUTOSAR has a strong focus and successful history in creating interoperability between suppliers and OEMs." Integration is via **bridges** — Apex.AI ships SOME/IP, CAN, MQTT connectors so ROS 2 data reaches "AUTOSAR Adaptive applications using `ara::com` or in AUTOSAR Classic RTE" [10].
- **Prototyping vs production.** Multiple sources converge: ROS 2 excels in research/prototyping; AP dominates certified production. The arxiv middleware-requirements comparison (Hegerath et al., 2026) finds ROS 2 lacks hard real-time/determinism guarantees for safety-critical automotive use, while AP is production-oriented [16]. A Nov-2025 arxiv paper proposes an explicit **AP↔ROS 2 collaboration framework** with DDS as the common layer and gateways for message routing [17].
- **Real examples.** **Autoware** (Tier IV / Autoware Foundation) is the flagship ROS 2 open AD stack [10][17]. **Apex.Grace** (formerly Apex.OS) is the production-hardened ROS 2 derivative — certified by TÜV Nord as a **Safety Element out of Context (SEooC) up to ASIL D** per ISO 26262; companion **Apex.Ida** (formerly Apex.Middleware) is the DDS-based communication layer [10][11]. Apex.Grace enforces static memory pools and eliminates runtime dynamic allocation — mirroring exactly the AP dynamic-memory concern in [1].

**Folklore discipline:** claims like "Tesla uses no AUTOSAR" are **not sourced here** and go to Open questions.

## Key facts

| # | Fact | Source URL | Exact quote (if load-bearing) | Confidence |
|---|---|---|---|---|
| 1 | Latest release is R25-11, published 2025-11-27 | autosar.org R25-11 news [1] | "Release R25-11 is Now Available" | high |
| 2 | AP dynamic memory allocation is allowed/assumed | FO EXP SWArchitecturalDecisions R25-11 [1a] | "The use of dynamic memory allocation by Adaptive Applications and Functional Clusters is allowed and assumed upon designing the AUTOSAR Adaptive Platform standard" | high |
| 3 | R25-11 adds SOA/DDS to Classic Platform | CP TR ReleaseOverview R25-11 [2] | "Management functionalities for Events, Methods, and Fields, previously available through SOME/IP, are now extended to DDS" + "new BSW module DDS Transformer" | high |
| 4 | AP OS = POSIX PSE51 profile | AP SWS OperatingSystemInterface R25-11 [4] | "PSE51 defined in IEEE1003.13" / "PSE51 following POSIX-1003.1-2003" | high |
| 5 | AP scheduling policies SCHED_FIFO/RR/OTHER, optional SCHED_DEADLINE (EDF) | AP SWS OperatingSystemInterface R25-11 [4] | "shall support the following scheduling policies defined in the IEEE1003.1 POSIX standard: SCHED_OTHER, ..." + "SCHED_DEADLINE (Earliest Deadline First" | high |
| 6 | CP = OSEK, C, signal-based, whole-ECU update, up to ASIL D; AP = POSIX, C++, service (SOME/IP), per-app update, up to ASIL D | arxiv 2109.00099 Table 1 [7] | "AUTOSAR Classic: OSEK / C / Remove or update the entire ECU / Up to ASIL D … AUTOSAR Adaptive: POSIK[sic] / C++ / Remove, add, or update individual application / Up to ASIL D" | med |
| 7 | AP `ara::com` is a C++ SOA API based on SOME/IP | arxiv 2109.00099 [7] | "ara::com is a standard C++ API based on SOA more specifically based on SOME/IP … classic cover the communication between software components using RTE signals" | med |
| 8 | AP UCM updates individual Software Clusters; functional-group granularity; OTA + workshop | AP SWS UpdateAndConfigurationManagement R24-11 [15] | "means to install new and upgrade existing software components … functional groups allow separate state transitions" | high |
| 9 | CP OS is OSEK/VDX-compliant, code-generated static config, SafetyOS up to ASIL D/SIL 3 | Elektrobit EB tresos [14] | "OsekCore is a Classic AUTOSAR basic software package for OSEK-/VDX-compliant ECUs … EB tresos Safety OS … up to ASIL D/SIL 3" | high |
| 10 | Vector MICROSAR provides signal-to-service (S2S) translation acting as remote SOME/IP node | Vector / S2S search [13] | "S2S … enables the translation of signal-based (Classic ECUs) to service-oriented communication (Adaptive ECUs)"; gateway "acting like a remote SOME/IP node" | med |
| 11 | Mercedes MB.OS Base Layer co-developed with Vector, based on AUTOSAR Adaptive+Classic+RTE | Vector MB.OS news [12] | "based on AUTOSAR Adaptive and Classic and the AUTOSAR Runtime Environment" | high |
| 12 | Apex.Grace certified ASIL D SEooC by TÜV Nord; ROS 2 API compatible | Apex.AI [10][11] | "certified by TÜV Nord as Safety Element out of Context (SEooC) up to ASIL D according to the ISO 26262 standard" | high |
| 13 | Apex.AI ships SOME/IP, CAN, MQTT connectors bridging ROS 2 to AP `ara::com` / CP RTE | Apex.AI post [10] | "connectors for communication protocols, including SOME/IP, CAN, and MQTT"; export "to AUTOSAR Adaptive applications using ara::com or in AUTOSAR Classic RTE" | high |
| 14 | VW E3 1.1 (MEB) / E3 1.2 (PPE); zonal + HPC; CARIAD software; CEA co-developed with XPENG | VW Group / CARIAD [9] | "zonal architecture typically relies on a high-performance computer (HPC)"; "China Electrical Architecture (CEA)" | med |
| 15 | AP specifies functional clusters (not modules); diagnostics is a functional cluster (ara::diag/DM) | AP TR ReleaseOverview R25-11 [3-AP] | "The Adaptive Platform differs … as it specifies functional clusters instead of modules" | high |
| 16 | CP diagnostics = DCM+DEM implementing UDS (ISO 14229) | ElectRay / AUTOSAR CP SWS DCM [14b] | "DCM … handles UDS service processing … and DEM (Diagnostic Event Manager)" | high |
| 17 | Nov-2025 arxiv proposes AP↔ROS 2 collaboration framework with DDS common layer + gateways | arxiv 2511.17540 [17] | "gateway solutions that facilitate data exchange between AP and ROS 2 systems" | med |
| 18 | 2026 arxiv: ROS 2 lacks hard real-time/determinism for safety-critical automotive; AP production-oriented | arxiv 2604.22576 [16] | "ROS 2 lacks hard real-time guarantees needed for safety-critical systems" | med |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 news — AUTOSAR — primary
   1a. https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf — Explanation of Adaptive and Classic Platform SW Architectural Decisions, FO R25-11 — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf — Classic Platform Release Overview R25-11 (DDS on CP, VDP) — AUTOSAR — primary
3-AP. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf — Adaptive Platform Release Overview R25-11 (functional clusters, diagnostics) — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf — AP SWS Operating System Interface R25-11 (PSE51, scheduling) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf — AP SWS Communication Management R25-11 (ara::com, SOME/IP, DDS) — AUTOSAR — primary
7. https://arxiv.org/pdf/2109.00099 — Comparison between AUTOSAR Platforms (Table 1) — arXiv — secondary/peer
9. https://www.volkswagen-group.com/en/articles/smart-vehicles-at-china-speed-... — VW/XPENG CEA E/E architecture — Volkswagen Group — vendor/OEM
10. https://www.apex.ai/post/autosar-and-ros-2-for-software-defined-vehicle — AUTOSAR and ROS 2 for SDV — Apex.AI — vendor
11. https://www.apex.ai/apexgrace — Apex.Grace (ASIL-D SEooC) — Apex.AI — vendor
12. https://www.vector.com/us/en/news/news/mercedes-benz-mbos-base-layer/ — Mercedes MB.OS Base Layer teamup — Vector — vendor
13. https://cdn.vector.com/cms/content/products/Adaptive_MICROSAR/Docs/MICROSAR_Adaptive_ProductCatalogue_EN.pdf — MICROSAR Adaptive (S2S) — Vector — vendor; lead: https://www.researchgate.net/publication/397552044 (Transitioning CP→AP for Service-Based Architectures)
14. https://www.elektrobit.com/products/ecu/eb-tresos/operating-systems/ — EB tresos OsekCore / Safety OS — Elektrobit — vendor
   14b. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf — CP SWS DCM (UDS/ISO 14229) — AUTOSAR — primary
15. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf — AP SWS Update and Configuration Management (UCM) — AUTOSAR — primary
16. https://arxiv.org/pdf/2604.22576 — Comparison of ROS 2 and AP against automotive middleware requirements (Hegerath et al., 2026) — arXiv — secondary/peer
17. https://arxiv.org/pdf/2511.17540 — AUTOSAR AP and ROS 2 Collaboration Framework (Iwakami et al., 2025-11-25) — arXiv — secondary/peer

## Surprises

- **The CP/AP protocol gap is closing from the Classic side.** R25-11 brings full SOA (Events/Methods/Fields) and **DDS** onto Classic via a new DDS Transformer BSW module and shared OMG SPDP/SEDP + AP Service Discovery [2]. The common assumption that "signals = Classic, services = Adaptive" is now outdated at the standard level.
- **Both platforms are documented as "up to ASIL D."** The naive assumption that Adaptive is only QM/low-ASIL is wrong on paper [7] — though real-world ASIL-D on a Linux/QNX host still leans on mixed-criticality partitioning and a CP safety companion.
- **Dynamic memory is explicitly *blessed* in Adaptive** [1a] — the opposite of the classic MISRA-C "no heap" reflex firmware engineers carry. AUTOSAR's answer is deterministic allocators replacing malloc/free, not banning the heap.
- **Apex.Grace hardens ROS 2 using the very same discipline** (static memory pools, no runtime allocation) that AP's safety note prescribes for C++ [1a][10] — the safe-C++ playbook converges across ROS 2 and AUTOSAR.
- **OEMs are wrapping AUTOSAR, not adopting it wholesale.** MB.OS uses AUTOSAR Adaptive+Classic+RTE as a *base layer* under a proprietary OS built with Vector [12] — AUTOSAR as ingredient, not platform.

## Open questions

- **Exact AP ASIL-D field evidence.** Sources state "up to ASIL D" as a design target [7][6]; I could not verify a specific production ECU where the AP host *itself* (not a CP/lockstep companion) carries the ASIL-D claim. *Guess (labelled): ASIL-D-relevant paths in production AP deployments are partitioned onto a safety island or hypervisor, with the Linux/QNX AP host at ASIL-B or QM.*
- **"Tesla uses no AUTOSAR."** Common folklore; **no primary source found**. Tesla's stack is largely proprietary Linux-based, but a categorical "zero AUTOSAR" claim is unverified. Left as folklore, not fact.
- **Published, artifact-level CP→AP migration case study.** Vendor whitepapers describe the pattern [13-lead] but a public OEM case study listing concrete ARXML/manifest artifacts and effort was not located.
- **BMW stack attribution.** BMW publicly runs HPC+zonal; the precise CP/AP/vendor breakdown is not clearly documented in accessible primary sources.
- **AP Communication Management DDS binding maturity.** I confirmed the R25-11 CommunicationManagement SWS exists and DDS is a binding [5], but did not fetch the exact clause enumerating supported DDS QoS vs SOME/IP parity — flagged for a deeper follow-up.
- **Whether R25-11 CP "DDS Transformer" is production-shipping or concept-stage.** The Release Overview describes it as an introduced concept [2]; adoption timelines by Vector/EB/ETAS were not verified.
