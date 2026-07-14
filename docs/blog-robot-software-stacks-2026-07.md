# Robot Software Stacks 2026 — from firmware to foundation models

**Wheeled · Humanoid · Fleet (Open-RMF) · NVIDIA Physical AI vs Automotive**

> This post is the long-form version of our July 2026 research deck. External claims are
> source-backed (full list at the end); the **14 headline claims** additionally went through
> an **independent audit pass** (re-verified against their primary sources) — the remaining
> claims are sourced but not exhaustively audited. Every demo number was
> **measured on our own machine** — nothing copied from marketing material.
>
> **How to read this.** This is a *deep-dive* — written for readers who already know what a
> ROS node is. **New to robotics? Start with the companion primer instead** (*How Robot
> Software Actually Works — a 10-minute primer*, `docs/blog-robot-software-primer.md`),
> then come back here — good first stops: §1 (the map), §2.3 (real code), §8 (the demo),
> §10 (takeaways). The middle sections (Open-RMF, NVIDIA, certification) are reference
> material — read them when the topic lands on your desk.
>
> **Images:** all figures live in the repo folder `slides/assets/` (same-named `.png`
> files) — attach them to the Confluence page when publishing.

---

## Contents

1. [The map: every robot converges on one stack shape](#1-the-map)
2. [ROS 2 up close: two worlds, key repos, real code](#2-ros-2-up-close)
3. [Reality check: wheels, humanoids, and where ROS 2 actually stands](#3-reality-check)
4. [The fleet layer: Open-RMF and the Fleet Adapter](#4-the-fleet-layer-open-rmf)
5. [NVIDIA Physical AI: Cosmos, GR00T, Isaac, and inside the Thor chip](#5-nvidia-physical-ai)
6. [Physical AI vs Automotive: same silicon, different rules](#6-physical-ai-vs-automotive)
7. [Trust, but audit](#7-trust-but-audit)
8. [The real demo: GR00T N1.7 on one desktop GPU](#8-the-real-demo)
9. [What this means for an embedded team + roadmap](#9-what-this-means-for-an-embedded-team)
10. [Key takeaways](#10-key-takeaways)
11. [References](#11-references)

---

## 1. The map

The single most useful finding of this research: **wheeled robots, humanoids, and autonomous
vehicles all converge on the same layered software shape** — and the bottom half of that
shape has not been touched by the AI wave.

![The unified robot software stack](stack-unified.png)

Bottom-up:

| Layer | Contents | Typical rate |
|---|---|---|
| MCU firmware | motor current loops using FOC (Field-Oriented Control — vector control of the motor's magnetic field), an RTOS (Real-Time Operating System), the E-stop safety path | 8–32 kHz |
| Fieldbus | EtherCAT / CAN-FD linking joint MCUs to the main computer | 1–10 kHz cycles |
| RT control | `ros2_control` on PREEMPT_RT Linux (the real-time kernel option, mainline since kernel 6.12) | ~1 kHz |
| **— the ROS 2 boundary (DDS) —** | | |
| ROS 2 graph | perception, SLAM (Simultaneous Localization and Mapping — building a map while locating yourself in it), sensor fusion | 5–200 Hz |
| Autonomy | Nav2/Autoware for wheels; RL policies (policies trained by Reinforcement Learning — trial-and-error learning in simulation) for humanoids | 1–50 Hz |
| Fleet | Open-RMF — coordinating many robots in one building | seconds–minutes |

### Which task lives on which layer?

![Task placement by layer](layer-tasks.png)

Rule #1: **the loop rate picks the layer** — the strongest *first* heuristic, though not
the only axis (real placement also weighs WCET — Worst-Case Execution Time — fault
containment, certification, and bus latency). Faster and must-run-on-time → lower
(MCU/RTOS); heavier math and latency-tolerant → higher (Linux/GPU). Three corollaries that
are commonly misunderstood:

1. **Motor control is three nested loops living on two layers** *(the common pattern)*.
   The current/FOC loop (8–32 kHz) lives on dedicated silicon — an MCU, DSP, FPGA, or
   inside a smart drive. The ~1 kHz position loop has two common homes:
   inside a smart servo drive (the industrial pattern) or inside `ros2_control` on
   PREEMPT_RT (the humanoid pattern). Choosing between those two architectures is the
   biggest call a robot-firmware team makes.
2. **Kinematics exists twice.** FK/IK (Forward/Inverse Kinematics — computing pose from
   joint angles and vice versa) in *control mode* — whole-body QP (Quadratic Programming —
   a fast convex optimizer), the Pinocchio library, allocation-free C++ — runs at 1 kHz
   inside the RT loop. *Planning mode* — MoveIt 2, collision-aware search taking hundreds
   of milliseconds — lives up in the ROS 2 graph.
3. **SLAM and global path planning stay out of the torque/safety loop.** When SLAM stalls
   for a few hundred ms on a loop closure, navigation pauses — torque is unaffected,
   *provided* the layers below carry independent safety functions. That is a design
   requirement to engineer in, not something a layered architecture grants for free.

> This rate-layering is engineering canon, not our invention: cascade control (inner loop
> ~10× faster — Åström/Hägglund), rate-monotonic scheduling (Liu & Layland, 1973), Albus's
> RCS reference architecture (NIST, 1980s — each level ~10× slower), and Gat's three-layer
> architecture (1998).

One addendum: rate is the *first* sorting axis, **criticality is the second** — the E-stop
almost never runs, yet it must sit on the lowest layer, because what earns that placement is
provable simplicity, not speed.

---

## 2. ROS 2 up close

### 2.1. "Real-time ≠ fast" — the two worlds inside ROS 2

The words "ROS 2" on our map actually cover **two different execution worlds**:

- **The DDS graph** — the pub/sub world: messages cross the middleware by default (DDS —
  Data Distribution Service, the standard distributed middleware; intra-process C++
  communication can bypass serialization entirely), with latency that is typically ms-class
  and **configuration-dependent**. The default graph is not by itself a hard-real-time
  boundary — DDS *can* be configured for deterministic operation, but whether a loop meets
  its deadline must be measured on the target kernel, RMW, hardware, and workload. SLAM,
  Nav2, and perception live here.
- **`ros2_control`** — *configured* by ROS 2, but its hot loop **bypasses DDS**: the
  real-time thread of `controller_manager` runs `read() → update() → write()` as direct
  C++ function calls between plugins, at a **configured rate** (1 kHz is the common
  choice, not a fixed default). Topic data reaches the loop through realtime-safe buffers
  filled on the non-real-time side.

And **real-time means a deadline you can prove (WCET + jitter) — not speed**. The budget
below is illustrative: the ~50 µs jitter figure is a typical tuned-PREEMPT_RT result, *not
a constant* — it depends on the kernel, CPU isolation, IRQ placement, and workload, and
must be measured on your own target (a cyclictest capture is on our repo roadmap):

| Loop | Period | Jitter budget vs period | Verdict |
|---|---|---|---|
| FOC on the MCU | 31–125 µs (8–32 kHz) | ns–µs (hardware timers) | hard real-time |
| ros2_control on PREEMPT_RT | 1,000 µs (1 kHz) | ~50 µs ≈ 5% of the period | comfortable |
| The same loop pushed to 10 kHz | 100 µs | ~50 µs ≈ 50% of the period | budget gone — prove it on target, or use dedicated silicon |
| One hop over a DDS topic (defaults) | — | typically ms-class, config-dependent | keep it out of the torque path |

1 kHz is where two limits meet: **well-tuned Linux gets comfortable** and **physics stops
caring** (mechanical time constants are ms-scale; the µs world belongs to motor
electronics on the MCU).

*Terminology note: "hard" real-time = a missed deadline is a system failure; "firm" = a
late result is worthless but rare misses are tolerable; "soft" = a late result merely
loses value. Provable hard real-time — backed by WCET analysis — is the domain of MCUs,
RTOSes, and QNX. DDS itself powers deterministic distributed systems when configured for
it (see the real-time and intra-process design articles on design.ros2.org) — the caution
here is about ROS graph defaults, not about DDS the standard.*

### 2.2. The ROS 2 ecosystem — which repo, and when

| Repo (github.com/…) | What it is | Reach for it when |
|---|---|---|
| `ros2/*` — rclcpp, rclpy, rcl, rmw_* | the core: client libraries → `rcl` → `rmw` (the middleware abstraction that lets you swap DDS vendors) | always — this *is* ROS 2 |
| `ros-controls/ros2_control` + ros2_controllers | the RT control framework + stock controllers (diff-drive, joint-trajectory, PID) | the robot has real actuators |
| `ros-navigation/navigation2` | Nav2 — behavior-tree-driven mobile navigation | wheeled autonomy |
| `moveit/moveit2` | manipulation planning (IK, collision-aware) | robot arms |
| `SteveMacenski/slam_toolbox` | 2D lifelong SLAM | mapping + localization |
| `ros2/rosbag2` | recording / replay (MCAP format) | data capture, debugging |
| `micro-ROS/*` | the MCU-side client (FreeRTOS/Zephyr/NuttX) | the MCU must be a first-class node |
| `gazebosim` + ros_gz | simulation (the Harmonic release pairs with Jazzy) | simulation & CI |
| `open-rmf/*` | multi-fleet coordination | many vendors, one building |

Docs: **docs.ros.org** · package index: **index.ros.org** · the distro we use:
**Jazzy (LTS, supported to 2029)** · licensing: Apache-2.0/BSD throughout — no gates anywhere.

### 2.3. What calling the framework looks like — a complete node in 20 lines

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

```bash
ros2 node list
ros2 topic echo /chatter
ros2 topic hz /chatter
ros2 topic info /chatter -v
```

*(QoS — Quality of Service: the ROS 2/DDS delivery-quality parameter set; depth 10 = a
keep-last buffer of the ten most recent messages.)*

### 2.4. Where firmware plugs in — `hardware_interface`

```cpp
class MyRobot : public hardware_interface::SystemInterface {
  CallbackReturn on_init(const HardwareInfo & info) override {
    // parse the <ros2_control> tags from the URDF; open your CAN / EtherCAT device here
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

- `read()/write()` run **inside the 1 kHz RT thread** — no malloc, no locks, no DDS.
- Controllers (PID, diff-drive…) are sibling plugins wired to the driver through shared
  handles and chosen in YAML — you can swap the control law without touching the driver.
- **This class is the front door for a CAN/EtherCAT firmware engineer** — the
  `ros2_canopen` and `ethercat_driver_ros2` packages are exactly this class, prebuilt.

### 2.5. The graph, live — a real screenshot

![rqt_graph captured from the running system](rqt-graph-real.png)

A real screenshot of `rqt_graph` attached to our repo's Demo 1: a Python `/talker` and a
C++ `/talker_cpp` publish the same `/chatter` topic into `/listener` — the subscriber cannot
tell the languages apart; the service/action servers idle until called. Nobody configured
any master: pure DDS discovery.

### 2.6. Nodes, the graph, and DDS — what is actually talking to what

![Node vs process vs thread](node-process-graph.png)

Three words carry most of ROS 2's conceptual weight, and all three mislead a firmware
engineer on first contact.

**A node is a name, not a thread.** A node is an *object* — an identity in the graph: a
name (`/camera`) plus its endpoints (publishers, subscriptions, services, timers,
parameters). How it maps to the OS is a separate, free choice: one process per node (the
classic layout — our Demo 1 runs five), or several nodes **composed** into one process —
where, if they **opt in** to intra-process communication
(`use_intra_process_comms(true)`; rclcpp/C++ only, not rclpy), co-located nodes exchange
messages as a pointer pass: no serialization, no network. Composition alone does *not*
switch this on — non-opting composed nodes still ride the normal DDS path. Threads
belong to the **executor** — the event loop that
dequeues ready work and invokes callbacks. A `SingleThreadedExecutor` runs *every*
callback of every node in it sequentially, to completion: no priority preemption between
callbacks, which is why one stuck callback starves its executor — and why hard-RT loops
live *outside* the graph in a plain `SCHED_FIFO` thread (section 2.1's `ros2_control`
pattern). Underneath either way, DDS runs its own pack of I/O threads — and the count
surprises everyone. Our captured run (`docs/img/demo1_threads.txt`): Demo 1's C++ talker
— one node, one process — is **15 OS threads** in `ps -T`: main + executor/rcl + tracing
+ a dozen `dds.*` I/O threads (Fast DDS, the Jazzy default RMW).

**The graph is discovered, not drawn.** There is no GUI where you wire nodes together,
no wiring file, no code generation. A connection exists because *names match*:
`create_publisher("chatter")` in one program, `create_subscription("chatter")` in
another, compatible type and QoS — the discovery handshake creates the edge. Stop a
process and its edges vanish. `rqt_graph` is an X-ray viewer, not an editor. The actual
"wiring harness" is the topic names in code plus **launch files**, which start nodes and
re-wire them via *remapping* (`('image_raw', '/front_cam/image')`). The contrast with
section 6's AUTOSAR Classic could not be sharper: there, connections are declared in
ARXML at build time and a generated RTE wires them — the diagram is the *input*. In
ROS 2 the diagram is the *output*: an observation of whatever matched at runtime. (The
one draw-then-run GUI in this ecosystem, Groot2, edits the behavior tree *inside* a node
— not the graph between nodes.)

![A real robot's graph](robot-node-graph.png)

Here is what those rules produce at robot scale — section 3.1's wheeled-AMR stack drawn
as the graph `rqt_graph` would show: driver nodes fan `/scan` out to both `/slam_toolbox`
and `/amcl`; `/ekf` fuses `/imu` with the wheel `/odom` that `ros2_control`'s
`/controller_manager` publishes; everything converges on the Nav2 servers, whose
`/cmd_vel` goes back down to `/controller_manager`; and the fleet layer reaches in
through exactly one door — the `/navigate_to_pose` *action* into `/bt_navigator`. Note
where the picture stops: below `/controller_manager` there are no topics, only the
1 kHz function-call loop and the fieldbus.

![What DDS connects](dds-scope.png)

**DDS connects processes, not controllers.** DDS (Data Distribution Service, an OMG
standard with several interoperable implementations — Fast DDS, Cyclone) is the
network stack under the graph, and its participants are *OS processes with an IP stack*.
The same pub/sub API covers three cases transparently: two nodes in one process
(opt-in intra-process, DDS bypassed), two processes on one machine (shared memory/loopback),
and processes across machines (Ethernet, multicast discovery). Below that line — MCUs
and fieldbuses, the FOC and safety loops on EtherCAT/CAN-FD — there is no DDS: no IP
stack, and no desire for one (that world wants static, predictable frames — the same
instinct that makes vehicle body ECUs speak signal-based CAN under Classic AUTOSAR
rather than SOME/IP). The sanctioned bridge is **micro-ROS**: not an RTOS and not an
application, but a *client library* (`rclc` + XRCE-DDS) linked into your firmware,
running as a task on *your* RTOS, speaking a slimmed protocol to an **Agent** on the big
computer — and the Agent joins the graph on the MCU's behalf. The automotive mirror
holds here too: on DRIVE Thor, the in-guest middleware (NvStreams, or AUTOSAR Adaptive's
`ara::com` with its SOME/IP and DDS bindings) plays exactly the role DDS plays on a
robot computer.

One consequence worth spelling out, because it surprises everyone the first time:
**Open-RMF's core is itself ROS 2 nodes.** The traffic scheduler, the task dispatcher,
the negotiation machinery — they arrive as nodes and topics in the same graph as
everything else. "Installing RMF" means launching more nodes.

---

## 3. Reality check

### 3.1. Wheeled robots (AMRs & autonomous vehicles)

*(AMR — Autonomous Mobile Robot: the self-driving carts of warehouses, hospitals, factories.)*

**Indoor AMRs — the de-facto standard stack in 2026, not displaced by ML:**

- `ros2_control` → EKF fusion (Extended Kalman Filter — merging wheel odometry with the
  IMU) → `slam_toolbox` + AMCL (particle-filter localization on a saved map) → **Nav2**
  (behavior trees; the modern local controller is MPPI — Model Predictive Path Integral, a
  sampling-based predictive controller) → the product's task layer.
- Cartographer is effectively legacy. No evidence of learned planners displacing Nav2 in
  production.

**On-road autonomous driving — a split world:**

- **Autoware** (on ROS 2): the open reference stack — ~500 participating companies
  *(the foundation's own figure)*; its
  first public-road L4 target (SAE Level 4 — fully driverless within a bounded domain) is
  shuttles and buses.
- Robotaxis and consumer vehicles (Waymo, Tesla): proprietary stacks; public materials
  show **end-to-end learned** architectures (one network from camera to steering) and
  expose no ROS — proprietary internals are not observable from outside.

### 3.2. Where ROS 2 actually stands

![ROS 2 by segment](ros2-reality.png)

| Segment | Verdict | Detail |
|---|---|---|
| AMR / industrial | **De-facto standard** | Nav2 + ros2_control + slam_toolbox; "100+ companies" (the project's own count) |
| Autonomous vehicles | **Open reference only** | Autoware for shuttles/L4 pilots; commercial robotaxis expose no ROS publicly |
| Humanoids | **Not exposed publicly** | Unitree offers an optional ROS 2 wrapper; Tesla/Figure/1X/Atlas run proprietary stacks whose internals aren't observable |

**Learning ROS 2 = learning the industrial mainstream** — and the ≤1 kHz firmware layers
are the same everywhere anyway.

### 3.3. Humanoids: locomotion moved to RL (2024→2026)

- The classical school — **MPC + whole-body QP** (MPC — Model Predictive Control; the
  Atlas/DRC lineage) — has retreated to the *low-level layer*.
- Every new platform we reviewed ships **RL policies trained in simulation** (Isaac Lab /
  MuJoCo), deployed on-robot at **~50 Hz** — even the new electric Atlas moved to RL
  "large behavior models".
- The task layer has converged on a **dual-system VLA motif** (VLA — Vision-Language-Action:
  a model that takes camera images plus a language instruction and outputs motion): a slow
  reasoning half plus a fast action head. The rates differ per model — Figure's Helix runs
  S2 at 7–9 Hz and S1 at 200 Hz (Helix 02 adds a 1 kHz S0 reflex layer); GR00T (NVIDIA)
  and π0.5 (Physical Intelligence) share the shape, not the exact rates.
- The joint-level firmware underneath (FOC at 8–32 kHz, EtherCAT/CAN-FD at 1–10 kHz) —
  **unchanged**.

---

## 4. The fleet layer: Open-RMF

### 4.1. What it is and where it sits

![Where Open-RMF sits](rmf-position.png)

**Mental model: air-traffic control for a building full of robots.** Open-RMF (Robotics
Middleware Framework) is not part of any robot and never replaces Nav2. Every robot (or
every vendor's fleet) keeps its own stack; a **Fleet Adapter** wraps each fleet; the RMF
Core coordinates *across* adapters: traffic scheduling, task auctioning, and shared
infrastructure (lifts, doors, chargers). And per section 2.6: RMF Core is not a separate
server stack — it is *ROS 2 nodes*, living in the same graph as the robots it
coordinates; the fleet adapters and even the door/lift adapters are nodes too.

Status in 2026: alive and maintained under OSRA (the Open Source Robotics Alliance — the
body governing the Open Robotics projects since 2024, backed by Intrinsic among others),
with active Jazzy branches. The flagship deployments remain Singapore's healthcare/airport
program (CGH hospital, Changi airport) — *niche, but real*.

**When to use it:** multi-vendor fleet + shared building resources → exactly its job. One
robot or a single-vendor fleet → skip it; Nav2 plus the vendor's fleet manager is enough.
VDA 5050 (the German intralogistics MQTT protocol standard between AGVs and a master
controller) is a *wire protocol*, not a coordinator — it can run **underneath** RMF rather
than competing with it.

### 4.2. Who does what: robot vs RMF Core

| Job | Owner | Note |
|---|---|---|
| Local path planning, obstacle avoidance | **the robot** (its own Nav2 / vendor stack) | RMF never touches sensors |
| Global **space-time** scheduling | **RMF Core** | reserves lanes *over time*, not just in space |
| Task allocation | **RMF Core** | an auction — fleets bid, the best offer wins |
| Conflict resolution between fleets | **RMF Core** | negotiation: schedules adjust *before* robots meet |
| Translating RMF ↔ vendor API | **Fleet Adapter** | where the real integration work lives |
| Doors, lifts, chargers | **RMF Core + infrastructure adapters** | the robot never talks to the lift directly |

> Coordination is *logically* centralized (one shared schedule), but conflict resolution is
> **negotiated among the fleet adapters** — closer to air-traffic control than to a joystick.

### 4.3. The Fleet Adapter — where ~80% of the integration effort goes

Data flow: `RMF Core ↔ rmf_fleet_msgs (standard) ↔ Fleet Adapter ↔ vendor API (proprietary)`

The adapter's jobs: report state (pose, battery, mode) · translate commands · bid for
tasks · transform coordinate frames · handle docking/charging · pause/resume when
negotiation says so.

| Integration level | You get | Effort |
|---|---|---|
| **Full Control** | RMF sends paths and adjusts speeds — full coordination | high — what most real deployments use |
| Easy Full Control | same idea, simplified API | medium |
| Read Only (+ Blockade) | observe only (Blockade = can still veto motion) — no control | low |

**Build path:** clone `open-rmf/fleet_adapter_template` → fill in `config.yaml` (speeds,
battery model, supported tasks) → implement `RobotClientAPI` (position / battery /
navigate / stop) — the template already speaks RMF. Robots running Nav2 can use
**`free_fleet`** directly. Existing adapters: MiR, Clearpath/OTTO, Gaussian Ecobot… (see
`open-rmf/awesome_adapters`).

Try it on a workstation: `rmf_demos` (jazzy branch) simulates an entire hotel/office with
multiple fleets — requires Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic.

### 4.4. VDA 5050 — the industry's fleet wire protocol, audited

![VDA 5050 interface](vda5050-interface.png)

Open-RMF is a *coordinator*; the industry also standardized the *wire* between any fleet
manager and the robots — **VDA 5050**, published jointly by VDA (the German automotive
association), VDMA and KIT-IFL. This section, like 6.7, survived an audit of an external
draft first (14 claims, verdicts in `research/vda5050-robot-fleet-2026-07.md`, manifest
rows V1–V12); what follows is the corrected version.

- **Current version: v3.0.0, released 2026-03-19** — the "AMR release": freely-navigating
  robots, a real zone concept (BLOCKED · SPEED_LIMIT · PRIORITY… — and *no* "charging
  zone", whatever summaries claim: charging is the `startCharging`/`stopCharging` action
  pair), CRITICAL/URGENT error levels. Most public write-ups still describe v2.x.
- **The wire is MQTT (3.1.1 minimum) + JSON** — topics
  `vda5050/v3/<manufacturer>/<serialNumber>/<topic>`: `order`, `instantActions`,
  `zoneSet` downstream; `state`, `factsheet`, `connection`, `visualization` upstream.
- **An order is a graph** of nodes and edges: master control releases the **base**
  (drive it now) and plans the **horizon** — that release mechanism *is* the traffic
  control, while the traffic *logic* itself is explicitly out of the spec's scope.
- **Robots self-describe via the factsheet** — physically detailed (geometry, envelope
  curves, protocol features), but no semantic sensor model.
- **Limits, per the spec itself:** no OTA, no deep diagnostics (a flat
  errorType/errorLevel — nothing like automotive UDS, see 6.7), security left to
  broker/TLS configuration, safety delegated to ISO 3691-4.
- **Adoption:** strongest in Europe (SYNAOS ecosystem: KUKA, Omron, SEW, STILL, MiR;
  Bosch Rexroth; DS Automotion) with real North-American uptake (OTTO by Rockwell's
  VDA 5050 certifications); Asia fragmented.
- **The landscape around it is complementary, not competing:** MassRobotics AMR Interop
  covers cross-fleet *state sharing* only ("not a task management type of system");
  OPC 40010 (OPC UA Robotics) covers vertical asset/condition monitoring; and Open-RMF
  can drive robots *over* VDA 5050 (`vda5050_connector`; MiR ships an adapter; NVIDIA's
  Isaac Mission Dispatch speaks it) — RMF above, VDA 5050 below is a real, shipping
  combination, not a choice.

---

## 5. NVIDIA Physical AI

### 5.1. The three-computer loop

![NVIDIA's three computers](nvidia-three-computers.png)

NVIDIA frames robotics as three computers: **TRAIN** (DGX/cloud — pretraining Cosmos and
GR00T) → **SIMULATE** (RTX/OVX workstations — Isaac Sim, Isaac Lab, Cosmos synthetic data,
demonstration capture via Isaac Teleop) → **DEPLOY** (Jetson Thor on the robot — a TensorRT
engine inside an Isaac ROS graph). Field data (MCAP recordings) flows back to training —
the "data flywheel".

### 5.2. The pieces — what is real as of July 2026 (audited)

| Piece | Status |
|---|---|
| **Cosmos 3** — world foundation model (a generative model of how the physical world evolves) | Real — launched May 31, 2026; MoT architecture (Mixture-of-Transformers: one reasoning tower + one generation tower in a single model); Nano 16B / Super 64B; OpenMDW-1.1 license (Linux Foundation) |
| **GR00T N1.7** — the robot VLA | Real — Early Access April 17, 2026; its backbone *is* Cosmos-Reason2-2B; "Action Cascade" architecture; commercial use allowed |
| **Isaac Sim 6 / Isaac Lab** | Apache-2.0 core / BSD-3; **Isaac Lab-Arena** (the policy-evaluation framework) is alpha — unstable APIs |
| **Isaac Teleop** | Demonstration capture via Apple Vision Pro / Quest 3; a browser demo needs no headset at all |
| **Isaac ROS 4.5** | GPU-accelerated ROS 2 Jazzy packages: cuVSLAM (replaces slam_toolbox), nvblox (replaces costmaps), cuMotion (replaces MoveIt planning) — NVIDIA GPUs only, no CPU path |
| **Jetson Thor** | 128 GB unified RAM, 40–130 W, $3,499 devkit; MIG (Multi-Instance GPU — hardware partitioning of the GPU) = **2** partitions, a technology preview in JetPack 7.2 |

Openness is layered: **weights and code are open; everything is locked to CUDA/TensorRT
underneath.**

### 5.3. Inside the Thor chip

![Thor SoC block diagram (our drawing)](thor-soc.png)

![NVIDIA's official block diagram](thor-official-block.png)

The second figure is **NVIDIA's own** ("Components of NVIDIA Jetson Thor modules",
developer blog, 2025). It answers "what connects the CPU and the GPU": *nothing
point-to-point* — the 14-core Arm Neoverse-V3AE CPU and the Blackwell GPU (2,560 CUDA
cores, 96 Tensor Cores) both hang off the **Memory Control Fabric**, sharing a 16 MB system
cache and 128 GB of unified DRAM.

**Honesty note:** this official figure shows an "SPE/RTOS" block — which NVIDIA staff later
disavowed on the forums: *"there is no SPE R5 core in Thor SoC."* Even vendor diagrams
deserve an audit.

**The hidden MCUs inside Thor** (verified from the public TRM — Technical Reference
Manual — and NVIDIA staff answers):

| Engine | Role | Thor status | Firmware |
|---|---|---|---|
| BPMP (Boot & Power Management Processor) | boot, clocks, power, thermal | present (in the boot chain) | closed, signed blob |
| PSC (Platform Security Controller) | security root of trust | present | closed |
| RCE / DCE | camera / display engines | present | closed, signed |
| SPE (Sensor Processing Engine) | always-on sensor MCU — *Orin's public FreeRTOS door* | **removed on Thor** — no replacement SDK | gone |
| FSI (Functional Safety Island) | lockstep safety cluster | **DRIVE / IGX SKUs only — not on Jetson T5000** | closed |

The consequence for firmware engineers: **there is no user-programmable RTOS core inside
Jetson Thor anymore** — your real-time code lives on PREEMPT_RT or on an external MCU over
the fieldbus (the cascade pattern from section 1).

### 5.4. Thor's memory: one 273 GB/s pool, a coherence flip, and a bandwidth budget

Two third-party reports on Thor's memory crossed our desk in July 2026; we audited both
against primary sources before using anything (full trail:
`research/jetson-thor-memory-2026-07.md`, `research/thor-unified-memory-2026-07.md`,
manifest rows M1–M16 and U1–U16). Three findings matter to an embedded team.

**The numbers (from the datasheet PDF, read directly).** Everything on the die shares
one LPDDR5X pool behind the Unified Coherency Fabric — no HBM anywhere in the family:

| | Jetson T5000 | T4000 / DRIVE AGX Thor |
|---|---|---|
| DRAM | 128 GB LPDDR5X (8×16 GB) | 64 GB (8×8 GB) |
| Bus · clock | 256-bit · 4,266 MHz (≈ 8533 MT/s) | same |
| Peak bandwidth | **273 GB/s** | **273 GB/s** — full bandwidth kept |
| Caches | L1 64+64 KB · L2 1 MB/core · **16 MB shared system cache** | same |
| Max module power | 130 W | 90 W |

Memory-bound workloads degrade less on the smaller SKUs than the TFLOPS gap (2070 vs
1200 FP4) suggests — the bandwidth is identical.

**The coherence flip.** Orin had one-way I/O coherency (GPU snoops CPU caches, not vice
versa). Thor is the first Tegra with **Sysmem Full Coherency** — two-way, in hardware.
That flips the allocator advice: in CUDA 13.0, `cudaMallocManaged()` allocations are
**not GPU-cached** on Thor, while plain pageable memory (`malloc`/`mmap`) accessed
through the new coherence path — the GPU walks the host's page tables directly — "can
outperform both Pinned memory or Unified memory" (CUDA for Tegra appnote, verbatim).
The fastest perception(GPU)→planning(CPU) handoff is now plain system memory.

**Beware dGPU folklore.** On a one-pool, hardware-coherent SoC, most discrete-GPU
unified-memory vocabulary stops applying: nothing *migrates* (there is no second pool —
"migration" never appears in the Tegra docs); *oversubscription* has no boundary to hit
(the limit is the shared 64/128 GB budget vs the OS); `cudaMemAdvise` tuning advice is
absent from the Tegra docs; and ranking Thor's coherence "weaker than Grace Hopper" is
the wrong axis — GH200's real edge is scale (480 GB LPDDR5X + 96/144 GB HBM over a
900 GB/s NVLink-C2C link), not coherence strength. Smell test: advice that mentions
migration, oversubscription or preferred location was written for a discrete GPU.

**The bandwidth budget.** 273 GB/s is 12–30× below data-center HBM (H100, HBM3,
3.35 TB/s → B200, HBM3e, ≈ 8 TB/s at ~1000 W). Autoregressive decode re-reads the
weights every token, so a *derived* roofline (tok/s ≈ bandwidth ÷ model bytes; batch 1,
not a measured run) puts a 10 B-param model at FP4 at ~55 tok/s theoretical peak, and a
20 B model at FP8 at ~14 — this is why edge VLA models cluster at 2–10 B parameters and
why FP4 matters more on Thor than on an H100.

### 5.5. From foundation model to motor

![The GR00T control cascade](groot-cascade.png)

Camera + language instruction → GR00T N1.7 (~94 ms per inference on Thor, emitting a
*chunk* of several actions per call) → whole-body policy at ~50 Hz → `ros2_control` at
1 kHz → EtherCAT/CAN-FD → MCU FOC at 8–32 kHz. **NVIDIA's stack ends above the 1 kHz
line — the bottom half is classical embedded engineering.**

---

## 6. Physical AI vs Automotive

### 6.1. One silicon, two worlds

![Robot vs Car](robot-vs-car.png)

The two product lines share **the same Thor die** and **the same Cosmos bloodline** (the
backbone of GR00T *and* of Alpamayo). What splits them into two product lines is not
technology — it is **the liability and certification regime**:

| | Robotics (Isaac/Jetson) | Automotive (DRIVE) |
|---|---|---|
| OS | Ubuntu 24.04 + PREEMPT_RT (JetPack 7) | DriveOS 7: hypervisor → a **QNX or Linux** guest (QNX = commercial safety-certified RTOS by BlackBerry) + NVIDIA service VMs |
| Middleware | **ROS 2** — shared by the whole industry | DriveWorks SDK — every OEM (vehicle manufacturer) builds its own layer on top |
| AI model | GR00T N1.7, 3B, open + commercial OK | Alpamayo-R1 10.5B / Alpamayo 2 Super 34B — weights not freely commercial |
| Safety certification | none — safety lives on a PLC next to the computer | ASIL-D (see 6.2) |
| Real-time approach | scheduling (PREEMPT_RT) + 2-way MIG | architectural isolation: a certified RTOS in its own VM |
| Developer access | $249–$3,499 retail, everything on GitHub | gated developer program, no public price |
| Release cadence | **days** | **quarters/years** (a safety case per release) |

### 6.2. The automotive software architecture, and how it earns certification

![DriveOS architecture](driveos-dualstack.png)

**DriveOS 7** splits the software with a Type-1 hypervisor (a virtual-machine monitor
running directly on the hardware): a **QNX VM** (pre-certified ASIL-D) holds the safety
functions — watchdogs, vehicle I/O, fail-operational logic — hardware-isolated from a
**Linux VM** carrying CUDA/TensorRT/DriveWorks and the AI stacks.

One honest asterisk on that picture (added after a dedicated cross-check): the dual
QNX+Linux view is NVIDIA's *platform-level framing*. The public SDK runs **one guest OS
at a time** — *"you can run QNX or Linux, but not both"* (DriveOS 7.0.3, and the same
note since 6.x on Orin; the only documented dual-guest configuration is dual-QNX). The
hypervisor genuinely hosts many VMs, but the others are NVIDIA's *service* VMs (storage,
display, GPU sharing…). A production QNX+Linux split therefore means an OEM-specific
build or multiple SoCs — manifest rows A2/F12.

*ASIL — Automotive Safety Integrity Level, ISO 26262's safety scale for road vehicles;
A is the lowest, D the highest. QM — Quality Managed: below A; requires quality process
only, no safety claim.*

**How each part earns its level:**

- **FSI**: a cluster of 4× Cortex-R52 in **DCLS** (Dual-Core LockStep — two cores execute
  identical code cycle-by-cycle; any mismatch flags a fault), with ~3 MB of private SRAM
  and ~10,000 ASIL-D MIPS — a physically isolated "referee" watching the rest of the SoC
  (public DriveOS 7.0.3 documentation).
- **SoC-wide diagnostics**: more than 22,000 fault-detection mechanisms — BIST (Built-In
  Self-Test), watchdogs, NoC firewalls (NoC — Network-on-Chip, the chip's internal
  interconnect), voltage/clock/thermal monitors *(secondary source — treat the exact count
  with care)*.
- **ASIL decomposition** (splitting one ASIL-D requirement across redundant lower-rated
  elements): the AI driving stack stays QM; a certified classical stack supervises it.
  This is the architecture that lets the OEM *argue* system-level ASIL-D in its item
  safety case — redundancy instead of certifying a neural network — but the system-level
  claim belongs to the OEM's safety case, hazard analysis, and validation; it is never
  automatic.
- **The board-level referee**: a separate safety MCU (Thor-generation evidence: Renesas
  **RH850**; the Orin era used Infineon AURIX) holds final watchdog/power authority
  *outside* the SoC.

### 6.3. The full stack in one picture — and where AUTOSAR fits

![The automotive software stack](stack-automotive.png)

This is the automotive counterpart of section 1's robot stack — same layer geometry, so
the two can be compared row by row. Sources and corrections:
`research/automotive-stack-autosar-2026-07.md`, manifest rows A1–A12.

Reading bottom-up: the vehicle's zonal/domain ECUs and the board safety MCU are
**AUTOSAR Classic land** — the statically configured, OSEK-heritage stack for deeply
embedded MCUs. The proof is in NVIDIA's own firmware naming: the safety MCU ships with
Vector's "**AFW**" — *AUTOSAR firmware* — on the AURIX (Orin generation) and on the
**Renesas RH850U2A16** that replaced it on DRIVE Thor boards. Connecting the ECUs to the
AD computer is the **in-vehicle network** — the car's equivalent of the robot stack's
fieldbus row: an automotive-Ethernet backbone (up to 10 Gbps, with TSN — Time-Sensitive
Networking, deterministic Ethernet) plus CAN-FD/LIN/FlexRay legacy branches. Above that: the Thor SoC
with its FSI; **DriveOS 7** (Type-1 hypervisor → a QNX ASIL-D *or* Linux guest — see
the single-guest caveat in 6.2 — with the TÜV
SÜD-assessed CUDA/TensorRT toolchain); the middleware line — NVIDIA's own transport is
**NvStreams**, while **SOME/IP and DDS arrive with AUTOSAR Adaptive**, not from NVIDIA;
**DriveWorks SDK**; and at the top, beside the OEM's AV application, the dashed box:
**AUTOSAR Adaptive** (`ara::com`, POSIX/C++) — a **Tier-1 layer, not NVIDIA IP**. NVIDIA
states DRIVE OS "offers full support of Adaptive AUTOSAR"; the actual products come from
Vector (MICROSAR Adaptive "can be enabled on the NVIDIA DRIVE AGX platform"; MICROSAR
Classic ASIL-D on DRIVE AGX Thor) and Elektrobit (EB corbos), with TTTech MotionWise as
a non-AUTOSAR safety framework bundled alongside QNX.

Three notes worth keeping:

- The line that moves here is not DDS (as in the robot stack) but the
  **hypervisor/ASIL boundary**.
- **AUTOSAR Adaptive has had a DDS network binding since release 18-03** — an Adaptive
  ECU and a ROS 2 node speak the same OMG DDS wire family, so interop without a gateway
  is possible in principle (QoS and type mapping still need care).
- Market reality (partner-confirmed): OEMs like Mercedes build their own Linux+QNX
  platform (MB.OS) and adopt AUTOSAR *selectively* through Vector — Adaptive and Classic
  in the base layer — rather than deploying a full off-the-shelf AP stack.

### 6.4. The certification table — who certified what, exactly

*TÜV — Technischer Überwachungsverein ("Technical Inspection Association"): Germany's
independent technical-certification bodies. TÜV SÜD (Munich) and TÜV Rheinland (Cologne)
are rival companies, not branches. An ASIL certificate only counts when an accredited body
like these signs it — self-declared "ASIL-D capable" means nothing.*

**Completed, third-party certifications:**

| Product + version | Standard · level | Body | When |
|---|---|---|---|
| DriveOS 5.2 (scope incl. CUDA + TensorRT) | ISO 26262 · **ASIL-B** | TÜV SÜD | Dec 2022 |
| DriveOS 6.0 | ISO 26262 · **ASIL-D** | TÜV SÜD | Jan 2025 — **on Orin, not Thor** |
| DRIVE core development **process** | ISO 26262 · ASIL-D (process) | TÜV SÜD | Jan 2025 |
| SoC/platform/SW engineering **process** | ISO/SAE 21434 (automotive cybersecurity) | TÜV SÜD | Jan 2025 |
| DRIVE AV / Hyperion platform | UNECE safety assessment (UNECE — the UN body that issues international vehicle regulations) | TÜV Rheinland | Jan 2025 |
| QNX OS for Safety 8.0 (supported on DRIVE AGX Thor) | ASIL-D · IEC 61508 SIL 3, as an SEooC (Safety Element out of Context — a pre-certified component awaiting integration) | BlackBerry/QNX's own cert | 2025 |

**"Assessed / capable" — NVIDIA's deliberate wording, weaker than "certified":**

- Orin SoC: ASIL-D *systematic* / ASIL-B *random* — an assessment (systematic = design-
  process faults; random = physical hardware faults such as bit flips).
- DRIVE **Thor-X: "assessed as ASIL-D conformant"** — as of July 2026 there is **no
  completed Thor product certification**.
- IGX Thor safety island: "SIL 3 **capable**" (IEC 61508 — the industrial functional-safety
  standard; SIL = Safety Integrity Level).
- **The robotics side (Jetson, Isaac ROS, GR00T): no completed product certifications** as
  of July 2026 — NVIDIA announced Halos for Robotics and an IGX Thor / QNX safety
  foundation in 2026, with certifications still pending.

One boundary worth spelling out: everything in this section is a *component, OS, or
process* certificate (SEooC). The **vehicle's** ASIL-D is established by the OEM's
item-level safety case — hazard analysis, integration evidence, validation. Chip and OS
certificates feed that case; they do not replace it.

### 6.5. Alpamayo — GR00T's driving sibling

NVIDIA frames AV software evolution as: **AV 1.0** modular pipeline → **AV 2.0** end-to-end
networks → **AV 3.0** reasoning VLA — Alpamayo (launched at CES, January 2026) is the 3.0
bet. *(AV — Autonomous Vehicle.)*

| | GR00T N1.7 (robot) | Alpamayo (car) |
|---|---|---|
| Backbone | Cosmos-Reason2, 2B | Cosmos-Reason, **8.2B** — same model lineage, not one shared brain |
| Action head | a 32-layer DiT (Diffusion Transformer — generates actions by iterative denoising) → joint/hand chunks | a 2.3B diffusion decoder → **driving trajectories** |
| Size / license | 3B — open, commercial OK | R1 = **10.5B**, non-commercial · 2 Super = **34B** (robotaxis; NVIDIA's newsroom says 34B while its product page says 32B — the sources conflict as of 07/2026) |
| Training data | 20,854 h of human egocentric video | **80,000 h** of multi-camera driving + ~700K reasoning traces |
| Trust model | the policy drives the robot directly | **never alone** — a certified classical stack supervises it |

The tooling mirrors robotics: AlpaSim (open simulator) · AlpaGym ("the Isaac Lab of
driving") · OmniDreams (world-model scenario generation).

### 6.6. Reference hardware, and shipping proof

![DRIVE Hyperion 10](hyperion-sensors.png)

**DRIVE Hyperion 10** is NVIDIA's **real** published reference architecture (source: the
DRIVE Hyperion page on nvidia.com; *the car drawing in our figure is illustrative*): 2×
DRIVE AGX Thor, 14 cameras, 9 radars, 1 lidar, 12 ultrasonics — one fixed, certifiable
sensor configuration reused across a fleet of hundreds of thousands of vehicles.

![DRIVE AGX Thor Developer Kit — official photo](drive-devkit-photo.png)

**Market proof (audited):** the Mercedes-Benz CLA has been in **series production since
June 2025** — the first MB.OS car — and the NVIDIA-powered enhanced Level 2 driving stack
(marketed as "L2++", an industry term rather than an SAE level) is slated for **US rollout
by the end of 2026**, as a dual-stack of AI plus a certified classical supervisor.
Uber × NVIDIA robotaxis — LA/SF in H1 2027 → **28 cities by 2028**, scaling toward
**100,000 L4 vehicles "over time, starting in 2027"**; queuing behind: Lucid, JLR,
BYD, XPeng, Zeekr, Li Auto. NVIDIA's automotive revenue in FY2026: **$2.3B** (+39% YoY) —
only ~1% of NVIDIA's total, but design wins lock in for a decade.

> The contrast in one line: robotics ships **experiments weekly**; automotive ships
> **certified products yearly** — on the same silicon.

### 6.7. Fleet management: how a backend talks to a hundred thousand cars

Section 4 covered the fleet layer for *robots* (Open-RMF). Cars have their own fleet
story, and it is older, more standardized, and — after the audit below — a good case
study in separating standards from hype. This section began as an external draft report;
it went through the standard audit before earning its place here: **30 claims checked —
7 refuted, 1 more without any public documentation**, verdict table in
`research/fleet-uds-autosar-2026-07.md`, manifest rows
F1–F17. What follows is the corrected version.

The fleet problem: remote diagnostics, predictive maintenance, OTA updates, and health
telemetry for vehicles you never touch. Three standards make it vendor-neutral: **UDS**
(*Unified Diagnostic Services*, ISO 14229) — one diagnostic language every ECU speaks;
**AUTOSAR** — one software architecture fixing *where* diagnostics live; and **SOVD**
(*Service-Oriented Vehicle Diagnostics*, ISO 17978, published 2026) — the new
cloud-facing REST/JSON API layered on top.

#### The two AUTOSAR stacks, drawn for firmware engineers

![AUTOSAR Classic layered stack](stack-autosar-classic.png)

**Classic** is the stack on the small ECUs — the door controllers, the safety MCU next
to the Thor SoC. Reading bottom-up: **MCAL** (*Microcontroller Abstraction Layer*) is
the vendor HAL you already know (CAN, ADC, PWM drivers); the **ECU Abstraction Layer**
hides the board wiring; the **Services Layer** holds AUTOSAR OS (a backward-compatible
superset of OSEK OS, the 1990s European automotive RTOS standard — adding memory/timing
protection, multicore, scalability classes SC1–SC4), communication stacks, NvM
(non-volatile memory management), and the two diagnostic modules we'll meet again below:
**DCM** (*Diagnostic Communication Manager* — service dispatch, sessions, security) and
**DEM** (*Diagnostic Event Manager* — fault memory). Above it all, the **RTE** (*Runtime
Environment*) — generated glue code — is the only interface application **SWC**s
(*Software Components*) ever see. Everything is statically configured at build time from
ARXML (AUTOSAR's XML configuration format); one binary, one ECU, hard real-time.

![AUTOSAR Adaptive stack](stack-autosar-adaptive.png)

**Adaptive** is not an OS — it is a POSIX *middleware platform*: C++14 processes on QNX
or Linux (applications see the PSE51 profile — IEEE 1003.13's minimal real-time POSIX
subset; platform services may use full POSIX), talking through **ARA** (*AUTOSAR Runtime
for Adaptive* — in code, the `ara::` C++ namespace) functional clusters — `ara::com`
(SOME/IP and, since R18-03, the same OMG DDS wire family ROS 2 speaks), `ara::diag`
(diagnostics), `ara::ucm` (updates).
Apps belong to **Software Clusters** — the unit of both update and diagnosis. It is
service-oriented on paper; in production, integrators pin service discovery down and
restrict dynamic allocation to startup — the dynamism is a development-time property.

Two pieces of folklore the audit killed: *"Classic can't do Ethernet"* — the SOME/IP
Transformer entered Classic in release 4.2.1 (2016), a year **before** Adaptive's first
release; and *"Adaptive = low ASIL"* — Vector ships MICROSAR Adaptive Safe at ASIL-B and
Wind River's Adaptive safety concept was assessed ASIL-D-suitable by TÜV SÜD (a 2019
program assessment — the oldest data point in this section, not a completed cert).

#### UDS: one language, two transports, two platforms

![UDS diagnostic stack](uds-diag-stack.png)

**UDS (ISO 14229-1)** is an application-layer request/response protocol: the same
request bytes reach a body ECU over CAN (**DoCAN** — *diagnostics over CAN*, transport
ISO 15765-2) or a central computer over automotive Ethernet (**DoIP** — *diagnostics
over IP*, ISO 13400). `22 F1 90` reads the VIN either way — `0x22` is
ReadDataByIdentifier, `0xF190` is the standardized **DID** (*Data Identifier* — a 16-bit
address of a readable value) for the VIN. The fleet-relevant services: `0x10` session
control, `0x27` security access (seed–key: the ECU hands out a random *seed*, the tester
must answer with the matching *key*), `0x19` read **DTC**s (*Diagnostic Trouble Codes* —
stored faults, each with a *freeze frame*: the sensor snapshot taken at fault time),
`0x31` routines (self-tests, pre-flash erase), and the flashing quartet
`0x34/0x35/0x36/0x37` (download/**upload**/transfer/exit — the draft, like most
summaries, forgot `0x35`).

On the receiving side the platforms differ: a Classic ECU dispatches through **DCM** and
stores faults in **DEM**; an Adaptive machine runs the **DM** functional cluster
(`ara::diag`) — **DoIP only**, no CAN — and instantiates one diagnostic server per
Software Cluster, so each independently-updatable software unit is also independently
diagnosable. That symmetry (update unit = diagnosis unit) is the quiet elegance of the
Adaptive design.

#### The honest end-to-end picture

![Fleet diagnostics end-to-end](fleet-uds-flow.png)

Here the draft needed the most correction. Two rules real deployments follow:

- **Raw UDS is never exposed to the internet.** The TCU (telematics unit) terminates
  the 4G/5G link with TLS and certificates; a central **gateway** — the security
  chokepoint — translates authenticated external requests into in-vehicle UDS. The
  standardized external-facing API is **SOVD**: REST/HTTP + JSON, designed to diagnose
  HPCs *and* front legacy UDS ECUs — and Adaptive's DM already implements ASAM SOVD
  alongside ISO 14229.
- **UDS is not a telemetry pipe.** `0x2A` (periodic reads) exists and works over DoIP,
  but it is session-scoped, time-polled, and DID-limited — a diagnostic burst tool.
  Continuous fleet telemetry runs on telematics pipelines (MQTT or proprietary), feeding
  the predictive-maintenance models; UDS stays the *diagnostic* protocol.

OTA follows the same platform split: Classic ECUs reflash whole images through the
bootloader (UDS `0x34/0x36/0x37`); Adaptive machines install per Software Cluster via
**UCM** — *Update and Configuration Management* — fed by an OTA client, no UDS required.

And on DRIVE Thor specifically, the draft's centerpiece — "multiple virtual Classic
AUTOSAR ECU partitions behind Thor's hypervisor, with Thor as the fleet's UDS gateway" —
is refuted by NVIDIA's own public SDK: *"Multiple Guest OS are not supported. In
addition, you can run QNX or Linux, but not both"* (DriveOS 7.0.3). Classic-AUTOSAR land
on a Thor board is the **companion MCU** (Renesas RH850), and Vector's announcement
(2025-08-25, primary-fetched this audit) places MICROSAR Classic as the reference
integration for the **FSI and the companion MCU**, "up to ASIL-D", with MICROSAR
Adaptive available *inside* the guest OS on DRIVE AGX. Virtual Classic ECUs under a
hypervisor are a real industry pattern — but the documented homes are EB corbos
Hypervisor and COQOS (Qualcomm-owned since June 2024; supported SoC list:
Qualcomm/NXP/Renesas/TI/Samsung — no NVIDIA).

![Fleet management on DRIVE Thor](fleet-on-thor.png)

Putting the corrected pieces on one Thor board: the fleet backend reaches the vehicle
through the TCU and gateway (separate ECUs); **DoIP/UDS lands on the DM inside Thor's
single guest OS**, where UCM installs OTA payloads per Software Cluster; the **companion
MCU (RH850)** is the Classic-AUTOSAR citizen on the in-vehicle network with its own
DCM + DEM; and the SoC talks to that MCU over NVIDIA's proprietary UDP-based interface —
not DoIP. Every box in this figure traces to a documented source (manifest rows
F12–F13); everything the draft invented is simply absent from it.

#### Why this got easier: the E/E consolidation

![E/E architecture evolution](sdv-ecu-consolidation.png)

The reason fleet management is tractable at all in 2026: vehicle E/E
(electrical/electronic) architecture collapsed from **distributed** (100+
single-function ECUs, point-to-point CAN) through **domain controllers** to **zonal +
central compute** — ECUs grouped by location, software consolidated onto a few HPCs
(high-performance computers) over an Ethernet/TSN backbone (Bosch's framing: distributed
application software "consolidated in a few powerful vehicle computers"; the "under a
dozen ECUs" targets are vendor figures, not measurements). Fewer boxes to flash, one
gateway to secure, one place to collect health data — and updates per Software Cluster
instead of per-ECU reflash campaigns.

For our team the rhyme with section 4 is worth noticing: Open-RMF's Fleet Adapter and
SOVD/UDS solve the same problem — a vendor-neutral seam between a fleet backend and
heterogeneous machines — one for robots, one for cars.

#### The two standard stacks, side by side

![Fleet standards, robots vs cars](fleet-standards-map.png)

Put section 4.4 and this section on one grid and the pattern is an *asymmetry*, not a
deficit list. Robots standardized **fleet orchestration** — VDA 5050 as the wire,
Open-RMF as a coordinator, MassRobotics for state-sharing — precisely the layer cars
leave operator-proprietary (there is no cross-OEM dispatch standard for a robotaxi
fleet). Cars standardized **diagnostics, OTA and the platform** — UDS, SOVD, UCM,
AUTOSAR — precisely the layers robots leave to ROS 2 conventions and vendor tooling
(InOrbit/Formant clouds ingesting `/diagnostics`; Mender/RAUC/SWUpdate as de-facto OTA
tooling with no interop standard). Each side built the standard the other skipped. The
gap both sides share: no semantic capability discovery — nothing like a UDS DID
dictionary for "what can this machine actually see and do"; VDA 5050's factsheet is
physical/protocol only. And the two worlds are drifting toward each other: SOVD borrowed
REST/JSON from the software world, and the emerging ISO work on mobile-robot
interoperability builds directly on VDA 5050 + MassRobotics.

---

## 7. Trust, but audit

The entire research ran through an independent audit pass: extract the load-bearing claims,
re-open the primary sources, rule CONFIRMED / INCORRECT / UNVERIFIABLE. The catches were
worth it:

| Claim as first reported | Audited reality |
|---|---|
| "Thor's MIG splits into up to 7 GPU instances" | Wrong — **2** instances (JetPack 7.2) |
| "GR00T TensorRT benchmark: Thor 117→92 ms, vs an RTX 5090" | Wrong — **144.9→93.8 ms** full-pipeline, vs RTX Pro 5000 / H100 |
| "Alpamayo-R1 is 10.3B parameters" | 10.5B |
| "Automotive revenue $2.35B" | **$2.3B** |

The lesson for the team: **secondhand Physical-AI numbers drift fast — re-fetch the primary
source before any number goes on a slide.** (That rule is how this document was written.)

Scope, honestly stated: the audit covered the headline claims above and the 14 headline
claims of the deck — the rest of this document is source-linked but not exhaustively
re-verified. The full claim-by-claim trail lives in `research/claims-audit-2026-07.md`.

Section 6.7 is the method's best showcase yet: an external draft arrived polished and
plausible, and the audit refuted 7 of its 30 claims outright (an eighth had no public
documentation at all) — including its centerpiece
architecture — before a word of it reached this document
(`research/fleet-uds-autosar-2026-07.md`). Section 4.4 got the same treatment (14
claims; the draft's "charging zone" and its proposed platform-standard trend were
struck). And the rule works on our own writing too: a third pass over the new section
2.6 caught a from-memory "5–7 threads" figure and replaced it with a measured **15**
(`docs/img/demo1_threads.txt`, `research/info-audit-2026-07-14.md`) — the drafted number
was off by 2×, which is the best argument for the capture rule we know of.

---

## 8. The real demo

We ran **NVIDIA Isaac GR00T N1.7-3B** zero-shot (no fine-tuning) on the sample data that
ships with the public `github.com/NVIDIA/Isaac-GR00T` repo, on a desktop RTX 5070 Ti with
16 GB of VRAM (July 2026). Two separate runs: **run A** = the first-ever run (cold cache;
raw log: `docs/img/groot_n17_inference.txt`), **run B** = a warm-cache rerun (the
screenshot below):

| Measured | Value |
|---|---|
| Latency per policy call (open-loop) | run A: **107.7 ms** average (P90 109.8 ms) · run B: **106.4 ms** average (P90 108.4 ms) |
| Model load time | run A (first run, cold cache): **94.6 s** · run B (warm local cache): **20.5 s** |
| Peak VRAM (sampled every 2 s) | **7.5 GB / 16 GB** — no out-of-memory, right at the documented 16 GB floor |
| Output per call | 8 future action steps → ~**75 generated action steps/s** — a compute-throughput figure, *not* an executed robot control rate |
| Open-loop prediction error (n=2) | MSE 0.0030 / 0.0370 (MSE — Mean Squared Error vs the recorded reference actions) — **not** task-success accuracy |

![Real screenshot of the GR00T run](groot-run-screenshot.png)

Everything involved is public: the weights on Hugging Face (`nvidia/GR00T-N1.7-3B`; the
gated `Cosmos-Reason2-2B` backbone needs a one-click license acceptance), the inference
script in the GitHub repo. Two honest caveats on the numbers: "open-loop" means the
predictions were scored against a recorded trajectory with no robot in the loop — it says
nothing about closed-loop task success; and an 8-step action chunk does not mean all
8 steps get executed before the next replan — that is a deployment choice. What action
chunking *does* buy you: one ~107 ms inference produces several future steps, which is
what turns ~9 calls/s into a usable command rate.

---

## 9. What this means for an embedded team

1. **The layers below 1 kHz never changed**: FOC loops, fieldbus, RT Linux, the safety
   path — that territory is ours, and every stack surveyed (wheeled, humanoid, NVIDIA)
   still needs it.
2. The fastest route to relevance in robotics for an embedded engineer:
   **`ros2_control` + EtherCAT/CANopen + PREEMPT_RT** — not learning to train policies.
3. Learn the **interfaces** of the ML layer (what a policy consumes and emits, at what
   rate) — its internals can wait.
4. Safety always sits **beside** the compute: a safety PLC or safety-rated MCU holds the
   kill switch — as of July 2026 no ROS 2 stack and no robotics Jetson has a completed
   safety certification (the industrial IGX Thor carries a safety island, and Halos for
   Robotics was announced in 2026).
5. **Which side to bet on?** Learn on Physical AI (open, cheap, fast — GR00T already runs
   on our desk) while keeping ISO 26262 literacy. When robotics gets its own rulebook — and
   the signals are visible: IGX Thor, Halos expanding into robotics — the engineer fluent
   in both worlds gets paid the most.

**Next demos for our repo (in order of value):**

1. A `ros2_control` demo (simulated hardware_interface → diff-drive)
2. Gazebo Harmonic (Jazzy's official simulation pairing)
3. micro-ROS (Zephyr/FreeRTOS) + `ros2_canopen` on vcan
4. PREEMPT_RT + a captured cyclictest run
5. Open-RMF `rmf_demos`
6. The NVIDIA track: Isaac Sim 6 + a cuVSLAM vs slam_toolbox comparison

---

## 10. Key takeaways

1. **Every robot type converges on one stack shape** — the bottom half is firmware, and it
   didn't move.
2. **ROS 2 = the industrial mainstream**: the standard for AMRs, a reference for AVs;
   commercial humanoids do not expose it publicly.
3. **Real-time means a deadline you can prove, not speed** — 1 kHz is where a well-tuned
   PREEMPT_RT Linux is comfortable; loops much faster than that need proof on the target,
   or dedicated silicon (MCU/DSP/FPGA).
4. **Open-RMF is a fleet-layer tool** — worth adopting only for multi-vendor buildings; the
   Fleet Adapter is where the integration effort goes.
5. **NVIDIA ships the most complete platform and the deepest hardware lock-in** — open
   weights and code, closed CUDA underneath, no CPU path.
6. **Robots and cars share one model lineage (Cosmos-Reason)** — what splits the two
   worlds is certification, not technology; "certified" and "assessed" are a world apart.
7. **Foundation-model robotics already runs on our desk** — ~106 ms per call, 7.5 GB of
   VRAM, everything from public sources.
8. **On Thor-class silicon, memory is the budget** — one 273 GB/s LPDDR5X pool for
   everything; size models by bandwidth before TOPS, pick the allocator (plain pageable
   memory beats managed on Thor), and distrust dGPU advice about migration or
   oversubscription — those concepts don't exist on a one-pool SoC.
9. **AUTOSAR is beside the NVIDIA stack, not inside it** — Classic on the vehicle MCUs
   (the safety MCU literally runs Vector "AUTOSAR firmware"), Adaptive as a Tier-1 layer
   on the SoC; its DDS binding makes Adaptive ECUs wire-compatible with ROS 2 in
   principle.

---

## 11. References

**Open stacks**

- Nav2 — docs.nav2.org · slam_toolbox — github.com/SteveMacenski/slam_toolbox
- ros2_control — control.ros.org · Autoware — autoware.org
- ROS 2 core — docs.ros.org · index.ros.org · github.com/ros2, ros-controls, ros-navigation, moveit
- Open-RMF — open-rmf.org · github.com/open-rmf (rmf_demos jazzy branch, fleet_adapter_template, free_fleet, awesome_adapters) · OSRA — osralliance.org
- Singapore deployment — cgh.com.sg/chart · micro-ROS — micro.ros.org
- PREEMPT_RT — wiki.linuxfoundation.org/realtime · Gazebo — gazebosim.org
- ROS 2 real-time & intra-process design — design.ros2.org (realtime_proposal, intraprocess_communications)
- Humanoid RL/VLA — research.nvidia.com/labs/gear (GR00T) · pi.website (π0.5) · figure.ai (Helix)

**NVIDIA Physical AI**

- Cosmos 3 — nvidianews.nvidia.com (May 31, 2026) · arXiv:2606.02800 · huggingface.co/nvidia/Cosmos3-Nano
- GR00T N1.7 — huggingface.co/blog/nvidia/gr00t-n1-7 · github.com/NVIDIA/Isaac-GR00T
- Isaac Sim/Lab/Arena — github.com/isaac-sim · Isaac Teleop — github.com/NVIDIA/IsaacTeleop
- Jetson Thor — developer.nvidia.com blog "Introducing NVIDIA Jetson Thor" · the JetPack 7.2 (MIG) blog
- Thor memory — Jetson Thor datasheet DS-11945-001 (PDF) · DRIVE AGX Thor deck (PDF) · docs.nvidia.com "CUDA for Tegra" appnote · "CUDA 13.0 for Jetson Thor" blog · GH200 architecture blog + datasheet
- Thor TRM DP-11881-002 — developer.nvidia.com download center · FSI — DriveOS 7.0.3 docs, "Functional Safety Island"
- Isaac ROS 4.5 — nvidia-isaac-ros.github.io/releases · LeRobot × NVIDIA — blogs.nvidia.com (Jul 6, 2026)

**NVIDIA Automotive**

- DRIVE AGX Thor devkit — developer.nvidia.com blog (GA, Sept 2025)
- DriveOS 5.2 ASIL-B — blogs.nvidia.com, TÜV SÜD (Dec 2022) · DriveOS 6.0 ASIL-D on Orin — eenewseurope.com (Jan 2025)
- QNX × NVIDIA — qnx.software/en/blog/2026 · automotiveworld.com
- DRIVE Hyperion — nvidia.com → solutions → drive-hyperion · Halos — blogs.nvidia.com (GTC 2025)
- Alpamayo — huggingface.co/nvidia/Alpamayo-R1-10B · nvidianews (Alpamayo 2 Super, May 2026)
- Mercedes CLA — group.mercedes-benz.com (series production, Jun 2025) · blogs.nvidia.com (drive-av-software-mercedes-benz-cla) · Uber robotaxi — investor.uber.com (Mar 2026)
- Halos for Robotics — nvidia.com/en-us/ai-trust-center/halos/robotics
- NVIDIA Q4 FY26 financial results (automotive $2.3B) — nvidianews.nvidia.com
- DriveOS — developer.nvidia.com/drive/os · DriveWorks — developer.nvidia.com/drive/driveworks · DriveOS MCU docs (AURIX + Vector AFW on Orin; RH850 flash thread on Thor)
- AUTOSAR — autosar.org (Classic/Adaptive) · vector.com (MICROSAR on DRIVE AGX/Thor · MB.OS base layer) · elektrobit.com (EB corbos) · rti.com (DDS in AUTOSAR, since R18-03) · nvidianews (Adaptive AUTOSAR support, TTTech MotionWise)

**Fleet / diagnostics (section 6.7)**

- UDS — iso.org 14229-1 · DoCAN — 15765-2 · DoIP — 13400 · UDSonIP — 14229-5 · ODX — 22901-1
- SOVD — iso.org 17978-1/-2/-3 (2026) · asam.net SOVD page
- AUTOSAR diagnostics — autosar.org: SWS_Diagnostics (Adaptive DM), SWS_UpdateAndConfigurationManagement (UCM), Classic DCM/DEM specs · SOME/IP Transformer since 4.2.1 — some-ip.com archive
- Vector — MICROSAR Adaptive product page · Thor FSI + companion-MCU announcement (2025-08-25) · MICROSAR Adaptive Safe ASIL-B news · Wind River Adaptive ASIL-D concept — windriver.com press
- Classic vECU / hypervisors — elektrobit.com tech corner + EB corbos Hypervisor · COQOS → Qualcomm (Jun 2024) — opensynergy.com
- E/E consolidation — bosch-mobility.com zone-ECU · nxp.com central compute
- DriveOS 7.0.3 single-guest + SoC↔MCU interface — developer.nvidia.com/docs/drive (Foundation Services, SoC-to-MCU Communication)
- Audit of the source draft — `research/fleet-uds-autosar-2026-07.md` + manifest rows F1–F17
- VDA 5050 (section 4.4) — github.com/VDA5050/VDA5050 (spec + 3.0.0 release, 2026-03-19) · ifr.org "VDA 5050 explained" · synaos.com · ottomotors.com (Rockwell certifications) · massrobotics.org · reference.opcfoundation.org (OPC 40010) · index.ros.org/p/vda5050_connector · github.com/nvidia-isaac/isaac_mission_dispatch · audit: `research/vda5050-robot-fleet-2026-07.md` (V1–V12)

*Demo numbers (the GR00T inference, the QoS/RMW matrices) are our own captured runs,
July 2026. Per-claim citations plus the audit trail: `research/claims-audit-2026-07.md`
and the repo's `research/` folder.*
