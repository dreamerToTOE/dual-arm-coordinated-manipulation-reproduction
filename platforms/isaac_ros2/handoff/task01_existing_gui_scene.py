"""[ENGINEERING] Isaac GUI Script Editor: scene, then user Play, then bridge.

不创建新的 SimulationApp，不运行旧四/五 Cube 场景或控制器。
"""
import sys
from pathlib import Path

_task01_handoff_path = Path("/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/handoff")
if str(_task01_handoff_path) not in sys.path:
    sys.path.insert(0, str(_task01_handoff_path))
from task01_existing_gui_session import load_scene

load_scene()
