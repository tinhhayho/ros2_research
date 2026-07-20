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

<style scoped>
  section { font-size: 22px; }
  li { margin-bottom: 6px; }
  .gloss { font-size: 15px; line-height: 1.32; margin-top: 10px; padding-top: 5px; }
</style>

- AUTOSAR is **a worldwide development partnership**. The founding talks happened in **2002**,
  and the Development Agreement was signed in **July 2003**. It has **about 340 partners today**
  (339 at the end of 2025) across the industry. The specs are free to read, but you need a
  license to build from them.
- **The model in one line** is a founding-era phrase (Heinecke et al., 2006): *cooperate on
  standards, compete on implementation*. There is one shared spec and one XML schema. Many vendors
  sell their own conformant stacks built from it.
- **The business rule that predicts adoption**: AUTOSAR value scales with how many organizational
  boundaries your software crosses. Tier-1 suppliers implement it to win OEM RFQs. A
  vertically-integrated OEM such as **Rivian** skips it and builds its own ([Sonatus interview](https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/)).

<div class="gloss">Tier-1 = the supplier who builds an ECU for the OEM · OEM = original equipment manufacturer (the vehicle maker) · RFQ = request for quotation · the partnership shares specifications and competes on the implementations built from them · founding dates: autosar.org · partner count: autosar.org introduction deck, partner status 2026-04-09</div>

<!-- ~75s | say: AUTOSAR is a partnership, not a product. The talks began in 2002, the agreement came in July 2003, and there are about 340 partners today. Remember the founding-era phrase: cooperate on standards, compete on implementation. One shared spec and schema, many vendors selling conformant stacks. One rule predicts who adopts it. The value scales with how many organizational boundaries your software crosses. Tier-1 suppliers implement it to win OEM contracts. A vertically-integrated maker like Rivian just skips it. -->

---

## One vehicle, two platforms

**CP runs on the deeply-embedded MCUs. AP runs on the high-performance-compute (HPC) SoCs. The two platforms coexist in one 2026 vehicle.**

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform</div>

<!-- ~55s | say: One vehicle, two platforms. Classic runs on the deeply-embedded microcontrollers that handle fast control tasks. Adaptive runs on the high-performance-compute SoCs that do heavy computing. They are not competitors. They coexist in one 2026 car, joined by Ethernet and gateways. -->

---

## Classic in one slide

<style scoped>
  section { font-size: 20px; }
  img { display:block; margin: 2px auto 6px; max-height: 248px; width:auto; }
  li { margin-bottom: 3px; }
  .gloss { font-size: 15px; margin-top: 8px; padding-top: 4px; line-height: 1.3; }
</style>

{{diagram:stack-autosar-classic}}

- **Everything is static and decided at build time.** The task set, memory map and communication matrix are frozen in **ARXML**. The tools then generate them into **one ECU binary**.
- **The OS is a static real-time kernel.** AUTOSAR OS fixes its whole task set at build time and uses fixed-priority preemptive scheduling with no heap, much like a statically configured RTOS you already know, but stricter. It is packaged as **Scalability Classes SC1-SC4**, where the higher classes add timing protection and memory protection.
- **Classic owns the mature ASIL-D path.** Its determinism comes from making everything static. The first AUTOSAR implementation certified to ISO 26262 up to ASIL D appeared in 2016.

<div class="gloss">ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · ECU = Electronic Control Unit · first ASIL-D certification = Vector MICROSAR Safe, certified by exida in 2016</div>

