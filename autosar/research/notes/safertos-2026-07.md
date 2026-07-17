# SAFERTOS (WITTENSTEIN high integrity systems / WHIS) — Primary-Source Research

**Date:** 2026-07-16
**Analyst brief:** Verify SAFERTOS against primary sources for an embedded firmware engineer
comparing it to FreeRTOS and to the AUTOSAR world.
**Method:** Fetched WHIS (`highintegritysystems.com`) product/certification pages, WHIS
datasheets/brochure/white-paper PDFs, and `freertos.org` partner pages. Verbatim quotes below
are transcribed from those sources. Primary-source PDFs were downloaded and converted with
`pdftotext`; page URLs are in the Sources list. Anything not confirmed in a primary source is
tagged **[UNVERIFIED]**.

Vendor typography note: WHIS renders the mark as "SAFE**RTOS**®" (the "RTOS" is bolded). In
quotes below it is transcribed as "SAFERTOS". `freertos.org` uses the spelling "SafeRTOS".

---

## Q1. LINEAGE — exact current relationship to FreeRTOS + API compatibility

**Bottom line:** SAFERTOS is **not** a patched FreeRTOS. It is an **independently
re-engineered RTOS built to the FreeRTOS *functional model*** under a full IEC 61508 SIL 3
safety lifecycle. WHIS keeps three distinct products: **FreeRTOS** (open source, now AWS-
stewarded), **OPENRTOS** (the *same code base* as FreeRTOS, commercially licensed), and
**SAFERTOS** (re-designed, safety-certified). API/functional model is close to FreeRTOS —
same task/queue/semaphore model, same `xTask*`/`xQueue*` naming — with a documented
migration ("upgrade") path, but it is a separate codebase, not the FreeRTOS source.

Verbatim (WHIS brochure v8.6, 2024):
- "SAFERTOS® is a pre-emptive, pre-certified real time operating system... **Based on the
  FreeRTOS functional model, but specifically re-designed for the safety market by our own
  team of safety experts**, SAFERTOS® has been independently certified by TÜV SÜD to
  IEC 61508-3 SIL3 and ISO 26262-6 ASIL D."
- "WHIS leverage RTOS technology from FreeRTOS, the market leading embedded RTOS.
  **SAFERTOS® has a similar functional model to FreeRTOS, whereas OPENRTOS® is FreeRTOS,
  with a commercial license** that includes professional support and middleware integration."
- "OPENRTOS® provides a commercial license for the FreeRTOS kernel... **OPENRTOS® and the
  FreeRTOS kernel share the same code base**, however OPENRTOS® truly transitions
  developers into the professional world..." (contrast: OPENRTOS shares code; SAFERTOS does not)
- History: "Richard Barry created FreeRTOS in 2003 whilst working as Innovation Manager at
  WHIS. In 2017, Amazon Web Services (AWS) announced it had taken over stewardship of
  FreeRTOS... Simultaneously, WHIS and AWS announced they had formed a Strategic Business
  Alliance, enabling WHIS to continue to supply commercial and safety critical alternatives
  to FreeRTOS."
- Feature bullet: SAFERTOS "**Contains no open source code**". (i.e. clean-room re-implementation,
  not derived open-source files — relevant to safety/IP/supply-chain arguments)

Verbatim (WHIS SAFERTOS Datasheet / Technical Overview PDFs):
- "SAFERTOS was built as a complementary offering to FreeRTOS™, with common functionality but
  with a **uniquely designed safety critical implementation**."
- "The FreeRTOS functional model was subjected to a full HAZOP and all weaknesses within the
  functional model and API were identified and resolved. The resulting requirements set was
  put through a full IEC 61508 SIL3 development life cycle, the highest possible for a software
  only component."

Verbatim (WHIS S32K datasheet — the migration story):
- "The FreeRTOS kernel and SAFERTOS **share the same functional model, meaning that upgrading
  is easy.** Many of our customers prototype using the FreeRTOS kernel, and convert to
  SAFERTOS at the start of their formal development phase."
- "WHIS supply a manual that details how to upgrade from FreeRTOS to SAFERTOS in easy steps."
- The DAP contents list confirms this manual exists: "Upgrading from FreeRTOS to SAFERTOS
  Application Note: Highlights the areas requiring modification when moving an application from
  FreeRTOS to SAFERTOS." (So migration is documented but requires *some* modification — the
  APIs are not bit-identical; SAFERTOS adds stricter parameter checking and error-code returns.)

