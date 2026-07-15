# AUTOSAR Adaptive Communication: ara::com, SOME/IP, DDS, and the ROS 2 Comparison

Research notes — 2026-07-15. Primary source is the AUTOSAR AP R25-11 Specification of
Communication Management (Document ID 717), retrieved as PDF and read directly. Written for
embedded/firmware engineers who know MCUs, CAN, and RTOS but are new to automotive SOA
middleware.

## Executive summary

AUTOSAR Adaptive Platform (AP) exposes one application API, `ara::com`, built on a
**proxy/skeleton** service model. That single API is deployment-bound to one of several
**network bindings**: SOME/IP (the automotive-native serialization+SD protocol), a **DDS
binding present since R18-03** (March/April 2018), and implementation-specific **local/IPC
bindings** (e.g. shared-memory zero-copy via iceoryx). Service elements are **events, methods,
fields, and triggers**. The DDS binding maps these onto DDS/RTPS primitives: events and
triggers become Topics + DataWriters/DataReaders; methods and field getters/setters become
**DDS-RPC "DDS Services"** (a Request Topic + a Reply Topic); field notifiers become Topics.
QoS is not fixed by the standard — it is pulled from a `qosProfile` in the deployment manifest.
Two discovery modes exist: a lean one riding on the DomainParticipant `USER_DATA` QoS, and a
Topic-based one. Because AP-DDS and ROS 2 both ride **DDS/RTPS**, they share a wire *family* —
but they are **not plug-compatible** (different topic-naming, type construction, discovery
conventions), so realistic ROS 2 <-> AP interop today uses **bridges/gateways**, not naive
DDS-to-DDS. Fresh finding: **R25-11 removed Raw Data Streaming from `ara::com` and obsoleted
Communication Groups.**

## 1. The ara::com programming model (proxy/skeleton) [1]

R25-11 §7.1.2 "Design decisions" states the API "uses the Proxy/Skeleton pattern":

> "The (service) proxy is the representative of the possibly remote (i.e. other process, other
> core, other node) service. It is an instance of a C++ class local to the application/client...
> The (service) skeleton is the connection of the user provided service implementation to the
> middleware transport infrastructure. Service implementation class is derived from the
> (service) skeleton." [1, §7.1.2]

Key design constraints (§7.1.1–7.1.2): service-oriented communication **without dependency on a
specific communication protocol**; the app codes against `ara::com`, and the integrator
chooses the binding via the manifest. Crucially, the **serialization runs in the execution
context of the Adaptive Application** (the binding is deployed inside the application binary,
not a separate broker) [1, §7.1.1]. The API supports both **event/callback and polling**
styles, synchronous and asynchronous method calls (using C++11 `std::future`/`std::promise`),
and "has **zero-copy capabilities** including the possibility for memory management in the
middleware" [1, §7.1.2].

Discovery philosophy (§7.1.1): "No discovery by application middleware, the clients know the
server but the Server does not know the clients. Event subscription is the only dynamic
communication pattern" — and separately a **full service-discovery API** lets the client pick a
service instance at runtime.

**Service element definitions** (R25-11 glossary §Terms) [1]:
- **Event** — "a notification mechanism that is used by the Service Skeleton to inform the
  Service Proxy that a specific condition or state change occurred. The notification includes
  the data related to the event. Events are sent to a Service Proxy only if it is subscribed."
- **Trigger** — same notification mechanism as an event but **without a data payload** (a
  data-less "something happened" signal; used to trigger fire-and-forget activation) [1; 2].
- **Method** — a client/server operation (request/response, or fire-and-forget when
  `requestNoReturn`).
- **Field** — a value with up to three accessors: a **notifier** (`hasNotifier`, behaves like an
  event carrying the current value), a **getter** (`hasGetter`), and a **setter**
  (`hasSetter`) [1, §7.2.3].

## 2. SOME/IP essentials vs DDS/RTPS — structural comparison

SOME/IP is the automotive-native option: a compact on-wire serialization plus **SOME/IP-SD**
service discovery. Message types (PRS_SOMEIP / SOME/IP-SD spec) [2, 3]:

