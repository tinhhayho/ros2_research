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

# AUTOSAR in 30 minutes — Classic vs Adaptive: what runs where

## for embedded/firmware engineers · 2026

This is the condensed field guide: **one organization, two platforms, one vehicle**. It is
written for engineers who know MCUs, CAN, an RTOS and bare-metal reflashing. Everything here is
release-stamped to **AUTOSAR R25-11** (published 2025-11-27). External claims are sourced from URLs.
The full deck carries the references.

<div class="gloss">AUTOSAR = AUTomotive Open System ARchitecture · CP = Classic Platform · AP = Adaptive Platform</div>

<!-- ~40s | say: Thirty minutes, one question: which AUTOSAR software runs on which chip. Everything here is stamped to R25-11, published in late November 2025. You already know MCUs, CAN and reflashing, so you have the mental model. We are just naming the automotive version of it. -->

---

## Why AUTOSAR exists — one standard, many competitors

- AUTOSAR is **a worldwide development partnership**. The founding talks happened in **2002**,
  and the Development Agreement was signed in **July 2003**. It has **~360 partners today** across
  the industry. The specs are free to read, but you need a license to build from them.
- **The model in one line** is a founding-era phrase (Heinecke et al., 2006): *cooperate on
  standards, compete on implementation*. There is one shared spec and one XML schema. Many vendors
  sell their own conformant stacks built from it.
- **The business rule that predicts adoption**: AUTOSAR value scales with how many organizational
  boundaries your software crosses. Tier-1 suppliers implement it to win OEM RFQs. A
  vertically-integrated OEM such as **Rivian** skips it and builds its own.

<div class="gloss">Tier-1 = the supplier who builds an ECU for the OEM · OEM = original equipment manufacturer (the vehicle maker) · RFQ = request for quotation · the partnership shares specifications and competes on the implementations built from them</div>

<!-- ~75s | say: AUTOSAR is a partnership, not a product. The talks began in 2002, the agreement came in July 2003, and there are about 360 partners today. Remember the founding-era phrase: cooperate on standards, compete on implementation. One shared spec and schema, many vendors selling conformant stacks. One rule predicts who adopts it. The value scales with how many organizational boundaries your software crosses. Tier-1 suppliers implement it to win OEM contracts. A vertically-integrated maker like Rivian just skips it. -->

---

## One vehicle, two platforms

**CP runs on the deeply-embedded MCUs. AP runs on the high-performance-compute (HPC) SoCs. The two platforms coexist in one 2026 vehicle.**

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform</div>

<!-- ~55s | say: One vehicle, two platforms. Classic runs on the deeply-embedded microcontrollers that handle fast control tasks. Adaptive runs on the high-performance-compute SoCs that do heavy computing. They are not competitors. They coexist in one 2026 car, joined by Ethernet and gateways. -->

---

## Classic in one slide

<style scoped>
  section { font-size: 21px; }
  img { display:block; margin: 4px auto 8px; max-height: 300px; width:auto; }
  li { margin-bottom: 4px; }
</style>

{{diagram:stack-autosar-classic}}

- **Everything is static and decided at build time.** The task set, memory map and communication matrix are frozen in **ARXML**. The tools then generate them into **one ECU binary**.
- **The OS comes from OSEK.** AUTOSAR OS is an OSEK/VDX superset. It is packaged as **Scalability Classes SC1–SC4**, which add timing and memory protection.
- **Classic owns the mature ASIL-D path.** Its determinism comes from making everything static. The first AUTOSAR implementation certified to ISO 26262 up to ASIL D appeared in 2016.

<div class="gloss">OSEK/VDX = the 1990s automotive RTOS standard AUTOSAR OS descends from · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · ECU = Electronic Control Unit</div>

<!-- ~70s | say: Classic in one slide. Everything is static and decided at build time. The task set, memory map and communication matrix are all frozen in ARXML, then generated into one ECU binary. The OS comes from OSEK heritage. It is packaged as scalability classes SC1 through SC4, which add timing and memory protection. Classic also owns the mature ASIL-D path. The first AUTOSAR implementation certified to ISO 26262 up to ASIL D appeared in 2016. -->

---

## The relocation trick — why an SWC relocates across ECUs without a code change

<style scoped>
  img { display:block; margin: 4px auto 6px; max-height: 360px; width:auto; }
</style>

{{diagram:vfb-relocation-annotated}}

SWCs talk **only** over the **Virtual Functional Bus**. They use `Rte_Write`, `Rte_Read` and `Rte_Call`, and never call a bus or a driver directly. The **RTE is generated per deployment**. It decides whether the peer is a local buffer copy or a remote COM message. So **relocating the SWC changes only what the generator emits.**

<div class="figsrc">Redrawn and annotated after AUTOSAR CP_TR_VFB, R25-11, Fig. 2.2 — original unmodified figure in the full deck and autosar/specs/.</div>

<div class="gloss">SWC = Software Component · ECU = Electronic Control Unit · COM = the AUTOSAR signal-packing communication module (not a serial port)</div>

