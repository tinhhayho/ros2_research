# AUTOSAR Classic Platform — the deeply embedded half of the vehicle (July 2026)

**What this is.** A single synthesis of four Classic-Platform research notes
(`notes/classic-architecture.md`, `notes/classic-communication.md`,
`notes/classic-services-diag.md`, `notes/classic-safety-limits.md`), written for
embedded/firmware engineers who already know MCUs, CAN framing, an RTOS, and bare-metal
C but are new to automotive software platforms. Every external, load-bearing claim keeps
the source URL it was verified against in the notes; nothing new was invented here.
Anything the notes could not source is parked in **Open questions** rather than asserted.
Two binding files govern this doc where a note disagrees:
`notes/repo-constraints.md` (what this repo already ships + refuted folklore) and
`notes/orchestrator-verification.md` (primary-source R25-11 checks). Confidence hedges
from the notes are preserved — medium/low-confidence items are marked, not upgraded.
Release stamp: the current AUTOSAR release is **R25-11** (Release Event 4 December 2025).

---

## 1. What the Classic Platform is, and where it runs

AUTOSAR Classic Platform (CP) is a **statically-configured software stack for deeply
embedded automotive ECUs** — single microcontrollers, no MMU-class OS, hard real-time,
safety-critical. It is the OSEK-heritage half of AUTOSAR; its sibling, the Adaptive
Platform (AP), is a POSIX/C++ service-oriented platform for high-performance compute and
is out of scope here except as a contrast.

The defining property, the one an embedded engineer should hold onto through everything
below, is that a CP ECU builds to **one statically configured binary**: a fixed task
set, a fixed communication matrix, and a fixed memory map, all decided at design time,
not runtime. "All tasks that will ever execute on a given computing hardware node are
allocated when the executable image is built" (embien/lhpes/cybellum) — no `malloc`, no
runtime task creation, no dynamic service negotiation. This is exactly the discipline
safety-critical firmware already follows by hand; CP formalizes it and generates the
glue.

Where it sits in a 2026 vehicle: CP owns the **edge** — zonal ECUs, body/chassis/
powertrain controllers, and the **safety MCU** that gates actuators on high-compute
boards. The repo's verified example: on an NVIDIA DRIVE board the big SoC (Adaptive/
Linux/QNX) does perception and planning while a small lock-step safety MCU running CP
owns the fail-operational/fail-safe path and diagnostics. The safety-MCU generation
detail is pinned by `orchestrator-verification.md` and must not be misstated: the
**Orin** generation uses an **Infineon AURIX TC397X** running Vector firmware; the
**Thor** generation uses a **Renesas RH850U2A16**, with Vector MICROSAR Classic as the
reference integration. (The safety-limits note guessed "Thor uses an AURIX TC4x" — that
guess is **wrong**; never say Thor uses AURIX.) CP is not being retired at the edge; it
is the trust anchor for the powerful-but-less-certifiable compute above it.

A myth this repo has already killed, and this doc must not resurrect: **"Classic = CAN
only, Adaptive = Ethernet only"** is false. CP has had a standardized SOME/IP Transformer
since AUTOSAR 4.2.1 (Oct 2014) — over two years before Adaptive's first release (R17-03, March 2017)
— plus Ethernet, DoIP, LIN, and FlexRay.

---

## 2. The layered architecture and the build methodology

### 2.1 Three layers on one microcontroller

CP distinguishes, at the highest level, three software layers: **Application**, the
**Runtime Environment (RTE)**, and the **Basic Software (BSW)** (autosar.org R25-11
Layered SW Architecture PDF). The BSW is itself split into three horizontal layers plus
one vertical escape hatch:

| BSW sub-layer | What it does | Firmware analogy |
|---|---|---|
| **Services Layer** (top) | OS, communication + network management, memory (NVRAM), diagnostics, ECU state management — application-facing basic services | your middleware: UDS server, EEPROM manager, state machine, watchdog kicker |
| **ECU Abstraction Layer** | Abstracts the *board* wiring — which peripheral (on-chip or external) a signal routes through — so higher layers are independent of ECU topology | your board-support glue |
| **Microcontroller Abstraction Layer (MCAL)** (bottom) | Direct register-level access to on-chip peripherals; makes higher layers MCU-independent. MCU-specific, supplied by the silicon vendor (NXP/Infineon/Renesas) | **the vendor HAL, made standard** — the thing you *port*, not rewrite |
| **Complex Device Drivers (CDD)** (vertical) | Sanctioned escape hatch: spans all layers, may touch hardware directly, for functionality AUTOSAR does not standardize or that needs extreme timing (injection control, custom sensors) | a bare-metal ISR that bypasses your own abstraction because timing demands it |

The CDD legitimately breaks the layering — the standard sanctions it. Drivers you already
know by register (Dio, Port, Adc, Pwm, Gpt, Spi, Can, Wdg, Mcu, Fls…) live in MCAL behind
a fixed API and generated config.

### 2.2 SWCs, ports, the VFB, and why the RTE is generated

Application logic is packaged as **Software Components (SWCs)**. A SWC exposes **ports**
typed by **port-interfaces** — the main kinds are **sender-receiver** (data-flow, e.g. a
signal) and **client-server** (function call / operation), plus parameter, non-volatile-
data, mode-switch, and trigger interfaces. Inside a SWC, code is organized into
**runnable entities**, each ultimately "a C function" (embetronicx), activated by **RTE
Events** (periodic timing, data reception, operation invocation, mode switch).

SWCs never call each other directly. They talk over the **Virtual Functional Bus (VFB)**,
a *logical* concept that "connects all the intercommunicating software applications… also
beyond various electronic control units" (USPTO 9235456 / HPI VFB paper). The VFB is an
abstraction; the thing that actually implements it on a concrete ECU is the **RTE**.

The RTE is **generated per deployment** by an RTE-generator tool, in two phases
(embetronicx / danlaw):

- **Contract phase** — from the SWC's interface description it emits an application header
  (`Rte_<SWC>.h`) that "defines the contract between the component and the RTE," letting
  the SWC compile in isolation before integration.
- **Generation phase** — after component-to-ECU, runnable-to-task, and data/service
  mappings are known, it emits the real `Rte_*` source: the bodies that move data and
  dispatch runnables.

SWC code calls generated APIs — **`Rte_Write()`** (send), **`Rte_Read()`** (receive),
**`Rte_Call()`** (client-server). The developer does not know whether the peer is a
runnable on the *same* ECU (RTE turns it into a local buffer copy / direct call) or a
*remote* ECU (RTE turns it into a COM/PDU message over CAN/Ethernet). **This is why the
same SWC relocates to a different ECU without code changes**: it references only ports and
`Rte_*` symbols — never a bus, a driver, or another SWC — so moving it changes only what
the RTE generator emits. Deployment is a late-binding configuration decision realized by
regenerating the RTE. There is no real bare-metal analogue to this location-independence.

### 2.3 AUTOSAR OS — OSEK heritage and what was added

