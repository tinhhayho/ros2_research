# 04 — Discovery and isolation (no master)

ROS 2 has **no `roscore`**. Nodes find each other through **distributed discovery**, and you
partition systems with `ROS_DOMAIN_ID`. Demo 1 shows it (5 separate processes form a graph with
nothing central); Demo 3 shows the isolation knob (domain 42 ✗ domain 99 → 0 messages).

## SPDP → SEDP (the two-phase handshake)

The default DDS RMWs use a two-stage simple-discovery protocol over **UDP multicast**:

```mermaid
sequenceDiagram
    participant A as Node A (new)
    participant B as Node B (already up)
    Note over A,B: SPDP — Simple Participant Discovery (UDP multicast)
    A->>B: "participant A here" (announce)
    B->>A: "participant B here" (announce)
    Note over A,B: SEDP — Simple Endpoint Discovery (now unicast)
    A->>B: my writers/readers + their topics, types, QoS
    B->>A: my writers/readers + their topics, types, QoS
    Note over A,B: QoS checked (RxO). Compatible endpoints connect; data flows.
```

**Firmware analogy:** SPDP is **bus endpoint enumeration** — devices announce themselves on a
shared medium; no controller hands out addresses. SEDP is the capability exchange that follows.

## Multicast works here — because this is Linux + host networking

On this native Linux Docker host with `network_mode: host`, discovery behaves exactly like
native ROS 2. What the three demos actually exercise is **multi-process discovery inside one
`ws` container**; separate containers would discover each other the same way with these
compose defaults (host network + shared IPC), but demo-1/2/3 do not exercise that path. The
classic "Docker drops multicast between containers" failure is specific to **bridge**
networks; host networking is the Linux fix.

| Setup | Multicast discovery | Used here? |
|---|---|---|
| `network_mode: host` (Linux) | ✅ works natively | **default** |
| user-defined bridge | ❌ multicast dropped → need Discovery Server / static peers | optional contrast only |

> `ipc: host` is also set, so Fast DDS's **shared-memory transport** works across containers
> (they share `/dev/shm`). Without it, two "same host" containers silently fall back / fail SHM.

## Isolation: `ROS_DOMAIN_ID`

The domain ID is the lightweight, canonical isolation knob — same domain → discover; different
domain → **fully isolated, no discovery** (Demo 3 Part C: domain 42 talker + domain 99 listener
= 0 msgs). It works identically under host networking, so it — not container walls — is how we
keep concurrent demos from cross-talking.

**Zenoh is different:** `rmw_zenoh` disables multicast scouting by default *by design*; nodes
discover through the `rmw_zenohd` **router** (gossip scouting). Demo 3 starts that router before
any Zenoh node — a real middleware behavior difference, not a Docker workaround. See
[05-rmw](05-rmw.md).