<!-- ~70s | say: Classic in one slide. Everything is static and decided at build time. The task set, memory map and communication matrix are all frozen in ARXML, then generated into one ECU binary. The OS is a static real-time kernel. AUTOSAR OS fixes its whole task set at build time and uses fixed-priority preemptive scheduling with no heap, much like a statically configured RTOS you already know, but stricter. It is packaged as scalability classes SC1 through SC4, where the higher classes add timing protection and memory protection. Classic also owns the mature ASIL-D path. The first AUTOSAR implementation certified to ISO 26262 up to ASIL D appeared in 2016. -->

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
| **Linux / AGL** | POSIX-conformant, but not formally certified. Used for dev and QM builds. | | **SAFERTOS** | **No POSIX personality.** It ships as a single static image. |
| **Green Hills INTEGRITY** | POSIX API on an MMU separation kernel | | **Zephyr** | POSIX subset layer, single-image kernel, no MMU processes |
| **PikeOS** | POSIX personality on a separation microkernel | | **NuttX** | The most POSIX-faithful MCU RTOS. An optional MMU "kernel build" exists, but it has no fork/exec. Still MCU-class. |
| **VxWorks** | POSIX plus user-mode processes (RTPs). Capable, but rare in AP practice. | | **AUTOSAR OS (CP's kernel)** | No POSIX by design. That is CP's OS. |

**The test is one question: does the OS speak PSE51 *and* run MMU-isolated processes?** If both are yes, the OS is AP-capable. Anything with a task model belongs to CP or bare-metal.

<div class="gloss">AP = Adaptive Platform · CP = Classic Platform · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · AGL = Automotive Grade Linux · PSE51/PSE52 = IEEE 1003.13 realtime profiles · MMU = per-process virtual address spaces (vs MPU region protection) · RTP = VxWorks Real-Time Process · left-column rows beyond QNX/Linux are capability-class statements, not AP-product endorsements · trivia: the Open Group live PSE52 register today lists VxWorks 7 + two Chinese automotive OSes — QNX's formal certificate was 2008-era</div>

<!-- ~70s | say: Here is the hard architectural line. The spec requires POSIX PSE51 plus the C++ standard library for apps. The platform also needs an MMU multi-process OS. This is the spec's virtual-memory requirement, SWS OSI 01010, because Execution Management spawns processes. It sorts every kernel into two groups. QNX and Linux are the production pair: QNX carries the ASIL-D certification, and Linux carries development. INTEGRITY, PikeOS and VxWorks are capable-class. Everything with a task model stays on the MCU side with Classic: FreeRTOS, SAFERTOS, Zephyr and NuttX. -->

---

## The functional clusters — straight from the spec

<style scoped>
  section { font-size: 20px; }
  img { display:block; margin: 2px auto 4px; max-height: 320px; width:auto; }
  .figsrc { margin: 2px 0 0; }
  .gloss { font-size: 12.5px; line-height: 1.3; margin-top: 6px; padding-top: 4px; }
</style>

{{image:spec-ap-architecture-logical-view}}

**Read this as a map, not a checklist.** R25-11 defines **20 functional clusters**. Four of them carry the rest of this talk: **Communication Mgmt (`ara::com`)**, **Execution Mgmt (`ara::exec`)**, **Diagnostic Mgmt (`ara::diag`)** and **Update & Config Mgmt (`ara::ucm`)**.

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1 — © AUTOSAR.</div>

<div class="gloss">FC = Functional Cluster · ara:: = the C++ namespace prefix under ARA (AUTOSAR Runtime for Adaptive Applications) each cluster's API lives in · PSE51 = IEEE 1003.13 minimal single-process POSIX profile · STL = C++ Standard Template Library · the other ~16 clusters shown are out of scope for this talk</div>

<!-- ~70s | say: This is the platform straight from the spec, an unmodified figure. Do not read all twenty clusters. Point at four: ara::com for communication, ara::exec for execution management, ara::diag for diagnostics, and ara::ucm for updates. Those four carry the story. -->

---

## `ara::com` — one API, swappable bindings

<style scoped>
  img { display:block; margin: 4px auto 6px; max-height: 350px; width:auto; }
</style>

{{diagram:aracom-bindings-annotated}}

There is one protocol-agnostic API, based on a **proxy/skeleton** model. The **integrator picks the wire binding in the manifest**. The three **standardized** bindings are **SOME/IP, Signal-Based and DDS** (DDS has been present since **R18-03**). **Local IPC is the reality inside one machine.** It is implementation-level, not a standardized inter-vendor protocol.

<div class="figsrc">Redrawn and annotated after AUTOSAR AP_SWS_CommunicationManagement, R25-11, Fig. 7.1 — original unmodified figure in the full deck and autosar/specs/.</div>

<div class="gloss">rmw = ROS 2's middleware-abstraction layer · protocol-agnostic = the API does not depend on any specific wire protocol</div>

<!-- ~80s | say: ara::com is one protocol-agnostic API on a proxy/skeleton model. The app codes against it, and the integrator picks the wire binding in the manifest. There are three standardized bindings: SOME/IP, Signal-Based and DDS. DDS has been present since R18-03. Local IPC is the reality inside one machine, but it is implementation-level, not a standardized inter-vendor protocol. The transferable idea: the API is protocol-agnostic and the binding is swappable underneath, exactly like ROS 2's rmw over DDS. -->

---

## Inside the repo 1/3: `Fang717/arccore-core-21`

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

Three repositories are worth reading, and this is what is inside each one. The first two are open Classic Platform stacks written in C. This first one is a full vendor stack, the Arctic Core embedded platform.

<div class="cols">
<div class="tree">

```text
arccore-core-21/   (@ 7874929 · one bulk upload)
core/
├── communication/   Com, PduR, CanIf, CanTp, SoAd
│   └── lwip-2.0.3/   bundled TCP/IP stack
├── system/          Os (static RTOS), EcuM, BswM, SchM
├── diagnostic/      Dem, Dcm, Det
├── mcal/            Can, Adc, Spi, Pwm, Wdg drivers
│   └── arch/         mpc5xxx, rh850_x, stm32, tms570
├── arch/            generic (linux sim), transceivers
└── boards/          mpc5xxx, rh850, jacinto, s32k
examples/            HelloWorld, LedBlinker, LinSimple
```

<p class="pin">Fang717/arccore-core-21 @ 7874929 · GPL-2.0 (README-stated, no LICENSE file)</p>
<p class="quote">"Arctic Core is an open-source implementation of the AUTOSAR (Automotive Open System Architecture) standard, designed for the development of automotive Electronic Control Units (ECUs)." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p>This is a full Classic AUTOSAR basic-software stack in C. <code>core/communication/</code> holds the communication chain (Com, PduR, CanIf, CanTp, SoAd) and a bundled <code>lwip-2.0.3</code> TCP/IP stack. <code>core/system/</code> holds the static real-time OS kernel plus the system services EcuM, BswM and SchM. <code>core/diagnostic/</code> holds the UDS modules Dem, Dcm and Det. The modules declare AUTOSAR 4.0.3 in release macros, for example <code>Com.h</code> sets <code>COM_AR_RELEASE</code> to 4/0/3.</p>
<h3>What you can do</h3>
<p>Read it for the shape of a real, complete Classic stack. Hardware support is broad. The microcontroller ports live under <code>core/mcal/arch/</code> (armv7_m, jacinto, mpc5xxx, rh850_x, stm32, tcxxx, tms570, zynq), with matching board configs under <code>core/boards/</code>. Note that <code>core/arch/</code> itself only holds a generic host target, which is a Linux simulation, plus CAN transceivers. The runnable programs under <code>examples/</code> show the application and RTE layer, not the basic-software internals.</p>
<h3>Know the limits</h3>
<p>This is an anonymous re-upload (GitHub user Fang717) of a commercial-era vendor snapshot, Arctic Core version 21.0.0. It has no genuine development history. All 8,481 source files were added in one bulk "Initial commit" in June 2024, and no later commit touches the code. The README states GPL-2.0, but there is no top-level LICENSE file, the GitHub API reports no license, and the per-file headers instead carry a dual notice, either a commercial ArcCore licence or GPL version 2. The code itself is old. The per-file copyright reads 2013 and 2014, so despite the 21.0.0 label and the 2024 upload it is AUTOSAR 4.0.3-era code.</p>
</div>
</div>

<div class="gloss">Com = the AUTOSAR signal-packing communication module (not a serial port) · PduR = PDU Router (routes PDUs between COM and the bus interfaces) · PDU = Protocol Data Unit · CanIf = CAN Interface (hardware-independent CAN) · CanTp = CAN Transport Protocol (ISO 15765-2 segmentation) · SoAd = Socket Adaptor (the Ethernet and IP transport interface) · CAN = Controller Area Network (the automotive serial bus) · LIN = Local Interconnect Network · lwip = lightweight IP (a small open-source TCP/IP stack) · TCP/IP = the standard internet transport and network protocols · RTOS = Real-Time Operating System · Os = the static real-time AUTOSAR OS kernel · EcuM = ECU Manager · BswM = Basic Software Mode Manager · SchM = BSW Scheduler · BSW = Basic Software (CP's generated C layer, built statically, no heap) · UDS = Unified Diagnostic Services (ISO 14229) · Dem = Diagnostic Event Manager (the fault store) · Dcm = Diagnostic Communication Manager (the UDS server) · Det = Default Error Tracer (AUTOSAR's development-time error hook) · MCAL = Microcontroller Abstraction Layer (the lowest driver layer) · Adc = Analog-to-Digital Converter driver · Spi = Serial Peripheral Interface driver · Pwm = Pulse-Width Modulation driver · Wdg = Watchdog driver · RTE = Runtime Environment (the generated glue between components and BSW) · ECU = Electronic Control Unit · MCU = Microcontroller · CP = Classic Platform · COM_AR_RELEASE = the macro that stamps the AUTOSAR release a module targets · GPL-2.0 = GNU General Public License version 2 (an open-source licence) · API = Application Programming Interface</div>

<!-- ~65s | say: This is the first of three repositories worth reading, a Classic Platform stack in C. It is Arctic Core, a full vendor basic-software stack. The communication folder holds Com, the PDU router, the CAN interface and the transport protocol, plus a bundled lightweight TCP/IP stack. The system folder holds the static real-time OS kernel and the ECU state managers, and the diagnostic folder holds the fault store and the UDS server. The modules stamp themselves as AUTOSAR four-oh-three in a release macro. Now the honest part. This is an anonymous re-upload of a commercial vendor snapshot, version twenty-one point zero, with no real history: all eight thousand source files were added in one initial commit. The README says GPL version two, but there is no license file, and the per-file headers carry a dual commercial-or-GPL notice instead. The copyright reads twenty-thirteen and fourteen, so it is four-oh-three era code. Read it for the shape, not for production. -->

---

## The code 1/3: Classic AUTOSAR in C

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 11px; margin-top: 6px; line-height: 1.3; }
</style>

