# AUTOSAR Adaptive Platform — Philosophy, Architecture, and Function Clusters (R25-11)

*Research notes for embedded/firmware engineers new to automotive software platforms. All primary sources are the AUTOSAR AP R25-11 standard PDFs unless noted. Compiled 2026-07-15.*

## Executive summary

AUTOSAR Adaptive Platform (AP) is a **middleware-and-services layer that runs on top of a POSIX operating system** — it is explicitly *not* a new OS [1]. It exists because deeply-embedded Classic Platform (CP) cannot serve high-performance-computing (HPC) ECUs driving Ethernet, many-core/GPU/FPGA hardware, service-oriented functions (ADAS, connectivity), and over-the-air (OTA) updates [1]. Adaptive Applications are ordinary **POSIX processes** written in **C++**, linked against **ARA** (AUTOSAR Runtime for Adaptive Applications) and restricted to the **POSIX PSE51** single-process profile [1]. The current release is **R25-11** (published 2025), confirmed against the R25-11 document set [2][3]. The architecture is a set of **Functional Clusters (FCs)** — 20 in R25-11 across seven categories [2]. Execution Management (EM) starts/stops processes according to **Function Group States** (a Machine State is just the state of the special `MachineFG` group); **State Management (SM)** decides *which* state, EM only enforces *how* [3][4]. Behaviour is defined by **Manifests** (Execution / Machine / Service-Instance + Raw-Data-Stream + Software-Distribution), authored at integration time [5]. The AUTOSAR C++14 coding guidelines have been **removed from the standard set** and folded into **MISRA C++:2023** [6][7].

## 1. Why AP exists — philosophy and technology drivers

The Platform Design explanation states the motivation directly: *"The AUTOSAR Classic Platform (CP) standard addresses the needs of deeply-embedded ECUs, while the needs of ECUs described above cannot be fulfilled. Therefore, AUTOSAR specifies a second software platform, the AUTOSAR Adaptive Platform (AP). AP provides mainly high-performance computing and communication mechanisms and offers flexible software configuration, e.g. to support software update over-the-air."* [1]

