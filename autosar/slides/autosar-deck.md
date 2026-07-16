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

1. **One org, three standards** — history, governance, the FO / CP / AP split, the release timeline
2. **Classic Platform** — the statically-configured RTOS stack you half-know: RTE/VFB, AUTOSAR OS, ARXML, the signal path, E2E/SecOC, DCM/DEM, NvM/WdgM, functional safety
3. **Adaptive Platform** — the POSIX/C++ service platform on the "big chip": function clusters, EM/SM, `ara::com`, SOME/IP vs DDS, UCM OTA, DM/SOVD, PHM, vendors & ASIL reality, the open-source AP landscape
4. **Head-to-head & coexistence** — one vehicle running both, the R25-11 convergence, where ROS 2 sits, what it means for our team

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
  Development Agreement July 2003), governed top-down by ~10 **Core Partners**; **~360
  partners today, Asia-led** (Jan 2025: Asia 174 > Europe 140 > NA 41). Jan 2026: DENSO, Huawei and
  Vector promoted to Core. Specs are **free to read, license-to-build**
- **Foundation (FO)** — the cross-platform glue: common requirements, the **meta-model and
  single XML schema**, methodology, and shared wire protocols (SOME/IP, time-sync, DoIP, E2E,
  SecOC). FO is what lets a Classic ECU and an Adaptive machine live in one vehicle project
- **Classic Platform (CP)** — statically-configured, real-time, **OSEK-heritage** stack for
  deeply embedded microcontrollers. First released 1.0 in **2005**
- **Adaptive Platform (AP)** — **POSIX**-based, service-oriented, dynamically-deployed stack
  for high-performance compute. First released **17-03 (March 2017)**
- **The naming trap**: the **R19-11 unification** (Nov 2019) merged CP's `4.x.y` and AP's
  `yy-mm` into one annual `R{yy}-11` label, one November release, one schema — **but the CP
  internal version never reset**. R25-11 is internally **R4.11.0**; "AUTOSAR 4.x" is alive
- **Document prefixes** you'll meet: **EXP** (explanatory), **TR** (technical report),
  **RS/SRS** (requirements), **SWS** (the detailed testable module spec), **TPS** (templates),
  **PRS** (wire-protocol requirements)

<div class="gloss">OSEK = the 1990s European automotive RTOS standard CP's OS descends from · POSIX = Portable Operating System Interface (IEEE 1003) · SOME/IP = Scalable service-Oriented MiddlewarE over IP · DoIP = Diagnostics over IP (ISO 13400) · E2E = End-to-End protection · SecOC = Secure Onboard Communication · SWS = Software Specification</div>

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
| AP function clusters | one SWS each: `AP_SWS_ExecutionManagement` · `…StateManagement` · `…CommunicationManagement` (`ara::com`, SOME/IP + DDS bindings) · `…Diagnostics` · `…UpdateAndConfigurationManagement` (+ `…VehicleUpdateAndConfigurationManagement`) · `…PlatformHealthManagement` · `…Persistency` · `…OperatingSystemInterface` (PSE51) — plus `AP_TPS_ManifestSpecification` |
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
  microcontrollers, no MMU-class OS, hard real-time, safety-critical. The OSEK-heritage half
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

## AUTOSAR OS — OSEK heritage, plus scalability classes

- AUTOSAR OS is a **backward-compatible superset of OSEK/VDX OS (ISO 17356-3)** — *not* "= OSEK".
  It keeps OSEK's core: static tasks, fixed-priority preemptive scheduling, priority-ceiling
  resources, events, alarms, counters, Cat-1 vs Cat-2 ISRs. **Know OSEK → you know ~70% of it**
- What AUTOSAR bundled on top, as **Scalability Classes**:

| Class | = | Adds |
|---|---|---|
| **SC1** | OSEK OS + | **Schedule Tables** (time-triggered, sync to global time), stack monitoring |
| **SC2** | SC1 + | **Timing Protection** (execution / inter-arrival budgets) + global time sync |
| **SC3** | SC1 + | **Memory Protection** + OS-Applications + trusted/non-trusted functions |
| **SC4** | SC2+SC3 | both timing and memory protection |

