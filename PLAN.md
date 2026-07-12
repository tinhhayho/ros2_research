> **Historical document (July 2026):** this is the original pre-build plan, kept for the
> record. The repo has long since been built — see `README.md` for the current state; the
> "no code yet" status below no longer applies.

# PLAN.md — `ros2-explained`

A self-contained repo that **explains** (slides + docs) and **demonstrates** (4 live Docker
demos) the architecture and middleware layer of ROS 2, for embedded/firmware engineers new
to robotics.

> **Status:** This is the plan only. **No real code has been written yet.** Per the brief, I
> stop here for your review. Everything below — versions, tree, demo design — is up for edits
> before I write a single line of code.

---

## 0. How I will work (process contract)

- **Incremental, verified, demo-by-demo.** I build one demo, run it *for real* in Docker on
  this machine, capture the *actual* output, write its verify script, and only then move on.
  I will report back after each demo.
- **No fabricated output, ever.** Every log/snippet in the docs is copy-pasted from a real run.
  Anything not yet run is written literally as `<!-- TODO: capture -->`.
- **Everything pinned.** ROS distro, base image (by **sha256 digest**), apt packages, pip
  packages, and Docker images are pinned. A committed `VERSIONS.lock` records the exact digests
  and resolved versions captured during `make build` (see §4). No `:latest`.
- **Single entrypoint = the Makefile.** `make build`, `make demo-1..4`, `make slides`,
  `make test`, `make clean`. The host needs **only Docker + the compose plugin** — no ROS 2.
- **Teaching code.** Each node is short, heavily commented, readability over performance.

---

## 1. Host & platform reality (this matters — verified on your machine)

| Probe | Result on this host |
|---|---|
| Docker Engine | `29.4.3` ✅ |
| Compose plugin | `v5.1.4` ✅ |
| Architecture | **`arm64` (Apple Silicon)** |
| OS | macOS (Darwin) — **Docker Desktop runs a Linux VM** |

**Consequences baked into the plan (all sourced during research):**

1. **`network_mode: host` does NOT behave like Linux** on Docker Desktop (host mode maps to the
   internal Linux VM, and the 4.34+ opt-in host networking is L4-only). → **We avoid host
   networking** and the demos do not depend on it.
2. **DDS multicast discovery across containers is unreliable** on Docker Desktop. → Demos 1 & 3
   run **all nodes inside a single container** (shared network namespace + shared memory →
   discovery just works). This is itself the lesson taught in `docs/04-discovery.md`.
3. **`vcan` / SocketCAN is unavailable** — Docker Desktop's LinuxKit kernel has no `CONFIG_CAN`,
   and `--privileged` / `--cap-add NET_ADMIN` **cannot** fix a missing kernel module. → The
   **CAN FD transport (Demo 4) is marked Linux-host-only and is skipped** on this Mac, with a
   UDP/serial fallback that *does* run here.
4. **arm64 image availability** must be confirmed at build time for every image
   (`ros`, `microros/micro-ros-agent`, `marpteam/marp-cli` are all multi-arch incl. arm64 per
   research; the micro-ROS agent has a from-source fallback if its arm64 tag is ever missing).

**What runs fully on this Mac:** Demo 1, Demo 2 (all 3 RMWs), Demo 3, Demo 4 (UDP + serial),
slides. **What needs a Linux host:** only Demo 4's optional CAN FD leg (clearly gated &
skippable). This honesty is part of the teaching content, not a defect.

---

## 2. Base image, RMWs, and middleware decisions (verified)

- **Base image:** `ros:jazzy-ros-base-noble` (the alias `ros:jazzy` points here) — Ubuntu
  24.04 LTS (Noble), Jazzy GA **2024-05-23**, **LTS until 2029-05-31**. `ros-base` gives the
  full `ros2` CLI; we apt-install tooling (`rqt_graph`, etc.) on top. (`desktop-full` lives under
  `osrf/ros`, is huge, and is not needed.) **Pinned by digest** in the Dockerfile.
- **Default RMW (Jazzy): `rmw_fastrtps_cpp`** (eProsima Fast DDS) — included with `ros-base`.
- **All 3 RMWs installed in the image:**
  - `rmw_fastrtps_cpp` (default, bundled; ~`8.4.4`)
  - `ros-jazzy-rmw-cyclonedds-cpp` (~`2.2.3`)
  - `ros-jazzy-rmw-zenoh-cpp` (~`0.2.9`) + the Zenoh router daemon `rmw_zenohd`