<!-- ~75s | say: Here is the one genuinely new idea for a firmware engineer: relocation. Software components never call each other. They talk over the Virtual Functional Bus using Rte_Write, Read and Call. They never name a bus or a driver. The RTE is generated per deployment. It decides whether the peer is a local buffer copy or a remote message on CAN or Ethernet. So moving a component to a different ECU changes only what the generator emits. There is no code change. Bare-metal has no equivalent to this. -->

---

## CP comms + diagnostics in 60 seconds

- **Communication uses a frozen communication matrix (K-matrix).** It is signal-oriented, **not** service-oriented. It fixes every frame, signal, sender and receiver at build time. **COM** packs
  signals into **I-PDUs** and sends them onto CAN, LIN, FlexRay or Ethernet. This is statically generated, so you can prove it at integration time.
- **Diagnostics split into two modules. Get this right.** **DEM computes.** It is the fault-memory database that
  debounces monitor results and maintains the per-DTC **UDS status byte**. **DCM formats.** It is a
  generated **UDS server** that reads DEM and talks to the tester. DCM computes nothing about faults.
- **Reflashing uses the bootloader you already know.** UDS services **0x34, 0x36 and 0x37** (RequestDownload,
  TransferData, RequestTransferExit) flash the **whole ECU** through the bootloader.

<div class="gloss">COM / PduR / CanIf = the build-time-frozen signal-packing / routing / CAN-interface chain · DEM = Diagnostic Event Manager · DCM = Diagnostic Communication Manager · DTC = Diagnostic Trouble Code · UDS = Unified Diagnostic Services (ISO 14229) · CP = Classic Platform · I-PDU = Interaction-layer PDU (the packed frame COM builds from signals) · LIN = Local Interconnect Network · FlexRay = the deterministic high-speed bus (now declining)</div>

<!-- ~75s | say: Classic comms and diagnostics in sixty seconds. Communication is a frozen signal matrix. The K-matrix fixes every frame and signal at build time, and COM packs signals into I-PDUs. Diagnostics split into two modules, and this is the number-one thing people get wrong. DEM computes. It is the fault-memory database that debounces and maintains the UDS status byte. DCM only formats. It is the UDS server that reads DEM and talks to the tester. And reflashing is the bootloader you already know. UDS services 0x34, 0x36 and 0x37 flash the whole ECU. -->

---

## Why Adaptive exists

<style scoped>
  section { font-size: 21px; }
  img { display:block; margin: 4px auto 4px; max-height: 300px; width:auto; }
  li { margin-bottom: 4px; }
</style>

- **CP's strengths turn into limits.** It has a **static communication matrix** with no runtime
  service discovery. It has no dynamic deployment and only limited OTA of function. Its **BSW is
  C-centric and has no heap**. So CP cannot host large, evolving C++ and perception stacks.
- **AUTOSAR's answer is a second platform: a service platform on POSIX.** AP is
  **middleware and services on top of a POSIX OS**. It is **not a new OS**. **Adaptive Applications
  are ordinary POSIX processes**, written in C++ and linked against ARA.