Two technology drivers are named: **Ethernet** (higher bandwidth, switched, point-to-point — CP is optimised for legacy CAN and "cannot fully utilise" Ethernet) and **processors** ("Manycore processors with tens to hundreds of cores, GPGPU … FPGA, and dedicated accelerators", heterogeneous computing, constrained by Pollack's Rule) [1]. AP's four design characteristics for a firmware engineer's mental model: **C++** ("now the language of choice … in performance critical complex applications"), **SOA** (service-oriented architecture, location-transparent whether the peer is local or on a remote AP instance), **updateability/OTA**, and **agile** development (incrementally scalable, updatable after deployment) [1]. Contrast with CP: CP is statically scheduled, signal/PDU-oriented, no dynamic memory, runs on an MCU with an OSEK/AUTOSAR-OS RTOS. AP is process-oriented, service-oriented, allows dynamic memory (mostly at startup), and runs on an MPU-class SoC under a POSIX OS.

## 2. "AP is middleware on an OS, not an OS"

This is a load-bearing framing that the repo audience must get right. The Operating System chapter states: *"The Adaptive Platform does not specify a new Operating System for highly performant processors. Rather, it defines an execution context and Operating System Interface"* [1]. *"There are several operating systems on the market, e.g. Linux, that provide POSIX compliant interfaces."* [1] The OS (Linux, QNX, PikeOS, VxWorks, Integrity, etc.) provides scheduling, resource management and IPC; AP's Functional Clusters are ordinary processes on top of it. The AP OS is *required* to provide **multi-process POSIX** capability [1], and the Machine may be *"a real physical machine, a fully-virtualized machine, a para-virtualized OS, an OS-level-virtualized container or any other virtualized"* environment [1] — AP presents a "consistent platform view regardless of any virtualization technology."

## 3. ARA — AUTOSAR Runtime for Adaptive Applications

*"The Adaptive Applications (AA), or just Applications run on top of ARA, AUTOSAR Runtime for Adaptive applications. ARA consists of application interfaces provided by Functional Clusters"* [1]. From the application's viewpoint the FCs "just provide specified C++ interface" — the app cannot tell whether an interface belongs to Foundation or Services [1]. ARA APIs live in the `ara::` C++ namespaces (e.g. `ara::com`, `ara::exec`, `ara::core`, `ara::log`, `ara::crypto`, `ara::diag`, `ara::per`, `ara::phm`). Note the two overlapping taxonomies:
- **Platform Design (doc 706)** logical view groups FCs into *Adaptive Platform Foundation*, *Adaptive Platform Services*, *Standard Application/Interfaces*, and *Vehicle Services* [1].
- **SW Architecture (doc 982)** building-block view groups the *same* clusters into seven **technical categories**: Runtime, Communication, Storage, Security, Safety, Configuration, Diagnostics [2] (used for the inventory in §4).

## 4. Full Functional-Cluster inventory — R25-11 (20 clusters)

From the SW Architecture doc's Building Block View (Figures 9.2–9.103) [2]. Each FC is specified in its own SWS document. "Daemon-based" means the reference design implements it as a separate daemon process.

**Runtime (5)**
1. **Execution Management** (`exec`, daemon) — controls Processes of the platform and AAs: starts, configures (resource groups, CPU/memory limits), and stops Processes per Function Group State; entry point started by the OS at boot [2].
2. **State Management** — controls which Function Group / Machine States are active; arbitrates overall machine behaviour and commands EM [2][4].
3. **Log and Trace** — `ara::log` logging/tracing (DLT) for platform and applications [2].
4. **Core** — `ara::core` foundational types (`ErrorCode`, `Result`, `Future`, `String`, `Vector`, `InstanceSpecifier`), initialization/`Abort` [2].
5. **Operating System Interface** — exposes the POSIX **PSE51** profile to applications; the single-process API surface [2].

**Communication (5)**
6. **Communication Management** (daemon) — `ara::com`, service-oriented communication, SOME/IP, service discovery, language/network bindings (sibling agent covers depth).
7. **Raw Data Stream** — `ara::rds`, byte-stream (non-SOME/IP) transport, e.g. sensor data.
8. **Network Management** (daemon) — coordinated network sleep/wake (UDP-NM).
9. **Time Synchronization** (daemon) — synchronized time bases (`ara::tsync`).
10. **Automotive API Gateway** (daemon) — standardized data-centric vehicle access via the **VISS** protocol; *added in R24-11* [2][8].

**Storage (2)**
11. **Persistency** — `ara::per` key-value and file storage for AAs.
12. **Remote Persistency** (daemon) — persistency backed by a remote/off-board store; *added in R25-11* [2][8].

**Security (3)**
13. **Cryptography** (daemon) — `ara::crypto`, key management and crypto primitives.
14. **Intrusion Detection System Manager** (daemon) — collects/forwards standardized security events (IdsM); *added R21-11* [2][8].
15. **Firewall** (daemon) — enable/disable firewall rules on the TCP/IP stack; *added R23-11* [2][8].

**Safety (2)**
16. **Platform Health Management** — `ara::phm`, supervision (alive/deadline/logical), health channels, watchdog interaction.
17. **Safe Hardware Acceleration** — safe API for HW accelerators (GPU/NPU); *added R25-11* [2][8].

**Configuration (2)**
18. **Update and Configuration Management (UCM)** — on-board software update/package management (sibling covers depth).
19. **Vehicle Update and Configuration Management (V-UCM)** — vehicle-wide (fleet/campaign) update coordination; *added R23-11* [2][8].

**Diagnostics (1)**
20. **Diagnostic Management** — `ara::diag`, UDS/DoIP diagnostics (sibling covers depth).

**Recent inventory churn (from doc 982 change history):** R25-11 added *Remote Persistency* and *Safe Hardware Acceleration* and Suspend-to-RAM in SM; R24-11 added *Automotive API Gateway*; R23-11 **removed Identity and Access Management (IAM)** and added V-UCM + Raw Data Stream; R21-11 **removed RESTful Communication** and added the IdsM [2].

## 5. Execution Management, Function Groups, Machine States

**Processes.** *"Execution Management is responsible to control Processes … it starts, configures, and stops Processes as configured in Function Group States using interfaces of the Operating System. The Operating System is responsible for runtime scheduling"* [2]. EM is the entry point, started by the OS at boot; all other FCs are just applications from EM's point of view and are launched the same way, *"except for EM itself"* [1]. EM decides start **order** via **Execution Dependencies** (declared in the Execution Manifest) but *"Execution Dependencies do not determine which Processes should be started, they only determine the order"* [4]. EM does **not** decide *which/when* — *"decisions on which and when the application starts or terminates are not made by EM. A special FC, called State Management (SM), is the controller, commanding EM"* [1].

**Function Group.** A named set of processes with a set of states; *"A Function Group State defines a set of active Applications for any certain situation"* and a modelled Process belongs to exactly one Function Group but can appear in several of that group's states. There is a predefined group **`MachineFG`** that controls machine lifecycle [3].

**Machine State = Function Group State of `MachineFG`.** EM obtains Machine-State configuration *"from Function Group 'MachineFG' within the SoftwareCluster with category PLATFORM_CORE"* (exactly one PLATFORM_CORE cluster per machine) [3]. The spec confirms a Machine State is *"a Function Group State"* when the group name is `MachineFg` [3]. Boot: EM self-initiates transition to the **Startup** Machine State, brings up SM, then hands *"responsibility for Function Group state management … to State Management"* [3]. Predefined machine states include Startup, Shutdown, Restart; SM must be configured to run in every machine state or the machine gets *"stuck forever"* [3].

**Transition mechanics.** SM calls `ara::exec::StateClient::SetState`. On a Function-Group-State change EM *"terminates running Processes and then starts Processes active in the new state before confirming the state change to State Management"* [3]. On a crash outside a transition, EM sets that group to **Undefined Function Group State** and calls SM's `undefinedStateCallback` [3].

**Difference from systemd.** Superficially systemd-like (a supervisor starting units by dependency ordering), but: (a) the *policy* of which set runs is externalized to a separate safety-relevant FC (SM), not encoded in unit files; (b) the unit of composition is the **Function Group State** (a full mode of the machine), not an individual service target; (c) EM enforces **resource groups** (CPU/memory policing) and supports **authenticated startup** from a Trust Anchor [2]; (d) configuration comes from ARXML **Manifests**, not `.service`/`.target` files; (e) EM is the *entry point* and part of the certified platform, sitting under a functional-safety argument (ISO 26262).

## 6. Manifests — what they contain, and how much "dynamic" is real

The Manifest spec (doc 713) subdivides the term into **five** kinds [5]:
- **Execution Manifest** — "target configuration-related information of applications" bundled with the executable: startup parameters, resource-group assignment, which Function Group States a process runs in (`StateDependentStartupConfig`), Execution Dependencies, scheduling [5].
- **Service Instance Manifest** — how service-oriented communication maps to the transport (SOME/IP instance IDs, endpoints, event groups), bundled with the executable [5].
- **Machine Manifest** — configuration of the machine itself *"without any applications"*: Function Groups & their states, Machine States, network/IP config, OS/resource config [5].
- **Raw Data Stream Manifest** and **Software Distribution** manifest (packaging/logistics) [5].

Manifests are **ARXML**, authored at integration time and transformed to a *"platform-specific format which is efficiently readable at Machine startup"* — the transform can be off-board at integration/deployment time or on-board [3].

**How dynamic is production really?** AP is "dynamic" *relative to CP*, but production determinism is high: the set of processes per state is fixed in Manifests; which state is active is arbitrated by SM; service discovery is the *runtime* dynamic element, but integrators are expected to *"ensure that all service dependencies are mapped to the State Management configuration"* [4]. The spec even discourages runtime coupling: *"user-level applications should not rely on Execution Dependencies unless strictly necessary"*, and dynamic memory is generally allocated at startup for freedom-from-interference. So "dynamic" in practice = *deployment-time flexibility and OTA reconfiguration*, not free-running runtime allocation/discovery. (Full quantification of allowed runtime dynamism is partly implementation/project policy — see Open questions.)

## 7. POSIX PSE51 and the C++ baseline

**PSE51.** *"Adaptive Applications are restricted by definition to use PSE51 interface, a single-process profile of POSIX standard. PSE51 has been selected to offer portability for AA and to enable freedom from interference among applications."* [1] PSE51 (IEEE 1003.13 "Minimal Realtime System Profile") gives threads, mutexes, semaphores, signals, real-time scheduling (`SCHED_FIFO`/`SCHED_RR`), timers, and a *single-process* filesystem/IO subset — but **excludes** `fork`/`exec` process creation, `mmap`-based shared memory as a general facility, and the multi-process APIs. Practical consequences for developers: **one process = one address space, multiple threads**; you cannot spawn child processes from an AA (EM owns process creation); freedom-from-interference between apps comes from OS process isolation + resource groups, not from within the app [1]. The OS *itself* must be multi-process POSIX; the *restriction to PSE51* applies only to the AAs [1]. Caveat from the spec: the C++ Standard Library "does not cover all the PSE51 functionalities, such as setting a thread scheduling policy," so mixing `std::thread` with native PSE51 threading may be necessary but is discouraged [1].

**C++ standard baseline.** The AP APIs (`ara::core` etc.) are specified against **C++14** (ISO/IEC 14882:2014) — the historical baseline. As of R24-11/R25-11 the standalone **AUTOSAR "Guidelines for the use of the C++14 language" document has been removed from the release set** (verified: `AUTOSAR_AP_RS_CPP14Guidelines.pdf` returns HTTP 404 for R23-11, R24-11, and R25-11; last present in **R22-11**) [6]. AUTOSAR and MISRA announced integration of the AUTOSAR C++14 guidelines into **MISRA C++:2023**, the single successor coding standard, which targets **C++17** [7]. So: C++14 is still the language *baseline* the ARA APIs assume; MISRA C++:2023 (C++17) is now the *coding-guideline* successor. Whether R25-11 has formally bumped the compiled language baseline to C++17 is not stated in the Platform Design doc — see Open questions.

## Key facts

| # | fact | source URL | exact quote if load-bearing | confidence |
|---|------|-----------|------------------------------|-----------|
| 1 | Current release is R25-11 | [2] | doc header "AUTOSAR AP R25-11" | high |
| 2 | AP exists because CP cannot serve HPC ECUs; provides HPC + OTA | [1] | "AP provides mainly high-performance computing and communication mechanisms and offers flexible software configuration, e.g. to support software update over-the-air" | high |
| 3 | AP is not a new OS, defines an OS Interface on POSIX | [1] | "The Adaptive Platform does not specify a new Operating System … Rather, it defines an execution context and Operating System Interface" | high |
| 4 | AAs run on ARA | [1] | "Adaptive Applications (AA) … run on top of ARA, AUTOSAR Runtime for Adaptive applications" | high |
| 5 | AAs restricted to PSE51 single-process profile | [1] | "Adaptive Applications are restricted by definition to use PSE51 interface, a single-process profile of POSIX standard" | high |
| 6 | 20 Functional Clusters in 7 categories (Runtime/Comm/Storage/Security/Safety/Config/Diag) | [2] | Figures 9.2–9.103 | high |
| 7 | EM controls (starts/configures/stops) Processes per Function Group State using OS interfaces | [2] | "Execution Management is responsible to control Processes … it starts, configures, and stops Processes as configured in Function Group States" | high |
| 8 | SM decides which/when; EM does not | [1] | "decisions on which and when the application starts or terminates are not made by EM" | high |
| 9 | Machine State is a Function Group State of special group MachineFG (PLATFORM_CORE) | [3] | "obtain the configuration of Machine States from Function Group 'MachineFG' within the SoftwareCluster with category PLATFORM_CORE" | high |
| 10 | Five kinds of Manifest | [5] | Execution / Service Instance / Machine / Raw Data Stream / Software Distribution | high |
| 11 | Execution Manifest bundled with executable, specifies target config | [5] | "An Execution Manifest is bundled with the actual executable code in order to support the integration" | high |
| 12 | Machine Manifest configures the machine without applications | [5] | "content that applies to the configuration of just the underlying machine (i.e. without any applications running on the machine)" | high |
| 13 | AUTOSAR C++14 Guidelines removed from standard set (404 R23/R24/R25; last in R22-11) | [6] | HTTP 404 on AUTOSAR_AP_RS_CPP14Guidelines.pdf for R23-11..R25-11 | high |
| 14 | AUTOSAR C++14 guidelines merged into MISRA C++:2023 (C++17) | [7] | "MISRA merging the AUTOSAR guidelines with its own established best practice … single 'go to' language subset"; MISRA C++:2023 targets C++17 | high |
| 15 | R25-11 added Remote Persistency, Safe Hardware Acceleration, Suspend-to-RAM (SM) | [2] | change history R25-11 | high |
| 16 | IAM removed R23-11; RESTful Communication removed R21-11 | [2] | "Removed Functional Cluster Identity and Access Management"; "Removed functional cluster RESTful Communication" | high |
| 17 | Standard scheduling policies are SCHED_FIFO and SCHED_RR | [1] | "The standard scheduling policies are SCHED_FIFO and SCHED_RR" | high |
| 18 | AP OS must provide multi-process POSIX capability | [1] | "The AP Operating System is required to provide multi-process POSIX OS capability" | high |
| 19 | Automotive API Gateway uses VISS protocol; added R24-11 | [2][8] | "Automotive API Gateway … standardized data-centric communication with the vehicle using VISS protocol" | med-high |
| 20 | On crash, EM sets group to Undefined FG State and calls undefinedStateCallback | [3] | SWS_EM_01309 | high |

## Sources

1. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_PlatformDesign.pdf — Explanation of Adaptive Platform Design (Doc 706), AP R25-11 — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SWArchitecture.pdf — Explanation of Adaptive Platform Software Architecture (Doc 982), AP R25-11 — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf — Specification of Execution Management (Doc 721), AP R25-11 — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_ExecutionManagement.pdf — (same doc; §7.3.4 Execution Dependencies / §7.4 state management) — AUTOSAR — primary
5. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_TPS_ManifestSpecification.pdf — Specification of Manifest (Doc 713), AP R25-11 — AUTOSAR — primary
6. https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_RS_CPP14Guidelines.pdf — Guidelines for the use of the C++14 language (last release present; 404 in R23-11+) — AUTOSAR — primary
7. https://www.autosar.org/news-events/detail/misra-consortium-announce-integration-of-autosar-c-coding-guidelines-into-updated-industry-standard — MISRA/AUTOSAR C++ guideline integration announcement — AUTOSAR/MISRA — primary (announcement); https://www.perforce.com/blog/qac/misra-cpp-2023-intro — MISRA C++:2023 targets C++17 — Perforce — vendor/secondary
8. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_OperatingSystemInterface.pdf — Specification of Operating System Interface (Doc, PSE51 profile), AP R25-11 — AUTOSAR — primary

## Surprises

- **AP is not an OS.** A firmware engineer's intuition ("AUTOSAR = the RTOS") is wrong for AP: it is middleware + services on Linux/QNX/PikeOS; AUTOSAR deliberately does *not* ship an OS for AP [1].
- **A "Machine State" is not a special concept — it is just the Function Group State of a reserved group named `MachineFG`** in the one PLATFORM_CORE SoftwareCluster [3]. The elegant unification is easy to miss.
- **EM is a dumb enforcer, not the brain.** The tempting analogy "EM ≈ systemd" breaks: EM never decides *which* apps run; that policy is owned by State Management, a separate safety-relevant FC [1].
- **The AUTOSAR C++14 Guidelines document is gone from the standard** (404 from R23-11 onward), superseded by MISRA C++:2023 (C++17) [6][7] — many secondary sources still present "AUTOSAR C++14" as a living, separate standard.
- **The FC inventory is not static across releases**: IAM and RESTful Communication were *removed*; Remote Persistency, Safe HW Acceleration, Firewall, V-UCM, Automotive API Gateway are relatively new [2]. Any "canonical list" must be release-stamped.
- **Two different official taxonomies** exist for the same clusters (Foundation/Services/Std-App/Vehicle vs. the 7 technical categories) [1][2] — a common source of confusion.

## Open questions

- **Exact compiled C++ language baseline in R25-11.** The Platform Design doc names "C++" but no ISO year; C++14 is the historical API baseline and MISRA C++:2023 (the successor guideline) targets C++17. *Best guess (labeled guess):* ara:: APIs still assume C++14 as the minimum, with C++17 now permitted/expected via MISRA C++:2023 — not verified in a primary R25-11 statement. Needs the R25-11 RS_General / SWS_Core language-binding clause to confirm.
- **Precise PSE51 include/exclude list as AUTOSAR scopes it.** I quoted the AP rationale and the IEEE 1003.13 general definition, but did not extract an itemized PSE51 API table from the R25-11 OperatingSystemInterface SWS (the PDF is short/interface-focused). The classic PSE51 exclusion of `fork`/multi-process is standard IEEE, not re-verified line-by-line against R25-11.
- **How much runtime dynamism is *permitted* vs. *typical*.** The spec constrains dependencies/discovery and expects static mapping, but the exact bound on runtime dynamic allocation / late service discovery in a *safety* configuration is largely project/OEM policy and ASIL-driven, not a single normative number.
- **Whether the Platform Design "logical view" figure still shows deprecated clusters.** Doc 706 warns its Figure 4.1 "contains Functional Clusters that are not part of the current release" — so the authoritative inventory is doc 982's building-block view, which I used.
