# AUTOSAR Adaptive — Lifecycle & Serviceability: UCM, Diagnostics (DM), PHM, Persistency, SOVD

*Research notes for embedded/firmware engineers new to automotive software platforms. Written 2026-07-15. Every load-bearing claim carries a source reference `[n]`; sources are listed at the bottom. Primary sources = AUTOSAR standard PDFs, ISO, ASAM.*

## Executive summary

The AUTOSAR Adaptive Platform (AP) serviceability story is built from five functional clusters. **UCM** (Update & Configuration Management) does on-board software updates as *Software Clusters* through a Transfer → Process → Activate → (Verify/Finish or Rollback) workflow, coordinated with **State Management**; vehicle-wide OTA campaigns are orchestrated by a separate **V-UCM** (Vehicle UCM, split into its own spec since R23-11) that talks to the OEM backend, the vehicle state manager and the human driver [1][2][12]. **Diagnostic Management (DM / ara::diag)** is a diagnostic *server* that implements a UDS (ISO 14229-1) server instance *and* SOVD; unlike CP it merges DCM-like communication and DEM-like fault memory behind one C++ interface, with one Diagnostic Server Instance per Software Cluster [3]. Crucially, the AP spec does **not** mandate DoIP-only: DoIP (ISO 13400-2:2019 + Amd 1:2023) is the only *standardized* UDS transport, but "a custom implementation of a transport protocol can be used" [3][4]. **PHM** provides Alive/Deadline/Logical supervision, notifies State Management for recovery, and falls back to a hardware watchdog; Health Channels are now obsolete [5]. **Persistency (ara::per)** gives key-value + file storage with redundancy (replication/CRC/hash) and defined install/update/rollback of data across cluster updates [6]. **SOVD** (HTTP/REST/JSON, ISO 17978) is realized inside the DM plus a SOVD Gateway — it is *not* a separate cluster [7][8].

## 1. UCM — end-to-end update workflow and OTA orchestration

**Software Clusters as the unit of update.** AP can be extended "with new software packages without re-flashing the entire ECU"; each package is described by a *SoftwareCluster* [3]. The per-machine UCM (`ara::ucm::PackageManagement`) exposes a service interface over ara::com with these methods: `TransferStart`, `TransferData`, `TransferExit`, `ProcessSwPackage`, `Activate`, `VerifyUpdate`, `Finish`, `Rollback`, `PrepareRollback`, `Cancel`, `RevertProcessedSwPackages`, `GetSwClusterInfo`, `GetSwClusterChangeInfo`, `GetSwPackages` [1].

The workflow has three tracked phases, expressed as two state machines plus a Software-Cluster lifecycle [1]:

1. **Transfer.** A Software Package is streamed with `TransferStart` → `TransferData` → `TransferExit`. The `TransferStateType` moves `kTransferring → kTransferred`; while streaming, the `ProcessingStateType` is set to `kProcessing` [1].
2. **Processing.** `ProcessSwPackage` unpacks/validates and writes the cluster. `processingState` runs `kProcessing → kProcessed` (or `kProcessingFailed`). After successful processing a *newly added* cluster is in lifecycle state **kAdded** (`SWS_UCM_00191`) [1].
3. **Activation.** `Activate` starts the critical phase: "At beginning of activation, UCM is asking State Management for an update session. Once granted, UCM is requesting State Management to stop running processes from the outdated SoftwareClusters. When processes stopped, UCM makes available … the updated or installed SoftwareClusters, the core action step of the activation." Verification is then done by asking State Management to switch the affected Function Groups to **Verify** mode (`VerifyUpdate`, `SWS_UCM_00293`), reaching **kActivated** (`SWS_UCM_00107`). A final `Finish` commits, moving the cluster to **kPresent** [1].

**Software-Cluster lifecycle states** (enum literals): `kPresent = 0x00`, `kAdded = 0x01`, `kUpdating = 0x02`, `kRemoved = 0x03` [1]. Transitions: kAdded → kPresent after successful `Finish`; kUpdating → kPresent after successful activation; kRemoved is reached after a completed removal; `RevertProcessedSwPackages` or `Finish` can bring kRemoved back to kPresent [1].

**Rollback.** UCM lists among its goals "Providing rollback functionality to restore a known functional state in case of failure" [1]. `Rollback`/`PrepareRollback` restore the previous version if activation fails (e.g. a process fails to reach kRunning), and `RevertProcessedSwPackages` discards processed-but-not-activated packages. Note the spec also documents *failing rollback* handling (`UCM ROLLBACK FAILED`) — rollback is best-effort, not guaranteed to always succeed [1].