| Concept | SOME/IP | DDS / RTPS |
|---|---|---|
| Paradigm | Service-oriented RPC + pub/sub events | Data-centric pub/sub (+ DDS-RPC for methods) |
| Request/response | REQUEST `0x00` / RESPONSE `0x80` | DDS-RPC over Request+Reply Topics [4] |
| Fire-and-forget | REQUEST_NO_RETURN `0x01` | one-way Topic write |
| Event push | NOTIFICATION `0x02` | Topic sample (DataWriter→DataReader) |
| Discovery | SOME/IP-SD: FindService, OfferService, StopOfferService, SubscribeEventgroup, Subscribe(N)Ack — **over UDP multicast only** [2, 3] | SPDP/SEDP (RTPS builtin) or AP's own USER_DATA / Topic-based scheme [1, §7.2.3] |
| Subscription granularity | **Eventgroup** (client subscribes to a group of events) | per-Topic DataReader |
| Transport | UDP and TCP (SD itself only over UDP) [3] | RTPS over UDP (typically); shared-mem for local |
| Addressing | Service ID / Instance ID / Method-Event ID / Eventgroup ID | Domain ID / Topic name / type / GUID |
| QoS | limited (reliability implied by TCP vs UDP) | rich QoS matrix (reliability, durability, history, deadline, liveliness…) |

The structural gap that matters for an embedded engineer: SOME/IP is **connection- and
ID-oriented** (like a service bus with numeric IDs, familiar from CAN/UDS thinking), whereas DDS
is **data-centric** — you publish to a Topic and the middleware matches by type+QoS+name, with
no explicit peer connection.

## 3. The DDS network binding — what it actually maps [1, §7.2.3]

This is the repo's load-bearing area. R25-11 confirms and details the binding.

**Compliance baseline** [SWS_CM_11000]: "The DDS network binding shall comply with the DDS
Minimum Profile..., the DDS Wire Interoperability protocol (RTPS)..., and the DDS-XTYPES
Minimal Programming Interface and Network Interoperability Profiles." References are OMG DDS 1.4
[21], DDSI-RTPS 2.2 [22], DDS-XTypes 1.2 [23], and **DDS-RPC 1.0 [24]** for methods.

**Two discovery modes** [SWS_CM_90500] — chosen per instance via a `discoveryType` attribute;
proxy and skeleton must agree:
1. **`DomainParticipantUserDataQos`** — "leverages the USER_DATA QoS policy of DDS Domain
   Participants, assigning a purpose-specific format string to it... fast and nimble, since no
   additional DDS Entities beyond Domain Participants need to be created." The USER_DATA carries
   Service ID, Instance ID, and ServiceInterface contract major/minor version
   [SWS_CM_11001, SWS_CM_09004].
2. **`Topic`** — "employs a purpose-specific Topic of a well-defined type to distribute Service
   Instance announcements in a publish-subscribe, instance-based fashion... more
   resource-demanding... enhances interoperability and enables advanced DDS features such as
   persistence, routing and durability." (This topic-based discovery was the R22-11-era
   addition RTI describes [5].)

**Entity assignment** [SWS_CM_11002]: one **DDS DomainParticipant per Service Instance**, whose
Domain ID and `qosProfile` come from the `DdsProvidedServiceInstance` manifest element;
participants are reused within a process when Domain+QoS match. Under each participant the
binding creates one DDS **Publisher** and one **Subscriber** whose Partition QoS carries the
name `"ara.com://services/<svcId>_<svcInId>"`.

**Element → DDS mapping:**
- **Event** [SWS_CM_11003]: one DDS **Topic** + one **DataWriter** per event; DataWriter
  configured from `DdsEventQosProps.qosProfile`.
- **Trigger** [SWS_CM_10550]: same as event — Topic + DataWriter (data-less).
- **Method** [SWS_CM_11029]: instantiate a **DDS Service [DDS-RPC]** = a **Request Topic** + a
  **Reply Topic**; provider creates a DataReader on Request and a DataWriter on Reply.
- **Field notifier** (`hasNotifier=true`) [SWS_CM_11030, 11130]: Topic + DataWriter, like an
  event carrying the current value.
- **Field getter/setter** (`hasGetter`/`hasSetter`) [SWS_CM_11031]: a **DDS Service**
  (Request/Reply Topics), exactly like a method.
- **Field subscribe/unsubscribe** [SWS_CM_11133–11136]: create/delete a DataReader on the
  notifier Topic.

**QoS is manifest-driven, not standard-fixed.** The spec repeatedly says entities "shall be
configured according to the `qosProfile` specified in the associated `DdsEventQosProps` /
`DdsFieldQosProps`" — i.e. the standard defines *which* DDS entities exist and *that* they carry
QoS, but the concrete reliability/durability/history values are a **deployment choice** in the
manifest, not baked into the spec. This is an important nuance for the repo: AP does **not**
mandate a fixed QoS set the way one might assume.

**Type mapping**: ServiceInterface data types are expressed in **DDS-IDL / DDS-XTypes**;
AUTOSAR primitives "map naturally to DDS-XTypes (booleans, numerics, strings, structures,
arrays, sequences...)" per RTI, who implemented the binding [6]. Field-notifier and event Topic
data types are constructed per the Foundation PRS (`FO_PRS_DDS_00401` etc.) [1].

