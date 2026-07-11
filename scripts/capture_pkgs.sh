#!/usr/bin/env bash
#
# capture_pkgs.sh — append the REAL installed package versions to VERSIONS.lock.
# Runs INSIDE the built image (via `docker compose run ws`), so dpkg sees the truth.
set -euo pipefail
LOCK="${1:-/repo/VERSIONS.lock}"

PKGS=(
  ros-jazzy-rmw-fastrtps-cpp
  ros-jazzy-rmw-cyclonedds-cpp
  ros-jazzy-rmw-zenoh-cpp
  ros-jazzy-example-interfaces
  ros-jazzy-rqt-graph
  graphviz
)

{
  echo "[apt-packages]   # captured inside the built image via dpkg-query"
  for p in "${PKGS[@]}"; do
    v="$(dpkg-query -W -f='${Version}' "$p" 2>/dev/null || echo 'NOT-INSTALLED')"
    printf '%-34s = %s\n' "$p" "$v"
  done
  echo
  echo "[rmw-available]  # RMW implementations present in the image"
  # ros2 doctor lists the discovered middleware; best-effort, never fails the build.
  ros2 doctor --report 2>/dev/null \
    | awk 'tolower($0) ~ /middleware/ {print "  " $0}' \
    || echo "  (ros2 doctor unavailable)"
  echo
  echo "[captured-in-image-at] $(date -u +%FT%TZ)"
} >> "${LOCK}"

echo "==> appended installed package versions to ${LOCK}"
