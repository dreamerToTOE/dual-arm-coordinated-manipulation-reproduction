#!/usr/bin/env python3
"""Read-only reduction of saved B/Q2 q/J/events; never calls FK/IK/collision.

Polynomial extrapolation is explicitly an inference, not a new measured center
Jacobian or a continuous-path counterexample. Original evidence is immutable.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import time

for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
B = ROOT/'results/p4_full/20261015_R2_VI_RSS_RECONSTRUCTED01'
Q = ROOT/'results/p4_full/20261015_R2_VI_RSS_BRIDGE01'
REPORT = ROOT/'reports/P4_FULL_R2_VI_RSS_BRIDGE_ROOT_CAUSE_20261015'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime+r.ru_stime


def rank(matrix, rows):
    a = np.array(matrix, dtype=float); a[rows, :] *= .001
    sv = np.linalg.svd(a, compute_uv=False)
    return int(np.count_nonzero(sv > sv[0]*1e-6)), sv


def branch_set(q):
    radial = 524.5+1250*math.sin(q[1])+210*math.sin(q[1]+q[2])+1436.5*math.cos(q[1]+q[2])
    factors = [radial, -math.sin(q[2]+math.atan2(1436.5, 210.)), math.sin(q[4])]
    scales = [524.5+1250+math.hypot(210., 1436.5), 1., 1.]
    signs = [None if abs(v) <= 64*np.finfo(float).eps*s else (1 if v > 0 else -1)
             for v, s in zip(factors, scales)]
    elbow = (1, -1, 1, -1, 1, -1, 1, -1)
    wrist = (1, -1, -1, 1, -1, 1, 1, -1)
    labels = [i for i in range(8) if
              (signs[0] is None or (1 if i < 4 else -1) == signs[0]) and
              (signs[1] is None or elbow[i] == signs[1]) and
              (signs[2] is None or wrist[i] == signs[2])]
    return labels


def tree_nodes(node):
    yield node
    if 'left' in node:
        yield from tree_nodes(node['left']); yield from tree_nodes(node['right'])


def scaled(a):
    result = np.array(a, dtype=float); result[:3] *= .001
    return result


def zero_extrapolate(points):
    weights = [math.prod(-y/(x-y) for j, (y, _) in enumerate(points) if j != i)
               for i, (x, _) in enumerate(points)]
    return sum(w*a for w, (_, a) in zip(weights, points)), weights


def analyze():
    started, c0 = time.monotonic(), cpu()
    b = json.loads((B/'execution.json').read_text())
    q = json.loads((Q/'execution.json').read_text())
    events = [json.loads(line) for line in (Q/'events.jsonl').read_text().splitlines()]
    finished = [r for r in events if r['event'] == 'construction_finished']
    parent, center_js = {}, {}
    for line in (B/'events.jsonl').read_text().splitlines():
        row = json.loads(line)
        if row.get('construction') not in (219, 643): continue
        if row['event'] == 'construction_finished': parent[row['construction']] = row
        if row['event'] == 'designated_singular_fk_and_rank': center_js[row['construction']] = row
    inputs = [B/'execution.json', B/'events.jsonl', Q/'execution.json', Q/'events.jsonl',
              ROOT/'configs/p4_full/r2_vi_rss_reconstructed_qualification_v1.json',
              ROOT/'configs/p4_full/r2_vi_rss_bridge_qualification_v1.json',
              *sorted(Q.glob('ik_*.jsonl'))]
    bounds = np.tile(np.array([[-180, 180], [-60, 125], [-90, 75],
                               [-2700, 2700], [-120, 120], [-400, 400]])*3.1416/180, (3, 1))
    mismatch, rcounts, collision_counts, root_counts = [], Counter(), Counter(), Counter()
    maxsv, maxactive, margin = 0., 0., math.inf
    for row in finished:
        qn = np.array(row['q_rad']); margin = min(margin, float(np.min(np.minimum(qn-bounds[:, 0], bounds[:, 1]-qn))))
        j = np.array(row['physical_jacobian'])
        rf, svf = rank(j, [0, 1, 2, 6, 7, 8]); rp, svp = rank(j[:, 6:], [0, 1, 2, 6, 7, 8])
        rarms = [rank(k, [0, 1, 2])[0] for k in row['body_jacobians'][1:]]
        rcounts[str([rf, rp, *rarms])] += 1
        maxsv = max(maxsv, float(np.max(np.abs(svf-row['independent_world_residual_rank_report']['full']['singular_values']))),
                    float(np.max(np.abs(svp-row['independent_world_residual_rank_report']['passive']['singular_values']))))
        c = row['collision']; collision_counts[str([c['status'], c['collision'], c['manifest_sha256']])] += 1
        for arm, expected in row['required_branches'].items():
            actual = branch_set(qn[6*(int(arm)-1):6*int(arm)])
            if actual != [expected]: mismatch.append({'construction': row['construction'], 'arm': arm, 'actual': actual})
        for arm, roots in row['all_roots'].items():
            for root in roots:
                root_counts['requested'] += 1
                if root['native']['success']:
                    root_counts['accepted'] += 1
                    root_counts['accepted_branch_'+str(root['branch'])] += 1
                    if root['branch'] not in branch_set(root['native']['solution']):
                        mismatch.append({'construction': row['construction'], 'root_arm': arm, 'branch': root['branch']})
        if row['construction_kind'].startswith('RBS_'):
            raw = np.array(row['unprojected_full18_midpoint_q_rad'])
            maxactive = max(maxactive, float(np.max(np.abs(qn[:6]-raw[:6]))))
    half_results = []
    for fixture in q['fixture_results']:
        identity = fixture['parent_construction']; s = fixture['designated_passive_arm']
        original = np.array(parent[identity]['q_rad']); js = np.array(center_js[identity]['world_geometric_jacobian'])
        u, sigma, vh = np.linalg.svd(scaled(js)); null = u[:, -1]
        axis = js[3:, 3]
        quadrature = np.r_[np.cross(axis, js[:3, 4]), np.cross(axis, js[3:, 4])]
        # At a q5=0 X-Y-X wrist, q4+theta/q6-theta preserves the pose.
        # Its J5 rotates about joint4; this supplies the missing column direction.
        basis = scaled(np.column_stack((js[:, :3], js[:, 3], js[:, 4], quadrature)))
        for half in fixture['half_results']:
            negative = half['half'].startswith('negative'); tree = half['tree']
            endpoint = np.array(tree['endpoint_a_q_rad'] if negative else tree['endpoint_b_q_rad'])
            center = np.array(tree['endpoint_b_q_rad'] if negative else tree['endpoint_a_q_rad'])
            if not np.array_equal(center, original): raise ValueError('Original singular family changed')
            delta = endpoint[:6]-center[:6]; nodes = list(tree_nodes(tree))
            leaves = [n for n in nodes if 'left' not in n]
            ratios = [child['distance_full18_rad']/n['distance_full18_rad']
                      for n in nodes if 'left' in n for child in (n['left'], n['right'])]
            projected = []; direct_image = []
            for node in nodes:
                if 'projection' not in node: continue
                r = node['projection']; qp = np.array(r['q_rad'])
                lam = float(np.dot(qp[:6]-center[:6], delta)/np.dot(delta, delta))
                active = np.array(r['physical_jacobian'])[6*(s-2):6*(s-1), :6]
                projected.append((lam, active))
                direct_image.append({'node_id': node['node_id'], 'lambda': lam,
                    'saved_active_J_times_fixed_chord_target_twist': scaled(-active@delta).tolist(),
                    'projection_on_exact_saved_center_left_null': float(null@scaled(-active@delta)),
                    'scope': 'Exact operation on saved matrices at this node; not the unknown center active J.'})
            projected.sort(key=lambda x: x[0]); extrapolations = []
            for degree in range(1, 7):
                j0, weights = zero_extrapolate(projected[:degree+1])
                v = scaled(-j0@delta); coefficients = np.linalg.solve(basis, v)
                theta = math.atan(coefficients[5]/coefficients[4])
                extrapolations.append({'degree': degree, 'lambdas': [x for x, _ in projected[:degree+1]],
                    'weights': weights, 'inferred_center_active_J': j0.tolist(),
                    'image_projection_residual_signed': float(null@v),
                    'target_twist_norm': float(np.linalg.norm(v)),
                    'wrist_basis_coefficients': coefficients.tolist(),
                    'inferred_family_q4_offset_rad': theta, 'inferred_family_q6_offset_rad': -theta,
                    'inferred_family_full18_gap_rad': math.sqrt(2)*abs(theta),
                    'q5_derivative_sign_matches_half': bool((coefficients[4] < 0) == negative)})
            near = []; node = tree
            while 'projection' in node:
                r = node['projection']; qp = np.array(r['q_rad']); dq = qp-center
                near.append({'node_id': node['node_id'], 'depth': node['depth'],
                    'center_full18_distance_rad': float(np.linalg.norm(dq)),
                    'designated_delta_q4_q5_q6_rad': dq[6*(s-1):6*s][[3, 4, 5]].tolist(),
                    'projection_from_raw_midpoint_full18_rad': float(np.linalg.norm(qp-np.array(r['unprojected_full18_midpoint_q_rad']))),
                    'full18_q_delta': dq.tolist()})
                node = node['right' if negative else 'left']
            direct_q_limit = sum(weight*np.array(row['full18_q_delta']) for weight, row in zip((1/3, -2, 8/3), near))
            half_results.append({'fixture': identity, 'designated_arm': s, 'half': half['half'],
                'observed_root_full18_distance_rad': tree['distance_full18_rad'],
                'observed_leaf_full18_range_rad': [min(n['distance_full18_rad'] for n in leaves), max(n['distance_full18_rad'] for n in leaves)],
                'observed_leaf_status_counts': dict(Counter(n['status'] for n in leaves)),
                'observed_child_parent_distance_ratio_range': [min(ratios), max(ratios)],
                'center_adjacent_saved_chain': near, 'center_adjacent_leaf': node,
                'saved_center_J_singular_values': sigma.tolist(),
                'saved_center_J_joint4_minus_joint6_maxabs': float(np.max(np.abs(js[:, 3]-js[:, 5]))),
                'saved_center_J_right_null_vector': vh[-1].tolist(),
                'saved_center_J_left_null_vector_scaled': null.tolist(),
                'wrist_six_basis_condition': float(np.linalg.cond(basis)),
                'direct_saved_node_image_projections': direct_image,
                'inferred_center_extrapolations_not_new_measurements': extrapolations,
                'inferred_q_three_level_limit_delta': direct_q_limit.tolist(),
                'inferred_q_three_level_full18_gap_rad': float(np.linalg.norm(direct_q_limit)),
                'source_text_ordinary_audit': half['source_text_ordinary_audit'],
                'source_text_singular_audit': half['source_text_singular_audit'],
                'strict_passed': half['strict_discrete_passed']})
    result = {'schema': 'P4_R2_VI_RSS_SAVED_BRIDGE_ROOT_CAUSE_V1',
        'classification': 'OUR-RECONSTRUCTION / LOCAL-PROJECTION-CHART-DESIGN / EVIDENCE-SUPPORTED-HYPOTHESIS',
        'original_Q2_status_unchanged': q['coverage_gate_status'],
        'new_FK_IK_sampling_collision_candidate_planning_calls': 0,
        'source_sha256': sha(__file__), 'input_sha256': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        'direct_saved_evidence': {'started': sum(r['event'] == 'construction_started' for r in events),
            'finished': len(finished), 'continuous_construction_ids': [r['construction'] for r in finished] == list(range(1, 37)),
            'qualified_nodes': sum(r['qualified'] for r in finished), 'root_counts': dict(root_counts),
            'native_rows': dict(Counter(json.loads(line)['op'] for p in Q.glob('ik_*.jsonl') for line in p.read_text().splitlines())),
            'required_and_accepted_root_branch_mismatches': mismatch,
            'physical_recomputed_rank_counts_full_passive_arm2_arm3': dict(rcounts),
            'saved_spectra_reduction_maxabs_difference': maxsv,
            'collision_status_counts': dict(collision_counts), 'minimum_source_bounds_margin_rad': margin,
            'maximum_active_midpoint_difference_rad': maxactive,
            'closure_position_maxabs_mm': max(m['position_maxabs_mm'] for r in finished for m in r['physical_loop_metrics']),
            'closure_rotation_matrix_maxabs': max(m['rotation_matrix_maxabs'] for r in finished for m in r['physical_loop_metrics'])},
        'halves': half_results,
        'inference_boundary': 'B保存了指定奇异臂center J，未保存active1 center J；Q2内点保存J直接归约属观察值，degree1..6向center外推和fiber极限是数学推断。高阶外推一致不等于严格误差界。未证明全局不连续/全局不可规划，未验证新增fiber连接器。',
        'first_order_condition': '若固定active弦的被动解以有限导数到达原center，则目标一阶twist必须在其rank5 Jacobian像内。非零image residual排除该C1正则接近条件，不能排除非C1路线、别的主动曲线或奇异fiber自运动。',
        'fiber_hypothesis': 'q5=0时q4+theta/q6-theta保持同pose，但改变其J5方向。固定active直弦的姿态切向可选择与保存center不同的腕fiber极限；非canonical q4=0大跳。',
        'next_action': '先在既有B资格预算内部冻结2次固定active1 center FK/J诊断，直接测center image residual；候选数0，不消耗56，wall/CPU入B及R2账。禁止自动加深/缩delta/放宽h或换fixture。',
        'continuation_design_only': {
            'unchanged_straight_active_RBS': '不建议盲延伸。219两侧外推floor均高于h，故不能把原UNKNOWN归结为深度不足。643即便有限离散门有望通过，也不证明到原fiber的连续性。',
            'versioned_singular_fiber_connector': '若exact-center诊断支持，可另冻RECONSTRUCTED连接器：保留原center，验证每侧推得fiber endpoint及两者间q4/q6反向自运动，再从保存RBS叶接入匹配fiber。每个新点仍需闭合/分支集合/rank/原界/碰撞；禁止冒名作者原生RBS。',
            'nonlinear_active_curve': '另可由指定臂保持原q4/q6、以q5参数曲线导出active1/other根；现有±.005曲线点可保留，但不是原RBS直active中点法。另冻参数化局部连接器资格，不能称原source RBS。',
            'candidate_cost_forecast_not_authorization': {'blind_full_dyadic_leaf_extension': 64,
                'fiber_endpoint_and_fiber_midpoint_forecast': 6,
                'combined_dyadic_fiber_route_forecast': 70,
                'remaining_original_candidate_cap': 56, 'forecast_shortfall': 14,
                'cost_basis': '219每侧8叶约.0066–.0074，预计各需2层=24新中点/半；643每侧8叶约.0030–.0036，预计各需1层=8/半，共64；另4匹配fiber端点+219两条fiber内中点约6。仅预测，几何/碰撞或收缩失败会改变需要；不得自动新增14。',
                'full_parameter_curve_dyadic_forecast': 88,
                'wall_cpu_forecast_basis': 'Q2实际36构造/7.987086492wall/6.310368CPU；70构造线性估约15.53wall/12.27CPU，只是成本估计，不能当科学或预算保证。'}},
        'budget': {'B_plus_Q2_actual_wall_s': b['wall_s']+q['wall_s'],
            'B_plus_Q2_actual_cpu_s': b['cpu_s']+q['cpu_s'],
            'remaining_original_authorization_before_exact_diagnostic': q['authorization_budget_remaining'],
            'ledger_rule': 'Scientific ledger sums each execution wall_s/cpu_s once; never sum cumulative_execution values. This saved-only reduction is a separate analysis ledger, no new candidate denominator.'}}
    result['analysis_ledger'] = {'wall_s': time.monotonic()-started, 'cpu_s': cpu()-c0,
        'scope': 'Saved-file reads/hashes/linear algebra/report-data assembly only; excludes interpreter startup and final report serialization. No scientific model calls.',
        'candidate_constructions': 0, 'new_scientific_calls': 0}
    return result


def render(report):
    facts = report['direct_saved_evidence']; rows = []
    for half in report['halves']:
        inference = half['inferred_center_extrapolations_not_new_measurements'][-1]
        lo, hi = half['observed_leaf_full18_range_rad']
        rows.append(f"| {half['fixture']} / {half['half']} | {lo:.9f}–{hi:.9f} | {inference['image_projection_residual_signed']:.9g} | {inference['inferred_family_q4_offset_rad']:.11f} | {inference['inferred_family_full18_gap_rad']:.11f} |")
    return '\n'.join([
        '# P4 R2 VI RSS Q2 保存数据根因审查（2026-10-15）', '',
        '原Q2仍为 **UNKNOWN_OR_FAILED**，四条严格半桥均在depth3未达h=0.0025。根因分类为 **OUR-RECONSTRUCTION：固定主动直弦与奇异腕fiber选择的局部投影图问题（有证据假设）**，不是作者论文理论错误。没有重跑构造、FK、IK、采样或碰撞。', '',
        '## 直接保存证据', '',
        f"独立归约36/36节点资格通过：576个IK根请求、144个accepted根（branch1/3各72），36份原生FK输出，36次CHECKED且collision=false。所有required分支和accepted根几何身份均一致；保存Jacobian重SVD全部full12/passive12/arm2=6/arm3=6，谱逐值差{facts['saved_spectra_reduction_maxabs_difference']}。主动中点差{facts['maximum_active_midpoint_difference_rad']}rad，原界最小余量{facts['minimum_source_bounds_margin_rad']:.9f}rad，最大闭合位置{facts['closure_position_maxabs_mm']:.4g}mm、旋转矩阵{facts['closure_rotation_matrix_maxabs']:.4g}。", '',
        '远离奇异center的叶大致每层减半，但贴center链的q5减半时，q4/q6反向偏差逐步增大：219两侧在前三层约0.00090→0.00134→0.00156和0.00096→0.00145→0.00169rad；643约0.00082→0.00122→0.00142和0.00082→0.00123→0.00145rad。投影离原18维算术中点约0.00114–0.00137rad，没有随层数同比消失。保存center原q4/q6未变，也不是把q4重置为0。', '',
        '## 数学推断及证据界限', '',
        report['first_order_condition'], '',
        'B中心保存J的第4/6列相等到约1e−13，右零方向是q4/q6反向自运动。对Q2每半7个已存active Jacobian在λ=1/8…7/8进行degree1…6向center外推，再将固定active弦切向投影到B中心rank5像。下表残差与fiber偏移是**外推推断，不是新测center J**。degree4/5/6的偏移变化约1e−12rad；这证明数值稳定，不能替代严格外推误差界。', '',
        '| 固定fixture / 半桥 | 保存depth3叶距离rad | 推断image残差（m/rad缩放） | 推断q4 fiber偏移rad | 推断fiber gap rad |',
        '|---|---:|---:|---:|---:|', *rows, '',
        'fiber公式依据：q5=0的X-Y-X腕在q4+θ、q6−θ时保持末端pose；原J的1–4/6列不变，J5沿轴4旋转。将目标twist在六基[J1,J2,J3,J4,J5,a4×J5]中分解，可推得近邻θ。保存q的三层直接外推与此推断gap相差不超过约3e−8rad。219推断floor两侧均大于h，643两侧小于h，因此不能把四条UNKNOWN都说成仅深度不足。', '',
        report['inference_boundary'], '',
        '## 下一步与预算', '',
        report['next_action'], '',
        '若精确诊断支持该解释，单独冻结带版本的奇异fiber connector，或由原q4/q6固定的非线性active参数曲线。原center、原Q2树/UNKNOWN、δ和h均保留；新连接器必须明确RECONSTRUCTED，分别验证闭合、分支集合、奇异/常规秩、限位、源碰撞策略。两条路线都不是作者VI原生RBS，不证明全物理几何或连续无碰撞。', '',
        '现有32个未达h叶按普通减半估计，219需要再2层约48新中点，643需要再1层约16，共64；还未计入保留原center的fiber连接资格。fiber方案粗估再4个匹配端点与2个fiber中点，合计约70，较剩56多14。参数曲线均匀二分粗估88新构造。均为设计成本预测，未实施/未授权扩count，也不能保证修复成功；不以剩余预算逼迫改局部方法、缩δ、放宽h或换fixture。', '',
        f"原B+Q2实际耗{report['budget']['B_plus_Q2_actual_wall_s']:.12f}秒墙钟、{report['budget']['B_plus_Q2_actual_cpu_s']:.9f}秒CPU，余56构造、126.879319736墙钟、348.048457 CPU。两次exact-center诊断属于用户既有B资格预算内部数学诊断，候选0，墙钟/CPU仍须从以上余额扣并进R2账。科学账只加各execution实际wall_s/cpu_s，不能重复加cumulative字段。", '',
        f"本保存归约另列分析账：wall={report['analysis_ledger']['wall_s']:.9f}s、CPU={report['analysis_ledger']['cpu_s']:.9f}s；源码与所有输入SHA见同名JSON。", ''])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-prefix', type=Path, default=REPORT)
    args = parser.parse_args(); prefix = args.output_prefix.resolve()
    json_path, md_path = Path(str(prefix)+'.json'), Path(str(prefix)+'.md')
    if json_path.exists() or md_path.exists(): raise SystemExit('Refuse overwrite of existing report')
    report = analyze()
    with json_path.open('x') as stream: json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    with md_path.open('x') as stream: stream.write(render(report))
    print(json.dumps({'json': str(json_path), 'markdown': str(md_path),
                      'analysis_ledger': report['analysis_ledger'], 'new_scientific_calls': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
