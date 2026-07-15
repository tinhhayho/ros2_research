# AUTOSAR Adaptive Platform — OSes, Vendor Stacks, Certification, Hardware, Open Efforts (mid-2026)

*Research notes for embedded/firmware engineers new to automotive software platforms. Date: 2026-07-15. All load-bearing claims carry a source reference `[n]` resolving to the Sources list.*

## Executive summary

AUTOSAR Adaptive Platform (AP) is a **specification**, not a product: the AUTOSAR consortium ships specs (latest release **R25-11**, dated 2025-11-27, superseding R24-11 [1][2]) plus a members-only reference **Demonstrator** [3]. Real cars run a **commercial vendor stack on a POSIX OS**. The dominant OS under AP is **QNX** (BlackBerry) for safety-critical use, with **Linux** (often via a safety hypervisor), **PikeOS**, **Integrity**, and **VxWorks** also supported [4][5]. On certification, the repo's summary — *"ASIL-B shipping, ASIL-D programs underway"* — is **CONFIRMED accurate as of mid-2026**: ETAS RTA-VRTE (TÜV SÜD, Feb 2026), Qorix (TÜV SÜD, Aug 2025), and Vector MICROSAR Adaptive Safe all hold/ship **ASIL-B**, while **ASIL-D is planned (Vector: 2026) or claimed as design-compliance (Elektrobit), not a shipped full-stack certificate** I could find [6][7][8][9]. Target hardware is the high-performance SoC tier: NVIDIA DRIVE Orin/Thor, NXP S32G, Qualcomm Snapdragon Ride, TI TDA4x [10][11]. The big 2025–26 shift: **Eclipse S-CORE**, an open-source safety middleware backed by BMW, Mercedes, Bosch, ETAS, Qorix, VW and others — positioned as a partial **alternative/complement** to AP — and **SOAFEE** (Arm-led, cloud-native), which is **complementary**: AP runs as a workload inside SOAFEE's container orchestration [12][13][14].

## 1. What AP actually runs on (operating systems)

AP is defined against a **POSIX PSE51** profile, so it needs a POSIX-compliant RTOS/OS underneath. The commercial reality:

- **QNX (BlackBerry QNX)** is the de-facto safety OS for AP. QNX OS for Safety is ISO 26262 **ASIL-D** certified, and vendors integrate their AP middleware on top of it [4][9]. QNX holds ~35–38% of the safety-critical automotive OS segment [9].
- **Linux** is used heavily for non-safety and ADAS compute, but stock Linux cannot itself be certified above ~ASIL-B; vendors reach safety by pairing it with a **certified hypervisor** or a "safety companion." Elektrobit's *EB corbos Linux (built on Ubuntu)* is marketed as "the first and only Linux OS solution to comply with ASIL B/SIL 2" — achieved via an exclusive hypervisor-based safety extension [8].
- **PikeOS (SYSGO), INTEGRITY (Green Hills), VxWorks (Wind River)** all appear as supported OS abstraction targets, e.g. in Vector MICROSAR Adaptive's OSAL list (Linux, QNX, INTEGRITY, VxWorks, Android) [5]. Wind River publicized an AUTOSAR Adaptive + VxWorks ASIL-D certification *program* as far back as 2019 [7].

Takeaway for firmware engineers: unlike Classic AUTOSAR (which *is* the RTOS-ish stack on a bare MCU), **AP sits on top of a general-purpose POSIX OS on an application-class SoC** — the OS is a separate procurement/certification decision from the AP middleware.

## 2. Commercial AP stacks (product pages, OS, ASIL)

