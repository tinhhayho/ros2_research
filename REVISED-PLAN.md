# PLAN.md — `ros2-explained` (Linux-native, medium scope, embedded audience)

A self-contained repo that **explains** (slides + concept docs) and **demonstrates** (three
focused live Docker demos) the architecture and middleware layer of ROS 2 — written for
**embedded / firmware engineers new to robotics**, to satisfy a manager's request to learn ROS 2
and introduce it to the team in a meeting.

> **Status:** Plan only. **No code written yet.** Everything below — versions, tree, demo design,
> distro pick — is up for edits before a single line is written.

---

## What changed vs the original PLAN.md (read this first)

This is a **retarget** of an earlier plan that assumed a macOS / Apple-Silicon / Docker Desktop
host and a four-demo scope. Three things changed:

1. **Host is native Linux** (`/home/tinhn/Documents/dev/ros2_research`, x86_64, kernel 7.0,
   Docker 29.6, Compose v5.2, `CONFIG_CAN_VCAN=m`). The entire Docker Desktop platform-limitation
   analysis is **deleted** and replaced with Linux reality. On Linux, real host networking works,
   cross-container DDS multicast discovery works, and `vcan`/SocketCAN is mainline. Most of the
   original's defensive workarounds simply disappear (see §1).
2. **Medium scope = exactly three demos.** Demo 1 (pub/sub + service + action), a **QoS
   compatibility** demo, and a **middleware / RMW-swap** demo. The original's micro-ROS demo and
   CAN FD work are **removed from the core** and reduced to a short **optional embedded appendix**
   (§7) — appropriate for the audience without bloating a meeting demo.
3. **Audience tilt = embedded/firmware.** Teaching leans on firmware analogies (discovery ≈ bus
   endpoint enumeration, RTPS HEARTBEAT/ACKNACK ≈ ARQ / sliding-window, QoS ≈ bus reliability
   trade-offs) and the appendix points at real MCUs as the next step.

The engineering rigor is **kept**: pinned versions via `VERSIONS.lock` (by sha256 digest), the
"no fabricated output" rule, a single `Makefile` entrypoint (host needs only Docker), the
build→verify→report-per-step workflow, and heavily-commented teaching code.

---

## 0. How I will work (process contract)

- **Incremental, verified, demo-by-demo.** Build one demo, run it *for real* in Docker on this
  Linux host, capture the *actual* output, write its verify script, then move on. Report back
  after each demo.
- **No fabricated output, ever.** Every log/snippet in the docs and runbook is copy-pasted from a
  real run. Anything not yet captured is written literally as `<!-- TODO-capture -->`.
- **Everything pinned.** ROS distro, base image (by **sha256 digest**), apt packages, pip
  packages, and helper images are pinned. A committed `VERSIONS.lock` records the exact digests
  and resolved versions captured during `make build`. No `:latest`.
- **Single entrypoint = `./run.sh` (canonical) with a thin `Makefile` wrapper.** `./run.sh build`,
  `./run.sh demo-1..3`, `./run.sh slides`, `./run.sh test`, `./run.sh clean`, `./run.sh shell` —
  and identical `make <target>` aliases where `make` is installed. The host needs **only Docker +
  the compose plugin**, no ROS 2 and **not even `make`** (this machine had no `make`, which is why
  the bash dispatcher — not the Makefile — is canonical).
- **Teaching code.** Each node is short, heavily commented, readability over performance.

---

## 1. Host & platform reality (Linux-native — verified on this machine)

| Probe | Result on this host |
|---|---|
| OS | **Linux (Ubuntu-class), kernel `7.0.0-22-generic`** |
| Architecture | **`x86_64` (amd64)** |
| Docker Engine | `29.6.0` ✅ |
| Compose plugin | `v5.2.0` ✅ |
| SocketCAN vcan | `CONFIG_CAN_VCAN=m` ✅ (loadable via `modprobe vcan`) |

**Because this is a native Linux Docker host, the original macOS constraints are DROPPED or
SIMPLIFIED. Concretely:**

