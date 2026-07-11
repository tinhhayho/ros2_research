# syntax=docker/dockerfile:1
#
# ros2-explained — teaching image for the three core demos (Linux-native).
#
# The base is pinned by sha256 *digest* via the ROS_IMAGE build-arg, which
# scripts/capture_versions.sh resolves and records in VERSIONS.lock. It defaults
# to the tag so a first bootstrap build works before the lockfile exists.
ARG ROS_IMAGE=ros:jazzy-ros-base-noble
FROM ${ROS_IMAGE}

# --- teaching / runtime tooling + the two extra RMWs --------------------------
# Fast DDS (rmw_fastrtps_cpp) is already in ros-base. We add Cyclone DDS and Zenoh
# so Demo 3 can swap all three. example_interfaces provides BOTH AddTwoInts (srv)
# and Fibonacci (action) used by Demo 1 — no custom interface generation needed.
#
# Package versions are captured into VERSIONS.lock at build time (the base-image
# digest is the primary reproducibility anchor — see PLAN §4). No :latest, no
# blanket apt upgrade.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-jazzy-rmw-cyclonedds-cpp \
      ros-jazzy-rmw-zenoh-cpp \
      ros-jazzy-example-interfaces \
      ros-jazzy-rqt-graph \
      ros-jazzy-turtlesim \
      ros-jazzy-teleop-twist-keyboard \
      python3-colcon-common-extensions \
      graphviz \
      librsvg2-bin \
      xvfb \
      tmux \
      iproute2 \
      iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# The colcon workspace lives in the mounted repo at /repo/ws (see docker-compose.yml).
WORKDIR /repo/ws

# Source ROS + (when present) the workspace overlay for every interactive/login shell.
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc \
 && echo '[ -f /repo/ws/install/setup.bash ] && source /repo/ws/install/setup.bash' >> /root/.bashrc

# The official ros_entrypoint.sh already sources the ROS env before exec-ing the
# command, so `docker compose run ws <cmd>` sees the ros2 CLI without extra sourcing.
CMD ["bash"]