| Vendor / product | OS support | Stated safety |
|---|---|---|
| **Vector MICROSAR Adaptive** / *Adaptive MICROSAR* + **MICROSAR Adaptive Safe** | Linux, QNX, PikeOS, INTEGRITY, VxWorks, Android (via OSAL) [5] | Safe variant **ASIL-B available, in first series projects**; **ASIL-D planned 2026**; deep QNX partnership for the ASIL-D path [6][4] |
| **ETAS RTA-VRTE** | POSIX (OS-agnostic; includes a hypervisor for mixed CP/AP) [15] | **ISO 26262 ASIL-B certified by TÜV SÜD**, announced Feb 2026, "certified on the first attempt" [16][6] |
| **Elektrobit EB corbos AdaptiveCore** (+ EB corbos Hypervisor, EB corbos Linux) | POSIX-based OSes; own type-1 microkernel hypervisor [8] | AdaptiveCore marketed **ISO 26262 up to ASIL-D** (design compliance); EB corbos Hypervisor **ASIL-B certified** (compliant up to ASIL-D); EB corbos Linux **ASIL-B/SIL 2** [8] |
| **Qorix** (Performance / Adaptive stack) | POSIX; target SoCs incl. Qualcomm [17] | **TÜV SÜD certified, ISO 26262 up to ASIL-B**, announced Aug 2025; "one of the few providers with a certified Adaptive AUTOSAR stack" [17][18] |
| **Wind River** AUTOSAR Adaptive | VxWorks / Linux | ASIL-D certification *program* (announced 2019; status of a shipped certificate unverified) [7] |

**Qorix** is worth flagging as new since the repo's likely last pass: it is a **joint venture of KPIT Technologies and ZF, with Qualcomm as a strategic shareholder** [17][19], selling both Classic and Adaptive AUTOSAR plus its own "Performance" stack — and it is a lead contributor bringing **Eclipse S-CORE** to production (see §4).

## 3. Certification reality — verifying "ASIL-B shipping, ASIL-D programs underway"

**Verdict: CONFIRMED for mid-2026.** Concrete, dated, primary/vendor-sourced evidence:

- **ETAS RTA-VRTE — ASIL-B, TÜV SÜD, Feb 2026** [16][6]. Quote: *"ETAS has officially received ISO 26262 ASIL-B certification from TÜV Süd for its AUTOSAR Adaptive stack, RTA-VRTE."* [16]
- **Qorix — ASIL-B, TÜV SÜD, Aug 2025** [17][18]. *"Qorix received TÜV SÜD certification for its Adaptive AUTOSAR stack, compliant with ISO 26262 up to … ASIL B."* [17]
- **Vector MICROSAR Adaptive Safe — ASIL-B available, ASIL-D planned 2026** [6]. Quote: *"A certification for ASIL D is planned for 2026. Currently, MICROSAR Adaptive Safe … is available in ASIL B quality and is already in use in the first series projects."* [6]

So multiple **ASIL-B** AP stacks are certified and in series production, and **ASIL-D is a work-in-progress**: Vector explicitly targets 2026, Elektrobit advertises *"up to ASIL-D"* as a design/compliance claim (its **hypervisor** is ASIL-B certified, ASIL-D compliant), and Wind River ran an ASIL-D *program*. **I found no evidence of a fully certified ASIL-D end-to-end AP middleware stack shipping as of mid-2026** — the ASIL-D story is still "programs underway," exactly as the repo states. The path to ASIL-D is consistently framed as **AP-middleware + QNX OS for Safety (ASIL-D) + safety hypervisor**, with the vendor supplying the integration and safety case [4][9].

Nuance for the deck: distinguish **"ISO 26262-compliant / developed according to ASIL-x"** (a process/design claim the vendor makes) from **"certified by TÜV SÜD at ASIL-x"** (an external assessment). ETAS and Qorix have the latter at ASIL-B; "up to ASIL-D" phrasing is usually the former.

## 4. Eclipse S-CORE — alternative or complement to AP?

**Eclipse S-CORE (Safe Open Vehicle Core)** was launched by the Eclipse Foundation on **2025-06-12** as *"the automotive industry's first open source core stack for software-defined vehicles"* [12][20]. It targets embedded high-performance ECUs and delivers a **safety-aligned, open-source middleware** intended to be certifiable (ISO 26262, ISO/SAE 21434) [12][20].