1. **`network_mode: host` is REAL host networking on Linux** — the container shares the host's
   network namespace, no NAT, no userland proxy, no L4-only VM bridge. **DROP** the original
   "avoid host networking" rule. We use `network_mode: host` as the default for the demo services.
   *(The L4-only host-mode caveat was a Docker Desktop artifact only.)*
2. **Cross-container DDS multicast discovery WORKS on Linux.** Fast DDS (the Jazzy default RMW)
   uses SPDP simple discovery over UDP multicast; with host networking it behaves like native
   ROS 2, so nodes in **separate containers** discover each other reliably. **SIMPLIFY** — the
   original "cram every node into one container" workaround is no longer required. Running each
   role as its own process/container is the default; single-container is kept only as an
   *optional* teaching variant. *(The classic "Docker bridge drops multicast between containers"
   failure is real but specific to bridge networks — host networking is the Linux fix.)*
3. **`vcan`/SocketCAN with CAN FD is mainline** (vcan since kernel 2.6.24; `CONFIG_CAN_VCAN=m`
   confirmed here). The original macOS "CAN is unavailable / self-skip" gate is **DROPPED**. CAN
   FD could run for real here — but per the medium scope it lives only in the **optional embedded
   appendix** (§7), not the core.

**Networking decision (Linux-native, simplest reliable single-host setup):**
**`network_mode: host` + `ipc: host`** for the demo services.
- `network_mode: host` → native multicast discovery + shared host IP, lowest latency, no NAT.
- `ipc: host` (or `-v /dev/shm:/dev/shm`) → Fast DDS **shared-memory transport** works across
  containers; without it two containers see "same host" but have separate `/dev/shm` and silently
  fall back / fail SHM. This is itself a teaching point.
- A user-defined bridge (`ros2net`) is demoted to an **optional isolation variant** only.
- **`ROS_DOMAIN_ID`** is the canonical, lightweight in-host isolation knob (same-domain nodes
  discover each other; different domains are fully isolated, no discovery). It works identically
  under host networking, so it — not container boundaries — is how we isolate concurrent demos
  and drive the Demo 3 domain-isolation bonus.

---

## 2. Distro, base image, and RMW decisions (verified 2026-06-26)

### Distro pick: **Jazzy Jalisco (LTS)** — with a documented forward-looking note on Lyrical Luth

As of mid-2026 there are three candidate distros; the verified facts:

| Distro | Released | Type | EOL | Ubuntu | Notes |
|---|---|---|---|---|---|
| **Jazzy Jalisco** | 2024-05-23 | **LTS** | **2029-05-31** | 24.04 Noble | ~2 yr mature, broadest ecosystem |
| Kilted Kaiju | 2025-05-23 | non-LTS | **~Nov 2026** | 24.04 Noble | EOL in ~5 months — **avoid** |
| **Lyrical Luth** | 2026-05-22 | **LTS** | **~2031-05-31** | 26.04 Resolute | longest runway, but ~1 month old |

Cadence (REP-2000): even years ship an **LTS** (5-yr support), odd years a **non-LTS** (1.5-yr).

**Final pick: Jazzy Jalisco.** Rationale: for a brand-new beginner-facing teaching/demo project
started in mid-2026, Jazzy is the safest choice — ~2 years mature, the **broadest ecosystem of
packages, drivers, and tutorials**, on stable Ubuntu 24.04, supported through **May 2029** (well
past any teaching cycle).

**Forward-looking note (put in `docs/05-rmw.md`):** **Lyrical Luth** (2026-05-22, LTS, EOL ~2031)
is the only justifiable alternative — it has the **longest support window**. But at ~1 month old
its package/driver/tutorial ecosystem and stability lag Jazzy, carrying early-adopter friction
undesirable for beginners. Recommend Lyrical only for teams that prioritize maximum longevity and
can tolerate bleeding edge. **Explicitly avoid Kilted** — it is non-LTS and goes EOL ~Nov 2026,
which would orphan a new project almost immediately.

### Base image & RMWs

- **Base image:** `ros:jazzy-ros-base-noble` (alias `ros:jazzy`) — Ubuntu 24.04 LTS. `ros-base`
  gives the full `ros2` CLI; we apt-install tooling (`rqt_graph`, `ros2cli` extras, `graphviz`)
  on top. **Pinned by sha256 digest** in the Dockerfile.
