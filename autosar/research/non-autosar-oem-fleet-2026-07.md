# Fleet/cloud connectivity for OEMs that do NOT run AUTOSAR on central compute

**Researcher A — 2026-07-17.** Question: how do vehicles from OEMs that do *not* run
AUTOSAR middleware on their central computer actually connect to their fleet/cloud
backends? Evidence-only. Every external claim carries a working source URL; verbatim
quotes are in quotation marks. Regulation-vs-de-facto-vs-optional labeled per claim.

**Headline:** the single most concrete artifact is **Tesla's own open-source
`fleet-telemetry` server** — a real production OEM's fleet-connectivity design published on
GitHub. It shows exactly what "fleet connectivity without AUTOSAR" looks like on the wire:
the vehicle is a **WebSocket client** pushing **protobuf**-encoded telemetry records over
**mTLS** directly to a server the fleet operator runs. No AUTOSAR, no SOME/IP, no DDS, no
DoIP in the telemetry path. Rivian and Li Auto corroborate the pattern from the
architecture side (in-house middleware on FreeRTOS / a bespoke OS, explicitly rejecting
AUTOSAR).

---

## 1. Tesla — the clearest primary evidence

### 1.1 `github.com/teslamotors/fleet-telemetry` — what it is

Owner is the real Tesla org: GitHub `login: teslamotors`, `name: "Tesla, Inc."`,
`blog: http://www.tesla.com/` (GitHub API `/orgs/teslamotors`).

Repo facts (GitHub REST API, `/repos/teslamotors/fleet-telemetry`, fetched 2026-07-17):

| Field | Value |
|---|---|
| Language | **Go** |
| License | **Apache-2.0** |
| Created | **2023-05-09** |
| Last push | **2026-07-15** (actively maintained) |
| Latest release | **v0.9.4**, published **2026-07-14** |
| Stars / forks | 871 / 148 |
| Contributors | 18 |
| Archived | no |

**What it is (verbatim, README):** *"Fleet Telemetry is a server reference implementation
for Tesla's telemetry protocol. It is the best way to get data from Tesla vehicles. Owners
can allow registered applications to receive telemetry securely and directly from their
vehicles."* — https://github.com/teslamotors/fleet-telemetry/blob/main/README.md

So the repo is the **server side** that a fleet operator (or an individual owner) *hosts*;
the **client** is Tesla's in-vehicle firmware (closed) which connects out to that server.
This is the mirror image of the AUTOSAR world, where the vehicle exposes a diagnostic
server (DoIP/UDS) and the backend polls in.

### 1.2 Protocol / encoding / security (all primary)

- **WebSocket, push, direct:** *"Once configured, devices establish a WebSocket connection
  to push configurable telemetry records. Fleet Telemetry provides clients with ack, error,
  or rate limit responses."* (README)
- **Protobuf encoding:** the repo carries the wire schema as `.proto` files under
  `protos/` — `vehicle_data.proto`, `vehicle_connectivity.proto`, `vehicle_alert.proto`,
  `vehicle_error.proto`, `vehicle_metric.proto` (all `syntax = "proto3"`). Example, the
  connectivity message:
  ```
  // vehicle_connectivity.proto
  syntax = "proto3";
  package telemetry.vehicle_connectivity;
  message VehicleConnectivity {
    string vin = 1;
    string connection_id = 2;
    ConnectivityEvent status = 3;   // UNKNOWN | CONNECTED | DISCONNECTED
    google.protobuf.Timestamp created_at = 4;
    string network_interface = 5;
  }
  ```
  A config flag `transmit_decoded_records` (bool) exists specifically to *"transmit JSON to
  dispatchers instead of proto"* — confirming the default on-vehicle-to-server encoding is
  protobuf. (README + `protos/vehicle_connectivity.proto`)
- **mTLS:** *"Ensure mTLS connections are terminated on the Fleet Telemetry service."*
  (README, Install steps). Vehicle-side auth is an EC key on the secp256r1/prime256v1
  curve; the developer app hosts its public key at
  `/.well-known/appspecific/com.tesla.3p.public-key.pem` and pairs a "virtual key" to each
  vehicle. (README setup steps)
- **Recommended backend topology:** *"Firewall/Loadbalancer -> Fleet Telemetry -> Kafka"*;
  dispatchers include Kafka, Kinesis, Google Pub/Sub, MQTT, etc.; Helm chart for Kubernetes
  provided. (README)

