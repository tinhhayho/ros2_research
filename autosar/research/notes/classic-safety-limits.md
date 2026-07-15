# AUTOSAR Classic Platform: Functional Safety, Real-Time Guarantees, and Structural Limits

*Research notes — 2026-07-15. Audience: embedded/firmware engineers (MCU/CAN/RTOS/bare-metal C) new to automotive software platforms. All load-bearing claims carry a source reference; unverifiable items are in Open questions.*

## Executive summary

AUTOSAR Classic Platform (CP) is the static, MCU-resident half of AUTOSAR. Its functional-safety story rests on the OSEK-derived OS: **OS-Applications** grouped into hardware-**MPU**-enforced **memory partitions** deliver ISO 26262 *freedom from interference* (FFI) in the memory dimension, **Timing Protection** (execution/lock/inter-arrival budgets) plus the **Watchdog Manager** (deadline/alive/logical supervision) cover the timing and execution dimensions, and the **E2E protection library** protects safety data crossing the (untrusted) communication path. These map onto the OS **scalability classes SC1–SC4**, where SC3 adds memory protection, SC2 adds timing protection, and SC4 adds both. Shipping stacks (Vector MICROSAR Classic Safe) are third-party certified to **ISO 26262 ASIL D** — the highest level [1][7]. CP's real-time credentials come from being *statically configured*: no dynamic memory, no runtime task creation, fixed-priority preemptive scheduling, everything sized at build time [10]. That same rigidity is its structural ceiling: a static communication matrix, no dynamic deployment/OTA of code, C-centric BSW, and heavy tooling/config friction. AUTOSAR's own architecture-decisions document confirms the split: the Adaptive Platform embraces C++ and dynamic memory precisely because CP refuses to [9]. This is why, in 2026, OEMs keep CP on zonal and safety MCUs (e.g. the Infineon AURIX safety island on NVIDIA DRIVE boards running Vector CP firmware) while pushing Adaptive to the high-performance compute [5].

## 1. OS-Applications + MPU = freedom from interference

ISO 26262-6 (Annex D) requires that software elements of different ASILs — or ASIL and QM — running on one ECU must not interfere with each other unless every element is developed to the highest ASIL present [1]. AUTOSAR's *Overview of Functional Safety Measures* (Doc ID 664) enumerates the mechanisms across three dimensions: **memory** (Memory Partitioning), **timing** (Timing Protection + Temporal Program Flow Monitoring), and **execution** (Logical Supervision) [1].

The memory mechanism is **Memory Partitioning**, implemented through **OS-Applications**. Quote: *"One Partition will be implemented using one OS-Application"* and *"SW-Cs grouped in separate user-mode memory partitions"* [1]. An OS-Application is a collection of OS objects (Tasks, ISRs, alarms, counters) that form a cohesive unit; objects inside one OS-Application freely access each other, but the OS blocks cross-partition access. Exact wording: *"The AUTOSAR Operating System provides freedom from interference for memory-related faults by placing OS-Applications into separate memory regions. This mechanism is called Memory Partitioning. OS-Applications are protected from each other, as code executing in the Memory Partition of one OS-Application cannot modify [the memory of another]"* [1].

Enforcement is by the microcontroller **MPU**: the OS runs untrusted partitions in user/non-privileged mode with MPU regions programmed on context switch, so any out-of-region access traps to a hardware exception regardless of software fault [1][3]. AUTOSAR distinguishes **Trusted OS-Applications** ("allowed to run with monitoring or protection features disabled … need not have their memory access checked") from **Non-Trusted OS-Applications** (run with protection enabled, in user mode) [1]. This is the hardware-backed spatial FFI a firmware engineer would recognise from an MPU-partitioned RTOS — but standardised and tied to the ASIL argument.

A subtle and important **limit**: partitioning is at OS-Application granularity, not finer. Quote: *"Memory Partitioning cannot be used to separate Runnables within the same SW-C"* — if two Runnables of one Software Component need different ASIL ratings with independent FFI, partitioning must be pushed down to Task level, which is awkward [1]. So FFI is real but coarse-grained; you architect around the partition boundary.

## 2. Scalability classes SC1–SC4

