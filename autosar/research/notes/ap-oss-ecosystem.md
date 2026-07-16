# Adaptive AUTOSAR — Open-Source Ecosystem / Consortium Layer

> **Corrections (fact-check 2026-07-16, wf_ecadf716-210):** (5) S-CORE **makes no AP-compatibility claim** — no official statement either way; community discussions about a compatibility/mapping layer exist (eclipse-score GitHub discussions #759, #882) but nothing official — rather than "states no AP-compatibility layer". (10) uProtocol is **Eclipse uProtocol** (originated from a GM contribution; pairs closely with COVESA VSS/uServices), not "Eclipse/COVESA uProtocol".

Scope of this scout: what the automotive industry is doing *in the open around* Adaptive
AUTOSAR (AP), and the honest boundaries. Not the educational AP implementations themselves
(sibling scouts cover those). Every claim below was fetched and verified on 2026-07-16.

---

## Key findings

1. **Eclipse S-CORE is real, active, and NOT an AP implementation.** It is the Eclipse "Safe
   Open Vehicle Core" — an Apache-2.0, dual-language **C++/Rust** open-source *core stack for
   SDVs* that "sits between the operating system and application layer, delivering core,
   non-differentiating services." Its own materials (project page, docs site, June-2025 launch
   announcement, Sept-2025 explainer) **do not mention AUTOSAR at all** — there is **no stated
   AP-compatibility layer and no AUTOSAR liaison** in S-CORE's own documentation. The launch
   was announced **2025-06-12** (Creation Review 2025-04-04). It ships real code: releases from
   v0.1.0 (2025-05-22) through **v0.6.2 (2026-07-14)**, ~76 repos, ~412–427 contributors.

2. **Eclipse OpenSOVD is real and directly connects to the deck's SOVD fleet slides.** It is an
   Apache-2.0, mostly-Rust "open source implementation of the Service-Oriented Vehicle
   Diagnostics (SOVD) standard, as defined in ISO 17978," in **Incubating** state (proposed
   2025-05-26), backed by an 11-committer team. It explicitly **bridges "modern HPCs (e.g.,
   AUTOSAR Adaptive) and legacy ECUs (e.g., UDS-based systems)"** and "complements and
   integrates the Eclipse S-CORE project." Actively developed (pushes July 2026).

3. **AUTOSAR's "opening strategy" page the deck references is dated 2022, not 2025-26.** The
   autosar.org "AUTOSAR Opening Strategy – Software Defined Vehicle Ecosystem" article is dated
   **05.05.2022**. It introduces a "Vehicle API" standard, opening SOME/IP and DLT, and a
   possible extra license for universities/startups. Do **not** present it as a fresh 2025/26
   statement.

4. **The concrete 2023-onward AUTOSAR↔Eclipse relationship is the SDV Alliance**, a cross-
   consortium "collaboration of collaborations" (AUTOSAR + COVESA + Eclipse SDV + SOAFEE),
   formed March 2023 and launched at CES 2024. It aligns SDV *vision/architecture*; it does
   **not** make S-CORE an AP implementation.

5. **AUTOSAR now delivers its own AP source code — but it is partner-gated, not open source.**
   The **CAPI (Common Adaptive Platform Implementation)** is AUTOSAR's "code-first" initiative
   giving partners "a certification-ready code implementation of the AUTOSAR Adaptive Platform,"
   with quarterly releases — "**Developed collaboratively by and for AUTOSAR partners.**" No
   public git URL is discoverable; it is inside the AUTOSAR partnership. This is the single most
   important nuance for the "what you cannot get openly" line.

6. **Honest summary line for the deck.** Openly today a team CAN get: educational/hobby AP
   implementations (sibling scouts); AP protocol/building-block code (SOME/IP, DLT, and SOVD via
   Eclipse OpenSOVD); and SDV middleware that surrounds AP (Eclipse S-CORE core stack, Eclipse
   Ankaios orchestration, Eclipse Kuksa VSS databroker, Eclipse uProtocol) — all Apache-2.0.
   What a team CANNOT get openly: **a conformant, complete, production-grade open AP stack.**
   The only *complete/harmonized/certification-ready* AP implementation is AUTOSAR's own CAPI,
   which is partner-only; commercial AP stacks (Vector, Elektrobit, ETAS, Apex.AI, Qorix, …) are
   proprietary; and Eclipse S-CORE is explicitly *not* an AP implementation and claims no AP
   compatibility. **Classic AUTOSAR had GPL-licensed open forks (Arctic Core / ArcCore →
   openAUTOSAR); Adaptive has no equivalent open, conformant stack.**

