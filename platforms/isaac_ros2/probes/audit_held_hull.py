"""[ENGINEERING] 原Isaac link7 authored convexHull与深墙的离线几何复核。

不是 PhysX cooked-hull/contact-offset 逆向、碰撞深度或连续执行安全证明。
输入是只读探针导出的精确双腕FK；不改碰撞几何，也不发送机器人命令。
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation


def common_ball_radius(points, position, quaternion, wall):
    """两凸集合交集内最大球半径；>0证明体积重叠，<0不叫欧式距离。"""
    points, position, quaternion, wall = map(np.asarray, (points, position, quaternion, wall))
    if (points.ndim != 2 or points.shape[1] != 3 or position.shape != (3,) or
            quaternion.shape != (4,) or wall.shape != (3, 2) or
            not all(np.isfinite(a).all() for a in (points, position, quaternion, wall)) or
            abs(np.linalg.norm(quaternion) - 1) > 1e-6 or np.any(wall[:, 1] <= wall[:, 0])):
        raise ValueError('Invalid recorded mesh/pose/wall')
    rotation = Rotation.from_quat(quaternion).as_matrix()
    world = points @ rotation.T + position
    equations = ConvexHull(points).equations
    normals = equations[:, :3] @ rotation.T
    # [ENGINEERING] LP中心变量用腕部附近坐标，避免世界系平面offset的消差。
    # 与原世界系不等式数学等价，不改变几何/重叠门限，witness最后转回世界系。
    offsets = equations[:, 3]
    a = np.c_[normals, np.ones(len(normals))]
    b = -offsets
    for axis, (lo, hi) in enumerate(wall):
        plane = np.zeros(4)
        plane[axis], plane[3] = 1, 1
        a, b = np.vstack([a, plane]), np.r_[b, hi-position[axis]]
        plane = np.zeros(4)
        plane[axis], plane[3] = -1, 1
        a, b = np.vstack([a, plane]), np.r_[b, position[axis]-lo]
    solution = linprog([0, 0, 0, -1], A_ub=a, b_ub=b,
                       bounds=[(None, None)] * 4, method='highs-ipm')
    if not solution.success or not np.isfinite(solution.x).all():
        raise ValueError(f'Geometry LP failed: {solution.status}: {solution.message}')
    violation = float(np.max(a @ solution.x - b))
    if violation > 1e-7 or (solution.x[3] > 0 and violation >= solution.x[3]):
        raise ValueError('Geometry LP returned an uncertified witness')
    return {'common_ball_radius_m': float(solution.x[3]),
            'deep_wall_x_plane_clearance_m': float(wall[0, 0] - world[:, 0].max()),
            'witness_center_m': (solution.x[:3]+position).tolist()}


def summarize_probe(lines, points, wall):
    phases, seen = {}, set()
    for line in lines:
        if not line.startswith('HELD_HULL_AUDIT '):
            continue
        tag, task, phase, index, arm, *pose = line.split()
        if arm not in ('left', 'right') or phase not in ('CONTACT', 'X', 'Y') or len(pose) != 7:
            raise ValueError('Malformed audit record')
        key = (task, phase, int(index), arm)
        if key in seen:
            raise ValueError('Repeated audit record')
        seen.add(key)
        values = [float(v) for v in pose]
        result = common_ball_radius(points, values[:3], values[3:], wall)
        name = f'{task}:{phase}:{arm}'
        group = phases.setdefault(name, {'samples': 0, 'overlapping_samples': 0,
            'max_common_ball_radius_mm': -math.inf, 'minimum_deep_wall_x_plane_clearance_mm': math.inf})
        group['samples'] += 1
        group['overlapping_samples'] += int(result['common_ball_radius_m'] > 0)
        group['max_common_ball_radius_mm'] = max(group['max_common_ball_radius_mm'],
                                                1000 * result['common_ball_radius_m'])
        group['minimum_deep_wall_x_plane_clearance_mm'] = min(
            group['minimum_deep_wall_x_plane_clearance_mm'],
            1000 * result['deep_wall_x_plane_clearance_m'])
    if not seen:
        raise ValueError('No exported wrist FK records')
    return {'samples': len(seen), 'phases': phases, 'boundary':
        'Discrete nominal FK / original authored link7 convex hull vs deep wall only. '
        'Not PhysX cooked mesh, contact offset, whole-robot or continuous tracking proof. '
        'Common-ball radius is not penetration depth or Euclidean distance. '
        'Full original robot/tool/Cube/table/other-wall FCL remains a separate gate.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('probe_log', type=Path)
    parser.add_argument('original_asset_mesh_json', type=Path)
    parser.add_argument('--all-walls', action='store_true',
                        help='Also audit original +/-Y walls; not a whole-robot physics guarantee')
    args = parser.parse_args()
    mesh = json.loads(args.original_asset_mesh_json.read_text())
    if mesh['attributes']['physics:approximation'] != 'convexHull':
        raise ValueError('Unexpected original asset approximation')
    # 原 Task27 深墙物理边界，出处 task26_truck_box_scene.py；不是新几何参数。
    wall = [(1.16, 1.18), (-.323, .323), (.2, .35)]
    if args.all_walls:
        # Exact original source: x0=.910, x1=1.160; Y inner +/-.303; thickness=.020.
        walls = {'WallDeep': wall,
                 'WallMinusY': [(.890, 1.180), (-.323, -.303), (.2, .35)],
                 'WallPlusY': [(.890, 1.180), (.303, .323), (.2, .35)]}
        lines = args.probe_log.read_text().splitlines()
        results = {}
        for name, bounds in walls.items():
            value = summarize_probe(lines, mesh['points'], bounds)
            results[name] = {'samples': value['samples'], 'overlapping_samples':
                sum(v['overlapping_samples'] for v in value['phases'].values()),
                'bounds_m': bounds, 'phases': {k: {'samples': v['samples'],
                    'overlapping_samples': v['overlapping_samples'],
                    'max_common_ball_radius_mm': v['max_common_ball_radius_mm']}
                    for k, v in value['phases'].items()}}
        result = {'walls': results, 'boundary': 'Discrete nominal original link7 authored convexHull only; '
            'LP radius is not penetration depth/distance, not PhysX cooked mesh/contact offsets, '
            'not whole-robot/continuous tracking or physical PASS.'}
    else:
        with args.probe_log.open() as stream:
            result = summarize_probe(stream, mesh['points'], wall)
    result.update(asset_sha256=mesh['asset_sha256'], wall_physical_bounds_m=wall)
    result['solver'] = 'SciPy HiGHS interior-point; identical recentered LP inequalities, witness residual checked'
    print(json.dumps(result, indent=2, sort_keys=True))
