# AUTOSAR Adaptive Platform — a firmware engineer's field guide (July 2026)

**What this is.** A single synthesized reference on the AUTOSAR Adaptive Platform (AP)
for embedded/firmware engineers who know MCUs, CAN, RTOSes, and bare-metal reflashing but
are new to automotive HPC software platforms. It merges four research notes under
`autosar/research/notes/` — `adaptive-arch.md` (philosophy, architecture, function
clusters), `adaptive-comm.md` (`ara::com`, SOME/IP, DDS, the ROS 2 comparison),
`adaptive-lifecycle-diag.md` (UCM, Diagnostic Management, PHM, Persistency, SOVD), and
`adaptive-platform-vendors.md` (OSes, vendor stacks, certification, silicon, open
efforts) — and is reconciled against the repo's two binding notes
(`repo-constraints.md`, `orchestrator-verification.md`), which win wherever a research
note conflicts. Every external, load-bearing claim carries a source URL, copied from the
notes; the numbered `[n]` markers resolve to the **Sources** list. Facts are
release-stamped to **AUTOSAR R25-11** (release date 2025-11-27, presented at a virtual
event on 4 December 2025 [1][15]). Nothing here is asserted beyond what those notes
verified — anything without a source is parked in **Open questions**.

The one-line orientation for this whole document: **AP is middleware and a set of
services running on top of a POSIX operating system — it is deliberately *not* a new
operating system** [2]. If your instinct from Classic AUTOSAR is "AUTOSAR = the RTOS on
my MCU," that instinct is wrong for Adaptive.

---

## 1. Why the Adaptive Platform exists

Classic AUTOSAR (CP) was built for deeply-embedded ECUs: a statically-scheduled,
signal/PDU-oriented stack with no dynamic memory, running on an MCU under an OSEK-heritage
RTOS. That model cannot serve the new tier of automotive compute — the **high-performance
computer (HPC)** ECUs that drive Ethernet backbones, many-core/GPU/FPGA silicon,
service-oriented functions (ADAS, connectivity, infotainment), and over-the-air (OTA)
software updates. AUTOSAR's own Platform Design explanation states the motivation plainly:
*"the needs of ECUs described above cannot be fulfilled [by CP]. Therefore, AUTOSAR
specifies a second software platform, the AUTOSAR Adaptive Platform (AP). AP provides
mainly high-performance computing and communication mechanisms and offers flexible
software configuration, e.g. to support software update over-the-air"* [2].

