# Robot fleet standards (VDA 5050) — audit of an external draft, and what survived (July 2026)

**What this is.** A second externally produced draft report ("Fleet management standards
for robots (AMR/AGV)", dated 2026-07-13) was submitted for the deck. Same workflow as
`research/fleet-uds-autosar-2026-07.md`: two parallel fact-check passes with
non-overlapping scopes (the VDA 5050 spec itself; the surrounding standards landscape) +
independent re-verification of the load-bearing claims straight from the spec sources
(raw `VDA5050_EN.md` from github.com/VDA5050/VDA5050 main + the GitHub release API).
Verdicts below; only corrected content feeds the deck. Claim rows: V-series in
`research/claims-audit-2026-07.md`.

**Headline result.** The draft's core claim holds — **VDA 5050 v3.0 is real and current**
(v3.0.0 released 2026-03-19; we verified the GitHub release and the spec text directly).
Its function table is half right (the "charging zone" is invented; MQTT — the actual
wire protocol — is never mentioned). Its "future direction" is the same failure mode as
the first draft's Thor architecture: **"Redfish + PICMG IoT.x for robot fleets" is
documented nowhere** — two real, unrelated standards stitched into a nonexistent trend.

## 1. Verdict table

Status: ✅ confirmed · 🟡 partly (kept with correction) · ❌ refuted (excluded) ·
❓ not documented anywhere (excluded).

| # | Draft claim | Verdict | Correction / evidence |
|---|---|---|---|
| V1 | VDA 5050 = the standard interface between fleet manager ("master control") and AMR/AGV | ✅ | spec §2: "standardized and vendor-neutral communication interface between a fleet control system and mobile robots"; published jointly by **VDA + VDMA + KIT-IFL** |
| V2 | Current version = v3.0 | ✅ | v3.0.0 released **2026-03-19** (GitHub release verified: "as released by the VDA on March 19th, 2026"); v2.0 = Jan 2020, v2.1 = Aug 2024 (corridors, map distribution, factsheet vehicle config) |
| V3 | (omitted by draft) transport = ? | 🟡 gap-filled | **MQTT (3.1.1 minimum) + JSON**; topic scheme `vda5050/v3/<manufacturer>/<serialNumber>/<topic>`; topics: order, instantActions, state, visualization, connection, factsheet + **zoneSet, responses (new in v3.0)** — verified in spec §4 |
| V4 | Task allocation from fleet manager to robot, "rất cao" standardization | ✅ | orders = graphs of nodes/edges; released part = **base**, planned part = **horizon** (spec §5.3, verified) |
| V5 | Path sharing & traffic control standardized | 🟡 | the *mechanism* (master control releasing base/horizon edges) is standardized; the traffic/deadlock *logic* is explicitly **out of scope** (§2: "routing, prioritization, congestion handling, or deadlock resolution… not included") |
| V6 | "Zone Management: vùng cấm, vùng sạc, vùng ưu tiên" | 🟡 | zones are real **as of v3.0** (§6.4): BLOCKED, LINE_GUIDED, RELEASE, COORDINATED_REPLANNING, SPEED_LIMIT, ACTION + PRIORITY, PENALTY, DIRECTED, BIDIRECTED. **No "charging zone" exists** (verified: zero matches in the spec) — charging is the `startCharging`/`stopCharging` action pair |
| V7 | Factsheet declares robot capability; "còn khá đơn giản" | 🟡 | factsheet since **v1.1 (2020)**, not basic physically (geometry, envelope curves, protocol features, per-action schemas, battery since v3.0) — but genuinely **no semantic sensor/perception model** (only a coarse localizationTypes enum). Fair criticism, wrong emphasis |
| V8 | Actions at nodes (pick, drop, charge…) | ✅ | predefined list incl. pick, drop, startCharging/stopCharging, initializePosition, map/zone management, finePositioning; manufacturer extensions allowed; only cancelOrder/startPause/stopPause are mandatory |
| V9 | Strong European vendor support | ✅ | SYNAOS ecosystem (KUKA, Omron, SEW, STILL, Jungheinrich, MiR), Bosch Rexroth ROKIT, DS Automotion, SAFELOG; **plus real North-American uptake** (OTTO by Rockwell VDA 5050 certifications) — "Europe-strongest, globally growing; Asia fragmented" |
| V10 | Limitations: application layer only; no firmware/OTA; shallow diagnostics | ✅ | spec §2 excludes cybersecurity ("not specified"; broker/TLS config's job) and safety; no OTA action exists (updateCertificate rotates TLS certs only); errors are flat errorType/errorLevel — no DTC/DID analog |
| V11 | (omitted by draft) the rest of the landscape | 🟡 gap-filled | **MassRobotics AMR Interop** = state-reporting only ("not a task management type of system"), complementary; **OPC 40010** (OPC UA Robotics) = vertical asset/condition monitoring; **Open-RMF** = coordinator that can drive robots *over* VDA 5050 (vda5050_connector, real integrations; MiR ships a VDA 5050 adapter; NVIDIA Isaac Mission Dispatch is VDA5050-compliant) |
| V12 | "Redfish + PICMG IoT.x đang được đẩy mạnh cho robotics"; combine VDA 5050 + Redfish | ❓ | **not documented anywhere.** Redfish = DMTF server/BMC management; PICMG IoT.1 (2021) = factory sensor/effecter data models, Redfish extension still "work in progress" (projected 2025, unconfirmed shipped); zero sources pair either with AMR fleets. Struck |
| V13 | OTA for AMRs is vendor-specific | ✅ | no interop standard exists; de-facto *tooling* = Mender, RAUC, SWUpdate (embedded-Linux updaters) |
| V14 | "Chưa có chuẩn tương đương UDS DID cho sensor discovery" | ✅ | real gap — in practice filled by vendor cloud platforms (InOrbit, Formant) ingesting **ROS 2 `/diagnostics`** topics + MQTT telemetry |

## 2. The corrected picture (what the deck now teaches)

1. **VDA 5050 is the robot fleet wire protocol**: MQTT + JSON, six core topics + two
   v3.0 zone topics; robots self-describe via the factsheet; orders are node/edge graphs
   released incrementally (base/horizon) by master control. v3.0 (03/2026) is the
   AMR-era release: freely-navigating robots, zones, CRITICAL/URGENT error levels.
2. **It is a wire protocol, not a coordinator** — Open-RMF (already in the deck) sits a
   layer above and can drive robots over VDA 5050; MassRobotics covers cross-fleet
   state-sharing; OPC 40010 covers robot→enterprise asset monitoring. Complementary
   layers, not competitors.
3. **The comparison with automotive is an asymmetry, not a deficit list**: robots
   standardized fleet orchestration (which automotive leaves operator-proprietary);
   automotive standardized diagnostics/OTA/platform (UDS, SOVD, UCM, AUTOSAR — which
   robotics leaves to ROS 2 conventions + vendor tooling). Neither side has a semantic
   capability/sensor discovery standard.
4. **The draft's "future = Redfish/PICMG"** is excluded; the honest statement is "the
   platform-layer gap is real and currently filled by de-facto tools (ROS 2
   diagnostics, InOrbit/Formant, Mender/RAUC), with no interop standard on the horizon".

## 3. Excluded from publication (refuted/undocumented)

- "Charging zone" as a VDA 5050 zone type (no such type; action pair instead).
- "Redfish + PICMG IoT.x being pushed for robotics"; "VDA 5050 + Redfish" as a trend.
- "Zone Management / traffic control fully standardized" without the out-of-scope
  caveat (the logic is explicitly excluded from the spec).

## 4. Verification notes

- Load-bearing claims re-verified directly by the orchestrating pass: raw
  `VDA5050_EN.md` (main = 3.0.0) fetched from GitHub — confirmed MQTT 3.1.1 quote,
  base/horizon definitions, all zone-type enums present, zero "charging zone" matches;
  GitHub release API for tag 3.0.0 — "released by the VDA on March 19th, 2026".
- Most public write-ups still describe v2.0/2.1; v3.0-specific features (zones, free
  navigation) are documented mainly in the spec/release notes themselves.
- MassRobotics v2.0 (mission API) unconfirmed as ratified by 07/2026 — treat as v1.x.

## Sources

- github.com/VDA5050/VDA5050 — VDA5050_EN.md (spec, main=3.0.0; §2 scope, §4 MQTT,
  §5.3 base/horizon, §6.2.3.1 actions, §6.4 zones, §7.10 factsheet) · releases 3.0.0 /
  2.1.0 / 2.0.0 (dates, changelogs)
- ifr.org "VDA 5050 explained" (VDA+VDMA+KIT-IFL governance)
- massrobotics.org AMR Interop standard + github.com/MassRobotics-AMR ("not a task
  management type of system")
- reference.opcfoundation.org OPC-40010-1 (asset management / condition monitoring)
- index.ros.org vda5050_connector · github.com/inorbit-ai/ros_amr_interop ·
  github.com/nvidia-isaac/isaac_mission_dispatch · discourse.openrobotics.org (real
  RMF-over-VDA5050 integration thread) · mobile-industrial-robots.com (MiR VDA5050)
- synaos.com (partner ecosystem; VDA5050 vs MassRobotics vs Open-RMF; Asia outlook) ·
  ottomotors.com / automate.org (OTTO by Rockwell VDA 5050 certifications) ·
  ds-automotion.com ("global standard from Europe") · boschrexroth.com (ROKIT)
- dmtf.org/standards/redfish (scope: "converged, hybrid IT and the Software Defined
  Data Center") · picmg.org (IoT.1 ratified 2021; Redfish IP submission "work in
  progress", projected 2025)
- inorbit.ai docs (ROS 2 /diagnostics ingestion) · Mender/RAUC/SWUpdate comparisons
