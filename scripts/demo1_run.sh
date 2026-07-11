#!/usr/bin/env bash
#
# demo1_run.sh — RUNS INSIDE the ws container. Brings up the Demo 1 graph as separate
# processes, exercises pub/sub + service + action, captures node-graph artifacts to
# docs/img/, and asserts acceptance. No -e: we capture everything, then assert at the end.
# NOTE: no `set -u` — ROS's setup.bash references unbound vars (AMENT_TRACE_SETUP_FILES).
set -o pipefail
source /opt/ros/jazzy/setup.bash
source /repo/ws/install/setup.bash
source /repo/scripts/lib.sh

IMG=/repo/docs/img
mkdir -p "$IMG"

PIDS=()
cleanup() { kill "${PIDS[@]}" 2>/dev/null || true; wait 2>/dev/null || true; }
trap cleanup EXIT

log "Bringing up the Demo 1 graph (separate processes, host networking, no master)..."
ros2 launch demo_basic demo_basic.launch.py > /tmp/demo1_launch.log 2>&1 &
PIDS+=($!)

log "Waiting for the full graph to be discovered (ros2 daemon discovery is racy)..."
EXPECT='/talker /talker_cpp /listener /add_two_ints_server /fibonacci_action_server'
for _ in $(seq 1 25); do
  ros2 node list > "$IMG/demo1_node_list.txt" 2>&1 || true
  missing=0
  for n in $EXPECT; do grep -qF "$n" "$IMG/demo1_node_list.txt" || missing=1; done
  [ "$missing" -eq 0 ] && break
  sleep 1
done

# --- node-graph artifacts (TEXT — always captured) ---------------------------
ros2 topic list                > "$IMG/demo1_topic_list.txt"    2>&1 || true
ros2 topic info /chatter -v    > "$IMG/demo1_chatter_info.txt"  2>&1 || true

# --- pub/sub: capture one real message off /chatter --------------------------
timeout 12 ros2 topic echo --once /chatter > "$IMG/demo1_chatter_echo.txt" 2>&1 || true

# --- service: 2 + 3 must equal 5 ---------------------------------------------
timeout 20 ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 2, b: 3}" \
  > "$IMG/demo1_service_call.txt" 2>&1 || true

# --- action: Fibonacci with feedback -----------------------------------------
timeout 25 ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci \
  "{order: 5}" --feedback > "$IMG/demo1_action.txt" 2>&1 || true

cleanup
trap - EXIT

log "=== acceptance ==="
assert_file_contains "$IMG/demo1_node_list.txt"   "/talker"      "node graph shows the talker"
assert_file_contains "$IMG/demo1_node_list.txt"   "/listener"    "node graph shows the listener"
assert_file_contains "$IMG/demo1_node_list.txt"   "/talker_cpp"  "node graph shows the C++ talker"
assert_file_contains "$IMG/demo1_chatter_echo.txt" "Hello"       "pub/sub delivered >=1 message on /chatter"
assert_file_contains "$IMG/demo1_service_call.txt" "sum=5"       "service: 2 + 3 = 5"
assert_file_contains "$IMG/demo1_action.txt"       "[Ff]eedback" "action emitted >=1 feedback"
assert_file_contains "$IMG/demo1_action.txt"       "[Rr]esult"   "action returned a result"
ok "Demo 1 acceptance PASSED"