**C: publishing a signal through AUTOSAR COM** (`Fang717/arccore-core-21`, Arctic Core 21.0.0):

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

<p class="attr"><a href="https://github.com/Fang717/arccore-core-21/blob/7874929df54e45530720f15441cb3bc20479cebd/core/communication/Com/src/Com_Com.c#L44-L52">Fang717/arccore-core-21 @ 7874929 · core/communication/Com/src/Com_Com.c</a></p>

**C: an application component that talks only through the RTE**:

```c
#include "Rte_SwcWriterType.h"

static DigitalLevel state = 0;
void swcWriterRunnable() {
	// just pass data on in-port to out-port
	Rte_IWrite_SwcWriterRunnable_SenderPort_data1(Rte_IRead_SwcWriterRunnable_InputPort_data1());
	Rte_Call_Blinker_Write(state);
	state = !state;
}

void SwcWriterInit() {
	Rte_IWrite_Init_ComMControl_requestedMode(COMM_FULL_COMMUNICATION);
}
```

<p class="attr"><a href="https://github.com/Fang717/arccore-core-21/blob/7874929df54e45530720f15441cb3bc20479cebd/examples/HelloWorld/HelloWorld_App/src/SwcWriter.c#L15-L27">Fang717/arccore-core-21 @ 7874929 · examples/HelloWorld/HelloWorld_App/src/SwcWriter.c</a></p>

