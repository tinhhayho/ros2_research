# AUTOSAR Classic — Services Layer: Diagnostics, Memory, Mode Management

*Research notes for embedded/firmware engineers new to automotive software platforms. Written 2026-07-15. Latest AUTOSAR release confirmed: **CP R25-11** (see §0). Load-bearing UDS/DEM claims verified against the AUTOSAR CP R24-11 SWS PDFs (primary), which is the newest SWS set publicly mirrored at fetch time.*

## Executive summary

The AUTOSAR Classic Platform (CP) "Services Layer" sits at the top of the Basic Software (BSW), directly under the RTE, and provides the standardized ECU services an application relies on but should never re-implement: diagnostics, non-volatile memory, mode/state management, watchdog supervision, and time synchronization. For an MCU firmware engineer, these modules formalize things you have already hand-rolled in bare-metal C — a UDS server, an EEPROM wear-leveling layer, a startup state machine, a windowed watchdog kicker, a PTP client — into configurable, vendor-portable BSW modules glued together by generated code. This note covers the diagnostic split (DCM vs DEM vs FiM), the memory stack (NvM/MemIf/Fee/Ea), mode management (EcuM vs BswM), the watchdog stack (WdgM/WdgIf), and time sync (StbM), and maps ISO 14229 (UDS) and ISO 15031/SAE J1979 (OBD) onto the DCM/DEM pair. The single most important mental model: **DEM is the fault database and status-byte engine; DCM is the protocol server that reads that database and talks to the tester.**

## 0. Release context (verified fresh)

AUTOSAR **R25-11** is the current release; the Classic Platform R25-11 was announced available (news item dated Dec 1 2025) and formally presented at the virtual Release Event on Dec 4 2025 [1]. The `yy-mm` naming means the nominal release month is November 2025. So my training-era assumption ("expected R25-11") is **confirmed, not assumed**. The deep-dive quotes below come from the R24-11 SWS PDFs because those were the newest module specs reliably fetchable; the module architecture is stable across R22-11 → R25-11, but any exact requirement ID should be re-checked against R25-11 before shipping.

## 1. DCM vs DEM: the exact split, DTC status bytes, debouncing

**DEM (Diagnostic Event Manager)** is the fault memory. Software components and BSW modules report a *monitor result* (Passed/Failed) for a *diagnostic event* via `Dem_SetEventStatus(...)`. DEM debounces that raw result, decides when a fault is mature, maintains the per-DTC **UDS status byte**, and stores event-related data (freeze frames / snapshots, extended data) to NvM. DEM explicitly "shall use the API `NvM_WriteBlock` of the NVRAMManager … if there is the necessity to trigger the storage of data between `Dem_Init` and `Dem_Shutdown`" [2] — i.e. DEM is a *client* of the memory stack, it does not touch flash itself.

**DCM (Diagnostic Communication Manager)** is the protocol server. The DEM spec itself describes DCM as "in charge of the UDS and SAE J1979 communication path and execution of diagnostic service … It forwards requests coming from an external diagnostic scan tool and is further responsible for assembly of response messages (DTC, status information, etc.)" [2]. DCM never *computes* DTC status; when a tester sends service 0x19 (ReadDTCInformation), DCM calls into DEM (e.g. `Dem_DcmGetStatusOfDTC`, `Dem_DcmReadDataOfPID01`) and formats the answer [2].

**Where the status byte lives:** in DEM. The status byte is "as defined in ISO 14229-1, based on DTC level" [2]. The 8 bits, quoted from the R24-11 DEM SWS [2]:

- bit 0 `testFailed` — result of the most recently performed test.
- bit 1 `testFailedThisOperationCycle` — a test reported testFailed at any time during the current operation cycle.
- bit 2 `pendingDTC` — testFailed at any time during the current or last completed operation cycle.
- bit 3 `confirmedDTC` — "malfunction was detected enough times to warrant that the DTC is desired to be stored in long-term memory."
- bit 4 `testNotCompletedSinceLastClear` — has a test run+completed since the last ClearDiagnosticInformation.
- bit 5 `testFailedSinceLastClear`.
- bit 6 `testNotCompletedThisOperationCycle`.
- bit 7 `warningIndicatorRequested` — status of any warning indicator (e.g. MIL) for this DTC.

