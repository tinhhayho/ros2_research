# Claims audit manifest — research deck (July 2026)

Per-claim audit trail for `slides/research.html` / `slides/research-deck.md`.
Two audit passes: the original 14-headline-claim recheck (early July 2026) and a second
independent recheck (2026-07-11) that triggered the wording corrections recorded here.

Legend — **status**: `confirmed` (primary source matches), `corrected` (deck was fixed),
`scoped` (claim reworded from absolute fact to bounded observation), `conflicting`
(sources disagree; deck now footnotes the conflict), `self-reported` (vendor/project's
own figure, labeled as such), `own-run` (our captured measurement, raw artifact in repo),
`unverified` (kept only as an explicitly-flagged secondary claim).

| # | Slide | Claim (as now stated) | Source (exact URL) | Accessed | Type | Status | Notes |
|---|---|---|---|---|---|---|---|
| 1 | 8 | ROS 2 Jazzy is LTS, EOL May 2029 | https://docs.ros.org/en/jazzy/Releases.html | 2026-07 | primary | confirmed | |
| 2 | 8 | rosbag2 default storage is MCAP | https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html | 2026-07 | primary | confirmed | |
| 3 | 12 | Cartographer no longer actively maintained | https://github.com/cartographer-project/cartographer | 2026-07 | primary | confirmed | README maintenance notice |
| 4 | 12 | Nav2 "100+ companies" | https://docs.nav2.org/ | 2026-07 | vendor self-report | self-reported | Labeled "the project's own count" on the slide |
| 5 | 12 | Autoware "~500 companies" | https://autoware.org/about/why-autoware/ | 2026-07 | vendor self-report | self-reported | Labeled "foundation's own figure" |
| 6 | 12, 14 | No ROS exposed in Waymo/Tesla/commercial-humanoid production stacks | (public materials reviewed; proprietary internals not observable) | 2026-07 | inference | scoped | Reworded from "no ROS / ROS 2 mostly absent" to "public materials expose no ROS 2" |
| 7 | 7 | ROS 2 default graph is not by itself a hard-RT boundary; intra-process can bypass serialization; DDS can be configured for deterministic use | https://design.ros2.org/articles/intraprocess_communications.html · https://design.ros2.org/articles/realtime_proposal.html | 2026-07-11 | primary | corrected | Replaced absolute "every message serialized / DDS not RT at all / 10 kHz impossible" |
| 8 | 7 | ~50 µs PREEMPT_RT jitter | https://wiki.linuxfoundation.org/realtime/preempt_rt_versions | 2026-07 | secondary | unverified | Explicitly labeled illustrative, not a constant; own cyclictest capture is roadmap step 4 |
| 9 | 7 | Firm RT = late result worthless, rare misses tolerable | https://docs.kernel.org/core-api/real-time/theory.html | 2026-07-11 | primary | corrected | Definition fixed (was "misses are rare") |
| 10 | 10 | ros2_control loop = read→update→write direct plugin calls at a configured rate | https://control.ros.org/jazzy/doc/getting_started/getting_started.html | 2026-07 | primary | confirmed | 1 kHz stated as common choice, not default; no-malloc/no-locks stated as design obligation |
| 11 | 14 | Figure Helix: S2 7–9 Hz + S1 200 Hz; Helix 02 adds 1 kHz S0 | https://www.figure.ai/news/helix · https://www.figure.ai/news/helix-02 | 2026-07-11 | primary | confirmed | Dual-system rates now per-model, not a universal range |
| 12 | 14 | π0.5 = VLM + flow-matching action expert | https://www.physicalintelligence.company/download/pi05.pdf | 2026-07 | primary | confirmed | Shares the motif, not necessarily Helix's scheduling |
| 13 | 16–18 | Open-RMF architecture: fleet adapters, negotiation, space-time scheduling | https://github.com/open-rmf/rmf · https://github.com/open-rmf/free_fleet | 2026-07 | primary | confirmed | |
| 14 | 20 | Cosmos 3: May 31 2026, MoT 16B/64B, open license | https://nvidianews.nvidia.com (Cosmos 3 announcement) | 2026-07 | primary | confirmed | |
| 15 | 20 | GR00T N1.7: Apr 17 2026, Cosmos-Reason2-2B backbone, commercial OK | https://huggingface.co/blog/nvidia/gr00t-n1-7 · https://github.com/NVIDIA/Isaac-GR00T | 2026-07 | primary | confirmed | |
| 16 | 20 | Isaac ROS 4.5 targets ROS 2 Jazzy | https://nvidia-isaac-ros.github.io/releases/ | 2026-07 | primary | confirmed | 3.x = Humble/Orin |
| 17 | 20 | Jetson Thor: 128 GB, 40–130 W, 2070 sparse-FP4 TFLOPS, $3,499 devkit | https://developer.nvidia.com/blog/introducing-nvidia-jetson-thor-the-ultimate-platform-for-physical-ai/ | 2026-07 | primary | confirmed | |
| 18 | 20 | Thor MIG = 2 instances, technology preview | https://developer.nvidia.com/embedded/jetpack/downloads (JetPack 7.2) | 2026-07-11 | primary | corrected | Was "up to 7" in first research pass; preview caveat added 07-11 |
| 19 | 22–23 | SPE removed on Thor; official block diagram's SPE block disavowed | https://forums.developer.nvidia.com (NVIDIA staff answers) | 2026-07 | primary (staff) | confirmed | |
| 20 | 23 | FSI only on DRIVE/IGX SKUs, not Jetson T5000 | https://forums.developer.nvidia.com/t/functional-safety-island-in-jetson-thor-t5000-module/360033 | 2026-07-11 | primary (staff) | confirmed | |
| 21 | 26, 30, 39 | Jetson Thor and DRIVE Thor = same Thor architecture/SoC family | (NVIDIA marketing materials) | 2026-07-11 | secondary | scoped | Not claimed to be same die/bin/qualification |
| 22 | 26, 30 | GR00T (Cosmos-Reason2-2B) and Alpamayo (Cosmos-Reason 8.2B) share lineage, not one brain | https://huggingface.co/nvidia/Alpamayo-R1-10B | 2026-07-11 | primary | corrected | "One brain" phrasing removed |
| 23 | 26, 30 | Alpamayo 2 Super parameter count | https://nvidianews.nvidia.com/news/nvidia-alpamayo-2-super-robotaxis (34B) vs https://www.nvidia.com/en-us/solutions/autonomous-vehicles/alpamayo/ (32B) | 2026-07-11 | primary | conflicting | NVIDIA's own sources disagree; deck footnotes both |
| 24 | 28 | DriveOS 5.2 ASIL-B (TÜV SÜD, Dec 2022) | https://blogs.nvidia.com/blog/nvidia-drive-os-tuv-sud-safety-certification/ | 2026-07 | primary | confirmed | |
| 25 | 28 | DriveOS 6.0 ASIL-D (Jan 2025) — on Orin, not Thor | https://www.nvidia.com/en-us/ai-trust-center/halos/autonomous-vehicles/ | 2026-07 | primary | confirmed | Audit pass 1 correction, held up in pass 2 |
| 26 | 28 | DRIVE Thor-X "assessed as ASIL-D conformant" (not certified) | https://www.nvidia.com/en-us/ai-trust-center/halos/autonomous-vehicles/ | 2026-07-11 | primary | confirmed | |
| 27 | 28 | QNX OS for Safety 8.0 = ASIL-D / SIL 3 as SEooC, supported on DRIVE AGX Thor | https://qnx.software/en/software/products-and-solutions/qnx-os-and-os-for-safety | 2026-07-11 | primary | corrected | "In the Thor devkit" → "supported on"; OS cert ≠ devkit/vehicle cert |
| 28 | 28–29 | Component/OS certs feed but do not replace the OEM item-level safety case | ISO 26262 structure (SEooC concept) | 2026-07-11 | primary | corrected | Boundary sentence added to both cert slides |
| 29 | 28, 38 | Robotics side: no *completed* product certs; Halos for Robotics announced 2026 | https://www.nvidia.com/en-us/ai-trust-center/halos/robotics/ | 2026-07-11 | primary | corrected | Was "zero certifications" unscoped |
| 30 | 29 | FSI = 4× lockstep Cortex-R52, ~10,000 ASIL-D MIPS | DriveOS 7.0.3 docs "Functional Safety Island" (developer.nvidia.com) | 2026-07 | primary | confirmed | |
| 31 | 29 | >22,000 fault-detection mechanisms | (press/secondary coverage) | 2026-07 | secondary | unverified | Flagged on-slide: "treat the exact count with care" |
| 32 | 29 | Board safety MCU: RH850 (Thor gen), AURIX (Orin gen) | https://forums.developer.nvidia.com (RH850 flashing threads) | 2026-07 | primary (staff) | confirmed | Board-level, outside the SoC |
| 33 | 31 | Hyperion 10: 2× Thor, 14 cam, 9 radar, 1 lidar, 12 USS | https://www.nvidia.com/en-eu/solutions/autonomous-vehicles/drive-hyperion/ | 2026-07-11 | primary | confirmed | |
| 34 | 33 | Mercedes CLA series production since June 4, 2025 (first MB.OS car) | https://group.mercedes-benz.com/innovations/digitalisation/industry-4-0/article.html | 2026-07-11 | primary | corrected | Deck said "in production since Q1 2026" — conflated with driving-stack rollout |
| 35 | 33 | NVIDIA enhanced-L2 for CLA: US rollout expected by end of 2026 | https://blogs.nvidia.com/blog/drive-av-software-mercedes-benz-cla/ | 2026-07-11 | primary | corrected | |
| 36 | 33 | Uber×NVIDIA: 28 cities by 2028; 100k L4 "over time, starting 2027" | https://investor.uber.com/news-events/news/press-release-details/2026/NVIDIA-to-Launch-L4-Software-Driven-Robotaxis-on-Uber-Across-28-Cities-by-2028/default.aspx · https://nvidianews.nvidia.com/news/nvidia-uber-robotaxi | 2026-07-11 | primary | corrected | 100k was previously implied "by 2028" |
| 37 | 33 | NVIDIA automotive revenue $2.3B FY26 (+39% YoY) | https://nvidianews.nvidia.com (Q4 FY26 results) | 2026-07 | primary | confirmed | |
| 38 | 35 | GR00T TensorRT on Thor: 144.9→93.8 ms (vs RTX Pro 5000 / H100) | https://huggingface.co/blog/nvidia/gr00t-n1-7 | 2026-07 | primary | confirmed | Audit pass 1 correction (was misquoted 117→92 vs RTX 5090) |
| 39 | 36 | GR00T run A: load 94.6 s, 107.7 ms avg, P90 109.8 | `docs/img/groot_n17_inference.txt` (this repo) | 2026-07 | own-run | own-run | First-ever run, cold cache |
| 40 | 36–37 | GR00T run B: load 20.5 s, 106.4 ms avg, P90 108.4, peak VRAM 7.5 GB | `slides/assets/groot-run-screenshot.png` (this repo) | 2026-07 | own-run | own-run | Warm cache; VRAM sampled every 2 s (may miss short peaks) |
| 41 | 36 | MSE 0.0030 / 0.0370 = open-loop action-prediction error, n=2 | https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/policy.md | 2026-07-11 | primary + own-run | corrected | Was labeled "accuracy"; ~75/s relabeled generated-step throughput |
| 42 | 20 | GR00T inference VRAM floor 16 GB / fine-tune 40 GB | https://github.com/NVIDIA/Isaac-GR00T | 2026-07 | primary | confirmed | |

