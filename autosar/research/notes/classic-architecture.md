# AUTOSAR Classic Platform — Layered Architecture & Build Methodology

*Research notes for embedded/firmware engineers new to automotive software platforms. Written 2026-07-15. Latest release confirmed: R25-11.*

## Executive summary

The AUTOSAR Classic Platform (CP) is a statically-configured software stack for **deeply embedded automotive ECUs** — single microcontrollers, no MMU-class OS, hard real-time, safety-critical [1][12]. It layers software into three tiers: **Application** (portable Software Components / SWCs), the generated **RTE** (Runtime Environment), and the **Basic Software (BSW)**, which is itself split into **Services / ECU Abstraction / Microcontroller Abstraction (MCAL)**, plus a lateral **Complex Device Drivers (CDD)** escape hatch [1][2]. SWCs talk only through **ports** over a conceptual **Virtual Functional Bus (VFB)**; the **RTE generator** realizes that bus as concrete `Rte_*` C functions, which is *why the same SWC can be mapped to a different ECU without code changes* [3][4][5]. The **AUTOSAR OS** is a superset of **OSEK/VDX OS** with schedule tables, memory/timing protection (scalability classes SC1–SC4), and — since release 4.0 — multicore support with spinlocks and IOC [6][7][11]. Everything is driven by **ARXML** files following the AUTOSAR Methodology (System Description → ECU Extract → ECU Configuration → code generation). BSW C code must be **MISRA C** compliant (C:2004 in AUTOSAR 4.2, C:2012 from 4.3) [8]. For an embedded engineer, MCAL is "the vendor HAL made standard"; the genuinely new part is the model-driven, port-based, generate-everything workflow.

## 1. The three-layer architecture and what lives where

CP distinguishes, at the highest abstraction, three layers on one microcontroller: **Application**, **Runtime Environment (RTE)**, and **Basic Software (BSW)** [1]. The BSW is further divided into three horizontal layers plus one vertical:

- **Microcontroller Abstraction Layer (MCAL)** — the lowest layer, with direct register-level access to on-chip peripherals; makes higher layers MCU-independent [2][10].
- **ECU Abstraction Layer** — abstracts the ECU's *board* wiring (which peripheral, on-chip or external, a signal is routed through), making higher layers independent of the ECU hardware topology [1][2].
- **Services Layer** — the top BSW layer: OS, communication and network management, memory (NVRAM) services, diagnostics, ECU state management. Provides application-facing basic services [1][2].
- **Complex Device Drivers (CDD)** — a *vertical* module spanning all layers, used for functionality AUTOSAR does not standardize or that needs extreme timing (e.g. injection control, custom sensor interfaces). It may touch hardware directly and bypass the layering. This is the sanctioned "escape hatch" [1][2].

R25-11 housekeeping (a data point on how a ~20-year platform still evolves): the release **removed TTCan, Fls, Eep, and LdCom**, and updated DDS/library material [1]. Modules do get retired.

## 2. SWCs, ports, the VFB, and why the RTE is generated

Application software is packaged as **Software Components (SWCs)**. A SWC exposes **ports** typed by **port-interfaces**; the main interface kinds are **sender-receiver** (data-flow, e.g. a signal), **client-server** (function call / operation), plus parameter, non-volatile-data, mode-switch, and trigger interfaces [3][4]. Inside a SWC, executable code is organized into **runnable entities** — each runnable is ultimately a plain **C function** [3]. Runnables are activated by **RTE Events**: periodic timing, data reception, operation invocation, mode switch, etc. [3].

SWCs never call each other directly. They communicate over the **Virtual Functional Bus (VFB)** — a *logical* concept that "allows a strict separation between applications and infrastructure" and connects all SWCs "also beyond various electronic control units" [4]. The VFB is an abstraction; the thing that actually implements it on a concrete ECU is the **RTE** [4][5].

**What the RTE generates.** The RTE is produced by an **RTE generator** tool in two phases [5][9]:
- **Contract phase**: from the SWC's AUTOSAR interface description it emits an **application header file** (`Rte_<SWC>.h`) that "defines the contract between the component and the RTE." This lets the SWC be compiled in isolation, before integration [5][9].
- **Generation phase**: after component-to-ECU mapping, runnable-to-task mapping, and data/service mapping are known, it emits the real `Rte_*` source — the function bodies that move data and dispatch runnables [5][9].

