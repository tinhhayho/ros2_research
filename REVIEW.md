# Full-repo review — 2026-07-08

**How this review was produced:** four independent review passes, each with a narrow
scope — (A) `ws/src` ROS 2 code, (B) Docker/scripts/run.sh infra, (C) docs/runbook/README/
plans, (D) slides + SVG diagrams. Findings were merged, de-duplicated, and **every MAJOR
finding was independently re-verified** against the files before writing this document.

**Verdict:** the repo is in genuinely good shape — every headline number (QoS 0/20/0,
RMW 8/8/8, sum=5, 5 nodes) traces back to captured real-run output, and the firmware-analogy
thread is consistent from README → docs → diagrams → deck. The problems found are
(1) one teaching-critical table on the slides, (2) stale plan files that misrepresent the
repo's state, (3) two gaps in the reproducibility/entrypoint story, and a tail of minor
packaging/docs polish.

---

## MAJOR — fix before the next presentation

1. **`slides/deck.md` Demo 3 table contradicts itself** (verified).
   Row 1 reads `Talker: Fast DDS → Listener: Fast DDS / Cyclone / Zenoh = 8/8/8 (all flow)`,
   which literally claims a Fast DDS talker delivers to a Zenoh listener — while row 3 of the
   same table says `Fast DDS → Zenoh = 0 (different wire)`. The 8/8/8 figures are actually
   three *same-RMW* legs (fastrtps↔fastrtps, cyclone↔cyclone, zenoh↔zenoh — see
   `docs/05-rmw.md`). This confuses the exact concept the slide teaches. Fix: row 1's Talker
   cell must read `Fast DDS / Cyclone / Zenoh` (paired with the listener column).

2. **`REVISED-PLAN.md` misidentifies itself and denies the repo exists** (verified).
   Its H1 says `# PLAN.md`, its status block says *"Plan only. No code written yet"*, its tree
   lists `PLAN.md  # this file`, and it ends with *"Next step (awaiting go-ahead)"* — yet the
   repo has fully built, verified code. Its package layout also drifted (describes the C++
   talker inside `demo_basic`; reality is a separate `demo_basic_cpp` package; the
   `demo1_run.sh`/`qos_run.sh`/`demo3_run.sh`/`build_slides.py` scripts are absent from its
   tree). Neither README nor either plan says which document is authoritative. Fix: retitle,
   add a status banner to both plans ("historical — see README for reality"), link from README.

