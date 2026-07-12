# How Robot Software Actually Works — a 10-minute primer

**For embedded/firmware engineers meeting robotics for the first time.**

> No prior robotics knowledge assumed. If you already know what a ROS node is, skip this
> and read the full deep-dive instead: *Robot Software Stacks 2026 — from firmware to
> foundation models*.
>
> **Images:** figures live in the repo folder `slides/assets/` — attach them to the
> Confluence page when publishing.

---

## 1. Start with a story: "pick up the cup"

Imagine a humanoid robot hears the command *"pick up the cup."* Here is the entire journey
of that command, from words to electrical current — and notice how each step runs **faster**
than the one above it:

1. **An AI model** looks at the camera image and the text, and decides *what motion to
   make* — roughly 10 times per second. (These models are called VLAs —
   Vision-Language-Action models. NVIDIA's GR00T is one; we actually ran it on a desktop
   GPU, more below.)
2. **A motion policy** turns that intention into smooth whole-body movement — about 50
   times per second.
3. **A control loop** on a Linux computer converts movement into torque targets for every
   joint — about 1,000 times per second (1 kHz).
4. **A fieldbus** (an industrial network like EtherCAT or CAN-FD — the same buses you know
   from automotive/industrial work) carries those targets to small microcontrollers, one
   per joint.
5. **Each joint's MCU firmware** runs the motor current loop — 8,000 to 32,000 times per
   second. This is classic embedded work: timers, PWM, ADCs, an RTOS or bare metal.

![From foundation model to motor](groot-cascade.png)

**The one insight to keep:** the AI at the top changed everything about *what robots can
do* — but steps 3, 4, and 5 are the same embedded engineering they have been for twenty
years. That bottom half is where firmware people already have all the skills.

---

## 2. The three words you actually need

All robot middleware talk boils down to three ideas. In plain words:

- **Node** — one running program. A camera driver is a node. A motor controller is a node.
  A path planner is a node. A robot is typically 5–50 nodes.
- **Topic** — a named data stream that nodes publish to and subscribe to, like a labeled
  radio channel. The camera node publishes images on `/camera/image`; anyone interested
  subscribes. Publishers don't know or care who is listening.
- **Service** — a request/response call between nodes ("add these two numbers", "reset the
  map") — like a remote function call.

For a firmware engineer, the mental mapping is easy: **topics ≈ broadcast frames on a bus,
services ≈ register read/write transactions.**

Here is a real screenshot from our own machine — five running nodes and the topic
connecting them (note: one publisher is Python, the other is C++, and the subscriber
cannot tell the difference):

![A live node graph](rqt-graph-real.png)

---

## 3. So what is ROS 2, actually?

**ROS 2 is not an operating system** (despite the name — Robot Operating System). It is
three things bundled together:

1. **A middleware** — the plumbing that lets nodes find each other and exchange topics/
   services over the network, with *no central server*. Two nodes on the same network
   discover each other automatically.
2. **A set of libraries** — you write nodes in Python (`rclpy`) or C++ (`rclcpp`). A
   complete, working publisher node is ~20 lines of Python.
3. **A huge ecosystem of ready-made nodes** — mapping, navigation, arm motion planning,
   drivers for hundreds of sensors. All open source (Apache/BSD licensed), all on GitHub.

Why the industry standardized on it: if your motor driver speaks ROS 2, it instantly works
with every mapping, navigation, and visualization tool ever written for ROS 2. It is the
USB of robot software.

*(Honest caveat: ROS 2 rules industrial and research robotics — warehouse robots, arms,
research humanoids. Commercial humanoids like Tesla's and Figure's, and self-driving cars,
run proprietary stacks. Details in the deep-dive.)*

---

## 4. The one rule that organizes everything

If you remember a single technical rule from this primer, make it this:

> **The loop rate picks the layer.** The faster a loop must run — and the more catastrophic
> a missed deadline — the lower in the stack it lives.

| Needs | Lives on | Examples |
|---|---|---|
| µs-level timing, provably never late | **MCU firmware** (bare metal / RTOS) | motor current loops, E-stop |
| ~1 ms timing, rarely late | **real-time Linux** (`ros2_control` framework) | joint position control |
| No hard deadline, heavy math | **plain Linux / GPU** (the ROS 2 world) | mapping, path planning, AI models |

Two consequences worth internalizing:

- **"Real-time" means guaranteed deadlines, not speed.** Linux with the PREEMPT_RT option
  can promise ~1 ms loops (jitter ≈ 50 µs — an illustrative tuned-PREEMPT_RT figure, not measured in this repo). It cannot promise 100 µs loops — that world
  belongs to MCUs. This is exactly why every robot still contains microcontrollers no
  matter how big its GPU is.
- **The AI never touches the motors directly.** If the vision model hangs for half a
  second, the layers below keep the robot stable and safe on their own. Safety-critical
  functions (the E-stop path) sit even lower — often on a separate safety-rated MCU or PLC
  that can cut power regardless of what any software above thinks.

![The full stack, one picture](stack-unified.png)

---

## 5. Five things that surprise firmware engineers

1. **There is no master.** Nodes discover each other peer-to-peer. You can start and kill
   nodes in any order; the graph heals itself.
2. **Your bus skills transfer directly.** The official way to connect real hardware to
   ROS 2 is a C++ class with two methods — `read()` (fieldbus → state) and `write()`
   (command → fieldbus) — running in the 1 kHz loop. If you have written a CAN or EtherCAT
   driver, you already know how to write one.
3. **Swappable everything.** The network layer under ROS 2 (DDS) can be swapped with an
   environment variable — no recompile. Controllers can be swapped from a YAML file.
   Think of it as a HAL culture applied to the whole robot.
4. **The tooling is genuinely good.** One command records every message on the system for
   later replay (`ros2 bag`). One command shows the live node graph (`rqt_graph`). One
   command plots any signal.
5. **A foundation model fits on a desktop.** We ran NVIDIA's GR00T N1.7 robot model
   (3 billion parameters) zero-shot on a single RTX GPU with 16 GB of memory: ~106 ms per
   inference, and each inference emits 8 future action steps (~75 generated steps/second
   of compute throughput). The frontier is closer than it looks.

---

## 6. Try it yourself in 30 minutes

Using our repo (everything runs in Docker — no ROS installation needed):

```bash
./run.sh build     # once: build the pinned image + workspace
./run.sh viz       # a turtle appears — drive it with the arrow keys
./run.sh rqt       # watch the live node graph while you drive
./run.sh demo-1    # pub/sub + service + action, Python and C++ on one graph
```

The turtle demo sounds like a toy, but it demonstrates the entire core: two nodes you can
see (`teleop` → `/turtle1/cmd_vel` topic → `turtlesim`), discovered with no configuration.

---

## 7. Where to go next

- **The full deep-dive** (same repo, `docs/blog-robot-software-stacks-2026-07.md`): the
  complete 2026 stack survey — wheeled robots, humanoids, fleet coordination (Open-RMF),
  NVIDIA's Physical AI platform vs its Automotive platform, safety certification, and our
  measured GR00T demo. Suggested first stops there: §1 (the map), §2.3 (real code),
  §8 (the demo).
- **Official ROS 2 tutorials:** docs.ros.org — the "Beginner: CLI tools" track takes an
  afternoon.
- **For the control-minded:** control.ros.org (`ros2_control`) — the bridge between your
  firmware world and the robot world.

*Written July 2026. All screenshots and numbers in this primer come from real runs on our
own machine.*