Two technology drivers are named explicitly: **Ethernet** (switched, point-to-point, high
bandwidth — CP was optimised for legacy CAN and "cannot fully utilise" Ethernet), and
**processors** ("Manycore processors with tens to hundreds of cores, GPGPU … FPGA, and
dedicated accelerators") [2]. For a firmware engineer, the four design characteristics
that define AP's personality are: **C++** as the implementation language; **SOA**
(service-oriented architecture, where a peer is addressed the same way whether it is a
local process or on a remote AP machine); **updateability/OTA**; and **agile**,
deploy-then-update development [2].

Put the two platforms side by side. CP: statically scheduled, signal-oriented, no dynamic
memory, MCU + OSEK/AUTOSAR-OS. AP: process-oriented, service-oriented, dynamic memory
(mostly allocated at startup), MPU-class SoC under a POSIX OS. This is not "CP is
obsolete" — the two coexist in every real vehicle, usually with CP on a companion safety
MCU and AP on the application SoC (see §5). One anti-folklore guardrail from the repo:
**do not frame this as "Classic = CAN only, Adaptive = Ethernet only."** Classic has had a
standardized SOME/IP transformer and Ethernet/DoIP since release 4.2.1 (Oct 2014), over two
years before AP's first release (R17-03, March 2017) [repo-constraints §1–2].

---

## 2. Architecture — processes, ARA, function clusters, and the "dumb enforcer"

### Adaptive Applications are POSIX processes

An Adaptive Application (AA) is an ordinary **POSIX process** written in **C++**, linked
against **ARA** (AUTOSAR Runtime for Adaptive Applications) [2]. Crucially, an AA is
restricted "by definition" to the **POSIX PSE51** profile — a *single-process* profile of
POSIX (IEEE 1003.13, "Minimal Realtime System Profile") "selected to offer portability for
AA and to enable freedom from interference among applications" [2]. PSE51 gives you
threads, mutexes, semaphores, signals, real-time scheduling (`SCHED_FIFO`/`SCHED_RR`),
timers, and a single-process I/O subset — but it **excludes** `fork`/`exec` process
creation (no multi-process support, not even `posix_spawn`). It does **not** exclude POSIX
shared memory, though: PSE51 mandates `_POSIX_SHARED_MEMORY_OBJECTS`; only XSI/System-V-style
IPC is unrequired (and that uniformly across PSE51–54). The practical consequences: **one process =
one address space with multiple threads**; you cannot spawn child processes from an AA
(process creation is owned by Execution Management, below); isolation between apps comes
from OS process boundaries plus resource groups, not from within the app [2]. Note the OS
*itself* is required to be **multi-process POSIX** — only the *AAs* are restricted to
PSE51 [2].

### "Middleware on an OS, not an OS" — say it precisely

The Operating System chapter is quotable: *"The Adaptive Platform does not specify a new
Operating System for highly performant processors. Rather, it defines an execution context
and Operating System Interface"* [2]. The OS underneath — Linux, QNX, PikeOS, INTEGRITY,
VxWorks — provides scheduling, resource management, and IPC; AP's function clusters are
processes on top. The Machine may even be *"a real physical machine, a fully-virtualized
machine, a para-virtualized OS, an OS-level-virtualized container or any other
virtualized"* environment [2]; AP presents a consistent view regardless of virtualization.

### ARA and its two taxonomies

AAs "run on top of ARA … [which] consists of application interfaces provided by Functional
Clusters" [2]. From the application's viewpoint every function cluster "just provides [a]
specified C++ interface" in the `ara::` namespaces — `ara::com`, `ara::exec`, `ara::core`,
`ara::log`, `ara::crypto`, `ara::diag`, `ara::per`, `ara::phm`. Watch for **two official
taxonomies of the same clusters**: the Platform Design logical view groups them into
*Foundation / Services / Standard Application Interfaces / Vehicle Services*, while the SW
Architecture building-block view groups the same clusters into **seven technical
categories** — Runtime, Communication, Storage, Security, Safety, Configuration,
Diagnostics [2]. This document uses the seven-category view for the inventory because the
Platform Design figure is warned to still contain deprecated clusters.

### The R25-11 function-cluster inventory (release-stamped — this list changes)

R25-11 defines **20 function clusters across seven categories** [2]. Each is its own SWS
document; "daemon-based" means the reference design runs it as a separate daemon process.

| Category | Function clusters (R25-11) |
|---|---|
| **Runtime (5)** | Execution Management (`exec`, daemon); State Management; Log & Trace (`ara::log`); Core (`ara::core`); Operating System Interface (PSE51 surface) |
| **Communication (5)** | Communication Management (`ara::com`, daemon); Raw Data Stream (`ara::rds`); Network Management (daemon); Time Synchronization (daemon); **Automotive API Gateway** (VISS protocol, *added R24-11*) |
| **Storage (2)** | Persistency (`ara::per`); **Remote Persistency** (daemon, *added R25-11*) |
| **Security (3)** | Cryptography (`ara::crypto`, daemon); Intrusion Detection System Manager (IdsM, *added R21-11*); **Firewall** (daemon, *added R22-11*) |
| **Safety (2)** | Platform Health Management (`ara::phm`); **Safe Hardware Acceleration** (*added R25-11*) |
| **Configuration (2)** | Update & Configuration Management (UCM); **Vehicle UCM (V-UCM)** (*added R23-11*) |
| **Diagnostics (1)** | Diagnostic Management (`ara::diag`) |

The inventory is **not static across releases** — a "canonical list" must always be
release-stamped [2]. R25-11 added *Remote Persistency*, *Safe Hardware Acceleration*, and
Suspend-to-RAM in State Management. Earlier churn that firmware readers should know:
**R23-11 removed Identity and Access Management (IAM)**; **R21-11 removed RESTful
Communication** [2]. Do not present IAM or RESTful Communication as current clusters.

### Execution Management vs State Management — EM is a dumb enforcer, SM is the brain

This is the single most-misunderstood pair. **Execution Management (EM)** "starts,
configures, and stops Processes as configured in Function Group States using interfaces of
the Operating System" [2] — it is the entry point the OS launches at boot, and every other
cluster is, from EM's viewpoint, just an application it starts the same way "except for EM
itself" [2]. But EM does **not** decide *which* apps run or *when*: *"decisions on which
and when the application starts or terminates are not made by EM. A special FC, called
State Management (SM), is the controller, commanding EM"* [2]. SM owns the policy; EM only
enforces the mechanism.

The unit of composition is the **Function Group** — a named set of processes with a set of
states, where "A Function Group State defines a set of active Applications for any certain
situation." A modelled process belongs to exactly one Function Group but can appear in
several of that group's states. The elegant unification worth calling out: **a "Machine
State" is not a special concept — it is simply the Function Group State of a reserved group
named `MachineFG`**, in the one `PLATFORM_CORE` SoftwareCluster per machine [3]. At boot,
EM self-initiates the transition to the **Startup** machine state, brings up SM, then hands
"responsibility for Function Group state management … to State Management" [3]. SM must be
configured to run in every machine state, or the machine gets "stuck forever" [3].
Transition mechanics: SM calls `ara::exec::StateClient::SetState`; on a state change EM
"terminates running Processes and then starts Processes active in the new state before
confirming the state change" [3]; on a crash outside a transition EM sets the group to
**Undefined Function Group State** and calls SM's `undefinedStateCallback` [3].

If you reach for "EM ≈ systemd," stop — it breaks in five ways: (a) the *policy* of which
set runs is externalized to a separate safety-relevant cluster (SM), not encoded in unit
files; (b) the unit of composition is a full machine mode (Function Group State), not an
individual service target; (c) EM enforces **resource groups** (CPU/memory policing) and
supports **authenticated startup** from a trust anchor; (d) configuration is ARXML
Manifests, not `.service` files; (e) EM is the certified entry point under an ISO 26262
safety argument [2][3].

### The five manifests, and how "dynamic" production really is

Behaviour is defined by **Manifests** (ARXML, authored at integration time, transformed to
a platform-specific format read efficiently at startup [3]). There are **five kinds** [5]:
**Execution Manifest** (bundled with the executable: startup parameters, resource-group
assignment, which Function Group States a process runs in, execution dependencies,
scheduling), **Service Instance Manifest** (how a service maps to a transport — SOME/IP
instance IDs, endpoints, event groups), **Machine Manifest** (the machine "without any
applications running on it" — function groups & states, machine states, network/IP, OS
config), plus the **Raw Data Stream Manifest** and the **Software Distribution** manifest.

How dynamic is production, really? AP is "dynamic" *relative to CP*, but production
determinism stays high: the set of processes per state is fixed in manifests; which state
is active is arbitrated by SM; service discovery is the runtime-dynamic element, yet
integrators are expected to "ensure that all service dependencies are mapped to the State
Management configuration" [4]. The spec even discourages runtime coupling ("user-level
applications should not rely on Execution Dependencies unless strictly necessary"), and
dynamic memory is generally allocated at startup for freedom-from-interference. So
"dynamic" in practice means **deployment-time flexibility and OTA reconfiguration**, not
free-running runtime allocation and discovery [4].

### The C++ baseline (and the question that stays OPEN)

The ARA APIs (`ara::core` et al.) are specified against **C++14** — the historical
baseline. As of R23-11 onward, the standalone AUTOSAR "Guidelines for the use of the C++14
language" document was **removed from the standard set** (the PDF returns HTTP 404 for
R23-11, R24-11, R25-11; last present in R22-11) and folded into **MISRA C++:2023**, the
single successor coding standard, which targets **C++17** [6][7]. Many secondary sources
still present "AUTOSAR C++14" as a living, separate standard — it is not. **Whether R25-11
formally moves the compiled language baseline to C++17 is an OPEN QUESTION** — keep it
hedged; the notes could not confirm it from a primary R25-11 statement (see Open
questions).

---

## 3. `ara::com` — one API, several bindings, and the ROS 2 comparison

### Proxy/skeleton programming model

AP exposes **one** application communication API, `ara::com`, on a **proxy/skeleton**
model. R25-11 §7.1.2: *"The (service) proxy is the representative of the possibly remote
… service. It is an instance of a C++ class local to the application/client … The
(service) skeleton is the connection of the user provided service implementation to the
middleware transport infrastructure"* [1]. The app codes against `ara::com`; the integrator
chooses the wire binding in the manifest. A subtlety that matters: **serialization runs in
the execution context of the AA itself** (the binding is compiled into the application
binary, not a separate broker process) [1]. The API supports event/callback *and* polling
styles, synchronous and asynchronous method calls (C++ `std::future`/`std::promise`), and
"has zero-copy capabilities including the possibility for memory management in the
middleware" [1].

Service elements are **events, methods, fields, and triggers** [1]: an **event** is a
notification carrying data, delivered only to subscribed proxies; a **trigger** is the same
notification *without* a data payload (a data-less "something happened"); a **method** is a
client/server operation (request/response, or fire-and-forget with `requestNoReturn`); a
**field** is a value with up to three accessors — a notifier (behaves like an event
carrying the current value), a getter, and a setter [1].

### Bindings: SOME/IP vs DDS vs local IPC