3. **Digest pinning is bypassed by every target except `build`** (verified, `run.sh`).
   Only `build()` sources `docker/image.env` (which is gitignored, so absent on a fresh
   clone). `demo-1/2/3`, `viz`, `rqt`, `shell`, `test` call compose directly, and
   `docker-compose.yml` falls back to the mutable `ros:jazzy-ros-base-noble` tag — so a fresh
   clone running `./run.sh demo-1` first silently builds an **unpinned** image, defeating the
   VERSIONS.lock guarantee with no warning. Fix: source `image.env` (or fail with "run
   ./run.sh build first") at the top of `run.sh`, not inside `build()` only.

4. **`Makefile` is missing `viz` and `rqt`** (verified) while README says
   "`make <target>` works too". `make viz` → *No rule to make target*. Fix: add both to the
   `.PHONY`/target lists.

## MINOR

**Slides / deck**
- `slides/slides.html` contains **6 live CDN references** (`cdn.jsdelivr.net` twemoji for the
  ✅/❌ glyphs Marp substitutes) — verified. Offline on stage, the pass/fail icons in the two
  results tables become broken images, and the "fully self-contained" claim is false. Fix:
  replace ✅/❌ in deck.md tables with plain text (`ok` / `X`) or styled spans.
- `transient_local` appears exactly once (Demo 2 table) with no definition, and the `qos-rxo`
  diagram illustrates only the reliability case — row 3's `0 ❌` is unexplained on-slide.
- Deck text mentions services `/spawn`, `/clear` while `turtlesim-graph.svg` also shows
  `/set_pen` (text/diagram out of sync; diagram is correct).

**Infra / reproducibility**
- `capture_versions.sh` re-resolves the mutable tag on every build and silently overwrites
  `VERSIONS.lock` — no diff/warning when the digest drifts from the committed one. Also
  `RepoDigests[0]` isn't guaranteed to correspond to the just-pulled tag.
- Dead config: compose `zenoh-router` service (profile `zenoh`) is never started by anything
  (demo3 starts `rmw_zenohd` inside the ws container); `scripts/run_in_container.sh` has zero
  callers but claims to be "used by the Makefile".
- Container runs as root on a `rw` bind mount → root-owned `docs/`, `VERSIONS.lock`,
  `ws/build|install|log`; the chown fix is only a manual runbook note, not wired into `run.sh`.
- `xhost +local:` is granted on every `viz`/`rqt` and never revoked; combined with
  `network_mode: host` + `ipc: host` + root container this deserves an explicit security note
  in README (fine for a single-user demo laptop, not for shared machines).
- Wayland-only host without XWayland: `viz`/`rqt` fail with an opaque "cannot open display"
  (`gui_prep` checks for `xhost`, not for a usable X socket).

**Code (`ws/src`)**
- Undeclared runtime deps (work only because ros-base ships them): `rcl_interfaces`
  (`demo_qos/qos_sub.py` imports `ParameterDescriptor`), `launch`/`launch_ros`
  (`demo_basic/launch/`). Add `<exec_depend>`s.
- `fibonacci_action_server.py` blocks the single-threaded executor with `time.sleep(0.3)`
  per step — matches upstream tutorials, but add a one-line comment so beginners don't
  conclude actions are non-blocking for free.
- `add_two_ints_client.py` / `fibonacci_action_client.py` use
  `spin_until_future_complete()` with no timeout and are **not used by `demo1_run.sh`**
  (acceptance uses `ros2 service call`/`action send_goal` under `timeout`) — orphaned,
  manual-only entry points that hang forever against a dead server.
- `qos_run.sh` synchronizes discovery with a flat `sleep 1` (race on a loaded host →
  could misreport a compatible pair as 0); `demo1_run.sh` cleanup does an unbounded `wait`.

**Docs / runbook**
- Runbook's "Expected (real)" `/chatter` line shows the C++ message, but the actual capture
  (`docs/img/demo1_chatter_echo.txt`) is the Python one — the `echo --once` race means either
  is valid; the runbook should say so instead of promising one specific string.
- `deadline` and `liveliness` are named in the QoS RxO policy list but never explained
  anywhere (reliability/durability get full treatment).
- `docs/img/demo2_topic_info.txt` shows `_NODE_NAME_UNKNOWN_` (daemon graph-cache race) with
  no caveat where it's referenced in `docs/03-qos.md`.
- `docs/06-microros-appendix.md`: "Live branches: humble/iron/jazzy/… ; Iron is EOL — avoid"
  is self-contradictory wording ("existing branches" is meant).

## NIT
- Comment in `add_two_ints_server.py` overstates *where* the `handle` name collision breaks
  (it's the `Node.handle` property used by later calls, not `__init__` itself).
- Style drift between packages meant to be read side by side: talker keeps a `self.timer`
  reference, qos_pub/qos_sub don't; demo_basic logs per-message, demo_qos is deliberately
  quiet (justified in docstring).
- `qos_common.py` raises a raw `KeyError` on a mistyped reliability/durability value — a
  clear error message would read better live on stage.
- QoS table rows 1–2 show only the reliability half of the pair; row 3 suddenly shows both
  halves — unannounced format shift.
- Version noise across stale plans (`~8.4.4` / `~8.4.2` vs actual `8.4.3`) — expected, both
  plans are historical.

## Firmware-research gaps (where to take the repo next)

The repo is a solid *communications-layer* foundation; for robot **firmware** research it
still lacks:
1. **micro-ROS hands-on** — docs-only appendix today; no client+agent demo with captured
   traffic comparable to Demos 1–3 (a QEMU or real-MCU freertos/zephyr client + `micro-ros-agent`).
2. **Real-time / executor determinism** — nothing on callback groups, executor jitter, or
   priorities; exactly what an ARQ/DMA-minded audience will probe.
3. **Latency/jitter metrics** — every demo measures "messages in N seconds", never round-trip
   latency; firmware audiences want timing distributions, not throughput booleans.
4. **CAN / CAN FD** — fully cut in the scope reduction; the host has vcan support, so a
   `ros2_socketcan` bridge demo is feasible.
5. **DDS-XRCE** — explained conceptually, never run/captured.
6. **DDS Security** — absent entirely; matters once "fielded robot" is the topic.

## Strengths (keep doing these)

- "No fabricated output" is real and independently verifiable — `docs/03-qos.md`/`05-rmw.md`
  are literal heredoc renders of their generator scripts; every deck/README number traces to
  `docs/img/` captures.
- Disciplined demo orchestration: every blocking `ros2` call bounded by `timeout`,
  capture-everything-assert-at-end via `scripts/lib.sh`.
- Correct, idiomatic rclpy/rclcpp throughout (action protocol, lifecycle
  `destroy_node`+`try_shutdown`, `dynamic_typing` param handling), with accurate
  firmware-analogy docstrings that read well aloud.
- Consistent visual language across all 8 SVG diagrams; `build_slides.py` fails loudly on
  missing/unresolved assets; deck↔assets invariant holds 1:1.
- Honest hedging in docs ("real-time is a potential, not a guarantee", self-published
  benchmark caveats) — the right tone for a research repo.
