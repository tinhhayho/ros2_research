#!/usr/bin/env bash
#
# run.sh — canonical entrypoint for ros2-explained.
# The host needs ONLY Docker + the compose plugin (no make, no ROS 2 install).
# `make <target>` is an optional thin wrapper over this script.
set -euo pipefail
cd "$(dirname "$0")"

COMPOSE=(docker compose -f docker/docker-compose.yml)
MARP="marpteam/marp-cli:v4.4.0"

# Fail-closed digest pin: every target that can build/run the ws container must either
# have the resolved pin (docker/image.env, written by `build`) or an already-built image.
# Otherwise compose would silently build from the mutable ros:jazzy tag.
load_pin() {
  if [[ -f docker/image.env ]]; then
    set -a; source docker/image.env; set +a
  elif ! docker image inspect ros2-explained:jazzy >/dev/null 2>&1; then
    echo "error: docker/image.env missing and image ros2-explained:jazzy not built." >&2
    echo "       Run ./run.sh build first (it resolves and records the base-image digest)." >&2
    exit 1
  fi
}

build() {
  bash scripts/capture_versions.sh
  set -a; source docker/image.env; set +a
  "${COMPOSE[@]}" build
  "${COMPOSE[@]}" run --rm -T ws bash -lc \
    'if ls src/*/package.xml >/dev/null 2>&1; then colcon build --symlink-install; else echo "(no packages yet — skipping colcon build)"; fi'
  "${COMPOSE[@]}" run --rm -T ws bash /repo/scripts/capture_pkgs.sh /repo/VERSIONS.lock
  echo "==> build complete. Image + VERSIONS.lock ready."
}

shell()  { load_pin; "${COMPOSE[@]}" run --rm ws bash; }

demo_1() { load_pin; bash scripts/verify_basic.sh; }
demo_2() { load_pin; bash scripts/verify_qos.sh; }
demo_3() { load_pin; bash scripts/verify_middleware.sh; }

slides() {
  python3 scripts/build_slides.py     # assemble slides.md (inlines the SVG diagrams)
  docker run --rm -v "$PWD/slides:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" \
    "$MARP" slides.md -o slides.html --html
  echo "==> slides/slides.html built (the committed deliverable)."
}
slides_research() {
  python3 scripts/build_slides.py --deck research-deck.md --out research.md
  docker run --rm -v "$PWD/slides:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" \
    "$MARP" research.md -o research.html --html
  echo "==> slides/research.html built (deep-research findings deck)."
}
slides_autosar() {
  python3 scripts/build_slides.py --dir autosar/slides --deck autosar-deck.md --out autosar.md
  docker run --rm -v "$PWD/autosar/slides:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" \
    "$MARP" autosar.md -o autosar.html --html
  echo "==> autosar/slides/autosar.html built (AUTOSAR Classic vs Adaptive deck)."
}
slides_autosar_compact() {
  python3 scripts/build_slides.py --dir autosar/slides --deck autosar-compact-deck.md --out autosar-compact.md
  docker run --rm -v "$PWD/autosar/slides:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" \
    "$MARP" autosar-compact.md -o autosar-compact.html --html
  echo "==> autosar/slides/autosar-compact.html built (20-minute AUTOSAR deck)."
}
slides_pdf() {
  python3 scripts/build_slides.py
  docker run --rm -v "$PWD/slides:/home/marp/app" -e MARP_USER="$(id -u):$(id -g)" \
    "$MARP" slides.md -o slides.pdf --pdf --allow-local-files
  echo "==> slides/slides.pdf built."
}
slides_pptx() {
  # text-only .pptx mirror of the research deck (stdlib only, no deps);
  # image slides become paste-here placeholders — see scripts/build_pptx.py
  python3 scripts/build_pptx.py "$@"
}

# Allow the container (local, non-network client) to talk to the host X server.
gui_prep() {
  if command -v xhost >/dev/null 2>&1; then
    xhost +local: >/dev/null 2>&1 \
      || echo "note: 'xhost +local:' failed — if no window appears, run it yourself in a terminal."
  else
    echo "note: xhost not found — if no GUI window appears, install x11-xserver-utils or run 'xhost +local:'."
  fi
}

# Visual demo: turtlesim window + drive it with the arrow keys (interactive TTY).
viz() {
  load_pin
  gui_prep
  echo "==> Opening turtlesim. A window should appear on your screen."
  echo "==> Click this terminal, then use the ARROW KEYS to drive the turtle. Ctrl-C to quit."
  "${COMPOSE[@]}" run --rm ws bash -lc '
    ros2 run turtlesim turtlesim_node &
    sleep 2
    ros2 run turtlesim turtle_teleop_key'
}

# Live node-graph window (rqt_graph). Run a demo in another terminal first to see nodes.
rqt() {
  load_pin
  gui_prep
  echo "==> Opening rqt_graph. Tip: run './run.sh demo-1' or './run.sh viz' in another terminal first."
  "${COMPOSE[@]}" run --rm ws bash -lc 'rqt_graph'
}

test_all() {
  load_pin
  bash scripts/verify_basic.sh
  bash scripts/verify_qos.sh
  bash scripts/verify_middleware.sh
  echo "==> all verify scripts passed."
}

clean() {
  "${COMPOSE[@]}" --profile zenoh down --remove-orphans || true
  rm -rf ws/build ws/install ws/log
  echo "==> cleaned."
}

usage() {
  cat <<'EOF'
Usage: ./run.sh <target>   (or: make <target>)
  build       Resolve digest, build image, colcon-build workspace, write VERSIONS.lock
  shell       Interactive ROS 2 shell in the ws container
  demo-1      Demo 1: pub/sub + service + action
  demo-2      Demo 2: QoS compatibility matrix
  demo-3      Demo 3: RMW / middleware swap + interop
  viz         Visual demo: turtlesim window, drive it with the arrow keys
  rqt         Open rqt_graph (live node/topic graph window)
  slides      Build slides/slides.html (the committed deliverable)
  slides-research  Build slides/research.html (deep-research findings deck)
  slides-autosar   Build autosar/slides/autosar.html (AUTOSAR Classic vs Adaptive deck)
  slides-autosar-compact  Build autosar/slides/autosar-compact.html (20-minute version)
  slides-pdf  Also export slides/slides.pdf (optional)
  slides-pptx Text-only slides/research.pptx (paste images by hand; optional)
  test        Run all verify scripts
  clean       Stop containers + remove colcon artifacts
EOF
}

case "${1:-help}" in
  build) build ;;
  shell) shell ;;
  demo-1) demo_1 ;;
  demo-2) demo_2 ;;
  demo-3) demo_3 ;;
  viz) viz ;;
  rqt) rqt ;;
  slides) slides ;;
  slides-research) slides_research ;;
  slides-autosar) slides_autosar ;;
  slides-autosar-compact) slides_autosar_compact ;;
  slides-pdf) slides_pdf ;;
  slides-pptx) shift; slides_pptx "$@" ;;
  test) test_all ;;
  clean) clean ;;
  help|-h|--help) usage ;;
  *) echo "unknown target: $1" >&2; usage; exit 2 ;;
esac