## ROS 2 deep-dive claims (added 2026-07-12 — for `research/ros2-deep-dive-2026-07.md`)

Second audited batch: 14 headline claims, re-fetched from primary sources by an
independent audit pass on 2026-07-12. Result: **13 confirmed · 1 corrected**.

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| R1 | Lyrical Luth released May 22 2026, LTS, EOL May 2031, newest ROS 2 | https://raw.githubusercontent.com/ros2/ros2_documentation/rolling/source/Releases/Release-Lyrical-Luth.rst | confirmed | |
| R2 | Kilted Kaiju non-LTS, EOL **November 2026** | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | **corrected** | Research pass said December 2026; REP 2000 says November |
| R3 | ROS 1 Noetic EOL May 31 2025 | https://discourse.openrobotics.org/t/ros-noetic-end-of-life-may-31-2025/43160 | confirmed | |
| R4 | First ROS 2 release Ardent Apalone, December 2017 | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | confirmed | |
| R5 | OSRA announced 2024-03-18; Platinum = Intrinsic, NVIDIA, Qualcomm | https://www.openrobotics.org/blog/2024/3/18/announcing-the-open-source-robotics-alliance-osra | confirmed | |
| R6 | Intrinsic acquired OSRC 2022-12-15; OSRF stayed independent | https://www.openrobotics.org/blog/2022/12/15/intrinsic-acquires-osrc-and-osrc-sg | confirmed | |
| R7 | 2025 Metrics Report: ~1B downloads 2025, 1.3M unique IPs Oct 2025, ROS 2 = 91.2% | https://discourse.openrobotics.org/t/2025-ros-metrics-report/52575 | confirmed | Self-reported by Open Robotics |
| R8 | rmw_zenoh Tier-1 from Kilted; Jazzy default RMW = Fast DDS | https://raw.githubusercontent.com/ros2/ros2_documentation/jazzy/source/Installation/RMW-Implementations.rst · https://github.com/ros2/rmw_zenoh/issues/265 | confirmed | |
| R9 | rosbag2 default storage = MCAP since Iron | https://discourse.openrobotics.org/t/psa-default-ros-2-bag-storage-format-is-changing-to-mcap-in-iron/28489 | confirmed | |
| R10 | REP 2000 Jazzy Tier-1: Ubuntu 24.04 amd64/arm64 + Windows 10 | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | confirmed | |
| R11 | MoveIt 2.10 LTS Jazzy binaries; panda demo.launch.py documented usage | https://picknik.ai/release/jazzy/rolling/2024/06/30/New-MoveIt-LTS-release-for-ROS-2-Jazzy.html | confirmed | |
| R12 | ros_gz_sim_demos diff_drive demo, model vehicle_blue, /model/vehicle_blue/cmd_vel; Jazzy pairs Gazebo Harmonic | https://raw.githubusercontent.com/gazebosim/ros_gz/ros2/ros_gz_sim_demos/config/diff_drive.yaml · https://www.openrobotics.org/blog/2024/5/ros-jazzy-jalisco-released | confirmed | Own-run addendum: the Jazzy **binary** ships `diff_drive.launch.py`, not the `.launch.xml` seen on the ros2 branch |
| R13 | ros2_control_demos: example_1 RRBot / example_2 DiffBot, Jazzy docs on control.ros.org | https://github.com/ros-controls/ros2_control_demos · https://control.ros.org/jazzy/doc/ros2_control_demos/example_2/doc/userdoc.html | confirmed | |
| R14 | ROSCon 2026 Toronto Sept 22–24; ROSCon 2025 Singapore | https://roscon.ros.org/2026/ | confirmed | |
| R15 | One "simple" C++ node = **15 OS threads** (main + executor/rcl + tracing + `dds.*` I/O pack; rmw_fastrtps_cpp, Jazzy) | own capture: `docs/img/demo1_threads.txt` (talker_cpp, 2026-07-14) | own-run | replaces an uncaptured "5–7 threads" figure caught by the 2026-07-14 info audit; thread count varies by RMW vendor |
| R16 | Intra-process comms is **opt-in** per node (`use_intra_process_comms(true)`), rclcpp-only — composition alone does not enable it | https://design.ros2.org/articles/intraprocess_communications.html | confirmed | corrects the 2026-07-14 first-draft wording that implied composition ⇒ automatic pointer-pass (info-audit 2026-07-14, MAJOR 1) |

