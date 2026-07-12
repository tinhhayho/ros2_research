# The automotive software stack on DRIVE Thor — and where AUTOSAR fits (July 2026)

**What this is.** Research behind the `stack-automotive` deck diagram — the automotive
counterpart of the robot-stack diagram on slide 4. Standard workflow: two parallel
research passes (NVIDIA stack layers; AUTOSAR landscape) + one independent audit pass.
Claim rows in `research/claims-audit-2026-07.md` (A-series).

## 1. The stack, bottom-up (all layers sourced)

| Layer | What's there | Source |
|---|---|---|
| Vehicle ECUs | Zonal/domain MCUs + the board **safety MCU** — **AUTOSAR Classic land**. Orin gen: Infineon AURIX TC397X "supported with Vector firmware" (AFW = Vector AUTOSAR firmware). **Thor gen: Renesas RH850U2A16** (`DRIVE-V7.0.3-…-AFW-RH850-U2A16-…hex`); IGX Thor: Renesas SMCU. Jetson Thor devkit: **no safety MCU** (only a button-power MCU) | DriveOS 6.0.9 MCU docs · DRIVE forum (7.0.3 flash thread) · IGX docs · Jetson Thor design guide |
| Thor SoC | Blackwell iGPU + Neoverse V3AE + FSI safety island (DRIVE/IGX SKUs only) | datasheet, prior M/U-series audits |
| DriveOS 7 | **Type-1 hypervisor**, "multiple OS domains… on the same SoC"; QNX OS for Safety (pre-certified ASIL-D) + Linux; CUDA, TensorRT, cuDNN, NvMedia, **NvStreams** (zero-copy inter-accelerator) | developer.nvidia.com/drive/os · DriveOS 7.0.3 virtualization docs · QNX Thor GA release |
| Middleware | NvStreams (NVIDIA); **SOME/IP and DDS come with AUTOSAR Adaptive** (`ara::com`), not from NVIDIA. AP has had a **DDS network binding since R18-03** — the same OMG DDS family ROS 2 speaks | RTI "status of DDS in AUTOSAR" · AUTOSAR CM spec |
| DriveWorks SDK | Sensor abstraction layer, dynamic calibration, egomotion, image/point-cloud, DNN tooling | developer.nvidia.com/drive/driveworks + docs |
| AV application | OEM-built stack; NVIDIA ships **Alpamayo as a teacher**: "Rather than running directly in-vehicle, Alpamayo models serve as large-scale teacher models that developers can fine-tune and distill into the backbones of their complete AV stacks" | nvidianews Alpamayo page |
| Cloud loop | The official three-computer framing: DGX (training) · Omniverse/Cosmos on OVX (simulation) · AGX in-vehicle | blogs.nvidia.com three-computer post |

## 2. Where AUTOSAR fits (the user's actual question)

- **AUTOSAR Classic** = statically configured, OSEK-heritage stack for deeply embedded
  MCUs. In this stack it lives at the **bottom row** — zonal/domain ECUs and the board
  safety MCU. Concrete proof on NVIDIA boards: the safety-MCU firmware *is* Vector
  AUTOSAR firmware ("AFW") — on AURIX (Orin) and on RH850 (Thor).
- **AUTOSAR Adaptive** = POSIX/C++ service-oriented platform (`ara::com`) for
  high-performance ECUs — the Thor class. It sits **beside the OEM AV apps on the SoC**,
  and it is a **Tier-1 layer, not NVIDIA IP**: NVIDIA states DRIVE OS "offers full
  support of Adaptive AUTOSAR" (2018 press release), and the actual stacks come from
  Vector ("MICROSAR Adaptive can be enabled on the NVIDIA DRIVE AGX platform"; MICROSAR
  Classic ASIL-D on DRIVE AGX Thor) and Elektrobit (EB corbos), plus TTTech MotionWise
  as a non-AUTOSAR safety framework bundled with QNX.
- **Market reality (secondary, partner-confirmed):** OEMs like Mercedes build custom
  Linux+QNX platforms (MB.OS) and adopt AUTOSAR **selectively** via Vector (Adaptive +
  Classic in the MB.OS base layer) rather than deploying a full off-the-shelf AP stack.
- **Bridge for our team:** AUTOSAR Adaptive's DDS binding (since R18-03) means an AP ECU
  and a ROS 2 node share the same wire family — interop without a gateway is possible
  in principle, with QoS/type-mapping care.

## 3. Corrections vs common folklore

1. "AURIX is the NVIDIA safety MCU" — **Orin-generation only**. Thor-generation
   DRIVE/IGX boards moved to **Renesas RH850 / Renesas SMCU**.
2. AUTOSAR AP's DDS binding dates to **R18-03**, not 18-10.
3. NVIDIA does **not ship** an AUTOSAR stack — "full support" means compatibility;
   Vector/EB provide the products.
4. The Jetson (robotics) Thor devkit has **no safety MCU** — the safety-companion
   pattern is automotive/IGX-specific. On Jetson the equivalent role falls to an
   external MCU you add yourself (our deck's cascade pattern).

## 4. Verification notes

- autosar.org itself was unreachable in-sandbox (TLS); CP/AP one-liners are
  paraphrase-level from cached snippets, cross-checked against multiple secondary
  sources. Marked accordingly in the manifest.
- "QNX safety VM + Linux AI VM run *concurrently* on one Thor" — DriveOS virtualization
  docs say "multiple OS domains… safely and securely run on the same SoC", but the
  fetched page did not name QNX+Linux+Thor in one sentence; kept as the deck's existing
  dual-stack framing with this caveat noted.

## Sources

- developer.nvidia.com/drive/os · /drive/driveworks · DriveOS 7.0.3 virtualization docs
- DriveOS 6.0.9 MCU setup docs (AURIX TC397X + Vector firmware, Orin)
- forums.developer.nvidia.com DRIVE AGX Thor flash thread (AFW-RH850-U2A16, DriveOS 7.0.3)
- docs.nvidia.com/igx SMCU page (Renesas SMCU on IGX Thor)
- Jetson Thor Series Modules Design Guide (no safety MCU; EFM8 power button MCU)
- nvidianews.nvidia.com: functionally-safe platform (Adaptive AUTOSAR / QNX / MotionWise) · Alpamayo teacher-model page
- vector.com: MICROSAR on DRIVE AGX / Thor · MB.OS base layer collaboration
- elektrobit.com: EB corbos / EB tresos on NVIDIA DRIVE, AURIX deliveries
- rti.com blog: status of DDS in AUTOSAR (binding since R18-03)
- autosar.org standards pages (paraphrase-level, TLS-blocked in sandbox)
- blogs.nvidia.com: three-computer framing · QNX-on-Thor GA coverage