- **Multicore** arrived in release **4.0 (2009)**: multi-core startup, **spinlocks**, and
  **IOC** (Inter-OS-Application Communication) — a spinlock-protected shared-memory ring for
  data crossing a core/partition boundary

<div class="gloss">OSEK/VDX = the 1990s automotive RTOS standard · ISR = interrupt service routine (Cat-1 = no OS calls, lowest latency; Cat-2 = may call OS services) · SC = Scalability Class · IOC = Inter-OS-Application Communication · exact SC1–SC4 wording is medium-confidence (structure high) — see references</div>

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

<div class="gloss">FFI = Freedom From Interference (ISO 26262 term) · MPU = Memory Protection Unit (region-compare, not virtual memory) · OS-Application = the partition unit that owns tasks/ISRs/resources · WdgM = Watchdog Manager · WCET = Worst-Case Execution Time · QM = Quality Managed (no ASIL) · execution-time enforcement requires MCU timer/MPU hardware</div>

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
- The building-block view groups the function clusters into **seven technical categories** —
  Runtime, Communication, Storage, Security, Safety, Configuration, Diagnostics

<div class="gloss">AA = Adaptive Application · ARA = AUTOSAR Runtime for Adaptive Applications (the `ara::` C++ API surface) · PSE51 = IEEE 1003.13's minimal single-process real-time POSIX profile · `fork`/`exec` = the POSIX process-creation calls PSE51 omits</div>

---

## The R25-11 function-cluster inventory (this list changes)

- R25-11 defines **20 function clusters across seven categories** — each its own SWS document.
  **A "canonical list" must always be release-stamped:**

| Category | Function clusters (R25-11) |
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

<div class="gloss">EM = Execution Management · SM = State Management · FC = Function Cluster · Function Group = a named set of processes with states · Manifest = ARXML authored at integration time, read at startup · systemd = the Linux service manager (the tempting-but-wrong analogy)</div>

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

## Binding choice: SOME/IP vs DDS vs local IPC

- **SOME/IP** — the automotive-native option: compact serialization + **SOME/IP-SD** service
  discovery. Connection- and ID-oriented (Service ID / Instance ID / Event ID / Eventgroup) —
  familiar from CAN/UDS thinking. Subscription granularity is the **eventgroup**; SD runs **over
  UDP multicast only**
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

## The real shape of AP code

<style scoped>
  section { font-size: 18px; padding-top: 22px; }
  pre { font-size: 12px; line-height: 1.25; margin: 4px 0; }
  pre code { font-size: 12px; }
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

**Rust — the `ara::com` skeleton `OfferService` lifecycle** (`ZiadAhmed9/ara-rs`, created 2026-03-30):

```rust
    /// Advertise this service instance so that remote proxies can find it.
    pub async fn offer(
        &self,
        major_version: MajorVersion,
        minor_version: MinorVersion,
    ) -> Result<(), AraComError> {
        self.transport
            .offer_service(
                self.service_id,
                self.instance_id,
                major_version,
                minor_version,
            )
            .await
    }
```
<p class="attr"><a href="https://github.com/ZiadAhmed9/ara-rs/blob/3bb2a86f8570c84be2d0e7cea9e31aa1d6409f67/ara-com/src/skeleton.rs#L46-L60">ZiadAhmed9/ara-rs @ 3bb2a86 — ara-com/src/skeleton.rs</a></p>

<div class="gloss">What to notice: both return an **`ara::core::Result` / `Result<…, AraComError>`** — AP signals errors as a *returned value*, **not a thrown exception**; `ReportExecutionState` is the **contract every AA implements** so EM knows it reached `kRunning`; `offer()`/`stop_offer()` are the **`OfferService`/`StopOfferService` skeleton lifecycle**. Educational caveat: the C++ repo is **dormant (3 years cold)** and the Rust repo is **weeks old** — read them to learn the shape; neither is conformant or production-grade. AA = Adaptive Application · EM = Execution Management.</div>

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
| **OS / kernel** | AUTOSAR OS — OSEK superset (SC1–SC4, no MMU) | not a new OS: an **OS Interface** on POSIX **PSE51** over Linux/QNX/PikeOS |
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