- **Default RMW (Jazzy): `rmw_fastrtps_cpp`** (eProsima Fast DDS) — bundled with `ros-base`. No
  `RMW_IMPLEMENTATION` needed for default behavior. Jazzy ships `rmw_fastrtps_cpp ~8.4.2`,
  `fastdds ~2.14.x`.
- **All three RMWs installed in the image:**
  - `rmw_fastrtps_cpp` (default, bundled; ~`8.4.2`)
  - `ros-jazzy-rmw-cyclonedds-cpp` (~`2.2.3`, Cyclone DDS ~0.10.x) — **Tier 1** in Jazzy
  - `ros-jazzy-rmw-zenoh-cpp` (~`0.2.9`) + the Zenoh router daemon `rmw_zenohd`
- **Zenoh / Tier-1 nuance (state precisely in `docs/05-rmw.md`):** **Kilted Kaiju (May 2025) is
  the first ROS 2 release with Zenoh as a Tier-1 RMW.** In **Jazzy, Zenoh is installable but NOT
  Tier 1** — Jazzy's Tier-1 RMW set is **Fast DDS, Cyclone DDS, and Connext** only. Describe Zenoh
  on Jazzy as "available add-on, not Tier 1." Also note the Jazzy Zenoh backport (`0.2.x`) is
  markedly older/less mature than Kilted's (`0.6.x`).
- **Zenoh requires its router by default:** `rmw_zenoh` **disables multicast scouting by default
  by design** (independent of any Docker concern); nodes discover via the `rmw_zenohd` router's
  gossip scouting. So we **must launch `rmw_zenohd`** before Zenoh nodes (or explicitly enable
  multicast scouting). This is a real behavioral difference from the DDS RMWs and a teaching point.

---

## 3. Proposed directory tree

Repo root = the working directory **`/home/tinhn/Documents/dev/ros2_research`** (a git repo
already). I will scaffold in place.

```
ros2_research/                  # = repo root
├── README.md                   # "Why ROS 2" narrative, ROS1-vs-2 table, arch diagram, quickstart, 5-min demo script
├── PLAN.md                     # this file
├── VERSIONS.lock               # captured at build: base-image digest + resolved apt/pip/image versions (REAL)
├── Makefile                    # single entrypoint: build / demo-1..3 / slides / test / clean / shell
├── .gitignore
├── .dockerignore
├── docker/
│   ├── Dockerfile              # FROM ros@sha256:<digest>; +Cyclone +Zenoh RMWs +tmux/graphviz/ros2cli extras
│   ├── docker-compose.yml      # services: ws, zenoh-router (network_mode: host, ipc: host)
│   └── zenoh/
│       └── router.json5        # optional rmw_zenohd / session config
├── ws/                         # ROS 2 colcon workspace (built inside the image)
│   └── src/
│       ├── demo_basic/         # Demo 1: rclpy talker/listener + 1 rclcpp talker, AddTwoInts svc, Fibonacci action
│       │   ├── demo_basic/                (rclpy nodes)
│       │   ├── src/                        (rclcpp talker.cpp)
│       │   ├── launch/                     (multi-process launch: brings up the whole graph)
│       │   └── package.xml  CMakeLists.txt / setup.py
│       └── demo_qos/           # Demo 2: configurable pub/sub (reliability / durability / depth via ROS args)
│           # Demo 3 (RMW swap) reuses demo_basic's talker/listener — no separate package.
├── docs/
│   ├── 01-architecture.md      # app → rclcpp/rclpy → rcl → rmw → DDS/Zenoh → OS/net (Mermaid layered diagram)
│   ├── 02-dds-rtps.md          # DCPS, global data space, RTPS, HEARTBEAT/ACKNACK ≈ ARQ / sliding-window
│   ├── 03-qos.md               # policies, RxO rule, AUTO-GENERATED results table, real `topic info -v`
│   ├── 04-discovery.md         # SPDP/SEDP (Mermaid sequence), multicast vs bridge, Domain ID isolation
│   ├── 05-rmw.md               # RMW abstraction, DDS-vendor interop, Zenoh + router, Jazzy-vs-Lyrical/Kilted tier note
│   ├── 06-microros-appendix.md # OPTIONAL embedded teaser: DDS-XRCE, Client↔Agent, rclc executor, footprint, real MCUs
│   └── img/                    # generated node-graph artifacts (text + PNG/SVG if produced)
├── slides/
│   └── slides.md               # Marp deck (10–15 slides), one "what you'll see + run command" slide per demo
├── runbook/
│   └── live-demo-runbook.md    # on-stage script: exact commands + expected output (TODO-capture placeholders)
└── scripts/
    ├── lib.sh                  # shared bash helpers (logging, in-container exec, wait-for)
    ├── run_in_container.sh     # docker compose run wrapper used by the Makefile
    ├── capture_versions.sh     # writes VERSIONS.lock (digests + resolved versions) — real data
    ├── verify_basic.sh         # Demo 1 acceptance
    ├── verify_qos.sh           # Demo 2 acceptance (+ generates the results table)
    └── verify_middleware.sh    # Demo 3 acceptance (3 RMWs + DDS↔Zenoh non-interop)
```

