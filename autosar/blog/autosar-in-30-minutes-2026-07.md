---
title: "AUTOSAR in 30 minutes: Classic vs Adaptive, and what runs where"
date: 2026-07-17
tags:
  - autosar
  - classic-platform
  - adaptive-platform
  - embedded
  - functional-safety
---

This is a short field guide: one organization, two platforms, one vehicle. It is for engineers who
already know microcontrollers (MCUs), the Controller Area Network (CAN) bus, a real-time operating
system (RTOS), and bare-metal reflashing, and new to automotive software platforms. Every fact here
is tied to one release: AUTOSAR (AUTomotive Open System ARchitecture) R25-11, published 2025-11-27.
If you know the embedded basics, you have the model; the automotive world just gives the same ideas
new names.

## Why AUTOSAR exists

AUTOSAR is a worldwide development partnership, not a product. The first talks began in 2002. The
Development Agreement was signed in July 2003. About 360 partners belong to it today. The
specifications are free to read, and you license them to build a product.

One founding-era phrase captures the model: *cooperate on standards, compete on implementation*
(Heinecke et al., 2006). There is one shared specification and one XML schema. Many vendors sell
their own conformant stacks on top of it.

One business rule predicts adoption: AUTOSAR's value grows with the number of organizational
boundaries your software crosses. A Tier-1 is the supplier who builds an Electronic Control Unit
(ECU) for the vehicle maker. It implements AUTOSAR to win an original-equipment-manufacturer (OEM)
request for quotation (RFQ). A vertically integrated OEM such as Rivian skips AUTOSAR and builds its
own software. Keep that rule; the decision tree at the end is built on it.

## One vehicle, two platforms

AUTOSAR ships two platforms, and both run in the same 2026 car. The Classic Platform (CP) runs on
the deeply-embedded MCUs, which handle the fast, low-level control. The Adaptive Platform (AP) runs
on the high-performance-compute (HPC) System-on-Chip (SoC) silicon, which does the heavy computing.
The two are not competitors; they work together, joined by automotive Ethernet and gateways.

## Classic in one pass

In Classic, everything is static and decided at build time. The task set, the memory map, and the
communication matrix are frozen in ARXML (AUTOSAR XML) and generated into one ECU binary. There is
no `malloc`, no runtime task creation, and no service negotiation. Safety firmware already follows
this discipline by hand; CP makes it formal and generates the connecting code for you.

AUTOSAR OS is a backward-compatible superset of OSEK/VDX, the automotive RTOS standard from the
1990s, packaged as Scalability Classes SC1 through SC4, which add timing and memory protection.
Because everything is static, CP has the mature safety path. The first AUTOSAR implementation
certified to ISO 26262 up to ASIL D was released in 2016. ASIL D is the highest Automotive Safety
Integrity Level.

For a firmware engineer, the one truly new idea is relocation. Software Components (SWCs) never call
each other directly. They talk only over the Virtual Functional Bus (VFB), using `Rte_Write`,
`Rte_Read`, and `Rte_Call`, and they never name a bus or a driver. The Runtime Environment (RTE),
generated per deployment, decides whether the peer is a local buffer copy or a remote message on CAN
or Ethernet. Moving a component to a different ECU changes only the generated code, not your own.
There is no equivalent in bare-metal work.

<!-- suggested figure: vfb-relocation-annotated - the same SWC mapping unchanged onto ECU I/II/n over the VFB; redrawn and annotated after AUTOSAR CP_TR_VFB, R25-11, Fig. 2.2 -->

Communication uses a frozen communication matrix, the K-matrix. It is signal-oriented, not
service-oriented, and fixes every frame, signal, sender, and receiver at build time. The COM module
packs signals into Interaction-layer Protocol Data Units (I-PDUs) on CAN, LIN (Local Interconnect
Network), FlexRay, or Ethernet, generated statically and provable at integration time.

Diagnostics split into two modules that people often confuse. DEM, the Diagnostic Event Manager,
computes: the fault-memory database that debounces monitor results and maintains the per-DTC
(Diagnostic Trouble Code) UDS status byte. DCM, the Diagnostic Communication Manager, formats: a
generated UDS (Unified Diagnostic Services, ISO 14229) server that reads DEM and talks to the tester.
DCM computes nothing about faults.