Verbatim (freertos.org — how the FreeRTOS project references SafeRTOS):
- "SafeRTOS is based on the functional model of the FreeRTOS kernel, however, **it is not the
  FreeRTOS kernel, having been completely re-designed** by a team of functional safety experts
  at WHIS." — from the freertos.org SafeRTOS DAP-deliverables page.
  **[PARTIAL VERIFICATION]** This sentence was returned by a freertos.org site-scoped search
  result; direct WebFetch of the freertos.org SafeRTOS pages repeatedly truncated before the
  body text, so the exact wording is high-confidence but was not re-confirmed by full-page
  fetch. The equivalent WHIS-authored statements above are fully verified.

**API model (from SAFERTOS Datasheet, primary):** same functional model as FreeRTOS — priority
pre-emptive scheduler with optional time-sliced round-robin for equal priority; "any number of
tasks"; queues (`xQueueSend`/`xQueueReceive`, copy-by-value, multi-sender/receiver); binary and
counting semaphores built on the queue primitive; mutexes; software timers; `xTaskSuspend()`/
`xTaskResume()`; `taskYIELD()`; `taskENTER_CRITICAL()`/`taskEXIT_CRITICAL()`; hook functions.
Key deltas vs FreeRTOS: **no dynamic allocation** ("SAFERTOS does not perform any dynamic memory
allocation operations, but instead requires the application to allocate a block of memory for
SAFERTOS during the initialisation sequence"); thorough API input-validity checking returning
error codes; run-time integrity checks (TCB mirror-copy checks, PSR check, tick-count check,
stack-space check before context save).

---

## Q2. CERTIFICATIONS as of 2026 — standards, levels, certifier, what is certified

**Bottom line:** Independently certified by **TÜV SÜD**. Pre-certified to **IEC 61508-3 SIL 3**
(since 2007 — WHIS claim it was "the world's first ever pre-certified RTOS") and
**ISO 26262 ASIL D** (parts -2, -6, -8). Assessed for **IEC 62304 Class C** (medical) and
supports **FDA 510(k) Class III** submissions. **DO-178C up to DAL A** for avionics is offered
as a compliance/lifecycle service (evidence produced through the SOI audit cycle), and **EN 50128**
(rail) evidence can be added to the DAP. "Available pre-certified" means WHIS ships a variant
already carrying a TÜV SÜD certificate; certification is **per processor/compiler combination**,
not a generic kernel certificate.

Verbatim (certifier + level, WHIS pages/brochure):
- "SAFERTOS® was initially certified in 2007 by TÜV SÜD to IEC 61508-3 SIL 3, the highest level
  possible for a software only component." (certification-and-standards page)
- "SAFERTOS® has been independently certified by TÜV SÜD to IEC 61508-3 SIL3 and
  ISO 26262-6 ASIL D." (brochure)
- Automotive page: "SAFERTOS® is available pre-certified to ISO 26262 -2,-6,-8 ASIL D by
  TÜV SÜD." / "ASIL D is the highest degree of automotive safety rating under this standard."
- Rail (brochure): "Pre-Certified to IEC 61508-3 SIL 3 by TÜV SÜD" and "for those companies
  that need to demonstrate compliance to the European Rail Standard EN 50128, WHIS can provide
  the additional information required integrated into the DAP."
- Medical (brochure): "Independently assessed by TÜV SÜD to IEC 62304 Class C"; "SAFERTOS®
  supports FDA 510(k) class III device submissions and IEC 62304 class C certifications";
  ships with a "Design History File" compliant with "21 CFR 820" and risk management per
  "ISO 14971:2009". Datasheet: "IEC 62304 Class C compliant".
- Aerospace (brochure): "The SAFERTOS® aerospace development life cycle fully complies with the
  requirements of DO 178C up to Design Assurance Level (DAL) A and supports the standard
  aerospace audit cycle." (delivered as source + verified binary library; PSAC/SOI 1-4 audits;
  MC/DC coverage). **Note:** DO-178C for DAL A is delivered as a project lifecycle/evidence
  engagement, not an off-the-shelf "pre-certified" badge like SIL 3 / ASIL D.

Verbatim (what exactly is certified — scope):
- "Each certification is specific to a processor/compiler combination, down to a specific
  version of the compiler and a specific compiler configuration." (certification-and-standards)
- "SAFERTOS is licensed as a SAFERTOS variant, where a variant is defined according to the
  developer's choice of micro-processor and tool chain... the API and the core SAFERTOS design
  and code is common between all SAFERTOS variants; the remaining port layer is adapted to
  support the selected micro-processor. Each SAFERTOS variant is subjected to the full
  IEC 61508 compliant development life cycle." (datasheet)
