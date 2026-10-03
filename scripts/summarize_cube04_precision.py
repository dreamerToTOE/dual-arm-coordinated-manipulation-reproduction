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
        'snapshots': 0, 'integrity_errors': [],
        'fourth_helper_closed_inside_samples': 0, 'fifth_helper_closed_inside_samples': 0}
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
    metrics['cube04_axis_center_neighbor_gap_mm'] = 1000*(fourth['position_m'][1]-outer['position_m'][1]-.120)
    metrics['cube04_oriented_projection_neighbor_gap_mm'] = 1000*(fourth['position_m'][1]-half_y(fourth['quaternion_xyzw'])-outer['position_m'][1]-half_y(outer['quaternion_xyzw']))
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
