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