The AUTOSAR OS is offered in four **Scalability Classes** that bundle these protections (this taxonomy is well-attested across vendor/teaching sources; treat exact wording as medium-confidence, the structure as high-confidence) [2][8]:

- **SC1** — baseline: OSEK/VDX OS extended with **schedule tables**. No memory/timing protection.
- **SC2** — SC1 **+ Timing Protection** (execution-time and inter-arrival monitoring).
- **SC3** — SC1 **+ Memory Protection** (MPU partitioning, the FFI mechanism of §1).
- **SC4** — SC1 **+ both** timing and memory protection.

In practice, an ASIL-D ECU that mixes safety and QM software on one core (or across cores) runs **SC3 or SC4**, because it needs the MPU partitions for spatial FFI and usually the timing budgets for temporal FFI. The cost is explicit: the extra RAM/ROM footprint and CPU overhead of protection push you to a larger, faster MCU with an MPU [2][8]. SC1 is what you use on a small QM-only classic ECU where the whole image is one trust domain.

## 3. Where CP's real-time behaviour actually comes from

CP is hard-real-time because it is **statically everything**. The OS is OSEK/VDX-derived: *"tasks, alarms, and resources are configured entirely at build time, with no dynamic memory allocation, no runtime task creation … which is exactly what functional safety and determinism demand"* [10]. Scheduling is **fixed-priority preemptive** — the scheduler always runs the highest-priority READY task — with a **priority ceiling protocol** to bound priority inversion [10]. Tasks are run-to-completion (Basic Tasks) or event-driven (Extended Tasks). Determinism therefore comes from four properties a firmware engineer will find familiar:

1. **No heap / no dynamic allocation** — no fragmentation, no non-deterministic malloc latency. AUTOSAR's architecture-decisions doc makes this the explicit dividing line vs Adaptive: dynamic allocation *"can cause non-deterministic behavior. Two typical issues are the fragmentation and non-deterministic allocation/de-allocation processing time"* [9]. CP simply forbids it.
2. **Static schedule tables** — time-triggered activation points are laid out offline; combined with fixed priorities this makes WCET analysis tractable.
3. **No MMU dependence** — protection is MPU-based (region compare), not virtual-memory paging, so there is no TLB-miss / page-fault jitter.
4. **Timing Protection as a runtime backstop.** Doc 664 is precise here, and it contains a genuine surprise: *"The AUTOSAR OS does not offer deadline supervision for timing protection."* Instead it enforces three budgets [1]:
   - **Execution Time Protection** — an upper bound (*Execution Budget*) on a Task/Cat-2 ISR's execution time, monitored by the OS.
   - **Locking Time Protection** — an upper bound (*Lock Budget*) on resource-hold / interrupt-disable time.
   - **Inter-Arrival Time Protection** — a lower bound (*Time Frame*) between activations, catching runaway triggering.
   Deadline supervision itself is done separately by the **Watchdog Manager** (Deadline, Alive, and Logical Supervision — the Temporal Program Flow Monitoring), all *"configured statically"* [1]. Note also: *"Execution time enforcement requires hardware support, e.g. a timing [protection timer]"* [1] — the guarantee is only as good as the MCU's timer/MPU hardware.

## 4. E2E as a safety mechanism

The communication path (RTE → COM → PDU router → bus driver → wire) is complex and treated as *untrusted*. E2E protects the *data*, not the channel: *"The use of the End-2-End protection mechanism assumes that the integrity of safety-relevant data has to be maintained during communication, protecting the data against the effects of faults within the communication link"* [1]. The sender appends an E2E header (checksum + counter + options); the receiver verifies and does the error handling [1]. Standardised **E2E Profiles** each pick from: (1) **CRC checksum**, (2) **sequence counter** (checked for correct increment), (3) **alive counter**, (4) a **Data ID** unique per data element across the whole system, (5) **timeout detection** [1]. R22-11 specifies Profiles 1 (two variants), 2, and 4, with Profiles 5 and 6 flagged as upcoming; *"Only the standardized End-2-End profiles shall be used"* [1]. This is what makes an ASIL signal safe to send over an otherwise-QM CAN/Ethernet stack, and it is a joint CP/AP mechanism.

