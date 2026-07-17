# The roll-your-own SDV fleet toolbox — open source *without* AUTOSAR (July 2026)

**Researcher C.** What a team assembles to connect a fleet — telemetry, OTA, orchestration,
signal model, in-vehicle messaging, diagnostics — when it deliberately does **not** use the
AUTOSAR Adaptive Platform's built-in clusters (UCM, DM/SOVD, `ara::com`). Every external fact below
was verified against a primary source (GitHub REST API, `projects.eclipse.org` API,
`raw.githubusercontent.com`, official docs) on **2026-07-17**. AUTOSAR-counterpart claims that were
already fact-checked in the repo are cited `repo:…`; everything else carries a fresh URL. Reputable
press is labeled `binding:"press"`.

---

## The one-paragraph orientation

There is a **complete, production-grade open-source shelf** for fleet connectivity that owes nothing
to AUTOSAR — and much of it is *more* mature than the open AUTOSAR-AP story (which has no complete
open conformant stack). The shelf splits cleanly by job: **cloud telemetry** (AWS IoT FleetWise +
its Apache-2.0 edge agent), **signal model** (COVESA VSS + the VISS access protocol),
**in-vehicle messaging/SOA** (Eclipse uProtocol over Zenoh/SOME/IP, plus the Kuksa VSS databroker),
**orchestration** (Eclipse Ankaios — the one that reached 1.0/"Regular"), and **OTA** (a two-layer
stack: Uptane for *trust*, hawkBit for *rollout back-end*, and RAUC / SWUpdate / Mender for the
*device-side apply*). The single biggest honesty caveat is on the cloud tile: **AWS quietly closed
IoT FleetWise to new customers in 2026**, so the reference "cloud telemetry" product is itself in
run-off even as its edge agent stays open. The AUTOSAR mapping is asymmetric: AP has direct
counterparts for messaging (`ara::com`), orchestration (Execution Management) and OTA
delivery (UCM/V-UCM), but **nothing for cloud telemetry** and **no standalone OTA-security framework**
like Uptane.

---

## The "roll-your-own shelf" table

