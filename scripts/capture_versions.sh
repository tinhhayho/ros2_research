#!/usr/bin/env bash
#
# capture_versions.sh — resolve the base-image's immutable sha256 digest and start
# VERSIONS.lock. Runs on the HOST, before `docker compose build`.
#
# Writes:
#   docker/image.env   ROS_IMAGE=ros@sha256:<digest>   (consumed by the build as a build-arg)
#   VERSIONS.lock      header with the pinned digest    (package versions appended post-build)
set -euo pipefail
cd "$(dirname "$0")/.."

ROS_TAG="ros:jazzy-ros-base-noble"

echo "==> Pulling ${ROS_TAG} to resolve its immutable digest (no :latest, ever)..."
docker pull "${ROS_TAG}" >/dev/null

DIGEST="$(docker inspect --format '{{index .RepoDigests 0}}' "${ROS_TAG}")"
[ -n "${DIGEST}" ] || { echo "ERR: could not resolve a RepoDigest for ${ROS_TAG}" >&2; exit 1; }

echo "ROS_IMAGE=${DIGEST}" > docker/image.env

{
  echo "# VERSIONS.lock — REAL, captured by scripts/capture_versions.sh + capture_pkgs.sh."
  echo "# Regenerate with: make build.  No value here is hand-written."
  echo "# Reproducibility caveat: apt archives prune old versions over time, so the"
  echo "# base-image digest below is the PRIMARY anchor; the rest is a best-effort record."
  echo
  echo "[base-image]"
  echo "tag        = ${ROS_TAG}"
  echo "digest     = ${DIGEST}"
  echo "resolved_at = $(date -u +%FT%TZ)"
  echo "# ^ the Dockerfile builds FROM this digest (passed as the ROS_IMAGE build-arg)."
  echo
} > VERSIONS.lock

echo "==> wrote docker/image.env and VERSIONS.lock header."
echo "    ${DIGEST}"
