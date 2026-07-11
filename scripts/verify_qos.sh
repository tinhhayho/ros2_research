#!/usr/bin/env bash
#
# verify_qos.sh — Demo 2 acceptance (host side). Runs the in-container QoS matrix and
# checks the results doc landed on the host.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose -f docker/docker-compose.yml run --rm -T ws bash /repo/scripts/qos_run.sh

test -s docs/03-qos.md \
  || { echo "FAIL: docs/03-qos.md not generated on host" >&2; exit 1; }
echo "==> Demo 2 verified. Results table in docs/03-qos.md."
