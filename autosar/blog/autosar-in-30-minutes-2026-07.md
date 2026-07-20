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
Development Agreement was signed in July 2003. About 340 partners belong to it today (339 at the end of 2025). The
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

AUTOSAR OS is a static, fixed-priority real-time kernel. Its whole task set is fixed at build time,
it uses fixed-priority preemptive scheduling with priority-ceiling resources, and it has no heap,
much like a statically configured RTOS you already know, but stricter. It is packaged as Scalability
Classes SC1 through SC4, which add timing and memory protection.
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
| **SAFERTOS** | no POSIX personality; ships as a single static image |
| **Zephyr** | POSIX subset layer, single-image kernel, no MMU processes |
| **NuttX** | the most POSIX-faithful MCU RTOS (an optional MMU "kernel build" exists, but no `fork`/`exec`); still MCU-class |
| **AUTOSAR OS (CP's kernel)** | no POSIX by design; this is CP's OS |

The test is one question: does the OS support PSE51 *and* run MMU-isolated processes? If yes to both,
it can host AP. Any task-model RTOS stays on the MCU side with Classic.

## Twenty functional clusters, four that matter

R25-11 defines 20 functional clusters. Read the platform diagram as a map, not a checklist. Four
clusters matter most for the rest of this article:
Communication Management (`ara::com`), Execution Management (`ara::exec`), Diagnostic Management
(`ara::diag`), and Update & Configuration Management (`ara::ucm`). The `ara::` prefix is the C++
namespace under ARA where each cluster's API lives.

<!-- suggested figure: spec-ap-architecture-logical-view - the AP logical architecture with all functional clusters; AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1, (c) AUTOSAR -->

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

Three repositories are worth your time. Together they cover both platforms. The first two are open
Classic Platform stacks written in C, and the third shows the Adaptive side. Every repository state
below was verified on 2026-07-20, and each one is pinned to a specific commit: 7874929 for the
first, bfe1805 for the second, and 866d158 for the third.

The first is `Fang717/arccore-core-21` at commit 7874929. It is a full Classic AUTOSAR
basic-software stack written in C, and it is the Arctic Core embedded platform, version 21.0.0. Its
README describes it as "an open-source implementation of the AUTOSAR (Automotive Open System
Architecture) standard, designed for the development of automotive Electronic Control Units (ECUs)."
Inside it, `core/communication/` holds the communication chain: the COM signal-packing module, the
PDU Router (PduR), the CAN Interface (CanIf), the CAN Transport Protocol (CanTp) for segmentation,
and the Socket Adaptor (SoAd) for Ethernet, together with a bundled lwip 2.0.3 stack, which is a
small open-source Transmission Control Protocol and Internet Protocol (TCP/IP) implementation.
`core/system/` holds the static real-time operating-system kernel plus the state managers EcuM, BswM, and
SchM, and `core/diagnostic/` holds the diagnostic modules Dem, Dcm, and Det, which are the fault
store, the UDS server, and the development-time error tracer. The modules stamp themselves as
AUTOSAR 4.0.3 in release macros; `Com.h`, for example, sets `COM_AR_RELEASE` to 4/0/3. Hardware
support is broad. The microcontroller ports live under `core/mcal/arch/` (armv7_m, jacinto, mpc5xxx,
rh850_x, stm32, tcxxx, tms570, and zynq), with matching board configurations under `core/boards/`.
Note that `core/arch/` itself only holds a generic host target, which is a Linux simulation, plus
CAN transceivers. Read it for the shape of a real, complete Classic stack, and read the runnable
programs under `examples/` for the application and Runtime Environment layer above the module
internals.