- The certified deliverable is the **Design Assurance Pack (DAP)**: "SAFERTOS is supplied with a
  Design Assurance Pack (DAP) which contains every design artefact produced during the full
  development life cycle, from development and safety life cycle plans, requirements
  specifications and design documents, to HAZOPS, the source code, all verification and
  validation documents and relating evidence." Medical variant ships a "Design History File"
  instead. DAP also contains an "Evidence Supporting IEC 61508-3 SIL3 Claim" (Claims-Argument-
  Evidence) and an "IEC 61508 Compliance Matrix".

**Certificate numbers: [UNVERIFIED]** — no TÜV SÜD certificate ID numbers were located in the
fetched pages/PDFs; WHIS states additional per-target TÜV SÜD certification "can be separately
purchased". The TÜV SÜD / Certipedia certificate database was not directly retrieved.

**"Contains no open source code": [PARTIAL]** — this claim appears in the WHIS brochure feature
list (verified there); it was not restated on the certification-and-standards page.

---

## Q3. POSIX — any PSE51 profile or POSIX compatibility layer?

**Answer: NO.** No POSIX or PSE51 layer is offered or mentioned in **any** primary source
examined. A full-text grep of every WHIS PDF (brochure, datasheet, technical overview) returned
**zero** occurrences of "POSIX" or "PSE5". The product/automotive/certification web pages do not
mention POSIX either. SAFERTOS exposes a **native FreeRTOS-style C API**, not a POSIX API.

The only standardized OS-API compatibility layer WHIS offers is an **OSEK OS adaptation layer**
(automotive), not POSIX:
- "SAFERTOS® can be supplied with an optional OSEK OS adaptation layer, supporting OSEK OS
  Conformance Classes BCC1, BCC2, ECC1 and ECC2. This allows SAFERTOS® to be used as a drop-in
  component within OSEK OS compliant systems."

(Verification is by absence across all fetched primary sources — a strong negative, but "absence
of evidence" caveat applies if WHIS offer a private/NDA POSIX layer not documented publicly:
**[UNVERIFIED negative]**, though none is advertised.)

---

## Q4. ARCHITECTURE CLASS — memory model, and could it host AUTOSAR Adaptive Platform?

**Bottom line:** SAFERTOS is a **single-image, statically-allocated microcontroller RTOS**:
all tasks live in **one build/address space**, with **optional per-task MPU regions** for
spatial separation. It is **MPU-based, not an MMU multi-process OS** — there is no per-process
virtual address space, no process model, no dynamic loading, no POSIX. Therefore it is the
architectural counterpart to **AUTOSAR Classic OS / OSEK** (MCU class), **not** to the AUTOSAR
**Adaptive Platform**.

**It cannot host AUTOSAR Adaptive Platform.** AP requires (a) a POSIX **PSE51** application
interface and (b) an **MMU-backed process model** with memory-isolated OS processes (an AP
"Machine" runs on a POSIX-conformant OS such as Linux or QNX). SAFERTOS provides neither: no
POSIX (Q3) and no MMU process model (below). This is my analytical conclusion from the primary
sources, not a WHIS statement — **[ANALYSIS]**, but the underlying facts are verified.

Verbatim (memory model, SAFERTOS Datasheet — primary):
- "SAFERTOS does not perform any dynamic memory allocation operations, but instead requires the
  application to allocate a block of memory for SAFERTOS during the initialisation sequence."
- "The Memory Protection Unit (MPU) allows software of different Safety Integrity Levels (SIL) to
  co-exist in a **single build of code** without unwanted mutual interference."
- "SAFERTOS supports the definition and manipulation of MPU regions on a **per task basis**,
  where each task is assigned to specific memory regions." / "The MPU implementation is tightly
  coupled to the selected processor core... The actual number of memory regions... is processor
  dependent." (This is MPU region protection within one image — not virtual-memory process
  isolation.)
- "SAFERTOS has been specifically designed for the **32 bit micro-controller market**. No
  allowances or compromises have been incorporated to support other platforms."

Verbatim (brochure): "MMU/MPU support as standard." — SAFERTOS can *drive* an MMU where the
silicon has one (e.g. Cortex-A / -R with MMU), but it uses it as a protection unit for the same
per-task spatial-separation model; there is no evidence of a POSIX/virtual-memory process OS.
Multicore support is **AMP** (Asymmetric Multi-Processing): "SAFERTOS® empowers engineers
working with multicore devices to swiftly and efficiently create integrated safety-critical
designs using an Asymmetric Multi-Processing (AMP) architecture." (Not an SMP process OS.)