<div class="gloss"><b>What to notice:</b> The first function is the COM service a task calls to publish an application signal, which COM later packs into an I-PDU on the bus. It returns a vendor typedef'd <code>uint8</code> and takes a <code>Com_SignalIdType</code>, not bare C types, so the module behaves identically on every MCU. Before it does any work it checks that COM was initialized, and if not it reports a development-time error through the DET and returns a service-not-available code rather than touching uninitialized config. The <code>/* @req COM334 */</code> tag links this exact line to a numbered clause in the AUTOSAR COM specification, and that requirement-to-code traceability runs through the whole stack. The second snippet is an application software component, and it never calls the basic software directly. It only uses generated <code>Rte_</code> functions: <code>Rte_IRead</code> and <code>Rte_IWrite</code> move port data, and <code>Rte_Call</code> invokes a client-server operation, so the component stays independent of the hardware and the bus. Even asking the network to wake up is done through the RTE, where <code>SwcWriterInit</code> requests full communication from the ComM module. Those long <code>Rte_</code> names are produced by the RTE generator from the ECU configuration, not written by hand, which is the essence of the config-driven Classic style. · COM = the AUTOSAR signal-packing communication module (not a serial port) · DET = Default Error Tracer (AUTOSAR's development-time error hook) · I-PDU = Interaction-layer PDU, the packed frame COM builds from signals · PDU = Protocol Data Unit · BSW = Basic Software (CP's generated C layer) · SWC = Software Component · RTE = Runtime Environment (the generated glue between components and BSW) · ComM = the Communication Manager module (controls bus wake-up and mode) · ECU = Electronic Control Unit · MCU = Microcontroller · id = identifier</div>

<!-- ~65s | say: These are two real functions from the Arctic Core stack. The first is Com send signal, the service a task calls to publish an application signal. Notice the fixed-width vendor type on the argument, so the code behaves the same on every microcontroller. Before it does anything it checks that the module was initialized; if not, it reports a development-time error through the Default Error Tracer and returns a service-not-available code. The comment tagged requirement COM three three four links that exact line to a numbered clause in the AUTOSAR COM specification, and that traceability runs through the whole stack. The second snippet is an example application component. It never calls a driver or the communication module directly. It only calls generated R-T-E functions: read and write move port data, and call invokes a client-server operation. Those long names come from the R-T-E generator, not written by hand. That is the config-driven Classic style. -->

---

## Inside the repo 2/3: `autoas/as`

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

<div class="cols">
<div class="tree">

```text
as/
├── infras/          Classic AUTOSAR BSW, mostly C
│   ├── communication/   Com, CanIf, PduR, CanTp, SomeIp
│   ├── diagnostic/      Dcm, Dem, Det
│   ├── memory/          NvM, Fee, Ea
│   ├── system/kernel/   AUTOSAR OS (static, task, alarm)
│   └── mcal/            Can, Dio, Fls MCAL drivers
├── tools/           config generators + GUI tools
│   ├── generator/       per-module Python codegen
│   └── asone/           QT Com/Dcm/bootloader GUI
├── app/             examples, bootloader, platform
├── LICENSE          dual GPLv3 / commercial
└── README.md
```

<p class="pin">autoas/as @ bfe1805 · dual GPLv3 / Commercial</p>
<p class="quote">"This project is only free to be used for evaluation and study purpose, all of the BSWs are developed by me alone according to AUTOSAR 4.4." <span class="src">(its README)</span></p>

</div>
<div class="info">
<h3>Start reading here</h3>
<p>This is a from-scratch Classic AUTOSAR 4.4 basic-software stack, written mostly in C, with the modules under <code>infras/</code>. It covers a broad set: a communication stack (Com, PduR, CanIf, CanTp, SomeIp, Sd, LinIf), diagnostics (Dcm, Dem, Det), memory services (NvM, Fee, Ea), crypto (Csm), MCAL drivers (Can, Dio, Fls, Lin, Port), and a static, fixed-priority real-time OS kernel with tasks, alarms, counters and resources under <code>infras/system/kernel/os/</code>.</p>
<h3>What you can do</h3>
<p>Unlike a bare stack, it also provides desktop tooling alongside the C that runs on the microcontroller. <code>tools/generator/</code> is a per-module Python configuration generator (Com.py, Dcm.py, CanTp.py and about forty more), and <code>tools/asone/</code> is a QT graphical tool for Com, Dcm and the flash loader. It also provides a bootloader and CAN or LIN bus simulators over IP sockets. The whole tree builds with SCons.</p>
<h3>Know the limits</h3>
<p>This is one person's project. The history shows a single maintainer, and the README says the modules were "developed by me alone". The AUTOSAR 4.4 conformance is the author's claim, not a verified or certified result, so treat it as AUTOSAR-style rather than compliant. The licence is also internally inconsistent. The LICENSE file declares a dual GPLv3-or-commercial grant, while the README restricts use to evaluation and study only, and GitHub reports the licence as "Other". Some paths are still works in progress.</p>
</div>
</div>

<div class="gloss">BSW = Basic Software (CP's generated C layer, built statically, no heap) · Com = the AUTOSAR signal-packing communication module · PduR = PDU Router (routes PDUs between COM and the bus interfaces) · PDU = Protocol Data Unit · CanIf = CAN Interface (hardware-independent CAN) · CanTp = CAN Transport Protocol (ISO 15765-2 segmentation) · SomeIp / SOME/IP = Scalable service-Oriented MiddlewarE over IP · Sd = SOME/IP Service Discovery · LinIf = LIN Interface · LIN = Local Interconnect Network · Dcm = Diagnostic Communication Manager (the UDS server) · Dem = Diagnostic Event Manager (the fault store) · Det = Default Error Tracer (AUTOSAR's development-time error hook) · UDS = Unified Diagnostic Services (ISO 14229) · NvM = Non-volatile Memory manager · Fee = Flash EEPROM Emulation · Ea = EEPROM Abstraction · EEPROM = Electrically Erasable Programmable Read-Only Memory · Csm = Crypto Service Manager · MCAL = Microcontroller Abstraction Layer (the lowest driver layer) · Can = the CAN driver · Dio = Digital Input/Output driver · Fls = Flash driver · Port = the pin-multiplexing (Port) driver · CAN = Controller Area Network (the automotive serial bus) · IP = Internet Protocol · QT = the Qt C++ GUI toolkit · GUI = Graphical User Interface · SCons = a Python-based software build tool · CP = Classic Platform · GPLv3 = GNU General Public License version 3 (an open-source licence)</div>

<!-- ~65s | say: The second repository is autoas slash as, a very different Classic stack. Where Arctic Core is an anonymous re-upload of a commercial snapshot, this one is written from scratch by one person as a Classic AUTOSAR four-point-four basic-software stack. It covers a lot: the communication stack including SOME/IP and service discovery, the diagnostic modules, memory services, crypto, the microcontroller drivers, and a static, fixed-priority real-time OS kernel. It also provides desktop tooling: a per-module Python configuration generator, a Qt tool for Com, Dcm and the flash loader, and bus simulators over sockets. It builds with SCons. This is one person's project; the README says the modules were developed by the author alone. The four-point-four conformance is the author's claim, not a certified result, so read it as AUTOSAR-style. The licence is also inconsistent: the license file says dual G-P-L or commercial, the README says evaluation and study only, and GitHub reports it as Other. -->

---

## The code 2/3: `autoas/as`

<style scoped>
  section { font-size: 17px; padding: 16px 40px 12px; }
  h2 { font-size: 24px; margin: 0 0 6px; }
  p { font-size: 13px; margin: 6px 0 2px; }
  pre { font-size: 11px; line-height: 1.24; margin: 3px 0 2px; background: #f6f8fc; }
  pre code { font-size: 11px; background: transparent; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px; }
  .gloss { font-size: 10.5px; margin-top: 6px; line-height: 1.3; }
</style>

**C: the same COM publish API, written from scratch** (`autoas/as`, AUTOSAR 4.4 per its author):

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

<p class="attr"><a href="https://github.com/autoas/as/blob/bfe1805f3cf61ddf0685aa981d64260bf9349cee/infras/communication/Com/Com.c#L457-L469">autoas/as @ bfe1805 · infras/communication/Com/Com.c</a></p>

**C: the priority-ceiling protocol, an excerpt from inside `GetResource()`**:

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

<p class="attr"><a href="https://github.com/autoas/as/blob/bfe1805f3cf61ddf0685aa981d64260bf9349cee/infras/system/kernel/os/kernel/resource.c#L74-L83">autoas/as @ bfe1805 · infras/system/kernel/os/kernel/resource.c (a slice from inside GetResource())</a></p>

<div class="gloss"><b>What to notice:</b> The first function is the same COM publish service you just saw in Arctic Core, but written independently. It is a public AUTOSAR service, so it returns <code>Std_ReturnType</code>, the standard E_OK or E_NOT_OK contract, and it sets <code>ret</code> to failure first so the caller sees an error unless the send really succeeds. The three <code>DET_VALIDATE</code> lines are the Classic development-error guards, all tagged with COM's service id 0x0A. They reject an uninitialized module, an out-of-range signal id and a NULL data pointer, and return early on any of them. The signal is then fetched by index from a generated, read-only configuration table, <code>COM_CONFIG->SignalConfigs</code>, which is the config-driven pattern again. The second snippet is a slice from inside <code>GetResource()</code> in the OS kernel, and it is the priority-ceiling protocol. Taking a resource raises the running task's priority up to the resource's statically configured ceiling, which is how the kernel prevents priority inversion and deadlock without ever blocking at runtime. The previous priority and previously held resource are saved first, so nested resource pairs unwind like a stack, strictly last-in first-out. The whole update runs inside <code>EnterCritical()</code> and <code>ExitCritical()</code> with interrupts masked, because it changes shared scheduler state, and it only applies in task context, not in an interrupt handler. · COM = the AUTOSAR signal-packing communication module (not a serial port) · DET = Default Error Tracer (AUTOSAR's development-time error hook) · id = identifier · API = Application Programming Interface</div>

<!-- ~65s | say: Now the same idea in the from-scratch stack. The first function is Com send signal again, but written independently. It is a public AUTOSAR service, so it returns the standard result type and sets the result to failure first. The three validate lines are the same development-error guards, all tagged with COM's service id oh-A: they reject an uninitialized module, an out-of-range signal id and a null pointer. Then the signal is looked up by index in a generated read-only configuration table. Same config-driven pattern, a different author. The second snippet is a slice from inside the operating system's get-resource call: the priority-ceiling protocol. Taking a resource raises the task's priority to the resource's statically configured ceiling, which is how the kernel prevents priority inversion and deadlock without blocking at runtime. The previous priority is saved first, so nested resources unwind last in first out. The whole update runs with interrupts masked, because it touches shared scheduler state. -->

---

## Inside the repo 3/3: `langroodi/Adaptive-AUTOSAR`

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

<div class="gloss">AP = Adaptive Platform · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · Proxy/Skeleton = <code>ara::com</code>'s client-/service-side stubs · SOME/IP = Scalable service-Oriented MiddlewarE over IP · RPC = Remote Procedure Call · ARXML = the AUTOSAR XML manifest and config format · OAuth = Open Authorization (token-based access) · REST = Representational State Transfer (an HTTP API style) · MIT = an open-source licence · API = Application Programming Interface</div>

<!-- ~65s | say: This is the third of three repositories worth your time. langroodi Adaptive-AUTOSAR is the teaching codebase. Start with the README. It says in one paragraph what the project is, and it lists the exact build, test and run commands. Then open main.cpp. It is about fifty-five lines. It builds Execution Management, spins a polling loop, and passes in the manifest files. The execution-client header is the one to study. It shows an app reporting its state to Execution Management, and its private members reveal that the call is really a SOME/IP remote procedure call, not a generated ara::com proxy. To run it, configure and build with CMake, run the unit tests with ctest, then launch by passing the four ARXML manifest files. Two honest limits. The demo is not offline. It needs a Volvo API key, an OAuth token and live network access. And the code has been dormant since 2023. Read it for the shape. -->

---

## The code 3/3: `langroodi/Adaptive-AUTOSAR`

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

<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/com/someip/rpc/rpc_client.h#L19-L29">langroodi/Adaptive-AUTOSAR @ 866d158 · src/ara/com/someip/rpc/rpc_client.h</a></p>

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

<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/application/platform/execution_management.cpp#L146-L156">langroodi/Adaptive-AUTOSAR @ 866d158 · src/application/platform/execution_management.cpp</a></p>

<div class="gloss"><b>What to notice:</b> <code>RpcClient</code> is the abstract SOME/IP request-and-response client that the platform's wiring is built on. Its public <code>HandlerType</code> is just a <code>std::function</code> taking a decoded message. Its private state is two maps keyed by a packed service and method id, one tracking per-method session ids and one holding the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass such as <code>SocketRpcClient</code> supplies the actual send. In the second snippet a concrete <code>SocketRpcServer</code> is built from the parsed RPC configuration (address, port, protocol version) and handed by pointer into an <code>ara::exec::ExecutionServer</code>, so the execution server speaks to clients only through the SOME/IP RPC abstraction. The last lines load the function-group states and their initial state from the ARXML model, which is the config-driven, model-first style of the codebase. · SOME/IP = Scalable service-Oriented MiddlewarE over IP · RPC = Remote Procedure Call · <code>ara::</code> = the AP C++ API namespaces · <code>ara::com</code> = AP's Communication Management API · <code>ara::exec</code> = AP's Execution Management API · ARXML = the AUTOSAR XML manifest and config format · id = identifier · AP = Adaptive Platform · API = Application Programming Interface</div>

<!-- ~65s | say: Now the same platform in the Adaptive teaching repository. The first snippet is the class shape. RpcClient is the abstract SOME/IP request and response client that all the wiring is built on. Its public handler type is just a function that takes a decoded message. Its private state is two maps, one tracking per-method session ids and one holding the registered response handlers. The class is deliberately transport-agnostic, so a concrete subclass supplies the actual send. The second snippet is the Execution Management entry point. A socket RPC server is built from the parsed configuration, the address, the port and the protocol version. That server is then handed by pointer into an execution server, so the execution server talks to clients only through the RPC abstraction. The last lines load the function-group states and their initial state from the ARXML model. That config-driven, model-first style runs through the whole codebase. -->

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
  .boundary { font-size: 14px; margin: 12px 0 0; line-height: 1.35; }
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
<p class="attr"><a href="https://github.com/langroodi/Adaptive-AUTOSAR/blob/866d158a10d895f1d269689a8ddf8153dc03b321/src/ara/exec/execution_client.h#L54-L58">langroodi/Adaptive-AUTOSAR @ 866d158 · src/ara/exec/execution_client.h</a></p>

<div class="gloss"><b>What to notice:</b> <code>ReportExecutionState</code> returns an <b><code>ara::core::Result&lt;void&gt;</code></b>. AP signals errors as a <i>returned value</i>, <b>not a thrown exception</b>, and it is the <b>contract every AA implements</b> so EM knows it reached <code>kRunning</code>. The spec box above names the matching <code>ara::com</code> event API, which is <code>Send(…)</code>, and the skeleton's offer lifecycle is likewise spec-named: <b><code>OfferService()</code> / <code>StopOfferService()</code> on the <code>ServiceSkeleton</code> class</b> ([SWS_CM_00101] / [SWS_CM_00111], same document). Educational caveat: this C++ repo is <b>dormant since 2023-06-22 (inactive for 3 years)</b>, so read it for the shape, not for production. <code>ara::</code> = the AP C++ API namespaces · AA = Adaptive Application · EM = Execution Management · AP = Adaptive Platform · API = Application Programming Interface · ara::com = AP's Communication Management API · CAPI = Common Adaptive Platform Implementation · CAPI partner-gated (AUTOSAR partners only): autosar.org/capi</div>

<p class="boundary"><b>The honest boundary for the whole tour: the building blocks and the teaching code are open. A complete, conformant, open AP stack does not exist. The one complete official implementation, CAPI, is gated to AUTOSAR partners.</b></p>

<!-- ~58s | say: This is the shape of real ara-colon-colon code from a public repo. Start with the standardized surface. The spec names the ara::com event-send API: Send of a sample type, and Send of a SampleAllocateePtr. That is the contract vendors implement. Now look at the code. ReportExecutionState returns an ara::core::Result, not a thrown exception. Adaptive signals errors as a returned value. It is the contract every Adaptive Application implements, so Execution Management knows it reached running. On the ara::com side, the skeleton lifecycle is spec-named too: OfferService and StopOfferService on the ServiceSkeleton class. But read this for the shape, not for production. The repo is educational and has been dormant since June 2023. And one boundary for the whole tour: the building blocks and the teaching code are open, but a complete, conformant, open Adaptive stack does not exist, and the one complete official implementation, called CAPI, is gated to AUTOSAR partners. -->

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
| **OS** | AUTOSAR OS, a static real-time kernel (SC1–SC4, no MMU) | **not a new OS**: an OS Interface on POSIX **PSE51** over Linux/QNX/PikeOS |
| **Model** | fully **static**: C, RTE-generated `Rte_Read/Write/Call`, one binary | **dynamic**: C++14, `ara::*`, manifests bound late, discovery and start/stop at runtime |
| **Comms** | **signal**-oriented: COM packs signals into I-PDUs on CAN/LIN/FlexRay/Ethernet | **service**-oriented: `ara::com` proxy/skeleton over **SOME/IP or DDS** |
| **Diagnostics** | **DCM + DEM**: UDS over DoCAN/DoIP | **DM** (`ara::diag`): UDS server *and* SOVD. **DoIP the only standardized transport** (custom permitted) |
| **Updates** | reflash the **whole ECU** via bootloader/UDS (0x34/0x36/0x37) | **UCM**: install or update individual **Software Clusters**, OTA-native |
| **Safety** | mature ISO 26262 **up to ASIL D** (first ASIL-D AUTOSAR impl certified **2016**) | "up to ASIL D" on paper, harder in practice. **ASIL-B shipping, ASIL-D underway** |

<div class="gloss">CP is <b>not CAN-only</b> — a standardized SOME/IP Transformer has shipped since <b>4.2.1 (Oct 2014)</b>, years before AP's first release · MMU = Memory Management Unit · PSE51 = minimal single-process POSIX profile · SOVD = Service-Oriented Vehicle Diagnostics · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · DCM = Diagnostic Communication Manager · DEM = Diagnostic Event Manager · DM = AP's Diagnostic Manager (`ara::diag`) · DoCAN = Diagnostics over CAN (ISO 15765-2) · DoIP = Diagnostics over IP (ISO 13400) · the ASIL hedge, exactly: no fully-certified end-to-end ASIL-D AP middleware ships as of mid-2026 — ASIL-D lives in the OS (QNX) + hypervisor + vendor safety case, and a "developed to ASIL-x" process claim ≠ a "certified at ASIL-x" claim · first cert = Vector MICROSAR Safe, exida, 2016 · ASIL status is our reading as of mid-2026; sources are in the full deck references · DoIP-only standardized transport rule: AP_SWS_Diagnostics (Doc ID 723) R25-11 §7.1 (UDS Transport Layer); DoIP (ISO 13400-2) is the only network transport the spec details, and custom UDS transports are permitted through the Transport Protocol API</div>

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

**The business rule underneath:** AUTOSAR value scales with how many organizational boundaries your software crosses. Vertically-integrated OEMs such as Rivian skip it ([Sonatus interview](https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/)). Tier-1s implement it to win OEM RFQs.

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

<div class="gloss">CP = Classic Platform · AP = Adaptive Platform · ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · HPC = High-Performance Computer · first cert = Vector MICROSAR Safe, exida, 2016</div>

<!-- ~65s | say: Three takeaways. One: AUTOSAR is a supply-chain standard, and ASIL comes from ISO 26262, not from AUTOSAR. Two: two platforms, coexisting by design. Classic is static and certified on MCUs, and Adaptive is a service platform on HPCs. Three: find your silicon row on the decision map, and you know the stack, the OS question, and who sells it. -->

---

## Q&A — and where to dig deeper

- **The full 73-slide deck** is `autosar/slides/autosar-deck.md`. It expands every point here with the
  primary-source references.
- **The local spec mirror** is `autosar/specs/`. It holds **35 R25-11 PDFs** (FO / CP / AP).
- **The research docs and blog** live under `autosar/` (Classic, Adaptive, Classic-vs-Adaptive).

<div class="gloss">FO = Foundation · CP = Classic Platform · AP = Adaptive Platform · Licensing: spec figures are reproduced <b>unmodified</b> (© AUTOSAR, R25-11); the adapted diagrams are <b>redrawn after the cited figures</b>, not copied from the spec artwork.</div>

<!-- ~35s | say: To go deeper: the full 73-slide deck expands every one of these. The local spec mirror has all 35 R25-11 PDFs. The research docs and blog live under autosar/. On licensing: the spec figures are unmodified and copyright AUTOSAR R25-11. The adapted diagrams are redrawn after the cited figures. Questions? -->