There is one important caveat about what this repository actually is. It is an anonymous re-upload,
by the GitHub user Fang717, of a commercial-era vendor snapshot. It has no genuine development
history: all 8,481 source files were added in a single bulk "Initial commit" in June 2024, and no
later commit touches the code. The README states GPL-2.0 (GNU General Public License version 2), but
there is no top-level LICENSE file, the GitHub Application Programming Interface (API) reports no
license, and the per-file headers instead carry a dual notice, either a commercial ArcCore licence
or GPL version 2. The code is also old. The per-file copyright reads 2013 and 2014, so despite the
21.0.0 label and the 2024 upload, it is AUTOSAR 4.0.3-era code. Here is the start of its
`Com_SendSignal`, the service a task calls to publish an application signal:

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

[Fang717/arccore-core-21 @ 7874929 — core/communication/Com/src/Com_Com.c#L44-L52](https://github.com/Fang717/arccore-core-21/blob/7874929df54e45530720f15441cb3bc20479cebd/core/communication/Com/src/Com_Com.c#L44-L52)

Notice the vendor-typedef argument and return types, `Com_SignalIdType` and `uint8` rather than bare
C types, so the module behaves the same on every microcontroller. Before it does any work, it checks
that COM was initialized; if it was not, it reports a development-time error through the Default
Error Tracer (DET) and returns a service-not-available code, rather than touching uninitialized
configuration. The `/* @req COM334 */` tag links this exact line to a numbered clause in the AUTOSAR
COM specification, and that requirement-to-code traceability runs through the whole stack.

The second is `autoas/as` at commit bfe1805, and it is a very different Classic stack. Where Arctic
Core is an anonymous re-upload of a commercial snapshot, this one is written from scratch by a single
person as a Classic AUTOSAR 4.4 basic-software stack, mostly in C, with the modules under `infras/`.
Its README states the terms plainly: "This project is only free to be used for evaluation and study
purpose, all of the BSWs are developed by me alone according to AUTOSAR 4.4." It covers a broad set:
a communication stack (Com, PduR, CanIf, CanTp, plus SOME/IP, its service discovery, and a LIN
interface), the diagnostic modules (Dcm, Dem, and Det), memory services for non-volatile storage
(NvM, Fee, and Ea), cryptographic services, the Microcontroller Abstraction Layer (MCAL) drivers
(Can, Dio, Fls, and more), and a static real-time operating-system kernel with tasks, alarms, counters,
and resources under `infras/system/kernel/os/`. Unlike a bare stack, it also ships desktop tooling
alongside the code that runs on the microcontroller. `tools/generator/` is a per-module Python
configuration generator, and `tools/asone/` is a Qt graphical tool for Com, Dcm, and the flash
loader. It also provides a bootloader and CAN or LIN bus simulators over Internet Protocol sockets,
and the whole tree builds with the SCons build tool.

Know the limits here too. This is one person's project. The history shows a single maintainer, and
the README says the modules were "developed by me alone." The AUTOSAR 4.4 conformance is the
author's own claim, not a verified or certified result, so treat it as AUTOSAR-style rather than
compliant. The licence is internally inconsistent as well: the LICENSE file declares a dual GPLv3
(GNU General Public License version 3) or commercial grant, while the README restricts use to
evaluation and study only, and GitHub reports the licence as "Other." Some paths are still works in
progress. What makes this repository worth reading next to Arctic Core is that it implements the same
public services independently. Here is its own `Com_SendSignal`:

```c
Std_ReturnType Com_SendSignal(Com_SignalIdType SignalId, const void *SignalDataPtr) {
  Std_ReturnType ret = E_NOT_OK;
  const Com_SignalConfigType *signal;

  DET_VALIDATE(NULL != COM_CONFIG, 0x0A, COM_E_UNINIT, return E_NOT_OK);
  DET_VALIDATE(SignalId < COM_CONFIG->numOfSignals, 0x0A, COM_E_PARAM, return E_NOT_OK);
  DET_VALIDATE(NULL != SignalDataPtr, 0x0A, COM_E_PARAM_POINTER, return E_NOT_OK);

  signal = &COM_CONFIG->SignalConfigs[SignalId];
  ret = comSendSignal(signal, SignalDataPtr);

  return ret;
}
```

[autoas/as @ bfe1805 — infras/communication/Com/Com.c#L457-L469](https://github.com/autoas/as/blob/bfe1805f3cf61ddf0685aa981d64260bf9349cee/infras/communication/Com/Com.c#L457-L469)

It is the same COM publish service you just saw in Arctic Core, written by a different author. It
returns `Std_ReturnType`, the standard `E_OK` or `E_NOT_OK` contract, and it sets the result to
failure first, so the caller sees an error unless the send really succeeds. The three `DET_VALIDATE`
lines are the Classic development-error guards, all tagged with COM's service identifier 0x0A: they
reject an uninitialized module, an out-of-range signal identifier, and a NULL data pointer. The
signal is then fetched by index from a generated, read-only configuration table,
`COM_CONFIG->SignalConfigs`, which is the configuration-driven pattern again. The same repository
also lets you read the operating system underneath. Here is a slice from inside its `GetResource()`,
the priority-ceiling protocol:

```c
  if (E_OK == ercd) {
    if (TCL_TASK == CallLevel) {
      EnterCritical();
      ResourceVarArray[ResID].prevRes = RunningVar->currentResource;
      ResourceVarArray[ResID].prevPrio = RunningVar->priority;
      RunningVar->currentResource = ResID;
      if (RunningVar->priority < ResourceConstArray[ResID].ceilPrio) {
        RunningVar->priority = ResourceConstArray[ResID].ceilPrio;
      }
      ExitCritical();
```

[autoas/as @ bfe1805 — infras/system/kernel/os/kernel/resource.c#L74-L83](https://github.com/autoas/as/blob/bfe1805f3cf61ddf0685aa981d64260bf9349cee/infras/system/kernel/os/kernel/resource.c#L74-L83)

Taking a resource raises the running task's priority up to the resource's statically configured
ceiling, which is how the kernel prevents priority inversion and deadlock without ever blocking at runtime.
The previous priority and the previously held resource are saved first, so nested resource pairs
unwind like a stack, strictly last-in first-out. The whole update runs inside `EnterCritical()` and
`ExitCritical()` with interrupts masked, because it changes shared scheduler state, and it applies
only in task context, not in an interrupt handler.

The third is `langroodi/Adaptive-AUTOSAR` at commit 866d158, under the MIT open-source license. It is
a teaching codebase, and its README says, "The goal of this project is to implement the interfaces
defined by the standard for educational purposes." It gives you seven `ara::` clusters, which are
com, core, diag, exec, log, phm, and sm, in one readable C++ tree. The entry point in `src/main.cpp`
is about fifty-five lines: it builds Execution Management, spins a polling loop, and passes in the
manifests. The code composes the platform from an abstract SOME/IP `RpcClient` and an Execution
Management server built on top of it. You configure and build it with CMake, using the GCC or Clang
compiler, then run the unit tests with `ctest`, and launch the simulation by passing four `.arxml`
manifest files to the executable. Two honest limits go with it. The demo is not offline: it needs a
Volvo API key, an OAuth 2.0 (Open Authorization) token, and live network access to the Volvo
Extended Vehicle REST (Representational State Transfer) web API. And the code stops at the SOME/IP
transport level, with no generated `ara::com` Proxy or Skeleton facade above it. The repository is
dormant, and its last source commit was on 2023-06-22, so read it to learn the structure, not to run
it.

So here is the boundary. The building blocks and the teaching code are open. A complete, conformant,
open AP stack does not exist. The one complete official implementation, CAPI (Common Adaptive
Platform Implementation), is gated to AUTOSAR partners. iceoryx, Fast DDS, and CommonAPI are covered
too, on the full deck's building-blocks slides.

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
| **OS** | AUTOSAR OS, a static real-time kernel (SC1–SC4, no MMU) | not a new OS: an OS Interface on POSIX PSE51 over Linux/QNX/PikeOS |
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
