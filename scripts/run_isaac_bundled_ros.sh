#!/usr/bin/env bash
# 使用 Isaac 自带 Humble，清除父终端继承的系统 ROS Python/库路径。
# 保留 ROS_DOMAIN_ID 等通信设置；外部 ROS 终端仍使用 /opt/ros/humble。
set -euo pipefail
task_isaac_root="${ISAACSIM_ROOT:-/home/ubuntu2004/isaacsim-4.5.0}"
if [[ ! -x "${task_isaac_root}/python.sh" ]]; then
  printf 'Isaac python.sh not found: %s\n' "${task_isaac_root}" >&2
  exit 1
fi
exec env -u AMENT_PREFIX_PATH -u COLCON_PREFIX_PATH -u CMAKE_PREFIX_PATH \
  -u PYTHONPATH -u ROS_DISTRO -u ROS_VERSION -u ROS_PYTHON_VERSION \
  -u ROS_PACKAGE_PATH \
  RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
  LD_LIBRARY_PATH="${task_isaac_root}/exts/isaacsim.ros2.bridge/humble/lib" \
  "${task_isaac_root}/python.sh" "$@"