- **Backers/members**: initial core Accenture, BMW, ETAS, Mercedes-Benz, Qorix; founding participants expanded to include Aumovio, Bosch, Hella, Valeo, Vector, Volkswagen, ZF, plus Qualcomm, QNX, Red Hat, Stellantis, Infineon and many more [12][21]. This is the **same OEM/Tier-1 roster that runs AUTOSAR** — they are hedging, not defecting.
- **Positioning vs AP**: partly a **competitor** (open-source, Apache-licensed, **Rust-first** — Rust is already in S-CORE while AP is still debating it [22]), partly a **complement**. AUTOSAR and S-CORE are explicitly cooperating: AUTOSAR wants an *automotive-grade reference implementation* and S-CORE has the processes/tooling AUTOSAR could reuse; S-CORE lists *"Adaptive AUTOSAR integration for early completeness"* [22][23]. Qorix frames it neatly: *"S-CORE is the blueprint; we build the actual structure"* — i.e. S-CORE defines the open core, vendors productize and certify it [24].
- **OS**: **QNX announced it will serve as a foundational OS for S-CORE** [21], reinforcing QNX's central role across both worlds.

Bottom line: S-CORE is the **most important 2025–26 development** in this space and reframes AP's monopoly on standardized HPC middleware. It is best taught as *"an open-source challenger that the AUTOSAR members themselves are building, aiming to co-exist with / partially replace AP middleware."*

## 5. SOAFEE — complementary cloud-native layer

**SOAFEE (Scalable Open Architecture For the Embedded Edge)** is an Arm-led special interest group launched **Sept 2021** (Arm, AWS, Bosch, CARIAD, Continental, Red Hat, SUSE, Woven Planet) [13][14]. It brings **cloud-native container orchestration + automotive functional safety + real-time** to Arm-based vehicle compute, building on Arm's Project Cassini/SystemReady [13][14].

Relationship to AUTOSAR: **complementary, not competing.** AP was *"not designed to support containerized applications,"* but SOAFEE blueprints show AUTOSAR Classic/Adaptive workloads **running as containerized components** alongside cloud-native apps [25]. The SDV Alliance Integration Blueprint explicitly pairs *"ECUs with AUTOSAR Classic and Adaptive"* with *"Virtualized Development with SOAFEE"* [25]. Teach SOAFEE as the **deployment/CI/orchestration environment**, AP as one of the **payloads** it can host and test in the cloud with hardware parity.

## 6. Reference / target hardware

AP targets application-class ("high-performance computer", HPC) automotive SoCs, not MCUs:

- **NVIDIA DRIVE Orin** (mainstream today) and **DRIVE Thor** (Blackwell-based, ~2000 TOPS, consolidates ADAS + cockpit, ramping into 2025–26) [10][11].
- **NXP S32G** — vehicle-network/gateway + safety processor (quad Cortex-A53 + triple lockstep Cortex-M7); explicitly cited as **supported by the AUTOSAR Adaptive standard** and runs Linux [10][11].
- **Qualcomm Snapdragon Ride / Ride Flex / Ride Elite** (Oryon CPUs, sampling 2025) [10] — note Qualcomm's strategic stake in Qorix ties its silicon to an AP stack.
- **TI TDA4x** (Jacinto) — common ADAS domain-controller target (widely used; specific AP-cert combo not separately verified here).

The recurring pattern: **AP middleware + safety OS (QNX) on an Arm application core, with a lockstep safety island (Cortex-R/M) or companion MCU running Classic AUTOSAR** for the hard-real-time/ASIL-D control — a split the firmware audience will recognize.

## 7. The AUTOSAR Demonstrator and open implementations for learning

