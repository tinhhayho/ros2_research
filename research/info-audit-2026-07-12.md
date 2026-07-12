# Information audit — 2026-07-12

**How produced:** five parallel read-only `info-auditor` / `repo-reviewer` agents per
`.claude/workflows/info-audit.md`, non-overlapping scopes A–E. Orchestrator merged,
de-duplicated, and re-verified every MAJOR against the cited files before writing this
document. Agents did **not** re-fetch external URLs; external facts are tagged
`[VERIFY-EXTERNALLY]` and deferred to `research/claims-audit-2026-07.md`.

| Agent | Scope | Lens |
|-------|--------|------|
| A | Teaching docs + demos + captures + `ws/src` + demo scripts | Numbers/names vs code & artifacts |
| B | `research/**` + claims-audit trail | Research note vs audit-trail honesty |
| C | Teaching + research decks, SVG text, captures | Slide tables vs captures & trail |
| D | README, blogs, runbooks, plans, REVIEW | Entrypoint honesty, expected outputs |
| E | `run.sh`, Makefile, docker, VERSIONS.lock, capture scripts | Pinning / make parity / lock provenance |

**Verdict:** Demo teaching numbers (QoS 0/20/0, RMW 8/8/8, sum=5, 5 nodes, GR00T run A)
remain solid and capture-backed. The main problems are (1) known-but-unfixed teaching and
entrypoint defects from `REVIEW.md`, (2) research/slide wording that reverts audited
corrections (“one brain”, absolute “no certs”, multi-container “verified by demos”), and
(3) digest-pinning that is recorded on build but not enforced on run. No auto-fixes applied.

---

## MAJOR — fix before next presentation / publish

1. **Demo 3 slide table self-contradicts** (`slides/deck.md:123`, `slides/slides.md:123`).
   Row 1: Talker=Fast DDS, Listener=`Fast DDS / Cyclone / Zenoh` → **8/8/8 all flow**.
   Row 3: Fast DDS → Zenoh → **0**. The 8/8/8 figures are three *same-RMW* legs
   (`docs/05-rmw.md`). **Fix:** Talker cell = `Fast DDS / Cyclone / Zenoh` (paired same-RMW),
   or label the row “same RMW both sides.” *(Also in REVIEW.md #1 — still open.)*

2. **Research deck reintroduces “one brain”** (`slides/research-deck.md:752`,
   `slides/research.md:752`): “same **Cosmos brain** in GR00T and Alpamayo.” Same deck
   earlier (`:673`) and claims-audit **#22 (corrected)** say share lineage, not one brain.
   **Fix:** replace with “same Cosmos *lineage*” / “shared backbone family.”

3. **vs-auto research note keeps pre-correction absolutes**
   (`research/nvidia-physical-ai-vs-automotive-2026-07.md:15–16,55`):
   - “cùng một con chip” + “cùng một bộ não world-model” → contradicts #21 (scoped) / #22
   - “Jetson AGX Thor: **không có cert nào**” → contradicts #29 (scoped to completed product
     certs; Halos for Robotics announced).
   **Fix:** align wording with claims-audit statuses.

4. **T4000 power envelope conflict** (`research/nvidia-physical-ai-2026-07.md:184–185` says
   **40–70 W** “AUDIT confirmed”; claims-audit **M6** / memory report say T4000 TMP **90 W**,
   modes 70/MAXN; 40 W floor is marketing for T5000 path only).
   **Fix:** use datasheet TMP/modes; footnote marketing range if kept.

5. **Multi-container discovery overclaimed** (`docs/04-discovery.md:29–30`): “nodes in
   **separate containers** discover … (verified across all three demos).” Demos only start
   peer processes **inside one `ws` container**. Host networking makes multi-container
   *possible*; demos do not prove it.
   **Fix:** “multi-process on host networking (demos); multi-container works with the same
   compose defaults but is not exercised by demo-1/2/3.”