{{diagram:stack-autosar-adaptive}}

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform · BSW = Basic Software (CP's generated C layer, statically built, no heap)</div>

<!-- ~85s | say: Why a second platform. Classic's strengths turn into limits: a static communication matrix with no runtime discovery, no dynamic deployment, and a C-centric stack with no heap. So it cannot host large, evolving C++ and perception code. The answer is Adaptive, a service platform on POSIX. Say it precisely: Adaptive is middleware and services on top of a POSIX OS. It is not a new OS. Adaptive Applications are ordinary POSIX processes, written in C++ and linked against ARA. -->

---

## AP runs only on a POSIX OS — the line that picks your kernel

<style scoped>
  section { font-size: 18px; padding-top: 20px; }
  table { font-size: 12.5px; }
  table td, table th { padding: 3px 8px; vertical-align: top; }
  table td:nth-child(3), table th:nth-child(3) { padding: 0 3px; width: 8px; }
  .gloss { font-size: 12px; margin-top: 8px; }
  h2 { margin-bottom: 8px; }
  p { margin: 6px 0; }
</style>

The spec makes this a hard requirement. Adaptive Applications program against **POSIX PSE51 plus the C++ Standard Library** (AP_SWS_OperatingSystemInterface, Doc 719, **[RS_OSI_00100] "POSIX PSE51 Compliance"**; PSE51 per IEEE 1003.13, following POSIX-1003.1-2003). The platform underneath also needs an **MMU multi-process OS**. **[SWS_OSI_01010] "Virtual Memory"** requires every Process to run in its own virtualized address space. Execution Management spawns *processes* per manifest.

| Can host AP | POSIX story | | Cannot host AP | why not |
|---|---|---|---|---|
| **QNX Neutrino** | Full POSIX. **PSE52-certified in the 2008 era**, advertised today as conformance. It is **the production default**. ASIL-D comes via QNX OS for Safety. | | **FreeRTOS** (+Labs POSIX) | Partial pthread subset. Its own README says a POSIX app *"cannot be ported... using only this wrapper"*. No processes. |
| **Linux / AGL** | POSIX-conformant, but not formally certified. Used for dev and QM builds. | | **SAFERTOS** | **No POSIX at all.** It ships an OSEK layer instead. Single static image. |
| **Green Hills INTEGRITY** | POSIX API on an MMU separation kernel | | **Zephyr** | POSIX subset layer, single-image kernel, no MMU processes |
| **PikeOS** | POSIX personality on a separation microkernel | | **NuttX** | The most POSIX-faithful MCU RTOS. An optional MMU "kernel build" exists, but it has no fork/exec. Still MCU-class. |
| **VxWorks** | POSIX plus user-mode processes (RTPs). Capable, but rare in AP practice. | | **AUTOSAR OS (OSEK)** | No POSIX by design. That is CP's OS. |

**The test is one question: does the OS speak PSE51 *and* run MMU-isolated processes?** If both are yes, the OS is AP-capable. Anything with a task model belongs to CP or bare-metal.

<div class="gloss">AP = Adaptive Platform · CP = Classic Platform · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · AGL = Automotive Grade Linux · PSE51/PSE52 = IEEE 1003.13 realtime profiles · MMU = per-process virtual address spaces (vs MPU region protection) · RTP = VxWorks Real-Time Process · left-column rows beyond QNX/Linux are capability-class statements, not AP-product endorsements · trivia: the Open Group live PSE52 register today lists VxWorks 7 + two Chinese automotive OSes — QNX's formal certificate was 2008-era</div>

<!-- ~70s | say: Here is the hard architectural line. The spec requires POSIX PSE51 plus the C++ standard library for apps. The platform also needs an MMU multi-process OS. This is the spec's virtual-memory requirement, SWS OSI 01010, because Execution Management spawns processes. It sorts every kernel into two groups. QNX and Linux are the production pair: QNX carries the ASIL-D certification, and Linux carries development. INTEGRITY, PikeOS and VxWorks are capable-class. Everything with a task model stays on the MCU side with Classic: FreeRTOS, SAFERTOS, Zephyr, NuttX and OSEK. -->

---

## The function clusters — straight from the spec

{{image:spec-ap-architecture-logical-view}}

**Read this as a map, not a checklist.** R25-11 defines **20 function clusters**. Four of them carry the rest of this talk: **Communication Mgmt (`ara::com`)**, **Execution Mgmt (`ara::exec`)**, **Diagnostic Mgmt (`ara::diag`)** and **Update & Config Mgmt (`ara::ucm`)**.

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1 — © AUTOSAR.</div>

<div class="gloss">FC = Function Cluster · ara:: = the C++ namespace prefix under ARA (AUTOSAR Runtime for Adaptive Applications) each cluster's API lives in · PSE51 = IEEE 1003.13 minimal single-process POSIX profile · STL = C++ Standard Template Library · the other ~16 clusters shown are out of scope for this talk</div>

<!-- ~70s | say: This is the platform straight from the spec, an unmodified figure. Do not read all twenty clusters. Point at four: ara::com for communication, ara::exec for execution management, ara::diag for diagnostics, and ara::ucm for updates. Those four carry the story. -->

---

## `ara::com` — one API, swappable bindings

<style scoped>
  img { display:block; margin: 4px auto 6px; max-height: 350px; width:auto; }
</style>

{{diagram:aracom-bindings-annotated}}

There is one protocol-agnostic API, based on a **proxy/skeleton** model. The **integrator picks the wire binding in the manifest**. The three **standardized** bindings are **SOME/IP, Signal-Based and DDS** (DDS has been present since **R18-03**). **Local IPC is the reality inside one machine.** It is implementation-level, not a standardized inter-vendor protocol.

<div class="figsrc">Redrawn and annotated after AUTOSAR AP_SWS_CommunicationManagement, R25-11, Fig. 7.1 — original unmodified figure in the full deck and autosar/specs/.</div>

<div class="gloss">rmw = ROS 2's middleware-abstraction layer</div>

<!-- ~80s | say: ara::com is one protocol-agnostic API on a proxy/skeleton model. The app codes against it, and the integrator picks the wire binding in the manifest. There are three standardized bindings: SOME/IP, Signal-Based and DDS. DDS has been present since R18-03. Local IPC is the reality inside one machine, but it is implementation-level, not a standardized inter-vendor protocol. The transferable idea: the API is protocol-agnostic and the binding is swappable underneath, exactly like ROS 2's rmw over DDS. -->

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
├── system/Os/rtos/          OSEK/AUTOSAR OS kernel
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
├── boards/<~40 targets>     MPC5xxx, TC2xx/3xx, S32K, RH850, gnulinux
└── makefile, scripts/       recursive make build (no examples/ dir here)
```

<p class="pin">openAUTOSAR/classic-platform @ 09433770 · GPL-2.0</p>
<p class="quote">"This is a fork of the Arctic Core (the open source AUTOSAR embedded platform)." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p>The top-level <code>makefile</code> is the build entry. It is a recursive GNU make build where you pick a target board with <code>BOARDDIR</code> and the module directories to compile with <code>BDIR</code>. The OS kernel is always built. <code>system/Os/rtos/inc/Os.h</code> is the public header for the OSEK/AUTOSAR OS kernel, and it declares the task, alarm, counter and event API. <code>communication/Com/src/Com_Com.c</code> is the COM signal input and output, where <code>Com_SendSignal</code> and <code>Com_ReceiveSignal</code> pack and unpack signals into an I-PDU. <code>diagnostic/Dcm/src/Dcm.c</code> is the UDS server and <code>diagnostic/Dem/src/Dem.c</code> is the fault and DTC store.</p>
<h3>What you can do</h3>
<p>Cross-compile for a board with <code>make BOARDDIR=&lt;board&gt; BDIR=&lt;dir&gt; CROSS_COMPILE=&lt;gcc&gt; all</code>. This builds the OS kernel, which is always built, plus the module directories you select, for one of about 40 boards. <code>scripts/build_example.sh</code> is a thin wrapper around the same build. There is no graphical development environment and no host application to run. The build produces an embedded firmware image for an MCU target. A gnulinux board also exists for host builds.</p>
<h3>Know the limits</h3>
<p>The default branch is dormant. Its last commit on <code>master</code> is from 2020-04-02, with the message "Remove GPLv2 violating files". The repository shows a later push date of 2024-08-06, but that reflects other branches, not <code>master</code>. There is no <code>examples/</code> directory at this commit, so the OSEK example applications the makefile mentions are not present here. This is a continuation of the Arctic Core codebase, a full Classic AUTOSAR basic-software stack in C across about 40 MCU board targets. Read it for the shape of a real Classic stack, not to run it.</p>
</div>
</div>

<div class="gloss">OSEK = the 1990s automotive RTOS standard AUTOSAR OS descends from · AUTOSAR OS = the OSEK-derived static real-time kernel · BSW = Basic Software (CP's generated C layer, built statically, no heap) · COM = the AUTOSAR signal-packing communication module (not a serial port) · PDU = Protocol Data Unit · I-PDU = Interaction-layer PDU (the packed frame COM builds from signals) · PduR = PDU Router (routes PDUs between COM and the bus interfaces) · CanIf = CAN Interface (hardware-independent CAN) · CanTp = CAN Transport Protocol (ISO 15765-2 segmentation) · CAN = Controller Area Network (the automotive serial bus) · HW = hardware · UDS = Unified Diagnostic Services (ISO 14229) · Dcm = Diagnostic Communication Manager (the UDS server) · Dem = Diagnostic Event Manager (the fault store) · DTC = Diagnostic Trouble Code · ECU = Electronic Control Unit · EcuM = ECU Manager · BswM = Basic Software Mode Manager · SchM = BSW Scheduler · MCU = Microcontroller · CP = Classic Platform · GNU make = the GNU project build tool · GPL-2.0 = GNU General Public License version 2 (an open-source licence)</div>

<!-- ~65s | say: This is the Classic Platform repository, the one open and complete Classic AUTOSAR stack worth reading. Start at the top makefile. It is a recursive GNU make build. You pick a target board and the module directories to compile, and the OS kernel is always built. Then open Os dot h. It is the public header for the OSEK-derived kernel, and it declares the task, alarm, counter and event calls. Com underscore Com dot c is the communication module, where Com send signal packs an application signal into an I-PDU. The diagnostic folder holds Dcm, the UDS server, and Dem, the fault store. To build it, you cross-compile for one of about forty-five boards. There is no host application to run, because the build produces firmware for a microcontroller. Two honest limits. The main branch has been dormant since 2020, and the example applications the makefile mentions are not in the tree. Read it for the shape. -->

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

<div class="gloss"><b>What to notice:</b> <code>Com_SendSignal</code> is the COM service a task calls to publish an application signal, later packed into an I-PDU on the bus. Before it does any work it checks the module state. If COM is not initialized, it reports a development-time error through the DET and returns a service-not-available code. The <code>/* @req COM334 */</code> comment ties this line to a numbered requirement in the AUTOSAR COM specification, and that traceability tag is the signature style of the whole codebase. <code>Dem_ReportErrorStatus</code> is the entry any basic-software module calls to report a fault as passed or failed by numeric event id. The two <code>VALIDATE_NO_RV</code> macros are the standard guard: they reject calls made before init or with an out-of-range status by reporting to the DET. <code>SchM_Enter_Dem_EA_0()</code> then opens a named exclusive area, so the fault-status update that follows is atomic against task preemption on the ECU. Both patterns, the requirement tags and the init-and-exclusive-area guards, are the OSEK-heritage Classic idiom. · COM = the AUTOSAR signal-packing communication module (not a serial port) · DET = Default Error Tracer (AUTOSAR's development-time error hook) · PDU = Protocol Data Unit · I-PDU = Interaction-layer PDU (the packed frame COM builds from signals) · DEM = Diagnostic Event Manager · BSW = Basic Software (CP's generated C layer) · SchM = BSW Scheduler; the <code>SchM_Enter</code>/<code>SchM_Exit</code> pair brackets an exclusive area (EA), an atomic section against preemption · OSEK = the 1990s automotive RTOS standard AUTOSAR OS descends from · id = identifier · ECU = Electronic Control Unit</div>

<!-- ~65s | say: These are two real functions from the Classic stack, and they show the house style. The first is Com send signal, the service a task calls to publish an application signal. Before it does any work, it checks that the module was initialized. If it was not, it reports a development-time error through the Default Error Tracer and returns a service-not-available code. The comment tagged requirement COM three three four links that line to a numbered requirement in the AUTOSAR COM specification. The second function is Dem report error status. Any basic-software module calls it to report a fault as passed or failed, using a numeric event id. The two validate macros are the standard guard. They reject calls made before init or with a bad status. Then SchM enter opens a named exclusive area, so the fault update that follows cannot be interrupted by another task. Requirement tags and state guards on every entry point are the OSEK-heritage Classic idiom. -->

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

<div class="gloss"><b>What to notice:</b> <code>RpcClient</code> is the abstract SOME/IP request-and-response client that the platform's wiring is built on. Its public <code>HandlerType</code> is just a <code>std::function</code> taking a decoded message. Its private state is two maps keyed by a packed service and method id, one tracking per-method session ids and one holding the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass such as <code>SocketRpcClient</code> supplies the actual send. In the second snippet a concrete <code>SocketRpcServer</code> is built from the parsed RPC configuration (address, port, protocol version) and handed by pointer into an <code>ara::exec::ExecutionServer</code>, so the execution server speaks to clients only through the SOME/IP RPC abstraction. The last lines load the function-group states and their initial state from the ARXML model, which is the config-driven, model-first style of the codebase. · SOME/IP = Scalable service-Oriented MiddlewarE over IP · RPC = Remote Procedure Call · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · <code>ara::exec</code> = AP's Execution Management API · ARXML = the AUTOSAR XML manifest and config format · id = identifier · AP = Adaptive Platform</div>

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

## The shape of the code — real ara:: from public repos

<style scoped>
  section { font-size: 18px; padding-top: 20px; }
  pre { font-size: 13px; line-height: 1.25; margin: 6px 0; }
  pre code { font-size: 13px; }
  h2 { margin-bottom: 6px; }
  p { margin: 5px 0; }
  .spec { font-size: 13px; background:#eef2f8; padding:6px 10px; border-radius:6px; margin: 4px 0 10px 0; }
  .cite { color:#66708a; font-size:12px; }
  .attr { font-size: 12px; color:#66708a; margin: 3px 0 10px 0; }
  .gloss { font-size: 12.5px; margin-top: 10px; }
</style>

<p class="spec"><b>The standardized surface.</b> The spec names the <code>ara::com</code> event-send API: <code>Send({&lt;s-sample-derived-type&gt;})</code> and <code>Send(ara::com::SampleAllocateePtr&lt;SampleType&gt;)</code>.<br><span class="cite">AP_SWS_CommunicationManagement, R25-11, sec. 8.4.2.2.2</span></p>

**C++: the state handshake from the AA to Execution Management** (`langroodi/Adaptive-AUTOSAR`, dormant since 2023-06-22):

```cpp
            /// @brief Report the application internal state to Execution Management
            /// @param state Application current internal state
            /// @returns Void Result if the state reporting was successful, otherwise a Result containing the occurred error
            ara::core::Result<void> ReportExecutionState(
                ExecutionState state) const;
```
<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L54-L58">langroodi/Adaptive-AUTOSAR @ 866d158 — src/ara/exec/execution_client.h</a></p>

<div class="gloss">What to notice: <code>ReportExecutionState</code> returns an <b><code>ara::core::Result&lt;void&gt;</code></b> — AP signals errors as a <i>returned value</i>, <b>not a thrown exception</b>; it is the <b>contract every AA implements</b> so EM knows it reached <code>kRunning</code>. The spec box above names the matching <code>ara::com</code> event API — <code>Send(…)</code> — and the skeleton's offer lifecycle is likewise spec-named: <b><code>OfferService()</code> / <code>StopOfferService()</code> on the <code>ServiceSkeleton</code> class</b> ([SWS_CM_00101] / [SWS_CM_00111], same document). Educational caveat: this C++ repo is <b>dormant since 2023-06-22 (inactive for 3 years)</b> — read it for the shape, not for production. AA = Adaptive Application · EM = Execution Management.</div>

<!-- ~58s | say: This is the shape of real ara-colon-colon code from a public repo. Start with the standardized surface. The spec names the ara::com event-send API: Send of a sample type, and Send of a SampleAllocateePtr. That is the contract vendors implement. Now look at the code. ReportExecutionState returns an ara::core::Result, not a thrown exception. Adaptive signals errors as a returned value. It is the contract every Adaptive Application implements, so Execution Management knows it reached running. On the ara::com side, the skeleton lifecycle is spec-named too: OfferService and StopOfferService on the ServiceSkeleton class. But read this for the shape, not for production. The repo is educational and has been dormant since June 2023. -->

---

## CP vs AP — the split that matters

<style scoped>
  section { font-size: 20px; padding-top: 30px; }
  table { font-size: 15px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 12.5px; margin-top: 6px; }
  h2 { margin-bottom: 6px; }
</style>

| | **Classic Platform (CP)** | **Adaptive Platform (AP)** |
|---|---|---|
| **Target** | deeply-embedded MCUs: Infineon AURIX · NXP S32K · Renesas RH850 | HPC SoCs: NVIDIA Orin/Thor · Qualcomm · NXP S32G · Renesas R-Car |
| **OS** | AUTOSAR OS, an OSEK superset (SC1–SC4, no MMU) | **not a new OS**: an OS Interface on POSIX **PSE51** over Linux/QNX/PikeOS |
| **Model** | fully **static**: C, RTE-generated `Rte_Read/Write/Call`, one binary | **dynamic**: C++14, `ara::*`, manifests bound late, discovery and start/stop at runtime |
| **Comms** | **signal**-oriented: COM packs signals into I-PDUs on CAN/LIN/FlexRay/Ethernet | **service**-oriented: `ara::com` proxy/skeleton over **SOME/IP or DDS** |
| **Diagnostics** | **DCM + DEM**: UDS over DoCAN/DoIP | **DM** (`ara::diag`): UDS server *and* SOVD. **DoIP the only standardized transport** (custom permitted) |
| **Updates** | reflash the **whole ECU** via bootloader/UDS (0x34/0x36/0x37) | **UCM**: install or update individual **Software Clusters**, OTA-native |
| **Safety** | mature ISO 26262 **up to ASIL D** (first ASIL-D AUTOSAR impl certified **2016**) | "up to ASIL D" on paper, harder in practice. **ASIL-B shipping, ASIL-D underway** |

<div class="gloss">CP is <b>not CAN-only</b> — a standardized SOME/IP Transformer has shipped since <b>4.2.1 (Oct 2014)</b>, years before AP's first release · MMU = Memory Management Unit · PSE51 = minimal single-process POSIX profile · SOVD = Service-Oriented Vehicle Diagnostics · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · DCM = Diagnostic Communication Manager · DEM = Diagnostic Event Manager · DM = AP's Diagnostic Manager (`ara::diag`) · DoCAN = Diagnostics over CAN (ISO 15765-2) · DoIP = Diagnostics over IP (ISO 13400) · the ASIL hedge, exactly: no fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026 — ASIL-D lives in the OS (QNX) + hypervisor + vendor safety case, and a "developed to ASIL-x" process claim ≠ a "certified at ASIL-x" claim</div>

<!-- ~75s | say: The split that matters has seven rows. Target: MCUs versus HPC SoCs. OS: AUTOSAR OS versus POSIX PSE51, and Adaptive is not a new OS. Model: fully static C versus dynamic C++. Comms: signals versus services. Diagnostics: DCM-plus-DEM versus one DM cluster. Note that DoIP is the only standardized transport, though a custom one is permitted. Updates: whole-ECU reflash versus per-cluster UCM. Safety: Classic is mature up to ASIL D since 2016, and Adaptive is ASIL-B shipping with ASIL-D underway. And Classic is not CAN-only. It has had a SOME/IP transformer since 4.2.1, in October 2014. -->

---

## Coexistence — AP plans, CP keeps the wheels

<style scoped>
  section { font-size: 15.5px; padding: 26px 46px 20px; }
  h2 { margin: 0 0 10px; font-size: 25px; }
  .cx { display: flex; gap: 24px; align-items: flex-start; }
  .cx-fig { flex: 0 0 58%; }
  .cx-fig img { display: block; width: 100%; max-width: 690px; max-height: 440px; height: auto; margin: 0; }
  .cx-fig .figsrc { font-size: 12px; color: #6b7280; text-align: left; margin: 6px 0 0; }
  .cx-txt { flex: 1 1 42%; }
  .cx-txt ol { margin: 2px 0 0; padding-left: 22px; }
  .cx-txt li { margin-bottom: 13px; line-height: 1.36; }
  .tagA { color: #2E5FAC; font-weight: 700; }
  .tagC { color: #12977e; font-weight: 700; }
  .take { margin: 14px 0 0; font-size: 16px; line-height: 1.35; }
  .gloss { font-size: 12px; margin-top: 12px; }
</style>

<div class="cx"><div class="cx-fig">

{{image:spec-ap-cp-interactions}}

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 3.2 — © AUTOSAR.</div>
</div>
<div class="cx-txt">
<ol>
<li><span class="tagA">Region A</span> (blue tag) <b>is the Adaptive Platform on the HPC.</b> This is the high-level compute side. It perceives the environment, driver and vehicle state. It fuses them into one <b>environment and state model</b>. Then it runs <b>maneuver and trajectory planning</b>.</li>
<li><span class="tagC">Region C</span> (teal tag) <b>is the Classic Platform side.</b> This is the fast control side. It groups the <b>sensor-input boxes</b> (camera/radar/lidar, inertial/odometry/GPS, C2C/C2I) and the bottom <b>trajectory-control and safety-function</b> box.</li>
<li><b>Some arrows run straight down</b> from the sensor boxes into the <b>safety function</b>, and they <b>bypass Region A</b>. The safety side keeps its <b>own sensor feed</b>. So the safe path does not depend on the planning path. If the HPC fails, the wheels stay safe.</li>
</ol>
</div>
</div>

<p class="take"><b>A modern software-defined vehicle (SDV) runs both platforms at once</b>, joined by <b>Ethernet and gateways</b>. The spec is explicit: AP <b>"will not replace CP"</b>. The two "interact … to form an integrated system" (AP_EXP_PlatformDesign §3.4).</p>

<div class="gloss">SDV = Software-Defined Vehicle · AP = Adaptive Platform · CP = Classic Platform · HPC = High-Performance Computer (the central compute SoC) · ECU = Electronic Control Unit · MCU = Microcontroller — CP's deeply-embedded silicon · C2C / C2I = car-to-car / car-to-infrastructure communication · GPS = Global Positioning System · OEM = original equipment manufacturer (the vehicle maker) · trajectory = the planned path the vehicle is to follow · safety function = the monitor that keeps actuation safe even if the planner fails</div>

<!-- ~75s | say: Coexistence, straight from the spec: one figure, two platforms. Region A, with the blue tag, is the Adaptive Platform on the high-performance computer. This is the high-level compute side. It perceives the environment, driver and vehicle state. It fuses them into one environment and state model. Then it plans the maneuver and the trajectory. Region C, the boxes on the left and along the bottom with the teal tag, is the Classic Platform side. This is the fast control side. It holds the sensor boxes: camera, radar, lidar, inertial, odometry, GPS, car-to-car and car-to-infrastructure. It also holds the trajectory-control box with its safety function. Now the point that matters. Watch the arrows from the sensors. Some feed perception up in Region A. But others run straight down into the safety function, and they bypass Region A entirely. So the safe path does not depend on the planning path. If the HPC goes down, the wheels stay safe. And the spec says it plainly: AP will not replace CP. The two interact to form an integrated system. Coexistence is the designed architecture, not legacy. -->

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

This is the whole deck in one procurement table. It shows what runs where, and who sells it:

| Silicon | What runs there | Who supplies it (examples) |
|---|---|---|
| **A-core SoC**: DRIVE Orin/Thor guest · NXP S32G/S32N · R-Car | **QNX or Linux plus an AP stack.** Or a non-AUTOSAR middleware (the Rivian path) | AP: **Vector · Elektrobit (corbos) · ETAS RTA-VRTE · Qorix**. The OS underneath is a separate procurement. |
| **Safety island on the SoC**: lockstep Cortex-R52 (Thor FSI) | vendor safety firmware, plus a Vector **FSI reference integration** (Thor) | NVIDIA FSI firmware · Vector. Its explicit **MICROSAR Classic** up-to-ASIL-D reference targets the **companion MCU**. |
| **Companion / safety MCU**: RH850 (Thor gen) · AURIX (Orin gen) | **CP** | Vector AFW, the NVIDIA reference integration |
| **Zonal / domain MCUs**: NXP S32Z/E · AURIX · RH850 | **CP** | Tier-1 Classic stacks (MICROSAR, EB tresos class) |
| **Small edge ECUs**: S32K class | **CP** or bare-metal/RTOS | Tier-1 stacks or in-house |

**The business rule underneath:** AUTOSAR value scales with how many organizational boundaries your software crosses. Vertically-integrated OEMs such as Rivian skip it. Tier-1s implement it to win OEM RFQs.

<div class="gloss">FSI = Functional Safety Island (dedicated lockstep silicon on DRIVE/IGX Thor) · AFW = the Vector-built AUTOSAR firmware NVIDIA ships for its companion MCUs · RFQ = request for quotation · examples only — the vendor cells repeat facts verified elsewhere, not an exhaustive market list · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · S32Z/E = NXP zonal-controller family (lockstep Cortex-R52) · ECU = Electronic Control Unit</div>

<!-- ~85s | say: This is the whole deck in one procurement table. Find your silicon row. A-core SoC: QNX or Linux plus an AP stack, or a non-AUTOSAR middleware, the Rivian path. The on-SoC safety island is a lockstep Cortex-R52. It runs vendor safety firmware. Vector's explicit MICROSAR Classic up-to-ASIL-D reference targets the companion MCU, not the island. The companion and zonal MCUs run Classic. The rule underneath: value scales with the organizational boundaries your software crosses. Integrated OEMs skip it, and Tier-1s implement it to win RFQs. -->

---

## Fleet and diagnostics in one picture

<style scoped>
  img { display:block; margin: 4px auto 8px; max-height: 330px; width:auto; }
  li { margin-bottom: 4px; }
</style>

{{diagram:fleet-uds-flow}}

- **Outside the car:** the backend speaks **SOVD (REST/JSON over HTTPS)** plus **MQTT telemetry**, and **never raw UDS**. The vehicle's entry point is the **TCU**.
- **Inside the car:** the **central gateway** is a DoIP router and firewall. It routes **DoIP/UDS** on the backbone. It re-transports **DoIP to DoCAN** for the CP branches. **Raw UDS is never exposed to the internet.**

<div class="gloss">DoCAN = Diagnostics over CAN (ISO 15765-2) — the CanTp transport shown in the diagram · SOME/IP = Scalable service-Oriented MiddlewarE over IP</div>

<!-- ~75s | say: Here is fleet and diagnostics in one picture. Outside the car, the backend speaks SOVD, which is REST and JSON over HTTPS, plus MQTT telemetry. It never uses raw UDS. The entry point is the TCU. Inside, the central gateway is a DoIP router plus firewall. It routes DoIP and UDS on the backbone. It re-transports DoIP to DoCAN down to the Classic branches. Raw UDS is never exposed to the internet. -->

---

## Choosing your stack — the decision tree

<style scoped>
  section { font-size: 15px; padding: 20px 40px 16px; }
  h2 { margin: 0 0 6px; }
  img { display: block; margin: 0 auto; max-height: 500px; width: auto; max-width: 100%; }
  p { margin: 5px 0; }
  .gloss { font-size: 11px; margin-top: 5px; }
</style>

{{diagram:stack-decision-tree}}

**Proof the build-your-own outcome works:** [Tesla fleet-telemetry](https://github.com/teslamotors/fleet-telemetry/blob/main/README.md) shows the car as a *client* that pushes protobuf over WebSocket plus mTLS. There is no SOME/IP, DDS or DoIP in the path. And Rivian is on record: ["We don't use any of the industry offerings such as AUTOSAR"](https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/). **Skipping AUTOSAR forfeits the pre-built in-vehicle endpoints, never fleet reachability.**

<div class="gloss">mTLS = mutual TLS (both ends authenticate) · protobuf = Protocol Buffers (Google's binary serialization) · WebSocket = a persistent channel upgraded from HTTP · SOME/IP / DDS = the standardized `ara::com` wire bindings (earlier slides) · every abbreviation inside the tree is expanded in the tree's own footnote lines</div>

<!-- ~95s | say: Two questions pick your stack, and on the MCU side the first fork is safety. Question one: where does the function run? If it is a deeply-embedded MCU, question two is: what safety level must this ECU carry, and who is the customer? If it carries an ASIL and you sell it to an OEM, the choice is made for you. RFQs demand AUTOSAR plus ASIL evidence, so you buy Classic with a pre-certified base such as MICROSAR Safe. If it carries an ASIL but it is your own product, there are two honest options. You can still buy Classic, for the certified base, the vendor drivers and the solved modules. Or you can take a certified non-AUTOSAR RTOS such as SAFERTOS and carry the whole ISO 26262 safety case yourself. That is the Rivian path, and it needs a real safety team. If the ECU is QM, no certificate is needed, so anything goes. On the HPC side the safety story lives in the certified OS, the hypervisor, the safety island and the companion MCU, and that companion MCU runs Classic. So the remaining question is only about supplier interop. Buy an AP stack if you need the standardized endpoints. Otherwise use S-CORE or build your own. The orange bar still holds: every outcome meets the same fleet contracts. -->

---

## Three takeaways

1. **AUTOSAR is a supply-chain standard.** Its value scales with the organizational boundaries
   your software crosses. And **ASIL comes from ISO 26262, not from AUTOSAR.**
2. **Two platforms, coexisting by design.** **CP is static, with a mature ISO 26262 path to ASIL D (first impl certified 2016), and it runs on MCUs.**
   **AP is a service platform on POSIX, and it runs on HPCs.** This is a designed hierarchy, not legacy baggage.
3. **Find your silicon row on the decision map.** Then you know the **stack**, the OS question,
   and **who sells it.**

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · HPC = High-Performance Computer</div>

<!-- ~65s | say: Three takeaways. One: AUTOSAR is a supply-chain standard, and ASIL comes from ISO 26262, not from AUTOSAR. Two: two platforms, coexisting by design. Classic is static and certified on MCUs, and Adaptive is a service platform on HPCs. Three: find your silicon row on the decision map, and you know the stack, the OS question, and who sells it. -->

---

## Q&A — and where to dig deeper

- **The full 73-slide deck** is `autosar/slides/autosar-deck.md`. It expands every point here with the
  primary-source references.
- **The local spec mirror** is `autosar/specs/`. It holds **35 R25-11 PDFs** (FO / CP / AP).
- **The research docs and blog** live under `autosar/` (Classic, Adaptive, Classic-vs-Adaptive).

<div class="gloss">FO = Foundation · CP = Classic Platform · AP = Adaptive Platform · Licensing: spec figures are reproduced <b>unmodified</b> (© AUTOSAR, R25-11); the adapted diagrams are <b>redrawn after the cited figures</b>, not copied from the spec artwork.</div>

<!-- ~35s | say: To go deeper: the full 73-slide deck expands every one of these. The local spec mirror has all 35 R25-11 PDFs. The research docs and blog live under autosar/. On licensing: the spec figures are unmodified and copyright AUTOSAR R25-11. The adapted diagrams are redrawn after the cited figures. Questions? -->