`confirmedDTC` (bit 3) is set via confirmation counters once the fault matures [2]. **Readiness** (OBD "complete/incomplete") is derived from bits 4 and 6 [2].

**Event debouncing** happens inside DEM, per event, using one of three algorithms [2]:
- **Counter-based**: `Dem_SetEventStatus(DEM_EVENT_STATUS_PREFAILED)` increments an internal counter by `DemDebounceCounterIncrementStepSize`; PREPASSED decrements it. Crossing `DemDebounceCounterFailedThreshold` latches FAILED; crossing `DemDebounceCounterPassedThreshold` latches PASSED. Counter is clamped at the threshold on overshoot [2].
- **Time-based**: a configurable timer replaces the counter threshold; the timer runs while the monitor keeps reporting the same pre-result.
- **Monitor-internal**: the SWC does its own debouncing and reports only final FAILED/PASSED.

So the pipeline is: **SWC monitor → PREFAILED/PREPASSED → DEM debounce → FAILED/PASSED → status byte + confirmation counter → (matured) NvM store → DCM reads on request.**

**FiM (Function Inhibition Manager)** is the third leg. Per the DEM SWS: FiM "stands for the evaluation and assignment of events to the required actions for Software Components (e.g. inhibition of specific 'Monitors'). The Dem informs and updates the Function Inhibition Manager (FiM) upon changes of the monitor status in order to stop or release function entities according to assigned dependencies" [2]. Concretely: if fault A is active, FiM inhibits monitor B that would give a false reading — it prevents cascade/false DTCs. FiM is downstream of DEM, not part of DCM.

## 2. A DID read (SID 0x22 ReadDataByIdentifier) through the stack

Flow for a *live application value* (not a stored DTC):

1. Tester frame arrives on CAN/Ethernet → CanTp/DoIP reassembles → **PduR** routes the request PDU to **DCM** [3].
2. DCM's **DSD** (Diagnostic Service Dispatcher) checks the service table. Unknown/unsupported service → NRC 0x11 [3].
3. **DSP** (Diagnostic Service Processor) handles 0x22: it verifies the requested DID exists and is permitted in the **current session and security level** [3]; if not → NRC 0x31 (requestOutOfRange) or 0x33 (securityAccessDenied).
4. DSP reads the data element. In configuration the DID points to a `DcmDspData` container that either (a) names an application **read callout** function, or (b) is bound to an RTE **port**. AUTOSAR states "the Dcm can directly access `SenderReceiverInterface`" — the Dcm ServiceSwComponentType has a required port typed by a compatible Sender-Receiver interface [3].
5. If configured as a client/server operation, the **RTE** calls the SWC's provided runnable (e.g. `DataServices_<DID>_ReadData`); if Sender-Receiver, the RTE just hands DCM the latest value the SWC last wrote. The SWC — the actual data provider — returns the raw bytes.
6. DCM assembles the positive response `0x62 <DID_hi> <DID_lo> <data…>` and hands it back down through PduR → transport → tester [3].

Mental model for a firmware engineer: DCM is a generated UDS server; a DID is a table row that maps a 2-byte identifier to either a getter function pointer or a shared variable, and the RTE is the "middleware" that resolves that binding at generation time.

## 3. NvM and the memory stack — what maps to what in MCU firmware

The CP memory stack, top to bottom: **NvM → MemIf → {Fee → Fls} or {Ea → Eep}** [4].