---

## 4. Pinned versions (lockfile strategy)

I will **not invent digests in this doc** (that would be fabricated output). Instead `make build`
runs `scripts/capture_versions.sh`, which pulls each tag, records its immutable `sha256` digest
and resolved package versions, and writes `VERSIONS.lock` (committed). The Dockerfile then pins
`FROM ros@sha256:<digest>`.

| Component | Tag we resolve & pin | Approx version (verified) | How pinned |
|---|---|---|---|
| Base image | `ros:jazzy-ros-base-noble` | Jazzy / Ubuntu 24.04 | `FROM ros@sha256:<digest>` |
| Fast DDS RMW | bundled in `ros-base` | `rmw_fastrtps_cpp ~8.4.2`, fastdds ~2.14.x | apt `pkg=version` |
| Cyclone DDS RMW | `ros-jazzy-rmw-cyclonedds-cpp` | `~2.2.3` (Cyclone ~0.10.x) | apt `pkg=version` |
| Zenoh RMW + router | `ros-jazzy-rmw-zenoh-cpp` | `~0.2.9` (not Tier 1 on Jazzy) | apt `pkg=version` |
| Slides | `marpteam/marp-cli:v4.4.0` | `4.4.0` | `@sha256:<digest>` |
| Headless graph (opt.) | `graphviz` (apt) | pinned in build | apt `pkg=version` |

> Reproducibility caveat (in README): apt/pip archives prune old versions over time, so the
> **base-image digest is the primary reproducibility anchor**; `VERSIONS.lock` records the rest.

---

## 5. Docker design (Linux-native compose + networking)

- **`make build`** → `docker compose build` the image + `colcon build` the workspace inside it +
  write `VERSIONS.lock`.
- **Services in `docker/docker-compose.yml`** (all `network_mode: host` + `ipc: host`):
  - **`ws`** — main workspace container. Demos run their node graph here; on Linux we can also
    spawn **multiple `ws` containers/processes** that discover each other natively. We isolate
    concurrent runs with `ROS_DOMAIN_ID`, not container walls.
  - **`zenoh-router`** — runs `ros2 run rmw_zenoh_cpp rmw_zenohd` for Demo 3's Zenoh leg. Because
    `rmw_zenoh` disables multicast scouting by default, **this router must be up before Zenoh
    nodes start** (a legitimate rmw_zenoh design lesson, not a Docker workaround).
- Each `make demo-N` does a `docker compose run`/`up` of **exactly** the services it needs, with
  the right `RMW_IMPLEMENTATION` / `ROS_DOMAIN_ID` env.