AUTOSAR OS is a **backward-compatible superset of OSEK/VDX OS** (ISO 17356-3) — not "= OSEK"
(that imprecision is refuted folklore). It keeps OSEK's core: statically-defined tasks,
fixed-priority preemptive scheduling, priority-ceiling resources, events, alarms,
counters, the BCC1/BCC2/ECC1/ECC2 conformance classes, and Category-1 ISRs (no OS calls,
lowest latency) vs Category-2 ISRs (may call OS services). An engineer who knows OSEK
already knows roughly 70% of AUTOSAR OS.

What AUTOSAR added, bundled as **Scalability Classes**:

| Class | = | Adds |
|---|---|---|
| **SC1** | OSEK OS + | **Schedule Tables** (statically-defined, time-triggered dispatch synchronizable to global time), counter interface, stack monitoring |
| **SC2** | SC1 + | **Timing Protection** (execution-time / inter-arrival budgets) + global time sync |
| **SC3** | SC1 + | **Memory Protection** + **OS-Applications** + service protection + trusted/non-trusted functions |
| **SC4** | SC2 + SC3 | Both timing and memory protection |

Schedule tables solve a real OSEK weakness — with bare alarms it is hard to keep a set of
activations in fixed phase; a schedule table is a dispatcher-driven sequence of expiry
points synchronizable to global time. **Multicore** arrived in **AUTOSAR release 4.0**
(2009): multi-core startup/shutdown, **spinlocks** for cross-core sync, and
**Inter-OS-Application Communication (IOC)** — a shared-memory ring buffer, spinlock-
protected, for data crossing a core or partition boundary. The extra classes cost RAM/ROM
and CPU and generally need a more capable MPU-equipped MCU. (The exact SC1–SC4 wording is
attested from Vector + secondary sources, not re-read against the R25-11 `SWS_OS.pdf`;
structure high-confidence, exact phrasing medium — see Open questions.)

### 2.4 The methodology chain, ARXML, and the toolchain

Everything is exchanged as **ARXML** ("AUTOSAR XML"), whose schema is fixed by the
standard, and it is rarely hand-authored — GUI configuration tools produce and consume it.
The classic OEM↔supplier flow (vtronics / autosar.org TR_Methodology):

1. **System / VFB Description** — the OEM describes all SWCs, ports, network topology and
   signals, and maps compositions onto the ECU set. Output: the System Configuration
   Description (ARXML).
2. **ECU Extract** — the ECU-relevant slice for *one* ECU is extracted and handed to the
   Tier-1 supplier: the "ECU Extract of System Description."
3. **ECU Configuration** — the supplier configures that ECU's BSW modules and RTE. Inputs:
   the ECU Extract **plus** each BSW module's BSW Module Description. Output: the ECU
   Configuration Description (**ECUC**) ARXML.
4. **Generation** — tools consume the ECUC to generate BSW config code, the RTE, and OS
   configuration; this compiles and links with hand-written SWC code and vendor MCAL into
   **one ECU executable**.

