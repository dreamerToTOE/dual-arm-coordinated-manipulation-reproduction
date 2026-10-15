"""Explicit hand-selected analytic RSS diagnostic; no IK/FK/model invocation.

This evaluates an elementary closed-form necessary condition, and up to the
first three angle identities, for one declared passive tuple. It is not one of
the frozen 100 samples, an execution retry or a certified closed-chain target.
"""
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def wrap(a):
    if a > math.pi: a -= 2*math.pi
    if a < -math.pi: a += 2*math.pi
    return a


def diagnostic():
    alpha = math.atan2(302., 70.)
    l34 = math.hypot(302., 70.)
    extension = 270.+l34
    q2_passive = 1.2
    delta = q2_passive-alpha
    out = {
        'schema': 'P4_R2_POST_RUN_HAND_SELECTED_ANALYTIC_CANDIDATE_V1',
        'scope': 'One explicitly selected point; elementary algebra only; no IK/FK, RNG or planning',
        'changes_original_fixed_0_of_100': False,
        'passive_q_rad': [0., q2_passive, -alpha, .48, 0., -.31],
        'source_base2_yaw_rad': 3.1416,
        'source_bounds_first3_rad': [[-165*3.1416/180, 165*3.1416/180],
                                     [-110*3.1416/180, 110*3.1416/180],
                                     [-110*3.1416/180, 70*3.1416/180]],
        'annulus_mm': [abs(270.-l34), 270.+l34],
        'environments': {},
    }
    for env, d, rod in [('II', 900., 300.), ('III', 1200., 500.)]:
        # Elbow alignment makes the two arm segments collinear. Wrist q5=0
        # keeps their terminal x direction independent of q4 and q6.
        local_x = extension*math.sin(q2_passive)+(264.+rod)*math.cos(delta)
        local_z = extension*math.cos(q2_passive)-(264.+rod)*math.sin(delta)
        w = [d+math.cos(3.1416)*local_x, math.sin(3.1416)*local_x, local_z]
        distance = math.sqrt(sum(v*v for v in w))
        cosine = (distance*distance-270.**2-l34**2)/(2*270.*l34)
        first3 = []
        for shoulder in (0, 1):
            q1 = wrap(math.atan2(w[1], w[0])+shoulder*math.pi)
            radial = w[0]*math.cos(q1)+w[1]*math.sin(q1)
            for elbow_sign in (1, -1):
                q3 = wrap(-(elbow_sign*math.acos(cosine)+alpha))
                a = 270.+l34*math.cos(q3+alpha)
                b = l34*math.sin(q3+alpha)
                q2 = wrap(math.atan2(radial, w[2])-math.atan2(b, a))
                angles = [q1, q2, q3]
                bound_ok = [lo <= v <= hi for v, (lo, hi) in
                            zip(angles, out['source_bounds_first3_rad'])]
                first3.append({'shoulder_pi_added': bool(shoulder), 'elbow_sign': elbow_sign,
                               'first3_angle_identity_rad': angles,
                               'source_first3_bounds_by_joint': bound_ok,
                               'source_first3_bounds_all_satisfied': all(bound_ok)})
        out['environments'][env] = {
            'source_d_mm': d, 'source_rod_length_mm': rod,
            'active_shoulder_to_wrist_vector_mm': w,
            'active_shoulder_to_wrist_distance_mm': distance,
            'cosine_law_factor': cosine,
            'annulus_necessary_condition': out['annulus_mm'][0] <= distance <= out['annulus_mm'][1],
            'first3_identity_candidates': first3,
            'full_active_ik': 'NOT_EXECUTED', 'wrist_bounds': 'NOT_CHECKED',
            'physical_closure': 'NOT_EXECUTED', 'collision_and_RBS': 'NOT_EXECUTED',
            'classification': 'ANALYTIC_WITNESS_CANDIDATE_ONLY',
        }
    return out


if __name__ == '__main__':
    result = diagnostic()
    output = ROOT/'reports/P4_FULL_R2_RSS_ANALYTIC_WITNESS_CANDIDATE.json'
    with output.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({'output': str(output), 'environments': {
        k: {'D_mm': v['active_shoulder_to_wrist_distance_mm'], 'cosine_law_factor': v['cosine_law_factor'],
            'first3_legal_count': sum(x['source_first3_bounds_all_satisfied'] for x in v['first3_identity_candidates'])}
        for k, v in result['environments'].items()}}, ensure_ascii=False))