- **Official AP Demonstrator**: an *"exemplary implementation of the Adaptive Platform specifications,"* released to **AUTOSAR partners only** ("available to all the partners"), and only informally reviewed — *"no strict quality assurance"* [3]. So it is effectively **members-only** and not a clean public teaching artifact.
- **Open-source learning options** (usable, but partial/simulation-grade, not production):
  - **`github.com/langroodi/Adaptive-AUTOSAR`** — MIT-licensed **Linux simulator** of AP interfaces (ara::com-style comms, diagnostics/DoIP/OBD-II, health management), C++14/CMake, explicitly educational [26].
  - **`github.com/insooth/autosar-adaptive`** — spec-oriented AP implementation notes/code [27].
  - dSPACE VEOS provides an AP Demonstrator-based virtual ECU environment, but that is a commercial tool [3].

For this repo's ROS 2 audience, `langroodi/Adaptive-AUTOSAR` is the most accessible hands-on artifact to contrast with `rclcpp`/DDS; treat it as illustrative, not a real AP.

## Key facts

| # | fact | source URL | exact quote (if load-bearing) | confidence |
|---|---|---|---|---|
| 1 | Latest AP/AUTOSAR release is R25-11, dated 2025-11-27, supersedes R24-11 | https://www.autosar.org/news-events/detail/release-r25-11-is-now-available | "R25-11 … release date is November 27, 2025 … supersedes R24-11" | high |
| 2 | R25-11 is a minor release; 10 new concepts across AP+CP toward unified E/E architecture | https://www.autosar.org/fileadmin/standards/R25-11/AP/ | — | high |
| 3 | AP Demonstrator is released to AUTOSAR partners only, informal review, no strict QA | https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf | "The Demonstrator release is available to all the partners"; "only informal reviews with no strict quality assurance" | high |
| 4 | Vector + QNX collaboration targets ASIL-D: MICROSAR Adaptive Safe on QNX OS for Safety, Vector supplies integration + safety case | https://www.vector.com/gb/en/news/news/vector-and-blackberry-qnx-cooperation-for-best-in-class-solution-of-safe-systems-in-sdvs/ | "pave the way to ASIL D … Vector provides a QNX operating system integration, the corresponding interface and a safety case" | high |
| 5 | Vector MICROSAR Adaptive supports Linux, QNX, INTEGRITY, VxWorks, Android via OS abstraction layers | https://www.vector.com/int/en/products/products-a-z/embedded-software/microsar-adaptive/ | "OS abstraction layers (OsAl) for … Linux, QNX, Integrity, VxWorks, and Android" | high |
| 6 | Vector MICROSAR Adaptive Safe: ASIL-B available and in first series projects; ASIL-D planned 2026 | https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ | "A certification for ASIL D is planned for 2026. Currently, MICROSAR Adaptive Safe … is available in ASIL B quality and is already in use in the first series projects." | high |
| 7 | Wind River announced AUTOSAR Adaptive + ISO 26262 ASIL-D certification *program* (2019); shipped cert status unverified | https://www.automotiveworld.com/news-releases/wind-river-autosar-adaptive-automotive-software-ready-for-iso-26262-asil-d-certification-program/ | — | med |
| 8 | Elektrobit EB corbos AdaptiveCore marketed ISO 26262 up to ASIL-D; EB corbos Hypervisor ASIL-B certified (compliant to ASIL-D); EB corbos Linux ASIL-B/SIL2 | https://www.elektrobit.com/products/ecu/eb-corbos/adaptivecore/ | "EB corbos AdaptiveCore is ISO 26262-compliant up to ASIL-D"; "first and only Linux OS solution to comply with ASIL B/SIL 2" | med |
| 9 | QNX OS for Safety is ISO 26262 ASIL-D certified; ~35–38% safety-OS market share | https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/ | "QNX complies with … ISO 26262 ASIL-D … around 35–38% market share" | med |
| 10 | NXP S32G supported by AUTOSAR Adaptive; runs Linux on quad-A53 + triple lockstep M7 | https://linuxgizmos.com/nxps-linux-driven-safety-critical-automotive-soc-mixes-cortex-a53-with-a7/ | "The NXP S32G is supported by the AUTOSAR Adaptive standard" | med |
| 11 | NVIDIA DRIVE Thor (~2000 TOPS, Blackwell) succeeds Orin, consolidates ADAS+cockpit | https://developer.nvidia.com/drive/agx | — | high |
| 12 | Eclipse S-CORE launched 2025-06-12 as first open-source SDV core stack; initial members incl. BMW, Mercedes, ETAS, Qorix, Accenture | https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open | "The Eclipse Foundation Launches the S-CORE Project: The Automotive Industry's First Open Source Core Stack" | high |
| 13 | SOAFEE (Arm-led, Sept 2021) enables cloud-native container orchestration + automotive functional safety | https://www.arm.com/company/success-library/made-possible/soafee | "SOAFEE … open-standards-based architecture … cloud-native automotive development" | high |
| 14 | AP not designed for containers; SOAFEE blueprints run AUTOSAR CP/AP as containerized workloads | https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf | "AUTOSAR Adaptive … was not designed to support containerized applications"; blueprint pairs "AUTOSAR Classic and Adaptive" with "Virtualized Development with SOAFEE" | med |
| 15 | ETAS RTA-VRTE includes a hypervisor for mixed CP/AP domain isolation | https://www.etas.com/ww/en/products-services/vehicle-software-platform/rta-vrte/ | "hypervisor … isolation of CP/AP domains … domain controller type-ECU" | high |
| 16 | ETAS RTA-VRTE ISO 26262 ASIL-B certified by TÜV SÜD (announced Feb 2026) | https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ | "ETAS has officially received ISO 26262 ASIL-B certification from TÜV Süd for its AUTOSAR Adaptive stack, RTA-VRTE." | high |
| 17 | Qorix is a KPIT+ZF JV (Qualcomm strategic shareholder); TÜV SÜD ASIL-B certified Adaptive AUTOSAR stack (Aug 2025) | https://www.qorix.ai/press-release/tuv-certified-qorix-is-one-of-the-few-providers-with-a-certified-adaptive-autosar-stack/ | "Qorix received TÜV SÜD certification … compliant with ISO 26262 up to … ASIL B" | high |
| 18 | Qorix ASIL-B certification independently reported (SP Global / Elektroniknet) | https://autotechinsight.spglobal.com/news/5283287/ | "Qorix achieves TÜV SÜD certification for Adaptive AUTOSAR stack, ensuring ASIL-B compliance" | high |
| 19 | Qorix formed by KPIT + ZF | https://www.kpit.com/news/kpit-zf-join-hands-to-promote-an-independent-company-qorix/ | — | high |
| 20 | S-CORE aims for certifiable, production-ready middleware (ISO 26262 / ISO 21434) | https://projects.eclipse.org/projects/automotive.score | — | high |
| 21 | S-CORE founding roster spans BMW, Mercedes, Bosch, ETAS, Vector, VW, ZF, Qualcomm, QNX, Red Hat, Stellantis, etc.; QNX to serve as a foundational OS | https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together | — | med |
| 22 | S-CORE is Rust-first; AUTOSAR AP still debating Rust; the two are cooperating on a reference impl | https://beza1e1.tuxen.de/oss_vs_std.html | "In AUTOSAR's Adaptive variant, Rust is still under discussion, while it is already part of S-CORE" | med |
| 23 | AUTOSAR wants an automotive-grade reference implementation; S-CORE processes/tools could be reused | https://github.com/orgs/eclipse-score/discussions/759 | — | med |
| 24 | Qorix positions S-CORE as blueprint, vendors as productizers | https://www.adt.media/software-defined-vehicles/score-is-the-blueprint-we-build-the-actual-structure/2580292 | "S-CORE is the blueprint we build the actual structure" | med |
| 25 | AP Demonstrator-based open learning: langroodi/Adaptive-AUTOSAR (MIT, Linux simulator, educational) | https://github.com/langroodi/Adaptive-AUTOSAR | "simulated Adaptive Platform environment running on Linux … educational purposes … MIT license" | high |
| 26 | Second open AP codebase: insooth/autosar-adaptive | https://github.com/insooth/autosar-adaptive | — | med |

