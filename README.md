# ros2-explained

A self-contained repo that **explains** (slides + concept docs) and **demonstrates** (three
focused, live Docker demos) the architecture and middleware layer of **ROS 2**, written for
**embedded / firmware engineers new to robotics**.

The host needs **only Docker + the compose plugin** — no ROS 2 install, not even `make`.
Everything runs in a pinned container; every number in the docs is captured from a **real run**.

```bash
./run.sh build      # build the image (digest-pinned) + the workspace; writes VERSIONS.lock
./run.sh demo-1     # pub/sub + service + action  (Python & C++ on one graph, no master)
./run.sh demo-2     # QoS compatibility matrix     -> docs/03-qos.md
./run.sh demo-3     # RMW swap + interop + domain isolation -> docs/05-rmw.md
./run.sh viz        # turtlesim: drive a turtle in a GUI window (great visual opener)
./run.sh rqt        # open the live node/topic graph (rqt_graph)
./run.sh test       # run all three acceptance checks
./run.sh slides     # build slides/slides.html (the deliverable, with inline diagrams)
```
(`make <target>` works too, if you have make.)

> **Visual demos need a desktop (X server).** On this Linux host they forward the GUI from the
> container to your screen via the X11 socket; `run.sh` calls `xhost +local:` for you. If no
> window appears, run `xhost +local:` once in a terminal. (turtle renders in software — fine.)

## Why ROS 2 (the 60-second pitch)

ROS 2 is middleware for building distributed systems out of small processes (**nodes**) that
talk over named **topics**, **services**, and **actions**. Its defining trait: **no central
master**. Nodes discover each other peer-to-peer, and the transport underneath is a **swappable
HAL** — you can change the entire networking stack with one environment variable.

## ROS 1 vs ROS 2 (what changed, and why an embedded team cares)

| | ROS 1 | ROS 2 |
|---|---|---|
| Discovery | central `roscore` master | **distributed**, no master (DDS/Zenoh) |
| Transport | custom TCPROS/UDPROS | **DDS (RTPS)** or Zenoh, pluggable via `rmw` |
| QoS | essentially TCP-reliable only | **rich QoS** (reliability, durability, deadline, …) |
| Real-time / small targets | not designed for it | **micro-ROS** for MCUs; deterministic `rclc` executor |
| Multi-vendor | n/a | swap Fast DDS / Cyclone / Zenoh, no recompile |

For firmware engineers the mental model is familiar: **topics ≈ broadcast frames**, **services
≈ register read/write transactions**, **actions ≈ long DMA/motor moves with progress + cancel**,
**QoS ≈ bus reliability/timing trade-offs**, **RMW ≈ a swappable transport/HAL**.

## The three demos (all verified on this machine)

1. **Demo 1 — pub/sub + service + action.** A Python talker *and* a C++ talker publish `/chatter`;
   one listener hears both; `AddTwoInts(2,3)=5`; a Fibonacci action streams feedback then returns
   a result. Five separate processes form a graph with **no master**.
2. **Demo 2 — QoS compatibility.** A live matrix proves the Request-vs-Offered rule:
   `best_effort→reliable = 0 msgs`, `reliable→best_effort = match`, durability mismatch = 0, and
   `transient_local` latching for late joiners. Auto-generates [`docs/03-qos.md`](docs/03-qos.md).
3. **Demo 3 — RMW / middleware swap.** The *same binaries* run over Fast DDS, Cyclone DDS, and
   Zenoh by flipping `RMW_IMPLEMENTATION`. Shows **Fast DDS↔Cyclone interop** (shared RTPS wire),
   **Fast DDS↔Zenoh non-interop** (different wire), and **`ROS_DOMAIN_ID` isolation**.
   Auto-generates [`docs/05-rmw.md`](docs/05-rmw.md).

## Concept docs
- [01 — architecture (the layer cake)](docs/01-architecture.md)
- [02 — DDS & RTPS (reliability ≈ ARQ)](docs/02-dds-rtps.md)
- [03 — QoS compatibility](docs/03-qos.md) *(auto-generated)*
- [04 — discovery & isolation (no master)](docs/04-discovery.md)
- [05 — RMW / middleware swap](docs/05-rmw.md) *(auto-generated)*
- [06 — micro-ROS on MCUs (appendix)](docs/06-microros-appendix.md)

## 5-minute live demo script
0. **Opener — `./run.sh viz`** — a turtle appears in a window; drive it with the arrow keys. In a
   second terminal `./run.sh rqt` shows the live graph: `teleop → /turtle1/cmd_vel → turtlesim →
   /turtle1/pose`. Now the abstract words (nodes, topics) are something the room can *see move*.
1. `./run.sh demo-1` — point out the Python **and** C++ talker on one topic, and that 5 separate
   OS processes found each other with **no master**. Show `2+3=5` and the action feedback stream.
2. `./run.sh demo-2` — open `docs/03-qos.md`: a `best_effort` sensor publisher delivers **nothing**
   to a `reliable` subscriber — and the RMW *logs a warning*, it is not silent.
3. `./run.sh demo-3` — the same nodes run over three middlewares; DDS vendors interoperate, Zenoh
   does not (different wire protocol), and a domain-ID change isolates everything.

See [`runbook/live-demo-runbook.md`](runbook/live-demo-runbook.md) for the exact on-stage commands
and real expected output.

## Reproducibility
ROS distro **Jazzy Jalisco (LTS, EOL 2029)**. The base image is pinned by **sha256 digest** in
[`VERSIONS.lock`](VERSIONS.lock) (the primary anchor); resolved package versions are recorded
there too. Regenerate with `./run.sh build`. No `:latest`, no hand-written version numbers.
