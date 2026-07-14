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
External claims are URL-sourced; the 14 headline claims were independently re-checked.
**Every demo number is from a real run on our machine.**

---

## Agenda

1. **The map** — one stack shape for every robot, and who does what per layer
2. **ROS 2 up close** — the two worlds, key repos, real code, a live graph
3. **Reality check** — wheeled AMR & AV · humanoids · where ROS 2 actually stands
4. **Fleet layer** — Open-RMF: the picture, the responsibility split, the Fleet Adapter · **VDA 5050 v3.0**
5. **NVIDIA Physical AI** — Cosmos · GR00T · Isaac · Jetson Thor (inside the chip)
6. **Physical AI vs Automotive** — same silicon, different rules (DRIVE, Alpamayo, certifications) + **fleet diagnostics**: UDS · AUTOSAR · SOVD
7. **Trust, but audit** + **live GR00T demo** on this machine
8. **So what** — what it means for an embedded team, and our roadmap

---

## How this research was made

- Primary sources (official docs, GitHub, Hugging Face, arXiv) were swept in **parallel
  research passes with hard budgets**; an **independent audit pass** re-fetched the
  sources for the **14 headline claims** — the remaining claims are source-linked
  but *not* exhaustively audited
- Audit result: **11 confirmed · 2 corrected · 1 partial** — the corrections made it
  into everything you'll see here
- Full reports + per-claim audit trail live in the repo:
  `research/robot-software-stack-2026-07.md` · `research/nvidia-physical-ai-2026-07.md`
- Finale: we ran **GR00T N1.7 (3B) for real** on this machine — numbers on the
  demo slide near the end

---

<!-- _class: diagram -->

{{diagram:stack-unified}}

---

<!-- _class: diagram -->

{{diagram:layer-tasks}}

---

## Which layer does your code go in? — three placement rules

<style scoped>
  section { font-size: 20.5px; padding-top: 32px; }
  h2 { margin-bottom: 4px; }
  p { margin: 7px 0; }
  blockquote { margin: 7px 0; }
  .gloss { font-size: 13.5px; margin-top: 6px; }
</style>

**1. The loop rate picks the layer** — the strongest *first* heuristic, not the only
axis. Faster + must-run-on-time → lower (MCU/RTOS); heavier math + latency-tolerant →
higher (Linux/GPU). Real placement also weighs WCET, fault containment, certification
and bus latency — rate gets you most of the way, the rest is engineering.

**2. Motor control = three nested loops, two layers** *(the common pattern)*. The
current/FOC loop (8–32 kHz) lives on dedicated silicon — MCU, DSP, FPGA or inside a
smart drive. The ~1 kHz position loop has two common homes: inside a smart servo drive
(industrial pattern) **or** inside `ros2_control` on PREEMPT_RT (humanoid pattern).
Choosing between them is your biggest architecture call.

**3. FK/IK exists twice.** *Control-mode* — Cartesian / whole-body QP (Pinocchio,
allocation-free C++) at 1 kHz inside the RT loop. *Planning-mode* — MoveIt 2,
collision-aware search taking 100s of ms, up in the ROS 2 graph.

> Corollary: **SLAM and global path planning stay out of the torque/safety loop.**
> A loop-closure stall then pauses navigation, not torque — *provided* the layers below
> carry independent safety functions. That's a design requirement, not a freebie.

<div class="gloss">WCET = Worst-Case Execution Time · This rate-layering is engineering canon, not our invention: cascade control (inner loop ~10× faster — Åström/Hägglund), rate-monotonic scheduling (Liu & Layland, 1973), Albus's RCS hierarchy (NIST, 1980s — each level ~10× slower), Gat's three-layer architecture (1998)</div>

---

## Real-time ≠ fast — the RT and non-RT worlds inside "ROS 2"

<style scoped>
  section { font-size: 18.5px; padding-top: 32px; }
  h2 { margin-bottom: 4px; }
  ul { margin-top: 4px; margin-bottom: 6px; }
  p { margin: 6px 0; }
  table { font-size: 15px; }
  table td, table th { padding: 3px 8px; }
  .gloss { font-size: 13px; margin-top: 5px; }
</style>

**"ROS 2" on our map is really two execution worlds:**
- **The DDS graph** — messages cross the middleware by default (intra-process C++ can
  bypass serialization); latency typically ms-class, **configuration-dependent**. Not a
  hard-RT boundary by default — DDS *can* be tuned deterministic, but prove it on your
  target. SLAM, Nav2, perception live here.
- **`ros2_control`** — *configured* by ROS 2, but its hot loop **bypasses DDS**: the
  `controller_manager` RT thread runs `read() → update() → write()` as direct C++ plugin
  calls at a **configured rate** (1 kHz is common). Topic data enters via RT-safe buffers.

**Real-time = a deadline you can prove (WCET + jitter), not speed.** Illustrative budget —
~50 µs is a *typical tuned-PREEMPT_RT figure, not a constant*; measure on your own
kernel + hardware (roadmap: our own cyclictest capture):

| Loop | Period | Jitter budget vs period | Verdict |
|---|---|---|---|
| MCU FOC | 31–125 µs (8–32 kHz) | ns–µs (hardware timers) | hard RT |
| ros2_control on PREEMPT_RT | 1,000 µs (1 kHz) | ~50 µs ≈ **5%** of period | comfortable |
| same loop pushed to 10 kHz | 100 µs | ~50 µs ≈ **50%** of period | budget gone — prove it on target, or use dedicated silicon |
| a DDS topic hop (defaults) | — | typically ms-class, config-dependent | keep it out of the torque path |

1 kHz is where well-tuned Linux gets comfortable **and** where physics stops caring —
mechanical time constants are ms-scale; the µs world belongs to motor electronics.

<div class="gloss">hard RT = a missed deadline is a system failure · firm RT = a late result is worthless, but rare misses are tolerable · soft RT = a late result just loses value · DDS itself powers deterministic distributed systems when configured for it (design.ros2.org real-time articles) — the caution here is about ROS graph defaults, not DDS the standard</div>

---

## The ROS 2 ecosystem — which repo to use, and when

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

<!-- _class: diagram -->

{{diagram:node-process-graph}}

---