---

## Eclipse S-CORE (Safe Open Vehicle Core)

**What it is.** Open-source core software stack for Software-Defined Vehicles, targeting
embedded high-performance ECUs. Official project-page scope (verbatim):
> "The Eclipse Safe Open Vehicle Core project aims to develop an open-source core stack for
> Software Defined Vehicles (SDVs), specifically targeting embedded high-performance Electronic
> Control Units (ECUs)."

Launch announcement (Eclipse newsroom, dated **Thursday, June 12, 2025**), verbatim:
> "the first open source core software stack specifically designed for Software-Defined Vehicles
> (SDVs)" … "S-CORE sits between the operating system and application layer, delivering core,
> non-differentiating services" (application orchestration, IPC, logging, data persistence).

September-2025 Eclipse explainer, verbatim:
> "a safety-compliant, service-oriented software platform for high-performance ECUs, developed
> collaboratively under the Eclipse Foundation." … "Instead of duplicating similar work across
> companies, the automotive industry could develop a shared open source platform that is free to
> use, shaped by a broad community, and available to all."

**License.** Apache-2.0 across the org's repositories (a few vendored libs carry their own
licenses, e.g. `nlohmann_json` = MIT). Confirmed on the GitHub org repo listing.

**Dual-language C++/Rust (pinned fact confirmed).** The org's repos are a genuine mix: C++
(`lifecycle`, `baselibs`, `time`, `inc_someip_gateway`, `inc_security_crypto`) and Rust
(`persistency`, `inc_diagnostics`). The template repo is literally named:
> `module_template` — "C++ & Rust Bazel Template Repository"

Never call S-CORE "Rust-first"; it is deliberately dual-language.

**Activity.** Creation Review 2025-04-04; progress reviews "Eclipse Safe Open Vehicle Core
2025.12" (2025-12-10) and "2026.12" (2026-12-16 planned). GitHub releases (primary source,
eclipse-score/score): v0.1.0 (2025-05-22, prerelease) → v0.4.1 (2025-11-11) → **v0.5.0
(2025-12-10)** → **v0.6.2 (2026-07-14, latest)**. ~76 repos in the org; metrics.eclipse.org
reports ~427 contributors and ~23.7k commits over the trailing 12 months. A full/production
release is targeted for 2026, aimed at vehicle programs reaching market by ~2030.

**Contributing companies (verified from the launch announcement).** BMW Group, Mercedes-Benz,
Bosch, ETAS, QNX, Qorix, Accenture. (The broader VDA "Automotive-Grade Open Source Software
Ecosystem" MoU that underpins S-CORE grew from 11 signatories at June-2025 launch toward ~32
companies per Eclipse/press reporting — treat the exact "32" as reported, not primary-verified
here.)

**Relationship to the AP standard.** *By omission.* S-CORE's project page, docs site
(`eclipse-score.github.io`, 0 AUTOSAR mentions), launch announcement, and Sept-2025 explainer
contain **no reference to AUTOSAR or the Adaptive Platform**. There is **no official
AP-compatibility layer and no AUTOSAR liaison stated** by S-CORE itself. The connection to AP is
only indirect: (a) the SDV Alliance (below), and (b) shared protocols — S-CORE has an incubating
SOME/IP gateway (`inc_someip_gateway`), and its sister project OpenSOVD explicitly bridges
AUTOSAR-Adaptive HPCs. Bottom line for the deck: **S-CORE is an independent open SDV core stack,
not an AP implementation, and it does not claim AP conformance.**

---

## Eclipse OpenSOVD

**What it is.** Open implementation of SOVD (Service-Oriented Vehicle Diagnostics). Official
project-page scope (verbatim):
> "Eclipse OpenSOVD provides an open source implementation of the Service-Oriented Vehicle
> Diagnostics (SOVD) standard, as defined in ISO 17978."

Components (project page): a **SOVD Gateway** (REST/HTTP endpoints for diagnostics, logging,
software updates), **Protocol Adapters** — verbatim "bridging modern HPCs (e.g., AUTOSAR
Adaptive) and legacy ECUs (e.g., UDS-based systems)" — and a **Diagnostic Manager**. Relation to
S-CORE (verbatim):
> "Eclipse OpenSOVD complements and integrates the Eclipse S-CORE project by providing an open
> implementation of the SOVD protocol that can be used for diagnostics and service orchestration
> within the S-CORE environment."