**Who orchestrates vehicle-wide OTA?** The old "UCM Master" concept was **split into its own specification, Vehicle UCM (V-UCM)**, first released "from split of SWS UCM" in R23-11 [1][2]. V-UCM "is coordinating an update campaign within the vehicle" and, per R25-11, is responsible for [2]:
- **Backend interaction**: identify updatable Software Clusters; **authenticate the Vehicle Package**; confirm inter-cluster dependencies before the campaign; "Inform Backend of needed Software Packages, receives them and dispatch them to targeted ECUs."
- **Vehicle State Manager interaction**: apply the safety conditions demanded by the Vehicle Package; share computed vehicle state.
- **Human Driver interaction**: provide campaign state; "Get vehicle modification approval or consent from Human when configured in Vehicle Package."
- Provide installed-software inventory, campaign history, and "Recovery in case of failure."

So the chain is: **OEM backend → V-UCM (campaign coordinator in-vehicle) → subordinate UCM instances (per machine, do the Transfer/Process/Activate/Rollback)** [1][2]. A "Vehicle Driver Application" mediates the HMI [1].

## 2. Diagnostic Management (ara::diag / DM)

**What DM is.** "The DM is a diagnostic server implementation that realizes a UDS server instance according to ISO 14229-1 and SOVD according to ASAM for the AUTOSAR Adaptive Platform" [3]. Since R19-03 the interface is **C++ (`ara::diag`)**, replacing the former ara::com service interface [3]. Configuration input is the **Diagnostic Extract Template (DEXT)** [3]. DM supports "an own diagnostic server instance per installed SoftwareCluster," and "All diagnostic server instances share a single TransportLayer instance (e.g. DoIP on TCP/IP port 13400)" [3].

**UDS services specified** (from the R24-11 SWS Diagnostics service chapter): `0x10` DiagnosticSessionControl, `0x11` ECUReset, `0x14` ClearDiagnosticInformation, `0x19` ReadDTCInformation (many sub-functions incl. mirror-memory/OBD 0x0F–0x19, 0x42), `0x22` ReadDataByIdentifier, `0x23` ReadMemoryByAddress, `0x27` SecurityAccess, `0x28` CommunicationControl, `0x29` Authentication (used for SOVD auth roles), `0x2E` WriteDataByIdentifier, `0x2F` InputOutputControlByIdentifier, `0x31` RoutineControl, `0x34` RequestDownload, `0x35` RequestUpload, `0x36` TransferData, `0x37` RequestTransferExit, `0x3E` TesterPresent, `0x85` ControlDTCSetting [3].

**Transport — the important nuance.** The AP spec applies "a flexible concept": "The DoIP protocol based on ISO 13400-2:2019, including ISO 13400-2:2019/Amd 1:2023 or a custom implementation of a transport protocol can be used" (R25-11 wording; R24-11 is the same concept, citing ISO 13400-2) [3][4]. The message-flow description lists inbound requests as "UDS DoIP or proprietary transport protocol requests" [3]. **Conclusion: DoIP is the only *standardized* UDS transport in AP (unchanged through R25-11); a proprietary/custom transport is explicitly *permitted* but left out of the standard.** This qualifies the repo's "DoIP-only confirmed in R24-11" note — accurate as "only standardized transport," an overstatement if read as "DoIP is the only transport possible." For SOVD, "the HTTP transport protocol with REST services is used" [3].

**How DM differs from CP's DCM + DEM.** On Classic Platform, DCM (Diagnostic Communication Manager) and DEM (Diagnostic Event Manager) are separate BSW modules over the PDU Router (CAN/LIN/FlexRay/Ethernet). On AP, DM is a single functional cluster whose "response handling basically resembles the functionality of the Dcm BSW module," but it also owns fault-memory behaviour and exposes everything through one `ara::diag` C++ API, with per-Software-Cluster server instances and DoIP-centric transport rather than the PDU Router [3]. (CP DCM/DEM internals are out of this agent's scope — covered by a sibling.)

## 3. Platform Health Management (PHM)

PHM is "the software specification of the Platform Health Management functional cluster," implementing Foundation Health Monitoring and required by ISO 26262:2018 [5]. It performs three elementary supervisions [5]:
- **Alive Supervision** — "check the timing constraints of cyclic Supervised Entitys to be within the configured min and max limits" (tolerates a configurable number of failed reference cycles).
- **Deadline Supervision** — timing of the transition from a Deadline Start Checkpoint to a Deadline End Checkpoint within min/max.
- **Logical Supervision** — checks the software executes "in the sequence defined by the programmer" (control-flow monitoring).