Own-run artifacts for the deep-dive: `docs/img/ros2_gz_diffdrive.png` (Gazebo Harmonic
diff-drive, before/after 14 s Twist) and `docs/img/ros2_moveit_panda.png` (MoveIt 2
Panda demo in RViz) — captured 2026-07 in the repo's pinned Jazzy container +
`ros-jazzy-ros-gz` / `ros-jazzy-moveit`, Xvfb + software rendering.

## Reproducibility gaps still open (honest list)

- No local `cyclictest` capture yet — the ~50 µs jitter figure stays secondary until
  roadmap step 4 lands.
- GR00T runs lack a pinned model revision + package lock + seed in the repo; the raw
  log and screenshot are committed, the environment bootstrap is not.
- The ">22,000 diagnostic mechanisms" count has no primary NVIDIA document behind it.

## Jetson Thor memory claims (added 2026-07-12)

Fact-check of a submitted third-party memory report; full write-up in
`research/jetson-thor-memory-2026-07.md`. The two NVIDIA PDFs were unreadable by the
audit agent's web tooling, so they were downloaded and read locally with `pdftotext`
(primary-verified).

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| M1 | T5000: 128 GB (8×16 GB) 256-bit LPDDR5X, 273 GB/s peak | https://developer.nvidia.com/downloads/assets/embedded/secure/jetson/thor/docs/jetson-thor-series-modules-datasheet_ds-11945-001.pdf | confirmed | Datasheet DS-11945-001, read locally |
| M2 | T4000: 64 GB (8×8 GB) 256-bit LPDDR5X, same 273 GB/s | same datasheet | confirmed | |
| M3 | Memory max operating frequency 4,266 MHz (≈ 8533 MT/s effective) | same datasheet · https://developer.download.nvidia.com/drive/docs/nvidia-drive-agx-thor-platform-for-developers.pdf | confirmed + derived | 8533 MT/s = 273 GB/s ÷ 32 B, our arithmetic |
| M4 | CPU caches: L1 64+64 KB/core, L2 1 MB/core, 16 MB shared System Cache (both SKUs) | same datasheet | confirmed | Refutes "no SRAM numbers published" |
| M5 | T5000 = 14× / T4000 = 12× Neoverse V3AE | same datasheet | confirmed | |
| M6 | Power: T5000 modes 70/90/120/MAXN, TMP 130 W; T4000 modes 70/MAXN, TMP 90 W | same datasheet | confirmed | 40 W floor exists only on marketing page — not in datasheet |
| M7 | Compute: T5000 2070 / T4000 1200 FP4 TFLOPS (sparse, MAXN) | same datasheet | confirmed | |
| M8 | DRIVE AGX Thor: 64 GB LPDDR5X at 4266 MHz, 273 GB/s | https://developer.download.nvidia.com/drive/docs/nvidia-drive-agx-thor-platform-for-developers.pdf | confirmed | Deck p.6, read locally |
| M9 | "Full Coherency is supported on Tegra devices starting with Thor SoC" (two-way; pre-Thor = one-way I/O coherency) | https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html | confirmed | Verbatim quotes re-fetched by orchestrator |
| M10 | CUDA 13.0: `cudaMallocManaged()` allocations are **not GPU-cached** on Thor | https://developer.nvidia.com/blog/whats-new-in-cuda-toolkit-13-0-for-jetson-thor-unified-arm-ecosystem-and-more/ | confirmed | Verbatim; refutes "managed = low latency" |
| M11 | Registered/pageable host memory on Thor "can outperform both Pinned memory or Unified memory" | https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html | confirmed | Verbatim |
| M12 | Thor uncore has a Unified Coherency Fabric (UCF) + system-level cache PMUs | https://docs.nvidia.com/jetson/archives/r38.2.1/DeveloperGuide/AT/JetsonLinuxDevelopmentTools/PerformanceMonitoring.html | confirmed | Audit pass fetched directly |
| M13 | H100 SXM 3.35 TB/s (HBM3); H200 4.8 TB/s HBM3e; B200 ≈ 8 TB/s HBM3e | https://www.nvidia.com/en-us/data-center/h100/ · https://www.nvidia.com/en-us/data-center/h200/ · https://www.nvidia.com/en-us/data-center/dgx-b200/ | confirmed | H100 "HBM3" label + B200 ~1000 W are datasheet/secondary-corroborated |
| M14 | GH200/GB200 NVLink-C2C: hardware-coherent, up to 900 GB/s, no page migration | https://developer.nvidia.com/blog/nvidia-grace-hopper-superchip-architecture-in-depth/ | confirmed | Refutes "server unified memory = inefficient" as a blanket claim |
| M15 | Jetson Thor GA August 25, 2025 | https://nvidianews.nvidia.com/news/nvidia-blackwell-powered-jetson-thor-now-available-accelerating-the-age-of-general-robotics | confirmed | |
| M16 | Decode roofline on 273 GB/s: 10–20 B params @ 4–8 bit ⇒ ~14–55 tok/s theoretical peak | — | derived | Our arithmetic, assumptions in the memory report §3; not a measured run |

