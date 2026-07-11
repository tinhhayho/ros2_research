# The full robot software stack — deep research, July 2026

**Scope:** wheeled robots (AMR + autonomous vehicles), humanoids, the fleet layer (Open-RMF),
the platform layers underneath (firmware/real-time, simulation, dev/ops, safety), and the
NVIDIA ecosystem as a whole platform.

**Method:** five parallel research sweeps, each with a hard budget (≤12 web searches +
≤12 fetches, report ≤1100 words, URL required per claim, `[UNVERIFIED]` tag where a primary
source wasn't reached), then synthesized into this document. Claims below inherit those
citations; anything still marked [UNVERIFIED] was not confirmed against a primary source.

---

## 1. The unified layer map

The single most useful finding: **every robot type converges on the same layered shape**, and
the layers below ~1 kHz are identical across wheeled robots, humanoids, and NVIDIA's stack —
that stable bottom half is exactly the embedded/firmware territory.

```
 FLEET / BUILDING   Open-RMF · vendor FMS · VDA 5050        (many robots, one building)
 ──────────────────────────────────────────────────────────
 TASK / COGNITION   mission logic · BTs        | VLA models (GR00T, Helix, π0)  ~1–10 Hz
 AUTONOMY           Nav2 / Autoware (wheeled)  | RL locomotion policy ~50 Hz (humanoid)
 PERCEPTION/STATE   SLAM (slam_toolbox/cuVSLAM), localization, EKF fusion, nvblox
 ══════════════════ ROS 2 graph boundary (DDS/Zenoh via rmw) ═══════════════════
 RT CONTROL ~1 kHz  ros2_control loop on PREEMPT_RT Linux (mainline since 6.12)
 FIELDBUS 1–10 kHz  EtherCAT / CAN-FD / CANopen  (ros2_canopen, ethercat_driver_ros2)
 MCU FIRMWARE       FOC torque/current loops 8–32 kHz · RTOS · safety E-stop path
```

Two boundaries matter:
- **The ROS 2 boundary**: above it, everything is nodes/topics; below it, deterministic loops
  that ROS 2 never touches directly. Even the most ML-heavy humanoids keep a classical 1 kHz
  torque/impedance layer under the RL policy — the ML wave *replaced the planner, not the
  firmware*.
- **The robot boundary**: one robot = one ROS 2 graph. Open-RMF lives entirely above that
  line (§4).

## 2. Wheeled robots

**AMR (indoor) — the de-facto 2026 standard stack** (docs.nav2.org, control.ros.org,
github.com/SteveMacenski/slam_toolbox):
- `ros2_control` (hardware_interface + diff_drive_controller) → `robot_localization` EKF →
  `slam_toolbox` (mapping) + AMCL (localization on a saved map) → **Nav2**
  (BehaviorTree.CPP orchestration; planner/controller/behavior servers; costmap_2d;
  MPPI is the modern controller, 50+ Hz on modest CPUs) → product task layer.
- Cartographer is effectively legacy/unmaintained on ROS 2. No evidence of learned planners
  displacing Nav2 in production AMRs [UNVERIFIED absence].
- Real example: Clearpath/TurtleBot 4 wires exactly this chain
  (docs.clearpathrobotics.com … navigation_demos).

**On-road autonomous vehicles:**
- **Autoware** (autoware.org) is the open reference stack: Core (stable, QA-gated) +
  Universe (experimental) on ROS 2; sensing → localization (NDT) → perception → planning →
  control → drive-by-wire, Lanelet2 HD maps. Adoption ~30 vehicle types / 500 companies;
  first public-road L4 target is shuttles/buses (Tier IV + Isuzu). Humble→Jazzy migration
  in progress (full support ~Apr 2026 [UNVERIFIED — GitHub issue via search]).
- The consumer/robotaxi market (Waymo, Tesla) runs proprietary, increasingly **end-to-end
  learned** stacks — not ROS. The modular→end-to-end shift is the big 2026 trend in driving,
  but has *not* reached indoor AMRs.

## 3. Humanoids

**The 2026 verdict: RL sim-to-real won locomotion.** Classical MPC + whole-body-QP
(500 Hz–1 kHz, the DRC/Atlas lineage) survives as the low-level torque/impedance layer and in
well-modeled subtasks, but the primary locomotion controller on new platforms is an RL policy
trained in Isaac Lab or MuJoCo and deployed at ~50 Hz — even Boston Dynamics moved electric
Atlas to RL-trained "large behavior models" (with TRI).

**Typical loop-rate cascade** (bottom-up): FOC current loops 8–32 kHz on joint MCUs →
EtherCAT/CAN-FD 1–10 kHz → torque/impedance ~1 kHz on PREEMPT_RT/RTOS → state estimation
1–2 kHz → RL policy ~50 Hz on GPU → VLA "System 2" reasoning 1–10 Hz + "System 1" action head
50–200 Hz. **Dual-system VLA is the convergent architecture** (NVIDIA GR00T N1.6, Figure
Helix, Physical Intelligence π0.5).

**ROS 2 reality check for humanoids:** mostly absent from production stacks.
| Player | Stack | ROS 2 role |
|---|---|---|
| Unitree G1/H1 | unitree_sdk2 (CycloneDDS) | optional `unitree_ros2` wrapper only |
| Boston Dynamics Atlas | proprietary + RL/LBM (TRI) | none found [UNVERIFIED] |
| Tesla Optimus | end-to-end NN from FSD lineage | none — vertically integrated |
| Figure 02/03 | Helix VLA in-house | none found [UNVERIFIED] |
| Agility Digit | Jetson (→Thor), Isaac Lab RL | unconfirmed [UNVERIFIED] |
| 1X Neo | Redwood on-device model + heavy teleop | none found [UNVERIFIED] |
| Berkeley Humanoid (Lite) | open hardware + Isaac Lab RL | sub-$5k open platform |

## 4. Open-RMF — what it is and where it sits

**Mental model: air-traffic control for a building full of robots.** It is *not* part of any
robot's stack and never replaces Nav2/DDS. Each robot (or vendor fleet) keeps its own ROS 2
graph; a **fleet adapter** wraps each fleet; RMF core coordinates *across* adapters: traffic
schedule + negotiation, task bidding/dispatch, and shared infrastructure (lifts, doors,
chargers).

```
        [ rmf-web dashboard ]  ← REST/WebSocket
        [ rmf_core: schedule · negotiation · dispatch ]  ← ROS 2
        /                |                \
 [fleet adapter A]  [fleet adapter B]  [door/lift adapters]
        |                |                    |
 [robot A: ROS2+Nav2] [robot B: vendor FMS] [building PLC]
```

- Protocol split: robot↔fleet-manager = whatever the vendor speaks (REST, VDA 5050…);
  fleet-manager↔RMF = ROS 2 (`rmf_fleet_msgs`); RMF↔humans = REST/WebSocket. `free_fleet`
  (the reference adapter) now uses **zenoh** robot-side.
- **Health, July 2026: alive, niche-but-real.** Governance under OSRA (post-Intrinsic);
  active roadmap post Apr 2026; jazzy branches with commits through Jun–Jul 2026; backers:
  CHART, ARTC, Intrinsic. Flagship deployments remain the Singapore healthcare/airport
  program (CGH RoMi-H, Changi) — broad independent adoption is thin.
- **When to use it:** multi-vendor fleet + shared building resources. Single robot or
  single-vendor fleet → skip it (Nav2 + vendor FMS is enough). VDA 5050 is a *wire protocol
  standard*, not a coordinator — it can run underneath RMF or another FMS, it doesn't
  compete with RMF's negotiation/dispatch logic.
- **Runnable demo on our exact setup** (Ubuntu 24.04 + Jazzy + Gazebo Harmonic):
  `rmf_demos` jazzy branch — `ros2 launch rmf_demos_gz office.launch.xml` spawns robots,
  adapters, core, and doors/lifts in sim; add `rmf-web` for the dashboard.

## 5. Platform layers (the firmware-research core)

**Firmware / real-time:**
- **PREEMPT_RT is mainline** since kernel 6.12 (x86_64/ARM64/RISC-V) — tens of µs latency;
  Linux SBC + `ros2_control` (RT thread for the loop, non-RT thread for ROS I/O) is now a
  legitimate soft-RT control host.
- **micro-ROS**: Jazzy branches for FreeRTOS/Zephyr/NuttX; DDS-XRCE via an agent process;
  Zephyr ships it as an upstream module. Adoption skews research/prototype — no evidence of
  certified-product scale use [UNVERIFIED ratio].
- **The decision rule** for an embedded team: MCU-as-ROS-2-node (topics/params on the MCU) →
  micro-ROS. Existing industrial fieldbus → `ros2_canopen` / `ethercat_driver_ros2` into
  ros2_control instead (reuses proven protocols; no DDS on the MCU). Innermost motor loops →
  always custom deterministic firmware, never middleware.
- Safety: ROS 2 itself is not certified; Apex.AI sells the certified derivative
  (ISO 26262 ASIL D). Real robots put E-stop/safety on a PLC or safety-rated MCU **beside**
  ROS 2, wired to cut motion regardless of software. Standards: ISO 3691-4 (AMR),
  ISO 13482 (service robots), IEC 61508 [names not re-verified this pass].

**Simulation matrix:** Gazebo **Harmonic** = the official Jazzy pairing, CPU-friendly,
right default for this repo. Isaac Sim/Lab = photorealism + GPU-parallel RL (needs RTX).
MuJoCo (+MJX) = fast contact dynamics, academic RL default; common dual-sim pattern is
train-in-Isaac, re-validate-in-MuJoCo.

**Dev/ops:** rosbag2 defaults to **MCAP**. ⚠ **Foxglove Studio's open-source edition is
discontinued** (last OSS v1.87.0, Feb 2024; now commercial — community forks exist). Docker
remains the dominant ROS 2 deploy pattern (this repo is already aligned); snaps for
appliance images; Yocto losing ground to container flows for iteration speed.

## 6. The NVIDIA ecosystem

**The "three computers" story:** DGX (train) → OVX/Omniverse+Cosmos (simulate + synthetic
data) → Jetson (deploy). The pieces stack as: Omniverse (USD foundation, free for dev+prod
since ~May 2026 [UNVERIFIED date]) → **Isaac Sim 6.0.1** (Apache-2.0 core on GitHub; Kit SDK
still proprietary-licensed) → **Isaac Lab** (BSD-3, RL/imitation) → **Cosmos** (world models,
synthetic data; used by Figure, Agility, Skild) → **GR00T N1.6** (open weights on HF, Dec
2025) → **Isaac ROS 4.5.0** (July 2026) on **Jetson Orin/Thor**.

**Isaac ROS is the part that touches our world**: ROS 2 Jazzy packages, GPU-accelerated
drop-ins for the classical stack —
| GEM | replaces/accelerates |
|---|---|
| cuVSLAM | slam_toolbox / RTAB-Map |
| nvblox | costmap_2d (dense 3D, <300 ms obstacle updates) |
| Isaac Perceptor | the whole AMR perception bundle (+ Nav2), ref robot Nova Carter |
| cuMotion / Manipulator | MoveIt planning |
| NITROS | zero-copy GPU transport under all of it |

- **x86_64 + discrete RTX is a first-class target** (4.5.0 benchmarks on RTX 5090), but
  there is **no CPU fallback** — every GEM needs CUDA/TensorRT. The lock-in is hardware, not
  source code (repos are public).
- **Version trap:** Isaac ROS 3.x = Humble/Orin; 4.x = Jazzy/Thor+x86. Following "latest"
  docs on an Orin Nano breaks silently.
- Honest verdict: the most complete, most polished vertically-integrated robotics platform
  in 2026 — and the most hardware-locked. Classical Gazebo+Nav2 stays the vendor-neutral,
  CPU-friendly baseline; NVIDIA is the accelerator you opt into per-component.

**This machine (RTX 5070 Ti, 16 GB VRAM)** meets Isaac Sim 6.0's minimum spec exactly
(16 GB VRAM floor, 4080-class recommended) → Isaac Sim + Isaac Lab locomotion examples and
Isaac ROS x86 GEMs are all locally runnable. Cheapest meaningful Jetson: **Orin Nano Super
devkit, $249** (Isaac ROS 3.x/Humble); the 4.x/GR00T deploy target is AGX Thor ($3,499).

## 7. Synthesis: where ROS 2 actually stands, and where we fit

1. **ROS 2's real footprint (2026):** de-facto standard for AMR/industrial mobile robots and
   research; reference-open-stack for AV shuttles (Autoware) while consumer AV is proprietary
   end-to-end; **optional wrapper at best in commercial humanoids**. Teaching ROS 2 = teaching
   the AMR/industrial mainstream, not the humanoid frontier — worth saying out loud in the team intro.
2. **The stable layer is ours.** Across every stack surveyed, the ≤1 kHz territory (FOC loops,
   fieldbus, RT Linux control, safety path) is classical, deterministic, and unchanged by the
   ML wave. An embedded team's fastest path to relevance in robotics runs through
   `ros2_control` + fieldbus + PREEMPT_RT, not through learning to train policies.
3. **The ML wave enters above the RT boundary** and is consolidating on: RL policy for motion
   (50 Hz) + dual-system VLA for tasks (GR00T/Helix/π0 pattern). Interface literacy (what a
   policy consumes/emits) matters even for firmware people; training them does not (yet).
4. **Open-RMF is a fleet-layer topic**, orthogonal to everything robot-internal. Know the
   mental model + run the sim demo; invest more only if multi-vendor building fleets become
   a real requirement.

## 8. Proposed roadmap for this repo (ordered)

1. **`ros2_control` demo** (sim hardware_interface → diff-drive): the missing bridge between
   our middleware demos and real actuation. Highest teaching value per hour.
2. **Gazebo Harmonic** integration (official Jazzy pair) — gives demos a physics world and
   extends our captured-real-output discipline to sim runs.
3. **micro-ROS demo** (Zephyr or FreeRTOS, DDS-XRCE agent in our compose) — the MCU↔ROS 2
   boundary firsthand; pairs with a `ros2_canopen` + **vcan** demo (host already has
   CONFIG_CAN_VCAN) for the fieldbus alternative.
4. **PREEMPT_RT + cyclictest** capture — quantify the RT story we already tell in slides.
5. **Open-RMF `rmf_demos` (jazzy)** — one fleet-layer demo, sim-only.
6. **NVIDIA track (optional, GPU-gated):** Isaac Sim 6.0 + ROS 2 bridge → one Isaac Lab
   locomotion example → Isaac ROS cuVSLAM on x86 vs slam_toolbox comparison.

---
*Sources: inherited per-section from the five research sweeps (URLs inline above). Anything
tagged [UNVERIFIED] needs a primary-source check before being quoted in slides — per this
repo's no-fabricated-output rule, do not put [UNVERIFIED] numbers into `slides/`.*