## 5. ASIL mix on one ECU + certified shipping stacks

Because §1–§4 give spatial + temporal + communication FFI, a single CP ECU can host mixed-criticality software: ASIL-D braking logic in one MPU partition, QM comfort code in another, on one or several cores. The certified proof point is **Vector MICROSAR Classic Safe**. Vector states it was, in 2016, *"the world's first AUTOSAR implementation to be successfully certified according to ISO 26262 up to ASIL D"* [7]. It was **re-certified by exida** (independent functional-safety assessor); the recert covered communication modules over Ethernet and J1939, modules for *"the safe separation of software on different microprocessor cores"* (multicore FFI), and a new analysis method proving *"upper limits for the execution time of the modules"* — tying directly to §3's execution-budget story and to redundant/high-availability steering-and-braking use cases [7]. MICROSAR Classic Safe is stated to meet ISO 26262 **up to ASIL D** with **ASPICE Level 3** process maturity [7]. (Elektrobit EB tresos Safety OS and ETAS RTA-CAR make comparable ASIL-D claims — see Open questions; I verified Vector directly.)

## 6. Multicore CP

Certified multicore is real: the Vector recert explicitly evaluated *"safe separation of software on different microprocessor cores"* [7]. AUTOSAR CP OS supports multicore with OS-Applications bound to cores; FFI between cores combines per-core MPU partitioning with the timing budgets. This underpins the lockstep safety-island pattern in §7.

## 7. Why CP lives at the edge: zonal and safety-MCU pattern (2026)

The industry keeps CP on zonal ECUs and **safety MCUs** precisely because its static determinism and ASIL-D certification are exactly what a safety island needs, and its lack of flexibility does not matter there. The repo's sourced example holds up on re-verification: on **NVIDIA DRIVE AGX Orin**, the safety MCU is the **Infineon AURIX TC397X (B-Step)**, and it runs **Vector firmware** [5]. NVIDIA's own forums/docs note the AURIX supports the *"Vector AFW"* firmware [5]. For **DRIVE Thor/DriveOS**, Vector states its *"MICROSAR Classic Solution takes an essential role, enabling the realization of safety-critical functions in compliance with ISO 26262 up to ASIL-D"* and is used *"as reference integration for the companion MCU"* [5]. Orin's safety island is built around **lock-step R52 cores** running classic-AUTOSAR modules [5]. Pattern: the big SoC (Adaptive/Linux/QNX) does perception and planning; a small lock-step AURIX/Cortex-R safety MCU running **CP** owns the fail-operational/fail-safe path, actuator gating, and diagnostics. CP is the trustworthy watchdog on the powerful-but-less-certifiable compute.

## 8. What CP structurally refuses to do (the limits that motivated Adaptive)

CP's strengths invert into hard structural limits:

- **Static communication matrix.** Every signal/PDU connection is defined offline and resolved by the RTE into fixed macros/BSW calls at build time. There is no service discovery; adding a communication relationship means re-generating and re-flashing. Secondary sources put it plainly: Classic communication is *"hard-wired … If you want to have software that can be replaced during run time, this does not work"* and adding a partition *"would require reflashing the whole software"* [4][11].
- **No dynamic deployment / limited OTA of function.** No runtime loading of applications; the whole ECU image is monolithic and static [4][10].
- **C-centric BSW, no dynamic memory.** CP's determinism *requires* no heap (§3); that forbids the C++/STL ecosystem AUTOSAR itself calls *"essentially indispensable"* for Adaptive [9]. CP cannot host large, evolving, object-oriented perception/AI stacks.
- **Tooling/licence and config friction.** The static model needs heavy configuration (comm matrix, ECU extract, RTE generation) through licensed toolchains — high change cost, slow iteration (secondary/industry consensus; see Open questions for a primary metric).
- **Scaling pain on HPCs.** CP is built for single-digit-core MCUs with kB–MB memory, not many-core SoCs with GB of RAM, POSIX, and Ethernet service meshes.