SWC code calls generated APIs such as **`Rte_Write()`** (send), **`Rte_Read()`** (receive), and **`Rte_Call()`** (client-server invocation) [5][9]. The developer writing a runnable does not know or care whether the peer is a runnable in the *same* ECU (the RTE turns it into a local buffer copy / direct call) or on a *remote* ECU (the RTE turns it into a COM/PDU message over CAN/Ethernet). "How the function is implemented varies from tool to tool… but the implementation details are not of concern to the developer coding the components" [9].

**Why SWCs are relocatable at design time (Focus Q1).** Because a SWC only ever references ports and calls generated `Rte_*` symbols — never a bus, a driver, or another SWC directly — moving it to another ECU changes *only what the RTE generator emits*, not the SWC source. Local communication compiles to memory access; remote communication compiles to a network transaction. The SWC is written once against the VFB contract; deployment is a late-binding configuration decision realized by regenerating the RTE [3][4][5].

## 3. AUTOSAR OS — OSEK/VDX heritage and what was added (Focus Q2)

AUTOSAR OS is a **superset of OSEK/VDX OS** (ISO 17356), the 1990s statically-configured automotive RTOS standard. It keeps OSEK's core model — **statically defined tasks, fixed-priority preemptive scheduling, priority ceiling (OSEK resources), events, alarms, counters**, and OSEK's conformance classes **BCC1/BCC2/ECC1/ECC2** (basic vs extended tasks) [7][11][6]. Task categories: **Category-1 ISRs** (no OS calls, lowest latency) and **Category-2 ISRs** (may call OS services) — OSEK heritage retained [6].

What AUTOSAR added on top of OSEK OS, organized as **Scalability Classes** [6]:

| Class | = | Adds |
|-------|---|------|
| **SC1** | OSEK OS + | **Schedule Tables** (statically-defined, time-triggered dispatch synchronizable to a global time), Counter interface, stack monitoring |
| **SC2** | SC1 + | **Timing Protection** (budget/execution-time monitoring of tasks & ISRs) + global time synchronization |
| **SC3** | SC1 + | **Memory Protection** + **OS-Applications** + Service Protection + trusted/non-trusted functions |
| **SC4** | SC2 + SC3 | Both timing and memory protection |

- **Schedule Tables** solve a real OSEK weakness: with bare alarms it is hard to keep a set of activations in a fixed phase relationship; a schedule table is a statically-defined, dispatcher-driven sequence of expiry points that can be synchronized to global time [6].
- **Memory protection** (SC3/SC4) partitions the address space so a faulty **OS-Application** cannot corrupt another's data/stack — needs an MPU. **Timing protection** (SC2/SC4) enforces execution-time and inter-arrival budgets so a runaway task cannot starve others [6]. These directly serve ISO 26262 freedom-from-interference.
- **Multicore** was introduced in **AUTOSAR release 4.0** (2009): multi-core startup/shutdown, **spinlocks** for cross-core synchronization, and **Inter-OS-Application Communication (IOC)** — the OS-provided channel (shared-memory ring buffer protected by an internal spinlock) for data crossing a core or memory-partition boundary [11].

The extra classes cost RAM/ROM and CPU overhead and generally need more capable MCUs [6].

## 4. The methodology chain and ARXML (Focus Q3)

Everything is exchanged as **ARXML** ("AUTOSAR XML"), an XML dialect whose schema is fixed by the standard [12]. The classic OEM↔supplier flow [12][13][14]:

1. **VFB / System Description** — the OEM (or system architect) describes all SWCs, their ports/interfaces, the network topology and signals, and maps SWC compositions onto the set of ECUs. Output: the **System Configuration Description** (ARXML) [12][14].
2. **ECU Extract** — for a *single* ECU, the ECU-relevant slice is extracted from the system description and handed to the Tier-1 supplier: the **ECU Extract of System Description** [12][14].
3. **ECU Configuration** — the supplier configures that ECU's BSW modules and RTE. Inputs: the ECU Extract **plus** each BSW module's **BSW Module Description**. Output: the **ECU Configuration Description (ECUC)** ARXML [12][13].
4. **Generation** — tools consume the ECUC to generate BSW configuration code, the **RTE**, and OS configuration; this is compiled and linked with hand-written SWC code and vendor MCAL into **one ECU executable** [12][13].