- **NvM (NVRAM Manager)** — the service every SWC talks to. It manages logical **NVRAM blocks**. Each block is a set of *basic storage objects*: a mandatory NV block (in flash/EEPROM), a RAM block (working copy), an optional ROM block (default/rollback values), and an administrative block (state + attempt counters) [4]. Block management types [4]:
  - **Native** — 1 NV block. Simplest, minimal overhead.
  - **Redundant** — 2 NV copies; on a corrupt read NvM recovers from the good copy. Use for safety-critical calibration.
  - **Dataset** — an array of equally sized sub-blocks; app selects index at runtime (e.g. per-slot logs).
  Integrity is optional per-block CRC (CRC8/16/32) [4].
- **Write strategies**: SWCs call `NvM_WriteBlock` for a single deferred/immediate write. The big-hammer multi-block calls are `NvM_ReadAll` at startup (RAM ← NV for all configured blocks) and **`NvM_WriteAll` at shutdown** — and `NvM_WriteAll` is invoked by **EcuM** during the shutdown sequence to flush all permanent blocks to NV [4][5]. "Immediate" priority blocks can jump the queue (used for crash/emergency data). Both ReadAll/WriteAll are asynchronous and progress via `NvM_MainFunction` [4].
- **MemIf** is a thin dispatcher: it routes NvM requests to Fee or Ea by device index, and unifies their APIs so NvM is device-agnostic [4].
- **Fee (Flash EEPROM Emulation)** sits on the **Fls** flash driver; **Ea (EEPROM Abstraction)** sits on the **Eep** EEPROM driver [4].

