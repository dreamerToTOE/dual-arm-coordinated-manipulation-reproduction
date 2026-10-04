"""[ENGINEERING] 汇总第四件日志/稀疏 PhysX 采样，不标记基准冻结。"""
import argparse
import json
import math
import re
from pathlib import Path


def yaw_deg(q):
    x, y, z, w = q
    return math.degrees(math.atan2(2*(w*z+x*y), 1-2*(y*y+z*z)))


def half_y(q):
    x, y, z, w = q
    return .060 * (abs(2*(x*y+z*w)) + abs(1-2*(x*x+z*z)) + abs(2*(y*z-x*w)))


def preclose_metrics(text):
    """仅汇总实际日志；无纠偏行时不虚构耗时或误差来源。"""
    stats = []
    for row in re.findall(
            r'(task27_\w+) PRE_CLOSE_XYZ_STATS checks=(\d+) corrections=(\d+) '
            r'plan_wall_s=([\d.]+) execute_wall_s=([\d.]+) total_wall_s=([\d.]+) result=(PASS|FAIL)', text):
        name, checks, corrections, planning, execution, total, result = row
        stats.append({'object': name, 'checks': int(checks), 'corrections': int(corrections),
                      'plan_wall_s': float(planning), 'execute_wall_s': float(execution),
                      'total_wall_s': float(total), 'result': result})
    diagnostics = []
    for name, side, attempt, tracking, difference in re.findall(
            r'(task27_\w+) PRE_CLOSE_KINEMATICS side=(left|right) attempt=(\d+) .*?'
            r'tracking_mm=\(([^)]+)\) fk_isaac_mm=\(([^)]+)\)', text):
        vectors = [[float(v) for v in value.split(',')] for value in (tracking, difference)]
        if any(len(v) != 3 or not all(math.isfinite(x) for x in v) for v in vectors):
            raise ValueError('Invalid preclose diagnostic vector')
        diagnostics.append({'object': name, 'side': side, 'attempt': int(attempt),
                            'tracking_xyz_mm': vectors[0], 'fk_isaac_xyz_mm': vectors[1]})
    correction_norms = [float(v) for v in re.findall(
        r'PRE_CLOSE_XYZ_CORRECTION side=\w+ delta_mm=\([^)]+\) norm_mm=(\d+(?:\.\d+)?)', text)]
    return {'preclose_xyz_stats': stats, 'preclose_kinematics': diagnostics,
            'preclose_total_correction_plan_wall_s': sum(row['plan_wall_s'] for row in stats),
            'preclose_total_correction_execute_wall_s': sum(row['execute_wall_s'] for row in stats),
            'preclose_max_correction_norm_mm_printed': max(correction_norms, default=None),
            'preclose_max_tracking_norm_mm_printed': max(
                (math.hypot(*row['tracking_xyz_mm']) for row in diagnostics), default=None),
            'preclose_max_fk_isaac_norm_mm_printed': max(
                (math.hypot(*row['fk_isaac_xyz_mm']) for row in diagnostics), default=None)}