## Thor unified-memory mechanism claims (added 2026-07-12)

Fact-check of a second submitted third-party report (UM mechanism); full write-up in
`research/thor-unified-memory-2026-07.md`.

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| U1 | No page migration on Tegra iGPU — managed memory = coherency/cache maintenance; "migration" absent from Tegra docs | https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html | corrected | Refutes third-party "driver migrates pages when necessary" |
| U2 | Zero-copy: duplicate allocations and transfers "can be avoided" (one SoC DRAM pool) | same appnote | confirmed | Not "cheaper migration" — no copy at all |
| U3 | Thor GPU accesses pageable memory "via the host's page tables"; system `malloc`/`mmap` usable directly on GPU | https://developer.nvidia.com/blog/whats-new-in-cuda-toolkit-13-0-for-jetson-thor-unified-arm-ecosystem-and-more/ | confirmed | Refutes "no ATS-like features on Thor" |
| U4 | `concurrentManagedAccess` = 1 only on Thor-or-later Tegra; `cudaMemPrefetchAsync` unsupported where it is 0 | https://docs.nvidia.com/cuda/cuda-for-tegra-appnote/index.html | confirmed | Verbatim quotes, audit pass |
| U5 | `cudaMemAdvise` / SetPreferredLocation: absent from the Tegra appnote | same appnote | confirmed (absence, scoped) | The third-party tuning advice is dGPU boilerplate |
| U6 | GH200 ATS = single shared per-process page table; CPU/GPU access each other's memory "without page-migrations" | https://developer.nvidia.com/blog/nvidia-grace-hopper-superchip-architecture-in-depth/ | confirmed | |
| U7 | GH200 capacities: up to 480 GB LPDDR5X + 96 GB HBM3 / 144 GB HBM3e (≤624 GB combined) | NVIDIA GH200 datasheet (official PDF) · https://www.nvidia.com/en-us/data-center/grace-hopper-superchip/ | confirmed | |
| U8 | No NVIDIA source ranks CPU–GPU coherence "strength" GH200 > Thor; correct axis = scale/topology (2 dies + 2 memory types vs 1 die + 1 pool) | absence across GH200 blog, Tegra appnote, product docs | scoped (analysis) | Thor Sysmem Full Coherency is two-way HW coherence on-die |
| U9 | Discrete-GPU UM: hardware Page Migration Engine (page faults) since Pascal + driver copies; HMM on Linux; ATS disables HMM | https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/unified-memory.html | confirmed | Refutes "software page migration" label |
| U10 | Jetson T5000 has no NVLink-C2C (NVIDIA staff); 2022 dual-Thor C2C config: no evidence it shipped as of 07/2026 | https://forums.developer.nvidia.com/t/request-for-technical-documentation-regarding-nvlink-c2c-gsc-on-nvidia-drive-thor-t5000/358185 · https://blogs.nvidia.com/blog/drive-thor/ | confirmed + scoped | DRIVE C2C ("GSC") docs partner-gated |
| U11 | Hot Chips 2025: no Thor session (NVIDIA sessions = RTX 5090, ConnectX-8, photonics, GB10); Thor GA was announced during HC week, not as a talk | https://hc2025.hotchips.org/program/ | confirmed | |
| U12 | FSI: "Jetson Thor does not support FSI. IGX Thor supports FSI." (NVIDIA staff) | https://forums.developer.nvidia.com/t/functional-safety-island-in-jetson-thor-t5000-module/360033 | confirmed | Matches deck slide "hidden MCUs" |
| U13 | DRIVE AGX Thor platforms cite AEC-Q100 + ISO 26262 + IATF 16949; AEC-Q100 = reliability qualification, not the functional-safety claim | search-corroborated NVIDIA statements | self-reported/secondary | |
| U14 | Thor DRAM placement (on-module memory-down vs Apple-style PoP) | no Thor teardown found (STH hands-on = specs only) | unverified (inferred from Jetson SoM convention) | Do not assert either way |
| U15 | `cudaMemPrefetchAsync` on one-pool Thor = page-table pre-population | forum-level explanation only | unverified | Benchmark before relying on it |
| U16 | Thor MSS = "scalable coherence fabric" (TRM wording); "single memory controller" oversimplifies; channel count not public | Thor SoC TRM DP-11881-002 (developer-gated; wording via secondary index) | scoped | |