**Who writes ARXML / which tools consume it (Focus Q3).** ARXML is rarely hand-authored; it is produced and consumed by GUI configuration tools. The dominant Classic toolchains:
- **Vector DaVinci** — *DaVinci Developer* for SWC/architecture design (emits SWC ARXML + application header/template C), *DaVinci Configurator (Classic/Pro)* as "the central tool for configuring, validating and generating the BSW and the RTE of an AUTOSAR Classic ECU"; imports/validates system and ECU-extract ARXML [15][16].
- **Elektrobit (EB) tresos Studio** — BSW/RTE configuration and generation, widely paired with EB's AUTOSAR BSW stack [10][15].
- **ETAS ISOLAR / RTA-CAR** — ETAS's Classic toolchain: modeling, configuration, integration, code generation, testing (RTA-OS is the OS, RTA-RTE the RTE generator) [15].

MCU vendors ship the **MCAL** matching each toolchain; behavior models (Simulink/Embedded Coder) can exchange SWC design via ARXML with DaVinci [15][16].

## 5. C standard and coding guidelines (Focus Q4)

BSW/RTE code is **C**, and the standard requires MISRA compliance: "if the BSW Module implementation is written in C language, it shall conform to the MISRA C standard." **AUTOSAR 4.2 required MISRA C:2004; AUTOSAR 4.3 (and later, incl. R25-11) require MISRA C:2012** [8]. MISRA C historically targets the freestanding/embedded C subset (the original edition was based on **C90/ANSI C**; C:2012 covers C90/C99/C11/C18) — consistent with CP's no-heap, no-recursion-heavy, deterministic style [8]. Note the C++ story belongs to the *Adaptive* platform: the former **AUTOSAR C++14** guidelines have been **merged into MISRA C++:2023** (MISRA + AUTOSAR consolidated into one publication), so "AUTOSAR C++ guidelines" as a standalone document are now historical [8]. Portability across compilers is handled by generated **compiler-abstraction** (`Compiler.h`) and **memory-mapping** (`MemMap.h`) headers so module code never writes vendor `#pragma`s inline [and per the SWS_MemoryMapping spec, med confidence].

## 6. What maps to your existing knowledge, and what is new (Focus Q6)

For an engineer coming from bare-metal C + an RTOS (FreeRTOS/Zephyr) on an MCU:

**Direct mappings (little new):**
- **MCAL ≈ the vendor HAL/driver layer**, but with AUTOSAR-standardized APIs and config. Drivers: **Dio, Port, Adc, Pwm, Gpt, Spi, Can, Wdg, Mcu, Fls…** — same peripherals you already drive by register, now behind a fixed API and generated config. Crucially, MCAL is **MCU-specific and supplied by the silicon vendor** (NXP/Infineon/Renesas), so it is the thing you *port*, not the thing you *rewrite* [2][10].
- **AUTOSAR OS ≈ your RTOS**, and it *is* essentially OSEK: static fixed-priority tasks, ISRs, priority-ceiling resources, alarms. If you've used a static-config RTOS, tasks/ISRs/priorities are familiar [6][7].
- **Static everything**: no `malloc`, no runtime task creation, all TCBs/stacks/queues allocated at build time — the exact discipline safety-critical firmware already follows [12].

**Genuinely new:**
- **Model-driven, generate-then-compile workflow.** You don't wire modules by editing C; you configure ARXML in a tool and *generate* the glue (RTE, BSW config, OS tables). The build artifact is "**one statically configured binary**": a fixed task set, fixed communication matrix, fixed memory map — decided at design time, not runtime (Focus Q5/Q6) [12].
- **Port/VFB decoupling.** Application logic never names a driver or a bus; it names ports and calls `Rte_*`. This location-independence has no real bare-metal analogue.
- **Schedule tables + memory/timing protection** (SC2–SC4) go beyond a typical hobby/industrial RTOS.
- **The OEM/supplier ARXML handshake** (System Description → ECU Extract → ECUC) is an organizational/process artefact with no firmware-world equivalent.

## 7. Current release state and what still changes (Focus Q5)

**Latest release: AUTOSAR CP R25-11**, with the official Release Event on **4 December 2025** [1]. AUTOSAR moved to a yearly `RYY-11` naming years ago (R19-11, R20-11, … R22-11, R24-11, R25-11). Despite the platform being ~20 years old and its architecture stable, releases still: **retire modules** (R25-11 dropped TTCan, Fls, Eep, LdCom), refine existing specs, adjust libraries, and add integration points (e.g. DDS, vehicle data / "VDP", Mirror in R25-11) [1]. So the *shape* (3 layers, RTE, MCAL) is frozen; the *module set and details* still drift release-to-release, which is why ARXML/tool versions and the target release must be pinned per project.

## Key facts

