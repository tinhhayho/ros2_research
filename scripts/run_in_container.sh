#!/usr/bin/env bash
#
# run_in_container.sh — run a command inside the `ws` service with ROS 2 sourced.
# Honors RMW_IMPLEMENTATION and ROS_DOMAIN_ID from the caller's environment.
#
# Usage: scripts/run_in_container.sh 'ros2 node list'
set -euo pipefail
cd "$(dirname "$0")/.."

exec docker compose -f docker/docker-compose.yml run --rm -T \
  ${RMW_IMPLEMENTATION:+-e RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}} \
  ${ROS_DOMAIN_ID:+-e ROS_DOMAIN_ID=${ROS_DOMAIN_ID}} \
  ws bash -lc "$*"
