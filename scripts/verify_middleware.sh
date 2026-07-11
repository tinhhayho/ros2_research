#!/usr/bin/env bash
#
# verify_middleware.sh — Demo 3 acceptance (host side). Runs the in-container RMW-swap +
# interop + domain-isolation orchestration and checks the results doc landed on the host.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose -f docker/docker-compose.yml run --rm -T ws bash /repo/scripts/demo3_run.sh

test -s docs/05-rmw.md \
  || { echo "FAIL: docs/05-rmw.md not generated on host" >&2; exit 1; }
echo "==> Demo 3 verified. Results in docs/05-rmw.md, active-RMW report in docs/img/."
