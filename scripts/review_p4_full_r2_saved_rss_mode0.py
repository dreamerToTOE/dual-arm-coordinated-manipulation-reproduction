"""Prove reach rejection from already saved RSS mode0 target matrices.

No IK/FK/NR function is called or imported.  No target or sample is generated.
Only base removal, terminal-offset subtraction, distances, cosine-law necessary
conditions and existing source joint bounds are evaluated on saved evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
R2_RUN = ROOT/'results/p4_full/20261015_R2_RSS_CONSTRUCTION01'
AUTHOR_PI = 3.1416
BOUNDS = [[a*AUTHOR_PI/180, b*AUTHOR_PI/180] for a, b in
          [[-165, 165], [-110, 110], [-110, 70], [-160, 160], [-120, 120], [-400, 400]]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    paths = [p for p in R2_RUN.rglob('*') if p.is_file()]
    before = {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}
    execution = json.loads((R2_RUN/'execution.json').read_text())
    l2, l34 = 270., math.hypot(70., 149.6+152.4)
    near, far = abs(l2-l34), l2+l34
    alpha = math.atan2(302., 70.)
    out = {
        'schema': 'P4_D079_R2_SAVED_RSS_MODE0_REACH_REVIEW_V1',
        'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'Only saved target algebra; no kinematic solve, FK evaluation, RNG, collision or planner',
        'source_commit': execution['source_commit'],
        'addendum_sha256': execution['addendum_sha256'],
        'run': str(R2_RUN.relative_to(ROOT)),
        'constants': {'l2_mm': l2, 'l34_mm': l34, 'terminal_x_offset_mm': 132.,
                      'shoulder_height_mm': 290., 'straight_elbow_rad': -alpha,
                      'source_pi_literal': AUTHOR_PI, 'source_joint_bounds_rad': BOUNDS,
                      'minimum_shoulder_wrist_distance_mm': near,
                      'maximum_shoulder_wrist_distance_mm': far},
        'environments': {},
    }
    for env, d in [('II', 900.), ('III', 1200.)]:
        rows = json.loads((R2_RUN/env/'observations.json').read_text())
        mode0 = [r for r in rows if r['mode'] == 0]
        assert len(mode0) == 800
        groups = {}
        for r in mode0:
            groups.setdefault(r['source_index'], []).append(r)
        assert len(groups) == 100
        derived, counts = [], Counter()
        for idx, rr in sorted(groups.items()):
            assert sorted(r['branch'] for r in rr) == list(range(8))
            r = rr[0]
            assert all(v['active_target'] == r['active_target'] for v in rr)
            assert all(v['forced_passive_q_rad'] == r['forced_passive_q_rad'] for v in rr)
            assert not any(v['native_active_ik']['success'] for v in rr)
            target = r['active_target']
            # Active source base is [-D/2, 0, 0] with yaw zero.  All rotations
            # of the passive approximate-pi base remain encoded in the data.
            local_p = [target[0][3]+d/2, target[1][3], target[2][3]]
            wrist = [local_p[i]-132.*target[i][0] for i in range(3)]
            relative = [wrist[0], wrist[1], wrist[2]-290.]
            distance = math.sqrt(sum(v*v for v in relative))
            cosine = (distance*distance-l2*l2-l34*l34)/(2*l2*l34)
            too_far = distance > far
            too_near = distance < near
            counts['targets_above_maximum_distance'] += too_far
            counts['targets_below_minimum_distance'] += too_near
            counts['targets_with_real_elbow_triangle'] += not (too_far or too_near)
            qp = r['forced_passive_q_rad']
            assert qp[2] == -alpha and qp[4] == 0.
            violations = [{'joint': j+1, 'value_rad': v, 'lower_rad': lo, 'upper_rad': hi}
                          for j, (v, (lo, hi)) in enumerate(zip(qp, BOUNDS)) if not lo <= v <= hi]
            counts['forced_passive_source_limits_legal'] += not violations
            counts['passive_rank_deficient'] += r['passive_rank'] < 6
            # This is the exact shoulder-angle necessary bound, not a returned
            # joint solution or call to an IK kernel.  The geometric failure
            # makes downstream q2/q3/wrist reconstruction unnecessary.
            q1s = []
            for b in range(8):
                q1 = math.atan2(wrist[1], wrist[0])+(math.pi if b >= 4 else 0.)
                if q1 > math.pi: q1 -= 2*math.pi
                if q1 < -math.pi: q1 += 2*math.pi
                shoulder_legal = BOUNDS[0][0] <= q1 <= BOUNDS[0][1]
                counts['branches_shoulder_limit_rejected_first'] += not shoulder_legal
                counts['branches_shoulder_legal_but_distance_unreachable'] += shoulder_legal and (too_far or too_near)
                q1s.append({'branch': b, 'shoulder_azimuth_rad': q1,
                            'source_q1_bound_satisfied': shoulder_legal})
            derived.append({
                'source_index': idx, 'saved_active_target': target,
                'wrist_center_in_active_base_mm': wrist,
                'shoulder_to_wrist_vector_mm': relative,
                'shoulder_to_wrist_distance_mm': distance,
                'excess_above_max_reach_mm': distance-far,
                'cosine_law_factor': cosine,
                'real_elbow_triangle_exists': not (too_far or too_near),
                'source_passive_joint_limits_legal': not violations,
                'source_passive_limit_violations': violations,
                'passive_rank': r['passive_rank'],
                'active_shoulder_bounds_by_branch': q1s,
                'active_elbow_q3_bound': 'NOT_REACHED_NO_REAL_TRIANGLE',
                'active_shoulder_elevation_q2_bound': 'NOT_REACHED_NO_REAL_TRIANGLE',
                'active_wrist_q4_q5_q6_bounds': 'NOT_REACHED_NO_REAL_TRIANGLE',
                'native_rejection_reason_recorded': 'ACTIVE_IK_REJECTED',
            })
        out['environments'][env] = {
            'source_base1': [-d/2, 0., 0.],
            'target_count': len(groups), 'native_branch_attempts_already_run': len(mode0),
            'counts': dict(counts),
            'distance_range_mm': [min(r['shoulder_to_wrist_distance_mm'] for r in derived),
                                  max(r['shoulder_to_wrist_distance_mm'] for r in derived)],
            'cosine_law_factor_range': [min(r['cosine_law_factor'] for r in derived),
                                       max(r['cosine_law_factor'] for r in derived)],
            'derived_targets': derived,
        }
    out['input_sha256'] = before
    out['all_input_bytes_unchanged_by_review'] = all(sha(ROOT/p) == h for p, h in before.items())
    assert out['all_input_bytes_unchanged_by_review']
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', default='reports/P4_FULL_R2_RSS_MODE0_SAVED_TARGET_REVIEW.json')
    args = p.parse_args()
    result = run()
    with (ROOT/args.out).open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({e: {'counts': v['counts'], 'distance_range_mm': v['distance_range_mm'],
                         'cosine_law_factor_range': v['cosine_law_factor_range']}
                      for e, v in result['environments'].items()}, ensure_ascii=False))