- **Zenoh / LTS trade-off (stated in `docs/05-zenoh.md`):** **Kilted Kaiju (May 2025) is the
  first ROS 2 release with Zenoh as a Tier-1 RMW.** Jazzy (our LTS pick) consumes Zenoh as a
  *binary add-on* package. We choose Jazzy for the 5-year LTS window and note the trade-off
  explicitly. The Zenoh router is **required by default** (multicast discovery is disabled in the
  stock session config), which is itself a teaching point.

---

## 3. Final directory tree

Repo root = the working directory **`/Users/tinhn/Documents/ros2`** (currently empty). I will
`git init` here as the first step. (If you'd rather nest it under `ros2-explained/`, say so.)

```
ros2-explained/                 # = repo root (/Users/tinhn/Documents/ros2)
├── README.md                   # "Why ROS 2" narrative, ROS1-vs-2 table, arch diagram, quickstart, 5-min demo script
├── PLAN.md                     # this file
├── VERSIONS.lock               # captured at build: base-image digest + resolved apt/pip/image versions (REAL)
├── Makefile                    # single entrypoint: build / demo-1..4 / slides / test / clean / shell
├── .gitignore
├── .dockerignore
├── docker/
│   ├── Dockerfile              # FROM ros@sha256:<digest>; +3 RMWs +micro_ros_setup deps +tmux/socat/can-utils/xvfb/graphviz
│   ├── docker-compose.yml      # services: ws, zenoh-router, micro-ros-agent (+ shared bridge net)
│   └── zenoh/
│       └── session_connect.json5   # rmw_zenoh session config pointing nodes at the zenoh-router service
├── ws/                         # ROS 2 colcon workspace (built inside the image)
│   └── src/
│       ├── demo_basic/         # Demo 1: rclpy talker/listener, AddTwoInts svc, Fibonacci action + 1 rclcpp talker
│       │   ├── demo_basic/                (rclpy nodes)
│       │   ├── src/                        (rclcpp talker.cpp)
│       │   ├── launch/                     (single-container launch: brings up the whole graph)
│       │   ├── package.xml  CMakeLists.txt / setup.py
│       ├── demo_qos/           # Demo 3: configurable pub/sub (reliability/durability/depth via args)
│       └── demo_microros/      # Demo 4: agent launch scripts + transport configs (client is built from micro_ros_setup)
│           # Note: Demo 2 reuses demo_basic's talker/listener — no separate package.
├── docs/
│   ├── 01-architecture.md      # app → rclcpp/rclpy → rcl → rmw → DDS/Zenoh → OS/net (Mermaid layered diagram)
│   ├── 02-dds-rtps.md          # DCPS, global data space, RTPS, HEARTBEAT/ACKNACK ~ ARQ/sliding-window
│   ├── 03-qos.md               # 6+1 policies, RxO rule, AUTO-GENERATED results table, real `topic info -v`
│   ├── 04-discovery.md         # SPDP/SEDP (Mermaid sequence), multicast issue, Discovery Server, Domain ID
│   ├── 05-zenoh.md             # why Zenoh, rmw_zenoh, liveliness tokens, router, Kilted-vs-Jazzy trade-off
│   ├── 06-microros.md          # DDS-XRCE, Client↔Agent (Mermaid), rclc executor, footprint, Zephyr appendix
│   └── img/                    # generated node-graph artifacts (text + PNG/SVG if produced)
├── slides/
│   └── slides.md               # Marp deck (10–15 slides), one "what you'll see + run command" slide per demo
└── scripts/
    ├── lib.sh                  # shared bash helpers (logging, in-container exec, wait-for)
    ├── run_in_container.sh     # docker compose run wrapper used by the Makefile
    ├── capture_versions.sh     # writes VERSIONS.lock (digests + resolved versions) — real data
    ├── verify_basic.sh         # Demo 1 acceptance
    ├── verify_middleware.sh    # Demo 2 acceptance
    ├── verify_qos.sh           # Demo 3 acceptance (+ generates the results table)
    ├── verify_microros.sh      # Demo 4 acceptance (UDP + serial)
    └── verify_microros_can.sh  # Demo 4 CAN FD — Linux-only, self-skips on macOS with a clear message
```

---

## 4. Pinned versions (the lockfile strategy)

I will **not invent digests in this doc** (that would be fabricated output). Instead `make build`
runs `scripts/capture_versions.sh`, which pulls each tag, records its immutable `sha256` digest
and resolved package versions, and writes `VERSIONS.lock` (committed). The Dockerfile then pins
`FROM ros@sha256:<digest>`.

| Component | Tag we resolve & pin | Approx version (verified) | How pinned |
|---|---|---|---|
| Base image | `ros:jazzy-ros-base-noble` | Jazzy / Ubuntu 24.04 | `FROM ros@sha256:<digest>` |
| Fast DDS RMW | bundled in `ros-base` | `rmw_fastrtps_cpp ~8.4.4` | apt `pkg=version` |
| Cyclone DDS RMW | `ros-jazzy-rmw-cyclonedds-cpp` | `~2.2.3` | apt `pkg=version` |
| Zenoh RMW + router | `ros-jazzy-rmw-zenoh-cpp` | `~0.2.9` | apt `pkg=version` |
| micro-ROS setup | `micro_ros_setup` git branch | `jazzy` | `git clone -b jazzy` (pinned commit recorded) |
| micro-ROS Agent | `microros/micro-ros-agent:jazzy` | jazzy | `@sha256:<digest>` (from-source fallback) |
| Slides | `marpteam/marp-cli:v4.4.0` | `4.4.0` | `@sha256:<digest>` |
| Headless graph (opt.) | `ros2-graph` (pip) / `graphviz` (apt) | pinned in build | `pip ==`, apt `pkg=version` |

> Reproducibility caveat documented in README: apt/pip archives prune old versions over time, so
> the **base-image digest is the primary reproducibility anchor**; `VERSIONS.lock` records the rest.

---

## 5. Docker design (compose services + networking)

- **`make build`** → `docker compose build` the image + `colcon build` the workspace inside it +
  build the micro-ROS host client + write `VERSIONS.lock`.
- **Single user-defined bridge network** (`ros2net`). **No `network_mode: host`** (see §1).
- **Services in `docker/docker-compose.yml`:**
  - **`ws`** — main workspace container. Demos 1 & 3 run their *entire* node graph here (one
    container → reliable discovery). Demo 2 also runs its talker/listener pairs here.
  - **`zenoh-router`** — runs `ros2 run rmw_zenoh_cpp rmw_zenohd` on `ros2net`. Demo 2's Zenoh leg
    and any Zenoh node connect to it via TCP (`zenoh-router:7447`) using
    `docker/zenoh/session_connect.json5` (`ZENOH_SESSION_CONFIG_URI`). TCP unicast works fine on
    Docker Desktop — this is exactly why Zenoh sidesteps the multicast problem.
  - **`micro-ros-agent`** — Demo 4's Agent (`microros/micro-ros-agent@sha256:...`). For **serial**,
    the agent + socat + client run in **one container** (PTYs are namespace-local). For **UDP**,
    agent and client share `ros2net`.
- Each `make demo-N` does a `docker compose run` of **exactly** the services it needs.

---

## 6. The four demos

### Demo 1 — pub/sub + service + action (`make demo-1`)
- **Nodes:** rclpy `talker`/`listener` (`std_msgs/String`); a **second talker in rclcpp** for the
  C++ audience; `AddTwoInts` service server+client; a **Fibonacci action** with feedback + cancel.
- **How it runs (macOS-safe):** one `ros2 launch` inside the `ws` container brings up the whole
  graph; CLI checks run in the same container.
- **CLI shown:** `ros2 topic echo`, `ros2 service call`, `ros2 action send_goal --feedback`.
- **Node graph artifact:** guaranteed **text** capture (`ros2 node list` / `ros2 node info` /
  `ros2 topic info`) into `docs/img/` **plus** a hand-written Mermaid graph in `docs/01`. *Bonus:*
  attempt a real PNG via `xvfb-run -a rqt_graph` (or `ros2-graph` headless) — if flaky in
  automation, the text artifact satisfies acceptance and I'll say so honestly.
- **Verify (`verify_basic.sh`):** listener received ≥1 msg; service returned `5` for `2+3`;
  action returned a result **with ≥1 feedback**; a node-graph file exists in `docs/img/`.
- **Aha moment:** separate processes discover each other automatically — **no master**.

### Demo 2 — middleware swap (`make demo-2`)
- Reuses Demo 1's talker/listener. A script loops over `rmw_fastrtps_cpp`,
  `rmw_cyclonedds_cpp`, `rmw_zenoh_cpp`: sets `RMW_IMPLEMENTATION`, **`ros2 daemon stop`**
  (explains *why*: the daemon caches the RMW from first launch), prints the **active RMW** via
  `ros2 doctor --report | grep -i middleware`, runs the pair, confirms data flows.
- **Zenoh leg:** auto-starts the `zenoh-router` service and connects nodes to it.
- **Required teaching moment:** Fast DDS talker ↔ Cyclone DDS listener **interoperate** (same
  DDSI-RTPS wire protocol); Fast DDS talker ↔ Zenoh listener → **no data** (different wire
  protocol, needs a bridge) → "must be the same RMW family."
- **Bonus:** `ROS_DOMAIN_ID` isolation mini-demo (same RMW, mismatched domain → silence).
- **Verify (`verify_middleware.sh`):** runs under all 3 RMWs, each prints the correct active RMW
  and confirms flow; demonstrates the DDS↔Zenoh non-interop (0 msgs) case.

### Demo 3 — QoS compatibility ⭐ (`make demo-3`)
- One configurable `qos_pub` + `qos_sub` (reliability / durability / depth via ROS args). A
  matrix runner logs **real** messages-received-in-N-seconds per combo and **auto-generates a
  Markdown table** into `docs/03-qos.md`.
- **Cases (RxO rule, offered ≥ requested):**
  - best_effort pub + reliable sub → **0 msgs** (NO match)
  - reliable pub + best_effort sub → match
  - volatile pub + transient_local sub → NO match
  - transient_local pub + sub, **late joiner** → receives old samples
- **Diagnostic tool taught:** real `ros2 topic info <topic> -v` output (per-endpoint QoS) embedded
  in the doc.
- **Verify (`verify_qos.sh`):** matrix completes & table generated; best_effort→reliable yields
  **exactly 0**; valid case ≥1; late-joiner transient_local receives old samples; real `-v` output
  captured.
- **Aha moment:** the topic still shows in `ros2 topic list`, but data is silently dropped on the
  incompatible path.

### Demo 4 — micro-ROS + DDS-XRCE (`make demo-4`)
- **No real MCU** (stated plainly): the "MCU" is a software **micro-ROS host client** built via
  `micro_ros_setup` (`create_firmware_ws.sh host` + `build_firmware.sh` → `micro_ros_demos_rclc`,
  e.g. `ping_pong`). The **Agent bridges it into DDS**, so it appears as an ordinary ROS 2 node.
- **Transports (guaranteed-run → closest-to-hardware):**
  1. **UDP** (baseline, runs everywhere): `micro_ros_agent udp4 -p 8888`.
  2. **SERIAL/UART** (main embedded demo): `socat` PTY pair simulates the UART; agent
     `serial --dev /dev/pts/N`; client on the other end. **Client + agent + socat run in one
     container** (PTYs are namespace-local).
  3. **CAN FD** (**Linux-only, skippable**): `vcan0` + `canfd --dev vcan0`, observe with
     `candump`. `verify_microros_can.sh` **self-skips on macOS** with a clear message.
- **Important constraint discovered:** the micro-ROS client's transport is **compile-time**
  (`RMW_UXRCE_TRANSPORT`), not a runtime flag → switching UDP↔serial means a rebuild. The plan
  builds both client variants (or rebuilds per leg) and documents this honestly.
- **Verify (`verify_microros.sh`):** UDP **and** serial bring the simulated client up; it shows in
  `ros2 node list` and publishes a topic a host-side `ros2 topic echo` receives.
- **`docs/06`:** Client–Agent model, **rclc executor** (static / fixed-order / non-preemptive /
  LET / sense-plan-act), footprint **"< 75 KB Flash, ~3 KB RAM for a pub+sub app"** (cited:
  micro.ros.org Micro XRCE-DDS), and a **hardware-only Zephyr/Cortex-M appendix** (not run in CI).
- **Aha moment:** a (simulated) MCU appears as a normal ROS 2 node; the Agent is the bridge.

---

## 7. Present layer (docs + slides)

- **README.md:** "why ROS 2" distributed-systems narrative → **ROS 1 vs ROS 2 table** (no master,
  QoS, real-time, security, multi-OS) → **Mermaid layered architecture** → **Quick start**
  (`make build`, `make demo-1`, `make slides`) → **"5-minute demo script"** walking a live talk
  through demos 1→4.
- **docs/** one concept per file (tree above), each with **Mermaid** (layered arch; SPDP/SEDP
  discovery sequence; QoS RxO matrix; micro-ROS Client–Agent–DDS). Embedded analogies for embedded
  folks (discovery ≈ endpoint enumeration; RTPS HEARTBEAT/ACKNACK ≈ ARQ / sliding-window).
- **slides/slides.md (Marp):** built via `marpteam/marp-cli:v4.4.0` in Docker → `slides.html`
  **and** `slides.pdf`. **Marp chosen over reveal.js** (one-shot static build vs. running a web
  server). **Note:** Marp does **not** render Mermaid natively → slide diagrams are either simple
  Marp-native or pre-rendered to SVG/PNG; the `mermaid` source stays in `docs/` where GitHub
  renders it live.
- **Honest caveats included in docs:** vendor benchmark figures are self-published (no single
  "best DDS"); "real-time" is potential, not automatic (depends on OS/scheduler/executor; default
  rclcpp executor isn't always deterministic → why micro-ROS uses rclc); the micro-ROS demo is a
  software simulation.

---

## 8. Order of work (each step ends with a real, verified run)

0. **Scaffold + image** — repo skeleton, `.gitignore`/`.dockerignore`, `Makefile` (build/shell),
   `Dockerfile`, `docker-compose.yml`, `capture_versions.sh`. ✅ when `make build` succeeds and
   `VERSIONS.lock` is written with real digests.
1. **Demo 1** → run for real → `verify_basic.sh` green → capture output → write `docs/01`, `02`,
   README quickstart. **I pause and report.**
2. **Demo 2** → run all 3 RMWs + non-interop → verify → write `docs/04`, `05`.
3. **Demo 3** → run matrix → verify → auto-generate QoS table + capture `topic info -v` → `docs/03`.
4. **Demo 4** → UDP + serial → verify (CAN gated/skipped on this Mac) → write `docs/06`.
5. **Slides** → `make slides` builds HTML+PDF in Docker.
6. **Finalize** → README narrative + ROS1-vs-2 table + 5-min script; `make test` aggregates all
   verify scripts; final "no fake output / Mermaid renders" pass.

---

## 9. Acceptance criteria → where each is met

| Criterion | Met by |
|---|---|
| `make build` succeeds, versions pinned | §4, step 0, `VERSIONS.lock` |
| Demo 1: ≥1 msg, correct service, action result + ≥1 feedback, node-graph file | `verify_basic.sh`, `docs/img/` |
| Demo 2: 3 RMWs, prints active RMW, data flows, DDS↔Zenoh non-interop | `verify_middleware.sh` |
| Demo 3: matrix table, 0-msg case exact, valid ≥1, late-joiner old samples, real `-v` | `verify_qos.sh`, `docs/03` |
| Demo 4: UDP + serial run, client in `ros2 node list`, host echo receives; CAN Linux-only | `verify_microros*.sh` |
| `make slides` builds with nothing on host | §7, Marp in Docker |
| Docs render on GitHub, Mermaid works, no fake output | step 6, lockfile + real captures |

---

## 10. Resolved decisions (confirmed by you)

1. **Repo location:** build directly in **`/Users/tinhn/Documents/ros2`** (repo root = this dir).
2. **CAN FD:** ship as a **documented, Linux-only, self-skipping** demo; **UDP + serial are fully
   verified on this Mac**. (No separate Linux verification requested.)
3. **Distro:** **Jazzy LTS** (EOL May 2029), Zenoh as a binary add-on, trade-off documented in
   `docs/05`.

**Next step (awaiting your go-ahead):** step 0 (scaffold + image, `make build`, `VERSIONS.lock`)
then Demo 1, after which I pause and report with the real verified output.
