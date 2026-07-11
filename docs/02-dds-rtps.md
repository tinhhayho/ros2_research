# 02 — DDS and the RTPS wire protocol

The default ROS 2 middleware is **DDS** (Data Distribution Service). Two pieces matter:

- **DCPS** — the *data-centric publish/subscribe* model: publishers and subscribers meet on a
  named **Topic** in a **global data space**, identified by topic name + data type. Nobody
  addresses anybody directly; you publish *to a topic*, not *to a node*.
- **RTPS / DDSI-RTPS** — the *wire protocol* DDS vendors speak. This is why **Fast DDS and
  Cyclone DDS interoperate** (Demo 3 proved it: 8 msgs across vendors) — they share this
  protocol. Zenoh does **not** speak RTPS, so it does **not** interoperate on the wire.

## Reliability ≈ ARQ (the part firmware folks already know)

RTPS runs over **unreliable UDP**, yet ROS 2's `RELIABLE` QoS guarantees delivery. It does this
with an ARQ / sliding-window scheme that maps directly onto serial/CAN reliability:

```mermaid
sequenceDiagram
    participant P as Publisher (Writer)
    participant S as Subscriber (Reader)
    P->>S: DATA seq=1
    P->>S: DATA seq=2  (lost on the wire)
    P->>S: DATA seq=3
    P->>S: HEARTBEAT (I have 1..3 — what do you have?)
    S->>P: ACKNACK (got 1 and 3; NACK 2)
    P->>S: DATA seq=2  (retransmit)
    S->>P: ACKNACK (got 1..3)
```

| RTPS | Firmware equivalent |
|---|---|
| `DATA` with sequence numbers | Numbered frames in a sliding window |
| `HEARTBEAT` | "Here's my window" poll |
| `ACKNACK` | Selective ACK / NACK |
| Retransmit on NACK | ARQ retry |
| `BEST_EFFORT` QoS | Fire-and-forget (raw UDP / unacked frame) |

So **`RELIABLE` is not magic** — it is acknowledged, retried delivery layered on UDP, paid for
in latency and memory. `BEST_EFFORT` skips all of it. You choose per stream, and **both ends
must agree** — which is the whole subject of [03-qos](03-qos.md).

## Honest caveats
- "DDS is real-time" is a *potential*, not a guarantee — it depends on OS scheduler, executor,
  and configuration (this is exactly why micro-ROS uses the deterministic `rclc` executor; see
  [06](06-microros-appendix.md)).
- Vendor benchmarks are self-published; there is no single "fastest DDS." Pick on Tier/support
  and features, not marketing graphs.