Applications report **Checkpoints** via `ReportCheckpoint`; each Supervised Entity yields an **Elementary Supervision Status**, aggregated into a **Global Supervision Status** per **Function Group** [5]. On a detected failure "Platform Health Management notifies State Management" via `ara::phm::RecoveryAction::RecoveryHandler`; State Management, as platform coordinator, decides and triggers the recovery action (e.g. restart a Function Group) [5]. PHM monitors the handler's return with a configurable timeout — "If no response by State Management is received in time, the PHM will do its own countermeasures" via the **hardware watchdog** (`WatchdogInterface`, `FireWatchdogReaction`) [5].

**Relation to a classic watchdog manager.** PHM is the AP analogue of CP's **WdgM**: the R22-11 change history notes "Alignment of Enumeration Literal Indices of SupervisionStatus with Classic Platform WdgM types" and introduced a `WatchdogInterface`, and PHM "has also an interface to the hardware watchdog" [5]. Two notable evolutions: PHM's role was changed to "a monitor who notifies State Management" (R21-11/R22-11), and **Health Channels (external supervision result inputs) were set to obsolete in R22-11 and further "Removed" in the R24-11 change history** [5] — a break from older AP material that treated health channels as a first-class input.

## 4. SOVD — Service-Oriented Vehicle Diagnostics (ISO 17978)

**What it is.** ASAM released the first SOVD standard in 2022; it is a "State-of-the-Art diagnostic API using current information technologies" based on **HTTP/REST, JSON and OAuth**, self-describing so it "does not rely and has no dependency to an external ODX data description," with **"UDS as a subset"** [7][10]. It targets remote, proximity and in-vehicle diagnostics of HPC machines while still reaching UDS-only microcontrollers [7].

**Standardization status.** SOVD is being standardized as **ISO 17978** — Part 1 (general principles) and Part 3 (API). R25-11's Diagnostics spec explicitly cites **"ISO 17978-3:2025"** and **"ISO 17978-3:2026"** and **"ASAM SOVD 1.1 (2026-01)"**, and warns of limitations: "The SOVD API based on version 1.1 / ISO 17978-3:2026 is not yet (fully) supported" [4][9]. So the ISO transition is live but AP support currently tracks the earlier SOVD version, with 1.1/ISO alignment landing in later releases. (ISO 17978-1 catalog entries show 2026 publication / 2025 DIS [11].)

**Where SOVD lives in AP — not a dedicated cluster.** AUTOSAR realizes SOVD *inside the Diagnostic Manager* using "known and new ara::diag (C++) interfaces," plus supporting blocks — there is no separate "SOVD functional cluster" [7][10]. The reference architecture has three main blocks [7]:
- **SOVD Gateway** — the SOVD edge node; an HTTP reverse proxy that routes on the URI *entity* path to internal SOVD endpoints (statically configured or discovered via **mDNS**); configured by `SOVDGatewayInstantiation` in the manifest.
- **Diagnostic Manager** — acts as the **SOVD server**: "The Diagnostic Manager itself represents a SOVD component, whereas each Diagnostic Server Instance is represented by an SOVD sub-component" [7][3]. SOVD reuses DEXT config: SOVD data ← DiagnosticDataIdentifier, operation ← DiagnosticRoutine, fault ← DiagnosticTroubleCodeUDS; standardized modes map to UDS `0x28`/`0x85`; the DM converts application byte streams ↔ SOVD JSON using DEXT compuMethods [7].
- **SOVD-to-UDS Translation** — an on-board test client that translates SOVD ↔ UDS "based on predefined ODX definition," the mapping details being "defined by ASAM" [7]. This is the **legacy-ECU gateway pattern**: HPC speaks SOVD/HTTP outward, but classic UDS ECUs are reached by translating to UDS requests.

**New SOVD-only capabilities** (no UDS equivalent): Authorization (OAuth tokens → `SovdAuthorization`), Proximity Challenge (`SovdProximityChallenge`), data-lists, plus software-update (via UCM), logging, bulk-data and configuration use-cases; software update splits into "vehicle update" (routed by the Gateway to an OTA client, DM not involved) and "component update" (DM maps `ara::diag` to `ara::ucm::PackageManagement`) [7].

## 5. Persistency (ara::per)

