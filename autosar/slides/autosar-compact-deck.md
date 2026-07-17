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

# AUTOSAR in 20 minutes — Classic vs Adaptive: what runs where

## for embedded/firmware engineers · 2026

The condensed field guide: **one organization, two platforms, one vehicle** — for engineers
who know MCUs, CAN, an RTOS and bare-metal reflashing. Release-stamped to **AUTOSAR R25-11**
(published 2025-11-27). External claims are URL-sourced — the **full deck carries the references.**

<!-- ~40s | say: Twenty minutes, one question — which AUTOSAR software runs on which chip. Everything here is stamped to R25-11, published late November 2025. If you already know MCUs, CAN and reflashing, you have the mental model; we're just naming the automotive version. -->

---

## Why AUTOSAR exists — one standard, many competitors

- **A worldwide development partnership** — founding talks **2002**, Development Agreement
  **July 2003**; **~360 partners today** across the industry. Specs are **free to read,
  license-to-build**
- **The model in one line** (a founding-era phrase — Heinecke et al., 2006): *cooperate on
  standards, compete on implementation* — one shared
  spec and one XML schema, many vendors selling their own conformant stacks
- **The business rule that predicts adoption**: **AUTOSAR value scales with how many
  organizational boundaries your software crosses** — Tier-1s implement it **to win OEM RFQs**;
  a vertically-integrated OEM (**Rivian**) skips it and rolls its own

<div class="gloss">RFQ = request for quotation · Tier-1 = the supplier who builds an ECU for the OEM · the partnership shares specifications and competes on the implementations built from them</div>

<!-- ~75s | say: AUTOSAR is a partnership, not a product — talks in 2002, the agreement in July 2003, about 360 partners today. The founding-era phrase — cooperate on standards, compete on implementation: one shared spec and schema, many vendors selling conformant stacks. The rule that predicts who adopts it — value scales with how many organizational boundaries your software crosses. Tier-1 suppliers implement it to win OEM contracts; a vertically-integrated maker like Rivian just skips it. -->

---

## One vehicle, two platforms

<style scoped>
  img { display:block; margin: 6px auto 10px; max-height: 430px; width:auto; }
</style>

{{diagram:sdv-ecu-consolidation}}

**CP runs on the deeply-embedded MCUs · AP runs on the high-performance-compute (HPC) SoCs — and the two coexist in one 2026 vehicle.**

<!-- ~55s | say: One vehicle, two platforms. Classic runs on the deeply-embedded microcontrollers — the reflex nervous system. Adaptive runs on the high-performance-compute SoCs — the brain. They aren't competitors; they coexist in one 2026 car, joined by Ethernet and gateways. -->

---

## Classic in one slide

<style scoped>
  section { font-size: 21px; }
  img { display:block; margin: 4px auto 8px; max-height: 300px; width:auto; }
  li { margin-bottom: 4px; }
</style>

{{diagram:stack-autosar-classic}}

- **Everything static at build time** — task set, memory map and communication matrix are frozen in **ARXML** and generated into **one ECU binary**
- **OSEK-heritage OS** — AUTOSAR OS is an OSEK/VDX superset, packaged as **Scalability Classes SC1–SC4** (adding timing + memory protection)
- **The mature ASIL-D path** — statically-everything determinism; first AUTOSAR impl certified ISO 26262 **up to ASIL D (2016)**

<!-- ~70s | say: Classic in one slide. Everything is static and decided at build time — task set, memory map, communication matrix — all frozen in ARXML and generated into one ECU binary. The OS is OSEK heritage, packaged as scalability classes SC1 through SC4 that add timing and memory protection. And it owns the mature ASIL-D path: the first AUTOSAR implementation certified to ISO 26262 up to ASIL D landed in 2016. -->

---

## The relocation trick — why an SWC moves ECUs without a code change

<style scoped>
  img { display:block; margin: 4px auto 6px; max-height: 360px; width:auto; }