## Automotive stack / AUTOSAR claims (added 2026-07-12)

Behind the `stack-automotive` deck diagram; full write-up in
`research/automotive-stack-autosar-2026-07.md`.

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| A1 | DriveOS = TÜV SÜD-certified automotive OS: Type-1 hypervisor, CUDA, TensorRT, cuDNN, NvMedia, NvStreams | https://developer.nvidia.com/drive/os | confirmed | |
| A2 | QNX OS for Safety (pre-certified ASIL-D) integrated on DRIVE AGX Thor devkit (GA Aug 2025) | QNX/press release + developer.nvidia.com/drive/os | confirmed | Concurrent QNX+Linux-on-one-Thor phrasing: virtualization docs say "multiple OS domains… on the same SoC" — kept with caveat |
| A3 | DriveWorks SDK = sensor abstraction, dynamic calibration, egomotion, image/point-cloud | https://developer.nvidia.com/drive/driveworks | confirmed | |
| A4 | "NVIDIA DRIVE OS offers full support of Adaptive AUTOSAR"; integrates QNX RTOS + TTTech MotionWise | https://nvidianews.nvidia.com/news/nvidia-announces-worlds-first-functionally-safe-ai-self-driving-platform | confirmed | 2018 press; support = compatibility, NVIDIA ships no AUTOSAR stack |
| A5 | Vector: MICROSAR Adaptive "can be enabled on the NVIDIA DRIVE AGX platform"; MICROSAR Classic ASIL-D on DRIVE AGX Thor | https://www.vector.com/int/en/news/news/on-the-fast-track-innovators-race-to-redefine-autonomous-mobility-with-safer-and-smarter-solutions/ | confirmed (via cached snippet of same URL) | |
| A6 | Orin safety MCU = Infineon AURIX TC397X B-Step "supported with Vector firmware" (AFW) | https://developer.nvidia.com/docs/drive/drive-os/6.0.9/public/drive-os-linux-sdk/common/topics/mcu_setup_usage/mcu_setup_and_usage1.html | confirmed | |
| A7 | **Thor-gen safety MCU = Renesas RH850U2A16** (DRIVE AGX Thor, `AFW-RH850-U2A16` firmware); IGX Thor = Renesas SMCU | https://forums.developer.nvidia.com/t/flash-rh850u2a16-via-thor-commands/367577 · https://docs.nvidia.com/igx/user-guide/latest/SMCU/smcu.html | confirmed | **Corrects** "AURIX continues on Thor" (Infineon partnership page ≠ board evidence) |
| A8 | Jetson AGX Thor devkit has no functional-safety MCU (only EFM8 power-button MCU) | Jetson Thor Series Modules Design Guide (PDF) | confirmed (absence, scoped to design guide) | |
| A9 | AUTOSAR Adaptive has a DDS network binding since **R18-03** (same OMG DDS family as ROS 2) | https://www.rti.com/blog/status-of-dds-in-autosar | confirmed | **Corrects** R18-10 folklore |
| A10 | Alpamayo = teacher models: "Rather than running directly in-vehicle… fine-tune and distill into the backbones of their complete AV stacks" | https://nvidianews.nvidia.com/news/alpamayo-autonomous-vehicle-development | confirmed | |
| A11 | AUTOSAR CP = static OSEK-heritage stack for deeply embedded MCUs; AP = POSIX/C++ SoA (`ara::com`) for HPC ECUs | https://www.autosar.org/standards/classic-platform · /adaptive-platform | paraphrase-level | autosar.org TLS-blocked in sandbox; cross-checked vs multiple secondaries |
| A12 | MB.OS base layer built with Vector using AUTOSAR Adaptive + Classic (selective adoption, not full off-the-shelf AP) | https://www.vector.com/int/en/news/news/mercedes-benz-mbos-base-layer/ | partner-confirmed / secondary | |

