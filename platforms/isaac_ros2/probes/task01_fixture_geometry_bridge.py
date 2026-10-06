"""Isaac Script Editor bootstrap AFTER original Task27 bridge, while PLAYING.

[ENGINEERING] Only adds atomic physics feedback; never replaces original topics.
"""
import builtins
import sys
from pathlib import Path
sys.path.insert(0, '/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2')
from fixture_geometry_stream import FixtureGeometryPublisher
bridge = getattr(builtins, '_task26_batched_feed_bridge', None)
if bridge is None or not bridge.cube_paths[0].startswith('/World/Task27/'):
    raise RuntimeError('先加载 Task27 场景与原 bridge，并按 PLAY。')
old = getattr(builtins, '_task01_fixture_geometry', None)
if old is not None:
    old.close()
# Read fixed local TCP dimensions from the existing stage, not new tool design.
tcp = bridge.stage.GetPrimAtPath('/World/left_fr3/fr3_link8/side_suction_tool/side_suction_tcp')
from pxr import UsdGeom
translation = UsdGeom.Xformable(tcp).GetLocalTransformation().ExtractTranslation()
other = bridge.stage.GetPrimAtPath('/World/right_fr3/fr3_link8/side_suction_tool/side_suction_tcp')
right = UsdGeom.Xformable(other).GetLocalTransformation().ExtractTranslation()
if abs(translation[0]) > 1e-8 or abs(right[0]) > 1e-8 or abs(translation[1] + right[1]) > 1e-8 or abs(translation[2] - right[2]) > 1e-8:
    raise RuntimeError('Existing fixed TCP offsets do not match mirrored tool contract')
signs = {'left': 1 if translation[1] > 0 else -1,
         'right': 1 if right[1] > 0 else -1}
builtins._task01_fixture_geometry = FixtureGeometryPublisher(bridge, bridge.cube_paths,
    {'tcp_y': abs(float(translation[1])), 'vertical_drop_z': float(translation[2]),
     'branch_sign': signs})
print('TASK01 atomic fixture geometry ready: /task01/physics/fixture_geometry')