**License.** Apache-2.0 (all active code repos).

**Backers / committers.** Creation Review lists **11 initial committers** (Thilo Schmitt,
Florian Roks, Elena Gantner, Alexander Mohr, Mark Schmitt, Frank Scholter Peres, Branimir
Djordjevic, Ramachandran Chakravadhanula, Ulrich Renner, Sanimir Agovic, Tim Kliefoth, Venkat
Sundar); **company affiliations are not stated in the creation-review document.** Proposal dated
2025-05-26; review period ended 2025-07-16.

**State / activity.** Project state **Incubating**. Multi-repo, **Rust-dominant**: `opensovd-core`
(server/client/gateway, Rust), `classic-diagnostic-adapter` (Rust), `uds2sovd-proxy` (Rust),
`fault-lib` (Rust), `dlt-tracing-lib` (Rust), plus `odx-converter` (Kotlin) and `cpp-bindings`
(C++). Active: pushes into July 2026 (e.g., `classic-diagnostic-adapter` and `mdd-ui` pushed
2026-07-15).

**How it relates to the AP standard.** SOVD is the *next-gen diagnostics* protocol that AP-class
HPCs expose (REST/HTTP over service-oriented architectures) alongside/above legacy UDS. OpenSOVD
is therefore an **open building block adjacent to AP**, not an AP stack. It is the most direct
open connection point for the deck's existing SOVD fleet slides.

**Load-bearing code (SOVD REST API shape).** `opensovd-server/src/routes/mod.rs` documents the
SOVD-compliant endpoint tree — the resource model (`components` → `data-categories` /
`data-groups` / `data` → read/write) that any SOVD client/HPC speaks:

```rust
//! HTTP route handlers for the SOVD API.
//!
//! This module provides all SOVD-compliant REST endpoints:
//!
//! ## Discovery
//! - GET / - Query capabilities of the root entity
//! - GET /components - List all components
//! - GET /components/{component_id} - Query capabilities of a component
//!
//! ## Data
//! - GET /components/{component_id}/data-categories - List data categories
//! - GET /components/{component_id}/data-groups - List data groups
//! - GET /components/{component_id}/data - List data resources
//! - GET /components/{component_id}/data/{data_id} - Read a data value
//! - PUT /components/{component_id}/data/{data_id} - Write a data value
```
Permalink (commit pinned):
https://github.com/eclipse-opensovd/opensovd-core/blob/fe75a8e3a9142d11a0ed7152610e29003493de2a/opensovd-server/src/routes/mod.rs#L4-L18
(same file also declares `const SOVD_VERSION: &str = "1.1";` and builds an `axum::Router`.)

---

## AUTOSAR and open source, officially

### 3a. The 2022 "Opening Strategy" page (the one the deck cites)
Page: autosar.org → News & Events → "AUTOSAR Opening Strategy – Software Defined Vehicle
Ecosystem", dated **05.05.2022**. Verbatim, load-bearing sentences:
> "AUTOSAR decided to introduce a new standard called 'Vehicle API' to simplify to interact with
> AUTOSAR in the vehicle for the world outside AUTOSAR, i.e. connecting the IoT world. This
> standard will be developed in a new framework, which will also be open to non-AUTOSAR
> Partners."
> "The next step is to clarify the opening protocols on network level, such as SOME/IP for
> service-oriented communication and Dlt (Diagnostics, Log and Trace), to support the
> development of compatible applications beyond AUTOSAR."
> "Furthermore, the introduction of an additional license is under consideration, which would
> allow the use of AUTOSAR specifications and implementations for non-AUTOSAR partners, e.g.
> universities and startups, before actual industrialization or without intention of commercial
> exploitation."

Caveat for the deck: this is **2022**. It is a statement of intent (Vehicle API, opening
protocols, a possible academic license), not a 2025/26 open-source release.

### 3b. SDV Alliance (the concrete cross-consortium collaboration)
Page: autosar.org → "Collaboration, The Key to Making the Software Defined Vehicle a Reality",
dated **09.01.2024** (CES 2024, Las Vegas). Verbatim:
> "In March 2023, AUTOSAR, COVESA, Eclipse SDV, and SOAFEE realized that a collaboration was
> needed - not just within the consortia, but between them. This has culminated in the SDV
> Alliance, a 'collaboration of collaborations' to help clarify the contributions each consortium
> brings to SDV and then actively work together to demonstrate their interconnectedness and
> synergy."