## Fleet / UDS / diagnostics claims (added 2026-07-13)

Behind the fleet-management section (deck + blog §6.7) and the six stack diagrams
`stack-autosar-classic` / `stack-autosar-adaptive` / `uds-diag-stack` / `fleet-uds-flow`
/ `fleet-on-thor` / `sdv-ecu-consolidation`; full audit of the source draft in
`research/fleet-uds-autosar-2026-07.md` (30-claim verdict table there).

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| F1 | UDS = ISO 14229-1 application-layer services; 0x10/0x22/0x2A/0x19/0x31/0x27, 0x34/0x35/0x36/0x37 = download/upload/transfer/exit; DID 0xF190 = VIN | https://www.iso.org/standard/72439.html · https://uds.readthedocs.io/en/stable/pages/knowledge_base/service.html | confirmed | draft omitted 0x35 RequestUpload |
| F2 | DoCAN = ISO 15765-2, DoIP = ISO 13400 (+ ISO 14229-5 UDSonIP) | https://www.iso.org/standard/84211.html · https://www.iso.org/standard/74785.html | confirmed | |
| F3 | Classic diagnostics = DCM + DEM (+NvM), CanTp transport | AUTOSAR CP SWS (DCM/DEM) | confirmed (secondary corroboration) | autosar.org PDFs TLS-blocked in sandbox |
| F4 | Adaptive DM (`ara::diag`) supports **only DoIP** as transport; one diagnostic server per Software Cluster; implements ISO 14229-1 + ASAM SOVD 1.0 | https://www.autosar.org/fileadmin/standards/R22-11/AP/AUTOSAR_SWS_Diagnostics.pdf | confirmed via 2 independent secondaries | primary PDF fetch blocked — flagged |
| F5 | UCM = "Update and Configuration Management"; native FOTA path = UCM `ara::com` transfer API, per-Software-Cluster; UDS 0x34-0x37 an alternate channel | https://www.autosar.org/fileadmin/standards/R21-11/AP/AUTOSAR_SWS_UpdateAndConfigurationManagement.pdf · https://www.elektrobit.com/blog/ota-updates-with-adaptive-autosar/ | confirmed | corrects draft's "Update Configuration Management" + "UDS is the usual path" |
| F6 | SOVD = ISO 17978-1/-2/-3:2026 (REST/HTTP + JSON), complements UDS, fronts HPCs and legacy ECUs | https://www.iso.org/standard/85133.html · https://www.iso.org/standard/86587.html · https://www.asam.net/standards/detail/sovd/ | confirmed | iso.org 403 in sandbox; titles verified via ANSI/iTeh mirrors |
| F7 | Continuous fleet telemetry ≠ UDS 0x2A: 0x2A is time-polled, session-scoped, 0xF2xx-DID-limited; telemetry runs on telematics pipelines; raw UDS not exposed to the internet — TCU/gateway terminates + translates | https://www.iso.org/standard/76882.html · https://www.embitel.com/doip-iso-13400-stack-solution-for-automotive | confirmed (practice-level, secondary) | replaces two refuted draft claims |
| F8 | Classic has SOME/IP Transformer since AUTOSAR 4.2.1 (2016) — predates AP R17-10; Classic also does Ethernet/DoIP/LIN/FlexRay | https://www.some-ip.com/papers/cache/AUTOSAR_SWS_SOMEIPTransformer_4.2.1.pdf | confirmed | refutes draft's "Classic = CAN only" row |
| F9 | Classic OS = AUTOSAR OS, backward-compatible superset of OSEK OS (SC1–SC4); Adaptive apps see POSIX PSE51, platform may use full POSIX | AUTOSAR SWS_OS · RS_OperatingSystemInterface | confirmed via secondaries | |
| F10 | Adaptive ASIL ceiling moving: MICROSAR Adaptive Safe ASIL-B shipping (ASIL-D planned); Wind River Adaptive safety concept assessed ASIL-D-suitable by TÜV SÜD | https://www.vector.com/int/en/news/news/safe-asil-b-autosar-adaptive-software-for-high-performance-control-units-hpc-available/ · https://www.windriver.com/news/press/news-22456 | confirmed | |
| F11 | "Classic on Adaptive" trend does not exist as named; real pattern = Classic vECU in a VM under a hypervisor (consolidation/simulation/HIL) | https://www.elektrobit.com/tech-corner/insights-into-the-virtualization-of-a-classic-autosar-based-ecu-platform/ | refuted-and-replaced | |
| F12 | Thor: no multiple guest VMs in public SDK ("Multiple Guest OS are not supported… QNX or Linux, but not both"); no virtual-Classic-ECU partitions; FSI = dedicated silicon, not a hypervisor partition; no documented DoIP/UDS gateway role (SoC↔MCU link = proprietary "Common Interface over UDP over Ethernet") | https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/core-concepts/FoundationServicesStack1.html · …/soc_to_mcu_communication.html | confirmed (refutes draft architecture) | quote re-fetched this audit. Refined by cross-check: rule = no *mixed* guests — Orin 6.x PCTs are `linux`/`qnx`/`dual-qnx` (…/6.0.6/…/avpct.html) and NVIDIA staff 2024-04-11: "Linux + QNX GOS VM is not supported" (forums.developer.nvidia.com/t/hypervisor-drive-orin/289279); policy consistent 6.x→7.x. "Multiple OS domains" = guest(s) + service VMs. Supersedes A2's softer caveat |
| F13 | Vector × Thor (2025-08-25): reference integration for FSI **and** companion MCU; MICROSAR Classic "up to ASIL-D"; "MICROSAR Adaptive can be enabled on NVIDIA DRIVE AGX platform" | https://www.vector.com/int/en/news/news/on-the-fast-track-innovators-race-to-redefine-autonomous-mobility-with-safer-and-smarter-solutions/ | confirmed — **full-page fetch** | upgrades A5 from cached-snippet status |
| F14 | Qualcomm acquired OpenSynergy's virtualization assets (COQOS) 2024-06-10; COQOS SoC list (Qualcomm/NXP/Renesas/TI/Samsung) does not include NVIDIA | https://www.opensynergy.com/qualcomm-acquires-opensynergys-virtualization-assets/ | confirmed (acquisition) / snippet-level (SoC list) | |
| F15 | Thor = Blackwell, "more than 1,000 INT8 TOPS (2,000 FP4 TFLOPs)"; 2022 unveil page (Hopper/Ada, FP8) is stale | https://www.nvidia.com/en-us/solutions/autonomous-vehicles/in-vehicle-computing/ | confirmed | Jetson Thor T5000 (2070 TFLOPS) is a different SKU figure |
| F16 | ECU consolidation trend: distributed → domain → zonal + central; "100+ → under a dozen" are vendor-reported targets | https://www.bosch-mobility.com/en/solutions/control-units/zone-ecu/ · https://www.nxp.com/applications/CENTRAL-COMPUTE | confirmed (framing) / vendor figures labeled | |
| F17 | NVIDIA AUTOSAR ecosystem: Elektrobit + Vector confirmed; ETAS, Neusoft not found with NVIDIA ties | https://www.elektrobit.com/products/ecu/eb-corbos/hypervisor/ · F13 URL | scoped | draft's 4-partner list cut to 2 |