`ara::per` provides two storage abstractions: **Key-Value Storage** (`ara::per::KeyValueStorage`) and **File Storage** (FileProxy/file API) [6]. Guarantees relevant to updates and safety:
- **Redundancy.** Storage "can be configured to use replication of stored data, CRCs, or Hashes" — "creating redundant copies … effectively create some redundancy," with a `PersistencyRedundancyHash` option verifying data via the **Crypto API** against a manifest hash (`PersistencyDeploymentToCryptoKeySlotMapping.verificationHash`) [6]. There is explicit **Recovery of Corrupted Data** behaviour [6].
- **Across software-cluster updates.** Persistency defines **Installation, Update, Finalization, and Roll-Back of Persistent Data** as first-class phases — i.e. data migration is handled when a Software Cluster is installed or updated, and "Roll-Back of Persistent Data after Failed Update" (`SWS_PER_00396`) restores prior data if the update fails [6]. Recent releases "Improved update sequence, allowing for independent updates of configuration" and reworked redundancy [6]. So ara::per's guarantee across updates is: defined install/update/finalize semantics with a rollback path and integrity protection, rather than transparent automatic migration.

## 6. Log & Trace (DLT) — brief

The Log & Trace cluster exposes `ara::log`; the transport binding is **DLT** ("Implementation of the LT protocol, e.g. DLT"), and ARTI-trace methods are integrated into `ara::log` [13]. Note (from SOVD): SOVD logging is *not* standardized through `ara::log` — reading log files via SOVD "is implemented based on the platform vendor's guidelines" [7].

## Key facts

| # | Fact | Source URL | Exact quote (if load-bearing) | Confidence |
|---|------|-----------|-------------------------------|------------|
| 1 | Latest AUTOSAR release is R25-11, presented at a virtual event on 4 Dec 2025; a minor release | [9] | "Release R25-11 is Now Available" / event "on December 4th, with over 800 participants" | high |
| 2 | DM realizes a UDS server (ISO 14229-1) **and** SOVD (ASAM) | [3] | "The DM is a diagnostic server implementation that realizes a UDS server instance according to ISO 14229-1 and SOVD according to ASAM" | high |
| 3 | DoIP is the only *standardized* UDS transport, but a custom transport is allowed (R25-11) | [4] | "The DoIP protocol based on ISO 13400-2:2019, including ISO 13400-2:2019/Amd 1:2023 or a custom implementation of a transport protocol can be used." | high |
| 4 | Same "DoIP or custom" concept already in R24-11 | [3] | "As transport layer for UDS a flexible concept is applied. DoIP protocol based on ISO 13400-2 or a custom implementation o[f] a transport protocol can be used." | high |
| 5 | SW-Cluster lifecycle states kPresent=0x00, kAdded=0x01, kUpdating=0x02, kRemoved=0x03 | [1] | enum literals in SWS_UCM_00078 | high |
| 6 | Activation asks State Management for an update session, stops old processes, then Verify | [1] | "UCM is asking State Management for an update session. Once granted, UCM is requesting State Management to stop running processes" | high |
| 7 | UCM Master is now V-UCM, split into its own SWS in R23-11 | [1][2] | "Initial release from split of SWS UCM" | high |
| 8 | V-UCM authenticates the Vehicle Package, checks dependencies, dispatches packages to ECUs, gets driver consent | [2] | "Authenticate Vehicle Package … Inform Backend of needed Software Packages, receives them and dispatch them to targeted ECUs … Get vehicle modification approval or consent from Human" | high |
| 9 | PHM notifies State Management for recovery; falls back to hardware watchdog on timeout | [5] | "If no response by State Management is received in time, the PHM will do its own countermeasures" | high |
| 10 | PHM Health Channels set to obsolete in R22-11, "Removed" in R24-11 | [5] | "Health Channels are set to obsolete" (R22-11); "Removed Health Channels" (R24-11) | high |
| 11 | PHM SupervisionStatus literal indices aligned with CP WdgM types; WatchdogInterface introduced | [5] | "Alignment of Enumeration Literal Indices of SupervisionStatus with Classic Platform WdgM types" | high |
| 12 | ara::per redundancy = replication, CRCs, or hashes; roll-back of persistent data after failed update | [6] | "It can be configured to use replication of stored data, CRCs, or Hashes"; "Roll-Back of Persistent Data after Failed Update" | high |
| 13 | SOVD lives inside the DM (SOVD server) + SOVD Gateway; not a separate cluster | [7] | "the Diagnostic Manager also aims on natively supporting SOVD and therefore acts as an SOVD server" | high |
| 14 | SOVD = HTTP/REST/JSON/OAuth, self-describing, "UDS as a subset" | [7] | "Self-explaining protocol (no need for ODX based interpretation)"; "UDS as a subset" | high |
| 15 | R25-11 cites ISO 17978-3:2025/2026 & ASAM SOVD 1.1 (2026-01); 1.1 not yet fully supported | [4] | "The SOVD API based on version 1.1 / ISO 17978-3:2026 is not yet (fully) supported." | high |
| 16 | SOVD-to-UDS translation is ODX-based and defined by ASAM (legacy-ECU gateway) | [7] | "translation of SOVD commands to UDS requests, based on predefined ODX definition … defined by ASAM" | high |
| 17 | UDS services specified incl. 0x10,0x11,0x14,0x19,0x22,0x23,0x27,0x28,0x29,0x2E,0x2F,0x31,0x34-0x37,0x3E,0x85 | [3] | service chapter headings 7.3.2.8.x | high |
| 18 | DM response handling "basically resembles the functionality of the Dcm BSW module" of CP | [3] | verbatim | high |