AUTOSAR's own R25-11 architecture-decisions document (Doc ID 1078) confirms the design intent rather than treating it as an accident: Adaptive was defined to *allow and assume* dynamic memory and C++ because those are needed for high-performance, updatable software — and it acknowledges this *"can cause non-deterministic behavior"* that must be re-tamed with deterministic allocators [9]. CP's refusal to take on that non-determinism is the whole point: it trades flexibility for a determinism and certification story that Adaptive has to work hard to partially recover. That is the structural fault line, stated by the standard body itself.

## Key facts

| # | Fact | Source URL | Exact quote if load-bearing | Confidence |
|---|------|-----------|------------------------------|-----------|
| 1 | Memory Partitioning = FFI for memory faults, one partition per OS-Application | autosar.org Doc 664 [1] | "The AUTOSAR Operating System provides freedom from interference for memory-related faults by placing OS-Applications into separate memory regions. This mechanism is called Memory Partitioning." | high |
| 2 | Partitioning is coarse: can't separate Runnables inside one SW-C | Doc 664 [1] | "Memory Partitioning cannot be used to separate Runnables within the same SW-C" | high |
| 3 | Trusted vs Non-Trusted OS-Applications (protection on/off) | Doc 664 [1] | "Trusted OS-Applications are allowed to run with monitoring or protection features [disabled]" | high |
| 4 | OS does NOT do deadline supervision for timing protection | Doc 664 [1] | "The AUTOSAR OS does not offer deadline supervision for timing protection." | high |
| 5 | Three timing-protection budgets: Execution, Lock, Inter-Arrival | Doc 664 [1] | "Execution Budget … Lock Budget … a so called Time Frame" | high |
| 6 | Execution-time enforcement needs HW support | Doc 664 [1] | "Execution time enforcement requires hardware support, e.g. a timing [protection timer]" | high |
| 7 | E2E protects data against comm-link faults; 5 mechanisms; profiles 1/2/4 (5/6 upcoming) | Doc 664 [1] | "protecting the data against the effects of faults within the communication link" | high |
| 8 | Scalability classes: SC1 base, SC2 +timing, SC3 +memory, SC4 +both | vendor/teaching [2][8] | "SC3 extends … memory protection … SC4 … both timing and memory protection" | med (structure high, wording med) |
| 9 | CP is fully static: no dynamic memory, no runtime task creation, build-time config | teaching src [10] | "no dynamic memory allocation, no runtime task creation … exactly what functional safety and determinism demand" | med-high |
| 10 | AP (not CP) uses C++/dynamic memory; it "can cause non-deterministic behavior" | autosar.org Doc 1078 R25-11 [9] | "dynamic memory allocation can cause non-deterministic behavior. Two typical issues are the fragmentation and non-deterministic allocation/de-allocation processing time." | high |
| 11 | Vector MICROSAR Classic Safe: first AUTOSAR impl certified ISO 26262 ASIL D (2016) | Vector [7] | "world's first AUTOSAR implementation … certified according to ISO 26262 up to ASIL D" | high |
| 12 | exida recert covered safe multicore separation + execution-time upper bounds + redundancy | Vector [7] | "safe separation of software on different microprocessor cores … upper limits for the execution time" | high |
| 13 | NVIDIA DRIVE AGX Orin safety MCU = Infineon AURIX TC397X running Vector firmware | NVIDIA/Vector [5] | "Safety MCU … Infineon AURIX TC397X B-Step … supported with Vector firmware"; DRIVE Thor uses "MICROSAR Classic … up to ASIL-D" | high |
| 14 | Classic comm is hard-wired/static; changes require re-flash | secondary [4][11] | "hard-wired … If you want … software that can be replaced during run time, this does not work" | med (secondary) |
| 15 | Latest AUTOSAR release = R25-11 (virtual event 4 Dec 2025) | autosar.org [6] | R25-11 "is a minor release"; CP R25-11 current | high |

## Sources