**Official developer docs** (companion to the repo): "Fleet Telemetry" overview at
https://developer.tesla.com/docs/fleet-api/fleet-telemetry — the official text states
vehicles *stream data directly to a server, eliminating the need to poll the vehicle_data
endpoint*, and that *data is encapsulated into protobuf messages*. (Note: `developer.tesla.com`
returns HTTP 403 to automated fetchers in this sandbox; content confirmed via the mirrored
README above and search-index snippets. Treat the developer.tesla.com URL as the canonical
doc, the GitHub README as the machine-verified primary.) There is also an official
onboarding: create an app at `developer.tesla.com`, register via the Fleet API partner
endpoints, then push `fleet_telemetry_config` to each VIN.

*Binding:* n/a (descriptive facts about Tesla's own proprietary design). The design choice
itself — proprietary telemetry protocol rather than an AUTOSAR service stack — is
**optional / OEM-proprietary**, not mandated by anyone.

### 1.3 Tesla's in-vehicle software stack — Linux, in-house, vertically integrated

- **Primary (GPL compliance):** Tesla publishes kernel sources at
  `github.com/teslamotors/linux` — GitHub API: `description: "Linux sources"`, `language: C`,
  created 2017-12-19, 1,462 stars, not archived (last push 2024-07-19). An OEM only publishes
  a kernel tree because it ships the Linux kernel in the product (GPL-2.0 source-offer
  obligation). This is direct primary evidence that Tesla's infotainment/central compute is
  **Linux-based**. https://github.com/teslamotors/linux
- **Companion tooling, also Tesla-published, Apache-2.0:**
  `github.com/teslamotors/vehicle-command` (Go; the signed command proxy used with
  fleet-telemetry), created 2023-10-04, last push 2026-07-16, 679 stars.
- **Press (label: press):** US News, Medium/Tesla Digest and others describe Tesla's
  "Vehicle Operating System (VOS)" as a Linux kernel with Buildroot/Ubuntu userland and an
  in-house stack that *combines IVI + CAN gateway + TCU into one unit* rather than separate
  ECUs. Useful color, not primary; cite only as press.
  https://cars.usnews.com/cars-trucks/features/what-os-does-tesla-use

### 1.4 Tesla service / diagnostics path

- Tesla's workshop tool is **proprietary "Toolbox" (Toolbox 3)**, sold by subscription;
  the CAN data on the vehicle is **encoded/proprietary**, not open OBD/UDS parameter IDs, so
  generic scan tools cannot interpret it without Tesla access. Official page:
  https://service.tesla.com/en-US/diagnostic-software . Press coverage of the right-to-repair
  subscription and encoded CAN: https://insideevs.com/news/770132/tesla-toolbox-diagnostic-software-mechanic/
  (label: press). *Binding:* the emissions-OBD mandate is largely n/a for a BEV; Tesla's
  chosen service path is **proprietary/optional**, not a standardized UDS/DoIP workshop
  interface.

---

## 2. Rivian — in-house middleware, FreeRTOS, explicitly no AUTOSAR

Two independent, on-record primary sources (both re-pinned; previously verified in
`repo:research/fact-check-2026-07-16.md` F1–F3 and Run 4/C5).

### 2.1 The AUTOSAR / FreeRTOS statement (Rivian SVP, on record)

Source: **The Garage** podcast (Sonatus), S2 E15, "How is Rivian Reinventing Vehicle
Architecture?", **Vidya Rajagopalan**, SVP Electrical Hardware Engineering at Rivian, in
conversation with John Heinlein (Sonatus CMO). Transcript page:
https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/

Verbatim:
- *"We don't use any of the industry offerings such as AUTOSAR."*
- *"Our zonal controllers are built on a very robust in-house system that the teams have
  developed... It's really based on top of Free RTOS, but we really added a lot of layers
  to it."*
- *"We migrated from the domain-based architecture, to a zonal architecture, which allowed
  us to go from 17 ECUs to 7 ECUs."*
- On keeping HPCs separate: *"We deliberately chose to keep the infotainment and ADAS
  separate... Both infotainment and ADAS are very complex, and they really have high compute
  needs."*

Scope discipline (from Run 4/C5): the FreeRTOS/no-AUTOSAR statement is scoped to the
**zonal controllers**; the central compute is Android Automotive (infotainment) + Rivian
middleware on NVIDIA foundations (ADAS). The point stands either way — none of it is
AUTOSAR.

### 2.2 Zonal topology + AUTOSAR-rejection, corroborating source (Munro / Lean Design)

https://leandesign.com/rivian-software-architecture-update/ — verbatim:
- *"Rivian's Gen 1 system followed this model with 17 discrete control units. With the Gen 2
  platform, that number has dropped to seven, thanks to Rivian's move to zonal
  architecture."*
- *"Each zonal controller—named East, West, and South—is a general-purpose compute node that
  communicates with sensors, actuators, and other parts of the vehicle."*
- *"Instead, Rivian built its own OS—Safe ARTUS—and encourages hand-coded software
  craftsmanship."*
- *"In a break from industry norms, Rivian has made a conscious decision to avoid AutoSAR...
  According to Bensaid, AutoSAR introduces 'obfuscation' that makes debugging and rapid
  iteration difficult."*

(The dual-DRIVE-Orin, ~250 TOPS central-compute detail is verified in
`repo:research/fact-check-2026-07-16.md` F2; NVIDIA partner page + Rivian announcement.)

*Binding:* n/a (architecture facts). The choice to skip AUTOSAR is **optional /
vertically-integrated-OEM** strategy.

### 2.3 Rivian service / diagnostics path (weaker sourcing — forum/community only)

- Community/forum evidence indicates the R1T/R1S expose an **OBD2-shaped port with Ethernet
  pins (DoIP-style)** but that the vehicle **does not answer standard DoIP messaging** —
  i.e. a proprietary or enhanced diagnostic protocol over Ethernet. Rivian's official
  workshop tool is **RiDE (Rivian Diagnostic Environment)**, offered to third-party shops by
  subscription (community-reported ~$5,500/yr). Forum threads:
  https://www.rivianownersforum.com/threads/diagnostics-scantool-and-networking.2885/ ;
  community service guide repo: https://github.com/kallisti5/rivian-service-guide
  **Label: press/forum, low confidence** — no Rivian primary doc pins the exact protocol.
  The safe, sourced statement is only: Rivian ships a proprietary workshop tool (RiDE) and
  the port is Ethernet/DoIP-style but not standard-DoIP-responsive per owners.

---

## 3. Li Auto — Halo OS, an in-house OS open-sourced *explicitly to challenge AUTOSAR*

This is a clean, citable third non-AUTOSAR central-compute example (China market).

- **Announcement:** 2025-03-27, Zhongguancun Forum, Beijing. Li Auto (Li Xiang, founder/CEO)
  announced open-sourcing **Halo OS**, its in-house automotive OS, positioned to *"challenge
  the position of AUTOSAR."* Modules named: **vehicle-control OS, smart-driving OS,
  communication middleware, virtualization platform.** Claimed vs AUTOSAR: *"the response
  speed is twice as fast as AUTOSAR and the response stability is five times better."*
  Primary-market press: https://cnevpost.com/2025/03/27/li-auto-open-sources-halo-os/
  and https://www.automotiveworld.com/articles/li-auto-challenges-autosar-open-sources-its-halo-os/
- A technical white paper detailing Halo OS architecture was reported published ~2025-04-15,
  with code to land in the open-source community "at the end of April."
- **Caveat (do NOT overclaim):** I could not confirm an official Halo OS source repository in
  this session. A GitHub search surfaced only a third-party benchmark repo
  (`LatorreEngineering/halo-vs-qnx-vs-autosar-2025`, 0 stars) — **not** an official Li Auto
  artifact; **do not cite it as evidence of Halo OS.** The open-source claim rests on the
  announcement + white-paper coverage.

*Binding:* **press.** The "challenges AUTOSAR / faster than AUTOSAR" framing is Li Auto's own
marketing claim reported by press — cite as press, not as measured fact.

---

## 4. Other OEMs — partial / adjacent (include only with caveats)

- **Hyundai "Pleos"** (launched 2025) is a **vehicle OS built on Google Android Automotive**
  with a zonal-plus-HPVC (high-performance vehicle computer) topology. It is a real
  non-Android-infotainment "vehicle OS" brand, but the public material does **not** show
  Hyundai *rejecting* AUTOSAR on safety/zonal ECUs — Hyundai remains an AUTOSAR consortium
  member. So Pleos is evidence of an **Android-based central-compute OS**, not a clean
  "non-AUTOSAR stack." Press: https://insideevs.com/news/793469/hyundai-pleos-os-explained/
  **Label: press; adjacent, not a clean non-AUTOSAR claim.**
- **VW CARIAD:** prior repo work (`repo:autosar/slides/autosar-deck.md`,
  head-to-head-coexistence note) establishes VW E³/SSP as **domain-controller-based today**
  with **Classic on zonal/safety ECUs and Adaptive/Linux on HPCs** — i.e. VW *does* use
  AUTOSAR. Not a non-AUTOSAR example; mention only to contrast.
- **NIO / XPeng / others:** no clean primary source pinned this session; left out per
  "empty result is fine."

---

## 5. Slide-worthy synthesis: "fleet connectivity without AUTOSAR"

The concrete shape, backed by Tesla's own repo:

1. **Vehicle firmware is a cloud client, not a diagnostic server.** It opens an outbound
   **WebSocket over mTLS** and **pushes protobuf** telemetry records to a server the operator
   runs (Tesla `fleet-telemetry`, Go, Apache-2.0). No SOME/IP, no DDS, no DoIP in this path.
2. **The OEM owns the whole stack.** Linux central compute (Tesla publishes its kernel tree),
   in-house middleware (Rivian's "layers on top of FreeRTOS"; Li Auto's Halo OS), so there is
   no Tier-1 boundary that AUTOSAR standardization is designed to bridge — which is precisely
   the stated reason these OEMs skip it (Rivian: AUTOSAR adds "obfuscation").
3. **Backend is commodity cloud plumbing** (Kafka / Kinesis / Pub/Sub / MQTT, Kubernetes +
   Helm), not an automotive-specific bus.
4. **Diagnostics diverge from the AUTOSAR UDS/DoIP norm:** Tesla uses proprietary,
   encrypted-CAN "Toolbox 3"; Rivian ships a proprietary "RiDE" tool over an Ethernet/DoIP-
   shaped port that reportedly doesn't answer standard DoIP. UDS/DoIP remains the de-facto
   workshop interface across the industry, but these vertically-integrated OEMs implement
   their own tools rather than exposing a standard one.

**Contrast with the AUTOSAR-CP+AP fleet path** (already in the deck): TCU → central gateway →
Diagnostic Manager on AP / DoIP→DoCAN → DCM+DEM on CP, OTA via UCM + UDS 0x34–0x37. The
non-AUTOSAR OEMs replace that entire standardized diagnostic-server + service-oriented
middleware chain with a proprietary push-telemetry client + cloud backend + proprietary
workshop tooling.

---

## Source ledger (working URLs)

- Tesla fleet-telemetry repo + README + protos: https://github.com/teslamotors/fleet-telemetry
  · https://github.com/teslamotors/fleet-telemetry/blob/main/README.md
  · https://github.com/teslamotors/fleet-telemetry/blob/main/protos/vehicle_connectivity.proto
- Tesla Fleet API telemetry docs: https://developer.tesla.com/docs/fleet-api/fleet-telemetry
  (403 to fetchers; canonical doc)
- Tesla Linux kernel sources: https://github.com/teslamotors/linux
- Tesla vehicle-command: https://github.com/teslamotors/vehicle-command
- Tesla diagnostics (official): https://service.tesla.com/en-US/diagnostic-software
  · (press) https://insideevs.com/news/770132/tesla-toolbox-diagnostic-software-mechanic/
- Rivian, Rajagopalan/FreeRTOS/AUTOSAR: https://www.sonatus.com/resources/vidya-rajagopalan-of-rivian/
- Rivian zonal + AUTOSAR-avoidance (Munro): https://leandesign.com/rivian-software-architecture-update/
- Rivian diagnostics (forum/community, low conf): https://www.rivianownersforum.com/threads/diagnostics-scantool-and-networking.2885/
- Li Auto Halo OS: https://cnevpost.com/2025/03/27/li-auto-open-sources-halo-os/
  · https://www.automotiveworld.com/articles/li-auto-challenges-autosar-open-sources-its-halo-os/
- Hyundai Pleos (adjacent, press): https://insideevs.com/news/793469/hyundai-pleos-os-explained/
- Reused repo facts: repo:research/fact-check-2026-07-16.md (F1–F3, F2 Orin, Run4/C5),
  repo:autosar/research/notes/head-to-head-coexistence.md (folklore discipline on Tesla)
