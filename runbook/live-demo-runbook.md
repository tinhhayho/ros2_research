# Live demo runbook

A tight, on-stage script. Each step lists the **exact command** and the **real expected output**
(captured from actual runs on this machine — see `docs/img/`). Total live time ≈ 8–10 min.

> **Before the meeting:** `./run.sh build` once (pulls the image, ~1 GB; compiles the workspace).
> Then `./run.sh test` to confirm all three demos are green. Have `docs/03-qos.md`,
> `docs/05-rmw.md`, and `slides/slides.html` open in tabs.

---

## 0. One-liner sanity check (optional, before you present)
```bash
./run.sh test          # runs all three acceptance scripts; expect "all verify scripts passed."
```

## Opener — turtlesim, something they can see  (~2 min)
```bash
./run.sh viz           # a turtle window opens; drive it with the ARROW KEYS (click the terminal first)
```
While driving, in a **second terminal**:
```bash
./run.sh rqt           # live node/topic graph window
```
Say: "Two separate programs — `/teleop_turtle` sends `/turtle1/cmd_vel` (a Topic), `/turtlesim`
sends back `/turtle1/pose`, and `/spawn` `/clear` are Services. No master wired them together."
This makes the abstract words concrete before the terminal-only demos. (Turtle renders in
software — that's expected. If no window appears, run `xhost +local:` once.)

## 1. Demo 1 — pub/sub + service + action  (~3 min)
```bash
./run.sh demo-1
```
Talking points while it runs:
- A **Python** talker and a **C++** talker both publish `/chatter`; the listener hears both.
- Five separate OS processes, **no master**.

Expected (real) highlights:
```
node list:  /add_two_ints_server  /fibonacci_action_server  /listener  /talker  /talker_cpp
/chatter:   "Hello from C++ (rclcpp): 9"        # C++ and Python on one topic
service:    example_interfaces.srv.AddTwoInts_Response(sum=5)
action:     Feedback: sequence: [0,1,1] -> [0,1,1,2] -> ...   then a Result + SUCCEEDED
```
Acceptance prints a row of `PASS` ending in `Demo 1 acceptance PASSED`.

## 2. Demo 2 — QoS compatibility  (~3 min)
```bash
./run.sh demo-2 && sed -n '1,40p' docs/03-qos.md
```
Talking points:
- A `best_effort` sensor publisher delivers **nothing** to a `reliable` subscriber.
- It is **not silent** — the RMW logs an incompatible-QoS warning.

Expected (real) results table:
```
best_effort -> reliable           : 0    (incompatible)
reliable    -> best_effort        : 20   (compatible)
volatile    -> transient_local    : 0    (incompatible)
late transient_local sub          : got old sample first (qos msg 7)
late volatile sub                 : got new only (qos msg 26)
```

## 3. Demo 3 — RMW swap + interop + isolation  (~3 min)
```bash
./run.sh demo-3 && sed -n '1,60p' docs/05-rmw.md
```
Talking points:
- Same node binaries over three middlewares — one env var, no recompile.
- DDS vendors interoperate; Zenoh uses a different wire protocol; domain IDs isolate.

Expected (real) results:
```
fastrtps / cyclonedds / zenoh   : 8 / 8 / 8   (all flow)
Fast DDS  -> Cyclone DDS         : 8           (interop, shared RTPS wire)
Fast DDS  -> Zenoh               : 0           (no interop, different wire)
domain 42 -> domain 99           : 0           (ROS_DOMAIN_ID isolation)
```

---

## If something looks slow or empty ("panic" section)
- **Discovery looks slow / a node is missing from `ros2 node list`.** It's the ros2 daemon
  cache racing. Wait a few seconds; the demo scripts already poll for the full graph.
- **Switching RMW shows the wrong/old middleware.** Run `ros2 daemon stop` (the daemon caches
  the RMW from first launch) — the demo script does this automatically.
- **Zenoh leg shows 0 between Zenoh nodes.** The `rmw_zenohd` router must be up *before* Zenoh
  nodes (multicast scouting is off by default); `demo3_run.sh` starts it first.
- **Permission denied on the Docker socket.** You're not in the `docker` group. Either
  `sudo usermod -aG docker $USER` (then re-login) or, for one session,
  `sudo setfacl -m u:$USER:rw /var/run/docker.sock`.
- **Files in `docs/`/`ws/` owned by root** (the container runs as root). Harmless for git; to
  reclaim: `docker compose -f docker/docker-compose.yml run --rm -T ws chown -R $(id -u):$(id -g) /repo`.
