#!/usr/bin/env bash
# 仅 inferior 使用 SDK 环境；GDB 本身不加载 Isaac/ROS 的库和 Python 路径。
set -eo pipefail
task_isaac_root="${ISAACSIM_ROOT:-/home/ubuntu2004/isaacsim-4.5.0}"
task_repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# != 1 || ! -d "$1" || -z "${DISPLAY:-}" ]]; then
  printf 'Usage: visible DISPLAY + bash %s existing-run-directory\n' "$0" >&2
  exit 2
fi
# 清除与原 bundled ROS launcher 相同的父终端路径，直接使用 SDK setup。
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH PYTHONPATH
unset ROS_DISTRO ROS_VERSION ROS_PYTHON_VERSION ROS_PACKAGE_PATH LD_PRELOAD
export PYTHONPATH=""
export LD_LIBRARY_PATH="${task_isaac_root}/exts/isaacsim.ros2.bridge/humble/lib"
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export CARB_APP_PATH="${task_isaac_root}/kit"
export ISAAC_PATH="${task_isaac_root}"
export EXP_PATH="${task_isaac_root}/apps"
source "${task_isaac_root}/setup_python_env.sh"
export RESOURCE_NAME=IsaacSim
task_gdb_args=(
  -nx -batch
  -iex "set debuginfod enabled off"
  -iex "set auto-load python-scripts off"
  -iex "set auto-load gdb-scripts off"
  -iex "set auto-load local-gdbinit off"
  -iex "set environment PYTHONPATH ${PYTHONPATH}"
  -iex "set environment LD_LIBRARY_PATH ${LD_LIBRARY_PATH}"
  -iex "set exec-wrapper env LD_PRELOAD=${task_isaac_root}/kit/libcarb.so"
  -x "${task_repo_root}/platforms/isaac_ros2/handoff/startup_stack_capture.gdb"
  --args "${task_isaac_root}/kit/python/bin/python3"
  "${task_repo_root}/platforms/isaac_ros2/handoff/task01_startup_debug_launcher.py"
  --run-dir "$1"
)
exec env -u LD_LIBRARY_PATH -u PYTHONPATH -u LD_PRELOAD /usr/bin/gdb "${task_gdb_args[@]}"