AUTOSAR chairperson quote on the same page:
> "AUTOSAR with more than 360 partners worldwide has been a reliable organization in the last 20
> years. … we look forward to enable a smooth transition together with other organizations to the
> Software Defined Vehicle of the future based on existing AUTOSAR technologies and newly, joint
> developed, technologies with our partner organizations." — Chairperson of AUTOSAR.

This is the official AUTOSAR↔Eclipse-SDV touchpoint. It is about *alignment/vision*, not about
AUTOSAR open-sourcing AP.

### 3c. CAPI — Common Adaptive Platform Implementation (partner-gated AP code)
Page: autosar.org/capi. This is AUTOSAR's own code delivery of AP. Verbatim tagline:
> "Accelerate SDV development with an automotive-grade, certification-ready code implementation of
> the AUTOSAR Adaptive Platform."

Verbatim body:
> "The AUTOSAR Common Adaptive Platform Implementation (CAPI) is a strategic, code-first
> initiative by the global AUTOSAR community to provide a standardized, automotive-grade
> implementation of the AUTOSAR Adaptive Platform standard. … Developed collaboratively by and
> for AUTOSAR partners, it creates a common foundation that eliminates redundant development of
> non-differentiating middleware components across the industry."
> "CAPI enforces AUTOSAR specifications through code-first advantages and quarterly releases of
> automotive-grade code."
> "CAPI is the harmonized implementation of the AUTOSAR Adaptive Platform standard, ensuring
> seamless interoperability between software components from different suppliers."
> "This is not a replacement for the AUTOSAR Adaptive Platform standard, but its natural evolution
> – combining the stability of consensus-driven standards with the velocity of modern software
> development."

**Distribution status (critical):** CAPI is **for AUTOSAR partners**, "by and for AUTOSAR
partners," released quarterly. The page's "CAPI Git" link resolves inside the AUTOSAR partnership
(no public git URL is discoverable). Treat CAPI as **the closest thing to a complete/conformant
AP implementation — but partner-gated, NOT open source.** This is what makes the "no complete
open AP stack" boundary honest even though AUTOSAR now ships AP code.

---

## Boundary items (SDV middleware often confused with AP, but not AP)

- **Eclipse Kuksa** — `eclipse-kuksa/kuksa-databroker`, **Apache-2.0**, Rust. "A modern in-vehicle
  VSS (Vehicle Signal Specification) server written in RUST." Active (pushed 2026-07-08). VSS data
  broker, not an AP stack.
- **Eclipse Ankaios** — `eclipse-ankaios/ankaios`, **Apache-2.0**, Rust. "provides workload and
  container orchestration for embedded devices like automotive HPCs." Active (pushed 2026-07-15).
  Workload orchestrator (a SOAFEE-style layer), not AP; overlaps conceptually with AP Execution
  Management but is a different thing.
- **COVESA / Eclipse uProtocol** — `eclipse-uprotocol/up-spec`, **Apache-2.0**. "uProtocol is a
  communication protocol that enables software applications (uEntities) to easily communicate …
  run on top of any other communication middleware (transport) such as SOME/IP, MQTT, zenoh,
  HTTP, etc." Now under the Eclipse `eclipse-uprotocol` org (commonly associated with COVESA, where
  it originated). A transport-agnostic messaging layer, not AP.

All three are Apache-2.0 SDV middleware in the same *neighborhood* as AP but are not AP
implementations and are not AP-conformant.

---

## Classic-side contrast (one safe line)

Open-source **Classic** AUTOSAR forks exist and are GPL-licensed; open **Adaptive** has no
equivalent conformant stack.

- `openAUTOSAR/classic-platform` — "Open source AUTOSAR classic platform forked from the Arctic
  Core", **GPL-2.0**, 2,453 commits (older / effectively legacy).
- `inniyah/arccore` — "Arctic Core - the open source AUTOSAR embedded platform" (Arctic Core /
  ArcCore lineage; historically dual-licensed **GPL-2.0 + commercial** ArcCore license).

Safe deck sentence: *"Classic AUTOSAR had GPL-licensed open forks (Arctic Core / ArcCore,
continued as openAUTOSAR); Adaptive has no equivalent open, conformant stack — only educational
implementations, protocol building blocks, and AUTOSAR's own partner-gated CAPI."*

---