**Does WHIS make any AUTOSAR claim / partnership?** No AUTOSAR *compatibility* or *partnership*
claim was found. SAFERTOS is explicitly positioned as the **non-AUTOSAR** / alternative path:
- Automotive page: "Automotive teams often turn to WHIS when **AUTOSAR does not fully align with
  their architectural or functional goals.**"
- NXP + WHIS joint white paper ("Real-Time Drivers and SAFERTOS"): "**SAFERTOS® and the NXP
  S32K/G processor families are well suited for non-AUTOSAR automotive applications** due to
  their high performance and safety credentials." (In that paper AUTOSAR is served by NXP's
  AUTOSAR MCAL/RTD drivers; SAFERTOS is the non-AUTOSAR RTOS option — the two are presented as
  parallel, not integrated.)
- The **OSEK OS adaptation layer** is the closest AUTOSAR-adjacent feature. Caveat: **OSEK OS is
  the historical ancestor of AUTOSAR Classic OS, but they are not the same** — AUTOSAR OS is a
  superset of OSEK OS (adds schedule tables, timing protection, OS-Applications, etc.). WHIS
  claim **OSEK OS conformance classes (BCC1/BCC2/ECC1/ECC2)**, *not* AUTOSAR OS conformance.
  No claim that SAFERTOS is an AUTOSAR Classic OS is made.

---

## Q5. POSITIONING, public design-ins, and how it is licensed/sold

**Positioning:** WHIS is "first and foremost a safety systems company." SAFERTOS targets
safety-certified microcontroller applications across **automotive, aerospace, medical,
industrial, and rail**. Its pitch vs FreeRTOS: prototype free on FreeRTOS, then convert to
SAFERTOS (same functional model) for the certified build. Its pitch vs AUTOSAR: a lean,
fast-boot, small-footprint, ASIL-D RTOS for teams that don't need / don't want the full AUTOSAR
stack (safety islands, zone/BMS controllers, non-AUTOSAR ECUs).