## A node is a name, not a thread

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  h2 { margin-bottom: 6px; }
  ul { margin-top: 4px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

The word "node" trips up every firmware engineer — it sounds like "task". It isn't:

- A **node = an identity in the graph**: a name (`/camera`) + its endpoints
  (publishers, subscriptions, services, timers, parameters). It's an *object*,
  not a unit of execution
- **The process/thread mapping is free**: 1 process = 1 node (classic, our demo-1
  runs 5 of these) · 1 process = N nodes (**composition**) — and with **opt-in**
  intra-process comms (rclcpp-only: `use_intra_process_comms(true)`), co-located
  nodes pass pointers: no serialization, no network
- **Threads belong to the executor, not the node**: a `SingleThreadedExecutor` runs
  *every* callback of *every* node in it sequentially; `MultiThreadedExecutor` uses a
  pool. DDS adds its own I/O threads underneath either way
- **Callbacks ≠ ISRs**: the executor runs each callback to completion — no priority
  preemption between callbacks. A stuck callback starves a single-threaded executor
  outright (a multi-threaded one merely degrades)
- Corollary you already know: hard-RT loops don't live in callbacks — `ros2_control`
  runs its 1 kHz loop in a plain `SCHED_FIFO` thread *outside* the graph

<div class="gloss">executor = the event loop that dequeues ready work (timer fired, message arrived) and invokes your callbacks · composition = loading several nodes into one container process · measured on our demo-1 (own capture: docs/img/demo1_threads.txt): the C++ talker alone — one node, one process — is <b>15 OS threads</b>: main + executor/rcl + tracing + a dozen <code>dds.*</code> I/O threads (rmw_fastrtps_cpp, the Jazzy default)</div>

---

## The graph is discovered, not drawn

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  h2 { margin-bottom: 6px; }
  table { font-size: 16px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

No GUI, no wiring file, no code generation. A connection exists because **names match**:

`create_publisher("chatter")` in one program + `create_subscription("chatter")` in
another + compatible type & QoS → discovery handshake → an edge in the graph. Stop a
process and its edges vanish. **`rqt_graph` is an X-ray viewer, not an editor.**

Where the real "wiring harness" lives: **topic names in code** + **launch files** —
which start the nodes and re-wire them (`remappings=[('image_raw', '/front_cam/image')]`),
set namespaces and parameters.

| | AUTOSAR Classic (section 6) | ROS 2 |
|---|---|---|
| Connections declared | **ARXML, at build time** (SWC ports) | **topic names, at runtime** |
| Who wires it | generated **RTE** glue | **DDS discovery** matches names |
| The diagram is | the *input* (authoring artifact) | the *output* (an observation) |
| Change a connection | rebuild | restart with a different remap |

<div class="gloss">the one draw-then-run GUI in this ecosystem is Groot2 — but that edits the <i>behavior tree inside</i> a node (Nav2's BT navigator), not the graph between nodes · remapping = renaming a node's topics/name/namespace at launch, the ROS 2 equivalent of re-pinning a harness connector</div>

---

<!-- _class: diagram -->

{{diagram:dds-scope}}

---

<!-- _class: diagram -->

{{diagram:robot-node-graph}}

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

- `read()`/`write()` run **inside the controller_manager RT thread** (rate is configured;
  1 kHz typical) — the hot path **must avoid** malloc, locks and DDS: that's *your* design
  obligation, the framework can't enforce it inside your plugin
- Controllers (PID, diff-drive…) are sibling plugins wired to you through shared handles,
  chosen in YAML — swap the control law without touching your driver
- **This class is the front door for a CAN/EtherCAT firmware engineer** —
  `ros2_canopen` and `ethercat_driver_ros2` are exactly this, prebuilt

---

<!-- _class: diagram -->

{{diagram:graph-to-joint}}

---

## The ROS 2 node graph, live — a real screenshot

<style scoped>
  section { font-size: 18px; padding-top: 34px; }
  h2 { margin-bottom: 2px; }
  img { display: block; margin: 2px auto 0 auto; max-height: 500px; width: auto; max-width: 100%; }
  .gloss { font-size: 13.5px; margin-top: 4px; }
</style>

{{image:rqt-graph-real}}

<div class="gloss"><b>Real screenshot</b> — rqt_graph attached to our running Demo 1 (this repo, July 2026): a Python <b>/talker</b> and a C++ <b>/talker_cpp</b> publish the same <b>/chatter</b> topic into <b>/listener</b> — the subscriber can't tell the languages apart; the service/action servers idle until called. Nobody configured any master: pure DDS discovery.</div>

---

## Wheeled robots — the stack the industry has settled on

**Indoor AMR — the de-facto standard stack (unchanged by the ML wave):**
- `ros2_control` → EKF fusion → `slam_toolbox` + AMCL → **Nav2** (behavior trees,
  MPPI controller) — "100+ companies" *(the project's own count)*
- Cartographer is unmaintained; in the public deployments we reviewed, no learned
  planner has displaced Nav2

**On-road AV — a split world:**
- **Autoware** (ROS 2): the open reference — ~500 companies *(foundation's own figure)*,
  L4 shuttle/bus pilots
- Robotaxi & consumer (Waymo, Tesla): proprietary; public materials show **end-to-end
  learned** stacks and expose no ROS

<style scoped>
  .gloss { font-size: 13.5px; margin-top: 10px; }
</style>

<div class="gloss">EKF = Extended Kalman Filter (fuses wheel odometry + IMU) · slam_toolbox / Cartographer = SLAM packages — build the map while driving · AMCL = Adaptive Monte-Carlo Localization (particle filter: find yourself on an existing map) · MPPI = Model-Predictive Path Integral, Nav2's sampling-based controller · Nav2 = the ROS 2 navigation framework</div>

---

<!-- _class: diagram -->

{{diagram:ros2-reality}}

---

## Humanoids: locomotion moved to RL (2024→2026)

- Classical **MPC + whole-body QP** (the Atlas/DRC lineage) → now the *low-level layer*
- Every new platform we reviewed ships **RL policies trained in simulation**
  (Isaac Lab / MuJoCo), deployed at **~50 Hz** — even electric Atlas moved to
  RL "large behavior models"
- Task layer converged on a **dual-system VLA motif**: slow reasoning + fast action head.
  Rates differ per model — Figure Helix: S2 7–9 Hz + S1 200 Hz (Helix 02 adds a 1 kHz S0);
  GR00T and π0.5 share the shape, not the exact rates
- **Public materials expose no ROS 2** in commercial humanoid production stacks
  (Tesla / Figure / 1X / Atlas are proprietary — internals aren't observable);
  Unitree ships an optional wrapper
- The joint-level firmware underneath (FOC 8–32 kHz, EtherCAT/CAN-FD 1–10 kHz) — unchanged

> Next figure: that cascade in one picture — then we zoom out from *one* robot to
> coordinating a *fleet* of them.

<div class="gloss">RL = Reinforcement Learning (policy learned by trial in simulation) · MPC = Model Predictive Control · QP = Quadratic Programming (whole-body optimizer) · VLA = Vision-Language-Action model (camera + text in → motion out) · FOC = Field-Oriented Control</div>

---

<!-- _class: diagram -->

{{diagram:groot-cascade}}

---

<!-- _class: diagram -->

{{diagram:rmf-position}}

---

## Open-RMF: when it matters (and when it doesn't)

- **What it is:** the coordination layer for **many robots from many vendors** in one
  building — traffic negotiation, task dispatch, doors/lifts/chargers
- **RMF Core is itself ROS 2 nodes** — the scheduler, dispatcher and negotiation arrive
  as nodes + topics in the same graph ("installing RMF" = launching more nodes);
  even doors and lifts join via small adapter nodes
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

## Fleet Adapter — ~80% of the work in an RMF deployment

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

{{diagram:vda5050-interface}}

---

## VDA 5050 — the robot-fleet wire protocol, audited

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  h2 { margin-bottom: 6px; }
  ul { margin-top: 4px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

The industry answer to "how does a fleet manager talk to robots from N vendors":

- **What:** a vendor-neutral interface between fleet control ("master control") and
  AMR/AGVs — published by **VDA + VDMA + KIT-IFL** (the automotive association again!)
- **Current: v3.0.0, released 2026-03-19** — the "AMR release": freely-navigating
  robots, a real **zone concept** (BLOCKED · SPEED_LIMIT · PRIORITY…), CRITICAL/URGENT
  error levels
- **Wire:** **MQTT (3.1.1+) + JSON** — topics `order · instantActions · zoneSet` down,
  `state · factsheet · connection · visualization` up
- **Order = a graph** of nodes/edges; master control releases the **base**, plans the
  **horizon** — that release mechanism *is* the traffic control (the logic itself:
  explicitly out of scope)
- **Factsheet** = robot self-description (geometry, speeds, protocol features — but no
  semantic sensor model)
- **Limits (per the spec itself):** no OTA, and diagnostics is just a flat
  errorType/errorLevel — nothing like the deep automotive diagnostic protocol (**UDS** —
  taught in section 6); security left to broker/TLS config, safety = ISO 3691-4's job
- **Adoption:** Europe-strongest (SYNAOS ecosystem: KUKA, Omron, SEW, STILL, MiR;
  Bosch Rexroth; DS Automotion) + real North-American uptake (OTTO by Rockwell
  certifications); Asia fragmented

> That closes the robot fleet layer — next: the silicon both worlds run on
> (NVIDIA's three computers, then inside the Thor chip).

<div class="gloss">VDA = Verband der Automobilindustrie · VDMA = German machine-builders' association · KIT-IFL = Karlsruhe Institute of Technology, material-handling institute · verified from the spec + GitHub release directly: rows V1–V8, research/vda5050-robot-fleet-2026-07.md · fits the previous slides: RMF can drive robots <i>over</i> VDA 5050 (vda5050_connector; MiR ships an adapter; Isaac Mission Dispatch speaks it)</div>

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
| **Jetson Thor** | 128 GB, 40–130 W, $3,499 devkit; MIG = **2** instances (not 7; preview in JetPack 7.2) |

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

*Optional deep dive (5 slides: MCUs → memory) — short on time? Skip ahead to
"Robotics vs automotive".*

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

## Thor memory — one 273 GB/s pool, no HBM

<style scoped>
  section { font-size: 19.5px; }
  table { font-size: 15.5px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 13.5px; margin-top: 6px; }
</style>

Everything on the die — CPU, GPU, accelerators — shares **one LPDDR5X pool** behind the
Unified Coherency Fabric. No HBM anywhere in the family: that's the power trade.

| | Jetson T5000 | T4000 / DRIVE AGX Thor |
|---|---|---|
| DRAM | **128 GB** LPDDR5X (8×16 GB) | **64 GB** LPDDR5X (8×8 GB) |
| Bus · clock | 256-bit · 4,266 MHz (≈ 8533 MT/s) | same |
| Peak bandwidth | **273 GB/s** | **273 GB/s** — full bandwidth kept |
| CPU | 14× Neoverse V3AE | 12× Neoverse V3AE |
| Caches | L1 64+64 KB · L2 1 MB/core · **16 MB shared system cache** | same |
| Compute (FP4 sparse) | 2070 TFLOPS | 1200 TFLOPS |
| Max module power | 130 W (modes 70/90/120/MAXN) | 90 W (modes 70/MAXN) |

> Memory-bound workloads degrade less on the smaller SKUs than the TFLOPS gap
> suggests — the bandwidth is identical.

<div class="gloss">HBM = High Bandwidth Memory (stacked, data-center) · TMP = Total Module Power · MT/s = megatransfers/s (8533 derived: 273 GB/s ÷ 32 B; the "4,266 MHz" is NVIDIA's printed figure) · Sources: Jetson Thor datasheet DS-11945-001 v1.5 + DRIVE AGX Thor deck (both PDFs read directly, 07/2026). The "40 W floor" seen in marketing does not appear in the datasheet.</div>

---

## CPU–GPU full coherence, new on Thor — allocator advice flipped

<style scoped>
  section { font-size: 20px; }
  table { font-size: 15.5px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 13.5px; margin-top: 6px; }
</style>

- **Orin**: one-way *I/O coherency* — GPU snoops CPU caches; CPU can't see GPU-cache updates
- **Thor**: first Tegra with **Sysmem Full Coherency** — two-way, managed by the hardware fabric

| Allocator | On Thor (CUDA 13.0) |
|---|---|
| `malloc` / `mmap` (pageable, GPU-accessed) | **fastest shared path** — GPU-cached, HW-coherent |
| `cudaHostAlloc` (pinned) | small buffers; no longer the top shared path |
| `cudaMallocManaged` | easy — but **not GPU-cached on Thor**: don't pick it for latency |
| `cudaMalloc` | GPU-only buffers, as always |

> A third-party report we reviewed recommended `cudaMallocManaged` "for low latency" —
> NVIDIA's own docs say the opposite: registered/pageable memory *"can outperform both
> Pinned memory or Unified memory"*. Perception(GPU)→planning(CPU) handoffs now go
> fastest through plain system memory.

<div class="gloss">Quotes verbatim from docs.nvidia.com "CUDA for Tegra" appnote ("Full Coherency is supported on Tegra devices starting with Thor SoC") and the "CUDA Toolkit 13.0 for Jetson Thor" blog ("cudaMallocManaged() allocations are not GPU-cached") · UVM = Unified Virtual Memory</div>

---

## Unified memory on Thor — dGPU folklore vs what actually happens

<style scoped>
  section { font-size: 19px; }
  table { font-size: 14.5px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 13px; margin-top: 6px; }
</style>

A second reviewed report explained Thor's UVM *mechanism* — in discrete-GPU vocabulary.
On a one-pool, hardware-coherent SoC, most of that vocabulary stops applying:

| dGPU folklore | On Thor (one pool, HW-coherent) |
|---|---|
| "The driver **migrates pages** when needed" | **Nothing migrates** — every allocator lands in the same LPDDR5X; only caching + coherence ownership differ ("migration" never appears in the Tegra docs) |
| "**Oversubscription** works, moderately" | Concept doesn't apply — no smaller GPU pool to oversubscribe; the limit is the shared 64/128 GB budget vs the OS |
| "**No ATS**-like features — weaker coherence than GH200" | GPU reaches pageable memory **via the host's page tables**; coherence concedes nothing — GH200's real edge is **scale** (480 GB + HBM over 900 GB/s C2C) |
| "Tune with `cudaMemAdvise` + **prefetch to device**" | `cudaMemAdvise` absent from Tegra docs; prefetch is Thor-only on Tegra (`concurrentManagedAccess=1`) and there is no "device pool" to move bytes to |

> Smell test: advice mentioning *migration, oversubscription or preferred location* was
> written for a discrete GPU. On Thor the whole game is **allocator choice** (previous slide).

<div class="gloss">dGPU = discrete GPU · Even for dGPUs, "software migration" is wrong — since Pascal it's a hardware page-fault engine + driver copies (HMM on Linux) · Sources: CUDA for Tegra appnote · CUDA 13.0 Jetson Thor blog · GH200 architecture blog + datasheet · full audit: research/thor-unified-memory-2026-07.md (claims U1–U16)</div>

---

## 273 GB/s is the budget — size models by bandwidth, not TOPS

<style scoped>
  section { font-size: 19.5px; }
  table { font-size: 15px; }
  table td, table th { padding: 3px 9px; }
  .gloss { font-size: 13px; margin-top: 6px; }
</style>

12–30× below data-center HBM: H100 (HBM3) 3.35 → H200 (HBM3e) 4.8 → B200 ≈ 8 TB/s at
~1000 W. Autoregressive decode re-reads the weights **every token** ⇒ bandwidth-bound:

| Model (quantized) | Bytes/token | Roofline peak | ~Realistic (60–80%) |
|---|---|---|---|
| 10 B @ FP4 | 5 GB | ~55 tok/s | ~33–44 |
| 20 B @ FP4 · 10 B @ FP8 | 10 GB | ~27 tok/s | ~16–22 |
| 20 B @ FP8 | 20 GB | ~14 tok/s | ~8–11 |

**What NVIDIA ships against it:** FP4/FP8 Transformer Engine (2–4× less traffic) ·
TensorRT fusion · MIG 2-way (12 SM inference + 8 SM control, JetPack 7.2 preview) ·
the 16 MB system cache. This is why edge VLA models cluster at 2–10 B params.

> Server nuance: "unified memory is slow on servers" is outdated — GH200/GB200 pair CPU+GPU
> over **NVLink-C2C, hardware-coherent at 900 GB/s**. Thor = the same idea at edge power.

<div class="gloss">Roofline table = derived arithmetic (tok/s ≈ bandwidth ÷ model bytes; batch 1, ignores KV-cache and prefill), <b>not a measured run</b> · VLA = Vision-Language-Action model · full audit trail: research/jetson-thor-memory-2026-07.md + claims-audit rows M1–M16</div>

---

<!-- _class: diagram -->

{{diagram:robot-vs-car}}

---

## Robotics vs automotive — same silicon, different software rules

<style scoped>
  section { font-size: 21px; }
  table { font-size: 18px; }
  .gloss { font-size: 13px; margin-top: 6px; }
</style>

| | Robotics (Isaac / Jetson) | Automotive (DRIVE) |
|---|---|---|
| OS | Ubuntu 24.04 + PREEMPT_RT (JetPack 7) | DriveOS 7: hypervisor → **QNX or Linux** guest + service VMs* |
| Middleware | **ROS 2** + Isaac ROS + ros2_control — industry-shared | DriveWorks SDK — every OEM builds its own on top |
| AI model | GR00T N1.7, **3B**, open + commercial OK | Alpamayo-R1 **10.5B** / 2-Super 34B*, weights gated |
| Safety cert | none — safety PLC lives *beside* the compute | ASIL-D: DriveOS 6.0 certified — **on Orin; Thor still pending** |
| Real-time | scheduling (PREEMPT_RT) + 2-way MIG | architecture: certified RTOS in its own VM |
| Dev access | $249–$3,499 retail, all on GitHub | gated developer program, no public price |
| Iteration | **days** (pip install, rebuild) | **quarters/years** (safety case per release) |

Shared underneath: **the Thor SoC family · the Cosmos-Reason model lineage · TensorRT ·
the three-computer loop** — same architecture, not necessarily the same die or the same model.

<div class="gloss">ASIL = Automotive Safety Integrity Level, ISO 26262 (D = highest) · QNX = safety-certified real-time OS (BlackBerry) · <b>Type-1 hypervisor</b> = runs on bare metal, boots first, schedules entire OSes — "an RTOS whose tasks are OSes"; small enough to certify; isolation means one VM's crash can't reach another · *public SDK runs ONE guest OS at a time — "QNX or Linux, but not both" (only dual-QNX documented, on Orin); dual QNX+Linux is platform framing, rows A2/F12 · MIG = Multi-Instance GPU · OEM = vehicle manufacturer · Alpamayo (NVIDIA's driving model) gets its own slide later this section · *Alpamayo 2 Super: NVIDIA newsroom says 34B, product page says 32B — sources conflict as of 07/2026</div>

---

<!-- _class: diagram -->

{{diagram:driveos-dualstack}}

---

<!-- _class: diagram -->

{{diagram:stack-automotive}}

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
| QNX OS for Safety 8.0 (supported on DRIVE AGX Thor) | ASIL-D · IEC 61508 SIL 3 (SEooC) | BlackBerry/QNX's cert | 2025 |

**"Assessed / capable" — NVIDIA's wording, deliberately weaker than "certified":**
Orin SoC = ASIL-D *systematic* / ASIL-B *random* (assessed) · DRIVE **Thor-X: "assessed as
ASIL-D conformant"** — no completed Thor product cert as of 07/2026 · IGX Thor safety island:
"SIL 3 **capable**" · **Robotics (Jetson, Isaac ROS, GR00T): no completed product certs** —
Halos for Robotics + IGX/QNX safety foundation announced 2026, certs pending.

**The boundary that matters:** these are *component/OS/process* certs (SEooC) — the
**vehicle's** ASIL-D is the OEM's item-level safety case; chip + OS certs feed it, not replace it.

<div class="gloss">TÜV = Technischer Überwachungsverein, German independent certification bodies (SÜD = Munich, Rheinland = Cologne — rivals, not branches); an ASIL cert only counts when such a body signs it · SEooC = Safety Element out of Context (certified component awaiting system integration) · systematic vs random = design-process faults vs hardware bit-flips · Sources: nvidianews.nvidia.com (Jan 6 2025) · docs.nvidia.com AV Safety Report · blogs.nvidia.com (Dec 2022) · qnx.software · nvidia.com Halos</div>

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
- **Software partitioning:** Type-1 hypervisor → the certified **QNX ASIL-D guest** kept
  hardware-isolated from the QM-rated AI stack (dual QNX+Linux = platform framing;
  the public SDK runs one guest at a time — row F12)
- **ASIL decomposition:** the AI driving stack stays QM; a certified classical stack
  supervises it — the architecture that lets the OEM *argue* system-level ASIL-D in its
  item safety case (redundancy instead of certifying a neural net; never automatic)
- **Board-level referee:** a separate safety MCU (Thor-gen evidence: Renesas **RH850**;
  Orin era used Infineon AURIX) holds final watchdog/power authority *outside* the SoC
- **Process wrapper:** ISO 26262 process cert + ISO/SAE 21434 + UNECE assessment (previous slide)

> The pattern to steal for robots: **isolate the safety brain, keep AI at QM, let a small
> certified core hold the kill switch.**

<div class="gloss">lockstep = two cores execute identical code cycle-by-cycle, mismatch ⇒ fault · QM = Quality Managed (lowest ISO 26262 class, no safety requirement) · decomposition = splitting one ASIL-D requirement across redundant lower-rated elements · BIST = Built-In Self-Test · NoC = Network-on-Chip · Sources: developer.nvidia.com DriveOS 7.0.3 "Functional Safety Island" · qnx.software · forums.developer.nvidia.com (RH850 flashing)</div>

---

## Fleet management — the same standards, one layer up

<style scoped>
  section { font-size: 22px; padding-top: 40px; }
  h2 { margin-bottom: 6px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

Running a **fleet** (robotaxis, trucks, delivery vans) means doing four things to
thousands of vehicles you'll never touch physically:

1. **Remote diagnostics** — read fault codes without a workshop visit
2. **Predictive maintenance** — spot the battery/brake/sensor drifting out of spec
3. **OTA updates** — fix software without a recall
4. **Health telemetry** — continuous data feeding the first two

The standards that make this vendor-neutral:

- **UDS (ISO 14229)** — one diagnostic *language* every ECU speaks, whatever the brand
- **AUTOSAR** — one software architecture that fixes *where* diagnostics live in the stack
- **SOVD (ISO 17978, new in 2026)** — the cloud-facing REST/JSON API layered on top

Next five figures: the two AUTOSAR stacks, the UDS path, the honest end-to-end fleet
picture, and why E/E consolidation makes all of it easier.

<div class="gloss">This section began as an external draft report — it went through the standard audit first: 30 claims checked — 7 refuted (incl. the draft's centerpiece "virtual Classic-AUTOSAR ECU partitions on Thor") + 1 with zero public documentation, corrections in <code>research/fleet-uds-autosar-2026-07.md</code> + manifest rows F1–F17. What you see here is the surviving, corrected version.</div>

---

<!-- _class: diagram -->

{{diagram:stack-autosar-classic}}

---

<!-- _class: diagram -->

{{diagram:stack-autosar-adaptive}}

---

## Classic vs Adaptive — the corrected comparison

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16.5px; }
  table td, table th { padding: 4px 10px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| | **AUTOSAR Classic** | **AUTOSAR Adaptive** |
|---|---|---|
| Target | deeply embedded hard-RT ECUs | HPC — central + zonal computers |
| OS | **AUTOSAR OS** (OSEK superset, SC1–SC4) | POSIX — QNX or Linux (apps see **PSE51**) |
| Model | signal-based, **static** — all wired at build time (ARXML) | **service-oriented** — discovery at runtime; production builds pin it down |
| Comms | CAN/LIN/FlexRay **+ Ethernet/SOME/IP since 4.2.1 (2016)** | Ethernet-native: SOME/IP · **DDS binding** |
| Diagnostics | **DCM + DEM** (BSW modules) | **DM** (`ara::diag`) — **DoIP only** |
| Updates | full reflash via bootloader (UDS 0x34/0x36/0x37) | per **Software Cluster** via **UCM** |
| Safety | the mature ASIL-D path | ASIL-B shipping; ASIL-D programs underway |

They **coexist** in one vehicle — Classic on the MCUs, Adaptive on the big computers.

<div class="gloss">Folklore killed by the audit: "Classic can't do Ethernet" — the SOME/IP Transformer landed in Classic 4.2.1 (2016), a year <i>before</i> Adaptive's first release (R17-03, March 2017) · "Adaptive = low ASIL" — Vector ships MICROSAR Adaptive Safe at ASIL-B, Wind River's Adaptive safety concept assessed ASIL-D-suitable by TÜV SÜD (2019 program assessment, not a completed cert) · OSEK = the 1990s automotive RTOS standard Classic's OS descends from · PSE51 = minimal real-time POSIX profile (IEEE 1003.13) · ARXML = AUTOSAR's build-time XML config · <code>ara::</code> = the Adaptive Runtime (ARA) C++ namespace · UCM = Update <i>and</i> Configuration Management · SC = scalability class · full expansions: glossary 3/3 · rows F5, F8–F10</div>

---

<!-- _class: diagram -->

{{diagram:uds-diag-stack}}

---

## The UDS services a fleet actually uses

<style scoped>
  section { font-size: 21px; padding-top: 38px; }
  table { font-size: 16px; }
  table td, table th { padding: 4px 9px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
  h2 { margin-bottom: 6px; }
</style>

| SID | Service | Fleet use |
|---|---|---|
| `0x10` | DiagnosticSessionControl | enter extended/programming session |
| `0x27` | SecurityAccess | seed–key unlock before touching anything sensitive |
| `0x22` | ReadDataByIdentifier | read a **DID**: `0xF190` = VIN, versions, sensor health |
| `0x19` | ReadDTCInformation | read fault codes (**DTC**s) + freeze frames |
| `0x31` | RoutineControl | run a routine: self-test, calibration, pre-flash erase |
| `0x34/0x35/0x36/0x37` | Download / **Upload** / TransferData / TransferExit | flashing (the draft forgot `0x35`) |
| `0x2A` | ReadDataByPeriodicIdentifier | periodic reads — **diagnostic bursts, not telemetry** |

Same bytes on a $2 body ECU and on a central computer: `22 F1 90` → VIN.

<div class="gloss">SID = service ID · DID = data identifier (16-bit, `0xF2xx` reserved for periodic) · DTC = Diagnostic Trouble Code · seed–key = challenge–response unlock · 0x2A is session-scoped and time-polled — continuous fleet telemetry runs on telematics pipelines (MQTT/proprietary), not on UDS; rows F1, F7</div>

---

<!-- _class: diagram -->

{{diagram:fleet-uds-flow}}

---

<!-- _class: diagram -->

{{diagram:fleet-on-thor}}

---

## Fleet reality check — what's documented vs what's hype

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  h2 { margin-bottom: 6px; }
  ul { margin-top: 4px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

**Documented (kept):**

- One gateway/TCU terminates the cloud link; **raw UDS never touches the internet**
- **SOVD (ISO 17978:2026)**: REST/JSON diagnostics for HPCs *and* legacy ECUs — and
  Adaptive's DM already implements ASAM SOVD alongside ISO 14229
- Classic **vECUs under a hypervisor** are real — on EB corbos, and COQOS
  (Qualcomm-owned since 06/2024; supported SoCs: Qualcomm/NXP/Renesas/TI/Samsung)

**Hype (refuted for Thor, public SDK 7.0.3):**

- ~~"Multiple virtual Classic-AUTOSAR ECU partitions on Thor"~~ — *"Multiple Guest OS
  are not supported. In addition, you can run QNX or Linux, but not both."*
- ~~"Thor as the fleet's UDS/DoIP gateway"~~ — zero documentation; the SoC-to-MCU link is
  a proprietary UDP-based interface, and Classic/UDS land is the **companion MCU (RH850)**
- ~~"FSI = hypervisor partition"~~ — FSI is separate lockstep-R52 silicon

> Vector (2025-08-25, primary-fetched): MICROSAR Classic = reference integration for the
> **FSI and companion MCU**, "up to ASIL-D"; MICROSAR Adaptive "can be enabled on
> NVIDIA DRIVE AGX platform" — that's where AUTOSAR really sits on a Thor car.

<div class="gloss">vECU = virtual ECU (a Classic stack in a VM — consolidation/simulation/HIL) · TCU = telematics control unit · sources + verbatim quotes: rows F11–F14, research/fleet-uds-autosar-2026-07.md</div>

---

<!-- _class: diagram -->

{{diagram:sdv-ecu-consolidation}}

---

<!-- _class: diagram -->

{{diagram:fleet-standards-map}}

---

## Two fleets, two standard stacks — what the audit caught

<style scoped>
  section { font-size: 20.5px; padding-top: 38px; }
  h2 { margin-bottom: 6px; }
  ul { margin-top: 4px; }
  .gloss { font-size: 13.5px; margin-top: 8px; }
</style>

**The asymmetry** (previous figure): robots standardized **fleet orchestration**
(VDA 5050 · Open-RMF · MassRobotics) — the layer cars leave operator-proprietary.
Cars standardized **diagnostics, OTA and the platform** (UDS · SOVD · UCM · AUTOSAR) —
the layer robots leave to ROS 2 conventions and vendor tooling. Each side built the
standard the other skipped.

**What the audit caught in the second external draft** (same treatment as the first):

- ✓ *"VDA 5050 v3.0 is current"* — **true**, and better than the draft knew: released
  2026-03-19, most public write-ups still describe v2.x
- ✗ *"charging zone"* — **invented**; the spec's zone types have no such entry
  (charging = `startCharging`/`stopCharging` actions)
- ✗ MQTT/JSON — the actual wire protocol — **never mentioned** in the draft
- ✗ *"Redfish + PICMG IoT.x is being pushed for robot fleets"* — **documented
  nowhere**; two real, unrelated standards stitched into a nonexistent trend
- ✗ landscape omitted: MassRobotics (state-sharing, complementary), OPC 40010
  (asset monitoring), and RMF-over-VDA-5050 (real, shipping integrations)

**The gap both industries share:** no semantic capability/sensor discovery —
nothing like a UDS DID dictionary for "what can this machine actually see and do".

<div class="gloss">verdict tables: research/vda5050-robot-fleet-2026-07.md (V1–V12) + research/fleet-uds-autosar-2026-07.md (F1–F17) · pattern worth remembering: both drafts were right about the standards and wrong about the architecture trends they extrapolated</div>

---

## Alpamayo — the driving counterpart of GR00T

<style scoped>
  section { font-size: 22px; }
  table { font-size: 19px; }
  .gloss { font-size: 15px; margin-top: 8px; }
</style>

NVIDIA's framing: **AV 1.0** modular pipeline → **AV 2.0** end-to-end nets → **AV 3.0
reasoning VLA** — Alpamayo (CES Jan 2026) is the 3.0 bet. Same Cosmos-Reason *lineage*
as GR00T — related models, **not one shared brain**:

| | GR00T N1.7 (robot) | Alpamayo (car) |
|---|---|---|
| Backbone | Cosmos-Reason2, 2B | Cosmos-Reason, **8.2B** — same family |
| Action head | 32-layer DiT → joint/EEF chunks | 2.3B diffusion decoder → **trajectories** |
| Size / license | 3B — open, commercial OK | R1 = **10.5B** non-commercial · 2 Super = **34B*** (robotaxi) |
| Training data | 20,854 h human egocentric video | **80,000 h** multi-cam driving + ~700K reasoning traces |
| Trust model | policy drives the robot directly | **never alone** — certified classical stack supervises |

Tooling mirrors robotics: **AlpaSim** (open sim) · **AlpaGym** (closed-loop RL — the
"Isaac Lab of driving") · **OmniDreams** (world-model scenario generation).

<div class="gloss">AV = autonomous vehicle · VLA = Vision-Language-Action model · DiT = Diffusion Transformer · EEF = end-effector · reasoning traces = recorded chain-of-thought explanations used as training data · *2 Super size: newsroom says 34B, product page says 32B — NVIDIA's own sources conflict (07/2026)</div>

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

## Automotive is shipping for real — just slowly

<style scoped>
  section { font-size: 21px; padding-top: 32px; }
  h2 { margin-bottom: 4px; }
  ul { margin-top: 6px; }
  blockquote { margin: 8px 0; }
  .gloss { font-size: 13px; margin-top: 5px; }
</style>

- **Mercedes-Benz CLA** — series production **since June 2025** (first MB.OS car);
  the NVIDIA-powered enhanced-L2 driving stack ("L2++" — industry term, not an SAE
  level) slated for **US rollout by end of 2026**; dual-stack AI + certified classical
- **Uber × NVIDIA robotaxi** — LA/SF **H1 2027** → **28 cities by 2028**; scaling toward
  **100,000 L4 vehicles** "over time, starting 2027" — on Hyperion 10 + Alpamayo
- Design wins queuing behind: Lucid, JLR, BYD, XPeng, Zeekr, Li Auto
- **Certification sets the pace**: DriveOS 5.2 ASIL-B (2022) → 6.0 **ASIL-D on Orin**
  (2025) → Thor: still *"developed for"* as of July 2026
- Business reality: automotive = **$2.3B FY26** (+39% YoY) — only ~1% of NVIDIA's
  revenue, but design-wins lock in for a decade

> The contrast in one line: robotics ships **experiments weekly**; automotive ships
> **certified products yearly** — and both run the same silicon underneath.

<div class="gloss">L2 / L4 = SAE driving-automation levels (L2 = assisted, driver responsible; L4 = driverless in a bounded domain) · ASIL = Automotive Safety Integrity Level (ISO 26262) · FY26 = NVIDIA fiscal year ending Jan 2026</div>

---

## Robotics or automotive, as an embedded *software* engineer?

**Robotics day-to-day** — write `ros2_control` hardware_interfaces, EtherCAT/CAN-FD
drivers, MCU firmware, tune PREEMPT_RT, wrap TensorRT policies into ROS 2 nodes.
Everything is inspectable; you ship weekly.

**Automotive day-to-day** — MISRA C/C++, requirements tracing, DriveWorks/AUTOSAR
modules, WCET analysis, safety-case reviews. You ship yearly — but your signature
is what the machine can't replace.

**The overlap IS the career:** real-time, fieldbus, safety boundaries, getting AI
onto silicon — identical skills on both sides of the fence.

> Verdict: **learn on Physical AI** (open, cheap — GR00T already runs on our desk),
> **keep ISO 26262 literacy**. Convergence is coming (same Cosmos-Reason lineage in GR00T and
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

Scope, honestly stated: the audit covered these **14 headline claims** — everything else
in the deck is source-linked but *not* exhaustively re-verified.

---

## Live demo — a robot foundation model on one desktop GPU

<style scoped>
  section { font-size: 19px; padding-top: 32px; }
  h2 { margin-bottom: 4px; }
  p { margin: 6px 0; }
  table { font-size: 15.5px; }
  table td, table th { padding: 3px 8px; }
  .gloss { font-size: 13px; margin-top: 5px; }
</style>

**NVIDIA Isaac GR00T N1.7-3B**, zero-shot, on the sample data that ships with the public
**github.com/NVIDIA/Isaac-GR00T** repo — two runs on an RTX 5070 Ti (16 GB), July 2026
(run A = first ever, cold; run B = warm cache — the screenshot next slide is run B):

| Measured | Value |
|---|---|
| Latency per policy call (open-loop) | run A: **107.7 ms** avg (P90 109.8) · run B: **106.4 ms** avg (P90 108.4) |
| Model load | run A (first run, cold cache): **94.6 s** · run B (warm local cache): **20.5 s** |
| Peak VRAM (sampled every 2 s) | **7.5 GB / 16 GB** — no OOM, at the documented 16 GB floor |
| Output per call | 8 future action steps → ~**75 generated steps/s** (compute throughput, *not* an executed robot rate) |
| Open-loop prediction error (n=2) | MSE 0.0030 / 0.0370 vs recorded reference — **not** task-success accuracy |

Everything is public: weights on Hugging Face (`nvidia/GR00T-N1.7-3B` — the gated
`Cosmos-Reason2-2B` backbone needs a one-click license), inference script in the repo.

<div class="gloss">zero-shot = no fine-tuning on our data · open-loop = predictions scored against a recorded trajectory, robot not in the loop — says nothing about closed-loop task success · MSE = mean squared error · VRAM = GPU memory (2 s sampling can miss short peaks) · action chunk = one inference emits 8 future steps; how many get executed before replanning is a deployment choice · Source: our own captured runs (raw log in the repo)</div>

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
4. Safety stays **beside** the compute: safety PLC / safety-rated MCU — as of 07/2026
   no ROS 2 stack and no robotics Jetson has a completed safety cert (IGX Thor has the
   safety island; Halos for Robotics was announced 2026)

---

## Roadmap for this repo + takeaways

**Next demos, in order:** 1. `ros2_control` (sim hardware) → 2. Gazebo Harmonic →
3. micro-ROS + `ros2_canopen` on vcan → 4. PREEMPT_RT + cyclictest capture →
5. Open-RMF `rmf_demos` → 6. NVIDIA track (Isaac Sim 6 + cuVSLAM vs slam_toolbox)

**Takeaways**
- Every robot type converges on the **same stack shape**; the bottom half is firmware
- **ROS 2 = the industrial mainstream** (AMR standard, AV reference; commercial
  humanoids don't expose it publicly)
- **Open-RMF** is a fleet-layer tool — adopt only for multi-vendor + shared buildings
- **NVIDIA** ships the most complete platform and the deepest hardware lock-in
- **Robots and cars share one model lineage (Cosmos-Reason)** — certification, not
  technology, is what splits the two worlds
- Foundation-model robotics **already runs on our desk** — ~106–108 ms/call, 7.5 GB VRAM

---

## Glossary 1/3 — robotics & software

<style scoped>
  section { font-size: 13px; padding-top: 30px; padding-bottom: 20px; line-height: 1.4; }
  ul { columns: 2; column-gap: 30px; margin-top: 4px; }
  li { margin-bottom: 1.5px; break-inside: avoid; }
  h2 { margin-bottom: 4px; font-size: 28px; }
  p { margin: 3px 0 2px 0; font-size: 14px; }
</style>

A lookup slide — don't read it, screenshot it. Every abbreviation from the robotics half:

- **ROS 2** — Robot Operating System 2: middleware framework for robots (not an OS)
- **DDS** — Data Distribution Service: the pub/sub middleware standard under ROS 2 (an OMG standard with several interoperable vendor implementations)
- **executor** — the event loop that runs a node's callbacks; owns the threads (nodes don't)
- **composition / intra-process** — several nodes in one process / the opt-in (rclcpp-only) zero-serialization path between them
- **remapping** — renaming a node's topics, node name or namespace at launch time: ROS 2's wiring harness
- **XRCE-DDS / Agent** — the slimmed client protocol micro-ROS speaks / the big-computer process that joins the graph on the MCU's behalf
- **RMW** — ROS MiddleWare interface: the swappable layer picking the DDS (or Zenoh) implementation
- **QoS** — Quality of Service: per-topic delivery contracts (reliability, history, deadline)
- **LTS / EOL** — Long-Term Support / End Of Life (distro lifecycle)
- **RTOS** — Real-Time Operating System (FreeRTOS, Zephyr, QNX…)
- **MCU / DSP / FPGA** — microcontroller / signal processor / programmable logic — the "dedicated silicon" tier
- **FOC** — Field-Oriented Control: the motor current loop (8–32 kHz)
- **FK / IK** — Forward / Inverse Kinematics: joint angles ⇄ end-effector pose
- **SLAM** — Simultaneous Localization And Mapping
- **AMCL** — Adaptive Monte Carlo Localization (Nav2's localizer)
- **AMR** — Autonomous Mobile Robot (warehouse/indoor)
- **AV** — Autonomous Vehicle
- **RL** — Reinforcement Learning (how humanoid locomotion is trained now)
- **VLA** — Vision-Language-Action model (GR00T, Helix, π0)
- **LLM** — Large Language Model
- **MPPI** — Model-Predictive Path Integral: Nav2's sampling controller
- **EKF** — Extended Kalman Filter (sensor fusion)
- **IMU** — Inertial Measurement Unit
- **WCET** — Worst-Case Execution Time: the number real-time proofs are made of
- **PREEMPT_RT** — the Linux real-time preemption patch set (mainline since 6.12)
- **EtherCAT / CAN-FD / CANopen** — industrial fieldbuses between computer and MCUs
- **Open-RMF / FMS** — Robotics Middleware Framework (open fleet layer) / Fleet Management System
- **OSRF / OSRA** — Open Source Robotics Foundation / Alliance (ROS governance)
- **MoveIt** — ROS 2 manipulation-planning framework (not an acronym, but load-bearing)
- **MSE** — Mean Squared Error (open-loop prediction error — *not* task success)
- **P90** — 90th percentile (latency statistics)
- **VRAM** — GPU memory
- **GA / SOP** — General Availability / Start Of Production

---

## Glossary 2/3 — silicon, memory & automotive

<style scoped>
  section { font-size: 12.5px; padding-top: 28px; padding-bottom: 18px; line-height: 1.38; }
  ul { columns: 2; column-gap: 30px; margin-top: 4px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 4px; font-size: 28px; }
  p { margin: 2px 0 2px 0; font-size: 13.5px; }
</style>

- **SoC / SoM** — System on Chip / System on Module (Jetson = SoM)
- **iGPU / dGPU** — integrated GPU (shares DRAM with CPU) / discrete GPU (own memory)
- **SM** — Streaming Multiprocessor: the GPU's core building block
- **TOPS / TFLOPS** — tera-operations / tera-FLOPs per second (marketing units — check precision + sparsity)
- **FP4 / FP8 / NVFP4** — 4- and 8-bit float formats; NVFP4 = NVIDIA's FP4 recipe
- **LPDDR5X** — low-power DRAM (Thor's one pool) · **HBM** — High Bandwidth Memory (stacked, data-center)
- **MT/s** — megatransfers per second · **TMP** — Total Module Power
- **MIG** — Multi-Instance GPU: hardware partitioning (2-way on Thor, preview)
- **UVM** — Unified Virtual Memory · **ATS** — Address Translation Services (shared page tables) · **HMM** — Heterogeneous Memory Management (Linux)
- **NVLink-C2C** — NVIDIA's coherent chip-to-chip link (GH200) · **UCF** — Unified Coherency Fabric (inside Thor)
- **CUDA / cuDNN / TensorRT** — NVIDIA's compute API / DNN kernels / inference optimizer
- **NvMedia / NvStreams** — DriveOS camera pipeline / zero-copy transport
- **BPMP · PSC · RCE/DCE · SPE · FSI** — Thor's auxiliary MCUs: boot-power · security · camera/display · sensor engine (removed) · safety island
- **SMCU / AFW** — Safety MCU / the Vector "AUTOSAR FirmWare" flashed onto it
- **TRM / BSP** — Technical Reference Manual / Board Support Package
- **ISP / PVA** — Image Signal Processor / Programmable Vision Accelerator
- **DGX / OVX / AGX** — NVIDIA's training / simulation / edge-vehicle computer lines
- **OTA** — Over-The-Air (software updates)
- **OEM / Tier-1** — vehicle manufacturer / its direct supplier (Vector, EB, Bosch…)
- **ASIL** — Automotive Safety Integrity Level, ISO 26262: QM < A < B < C < D
- **QM** — Quality Managed: no safety claim, process only
- **SEooC** — Safety Element out of Context: pre-certified component awaiting integration
- **IEC 61508 / SIL** — the industrial functional-safety standard and its levels
- **AEC-Q100** — automotive IC stress/reliability qualification (not functional safety)
- **IATF 16949** — automotive quality-management standard
- **TÜV** — independent German certification bodies (SÜD and Rheinland are rivals)
- **UNECE** — UN body issuing international vehicle regulations
- **QNX** — BlackBerry's commercial safety-certified RTOS
- **VM / Type-1 hypervisor** — virtual machine / a hypervisor running directly on bare metal (no host OS): boots first, then schedules entire OSes the way an RTOS schedules tasks — small enough to certify, and one VM's crash can't reach another (vs Type-2 = an app inside a host OS, e.g. VirtualBox)
- **AUTOSAR CP / AP** — AUTomotive Open System ARchitecture: Classic (static, MCU) / Adaptive (POSIX, HPC) platforms
- **ara::com** — Adaptive AUTOSAR's communication API
- **SOME/IP** — Scalable service-Oriented MiddlewarE over IP (automotive services)
- **LIN / FlexRay / TSN** — legacy low-cost bus / pre-Ethernet redundant bus / Time-Sensitive Networking (deterministic Ethernet)
- **SAE L2 / L4** — driving-automation levels (assisted, driver liable / driverless in a domain); "L2++" is marketing, not SAE
- **ECU** — Electronic Control Unit (any vehicle computer node)
- **E/E** — Electrical/Electronic (as in "E/E architecture": the vehicle's full electronics layout)
- **HPC** — High-Performance Computer: a vehicle central/zonal computer (Thor-class)

---

## Glossary 3/3 — AUTOSAR & vehicle diagnostics

<style scoped>
  section { font-size: 12.5px; padding-top: 28px; padding-bottom: 18px; line-height: 1.38; }
  ul { columns: 2; column-gap: 30px; margin-top: 4px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 4px; font-size: 28px; }
  p { margin: 2px 0 2px 0; font-size: 13.5px; }
</style>

- **SWC** — Software Component: Classic's unit of application code, wired via ports (never addresses)
- **RTE** — Runtime Environment: the generated glue layer — the only interface SWCs ever see
- **BSW** — Basic Software: Classic's standardized lower layers (Services, ECU Abstraction, MCAL)
- **MCAL** — Microcontroller Abstraction Layer: the standardized vendor-driver layer (≈ the vendor HAL you know)
- **CDD** — Complex Device Driver: the sanctioned bypass lane for drivers that don't fit the BSW layering
- **NvM / WdgM / COM** — Classic BSW services: non-volatile memory · watchdog manager · signal communication
- **ARXML** — AUTOSAR XML: the build-time configuration format everything is generated from
- **OSEK/VDX** — the 1990s European automotive RTOS standard; AUTOSAR OS is its backward-compatible superset
- **AUTOSAR OS / SC1–SC4** — Classic's statically configured RTOS; scalability classes add memory/timing protection
- **ARA / `ara::`** — AUTOSAR Runtime for Adaptive: the platform's C++ API namespace (`ara::com`, `ara::diag`, `ara::ucm`, `ara::exec`…)
- **PSE51** — IEEE 1003.13's minimal real-time POSIX profile — the interface Adaptive *applications* are held to
- **Software Cluster** — Adaptive's unit of deployment: updated by UCM, diagnosed by its own server
- **UDS** — Unified Diagnostic Services, ISO 14229: the standard in-vehicle diagnostic protocol
- **SID** — UDS service identifier: the first request byte (0x22 = read DID, 0x19 = read DTCs…)
- **DTC / DID** — Diagnostic Trouble Code (a stored fault) / Data Identifier (16-bit address of a readable value; 0xF190 = VIN)
- **freeze frame** — the sensor snapshot DEM stores alongside a DTC at the moment of the fault
- **seed–key** — SecurityAccess (0x27) challenge–response: ECU sends a seed, tester answers with the key
- **DoCAN / DoIP** — Diagnostics over CAN (ISO 15765-2) / over Ethernet-IP (ISO 13400) — UDS's two transports
- **DCM / DEM** — Classic's diagnostic modules: Diagnostic Communication Manager (dispatch, sessions, security) / Diagnostic Event Manager (fault memory)
- **DM / UCM** — Adaptive's Diagnostic Manager (`ara::diag`, DoIP-only) / Update and Configuration Management (per-cluster OTA)
- **SOVD** — Service-Oriented Vehicle Diagnostics, ISO 17978 (2026): REST/JSON diagnostic API above UDS
- **ODX / DEXT / PDX** — diagnostic data formats (ISO 22901 "Open Diagnostic data eXchange" / AUTOSAR Diagnostic Extract) and the packaged container file tools load
- **TCU** — Telematics Control Unit: the vehicle's modem + cloud endpoint
- **vECU** — virtual ECU: a Classic AUTOSAR stack running in a VM (consolidation, simulation, HIL)
- **HIL** — Hardware-In-the-Loop: testing real ECU software against simulated plant/vehicle
- **VDA 5050** — the AGV/AMR fleet wire protocol (VDA + VDMA + KIT-IFL); v3.0.0 since 03/2026, MQTT + JSON
- **AGV** — Automated Guided Vehicle: line/track-guided predecessor of the freely-navigating AMR
- **MQTT** — lightweight publish/subscribe messaging protocol (broker-based) — VDA 5050's transport
- **base / horizon** — VDA 5050 order graph: released-for-driving part / planned-but-not-released part
- **MassRobotics AMR Interop** — complementary robot-fleet standard: cross-fleet *state sharing* only, no task assignment
- **OPC 40010** — OPC UA for Robotics: vertical asset/condition monitoring (robot → MES/cloud), not fleet orchestration
- **ISO 3691-4** — safety standard for driverless industrial trucks — the safety half VDA 5050 explicitly leaves out

---

## References

<style scoped>
  section { font-size: 13.5px; padding-top: 30px; padding-bottom: 20px; line-height: 1.35; }
  ul { columns: 2; column-gap: 32px; margin-top: 2px; }
  li { margin-bottom: 1px; break-inside: avoid; }
  h2 { margin-bottom: 2px; font-size: 28px; }
  p { margin: 3px 0 2px 0; }
</style>

**Open stacks** ·
- Nav2 — docs.nav2.org · slam_toolbox — github.com/SteveMacenski/slam_toolbox
- ros2_control — control.ros.org · Autoware — autoware.org
- Open-RMF — open-rmf.org · github.com/open-rmf: rmf_demos (jazzy), fleet_adapter_template, free_fleet, awesome_adapters · OSRA — osralliance.org
- ROS 2 core — docs.ros.org · index.ros.org · github.com/ros2, ros-controls, ros-navigation, moveit
- RoMi-H deployment — cgh.com.sg/chart · micro-ROS — micro.ros.org
- PREEMPT_RT mainline — wiki.linuxfoundation.org/realtime · Gazebo — gazebosim.org
- ROS 2 real-time & intra-process design — design.ros2.org (realtime_proposal, intraprocess_communications)
- Humanoid RL/VLA: research.nvidia.com/labs/gear (GR00T) · pi.website (π0.5) · figure.ai (Helix)

**NVIDIA Physical AI** ·
- Cosmos 3 — nvidianews.nvidia.com (May 31 2026) · arXiv:2606.02800 · huggingface.co/nvidia/Cosmos3-Nano
- GR00T N1.7 — huggingface.co/blog/nvidia/gr00t-n1-7 · github.com/NVIDIA/Isaac-GR00T
- Isaac Sim/Lab/Arena — github.com/isaac-sim · Isaac Teleop — github.com/NVIDIA/IsaacTeleop
- Jetson Thor — developer.nvidia.com blog "Introducing NVIDIA Jetson Thor" · JetPack 7.2 MIG blog
- Thor memory — Jetson Thor datasheet DS-11945-001 (PDF) · DRIVE AGX Thor deck (PDF) · docs.nvidia.com "CUDA for Tegra" · "CUDA 13.0 for Jetson Thor" blog · GH200 NVLink-C2C blog + datasheet · audits: research/jetson-thor-memory-2026-07.md, thor-unified-memory-2026-07.md
- Isaac ROS 4.5 — nvidia-isaac-ros.github.io/releases · LeRobot ×NVIDIA — blogs.nvidia.com (Jul 6 2026)

**NVIDIA Automotive** ·
- DRIVE AGX Thor devkit — developer.nvidia.com blog (Sept 2025 GA)
- DriveOS 5.2 ASIL-B — blogs.nvidia.com TÜV SÜD (Dec 2022); DriveOS 6.0 ASIL-D on Orin — eenewseurope.com (Jan 2025)
- QNX × NVIDIA — qnx.software/en/blog/2026 · automotiveworld.com (QNX in Thor devkit)
- AUTOSAR — autosar.org (Classic/Adaptive) · vector.com (MICROSAR on DRIVE AGX/Thor, MB.OS) · elektrobit.com (EB corbos) · rti.com (DDS in AUTOSAR, R18-03) · DriveOS MCU docs (AURIX+Vector AFW on Orin; RH850 on Thor) · audit: research/automotive-stack-autosar-2026-07.md
- DRIVE Hyperion — nvidia.com → solutions → drive-hyperion · Halos — blogs.nvidia.com (GTC 2025)
- Alpamayo — huggingface.co/nvidia/Alpamayo-R1-10B · nvidianews (Alpamayo 2 Super, May 2026)
- Mercedes CLA — group.mercedes-benz.com (SOP Jun 2025) · blogs.nvidia.com (drive-av-software-mercedes-benz-cla) · Uber robotaxi — investor.uber.com (Mar 2026)
- Halos for Robotics — nvidia.com/en-us/ai-trust-center/halos/robotics
- NVIDIA Q4 FY26 results (automotive $2.3B) — nvidianews.nvidia.com
- Thor SoC TRM DP-11881-002 — developer.nvidia.com download center · FSI — DriveOS 7.0.3 docs "Functional Safety Island"
- Thor internal engines — forums.developer.nvidia.com (NVIDIA staff: SPE removal, FSI/SMCU SKU-gating, RH850)

**Fleet / diagnostics** ·
- UDS/DoCAN/DoIP/UDSonIP — iso.org: 14229-1, 15765-2, 13400, 14229-5 · SOVD — iso.org 17978-1/-2/-3 (2026) + asam.net
- AUTOSAR diagnostics — autosar.org: SWS_Diagnostics (AP DM), SWS_UpdateAndConfigurationManagement (UCM), CP DCM/DEM specs
- Vector × Thor (FSI + companion-MCU reference integration, 2025-08-25) — vector.com news · EB corbos Hypervisor / Classic-vECU — elektrobit.com
- COQOS → Qualcomm (Jun 2024) — opensynergy.com · zone-ECU / central compute — bosch-mobility.com, nxp.com
- VDA 5050 — github.com/VDA5050/VDA5050 (spec + 3.0.0 release, 2026-03-19) · ifr.org "VDA 5050 explained" · synaos.com (ecosystem; vs MassRobotics/Open-RMF) · ottomotors.com (Rockwell certifications) · massrobotics.org · reference.opcfoundation.org (OPC 40010) · index.ros.org/p/vda5050_connector · github.com/nvidia-isaac/isaac_mission_dispatch
- audits of the two source drafts: research/fleet-uds-autosar-2026-07.md (F1–F17) · research/vda5050-robot-fleet-2026-07.md (V1–V12)

*Demo numbers (GR00T inference, QoS/RMW matrices) are our own captured runs, July 2026.
Per-claim citations + audit trail: `research/claims-audit-2026-07.md` and the research reports.*