def summarize(run_dir):
    text = (run_dir / 'raw/controller.log').read_text(encoding='utf-8')
    audit_path = run_dir / 'raw/model_audit.json'
    preplaced_count = json.loads(audit_path.read_text()).get('preplaced_count') if audit_path.exists() else None
    metrics = {
        'fixture_preplaced_count': preplaced_count,
        'completed_batches': [int(n) for n in re.findall(r'Task27 batch (\d+) PASS:', text)],
        'cube04_inner_trim_command_lines': len(re.findall(r'task27_minus_inner INNER_(?:SIDE|EXTRA)_TRIM', text)),
        'cube04_precision_gate': re.findall(r'CUBE04_PRECISION_GATE: (.*)', text),
        'controller_final_geometry_lines': re.findall(r'task27_(?:minus_inner|center_insert) (?:final|center) Ground Truth: (.*)', text),
        'all_controller_final_geometry_lines': re.findall(
            r'(task27_(?:plus_outer|minus_outer|plus_inner|minus_inner|center_insert)) (?:final|center) Ground Truth: (.*)', text),
        'snapshots': 0, 'integrity_errors': [],
        'fourth_helper_closed_inside_samples': 0, 'fifth_helper_closed_inside_samples': 0}
    metrics.update(preclose_metrics(text))
    # ARRIVED 是供料状态，不是码垛成功；预置夹具也不能算五件实际执行。
    metrics['full_five_batch_completion_reported'] = (
        preplaced_count == 0 and metrics['completed_batches'] == [1, 2, 3, 4, 5])
    peaks = [float(v) for v in re.findall(r'PUSH slice .*?peak_torque=([\d.]+) Nm', text)]
    metrics['peak_push_joint_torque_nm_raw'] = max(peaks, default=None)
    last_step = last_stamp = latest = None
    ys, yaws = [], []
    with (run_dir / 'raw/physics_pose_samples.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            snapshot = row['physics']
            step, stamp = snapshot['physics_step'], snapshot['stamp_ns']
            if last_step is not None and (step-last_step != 6 or stamp <= last_stamp):
                metrics['integrity_errors'].append({'step': step, 'previous': last_step})
            bodies = snapshot['bodies']
            if len(bodies) != 5:
                raise ValueError('Wrong body count')
            for body in bodies:
                if not all(math.isfinite(v) for v in body['position_m']+body['quaternion_xyzw']):
                    raise ValueError('Nonfinite pose')
                if abs(math.sqrt(sum(v*v for v in body['quaternion_xyzw']))-1) > 1e-6:
                    raise ValueError('Nonunit quaternion')
            fourth, fifth = bodies[3], bodies[4]
            # 下一件供料前统计第四件，避免误计第五件双臂搬运的 CLOSED。
            if (preplaced_count is None or preplaced_count < 4) and row['feed_state'][4] == 0 and fourth['position_m'][0] >= .91:
                metrics['fourth_helper_closed_inside_samples'] += int(row['suction_closed']['right'])
                if row['suction_closed']['left']:
                    ys.append(fourth['position_m'][1]); yaws.append(yaw_deg(fourth['quaternion_xyzw']))
            if row['feed_state'][4] == 2 and fifth['position_m'][0] >= .91:
                metrics['fifth_helper_closed_inside_samples'] += int(row['suction_closed']['left'])
            last_step, last_stamp, latest = step, stamp, row
            metrics['snapshots'] += 1
    if latest is None:
        raise ValueError('No physical samples')
    bodies = latest['physics']['bodies']
    metrics['final_physical_poses'] = [{'path': b['prim_path'], 'position_m': b['position_m'],
        'quaternion_xyzw': b['quaternion_xyzw'], 'yaw_deg': yaw_deg(b['quaternion_xyzw'])} for b in bodies]
    outer, fourth = bodies[1], bodies[3]
    # 中途失败时第四件可能仍在桌下停车位，不能将其坐标差报成码垛间隙。
    neighbor_geometry_available = preplaced_count is None or (
        (preplaced_count >= 2 or 2 in metrics['completed_batches']) and
        (preplaced_count >= 4 or 4 in metrics['completed_batches']))
    metrics['cube04_neighbor_geometry_available'] = neighbor_geometry_available
    metrics['cube04_axis_center_neighbor_gap_mm'] = (
        1000*(fourth['position_m'][1]-outer['position_m'][1]-.120)
        if neighbor_geometry_available else None)
    metrics['cube04_oriented_projection_neighbor_gap_mm'] = (
        1000*(fourth['position_m'][1]-half_y(fourth['quaternion_xyzw'])-
              outer['position_m'][1]-half_y(outer['quaternion_xyzw']))
        if neighbor_geometry_available else None)
    if ys:
        metrics['cube04_insertion_y_span_mm'] = 1000*(max(ys)-min(ys))
        metrics['cube04_insertion_abs_yaw_max_deg'] = max(map(abs, yaws))
    metrics['boundary'] = (f'Fixture preplaced count={preplaced_count}; preplaced cubes are not executed; '
        'sparse readout is not force/reliability proof; projected gap is not PhysX penetration depth')
    return metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    result = summarize(args.run_dir)
    (args.run_dir / 'analysis.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'final_physical_poses'}, indent=2))