**MCU-firmware mapping:** NvM ≈ your key/value non-volatile parameter manager. The RAM block ≈ your in-RAM shadow struct. `NvM_WriteAll` ≈ the "save settings on power-down / ignition-off" routine you fire from a brown-out or shutdown ISR. **Fee is the important one to internalize**: it is the standardized version of the *flash-as-EEPROM wear-leveling + sectored log-structured emulation* layer you write by hand when an MCU has flash but no true byte-erasable EEPROM — Fee gives you virtual fixed-ID blocks on top of erase-block flash, handling sector swapping and garbage collection. Ea is the same abstraction for parts that *do* have real external EEPROM. Fls/Eep are the MCAL hardware drivers (the register-level code you'd otherwise write against the flash controller).

## 4. EcuM vs BswM: who orchestrates startup/shutdown/sleep

Both are mode managers but at different phases; the division is the classic "bootstrap vs steady-state" split [6].

- **EcuM (ECU State Manager)** owns the *edges* of the ECU lifecycle. `EcuM_Init` takes control of the startup procedure, initializes the OS scheduler, drivers, and the BSW up to the point it calls `StartOS`; after that it "temporarily relinquishes control" [6]. EcuM manages **wakeup sources**, sleep, and shutdown targets (SLEEP / RESET / OFF), and it is EcuM that calls `NvM_WriteAll` on the way down [5][6]. EcuM also runs the shutdown/sleep sequences (`EcuM_GoDownHaltPoll`) [6].
- **BswM (BSW Mode Manager)** owns *steady-state* mode arbitration. Once the OS is running, "the BSW Mode Manager Module then starts mode arbitration and all further BSW initialization; starting the RTE and (implicitly) starting SW-Cs becomes code executed in the BswM's action lists" [6]. BswM works on a **rule engine**: mode requests (arbitration) → conditions → **action lists**. BswM sets EcuM's coarse state via `EcuM_SetState`, and triggers shutdown/sleep via actions like `BswMEcuMGoDownHaltPoll` [6].

So: **EcuM is the low-level state machine that boots and tears down the ECU; BswM is the configurable rules engine that decides mode transitions (RUN/SLEEP, comm on/off, partial networking) while the ECU is alive and asks EcuM to execute the physical sleep/off.** In the modern "flexible ECU management" scheme most decision logic moved from EcuM-Fixed into BswM rules.

## 5. OBD (legislated) vs UDS (enhanced) in DCM — what a CP ECU must serve by law

DCM implements two protocol families side by side:

- **UDS / ISO 14229-1** — the "enhanced" diagnostics: session control (0x10), ECU reset (0x11), read/write DID (0x22/0x2E), read DTC info (0x19), clear DTC (0x14), security access (0x27), routine control (0x31), request download/upload + transfer data (0x34/0x35/0x36/0x37) for reflash, etc. These are manufacturer-defined and **not** legally mandated in content — they are how the OEM/supplier services the ECU.
- **OBD / ISO 15031-5 + SAE J1979** — the *legislated* emissions diagnostics. The DCM "provides mechanisms to support the OBD services $01 – $0A defined in … SAE J1979 and ISO 15031-5", and AUTOSAR states this "is capable of meeting all light duty OBD regulations worldwide" (CARB OBD-II, EOBD, Japan OBD) [7]. The mandatory OBD service set (modes $01–$0A) includes: $01 current powertrain data (PIDs), $02 freeze-frame data, $03 emissions DTCs, $04 clear emissions DTCs/reset readiness, $06 on-board monitoring test results (DTRs), $07 pending DTCs, $08 control of on-board system, $09 vehicle info (VIN, CALID/CVN), $0A permanent DTCs [7].

**Which must a CP ECU serve by law?** Only **emissions-relevant ("OBD") ECUs** (engine/powertrain, and increasingly EV/hybrid propulsion controllers) are legally obligated, and only for the OBD services $01–$0A over the legislated transport (ISO 15765-4 / SAE J1979 for CAN, or J1979-2/ISO 13400 for OBDonUDS). A body/comfort/chassis ECU has **no legal OBD obligation** — it typically serves only UDS. DEM feeds OBD via the same event memory, with OBD-specific handling (readiness bits, permanent DTCs $0A, centralized PID $21/$31/$4D/$4E and DTR/Service $06 handling) enabled by config switches like `DemOBDCentralizedPID21Handling` [2]. This is the practical answer to focus question 5: **UDS is contractual, OBD $01–$0A is statutory — and statutory only for emissions ECUs.**

## 6. Watchdog stack (WdgM/WdgIf) and time sync (StbM) — brief

- **WdgM (Watchdog Manager)** supervises program flow, not just liveness. Units are **Supervised Entities** with **Checkpoints**. Three supervision types [8]: **Alive Supervision** (a checkpoint is reached the right number of times within a time window — catches too-fast/too-slow execution), **Deadline Supervision** (elapsed time between two checkpoints is within min/max — catches a runnable overrunning), and **Logical Supervision** (checkpoints occur in the allowed control-flow order — catches corrupted program flow). WdgM aggregates local results into a global status and, only while everything is correct, calls `WdgIf_SetTriggerCondition` so the hardware watchdog keeps being serviced; a failure withholds the trigger and the HW watchdog resets the ECU [8]. **WdgIf** is a thin interface layer that multiplexes multiple watchdog driver (Wdg) instances (internal + external SBC watchdog). Firmware mapping: WdgM is a *windowed, flow-aware* watchdog framework — far beyond the single `IWDG_Refresh()` kick, closer to an ASIL-oriented program-flow monitor.
- **StbM (Synchronized Time-Base Manager)** is the ECU's time hub. It maintains **Time Bases**; a **Global Time Master** is the origin, distributing time to **Time Slaves** via time-sync messages (the on-wire protocol is gPTP/802.1AS for Ethernet, or CAN/FR time-sync) handled by the bus-specific `<Bus>TSyn` modules — StbM is the bus-agnostic API SWCs read [9]. It supports **Rate Correction** and **Offset Correction** (jump or rate-adaption). Time Domains **16–31 are Offset Time Bases** layered on Synchronized Time Bases (0–15) [9]. Firmware mapping: StbM ≈ your PTP/time-of-day service, decoupled from the transport.

## Key facts

| # | fact | source URL | exact quote if load-bearing | confidence |
|---|------|-----------|------------------------------|-----------|
| 1 | AUTOSAR CP R25-11 is the current release, presented Dec 4 2025 | [1] | news item "Release R25-11 is Now Available" (Dec 1 2025); Release Event Dec 4 2025 | high |
| 2 | DEM owns and updates the UDS DTC status byte; it is "as defined in ISO 14229-1, based on DTC level" | [2] | "Status byte as defined in ISO 14229-1 [1], based on DTC level." | high |
| 3 | confirmedDTC (bit 3) = "malfunction detected enough times to warrant … stored in long-term memory" | [2] | exact quote from DEM SWS R24-11 §2.1 | high |
| 4 | DCM is "in charge of the UDS and SAE J1979 communication path"; it forwards requests and assembles responses, it does not compute status | [2] | "The Diagnostic Communication Manager (Dcm) … is in charge of the UDS and SAE J1979 communication path … responsible for assembly of response messages (DTC, status information, etc.)" | high |
| 5 | FiM inhibits monitors based on DEM event status; DEM informs FiM on monitor-status change | [2] | "The Dem informs and updates the Function Inhibition Manager (FiM) upon changes of the monitor status in order to stop or release function entities" | high |
| 6 | Counter debounce: PREFAILED increments by `DemDebounceCounterIncrementStepSize`; crossing `DemDebounceCounterFailedThreshold` → FAILED | [2] | "shall increment the internal debounce counter with its configured step-size … when the monitor reports DEM_EVENT_STATUS_PREFAILED" | high |
| 7 | DEM stores event data via `NvM_WriteBlock` and waits for positive response — DEM is a client of NvM | [2] | "The Dem module shall use the API NvM_WriteBlock of the NVRAMManager …" | high |
| 8 | NvM block management types: Native, Redundant, Dataset; each block = NV+RAM+(ROM)+Admin storage objects | [4] | three types enumerated in NvM SWS | high |
| 9 | `NvM_WriteAll` is the NvM shutdown procedure, invoked by EcuM on shutdown | [4][5] | "NvM_WriteAll … invoked by ECUM on shutdown and synchronizes the contents of the permanent NvM blocks" | high |
| 10 | MemIf routes to Fee→Fls (flash) or Ea→Eep (EEPROM) by device index | [4] | memory-stack hierarchy | high |
| 11 | EcuM controls startup/shutdown/sleep and wakeup; hands off to BswM after StartOS | [6] | "the ECU Manager module takes control of the ECU startup procedure. With the call to StartOS, the ECU Manager module temporarily relinquishes control." | high |
| 12 | BswM runs mode arbitration + action lists in steady state; sets EcuM state via EcuM_SetState | [6] | "BSW Mode Manager Module then starts mode arbitration and all further BSW initialization" | high |
| 13 | DCM 0x22: checks DID exists + session + security level before reading; can bind DIDs to Sender-Receiver ports or read callouts | [3] | "the Dcm will first check that the DID is available in the current session and security level"; "the Dcm can directly access SenderReceiverInterface" | high |
| 14 | DCM supports OBD services $01–$0A per SAE J1979 / ISO 15031-5; meets light-duty OBD regs worldwide | [7] | "support the OBD services $01 – $0A defined in … SAE J1979 and ISO 15031-5 … capable of meeting all light duty OBD regulations worldwide" | high |
| 15 | WdgM has Alive, Deadline, and Logical Supervision; feeds WdgIf_SetTriggerCondition only when correct | [8] | supervision definitions from WdgM SWS | high |
| 16 | StbM: Global Time Master distributes to Time Slaves; Time Domains 16–31 are Offset Time Bases | [9] | "Time Domains 16 to 31 are Offset Time Bases" | high |
| 17 | Security Access 0x27: sub-func 0x01 requestSeed, 0x02 sendKey; Session Control = 0x10 | [10] | "0x01 means requesting for seed … 0x02 means key" | high |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — "Release R25-11 is Now Available" — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf — Specification of Diagnostic Event Manager, CP R24-11 — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf — Specification of Diagnostic Communication Manager, CP R24-11 — AUTOSAR — primary
4. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf — Specification of NVRAM Manager, CP R22-11 — AUTOSAR — primary
5. https://rtahotline.etas.com/confluence/display/RH/An+Introduction+to+the+AUTOSAR+Memory+Stack — Intro to the AUTOSAR Memory Stack — ETAS/RTA — vendor
6. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_ModeManagementGuide.pdf — Guide to Mode Management, CP R22-11 — AUTOSAR — primary
7. https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticCommunicationManager.pdf (OBD section) — DCM SWS — AUTOSAR — primary
8. https://www.autosar.org/fileadmin/standards/R23-11/CP/AUTOSAR_CP_SWS_WatchdogManager.pdf — Specification of Watchdog Manager, CP R23-11 — AUTOSAR — primary
9. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_SynchronizedTimeBaseManager.pdf — Specification of Synchronized Time-Base Manager, CP R22-11 — AUTOSAR — primary
10. https://uds.readthedocs.io/en/latest/pages/knowledge_base/dtc.html — DTC / UDS knowledge base — py-uds docs — secondary (cross-check for ISO 14229 bit layout)
11. https://www.autosartoday.com/posts/mode_management — Mode Management overview — AutosarToday — secondary (lead)

## Surprises

- **No contradiction with the repo's verified UDS facts.** This repo already confirmed DoCAN = ISO 15765-2, DoIP = ISO 13400, the SID table, and that SID 0x2A serves diagnostic bursts (ReadDataByPeriodicIdentifier), NOT general fleet telemetry. Nothing here disputes that; DCM's 0x2A is a periodic *diagnostic* DID push. **Consistent — flag nothing.**
- The load-bearing surprise for a firmware engineer: **DCM computes nothing about faults.** Newcomers assume "the diagnostic module" decides a DTC is real. It doesn't — DEM does (debounce + confirmation + status byte), and DCM is a dumb-but-strict protocol formatter. Getting this split wrong is the #1 conceptual error.
- **OBD legislation is narrower than people think.** Only emissions-relevant ECUs are legally bound, and only for services $01–$0A. A body-control ECU serving 0x22/0x19 all day has zero statutory OBD duty. "AUTOSAR ECU therefore must do OBD" is false.
- **Fee is not "a flash driver."** It is a log-structured EEPROM *emulation* layer (sector swap + GC) on top of the Fls driver — the standardized version of the wear-leveling code embedded engineers hand-write. Easy to under-estimate.
- WdgM does **Logical Supervision** (control-flow order), not just alive/deadline timing — it is a program-flow monitor, closer to an ASIL mechanism than a plain HW watchdog kick.

## Open questions

- **Exact R25-11 requirement-ID deltas** for DEM/DCM/NvM vs R24-11: I verified module architecture is stable and R25-11 exists, but I fetched the R24-11 SWS text (the R25-11 SWS PDFs were not confirmed fetched in this session). Any *requirement ID* cited from these notes should be re-diffed against the R25-11 SWS before it ships. *(Best guess, labeled guess: no breaking changes to the status-byte/debounce model in R25-11 — these have been stable since R4.x.)*
- **Precise `confirmedDTC` vs `warningIndicatorRequested` coupling** ("if warning indicator on, confirmedDTC also set to 1") came from a secondary UDS source, not quoted verbatim from ISO 14229-1 (paywalled). Directionally correct but treat the exact conditional as *med confidence*.
- **J1979-2 / OBDonUDS transport specifics** (mode $01–$0A mapped onto UDS 0x22/0x19 over DoIP for newer emissions ECUs) I did not verify to primary depth; sibling Adaptive-diagnostics agent may overlap. *(Guess: modern EV/hybrid emissions ECUs increasingly use OBDonUDS rather than raw SAE J1979 CAN — unverified here.)*
- **StbM on-wire protocol binding**: I attributed Ethernet time sync to gPTP/802.1AS via EthTSyn; confirmed StbM is bus-agnostic, but did not fetch the EthTSyn SWS to confirm 802.1AS profile version used in R24/R25-11.
