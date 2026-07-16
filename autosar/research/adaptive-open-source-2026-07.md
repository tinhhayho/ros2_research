# Open-source Adaptive AUTOSAR — an honest landscape (July 2026)

**What this is.** A single synthesized reference on *what a team can and cannot get openly* for the
AUTOSAR Adaptive Platform (AP), written for embedded/firmware engineers who wanted to **see the real
shape of AP code** from public repositories. It merges three research notes under
`autosar/research/notes/` — `ap-oss-implementations.md` (the community `ara::*` codebases and the
official CAPI), `ap-oss-building-blocks.md` (production protocol/IPC components under commercial AP),
and `ap-oss-ecosystem.md` (the Eclipse/consortium layer around AP and the honest boundary). Every
load-bearing fact was verified against a primary source (GitHub API, `raw.githubusercontent.com`,
project pages, autosar.org) on **2026-07-16**; nothing is asserted beyond what those notes verified,
and anything without a primary source is parked in **Open questions**.

The one-line orientation for the whole document: **openly today a team CAN assemble education, the
production protocol/transport layer, and the SDV middleware that surrounds AP — it CANNOT get a
conformant, complete, production-grade open AP stack.** The only complete official AP implementation
is AUTOSAR's own **CAPI**, which is partner-gated; commercial stacks (Vector, Elektrobit, ETAS,
Apex.AI, Qorix) are proprietary; and Eclipse S-CORE is explicitly *not* an AP implementation.

---

## Key claims