*(Extends the main deck's three-slide glossary — SWC/RTE/BSW/MCAL/CDD/ARXML/OSEK/AUTOSAR-OS/ARA/POSIX/PSE51/UDS/DoCAN/DoIP/DCM/DEM/UCM/SOVD are defined there.)*

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
- **Function Group / Function Cluster** — AP's unit of composition (a set of processes with states) / a platform building block (`ara::…`)
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

## References 1/3 — AUTOSAR primary sources

<style scoped>
  section { font-size: 15px; padding-top: 28px; line-height: 1.32; }
  ul { margin-top: 4px; }
  li { margin-bottom: 2px; }
  h2 { margin-bottom: 6px; }
</style>

- **Release / structure**: [autosar.org/news-events/release-event](https://www.autosar.org/news-events/release-event) · [.../detail/release-r25-11-is-now-available](https://www.autosar.org/news-events/detail/release-r25-11-is-now-available) · [CP_TR_ReleaseOverview](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf) (R25-11, DDS-on-CP, removed specs, schema) · [autosar.org/about/history](https://www.autosar.org/about/history)
- **Classic architecture**: [CP_EXP_LayeredSoftwareArchitecture](https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf) (R25-11) · [FO_EXP_SWArchitecturalDecisions](https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf) (R25-11, Doc 1078, dynamic memory) · [TR_Methodology](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf) (R22-11) · RTE/VFB: [hpi.de Naumann RTE_VFB](https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf) · embetronicx.com RTE tutorial · [mxhelp.danlawinc.com](https://mxhelp.danlawinc.com/autosar_reference.htm)
- **Classic OS / comms**: [Vector AUTOSAR_Task_Scheduling](https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf) (SC1–SC4) · [osek-vdx.org OS 2.2.3](https://www.osek-vdx.org/mirror/os223.pdf) · [SWS_ServiceDiscovery](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf) (R22-11) · [PRS_E2EProtocol](https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf) (R19-03) · [FO_PRS_SecOcProtocol](https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf) (R24-11) · [PRS_NetworkManagementProtocol](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf) (R22-11) · [eenews CAN-FD-vs-FlexRay](https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/)
- **Classic services / safety**: [CP_SWS_DiagnosticEventManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf) (R24-11) · [CP_SWS_DiagnosticCommunicationManager](https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf) (R24-11) · [SWS_NVRAMManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf) (R22-11) · [EXP_ModeManagementGuide](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf) (R22-11) · [CP_SWS_WatchdogManager](https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf) (R23-11) · [SWS_SynchronizedTimeBaseManager](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf) (R22-11) · [EXP_FunctionalSafetyMeasures](https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf) (R22-11, Doc 664)
- **Vendors / silicon**: [vector.com MICROSAR Classic Safe ASIL-D recert](https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/) (exida) · [developer.nvidia.com DRIVE safety-MCU](https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html) (Orin=AURIX TC397X / Thor=RH850U2A16, repo-verified) · [btc-embedded.com Classic vs Adaptive](https://www.btc-embedded.com/autosar-classic-vs-adaptive)

<div class="gloss">Full URLs, confidence levels and per-claim sourcing live in the three research docs behind this deck: autosar/research/autosar-classic-2026-07.md · autosar-adaptive-2026-07.md · classic-vs-adaptive-2026-07.md</div>

---

## References 2/3 — Adaptive, comparison & open efforts

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

## References 3/3 — open-source Adaptive AUTOSAR

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

<div class="gloss">All repositories, releases and dates verified against their GitHub API / project pages on 2026-07-16 · the CAPI git endpoint (code.autosar.org/capi/capi) is partner-gated (302 → sign-in) and is listed as the boundary, not an open-source download · autosar.org links fetched with the deck's `-ksL` TLS workaround · full provenance in autosar/research/adaptive-open-source-2026-07.md</div>