</style>

{{diagram:vfb-relocation-annotated}}

SWCs talk **only** over the **Virtual Functional Bus** via **`Rte_Write` / `Rte_Read` / `Rte_Call`** — never a bus or a driver. The **RTE, generated per deployment**, decides whether the peer is a local buffer copy or a remote COM message. **Relocating the SWC changes only what the generator emits.**

<div class="figsrc">Redrawn and annotated after AUTOSAR CP_TR_VFB, R25-11, Fig. 2.2 — original unmodified figure in the full deck and autosar/specs/.</div>

<!-- ~75s | say: The one genuinely new idea for a firmware engineer — relocation. Software components never call each other; they talk over the Virtual Functional Bus using Rte_Write, Read and Call, and they never name a bus or a driver. The RTE, generated per deployment, decides whether the peer is a local buffer copy or a remote message on CAN or Ethernet. So moving a component to a different ECU changes only what the generator emits — no code change. There is no bare-metal analogue. -->

---

## CP comms + diagnostics in 60 seconds

- **Communication is a frozen matrix** — signal-oriented, **not** service-oriented. The
  **K-matrix** fixes every frame, signal, sender and receiver at build time; **COM** packs
  signals → **I-PDUs** onto CAN/LIN/FlexRay/Ethernet, statically generated and provable at integration
- **Diagnostics split — get it right**: **DEM computes** — the fault-memory database that
  debounces monitor results and maintains the per-DTC **UDS status byte**; **DCM formats** — a
  generated **UDS server** that reads DEM and talks to the tester. **DCM computes nothing about faults**
- **Reflash = the bootloader you know** — UDS **0x34 / 0x36 / 0x37** (RequestDownload /
  TransferData / RequestTransferExit) flashes the **whole ECU** through the bootloader

<div class="gloss">COM / PduR / CanIf = the build-time-frozen signal-packing / routing / CAN-interface chain · DEM = Diagnostic Event Manager · DCM = Diagnostic Communication Manager · DTC = Diagnostic Trouble Code · UDS = Unified Diagnostic Services (ISO 14229)</div>

<!-- ~75s | say: Classic comms and diagnostics in sixty seconds. Communication is a frozen signal matrix — the K-matrix fixes every frame and signal at build time; COM packs signals into I-PDUs. Diagnostics split into two modules, and this is the number-one thing people get wrong: DEM computes — it's the fault-memory database that debounces and maintains the UDS status byte. DCM only formats — it's the UDS server that reads DEM and talks to the tester. And reflashing is the bootloader you already know: UDS services 0x34, 0x36 and 0x37 flash the whole ECU. -->

---

## Why Adaptive exists

<style scoped>
  section { font-size: 21px; }
  img { display:block; margin: 4px auto 4px; max-height: 300px; width:auto; }
  li { margin-bottom: 4px; }
</style>

- **CP's strengths invert into limits**: a **static communication matrix** (no runtime service
  discovery), **no dynamic deployment / limited OTA of function**, and a **C-centric BSW with no
  heap** — so it cannot host large, evolving C++/perception stacks
- **AUTOSAR's answer is a second platform** — a **service platform on POSIX**. AP is
  **middleware + services on top of a POSIX OS, *not* a new OS**; **Adaptive Applications are
  ordinary POSIX processes (C++) linked against ARA**

{{diagram:stack-autosar-adaptive}}

<!-- ~85s | say: Why a second platform. Classic's strengths invert into limits: a static communication matrix with no runtime discovery, no dynamic deployment, and a C-centric stack with no heap — so it can't host large, evolving C++ and perception code. The answer is Adaptive: a service platform on POSIX. Say it precisely — Adaptive is middleware and services on top of a POSIX OS, not a new OS. Adaptive Applications are ordinary POSIX processes, written in C++, linked against ARA. -->

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

