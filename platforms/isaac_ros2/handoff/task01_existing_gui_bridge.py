"""[ENGINEERING] 手动 Play 后在 Script Editor 执行；保留非阻塞 session。

仅复用现有 TASK01 单 Cube bridge/初始化协议；不自动运行 MoveIt driver。
输出目录按显式加载生成一次，旧 evidence 不覆盖；没有自动重载/重试。
"""
import sys
from datetime import datetime
from pathlib import Path

_task01_root = Path("/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction")
_task01_handoff_path = _task01_root / "platforms/isaac_ros2/handoff"
if str(_task01_handoff_path) not in sys.path:
    sys.path.insert(0, str(_task01_handoff_path))
from task01_existing_gui_session import start_bridge

_task01_output = _task01_root / "results" / (
    datetime.now().strftime("%Y%m%d_%H%M%S_%f") + "_TASK01_existing_gui_handoff01")
start_bridge(_task01_output, wall_limit_sec=180.0, launch_driver=False)