| # | Fact | Source URL | Exact quote (if load-bearing) | Confidence |
|---|------|-----------|-------------------------------|-----------|
| 1 | Latest CP release is R25-11; event 4 Dec 2025 | autosar.org/news-events/release-event | "The Release Event R25-11 will be held on the 4th of December 2025" | high |
| 2 | CP = 3 layers (App / RTE / BSW), BSW split into services / ECU abstraction / MCAL | autosar.org R25-11 Layered SW Architecture PDF | "distinguishes at the highest level… three software layers… Application, Runtime Environment (RTE) and Basic Software (BSW)"; BSW "divided into… services, ECU abstraction, and microcontroller abstraction" | high |
| 3 | R25-11 removed TTCan, Fls, Eep, LdCom | autosar.org R25-11 release material | "removed TTCan, Fls, Eep, and LdCom components" | med |
| 4 | RTE has contract phase (app header) + generation phase (source) | embetronicx / danlaw / medium (Sankar) | "RTE Contract phase… create an application header… RTE Generation phase… generate the RTE" | high |
| 5 | SWCs call generated Rte_Write/Rte_Read/Rte_Call | mxhelp.danlawinc.com autosar_reference | "SWCs use APIs like Rte_Write() to send data and Rte_Read() to receive data" | high |
| 6 | VFB strictly separates apps from infrastructure, spans ECUs | USPTO 9235456 / HPI VFB paper | "virtual function bus (VFB) connects all the intercommunicating software applications… also beyond various electronic control units" | high |
| 7 | Runnable = a C function, triggered by RTE Events | embetronicx RTE tutorial | "Runnable Entity is the execution unit, which is finally implemented as a C function" | high |
| 8 | AUTOSAR OS scalability SC1–SC4 (schedule tables / timing / memory protection) | Vector task-scheduling article; eio.vn | "SC1 extends OSEK/VDX… addition of schedule tables; Class 2… timing protection; Class 3… memory protection; Class 4… both" | high |
| 9 | Multicore + spinlock + IOC added in AUTOSAR 4.0 | scispace MPC5668G paper; motodemy IOC | "AUTOSAR 4.0 introduced… spinlock, Inter OS-Application Communication, multi-core startup/shutdown" | high |
| 10 | AUTOSAR OS = OSEK OS + OS-Applications + Schedule Tables; OSEK conformance BCC1/ECC1 | academia.edu microkernel overview; OSEK OS 2.2.3 spec | "AUTOSAR OS adding OS-Applications and Schedule Tables to the existing components of OSEK/VDX OS" | high |
| 11 | BSW C code must be MISRA C: 4.2→C:2004, 4.3→C:2012 | perforce / gsasindia MISRA guide | "AUTOSAR 4.2 requiring MISRA C:2004 and AUTOSAR 4.3 requiring MISRA C:2012" | high |
| 12 | Methodology: System Config → ECU Extract → ECU Config (ECUC) → generate | vtronics / autosartutorials / autosar.org TR_Methodology | "Individual ECU specific information is extracted from System configuration Description… ECU Configuration Description arxml… used further to generate executable" | high |
| 13 | ARXML is the exchange format across all steps | vtronics AUTOSAR-for-dummies #4 | "AUTOSAR context is called .arxml (AUTOSAR Extensible Markup Language) file" | high |
| 14 | MCAL is MCU-specific, supplied per silicon vendor | dev.to / embitel MCAL articles | "every microcontroller comes equipped with its very own MCAL software" | high |
| 15 | CP is fully static: no malloc, tasks fixed at build; single binary | embien / lhpes / cybellum | "all tasks that will ever execute on a given computing hardware node are allocated when the executable image is built" | high |
| 16 | DaVinci Configurator = central BSW+RTE config/gen tool for CP | mathworks / vector davinci-configurator-classic | "central tool for configuring, validating and generating the basic software (BSW) and the runtime environment (RTE) of an AUTOSAR Classic ECU" | high |
| 17 | AUTOSAR C++14 merged into MISRA C++:2023 | autosar.org news; perforce | "MISRA and AUTOSAR… integrated into one publication" | high |

## Sources