## Robot fleet standards / VDA 5050 claims (added 2026-07-13)

Behind the VDA 5050 deck slides and the `vda5050-interface` / `fleet-standards-map`
diagrams; full audit of the second external draft in
`research/vda5050-robot-fleet-2026-07.md` (14-claim verdict table there).

| # | Claim (as now stated) | Source (exact URL) | Status | Notes |
|---|---|---|---|---|
| V1 | VDA 5050 = vendor-neutral fleet-control↔robot interface, published by VDA + VDMA + KIT-IFL | https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md · https://ifr.org/post/vda-5050-explained | confirmed | spec §2 quote verified in raw fetch |
| V2 | Current version 3.0.0, released 2026-03-19; v2.0 = 01/2020, v2.1 = 08/2024 | https://github.com/VDA5050/VDA5050/releases/tag/3.0.0 | confirmed — **release API + spec header fetched directly** | "as released by the VDA on March 19th, 2026" |
| V3 | Transport = MQTT (3.1.1 min) + JSON; topics order/instantActions/state/visualization/connection/factsheet + zoneSet/responses (v3.0); scheme vda5050/v3/&lt;manufacturer&gt;/&lt;serialNumber&gt;/&lt;topic&gt; | VDA5050_EN.md §4 | confirmed (direct fetch) | the draft omitted the wire protocol entirely |
| V4 | Orders = node/edge graphs; released "base" vs planned "horizon"; master control does traffic control by releasing edges — but the traffic/deadlock LOGIC is explicitly out of spec scope | VDA5050_EN.md §2, §5.3 | confirmed (direct fetch) | |
| V5 | v3.0 zones: BLOCKED/LINE_GUIDED/RELEASE/COORDINATED_REPLANNING/SPEED_LIMIT/ACTION/PRIORITY/PENALTY/DIRECTED/BIDIRECTED; **no "charging zone"** — charging = startCharging/stopCharging actions | VDA5050_EN.md §6.4, §6.2.3.1 | confirmed (direct fetch; 0 grep hits for charging zone) | refutes the draft's zone list |
| V6 | Factsheet since v1.1 (2020); physically detailed (geometry, envelope curves, protocol features) but no semantic sensor/perception model (coarse localizationTypes only) | VDA5050_EN.md §7.10 · coatyio.github.io/vda-5050-lib.js | confirmed | draft's "basic" criticism re-aimed |
| V7 | Adoption: Europe-strongest (SYNAOS ecosystem: KUKA/Omron/SEW/STILL/Jungheinrich/MiR; Bosch Rexroth; DS Automotion), real NA uptake (OTTO by Rockwell certifications), Asia fragmented | https://www.synaos.com/en/blog/vda-5050-massrobotics-open-rmf · https://ottomotors.com/company/newsroom/press-releases/otto-adds-vda-5050-certifications-to-support-mixed-fleet-deployments/ | confirmed (secondary) | |
| V8 | Scope limits: no cybersecurity (broker/TLS's job), no safety, no OTA (updateCertificate = TLS rotation only), flat errorType/errorLevel (no DTC/DID analog) | VDA5050_EN.md §2, §4.1 | confirmed (direct fetch) | |
| V9 | Landscape: MassRobotics AMR Interop = state-reporting only, complementary; OPC 40010 = vertical asset/condition monitoring; Open-RMF can drive robots over VDA 5050 (vda5050_connector; MiR adapter; Isaac Mission Dispatch VDA5050-compliant) | massrobotics.org · reference.opcfoundation.org/specs/OPC-40010-1 · index.ros.org/p/vda5050_connector · github.com/nvidia-isaac/isaac_mission_dispatch | confirmed | draft omitted all three |
| V10 | "Redfish + PICMG IoT.x for robot fleets" = documented nowhere; Redfish = DMTF server/BMC management; PICMG IoT.1 (2021) = factory sensors, Redfish extension still WIP | https://www.dmtf.org/standards/redfish · picmg.org | not-documented — struck from publication | the draft's fabricated-trend claim |
| V11 | AMR OTA: no interop standard; de-facto tooling = Mender/RAUC/SWUpdate; platform telemetry in practice = ROS 2 /diagnostics + vendor clouds (InOrbit/Formant) | inorbit.ai docs ("/diagnostics or /diagnostics_agg… can be configured") | confirmed (practice-level) | |
| V12 | ISO 3691-4 = the safety complement (VDA 5050 explicitly disclaims safety scope, cites 3691-4 for its Mobile Robot definition) | VDA5050_EN.md §2/§3.1/Bibliography | confirmed (direct fetch) | |