`ara::com` is deployment-bound to one of several **network bindings**:

- **SOME/IP** — the automotive-native option: compact on-wire serialization plus
  **SOME/IP-SD** service discovery. It is connection- and ID-oriented (Service ID /
  Instance ID / Method-Event ID / Eventgroup ID), which will feel familiar from CAN/UDS
  thinking. Message types: REQUEST `0x00` / RESPONSE `0x80`, REQUEST_NO_RETURN `0x01`,
  NOTIFICATION `0x02` [11]. Subscription granularity is the **eventgroup**. SOME/IP-SD runs
  **over UDP multicast only** [12].
- **DDS binding — present since R18-03** (published 23 April 2018; *not* R18-10, a folklore
  correction the repo already made) [4][repo-constraints §1]. DDS is data-centric: you
  publish to a Topic and the middleware matches by type + QoS + name, with no explicit peer
  connection. The binding must comply with the DDS Minimum Profile, the RTPS wire protocol,
  and DDS-XTypes [5]. **Element → DDS mapping**: events and triggers → a **Topic +
  DataWriter**; methods and field getters/setters → a **DDS Service (DDS-RPC)** = a Request
  Topic + a Reply Topic; field notifiers → a Topic [8]. There is **one DDS
  DomainParticipant per service instance**, with Domain ID and `qosProfile` pulled from the
  manifest, and a Partition name `"ara.com://services/<svcId>_<svcInId>"` [7][10]. **QoS is
  manifest-driven, not fixed by the standard** — the spec defines *which* DDS entities exist
  and *that* they carry QoS, but the concrete reliability/durability/history values are a
  deployment choice [9]. **Two discovery modes** [6]: a lean `DomainParticipantUserDataQos`
  mode (rides the USER_DATA QoS of Domain Participants — creates no extra DDS entities), and
  a heavier `Topic` mode (announcements over a purpose-specific Topic; enables persistence,
  routing, durability). Proxy and skeleton must agree on the mode.