1. https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_EXP_FunctionalSafetyMeasures.pdf — Overview of Functional Safety Measures in AUTOSAR, CP R22-11 (Doc ID 664) — AUTOSAR — **primary**
2. https://automotiveembeddedsite.wordpress.com/rtos-2/ — AUTOSAR OS / scalability classes — secondary (teaching)
3. https://piembsystech.com/freedom-from-interference-iso-26262/ — Freedom from Interference ISO 26262 — secondary
4. https://www.btc-embedded.com/autosar-classic-vs-adaptive/ — Classic vs Adaptive, RTE hard-wired communication — vendor/secondary
5. https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html + https://www.vector.com/int/en/news/news/on-the-fast-track-innovators-race-to-redefine-autonomous-mobility-with-safer-and-smarter-solutions/ — DRIVE safety MCU (AURIX) + Vector CP firmware — vendor/primary
6. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 announcement — **primary**
7. https://www.vector.com/us/en/news/news/vector-autosar-basic-software-successfully-re-certified-additional-modules-available-in-asil-d-2/ — MICROSAR Classic Safe ASIL-D recert (exida) — vendor/primary
8. https://www.mirabilisdesign.com/autosar/ — AUTOSAR OS scalability classes — vendor/secondary
9. https://www.autosar.org/fileadmin/standards/R25-11/FO/AUTOSAR_FO_EXP_SWArchitecturalDecisions.pdf — Explanation of Adaptive and Classic Platform Software Architectural Decisions, FO R25-11 (Doc ID 1078) — AUTOSAR — **primary**
10. https://auto-embedded-learning.com/2025/01/13/understanding-osek-os-the-foundation-of-automotive-embedded-systems/ — OSEK OS static config / determinism — secondary
11. https://blog.esol.com/autosar_ap_cp_difference — Difference between AP and CP — vendor/secondary

## Surprises

- **The AUTOSAR OS explicitly does NOT do deadline supervision as part of "Timing Protection."** Common belief is "RTOS timing protection = deadline monitoring." Doc 664 states the opposite: timing protection is execution-budget / lock-budget / inter-arrival, and *deadline* supervision is a separate Watchdog Manager job [1]. Easy to get wrong on a slide.
- **FFI granularity stops at the OS-Application.** You cannot get MPU-enforced FFI between two Runnables of the same SW-C without pushing partitioning to Task level [1]. Mixed-ASIL architecture is constrained by this.
- **AUTOSAR itself frames the CP/AP split around dynamic memory + C++, not "OTA" marketing.** The primary architecture-decisions doc says dynamic allocation is "essentially indispensable" for AP *because* of C++, and openly admits it hurts determinism [9]. CP's whole value is refusing that trade — a cleaner framing than the usual "Classic = old, Adaptive = new."
- **The safety-MCU pattern is a designed hierarchy, not legacy baggage:** the most advanced 2026 AV compute (NVIDIA DRIVE) still delegates the certified fail-safe path to a small AURIX running Vector *Classic* [5]. CP is not being retired at the edge; it is the trust anchor.

## Open questions

- **Exact SC1–SC4 wording from the primary AUTOSAR OS SWS (Doc ID 034).** I could not fetch the OS specification PDF directly (TLS/time). The SC structure is well-attested across vendor sources [2][8] but I'd rate the *exact* AUTOSAR phrasing as unverified. *Guess: SC definitions in AUTOSAR_SWS_OS match the "SC1 base / +timing / +memory / +both" mapping — high likelihood, unconfirmed against primary.*
- **Whether R25-11 changed any of the safety-measure content vs R22-11.** I used the R22-11 Doc 664 (latest I could fetch); its own change log shows "No content changes" through R19-11→R22-11, so it is likely current, but I did not confirm an R25-11 revision of Doc 664 exists/differs.
- **Elektrobit and ETAS ASIL-D certification specifics** (EB tresos Safety OS, RTA-CAR) — widely claimed but I verified only Vector directly this pass. *Guess: both hold ISO 26262 ASIL-D assessments — very likely, sibling/secondary confirmation needed.*
- **A primary metric for "tooling/licence friction"** (e.g. config-parameter count, re-flash turnaround). This is industry consensus but I have no primary number; left as qualitative.
- **The precise AURIX part on DRIVE Thor** (vs Orin's TC397X). Vector confirms MICROSAR Classic on the Thor companion MCU [5]; the exact AURIX SKU on Thor I did not pin down. *Guess: an AURIX TC4x-generation device — unconfirmed.*