Dominant Classic toolchains: **Vector DaVinci** (Developer for SWC/architecture design;
Configurator as "the central tool for configuring, validating and generating the BSW and
the RTE of an AUTOSAR Classic ECU"), **Elektrobit (EB) tresos Studio**, and **ETAS ISOLAR
/ RTA-CAR** (RTA-OS is the OS, RTA-RTE the RTE generator). MCU vendors ship the MCAL
matching each toolchain.

BSW/RTE code is **C** and must be **MISRA C** compliant: AUTOSAR 4.2 required MISRA
C:2004; **4.3 and later (incl. R25-11) require MISRA C:2012** (perforce/gsasindia). The
"AUTOSAR C++14" guideline set was **merged into MISRA C++:2023** and is now historical —
and it never applied to Classic anyway (CP is C; C++ is an Adaptive concern; easy to
conflate). Portability across compilers is handled by generated compiler-abstraction
(`Compiler.h`) and memory-mapping (`MemMap.h`) headers so module code never writes vendor
`#pragma`s inline (medium confidence — SWS_MemoryMapping body not readable in-sandbox).

**What is genuinely new** for a bare-metal + RTOS engineer is not the OS (that is
essentially OSEK) or MCAL (that is a standardized HAL), but the **model-driven, generate-
then-compile workflow** and the **OEM/supplier ARXML handshake** — an organizational
artefact with no firmware-world equivalent.

---

## 3. Communication — signal to PDU to frame, frozen at build time

CP communication is **signal-oriented and frozen at build time**. It is a layered
pipeline of BSW modules, each doing one abstraction step, wired by build-time config.

### 3.1 The module chain (TX and RX)

**TX (application → wire), CAN example** (mohamedayman23 Medium, matching the SWS):

1. **SW-C / RTE** — application writes a value; RTE calls `Com_SendSignal`.
2. **COM** — packs the signal (bit position, length, endianness, sign extension all resolved at
   build time) into an **I-PDU** (byte array), applies TX modes (periodic/on-change),
   minimum delay, and can invoke the E2E/SOME/IP **transformer chain** here.
3. **PduR (PDU Router)** — a configurable routing table forwards the I-PDU to the correct
   lower module (CanIf for a normal PDU, CanTp first for a large one). PduR is also where
   **gateway routing** (bus-to-bus forwarding) happens.
4. **(CanTp)** — only if the PDU exceeds one frame's payload: segments into First Frame /
   Consecutive Frames with flow control (ISO 15765-2 style).
5. **CanIf** — ECU-abstraction: maps the abstract PDU to a hardware transmit handle/
   mailbox, manages controller/PDU mode, calls the driver.
6. **CanDrv (MCAL)** — writes the CAN/CAN FD frame; transmit confirmation propagates back
   up (CanIf → PduR → COM → RTE).

**RX** is the mirror: CanDrv ISR → CanIf indication → PduR → (CanTp reassembly) → COM
unpacks bytes into signals and runs reception deadline monitoring → RTE delivers to the
SW-C. Helper modules: **IpduM** multiplexes alternative sub-PDUs into one wire PDU and
handles container/contained PDUs. The same skeleton holds for other buses by swapping the
interface/driver: LIN → LinIf/LinTp/LinDrv, FlexRay → FrIf/FrTp/FrDrv, Ethernet →
SoAd/TcpIp/EthIf.

(Note: **LdCom**, a thin large-data path that bypasses signal packing, was **removed in
R25-11** — its functionality was **absorbed into Com** via the COMHandler concept, not
deleted; see §7.)

### 3.2 The frozen communication matrix

The **communication matrix (K-matrix)** is the master description of *all* network
communication in the vehicle: every frame/PDU, every signal, sender ECU, receiver ECUs,
byte layout, timing, and value encoding (scaling, offset, units). It is frozen because CP
targets small-flash/RAM, deterministic, ASIL ECUs with no dynamic allocation or runtime
negotiation: COM's packing, PduR's routing table, and CanIf's handle map are all
**statically generated** from the matrix, so timing and memory are provable at integration
time. A given ECU only ever sees the PDUs configured for it.

File-format lineage: historical exchange formats are **DBC** (Vector, CAN), **LDF** (LIN),
**FIBEX** (ASAM, multi-bus); AUTOSAR's own carrier is **ARXML**. Tools import DBC/LDF/
FIBEX, fill in AUTOSAR-specific parameters per the System Template, and export an ARXML
system extract (eeacom-docs.intrepidcs.com). For a firmware engineer: it is the CAN
"message database" (DBC) you know, promoted to a whole-vehicle, multi-bus, code-generating
source of truth.

### 3.3 SOME/IP on Classic — "static services, dynamic subscription"

CP can do service-oriented SOME/IP over automotive Ethernet, split across three modules:
**SomeIpXf** (the transformer that serializes VFB data to/from the SOME/IP on-wire
format), **SoAd (Socket Adaptor)** (maps PDUs to TCP/UDP sockets via TcpIp; must be
initialized before SD), and **SD (SOME/IP-SD Service Discovery)** (sends OfferService/
FindService, handles SubscribeEventgroup incl. multicast and TTL, interacting with BswM
and SoAd). The **structural limit**: even with runtime offer/find/subscribe, the *set of
services, their IDs, interfaces, and serialization layout are still fixed in ARXML and
code-generated*. CP cannot load new service software or renegotiate interfaces at runtime.
So CP SOME/IP is best described as **"static services with dynamic availability/
subscription"** — not dynamically deployable software the way AP is.

### 3.4 E2E protection — profiles and the fault model

**E2E (End-to-End)** protection guards safety-relevant data against communication faults
per ISO 26262. It is a library/transformer invoked in the COM transformer chain, so
protection travels **with the payload across ECU and bus boundaries — including through
PduR gateways**: the CRC and counter are computed at the true sender and checked at the
true receiver, so a bus-to-bus gateway cannot silently corrupt safety data undetected. The
PRS fault model: repetition, loss, delay, insertion, masquerade/incorrect addressing,
incorrect sequence, corruption, asymmetric information to multiple receivers, subset
reception, blocking of the channel (autosar.org PRS_E2EProtocol). Mechanisms: a **CRC**,
a **counter**, **timeout monitoring**, and a **Data ID** folded into the CRC.

| Profile | CRC | Typical use |
|---|---|---|
| P1 | 8-bit (CRC-8-SAE J1850), CP-only | legacy CAN |
| P2 | 8-bit, CP-only | legacy CAN (predefined Data ID lists) |
| P4 | 32-bit (CRC-32P4) | FlexRay/Ethernet, high Hamming distance, long data |
| P5 | 16-bit (CRC-16 CCITT-FALSE) | CAN/general |
| P6 | 16-bit | SOME/IP (aligned to SOME/IP layout) |
| P7 | 64-bit (CRC-64-ECMA) | very large Ethernet data, highest detection |
| P11 | 8-bit | LIN / simplified, P1-like |
| P22 | 8-bit | SOME/IP events, P5-family style |

An important non-obvious limitation that matters for ASIL decomposition: the **8-bit
profiles cannot detect a masquerading fault in a specific single cycle** (short
polynomial). (P1/P2 are labeled CP-only in the R19-03 PRS; not re-verified against a
newer FO E2E release — see Open questions.)

### 3.5 SecOC — authenticity, NOT confidentiality

**SecOC (Secure Onboard Communication)** adds **authenticity and freshness** to PDU
communication; it does **not encrypt** — payload stays in the clear (autosar.org
PRS_SecOcProtocol, R24-11). This is easy to overstate; the name misleads.

- On TX, SecOC builds a **Secured I-PDU** = Authentic I-PDU + **Authenticator (a MAC)** +
  optionally a (truncated) **Freshness Value** (always mixed into the MAC even when not
  transmitted).
- **Algorithm:** "Using the CMAC algorithm based on AES-128 according to NIST SP 800-38B
  to calculate the MAC" (Profile 1 = 24Bit-CMAC-8Bit-FV).
- **Truncation:** to fit tight CAN payloads the MAC is truncated to its most-significant
  bits and freshness to its least-significant bits. Profile 1 uses "the eight least
  significant bit of the freshness value… and the 24 most significant bits of the MAC as
  truncated MAC." Truncation lowers the security level — an explicit, configurable
  bandwidth/security tradeoff.
- **Freshness** comes from a Freshness Manager (monotonic counter or timestamp) shared by
  sender and receiver — this is what defeats **replay**.

**Honest guarantee:** a receiver that verifies the MAC knows the message (1) came from a
holder of the shared symmetric key (data-origin authentication, which implicitly provides
data integrity) and (2) is fresh, not a replay — *provided* key distribution and freshness
sync are sound. It does **not** hide the data and, being symmetric, gives no
non-repudiation. Key management is out of SecOC's scope; it relies on the Crypto stack
(CSM/CryIf/Crypto driver) for keys. (The literal "no confidentiality" sentence is inferred
from the PRS scope, not quoted verbatim — medium confidence.)

### 3.6 Network management, partial networking, and the 2026 bus landscape

**Network Management (NM)** coordinates "one or more groups of ECUs to wake up and shutdown
their communication stack synchronously" (autosar.org PRS_NetworkManagementProtocol) via
periodic NM messages in an NM cluster: receiving them means "keep awake"; when a timer
elapses with no NM messages, all nodes transition together to Bus-Sleep (via Prepare
Bus-Sleep). A bus-independent NM Interface coordinates **CanNm / FrNm / UdpNm**. This is
how a parked car saves battery with no single master.

**Partial Networking (PN)** lets a *subset* of ECUs on a shared bus sleep while others stay
awake (keep the door module alive while powertrain sleeps). Each bit of the PN Info Range
in the NM Control Bit Vector represents one **Partial Network Cluster (PNC)**; dedicated
PN-capable CAN transceivers wake the controller only on matching frames.

**Bus landscape (2026):** **CAN FD** is mainstream in CP (up to 64-byte payload, faster
data phase); classic CAN survives for low-cost/legacy nodes. **FlexRay is in decline** —
squeezed by CAN FD from below and automotive Ethernet from above ("CAN FD will eat up
FlexRay's market share," eeNews) — but AUTOSAR still specifies FrIf/FrNm/FrTp, so it is
supported, not removed. **Automotive Ethernet** (100/1000BASE-T1, TSN) is the growth path,
carrying SOME/IP and DoIP. **CAN XL** (ISO 11898-1:2024, up to 2048-byte payloads) is
emerging (AUTOSAR support release unconfirmed — see Open questions).

---

## 4. The Services layer — diagnostics, memory, mode, watchdog, time

The single most important mental model in this section: **DEM is the fault database and
status-byte engine; DCM is the protocol server that reads that database and talks to the
tester.** Getting this split wrong is the #1 conceptual error.

### 4.1 DCM vs DEM vs FiM

**DEM (Diagnostic Event Manager)** is the fault memory. SWCs and BSW modules report a
monitor result (Passed/Failed) for a diagnostic event via `Dem_SetEventStatus(...)`. DEM
**debounces** that raw result, decides when a fault is mature, maintains the per-DTC **UDS
status byte**, and stores freeze frames / extended data to NvM — it is a *client* of the
memory stack, it never touches flash itself ("shall use the API `NvM_WriteBlock`…",
autosar.org DEM SWS R24-11).

The 8-bit UDS status byte, "as defined in ISO 14229-1, based on DTC level," lives in DEM:
bit 0 `testFailed`, bit 1 `testFailedThisOperationCycle`, bit 2 `pendingDTC`, bit 3
`confirmedDTC` ("malfunction was detected enough times to warrant… stored in long-term
memory"), bit 4 `testNotCompletedSinceLastClear`, bit 5 `testFailedSinceLastClear`, bit 6
`testNotCompletedThisOperationCycle`, bit 7 `warningIndicatorRequested`. Readiness (OBD
complete/incomplete) is derived from bits 4 and 6. Debouncing is per-event and uses one of
three algorithms — **counter-based** (PREFAILED increments by
`DemDebounceCounterIncrementStepSize`, crossing `DemDebounceCounterFailedThreshold` latches
FAILED), **time-based**, or **monitor-internal**.

**DCM (Diagnostic Communication Manager)** is the protocol server — "in charge of the UDS
and SAE J1979 communication path… responsible for assembly of response messages" (DEM
SWS). It **computes nothing about faults**: on service 0x19 (ReadDTCInformation) it calls
into DEM (`Dem_DcmGetStatusOfDTC`, …) and formats the answer. DCM is a generated,
dumb-but-strict UDS server.

**FiM (Function Inhibition Manager)** is the third leg, downstream of DEM: "The Dem informs
and updates the Function Inhibition Manager (FiM) upon changes of the monitor status in
order to stop or release function entities." If fault A is active, FiM inhibits monitor B
that would give a false reading — it prevents cascade/false DTCs.

The full pipeline: **SWC monitor → PREFAILED/PREPASSED → DEM debounce → FAILED/PASSED →
status byte + confirmation counter → (matured) NvM store → DCM reads on request.**

### 4.2 A 0x22 (ReadDataByIdentifier) DID read through the stack

For a *live application value* (autosar.org DCM SWS R24-11):

1. Tester frame → CanTp/DoIP reassembles → **PduR** routes the request PDU to **DCM**.
2. DCM's **DSD** (Service Dispatcher) checks the service table; unknown service → NRC 0x11.
3. DCM's **DSP** (Service Processor) handles 0x22: verifies the DID exists and is permitted
   in the current **session and security level** — else NRC 0x31 (requestOutOfRange) or
   0x33 (securityAccessDenied).
4. DSP reads the data element: the DID's `DcmDspData` container either names an application
   **read callout** or is bound to an RTE **port** ("the Dcm can directly access
   `SenderReceiverInterface`").
5. The RTE resolves the binding — calls the SWC's runnable, or hands DCM the last value the
   SWC wrote. The SWC returns the raw bytes.
6. DCM assembles `0x62 <DID_hi> <DID_lo> <data…>` and sends it back down PduR → transport →
   tester.

Mental model: DCM is a generated UDS server; a DID is a table row mapping a 2-byte
identifier to either a getter function pointer or a shared variable, and the RTE resolves
that binding at generation time. (Related, and consistent with this repo's prior UDS work:
SID 0x2A ReadDataByPeriodicIdentifier is a *diagnostic* periodic push — time-polled,
session-scoped, 0xF2xx-DID-limited — **not** a fleet telemetry channel; continuous
telemetry runs on telematics pipelines, MQTT/proprietary.)

### 4.3 The NvM memory stack

Top to bottom: **NvM → MemIf → {Fee → Fls} or {Ea → Eep}** (autosar.org NVRAMManager
SWS).

- **NvM (NVRAM Manager)** — the service every SWC talks to; manages logical **NVRAM
  blocks**, each a set of storage objects (mandatory NV block, RAM working copy, optional
  ROM default/rollback, admin block). Block management types: **Native** (1 NV block),
  **Redundant** (2 copies, recovers from the good one — for safety-critical calibration),
  **Dataset** (array of equal sub-blocks, index chosen at runtime). Integrity is optional
  per-block CRC. Write strategies: `NvM_WriteBlock` for single writes; `NvM_ReadAll` at
  startup and **`NvM_WriteAll` at shutdown (invoked by EcuM)** to flush permanent blocks.
- **MemIf** is a thin dispatcher routing NvM requests to Fee or Ea by device index,
  unifying their APIs so NvM is device-agnostic.
- **Fee (Flash EEPROM Emulation)** sits on the **Fls** flash driver; **Ea (EEPROM
  Abstraction)** sits on the **Eep** EEPROM driver.

MCU-firmware mapping: NvM ≈ your key/value non-volatile parameter manager; the RAM block ≈
your in-RAM shadow struct; `NvM_WriteAll` ≈ the "save settings on ignition-off" routine you
fire from a brown-out/shutdown ISR. **Fee is the one to internalize**: it is the
standardized version of the flash-as-EEPROM *wear-leveling + sectored, log-structured
emulation* layer you hand-write when an MCU has flash but no byte-erasable EEPROM — sector
swapping and garbage collection included. It is **not** "a flash driver"; Fls/Eep are the
MCAL register-level drivers.

**R25-11 nuance (binding, per `orchestrator-verification.md`):** R25-11 set **Fls and Eep**
to "removed," but they have **successors** — R25-11 still ships "Specification of Memory
Access" (**MemAcc**) and "Specification of Memory Driver" (**Mem**), the generic
memory-driver pair replacing the part-specific Fls/Eep. The teaching stack NvM → MemIf →
{Fee | Ea} remains valid; only the bottom driver layer was modernized. Do **not** write
"R25-11 removed flash support" or present NvM→Fee→Fls as the current-release wiring without
this footnote.

### 4.4 EcuM vs BswM — bootstrap vs steady-state

Both are mode managers, at different phases (autosar.org Mode Management Guide):

- **EcuM (ECU State Manager)** owns the *edges* of the lifecycle. `EcuM_Init` takes control
  of startup, initializes the OS scheduler, drivers, and BSW up to `StartOS`, then
  "temporarily relinquishes control." It manages **wakeup sources**, sleep, and shutdown
  targets (SLEEP/RESET/OFF), and it is EcuM that calls `NvM_WriteAll` on the way down.
- **BswM (BSW Mode Manager)** owns *steady-state* mode arbitration. Once the OS runs, BswM
  "starts mode arbitration and all further BSW initialization; starting the RTE and
  (implicitly) starting SW-Cs becomes code executed in the BswM's action lists." It is a
  **rule engine**: mode requests → conditions → action lists; it sets EcuM's coarse state
  via `EcuM_SetState` and triggers physical sleep/off via actions.

So: EcuM is the low-level state machine that boots and tears down the ECU; BswM is the
configurable rules engine that decides mode transitions (RUN/SLEEP, comm on/off, partial
networking) while alive and asks EcuM to execute the physical sleep/off. In the modern
"flexible ECU management" scheme most decision logic moved from EcuM-Fixed into BswM rules.

### 4.5 OBD (statutory) vs UDS (contractual) in DCM

DCM implements two protocol families side by side. **UDS / ISO 14229-1** is the "enhanced"
diagnostics — session control (0x10), ECU reset (0x11), read/write DID (0x22/0x2E), read
DTC (0x19), clear DTC (0x14), security access (0x27: sub-func 0x01 requestSeed / 0x02
sendKey), routine control (0x31), request download/upload + transfer data (0x34/0x35/0x36/
0x37) for reflash. These are manufacturer-defined and **not legally mandated in content**.
**OBD / ISO 15031-5 + SAE J1979** is the *legislated* emissions diagnostics: DCM supports
"OBD services $01–$0A… capable of meeting all light duty OBD regulations worldwide"
(autosar.org DCM SWS). **Only emissions-relevant ECUs** (engine/powertrain, increasingly
EV/hybrid propulsion) are legally obligated, and only for $01–$0A. A body/comfort/chassis
ECU has **no statutory OBD duty** — it typically serves only UDS. Bottom line: **UDS is
contractual; OBD $01–$0A is statutory, and statutory only for emissions ECUs.**

### 4.6 Watchdog (WdgM/WdgIf) and time sync (StbM)

**WdgM (Watchdog Manager)** supervises program *flow*, not just liveness. Units are
**Supervised Entities** with **Checkpoints**, and it does three supervision types
(autosar.org WdgM SWS R23-11): **Alive Supervision** (a checkpoint reached the right number
of times within a window — catches too-fast/too-slow execution), **Deadline Supervision**
(elapsed time between two checkpoints within min/max — catches an overrunning runnable),
and **Logical Supervision** (checkpoints occur in the allowed control-flow order — catches
corrupted program flow). WdgM aggregates local results and, **only while everything is
correct**, calls `WdgIf_SetTriggerCondition` so the hardware watchdog keeps being serviced;
a failure withholds the trigger and the HW watchdog resets the ECU. **WdgIf** multiplexes
multiple Wdg driver instances (internal + external SBC watchdog). Firmware mapping: WdgM is
a *windowed, flow-aware* watchdog framework, far beyond a single `IWDG_Refresh()` kick —
closer to an ASIL-oriented program-flow monitor.

**StbM (Synchronized Time-Base Manager)** is the ECU's bus-agnostic time hub. It maintains
**Time Bases**; a **Global Time Master** distributes time to **Time Slaves** via time-sync
messages (gPTP/802.1AS for Ethernet, or CAN/FR time-sync) handled by bus-specific
`<Bus>TSyn` modules. It supports Rate and Offset Correction; Time Domains 16–31 are Offset
Time Bases layered on Synchronized Time Bases (0–15). Firmware mapping: StbM ≈ your
PTP/time-of-day service, decoupled from the transport.

---

## 5. Functional safety and real-time guarantees

CP's safety story rests on the OSEK-derived OS delivering ISO 26262 **freedom from
interference (FFI)** across three dimensions — memory, timing, execution — plus E2E for the
communication path. AUTOSAR's *Overview of Functional Safety Measures* (Doc ID 664)
enumerates them.

### 5.1 OS-Applications + MPU = freedom from interference

The memory mechanism is **Memory Partitioning** via **OS-Applications**: "One Partition
will be implemented using one OS-Application"; "The AUTOSAR Operating System provides
freedom from interference for memory-related faults by placing OS-Applications into
separate memory regions… OS-Applications are protected from each other, as code executing
in the Memory Partition of one OS-Application cannot modify [the memory of another]" (Doc
664). Enforcement is by the microcontroller **MPU**: untrusted partitions run in
user/non-privileged mode with MPU regions reprogrammed on context switch, so any
out-of-region access traps to a hardware exception regardless of software fault. AUTOSAR
distinguishes **Trusted OS-Applications** (may run with monitoring/protection disabled,
memory access not checked) from **Non-Trusted OS-Applications** (protection enabled, user
mode). This is the hardware-backed spatial FFI a firmware engineer knows from an
MPU-partitioned RTOS — standardized and tied to the ASIL argument.

An important **limit**: partitioning is at OS-Application granularity — "Memory
Partitioning cannot be used to separate Runnables within the same SW-C." If two Runnables
of one SWC need different ASIL ratings with independent FFI, partitioning must be pushed
down to Task level, which is awkward. FFI is real but coarse-grained; you architect around
the partition boundary. These SC1–SC4 protections map as in §2.3 (SC3 memory, SC2 timing,
SC4 both); an ASIL-D ECU mixing safety and QM software runs SC3 or SC4.

### 5.2 Where determinism comes from — and what timing protection is NOT

CP is hard-real-time because it is **statically everything**: OSEK-derived tasks/alarms/
resources configured entirely at build time, no dynamic memory, no runtime task creation,
fixed-priority preemptive scheduling with a priority-ceiling protocol to bound priority
inversion. Determinism comes from four familiar properties: **no heap** (no fragmentation,
no non-deterministic `malloc` latency), **static schedule tables** (offline time-triggered
activation, WCET-tractable), **no MMU dependence** (protection is MPU region-compare, not
virtual-memory paging, so no TLB-miss/page-fault jitter), and **Timing Protection as a
runtime backstop**.

Here is the genuine surprise, easy to get wrong on a slide: **"The AUTOSAR OS does not
offer deadline supervision for timing protection"** (Doc 664). Timing Protection enforces
three *budgets*, not deadlines:

- **Execution Time Protection** — an upper bound (Execution Budget) on a Task/Cat-2 ISR's
  execution time.
- **Locking Time Protection** — an upper bound (Lock Budget) on resource-hold /
  interrupt-disable time.
- **Inter-Arrival Time Protection** — a lower bound (Time Frame) between activations,
  catching runaway triggering.

**Deadline supervision itself is a separate Watchdog Manager job** (§4.6). And "Execution
time enforcement requires hardware support, e.g. a timing [protection timer]" — the
guarantee is only as good as the MCU's timer/MPU hardware.

### 5.3 E2E as a safety mechanism, and the certified reality

The communication path (RTE → COM → PDU router → bus driver → wire) is treated as
*untrusted*; E2E protects the *data*, not the channel: "protecting the data against the
effects of faults within the communication link" (Doc 664). This is what makes an ASIL
signal safe to send over an otherwise-QM CAN/Ethernet stack, and it is a joint CP/AP
mechanism. "Only the standardized End-2-End profiles shall be used." (Doc 664's R22-11 text
lists Profiles 1/2/4 with 5/6 upcoming; the fuller profile list in §3.4 comes from the FO
PRS — the two notes reflect different spec revisions, both preserved.)

The certified proof point is **Vector MICROSAR Classic Safe**, stated as "the world's first
AUTOSAR implementation to be successfully certified according to ISO 26262 up to ASIL D"
(2016), later **re-certified by exida** covering communication modules over Ethernet/J1939,
"the safe separation of software on different microprocessor cores" (multicore FFI), and a
method proving "upper limits for the execution time of the modules" — tying directly to the
execution-budget story. It is stated to meet ISO 26262 **up to ASIL D** at **ASPICE Level
3**. (Elektrobit EB tresos Safety OS and ETAS RTA-CAR make comparable ASIL-D claims;
verified only Vector directly this pass — see Open questions.)

Because §5.1–§5.3 give spatial + temporal + communication FFI, a single CP ECU can host
mixed-criticality software — ASIL-D braking logic in one MPU partition, QM comfort code in
another, on one or several cores.

---

## 6. Structural limits and why CP persists

CP's strengths invert into hard structural limits, and AUTOSAR's own R25-11 architecture-
decisions document (Doc ID 1078) frames the CP/AP split around them rather than treating it
as accident:

- **Static communication matrix.** Every signal/PDU connection is defined offline and
  resolved by the RTE into fixed macros/BSW calls at build time. No service discovery of
  new relationships; adding one means re-generating and re-flashing — "hard-wired… If you
  want software that can be replaced during run time, this does not work" (btc-embedded).
- **No dynamic deployment / limited OTA of function.** No runtime loading of applications;
  the ECU image is monolithic and static.
- **C-centric BSW, no dynamic memory.** CP's determinism *requires* no heap, which forbids
  the C++/STL ecosystem AUTOSAR itself calls "essentially indispensable" for Adaptive. CP
  cannot host large, evolving, object-oriented perception/AI stacks. AUTOSAR states dynamic
  allocation "can cause non-deterministic behavior. Two typical issues are the
  fragmentation and non-deterministic allocation/de-allocation processing time" (Doc 1078,
  R25-11) — and CP's refusal to take that on is the whole point. It trades flexibility for
  a determinism/certification story AP has to work hard to partially recover.
- **Tooling/licence and config friction.** Heavy configuration through licensed toolchains;
  high change cost, slow iteration (industry consensus; no primary metric — see Open
  questions).
- **Scaling pain on HPCs.** CP is built for single-digit-core MCUs with kB–MB memory, not
  many-core SoCs with GB RAM, POSIX, and Ethernet service meshes.

This is exactly why CP persists at the **edge**: its static determinism and ASIL-D
certification are what a **safety island** needs, and its inflexibility does not matter
there. The 2026 pattern is a **designed hierarchy, not legacy baggage** — the most advanced
AV compute still delegates the certified fail-safe path to a small lock-step safety MCU
running Vector *Classic*. On **DRIVE AGX Orin**, the safety MCU is the **Infineon AURIX
TC397X (B-Step)** running Vector firmware, with the safety island built around lock-step
R52 cores; for **DRIVE Thor**, Vector's "MICROSAR Classic Solution takes an essential
role… ISO 26262 up to ASIL-D" and is used "as reference integration for the companion
MCU," which is a **Renesas RH850U2A16** (per `orchestrator-verification.md` — not AURIX).
The big SoC does perception and planning; the small CP MCU owns actuator gating and
diagnostics. CP is the trustworthy watchdog on the powerful-but-less-certifiable compute,
and it is why CP lives on zonal ECUs across the vehicle. (Refuted folklore not to repeat:
Thor does *not* host "virtual Classic AUTOSAR ECU" partitions in a hypervisor — the SDK is
single-guest; Classic lives on the companion MCU. Thor is *not* a documented fleet UDS/DoIP
gateway.)

---

## 7. R25-11 currency notes

The *shape* of CP (three layers, RTE, MCAL, OSEK-derived OS) is frozen; the *module
catalogue* still churns yearly. R25-11's Release Event was 4 December 2025.

**DDS Transformer arrives on Classic (new in R25-11, CONFIRMED verbatim, high confidence
per `orchestrator-verification.md`).** From the R25-11 CP Release Overview §2.1.1.5 "DDS
Support on Classic Platform":

> "Management functionalities for Events, Methods, and Fields, previously available through
> SOME/IP, are now extended to DDS, offering increased flexibility thanks to its native
> capability of defining Quality of Service (QoS) parameters at various levels."

> "Introduction of full support of ClientServerInterface and the new BSW module DDS
> Transformer." … "Integration of the OMG SPDP and SEDP discovery protocols, along with the
> Service Discovery protocol already defined in the AUTOSAR Adaptive Platform, thus ensuring
> cross-solution compatibility."

New specs: `CP SWS DataDistributionServiceTransformer`, updates to `CP SWS
DataDistributionService`, and `CP RS Transformer` ("Added support of DDS Transformer").
**Caveat to preserve:** this is a *standard-level concept new in R25-11*; there is no
evidence yet of a shipping vendor implementation (adoption timelines unverified). (This also
connects CP to the DDS wire family ROS 2 and AUTOSAR Adaptive already share.)

**Removed specifications in R25-11 (§2.2.4, high confidence).** Set to status "removed":
**CP SWS/RS FlashDriver (Fls)**, **CP SWS/RS EEPROMDriver (Eep)**, **CP RS+SWS TTCAN Driver
& Interface**, **CP SWS LargeDataCOM (LdCom)**, plus template/RS housekeeping docs
(BSWModuleDescriptionTemplate, DiagnosticExtractTemplate, ECUConfiguration,
ECUResourceTemplate, SoftwareComponentTemplate, SystemTemplate, Features, TR
FrancaIntegration). Two nuances that must accompany this list:

- **LdCom was absorbed, not deleted** — the COMHandler concept "merges LdCom functionality
  into Com."
- **Fls/Eep have successors** — R25-11 still ships "Specification of Memory Access"
  (**MemAcc**) and "Specification of Memory Driver" (**Mem**), the generic pair replacing
  part-specific Fls/Eep. The NvM → MemIf → {Fee | Ea} teaching stack stays valid; only the
  bottom driver layer modernized.

R25-11 also added integration points such as DDS (above), vehicle data ("VDP"), and Mirror.
So per-project the target release and ARXML/tool versions must be pinned; requirement IDs
cited from R22-11/R23-11/R24-11 SWS PDFs should be re-diffed against R25-11 before shipping
(the R25-11 SWS PDFs were not all fetchable in-sandbox).

---

## Key claims

| # | Claim | Source URL | Confidence |
|---|---|---|---|
| 1 | Latest CP release is R25-11; Release Event 4 Dec 2025 | https://www.autosar.org/news-events/release-event | high |
| 2 | CP = 3 layers (App / RTE / BSW); BSW split into Services / ECU Abstraction / MCAL | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf | high |
| 3 | CDD is a vertical module that may bypass layering for non-standard / extreme-timing functions | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf | high |
| 4 | RTE has contract phase (app header) + generation phase (source); SWCs call Rte_Write/Rte_Read/Rte_Call | https://mxhelp.danlawinc.com/autosar_reference.htm | high |
| 5 | VFB strictly separates apps from infrastructure, spans ECUs; SWC relocates without code change | https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf | high |
| 6 | Runnable = a C function triggered by RTE Events | https://embetronicx.com/tutorials/automotive/autosar/run-time-environment-rte-layer-autosar/ | high |
| 7 | AUTOSAR OS = OSEK OS superset; SC1 schedule tables, SC2 timing, SC3 memory, SC4 both | https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf | med (structure high, wording med) |
| 8 | Multicore + spinlock + IOC added in AUTOSAR 4.0 | https://scispace.com/pdf/technology-autosar-multicore-operating-system-implementation-1pl2ihoecs.pdf | high |
| 9 | BSW C must be MISRA C: 4.2→C:2004, 4.3+→C:2012; AUTOSAR C++14 merged into MISRA C++:2023 | https://www.perforce.com/blog/qac/misra-and-autosar-unite-cpp-coding-guidelines-what-means | high |
| 10 | Methodology: System Config → ECU Extract → ECU Config (ECUC) → generate; ARXML throughout | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf | high |
| 11 | MCAL is MCU-specific, supplied per silicon vendor; DaVinci Configurator = central BSW+RTE gen tool | https://www.vector.com/us/en/products/products-a-z/software/davinci-configurator-classic/ | high |
| 12 | CP is fully static: no malloc, tasks fixed at build, single binary | https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf | high |
| 13 | TX chain: COM packs signal→I-PDU, PduR routes, CanTp segments, CanIf→CAN driver | https://mohamedayman23.medium.com/inside-the-autosar-can-communication-stack-a-layered-architecture-explained-8e92e0f265f9 | high (secondary, matches SWS) |
| 14 | Comm matrix imported as ARXML/FIBEX/DBC/LDF and code-generated; frozen at build time | https://eeacom-docs.intrepidcs.com/intro/ | high |
| 15 | CP SOME/IP = SomeIpXf + SoAd + SD; static services, dynamic subscription only | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf | high |
| 16 | E2E fault model + CRC widths (P1/2/11/22=8b, P5/6=16b, P4=32b, P7=64b); protection is end-to-end through gateways | https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf | high (primary) |
| 17 | SecOC = authenticity + freshness (CMAC/AES-128, NIST SP 800-38B), truncated MAC; NO confidentiality | https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf | high (no-confidentiality = med, inferred) |
| 18 | NM coordinates synchronized wake/sleep; PN lets a subset sleep via PNC bits | https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf | high (primary) |
| 19 | CAN FD mainstream, FlexRay declining (still specified), Ethernet/TSN the growth path | https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/ | med (industry press) |
| 20 | DEM owns/updates the UDS DTC status byte ("as defined in ISO 14229-1, based on DTC level"); DCM computes nothing | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf | high (primary) |
| 21 | DEM debounces (counter/time/monitor-internal); is a client of NvM (NvM_WriteBlock) | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf | high (primary) |
| 22 | FiM inhibits monitors on DEM event-status change (prevents cascade/false DTCs) | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf | high (primary) |
| 23 | DCM 0x22: checks DID exists + session + security before reading; binds DID to S-R port or read callout | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf | high (primary) |
| 24 | Memory stack NvM → MemIf → {Fee→Fls} or {Ea→Eep}; Fee = standardized flash-EEPROM wear-leveling; NvM_WriteAll invoked by EcuM on shutdown | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf | high (primary) |
| 25 | EcuM owns startup/shutdown/sleep (hands off after StartOS); BswM runs steady-state mode arbitration | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf | high (primary) |
| 26 | DCM supports OBD $01–$0A (J1979/ISO 15031-5); OBD statutory only for emissions ECUs, UDS contractual | https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf | high (primary) |
| 27 | WdgM does Alive + Deadline + Logical Supervision; triggers HW watchdog only while correct | https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf | high (primary) |
| 28 | StbM: Global Time Master → Time Slaves; bus-agnostic; Domains 16–31 are Offset Time Bases | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf | high (primary) |
| 29 | Memory Partitioning = FFI via one OS-Application per partition, MPU-enforced; can't separate Runnables in one SW-C | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf | high (primary) |
| 30 | Timing Protection = Execution/Lock/Inter-Arrival budgets; OS does NOT do deadline supervision (that is WdgM); needs HW support | https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf | high (primary) |
| 31 | Vector MICROSAR Classic Safe: first AUTOSAR impl ISO 26262 ASIL-D certified (2016), exida recert incl. multicore FFI + execution-time bounds | https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/ | high (vendor/primary) |
| 32 | Orin safety MCU = Infineon AURIX TC397X + Vector firmware; Thor companion MCU = Renesas RH850U2A16 + MICROSAR Classic (NOT AURIX) | https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html | high |
| 33 | R25-11 adds DDS Transformer on CP (new BSW module, SPDP/SEDP discovery); no shipping vendor impl yet | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high (adoption unverified) |
| 34 | R25-11 removed Fls, Eep, TTCAN, LdCom; LdCom absorbed into Com; Fls/Eep succeeded by Mem/MemAcc | https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf | high |

## Sources

1. https://www.autosar.org/news-events/release-event — AUTOSAR Release Event R25-11 — AUTOSAR — primary
2. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_TR_ReleaseOverview.pdf — CP Release Overview (R25-11) — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/CP/AUTOSAR_CP_EXP_LayeredSoftwareArchitecture.pdf — Layered Software Architecture (CP R25-11) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/standards/R20-11/CP/AUTOSAR_EXP_VFB.pdf — Explanation of the Virtual Functional Bus — AUTOSAR — primary
6. https://hpi.de/fileadmin/user_upload/fachgebiete/giese/Ausarbeitungen_AUTOSAR0809/NicoNaumann_RTE_VFB.pdf — RTE and Virtual Function Bus (Naumann, HPI) — Hasso Plattner Institut — secondary/academic
7. https://embetronicx.com/tutorials/automotive/autosar/run-time-environment-rte-layer-autosar/ — RTE Layer tutorial — Embetronicx — secondary
8. https://mxhelp.danlawinc.com/autosar_reference.htm — AUTOSAR Reference (RTE APIs) — Danlaw — vendor
9. https://cdn.vector.com/cms/content/know-how/_technical-articles/AUTOSAR/AUTOSAR_Task_Scheduling_VU_201507_PressArticle_EN.pdf — High-Rate Task Scheduling within AUTOSAR — Vector — vendor
10. https://www.osek-vdx.org/mirror/os223.pdf — OSEK/VDX OS Specification 2.2.3 — OSEK/VDX — primary
11. https://scispace.com/pdf/technology-autosar-multicore-operating-system-implementation-1pl2ihoecs.pdf — AUTOSAR Multicore OS Implementation (MPC5668G) — secondary/academic
12. https://www.perforce.com/blog/qac/misra-and-autosar-unite-cpp-coding-guidelines-what-means — MISRA + AUTOSAR unification — Perforce — vendor/secondary
13. https://www.vtronics.in/2019/09/autosar-for-dummies-part-4-autosar.html — AUTOSAR Methodology: system & ECU extract — Vtronics — secondary
14. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_TR_Methodology.pdf — Methodology for Classic Platform — AUTOSAR — primary
15. https://www.vector.com/us/en/products/products-a-z/software/davinci-configurator-classic/ — DaVinci Configurator (Classic) — Vector — vendor
16. https://www.embitel.com/blog/embedded-blog/what-is-autosar-mcal-software-architecture — What is AUTOSAR MCAL — Embitel — secondary
17. https://mohamedayman23.medium.com/inside-the-autosar-can-communication-stack-a-layered-architecture-explained-8e92e0f265f9 — Inside the AUTOSAR CAN Communication Stack — Medium — secondary
18. https://eeacom-docs.intrepidcs.com/intro/ — EEA COM Expert / ARXML tooling — Intrepid Control Systems — vendor
19. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_ServiceDiscovery.pdf — Specification of Service Discovery (R22-11) — AUTOSAR — primary
20. https://www.autosartoday.com/posts/someipxf_overview_-_messages_and_vfb_serialization_in_autosar — SomeIpXf Overview — AutosarToday — secondary
21. https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_E2EProtocol.pdf — E2E Protocol Specification (FO 1.5.1) — AUTOSAR — primary
22. https://www.autosar.org/fileadmin/standards/R24-11/FO/AUTOSAR_FO_PRS_SecOcProtocol.pdf — SecOC Protocol Specification (R24-11) — AUTOSAR — primary
23. https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_PRS_NetworkManagementProtocol.pdf — NM Protocol Specification (R22-11) — AUTOSAR — primary
24. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NetworkManagementInterface.pdf — Specification of NM Interface (R22-11) — AUTOSAR — primary
25. https://www.eenewseurope.com/en/infineon-can-fd-success-goes-at-the-expense-of-flexray/ — CAN FD success at expense of FlexRay — eeNews Europe — secondary
26. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf — Specification of Diagnostic Event Manager (CP R24-11) — AUTOSAR — primary
27. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf — Specification of Diagnostic Communication Manager (CP R24-11) — AUTOSAR — primary
28. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf — Specification of NVRAM Manager (CP R22-11) — AUTOSAR — primary
29. https://rtahotline.etas.com/confluence/display/RH/An+Introduction+to+the+AUTOSAR+Memory+Stack — Intro to the AUTOSAR Memory Stack — ETAS/RTA — vendor
30. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf — Guide to Mode Management (CP R22-11) — AUTOSAR — primary
31. https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf — Specification of Watchdog Manager (CP R23-11) — AUTOSAR — primary
32. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf — Specification of Synchronized Time-Base Manager (CP R22-11) — AUTOSAR — primary
33. https://uds.readthedocs.io/en/latest/pages/knowledge_base/dtc.html — DTC / UDS knowledge base — py-uds docs — secondary
34. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf — Overview of Functional Safety Measures (CP R22-11, Doc ID 664) — AUTOSAR — primary
35. https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf — Explanation of Adaptive and Classic Platform Software Architectural Decisions (FO R25-11, Doc ID 1078) — AUTOSAR — primary
36. https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/ — MICROSAR Classic Safe ASIL-D recert (exida) — Vector — vendor/primary
37. https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html — DRIVE safety MCU (AURIX) setup — NVIDIA — vendor/primary
38. https://www.btc-embedded.com/autosar-classic-vs-adaptive/ — Classic vs Adaptive, RTE hard-wired communication — BTC — vendor/secondary

## Open questions

- **Exact R25-11 wording of the MCAL/ECU-Abstraction/Services/CDD definitions** and any
  scalability-class renumbering: the autosar.org PDFs fail TLS in-sandbox, so §2 definitions
  are reconstructed from search abstracts + secondary sources. *Best guess: R25-11 wording
  is materially unchanged from R22-11; SC1–SC4 stable since 4.x.*
- **Exact SC1–SC4 phrasing from the primary AUTOSAR OS SWS (Doc ID 034).** Structure
  high-confidence (Vector + secondary); exact AUTOSAR phrasing unverified against the SWS.
- **Precise release/year AUTOSAR OS first shipped memory & timing protection** (SC3/SC4).
  Multicore→4.0 is well sourced; the protection-class introduction date is not pinned.
- **Compiler.h / MemMap.h exact obligations** — from general knowledge + the
  SWS_MemoryMapping title; PDF body not readable in-sandbox (medium confidence).
- **Current tool-version compatibility** (DaVinci / EB tresos / ISOLAR vs R25-11 ARXML) —
  some DaVinci material cites "AUTOSAR 4.4-compliant ARXML"; full R25-11 consumption
  unverified.
- **CAN XL AUTOSAR support release.** ISO 11898-1:2024 defines CAN XL; the release that
  first added CanXl driver/CanIf support is unconfirmed against a primary R25-11 doc. *Best
  guess: CP added CanXL handling around R23-11/R24-11 — needs verification.*
- **Exact SecOC "no confidentiality" wording.** The PRS scopes SecOC to authenticity/
  integrity/freshness and lists no encryption mechanism, but no single verbatim sentence
  says "SecOC does not provide confidentiality" (fact is an inference from scope, medium).
- **R25-11 deltas to the communication and services stacks** (COM/PduR/SecOC/E2E/DEM/DCM/
  NvM vs R24-11). R25-11 existence confirmed; per-module requirement-ID diffs not
  enumerated (release-overview / SWS PDFs not all fetchable). *Best guess: no breaking
  changes to the status-byte/debounce or E2E-profile models — stable since R4.x.*
- **Whether P1/P2 remain CP-only in the latest FO E2E spec** — labeled CP-only in R19-03;
  not re-verified against a newer release.
- **J1979-2 / OBDonUDS transport specifics** (modes $01–$0A mapped onto UDS 0x22/0x19 over
  DoIP for modern EV/hybrid emissions ECUs) not verified to primary depth. *Best guess:
  modern emissions ECUs increasingly use OBDonUDS over raw J1979 CAN — unverified.*
- **StbM on-wire binding version** (802.1AS/gPTP profile via EthTSyn in R24/R25-11) not
  fetched to primary depth.
- **Whether R25-11 changed any safety-measure content vs R22-11 Doc 664** — Doc 664's own
  change log shows "No content changes" through R19-11→R22-11; an R25-11 revision was not
  confirmed to exist/differ.
- **Elektrobit (EB tresos Safety OS) and ETAS (RTA-CAR) ASIL-D certification specifics** —
  widely claimed; only Vector verified directly this pass. *Best guess: both hold ISO 26262
  ASIL-D assessments — very likely, needs confirmation.*
- **Whether R25-11 formally moves the ARA C++ baseline from C++14 to C++17** (MISRA C++:2023
  targets C++17) — open per `orchestrator-verification.md`; an Adaptive concern, noted for
  completeness. Keep as an open question.
- **A primary metric for "tooling/licence friction"** (config-parameter count, re-flash
  turnaround) — industry consensus only; left qualitative.

*Fact-checked 2026-07-15 (workflow run wf_4748cedc-22d, 97 claims: 79 correct / 16 partially correct / 2 wrong — all corrected in place; full findings in autosar/research/notes/fact-check-findings-2026-07-15.md).*