- **Local IPC / zero-copy** — `ara::com` promises "zero-copy capabilities," but the
  local/IPC wire is **implementation-specific**, not a standardized inter-vendor protocol
  (unlike SOME/IP and RTPS, which are). The dominant realization is **Eclipse iceoryx**, a
  low-level zero-copy shared-memory IPC ("plumbing") that higher layers wrap: it sits
  *under* both ROS 2 (via the `rmw_iceoryx` binding) and some `ara::com` implementations (via
  separate bindings), rather than being either API itself. (The old FOSDEM-2020 marketing
  line "fully compatible with the ROS 2 and Adaptive AUTOSAR APIs" is superseded by iceoryx's
  own current, narrower self-description [14].) For an MCU reader: think of a
  lock-free shared-memory ring between processes on one SoC, with pointers handed across via
  a routing daemon (iceoryx's RouDi) — no serialization.

**R25-11 currency for `ara::com`**: the two big retirements actually happened at **R23-11** —
**Raw Data Streaming was removed from `ara::com`** and **Communication Groups marked
OBSOLETE** in that release (Communication Groups had been introduced at R20-11; the
raw-data-streaming capability inside `ara::com` dated to R19-11). What **R25-11** did was
rework the `ara::com` C++ API against generated headers and finally delete the leftover
obsolete Communication Groups chapter text — it did not newly remove or obsolete anything
[2 (comm-note)]. Any teaching material listing "raw data streams" or "communication groups"
as current `ara::com` features is out of date. (Note the standalone *Raw Data Stream* function cluster
`ara::rds` in §2 still exists — it is the raw-data-streaming *inside* `ara::com` that was
removed.)

### `ara::com` ↔ `rclcpp` — the mapping a ROS 2 reader should carry

| `ara::com` (AP) | ROS 2 `rclcpp` | Note |
|---|---|---|
| Skeleton (offers service) | Publisher + Service server | offer-side |
| Proxy (consumes service) | Subscription + Service client | consume-side |
| Event | Topic publish/subscribe | closest 1:1 |
| Trigger | (no direct equiv; `std_msgs/Empty`) | data-less notify |
| Method (req/resp) | Service (`.srv`) | AP-DDS uses DDS-RPC |
| Field (notifier+get+set) | Topic + 2 services / a Parameter | no single ROS 2 equivalent |
| Manifest `qosProfile` | `rclcpp::QoS` / RMW QoS | both DDS QoS underneath |
| Binding chosen at deploy | RMW chosen (`RMW_IMPLEMENTATION`) | analogous indirection |

The single most transferable idea: **the application API is protocol-agnostic; DDS/SOME-IP
is a swappable binding underneath.** An engineer who understands ROS 2's `rmw`/DDS layering
already understands AP's binding layering.

### Shared DDS wire, but NOT plug-compatible

The repo's shipped claim — "the DDS wire family is what AUTOSAR Adaptive shares with ROS 2"
— is correct: both can speak DDS/RTPS. But sharing a wire *family* is **not** the same as
interoperating. Blockers to naive DDS-to-DDS: ROS 2 mangles topic names (`rt/…`,
`rq/…Request`, `rr/…Reply`) while AP-DDS uses `"ara.com://services/…"` partitions and its
own scheme; type construction differs (ROS 2 from `.msg`, AP from the ServiceInterface);
AP's USER_DATA discovery mode is something ROS 2 does not implement; and AP methods use
DDS-RPC where ROS 2 services use a different (also RTPS-based) convention [1]. So the
practical interop path is a **bridge/gateway** — an active 2024–2026 research area (a
dynamic SOME/IP-DDS bridge, ROS 2 ↔ SOME/IP bridges) [15-comm][16-comm]. A 2026 comparison
paper notes ROS 2 "lacks several concepts essential for series-production" (operation
modes, allocation, watchdog supervision) — which is *why* AP exists alongside ROS 2 rather
than replacing it [17-comm].

---

## 4. Lifecycle & serviceability — UCM, DM, SOVD, PHM, Persistency, DLT

### UCM — the update workflow, and who orchestrates OTA

The unit of update is the **Software Cluster**: AP can be extended "with new software
packages without re-flashing the entire ECU" [D3]. The per-machine **UCM**
(`ara::ucm::PackageManagement`) exposes a service interface with `TransferStart`,
`TransferData`, `TransferExit`, `ProcessSwPackage`, `Activate`, `VerifyUpdate`, `Finish`,
`Rollback`, `PrepareRollback`, `Cancel`, `RevertProcessedSwPackages`, and inventory getters
[D1]. The workflow is **Transfer → Process → Activate → (Verify/Finish or Rollback)**:

1. **Transfer** — stream the package (`TransferStart → TransferData → TransferExit`);
   `TransferStateType` moves `kTransferring → kTransferred` [D1].
2. **Process** — `ProcessSwPackage` unpacks, validates, writes the cluster
   (`kProcessing → kProcessed`); a newly added cluster reaches lifecycle state **kAdded** [D1].
3. **Activate** — the critical phase: "UCM is asking State Management for an update session.
   Once granted, UCM is requesting State Management to stop running processes from the
   outdated SoftwareClusters," then makes the updated clusters available; `VerifyUpdate`
   switches the affected Function Groups to **Verify** mode; a final `Finish` commits to
   **kPresent** [D1].

Software-Cluster lifecycle states are `kPresent=0x00`, `kAdded=0x01`, `kUpdating=0x02`,
`kRemoved=0x03` [D1]. **Rollback** restores a known-good state if activation fails, but the
spec also documents *failing rollback* (`UCM ROLLBACK FAILED`) — rollback is best-effort,
**not guaranteed** [D1]. For an MCU engineer this is the A/B-bank reflash idea, but
per-Software-Cluster and coordinated with a state machine rather than a bootloader.

Vehicle-wide OTA is orchestrated by **V-UCM (Vehicle UCM)** — the concept formerly called
"UCM Master," now split into its **own specification since R23-11** [D1][D2][D12]. V-UCM
coordinates the campaign: **backend interaction** (identify updatable clusters,
*authenticate the Vehicle Package*, confirm inter-cluster dependencies, "receive [packages]
and dispatch them to targeted ECUs"), **Vehicle State Manager interaction** (apply the
safety conditions the Vehicle Package demands), and **human-driver interaction** ("get
vehicle modification approval or consent from Human when configured") [D2]. The chain is:
**OEM backend → V-UCM (in-vehicle campaign coordinator) → subordinate per-machine UCM
instances** that do the actual Transfer/Process/Activate/Rollback [D1][D2].

### Diagnostic Management (`ara::diag`) — one cluster does DCM + DEM's jobs

*"The DM is a diagnostic server implementation that realizes a UDS server instance
according to ISO 14229-1 and SOVD according to ASAM"* [D3]. Since R19-03 the interface is
C++ (`ara::diag`), configured from the **Diagnostic Extract Template (DEXT)** [D3]. There is
**one Diagnostic Server Instance per Software Cluster**, and "all diagnostic server
instances share a single TransportLayer instance (e.g. DoIP on TCP/IP port 13400)" [D3].
The UDS services specified include `0x10`, `0x11`, `0x14`, `0x19`, `0x22`, `0x23`, `0x27`,
`0x28`, `0x29`, `0x2E`, `0x2F`, `0x31`, `0x34`–`0x37`, `0x3E`, `0x85` [D3]. Where CP splits
diagnostics into the DCM (communication) and DEM (fault memory) BSW modules over the PDU
Router, **AP merges both roles into one cluster**: DM's "response handling basically
resembles the functionality of the Dcm BSW module," but it also owns fault-memory behaviour,
all behind one `ara::diag` C++ API [D3].

**The transport nuance — get the phrasing exactly right.** Use: **DoIP (ISO 13400-2:2019,
incl. Amd 1:2023) is the only *standardized* UDS transport for the AP Diagnostic Manager;
the SWS explicitly permits a custom transport implementation** [D3][D4][orchestrator-verif
§4]. Verbatim: *"The DoIP protocol based on ISO 13400-2:2019 … or a custom implementation of
a transport protocol can be used"* [D4]. The same "DoIP or custom" concept is already in
R24-11 [D3]. The shorthand "DoIP-only" is acceptable only with the word "standardized"
nearby. And note the refuted folklore: a web claim that "R24-11 added CAN transport to
Adaptive DM" is a **hallucination** — DoIP-only-as-standard is unchanged verbatim across
R22-11/R23-11/R24-11/R25-11 [repo-constraints §2.9].

### SOVD — inside the DM, not a separate cluster

**SOVD (Service-Oriented Vehicle Diagnostics)** is a modern diagnostic API over
**HTTP/REST, JSON and OAuth**, self-describing (no dependency on an external ODX
description) with "UDS as a subset" [D7]. The critical architectural fact: **SOVD is
realized *inside* the Diagnostic Manager plus a SOVD Gateway — there is no separate "SOVD
functional cluster"** [D7]. Three blocks: the **SOVD Gateway** (an HTTP reverse proxy
routing on the URI entity path, configured statically or discovered via mDNS); the
**Diagnostic Manager as SOVD server** (each Diagnostic Server Instance is an SOVD
sub-component, reusing DEXT config); and **SOVD-to-UDS Translation** (an on-board client
translating SOVD ↔ UDS "based on predefined ODX definition … defined by ASAM" — the
legacy-ECU gateway pattern: HPC speaks SOVD outward, classic UDS ECUs are reached by
translation) [D7]. SOVD adds capabilities with no UDS equivalent: OAuth authorization,
proximity challenge, data-lists, logging, bulk data. **The ISO transition is mid-flight**:
R25-11's Diagnostics spec cites ISO 17978-3:2025 *and* :2026 and ASAM SOVD 1.1 (2026-01),
but warns "the SOVD API based on version 1.1 / ISO 17978-3:2026 is not yet (fully)
supported" [D4] — so "AP supports ISO 17978 SOVD" is only partly true today.

### PHM — supervision, and what got removed

**Platform Health Management (`ara::phm`)** is the AP analogue of CP's WdgM, required by
ISO 26262. It performs three supervisions [D5]: **Alive** (cyclic entities stay within
min/max timing), **Deadline** (a start-checkpoint → end-checkpoint transition within
min/max), and **Logical** (control-flow executes "in the sequence defined by the
programmer"). Apps report **Checkpoints** via `ReportCheckpoint`; statuses aggregate into a
**Global Supervision Status** per Function Group. On failure, **PHM notifies State
Management** (which decides and triggers the recovery — e.g. restart a Function Group);
"if no response by State Management is received in time, the PHM will do its own
countermeasures" via the **hardware watchdog** [D5]. Two release-stamped evolutions to
keep: PHM's SupervisionStatus literal indices were aligned with CP WdgM types (R22-11), and
**Health Channels are obsolete** (set obsolete R21-11, "Removed" in the R24-11 change
history) [D5][orchestrator-verif §5] — teaching material presenting health channels as a
live PHM input is out of date.

### Persistency (`ara::per`) and Log & Trace (DLT)

`ara::per` provides **Key-Value Storage** and **File Storage** [D6]. Its update-relevant
guarantees: **redundancy** "can be configured to use replication of stored data, CRCs, or
Hashes," with hash verification via the Crypto API against a manifest hash, plus explicit
recovery of corrupted data [D6]; and defined **Installation, Update, Finalization, and
Roll-Back of Persistent Data** as first-class phases across Software-Cluster updates
(`SWS_PER_00396` restores prior data after a failed update) [D6]. The guarantee is
*defined install/update/finalize semantics with a rollback path and integrity
protection* — not transparent automatic migration. **Log & Trace** exposes `ara::log` over
the **DLT** protocol [D13]; note that SOVD logging is *not* standardized through `ara::log`
and is "implemented based on the platform vendor's guidelines" [D7].

---

## 5. Reality check, mid-2026 — OSes, vendors, certification, silicon, open efforts

### The OS underneath

AP needs a POSIX OS beneath it, and that OS is a **separate procurement and certification
decision** from the AP middleware. **QNX (BlackBerry)** is the de-facto safety OS: QNX OS
for Safety is ISO 26262 **ASIL-D** certified; commercial market-research firms estimate QNX
at ~35–38% of the **overall automotive-OS market** — a share by OS type (spanning
infotainment/cockpit/telematics as well as safety), not a distinct "safety-critical"
sub-segment, and not an official QNX figure [V9]. **Linux** carries most non-safety/ADAS compute,
but stock Linux cannot itself certify above ~ASIL-B; vendors reach safety by pairing it
with a **certified hypervisor** or safety companion (Elektrobit's EB corbos Linux markets
itself as "the first and only Linux OS solution to comply with ASIL B/SIL 2," achieved via
an exclusive hypervisor) [V8]. **PikeOS (SYSGO), INTEGRITY (Green Hills), VxWorks (Wind
River)** all appear as supported OS-abstraction targets [V5].

### Commercial stacks and certification — the exact hedge

The repo's summary — **"ASIL-B shipping, ASIL-D programs underway"** — is **confirmed
accurate for mid-2026**. Keep it in exactly that shape. Dated evidence:

| Vendor / product | OS support | Stated safety (mid-2026) |
|---|---|---|
| **Vector MICROSAR Adaptive** (+ MICROSAR Adaptive Safe) | Linux, QNX, PikeOS, INTEGRITY, VxWorks, Android (OSAL) [V5] | Safe variant **ASIL-B available, in first series projects**; Vector's own **ASIL-D target 2026** (stated without QNX attribution); a *separate* Vector–QNX partnership (June 2024) targets ASIL-D on QNX OS for Safety, no completion date given [V4][V6] |
| **ETAS RTA-VRTE** | POSIX; hypervisor for mixed CP/AP [V15] | **ISO 26262 ASIL-B certified by TÜV SÜD, ~March 2025**, "on the first attempt" [V16] |
| **Qorix** (Adaptive + Performance) | POSIX; SoCs incl. Qualcomm [V17] | **TÜV SÜD ASIL-B certified, Aug 2025**; "one of the few providers with a certified Adaptive AUTOSAR stack" [V17][V18] |
| **Elektrobit EB corbos AdaptiveCore** | POSIX; own type-1 hypervisor [V8] | hypervisor **ASIL-B certified** (TÜV SÜD, 2024); EB corbos Linux ASIL-B/SIL2. AdaptiveCore itself makes **no current ASIL-D claim** — "up to ASIL-D" is a stale 2017 press-release line; it is paired with a separately ASIL-D-certified OS (EB's own ASIL-D certs belong to Classic/EB tresos) [V8] |
| **Wind River** AUTOSAR Adaptive | VxWorks / Linux | ASIL-D **program** (announced 2019; shipped certificate unverified) [V7] |

Key distinction for any downstream slide: separate **"ISO 26262-compliant / developed
according to ASIL-x"** (a process/design claim the vendor makes) from **"certified by TÜV
SÜD at ASIL-x"** (an external assessment). ETAS and Qorix hold the latter at **ASIL-B**;
"up to ASIL-D" is usually the former. **No fully certified, end-to-end ASIL-D AP middleware
stack ships as of mid-2026** — the ASIL-D story is consistently *AP middleware + QNX OS for
Safety (ASIL-D) + safety hypervisor + vendor safety case* [V4][V9]. Note **Qorix** as new
since the repo's last pass: a KPIT + ZF joint venture with Qualcomm as a strategic
shareholder, and a lead contributor bringing Eclipse S-CORE to production [V17][V19].

### Target silicon

AP targets application-class HPC SoCs, not MCUs: **NVIDIA DRIVE Orin** (mainstream today)
and **DRIVE Thor** (Blackwell-based, ~2000 TOPS, consolidating ADAS + cockpit) [V11];
**NXP S32G** (vehicle-network/gateway + safety, "supported by the AUTOSAR Adaptive
standard," runs Linux on quad-A53 + triple-lockstep M7) [V10]; **Qualcomm Snapdragon Ride /
Ride Flex / Ride Elite** [V10-note]; and **TI TDA4x** (Jacinto, common ADAS target). The
recurring split the firmware audience will recognize: **AP middleware + QNX on an Arm
application core, with a lockstep safety island (Cortex-R/M) or companion MCU running
Classic AUTOSAR** for the hard-real-time/ASIL-D control. Repo-pinned silicon facts that
must not be contradicted: the **Orin-generation safety MCU is Infineon AURIX TC397X**;
the **Thor-generation companion/safety MCU is Renesas RH850U2A16** with Vector MICROSAR
Classic as reference integration — **never say Thor uses AURIX** [orchestrator-verif §3].

### The 2025–26 strategic shift: Eclipse S-CORE and SOAFEE

**Eclipse S-CORE (Safe Open Vehicle Core)** launched 2025-06-12 as "the automotive
industry's first open source core stack for software-defined vehicles" [V12] — a
safety-aligned, Apache-licensed, **dual-language (C++ and Rust)** middleware intended to be certifiable
(ISO 26262 / ISO 21434). The striking part is the roster: BMW, Mercedes-Benz, Bosch, ETAS,
Vector, Volkswagen, ZF, plus Qualcomm, QNX, Red Hat, Stellantis, Infineon — **the same
OEM/Tier-1 members who run AUTOSAR** [V12][V21]. They are hedging, not defecting: AUTOSAR
and S-CORE are cooperating (AUTOSAR wants an automotive-grade reference implementation;
S-CORE lists "Adaptive AUTOSAR integration for early completeness"), and Qorix frames it as
"S-CORE is the blueprint; we build the actual structure" [V22][V24]. Rust is already in
S-CORE while AP is still debating it [V22]. Best taught as *an open-source challenger the
AUTOSAR members themselves are building, aiming to co-exist with / partially replace AP
middleware.*

**SOAFEE (Scalable Open Architecture For the Embedded Edge)** is an **Arm-led industry SIG**
(since Sept 2021) that defines a **cloud-native architecture** — containers, hypervisors,
Kubernetes/K3s orchestration, CI/CD ("DevOps in the cloud, deploy at the edge") — for
**mixed-criticality SDV workloads**. It is **complementary, not competing** with AUTOSAR
(the two collaborate as peers inside the SDV Alliance). Note its published
blueprints/reference implementations (EWAOL, Open AD Kit/Autoware, AosEdge, RHIVOS)
demonstrate *generic* containerized workloads, not AUTOSAR applications — running an AP stack
as a container is a **demonstrated pattern**, not part of SOAFEE's own definition [V14].
Teach SOAFEE as the deployment/orchestration environment, AP as one of the **payloads** it
can host.

### Learning options

The **official AP Demonstrator** is an "exemplary implementation … available to all the
partners," informally reviewed with "no strict quality assurance" — effectively
**members-only**, not a clean public teaching artifact [V3]. The most accessible hands-on
open artifact is **`github.com/langroodi/Adaptive-AUTOSAR`** — an **MIT-licensed Linux
simulator** of AP interfaces (`ara::com`-style comms, diagnostics/DoIP/OBD-II, health
management), C++14/CMake, explicitly educational [V25]. Treat it as illustrative, not a
real AP; for this repo's ROS 2 audience it is the natural thing to contrast with
`rclcpp`/DDS. (A second, spec-oriented codebase: `github.com/insooth/autosar-adaptive`
[V26].)

---

## 6. R25-11 currency notes for AP

A consolidated "what changed / what to not say" list for anything shipping in 2026:

- **Release**: current is **R25-11** (2025-11-27; presented 4 Dec 2025), a minor release,
  superseding R24-11 [1][15].
- **Function-cluster inventory (20)**: R25-11 **added** Remote Persistency, Safe Hardware
  Acceleration, Suspend-to-RAM (SM). Historically **removed**: IAM (R23-11), RESTful
  Communication (R21-11) — do not present these as current [2].
- **`ara::com`**: the retirements landed at **R23-11** — **Raw Data Streaming removed from
  `ara::com`** and **Communication Groups marked OBSOLETE** (Comm Groups introduced R20-11; RDS in
  `ara::com` since R19-11). **R25-11** only reworked the `ara::com` C++ API against generated headers
  and deleted the leftover obsolete text [2-comm].
- **Diagnostics transport**: **DoIP is the only *standardized* UDS transport; custom
  transport is explicitly permitted** — unchanged verbatim through R25-11 [D4]. Do not
  repeat "R24-11 added CAN."
- **SOVD**: R25-11 cites ISO 17978-3:2025/2026 and ASAM SOVD 1.1, but 1.1/ISO "not yet
  (fully) supported" — transition mid-flight [D4].
- **PHM**: Health Channels obsolete (R21-11) and Removed (R24-11) [D5].
- **V-UCM**: "UCM Master" is gone by that name; V-UCM is its own spec since R23-11 [D1][D2].
- **C++**: standalone AUTOSAR C++14 Guidelines removed (404 since R23-11), merged into MISRA
  C++:2023 (targets C++17); C++14 remains the historical ARA API baseline. **Whether R25-11
  moves the compiled baseline to C++17 stays OPEN** [6][7].
- **DDS on Classic Platform** (context, not AP): R25-11 newly extends Events/Methods/Fields
  management to DDS on *CP* and adds a DDS Transformer BSW module — but this is a
  **standard-level concept new in R25-11 with no evidence yet of a shipping vendor
  implementation** [orchestrator-verif §1]. Mentioned only so the deck does not conflate it
  with AP's long-standing (R18-03) DDS binding.

---

## Key claims

| # | Claim | Source URL | Confidence |
|---|---|---|---|
| 1 | Current release is R25-11 (2025-11-27, presented 4 Dec 2025), minor, supersedes R24-11 | https://www.autosar.org/news-events/detail/release-r25-11-is-now-available | high |
| 2 | AP exists because CP cannot serve HPC ECUs; provides HPC + OTA | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf | high |
| 3 | AP is not a new OS; it defines an execution context + OS Interface on POSIX | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf | high |
| 4 | AAs are POSIX processes running on ARA, restricted to the PSE51 single-process profile | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf | high |
| 5 | R25-11 has 20 function clusters in 7 categories | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf | high |
| 6 | R25-11 added Remote Persistency + Safe HW Acceleration; IAM removed R23-11, RESTful removed R21-11 | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf | high |
| 7 | EM starts/configures/stops Processes per Function Group State via OS interfaces | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf | high |
| 8 | SM decides which/when apps run; EM does not (EM = enforcer, SM = policy) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf | high |
| 9 | A Machine State is the Function Group State of reserved group MachineFG (PLATFORM_CORE) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf | high |
| 10 | Behaviour defined by five manifest kinds (Execution/Service-Instance/Machine/Raw-Data-Stream/Software-Distribution) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf | high |
| 11 | "Dynamic" = deploy-time flexibility + OTA, not free-running runtime allocation/discovery | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf | med |
| 12 | Standalone AUTOSAR C++14 Guidelines removed (404 R23–R25); merged into MISRA C++:2023 (C++17) | https://www.autosar.org/news-events/detail/misra-consortium-announce-integration-of-autosar-c-coding-guidelines-into-updated-industry-standard | high |
| 13 | `ara::com` uses proxy/skeleton; serialization runs in the AA's execution context; zero-copy capable | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 14 | Service elements = events, methods, fields, triggers (trigger = data-less event) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 15 | DDS binding present since R18-03 (published 23 Apr 2018) | https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds | high |
| 16 | DDS mapping: events/triggers→Topic+DataWriter; methods & field get/set→DDS Service (DDS-RPC); field notifier→Topic | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 17 | DDS QoS is manifest-driven (qosProfile), not fixed by the spec | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 18 | Two DDS discovery modes: DomainParticipant USER_DATA QoS, and Topic-based | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 19 | R23-11 removed Raw Data Streaming from ara::com and marked Communication Groups obsolete (Comm Groups introduced R20-11; RDS in ara::com since R19-11); R25-11 only deleted the leftover obsolete text | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf | high |
| 20 | Local/IPC zero-copy binding is implementation-specific; iceoryx is the common realization — a low-level zero-copy IPC that sits under both AP and ROS 2 via separate bindings, not directly either API | https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 | high |
| 21 | Shared DDS/RTPS wire family, but AP-DDS and ROS 2 are NOT plug-compatible; interop needs bridges | https://doi.org/10.3390/electronics14183635 | med-high |
| 22 | UCM workflow: Transfer → Process → Activate → Verify/Finish or Rollback; SW-Cluster states kPresent/kAdded/kUpdating/kRemoved | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf | high |
| 23 | Rollback is best-effort (UCM ROLLBACK FAILED documented), not guaranteed | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf | high |
| 24 | "UCM Master" is now V-UCM, its own spec since R23-11; orchestrates campaign backend→ECUs, driver consent | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf | high |
| 25 | DM realizes a UDS server (ISO 14229-1) + SOVD; merges CP DCM+DEM roles; one server instance per Software Cluster | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf | high |
| 26 | DoIP is the only *standardized* UDS transport for AP DM; custom transport explicitly permitted (R24-11 & R25-11) | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf | high |
| 27 | SOVD = HTTP/REST/JSON/OAuth, "UDS as a subset"; realized inside DM + SOVD Gateway, not a separate cluster | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf | high |
| 28 | R25-11 cites ISO 17978-3:2025/2026 & ASAM SOVD 1.1; 1.1/ISO "not yet (fully) supported" | https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf | high |
| 29 | PHM does Alive/Deadline/Logical supervision; notifies SM, falls back to HW watchdog; Health Channels removed | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf | high |
| 30 | ara::per: KVS + File Storage; redundancy via replication/CRC/hash; defined install/update/finalize/rollback of data | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Persistency.pdf | high |
| 31 | AP runs on a POSIX OS; QNX = de-facto ASIL-D safety OS (~35–38% of the overall automotive-OS market by analyst estimates — an OS-type share, not a safety-only figure); Linux via hypervisor | https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/ | med |
| 32 | ASIL-B AP stacks shipping/certified (Vector, ETAS TÜV SÜD ~March 2025, Qorix TÜV SÜD Aug 2025); no fully certified ASIL-D middleware found | https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ | high |
| 33 | Qorix = KPIT+ZF JV (Qualcomm strategic shareholder); TÜV SÜD ASIL-B, Aug 2025 | https://www.qorix.ai/press-release/tuv-certified-qorix-is-one-of-the-few-providers-with-a-certified-adaptive-autosar-stack/ | high |
| 34 | Eclipse S-CORE launched 2025-06-12: dual-language (C++ and Rust), Apache-licensed open safety middleware by AUTOSAR members; cooperating with AUTOSAR | https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open | high |
| 35 | SOAFEE (Arm-led SIG) defines a cloud-native architecture (containers/hypervisors/K8s, CI/CD) for mixed-criticality SDV workloads; complementary to AUTOSAR — running AP as a container is a demonstrated pattern, not SOAFEE's definition | https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf | med |
| 36 | Official AP Demonstrator is members-only, informal QA; langroodi/Adaptive-AUTOSAR (MIT, Linux sim) is the accessible learning artifact | https://github.com/langroodi/Adaptive-AUTOSAR | high |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf — Explanation of Adaptive Platform Design (Doc 706), AP R25-11 — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf — Explanation of Adaptive Platform Software Architecture (Doc 982), AP R25-11 — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf — Specification of Execution Management (Doc 721), AP R25-11 — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf — Specification of Manifest (Doc 713), AP R25-11 — AUTOSAR — primary
6. https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_RS_CPP14Guidelines.pdf — Guidelines for the use of the C++14 language (last release present; 404 in R23-11+) — AUTOSAR — primary
7. https://www.autosar.org/news-events/detail/misra-consortium-announce-integration-of-autosar-c-coding-guidelines-into-updated-industry-standard — MISRA/AUTOSAR C++ integration announcement — AUTOSAR/MISRA — primary; https://www.perforce.com/blog/qac/misra-cpp-2023-intro — MISRA C++:2023 targets C++17 — Perforce — vendor/secondary
8. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf — Specification of Operating System Interface (PSE51 profile), AP R25-11 — AUTOSAR — primary
9. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_CommunicationManagement.pdf — Specification of Communication Management (Doc 717), AP R25-11 — AUTOSAR — primary
10. https://www.rti.com/blog/autosar-adaptive-platform-18.03-now-with-dds — AUTOSAR Adaptive Platform 18.03: Now with DDS! — RTI — vendor
11. https://www.rti.com/blog/status-of-dds-in-autosar — Connectivity at the Core: The Status of DDS in AUTOSAR — RTI — vendor
12. https://www.autosar.org/fileadmin/standards/R19-03/FO/AUTOSAR_PRS_SOMEIPServiceDiscoveryProtocol.pdf — SOME/IP Service Discovery Protocol Specification — AUTOSAR — primary
13. https://www.omg.org/spec/DDS-RPC/1.0 — RPC over DDS 1.0 — OMG — primary (referenced by the CM spec)
14. https://www.apex.ai/post/eclipse-iceoryx-blueberry-speeds-up-autosar-and-ros-2 — iceoryx speeds up AUTOSAR and ROS 2 — Apex.AI — vendor
15. https://doi.org/10.3390/electronics14183635 — A Dynamic Bridge Architecture for Interoperability Between AUTOSAR Adaptive and ROS2 (2025) — MDPI Electronics — peer-reviewed
16. https://doi.org/10.3390/electronics13071303 — Autonomous Driving System with Integrated ROS2 and Adaptive AUTOSAR (ASIRA, 2024) — MDPI Electronics — peer-reviewed
17. https://arxiv.org/html/2604.22576 — A Comparison of ROS 2 and AUTOSAR AP Against Industry-Elicited Automotive Middleware Requirements (2026) — arXiv preprint — secondary/preprint
18. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf — Specification of Update and Configuration Management (Doc 888), AP R24-11 — AUTOSAR — primary
19. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf — Specification of Vehicle Update and Configuration Management (Doc 1090), AP R25-11 — AUTOSAR — primary
20. https://www.autosar.org/fileadmin/standards/R23-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf — Vehicle UCM, AP R23-11 (first split release) — AUTOSAR — primary
21. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf — Specification of Diagnostics (Doc 723), AP R24-11 — AUTOSAR — primary
22. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf — Specification of Diagnostics, AP R25-11 — AUTOSAR — primary
23. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf — Explanation of Service-Oriented Vehicle Diagnostics (Doc 1064), AP R24-11 — AUTOSAR — primary
24. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf — Specification of Platform Health Management (Doc 851), AP R24-11 — AUTOSAR — primary
25. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Persistency.pdf — Specification of Persistency, AP R24-11 — AUTOSAR — primary
26. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_LogAndTrace.pdf — Specification of Log and Trace, AP R24-11 — AUTOSAR — primary
27. https://www.iso.org/standard/85133.html — ISO 17978-1 Road vehicles — SOVD Part 1 — ISO — primary
28. https://www.vector.com/gb/en/news/news/vector-and-blackberry-qnx-cooperation-for-best-in-class-solution-of-safe-systems-in-sdvs/ — Vector & QNX cooperation for safe SDVs — Vector — vendor
29. https://www.vector.com/int/en/products/products-a-z/embedded-software/microsar-adaptive/ — MICROSAR Adaptive product page — Vector — vendor
30. https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ — Safe ASIL-B AUTOSAR Adaptive for HPC available — Vector — vendor
31. https://www.etas.com/ww/en/products-services/vehicle-software-platform/rta-vrte/ — RTA-VRTE product page — ETAS — vendor
32. https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ — RTA-VRTE ASIL-B TÜV SÜD certification (~March 2025) — ETAS — vendor
33. https://www.qorix.ai/press-release/tuv-certified-qorix-is-one-of-the-few-providers-with-a-certified-adaptive-autosar-stack/ — Qorix TÜV SÜD ASIL-B (Aug 2025) — Qorix — vendor
34. https://autotechinsight.spglobal.com/news/5283287/ — Qorix ASIL-B certification (independent) — S&P Global — secondary
35. https://www.kpit.com/news/kpit-zf-join-hands-to-promote-an-independent-company-qorix/ — KPIT + ZF form Qorix — KPIT — vendor
36. https://www.elektrobit.com/products/ecu/eb-corbos/adaptivecore/ — EB corbos AdaptiveCore — Elektrobit — vendor
37. https://www.automotiveworld.com/news-releases/wind-river-autosar-adaptive-automotive-software-ready-for-iso-26262-asil-d-certification-program/ — Wind River AP ASIL-D program (2019) — Automotive World — secondary
38. https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/ — Vehicle OS Wars (QNX share) — VVDN — secondary
39. https://linuxgizmos.com/nxps-linux-driven-safety-critical-automotive-soc-mixes-cortex-a53-with-a7/ — NXP S32G Linux/AP support — LinuxGizmos — secondary
40. https://developer.nvidia.com/drive/agx — DRIVE AGX / Orin / Thor platform — NVIDIA — vendor
41. https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open — Eclipse launches S-CORE — Eclipse Foundation — primary
42. https://projects.eclipse.org/projects/automotive.score — Eclipse Safe Open Vehicle Core project — Eclipse Foundation — primary
43. https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together — S-CORE newsletter (members, QNX OS) — Eclipse Foundation — primary
44. https://beza1e1.tuxen.de/oss_vs_std.html — S-CORE vs AUTOSAR (Rust) — A. Bergmann blog — secondary
45. https://www.adt.media/software-defined-vehicles/score-is-the-blueprint-we-build-the-actual-structure/2580292 — Qorix on S-CORE to production — adt.media — secondary
46. https://www.arm.com/company/success-library/made-possible/soafee — SOAFEE cloud-native architecture — Arm — vendor
47. https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf — SDV Alliance Integration Blueprint — COVESA/SDV Alliance — primary
48. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf — Adaptive Platform Release Overview (Demonstrator terms) — AUTOSAR — primary
49. https://github.com/langroodi/Adaptive-AUTOSAR — Adaptive-AUTOSAR Linux simulator (MIT) — GitHub/langroodi — secondary
50. https://github.com/insooth/autosar-adaptive — AUTOSAR Adaptive spec implementation — GitHub/insooth — secondary

## Open questions

*(Merged and deduped across the four notes; best-guess labels preserved.)*

1. **Exact compiled C++ language baseline in R25-11.** The Platform Design doc names "C++"
   with no ISO year; C++14 is the historical API baseline and MISRA C++:2023 (the successor
   guideline) targets C++17. *Best guess (labeled guess): `ara::` APIs still assume C++14 as
   the minimum, with C++17 now permitted/expected via MISRA C++:2023* — not verified in a
   primary R25-11 statement; needs the R25-11 RS_General / SWS_Core language clause.
2. **Precise PSE51 include/exclude list as AUTOSAR scopes it.** The AP rationale and the IEEE
   1003.13 general definition were quoted, but an itemized PSE51 API table was not extracted
   from the R25-11 OperatingSystemInterface SWS; the `fork`/multi-process exclusion is
   standard IEEE, not re-verified line-by-line against R25-11.
3. **How much runtime dynamism is *permitted* vs *typical*.** The spec constrains
   dependencies/discovery and expects static mapping, but the exact bound on runtime dynamic
   allocation / late service discovery in a *safety* configuration is largely project/OEM
   policy and ASIL-driven, not a single normative number.
4. **Production deployment of the DDS binding on-vehicle.** Tooling (RTI Connext binding) and
   demonstrators are confirmed, but no primary source names a shipping production vehicle
   whose AP ECUs use the DDS binding on the wire rather than SOME/IP. *Best guess: SOME/IP
   still dominates production AP inter-ECU links; DDS is used mainly where AD/HPC stacks meet
   AP.* Needs a vendor case study.
5. **Exact trigger semantics** (fully data-less vs minimal payload). Glossary text for
   "Trigger" was truncated in extraction and mirrors "Event." *Guess: a trigger carries no
   application payload.* Medium confidence.
6. **Rust `ara::com`.** R25-11 released "code for Rust on adaptive platform," but whether that
   includes a Rust `ara::com` binding surface (relevant to a future ROS 2 ↔ AP comparison in
   Rust) was not verified.
7. **Whether any ROS 2 ↔ AP bridge is used beyond academia (series production)** — unverified.
8. **Whether R25-11's subordinate UCM SWS changed the lifecycle enum or added methods** vs
   R24-11. R24-11 UCM was read in full; R25-11 UCM (196 pp) only skimmed — workflow appears
   unchanged but was not diffed method-by-method.
9. **Full authoritative, mandatory-vs-optional UDS service list for AP DM**, and whether
   R25-11 added services (e.g. `0x24`, `0x2C`). *Guess: the set is stable; unverified.*
10. **Publication status of ISO 17978-1/-3** — catalog pages show ISO 17978-1:2026 and
    DIS/2025 for Part 3; the paywalled text was not opened to confirm exact dates or whether
    Part 2 exists.
11. **CAPI (Common Adaptive Platform Implementation)** was highlighted at the R25-11 event as
    a "certification-ready" reference AP implementation; its exact relationship to the
    clusters (esp. certified UCM/DM) was not verifiable from primary specs — out of scope
    (vendor/implementation).
12. **Has any vendor achieved a *certified* (not merely "compliant up to") ASIL-D full AP
    middleware stack by mid-2026?** ASIL-B certificates found (ETAS, Qorix); ASIL-D
    plans/claims only (Vector's own 2026 target; Elektrobit's "up to ASIL-D" is a stale 2017
    press-release line, not on current EB pages). *Best guess: no — ASIL-D at
    the middleware level is still in progress; ASIL-D today lives in the OS (QNX) and
    hypervisor layers.*
13. **Which OEM production programs run AP vs S-CORE vs in-house.** Mercedes MB.OS and
    VW/CARIAD are public SDV programs and both OEMs are in S-CORE, but the specific
    OEM+vendor+AP production pairing could not be confirmed from primary OEM sources. *Guess:
    both use AP for some ECUs today and are steering future platforms toward S-CORE.*
14. **Exact OS under each certified stack** — ETAS/Qorix press did not name the certified
    configuration's OS. *Guess: QNX for the ASIL path, Linux+hypervisor for mixed-criticality.*
15. **TI TDA4x + certified AP combo** — a common ADAS target, but no specific vendor's AP
    certification on it was verified.

*Fact-checked 2026-07-15 (workflow run wf_4748cedc-22d, 97 claims: 79 correct / 16 partially correct / 2 wrong — all corrected in place; full findings in autosar/research/notes/fact-check-findings-2026-07-15.md).*
