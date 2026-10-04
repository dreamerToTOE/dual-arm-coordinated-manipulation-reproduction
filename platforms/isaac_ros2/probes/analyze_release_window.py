#!/usr/bin/env python3
"""[ENGINEERING] 分阶段保留释放窗口真实位移/接触，标签只代表异步收到时刻。"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_diagnostics import active_cube_index


def summarize(rows):
    grouped = defaultdict(list)
    for row in rows:
        phase = row['phase_received_async']
        index = active_cube_index(phase)
        if index is None:
            raise ValueError('Unexpected phase in release-only stream')
        physics, tools = row['physics'], row['tools_physics']
        if (physics['stamp_ns'], physics['physics_step']) != (tools['stamp_ns'], tools['physics_step']):
            raise ValueError('Mixed physics step')
        if any(not math.isfinite(x) for body in physics['bodies'] for x in body['position_m']):
            raise ValueError('Nonfinite position')
        grouped[phase].append((row, index))
    phases = []
    for phase, samples in grouped.items():
        first, index = samples[0]
        last = samples[-1][0]
        bodies = [row['physics']['bodies'][index] for row, _ in samples]
        positions = [body['position_m'] for body in bodies]
        entry = {
            'phase_received_async': phase, 'samples': len(samples),
            'first_stamp_s': first['physics']['stamp_ns'] / 1e9,
            'last_stamp_s': last['physics']['stamp_ns'] / 1e9,
            'first_position_m': positions[0], 'last_position_m': positions[-1],
            'delta_mm': [1000 * (positions[-1][i] - positions[0][i]) for i in range(3)],
            'range_mm': [1000 * (max(p[i] for p in positions) - min(p[i] for p in positions)) for i in range(3)],
            'max_linear_speed_m_s': max(math.hypot(*body['linear_velocity_m_s']) for body in bodies),
            'first_closed': first['suction_closed'], 'last_closed': last['suction_closed'],
            'tool_tcp_delta_mm': {
                side: [1000 * (last['tcp_poses_world_from_physics_link8'][side]['position_m'][i] -
                               first['tcp_poses_world_from_physics_link8'][side]['position_m'][i]) for i in range(3)]
                for side in ('left', 'right')},
            'collision_pairs': {},
        }
        pairs = defaultdict(list)
        for row, _ in samples:
            for pair in row['collision_contacts']['pairs']:
                pairs[pair['other_path']].append(pair)
        for path, contacts in pairs.items():
            forces = [pair['collision_force_world_n'] for pair in contacts]
            entry['collision_pairs'][path] = {
                'max_force_norm_n': max(math.hypot(*force) for force in forces),
                'mean_force_world_n': [sum(f[i] for f in forces) / len(forces) for i in range(3)],
                'max_reported_normal_contacts': max(pair['normal_contact_count'] for pair in contacts),
            }
        phases.append(entry)
    return {'phases': phases, 'samples': sum(len(v) for v in grouped.values()),
            'boundary': 'Async phase-arrival labels; object/tool poses share the physics step. '
                        'Collision impulses are not suction D6 or calibrated TCP wrench. '
                        'Diagnostic hold changes timing and is not normal benchmark PASS.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stream', type=Path)
    args = parser.parse_args()
    # 输出到 stdout；由调用方保存所需摘要。完整坏行会报错，不静默忽略采样损坏。
    with args.stream.open() as source:
        result = summarize(json.loads(line) for line in source if line.strip())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
