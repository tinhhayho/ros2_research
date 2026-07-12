---
marp: true
paginate: true
theme: default
style: |
  section { font-size: 27px; }
  h1 { color: #1b2b4a; }
  h2 { color: #2E5FAC; }
  table { font-size: 24px; }
  code { background: #eef2f8; }
  section.lead h1 { font-size: 52px; }
  section.lead h2 { color: #5b7bb0; font-weight: 500; }
  section.diagram { display: flex; align-items: center; justify-content: center; padding: 14px; }
  section.diagram img { height: 650px; width: auto; max-width: 100%; }
  .cmd { display:inline-block; background:#11233f; color:#e8eefc; padding:8px 16px;
         border-radius:8px; font-family:monospace; font-size:24px; margin:4px 0; }
---

<!-- _class: lead -->

# ROS 2 for embedded engineers
## see it · run it · swap it

A hands-on intro: three live demos + a turtle you can drive.
Everything runs in Docker — **every number on these slides is from a real run.**

---

## Why ROS 2?

- Build systems from small processes (**nodes**) that talk over a network
- **No central master** — nodes find each other peer-to-peer
- Rich **QoS** (reliability, durability, …) you tune per data stream
- The transport is a **swappable HAL** — change the whole network stack with one env var
- Scales down to microcontrollers via **micro-ROS**

> Firmware mental model: **topics ≈ broadcast frames**, **services ≈ register read/write**,
> **actions ≈ a DMA/motor move** with progress + cancel.

---

## ROS 1 vs ROS 2

| | ROS 1 | ROS 2 |
|---|---|---|
| Discovery | central `roscore` | **distributed, no master** |
| Transport | custom TCPROS | **DDS (RTPS)** / Zenoh, pluggable |
| QoS | basically reliable-only | **rich, per-stream QoS** |
| Small targets | not designed for it | **micro-ROS** on MCUs |
| Multi-vendor | — | swap Fast DDS / Cyclone / Zenoh |

---

<!-- _class: diagram -->

{{diagram:arch-layers}}

---

<!-- _class: diagram -->

{{diagram:discovery}}

---

<!-- _class: diagram -->

{{diagram:comms-patterns}}

---

## Demo 1 — pub/sub + service + action

<span class="cmd">./run.sh demo-1</span>

What you'll see (all real):
- A **Python** talker *and* a **C++** talker on the same `/chatter` — one listener hears both
- Service: `AddTwoInts(2, 3)` → **`sum=5`**
- Action: Fibonacci streams **feedback** `[0,1,1] → [0,1,1,2] → …`, then a result
- `ros2 node list` shows **5 separate processes** that found each other with **no master**

---

<!-- _class: diagram -->

{{diagram:qos-rxo}}

---

## Demo 2 — QoS, real results

<span class="cmd">./run.sh demo-2</span> → writes `docs/03-qos.md`

| Publisher offers | Subscriber requests | Msgs |
|---|---|---|
| best_effort | reliable | **0** ❌ |
| reliable | best_effort | **20** ✅ |
| reliable / volatile | reliable / transient_local | **0** ❌ |

A `best_effort` sensor publisher delivers **nothing** to a `reliable` subscriber — and the RMW
**logs a warning**, it is *not* silent.

---

<!-- _class: diagram -->

{{diagram:rtps-arq}}

---

<!-- _class: diagram -->

{{diagram:rmw-swap}}

---

## Demo 3 — swap + interop, real results

<span class="cmd">./run.sh demo-3</span> → writes `docs/05-rmw.md`

| Talker | Listener | Msgs | |
|---|---|---|---|
| Fast DDS / Cyclone / Zenoh | same RMW on both sides | **8 / 8 / 8** | each same-RMW pair flows |
| Fast DDS | Cyclone | **8** | ✅ shared RTPS wire |
| Fast DDS | Zenoh | **0** | ❌ different wire |
| domain 42 | domain 99 | **0** | ✅ `ROS_DOMAIN_ID` isolation |

---

<!-- _class: diagram -->

{{diagram:turtlesim-graph}}

---

## Run the visual demos live

<span class="cmd">./run.sh viz</span> — turtlesim window; **drive the turtle with the arrow keys**

<span class="cmd">./run.sh rqt</span> — live node/topic graph (rqt_graph)

<span class="cmd">./run.sh demo-1</span> — then run `./run.sh rqt` in a second terminal to watch the graph

> `viz` makes topics (`/turtle1/cmd_vel`, `/turtle1/pose`) and services (`/spawn`, `/clear`)
> **visible** — the same concepts from Demo 1, but you can watch them move.

---

<!-- _class: diagram -->

{{diagram:microros}}

---

## Takeaways

1. ROS 2 = distributed nodes, **no master**, rich QoS
2. **Topics / services / actions** = stream / RPC / long task
3. **QoS must agree on both ends** — and it warns you when it doesn't
4. The **RMW is a HAL** — swap Fast DDS / Cyclone / Zenoh with one env var
5. **micro-ROS** takes the same model down to an MCU

Try it now: <span class="cmd">./run.sh build && ./run.sh demo-1 && ./run.sh viz</span>