| Project | Fleet job | What it does (1 line) | Governance | License | Latest / activity (2026) | Closest AUTOSAR counterpart |
|---|---|---|---|---|---|---|
| **AWS IoT FleetWise** (service) | cloud telemetry | Managed cloud service: collect, decode (raw→human-readable), VSS-model & campaign vehicle data | AWS (proprietary service) | proprietary | **Closed to new customers (2026)** | **none** (AUTOSAR stops at the vehicle) `repo:` |
| **aws-iot-fleetwise-edge** ("FWE") | telemetry (edge agent) | C++ on-vehicle agent: decodes CAN/OBD-II/SOME/IP, uploads via MQTT to IoT Core | AWS (GitHub) | Apache-2.0 | v1.3.5, 2026-06-02; active | none |
| **COVESA VSS** | signal model | Standardized tree/taxonomy naming vehicle signals (`Vehicle.Speed`…), transport-agnostic | COVESA | MPL-2.0 | **v6.0**, 2026-01-16 | ARXML data model (partial) |
| **COVESA VISS / VISSR** | telemetry / signal access | Protocol+reference server to read/write VSS data (WebSocket/HTTP/MQTT/gRPC) | COVESA (ex-W3C) | MPL-2.0 | **VISS v3.0 RC**; VISSR active | SOVD (external read API, loose) |
| **Eclipse uProtocol** | in-vehicle SOA / messaging | Transport-agnostic pub/sub+RPC layer that *maps onto* Zenoh/SOME/IP/MQTT/Binder | Eclipse SDV (GM lineage) | Apache-2.0 | Incubating; active | **`ara::com`** `repo:` |
| **Eclipse Zenoh** | messaging transport | Unified pub/sub + query + storage, MCU→cloud; uProtocol's primary in-vehicle transport | Eclipse (ZettaScale) | EPL-2.0 OR Apache-2.0 | 1.9.0, 2026-04-10; very active | SOME/IP / DDS binding under `ara::com` |
| **Eclipse Kuksa** (databroker) | signal model runtime | In-vehicle VSS server: apps read/write current signal values over gRPC | Eclipse SDV (Bosch origin) | Apache-2.0 | 0.7.0, 2026-07-03; active | (none direct) |
| **Eclipse Velocitas** | app framework | Toolchain/SDKs (Py/C++) + CLI to build & containerize "Vehicle Apps" on VSS/Kuksa | Eclipse SDV | Apache-2.0 | Incubating; **cooling** (last SDK 2025-07) | (AP app dev tooling) |
| **Eclipse Leda** | reference integration | Yocto/Poky reference distro + meta-layer gluing SDV components into bootable images | Eclipse SDV | Apache-2.0 | Incubating; low activity | (none) |
| **Eclipse Ankaios** | orchestration | Lightweight workload/container orchestrator for automotive HPCs (K8s-lite, Rust, Podman) | Eclipse SDV (Elektrobit) | Apache-2.0 | **1.0 GA / "Regular"**; very active | **AP Execution Management** `repo:` |
| **Uptane** | OTA (security) | Compromise-resilient OTA *trust framework* (Director+Image repos, role separation) | Linux Foundation JDF | open standard | **Standard v2.1.0** | none (UCM signs, but no Uptane equivalent) |
| **aktualizr / OSTree** | OTA (client/delivery) | Uptane C++ client + atomic "git-for-rootfs" delivery (Torizon/AGL) | HERE/CoreOS lineage | MPL-2.0 / LGPL | maintenance / stable | UCM install engine |
| **Eclipse hawkBit** | OTA (rollout back-end) | Server that manages artifacts, targets & staged rollouts via a device DDI API | Eclipse IoT (Bosch) | EPL-2.0 | **1.0/1.1.0**, 2026-07; active | **V-UCM** (campaign coordinator) `repo:` |
| **RAUC** | OTA (device apply) | A/B slot updater for embedded Linux: signed bundles, atomic switch, rollback | Pengutronix | LGPL-2.1 | v1.15.2, 2026-03; very active | **UCM** (per-machine) `repo:` |
| **SWUpdate** | OTA (device apply) | Flexible single-image updater (Lua handlers, hawkBit client) for embedded Linux | Stefano Babic / DENX | GPL-2.0 | 2026.05.1, 2026-06; very active | UCM |
| **Mender** | OTA (device apply + server) | End-to-end A/B updater, dual OSS+commercial | Northern.tech | Apache-2.0 | 5.1.0, 2026-05; very active | UCM / V-UCM |

---

## 1 — Cloud telemetry: AWS IoT FleetWise (+ the OSS edge agent)

**AWS IoT FleetWise** is a managed AWS service that collects vehicle data, transforms low-level bus
messages into human-readable values, standardizes them in the cloud, and lets you define
"collection campaigns" controlling what to collect and when to upload — vehicles send data via
**MQTT** to AWS IoT Core, landing in Timestream/S3.
[AWS docs](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/what-is-iotfleetwise.html)

- **VSS relation.** FleetWise models signals in the cloud with **COVESA VSS**: the *signal catalog*
  follows VSS and signals are imported as VSS-formatted JSON.
  [signal-catalog docs](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/signal-catalogs.html)
- **The big caveat (slide-worthy).** The service is being wound down for new customers. The official
  docs now open with, verbatim: *"AWS IoT FleetWise is no longer open to new customers. Existing AWS
  IoT FleetWise customers can continue using the service."* AWS points new builds to the
  "Guidance for Connected Mobility on AWS" blueprint instead.
  [AWS docs](https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/what-is-iotfleetwise.html)
  (Press widely reports the new-customer cutoff as **April 30, 2026**; treat the date as press,
  the quote as primary.)
