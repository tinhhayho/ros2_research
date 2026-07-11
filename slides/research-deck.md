---
marp: true
paginate: true
theme: default
style: |
  section { font-size: 26px; }
  h1 { color: #1b2b4a; }
  h2 { color: #2E5FAC; }
  table { font-size: 22px; }
  code { background: #eef2f8; }
  section.lead h1 { font-size: 50px; }
  section.lead h2 { color: #5b7bb0; font-weight: 500; }
  section.diagram { display: flex; align-items: center; justify-content: center; padding: 14px; }
  section.diagram img { height: 650px; width: auto; max-width: 100%; }
  .cmd { display:inline-block; background:#11233f; color:#e8eefc; padding:8px 16px;
         border-radius:8px; font-family:monospace; font-size:22px; margin:4px 0; }
  .ok { color:#2e7d32; font-weight:bold; }
  .bad { color:#c62828; font-weight:bold; }
  .gloss { font-size:17px; color:#66708a; border-top:1px solid #dde3ee;
           margin-top:16px; padding-top:6px; }
---

<!-- _class: lead -->

# Robot software stacks — 2026
## wheeled · humanoid · fleet · NVIDIA Physical AI

Findings from a deep-research pass (July 2026).
Every external claim is URL-sourced and audited; **every demo number is from a real run on our machine.**

---

## Agenda

1. **The map** — one stack shape for every robot, and who does what per layer
2. **ROS 2 up close** — the two worlds, key repos, real code, a live graph
3. **Reality check** — wheeled AMR & AV · humanoids · where ROS 2 actually stands
4. **Fleet layer** — Open-RMF: the picture, the responsibility split, the Fleet Adapter
5. **NVIDIA Physical AI** — Cosmos · GR00T · Isaac · Jetson Thor (inside the chip)
6. **Physical AI vs Automotive** — same silicon, different rules (DRIVE, Alpamayo, certifications)
7. **Trust, but audit** + **live GR00T demo** on this machine
8. **So what** — what it means for an embedded team, and our roadmap

---

## How this research was made

- Primary sources (official docs, GitHub, Hugging Face, arXiv) were swept in **parallel
  research passes with hard budgets**; an **independent audit pass** re-fetched the
  sources for the 14 load-bearing claims
- Audit result: **11 confirmed · 2 corrected · 1 partial** — the corrections made it
  into everything you'll see here
- Full reports live in the repo: `research/robot-software-stack-2026-07.md`,
  `research/nvidia-physical-ai-2026-07.md`
- Finale: we ran **GR00T N1.7 (3B) for real** on this machine — numbers on slide 13

---

<!-- _class: diagram -->

{{diagram:stack-unified}}

---

<!-- _class: diagram -->

{{diagram:layer-tasks}}

---

## Reading the map: three placement rules

**1. The loop rate picks the layer.** Faster + must-run-on-time → lower (MCU/RTOS);
heavier math + latency-tolerant → higher (Linux/GPU). That one rule places everything.

**2. Motor control = three nested loops, two layers.** The current/FOC loop (8–32 kHz)
lives on the MCU — always. The ~1 kHz position loop has two real-world homes:
inside a smart servo drive (industrial pattern) **or** inside `ros2_control` on
PREEMPT_RT (humanoid pattern). Choosing between them is your biggest architecture call.

**3. FK/IK exists twice.** *Control-mode* — Cartesian / whole-body QP (Pinocchio,
allocation-free C++) at 1 kHz inside the RT loop. *Planning-mode* — MoveIt 2,
collision-aware search taking 100s of ms, up in the ROS 2 graph.

> Corollary: **SLAM and path planning are never real-time.** A loop-closure stall pauses
> navigation, not torque — the layers below keep the robot safe on their own.

<div class="gloss">This rate-layering is engineering canon, not our invention: cascade control (inner loop ~10× faster — Åström/Hägglund), rate-monotonic scheduling (Liu & Layland, 1973), Albus's RCS hierarchy (NIST, 1980s — each level ~10× slower), Gat's three-layer architecture (1998)</div>

---

## Real-time ≠ fast — the two worlds inside "ROS 2"

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 14px; margin-top: 6px; }
</style>

**"ROS 2" on our map is really two execution worlds:**
- **The DDS graph** — every message serialized through middleware; ms-class best-effort
  latency. SLAM, Nav2, perception live here.
- **`ros2_control`** — *configured* by ROS 2, but its hot loop **bypasses DDS entirely**:
  the `controller_manager` RT thread runs `read() → update() → write()` as direct C++
  plugin calls. Topics only touch the non-RT side (`/joint_states`, controller switching).

**And real-time means guaranteed worst-case deadline — not speed:**

| Loop | Period | Worst-case jitter | Verdict |
|---|---|---|---|
| MCU FOC | 31–125 µs (8–32 kHz) | ns–µs (hardware timers) | hard RT |
| ros2_control on PREEMPT_RT | 1,000 µs (1 kHz) | ~50 µs ≈ **5%** of period | firm RT — fine |
| same Linux pushed to 10 kHz | 100 µs | ~50 µs ≈ **50%** of period | impossible — the OS ceiling |
| a DDS topic hop | — | ms-class, unbounded | not RT at all |

1 kHz is where Linux stops embarrassing itself **and** where physics stops caring —
mechanical time constants are ms-scale; the µs world belongs to motor electronics.

<div class="gloss">firm RT = misses are rare but not provably impossible; provable hard RT lives on MCU/RTOS/QNX — exactly why DRIVE keeps safety on QNX · jitter figures: cyclictest on mainline PREEMPT_RT</div>

---

## The ROS 2 ecosystem — which repo, and when

<style scoped>
  section { font-size: 20px; padding-top: 38px; }
  table { font-size: 16px; }
  table td, table th { padding: 4px 9px; }
</style>

| Repo (github.com/…) | What it is | Reach for it when |
|---|---|---|
| **ros2/**\* — rclcpp, rclpy, rcl, rmw_\* | the core: client libs → `rcl` → `rmw` middleware abstraction | always — this *is* ROS 2 |
| **ros-controls/ros2_control** + ros2_controllers | RT control framework + stock controllers (diff-drive, joint-trajectory, PID) | the robot has real actuators |
| **ros-navigation/navigation2** | Nav2 — behavior-tree mobile navigation | wheeled autonomy |
| **moveit/moveit2** | manipulation planning (IK, collision-aware) | robot arms |
| **SteveMacenski/slam_toolbox** | 2D lifelong SLAM | mapping + localization |
| **ros2/rosbag2** | record / replay (MCAP format) | data capture, debugging |
| **micro-ROS/**\* | MCU-side client (FreeRTOS / Zephyr / NuttX) | the MCU must be a first-class node |
| **gazebosim** + ros_gz | simulation (Harmonic pairs with Jazzy) | sim & CI |
| **open-rmf/**\* | multi-fleet coordination | many vendors, one building |

Docs: **docs.ros.org** · package index: **index.ros.org** · our distro: **Jazzy (LTS, EOL 2029)** · licenses: Apache-2.0 / BSD throughout — no gates anywhere.

---

## Calling the framework — a complete node in 20 lines

<style scoped>
  section { font-size: 20px; padding-top: 36px; }
  pre { font-size: 15.5px; line-height: 1.25; }
  .gloss { font-size: 14px; margin-top: 6px; }
</style>

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')                               # name on the graph
        self.pub = self.create_publisher(String, 'chatter', 10)  # topic + QoS depth
        self.timer = self.create_timer(0.5, self.tick)           # 2 Hz callback

    def tick(self):
        self.pub.publish(String(data='Hello ROS 2'))

def main():
    rclpy.init()
    rclpy.spin(Talker())    # hand the thread to the executor — callbacks run here
```

Poke it from any shell — discovery is automatic, there is no master to configure:
`ros2 node list` · `ros2 topic echo /chatter` · `ros2 topic hz /chatter` · `ros2 topic info /chatter -v`

<div class="gloss">This exact node runs in our Demo 1 — alongside a C++ twin (rclcpp) publishing the same topic; the listener cannot tell the languages apart · QoS depth 10 = keep-last buffer size</div>

---

## Where firmware plugs in — `hardware_interface`

<style scoped>
  section { font-size: 19.5px; padding-top: 34px; }
  pre { font-size: 14.5px; line-height: 1.22; }
  .gloss { font-size: 14px; margin-top: 5px; }
</style>

```cpp
class MyRobot : public hardware_interface::SystemInterface {
  CallbackReturn on_init(const HardwareInfo & info) override {
    // parse <ros2_control> tags from the URDF; open your CAN / EtherCAT device here
  }
  return_type read(const rclcpp::Time &, const rclcpp::Duration &) override {
    pos_[0] = can_.encoder(0);        // fieldbus → state, every cycle
    return return_type::OK;
  }
  return_type write(const rclcpp::Time &, const rclcpp::Duration &) override {
    can_.torque(0, cmd_[0]);          // command → fieldbus, every cycle
    return return_type::OK;
  }
};
PLUGINLIB_EXPORT_CLASS(MyRobot, hardware_interface::SystemInterface)
```

- `read()`/`write()` run **inside the 1 kHz RT thread** — no malloc, no locks, no DDS here
- Controllers (PID, diff-drive…) are sibling plugins wired to you through shared handles,
  chosen in YAML — swap the control law without touching your driver
- **This class is the front door for a CAN/EtherCAT firmware engineer** —
  `ros2_canopen` and `ethercat_driver_ros2` are exactly this, prebuilt

---

## The graph, live — a real screenshot

<style scoped>
  section { font-size: 18px; padding-top: 34px; }
  h2 { margin-bottom: 2px; }
  img { display: block; margin: 2px auto 0 auto; max-height: 500px; width: auto; max-width: 100%; }
  .gloss { font-size: 13.5px; margin-top: 4px; }
</style>

{{image:rqt-graph-real}}

<div class="gloss"><b>Real screenshot</b> — rqt_graph attached to our running Demo 1 (this repo, July 2026): a Python <b>/talker</b> and a C++ <b>/talker_cpp</b> publish the same <b>/chatter</b> topic into <b>/listener</b> — the subscriber can't tell the languages apart; the service/action servers idle until called. Nobody configured any master: pure DDS discovery.</div>

---

## Wheeled robots: the settled part

**Indoor AMR — the de-facto standard stack (unchanged by the ML wave):**
- `ros2_control` → EKF fusion → `slam_toolbox` + AMCL → **Nav2** (behavior trees,
  MPPI controller) — "trusted by 100+ companies"
- Cartographer is legacy; no learned planner has displaced Nav2 in production

**On-road AV — a split world:**
- **Autoware** (ROS 2): the open reference — ~500 companies, L4 shuttle/bus pilots
- Robotaxi & consumer (Waymo, Tesla): proprietary, increasingly **end-to-end learned**, no ROS

---

<!-- _class: diagram -->

{{diagram:ros2-reality}}

---

## Humanoids: RL won locomotion (2024→2026)

- Classical **MPC + whole-body QP** (the Atlas/DRC lineage) → now the *low-level layer*
- New platforms ship **RL policies trained in simulation** (Isaac Lab / MuJoCo),
  deployed at **~50 Hz** — even electric Atlas moved to RL "large behavior models"
- Task layer converged on **dual-system VLA**: slow reasoning (1–10 Hz) + fast action
  head (50–200 Hz) — GR00T, Figure Helix, π0.5 all share this shape
- **ROS 2 is mostly absent** from commercial humanoids: optional wrapper at Unitree;
  Tesla / Figure / 1X / Atlas run proprietary stacks
- The joint-level firmware underneath (FOC 8–32 kHz, EtherCAT/CAN-FD 1–10 kHz) — unchanged

<div class="gloss">RL = Reinforcement Learning (policy learned by trial in simulation) · MPC = Model Predictive Control · QP = Quadratic Programming (whole-body optimizer) · VLA = Vision-Language-Action model (camera + text in → motion out) · FOC = Field-Oriented Control</div>

---

<!-- _class: diagram -->

{{diagram:rmf-position}}

---

## Open-RMF: when it matters (and when it doesn't)

- **What it is:** the coordination layer for **many robots from many vendors** in one
  building — traffic negotiation, task dispatch, doors/lifts/chargers
- **Not** middleware, **not** a Nav2 replacement — robots plug in via *fleet adapters*
- **Health 2026:** alive under OSRA (+ Intrinsic backing), active Jazzy branches;
  flagship deployments = Singapore hospitals/airport → *niche but real*
- **VDA 5050** is a wire protocol, not a coordinator — it can live *under* RMF
- Rule of thumb: single-vendor fleet, no shared infrastructure → **skip RMF**
- Try it: `rmf_demos` (jazzy) runs a full simulated hotel/office on our exact setup

---

## Open-RMF — who does what: robot vs Core

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 17px; }
  table td, table th { padding: 4px 10px; }
</style>

| Job | Owner | Note |
|---|---|---|
| Local path planning, obstacle avoidance | **the robot** (its own Nav2 / vendor stack) | RMF never touches sensors |
| Global **space-time** scheduling | **RMF Core** | reserves lanes *over time*, not just space |
| Task allocation | **RMF Core** | auction — fleets bid, best offer wins |
| Conflict resolution between fleets | **RMF Core** | negotiation: schedules adjust *before* robots meet |
| Translating RMF <-> vendor API | **Fleet Adapter** | where the real integration work lives |
| Doors, lifts, chargers | **RMF Core + infra adapters** | the robot never talks to the lift directly |

> Coordination is *logically* centralized (one shared schedule) but conflict resolution is
> **negotiated among fleet adapters** — closer to air-traffic control than to a joystick.

---

## Fleet Adapter — where ~80% of the work lives

<style scoped>
  section { font-size: 20px; padding-top: 36px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 14px; margin-top: 6px; }
</style>

`RMF Core <-> rmf_fleet_msgs (standard) <-> Fleet Adapter <-> vendor API (proprietary)`

**Its jobs:** report state (pose, battery, mode) · translate commands · bid for tasks ·
transform coordinates · docking/charging · pause/resume when negotiation says so.

| Integration level | You get | Effort |
|---|---|---|
| **Full Control** | RMF sends paths, adjusts speed — full coordination | high — what most real deployments use |
| Easy Full Control | same idea, simplified API | medium |
| Read Only (+ Blockade) | observe (optionally block) — no control | low |

**Build path:** clone `open-rmf/fleet_adapter_template` → fill `config.yaml` (speeds,
battery, supported tasks) → implement `RobotClientAPI` (position / battery / navigate /
stop) — the template already speaks RMF. Nav2 robots: use **`free_fleet`** instead.
Existing adapters: MiR, Clearpath/OTTO, Gaussian Ecobot… (`open-rmf/awesome_adapters`).

<div class="gloss">rmf_fleet_msgs = RMF's standard ROS 2 message set for fleets · Blockade = read-only mode that can still veto motion · Sources: github.com/open-rmf (fleet_adapter_template, free_fleet, awesome_adapters), rmf docs</div>

---

<!-- _class: diagram -->

{{diagram:nvidia-three-computers}}

---

## NVIDIA Physical AI: what's real in July 2026

| Piece | Status (audited) |
|---|---|
| **Cosmos 3** world model | Real — May 31, 2026; MoT 16B/64B; Linux Foundation license |
| **GR00T N1.7** VLA | Real — Apr 17, 2026; Cosmos-Reason2 backbone; commercial use OK |
| **Isaac Sim 6 / Lab** | Apache-2.0 core / BSD-3; Lab-**Arena** eval = alpha, APIs unstable |
| **Isaac Teleop** | Vision Pro / Quest 3; browser demo needs **no headset** |
| **Isaac ROS 4.5** | ROS 2 Jazzy GEMs: cuVSLAM, nvblox, cuMotion — GPU-only, no CPU path |
| **Jetson Thor** | 128 GB, 40–130 W, $3,499 devkit; MIG = **2** instances (not 7) |

Openness is layered: **weights + code open, CUDA/TensorRT-locked underneath.**

<div class="gloss">MoT = Mixture-of-Transformers (reasoning tower + generation tower in one model) · VLA = Vision-Language-Action model · MIG = Multi-Instance GPU (hardware partitioning) · GEM = an accelerated Isaac ROS package · Sources: nvidianews.nvidia.com, huggingface.co/nvidia, developer.nvidia.com (full list on the References slide)</div>

---

<!-- _class: diagram -->

{{diagram:thor-soc}}

---

## The real spec — NVIDIA's own Thor block diagram

<style scoped>
  section { font-size: 18px; padding-top: 34px; }
  h2 { margin-bottom: 2px; }
  img { display: block; margin: 2px auto 0 auto; max-height: 478px; width: auto; max-width: 100%; }
  .gloss { font-size: 13.5px; margin-top: 4px; }
</style>

{{image:thor-official-block}}

<div class="gloss"><b>Official NVIDIA figure</b> — "Components of NVIDIA Jetson Thor modules", developer.nvidia.com blog (2025). Answer to "what connects CPU and GPU": nothing point-to-point — both sit on the <b>Memory Control Fabric</b> with a shared 16 MB system cache and 128 GB unified DRAM. ⚠ Accuracy note: the <b>SPE/RTOS block in this official figure was later disavowed by NVIDIA staff</b> ("there is no SPE R5 core in Thor SoC") — even vendor diagrams deserve an audit (next slide).</div>

---

## Inside Thor — the hidden MCUs (what's public)

<style scoped>
  section { font-size: 21px; }
  table { font-size: 17.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 14px; margin-top: 8px; }
</style>

Beyond CPU+GPU, a Tegra-class SoC ships a village of auxiliary MCU cores — each running
its own firmware. Thor status, verified from NVIDIA docs + staff forum answers:

| Engine | Role | Thor status | Firmware |
|---|---|---|---|
| **BPMP** | boot, clocks, power, thermal | present (in the boot chain) | closed signed blob |
| **PSC** | security root-of-trust (PSCROM/BL1) | present | closed |
| **RCE / DCE** | camera / display engines | present (rollback-protection list) | closed, signed |
| **SPE** | always-on sensor MCU — *Orin's public FreeRTOS door* | <span class="bad">**removed on Thor**</span> — "no SPE R5 core in Thor SoC" (NVIDIA staff) | gone, no replacement SDK |
| **FSI** safety island | lockstep safety cluster | **DRIVE / IGX SKUs only — not on Jetson T5000** | closed |

> For firmware engineers this closes a door: on Jetson Thor there is **no user-programmable
> RTOS core inside the SoC** anymore — your real-time code lives on PREEMPT_RT or on an
> **external MCU over the fieldbus** (the cascade pattern from earlier slides).

<div class="gloss">BPMP = Boot & Power Management Processor · PSC = Platform Security Controller · RCE/DCE = camera/display engines · SPE = Sensor Processing Engine · FSI = Functional Safety Island · Sources: Thor TRM DP-11881-002 (public download) · docs.nvidia.com Jetson Thor boot flow · forums.developer.nvidia.com (NVIDIA staff answers, 2026)</div>

---

<!-- _class: diagram -->

{{diagram:groot-cascade}}

---

<!-- _class: diagram -->

{{diagram:robot-vs-car}}

---

## Same silicon, different rules — the software view

<style scoped>
  section { font-size: 22px; }
  table { font-size: 19px; }
  .gloss { font-size: 15px; margin-top: 8px; }
</style>

| | Robotics (Isaac / Jetson) | Automotive (DRIVE) |
|---|---|---|
| OS | Ubuntu 24.04 + PREEMPT_RT (JetPack 7) | DriveOS 7: hypervisor → **QNX** (safety) + Linux (AI) |
| Middleware | **ROS 2** + Isaac ROS + ros2_control — industry-shared | DriveWorks SDK — every OEM builds its own on top |
| AI model | GR00T N1.7, **3B**, open + commercial OK | Alpamayo-R1 **10.5B** / 2-Super 34B, weights gated |
| Safety cert | none — safety PLC lives *beside* the compute | ASIL-D: DriveOS 6.0 certified — **on Orin; Thor still pending** |
| Real-time | scheduling (PREEMPT_RT) + 2-way MIG | architecture: certified RTOS in its own VM |
| Dev access | $249–$3,499 retail, all on GitHub | gated developer program, no public price |
| Iteration | **days** (pip install, rebuild) | **quarters/years** (safety case per release) |

Shared underneath: **Thor SoC · Cosmos backbone · TensorRT · the three-computer loop.**

<div class="gloss">ASIL = Automotive Safety Integrity Level, ISO 26262 (D = highest) · QNX = safety-certified real-time OS (BlackBerry) · MIG = Multi-Instance GPU · OEM = vehicle manufacturer</div>

---

<!-- _class: diagram -->

{{diagram:driveos-dualstack}}

---

## NVIDIA certifications — who certified what, exactly

<style scoped>
  section { font-size: 19px; padding-top: 40px; }
  table { font-size: 16px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 6px; }
  h2 { margin-bottom: 4px; }
</style>

**Completed, third-party certifications:**

| What (product + version) | Standard · level | Body | When |
|---|---|---|---|
| DriveOS **5.2** — scope incl. CUDA + TensorRT | ISO 26262 · **ASIL-B** | TÜV SÜD | Dec 2022 |
| DriveOS **6.0** | ISO 26262 · **ASIL-D** | TÜV SÜD | Jan 2025 — on **Orin**, not Thor |
| DRIVE core development **process** | ISO 26262 · ASIL-D (process) | TÜV SÜD | Jan 2025 |
| SoC/platform/SW engineering **process** | ISO/SAE 21434 (cybersecurity) | TÜV SÜD | Jan 2025 |
| DRIVE AV / Hyperion platform | UNECE safety **assessment** | TÜV Rheinland | Jan 2025 |
| QNX OS for Safety 8.0 (in the Thor devkit) | ASIL-D · IEC 61508 SIL 3 (SEooC) | BlackBerry/QNX's cert | 2025 |

**"Assessed / capable" — NVIDIA's wording, deliberately weaker than "certified":**
Orin SoC = ASIL-D *systematic* / ASIL-B *random* (assessed) · DRIVE **Thor-X: "assessed as
ASIL-D conformant"** — no completed Thor product cert as of 07/2026 · IGX Thor safety island:
"SIL 3 **capable**" · **Robotics side (Jetson, Isaac ROS, GR00T): zero certifications.**

<div class="gloss">TÜV = Technischer Überwachungsverein, German independent technical-certification bodies (SÜD = Munich, Rheinland = Cologne — rival companies, not branches); an ASIL cert only counts when such an accredited body signs it · SEooC = Safety Element out of Context (certified component awaiting integration) · systematic vs random = design-process faults vs hardware bit-flip faults · Sources: nvidianews.nvidia.com (Jan 6 2025) · docs.nvidia.com AV Safety Report · blogs.nvidia.com (Dec 2022) · qnx.software</div>

---

## DRIVE Thor: how each part earns its ASIL

<style scoped>
  section { font-size: 20px; padding-top: 36px; }
  h2 { margin-bottom: 4px; }
  ul { margin-top: 4px; }
  .gloss { font-size: 13.5px; margin-top: 5px; }
</style>

Certification isn't sprinkled on at the end — every layer is designed for its role:

- **FSI (Functional Safety Island):** 4× dual-core-**lockstep** Cortex-R52, own ~3 MB SRAM
  + crypto module, ~10,000 ASIL-D MIPS — a physically isolated "referee" that monitors the
  rest of the SoC (public DriveOS 7.0.3 docs)
- **SoC-wide diagnostics:** >22,000 fault-detection mechanisms — BIST, watchdogs, NoC
  firewalls, voltage/clock/thermal monitors *(secondary source — treat the exact count with care)*
- **Software partitioning:** Type-1 hypervisor → **QNX ASIL-D VM** (safety functions) kept
  hardware-isolated from the **Linux VM** (AI, rated QM — no safety claim needed)
- **ASIL decomposition:** the AI driving stack stays QM; a certified classical stack
  supervises it → the *system* reaches ASIL-D through redundancy, not by certifying a neural net
- **Board-level referee:** a separate safety MCU (Thor-gen evidence: Renesas **RH850**;
  Orin era used Infineon AURIX) holds final watchdog/power authority *outside* the SoC
- **Process wrapper:** ISO 26262 process cert + ISO/SAE 21434 + UNECE assessment (previous slide)

> The pattern to steal for robots: **isolate the safety brain, keep AI at QM, let a small
> certified core hold the kill switch.**

<div class="gloss">lockstep = two cores execute identical code cycle-by-cycle, mismatch ⇒ fault · QM = Quality Managed (lowest ISO 26262 class, no safety requirement) · decomposition = splitting one ASIL-D requirement across redundant lower-rated elements · BIST = Built-In Self-Test · NoC = Network-on-Chip · Sources: developer.nvidia.com DriveOS 7.0.3 "Functional Safety Island" · qnx.software · forums.developer.nvidia.com (RH850 flashing)</div>

---

## Alpamayo — the driving counterpart of GR00T

<style scoped>
  section { font-size: 22px; }
  table { font-size: 19px; }
  .gloss { font-size: 15px; margin-top: 8px; }
</style>

NVIDIA's framing: **AV 1.0** modular pipeline → **AV 2.0** end-to-end nets → **AV 3.0
reasoning VLA** — Alpamayo (CES Jan 2026) is the 3.0 bet. Same blood as GR00T:

| | GR00T N1.7 (robot) | Alpamayo (car) |
|---|---|---|
| Backbone | Cosmos-Reason2, 2B | Cosmos-Reason, **8.2B** — same family |
| Action head | 32-layer DiT → joint/EEF chunks | 2.3B diffusion decoder → **trajectories** |
| Size / license | 3B — open, commercial OK | R1 = **10.5B** non-commercial · 2 Super = **34B** (robotaxi) |
| Training data | 20,854 h human egocentric video | **80,000 h** multi-cam driving + ~700K reasoning traces |
| Trust model | policy drives the robot directly | **never alone** — certified classical stack supervises |

Tooling mirrors robotics: **AlpaSim** (open sim) · **AlpaGym** (closed-loop RL — the
"Isaac Lab of driving") · **OmniDreams** (world-model scenario generation).

<div class="gloss">AV = autonomous vehicle · VLA = Vision-Language-Action model · DiT = Diffusion Transformer · EEF = end-effector · reasoning traces = recorded chain-of-thought explanations used as training data</div>

---

<!-- _class: diagram -->

{{diagram:hyperion-sensors}}

---

## The hardware itself — DRIVE AGX Thor Developer Kit

<style scoped>
  section { font-size: 18px; }
  img { display: block; margin: 4px auto 2px auto; max-height: 530px; width: auto; max-width: 100%; }
  .gloss { font-size: 14px; margin-top: 6px; }
</style>

{{image:drive-devkit-photo}}

<div class="gloss"><b>Official product photo</b> — DRIVE AGX Thor Developer Kit (developer.nvidia.com blog, Sept 2025 GA): Thor SoC center-board, vertical daughter card, automotive I/O incl. 16× GMSL2 + 2× GMSL3 camera inputs · SKU 10 (bench) / SKU 12 (in-vehicle) · access via the DRIVE AGX SDK Developer Program, no public retail price.</div>

---

## Automotive ships — slowly, and for real

- **Mercedes-Benz CLA** — **in production since Q1 2026**: first MB.OS car, dual-stack
  (AI end-to-end + certified classical) sold as L2++
- **Uber × NVIDIA robotaxi** — LA/SF **H1 2027** → **28 cities by 2028**, targeting
  **100,000 L4 vehicles** on Hyperion 10 + Alpamayo
- Design wins queuing behind: Lucid, JLR, BYD, XPeng, Zeekr, Li Auto
- **Certification sets the pace**: DriveOS 5.2 ASIL-B (2022) → 6.0 **ASIL-D on Orin**
  (2025) → Thor: still *"developed for"* as of July 2026
- Business reality: automotive = **$2.3B FY26** (+39% YoY) — only ~1% of NVIDIA's
  revenue, but design-wins lock in for a decade

> The contrast in one line: robotics ships **experiments weekly**; automotive ships
> **certified products yearly** — and both run the same silicon underneath.

<div class="gloss">L2++ / L4 = SAE driving-automation levels (L2 = assisted, driver responsible; L4 = driverless within a bounded domain) · ASIL = Automotive Safety Integrity Level (ISO 26262) · SOP = start of production · FY26 = NVIDIA fiscal year ending Jan 2026</div>

---

## Which side, as an embedded *software* engineer?

**Robotics day-to-day** — write `ros2_control` hardware_interfaces, EtherCAT/CAN-FD
drivers, MCU firmware, tune PREEMPT_RT, wrap TensorRT policies into ROS 2 nodes.
Everything is inspectable; you ship weekly.

**Automotive day-to-day** — MISRA C/C++, requirements tracing, DriveWorks/AUTOSAR
modules, WCET analysis, safety-case reviews. You ship yearly — but your signature
is what the machine can't replace.

**The overlap IS the career:** real-time, fieldbus, safety boundaries, getting AI
onto silicon — identical skills on both sides of the fence.

> Verdict: **learn on Physical AI** (open, cheap — GR00T already runs on our desk),
> **keep ISO 26262 literacy**. Convergence is coming (same Cosmos brain in GR00T and
> Alpamayo; Halos expanding to robotics) — the bilingual engineer gets paid most.

<div class="gloss">MISRA = automotive C/C++ coding standard · AUTOSAR = automotive SW architecture standard · WCET = Worst-Case Execution Time · ASPICE = automotive process-maturity model · Halos = NVIDIA's full-stack safety program</div>

---

## Trust, but audit

We re-verified the 14 headline claims against primary sources. Two failed:

| Claim as first reported | Audited reality |
|---|---|
| "Thor MIG splits into up to 7 GPU instances" | <span class="bad">Wrong</span> — **2** instances (JetPack 7.2) |
| "GR00T TensorRT: Thor 117→92 ms, vs RTX 5090" | <span class="bad">Wrong</span> — **144.9→93.8 ms**, vs RTX Pro 5000 / H100 |

Lesson for the team: **secondhand Physical-AI numbers drift fast — re-fetch the primary
source before a number goes into a slide.** (That rule is how this deck was built.)

---

## Live demo — a robot foundation model on one desktop GPU

<style scoped>
  section { font-size: 23px; }
  table { font-size: 20px; }
  .gloss { font-size: 15px; margin-top: 8px; }
</style>

**NVIDIA Isaac GR00T N1.7-3B**, zero-shot, on the sample data that ships with the
public **github.com/NVIDIA/Isaac-GR00T** repo — measured on an RTX 5070 Ti (16 GB), July 2026:

| Measured | Value |
|---|---|
| Peak VRAM | **7.5 GB / 16 GB** — no OOM, right at the documented 16 GB floor |
| Latency per policy call | **106.4 ms** avg (P90 108.4 ms) |
| Action throughput | 8-action chunks → **~75 robot actions/s** |
| Accuracy (2 sample trajectories) | MSE 0.0030 / 0.0370 (avg 0.0200) |
| Model load | 20.5 s from local cache (first run: ~95 s incl. 4.6 GB backbone download) |

Everything is public: weights on Hugging Face (`nvidia/GR00T-N1.7-3B` — the gated
`Cosmos-Reason2-2B` backbone needs a one-click license), inference script in the repo.
**Action chunking** turns ~9 calls/s into a usable command rate.

<div class="gloss">zero-shot = no fine-tuning on our data · MSE / MAE = mean squared / absolute error vs recorded reference actions · VRAM = GPU memory · action chunking = one inference emits several future actions · Source: our own captured run (next slide shows it live)</div>

---

<!-- _class: diagram -->

{{image:groot-run-screenshot}}

---

## What this means for an embedded team

1. The layers **below 1 kHz never changed**: FOC loops, fieldbus, RT Linux, safety —
   that's our territory, and every stack (wheeled, humanoid, NVIDIA) still needs it
2. Fastest path to relevance: **`ros2_control` + EtherCAT/CANopen + PREEMPT_RT**
   (mainline since kernel 6.12) — not training policies
3. Learn the **interfaces** of the ML layer (what a policy consumes/emits at 50 Hz),
   not the training internals
4. Safety stays **beside** the compute: safety PLC / safety-rated MCU — no ROS 2 stack
   and no robotics Jetson is safety-certified (only the industrial IGX Thor has the island)

---

## Roadmap for this repo + takeaways

**Next demos, in order:** 1. `ros2_control` (sim hardware) → 2. Gazebo Harmonic →
3. micro-ROS + `ros2_canopen` on vcan → 4. PREEMPT_RT + cyclictest capture →
5. Open-RMF `rmf_demos` → 6. NVIDIA track (Isaac Sim 6 + cuVSLAM vs slam_toolbox)

**Takeaways**
- Every robot type converges on the **same stack shape**; the bottom half is firmware
- **ROS 2 = the industrial mainstream** (AMR standard, AV reference, humanoid absent)
- **Open-RMF** is a fleet-layer tool — adopt only for multi-vendor + shared buildings
- **NVIDIA** ships the most complete platform and the deepest hardware lock-in
- **Robots and cars share one brain (Cosmos)** — certification, not technology, is what splits the two worlds
- Foundation-model robotics **already runs on our desk** — ~106 ms/call, 7.5 GB VRAM

---

## References

<style scoped>
  section { font-size: 14.5px; padding-top: 36px; padding-bottom: 24px; }
  ul { columns: 2; column-gap: 36px; margin-top: 2px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 2px; font-size: 30px; }
  p { margin: 4px 0 2px 0; }
</style>

**Open stacks** ·
- Nav2 — docs.nav2.org · slam_toolbox — github.com/SteveMacenski/slam_toolbox
- ros2_control — control.ros.org · Autoware — autoware.org
- Open-RMF — open-rmf.org · github.com/open-rmf: rmf_demos (jazzy), fleet_adapter_template, free_fleet, awesome_adapters · OSRA — osralliance.org
- ROS 2 core — docs.ros.org · index.ros.org · github.com/ros2, ros-controls, ros-navigation, moveit
- RoMi-H deployment — cgh.com.sg/chart · micro-ROS — micro.ros.org
- PREEMPT_RT mainline — wiki.linuxfoundation.org/realtime · Gazebo — gazebosim.org
- Humanoid RL/VLA: research.nvidia.com/labs/gear (GR00T) · pi.website (π0.5) · figure.ai (Helix)

**NVIDIA Physical AI** ·
- Cosmos 3 — nvidianews.nvidia.com (May 31 2026) · arXiv:2606.02800 · huggingface.co/nvidia/Cosmos3-Nano
- GR00T N1.7 — huggingface.co/blog/nvidia/gr00t-n1-7 · github.com/NVIDIA/Isaac-GR00T
- Isaac Sim/Lab/Arena — github.com/isaac-sim · Isaac Teleop — github.com/NVIDIA/IsaacTeleop
- Jetson Thor — developer.nvidia.com blog "Introducing NVIDIA Jetson Thor" · JetPack 7.2 MIG blog
- Isaac ROS 4.5 — nvidia-isaac-ros.github.io/releases · LeRobot ×NVIDIA — blogs.nvidia.com (Jul 6 2026)

**NVIDIA Automotive** ·
- DRIVE AGX Thor devkit — developer.nvidia.com blog (Sept 2025 GA)
- DriveOS 5.2 ASIL-B — blogs.nvidia.com TÜV SÜD (Dec 2022); DriveOS 6.0 ASIL-D on Orin — eenewseurope.com (Jan 2025)
- QNX × NVIDIA — qnx.software/en/blog/2026 · automotiveworld.com (QNX in Thor devkit)
- DRIVE Hyperion — nvidia.com → solutions → drive-hyperion · Halos — blogs.nvidia.com (GTC 2025)
- Alpamayo — huggingface.co/nvidia/Alpamayo-R1-10B · nvidianews (Alpamayo 2 Super, May 2026)
- Mercedes CLA — blogs.nvidia.com (drive-av-software-mercedes-benz-cla) · Uber robotaxi — investor.uber.com (Mar 2026)
- NVIDIA Q4 FY26 results (automotive $2.3B) — nvidianews.nvidia.com
- Thor SoC TRM DP-11881-002 — developer.nvidia.com download center · FSI — DriveOS 7.0.3 docs "Functional Safety Island"
- Thor internal engines — forums.developer.nvidia.com (NVIDIA staff: SPE removal, FSI/SMCU SKU-gating, RH850)

*Demo numbers (GR00T inference, QoS/RMW matrices) are our own captured runs, July 2026.
Per-claim citations + audit trail live in the accompanying research reports.*