The spec makes it a hard requirement: Adaptive Applications program against **POSIX PSE51 + the C++ Standard Library** (AP_SWS_OperatingSystemInterface, Doc 719 — **[RS_OSI_00100] "POSIX PSE51 Compliance"**; PSE51 per IEEE 1003.13, following POSIX-1003.1-2003). The platform underneath additionally needs an **MMU multi-process OS** — Execution Management spawns *processes* per manifest.

| Can host AP | POSIX story | | Cannot host AP | why not |
|---|---|---|---|---|
| **QNX Neutrino** | full POSIX — **PSE52-certified in the 2008 era**, advertised today as conformance — **the production default**, ASIL-D via QNX OS for Safety | | **FreeRTOS** (+Labs POSIX) | partial pthread subset — its own README: a POSIX app *"cannot be ported... using only this wrapper"*; no processes |
| **Linux / AGL** | POSIX-conformant (not formally certified) — dev + QM builds | | **SAFERTOS** | **no POSIX at all** (ships an OSEK layer instead); single static image |
| **Green Hills INTEGRITY** | POSIX API on an MMU separation kernel | | **Zephyr** | POSIX subset layer, single-image kernel, no MMU processes |
| **PikeOS** | POSIX personality on a separation microkernel | | **NuttX** | the most POSIX-faithful MCU RTOS (an optional MMU "kernel build" exists, but no fork/exec) — still MCU-class |
| **VxWorks** | POSIX + user-mode processes (RTPs) — capable, rare in AP practice | | **AUTOSAR OS (OSEK)** | no POSIX by design — that is CP’s OS |

**The test in one question: does the OS speak PSE51 *and* run MMU-isolated processes? Both yes → AP-capable. Anything task-model → CP/bare-metal land.**

<div class="gloss">PSE51/PSE52 = IEEE 1003.13 realtime profiles · MMU = per-process virtual address spaces (vs MPU region protection) · RTP = VxWorks Real-Time Process · left-column rows beyond QNX/Linux are capability-class statements, not AP-product endorsements · trivia: the Open Group live PSE52 register today lists VxWorks 7 + two Chinese automotive OSes — QNX's formal certificate was 2008-era</div>

<!-- ~70s | say: here is the hard architectural line: the spec requires POSIX PSE51 plus the C++ standard library for apps, and the platform needs an MMU multi-process OS because Execution Management spawns processes. That sorts every kernel you know into two buckets: QNX and Linux are the production pair - QNX carries the ASIL-D certification, Linux carries development. INTEGRITY, PikeOS, VxWorks are capable-class. Everything task-model - FreeRTOS, SAFERTOS, Zephyr, NuttX, OSEK - stays on the MCU side with Classic. -->

---

## The function clusters — straight from the spec

{{image:spec-ap-architecture-logical-view}}

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 4.1 — © AUTOSAR.</div>

<!-- ~70s | say: The platform straight from the spec — an unmodified figure. Don't read all twenty clusters. Point at four: ara::com for communication, ara::exec for execution management, ara::diag for diagnostics, ara::ucm for updates. Those four carry the whole story. -->

---

## `ara::com` — one API, swappable transports

<style scoped>
  img { display:block; margin: 4px auto 6px; max-height: 350px; width:auto; }
</style>

{{diagram:aracom-bindings-annotated}}

One protocol-agnostic API (**proxy/skeleton**); the **integrator picks the wire binding in the manifest**. The three **standardized** bindings are **SOME/IP · Signal-Based · DDS** (DDS present since **R18-03**). **Local IPC is the intra-machine reality — implementation-level, not a standardized inter-vendor protocol.**

<div class="figsrc">Redrawn and annotated after AUTOSAR AP_SWS_CommunicationManagement, R25-11, Fig. 7.1 — original unmodified figure in the full deck and autosar/specs/.</div>