- **The edge agent** — `github.com/aws/aws-iot-fleetwise-edge` ("FWE") — is the open part and stays
  open: **C++** libraries + a sample app, **Apache-2.0**, created 2022, **v1.3.5 (2026-06-02)**,
  repo pushed 2026-07-01, 76★. It decodes **CAN / OBD-II / SOME/IP** on-vehicle (its build deps list
  the AWS SDK for C++ **plus COVESA CommonAPI C++ Core + SOME/IP runtime**), then uploads.
  [repo](https://github.com/aws/aws-iot-fleetwise-edge) ·
  [API metadata](https://api.github.com/repos/aws/aws-iot-fleetwise-edge)
- **AUTOSAR counterpart: none.** AUTOSAR's scope ends at the vehicle boundary — there is **no
  AUTOSAR cluster for cloud telemetry**. `repo:autosar/slides/autosar-deck.md`

---

## 2 — Signal model: COVESA VSS + VISS/VISSR

- **VSS (Vehicle Signal Specification).** A standardized, hierarchical **domain model / naming
  taxonomy** for vehicle signals (`Vehicle.Speed`, `Vehicle.Cabin.Door.Row1…`) — a *catalog*, not a
  protocol, deliberately transport-agnostic. Governance **COVESA**, **MPL-2.0**, 431★, current
  release **v6.0 (2026-01-16)**, actively maintained.
  [repo](https://github.com/COVESA/vehicle_signal_specification) ·
  [API](https://api.github.com/repos/COVESA/vehicle_signal_specification/releases/latest)
  It is the *de-facto* SDV signal vocabulary: AWS IoT FleetWise and Eclipse Kuksa both build on it.
- **VISS (Vehicle Information Service Specification).** The **access protocol/API** on top of VSS:
  JSON messages over WebSocket (VISSv1), +HTTP/MQTT (VISSv2), +**gRPC/compression/file-transfer
  (VISSv3)**. Governance **migrated from W3C to COVESA in 2024** (the W3C Automotive Working Group
  closed Feb 2024); **VISS v3.0 Release Candidate** is out for review, **VISSv2** remains the
  W3C-published version. **VISSR** is COVESA's Go reference server (MPL-2.0, active 2026-07).
  [COVESA VISS v3.0 RC](https://covesa.global/covesa-viss-version-3-0-release-candidate/) ·
  [W3C VISSv2](https://www.w3.org/TR/viss2-core/) ·
  [VISSR repo](https://github.com/COVESA/vissr)
- **AUTOSAR counterpart:** no single equivalent open signal catalog; the loose analog for the
  *external read API* is SOVD (ISO 17978). VSS is orthogonal to ARXML's data-type model.

---

## 3 — In-vehicle messaging / SOA: uProtocol, Zenoh, Kuksa (+ Velocitas, Leda)

- **Eclipse uProtocol.** A **transport-agnostic, layered messaging/SOA protocol** (uEntities +
  UUri addressing, pub/sub **and** RPC) whose whole design point is to **map onto existing
  transports** rather than replace them. **GM lineage** — the initial spec derived from GM's internal
  "Blue Dragon" 1.3.7 release. Eclipse SDV, **Apache-2.0**, `up-spec` 43★, active (pushed 2026-07-15),
  **Incubating**.
  - **Yes, it has both a Zenoh and a SOME/IP transport.** Out-of-the-box transports are
    **Eclipse Zenoh** (chosen as the *primary in-vehicle* transport; `up-transport-zenoh-rust`),
    **SOME/IP**, **MQTT 5**, and **Android/Binder**.
    [uProtocol](https://uprotocol.org/) · [org](https://github.com/eclipse-uprotocol) ·
    [up-transport-zenoh-rust](https://github.com/eclipse-uprotocol/up-transport-zenoh-rust) ·
    [eclipse state](https://projects.eclipse.org/api/projects/automotive.uprotocol)
  - **AUTOSAR counterpart: `ara::com`** (in-vehicle SOA). `repo:autosar/research/adaptive-open-source-2026-07.md`
- **Eclipse Zenoh.** Unified **pub/sub + geo-distributed query + storage** protocol spanning
  microcontrollers to cloud; also ships a ROS 2 RMW. Eclipse Foundation (ZettaScale/ADLINK origin),
  **dual EPL-2.0 OR Apache-2.0**, **2,988★** (by far the most-starred here), **1.9.0 (2026-04-10)**,
  extremely active, **Incubating** (`iot.zenoh`). Automotive relevance: uProtocol's default
  in-vehicle transport; positioned by ZettaScale for SDV.
  [repo](https://github.com/eclipse-zenoh/zenoh) ·
  [license (README/Cargo)](https://raw.githubusercontent.com/eclipse-zenoh/zenoh/main/README.md) ·
  [eclipse state](https://projects.eclipse.org/api/projects/iot.zenoh)
- **Eclipse Kuksa (`kuksa-databroker`).** An **in-vehicle VSS server / databroker** in **Rust**: a
  central point where "provider" and "consumer" apps read/write current VSS signal values over gRPC.
  Eclipse SDV (Bosch origin), **Apache-2.0**, 70★, **0.7.0 (2026-07-03)**, active, **Incubating**.
  Pairs directly with COVESA VSS.
  [repo](https://github.com/eclipse-kuksa/kuksa-databroker) ·
  [eclipse state](https://projects.eclipse.org/api/projects/automotive.kuksa)
- **Eclipse Velocitas.** A **development toolchain/framework** (Python + C++ SDKs, a CLI, dev
  containers) for building and **containerizing "Vehicle Apps"** that consume VSS via Kuksa.
  Eclipse SDV, **Apache-2.0**, **Incubating** — but **cooling**: the Python SDK's last commit is
  **2025-07-03** and the most recent org activity is Jan 2026 (C++ template); low stars. Present as
  *incubating, adoption-thin*.
  [org repos](https://api.github.com/orgs/eclipse-velocitas/repos) ·
  [eclipse state](https://projects.eclipse.org/api/projects/automotive.velocitas)
- **Eclipse Leda.** A **Yocto/Poky-based reference distro + `meta-leda` layer** that integrates the
  Eclipse SDV pieces (Kuksa, Ankaios, container runtimes) into bootable **quickstart/showcase**
  images — explicitly a dev/test/showcase reference, not a production OS. Eclipse SDV, **Apache-2.0**,
  22★, **Incubating**, **still alive but low activity** (docs repo pushed 2026-03-08).
  [repo](https://github.com/eclipse-leda/leda) ·
  [eclipse state](https://projects.eclipse.org/api/projects/automotive.leda)

---

## 4 — Orchestration: Eclipse Ankaios

**The most mature Eclipse SDV project in this set.** Ankaios is a **lightweight workload + container
orchestrator for automotive HPCs** — think "Kubernetes-lite for the car": written from scratch in
**Rust**, Podman-first (other runtimes and native apps supported), one unified API across physical
or virtual nodes. Eclipse SDV, **Elektrobit-originated/donated**, **Apache-2.0**, **123★**, very
active (pushed 2026-07-16). It **reached 1.0.0 GA** (latest **v1.0.1, 2026-05-19**) and its Eclipse
lifecycle state is **"Regular"** — i.e. graduated past incubation, unlike every other SDV project
here.
[repo](https://github.com/eclipse-ankaios/ankaios) ·
[1.0.0 announcement](https://eclipsesdv.org/news/eclipse-ankaios-1-0-0-released/) ·
[Elektrobit blog](https://www.elektrobit.com/blog/managing-automotive-hpc-software-complexity-with-eclipse-ankaios/) ·
[eclipse state](https://projects.eclipse.org/api/projects/automotive.ankaios)

- **AUTOSAR counterpart: AP Execution Management (EM).** The repo deck already frames Ankaios as
  "conceptually overlaps AP Execution Management." `repo:autosar/slides/autosar-deck.md`

---

## 5 — OTA without UCM: a two-layer stack (security → back-end → device agent)

OTA is where the AUTOSAR-vs-OSS split is clearest. AP's answer is **UCM** (per-machine installer) +
**V-UCM** (vehicle-wide campaign coordinator). The OSS answer is a **stack of specialized layers**:

**(a) Security framework — Uptane.** Not an updater; a **compromise-resilient OTA *trust*
framework** built from an explicit automotive threat model: separate **Director** and **Image**
repositories, strict role/key separation, so a single server or key compromise cannot push a
malicious image. Self-described as *"the first software update security system for the automotive
industry capable of resisting even attacks by nation-state level actors."* Governance:
**Linux Foundation Joint Development Foundation (JDF)**, Uptane Series; current **Uptane Standard
v2.1.0**.
[uptane.org](https://uptane.org/)
- **Adopters (named, citable):** built into **Automotive Grade Linux** (via **aktualizr**);
  **HERE OTA Connect** (formerly ATS Garage — first European third-party supplier to adopt Uptane);
  **Airbiquity OTAmatic**; **Toradex Torizon** (an "Uptane-as-a-service" implementation, first to
  support PURE-2 offline updates). Uptane states adoption by "several major automakers … millions of
  vehicles."
  [Uptane adoptions](https://uptane.org/learn-more/adoptions)
- **AUTOSAR counterpart: none.** UCM/V-UCM sign and authenticate Vehicle Packages, but AUTOSAR has
  no standalone Uptane-style trust framework; Uptane can even sit *under* an AP OTA flow.

**(b) Delivery/client — aktualizr / OSTree.** **aktualizr** is the C++ Uptane client (HERE/ATS
lineage); **OSTree** is atomic "git-for-the-rootfs" delivery. Toradex Torizon combines OSTree +
Uptane (aktualizr-lite). Largely stable/maintenance now.
[Torizon OTA](https://www.torizon.io/security)

**(c) Rollout back-end — Eclipse hawkBit.** A **server-side update-management back-end**: manages
artifacts, targets and **staged/canary rollouts**, exposing a device-facing **DDI API**. Domain-
independent (IoT + automotive). Eclipse IoT, **Bosch-originated (2015)**, **Java**, **EPL-2.0**,
585★, reached its **first production-ready 1.0** and now **1.1.0 (2026-07-03)**. Adopters:
**Bosch IoT Rollouts** and **Kynetics Update Factory** are commercial products built on hawkBit.
[repo](https://github.com/eclipse-hawkbit/hawkbit) ·
[hawkBit 1.0](https://www.eenewseurope.com/en/eclipse-hawkbit-1-0-released-for-open-source-iot-software-updates/)
- **AUTOSAR counterpart: V-UCM** (the vehicle-wide campaign coordinator role). `repo:autosar/slides/autosar-deck.md`

**(d) Device-side apply — RAUC / SWUpdate / Mender** (pick one; all mature):
- **RAUC** — A/B **slot-based** updater for embedded Linux (signed bundles, atomic switch, rollback,
  bootloader integration). **Pengutronix**, **C**, **LGPL-2.1**, **1,207★**, v1.15.2 (2026-03-27).
  Named production users: **Valve Steam Deck / SteamOS** (RAUC + casync); press also cites IKEA
  Dirigera, Home Assistant OS, Deutsche Bahn Linux4ICE.
  [repo](https://github.com/rauc/rauc) ·
  [SteamOS uses RAUC (Collabora)](https://www.collabora.com/news-and-blog/news-and-events/steamos-3-6-how-the-steam-deck-atomic-updates-are-improving.html)
- **SWUpdate** — flexible **single-image** updater (Lua handlers, many storage backends, native
  hawkBit client). **Stefano Babic / DENX**, **C**, **GPL-2.0**, **1,834★**, 2026.05.1 (2026-06-22).
  [repo](https://github.com/sbabic/swupdate)
- **Mender** — **end-to-end** A/B updater (client **and** server), dual open-source + commercial.
  **Northern.tech**, **C++** client, **Apache-2.0**, **1,207★**, 5.1.0 (2026-05-12).
  [repo](https://github.com/mendersoftware/mender) ·
  [license](https://raw.githubusercontent.com/mendersoftware/mender/master/LICENSE)
- **AUTOSAR counterpart: UCM** (per-machine install/activate/rollback engine). `repo:autosar/slides/autosar-deck.md`

---

## The honest maturity picture

- **The OSS shelf is real and, in parts, more mature than open AUTOSAR-AP.** RAUC, SWUpdate, Mender
  (1.2k–1.8k★, 10-year track records, named production fleets) and hawkBit (Bosch-backed, 1.0) are
  battle-tested. Zenoh (≈3k★) is heavily used beyond automotive. That contrasts with the AP world,
  where there is **no complete open conformant stack** (`repo:` adaptive-open-source note).
- **But the automotive-specific SDV layer is young.** Of the Eclipse SDV projects, **only Ankaios has
  graduated ("Regular", 1.0)**; Kuksa, uProtocol, Velocitas, Leda and Zenoh are all **Incubating**,
  and **Velocitas/Leda are visibly cooling** (SDK last touched mid-2025; Leda is a showcase distro).
  Read stars/state as a maturity gradient, not a guarantee.
- **The cloud tile has a hole.** The natural reference for "cloud telemetry" — AWS IoT FleetWise — is
  **closed to new customers in 2026**. The edge agent stays Apache-2.0, and COVESA VSS/VISS remain
  the vendor-neutral signal layer, but a 2026 greenfield team can no longer just adopt FleetWise;
  it must self-host (VSS + VISS/VISSR + Kuksa + an MQTT/Zenoh pipe) or use another cloud.
- **The AUTOSAR mapping is asymmetric.** Direct AP counterparts exist for **messaging (`ara::com`)**,
  **orchestration (Execution Management)** and **OTA delivery (UCM/V-UCM)** — but there is **no AP
  counterpart for cloud telemetry**, and **no AP standalone OTA-security framework** matching Uptane
  (UCM does packaging/auth; Uptane is a dedicated compromise-resilient trust model, usable even on
  AP). Diagnostics maps to **DM (`ara::diag`) / SOVD**, whose *open* fleet-side counterpart is
  **Eclipse OpenSOVD** (`repo:` — from the earlier open-AP run).

---

## Open questions / caveats

- **FleetWise cutoff date.** The verbatim "no longer open to new customers" line is primary (AWS
  docs); the specific **April 30, 2026** date is press/search-reported, not re-verified against an
  AWS announcement — mark `binding:"press"` if used on a slide.
- **Uptane governance history.** Uptane began under the Uptane Alliance / IEEE-ISTO, then moved to
  the Linux Foundation Joint Development Foundation; the site now says JDF. Cite JDF as current.
- **RAUC named users beyond Steam Deck** (IKEA, Home Assistant OS, Deutsche Bahn) come from
  comparison blogs, not vendor pages — `binding:"press"`. The SteamOS/RAUC link is solidly sourced
  (Collabora, who build SteamOS).
- **Mender license nuance.** The client is Apache-2.0; the broader Mender product mixes OSS +
  commercial/enterprise components (GitHub API reports `NOASSERTION`; LICENSE file states Apache-2.0
  for the client repo).

---

## Sources (all fetched 2026-07-17)

**Cloud telemetry / signal model**
1. https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/what-is-iotfleetwise.html — FleetWise "no longer open to new customers" (verbatim) + what-it-does — AWS — primary
2. https://docs.aws.amazon.com/iot-fleetwise/latest/developerguide/signal-catalogs.html — FleetWise signal catalog follows VSS — AWS — primary
3. https://github.com/aws/aws-iot-fleetwise-edge — FWE edge agent (C++, Apache-2.0) — AWS/GitHub — primary
4. https://api.github.com/repos/aws/aws-iot-fleetwise-edge — metadata (Apache-2.0, v1.3.5) — GitHub API — primary
5. https://github.com/COVESA/vehicle_signal_specification — VSS (MPL-2.0, v6.0) — COVESA — primary
6. https://covesa.global/covesa-viss-version-3-0-release-candidate/ — VISS v3.0 RC (gRPC etc.) — COVESA — primary
7. https://www.w3.org/TR/viss2-core/ — VISSv2 (W3C) — W3C — primary
8. https://github.com/COVESA/vissr — VISSR reference server (Go, MPL-2.0) — COVESA — primary

**In-vehicle messaging / orchestration**
9. https://uprotocol.org/ — uProtocol overview + transports — Eclipse — primary
10. https://github.com/eclipse-uprotocol/up-transport-zenoh-rust — Zenoh transport for uProtocol — Eclipse — primary
11. https://github.com/eclipse-zenoh/zenoh — Zenoh (dual EPL-2.0/Apache-2.0, 2988★, 1.9.0) — Eclipse — primary
12. https://github.com/eclipse-kuksa/kuksa-databroker — Kuksa VSS databroker (Rust, Apache-2.0) — Eclipse — primary
13. https://github.com/eclipse-leda/leda — Leda reference distro (Apache-2.0) — Eclipse — primary
14. https://github.com/eclipse-ankaios/ankaios — Ankaios orchestrator (Rust, Apache-2.0, 123★) — Eclipse — primary
15. https://eclipsesdv.org/news/eclipse-ankaios-1-0-0-released/ — Ankaios 1.0.0 GA — Eclipse SDV — primary
16. https://www.elektrobit.com/blog/managing-automotive-hpc-software-complexity-with-eclipse-ankaios/ — Elektrobit origin — Elektrobit — vendor
17. https://projects.eclipse.org/api/projects/automotive.ankaios — state "Regular"; and .kuksa/.velocitas/.uprotocol/.leda "Incubating"; iot.zenoh "Incubating" — Eclipse — primary

**OTA**
18. https://uptane.org/ — Uptane one-liner (verbatim), Standard v2.1.0, JDF governance — Uptane/LF — primary
19. https://uptane.org/learn-more/adoptions — AGL, HERE OTA Connect, Airbiquity OTAmatic, Torizon — Uptane — primary
20. https://www.torizon.io/security — Torizon = Uptane + OSTree — Toradex — vendor
21. https://github.com/eclipse-hawkbit/hawkbit — hawkBit (Java, EPL-2.0, 585★, 1.1.0) — Eclipse — primary
22. https://www.eenewseurope.com/en/eclipse-hawkbit-1-0-released-for-open-source-iot-software-updates/ — hawkBit 1.0 + Bosch IoT Rollouts / Kynetics adopters — press
23. https://github.com/rauc/rauc — RAUC (C, LGPL-2.1, 1207★) — Pengutronix/GitHub — primary
24. https://www.collabora.com/news-and-blog/news-and-events/steamos-3-6-how-the-steam-deck-atomic-updates-are-improving.html — SteamOS/Steam Deck uses RAUC — Collabora — press/primary-adjacent
25. https://github.com/sbabic/swupdate — SWUpdate (C, GPL-2.0, 1834★) — DENX/GitHub — primary
26. https://github.com/mendersoftware/mender — Mender (C++, Apache-2.0 client, 1207★) — Northern.tech/GitHub — primary
27. https://raw.githubusercontent.com/mendersoftware/mender/master/LICENSE — Mender client Apache-2.0 — GitHub — primary

**Repo (already fact-checked; AUTOSAR-counterpart claims)**
28. repo:autosar/slides/autosar-deck.md — UCM/V-UCM (OTA), DM/`ara::diag`/SOVD (diagnostics), Ankaios↔AP EM
29. repo:autosar/research/adaptive-open-source-2026-07.md — `ara::com`, Kuksa/uProtocol as SDV-neighbour OSS, "no complete open conformant AP stack"

*Synthesized 2026-07-17. No claim asserted beyond its cited primary source.*