**Production evidence**: The binding is implemented commercially — **RTI Connext** ships an
AUTOSAR DDS binding toolkit [5, 6]. I found **no primary confirmation of a shipping production
vehicle whose AP ECUs use the DDS binding on the wire**; vendor material describes availability
and prototypes, and academic work uses it in demonstrators. Treat "production use" as *tooling
exists and is validated, series deployment unconfirmed* (see Open questions).

## 4. Local IPC / zero-copy bindings — standardized vs implementation-specific

`ara::com` §7.1.2 promises "zero-copy capabilities," and §7.1 shows an "IPC Transport" path
parallel to the SOME/IP path in the architecture figure [1]. **But the local/IPC wire is not a
standardized inter-vendor protocol** — unlike SOME/IP (fully specified) and DDS (RTPS is
standardized), the local binding is left to the implementation. In practice the dominant
realization is **Eclipse iceoryx**, a true zero-copy shared-memory IPC whose API "is very close
to `ara::com`" and "is fully compatible with the ROS 2 and Adaptive AUTOSAR APIs" [7, 8]. So:
- **Standardized on the wire**: SOME/IP, DDS/RTPS.
- **Standardized as an API surface only**: `ara::com` (any binding behind it).
- **Implementation-specific**: local shared-memory/zero-copy IPC (iceoryx or a vendor's own),
  and the "no standardized API layer between application-facing APIs and network binding
  components" [6].

For an MCU-background reader: the zero-copy path is conceptually like a lock-free shared-memory
ring between processes on one SoC — no serialization, pointers handed across via a broker
(iceoryx's RouDi routing/discovery daemon) [7].

## 5. ara::com vs rclcpp — the mapping an embedded engineer should carry

| ara::com (AP) | ROS 2 rclcpp | Note |
|---|---|---|
| Skeleton (offers service) | Publisher + Service server | offer-side |
| Proxy (consumes service) | Subscription + Service client | consume-side |
| Event | Topic publish/subscribe | closest 1:1 |
| Trigger | (no direct equiv; empty msg / std_msgs/Empty) | data-less notify |
| Method (req/resp) | Service (`srv`) | rclcpp uses its own req/resp, AP-DDS uses DDS-RPC |
| Field (notifier+get+set) | Topic (latched-ish) + 2 services / a Parameter | AP has no single equivalent in ROS 2 |
| Manifest `qosProfile` | `rclcpp::QoS` / RMW QoS profile | both DDS QoS underneath |
| Binding chosen at deploy | RMW chosen at build/runtime (`RMW_IMPLEMENTATION`) | analogous indirection |

Both stacks are **`ara::com`/`rclcpp` thin C++ facades over pluggable middleware**. The single
most transferable idea: *the application API is protocol-agnostic; DDS/SOME/IP is a swappable
binding underneath.* An engineer who understands ROS 2's rmw/DDS layering already understands
AP's binding layering.

## 6. Realistic ROS 2 <-> AP interop today

The repo's shipped claim — "the DDS wire family is what AUTOSAR Adaptive shares with ROS 2" — is
**correct and well-supported**: both can speak DDS/RTPS. But sharing a wire *family* is not the
same as being interoperable out of the box. Blockers to naive DDS-to-DDS:
- **Topic naming**: ROS 2 mangles names (`rt/<topic>`, `rq/…Request`, `rr/…Reply`) and derives
  type names its own way; AP-DDS uses `"ara.com://services/…"` Partition names and its own
  Topic-naming scheme [1, §7.2.3]. They will not discover each other's endpoints without a map.
- **Type construction**: ROS 2 generates IDL/type-support from `.msg`; AP generates DDS-IDL from
  the ServiceInterface. Byte layouts can be made to match (both XTypes) but only with a
  deliberately shared IDL.
- **Discovery mode**: AP may use USER_DATA-based discovery, which ROS 2 does not implement.
- **Methods/fields**: AP methods use DDS-RPC (Request/Reply Topics); ROS 2 services use a
  different (also RTPS-based) convention — not automatically compatible.

Consequently the **practical interop path is a bridge/gateway**, and this is an active research
area (2024–2026): the ASIRA architecture uses a **ROS 2 <-> SOME/IP bridge** [10]; a 2025
**dynamic SOME/IP-DDS bridge** (Discovery Manager + Bridge Manager + Message Router) detects SD
events on both sides and creates/destroys mapping entities at runtime [9]. A 2026 comparison
paper notes ROS 2 "meets many communication and data type requirements through its use of DDS
and IDL-based message definitions" but "lacks several concepts essential for series-production"
(operation modes, allocation, watchdog supervision) [11] — which is *why* AP exists alongside
ROS 2 rather than being replaced by it.

## Key facts

| # | fact | source URL | exact quote if load-bearing | confidence |
|---|---|---|---|---|
| 1 | Latest release is R25-11, presented at virtual event Dec 4 2025 | https://www.autosar.org/news-events/detail/release-r25-11-is-now-available | "The latest AUTOSAR Release, R25-11, was officially presented at the Virtual Release Event on December 4th, 2025." | high |
| 2 | R25-11 removed Raw Data Streaming from ara::com and obsoleted Communication Groups; reworked C++ API | R25-11 SWS_CommunicationManagement PDF, change history p.1 | "Removed Raw Data Stream functionality from ara::com"; "Communication Groups are now OBSOLETE"; "Reworked ara::com C++ API descriptions based on header files" | high |
| 3 | ara::com uses the Proxy/Skeleton pattern; proxy = local rep of possibly-remote service | R25-11 CM §7.1.2 | "It uses the Proxy/Skeleton pattern: The (service) proxy is the representative of the possibly remote... service." | high |
| 4 | DDS binding first appeared in R18-03 (published Apr 23 2018) | R25-11 CM change history + https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds | "the latest AUTOSAR Adaptive Platform specification, release 18.03, was published" with DDS binding | high |
| 5 | DDS binding must comply with DDS Minimum Profile, RTPS wire protocol, DDS-XTypes | R25-11 CM §7.2.3 [SWS_CM_11000] | "shall comply with the DDS Minimum Profile..., the DDS Wire Interoperability protocol (RTPS)..., and the DDS-XTYPES Minimal... Profiles." | high |
| 6 | Two discovery modes: DomainParticipant USER_DATA QoS, and Topic-based | R25-11 CM [SWS_CM_90500] | "leverages the USER_DATA QoS policy of DDS Domain Participants"; Topic mode "employs a purpose-specific Topic... in a publish-subscribe, instance-based fashion" | high |
| 7 | One DomainParticipant per Service Instance; Domain ID + qosProfile from manifest | R25-11 CM [SWS_CM_11002] | "assign a DDS DomainParticipant to every Service Instance... Domain ID... shall be derived from the Manifest... QoS Profile... derived from the Manifest" | high |
| 8 | Events/triggers → Topic+DataWriter; methods & field get/set → DDS Service (Request+Reply Topics, DDS-RPC); field notifier → Topic | R25-11 CM [SWS_CM_11003,10550,11029,11030,11031] | "instantiate a DDS Service [24] to handle requests to all the methods"; "assign a DDS Topic... per event" | high |
| 9 | DDS QoS is manifest-driven (DdsEventQosProps/DdsFieldQosProps.qosProfile), not fixed by spec | R25-11 CM [SWS_CM_11003 etc.] | "The DataWriter shall be configured according to the qosProfile specified in the associated DdsEventQosProps." | high |
| 10 | Partition name for a service instance is ara.com://services/<svcId>_<svcInId> | R25-11 CM [SWS_CM_11002] | "\"ara.com://services/<svcId>_<svcInId>\"" | high |
| 11 | SOME/IP message types: REQUEST 0x00/RESPONSE 0x80, REQUEST_NO_RETURN 0x01, NOTIFICATION 0x02 | https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf (+ PRS SOME/IP) | message-type field values | high |
| 12 | SOME/IP-SD runs over UDP multicast only; entries FindService/OfferService/StopOffer/SubscribeEventgroup | SOME/IP-SD PRS (autosar.org) | "SOME/IP SD is constrained to use SOME/IP only over UDP" | high |
| 13 | ara::com API "has zero-copy capabilities including... memory management in the middleware" | R25-11 CM §7.1.2 | direct quote | high |
| 14 | Local/IPC zero-copy binding is implementation-specific; iceoryx is the common realization, API-compatible with both AP and ROS 2 | https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 | "fully compatible with the ROS2 and Adaptive AUTOSAR APIs and can be used as an implementation for both" | high |
| 15 | Practical ROS 2 <-> AP interop uses bridges (SOME/IP-DDS bridge / ROS2-SOME/IP bridge), not naive DDS-to-DDS | https://doi.org/10.3390/electronics14183635 ; https://doi.org/10.3390/electronics13071303 | dynamic SOME/IP-DDS bridge with Discovery/Bridge/Message-Router components | med-high |
| 16 | ROS 2 lacks series-production automotive concepts (operation modes, allocation, watchdog supervision) | https://arxiv.org/html/2604.22576 | "lacks several concepts essential for series-production automotive systems" | med |

## Sources

1. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf — Specification of Communication Management, AP R25-11 (Doc ID 717) — AUTOSAR — **primary**
2. Web search synthesis of PRS_SOMEIP message types (autosartoday / KopherBit / ETAS RTA) — **secondary (leads), corroborated against PRS**
3. https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf — SOME/IP Service Discovery Protocol Specification — AUTOSAR — **primary**
4. https://www.omg.org/spec/DDS-RPC/1.0 — RPC over DDS 1.0 — OMG — **primary** (referenced as [24] by the CM spec)
5. https://www.rti.com/blog/status-of-dds-in-autosar — Connectivity at the Core: The Status of DDS in AUTOSAR — RTI — **vendor**
6. https://www.rti.com/blog/implementing-autosars-dds-network-binding — Implementing AUTOSAR's DDS Network Binding — RTI — **vendor**
7. https://github.com/eclipse-iceoryx/iceoryx — Eclipse iceoryx (true zero-copy IPC) — Eclipse — **vendor/OSS**
8. https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 — iceoryx speeds up AUTOSAR and ROS 2 — Apex.AI — **vendor**
9. https://doi.org/10.3390/electronics14183635 — A Dynamic Bridge Architecture for Interoperability Between AUTOSAR Adaptive and ROS2 (2025) — MDPI Electronics — **peer-reviewed**
10. https://doi.org/10.3390/electronics13071303 — Autonomous Driving System with Integrated ROS2 and Adaptive AUTOSAR (ASIRA, 2024) — MDPI Electronics — **peer-reviewed**
11. https://arxiv.org/html/2604.22576 — A Comparison of ROS 2 and AUTOSAR AP Against Industry-Elicited Automotive Middleware Requirements (2026) — arXiv preprint — **secondary/preprint**
12. https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds — AUTOSAR Adaptive Platform 18.03: Now with DDS! — RTI — **vendor**

## Surprises

- **R25-11 REMOVED Raw Data Streaming from `ara::com`** and marked **Communication Groups
  OBSOLETE**, and reworked the whole ara::com C++ API against generated headers. Any repo slide
  listing "raw data streams" as a current ara::com feature is now out of date — it existed
  R19-11 → R24-11 and is gone in R25-11 [fact 2].
- **DDS QoS in AP is not a fixed standard profile** — it is entirely manifest/`qosProfile`
  driven. The spec standardizes *which entities* exist, not the reliability/durability values.
  This contradicts a natural assumption that "AP-DDS mandates QoS X."
- **AP has TWO DDS discovery modes**, one of which (USER_DATA-QoS-based) creates *no* extra DDS
  entities and is deliberately different from ordinary DDS Topic discovery — and different from
  what ROS 2 does. This is a concrete reason AP-DDS and ROS 2 do not auto-discover each other.
- Methods and field getters/setters map to **DDS-RPC** (a full OMG spec), not to plain topics —
  so "AP-DDS = pub/sub" is an oversimplification.
- Sharing DDS/RTPS is necessary but **not sufficient** for ROS 2 interop; the literature
  universally reaches for bridges, confirming naive DDS-to-DDS does not work.

## Open questions

- **Production deployment of the DDS binding on-vehicle**: I could confirm tooling (RTI Connext
  binding) and demonstrators, but found **no primary source naming a shipping production vehicle
  whose AP ECUs use the DDS binding on the wire** rather than SOME/IP. *Best guess (labeled
  guess): SOME/IP still dominates production AP inter-ECU links; DDS is used mainly where AD/HPC
  stacks meet AP.* Needs a vendor case study to confirm.
- **Whether R25-11 changed the DDS binding's discovery/QoS mechanics vs R22-11.** I read the
  R25-11 mapping in detail but did not diff every SWS item against R22-11; the change history
  mentions "Refined DDS network binding" historically but the R25-11 delta is dominated by the
  ara::com API rework. Low-risk, but unverified line-by-line.
- **Exact trigger semantics** (fully data-less vs minimal payload): the glossary text for
  "Trigger" is truncated in extraction and mirrors "Event"; I infer data-less from SOME/IP
  handling. *Guess: trigger carries no application payload.* Medium confidence.
- **Rust ara::com**: R25-11 released "code for Rust on adaptive platform" — whether that Rust
  code includes a Rust ara::com binding surface (relevant to a future ROS 2 <-> AP comparison in
  Rust) was not verified.
- Whether any of the ROS 2<->AP bridges [9,10] are used beyond academia (series production) —
  unverified.