<!-- ~80s | say: ara::com is one protocol-agnostic API on a proxy/skeleton model — the app codes against it, the integrator picks the wire binding in the manifest. Three standardized bindings: SOME/IP, Signal-Based, and DDS — DDS has been present since R18-03. Local IPC is the intra-machine reality, but it's implementation-level, not a standardized inter-vendor protocol. The transferable idea: the API is protocol-agnostic and the binding is swappable underneath — exactly like ROS 2's rmw over DDS. -->

---

## The shape of the code — real ara:: from public repos

<style scoped>
  section { font-size: 17px; padding-top: 14px; }
  pre { font-size: 11px; line-height: 1.18; margin: 3px 0; }
  pre code { font-size: 11px; }
  h2 { margin-bottom: 4px; }
  p { margin: 3px 0; }
  .spec { font-size: 12.5px; background:#eef2f8; padding:5px 9px; border-radius:6px; margin: 3px 0 8px 0; }
  .cite { color:#66708a; font-size:11.5px; }
  .attr { font-size: 11.5px; color:#66708a; margin: 2px 0 8px 0; }
  .gloss { font-size: 12px; margin-top: 7px; }
</style>

<p class="spec"><b>The standardized surface</b> — the spec names the <code>ara::com</code> event-send API: <code>Send({&lt;s-sample-derived-type&gt;})</code> and <code>Send(ara::com::SampleAllocateePtr&lt;SampleType&gt;)</code>.<br><span class="cite">AP_SWS_CommunicationManagement, R25-11, sec. 8.4.2.2.2</span></p>

**C++ — the AA → Execution Management state handshake** (`langroodi/Adaptive-AUTOSAR`, dormant since 2023-06-22):

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

<div class="gloss">What to notice: both return an <b><code>ara::core::Result</code> / <code>Result&lt;…, AraComError&gt;</code></b> — AP signals errors as a <i>returned value</i>, <b>not a thrown exception</b>; <code>ReportExecutionState</code> is the <b>contract every AA implements</b> so EM knows it reached <code>kRunning</code>; <code>offer()</code>/<code>stop_offer()</code> are the <b><code>OfferService</code>/<code>StopOfferService</code> skeleton lifecycle</b>. Educational caveat: the C++ repo is <b>dormant since 2023-06-22 (3 years cold)</b> and the Rust repo was <b>created 2026-03-30 — promise, not track record</b>; read them for the shape, not for production. AA = Adaptive Application · EM = Execution Management.</div>

<!-- ~78s | say: The shape of real ara-colon-colon code from public repos. Start with the standardized surface — the spec names the ara::com event-send API: Send of a sample type, and Send of a SampleAllocateePtr; that is the contract vendors implement. Now two public repos. Notice both return an ara::core::Result, not a thrown exception — Adaptive signals errors as a returned value. ReportExecutionState is the contract every Adaptive Application implements so Execution Management knows it reached running. And offer, with its stop-offer pair, is the skeleton's OfferService lifecycle. But read these for the shape, not for production: the C++ repo is educational and dormant, the Rust one is only weeks old. -->

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
| **Target** | deeply-embedded MCUs — Infineon AURIX · NXP S32K · Renesas RH850 | HPC SoCs — NVIDIA Orin/Thor · Qualcomm · NXP S32G · Renesas R-Car |
| **OS** | AUTOSAR OS — OSEK superset (SC1–SC4, no MMU) | **not a new OS**: an OS Interface on POSIX **PSE51** over Linux/QNX/PikeOS |
| **Model** | fully **static** — C, RTE-generated `Rte_Read/Write/Call`, one binary | **dynamic** — C++14, `ara::*`, manifests bound late; discovery + start/stop at runtime |
| **Comms** | **signal**-oriented — COM packs signals → I-PDUs on CAN/LIN/FlexRay/Ethernet | **service**-oriented — `ara::com` proxy/skeleton over **SOME/IP or DDS** |
| **Diagnostics** | **DCM + DEM** — UDS over DoCAN/DoIP | **DM** (`ara::diag`) — UDS server *and* SOVD; **DoIP the only standardized transport** (custom permitted) |
| **Updates** | reflash the **whole ECU** — bootloader/UDS (0x34/0x36/0x37) | **UCM** — install/update individual **Software Clusters**; OTA-native |
| **Safety** | mature ISO 26262 **up to ASIL D** (first ASIL-D AUTOSAR impl certified **2016**) | "up to ASIL D" on paper, harder in practice — **ASIL-B shipping, ASIL-D underway** |

<div class="gloss">CP is <b>not CAN-only</b> — a standardized SOME/IP Transformer has shipped since <b>4.2.1 (Oct 2014)</b>, years before AP's first release · MMU = Memory Management Unit · PSE51 = minimal single-process POSIX profile · SOVD = Service-Oriented Vehicle Diagnostics</div>

<!-- ~75s | say: The split that matters, seven rows. Target — MCUs versus HPC SoCs. OS — AUTOSAR OS versus POSIX PSE51, and Adaptive is not a new OS. Model — fully static C versus dynamic C++. Comms — signals versus services. Diagnostics — DCM-plus-DEM versus one DM cluster, and note: DoIP is the only standardized transport, though a custom one is permitted. Updates — whole-ECU reflash versus per-cluster UCM. Safety — Classic mature up to ASIL D since 2016, Adaptive ASIL-B shipping with ASIL-D underway. And Classic is not CAN-only — it's had a SOME/IP transformer since 4.2.1, October 2014. -->

---

## Coexistence — AP plans, CP keeps the wheels

{{image:spec-ap-cp-interactions}}

A modern SDV runs **both platforms at once** — central HPCs on **AP** for the brain, zonal/actuator ECUs on **CP** for the reflex nervous system, **Ethernet + gateways** for the spine.

<div class="figsrc">Source: AUTOSAR AP_EXP_PlatformDesign, R25-11, Figure 3.2 — © AUTOSAR.</div>

<!-- ~70s | say: Coexistence, from the spec. A modern software-defined vehicle runs both at once: central HPCs on Adaptive for the brain, zonal and actuator ECUs on Classic for the reflexes, Ethernet and gateways for the spine. Adaptive plans and orchestrates; Classic keeps the wheels turning on the certified fail-safe path. -->

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

<div class="gloss">FSI = Functional Safety Island (dedicated lockstep silicon on DRIVE/IGX Thor) · AFW = the Vector-built AUTOSAR firmware NVIDIA ships for its companion MCUs · RFQ = request for quotation · examples only — the vendor cells repeat facts verified elsewhere, not an exhaustive market list</div>

<!-- ~85s | say: The whole deck in one procurement table — find your silicon row. A-core SoC: QNX or Linux plus an AP stack, or a non-AUTOSAR middleware, the Rivian path. The on-SoC safety island — lockstep Cortex-R52 — runs vendor safety firmware; Vector's explicit MICROSAR Classic up-to-ASIL-D reference targets the companion MCU, not the island. The companion and zonal MCUs run Classic. The rule underneath: value scales with the organizational boundaries your software crosses — integrated OEMs skip it, Tier-1s implement it to win RFQs. -->

---

## Fleet and diagnostics in one picture

<style scoped>
  img { display:block; margin: 4px auto 8px; max-height: 330px; width:auto; }
  li { margin-bottom: 4px; }
</style>

{{diagram:fleet-uds-flow}}

- **Outside the car**: the backend speaks **SOVD (REST/JSON over HTTPS)** + **MQTT telemetry** — **never raw UDS**; the vehicle's entry point is the **TCU**
- **Inside the car**: the **central gateway** (DoIP router + firewall) routes **DoIP/UDS** on the backbone and re-transports **DoIP → DoCAN** to CP branches — **raw UDS is never exposed to the internet**

<!-- ~75s | say: Fleet and diagnostics in one picture. Outside the car, the backend speaks SOVD — REST and JSON over HTTPS — plus MQTT telemetry, never raw UDS; the entry point is the TCU. Inside, the central gateway is a DoIP router plus firewall — it routes DoIP and UDS on the backbone and re-transports DoIP to DoCAN down to the Classic branches. Raw UDS is never exposed to the internet. -->

---

## The mid-2026 reality

- **Vendors ship AP today** — **Vector** MICROSAR Adaptive · **Elektrobit** EB corbos ·
  **ETAS RTA-VRTE** · **Qorix**; the POSIX OS underneath (QNX / Linux / PikeOS) is a **separate
  procurement + certification decision**
- **The ASIL hedge, exactly**: **ASIL-B shipping, ASIL-D programs underway** — no fully-certified
  end-to-end **ASIL-D** AP middleware ships as of mid-2026; **ASIL-D lives in the OS (QNX) +
  hypervisor + vendor safety case**
- **The open-source boundary**: education repos + production protocol/transport **building blocks**
  exist (vsomeip, iceoryx, Fast DDS) — but a **complete conformant open AP stack does not**. The
  one complete official implementation, **CAPI, is partner-gated — not open source**

<div class="gloss">ASIL = Automotive Safety Integrity Level (QM < A < B < C < D, ISO 26262) · CAPI = Common Adaptive Platform Implementation · a "developed to ASIL-x" process claim ≠ a "certified at ASIL-x" claim</div>

<!-- ~75s | say: The mid-2026 reality. Vendors ship Adaptive today — Vector, Elektrobit corbos, ETAS RTA-VRTE, Qorix — and the POSIX OS underneath is a separate procurement and certification decision. The honest safety hedge: ASIL-B shipping, ASIL-D programs underway — no fully-certified end-to-end ASIL-D AP middleware ships yet; ASIL-D lives in the OS, the hypervisor, and the vendor safety case. On open source: education repos and production transport building blocks exist, but a complete conformant open AP stack does not — the one complete official implementation, CAPI, is partner-gated, not open source. -->

---

## Three takeaways

1. **AUTOSAR is a supply-chain standard.** Its value scales with the organizational boundaries
   your software crosses — and **ASIL comes from ISO 26262, not from AUTOSAR**
2. **Two platforms, coexisting by design.** **CP = static + certified, on MCUs**;
   **AP = a service platform on POSIX, on HPCs** — a designed hierarchy, not legacy baggage
3. **Find your silicon row on the decision map** and you know the **stack**, the OS question,
   and **who sells it**

<!-- ~65s | say: Three takeaways. One: AUTOSAR is a supply-chain standard — and ASIL comes from ISO 26262, not from AUTOSAR. Two: two platforms, coexisting by design — Classic static and certified on MCUs, Adaptive a service platform on HPCs. Three: find your silicon row on the decision map and you know the stack, the OS question, and who sells it. -->

---

## Q&A — and where to dig deeper

- **The full 62-slide deck** — `autosar/slides/autosar-deck.md` — expands every point here with the
  primary-source references
- **The local spec mirror** — `autosar/specs/` (**35 R25-11 PDFs**, FO / CP / AP)
- **The research docs and blog** — under `autosar/` (Classic, Adaptive, Classic-vs-Adaptive)

<div class="gloss">Licensing: spec figures are reproduced <b>unmodified</b> (© AUTOSAR, R25-11); the adapted diagrams are <b>redrawn after the cited figures</b>, not copied from the spec artwork.</div>

<!-- ~35s | say: To go deeper — the full 62-slide deck expands every one of these, the local spec mirror has all 35 R25-11 PDFs, and the research docs and blog live under autosar/. On licensing: the spec figures are unmodified and copyright AUTOSAR R25-11; the adapted diagrams are redrawn after the cited figures. Questions? -->