- **Optional isolation variant:** a user-defined bridge (`ros2net`) is documented in
  `docs/04-discovery.md` to *demonstrate* that bridge networks drop multicast between containers
  (so you'd need a Discovery Server / explicit peer list) — i.e. as a teaching contrast to host
  networking, not the default.

---

## 6. The three core demos

### Demo 1 — pub/sub + service + action (`make demo-1`)
- **Nodes:** rclpy `talker`/`listener` (`std_msgs/String`); a **second talker in rclcpp** for the
  C++/firmware audience; `AddTwoInts` service server+client; a **Fibonacci action** with feedback
  + cancel.
- **How it runs on Linux:** one `ros2 launch` brings up the graph, and (to show off native
  discovery) at least one node runs as a **separate process/container** under `network_mode: host`
  — separate processes find each other with no master and no central broker.
- **CLI shown:** `ros2 node list`, `ros2 topic echo`, `ros2 service call`,
  `ros2 action send_goal --feedback`.
- **Node-graph artifact:** guaranteed **text** capture (`ros2 node list` / `ros2 node info` /
  `ros2 topic info`) into `docs/img/`, **plus** a hand-written Mermaid graph in `docs/01`. *Bonus:*
  attempt a real PNG via `xvfb-run -a rqt_graph` — if flaky in automation, the text artifact
  satisfies acceptance and I'll say so honestly.
- **Embedded analogy:** discovery ≈ **bus endpoint enumeration** (like devices announcing
  themselves on a bus) — no master, no hand-assigned addresses.
- **Aha moment:** separate OS processes discover and talk automatically — **no ROS master**.
- **Verify (`verify_basic.sh`) — acceptance:** listener received ≥1 msg; service returned `5` for
  `2+3`; action returned a result **with ≥1 feedback**; a node-graph text file exists in
  `docs/img/`.

### Demo 2 — QoS compatibility ⭐ (`make demo-2`)
- One configurable `qos_pub` + `qos_sub` (reliability / durability / depth via ROS args). A matrix
  runner logs **real** messages-received-in-N-seconds per combo and **auto-generates a Markdown
  table** into `docs/03-qos.md`.
- **The rule, stated directionally:** a subscription **requests** the *minimum* quality it will
  accept; a publisher **offers** the *maximum* it can provide; they match only if every requested
  policy is **not more stringent** than the offered one — i.e. **offered ≥ requested**
  (publisher/offered side must be the stronger of the pair).
- **Cases (factually corrected per ROS 2 QoS docs):**
  - `best_effort` pub + `reliable` sub → **0 msgs** (INCOMPATIBLE; the headline real-world case —
    sensor publishers default best_effort, a reliable subscriber gets nothing).
  - `reliable` pub + `best_effort` sub → **match** (asymmetry — show both directions).
  - `volatile` pub + `transient_local` sub → **INCOMPATIBLE** (0 msgs).
  - **Late-joiner:** `transient_local` pub **AND** `transient_local` sub → late subscriber
    receives **old/previously-sent** samples (latched). *Note:* `transient_local` pub +
    `volatile` sub is compatible but the volatile sub gets **new messages only** — latching needs
    `transient_local` on **both** sides.
- **Which policies even participate:** durability, deadline, liveliness (incl. lease duration),
  reliability. **History, Depth, and Lifespan do NOT affect compatibility** (common
  misconception — mismatched depth never blocks a connection). And it's an **AND** rule: fixing
  only reliability while durability still mismatches still yields no data.
- **Diagnostic taught:** real `ros2 topic info <topic> -v` (per-endpoint QoS) embedded in the doc;
  also watch **node logs** — on an incompatible match the RMW **logs a warning** (e.g. "offering
  incompatible QoS. No messages will be sent to it") and raises an Incompatible-QoS event.
- **Embedded analogy:** QoS ≈ **bus reliability/timing trade-offs** — reliable+durable is like an
  acknowledged, buffered transfer (CAN ACK / retried frame); best_effort is fire-and-forget (raw
  UDP / unacknowledged frame). You pick per-stream, and **both ends must agree**.
- **Aha moment:** the topic still appears in `ros2 topic list` and both endpoints stay visible,
  but **data is not delivered and a warning is logged** (it is *not* truly silent).
- **Verify (`verify_qos.sh`) — acceptance:** matrix completes & table generated; the
  best_effort→reliable case yields **exactly 0**; a valid case yields **≥1**; the both-sides
  `transient_local` late-joiner receives old samples; real `topic info -v` output captured.

### Demo 3 — middleware / RMW swap (`make demo-3`)
- Reuses Demo 1's talker/listener. A script loops over `rmw_fastrtps_cpp`, `rmw_cyclonedds_cpp`,
  `rmw_zenoh_cpp`: sets `RMW_IMPLEMENTATION`, runs **`ros2 daemon stop`** (explains *why* — the
  daemon caches the RMW from first launch), prints the **active RMW** via
  `ros2 doctor --report | grep -i middleware`, runs the pair, confirms data flows.
- **Zenoh leg:** auto-starts the `zenoh-router` (`rmw_zenohd`) service **first** (multicast
  scouting is off by default in `rmw_zenoh`), then connects nodes to it.
- **Required teaching moments (factually corrected per rmw/Zenoh research):**
  - **Fast DDS talker ↔ Cyclone DDS listener interoperate** at the **topic** level — both speak
    the OMG **DDSI-RTPS** wire protocol. *Caveat to state:* this is true for topics with matching
    QoS/types; **cross-vendor services/actions are not guaranteed**, and ROS 2 still recommends
    all nodes in a system use the **same RMW**. So show interop, but don't sell it as fully
    seamless.
  - **Fast DDS talker ↔ Zenoh listener → NO data.** `rmw_zenoh` uses the **Zenoh wire protocol,
    not DDSI-RTPS**, so it does **not** interoperate on the wire with DDS RMWs. Cross-stack comms
    need a **separate bridge** (`zenoh-bridge-ros2dds` / `zenoh-plugin-ros2dds`); we do **not** mix
    Zenoh and DDS nodes expecting native discovery. (Correct the original's implication that they
    interoperate.)
- **Bonus (first-class on Linux host net):** `ROS_DOMAIN_ID` isolation — same RMW, mismatched
  domain → **no discovery, silence**. This is the canonical logical-isolation mechanism and works
  identically under host networking.
- **Embedded analogy:** the RMW is a **swappable transport/PHY driver** behind a stable API
  (`rcl`/`rmw`) — like retargeting the same app from UART to SPI to CAN by swapping the HAL, except
  here it's Fast DDS ↔ Cyclone ↔ Zenoh. Same app code, different wire.
- **Aha moment:** the *same node binaries* run over three different middlewares by flipping one
  env var — and DDS↔DDS interoperate on the wire while DDS↔Zenoh do not (different protocol).
- **Verify (`verify_middleware.sh`) — acceptance:** runs under all 3 RMWs, each prints the correct
  active RMW and confirms flow; Fast DDS↔Cyclone topic interop shows ≥1 msg; DDS↔Zenoh shows
  **0 msgs** (non-interop); the domain-mismatch case shows 0 msgs.

---

## 7. OPTIONAL appendix — micro-ROS on real MCUs (the natural next step)

Short teaser only — **not part of the core three demos, not run in CI** — written for the embedded
audience as "where ROS 2 meets your firmware." Lives in `docs/06-microros-appendix.md` and one
closing slide. Facts (verified 2026-06-26):

- **What it is:** micro-ROS puts a ROS 2 client on resource-constrained MCUs. The MCU runs a
  lightweight **XRCE Client**; a **`micro_ros_agent`** process on a Linux host bridges it into DDS
  via the **DDS-XRCE** protocol, so the MCU appears as an **ordinary ROS 2 node**
  (`ros2 node list` / `ros2 topic echo` interop). **Gotcha to call out:** you must run the
  **micro-ROS Agent** (which adds the ROS 2 Graph manager), *not* the bare eProsima Micro XRCE-DDS
  Agent, to get node-graph visibility.
- **Transports:** built-in profiles are **UDP, TCP, and Serial (UART & USB-CDC)**, selected at
  **compile time** via `RMW_UXRCE_TRANSPORT` (`udp` default | `serial` | `custom`). **CAN FD is a
  *custom* transport** (Micro XRCE-DDS v2.1; Renesas RA reference platform) — *not* a drop-in
  fourth profile. Runtime config covers transport **parameters/instance** (agent IP:port, serial
  device, or a user-supplied open/close/write/read callback set via
  `rmw_uros_set_custom_transport`), not the profile *type*.
- **Executor:** micro-ROS uses **`rclc` (C)** on the shared **`rcl`** core instead of **`rclcpp`
  (C++)**. Lead with **footprint** (C-only, no heavy C++ runtime/dynamic allocation) then
  **determinism** (the `rclc` Executor gives user-defined static execution order, conditional
  execution, trigger conditions, and Logical Execution Time semantics, vs the non-deterministic
  round-robin of the `rclcpp` Executor). Good talking point: "same core (`rcl`), lighter shell."
- **Footprint (cite micro.ros.org):** **< 75 KB flash, ~3 KB RAM for a full publisher+subscriber
  app at 512 B messages**, ~**400 B/publisher** and ~**500 B/subscriber** incremental; the Client
  is dynamic-memory-free at runtime. **Label this as the *middleware* figure** — the whole firmware
  image also includes RTOS + `rcl`/`rclc` + network stack, so size boards at **tens of KB RAM,
  ~256 KB+ flash** minimum.
- **Real hardware next step:** recommend **ESP32** (cheapest/most documented, Wi-Fi UDP) or
  **Raspberry Pi Pico / RP2040** (USB serial) as a first board; **Zephyr + STM32** or the
  **Renesas EK-RA6M5** as the professional/reference path. RTOS options: **FreeRTOS / Zephyr /
  NuttX / bare-metal** (micro-ROS is an official Zephyr module). Integration components:
  `micro_ros_arduino`, `micro_ros_espidf_component`, `micro_ros_stm32cubemx_utils`,
  `micro_ros_platformio`, `micro_ros_zephyr_module`.
- **Version-sensitive note:** `micro_ros_setup` is released per-distro; pin the branch to match the
  core demo. For this Jazzy-based project use the **`jazzy` branch**
  (`git checkout jazzy` in `micro_ros_setup`). Live branches include humble/iron/jazzy/kilted/
  rolling; **Iron is EOL — avoid**.

---

## 8. Deliverables

### a) Marp slide deck → **HTML** (built in Docker)
- `slides/slides.md` → built via `marpteam/marp-cli:v4.4.0` in Docker → **`slides.html`** (the
  deliverable). Marp emits a **single self-contained HTML file** (CSS inlined) you open in a
  browser and present (keyboard nav + presenter view) — no web server, no runtime deps.
  **Marp over reveal.js** (one-shot static build vs running a server). PDF is **optional only**
  (`make slides-pdf`); the primary/committed slide artifact is **HTML**.
- 10–15 slides: Why ROS 2 → ROS 1 vs ROS 2 → layered architecture → one "what you'll see + run
  command" slide per demo → QoS RxO rule → RMW swap / interop → closing micro-ROS-on-MCUs teaser.
- **Caveat:** Marp does **not** render Mermaid natively → slide diagrams are simple Marp-native or
  pre-rendered to SVG/PNG; the `mermaid` source stays in `docs/` where GitHub renders it live.

### b) Concept docs (one concept per file, each with Mermaid)
Tree in §3. Mermaid diagrams: layered architecture (`01`); RTPS HEARTBEAT/ACKNACK ≈ ARQ /
sliding-window (`02`); QoS RxO matrix (`03`); SPDP/SEDP discovery sequence + Domain-ID isolation
(`04`); RMW abstraction + DDS interop vs Zenoh-needs-a-bridge (`05`); micro-ROS Client↔Agent↔DDS
(`06`, appendix). Embedded analogies throughout (discovery ≈ endpoint enumeration;
HEARTBEAT/ACKNACK ≈ ARQ; QoS ≈ bus reliability trade-offs; RMW ≈ swappable transport/HAL).
**Honest caveats included:** vendor benchmarks are self-published (no single "best DDS");
"real-time" is potential, not automatic (depends on OS/scheduler/executor — why micro-ROS uses
rclc); cross-vendor services/actions and DDS↔Zenoh interop have limits.

### c) Live demo runbook (`runbook/live-demo-runbook.md`)
A tight, on-stage script the user **reads from in the meeting**: numbered steps, the **exact
command** to type for each demo, and the **real expected output** beside it. Every output block is
a real capture or marked `<!-- TODO-capture -->` until the demo has actually been run. Includes a
"if discovery looks slow, do X" panic section and the `ros2 daemon stop` reminder for the RMW swap.

---

## 9. Order of work (each step ends in a real, verified run)

| Step | What | Done when | Time est. |
|---|---|---|---|
| 0 | **Scaffold + image** — skeleton, `.gitignore`/`.dockerignore`, `Makefile` (build/shell), `Dockerfile`, `docker-compose.yml` (host net + ipc host), `capture_versions.sh` | `make build` succeeds; `VERSIONS.lock` written with **real** digests | **2–3 h** |
| 1 | **Demo 1** (pub/sub + service + action) → run for real (multi-process, host net) → `verify_basic.sh` green → capture output → write `docs/01`, `02`, README quickstart. **Pause & report.** | verify_basic green; node-graph artifact in `docs/img/` | **3–4 h** |
| 2 | **Demo 2** (QoS) → run matrix → `verify_qos.sh` green → auto-generate QoS table + capture `topic info -v` → write `docs/03` | 0-msg case exact; valid ≥1; late-joiner old samples; `-v` captured | **3–4 h** |
| 3 | **Demo 3** (RMW swap) → run all 3 RMWs + DDS↔DDS interop + DDS↔Zenoh non-interop + domain isolation → `verify_middleware.sh` green → write `docs/04`, `05` | each RMW prints active RMW + flows; Zenoh non-interop = 0 | **3–4 h** |
| 4 | **Appendix + slides** → write `docs/06` micro-ROS teaser (no run) → `make slides` builds **`slides.html`** in Docker (PDF optional via `make slides-pdf`) | `slides.html` produced with nothing on host but Docker | **2–3 h** |
| 5 | **Runbook + finalize** → write `runbook/live-demo-runbook.md` from real captures → README narrative + ROS1-vs-2 table + 5-min script → `make test` aggregates all verify scripts → final "no fake output / Mermaid renders" pass | `make test` green; runbook has no stray `TODO-capture` | **2–3 h** |

**Total rough estimate: ~15–21 hours of focused work.**

---

## 10. Acceptance criteria → where each is met

| Criterion | Met by |
|---|---|
| `make build` succeeds, versions pinned by digest | §4, step 0, `VERSIONS.lock` |
| Host needs only Docker (no ROS install) | §0, Makefile, §5 |
| Demo 1: ≥1 msg, correct service (`2+3=5`), action result + ≥1 feedback, node-graph file | `verify_basic.sh`, `docs/img/` |
| Demo 2: matrix table, best_effort→reliable **exactly 0**, valid ≥1, both-sides transient_local late-joiner gets old samples, real `-v` captured | `verify_qos.sh`, `docs/03` |
| Demo 3: 3 RMWs print active RMW + flow, Fast DDS↔Cyclone topic interop ≥1, **DDS↔Zenoh = 0** (non-interop), domain-mismatch = 0 | `verify_middleware.sh` |
| `make slides` builds **`slides.html`** with nothing on host but Docker (PDF optional) | §8a, Marp in Docker |
| Live runbook reads cleanly on stage, all outputs real or TODO-capture | `runbook/live-demo-runbook.md`, step 5 |
| Docs render on GitHub, Mermaid works, no fabricated output | step 5, lockfile + real captures |
| micro-ROS appendix factually correct (transports, footprint, agent gotcha, Jazzy branch) | `docs/06`, §7 |

---

## 11. Resolved decisions

1. **Repo location:** build directly in **`/home/tinhn/Documents/dev/ros2_research`** (repo root =
   this dir; already a git repo).
2. **Distro:** **Jazzy Jalisco (LTS, EOL 2029-05-31)**; Lyrical Luth noted as the longest-runway
   alternative, Kilted explicitly avoided (EOL ~Nov 2026). Zenoh on Jazzy = available add-on, not
   Tier 1.
3. **Networking:** **`network_mode: host` + `ipc: host`** (Linux-native); `ROS_DOMAIN_ID` for
   in-host isolation; user-defined bridge only as an optional contrast lesson.
4. **Scope:** **three core demos** (pub/sub+service+action, QoS, RMW swap); **micro-ROS/CAN FD is
   an optional appendix only**, not run in CI.

**Next step (awaiting go-ahead):** step 0 (scaffold + image, `make build`, `VERSIONS.lock`), then
Demo 1, after which I pause and report with the real verified output.