Reflashing uses the bootloader you already know. UDS services 0x34, 0x36, and 0x37 (RequestDownload,
TransferData, and RequestTransferExit) flash the whole ECU.

<!-- suggested figure: stack-autosar-classic - the CP layered stack (Application -> RTE -> Basic Software -> MCAL) -->

## Why Adaptive exists

The strengths of Classic also become its limits. The static communication matrix gives no runtime
service discovery. There is no dynamic deployment, and only limited over-the-air (OTA) update of
function. The C-centric Basic Software (BSW) has no heap. So CP cannot host large, changing C++ and
perception stacks.

The AUTOSAR answer is a second platform, a service platform on POSIX (Portable Operating System
Interface). AP is middleware and services on top of a POSIX operating system. It is *not* a new OS. Adaptive Applications (AAs) are ordinary POSIX processes, written in C++ and linked against
ARA (the AUTOSAR Runtime for Adaptive Applications).

<!-- suggested figure: stack-autosar-adaptive - the AP stack (Adaptive Applications on ara:: over a POSIX OS on the HPC SoC) -->

## The requirement that decides your kernel

The spec makes POSIX a hard requirement. Adaptive Applications program against POSIX PSE51 plus the
C++ Standard Library (AP_SWS_OperatingSystemInterface, Doc 719, **[RS_OSI_00100] "POSIX PSE51
Compliance"**; PSE51 per IEEE 1003.13, following POSIX-1003.1-2003). The platform underneath also
needs a Memory-Management-Unit (MMU) multi-process OS. **[SWS_OSI_01010] "Virtual Memory"** requires
every Process to run in a dedicated, virtualized address space, and Execution Management spawns
*processes* per manifest.

That requirement sorts every kernel. The following can host AP:

| Can host AP | POSIX story |
|---|---|
| **QNX Neutrino** | full POSIX; PSE52-certified in the 2008 era, advertised today as conformance; the production default, ASIL-D via QNX OS for Safety |
| **Linux / AGL** (Automotive Grade Linux) | POSIX-conformant (not formally certified); development and QM (Quality-Managed, no ASIL) builds |
| **Green Hills INTEGRITY** | POSIX API on an MMU separation kernel |
| **PikeOS** | POSIX personality on a separation microkernel |
| **VxWorks** | POSIX plus user-mode processes (Real-Time Processes, RTPs); capable but rare in AP practice |

The following cannot host AP:

| Cannot host AP | why not |
|---|---|
| **FreeRTOS** (+Labs POSIX) | partial pthread subset. Its own README says a POSIX app *"cannot be ported... using only this wrapper"*. No processes |
| **SAFERTOS** | no POSIX at all (ships an OSEK layer instead); single static image |
| **Zephyr** | POSIX subset layer, single-image kernel, no MMU processes |
| **NuttX** | the most POSIX-faithful MCU RTOS (an optional MMU "kernel build" exists, but no `fork`/`exec`); still MCU-class |
| **AUTOSAR OS (OSEK)** | no POSIX by design; this is CP's OS |

The test is one question: does the OS support PSE51 *and* run MMU-isolated processes? If yes to both,
it can host AP. Any task-model RTOS stays on the MCU side with Classic.

## Twenty function clusters, four that matter

R25-11 defines 20 function clusters. Read the platform diagram as a map, not a checklist. Four
clusters matter most for the rest of this article:
Communication Management (`ara::com`), Execution Management (`ara::exec`), Diagnostic Management
(`ara::diag`), and Update & Configuration Management (`ara::ucm`). The `ara::` prefix is the C++
namespace under ARA where each cluster's API lives.

<!-- suggested figure: spec-ap-architecture-logical-view - the AP logical architecture with all function clusters; AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1, (c) AUTOSAR -->

## ara::com: one API, swappable bindings

`ara::com` is one protocol-agnostic API on a proxy/skeleton model. The application codes against it;
the integrator picks the wire binding in the manifest. There are three *standardized*
bindings: SOME/IP (Scalable service-Oriented MiddlewarE over IP), Signal-Based, and DDS (Data
Distribution Service), with DDS present since R18-03. Local Inter-Process Communication (IPC) is the
real path inside one machine, but it is implementation-level, not a standardized inter-vendor
protocol. The idea to remember: the API is protocol-agnostic, and the binding is swappable
underneath, exactly like the `rmw` middleware-abstraction layer over DDS in ROS 2 (Robot Operating
System 2).

<!-- suggested figure: aracom-bindings-annotated - the ara::com proxy/skeleton API over swappable wire bindings; redrawn and annotated after AUTOSAR AP_SWS_CommunicationManagement, R25-11, Fig. 7.1 -->

## The open-source projects

Four repositories are worth your time. Together they cover both platforms: the first is a complete
Classic stack, and the other three show pieces of the Adaptive side. All repository states were
verified 2026-07-16.

The first is `openAUTOSAR/classic-platform` at commit 09433770, under GPL-2.0 (GNU General Public License version 2). Its README calls it a
fork of the Arctic Core, the open-source AUTOSAR embedded platform, so it carries that lineage.
Inside it, `system/Os/rtos/` holds the OSEK-derived OS kernel, `communication/Com/` holds the COM
module that packs signals into I-PDUs, and `diagnostic/Dem/` holds the fault store. The `master`
branch has not changed since 2020-04-02, so read it as a textbook, not to run it. The
`Com_SendSignal` and `Dem_ReportErrorStatus` functions both sit in the tree with stable permalinks.
Here is the start of the first one:

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

[openAUTOSAR/classic-platform @ 09433770 — communication/Com/src/Com_Com.c#L44-L52](https://github.com/openAUTOSAR/classic-platform/blob/09433770bebb8f27a7b480d7c96d814c68ffed3e/communication/Com/src/Com_Com.c#L44-L52)

The second is `langroodi/Adaptive-AUTOSAR` at commit 866d158, under MIT. It is a teaching codebase,
and its README says the goal is to implement the interfaces defined by the standard for educational
purposes. It gives you seven `ara::` clusters, which are com, core, diag, exec, log, phm, and sm, in
one readable C++ tree. The code composes the platform from an abstract SOME/IP `RpcClient` and an
Execution Management server built on top of it. This repository is dormant, and its last source
commit was on 2023-06-22, so you should read it to learn the structure, not to run it.

The third is Eclipse S-CORE's communication module, nicknamed LoLa, at commit 6acba35, under
Apache-2.0. Its README describes a partial `ara::com` implementation, based on the Adaptive AUTOSAR
Communication Management specification. But its namespace is `score::mw::com`, not `ara::com`. It
ships a tutorial with a matching provider and consumer pair, and they follow the same skeleton and
proxy idioms as `ara::com`. Its README states that it is ASIL-B qualified.

The fourth is COVESA `vsomeip` at tag 3.7.4, under MPL-2.0 (Mozilla Public License). It is the SOME/IP wire binding that sits
under `ara::com`, and it is never the `ara::com` API itself. The repository ships runnable request
and response examples. It is the transport layer, not the Adaptive API.

So here is the boundary. The building blocks and the teaching code are open. A complete, conformant,
open AP stack does not exist. The one complete official implementation, CAPI (Common Adaptive Platform Implementation), is partner-gated.
iceoryx, Fast DDS, and CommonAPI are covered too, on the full deck's building-blocks slides.

## The shape of the code

Start with the standardized surface. The spec names the `ara::com` event-send API:
`Send({<s-sample-derived-type>})` and
`Send(ara::com::SampleAllocateePtr<SampleType>)` (AP_SWS_CommunicationManagement, R25-11, sec.
8.4.2.2.2). That is the contract vendors implement.

Now look at real code: the state handshake from an Adaptive Application to Execution Management, from
`langroodi/Adaptive-AUTOSAR` (inactive since 2023-06-22):

```cpp
            /// @brief Report the application internal state to Execution Management
            /// @param state Application current internal state
            /// @returns Void Result if the state reporting was successful, otherwise a Result containing the occurred error
            ara::core::Result<void> ReportExecutionState(
                ExecutionState state) const;
```

[langroodi/Adaptive-AUTOSAR @ 866d158 — src/ara/exec/execution_client.h#L54-L58](https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L54-L58)

Notice the return type: `ReportExecutionState` returns an **`ara::core::Result<void>`**, not `void`
plus a `throw`. AP signals errors as a *returned value*, not a thrown exception. That is exactly the
discipline an MCU engineer already follows after banning exceptions in safety code.
`ReportExecutionState` is the contract every Adaptive Application implements, so Execution Management
knows the process reached its running state (`kRunning`). On the `ara::com` side, the skeleton offer
lifecycle is also spec-named: `OfferService()` and `StopOfferService()` on the `ServiceSkeleton`
class ([SWS_CM_00101] / [SWS_CM_00111], same document). Read this for the structure, not production:
the repo has been inactive for three years.

## Classic vs Adaptive, the split that matters

Seven rows show the contrast:

| | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **Target** | deeply-embedded MCUs: Infineon AURIX, NXP S32K, Renesas RH850 | HPC SoCs: NVIDIA Orin/Thor, Qualcomm, NXP S32G, Renesas R-Car |
| **OS** | AUTOSAR OS, an OSEK superset (SC1–SC4, no MMU) | not a new OS: an OS Interface on POSIX PSE51 over Linux/QNX/PikeOS |
| **Model** | fully static: C, RTE-generated `Rte_Read/Write/Call`, one binary | dynamic: C++14, `ara::*`, manifests bound late; discovery plus start/stop at runtime |
| **Comms** | signal-oriented: COM packs signals → I-PDUs on CAN/LIN/FlexRay/Ethernet | service-oriented: `ara::com` proxy/skeleton over SOME/IP or DDS |
| **Diagnostics** | DCM plus DEM: UDS over DoCAN/DoIP | DM (`ara::diag`): UDS server *and* SOVD; DoIP the only standardized transport (custom permitted) |
| **Updates** | reflash the whole ECU: bootloader/UDS (0x34/0x36/0x37) | UCM: install/update individual Software Clusters; OTA-native |
| **Safety** | mature ISO 26262 up to ASIL D (first ASIL-D AUTOSAR impl certified 2016) | "up to ASIL D" on paper, harder in practice; ASIL-B shipping, ASIL-D underway |

Two notes go with the table. Here DM is AP's Diagnostic Management (`ara::diag`). DoCAN
(Diagnostics over CAN, ISO 15765-2) and DoIP (Diagnostics over IP, ISO 13400) are the two UDS
transports named in the Diagnostics row: CP runs UDS over both, while AP's DM standardizes DoIP only
(custom transports permitted). SOVD is Service-Oriented Vehicle Diagnostics, and UCM is Update and
Configuration Management. First, Classic is not CAN-only: a standardized SOME/IP Transformer has
shipped since 4.2.1 (October 2014), years before AP's first release. Second, the safety line is
exact. No fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026. ASIL-D lives in the
OS (QNX), the hypervisor, and the vendor safety case. And *developed to* ASIL-x is a process claim,
which is not the same as *certified at* ASIL-x.

## Coexistence: Adaptive plans, Classic controls the vehicle

The spec draws coexistence in one figure. Region A (blue tag) is the Adaptive Platform on the HPC,
the thinking side: it perceives the environment, driver, and vehicle state, fuses them into one
environment-and-state model, then runs maneuver and trajectory planning. Region C (teal tag) is
the Classic Platform side, the reflex side: the sensor-input boxes (camera, radar, lidar, inertial,
odometry, GPS, car-to-car, and car-to-infrastructure) and the trajectory-control-plus-safety-function
box.

Watch the arrows. Some sensor feeds run up into perception in Region A. Others run straight down into
the safety function, bypassing Region A. The safety side keeps its own sensor feed, so the
safe path does not depend on the high-compute path. If the HPC fails, the safety control still works.

A modern SDV runs both platforms at once, joined by Ethernet and gateways. The spec is explicit: AP
*"will not replace CP"*, and the two *"interact … to form an integrated system"*
(AP_EXP_PlatformDesign §3.4). Coexistence is the planned design, not a leftover from the past.

<!-- suggested figure: spec-ap-cp-interactions - Region A (AP: perception -> planning) and Region C (CP: safety function) with direct sensor-to-safety arrows; AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 3.2, (c) AUTOSAR -->

## Which stack on which silicon

One procurement question settles it: find your silicon row, and you know the stack and who sells it.

- **A-core SoC** (DRIVE Orin/Thor guest, NXP S32G/S32N, R-Car): QNX or Linux plus an AP stack, or a
  non-AUTOSAR middleware (the Rivian path). AP stacks come from Vector, Elektrobit (corbos), ETAS
  RTA-VRTE, and Qorix; the OS underneath is a separate procurement.
- **Safety island on the SoC** (lockstep Cortex-R52, the Thor Functional Safety Island, FSI): vendor
  safety firmware, plus a Vector FSI reference integration on Thor.
- **Companion / safety MCU** (RH850 on the Thor generation, AURIX on the Orin generation): CP, via
  the Vector-built AUTOSAR firmware NVIDIA ships as its reference integration. Vector's explicit
  MICROSAR Classic up-to-ASIL-D reference targets this companion MCU, not the island.
- **Zonal / domain MCUs** (NXP S32Z/E, AURIX, RH850): CP, from Tier-1 Classic stacks.
- **Small edge ECUs** (S32K class): CP or bare-metal/RTOS.

The same rule holds: integrated OEMs skip AUTOSAR; Tier-1s implement it to win RFQs.

## Fleet and diagnostics

Outside the car, the backend uses SOVD (a REST/JSON web API over HTTPS) plus MQTT (Message Queuing
Telemetry Transport) telemetry, never raw UDS. The vehicle's entry point is the TCU (Telematics
Control Unit). Inside the car, the central gateway is a DoIP router plus firewall: it routes DoIP/UDS
on the backbone and re-transports DoIP down to DoCAN on the Classic branches. Raw UDS is never
exposed to the internet.

<!-- suggested figure: fleet-uds-flow - backend (SOVD/MQTT) -> TCU -> central gateway (DoIP router + firewall) -> DoIP/UDS backbone and DoIP->DoCAN to CP branches -->

## The decision tree

Two questions choose your stack. Question one is where the function runs. A deeply-embedded MCU
sends you down the Classic branch. An HPC SoC with an MMU sends you down the Adaptive branch.

On the MCU branch, question two is about safety and the customer: what safety level must this ECU
carry, and who is the buyer? If the ECU carries an ASIL and you sell it to an OEM, the choice is
made for you. The RFQ demands AUTOSAR plus ASIL evidence, so you buy Classic on a pre-certified base
such as MICROSAR Safe. If it carries an ASIL but it is your own product, you have two honest options.
You can still buy Classic for the certified base, the vendor drivers, and the solved modules. Or you
can take a certified non-AUTOSAR RTOS such as SAFERTOS and carry the whole ISO 26262 safety case
yourself. That is the Rivian path, and it needs a real safety team. If the ECU is QM, no certificate
is needed, so the choice is free.

On the HPC branch, the safety story does not live in the middleware. It lives in the certified OS,
the hypervisor, the safety island, and the companion MCU, and that companion MCU runs CP. So question
two is only about supplier interoperability. Buy an AP stack if you need the standardized service
endpoints. Otherwise take the S-CORE path or build your own.

Every outcome still meets the same fleet contracts, whichever stack you picked. UDS and DoIP are
de-facto, not mandated. Telemetry is always an OEM cloud choice, and AUTOSAR standardizes none of it.
Skipping AUTOSAR forfeits the pre-built in-vehicle endpoints, but never fleet reachability. Rivian
says this on the record: *"We don't use any of the industry offerings such as AUTOSAR."*

<!-- suggested figure: stack-decision-tree - Q1 (MCU vs HPC) -> Q2 per branch -> five landings, with the shared fleet-contracts bar underneath -->

## Three takeaways

1. **AUTOSAR is a supply-chain standard.** Its value grows with the organizational boundaries your
   software crosses. ASIL comes from ISO 26262, not from AUTOSAR.
2. **Two platforms, coexisting by design.** Classic is static and runs on MCUs, with a mature ISO
   26262 path to ASIL D (first implementation certified 2016). Adaptive is a service platform on
   POSIX and runs on HPCs. This is a planned hierarchy, not old baggage.
3. **Find your silicon row on the decision map**, and you know the stack, the OS question, and who
   sells it.

To go deeper, everything lives in the same repository. The full deck at
`autosar/slides/autosar-deck.md` expands every point here with its primary-source references. The
local spec mirror at `autosar/specs/` holds all 35 R25-11 PDFs (Foundation, CP, and AP). The earlier
open-source deep-dive, `autosar/blog/adaptive-autosar-open-source-2026-07.md`, walks through the full
"what can you actually clone" question behind the set of projects above.