**Public design-ins / uses (from WHIS marketing lists — verified as WHIS *claims*, not
independently confirmed customer names — treat named end-customers as [UNVERIFIED]):**
- Silicon-vendor partner listings (verified these vendors publish SAFERTOS partner pages):
  **Renesas (RA Cortex-M)**, **STMicroelectronics**, **Texas Instruments** (`WHIS-3P-SAFERTOS`;
  TI's Hercules safety MCUs historically ship SafeRTOS), **NXP (S32K1/S32K3, S32G)**, and **Arm**
  (partner catalog). Tool support: PLS UDE, Lauterbach TRACE32, Percepio Tracealyzer, VectorCAST.
- Automotive application areas (WHIS brochure): "Zone controller safety islands; Battery
  management systems; Digital cockpits; Engine control units; Radar/vision systems; Cameras and
  sensors; Network hubs; Advance driver assist systems; Autonomous drive systems."
- Medical devices (WHIS brochure): infusion pumps, dialysis machines, insulin pumps, surgical
  robots, defibrillators, ventricular assist devices, etc.
- WHIS marketing claim: "WHIS customers have a 100% success rate in certifying SAFERTOS for
  their applications." **[UNVERIFIED marketing claim]**
- **RISC-V:** WHIS announced SAFERTOS support for the RISC-V ISA (news release). **[PARTIAL]**
  seen as a search/news result; not deep-fetched.

**Licensing / how it is sold (verified, WHIS primary):**
- "SAFERTOS is royalty free, with flexible licensing models." (datasheet)
- "Our standard licensing model uses a **royalty free, perpetual license** with an unlimited
  number of production units. We have three standard levels of licensing- **Product, Multi
  Product and Corporate**." (brochure)
- Sold **per SAFERTOS variant** = chosen microprocessor + toolchain; delivered as **full source
  code + the DAP** (or Design History File for medical), tailored to that processor/compiler,
  "removing the need for retesting on the target hardware." Typically includes "the kernel,
  processor/compiler combination, certification artefacts, and support for the first year."
- Add-ons: **SAFERTOS CORE** (same source/API, commercial-grade port, no certification pack —
  for "systems that need to consider safety but don't require certification"); **Enhanced
  Security Module (ESM)** designed to comply with **ISO 21434**; safety plugins
  (SAFECheckpoints runtime monitor, SAFEXchange, SAFECRC); OSEK OS adaptation layer; middleware
  (TCP/IP, etc.). Company QMS: **ISO 9001:2015**, certified by **LRQA (Lloyd's Register)**.

---

## Cross-comparison cheat-sheet (for the FreeRTOS/AUTOSAR-oriented reader)

| Dimension | FreeRTOS | SAFERTOS | AUTOSAR Classic OS | AUTOSAR Adaptive |
|---|---|---|---|---|
| Code origin | Open source (AWS) | Clean re-implementation of the FreeRTOS *functional model* | OSEK-derived spec, many vendors | POSIX PSE51 + MMU, Linux/QNX-class |
| API | FreeRTOS C API | ~FreeRTOS C API (stricter, migration note) | OSEK/AUTOSAR OS API | C++ ara::* + POSIX PSE51 |
| Memory model | Single image, MPU variant | Single image, static alloc, per-task MPU (drives MMU as MPU) | Single image, MPU/OS-Applications | MMU multi-process, virtual memory |
| Cert | none (evidence via SafeRTOS) | TÜV SÜD SIL3 / ASIL D / 62304-C / DO-178C DAL A | ASIL up to D (vendor) | ASIL (vendor) |
| POSIX | no | **no** (OSEK OS layer only) | no | **yes (PSE51)** |
| Can host AUTOSAR AP? | no | **no** | n/a | is AP |

---

## Sources (every URL used)

WHIS (highintegritysystems.com) — primary vendor:
- https://www.highintegritysystems.com/safertos/  (product page — fetched)
- https://www.highintegritysystems.com/safertos/certification-and-standards/  (fetched)
- https://www.highintegritysystems.com/rtos/safety-critical-rtos/embedded-rtos-for-automotive/  (fetched)
- https://www.highintegritysystems.com/wp-content/uploads/2024/05/brochure_v8.6.pdf  (v8.6, 2024 — downloaded + pdftotext)
- https://www.highintegritysystems.com/downloads/manuals_and_datasheets/SafeRTOS_Datasheet.pdf  (downloaded + pdftotext)
- https://www.highintegritysystems.com/downloads/manuals_and_datasheets/SafeRTOS_Technical_Overview.pdf  (downloaded + pdftotext)
- https://www.highintegritysystems.com/downloads/manuals_and_datasheets/S32K_SAFERTOS_Datasheet_v1.1.pdf  (downloaded + pdftotext)
- https://www.highintegritysystems.com/downloads/white_papers/nxp_real_time_drivers_and_safertos.pdf  (downloaded + pdftotext)
- https://www.highintegritysystems.com/safertos/rtos-features/  (search-indexed)
- https://www.highintegritysystems.com/safertos/supported-platforms/  (search-indexed)

FreeRTOS project (freertos.org) — how the FreeRTOS side references SafeRTOS:
- https://www.freertos.org/Partners/Software/SafeRTOS-and-OpenRTOS  (fetch truncated; used site-scoped search result)
- https://www.freertos.org/FreeRTOS-Plus/Safety_Critical_Certified/SafeRTOS-Design-Assurance-Pack-Deliverables.html  (source of "not the FreeRTOS kernel, completely re-designed" quote; fetch truncated)
- https://www.freertos.org/Partners/Software/SafeRTOS  (fetch truncated)

Silicon-vendor / ecosystem partner pages (corroborate design-ins, not deep-fetched):
- https://www.renesas.com/en/products/microcontrollers-microprocessors/ra-cortex-m-mcus/ra-partners/safertos-wittenstein-high-integrity-systems
- https://www.st.com/en/partner-products-and-services/wittenstein-safertos.html
- https://www.ti.com/tool/WHIS-3P-SAFERTOS
- https://www.arm.com/partners/catalog/wittenstein-high-integrity-systems
- https://www.wittenstein-group.com/en-us/products/software-and-digitalization/safety-critical-operating-system

TÜV SÜD certificate database (NOT retrieved — certificate numbers unverified):
- https://www.certipedia.com/  (TÜV Rheinland DB; TÜV SÜD SAFERTOS cert IDs not located)

---

## Verification status summary
- **VERIFIED (primary WHIS + corroborating):** lineage (re-engineered to FreeRTOS functional
  model, separate codebase, migration path), no-POSIX, MPU/single-image architecture,
  cannot-host-AP conclusion, non-AUTOSAR positioning, OSEK OS layer, TÜV SÜD SIL3/ASIL D/62304-C
  /DO-178C-DAL-A/EN50128, per-processor/compiler cert scope, royalty-free perpetual licensing,
  DAP delivery.
- **PARTIAL:** exact freertos.org wording (search-indexed, full-page fetch truncated);
  RISC-V support (news-indexed).
- **UNVERIFIED:** specific TÜV SÜD certificate numbers; named end-customer design-ins;
  "100% certification success" marketing claim; existence of any non-public POSIX layer (none
  advertised).
