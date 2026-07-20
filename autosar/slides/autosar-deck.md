---
marp: true
paginate: true
theme: default
style: |
  section { font-size: 26px; }
  h1 { color: #1b2b4a; }
  h2 { color: #2E5FAC; }
  table { font-size: 22px; }
  code { background: #eef2f8; }
  section.lead h1 { font-size: 50px; }
  section.lead h2 { color: #5b7bb0; font-weight: 500; }
  section.diagram { display: flex; align-items: center; justify-content: center; padding: 14px; }
  section.diagram img { height: 650px; width: auto; max-width: 100%; }
  .cmd { display:inline-block; background:#11233f; color:#e8eefc; padding:8px 16px;
         border-radius:8px; font-family:monospace; font-size:22px; margin:4px 0; }
  .ok { color:#2e7d32; font-weight:bold; }
  .bad { color:#c62828; font-weight:bold; }
  .gloss { font-size:17px; color:#66708a; border-top:1px solid #dde3ee;
           margin-top:16px; padding-top:6px; }
  img[alt^="spec-"] { display: block; margin: 0 auto; max-width: 88%; max-height: 430px; }
  .figsrc { font-size: 12px; color: #6b7280; text-align: center; margin-top: 6px; }
---

<!-- _class: lead -->

# AUTOSAR for firmware engineers — 2026

## one organization · two platforms · one vehicle

A field guide for embedded engineers who know MCUs, CAN, an RTOS and bare-metal
reflashing — and are new to automotive software platforms. Release-stamped to
**AUTOSAR R25-11** (published 2025-11-27). External claims are URL-sourced —
**references at the end.**

---

## Agenda

<style scoped>
  section { font-size: 22px; }
</style>

1. **One org, three standards** — history, governance, the FO / CP / AP split, the release timeline
2. **Classic Platform** — the statically-configured RTOS stack you half-know: RTE/VFB, AUTOSAR OS, ARXML, the signal path, E2E/SecOC, DCM/DEM, NvM/WdgM, functional safety
3. **Adaptive Platform** — the POSIX/C++ service platform on the "big chip": functional clusters, EM/SM, `ara::com`, SOME/IP vs DDS, UCM OTA, DM/SOVD, PHM, vendors & ASIL reality, the open-source AP landscape
4. **Head-to-head & coexistence** — one vehicle running both, the R25-11 convergence, where ROS 2 sits, what it means for our team

**Manager fast path (~10 min):** slides 3–6 (what AUTOSAR is and why) · 46–50 (which stack on which silicon: the split, coexistence, fleet, decision map)

<div class="gloss">AUTOSAR = AUTomotive Open System ARchitecture · FO = Foundation · CP = Classic Platform · AP = Adaptive Platform · RTE = Runtime Environment · VFB = Virtual Functional Bus · UDS = Unified Diagnostic Services (ISO 14229) · SOVD = Service-Oriented Vehicle Diagnostics · full expansions on the glossary slide near the end</div>

---

<!-- _class: lead -->

# Part 0
## one organization, three standards

---

<!-- _class: diagram -->

{{diagram:autosar-timeline}}

---

## One standard set, three members: FO · CP · AP

- **The org, in one line**: a **worldwide development partnership** (founding talks 2002,
  Development Agreement July 2003), governed top-down by ~10 **Core Partners**; **about 340
  partners today (339 at the end of 2025), Asia-led** (status Apr 2026: Asia 164 > Europe 128 > NA 41). Jan 2026: DENSO, Huawei and
  Vector promoted to Core. Specs are **free to read, license-to-build**
- **Foundation (FO)** — the cross-platform glue: common requirements, the **meta-model and
  single XML schema**, methodology, and shared wire protocols (SOME/IP, time-sync, DoIP, E2E,
  SecOC). FO is what lets a Classic ECU and an Adaptive machine live in one vehicle project
- **Classic Platform (CP)** — statically-configured, real-time stack for deeply embedded
  microcontrollers, built on a **fixed-priority preemptive kernel**. First released 1.0 in **2005**
- **Adaptive Platform (AP)** — **POSIX**-based, service-oriented, dynamically-deployed stack
  for high-performance compute. First released **17-03 (March 2017)**
- **The naming trap**: the **R19-11 unification** (Nov 2019) merged CP's `4.x.y` and AP's
  `yy-mm` into one annual `R{yy}-11` label, one November release, one schema — **but the CP
  internal version never reset**. R25-11 is internally **R4.11.0**; "AUTOSAR 4.x" is alive
- **Document prefixes** you'll meet: **EXP** (explanatory), **TR** (technical report),
  **RS/SRS** (requirements), **SWS** (the detailed testable module spec), **TPS** (templates),
  **PRS** (wire-protocol requirements)

<div class="gloss">POSIX = Portable Operating System Interface (IEEE 1003) · SOME/IP = Scalable service-Oriented MiddlewarE over IP · DoIP = Diagnostics over IP (ISO 13400) · E2E = End-to-End protection · SecOC = Secure Onboard Communication · SWS = Software Specification</div>

---

## The spec landscape — a reading map (every PDF is a free download)

<style scoped>
  section { font-size: 18.5px; padding-top: 28px; }
  h2 { margin-bottom: 4px; }
  p { margin: 5px 0; }
  table { font-size: 15.5px; }
  .gloss { font-size: 13px; margin-top: 8px; }
</style>

All specs live at `autosar.org/fileadmin/standards/R25-11/<FO|CP|AP>/<name>.pdf` — no login, no
membership. **Start with the three EXP intros**, use the TR ReleaseOverviews to stay current,
open an SWS only when you implement. (Every filename below verified live against R25-11.)

| You want… | Read (`AUTOSAR_` prefix omitted) |
|---|---|
| **the big picture, first** | `CP_EXP_LayeredSoftwareArchitecture` · `AP_EXP_PlatformDesign` · `FO_EXP_SWArchitecturalDecisions` (why two platforms exist) |
| CP OS, RTE & the VFB | `CP_SWS_OS` (SC1–SC4) · `CP_SWS_RTE` · `CP_TR_VFB` |
| CP comm stack (our diagram) | `CP_SWS_COM` · `CP_SWS_PDURouter` · `CP_SWS_CANTransportLayer` · `CP_SWS_CANInterface` |
| CP diagnostics & services | `CP_SWS_DiagnosticEventManager` (DEM) · `CP_SWS_DiagnosticCommunicationManager` (DCM) · `CP_SWS_NVRAMManager` · `CP_EXP_ModeManagementGuide` · `CP_SWS_WatchdogManager` |
| CP functional safety | `CP_EXP_FunctionalSafetyMeasures` |
| AP functional clusters | one SWS each: `AP_SWS_ExecutionManagement` · `…StateManagement` · `…CommunicationManagement` (`ara::com`, SOME/IP + DDS bindings) · `…Diagnostics` · `…UpdateAndConfigurationManagement` (+ `…VehicleUpdateAndConfigurationManagement`) · `…PlatformHealthManagement` · `…Persistency` · `…OperatingSystemInterface` (PSE51) — plus `AP_TPS_ManifestSpecification` |
| wire protocols (CP + AP share) | `FO_PRS_SOMEIPProtocol` · `FO_PRS_SOMEIPServiceDiscoveryProtocol` · `FO_PRS_E2EProtocol` · `FO_PRS_SecOCProtocol` · `FO_PRS_NetworkManagementProtocol` |
| what changed this year | `CP_TR_ReleaseOverview` · `AP_TR_ReleaseOverview` |

<div class="gloss">EXP = explanatory (read these first) · SWS = software specification (one per module, testable) · PRS = wire-protocol requirements · TPS = template spec (ARXML/manifests) · TR = technical report · reading is free — implementing commercially requires an AUTOSAR partner license · R25-11 renames to note: the VFB doc is now CP_TR_VFB (was CP_EXP_VFB in R24-11) and SecOC is FO_PRS_SecOCProtocol (was …SecOcProtocol)</div>

---

<!-- _class: lead -->

# Part 1
## the Classic Platform — the deeply embedded half

---

## What Classic is, and where it runs

- **A statically-configured software stack for deeply embedded ECUs** — single
  microcontrollers, no MMU-class OS, hard real-time, safety-critical. The static real-time half
- **Hold onto this one property**: a CP ECU builds to **one statically configured binary** —
  fixed task set, fixed communication matrix, fixed memory map, all decided at design time.
  *"All tasks that will ever execute … are allocated when the executable image is built."*
  No `malloc`, no runtime task creation, no service negotiation
- This is the discipline safety-critical firmware already follows by hand — **CP formalizes it
  and generates the glue**
- **Where it sits in a 2026 vehicle**: CP owns the **edge** — zonal, body/chassis/powertrain
  ECUs, and the **safety MCU** that gates actuators on high-compute boards. On an NVIDIA DRIVE
  board: the big SoC does perception; a small lock-step safety MCU running CP owns the
  fail-safe path and diagnostics
- **Pinned silicon**: Orin-gen safety MCU = **Infineon AURIX TC397X**; Thor-gen companion MCU
  = **Renesas RH850U2A16** (Vector MICROSAR Classic as reference). *Never say Thor uses AURIX*
- Myth this repo already killed: **"Classic = CAN only" is false** — CP has had a standardized
  SOME/IP Transformer since **4.2.1 (Oct 2014)**, years before AP's first release, plus Ethernet,
  DoIP, LIN, FlexRay

<div class="gloss">ECU = Electronic Control Unit · MMU = Memory Management Unit (virtual memory; CP has none) · MCU = microcontroller · SoC = System-on-Chip · lock-step = two cores running identical code compared each cycle for fault detection · MICROSAR = Vector's AUTOSAR product family</div>

---

<!-- _class: diagram -->

{{diagram:stack-autosar-classic}}

---

## The three layers, and the one escape hatch

- CP has three top-level layers: **Application → Runtime Environment (RTE) → Basic Software
  (BSW)**. The BSW splits into three horizontal layers plus one vertical bypass:

| BSW sub-layer | What it does | Firmware analogy |
|---|---|---|
| **Services** (top) | OS, comms + network mgmt, NVRAM, diagnostics, ECU-state mgmt | your middleware: UDS server, EEPROM mgr, watchdog kicker |
| **ECU Abstraction** | abstracts *board* wiring — which peripheral a signal routes through | your board-support glue |
| **MCAL** (bottom) | register-level access to on-chip peripherals; MCU-specific, silicon-vendor-supplied | **the vendor HAL, made standard** — you *port* it, not rewrite |
| **CDD** (vertical) | sanctioned escape hatch: may touch hardware directly for non-standard / extreme-timing needs | a bare-metal ISR that bypasses your own abstraction |

- Drivers you know by register — Dio, Port, Adc, Pwm, Spi, Can, Wdg, Mcu — live in **MCAL**
  behind a fixed API and generated config

<div class="gloss">RTE = Runtime Environment · BSW = Basic Software · MCAL = Microcontroller Abstraction Layer · NVRAM = non-volatile RAM · CDD = Complex Device Driver · HAL = hardware abstraction layer · ISR = interrupt service routine · the CDD legitimately breaks the layering — the standard sanctions it</div>

---

## The layered software architecture — as the spec draws it

{{image:spec-lsa-detailed-view}}

<div class="figsrc">Source: AUTOSAR CP_EXP_LayeredSoftwareArchitecture, R25-11, "Overview of Software Layers — detailed view" (p. 24) — © AUTOSAR.</div>

<div class="gloss">Map the spec labels to the deck's terms: 'Runtime Environment' = the RTE · the BSW (Basic Software) has four layers — Services, ECU Abstraction, Microcontroller Abstraction and Complex Drivers · the bottom 'Drivers' row = MCAL (Microcontroller Abstraction Layer) · 'Complex Drivers' (CDD) = the fourth BSW layer, drawn spanning hardware→RTE — the non-standard escape hatch · HW = hardware (I/O = input/output)</div>

---

## The relocation trick — SWCs, the VFB, and why the RTE is generated

- Application logic is packaged as **Software Components (SWCs)** exposing **ports** typed by
  interfaces — mainly **sender-receiver** (data-flow) and **client-server** (operation). Code
  is organized as **runnable entities**, each ultimately *"a C function"* fired by RTE Events
- **SWCs never call each other directly.** They talk over the **Virtual Functional Bus (VFB)**
  — a *logical* concept spanning ECUs. The thing that actually implements the VFB on a real
  ECU is the **RTE**, generated per deployment
- RTE generation has two phases: **contract phase** (emits `Rte_<SWC>.h` so a SWC compiles in
  isolation) and **generation phase** (emits the real code that moves data / dispatches runnables)
- SWC code calls **`Rte_Write()` / `Rte_Read()` / `Rte_Call()`** — and *never knows* whether the
  peer is a runnable on the **same** ECU (a local buffer copy) or a **remote** one (a COM
  message over CAN/Ethernet)
- **This is why the same SWC relocates to a different ECU without code changes** — it
  references only ports and `Rte_*` symbols, never a bus or a driver. Moving it changes only
  what the RTE generator emits. **There is no real bare-metal analogue to this**

<div class="gloss">SWC = Software Component · VFB = Virtual Functional Bus · runnable = the schedulable C-function unit inside a SWC · COM = the AUTOSAR signal-packing communication module · deployment (which SWC runs on which ECU) is a late-binding config decision realized by regenerating the RTE</div>

---

## The VFB — as the spec draws it

<style scoped>
  img[alt^="spec-"] { max-height: 470px; }
</style>

{{image:spec-vfb-concept}}

<div class="figsrc">Source: AUTOSAR CP_TR_VFB, R25-11, Figure 2.2 — © AUTOSAR.</div>

<div class="gloss">SW-C = Software Component · ECU = Electronic Control Unit · RTE = Runtime Environment (the generated per-ECU code that actually implements the VFB) · the figure's point: the same SW-C maps onto ECU I / II / n unchanged, over FlexRay or CAN. (VFB itself is spelled 'Virtual Functional Bus' inside the figure.)</div>

---

## AUTOSAR OS — a static real-time kernel with scalability classes

<style scoped>
  section { font-size: 21px; }
  li { margin-bottom: 4px; }
  table { font-size: 18px; }
  th, td { padding: 3px 8px; }
  .gloss { font-size: 15px; margin-top: 8px; padding-top: 4px; line-height: 1.3; }
</style>

- AUTOSAR OS is a **static, fixed-priority real-time kernel**. Its whole task set is fixed at
  build time, and it provides fixed-priority preemptive scheduling, priority-ceiling resources,
  events, alarms, counters, and Cat-1 vs Cat-2 ISRs, all with no heap. **If you already know a
  statically configured RTOS, you know most of it**, but it is stricter.
- What AUTOSAR bundled on top, as **Scalability Classes**:

| Class | = | Adds |
|---|---|---|
| **SC1** | base OS + | **Schedule Tables** (time-triggered, sync to global time), stack monitoring |
| **SC2** | SC1 + | **Timing Protection** (execution / inter-arrival budgets) + global time sync |
| **SC3** | SC1 + | **Memory Protection** + OS-Applications + trusted/non-trusted functions |
| **SC4** | SC2+SC3 | both timing and memory protection |

- **Multicore** arrived in release **4.0 (2009)**: multi-core startup, **spinlocks**, and
  **IOC** (Inter-OS-Application Communication) — a spinlock-protected shared-memory ring for
  data crossing a core/partition boundary

<div class="gloss">ISR = interrupt service routine (Cat-1 = no OS calls, lowest latency; Cat-2 = may call OS services) · SC = Scalability Class · IOC = Inter-OS-Application Communication · exact SC1–SC4 wording is medium-confidence (structure high) — see references</div>

---

## The model-driven workflow — ARXML and the OEM↔supplier handshake

- Everything is exchanged as **ARXML** ("AUTOSAR XML"), a fixed-schema format that is **rarely
  hand-authored** — GUI configuration tools produce and consume it. The classic flow:
  1. **System / VFB Description** (OEM) — all SWCs, ports, topology, signals → System Config
  2. **ECU Extract** — the slice for *one* ECU, handed to the Tier-1 supplier
  3. **ECU Configuration (ECUC)** — supplier configures that ECU's BSW + RTE
  4. **Generation** — tools emit BSW config, the RTE and OS config; compiles with hand-written
     SWC code + vendor MCAL into **one ECU executable**
- **Dominant toolchains**: **Vector DaVinci** (Developer + Configurator), **EB tresos Studio**,
  **ETAS ISOLAR / RTA-CAR**. MCU vendors ship the MCAL matching each toolchain
- **Language rule**: BSW/RTE code is **C** and must be **MISRA C** — 4.2 required C:2004; **4.3
  and later (incl. R25-11) require MISRA C:2012**. (C++14 is an *Adaptive* concern — easy to conflate)
- **What is genuinely new** for a bare-metal + RTOS engineer is not the OS or the HAL — it's the
  **generate-then-compile workflow** and the **ARXML handshake**, an artefact with no firmware-world equivalent

<div class="gloss">ARXML = AUTOSAR XML config format · ECUC = ECU Configuration Description · Tier-1 = the supplier who builds an ECU for the OEM · MISRA C = the automotive safe-C coding-rule set · MCAL = Microcontroller Abstraction Layer</div>

---

<!-- _class: diagram -->

{{diagram:cp-signal-path}}

<div class="gloss">Extend the diagram's abbreviation key: DBC = Vector CAN database · LDF = LIN Description File · FIBEX = ASAM multi-bus exchange format · ARXML = AUTOSAR XML · CRC = Cyclic Redundancy Check · MAC = Message Authentication Code (the SVG key already covers SW-C/RTE/COM/I-PDU/PduR/CanTp/CanIf/MCAL/E2E/SecOC/SomeIpXf)</div>

---

## The frozen communication matrix

- CP communication is **signal-oriented and frozen at build time** — a layered pipeline of BSW
  modules, each doing one abstraction step (see the previous diagram)
- The **communication matrix (K-matrix)** is the master description of *all* network
  communication in the vehicle: every frame/PDU, every signal, sender ECU, receivers, byte
  layout, timing, value encoding. It is frozen because CP targets small-flash, deterministic,
  ASIL ECUs — so COM's packing, PduR's routing and CanIf's handle map are all **statically
  generated** and provable at integration time
- **File-format lineage**: **DBC** (Vector, CAN), **LDF** (LIN), **FIBEX** (ASAM, multi-bus),
  and AUTOSAR's own **ARXML** carrier. It is the CAN message database (DBC) you know — promoted
  to a whole-vehicle, multi-bus, code-generating source of truth
- **Bus landscape 2026**: **CAN FD** mainstream (up to 64-byte payload); classic CAN survives
  for low-cost nodes; **FlexRay in decline** (still specified, not removed); **Automotive
  Ethernet (100/1000BASE-T1, TSN)** is the growth path, carrying SOME/IP and DoIP
- **CAN XL** (ISO 11898-1:2024, up to 2048-byte payloads) is emerging — AUTOSAR support release
  unconfirmed (open question)

<div class="gloss">PDU = Protocol Data Unit (the byte array a signal is packed into) · PduR = PDU Router · CanIf = CAN Interface · ASIL = Automotive Safety Integrity Level (ISO 26262, QM < A < B < C < D) · TSN = Time-Sensitive Networking (IEEE 802.1) · CAN FD = CAN with Flexible Data-rate</div>

---

## E2E and SecOC — protect the data, not the channel

- **E2E (End-to-End) protection** guards safety-relevant data per ISO 26262. It's a
  transformer in the COM chain, so protection travels **with the payload across ECU and bus
  boundaries — including through PduR gateways**: CRC + counter computed at the true sender,
  checked at the true receiver, so a gateway can't silently corrupt safety data
- Fault model: repetition, loss, delay, insertion, masquerade, wrong sequence, corruption…
  Mechanisms: a **CRC**, a **counter**, **timeout monitoring**, and a **Data ID** folded in.
  Profiles range **P1/P2/P11/P22 (8-bit)** · **P5/P6 (16-bit)** · **P4 (32-bit)** · **P7 (64-bit)**
  — 8-bit profiles *cannot* detect a masquerade fault in a single cycle
- **SecOC (Secure Onboard Communication)** adds **authenticity + freshness** — **it does NOT
  encrypt.** The payload stays in the clear. TX builds a **Secured I-PDU** = data +
  **Authenticator (a MAC)** + optional **Freshness Value**, using **CMAC / AES-128** (NIST
  SP 800-38B); the MAC is **truncated** to fit tight CAN payloads (a bandwidth/security tradeoff)
- **Honest guarantee**: a verified MAC proves the message came from a holder of the shared
  symmetric key and is fresh (defeats replay) — it does **not** hide data and gives **no
  non-repudiation**. Keys come from the Crypto stack, out of SecOC's scope

<div class="gloss">E2E = End-to-End · CRC = Cyclic Redundancy Check · Data ID = a per-signal identifier mixed into the CRC · SecOC = Secure Onboard Communication · MAC = Message Authentication Code · CMAC = Cipher-based MAC · "no confidentiality" is inferred from the PRS scope — medium confidence</div>

---

## The Secured I-PDU — as the spec draws it

{{image:spec-secured-ipdu-layout}}

<div class="figsrc">Source: AUTOSAR FO_PRS_SecOCProtocol, R25-11, Figure 5.1 — © AUTOSAR.</div>

<div class="gloss">I-PDU = Interaction-layer PDU (Protocol Data Unit — the packed signal payload) · Authentic I-PDU = the original data, carried in the clear · Freshness Value = the anti-replay counter (optional, transmitted truncated) · Authenticator = the (typically truncated) MAC (Message Authentication Code) · wire order per [PRS_SecOc_00211]: Authentic I-PDU → Freshness Value → Authenticator · SecOC authenticates, it does not encrypt</div>

---

## E2E protection — as the spec draws it

{{image:spec-e2e-overview}}

<div class="figsrc">Source: AUTOSAR FO_PRS_E2EProtocol, R25-11, Figure 1.1 — © AUTOSAR.</div>

<div class="gloss">E2E = End-to-End protection (CRC + counter + Data ID, ISO 26262) · ECU = Electronic Control Unit · MCU = microcontroller · protection is added at the sending SW-C and checked at the receiving SW-C, so corruption introduced in between (lower layers, pass-through gateways) is detected with the profile's bounded residual risk — high-probability detection, not an absolute guarantee</div>

---

## Diagnostics — DEM computes, DCM formats (get this split right)

- **The #1 conceptual error to avoid**: **DEM is the fault database; DCM is the protocol
  server that reads it and talks to the tester.** DCM computes nothing about faults
- **DEM (Diagnostic Event Manager)** is the fault memory. SWCs report a monitor result
  (Passed/Failed) via `Dem_SetEventStatus`; DEM **debounces** it (counter / time / monitor-
  internal), decides when a fault is mature, maintains the per-DTC **8-bit UDS status byte**
  (bit 0 `testFailed` … bit 3 `confirmedDTC` … bit 7 `warningIndicatorRequested`), and stores
  freeze frames to NvM — it is a *client* of the memory stack, it never touches flash itself
- **DCM (Diagnostic Communication Manager)** is a generated, dumb-but-strict **UDS server**. On
  `0x19 ReadDTCInformation` it calls into DEM and formats the answer. It also runs **OBD
  $01–$0A** (J1979) side by side
- **FiM (Function Inhibition Manager)** is the third leg: DEM informs FiM on status change, and
  FiM **inhibits monitors** that would give false readings — prevents cascade/false DTCs
- **OBD vs UDS**: **UDS (ISO 14229) is contractual**; **OBD $01–$0A is statutory — and only for
  emissions ECUs**. A body/comfort ECU has no OBD duty; it serves only UDS

<div class="gloss">DEM = Diagnostic Event Manager · DCM = Diagnostic Communication Manager · FiM = Function Inhibition Manager · DTC = Diagnostic Trouble Code · DID = Data Identifier · NvM = the non-volatile-memory manager · OBD = On-Board Diagnostics · J1979 = SAE emissions-diagnostic standard · a DID read (0x22) checks the DID exists + session + security, then binds to an RTE port or read callout</div>

---

<!-- _class: diagram -->

{{diagram:uds-diag-stack}}

---

## Functional safety — FFI, and what timing protection is NOT

- CP's safety story is **freedom from interference (FFI)** on three axes — memory, timing,
  execution — plus E2E for the communication path (AUTOSAR *Functional Safety Measures*, Doc 664)
- **Memory FFI = Memory Partitioning via OS-Applications**, MPU-enforced: untrusted partitions
  run non-privileged, MPU regions reprogrammed on context switch, any out-of-region access
  traps to hardware. **Trusted** vs **Non-Trusted** OS-Applications. *Limit*: partitioning is at
  OS-Application granularity — **it cannot separate two Runnables inside one SWC**
- **The genuine surprise** (easy to get wrong on a slide): *"The AUTOSAR OS does **not** offer
  deadline supervision for timing protection."* Timing Protection enforces three **budgets** —
  **Execution Time**, **Locking Time**, **Inter-Arrival Time** — **not** deadlines.
  **Deadline supervision is a separate WdgM job** — the **Watchdog Manager** does **Alive /
  Deadline / Logical** supervision over checkpoints and services the HW watchdog *only while
  everything is correct* (far beyond a single `IWDG_Refresh()`)
- Determinism comes from being **statically everything**: no heap, static schedule tables, no
  MMU dependence, timing protection as a runtime backstop
- **Certified proof point**: **Vector MICROSAR Classic Safe** — *"the world's first AUTOSAR
  implementation … certified to ISO 26262 up to ASIL D"* (2016), later exida re-cert covering
  multicore FFI and execution-time bounds. So one CP ECU can host mixed-criticality software:
  ASIL-D braking in one partition, QM comfort code in another

<div class="gloss">FFI = Freedom From Interference (ISO 26262 term) · MPU = Memory Protection Unit (region-compare, not virtual memory) · OS-Application = the partition unit that owns Tasks/ISRs/Alarms/ScheduleTables (Resources are granted, not owned) · WdgM = Watchdog Manager · WCET = Worst-Case Execution Time · QM = Quality Managed (no ASIL) · execution-time enforcement requires MCU timer/MPU hardware</div>

---

## Memory partitioning and modes — as the spec draws it

<style scoped>
  img[alt^="spec-"] { max-height: 470px; }
</style>

{{image:spec-memory-partitioning-modes}}

<div class="figsrc">Source: AUTOSAR CP_EXP_FunctionalSafetyMeasures, R25-11, Figure 2.8 — © AUTOSAR.</div>

<div class="gloss">OS-Application (OS-App) = the partition unit that owns Tasks/ISRs/Alarms/ScheduleTables (Resources are granted to OS-Applications, not owned) — trusted ones may run in CPU supervisor mode with protection off, non-trusted run in user mode with MPU protection on · SW-C = Software Component (allocated to one or more OS-Applications) · IPC = Inter-Process Communication · ECU = Electronic Control Unit</div>

---

## Why Classic persists — structural limits, by design

- CP's strengths invert into hard limits, and AUTOSAR's own R25-11 architecture-decisions doc
  (Doc 1078) frames the CP/AP split around them **on purpose**:
  - **Static communication matrix** — no service discovery of new relationships; adding one
    means re-generate + re-flash. *"If you want software that can be replaced during run time,
    this does not work"*
  - **No dynamic deployment / limited OTA of function** — the ECU image is monolithic and static
  - **C-centric BSW, no dynamic memory** — determinism *requires* no heap, which forbids the
    C++/STL ecosystem AUTOSAR itself calls *"essentially indispensable"* for Adaptive. CP cannot
    host large evolving perception/AI stacks
  - **Scaling pain on HPCs** — built for single-digit-core MCUs with kB–MB memory
- **This is exactly why CP persists at the edge**: its static determinism and ASIL-D cert are
  what a **safety island** needs, and its inflexibility doesn't matter there
- The 2026 pattern is a **designed hierarchy, not legacy baggage** — the most advanced AV
  compute still delegates the certified fail-safe path to a small lock-step MCU running Vector
  *Classic* (Orin → AURIX TC397X; Thor → Renesas RH850U2A16). *Not* a hypervisor guest on Thor;
  *not* a documented Thor fleet gateway

<div class="gloss">OTA = Over-The-Air (software update) · STL = C++ Standard Template Library · HPC = High-Performance Computer/Computing · safety island = the small certified MCU that gates actuators for a powerful-but-less-certifiable SoC · AV = Autonomous Vehicle</div>

---

<!-- _class: lead -->

# Part 2
## the Adaptive Platform — the service platform on the big chip

---

## Why the Adaptive Platform exists

<style scoped>
  section { font-size: 22px; }
</style>

- CP cannot serve the new tier of automotive compute — **high-performance computer (HPC)** ECUs
  driving Ethernet backbones, many-core/GPU/FPGA silicon, service-oriented ADAS/connectivity,
  and **OTA**. AUTOSAR says so plainly: *"the needs of ECUs described above cannot be fulfilled
  [by CP]. Therefore, AUTOSAR specifies a second software platform, the Adaptive Platform …
  offers flexible software configuration, e.g. to support software update over-the-air"*
- Two named drivers: **Ethernet** (switched, high-bandwidth — CP *"cannot fully utilise"* it)
  and **processors** (*"manycore … tens to hundreds of cores, GPGPU … FPGA"*)
- **The one-line orientation, say it precisely**: *"The Adaptive Platform does **not** specify a
  new Operating System … it defines an execution context and Operating System Interface."*
  **AP is middleware + services on top of a POSIX OS — not a new OS.** If your CP instinct is
  "AUTOSAR = the RTOS on my MCU," that instinct is wrong for AP
- **Not "CP is obsolete"** — the two coexist in every real vehicle, usually CP on a companion
  safety MCU and AP on the application SoC
- **The four design traits**: **C++**, **SOA** (a peer is addressed the same whether local
  process or remote machine), **updateability/OTA**, and **agile** deploy-then-update development
- **The dynamic-memory culture shock**: every MISRA-C engineer carries a "no `malloc` in safety
  code" reflex — AUTOSAR says the *opposite* for AP (dynamic allocation is *"allowed and
  assumed"*), answering the non-determinism cost not by banning the heap but with **deterministic
  allocators**. Still, "dynamic" means **deploy-time flexibility + OTA**, *not* free-running
  runtime allocation: the process set per state is fixed in manifests, only discovery is runtime

<div class="gloss">HPC = High-Performance Computer · ADAS = Advanced Driver-Assistance Systems · FPGA = Field-Programmable Gate Array · GPGPU = General-Purpose GPU computing · SOA = Service-Oriented Architecture · POSIX = the standard OS API family (Linux/QNX/PikeOS) AP builds on · deterministic allocator = a fixed-time, fragmentation-bounded replacement for `malloc`/`free`</div>

---

<!-- _class: diagram -->

{{diagram:stack-autosar-adaptive}}

<div class="gloss">Extend the diagram's key: DDS = Data Distribution Service · UDS = Unified Diagnostic Services (ISO 14229) · DoIP = Diagnostics over IP · SoC = System-on-Chip · HPC = High-Performance Computer · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D) (the SVG key already covers DM/UCM/SOME/IP/PSE51)</div>

---

## Adaptive Applications are POSIX processes on ARA

- An **Adaptive Application (AA)** is an ordinary **POSIX process** written in **C++**, linked
  against **ARA** (AUTOSAR Runtime for Adaptive Applications)
- Crucially an AA is restricted "by definition" to the **POSIX PSE51** profile — a
  *single-process* profile (IEEE 1003.13). PSE51 gives threads, mutexes, RT scheduling, timers —
  but **excludes `fork`/`exec`** (no multi-process, no `posix_spawn`) — POSIX shared-memory objects it keeps. Consequences: **one process = one
  address space, multiple threads**; you cannot spawn children (that's Execution Management's
  job); isolation comes from OS process boundaries. Note the OS *itself* must be **multi-process
  POSIX** — only the *AAs* are held to PSE51
- The Machine may be *"a real physical machine, a fully-virtualized machine, a para-virtualized
  OS, an OS-level container or any other virtualized"* environment — AP presents a consistent view
- AAs code against the **`ara::` C++ namespaces** — `ara::com`, `ara::exec`, `ara::core`,
  `ara::log`, `ara::crypto`, `ara::diag`, `ara::per`, `ara::phm`
- The building-block view groups the functional clusters into **seven technical categories** —
  Runtime, Communication, Storage, Security, Safety, Configuration, Diagnostics

<div class="gloss">AA = Adaptive Application · ARA = AUTOSAR Runtime for Adaptive Applications (the `ara::` C++ API surface) · PSE51 = IEEE 1003.13's minimal single-process real-time POSIX profile · `fork`/`exec` = the POSIX process-creation calls PSE51 omits</div>

---

## The R25-11 functional-cluster inventory (this list changes)

- R25-11 defines **20 functional clusters across seven categories** — each its own SWS document.
  **A "canonical list" must always be release-stamped:**

| Category | Functional clusters (R25-11) |
|---|---|
| **Runtime (5)** | Execution Mgmt · State Mgmt · Log & Trace · Core · OS Interface (PSE51) |
| **Communication (5)** | Communication Mgmt (`ara::com`) · Raw Data Stream · Network Mgmt · Time Sync · Automotive API Gateway *(R24-11)* |
| **Storage (2)** | Persistency (`ara::per`) · **Remote Persistency** *(new R25-11)* |
| **Security (3)** | Cryptography · Intrusion Detection Mgr *(R21-11)* · Firewall *(R22-11)* |
| **Safety (2)** | Platform Health Mgmt (`ara::phm`) · **Safe HW Acceleration** *(new R25-11)* |
| **Configuration (2)** | Update & Configuration Mgmt (UCM) · Vehicle UCM *(R23-11)* |
| **Diagnostics (1)** | Diagnostic Mgmt (`ara::diag`) |

- **Do not present as current**: **IAM** (Identity & Access Mgmt, removed R23-11) and **RESTful
  Communication** (removed R21-11). R25-11 also added **Suspend-to-RAM** in State Management

<div class="gloss">SWS = Software Specification (one per cluster) · UCM = Update and Configuration Management · IAM = Identity and Access Management (removed) · "daemon-based" = the reference design runs the cluster as a separate daemon process · the inventory is not static across releases</div>

---

## The AP functional clusters — as the spec draws it

{{image:spec-ap-architecture-logical-view}}

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1 — © AUTOSAR.</div>

<div class="gloss">AP = Adaptive Platform · each 'ara::…' box is one Functional Cluster (FC) · PSE51 = the minimal single-process real-time POSIX profile exposed by the OS Interface · C++ STL = C++ Standard Template Library (each cluster's full name is printed above its ara:: namespace)</div>

---

## Execution Mgmt vs State Mgmt — EM enforces, SM decides

- **The single most-misunderstood pair.** **Execution Management (EM)** *"starts, configures,
  and stops Processes as configured in Function Group States using interfaces of the OS"* — it's
  the entry point the OS launches at boot. **But EM does not decide *which* apps run or *when***:
  *"a special FC, called State Management (SM), is the controller, commanding EM."* **SM owns the
  policy; EM only enforces the mechanism**
- The unit of composition is the **Function Group** — a named set of processes with states,
  where *"a Function Group State defines a set of active Applications for any certain situation."*
  Elegant unification: a **"Machine State" is just the Function Group State of a reserved group
  `MachineFG`** in the one `PLATFORM_CORE` cluster
- **"EM ≈ systemd" breaks in five ways**: (a) policy is externalized to a safety cluster (SM),
  not unit files; (b) the unit is a whole machine mode, not a service target; (c) EM enforces
  **resource groups** + **authenticated startup**; (d) config is **ARXML Manifests**, not
  `.service` files; (e) EM is a **certified entry point** under an ISO 26262 argument
- **Five manifest kinds**: **Execution** (per-executable), **Service Instance** (service→transport
  mapping), **Machine** (the machine with no apps), **Raw Data Stream**, **Software Distribution**

<div class="gloss">EM = Execution Management · SM = State Management · FC = Functional Cluster · Function Group = a named set of processes with states · Manifest = ARXML authored at integration time, read at startup · systemd = the Linux service manager (the tempting-but-wrong analogy)</div>

---

## `ara::com` — one API, several bindings

- AP exposes **one** application communication API, `ara::com`, on a **proxy/skeleton** model:
  the **proxy** is the local representative of a possibly-remote service; the **skeleton**
  connects the service implementation to the transport. **The app codes against `ara::com`; the
  integrator chooses the wire binding in the manifest**
- A subtlety: **serialization runs in the AA's own execution context** (the binding is compiled
  into the app binary, not a separate broker). The API supports event/callback *and* polling,
  sync + async methods (`std::future`/`std::promise`), and **zero-copy** capabilities
- **Four service elements**: an **event** (a notification carrying data, to subscribers only); a
  **trigger** (the same, *without* payload — a data-less "something happened"); a **method**
  (client/server request/response, or fire-and-forget); a **field** (a value with up to three
  accessors — notifier, getter, setter)
- **R25-11 currency**: the big `ara::com` cuts actually landed at **R23-11** — **Raw Data Streaming
  removed** and **Communication Groups marked OBSOLETE** (Comm Groups ran R20-11 → R23-11; Raw Data
  Streaming had been in `ara::com` since R19-11). R25-11 itself just **reworked the `ara::com` C++
  API** against generated headers and deleted the leftover obsolete text. Listing those as current is stale

<div class="gloss">`ara::com` = the Adaptive communication-management API · proxy = client-side stub · skeleton = server-side stub · event / trigger / method / field = the four service-element kinds · zero-copy = passing data by pointer in shared memory, no serialization copy</div>

---

## Service-oriented communication — as the spec draws it

{{image:spec-cm-service-oriented-communication}}

<div class="figsrc">Source: AUTOSAR AP_SWS_CommunicationManagement, R25-11, Figure 7.2 — © AUTOSAR.</div>

---

## Binding choice: SOME/IP vs DDS vs local IPC

- **SOME/IP** — the automotive-native option: compact serialization + **SOME/IP-SD** service
  discovery. Connection- and ID-oriented (Service ID / Instance ID / Event ID / Eventgroup) —
  familiar from CAN/UDS thinking. Subscription granularity is the **eventgroup**; SD runs **over
  UDP only** (multicast offer/find announcements + unicast subscribes)
- **DDS binding — present since R18-03** (published 23 Apr 2018; *not* R18-10, a folklore
  correction this repo already made). **Data-centric**: publish to a Topic, matched by type +
  QoS + name, no explicit peer connection. Mapping: events/triggers → **Topic + DataWriter**;
  methods & field get/set → **DDS Service (DDS-RPC)**; field notifiers → a Topic. **QoS is
  manifest-driven** (`qosProfile`), not fixed by the spec
- **Local IPC / zero-copy** — the local wire is **implementation-specific**, *not* a
  standardized inter-vendor protocol (unlike SOME/IP and RTPS). The dominant realization is
  **Eclipse iceoryx** — a low-level zero-copy shared-memory IPC ("plumbing") that higher layers wrap:
  it sits *under* both ROS 2 (via `rmw_iceoryx`) and some `ara::com` implementations, not either API itself
- **The single most transferable idea**: **the application API is protocol-agnostic; DDS/SOME-IP
  is a swappable binding underneath** — exactly like ROS 2's `rmw`/DDS layering

<div class="gloss">SOME/IP = Scalable service-Oriented MiddlewarE over IP · SD = Service Discovery · DDS = Data Distribution Service (OMG) · QoS = Quality of Service · RTPS = the DDS wire protocol · IPC = Inter-Process Communication · iceoryx = the shared-memory zero-copy IPC shared with ROS 2 · `rmw` = ROS 2's middleware-abstraction layer</div>

---

## Communication Management architecture — as the spec draws it

{{image:spec-cm-technical-architecture}}

<div class="figsrc">Source: AUTOSAR AP_SWS_CommunicationManagement, R25-11, Figure 7.1 — © AUTOSAR.</div>

<div class="gloss">ara::com = the one AP communication API · SOME/IP = Scalable service-Oriented MiddlewarE over IP (the cross-machine network binding, over TCP/IP) · IPC = Inter-Process Communication (the same-machine binding) · the app codes to ara::com; the binding beneath it is chosen in the manifest</div>

---

## The SOME/IP message header — as the spec draws it

{{image:spec-someip-message-header}}

<div class="figsrc">Source: AUTOSAR FO_PRS_SOMEIPProtocol, R25-11, Figure 5.11 — © AUTOSAR.</div>

<div class="gloss">SOME/IP = Scalable service-Oriented MiddlewarE over IP · ID = Identifier — a call is addressed by Message ID (Service ID + Method ID) and correlated by Request ID (Client ID + Session ID) · Message Type ([PRS_SOMEIP_00055]): 0x00 = REQUEST, 0x01 = REQUEST_NO_RETURN (fire-and-forget), 0x02 = NOTIFICATION, 0x80 = RESPONSE, 0x81 = ERROR · Return Code 0x00 = E_OK · 'Covered by Length' = the byte span the Length field counts · note: this crop is the Magic Cookie Message (§5.2.1.2) — a fixed-value sentinel marking message boundaries in a TCP stream; its Message Type bytes 0x01/0x02 are the sentinel's reserved constants, not the request/response codes</div>

---

## UCM — OTA the automotive way

- The unit of update is the **Software Cluster**: AP can be extended *"with new software packages
  without re-flashing the entire ECU."* The per-machine **UCM** (`ara::ucm::PackageManagement`)
  runs the workflow **Transfer → Process → Activate → (Verify/Finish or Rollback)**:
  1. **Transfer** — stream the package (`TransferStart → TransferData → TransferExit`)
  2. **Process** — `ProcessSwPackage` unpacks, validates, writes the cluster
  3. **Activate** — *UCM asks State Management for an update session*, SM stops the outdated
     clusters' processes, UCM makes the new ones available; `VerifyUpdate` → `Finish` commits
- **Rollback is best-effort, NOT guaranteed** — the spec documents a *failing* rollback
  (`UCM ROLLBACK FAILED`). For an MCU engineer: the A/B-bank reflash idea, but per-cluster and
  coordinated with a state machine, not a bootloader
- **Vehicle-wide OTA = V-UCM (Vehicle UCM)** — formerly "UCM Master," now its **own spec since
  R23-11**. It coordinates the campaign: **backend** (authenticate the Vehicle Package, resolve
  inter-cluster dependencies), **Vehicle State Manager** (apply safety conditions), and
  **driver consent**. Chain: **OEM backend → V-UCM → subordinate per-machine UCM instances**

<div class="gloss">UCM = Update and Configuration Management (per machine) · V-UCM = Vehicle UCM (vehicle-wide campaign coordinator) · Software Cluster = AP's unit of deployment/update · Vehicle Package = the signed bundle V-UCM authenticates · A/B bank = the dual-slot reflash pattern from MCU bootloaders</div>

---

## Diagnostics on AP — one cluster does DCM + DEM's jobs

- *"The DM is a diagnostic server … that realizes a UDS server instance according to
  ISO 14229-1 and SOVD according to ASAM."* Since R19-03 the interface is C++ (`ara::diag`),
  configured from the **Diagnostic Extract Template (DEXT)**. Where CP splits diagnostics into
  **DCM + DEM** BSW modules, **AP merges both roles into one cluster** — one `ara::diag` API
- **One Diagnostic Server Instance per Software Cluster**, and all instances *"share a single
  TransportLayer instance (e.g. DoIP on TCP/IP port 13400)"*
- **Transport phrasing — get it exactly right**: **DoIP (ISO 13400-2:2019) is the only
  *standardized* UDS transport for the AP DM; the SWS explicitly permits a custom transport.**
  Verbatim: *"the DoIP protocol … or a custom implementation of a transport protocol can be
  used."* **Do not repeat the refuted web claim "R24-11 added CAN transport" — a hallucination**;
  DoIP-only-as-standard is confirmed against the R24-11 **and R25-11** SWS texts (this research
  re-read both; earlier releases not re-checked)
- **SOVD is realized *inside* the DM + a SOVD Gateway — there is no separate "SOVD cluster."**
  It's a modern API over **HTTP/REST + JSON + OAuth**, self-describing, *"UDS as a subset,"* and
  can front legacy ECUs via **SOVD→UDS translation**. *ISO transition mid-flight*: R25-11 cites
  ISO 17978-3:2025/2026 & ASAM SOVD 1.1, but warns 1.1 is *"not yet (fully) supported"*

<div class="gloss">DM = Diagnostic Management (`ara::diag`) · DEXT = Diagnostic Extract Template · DoIP = Diagnostics over IP (ISO 13400) · SOVD = Service-Oriented Vehicle Diagnostics · OAuth = the token-based authorization framework · SOVD adds OAuth, proximity challenge, data-lists, bulk data — no UDS equivalent</div>

---

## PHM and Persistency — supervision and stored state

- **Platform Health Management (`ara::phm`)** is AP's analogue of CP's WdgM, required by
  ISO 26262. Three supervisions — **Alive**, **Deadline**, **Logical** — over **Checkpoints**
  apps report via `ReportCheckpoint`, aggregated into a **Global Supervision Status** per
  Function Group
- On failure, **PHM notifies State Management** (which decides + triggers recovery — e.g. restart
  a Function Group); *"if no response … is received in time, the PHM will do its own
  countermeasures"* via the **hardware watchdog**
- *Release-stamped*: **Health Channels are obsolete** (set obsolete R21-11, "Removed" R24-11) —
  material presenting them as a live PHM input is out of date
- **Persistency (`ara::per`)** provides **Key-Value Storage** and **File Storage**, with
  **redundancy** *"configured to use replication of stored data, CRCs, or Hashes"* and defined
  **Install / Update / Finalize / Roll-Back of persistent data** across Software-Cluster updates.
  The guarantee is *defined install/update/finalize semantics with a rollback path* — **not
  transparent automatic migration**
- **Log & Trace** exposes `ara::log` over the **DLT** protocol (note SOVD logging is *not*
  standardized through `ara::log`)

<div class="gloss">PHM = Platform Health Management · WdgM = CP's Watchdog Manager (the analogue) · Checkpoint = the point an app reports it reached · `ara::per` = the persistency cluster · KVS = Key-Value Storage · DLT = Diagnostic Log and Trace protocol</div>

---

## The mid-2026 reality — OSes, vendors, and the ASIL hedge

- **The OS underneath is a separate procurement + certification decision.** **QNX** is the
  de-facto safety OS — QNX OS for Safety is ISO 26262 **ASIL-D** certified (~35–38% of the
  *overall* automotive-OS market by analyst estimates — an OS-type share, not a safety-only figure).
  **Linux** carries most non-safety/ADAS compute but
  can't itself certify above ~ASIL-B (reached via a **certified hypervisor** or safety companion).
  **PikeOS, INTEGRITY, VxWorks** also appear
- **The exact hedge to keep — "ASIL-B shipping, ASIL-D programs underway":**

| Vendor / product | Stated safety (mid-2026) |
|---|---|
| **Vector MICROSAR Adaptive (Safe)** | ASIL-B in first series projects; Vector's own **ASIL-D target 2026**; a *separate* Vector–QNX deal (Jun 2024) targets ASIL-D on QNX OS, no date |
| **ETAS RTA-VRTE** | **ISO 26262 ASIL-B certified, TÜV SÜD, March 2025** |
| **Qorix** (KPIT+ZF JV, Qualcomm shareholder) | **TÜV SÜD ASIL-B certified, Aug 2025** |
| **Elektrobit EB corbos AdaptiveCore** | hypervisor **ASIL-B certified** (TÜV SÜD, 2024); AdaptiveCore itself makes no ASIL-D claim — it pairs with a separately ASIL-D-certified OS |
| **Wind River** AUTOSAR Adaptive | ASIL-D **program** (2019; shipped certificate unverified) |

- **Separate "developed to ASIL-x" (a process claim) from "certified by TÜV SÜD at ASIL-x."**
  **No fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026** — ASIL-D lives in
  the **OS (QNX) + hypervisor + vendor safety case**
- **The 2025–26 ecosystem shift**: **Eclipse S-CORE** (launched 2025-06-12, dual-language C++/Rust,
  Apache-licensed, built by the *same* AUTOSAR members — hedging, not defecting, and cooperating
  with AUTOSAR) and **SOAFEE** (Arm-led SIG defining a **cloud-native architecture** — containers,
  hypervisors, K8s, CI/CD — for mixed-criticality SDV workloads; running an AP stack as a container
  is a *demonstrated pattern*, not SOAFEE's definition). Teach SOAFEE as the environment, AP as one payload it can host

<div class="gloss">ASIL = Automotive Safety Integrity Level (QM < A < B < C < D) · TÜV SÜD = a German technical-certification body · JV = joint venture · SEooC = Safety Element out of Context · S-CORE = Eclipse Safe Open Vehicle Core · SOAFEE = Scalable Open Architecture For the Embedded Edge · SIG = Special Interest Group · K8s = Kubernetes · CI/CD = continuous integration/delivery · Silicon targets: NVIDIA Orin/Thor · NXP S32G · Qualcomm Snapdragon Ride · TI TDA4x</div>

---

## Open-source Adaptive AUTOSAR — an honest landscape

<style scoped>
  section { font-size: 20px; padding-top: 30px; }
  table { font-size: 13.5px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 12.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
  p { margin: 6px 0; }
</style>

| Project | What it really is | License | State (2026-07) |
|---|---|---|---|
| **`langroodi/Adaptive-AUTOSAR`** | the broadest readable AP *teaching* codebase — 7 `ara::` clusters (com, exec, diag, phm, sm, core, log) + a runnable simulated demo; exposes **SOME/IP-transport-level** APIs with **no generated `ara::com` Proxy/Skeleton facade**; self-describes **per cluster** against **R20-11 – R22-11** (R21-11 most-cited; R22-11 only for `com`'s E2E Profile 11 + `phm`) | MIT · C++14 | **489★, dormant** — last source commit **2023-06-22** (later commits documentation-only) |
| **`ZiadAhmed9/ara-rs`** | Rust `ProxyBase`/`SkeletonBase` + SOME/IP transport + `cargo-arxml` ARXML codegen + worked examples | Apache-2.0/MIT · Rust | created **2026-03-30**, solo author, 6★ — **promise, not track record** |
| **Eclipse S-CORE "LoLa"** | a *partial* `ara::com` communication middleware — but its API namespace is **`score::mw::com`, not `ara::com`**; part of an SDV core stack, **not an AP implementation** | Apache-2.0 · C++/Rust | very active (S-CORE launched 2025-06-12) |
| **AUTOSAR CAPI** | the **only** official, complete, code-first AP implementation — **partner-gated, NOT open source** (`code.autosar.org/capi/capi` → sign-in, verified 2026-07-16) | partner licence | "by and for AUTOSAR partners"; quarterly releases |
| **Graveyard** | `insooth/autosar-adaptive` = 64 spec PDFs + 17 spec ZIP archives (88 files total) + one `ara::per` header (33★ mislead) · `LoyenWang/AUTOSAR-Adaptive` = scaffolding whose 14 submodules point at a **deleted org (404)** · several near-empty shells | mixed | mostly abandoned, **2019 onward** |

**Takeaway:** a team **CAN** get educational AP repos, production protocol building blocks, and SDV middleware *around* AP — it **CANNOT** get a conformant, complete, production-grade **open AP stack**; the only complete official one (**CAPI**) is partner-gated, and commercial stacks (Vector, EB, ETAS, Apex.AI, Qorix) are proprietary.

<div class="gloss">AP = Adaptive Platform · `ara::` = the AP C++ API namespaces · Proxy/Skeleton = `ara::com`'s client-/service-side stubs · CAPI = Common Adaptive Platform Implementation · SDV = Software-Defined Vehicle · ★ = GitHub stars · every repo/date verified against its GitHub API on 2026-07-16</div>

---

## Inside the repo 1/4: `openAUTOSAR/classic-platform`

<style scoped>
  section { font-size: 16px; padding: 14px 40px 10px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  .cols { display: flex; gap: 22px; align-items: flex-start; }
  .tree { flex: 0 0 47%; }
  .tree pre { font-size: 11px; line-height: 1.3; margin: 0; background: #f6f8fc; }
  .tree pre code { font-size: 11px; background: transparent; }
  .pin { font-family: monospace; font-size: 12px; color: #445; margin: 8px 0 0; }
  .quote { font-size: 13px; font-style: italic; color: #33415c; line-height: 1.34; margin: 8px 0 0; }
  .quote .src { font-style: normal; color: #66708a; }
  .info { flex: 1 1 53%; }
  .info h3 { font-size: 14px; color: #2E5FAC; margin: 0 0 2px; }
  .info p { margin: 0 0 6px; line-height: 1.26; font-size: 13.5px; }
  .info code { font-size: 12px; }
  .gloss { font-size: 11px; margin-top: 7px; line-height: 1.3; }
</style>

Four repositories are worth your time. This is what is inside each one. This is the Classic Platform side of the story, the one open and complete Classic AUTOSAR stack in this repository tour.

<div class="cols">
<div class="tree">

```text
classic-platform/  (master @ 09433770, 2049 tree entries)
├── system/Os/rtos/          AUTOSAR OS kernel (static real-time)
│   ├── inc/Os.h             public OS API (tasks, alarms, events)
│   └── src/os_task.c, os_alarm.c, os_counter.c, os_sched_table.c
├── communication/           BSW comm stack
│   ├── Com/src/Com_Com.c    signal <-> I-PDU packing (Com_SendSignal)
│   ├── PduR/src/PduR.c      PDU Router (COM <-> CanIf/CanTp/Dcm)
│   └── CanIf/src/CanIf.c    CAN Interface (HW-independent CAN)
├── diagnostic/              UDS diagnostics
│   ├── Dcm/src/Dcm.c        Diagnostic Communication Manager (UDS server)
│   └── Dem/src/Dem.c        Diagnostic Event Manager (fault/DTC store)
├── system/{EcuM,BswM,SchM}  ECU state mgmt + BSW scheduler
├── boards/<~45 targets>     MPC5xxx, TC2xx/3xx, S32K, RH850, gnulinux
└── makefile, scripts/       recursive make build (no examples/ dir here)
```

<p class="pin">openAUTOSAR/classic-platform @ 09433770 · GPL-2.0</p>
<p class="quote">"This is a fork of the Arctic Core (the open source AUTOSAR embedded platform)." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p>The top-level <code>makefile</code> is the build entry. It is a recursive GNU make build where you pick a target board with <code>BOARDDIR</code> and the module directories to compile with <code>BDIR</code>. The OS kernel is always built. <code>system/Os/rtos/inc/Os.h</code> is the public header for the AUTOSAR OS kernel, and it declares the task, alarm, counter and event API. <code>communication/Com/src/Com_Com.c</code> is the COM signal input and output, where <code>Com_SendSignal</code> and <code>Com_ReceiveSignal</code> pack and unpack signals into an I-PDU. <code>diagnostic/Dcm/src/Dcm.c</code> is the UDS server and <code>diagnostic/Dem/src/Dem.c</code> is the fault and DTC store.</p>
<h3>What you can do</h3>
<p>Cross-compile for a board with <code>make BOARDDIR=&lt;board&gt; BDIR=&lt;dir&gt; CROSS_COMPILE=&lt;gcc&gt; all</code>. This builds the OS kernel, which is always built, plus the module directories you select, for one of about 45 boards. <code>scripts/build_example.sh</code> is a thin wrapper around the same build. There is no graphical development environment and no host application to run. The build produces an embedded firmware image for an MCU target. A gnulinux board also exists for host builds.</p>
<h3>Know the limits</h3>
<p>The default branch is dormant. Its last commit on <code>master</code> is from 2020-04-02, with the message "Remove GPLv2 violating files". The repository shows a later push date of 2024-08-06, but that reflects other branches, not <code>master</code>. There is no <code>examples/</code> directory at this commit, so the example applications the makefile mentions are not present here. This is a continuation of the Arctic Core codebase, a full Classic AUTOSAR basic-software stack in C across about 45 MCU board targets. Read it for the shape of a real Classic stack, not to run it.</p>
</div>
</div>

<div class="gloss">AUTOSAR OS = CP's static real-time kernel (fixed-priority, no heap) · BSW = Basic Software (CP's generated C layer, built statically, no heap) · COM = the AUTOSAR signal-packing communication module (not a serial port) · PDU = Protocol Data Unit · I-PDU = Interaction-layer PDU (the packed frame COM builds from signals) · PduR = PDU Router (routes PDUs between COM and the bus interfaces) · CanIf = CAN Interface (hardware-independent CAN) · CanTp = CAN Transport Protocol (ISO 15765-2 segmentation) · CAN = Controller Area Network (the automotive serial bus) · HW = hardware · UDS = Unified Diagnostic Services (ISO 14229) · Dcm = Diagnostic Communication Manager (the UDS server) · Dem = Diagnostic Event Manager (the fault store) · DTC = Diagnostic Trouble Code · ECU = Electronic Control Unit · EcuM = ECU Manager · BswM = Basic Software Mode Manager · SchM = BSW Scheduler · MCU = Microcontroller · CP = Classic Platform · GNU make = the GNU project build tool · GPL-2.0 = GNU General Public License version 2 (an open-source licence)</div>

<!-- ~65s | say: This is the Classic Platform repository, the one open and complete Classic AUTOSAR stack worth reading. Start at the top makefile. It is a recursive GNU make build. You pick a target board and the module directories to compile, and the OS kernel is always built. Then open Os dot h. It is the public header for the AUTOSAR OS kernel, and it declares the task, alarm, counter and event calls. Com underscore Com dot c is the communication module, where Com send signal packs an application signal into an I-PDU. The diagnostic folder holds Dcm, the UDS server, and Dem, the fault store. To build it, you cross-compile for one of about forty-five boards. There is no host application to run, because the build produces firmware for a microcontroller. Two honest limits. The main branch has been dormant since 2020, and the example applications the makefile mentions are not in the tree. Read it for the shape. -->

---

## The code 1/4: Classic AUTOSAR in C

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 12px; margin-top: 8px; }
</style>

**C: publishing a signal through AUTOSAR COM** (`openAUTOSAR/classic-platform`, dormant since 2020):

```c
uint8 Com_SendSignal(Com_SignalIdType SignalId, const void *SignalDataPtr) {
    /* @req COM334 */ /* Shall update buffer if pdu stopped, should not store trigger */
    uint8 ret = E_OK;
    boolean dataChanged = FALSE;
    if( COM_INIT != Com_GetStatus() ) {
        DET_REPORTERROR(COM_SENDSIGNAL_ID, COM_E_UNINIT);
        /*lint -e{904} Return statement is necessary in case of reporting a DET error */
        return COM_SERVICE_NOT_AVAILABLE;
    }
```

<p class="attr"><a href="https://github.com/openAUTOSAR/classic-platform/blob/09433770bebb8f27a7b480d7c96d814c68ffed3e/communication/Com/src/Com_Com.c#L44-L52">openAUTOSAR/classic-platform @ 09433770 — communication/Com/src/Com_Com.c</a></p>

**C: reporting a fault to the Diagnostic Event Manager**:

```c
void Dem_ReportErrorStatus( Dem_EventIdType eventId, Dem_EventStatusType eventStatus ) /** @req DEM206 */
{
    /* @req DEM330 */
    /* @req DEM107 */
    VALIDATE_NO_RV((DEM_UNINITIALIZED != demState), DEM_REPORTERRORSTATUS_ID, DEM_E_UNINIT);
    VALIDATE_NO_RV(IS_VALID_EVENT_STATUS(eventStatus), DEM_REPORTERRORSTATUS_ID, DEM_E_PARAM_DATA);

    SchM_Enter_Dem_EA_0();
```

<p class="attr"><a href="https://github.com/openAUTOSAR/classic-platform/blob/09433770bebb8f27a7b480d7c96d814c68ffed3e/diagnostic/Dem/src/Dem.c#L7458-L7465">openAUTOSAR/classic-platform @ 09433770 — diagnostic/Dem/src/Dem.c</a></p>

<div class="gloss"><b>What to notice:</b> <code>Com_SendSignal</code> is the COM service a task calls to publish an application signal, later packed into an I-PDU on the bus. Before it does any work it checks the module state. If COM is not initialized, it reports a development-time error through the DET and returns a service-not-available code. The <code>/* @req COM334 */</code> comment ties this line to a numbered requirement in the AUTOSAR COM specification, and that traceability tag is the signature style of the whole codebase. <code>Dem_ReportErrorStatus</code> is the entry any basic-software module calls to report a fault as passed or failed by numeric event id. The two <code>VALIDATE_NO_RV</code> macros are the standard guard: they reject calls made before init or with an out-of-range status by reporting to the DET. <code>SchM_Enter_Dem_EA_0()</code> then opens a named exclusive area, so the fault-status update that follows is atomic against task preemption on the ECU. Both patterns, the requirement tags and the init-and-exclusive-area guards, are the static-kernel Classic idiom. · COM = the AUTOSAR signal-packing communication module (not a serial port) · DET = Default Error Tracer (AUTOSAR's development-time error hook) · PDU = Protocol Data Unit · I-PDU = Interaction-layer PDU (the packed frame COM builds from signals) · DEM = Diagnostic Event Manager · BSW = Basic Software (CP's generated C layer) · SchM = BSW Scheduler; the <code>SchM_Enter</code>/<code>SchM_Exit</code> pair brackets an exclusive area (EA), an atomic section against preemption · id = identifier · ECU = Electronic Control Unit</div>

<!-- ~65s | say: These are two real functions from the Classic stack, and they show the house style. The first is Com send signal, the service a task calls to publish an application signal. Before it does any work, it checks that the module was initialized. If it was not, it reports a development-time error through the Default Error Tracer and returns a service-not-available code. The comment tagged requirement COM three three four links that line to a numbered requirement in the AUTOSAR COM specification. The second function is Dem report error status. Any basic-software module calls it to report a fault as passed or failed, using a numeric event id. The two validate macros are the standard guard. They reject calls made before init or with a bad status. Then SchM enter opens a named exclusive area, so the fault update that follows cannot be interrupted by another task. Requirement tags and state guards on every entry point are the static-kernel Classic idiom. -->

---

## Inside the repo 2/4: `langroodi/Adaptive-AUTOSAR`

<style scoped>
  section { font-size: 16px; padding: 20px 40px 16px; }
  h2 { font-size: 25px; margin: 0 0 8px; }
  .cols { display: flex; gap: 22px; align-items: flex-start; }
  .tree { flex: 0 0 47%; }
  .tree pre { font-size: 11px; line-height: 1.3; margin: 0; background: #f6f8fc; }
  .tree pre code { font-size: 11px; background: transparent; }
  .pin { font-family: monospace; font-size: 12px; color: #445; margin: 8px 0 0; }
  .quote { font-size: 13px; font-style: italic; color: #33415c; line-height: 1.34; margin: 8px 0 0; }
  .quote .src { font-style: normal; color: #66708a; }
  .info { flex: 1 1 53%; }
  .info h3 { font-size: 15px; color: #2E5FAC; margin: 0 0 3px; }
  .info p { margin: 0 0 9px; line-height: 1.34; }
  .info code { font-size: 12.5px; }
  .gloss { font-size: 12px; margin-top: 10px; }
</style>

<div class="cols">
<div class="tree">

```text
Adaptive-AUTOSAR/
|-- src/
|   |-- ara/              # seven AP interface clusters
|   |   |-- com/          # SOME/IP transport layer
|   |   |-- core/         # Result, ErrorCode, specifiers
|   |   |-- diag/         # Diagnostic Management
|   |   `-- exec/         # Execution Management
|   |   `-- log/ phm/ sm/ # logging, health, state
|   |-- application/      # simulated demo + managers
|   `-- arxml/            # ARXML reader (pugixml)
|-- configuration/        # *.arxml launch manifests
`-- test/ara/             # GoogleTest units
```

<p class="pin">langroodi/Adaptive-AUTOSAR @ 866d158 · MIT</p>
<p class="quote">"The goal of this project is to implement the interfaces defined by the standard for educational purposes." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p><code>README.md</code> states what the project is and lists the exact build, test and run commands. <code>src/main.cpp</code> is the ~55-line entry point: it builds Execution Management, spins a polling loop, and passes in the manifests. <code>src/ara/exec/execution_client.h</code> shows an app reporting its state to Execution Management; its private members reveal the call is really a SOME/IP RPC, not a generated ara::com proxy. <code>CMakeLists.txt</code> pins C++14, fetches GoogleTest, and defines the executable plus two test targets.</p>
<h3>What you can do</h3>
<p>Configure and build with CMake using GCC or Clang, then run the unit tests with <code>ctest</code>. Launch the simulation by passing the four <code>.arxml</code> manifest files to the executable.</p>
<h3>Know the limits</h3>
<p>The demo is not offline. It needs a Volvo API key, an OAuth 2.0 token and live network access to the Volvo Extended Vehicle REST API. The code stops at the SOME/IP transport level, with no generated ara::com Proxy/Skeleton facade. It is dormant, with its last source commit on 2023-06-22. Read it for the shape, not for production.</p>
</div>
</div>

<div class="gloss">AP = Adaptive Platform · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · Proxy/Skeleton = <code>ara::com</code>'s client-/service-side stubs · SOME/IP = Scalable service-Oriented MiddlewarE over IP · RPC = Remote Procedure Call · ARXML = the AUTOSAR XML manifest and config format · OAuth = Open Authorization (token-based access) · REST = Representational State Transfer (an HTTP API style) · MIT = an open-source licence</div>

<!-- ~65s | say: This is the second of four repositories worth your time. langroodi Adaptive-AUTOSAR is the teaching codebase. Start with the README. It says in one paragraph what the project is, and it lists the exact build, test and run commands. Then open main.cpp. It is about fifty-five lines. It builds Execution Management, spins a polling loop, and passes in the manifest files. The execution-client header is the one to study. It shows an app reporting its state to Execution Management, and its private members reveal that the call is really a SOME/IP remote procedure call, not a generated ara::com proxy. To run it, configure and build with CMake, run the unit tests with ctest, then launch by passing the four ARXML manifest files. Two honest limits. The demo is not offline. It needs a Volvo API key, an OAuth token and live network access. And the code has been dormant since 2023. Read it for the shape. -->

---

## The code 2/4: `langroodi/Adaptive-AUTOSAR`

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 12px; margin-top: 8px; }
</style>

**C++: the abstract SOME/IP RPC client** (`langroodi/Adaptive-AUTOSAR`, dormant since 2023):

```cpp
                class RpcClient
                {
                public:
                    /// @brief SOME/IP RPC response handler type
                    using HandlerType = std::function<void(const SomeIpRpcMessage &)>;

                private:
                    const uint8_t mProtocolVersion;
                    const uint8_t mInterfaceVersion;
                    std::map<uint32_t, uint16_t> mSessionIds;
                    std::map<uint32_t, HandlerType> mHandlers;
```

<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/com/someip/rpc/rpc_client.h#L19-L29">langroodi/Adaptive-AUTOSAR @ 866d158 — src/ara/com/someip/rpc/rpc_client.h</a></p>

**C++: composing the Execution Management cluster**:

```cpp
                ara::com::someip::rpc::SocketRpcServer _rpcServer(
                    Poller,
                    cRpcConfiguration.ipAddress,
                    cRpcConfiguration.portNumber,
                    cRpcConfiguration.protocolVersion);

                ara::exec::ExecutionServer _executionServer(&_rpcServer);

                std::set<std::pair<std::string, std::string>> _functionGroupStates;
                std::map<std::string, std::string> _initialState;
                fillStates(cConfigFilepath, _functionGroupStates, _initialState);
```

<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/application/platform/execution_management.cpp#L146-L156">langroodi/Adaptive-AUTOSAR @ 866d158 — src/application/platform/execution_management.cpp</a></p>

<div class="gloss"><b>What to notice:</b> <code>RpcClient</code> is the abstract SOME/IP request-and-response client that the platform's wiring is built on. Its public <code>HandlerType</code> is just a <code>std::function</code> taking a decoded message. Its private state is two maps keyed by a packed service and method id, one tracking per-method session ids and one holding the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass such as <code>SocketRpcServer</code> supplies the actual send. In the second snippet a concrete <code>SocketRpcServer</code> is built from the parsed RPC configuration (address, port, protocol version) and handed by pointer into an <code>ara::exec::ExecutionServer</code>, so the execution server speaks to clients only through the SOME/IP RPC abstraction. The last lines load the function-group states and their initial state from the ARXML model, which is the config-driven, model-first style of the codebase. · SOME/IP = Scalable service-Oriented MiddlewarE over IP · RPC = Remote Procedure Call · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · <code>ara::exec</code> = AP's Execution Management API · ARXML = the AUTOSAR XML manifest and config format · id = identifier · AP = Adaptive Platform</div>

<!-- ~65s | say: Now the same platform in the Adaptive teaching repository. The first snippet is the class shape. RpcClient is the abstract SOME/IP request and response client that all the wiring is built on. Its public handler type is just a function that takes a decoded message. Its private state is two maps, one tracking per-method session ids and one holding the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass supplies the actual send. The second snippet is the Execution Management entry point. A socket RPC server is built from the parsed configuration, the address, the port and the protocol version. That server is then handed by pointer into an execution server, so the execution server talks to clients only through the RPC abstraction. The last lines load the function-group states and their initial state from the ARXML model. That config-driven, model-first style runs through the whole codebase. -->

---

## Inside the repo 3/4: Eclipse S-CORE `communication` (LoLa)

<style scoped>
  section { font-size: 16px; padding: 20px 40px 16px; }
  h2 { font-size: 25px; margin: 0 0 8px; }
  .cols { display: flex; gap: 22px; align-items: flex-start; }
  .tree { flex: 0 0 47%; }
  .tree pre { font-size: 11px; line-height: 1.3; margin: 0; background: #f6f8fc; }
  .tree pre code { font-size: 11px; background: transparent; }
  .pin { font-family: monospace; font-size: 12px; color: #445; margin: 8px 0 0; }
  .quote { font-size: 13px; font-style: italic; color: #33415c; line-height: 1.34; margin: 8px 0 0; }
  .quote .src { font-style: normal; color: #66708a; }
  .info { flex: 1 1 53%; }
  .info h3 { font-size: 15px; color: #2E5FAC; margin: 0 0 3px; }
  .info p { margin: 0 0 9px; line-height: 1.34; }
  .info code { font-size: 12.5px; }
  .gloss { font-size: 12px; margin-top: 10px; }
</style>

<div class="cols">
<div class="tree">

```text
communication/
├── score/mw/com/                  # score::mw::com API (C++)
│   ├── impl/                      # core middleware
│   │   ├── bindings/lola/         # LoLa shared-memory IPC
│   │   ├── bindings/mock_binding/ # test-double binding
│   │   ├── configuration/         # service / instance config
│   │   └── rust/com-api/          # Rust API + FFI bridge
│   ├── doc/tutorial/              # API walkthrough
│   ├── example/com-api-example/   # runnable example
│   └── test/                      # integration tests
├── score/message_passing/         # low-level messaging
└── bazel/                         # Bazel build config
```

<p class="pin">eclipse-score/communication @ 6acba35 · Apache-2.0</p>
<p class="quote">"A high-performance, safety-critical communication middleware implementation based on the Adaptive AUTOSAR Communication Management specification." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p><code>README.md</code> gives the overview and sketches the two-layer design: <code>mw::com</code> over a message-passing layer. <code>score/mw/com/README.md</code> is the API user guide, your first stop after that. <code>score/mw/com/types.h</code> is the public types header, with the Proxy and Skeleton handles and the instance-specifier types you code against (the README maps its ASIL-B and QM QoS support to this header). <code>score/mw/com/impl/bindings/lola/proxy.h</code> is where the concrete zero-copy shared-memory layer lives, under the abstract API in <code>impl/</code>.</p>
<h3>What you can do</h3>
<p>Build and test with Bazel from the repo root: <code>bazel build //...</code> and <code>bazel test //...</code>. You need GCC 12 or newer with C++17, and Linux (Ubuntu 24.04+) or QNX. A DevContainer is the recommended setup.</p>
<h3>Know the limits</h3>
<p>The namespace is <code>score::mw::com</code>, not <code>ara::com</code>, and it is a partial ara::com implementation. Its shared-memory IPC is declared on boost.interprocess, not iceoryx. It self-describes as ASIL-B qualified. It is part of Eclipse S-CORE, which makes no official Adaptive AUTOSAR compatibility claim.</p>
</div>
</div>

<div class="gloss">LoLa = S-CORE's Low-Latency communication module · S-CORE = Eclipse Safe Open Vehicle Core · AP = Adaptive Platform · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · Proxy/Skeleton = <code>ara::com</code>'s client-/service-side stubs · IPC = Inter-Process Communication · QoS = Quality of Service · ASIL = Automotive Safety Integrity Level (ISO 26262) · FFI = Foreign Function Interface (the C++/Rust bridge) · Apache-2.0 = an open-source licence</div>

<!-- ~65s | say: The third repository is Eclipse S-CORE's communication module, nicknamed LoLa. Start with the top-level README. It states what LoLa is and sketches the two-layer design, the middleware over a message-passing layer. Then read the API user guide under score, mw, com. The public types header shows the Proxy and Skeleton handles and the instance-specifier types you code against; the README maps its ASIL-B and QM quality-of-service support to this header. The concrete zero-copy shared-memory layer lives in the LoLa binding under impl. To build and test, use Bazel from the repo root: bazel build slash slash dot dot dot, and bazel test the same way. You need GCC twelve or newer with C plus plus seventeen. Now the limits. The namespace is score mw com, not ara com, and it is only a partial ara com implementation. Its shared memory runs on boost interprocess, not iceoryx. It is ASIL-B qualified, and it makes no official Adaptive AUTOSAR compatibility claim. -->

---

## The code 3/4: Eclipse S-CORE LoLa

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 12px; margin-top: 8px; }
</style>

**C++: the service (skeleton) side** (`eclipse-score/communication`, LoLa):

```cpp
    auto instance_specifier = score::mw::com::InstanceSpecifier::Create(std::string{"MyHelloWorldServiceInstance"});
    SCORE_LANGUAGE_FUTURECPP_ASSERT_PRD_MESSAGE(instance_specifier.has_value(), "Failed to create InstanceSpecifier!");

    auto hello_world_service_instance_result = HelloWorldSkeleton::Create(instance_specifier.value());
    SCORE_LANGUAGE_FUTURECPP_ASSERT_PRD_MESSAGE(hello_world_service_instance_result.has_value(),
                                                "Failed to create HelloWorldSkeleton instance!");
    auto hello_world_service_instance = std::move(hello_world_service_instance_result).value();

    auto offer_result = hello_world_service_instance.OfferService();
    SCORE_LANGUAGE_FUTURECPP_ASSERT_PRD_MESSAGE(offer_result.has_value(),
                                                "Failed to offer HelloWorldSkeleton instance!");
```

<p class="attr"><a href="https://github.com/eclipse-score/communication/blob/6acba35a973db81c0fd2a97e4248db0f3eeeb5d1/score/mw/com/doc/tutorial/chapter_1/provider.cpp#L37-L47">eclipse-score/communication @ 6acba35 — score/mw/com/doc/tutorial/chapter_1/provider.cpp</a></p>

**C++: the client (proxy) side**:

```cpp
    auto proxy_result = HelloWorldProxy::Create(service_handle.value());
    if (!proxy_result)
    {
        std::cerr << "Failed to create HelloWorldProxy: " << proxy_result.error() << std::endl;
        exit(1);
    }

    auto hello_world_proxy = std::move(proxy_result).value();
    const auto subscribe_result = hello_world_proxy.message.Subscribe(1);
```

<p class="attr"><a href="https://github.com/eclipse-score/communication/blob/6acba35a973db81c0fd2a97e4248db0f3eeeb5d1/score/mw/com/doc/tutorial/chapter_1/consumer.cpp#L58-L66">eclipse-score/communication @ 6acba35 — score/mw/com/doc/tutorial/chapter_1/consumer.cpp</a></p>

<div class="gloss"><b>What to notice:</b> The first snippet is the service (skeleton) side. It names the instance with <code>InstanceSpecifier::Create</code>, builds the service with <code>HelloWorldSkeleton::Create</code> (the alias for <code>AsSkeleton&lt;HelloWorldInterface&gt;</code>), and publishes it with <code>OfferService()</code>. The second snippet is the client (proxy) side. It builds a typed proxy from a discovered service handle with <code>HelloWorldProxy::Create</code>, then subscribes to the typed event with <code>message.Subscribe(1)</code>, where 1 is the sample-cache depth. <b>The point:</b> name-the-instance-then-offer and typed-proxy-then-subscribe are exactly ara::com's skeleton and proxy idioms. Only two things differ. The namespace is <code>score::mw::com</code>, not <code>ara::com</code>. And errors come back as checkable <code>Result</code> values instead of thrown exceptions. · LoLa = S-CORE's Low-Latency communication module · S-CORE = Eclipse Safe Open Vehicle Core · <code>score::mw::com</code> = S-CORE's Communication Management API · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · Skeleton = the service-side stub · Proxy = the client-side stub · AP = Adaptive Platform</div>

<!-- ~65s | say: This is Eclipse S-CORE's LoLa, and the point is the shape. The first snippet is the service side, the skeleton. It names the instance with instance specifier create. It builds the service with HelloWorldSkeleton create. And it publishes it with offer service. That name-the-instance then offer-service shape is exactly the Adaptive skeleton idiom. The second snippet is the client side, the proxy. It builds a typed proxy from a discovered service handle, then subscribes to the typed event, where the number one is the sample-cache depth. Typed-proxy creation plus event subscribe is exactly the Adaptive proxy idiom. So here is the takeaway. The API shape matches ara com almost line for line. Only two things differ. The namespace is score mw com, not ara com. And errors come back as checkable result values instead of thrown exceptions. Same idiom, different namespace. -->

---

## Inside the repo 4/4: COVESA `vsomeip`

<style scoped>
  section { font-size: 16px; padding: 20px 40px 16px; }
  h2 { font-size: 25px; margin: 0 0 8px; }
  .cols { display: flex; gap: 22px; align-items: flex-start; }
  .tree { flex: 0 0 47%; }
  .tree pre { font-size: 11px; line-height: 1.3; margin: 0; background: #f6f8fc; }
  .tree pre code { font-size: 11px; background: transparent; }
  .pin { font-family: monospace; font-size: 12px; color: #445; margin: 8px 0 0; }
  .quote { font-size: 13px; font-style: italic; color: #33415c; line-height: 1.34; margin: 8px 0 0; }
  .quote .src { font-style: normal; color: #66708a; }
  .info { flex: 1 1 53%; }
  .info h3 { font-size: 15px; color: #2E5FAC; margin: 0 0 3px; }
  .info p { margin: 0 0 8px; line-height: 1.33; }
  .info code { font-size: 12.5px; }
  .boundary { font-size: 14px; margin: 10px 0 0; line-height: 1.35; }
  .gloss { font-size: 12px; margin-top: 8px; }
</style>

<div class="cols">
<div class="tree">

```text
vsomeip/  (tag 3.7.4)
├── interface/vsomeip/        # public API you code against
│   ├── application.hpp       # offer/request, send, handlers
│   └── runtime.hpp           # factory: app, message, payload
├── implementation/           # the stack internals
│   ├── endpoints/            # TCP/UDP client & server sockets
│   ├── routing/              # routing manager (dispatch)
│   ├── service_discovery/    # SOME/IP-SD: offer/find/sub
│   └── e2e_protection/       # End-to-End (E2E) protection
├── config/                   # ready-to-use JSON configs
└── examples/                 # request/response, subscribe
```

<p class="pin">COVESA/vsomeip @ 7bcc1e0 · MPL-2.0 (tag 3.7.4)</p>
<p class="quote">"The vSomeIP stack implements the ... Scalable service-Oriented MiddlewarE over IP (SOME/IP) ... Protocol." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p><code>interface/vsomeip/runtime.hpp</code> is the singleton factory you call first: <code>runtime::get()</code> hands you the object that creates your application, messages and payloads. <code>interface/vsomeip/application.hpp</code> is the main interface you code against: start and stop, <code>offer_service</code> and <code>request_service</code>, <code>send</code>, and <code>register_message_handler</code>. <code>examples/request-sample.cpp</code> is a short, runnable client paired with <code>response-sample.cpp</code>. <code>implementation/routing/src/routing_manager_impl.cpp</code> is where the routing manager dispatches messages between local apps and remote TCP/UDP endpoints.</p>
<h3>What you can do</h3>
<p>Build with CMake: <code>mkdir build</code>, <code>cd build</code>, <code>cmake ..</code>, <code>make</code>. You need a C++20 compiler and Boost 1.75 or newer. Run an example as two processes, each pointed at a JSON config through the <code>VSOMEIP_CONFIGURATION</code> environment variable, for example <code>config/vsomeip-local.json</code>.</p>
<h3>Know the limits</h3>
<p>This is the wire binding under <code>ara::com</code>, never the ara::com API, and the repo never mentions ara::com. The samples assume two devices on the same network, so the addresses in the config files must be adapted.</p>
</div>
</div>

<div class="gloss">COVESA = Connected Vehicle Systems Alliance · SOME/IP = Scalable service-Oriented MiddlewarE over IP · SD = Service Discovery · E2E = End-to-End protection · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · TCP/UDP = the two IP transport protocols · JSON = JavaScript Object Notation (config format) · CAPI = Common Adaptive Platform Implementation · AP = Adaptive Platform · MPL-2.0 = Mozilla Public License (open-source)</div>

<!-- ~65s | say: The fourth repository is COVESA vsomeip, the SOME/IP stack that BMW originated. Start with runtime dot h-p-p. It is the singleton factory you call first. runtime get hands you the object that creates your application, your messages and your payloads. Then read application dot h-p-p, the interface you code against: start and stop, offer service and request service, send, and register message handler. The request sample is a short runnable client, and the routing manager implementation is where messages are dispatched to local apps and remote TCP and UDP endpoints. To build, use CMake, and you need a C plus plus twenty compiler and Boost. Run an example as two processes, each pointed at a JSON config through the configuration environment variable. The key limit: this is the wire binding under ara com, never the ara com API. The repo never mentions ara com. That is the honest boundary for all four. -->

---

## The code 4/4: COVESA `vsomeip`

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 12px; margin-top: 8px; }
  .boundary { font-size: 14px; margin: 8px 0 0; line-height: 1.35; }
</style>

**C++: the SOME/IP service coming up** (`COVESA/vsomeip`):

```cpp
    bool init() {
        std::scoped_lock its_lock(mutex_);

        if (!app_->init()) {
            std::cerr << "Couldn't initialize application" << std::endl;
            return false;
        }
        app_->register_state_handler(std::bind(&service_sample::on_state, this, std::placeholders::_1));
        app_->register_message_handler(SAMPLE_SERVICE_ID, SAMPLE_INSTANCE_ID, SAMPLE_METHOD_ID,
                                       std::bind(&service_sample::on_message, this, std::placeholders::_1));

        std::cout << "Static routing " << (use_static_routing_ ? "ON" : "OFF") << std::endl;
        return true;
    }
```

<p class="attr"><a href="https://github.com/COVESA/vsomeip/blob/7bcc1e06f16a774e70931ed641f475fbba9c8c64/examples/response-sample.cpp#L30-L43">COVESA/vsomeip @ 7bcc1e0 — examples/response-sample.cpp</a></p>

**C++: the client firing a request**:

```cpp
                if (is_available_) {
                    app_->send(request_);
                    std::cout << "Client/Session [" << std::hex << std::setfill('0') << std::setw(4) << request_->get_client() << "/"
                              << std::setw(4) << request_->get_session() << "] sent a request to Service [" << std::setw(4)
                              << request_->get_service() << "." << std::setw(4) << request_->get_instance() << "]" << std::endl;
                    blocked_ = false;
                }
```

<p class="attr"><a href="https://github.com/COVESA/vsomeip/blob/7bcc1e06f16a774e70931ed641f475fbba9c8c64/examples/request-sample.cpp#L126-L132">COVESA/vsomeip @ 7bcc1e0 — examples/request-sample.cpp</a></p>

<div class="gloss"><b>What to notice:</b> The first snippet is the SOME/IP service coming up. <code>init()</code> attaches the application to the vsomeip routing with <code>app_->init()</code>, then <code>register_message_handler</code> for one service, instance and method triple, so every incoming request for that triple is dispatched to <code>on_message</code>. <code>register_state_handler</code> installs a second callback that fires when the app reaches <code>ST_REGISTERED</code>, which is the cue to actually offer the service on the network. The second snippet is the client firing the request. Once the availability handler reports the service is up, it calls <code>app_->send(request_)</code> on the message it pre-addressed with set_service, set_instance and set_method. vsomeip stamps the outgoing message with a client id and a session id, printed in the log line, and the matching response arrives later in the client's own <code>on_message</code> handler. · vsomeip = COVESA's open SOME/IP stack · COVESA = Connected Vehicle Systems Alliance · SOME/IP = Scalable service-Oriented MiddlewarE over IP · id = identifier · <code>ara::com</code> = AP's Communication Management API · AP = Adaptive Platform · CAPI = Common Adaptive Platform Implementation</div>

<p class="boundary"><b>The honest boundary: building blocks and teaching code are open. A complete, conformant, open AP stack does not exist. The one complete official implementation, CAPI, is partner-gated.</b></p>

<!-- ~65s | say: The last repository is COVESA vsomeip, the wire binding that sits under ara com. The first snippet is the service coming up. Init attaches the application to the vsomeip routing, then registers a message handler for one service, instance and method triple, so every matching request is dispatched to on message. It also registers a state handler, which fires when the app is registered and is the cue to actually offer the service on the network. The second snippet is the client firing the request. Once the availability handler reports the service is up, it calls send on the pre-addressed request. vsomeip stamps the message with a client id and a session id, and the matching response arrives later in the client's own handler. Now the honest boundary for the whole tour. The building blocks and the teaching code are open. A complete, conformant, open Adaptive stack does not exist. The one complete official implementation is partner-gated. -->

---

## The real shape of AP code

<style scoped>
  section { font-size: 18px; padding-top: 22px; }
  pre { font-size: 13px; line-height: 1.3; margin: 6px 0; }
  pre code { font-size: 13px; }
  h2 { margin-bottom: 4px; }
  p { margin: 4px 0; }
  .attr { font-size: 12.5px; color:#66708a; margin: 2px 0 10px 0; }
  .gloss { font-size: 12.5px; margin-top: 8px; }
</style>

**C++ — the Adaptive Application → Execution Management state handshake** (`langroodi/Adaptive-AUTOSAR`, dormant since 2023-06-22):

```cpp
            /// @brief Report the application internal state to Execution Management
            /// @param state Application current internal state
            /// @returns Void Result if the state reporting was successful, otherwise a Result containing the occurred error
            ara::core::Result<void> ReportExecutionState(
                ExecutionState state) const;
```
<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L54-L58">langroodi/Adaptive-AUTOSAR @ 866d158 — src/ara/exec/execution_client.h</a></p>

<div class="gloss">What to notice: `ReportExecutionState` returns an **`ara::core::Result<void>`** — AP signals errors as a *returned value*, **not a thrown exception**; it is the **contract every AA implements** so EM knows it reached `kRunning`. On the `ara::com` side the skeleton lifecycle is likewise spec-named: **`OfferService()` / `StopOfferService()` on the `ServiceSkeleton` class** ([SWS_CM_00101] / [SWS_CM_00111], AP_SWS_CommunicationManagement). Educational caveat: this C++ repo is **dormant since 2023-06-22 (3 years cold)** — read it to learn the shape; it is not conformant or production-grade. AA = Adaptive Application · EM = Execution Management.</div>

---

## Building blocks you can actually ship today

<style scoped>
  section { font-size: 20px; padding-top: 30px; }
  table { font-size: 13.5px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 12.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
  p { margin: 6px 0; }
</style>

| Building block | License | Activity (2026) | Exact relation to `ara::com` |
|---|---|---|---|
| **vsomeip** (COVESA, BMW-originated) | MPL-2.0 | release **3.7.4, 2026-07-06** — actively maintained | a standalone **SOME/IP + Service Discovery + E2E** stack = the standardized **network binding** *under* `ara::com`, not an `ara::com` API; the repo **never mentions `ara::com`**, though AUTOSAR appears around its E2E support (changelog *"Support AutoSAR E2E Profile 4"*, E2E test docs citing the AUTOSAR E2E/CRC specs, two source files citing AUTOSAR FO R22-11) |
| **Eclipse iceoryx** | Apache-2.0 | **v2.0.8, 2026-05-19** — maintained | zero-copy shared-memory IPC; ships `iceoryx-automotive-soa`, per its README *"a Binding for automotive frameworks like AUTOSAR Adaptive `ara::com`"* (its "Where is iceoryx used" table labels **RTA-VRTE (ETAS)** and **AVIN AGNOSAR** as AUTOSAR Adaptive Platform products, while **Apex.Ida is listed as safe/certified middleware without the AP label**) |
| **Eclipse iceoryx2** | Apache-2.0 OR MIT | **v0.9.3, 2026-07-08** (pre-1.0) — very active | Rust-core zero-copy IPC successor; its README/FAQ describe safety-critical ambitions (*"designed to operate in safety-critical systems"*) but make **no AUTOSAR / ISO 26262 / ASIL certification claim** |
| **eProsima Fast DDS** | Apache-2.0 | **v3.6.2, 2026-07-02** — very active | full OMG **DDS/RTPS**; DDS is one of the three standardized `ara::com` network bindings (SOME/IP · Signal-Based · DDS), so technically eligible — but **not** the documented AP Demonstrator binding (that reference work is RTI Connext, proprietary) |
| **CommonAPI C++ / -SomeIP** (COVESA) | MPL-2.0 | **dormant since 2024-10-09** | Franca-IDL proxy/stub codegen whose shape *rhymes with* `ara::com` proxies/skeletons — but a separate, **non-AUTOSAR** lineage |

**Takeaway:** the **protocol/transport layer** of AP is fully available as production open source — the **`ara::` API layer** is not.

<div class="gloss">SOME/IP = Scalable service-Oriented MiddlewarE over IP · SD = Service Discovery · E2E = End-to-End protection · IPC = Inter-Process Communication · DDS/RTPS = Data Distribution Service + its wire protocol (OMG) · MPL = Mozilla Public License · Franca IDL = the interface-definition language CommonAPI generates from (the non-AUTOSAR analogue to ARXML) · all versions/dates verified 2026-07-16</div>

---

## The open ecosystem around AP — and where the line sits

<style scoped>
  section { font-size: 18.5px; padding-top: 24px; }
  h2 { margin-bottom: 6px; }
  li { margin-bottom: 6px; }
  .gloss { font-size: 12.5px; margin-top: 8px; }
</style>

- **Eclipse S-CORE** (Apache-2.0, dual-language **C++/Rust** — never Rust-first; launched **2025-06-12**; backers BMW Group, Mercedes-Benz, Bosch, ETAS, QNX, Qorix, Accenture) is an open SDV **core stack**, **not an AP implementation**, and **makes no AP-compatibility claim** — no official statement either way (community discussions about a compatibility/mapping layer exist — eclipse-score GitHub discussions #759, #882 — but nothing official). Its comms module **LoLa** is *"a communication middleware implementation based on the Adaptive AUTOSAR Communication Management specification"* / *"Partial implementation of Adaptive AUTOSAR Communication Management (ara::com)"* (its README also self-describes **ASIL-B qualified**) — yet its API namespace is **`score::mw::com`, not `ara::com`**, and its IPC is built on **boost.interprocess, not iceoryx**
- **Eclipse OpenSOVD** (Apache-2.0, mostly Rust, Eclipse **Incubating** (proposed 2025-05-26), active into July 2026) — an open implementation of **SOVD (ISO 17978)** that explicitly **bridges AUTOSAR-Adaptive HPCs and legacy UDS ECUs** and complements S-CORE. It sits exactly on this deck's **Fleet ↔ CP+AP walkthrough** + **fleet-uds-flow** SOVD path: [its Rust REST route table](https://github.com/eclipse-opensovd/opensovd-core/blob/fe75a8e3a9142d11a0ed7152610e29003493de2a/opensovd-server/src/routes/mod.rs#L4-L18) enumerates the `components → data` SOVD endpoints a diagnostics client speaks
- **Same neighbourhood, none are AP** (all Apache-2.0, all active): **Eclipse Ankaios** (workload orchestration for automotive HPCs — conceptually overlaps AP Execution Management) · **Eclipse Kuksa** (VSS signal databroker, Rust) · **Eclipse uProtocol** (transport-agnostic messaging; originated as a GM contribution, pairs with COVESA VSS/uServices)
- **Classic contrast**: Classic AUTOSAR has an open **GPL-2.0** lineage (Arctic Core, continued as **`openAUTOSAR/classic-platform`**, 2453 commits) — **Adaptive has no equivalent open conformant stack**
- **The boundary-keeper**: the one complete official AP implementation is **CAPI**, *"developed collaboratively by and for AUTOSAR partners"* — **partner-gated, not open source.** That is why the honest line holds: open AP means education + building blocks + surrounding middleware, **not a production AP stack**

<div class="gloss">SDV = Software-Defined Vehicle · LoLa = S-CORE's Low-Latency communication module · SOVD = Service-Oriented Vehicle Diagnostics (ISO 17978) · HPC = High-Performance Computer · UDS = Unified Diagnostic Services · VSS = Vehicle Signal Specification · CAPI = Common Adaptive Platform Implementation · the concrete AUTOSAR↔Eclipse tie is the SDV Alliance (formed March 2023, launched CES 2024) — see references</div>

---

## CP vs AP — the platform split (1/2)

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| Dimension | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **OS / kernel** | AUTOSAR OS — static real-time kernel (SC1–SC4, no MMU) | not a new OS: an **OS Interface** on POSIX **PSE51** over Linux/QNX/PikeOS |
| **Language & API** | C; RTE-generated `Rte_Read/Write/Call` | C++14 (C++17 via MISRA C++:2023 merge); `ara::*` |
| **Config time** | fully **static** — fixed pre-build (ECUC) → one binary | **dynamic** — manifests bound late; discovery + start/stop at runtime |
| **Communication** | **signal**-oriented — COM packs signals→I-PDUs on CAN/LIN/FlexRay/Ethernet | **service**-oriented — `ara::com` proxy/skeleton over **SOME/IP or DDS** |
| **Scheduling** | static priority table; hard RT by construction | POSIX `SCHED_FIFO`/`RR`, optional `SCHED_DEADLINE`; determinism *engineered* |
| **Memory** | static allocation; MPU partitions; **no heap in safety paths** | **dynamic allocation allowed and assumed** (C++/STL); deterministic allocators |

<div class="gloss">SC = Scalability Class · MMU = Memory Management Unit · PSE51 = minimal single-process POSIX profile · ECUC = ECU Configuration · I-PDU = Interaction-layer PDU · `SCHED_DEADLINE` = Linux EDF scheduler · every row is sourced in the references</div>

---

## CP vs AP — the platform split (2/2)

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| Dimension | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **Safety** | mature ISO 26262 **up to ASIL D** (first ASIL-D AUTOSAR impl certified 2016) | documented "up to ASIL D," harder in practice; **ASIL-B shipping, ASIL-D underway** |
| **Update** | reflash the **whole ECU** via bootloader/UDS (0x34/0x36/0x37) | **UCM** — install/update individual Software Clusters; OTA-native |
| **Diagnostics** | **DCM + DEM** — UDS over DoCAN/DoIP | **DM** (`ara::diag`) — UDS server *and* SOVD; DoIP only standardized transport (custom permitted) |
| **Tooling** | Vector MICROSAR / EB tresos / ETAS RTA-CAR; DaVinci | Vector MICROSAR Adaptive / EB corbos / ETAS RTA-VRTE / Qorix |
| **Silicon** | MCUs: Infineon AURIX, NXP S32K, Renesas RH850 | SoCs: NVIDIA Orin/Thor, Qualcomm, NXP S32G, Renesas R-Car |
| **Typical use** | brakes, EPS, body, powertrain — ASIL B–D actuators | ADAS/AD, HPC gateways, infotainment — often mixed-criticality with a CP safety island |

- **The "up to ASIL D" trap**: on paper both are "up to ASIL D." In practice AP's ASIL-D is
  achieved via mixed-criticality partitioning + a CP/lockstep companion — **not** the Linux/QNX
  host alone. **Do not call AP "low-ASIL," but do not call it "ASIL-D certified" either**

<div class="gloss">DCM/DEM = CP's diagnostic modules · DM = AP's Diagnostic Manager · UCM = Update and Configuration Management · DoCAN = Diagnostics over CAN (ISO 15765-2) · EPS = Electric Power Steering · AD = Autonomous Driving</div>

---

## Coexistence in one 2026 vehicle

- A modern SDV runs **both platforms at once**: **CP for the reflex nervous system, AP for the
  brain, Ethernet + gateways for the spine.** Zonal/actuator ECUs run Classic on CAN/LIN/FlexRay;
  central HPCs run Adaptive on Linux/QNX over automotive Ethernet
- **The signal↔service (S2S) gateway** is the key coexistence mechanism: it subscribes to
  Classic COM **signals**, repackages them, and offers them as SOME/IP **services** (and
  vice-versa) — *"acting like a remote SOME/IP node."* Shipped by **Vector MICROSAR** (S2S
  add-on), **Elektrobit** (EB tresos + EB corbos), **ETAS** (RTA-CAR + RTA-VRTE)
- **Diagnostics routing across the split — two distinct boxes**: the **TCU** terminates the
  external 4G/5G link (TLS + certificates); a separate **central gateway** (DoIP router +
  **firewall** — the security chokepoint) routes **DoIP** on the backbone and re-transports it
  to **DoCAN** on CAN branches — **raw UDS is never exposed to the internet; SOVD is the external API**
- **The OEM "wrap" pattern**: AUTOSAR adopted *selectively* inside a proprietary base layer.
  **Mercedes MB.OS** Base Layer was co-developed with Vector, *"based on AUTOSAR Adaptive and
  Classic and the AUTOSAR Runtime Environment"* — AUTOSAR is an **ingredient, not the platform**.
  VW's **E³** (E3 1.1 MEB / E3 1.2 PPE, CARIAD software) is **domain-controller-based today** (ICAS1–3 / five HPCs); its zonal + central-AP shape is the announced next step (**SSP / E3 2.0**)

<div class="gloss">SDV = Software-Defined Vehicle · S2S = Signal-to-Service gateway · TCU = Telematics Control Unit (modem + cloud endpoint) · MB.OS = Mercedes-Benz Operating System · MEB = VW's Modular Electric Drive Matrix · PPE = Premium Platform Electric · CARIAD = VW Group's software subsidiary · ICAS = In-Car Application Server · SSP = Scalable Systems Platform · migrating a function CP→AP is a re-architecting (new interface, rewrite in `ara::com`, manifests + UCM packaging, S2S gateway, re-done safety case) — not a recompile</div>

---

## AP and CP interactions — as the spec draws it

{{image:spec-ap-cp-interactions}}

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 3.2 — © AUTOSAR.</div>

<div class="gloss">In the figure the blue 'A' region = Adaptive Platform (perception → planning → trajectory) and the green 'C' region = Classic Platform (the safety function gating trajectory control) — that split is the whole point · C2C / C2I = Car-to-Car / Car-to-Infrastructure · OEM = the vehicle maker · GPS = satellite positioning</div>

---

## Which stack on which silicon — the decision map

<style scoped>
  section { font-size: 18px; padding-top: 24px; }
  h2 { margin-bottom: 6px; }
  p { margin: 6px 0; }
  table { font-size: 14px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 12.5px; margin-top: 8px; }
</style>

The whole deck in one procurement table — what runs where, and who sells it:

| Silicon | What runs there | Who supplies it (examples) |
|---|---|---|
| **A-core SoC** — DRIVE Orin/Thor guest · NXP S32G/S32N · R-Car | **QNX or Linux + an AP stack** — or a non-AUTOSAR middleware (the Rivian path) | AP: **Vector · Elektrobit (corbos) · ETAS RTA-VRTE · Qorix** — the OS underneath is a separate procurement |
| **Safety island on the SoC** — lockstep Cortex-R52 (Thor FSI) | vendor safety firmware — plus a Vector **FSI reference integration** (Thor) | NVIDIA FSI firmware · Vector — its explicit **MICROSAR Classic** up-to-ASIL-D reference targets the **companion MCU** |
| **Companion / safety MCU** — RH850 (Thor gen) · AURIX (Orin gen) | **CP** | Vector AFW — the NVIDIA reference integration |
| **Zonal / domain MCUs** — NXP S32Z/E · AURIX · RH850 | **CP** | Tier-1 Classic stacks (MICROSAR, EB tresos class) |
| **Small edge ECUs** — S32K class | **CP** or bare-metal/RTOS | Tier-1 stacks or in-house |

**The business rule underneath: AUTOSAR value scales with how many organizational boundaries your software crosses** — vertically-integrated OEMs (Rivian) skip it; Tier-1s implement it to win OEM RFQs.

<div class="gloss">FSI = Functional Safety Island (dedicated lockstep silicon on DRIVE/IGX Thor) · AFW = the Vector-built AUTOSAR firmware NVIDIA ships for its companion MCUs · RFQ = request for quotation · S32Z/E = NXP zonal-controller family (lockstep Cortex-R52) · examples only — the vendor cells repeat facts verified elsewhere in this deck, not an exhaustive market list</div>

---

## Fleet ↔ a CP+AP vehicle — one request, end to end

<style scoped>
  section { font-size: 19.5px; padding-top: 28px; }
  h2 { margin-bottom: 4px; }
  p { margin: 5px 0; }
  ol { margin: 4px 0; }
  .gloss { font-size: 13px; margin-top: 8px; }
</style>

**Read a fault code from a zonal brake ECU, starting in the cloud:**

1. The backend speaks **SOVD (REST/JSON over HTTPS)** and collects **MQTT telemetry** — **never raw UDS**; the vehicle's entry point is the **TCU**
2. The **central gateway** (DoIP router + firewall) is the security chokepoint for everything below it
3. Target lives on **AP** → the **DM** (`ara::diag`) on the HPC answers: UDS-over-DoIP, or SOVD natively
4. Target lives on **CP** → the gateway **re-transports DoIP → DoCAN**; the ECU's **DCM+DEM** answer. **Same UDS bytes, different transport** — the Classic ECU just sees "a tester"

**Push an update:** **V-UCM** on the HPC orchestrates the whole vehicle — AP **Software Clusters** go through UCM (transfer → process → activate, with rollback); CP ECUs are **reflashed over UDS 0x34–0x37** through the gateway, exactly like a workshop flash session

**Real vehicles shaped like this:** **Mercedes MB.OS** — CP + AP coexisting under one Vector-built base layer (the named production example) · **Rivian Gen 2** — the zonal topology shipped for real: **3 zone ECUs (West / East / South) + dual NVIDIA DRIVE Orin** as central compute — cited for the *shape*; Rivian's software stack is its own, not an AUTOSAR deployment

<div class="gloss">SOVD = Service-Oriented Vehicle Diagnostics (ISO 17978) · TCU = Telematics Control Unit · DoIP / DoCAN = UDS transports (ISO 13400 / ISO 15765-2) · DM = Diagnostic Manager (AP — one diagnostic server per Software Cluster) · DCM + DEM = Diagnostic Communication / Event Manager (CP) · V-UCM = Vehicle Update & Configuration Management · the punchline: one diagnostic language (UDS, ISO 14229), two transports, two server implementations</div>

---

## If you skip AUTOSAR — four buildable stack paths

<style scoped>
  section { font-size: 17px; padding-top: 22px; }
  table { font-size: 12.5px; }
  table td, table th { padding: 3px 8px; vertical-align: top; }
  h2 { margin-bottom: 6px; }
  p { margin: 6px 0; }
  .gloss { font-size: 12px; margin-top: 8px; }
</style>

The org-boundary rule scales up to four buildable paths:

| Path | What you get | What you still owe | Named evidence |
|---|---|---|---|
| **Buy CP** — Tier-1 Classic (MCUs) | a pre-certified ASIL-D base off the shelf | ECU integration + ARXML supply-chain plumbing | Vector MICROSAR Safe — ISO 26262 up to ASIL D since **2016**; the 2020 exida certificate covers 29 + 19 modules |
| **Buy an AP stack** — HPC | standardized in-vehicle service endpoints (`ara::com`, DM, V-UCM) | the POSIX OS + hypervisor + your own ASIL-D safety case | Vector · EB corbos · ETAS RTA-VRTE · Qorix |
| **Join the open collective** — Eclipse S-CORE | a shared open SDV core for non-differentiating scope, Apache-2.0, C++/Rust | it's a core stack, **not** an AP implementation — you still integrate + certify | launched 2025-06-12; BMW · Mercedes-Benz · Bosch · ETAS · QNX · Qorix · Accenture |
| **Roll your own** — Linux/QNX + in-house middleware | full vertical control + iteration speed | every wire contract re-implemented — **you own the entire ISO 26262 argument** | Rivian: in-house OS on FreeRTOS · Tesla: in-house Linux stack ([teslamotors/linux](https://github.com/teslamotors/linux)) + a non-AUTOSAR telemetry path · Li Auto: Halo OS (**press**) |

**Why fund a collective instead of just buying AP?** S-CORE's charter: build ["a single, joint solution instead of multiple specific ones"](https://projects.eclipse.org/projects/automotive.score) for non-differentiating scope, ["shaped by a broad community"](https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together) rather than duplicated company-by-company — an open, safety-targeted core stack alongside the specs, **not** an AP implementation and with **no official AP-compatibility statement either way** ([discussion #759](https://github.com/orgs/eclipse-score/discussions/759) even proposes AUTOSAR reuse S-CORE's processes and tooling). ETAS states the both-and out loud: [robust AUTOSAR for safety-critical / hard-real-time, open-source S-CORE for the rest](https://www.etas.com/ww/en/topics/s-core/). Rivian's SVP is on record — ["We don't use any of the industry offerings such as AUTOSAR"](https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/); its Gen-2 zonal controllers (East / West / South) run an in-house OS layered on FreeRTOS.

**The cautionary tail — press:** in-house at OEM scale is brutal. VW's CARIAD posted an operating loss of **€2.431 bn in 2024** and — per the cited article — ["over $7.5 billion"](https://insideevs.com/news/753673/vw-group-cariad-billions-losses-2024/) (≈ €6.9 bn) in cumulative operating losses across 2022–2024 — a large part of why most OEMs still *buy* rather than *build*.

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform · HPC = High-Performance Computer · MCU = Microcontroller · SDV = Software-Defined Vehicle · S-CORE = Eclipse Safe Open Vehicle Core · SVP = Senior Vice President · DM = Diagnostic Manager · V-UCM = Vehicle Update & Configuration Management · ARXML = AUTOSAR XML exchange format · ASIL = Automotive Safety Integrity Level (ISO 26262) · CARIAD = VW Group's software unit · rows labelled **press** rest on reputable reporting, not primary sources; the "no AUTOSAR" absolute is sourceable for Rivian, not for Tesla</div>

---

## The fleet contracts that don't care which stack you picked

<style scoped>
  section { font-size: 17px; padding-top: 22px; }
  h2 { margin-bottom: 6px; }
  p { margin: 6px 0; }
  li { margin-bottom: 3px; }
  .gloss { font-size: 12px; margin-top: 8px; }
  em { color:#2E5FAC; font-style: normal; font-weight: bold; }
</style>

**AUTOSAR standardizes the *vehicle*, not the backend link** — V-UCM: the Backend↔OTA-Client protocol is *"out of scope for this specification document"* (AP_SWS_VehicleUpdateAndConfigurationManagement, R25-11). The contracts below are identical whichever stack path you build on:

- **UDS (ISO 14229) + DoIP (ISO 13400)** — *de-facto, tilting legal in the US*: no law mandates DoIP; UDS is de-facto for reflash/diagnostics everywhere and named only as an allowed option in EU 2017/1151 — but **CARB mandates the UDS-based SAE J1979-2 "OBDonUDS" for all MY2027+ vehicles** (13 CCR §§1968.2/1971.1, rule in force since Nov 2022; the older mandated cousin: OBD-II since MY1996 — gasoline, diesel followed 1997)
- **UN R155 CSMS (cyber) + R156 SUMS (software update)** — *mandated (type approval)*: management systems (organizational processes), not protocols or middleware; **ISO 24089** operationalises R156 but stays *optional*
- **eCall (EU 2015/758)** — *mandated (type approval)*: auto-dials 112 + transmits location on a severe crash — new M1/N1 types since 31 Mar 2018
- **SOVD (ISO 17978, parts 1–3 published 2026)** — *de-facto, emerging*: self-describing REST/JSON diagnostics for HPCs
- **ISO 15118 Plug & Charge** — *de-facto* EV↔charger contract (AFIR pushes 15118-capable public charge-points, making vehicle-side support effectively unavoidable ~2027)
- **Telemetry** — *AUTOSAR standardizes none of it*: always an OEM/cloud choice — Tesla's [fleet-telemetry](https://github.com/teslamotors/fleet-telemetry/blob/main/README.md) makes the car a *client* pushing protobuf records over WebSocket + mTLS to an operator-hosted server (Kafka behind it); even **AWS IoT FleetWise is closed to new customers (2026)**

**Punchline:** skipping AUTOSAR forfeits pre-built in-vehicle endpoints, **never fleet reachability** — the contracts above are transport/process standards you re-implement on your own OS, proven by **Rivian's non-AUTOSAR stack** and **Tesla's non-AUTOSAR telemetry path**.

<div class="gloss">V-UCM = Vehicle Update & Configuration Management · OTA = Over-The-Air · UDS = Unified Diagnostic Services · DoIP = Diagnostics over IP · OBD = On-Board Diagnostics · CARB = California Air Resources Board · CSMS = Cyber Security Management System · SUMS = Software Update Management System · SOVD = Service-Oriented Vehicle Diagnostics · HPC = High-Performance Computer · AFIR = EU Alternative Fuels Infrastructure Regulation · mTLS = mutual TLS (both ends authenticate) · protobuf = Protocol Buffers (Google's binary serialization) · Kafka = a high-throughput message-streaming backend · SAE J1979-2 (OBDonUDS) = the US emissions-OBD standard rebuilt on UDS · MY = model year · 13 CCR = California Code of Regulations, Title 13</div>

---

## The AP and external systems — as the spec draws it

{{image:spec-aap-external-systems}}

<div class="figsrc">Source: AUTOSAR AP_EXP_SWArchitecture, R25-11, Figure 7.2 — © AUTOSAR.</div>

<div class="gloss">DoIP = Diagnostics over IP (ISO 13400) · ECU = Electronic Control Unit · «aracom» = an ara::com link (SOME/IP or DDS) · UML notation: «…» is a stereotype (the kind of node/connection) and 0..* / 1 are multiplicities ('zero-or-more' / 'exactly one')</div>

---

<!-- _class: diagram -->

{{diagram:fleet-uds-flow}}

---

<!-- _class: diagram -->

{{diagram:fleet-on-thor}}

---

## Convergence — the two worlds are moving together

- The old dichotomy *"signals = Classic, services = Adaptive; CAN = Classic, Ethernet = Adaptive"*
  is **outdated at the standard level.** R25-11-era moves close the gap:
- **DDS on the Classic Platform (new in R25-11 — the headline).** The CP Release Overview §2.1.1.5
  states management of *"Events, Methods, and Fields, previously available through SOME/IP, are
  now extended to DDS"* with a *"new BSW module **DDS Transformer**,"* *"full support of
  ClientServerInterface,"* and integration of the OMG **SPDP/SEDP** discovery protocols plus AP's
  Service Discovery. **Hedge to preserve: this is a *standard-level concept new in R25-11* — no
  shipping vendor implementation was verified; adoption timelines unconfirmed.** In principle a CP
  ECU can join the same DDS databus AP and ROS 2 already use
- **Dynamic memory, blessed on purpose** — the heap is permitted on the compute side, provided
  determinism is engineered back in (a philosophical convergence with the C++ application world)
- **MISRA C++:2023 merge** — the AUTOSAR C++14 guidelines folded into one industry standard
  targeting C++17 (formal ARA C++17 move stays open)
- **SOVD as the external-facing diagnostic API** (ISO 17978-3, REST/JSON/OAuth) and **Eclipse
  S-CORE** (open, dual-language C++/Rust, built by AUTOSAR's own members) are the other convergence signals

<div class="gloss">DDS = Data Distribution Service · SPDP/SEDP = the OMG Simple Participant / Endpoint Discovery Protocols · BSW = Basic Software · the CP DDS Transformer is R25-11 standard-level only — never present it as shipping</div>

---

<!-- _class: diagram -->

{{diagram:dds-scope}}

---

## Where ROS 2 sits — next to, not inside, AUTOSAR

- ROS 2 and AP **share the DDS wire family** (ROS 2's default RMW is DDS; AP has a DDS binding
  since R18-03) — **but they are NOT plug-compatible.** Blockers to naive DDS-to-DDS: ROS 2
  mangles topic names (`rt/…`, `rq/…`, `rr/…`) while AP-DDS uses `"ara.com://services/…"`
  partitions; type construction differs; AP's USER_DATA discovery mode isn't in ROS 2. **Interop
  goes through a bridge/gateway** (SOME/IP-DDS, ROS2-SOME/IP) — an active 2024–2026 research area
- **Positioning — prototyping/R&D vs production**: Apex.AI frames it as *"ROS 2 … code-first …
  as easy as possible to develop"* vs *"AUTOSAR … interoperability between suppliers and OEMs."*
  A 2026 arXiv comparison finds ROS 2 *"lacks several concepts essential for series-production"*
  (operation modes, allocation control, watchdog supervision) — **which is why AP exists alongside
  ROS 2 rather than replacing it**
- **The safe-C++ playbook converges**: the production ROS 2 derivative **Apex.Grace** is
  *"certified by TÜV Nord as a Safety Element out of Context (SEooC) up to ASIL D."* It enforces
  static memory pools and eliminates runtime allocation — mirroring AP's deterministic-allocator
  discipline. One genuinely shared building block: **iceoryx** — the low-level zero-copy IPC that sits *under* both stacks via separate bindings

<div class="gloss">ROS 2 = Robot Operating System 2 · RMW = ROS Middleware abstraction · DDS/RTPS = the shared wire family · SEooC = Safety Element out of Context · Apex.Grace = the ASIL-D-certified ROS 2 derivative (formerly Apex.OS) · Autoware = the flagship open AD stack on ROS 2</div>

---

## What this means for our embedded team

- **Classic is the world you already half-know.** Static config, no heap in safety paths,
  MPU partitions, E2E/SecOC, windowed watchdogs — **it is the same functional-safety mindset you
  use on MCUs, formalized and code-generated.** Learn CP to understand *why* automotive safety
  code looks the way it does
- **Adaptive is where the "big chip" is going.** Service-oriented, manifest-driven, OTA-updatable,
  C++ on POSIX — and its **DDS binding is the bridge to the ROS 2 knowledge this repo already
  teaches.** Learn AP (and ROS 2) to understand where the compute side is heading
- **Carry the corrected mental models, not the folklore:**
  - **DEM computes fault status; DCM only formats** — the #1 conceptual error to avoid
  - **SecOC = authenticity + freshness, NOT encryption**
  - **OS Timing Protection = budgets, NOT deadline supervision** (that's WdgM)
  - **Thor safety MCU = Renesas RH850U2A16, NOT AURIX** (Orin = AURIX TC397X)
  - **"DoIP-only" only with "standardized" attached**; **CP is not CAN-only**; **AP is not low-ASIL**
- **The hands-on next step**: contrast `github.com/langroodi/Adaptive-AUTOSAR` (MIT Linux AP
  simulator) with our `rclcpp`/DDS work — the natural bridge from ROS 2 into the AUTOSAR world

<div class="gloss">DEM/DCM = Diagnostic Event / Communication Manager · SecOC = Secure Onboard Communication · WdgM = Watchdog Manager · DoIP = Diagnostics over IP · every corrected model here is drawn from the three research docs behind this deck</div>

---

## Glossary — Adaptive Platform additions

<style scoped>
  section { font-size: 12.5px; padding-top: 28px; padding-bottom: 18px; line-height: 1.38; }
  ul { columns: 2; column-gap: 30px; margin-top: 4px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 4px; font-size: 28px; }
  p { margin: 2px 0 2px 0; font-size: 13.5px; }
</style>

*(Extends the main deck's three-slide glossary — SWC/RTE/BSW/MCAL/CDD/ARXML/AUTOSAR-OS/ARA/POSIX/PSE51/UDS/DoCAN/DoIP/DCM/DEM/UCM/SOVD are defined there.)*

- **FO / CP / AP** — Foundation / Classic Platform / Adaptive Platform: the three members of one AUTOSAR standard set
- **VFB** — Virtual Functional Bus: the logical bus SWCs talk over; the RTE implements it per ECU
- **COM / PduR / CanIf** — Classic signal packing / PDU router / CAN interface — the build-time-frozen TX/RX chain
- **E2E / SecOC** — End-to-End protection (CRC+counter, ISO 26262) / Secure Onboard Communication (MAC + freshness, no encryption)
- **NM / PN** — Network Management (synchronized wake/sleep) / Partial Networking (a subset sleeps)
- **EcuM / BswM** — ECU State Manager (lifecycle edges) / BSW Mode Manager (steady-state rule engine)
- **WdgM / StbM** — Watchdog Manager (Alive/Deadline/Logical supervision) / Synchronized Time-Base Manager
- **FFI** — Freedom From Interference: ISO 26262 spatial/temporal isolation between mixed-ASIL software
- **AA** — Adaptive Application: a POSIX process (C++, PSE51) linked against ARA
- **EM / SM** — Execution Management (starts/stops processes — the enforcer) / State Management (decides which run — the brain)
- **Function Group / Functional Cluster** — AP's unit of composition (a set of processes with states) / a platform building block (`ara::…`)
- **Manifest** — ARXML deployment config (Execution / Service-Instance / Machine / Raw-Data-Stream / Software-Distribution)
- **`ara::com`** — the one AP communication API (proxy/skeleton), bound to SOME/IP or DDS in the manifest
- **event / trigger / method / field** — the four `ara::com` service-element kinds (trigger = a data-less event)
- **SOME/IP / DDS** — the two standardized `ara::com` wire bindings (DDS present since R18-03)
- **DM / V-UCM** — Diagnostic Management (`ara::diag`, merges DCM+DEM) / Vehicle UCM (vehicle-wide OTA campaign coordinator)
- **PHM / `ara::per`** — Platform Health Management (AP's WdgM analogue) / Persistency (KVS + File Storage)
- **iceoryx** — low-level zero-copy shared-memory IPC that sits under both AP and ROS 2 via separate bindings
- **S-CORE / SOAFEE** — Eclipse open dual-language (C++/Rust) SDV core stack / Arm-led cloud-native SDV architecture (containers, K8s, CI/CD)
- **S2S gateway** — Signal-to-Service gateway bridging Classic COM signals ⇄ SOME/IP services

---

## References 1/4 — AUTOSAR primary sources

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 2px; }
  h2 { margin-bottom: 6px; }
</style>

- **Release / structure**: [autosar.org/news-events/release-event](https://www.autosar.org/news-events/release-event) · [.../detail/release-r25-11-is-now-available](https://www.autosar.org/news-events/detail/release-r25-11-is-now-available) · [CP_TR_ReleaseOverview](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf) (R25-11, DDS-on-CP, removed specs, schema) · [autosar.org/about/history](https://www.autosar.org/about/history)
- **Classic architecture**: [CP_EXP_LayeredSoftwareArchitecture](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf) (R25-11) · [FO_EXP_SWArchitecturalDecisions](https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf) (R25-11, Doc 1078, dynamic memory) · [TR_Methodology](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf) (R22-11) · RTE/VFB: [hpi.de Naumann RTE_VFB](https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf) · embetronicx.com RTE tutorial · [mxhelp.danlawinc.com](https://mxhelp.danlawinc.com/autosar_reference.htm)
- **Classic OS / comms**: [Vector AUTOSAR_Task_Scheduling](https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf) (SC1–SC4) · [SWS_ServiceDiscovery](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf) (R22-11) · [PRS_E2EProtocol](https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf) (R19-03) · [FO_PRS_SecOcProtocol](https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf) (R24-11) · [PRS_NetworkManagementProtocol](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf) (R22-11) · [eenews CAN-FD-vs-FlexRay](https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/)
- **Classic services / safety**: [CP_SWS_DiagnosticEventManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf) (R24-11) · [CP_SWS_DiagnosticCommunicationManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf) (R24-11) · [SWS_NVRAMManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf) (R22-11) · [EXP_ModeManagementGuide](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf) (R22-11) · [CP_SWS_WatchdogManager](https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf) (R23-11) · [SWS_SynchronizedTimeBaseManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf) (R22-11) · [EXP_FunctionalSafetyMeasures](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf) (R22-11, Doc 664)
- **Vendors / silicon**: [vector.com MICROSAR Classic Safe ASIL-D recert](https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/) (exida) · [developer.nvidia.com DRIVE safety-MCU](https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html) (Orin=AURIX TC397X / Thor=RH850U2A16, repo-verified) · [btc-embedded.com Classic vs Adaptive](https://www.btc-embedded.com/autosar-classic-vs-adaptive)

<div class="gloss">Full URLs, confidence levels and per-claim sourcing live in the three research docs behind this deck: autosar/research/autosar-classic-2026-07.md · autosar-adaptive-2026-07.md · classic-vs-adaptive-2026-07.md</div>

---

## References 2/4 — Adaptive, comparison & open efforts

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 2px; }
  h2 { margin-bottom: 6px; }
</style>

- **Adaptive architecture**: [AP_EXP_PlatformDesign](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf) (R25-11, Doc 706) · [AP_EXP_SWArchitecture](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf) (R25-11, Doc 982) · [AP_SWS_ExecutionManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf) (R25-11, Doc 721) · [AP_TPS_ManifestSpecification](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf) (R25-11) · [AP_SWS_OperatingSystemInterface](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf) (R25-11, PSE51)
- **Adaptive comms**: [AP_SWS_CommunicationManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf) (R25-11, Doc 717) · [rti.com AP 18.03 now-with-DDS](https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds) + [status-of-DDS-in-AUTOSAR](https://www.rti.com/blog/status-of-dds-in-autosar) · [PRS_SOMEIPServiceDiscovery](https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf) (R19-03) · [omg.org DDS-RPC 1.0](https://www.omg.org/spec/DDS-RPC/1.0) · [apex.ai iceoryx-speeds-up-AUTOSAR-and-ROS-2](https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2)
- **Adaptive lifecycle / diag**: [AP_SWS_UpdateAndConfigurationManagement](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf) (R24-11, Doc 888) · [AP_SWS_VehicleUpdateAndConfigurationManagement](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf) (R25-11, Doc 1090) · [AP_SWS_Diagnostics](https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf) (R25-11) · [AP_EXP_SOVD](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf) (R24-11, Doc 1064) · [AP_SWS_PlatformHealthManagement](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf) (R24-11) · [AP_SWS_Persistency](https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Persistency.pdf) (R24-11) · [asam.net SOVD](https://www.asam.net/standards/detail/sovd/) · [iso.org 17978-1](https://www.iso.org/standard/85133.html)
- **C++ / vendors / certs**: [autosar.org MISRA-integration announcement](https://www.autosar.org/news-events/detail/misra-consortium-announce-integration-of-autosar-c-coding-guidelines-into-updated-industry-standard) · [perforce.com MISRA-C++:2023](https://www.perforce.com/blog/qac/misra-cpp-2023-intro) · [vector.com Adaptive-Safe ASIL-B](https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/) · [etas.com ASIL-B TÜV SÜD](https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/) (March 2025) · qorix.ai TÜV-certified (Aug 2025) · [elektrobit.com EB-corbos-AdaptiveCore](https://www.elektrobit.com/products/ecu/eb-corbos/adaptivecore/) · [automotiveworld.com Wind-River ASIL-D program](https://www.automotiveworld.com/news-releases/wind-river-autosar-adaptive-automotive-software-ready-for-iso-26262-asil-d-certification-program/) · [vvdntech.com Vehicle-OS-Wars](https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/) (QNX share)
- **Comparison / open**: [arxiv.org/pdf/2109.00099](https://arxiv.org/pdf/2109.00099) (AUTOSAR platforms) · [doi.org/10.3390/electronics14183635](https://doi.org/10.3390/electronics14183635) (AP↔ROS2 bridge) · [arxiv.org 2604.22576](https://arxiv.org/pdf/2604.22576) (ROS 2 vs AP, 2026) · [arxiv.org 2511.17540](https://arxiv.org/pdf/2511.17540) (AP↔ROS2 framework, 2025-11) · [apex.ai apexgrace](https://www.apex.ai/apexgrace) + [autosar-and-ros-2-for-SDV](https://www.apex.ai/post/autosar-and-ros-2-for-software-defined-vehicle) · [eclipse S-CORE launch](https://www.globenewswire.com/news-release/2025/06/12/3098131/0/en/the-eclipse-foundation-launches-the-s-core-project-the-automotive-industry-s-first-open-source-core-stack-for-software-defined-vehicles.html) · [covesa SOAFEE blueprint](https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf) · [github.com/langroodi/Adaptive-AUTOSAR](https://github.com/langroodi/Adaptive-AUTOSAR) (MIT AP simulator)

<div class="gloss">Med/low-confidence items and open questions (CAN XL release · C++17 ARA move · SecOC "no confidentiality" wording · exact SC1–SC4 phrasing · S2S-gateway and arXiv rows · ASIL-D field evidence) are flagged as such in the research docs — not asserted here as settled fact.</div>

---

## References 3/4 — open-source Adaptive AUTOSAR

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 3px; }
  h2 { margin-bottom: 6px; }
</style>

- **AP implementations**: [github.com/langroodi/Adaptive-AUTOSAR](https://github.com/langroodi/Adaptive-AUTOSAR) (MIT · C++ · 7 `ara::` clusters · dormant since 2023-06) · [github.com/ZiadAhmed9/ara-rs](https://github.com/ZiadAhmed9/ara-rs) (Apache-2.0/MIT · Rust proxy/skeleton + `cargo-arxml` · created 2026-03) · [autosar.org/capi](https://www.autosar.org/capi) (CAPI — official, partner-gated, **not** open source)
- **Protocol / IPC building blocks**: [github.com/COVESA/vsomeip](https://github.com/COVESA/vsomeip) (MPL-2.0 · SOME/IP) · [github.com/COVESA/capicxx-core-runtime](https://github.com/COVESA/capicxx-core-runtime) (MPL-2.0 · CommonAPI · dormant) · [github.com/eclipse-iceoryx/iceoryx](https://github.com/eclipse-iceoryx/iceoryx) (Apache-2.0 · zero-copy IPC) · [github.com/eclipse-iceoryx/iceoryx2](https://github.com/eclipse-iceoryx/iceoryx2) (Apache-2.0 OR MIT · Rust core) · [github.com/eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS) (Apache-2.0 · DDS/RTPS)
- **Open ecosystem around AP**: [github.com/eclipse-score](https://github.com/eclipse-score) (S-CORE org · Apache-2.0) · [github.com/eclipse-score/communication](https://github.com/eclipse-score/communication) (LoLa — partial `ara::com`, `score::mw::com`) · [github.com/eclipse-opensovd/opensovd-core](https://github.com/eclipse-opensovd/opensovd-core) (Apache-2.0 · SOVD / ISO 17978) · [autosar.org — SDV Alliance (CES 2024)](https://www.autosar.org/news-events/detail/collaboration-the-key-to-making-the-software-defined-vehicle-a-reality)
- **Classic-side contrast**: [github.com/openAUTOSAR/classic-platform](https://github.com/openAUTOSAR/classic-platform) (GPL-2.0 · Arctic Core lineage — the open Classic fork Adaptive has no equivalent of)
- **Spec figures**: Spec figures on the "as the spec draws it" slides are unmodified excerpts from the AUTOSAR R25-11 PDFs, reproduced for informational purposes — © AUTOSAR (local mirror: autosar/specs/)

<div class="gloss">All repositories, releases and dates verified against their GitHub API / project pages on 2026-07-16 · the CAPI git endpoint (code.autosar.org/capi/capi) is partner-gated (302 → sign-in) and is listed as the boundary, not an open-source download · autosar.org links fetched with the deck's `-ksL` TLS workaround · full provenance in autosar/research/adaptive-open-source-2026-07.md</div>

---

## References 4/4 — the non-AUTOSAR fleet & stack choice

<style scoped>
  section { font-size: 15px; padding-top: 26px; line-height: 1.3; }
  ul { margin-top: 4px; }
  li { margin-bottom: 3px; }
  h2 { margin-bottom: 6px; }
</style>

- **Non-AUTOSAR OEM stacks (primary)**: [github.com/teslamotors/fleet-telemetry](https://github.com/teslamotors/fleet-telemetry/blob/main/README.md) (server reference impl; vehicle = client, WebSocket + mTLS + protobuf, Kafka behind it — the concrete non-AUTOSAR fleet path) · [github.com/teslamotors/linux](https://github.com/teslamotors/linux) (Tesla's published in-vehicle Linux kernel tree — GPL source offer) · [sonatus.com — Rivian's Vidya Rajagopalan](https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/) (SVP on record: "we don't use … AUTOSAR"; in-house on FreeRTOS) · [leandesign.com — Rivian software architecture](https://leandesign.com/rivian-software-architecture-update/) (Gen-2 zonal East/West/South) · [cnevpost.com — Li Auto open-sources Halo OS](https://cnevpost.com/2025/03/27/li-auto-open-sources-halo-os/) (announced 2025-03-27; code released in phases to v1.0.0 on 2025-06-30 via Gitee, Apache-2.0; "to challenge the position of AUTOSAR" — **press**)
- **Fleet contracts — mandated vs de-facto**: [unece.org — UN R156 (SUMS)](https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update) (**mandated, type approval** — a process, not a protocol) · [europarl.europa.eu — eCall mandatory](https://www.europarl.europa.eu/news/en/press-room/20180326IPR00510/saving-lives-ecall-mandatory-in-new-car-models-from-this-week) (Reg (EU) 2015/758, **mandated** since 31 Mar 2018) · [arb.ca.gov — OBD-II fact sheet](https://ww2.arb.ca.gov/resources/fact-sheets/board-diagnostic-ii-obd-ii-systems-fact-sheet) (the emissions-OBD interface is the **mandated** cousin of de-facto UDS) · [iso.org/standard/74785 — ISO 13400 DoIP](https://www.iso.org/standard/74785.html) (**de-facto** UDS-over-IP transport) · [iso.org/standard/77796 — ISO 24089](https://www.iso.org/standard/77796.html) (software-update engineering — **optional**, operationalises R156) · [charin.global — ISO 15118 Plug & Charge](https://www.charin.global/technology/plug-charge/) (**de-facto** EV↔charger contract; AFIR-pushed) · [docs.aws.amazon.com — IoT FleetWise](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/what-is-iotfleetwise.html) (closed to new customers, 2026 — telemetry is a churning vendor choice, never an AUTOSAR standard)
- **The open collective + AUTOSAR's own rationale**: [projects.eclipse.org/projects/automotive.score](https://projects.eclipse.org/projects/automotive.score) (S-CORE charter — "single, joint solution … non-differentiating scopes") · [newsroom.eclipse.org — S-CORE newsletter, Sept 2025](https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together) (shared open platform vs duplicating work) · [github.com/orgs/eclipse-score/discussions/759](https://github.com/orgs/eclipse-score/discussions/759) (S-CORE positioned complementary to AUTOSAR) · [etas.com/ww/en/topics/s-core](https://www.etas.com/ww/en/topics/s-core/) (Bosch/ETAS both-and: AUTOSAR for safety-critical, S-CORE for the rest) · [presseagentur.com — Vector MICROSAR Safe](https://www.presseagentur.com/vector/detail.php?pr_id=5546&lang=en) (ISO 26262 up to ASIL D, exida 2020 — what "buy CP" gets you) · [autosar.org/faq](https://www.autosar.org/faq) (value = crossing OEM↔supplier boundaries) · [insideevs.com — CARIAD losses](https://insideevs.com/news/753673/vw-group-cariad-billions-losses-2024/) (€2.431 bn 2024, >€7.5 bn 2022–24 — **press**)

<div class="gloss">GitHub facts verified via the GitHub API on 2026-07-17 · SOVD (ISO 17978), the AP V-UCM spec, the AP-vendor list and the S-CORE launch details are reused from this deck's existing References + research docs (autosar/research/), not re-listed here · press-labelled rows (CARIAD, Li Auto) are the only non-primary sources and are marked in-slide · full provenance: autosar/research/{non-autosar-oem-fleet, fleet-contracts-standards, sdv-fleet-oss-toolbox, autosar-vs-inhouse-decision}-2026-07.md</div>
