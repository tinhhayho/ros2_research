#!/usr/bin/env bash
#
# verify_basic.sh — Demo 1 acceptance (host side). Runs the in-container orchestration,
# then sanity-checks that the node-graph artifact actually landed on the host.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose -f docker/docker-compose.yml run --rm -T ws bash /repo/scripts/demo1_run.sh

test -s docs/img/demo1_node_list.txt \
  || { echo "FAIL: docs/img/demo1_node_list.txt missing on host" >&2; exit 1; }
echo "==> Demo 1 verified. Artifacts captured in docs/img/."