| Claim | Status | Source |
|---|---|---|
| `langroodi/Adaptive-AUTOSAR` — MIT, C++14, 489★; the broadest readable AP teaching codebase, 7 `ara::` clusters (com, exec, diag, phm, sm, core, log) + runnable simulated demo; self-describes per cluster against R20-11 – R22-11 (R21-11 most-cited; R22-11 only for `com`'s E2E Profile 11 and `phm`) | verified | https://github.com/langroodi/Adaptive-AUTOSAR |
| langroodi is **dormant** — last *source* commit 2023-06-22 (later commits README/CONTRIBUTING only); not archived | verified | https://api.github.com/repos/langroodi/Adaptive-AUTOSAR/commits?path=src |
| langroodi exposes **SOME/IP-transport-level** APIs and has **no generated `ara::com` Proxy/Skeleton facade** (no `src/ara/com/proxy` or `skeleton` dir) | verified (from `src/` tree) | https://github.com/langroodi/Adaptive-AUTOSAR |
| `ZiadAhmed9/ara-rs` — Apache-2.0 OR MIT, Rust; `ProxyBase`/`SkeletonBase` + SOME/IP transport + `cargo-arxml` ARXML codegen + worked examples; created 2026-03-30, solo author, 6★ | verified (promise, not track record) | https://github.com/ZiadAhmed9/ara-rs |
| Graveyard: `insooth/autosar-adaptive` = 64 spec PDFs + 17 spec ZIP archives (88 files total) + one `ara::per` header (33★ mislead); `LoyenWang/AUTOSAR-Adaptive` = 14 submodules → deleted org (HTTP 404); several near-empty shells | verified | https://github.com/insooth/autosar-adaptive · https://github.com/LoyenWang/AUTOSAR-Adaptive |
| AUTOSAR **CAPI** (Common Adaptive Platform Implementation) — official, code-first, quarterly, certification-ready wording; **partner-gated, NOT open source** (`code.autosar.org/capi/capi` → 302 sign-in) | verified | https://www.autosar.org/capi |
| **vsomeip** (COVESA, BMW-originated) — MPL-2.0, release 3.7.4 (2026-07-06), actively maintained; standalone SOME/IP + SD + E2E = the standardized network binding under `ara::com`, not an `ara::com` API; repo never mentions `ara::com`, though AUTOSAR appears around its E2E support (changelog "Support AutoSAR E2E Profile 4", E2E test docs citing the AUTOSAR E2E/CRC specs, two source files citing AUTOSAR FO R22-11) | verified | https://github.com/COVESA/vsomeip |
| **Eclipse iceoryx** — Apache-2.0, v2.0.8 (2026-05-19); ships `iceoryx-automotive-soa` = *"a Binding for automotive frameworks like AUTOSAR Adaptive ara::com"*; its "Where is iceoryx used" table labels RTA-VRTE (ETAS) and AVIN AGNOSAR as AUTOSAR Adaptive Platform products, while Apex.Ida is listed as safe/certified middleware without the AP label | verified (do not use stale 2019 "fully compatible" line) | https://github.com/eclipse-iceoryx/iceoryx |
| **Eclipse iceoryx2** — Rust core, Apache-2.0 OR MIT, v0.9.3 (2026-07-08), very active, pre-1.0; README/FAQ describe safety-critical ambitions ("designed to operate in safety-critical systems") but make **no** AUTOSAR/ISO 26262/ASIL certification claim | verified | https://github.com/eclipse-iceoryx/iceoryx2 |
| **eProsima Fast DDS** — Apache-2.0, v3.6.2 (2026-07-02); DDS is one of the three standardized `ara::com` network bindings (SOME/IP · Signal-Based · DDS) so it is technically eligible — but not documented as the AP Demonstrator binding (that reference work is RTI Connext, proprietary) | verified / gap called out | https://github.com/eProsima/Fast-DDS |
| **CommonAPI C++ / -SomeIP** (COVESA) — MPL-2.0; Franca-IDL proxy/stub codegen whose shape rhymes with `ara::com`, separate non-AUTOSAR lineage; dormant since 2024-10-09 | verified | https://github.com/COVESA/capicxx-core-runtime |
| **Eclipse S-CORE** — Apache-2.0, dual-language C++/Rust (never Rust-first), launched 2025-06-12, releases v0.1.0 → v0.6.2 (2026-07-14); backers BMW, Mercedes-Benz, Bosch, ETAS, QNX, Qorix, Accenture; **not an AP implementation**, makes no AP-compatibility claim (no official statement either way; eclipse-score GitHub discussions #759, #882 exist but nothing official) | verified | https://github.com/eclipse-score |
| S-CORE comms module **LoLa** — *"a communication middleware implementation based on the Adaptive AUTOSAR Communication Management specification"*, *"Partial implementation of … (ara::com)"*, README self-describes ASIL-B qualified; API namespace `score::mw::com`, **not `ara::com`**; IPC on boost.interprocess, **not iceoryx** | verified | https://github.com/eclipse-score/communication |
| **Eclipse OpenSOVD** — Apache-2.0, mostly Rust, Eclipse Incubating (proposed 2025-05-26), active into July 2026; open implementation of **SOVD (ISO 17978)**; bridges AUTOSAR-Adaptive HPCs and legacy UDS ECUs; complements S-CORE | verified | https://github.com/eclipse-opensovd/opensovd-core |
| Boundary items (Apache-2.0, active, none are AP): Eclipse Ankaios (workload orchestration, overlaps AP EM), Eclipse Kuksa (VSS databroker, Rust), Eclipse uProtocol (transport-agnostic messaging; GM-originated, pairs with COVESA VSS/uServices) | verified | https://github.com/eclipse-ankaios/ankaios · https://github.com/eclipse-kuksa/kuksa-databroker · https://github.com/eclipse-uprotocol/up-spec |
| Classic contrast: Classic AUTOSAR has an open **GPL-2.0** lineage (Arctic Core → `openAUTOSAR/classic-platform`, 2453 commits); Adaptive has **no** equivalent open conformant stack | verified | https://github.com/openAUTOSAR/classic-platform |
| The concrete AUTOSAR↔Eclipse tie is the **SDV Alliance** (AUTOSAR + COVESA + Eclipse SDV + SOAFEE, formed March 2023, launched CES 2024); the autosar.org "Opening Strategy" page is dated 2022-05-05 | verified | https://www.autosar.org/news-events/detail/collaboration-the-key-to-making-the-software-defined-vehicle-a-reality |

---

## Implementations — the `ara::*` codebases

`langroodi/Adaptive-AUTOSAR` is the one genuinely broad, readable AP teaching codebase: an
explicitly *educational Linux simulator* that implements real code across seven `ara::` clusters,
ships runnable platform daemons (execution/state/health/diagnostic managers) plus an
`extended_vehicle` demo, and has a `test/` tree with mock network layers. Two caveats must stay
attached wherever it appears: it is **dormant** (last source commit 2023-06-22; everything after is
documentation-only), and it exposes a **SOME/IP-transport-level** API surface with **no generated
`ara::com` Proxy/Skeleton facade** — apps drive `Subscribe(...)`/`OfferService`-style calls at the
SOME/IP layer. It follows AP naming and semantics (`ara::core::Result<void>`, `InstanceSpecifier`,
`ReportExecutionState`) but is hand-written, not ARXML-generated, and makes no conformance claim.
The load-bearing C++ snippet for the deck is `ExecutionClient::ReportExecutionState`
(`src/ara/exec/execution_client.h` L54-L58) — the canonical Adaptive-Application → Execution-Management
handshake, returning `ara::core::Result<void>` rather than throwing.

`ZiadAhmed9/ara-rs` is a real, coherent Rust attempt — not vapor — that mirrors the canonical
`ara::com` **ProxyBase/SkeletonBase** shape in idiomatic async Rust, ships a `cargo-arxml` generator,
a SOME/IP transport crate, and worked `battery-service`/`diagnostics-service` examples. But it was
created 2026-03-30 by a solo author with 6★, and its breadth (15 planned sprints, Yocto, benchmarks)
far outruns its age. Present it as **promise, not track record.** The deck's Rust snippet is
`SkeletonBase::offer` (`ara-com/src/skeleton.rs` L46-L60) — the `OfferService`/`StopOfferService`
lifecycle as async Rust delegating to a SOME/IP transport.

Everything else is a graveyard or a near-empty shell: `insooth/autosar-adaptive` is 64 AUTOSAR
19-03 spec PDFs + 17 spec ZIP archives (88 files total) plus exactly one implementation header (its 33★ are legacy/misleading);
`LoyenWang/AUTOSAR-Adaptive` is dead scaffolding whose 14 submodules point at the
`UmlautSoftwareDevelopmentAccount` org, which now returns HTTP 404; and `Chaos0929`, `tianxingyang`,
`TreeNeeBee`, `cflaviu` (2019) are early skeletons or single-cluster fragments. The **official**
route — AUTOSAR's **CAPI** — is code-first, automotive-grade, quarterly, and described as
certification-ready, but its git (`code.autosar.org/capi/capi`) redirects to a GitLab `users/sign_in`
login: it is *"developed collaboratively by and for AUTOSAR partners,"* i.e. **partner-gated, not
open source.** There is no public download of official AP reference code.

## Building blocks — the protocol layer you can ship

Beneath any commercial AP stack sits a production open-source protocol/transport layer that *is*
freely available. **vsomeip** (COVESA, MPL-2.0, release 3.7.4 on 2026-07-06) is the de-facto
open-source **SOME/IP + Service Discovery + E2E** stack — the standardized *network binding* under
`ara::com`, onto which a commercial AP maps proxy/skeleton calls; the repo itself never mentions
`ara::com`, though AUTOSAR appears around its E2E support (changelog "Support AutoSAR E2E Profile 4",
E2E test docs citing the AUTOSAR E2E/CRC specs, two source files citing AUTOSAR FO R22-11).
**Eclipse iceoryx** (Apache-2.0, v2.0.8) is the zero-copy shared-memory IPC AP
stacks name explicitly; the only permitted 2026 wording is its README's `iceoryx-automotive-soa` line
— *"a Binding for automotive frameworks like AUTOSAR Adaptive ara::com"* — whose "Where is iceoryx used"
table labels RTA-VRTE (ETAS) and AVIN AGNOSAR as AUTOSAR Adaptive Platform products, while Apex.Ida is
listed as safe/certified middleware without the AP label (never the stale 2019 "fully compatible with ara::com" phrase).
**iceoryx2** (Rust core, Apache-2.0 OR MIT, v0.9.3, very active but pre-1.0) is the successor whose
README/FAQ describe safety-critical ambitions ("designed to operate in safety-critical systems") but make
no AUTOSAR/ISO 26262/ASIL certification claim.
**eProsima Fast DDS** (Apache-2.0, v3.6.2) implements the OMG DDS/RTPS that one of AP's three standardized
bindings (SOME/IP · Signal-Based · DDS) is defined against, so it is technically eligible — but no primary source names it as the AP
Demonstrator's binding (the documented reference work is RTI's proprietary Connext). **CommonAPI
C++/-SomeIP** (COVESA, MPL-2.0) generates Franca-IDL proxy/stub classes whose shape rhymes with
`ara::com` proxies/skeletons, but it is a separate non-AUTOSAR lineage and has been dormant since
2024-10-09. Net: **the protocol/transport layer of AP is fully available as production OSS; the
`ara::` API layer is not.**

## Ecosystem and boundary — where the line sits

Around AP sits a live Eclipse/consortium layer that is open but is **not** AP. **Eclipse S-CORE**
(Apache-2.0, dual-language C++/Rust, launched 2025-06-12, backed by BMW, Mercedes-Benz, Bosch, ETAS,
QNX, Qorix, Accenture) is an open SDV core stack that makes no AP-compatibility claim (no official
statement either way; eclipse-score GitHub discussions #759, #882 exist but nothing official); its comms
module **LoLa** self-describes as a *partial* implementation of Adaptive AUTOSAR Communication
Management (ara::com) and as ASIL-B qualified in its README, yet its API namespace is `score::mw::com`
(not `ara::com`) and its IPC is built on boost.interprocess (not iceoryx). **Eclipse OpenSOVD**
(Apache-2.0, mostly Rust, Incubating) is the most direct open connection to the deck's existing fleet
diagnostics slides: an open implementation of SOVD (ISO 17978) that bridges AUTOSAR-Adaptive HPCs and
legacy UDS ECUs. **Eclipse Ankaios**, **Eclipse Kuksa**, and **Eclipse uProtocol** are all
Apache-2.0, active SDV middleware in AP's neighbourhood but are not AP. Finally, the honest boundary:
Classic AUTOSAR had a GPL-2.0 open lineage (Arctic Core → openAUTOSAR/classic-platform); Adaptive has
no equivalent open conformant stack, and the one complete official AP implementation (CAPI) is
partner-gated — which is what keeps the "no complete open AP stack" line honest even though AUTOSAR
now ships AP code.

---

## Open questions

- **Fast DDS as an AP DDS binding.** DDS is a standardized `ara::com` binding and Fast DDS fully
  implements OMG DDS/RTPS, but no primary source integrates it as the *official AP Demonstrator's*
  DDS binding; the documented reference work is RTI Connext (proprietary). Treat "Fast DDS = the AP
  Demonstrator binding" as **unverified**.
- **AP Demonstrator vs CAPI.** The older member-only AP *Demonstrator*'s exact current distribution
  status was not re-verified; AUTOSAR's current "code implementation of AP" initiative is CAPI
  (partner-gated, quarterly). No public open-source official AP reference implementation exists.
- **LoLa's "ASIL-B qualified" claim.** This is a README self-description, attributed to the README —
  not a certificate this research verified.
- **S-CORE ↔ AUTOSAR relationship.** S-CORE's own materials contain no AUTOSAR mention; the only
  concrete tie is the SDV Alliance (vision/architecture alignment), not an AP-compatibility layer or
  a stated AUTOSAR liaison.
- **The VDA MoU signatory count** behind S-CORE (reported growing from 11 toward ~32 companies) is
  reported, not primary-verified here.
- **Whether the 2022 opening-strategy "university/startup" non-partner license launched**, and its
  terms — status unverified; the Opening Strategy page is dated 2022-05-05 and is intent, not a
  2025/26 open-source release.

---

## Sources (all fetched 2026-07-16)

1. https://github.com/langroodi/Adaptive-AUTOSAR — Adaptive Runtime AUTOSAR Linux Simulator (MIT, C++, 7 clusters) — GitHub — primary
2. https://api.github.com/repos/langroodi/Adaptive-AUTOSAR/commits?path=src — last source commit 2023-06-22 — GitHub API — primary
3. https://github.com/ZiadAhmed9/ara-rs — Rust AP toolkit (Apache-2.0 OR MIT, proxy/skeleton, cargo-arxml) — GitHub — primary
4. https://github.com/insooth/autosar-adaptive — 64 spec PDFs + 17 spec ZIP archives (88 files total) + one `ara::per` header (33★) — GitHub — primary
5. https://github.com/LoyenWang/AUTOSAR-Adaptive — scaffolding, 14 submodules → deleted org — GitHub — primary
6. https://www.autosar.org/capi — CAPI (code-first, quarterly, partner-gated) — AUTOSAR — primary
7. https://code.autosar.org/capi/capi — redirects to `users/sign_in` (GitLab login; partner-gated) — AUTOSAR — primary
8. https://github.com/COVESA/vsomeip — SOME/IP stack (MPL-2.0, 3.7.4) — COVESA — primary
9. https://github.com/COVESA/capicxx-core-runtime — CommonAPI core runtime (MPL-2.0, dormant) — COVESA — primary
10. https://github.com/eclipse-iceoryx/iceoryx — zero-copy IPC (Apache-2.0, v2.0.8) + `iceoryx-automotive-soa` README line — Eclipse — primary
11. https://github.com/eclipse-iceoryx/iceoryx2 — Rust-core zero-copy IPC (Apache-2.0 OR MIT, v0.9.3, no AUTOSAR/ASIL claim) — Eclipse — primary
12. https://github.com/eProsima/Fast-DDS — OMG DDS/RTPS (Apache-2.0, v3.6.2) — eProsima — primary
13. https://github.com/eclipse-score — S-CORE org (Apache-2.0, dual C++/Rust, releases to v0.6.2) — Eclipse — primary
14. https://github.com/eclipse-score/communication — LoLa (partial ara::com, `score::mw::com`, boost.interprocess) — Eclipse — primary
15. https://github.com/eclipse-opensovd/opensovd-core — OpenSOVD (Apache-2.0, SOVD/ISO 17978, bridges AP HPC ↔ UDS) — Eclipse — primary
16. https://github.com/eclipse-ankaios/ankaios — workload orchestration for automotive HPCs (Apache-2.0) — Eclipse — primary
17. https://github.com/eclipse-kuksa/kuksa-databroker — VSS databroker (Apache-2.0, Rust) — Eclipse — primary
18. https://github.com/eclipse-uprotocol/up-spec — transport-agnostic messaging (Apache-2.0) — Eclipse — primary
19. https://github.com/openAUTOSAR/classic-platform — open Classic fork (GPL-2.0, Arctic Core lineage, 2453 commits) — GitHub — primary
20. https://www.autosar.org/news-events/detail/collaboration-the-key-to-making-the-software-defined-vehicle-a-reality — SDV Alliance (CES 2024) — AUTOSAR — primary
21. https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open — S-CORE launch (2025-06-12) — Eclipse — primary
22. https://www.rti.com/blog/integrating-dds-into-the-autosar-adaptive-platform — RTI's reference DDS binding (context for Fast DDS gap) — RTI — vendor/secondary

*Synthesized 2026-07-16 from `autosar/research/notes/ap-oss-implementations.md`,
`ap-oss-building-blocks.md`, and `ap-oss-ecosystem.md`; no new web research beyond re-fetching the
snippet permalinks and link-checking the reference URLs.*