## What a team CAN vs CANNOT get openly (the honest boundary)

**CAN (Apache-2.0 / GPL, public):**
- Educational/hobby AP implementations on GitHub (sibling scouts cover the specific repos).
- AP protocol / building-block code: SOME/IP + DLT (opened per AUTOSAR's 2022 strategy) and SOVD
  via **Eclipse OpenSOVD**.
- SDV middleware surrounding AP: **Eclipse S-CORE** (core stack), **Eclipse Ankaios**
  (orchestration), **Eclipse Kuksa** (VSS databroker), **Eclipse/COVESA uProtocol** (messaging).
- Classic AUTOSAR GPL forks (Arctic Core / openAUTOSAR) — for the Classic contrast only.

**CANNOT (not openly available):**
- A conformant, complete, production-grade **open** AP stack. It does not exist in public open
  source.
- AUTOSAR's own complete AP code = **CAPI**, but that is **partner-gated** ("by and for AUTOSAR
  partners"), not open source.
- Commercial AP stacks (Vector, Elektrobit/EB, ETAS, Apex.AI, Qorix, …) are proprietary.
- Note: **Eclipse S-CORE is NOT an AP implementation** and makes **no AP-compatibility claim**; do
  not present it as "open Adaptive AUTOSAR."

---

## Notes on pinned facts / cautions honored
- S-CORE stated as dual-language **C++/Rust**, **Apache-2.0**, launched **2025-06-12** — all
  re-verified above.
- **iceoryx**: not independently re-verified in this pass. The historical "iceoryx is fully
  compatible with ara::com" line is **stale 2019 marketing** and is deliberately NOT repeated
  here. If the deck mentions iceoryx as an AP zero-copy IPC building block, that specific
  compatibility claim must be re-verified before use.
- AUTOSAR AP Demonstrator distribution status: not the subject of this scout. CAPI (partner-gated,
  quarterly code releases) appears to be AUTOSAR's current "code implementation of AP" initiative;
  the exact status of the older AP *Demonstrator* is left to the sibling scout / must be verified,
  not assumed.

---

## Sources (all fetched 2026-07-16)

**Eclipse S-CORE**
- https://projects.eclipse.org/projects/automotive.score
- https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open
- https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together
- https://metrics.eclipse.org/projects/automotive.score/
- https://github.com/eclipse-score  (org repo listing, incl. `module_template` = "C++ & Rust Bazel Template Repository")
- https://api.github.com/repos/eclipse-score/score/releases  (release tags/dates)
- https://eclipse.dev/score/  (landing; no AUTOSAR mention)
- https://eclipse-score.github.io/  (docs; 0 AUTOSAR mentions)

**Eclipse OpenSOVD**
- https://projects.eclipse.org/projects/automotive.opensovd
- https://projects.eclipse.org/projects/automotive.opensovd/reviews/creation-review
- https://github.com/eclipse-opensovd  (org repo listing)
- https://raw.githubusercontent.com/eclipse-opensovd/opensovd-core/fe75a8e3a9142d11a0ed7152610e29003493de2a/opensovd-server/src/routes/mod.rs
- https://github.com/eclipse-opensovd/opensovd-core/blob/fe75a8e3a9142d11a0ed7152610e29003493de2a/opensovd-server/src/routes/mod.rs#L4-L18

**AUTOSAR (curl -ksL workaround; broken TLS chain in sandbox)**
- https://www.autosar.org/news-events/detail/autosar-opening-strategy-software-defined-vehicle-ecosystem  (dated 05.05.2022)
- https://www.autosar.org/news-events/detail/collaboration-the-key-to-making-the-software-defined-vehicle-a-reality  (dated 09.01.2024, SDV Alliance)
- https://www.autosar.org/capi  and  https://www.autosar.org/capi/aoc  (CAPI)
- https://www.autosar.org/news-events/detail/sdv-forum-x-1  (SDV Forum X, 09–11.09.2026, networking event)

**Boundary + Classic**
- https://github.com/eclipse-kuksa/kuksa-databroker  (Apache-2.0)
- https://github.com/eclipse-ankaios/ankaios  (Apache-2.0)
- https://github.com/eclipse-uprotocol/up-spec  (Apache-2.0)
- https://github.com/openAUTOSAR/classic-platform  (GPL-2.0, forked from Arctic Core)
- https://github.com/inniyah/arccore  (Arctic Core / ArcCore lineage)
</content>
</invoke>
