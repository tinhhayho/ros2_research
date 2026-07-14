# Fact-check — 2026-07-14

**Scope:** the 10 technical claims behind the new `graph-to-joint` component diagram
(fleet → ROS 2 graph → RT boundary → ros2_control → fieldbus → MCU) and the chat
explanation it came from, before the diagram ships into `slides/research-deck.md`.

**Method:** `.claude/workflows/fact-check.js` (first production run) — one Sonnet
web-research agent per claim against primary sources, plus an adversarial second agent on
every non-clean verdict. 11 agents, 0 errors, ~330k subagent tokens.

**Result: 9 correct (high confidence) · 1 partially-correct · 0 wrong.**

| # | Claim (short) | Verdict | Primary source |
|---|---|---|---|
| C1 | RMF core = ROS 2 nodes; fleets via fleet adapters; doors/lifts/chargers via adapter nodes; rmf-web REST/WS | **partially-correct** — see below | osrf.github.io/ros2multirobotbook · open-rmf GitHub |
| C2 | Nav2 controller server publishes /cmd_vel, `controller_frequency` default 20 Hz | correct | docs.nav2.org controller-server config |
| C3 | diff_drive_controller: non-RT subscription → realtime_tools buffer; cmd timeout 0.5 s → zero velocity | correct | ros2_controllers jazzy branch source |
| C4 | joint_state_broadcaster → RealtimePublisher: RT side try-locks & drops, non-RT thread does the DDS publish | correct | ros2_controllers + realtime_tools source |
| C5 | controller_manager read→update→write at update_rate; 1 kHz typical for demanding robots; SCHED_FIFO on PREEMPT_RT; framework can't enforce RT-safety in plugins | correct | control.ros.org controller_manager userdoc |
| C6 | Jazzy default rmw_fastrtps; UDP between hosts, Fast DDS SHM on one host; intra-process pointer passing is rclcpp (opt-in), not DDS | correct | docs.ros.org/en/jazzy |
| C7 | SystemInterface on_init(HardwareInfo from `<ros2_control>` URDF tags); read/write every cycle; pluginlib export + runtime load by URDF plugin name | correct | control.ros.org writing_new_hardware_component |
| C8 | ros2_canopen and ethercat_driver_ros2 exist as ros2_control hardware interfaces | correct | ros-industrial/ros2_canopen · ICube-Robotics/ethercat_driver_ros2 |
| C9 | MoveIt → joint_trajectory_controller via FollowJointTrajectory action; controller interpolates each cycle | correct | control.ros.org JTC userdoc · moveit.picknik.ai |
| C10 | controllers ↔ hardware via loaned state/command interface handles in-process, no topics/DDS | correct | control.ros.org LoanedCommandInterface API |

## C1 correction (the one finding)

Doors and lifts each have a dedicated standalone adapter node
(`door_adapter_template`, `lift_adapter_template`). **Chargers do not** — there is no
"charger adapter node": charging stations are waypoints configured inside each fleet
adapter (`rmf_config.charger.waypoint`, `set_charger_waypoint()`, optional `dock_name`),
plus an optional `rmf_charging_schedule` node that only arbitrates shared-charger
time-slots. open-rmf's own `awesome_adapters` list has Door/Lift/Fleet categories, no
Charger category. Both the verify agent and the adversarial reviewer confirmed this
independently.

**Impact on repo content:** none found. `slides/research-deck.md` (Open-RMF slide) says
RMF coordinates "doors/lifts/chargers" as shared infrastructure — true (charging *is*
coordinated, just not via a hardware adapter node). `assets/rmf-position.svg` shows only
"Door / lift adapter" — correct. The new `assets/graph-to-joint.svg` does not mention
chargers. The only artifact with the wrong phrasing was the discarded Vietnamese draft
diagram in the session scratchpad ("door / lift / charger adapters"), superseded by the
English asset.

## Addendum (same day) — controller nodes, for the diagram redesign

Two further claims verified (2 Sonnet agents, both **correct, high confidence**,
straight from the `jazzy` branch source):

| # | Claim (short) | Verdict | Primary source |
|---|---|---|---|
| N1 | Each loaded ros2_control controller instantiates its own LifecycleNode named after the controller, visible in `ros2 node list`, spun by controller_manager's executor in the same process | correct | `controller_interface_base.cpp` (`make_shared<LifecycleNode>(controller_name…)`) · `controller_manager.cpp` (`executor_->add_node(...)`) · `ros2_control_node.cpp` |
| N2 | diff_drive's `/cmd_vel` subscription lives on the controller's own node (callback on executor threads); joint_state_broadcaster publishes `/joint_states` from its node; both `update()`s run in the RT loop; realtime_tools buffers bridge | correct | `diff_drive_controller.cpp` · `joint_state_broadcaster.cpp` · realtime_tools docs |

Nuance from N2: `RealtimePublisher`'s actual `publish()` runs on a thread the
RealtimePublisher spawns itself (`publishingLoop`), not on the executor pool — the
diagram's wording "from a normal thread (the postman)" stays correct.

This addendum also corrects a statement made in chat during this session
("plugins never appear on the graph" — wrong: each controller's node *does* appear).

## Nuances worth keeping in the speaker's head (not errors)

- C4: try-lock/drop semantics confirmed in `realtime_tools` source — the "postman"
  metaphor in the transcript is accurate.
- C5: 1 kHz is "typical/achievable for demanding robots", not a default —
  `update_rate` is explicit configuration (deck already phrases it as "rate is
  configured; 1 kHz typical").
- C6: intra-process zero-copy is an **rclcpp** feature (opt-in, composition), not a DDS
  transport — the diagram credits it to rclcpp explicitly.
