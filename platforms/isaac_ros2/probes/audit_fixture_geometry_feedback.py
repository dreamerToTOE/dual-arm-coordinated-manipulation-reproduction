"""[ENGINEERING] Replay controller atomic-stamp geometry against exact held row.

No nearest-wall-clock joining; unmatched stamps fail. Not physics task acceptance.
"""
import argparse
import json
import math
from pathlib import Path
import re

TASKS = ('task27_plus_outer', 'task27_minus_outer', 'task27_plus_inner')
PATTERN = re.compile(r'(task27_\w+) (.+) rear=\w+ side=\w+ rear_gap=([-\d.]+) mm '
    r'side_gap=([-\d.]+) mm alignment=([-\d.]+) mm tilt=([-\d.]+) deg\. physics_stamp_ns=(\d+)')


def gaps(cube, rear, side, direction):
    c, r, s = (v['position_m'] for v in (cube, rear, side))
    alignment = max(abs(r[1]-c[1]), abs(r[2]-c[2]), abs(s[0]-c[0]), abs(s[2]-c[2]))
    tilt = math.degrees(2*math.acos(min(1., abs(cube['quaternion_xyzw'][3]))))
    result = [(c[0]-r[0]-.06)*1000, (direction*(c[1]-s[1])-.06)*1000,
              alignment*1000, tilt]
    if not all(math.isfinite(v) for v in result):
        raise ValueError('Nonfinite replay geometry')
    return result


def audit(controller_text, rows):
    requests = []
    for m in PATTERN.finditer(controller_text):
        if m[1] not in TASKS:
            raise ValueError('Unknown task')
        requests.append({'task': m[1], 'label': m[2], 'stamp_ns': int(m[7]),
                         'logged': [float(m[i]) for i in range(3, 7)]})
    if not requests:
        raise ValueError('No atomic-stamp controller observations')
    stamps = {r['stamp_ns'] for r in requests}
    snapshots = {}
    for row in rows:
        stamp = row['physics']['stamp_ns']
        if stamp not in stamps:
            continue
        if stamp in snapshots:
            raise ValueError('Duplicate selected physical stamp')
        if row['tools_physics']['stamp_ns'] != stamp:
            raise ValueError('Mixed Cube/TCP physical timestamp')
        snapshots[stamp] = row
    if set(snapshots) != stamps:
        raise ValueError(f'Missing exact physical stamps: {sorted(stamps-set(snapshots))}')
    maximum = 0.
    for request in requests:
        row = snapshots[request['stamp_ns']]
        index = TASKS.index(request['task'])
        cube = row['physics']['bodies'][index]
        side, rear, direction = ('right', 'left', -1) if index == 1 else ('left', 'right', 1)
        values = gaps(cube, row['tcp_poses_world_from_physics_link8'][rear],
                      row['tcp_poses_world_from_physics_link8'][side], direction)
        delta = max(abs(a-b) for a, b in zip(values, request['logged']))
        if delta > .000501:
            raise ValueError(f'Logged geometry does not match exact physical snapshot: {request}')
        maximum = max(maximum, delta)
        request['same_step_values'] = values
        request['physics_step'] = row['physics']['physics_step']
    return {'status': 'PASS_EXACT_STAMP_GEOMETRY_ONLY', 'observations': requests,
            'maximum_print_rounding_difference_mm_or_deg': maximum,
            'boundary': 'No delivery-clock nearest join, no force/task-success inference'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('controller', type=Path)
    parser.add_argument('held_stream', type=Path)
    args = parser.parse_args()
    with args.held_stream.open() as source:
        print(json.dumps(audit(args.controller.read_text(),
            (json.loads(line) for line in source if line.strip())), indent=2))