## Sources

1. https://www.autosar.org/news-events/detail/release-r25-11-is-now-available — Release R25-11 is Now Available — AUTOSAR — primary
2. https://www.autosar.org/fileadmin/standards/R25-11/AP/AUTOSAR_AP_SWS_VehicleUpdateAndConfigurationManagement.pdf — AP R25-11 SWS (example) — AUTOSAR — primary
3. https://www.autosar.org/fileadmin/standards/R24-11/AP/AUTOSAR_AP_TR_ReleaseOverview.pdf — Adaptive Platform Release Overview R24-11 — AUTOSAR — primary
4. https://www.vector.com/gb/en/news/news/vector-and-blackberry-qnx-cooperation-for-best-in-class-solution-of-safe-systems-in-sdvs/ — Vector & QNX cooperation for safe SDVs — Vector — vendor
5. https://www.vector.com/int/en/products/products-a-z/embedded-software/microsar-adaptive/ — MICROSAR Adaptive product page — Vector — vendor
6. https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ — Safe ASIL-B AUTOSAR Adaptive for HPC available — Vector — vendor
7. https://www.automotiveworld.com/news-releases/wind-river-autosar-adaptive-automotive-software-ready-for-iso-26262-asil-d-certification-program/ — Wind River AP ASIL-D program — Automotive World — secondary
8. https://www.elektrobit.com/products/ecu/eb-corbos/adaptivecore/ — EB corbos AdaptiveCore — Elektrobit — vendor
9. https://www.vvdntech.com/en-us/blog/vehicle-os-wars-android-automotive-vs-qnx-vs-autosar-adaptive-vs-linux/ — Vehicle OS Wars — VVDN — secondary
10. https://linuxgizmos.com/nxps-linux-driven-safety-critical-automotive-soc-mixes-cortex-a53-with-a7/ — NXP S32G Linux/AP support — LinuxGizmos — secondary
11. https://developer.nvidia.com/drive/agx — DRIVE AGX / Orin / Thor platform — NVIDIA — vendor
12. https://newsroom.eclipse.org/news/announcements/eclipse-foundation-launches-s-core-project-automotive-industrys-first-open — Eclipse launches S-CORE — Eclipse Foundation — primary
13. https://www.arm.com/company/success-library/made-possible/soafee — SOAFEE cloud-native architecture — Arm — vendor
14. https://newsroom.arm.com/blog/cloud-native-automotive-development — Arm+AWS SOAFEE demo — Arm — vendor
15. https://www.etas.com/ww/en/products-services/vehicle-software-platform/rta-vrte/ — RTA-VRTE product page — ETAS — vendor
16. https://www.etas.com/ww/en/about-etas/newsroom/overview/strengthening-automotive-safety-compliance/ — RTA-VRTE ASIL-B TÜV SÜD certification — ETAS — vendor
17. https://www.qorix.ai/press-release/tuv-certified-qorix-is-one-of-the-few-providers-with-a-certified-adaptive-autosar-stack/ — Qorix TÜV ASIL-B — Qorix — vendor
18. https://autotechinsight.spglobal.com/news/5283287/qorix-achieves-tv-sd-certification-for-adaptive-autosar-stack-ensuring-asil-b-compliance — Qorix ASIL-B — S&P Global — secondary
19. https://www.kpit.com/news/kpit-zf-join-hands-to-promote-an-independent-company-qorix/ — KPIT+ZF form Qorix — KPIT — vendor
20. https://projects.eclipse.org/projects/automotive.score — Eclipse Safe Open Vehicle Core project — Eclipse Foundation — primary
21. https://newsroom.eclipse.org/eclipse-newsletter/2025/september/eclipse-s-core-new-approach-building-automotive-software-together — S-CORE newsletter (members, QNX OS) — Eclipse Foundation — primary
22. https://beza1e1.tuxen.de/oss_vs_std.html — S-CORE vs AUTOSAR (Rust) — A. Bergmann blog — secondary
23. https://github.com/orgs/eclipse-score/discussions/759 — Onboarding AUTOSAR discussion — Eclipse S-CORE — primary
24. https://www.adt.media/software-defined-vehicles/score-is-the-blueprint-we-build-the-actual-structure/2580292 — Qorix on S-CORE to production — Automotive IT/adt.media — secondary
25. https://covesa.global/wp-content/uploads/2024/05/SDV-Alliance-Integration-Blueprint-20240109.pdf — SDV Alliance Integration Blueprint — COVESA/SDV Alliance — primary
26. https://github.com/langroodi/Adaptive-AUTOSAR — Adaptive-AUTOSAR Linux simulator (MIT) — GitHub/langroodi — secondary
27. https://github.com/insooth/autosar-adaptive — AUTOSAR Adaptive spec implementation — GitHub/insooth — secondary