## Sources

1. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_UpdateAndConfigurationManagement.pdf — Specification of Update and Configuration Management, AP R24-11 (Doc ID 888) — AUTOSAR — **primary**
2. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf — Specification of Vehicle Update and Configuration Management, AP R25-11 (Doc ID 1090) — AUTOSAR — **primary**
3. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf — Specification of Diagnostics, AP R24-11 (Doc ID 723) — AUTOSAR — **primary**
4. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_Diagnostics.pdf — Specification of Diagnostics, AP R25-11 — AUTOSAR — **primary**
5. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_PlatformHealthManagement.pdf — Specification of Platform Health Management, AP R24-11 (Doc ID 851) — AUTOSAR — **primary**
6. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_Persistency.pdf — Specification of Persistency, AP R24-11 — AUTOSAR — **primary**
7. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_EXP_SOVD.pdf — Explanation of Service-Oriented Vehicle Diagnostics, AP R24-11 (Doc ID 1064) — AUTOSAR — **primary**
8. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_EXP_SOVD.pdf — Explanation of SOVD, AP R25-11 — AUTOSAR — **primary**
9. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — **primary**
10. https://www.vector.com/int/en/products/solutions/diagnostic-standards/sovd-service-oriented-vehicle-diagnostics/ — SOVD (ISO 17978-3) — Vector — **vendor**
11. https://www.iso.org/standard/85133.html — ISO 17978-1 Road vehicles — SOVD Part 1 — ISO — **primary**
12. https://www.autosar.org/fileadmin/standards/R23-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf — Vehicle UCM, AP R23-11 (first split release) — AUTOSAR — **primary**
13. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_SWS_LogAndTrace.pdf — Specification of Log and Trace, AP R24-11 — AUTOSAR — **primary**

## Surprises

- **"DoIP-only" is an oversimplification.** The AP Diagnostics SWS explicitly permits "a custom implementation of a transport protocol" alongside DoIP, in both R24-11 and R25-11 [3][4]. DoIP is the only *standardized* transport, not the only *possible* one. The repo's commit note "DoIP-only confirmed in R24-11" should be read/worded as **"DoIP is the only standardized transport"** to stay strictly accurate.
- **PHM Health Channels are obsolete** [5] — teaching material that presents health channels as a live PHM input would be out of date; PHM's external-result path has been deprecated.
- **SOVD is not a separate functional cluster.** It is realized *inside* ara::diag (the Diagnostic Manager as SOVD server) plus a SOVD Gateway — a natural point of confusion given SOVD's very different HTTP/REST nature [7].
- **The "UCM Master" no longer exists by that name** — it is now **V-UCM (Vehicle UCM)**, a separate spec since R23-11 [1][2].
- **SOVD ISO transition is mid-flight:** R25-11 references ISO 17978-3:2025 *and* :2026 and ASAM SOVD 1.1, but AP does "not yet (fully) support" the 1.1/ISO version [4] — so "AP supports ISO 17978 SOVD" is only partly true today.

## Open questions

- **Whether R25-11's UCM (subordinate) SWS changed the lifecycle enum or added methods** vs R24-11. I read the R24-11 UCM SWS in full and only skimmed R25-11 UCM (196 pp); the R25 workflow appears unchanged but I did not diff method-by-method.
- **Full authoritative UDS service list for AP DM** — I enumerated services from the R24-11 SWS table of contents; I did not verify every listed service is *mandatory* vs optional, nor whether R25-11 added services (e.g. `0x24`, `0x2C`). *Guess: the set is stable; unverified.*
- **Publication status of ISO 17978-1 and -3** — catalog pages show ISO 17978-1:2026 and DIS/2025 for Part 3, but I could not open the ISO paywalled text to confirm the exact published dates and whether Part 2 exists [11].
- **CAPI (Common Adaptive Platform Implementation)** was highlighted at the R25-11 event as a "certification-ready" reference AP implementation; its exact relationship to these clusters (esp. certified UCM/DM) was not verifiable from primary specs and is out of scope (vendor/implementation).
