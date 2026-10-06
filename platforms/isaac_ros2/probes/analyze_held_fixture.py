"""[ENGINEERING] 流式同一步持件诊断汇总；没有TCP力/事件时钟等价声明。"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from held_fixture_diagnostics import held_cube_index


def summarize(rows):
    groups = {}
    last_step = last_stamp = None
    count = 0
    for row in rows:
        p = row['physics']
        step, stamp = p['physics_step'], p['stamp_ns']
        if last_step is not None and (step != last_step + 1 or stamp <= last_stamp):
            raise ValueError('Held stream skipped or repeated a physics step')
        for key in ('tools_physics', 'robots_physics', 'collision_contacts', 'robot_collision_contacts'):
            if (row[key]['physics_step'], row[key]['stamp_ns']) != (step, stamp):
                raise ValueError('Mixed contact/pose physics step')
        phase = row['phase_received_async']
        index = held_cube_index(phase)
        if index is None:
            raise ValueError('Unknown held phase')
        cube = p['bodies'][index]['position_m']
        if not all(math.isfinite(v) for v in cube):
            raise ValueError('Nonfinite Cube pose')
        group = groups.setdefault(phase, {'samples': 0, 'first_step': step,
            'first_cube_m': cube, 'both_closed_samples': 0, 'max_raw_effort': {},
            'max_arm_tracking_error_deg': {}, 'collision_pairs': {}})
        group['samples'] += 1
        group['last_step'], group['last_cube_m'] = step, cube
        group['both_closed_samples'] += int(all(row['suction_closed'].values()))
        for side, values in row['articulations'].items():
            names = values['dof_names']
            fields = ('positions_rad', 'position_targets_rad', 'projected_joint_effort_raw', 'velocities_rad_s')
            if any(len(values[f]) != len(names) or not all(math.isfinite(v) for v in values[f]) for f in fields):
                raise ValueError('Invalid articulation vectors')
            joint = max(range(len(names)), key=lambda j: abs(values['projected_joint_effort_raw'][j]))
            peak = abs(values['projected_joint_effort_raw'][joint])
            old = group['max_raw_effort'].get(side, {'abs_value': -1})
            if peak > old['abs_value']:
                group['max_raw_effort'][side] = {'abs_value': peak, 'joint': names[joint],
                    'physics_step': step, 'cube_m': cube, 'suction_closed': row['suction_closed']}
            arm = [j for j, name in enumerate(names) if 'finger' not in name]
            error = max(abs(values['positions_rad'][j] - values['position_targets_rad'][j]) for j in arm) * 180 / math.pi
            group['max_arm_tracking_error_deg'][side] = max(error, group['max_arm_tracking_error_deg'].get(side, 0))
        for key in ('collision_contacts', 'robot_collision_contacts'):
            for pair in row[key]['pairs']:
                force = math.hypot(*pair['collision_force_world_n'])
                if not math.isfinite(force):
                    raise ValueError('Nonfinite contact force')
                if pair['normal_contact_count'] or pair['friction_anchor_count'] or force:
                    name = pair['sensor_path'] + ' <-> ' + pair['other_path']
                    record = group['collision_pairs'].setdefault(name, {'samples': 0, 'peak_force_n': 0})
                    record['samples'] += 1
                    if force >= record['peak_force_n']:
                        record.update(peak_force_n=force, peak_step=step,
                                      force_world_n=pair['collision_force_world_n'])
        last_step, last_stamp, count = step, stamp, count + 1
    if not count:
        raise ValueError('No held physics samples; cannot validate record integrity')
    return {'samples': count, 'phases': groups, 'integrity_errors': 0,
        'boundary': 'Phase tags asynchronous; within rows physics pose/contact/DOF synchronous. '
        'Contact force excludes D6 wrench; raw revolute effort Nm/prismatic N, not calibrated TCP wrench. '
        'No physical task PASS is inferred from diagnostic completeness.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stream', type=Path)
    args = parser.parse_args()
    with args.stream.open() as source:
        print(json.dumps(summarize(json.loads(line) for line in source if line.strip()), indent=2, sort_keys=True))