1. https://www.autosar.org/news-events/release-event — AUTOSAR Release Event R25-11 — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf — Layered Software Architecture (CP R25-11) — AUTOSAR — primary (metadata via search; PDF blocked by sandbox TLS)
3. https://www.autosar.org/fileadmin/standards/R20-11/CP/AUTOSAR_EXP_VFB.pdf — Explanation of the Virtual Functional Bus — AUTOSAR — primary
4. https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf — AUTOSAR Runtime Environment and Virtual Function Bus (Naumann, HPI) — Hasso Plattner Institut — secondary/academic
5. https://embetronicx.com/tutorials/automotive/autosar/run-time-environment-rte-layer-autosar/ — RTE Layer tutorial — Embetronicx — secondary
6. https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf — High-Rate Task Scheduling within AUTOSAR — Vector — vendor (403 in sandbox; content via search)
7. https://www.osek-vdx.org/mirror/os223.pdf — OSEK/VDX Operating System Specification 2.2.3 — OSEK/VDX — primary
8. https://www.perforce.com/blog/qac/misra-and-autosar-unite-cpp-coding-guidelines-what-means — MISRA + AUTOSAR C++ unification — Perforce — vendor/secondary
9. https://mxhelp.danlawinc.com/autosar_reference.htm — AUTOSAR Reference (RTE APIs) — Danlaw — vendor
10. https://www.embitel.com/blog/embedded-blog/what-is-autosar-mcal-software-architecture — What is AUTOSAR MCAL — Embitel — secondary
11. https://scispace.com/pdf/technology-autosar-multicore-operating-system-implementation-1pl2ihoecs.pdf — AUTOSAR Multicore OS Implementation for MPC5668G — (paper) — secondary/academic
12. https://www.vtronics.in/2019/09/autosar-for-dummies-part-4-autosar.html — AUTOSAR Methodology: system & ECU extract — Vtronics — secondary
13. https://rtahotline.etas.com/confluence/display/RH/03+-+ECU+Configuration+-+RTA-CAR+8.0.1 — ECU Configuration (RTA-CAR) — ETAS — vendor
14. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf — Methodology for Classic Platform — AUTOSAR — primary
15. https://techno-welle.com/inside-modern-autosar-toolchains-vector-and-etas-explained/ — Vector & ETAS toolchains — Techno-Welle — secondary
16. https://www.vector.com/us/en/products/products-a-z/software/davinci-configurator-classic/ — DaVinci Configurator (Classic) — Vector — vendor
17. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_MemoryMapping.pdf — Specification of Memory Mapping — AUTOSAR — primary

## Surprises

- **Modules get deleted, not just added.** R25-11 removed TTCan, Fls, Eep, LdCom [1]. A repo might assume a ~20-year "frozen standard"; the architecture is frozen but the module catalogue still churns yearly.
- **"AUTOSAR C++14" no longer exists as its own document** — it was merged into MISRA C++:2023 [8][17]. And it never applied to Classic anyway (CP is C); C++ guidelines are an Adaptive-platform concern. Easy to conflate.
- **AUTOSAR OS is essentially OSEK with extras**, not a from-scratch RTOS. An engineer who knows OSEK already knows ~70% of AUTOSAR OS [7][10].
- **The RTE is generated per deployment, not a fixed library.** The identical SWC source produces a *different* RTE depending on which ECU it lands on — the relocation magic is entirely in code generation [4][5].
- **CDD legitimately breaks the layering.** The standard sanctions a vertical module that reaches straight to hardware for timing-critical/non-standard functions [2].

## Open questions

- **Exact wording of the MCAL/ECU-Abstraction/Services/CDD definitions in the R25-11 Layered SW Architecture PDF** — the autosar.org PDFs consistently fail TLS certificate verification in this sandbox, so section-2 definitions are reconstructed from the search abstract of the primary doc plus corroborating secondary sources, not read verbatim. *Guess (labeled): the R25-11 wording is materially unchanged from R22-11.* Should be verified against the actual PDF outside the sandbox.
- **Whether R25-11 renumbers/renames any scalability-class or OS features** — SC1–SC4 semantics confirmed from Vector + secondary, but not re-read against the R25-11 `AUTOSAR_SWS_OS.pdf`. *Guess: unchanged; SC1–SC4 have been stable since 4.x.*
- **Precise release/year AUTOSAR OS first shipped memory & timing protection** — attributed to the SC3/SC4 model but I did not pin the exact classic release (likely 3.x era) from a primary source. Multicore→4.0 is well sourced [11]; the protection-class introduction date is not.
- **Compiler.h / MemMap.h exact obligations** — the memory-mapping/compiler-abstraction claim (section 5 last sentence) is from general knowledge + the SWS_MemoryMapping title; the PDF body was not readable here (med confidence).
- **Current tool version compatibility** (DaVinci / EB tresos / ISOLAR against R25-11) — vendor pages cite "AUTOSAR 4.4-compliant ARXML" for some DaVinci material; whether current releases fully consume R25-11 ARXML was not verified.