6. **Plan files deny the repo exists** (`PLAN.md:7–9`, `REVISED-PLAN.md:1,8–9,…`):
   “No real code has been written yet” / H1 still `# PLAN.md` / “awaiting go-ahead.”
   **Fix:** historical banners + README pointer. *(REVIEW.md #2 — still open.)*

7. **`make viz` / `make rqt` missing** (`Makefile:4–7` vs `README.md:15–20`): README says
   `make <target>` works after listing viz/rqt. **Fix:** add both to `.PHONY`/target list.
   *(REVIEW.md #4 — still open.)*

8. **Digest pin not enforced on run** (`run.sh`: only `build()` sources `docker/image.env`;
   compose defaults to mutable `ros:jazzy-ros-base-noble`). Fresh clone `./run.sh demo-1`
   can build unpinned. **Fix:** source pin (or fail “run ./run.sh build first”) at top of
   every container path. *(REVIEW.md #3 — still open; agent E also notes build re-resolves
   the tag rather than building *from* the committed lock.)*

---

## MINOR

**Teaching / captures**
- QoS incompatible-warning claim has no raw stdout under `docs/img/` (summary only in
  `docs/03-qos.md`).
- `demo1_chatter_echo.txt` shows only rclpy; dual-language *publishers* proven by
  `demo1_chatter_info.txt`, not by echo.
- Runbook expected chatter string is C++ (`Hello from C++…: 9`) while capture is Python
  — live race, either OK; side-by-side check against `docs/img` can “fail.”
- Research slide “This exact node runs in our Demo 1” uses a simplified String payload,
  not the real `Hello ROS 2 (rclpy): {count}` talker.
- GR00T run B numbers only on screenshot (no text twin in `docs/img/`).

**Research trail gaps**
- Physical-AI “14 load-bearing claims” and vs-auto “10 claims” self-scores have **no P-/**
  batch rows in claims-audit (trail-gap).
- `robot-software-stack` still cites GR00T **N1.6** while audit #15 / physical-ai use **N1.7**.
- Autoware “~500 companies” missing self-reported label in stack survey.
- AEC-Q100: vs-auto “not public” vs U13 “platforms cite it” (self-reported).
- `>22,000` fault mechanisms still stated without “treat with care” (#31 unverified).
- EventsCBGExecutor 10–15% CPU, Cosmos/Lab-Arena/Isaac Sim date headlines: trail-gaps.

**Infra**
- `image.env` gitignored → pin not in clone without prior build; no fail-closed from lock.
- Build always `docker pull` mutable tag and rewrites lock (record-after-resolve, not
  lock-as-input).
- Marp image is tag-pinned (`v4.4.0`), not digest; not in VERSIONS.lock.
- Dead: compose `zenoh-router` profile; `scripts/run_in_container.sh` (no callers).
- `capture_pkgs.sh` omits turtlesim / GUI stack packages.
- `xhost +local:` never revoked; no shared-host security note in README.

**Other**
- Panic note typo `rmf_zenohd` → should be `rmw_zenohd` (`runbook/slides-transcript-vi.md`).
- Primer states ~50 µs PREEMPT_RT jitter without “illustrative / no own cyclictest.”

---

## NIT

- `std_msgs/String` vs `std_msgs/msg/String` in QoS doc header.
- Domain isolation ✅ on slides vs ❌ in auto-gen doc (both mean 0 msgs / isolation worked).
- `rmw_zenoh` shorthand vs `rmw_zenoh_cpp` / `rmw_zenohd` in code.
- VERSIONS.lock `[rmw-available]` only lists fastrtps despite three RMWs installed.
- README omits `slides-research` / `shell` / `clean` from the quick blurb.

---

## Claim inventory (orchestrator summary)

| Area | Result |
|------|--------|
| Demo 1 nodes / sum=5 / Fibonacci / dual pubs | **confirmed** (captures) |
| Demo 2 QoS 0 / 20 / 0 + late-joiner | **confirmed** (auto-gen + script math) |
| Demo 3 same-RMW 8/8/8, Fast↔Cyclone 8, Fast→Zenoh 0, domain 0 | **confirmed** numbers; **mismatch** slide table presentation |
| GR00T run A (94.6 s / 107.7 ms / P90 109.8 / MSE) | **confirmed** (`docs/img/groot_n17_inference.txt`) |
| R-series (ros2-deep-dive) incl. Kilted **Nov** 2026 | **confirmed** aligned with claims-audit |
| M/U/A series research notes | **mostly confirmed**; T4000 power + a few absolutes fail |
| Deck #22 “one brain” | **mismatch** (research deck + vs-auto) |
| Digest-pinned for all runs | **mismatch** (build-only pin source) |
| `make` parity with README | **mismatch** (`viz`/`rqt`) |
| Plan status honesty | **mismatch** |
| External NVIDIA/ROS product numbers | **[VERIFY-EXTERNALLY]** — defer to claims-audit |

---

## Strengths

1. Demo matrix numbers are script-driven auto-gen (`docs/03-qos.md`, `docs/05-rmw.md`) and
   match timer math (5 Hz×4 s → 20; 2 Hz×4 s → 8).
2. Demo 1 CLI commands, types, and acceptance strings line up with `docs/img/*` end-to-end.
3. R/M/U/A claims-audit batches are high quality where research notes apply corrections
   (Kilted EOL, MIG=2, TRT 144.9→93.8, Alpamayo 34/32B conflict footnotes).
4. Canonical `./run.sh` story is clear; no `:latest` on the ROS teaching image path.
5. Open gaps are listed honestly in claims-audit (no cyclictest; >22k primary missing;
   GR00T env not locked).

---

## Suggested fix order (for approval — not applied)

| Priority | Item | Files |
|----------|------|--------|
| P0 | Demo 3 table Talker cell | `slides/deck.md` → rebuild slides |
| P0 | “Cosmos brain” → lineage | `slides/research-deck.md` → rebuild research slides |
| P0 | vs-auto absolutes + T4000 power | research notes |
| P1 | discovery multi-container wording | `docs/04-discovery.md` |
| P1 | Plan historical banners | `PLAN.md`, `REVISED-PLAN.md`, README link |
| P1 | Makefile `viz` `rqt` | `Makefile` |
| P1 | Fail-closed pin on all run targets | `run.sh` (+ optional lock-as-input) |
| P2 | Trail-gap rows / N1.6→N1.7 / self-report labels | research + claims-audit append |
| P2 | Capture gaps (QoS warning log, dual echo, run B text) | scripts + docs/img |
| P3 | Dead config cleanup, marp digest, xhost note | docker/scripts/README |

---

## Relation to prior reviews

| Artifact | Overlap |
|----------|---------|
| `REVIEW.md` (2026-07-08) | MAJORs 1, 6, 7, 8 above still open; this pass reconfirms |
| `research/claims-audit-2026-07.md` | External primary-source trail; this pass is **internal** consistency only |
| `.claude/workflows/info-audit.md` | Playbook used to produce this document |

---

## Applied fixes (2026-07-12, same day — after orchestrator re-verification)

Every MAJOR was re-verified against the cited file:line and confirmed real, then fixed:

| # | Fix | Files |
|---|-----|-------|
| M1 | Demo 3 table row 1 → "Fast DDS / Cyclone / Zenoh · same RMW on both sides" (no more self-contradiction with the Fast→Zenoh=0 row); decks rebuilt | slides/deck.md (+slides.md/html) |
| M2 | "same Cosmos brain" → "same Cosmos-Reason lineage" | slides/research-deck.md (+research.md/html) |
| M3 | vs-auto: "cùng một con chip/bộ não" → dòng SoC + lineage; "không có cert nào" → scoped to completed product certs; AEC-Q100 row updated per A-series | research/nvidia-physical-ai-vs-automotive-2026-07.md |
| M4 | T4000 power → modes 70 W/MAXN, TMP 90 W per datasheet (marketing 40 W floor flagged) | research/nvidia-physical-ai-2026-07.md |
| M5 | Discovery doc scoped to what demos exercise (multi-process in one container; multi-container possible but not exercised) | docs/04-discovery.md |
| M6 | Historical banners added; REVISED-PLAN H1 fixed | PLAN.md, REVISED-PLAN.md |
| M7 | `viz` + `rqt` added to Makefile pass-through | Makefile |
| M8 | `load_pin()` fail-closed: every container target sources docker/image.env or requires a built image | run.sh |

MINOR one-liners also applied: primer ~50 µs labeled illustrative; Autoware ~500 labeled
self-reported; GR00T N1.6→N1.7 (stack survey, 2 places); `rmf_zenohd`→`rmw_zenohd` typo;
>22,000 mechanisms + AEC-Q100 rows re-labeled in vs-auto.

Still open (not fixed this pass): teaching-deck twemoji CDN icons (6, pre-existing);
lock-as-input rebuild semantics; capture gaps (QoS warning stdout, GR00T run B text twin);
remaining trail-gap rows; dead compose profile / run_in_container.sh; xhost note.