## Surprises

1. **S-CORE is the AUTOSAR members building an open-source alternative to their own AP.** BMW, Mercedes, Bosch, ETAS, VW, Vector, ZF, Qualcomm — the AUTOSAR core — launched Eclipse S-CORE (June 2025), a Rust-first, Apache-licensed open safety middleware. This is a bigger strategic shift than the repo likely assumes; AP no longer has an uncontested lock on standardized HPC middleware.
2. **A brand-new AP vendor, Qorix (KPIT+ZF, Qualcomm-backed), got TÜV ASIL-B before some incumbents** (Aug 2025, vs ETAS Feb 2026). The vendor landscape is not just Vector/EB/ETAS anymore.
3. **No fully certified ASIL-D end-to-end AP stack ships yet** (mid-2026) — even after years of "ASIL-D coming." The ASIL-D story is still integration-of-parts (AP middleware + QNX ASIL-D OS + ASIL-B/D hypervisor + safety case), validating the repo's cautious "programs underway" wording.
4. **SOAFEE explicitly treats AP as a container payload** despite AP "not being designed for containers" — the cloud-native world is absorbing AUTOSAR rather than replacing it.

## Open questions

1. **Has any vendor achieved a *certified* (not merely "compliant up to") ASIL-D for the full AP middleware by mid-2026?** I found ASIL-B certificates (ETAS, Qorix) and ASIL-D *plans/claims* (Vector 2026, Elektrobit "up to ASIL-D"), but no primary certificate document confirming shipped full-stack ASIL-D. *Best guess (labeled guess): no — ASIL-D at the middleware level is still in progress; ASIL-D today lives in the OS (QNX) and hypervisor layers.*
2. **Which OEM production programs run AP vs S-CORE vs in-house?** Mercedes MB.OS and VW/CARIAD are public SDV programs, and both OEMs are in S-CORE, but I could not verify from primary OEM sources exactly where AP middleware ships in a production model vs where they use S-CORE or proprietary stacks. The repo's note that "Mercedes adopts AUTOSAR selectively via Vector" is plausible but I could not confirm the specific Mercedes+Vector+AP production pairing from a primary source. *Guess: both OEMs use AP for some ECUs today and are steering future platforms toward S-CORE.*
3. **Exact OS under each certified stack.** ETAS/Qorix press did not name the certified-configuration OS. *Guess: QNX for the ASIL path, Linux+hypervisor for mixed-criticality.*
4. **TI TDA4x + certified AP combo** — TDA4x is a common ADAS target but I did not verify a specific vendor's AP certification on it.
5. **R25-11 AP-specific changes** — confirmed the release exists and is minor; did not enumerate AP-specific new features (sibling agents cover AP internals).
