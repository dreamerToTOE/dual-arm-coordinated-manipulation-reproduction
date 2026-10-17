"""Independent, stdlib-only saved-data D080 overlay audit; no generator import."""
from pathlib import Path
from collections import Counter, defaultdict
import ast
import csv
import hashlib
import itertools
import json
import math
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[3]
STEM = ROOT / 'reports/P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_20261017'
SOURCE = 'reports/P4_FULL_R2_SBL_PCS_SETUP01_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv'
MATRIX = 'reports/P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017.csv'
MATRIX_MD = 'reports/P4_D080_ORIGINAL_VS_APPROVED_VS_ACTUAL_COVERAGE_20261017.md'
VALIDATION = 'reports/P4_D080_SCOPE_MAPPING_VALIDATION_20261017.json'
JOBS = 'configs/p4_d080/formal_18000_jobs_DRAFT_NOT_AUTHORIZED_v1.csv'
BUDGET = 'results/p4_d080/20261017_SCOPE_RECOVERY/budget_scope_overlay.json'
PRESERVE = 'reports/P4_D080_PRE_SWITCH_LOCAL_PRESERVATION_20261017.json'
LEDGER = 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json'
IMMUTABLE = 'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V25.json'
GENERATOR = 'scripts/p4_d080/map_scope.py'
BASE_COMMIT = 'bb3ca7e1fa37165d1b788dffa562c4eff73e021f'
EXTRA = ['d080_scope', 'd080_reason', 'd080_environments', 'd080_actual_evidence',
         'd080_status', 'd080_original_table_I_trials', 'd080_approved_table_I_trials',
         'd080_formal_trials_completed', 'd080_statistical_scale', 'd080_next_action']
checks = []
retained = {}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    data = (ROOT / name).read_bytes()
    retained[name] = sha_bytes(data)
    return data


def doc(name):
    return json.loads(read(name))


def table(name):
    read(name)
    with (ROOT / name).open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def check(name, ok, detail=None):
    record = {'name': name, 'passed': bool(ok)}
    if detail is not None:
        record['detail'] = detail
    checks.append(record)


def git_saved(name):
    return subprocess.check_output(['git', 'show', BASE_COMMIT + ':' + name], cwd=ROOT)


def main():
    old_fields, old = table(SOURCE)
    fields, rows = table(MATRIX)
    md = read(MATRIX_MD).decode()
    valid, budget, prior = doc(VALIDATION), doc(BUDGET), doc(LEDGER)
    preserve, immutable = doc(PRESERVE), doc(IMMUTABLE)
    job_fields, jobs = table(JOBS)
    source = read(GENERATOR).decode()
    check('fixed_source_sha', retained[SOURCE] == '2b34a55a39f3678d1d5a7ec1ca1d1c0bf13c828fad9ec6f2f4cfe7461604a491')
    check('fixed_matrix_sha', retained[MATRIX] == 'c9599003f3a2369e1f9ce106884ac2ebc5453d1774b185899eb6a397191bd3b7')
    check('source_shape', len(old_fields) == 186 and len(old) == 211)
    check('output_shape_and_field_order', len(rows) == 211 and fields == old_fields + EXTRA and len(fields) == 196)
    check('ordered_item_ids_preserved', [r['item_id'] for r in rows] == [r['item_id'] for r in old] and len({r['item_id'] for r in rows}) == 211)
    for before, after in zip(old, rows):
        check('historical_values:' + before['item_id'], {k: after[k] for k in old_fields} == before)
        check('original_statistics_retained:' + before['item_id'], after['d080_statistical_scale'] == before['original_repeats'] + '; ' + before['original_duration_budget'])
    index = {r['item_id']: r for r in rows}
    vi = {'P4-T15', 'P4-T02-VI', 'P4-T03-VI', 'P4-T16-VI', 'P4-T23-VI', 'P4-T30-VI',
          'P4-T08-VI_ABLATION', 'P4-T07-RSS_VI', 'P4-T24-STEP_VI'}
    vi |= {'P4-T05-VI_' + m for m in ('RSS', 'PCS', 'NR')}
    vi |= {'P4-T18-VI_' + p + '_' + m for p, m in itertools.product(('RRT', 'Bi-RRT', 'SBL'), ('RSS', 'PCS', 'NR'))}
    partial = {f'P4-T{i:02}' for i in (1, 2, 3, 5, 6, 7, 8, 9, 16, 17, 18, 23, 24, 25, 26, 27, 28, 30)}
    equations = {'P4-T01-EQ1', 'P4-T01-EQ2'} | {f'P4-T06-EQ{i}' for i in range(3, 10)}
    partial |= equations | {'P4-T24-GAMMA', 'P4-T20-NN_COST', 'P4-T25-AUTHOR_RAW_LINEAGE'}
    check('independent_closed_lists', len(vi) == 21 and len(partial) == 30 and not vi & partial and (vi | partial) <= set(index))
    check('exact_vi_archival_set', {r['item_id'] for r in rows if r['d080_scope'] == 'ARCHIVED_OUT_OF_APPROVED_SCOPE'} == vi)
    check('exact_partial_scope_set', {r['item_id'] for r in rows if r['d080_scope'] == 'PARTIAL_SCOPE_I_V_VI_ARCHIVED'} == partial)
    expected_scopes = Counter()
    for row in rows:
        ident = row['item_id']
        if ident in vi:
            expected = 'ARCHIVED_OUT_OF_APPROVED_SCOPE'
            check('vi_stop_and_original_status:' + ident, row['d080_environments'] == 'VI' and row['d080_status'] == 'ARCHIVED_HISTORY_NOT_D080_COMPLETION' and '不再追加VI' in row['d080_next_action'])
        elif ident in partial:
            expected = 'PARTIAL_SCOPE_I_V_VI_ARCHIVED'
        elif ident == 'P4-T29':
            expected = 'IN_SCOPE_APPLICATION_ANALYSIS_ONLY'
        elif row['original_model_platform'] == 'V' or ident == 'P4-T14':
            expected = 'IN_SCOPE_FULL_APPLICATION_PRIORITY'
        elif row['original_model_platform'] == 'I' or ident in {'P4-T10', 'P4-T19'} or ident.startswith('P4-T01-FIG1'):
            expected = 'IN_SCOPE_METHOD_BENCHMARK'
        else:
            expected = 'IN_SCOPE_FULL'
        check('scope_semantics:' + ident, row['d080_scope'] == expected)
        expected_scopes[expected] += 1
    check('scope_counts_21_30_160', expected_scopes == Counter(valid['scope_counts']) and sum(expected_scopes.values()) == 211 and 211 - len(vi) - len(partial) == 160)
    check('nn_cost_not_silently_restricted_to_II', index['P4-T20-NN_COST']['d080_scope'] == 'PARTIAL_SCOPE_I_V_VI_ARCHIVED')
    for ident in equations:
        row = index[ident]
        check('full_theory_retained:' + ident, '全文核对完整保留' in row['d080_reason'] and '不删数学定义或理论审查' in row['d080_reason'] and 'VI历史证据只读归档' in row['d080_next_action'])
    for ident in ('P4-T21', 'P4-T21-RSS', 'P4-T21-PCS', 'P4-T21-NR'):
        row = index[ident]
        check('fig4_ambiguity_retained:' + ident, row['d080_scope'] == 'IN_SCOPE_FULL' and row['d080_environments'] == 'I|II_PAPER_FIG4_CAPTION_BODY_AMBIGUITY' and '歧义' in row['d080_reason'])
    fr3 = index['P4-T29']
    check('fr3_analysis_only_no_automatic_execution', fr3['d080_environments'] == 'FUTURE_APPLICATION_ANALYSIS_ONLY' and '仅逐方法分析FR3' in fr3['d080_next_action'] and '不启动FR3/Isaac/P2实验' in fr3['d080_next_action'])
    cells = [r for r in rows if re.fullmatch(r'P4-T18-(II|III|IV|V|VI)_(RRT|Bi-RRT|SBL)_(RSS|PCS|NR)', r['item_id'])]
    expected_cells = set(itertools.product(('II', 'III', 'IV', 'V', 'VI'), ('RRT', 'Bi-RRT', 'SBL'), ('RSS', 'PCS', 'NR')))
    check('tableI_exact_45_cells', len(cells) == 45 and {tuple(r['item_id'][7:].split('_')) for r in cells} == expected_cells)
    for row in cells:
        is_vi = row['d080_environments'] == 'VI'
        check('tableI_cell_scale:' + row['item_id'], row['original_repeats'] == '500' and row['original_duration_budget'] == '1000s/call' and row['d080_original_table_I_trials'] == '500' and row['d080_approved_table_I_trials'] == ('0' if is_vi else '500') and row['d080_formal_trials_completed'] == '0')
    check('tableI_22500_18000_4500', sum(int(r['d080_original_table_I_trials']) for r in cells) == 22500 and sum(int(r['d080_approved_table_I_trials']) for r in cells) == 18000 and sum(500 for r in cells if r['d080_environments'] == 'VI') == 4500)
    check('tableI_parent_denominators', tuple(index['P4-T18'][k] for k in ('d080_original_table_I_trials', 'd080_approved_table_I_trials', 'd080_formal_trials_completed')) == ('22500', '18000', '0'))
    path_names = ('RRT_PCS', 'RRT_NR', 'Bi-RRT_PCS', 'Bi-RRT_NR')
    for name in path_names:
        row = index['P4-T18-II_' + name]
        check('existing_path_not_counted_formal:' + name, '单seed离散路径只读复用' in row['d080_actual_evidence'] and '正式统计0/500' in row['d080_actual_evidence'] and 'CCD未证' in row['d080_actual_evidence'])
    check('sbl_setup_not_promoted_to_path', 'setup已验收，局部/solve/完整路径待资格' in index['P4-T18-II_SBL_PCS']['d080_actual_evidence'])
    check('markdown_all_211_ordered_rows', [line.split('|')[1] for line in md.splitlines() if line.startswith('|P4-')] == [r['item_id'] for r in rows])
    check('markdown_denominators', all(s in md for s in ('45×500=22500', '36×500=18000', '9×500=4500', '正式已执行0/18000')))
    check('job_fields', job_fields == ['job_id', 'coverage_item_id', 'environment', 'planner', 'method', 'repeat_index_1based', 'seed', 'timeout_s', 'protocol_status', 'source_version', 'result'])
    check('jobs_18000_unique', len(jobs) == len({r['job_id'] for r in jobs}) == 18000)
    job_groups = defaultdict(list)
    job_errors = []
    for job in jobs:
        job_groups[job['coverage_item_id']].append(job)
        e, p, m = job['environment'], job['planner'], job['method']
        repeat = int(job['repeat_index_1based'])
        ok = (e in ('II', 'III', 'IV', 'V') and p in ('RRT', 'Bi-RRT', 'SBL') and m in ('RSS', 'PCS', 'NR') and 1 <= repeat <= 500
              and job['job_id'] == f'D080_{e}_{p}_{m}_{repeat:03d}' and job['coverage_item_id'] == f'P4-T18-{e}_{p}_{m}'
              and job['seed'] == 'PENDING_PAIRED_SEED_FREEZE' and job['timeout_s'] == '1000' and job['protocol_status'] == 'DRAFT_NOT_AUTHORIZED'
              and job['source_version'] == 'PENDING_PER_CELL_QUALIFICATION' and job['result'] == 'NOT_RUN')
        if not ok:
            job_errors.append(job['job_id'])
    check('all_jobs_draft_unexecuted_exact_conditions', not job_errors, job_errors)
    expected_kept = {r['item_id'] for r in cells if r['d080_environments'] != 'VI'}
    check('jobs_exact_36_nonVI_groups', set(job_groups) == expected_kept)
    for ident, group in sorted(job_groups.items()):
        check('job_group_exact_500:' + ident, len(group) == 500 and {int(r['repeat_index_1based']) for r in group} == set(range(1, 501)))
    check('mapping_validation_hashes', valid['source_sha256'] == retained[SOURCE] and valid['output_sha256'] == retained[MATRIX] and valid['job_manifest_sha256'] == retained[JOBS])
    check('mapping_validation_totals_and_no_science', all(valid[k] == v for k, v in {'rows': 211, 'historical_columns': 186, 'total_columns': 196, 'historical_column_value_differences': 0, 'original_cells': 45, 'approved_cells': 36, 'archived_VI_cells': 9, 'original_trials': 22500, 'approved_trials': 18000, 'archived_trials': 4500, 'unique_jobs': 18000, 'formal_trials_completed': 0, 'new_scientific_calls': 0, 'job_status': 'DRAFT_NOT_AUTHORIZED'}.items()))
    check('v25_fixed_sha', retained[LEDGER] == 'ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a')
    check('v25_count', prior['count'] == len(prior['executions']) == 43 and prior['science_count'] == 32 and prior['engineering_count'] == 11)
    check('v25_original_formal_obligation_retained', prior['formal_table_I_calls'] == 0 and prior['formal_table_I_required_calls'] == 22500)
    check('v25_vi_original_budget_retained', prior['vi_B_candidate_cap'] == prior['vi_B_consumed'] == 974 and prior['vi_B_remaining'] == 0)
    for ex in prior['executions']:
        check('v25_execution_sha:' + ex['run_id'], sha_bytes(read(ex['execution'])) == ex['execution_sha256'])
    for path in (SOURCE, LEDGER, IMMUTABLE):
        check('original_git_blob_unchanged:' + path, read(path) == git_saved(path))
    check('v25_preservation_passed_retained', immutable['passed'] is True and immutable['preservation_new_scientific_calls'] == 0 and immutable['coverage']['new_sha256'] == retained[SOURCE] and immutable['ledger']['sha256'] == retained[LEDGER])
    check('overlay_ledger_binding', budget['historical_ledger'] == LEDGER and budget['historical_ledger_sha256'] == retained[LEDGER] and budget['historical_costs_unchanged'] is True)
    check('overlay_counts_retained', tuple(budget[k] for k in ('executions', 'science_count', 'engineering_count')) == (43, 32, 11))
    check('overlay_costs_and_caps_retained', budget['charged_wall_s'] == prior['conservative_r2_sum_wall_s'] and budget['charged_cpu_s'] == prior['conservative_r2_sum_cpu_s'] and budget['r2_caps'] == prior['r2_caps'] and budget['r2_remaining_upper_bound'] == prior['r2_remaining'])
    check('overlay_remaining_arithmetic', all(math.isclose(budget['r2_caps'][k] - budget['charged_' + k], budget['r2_remaining_upper_bound'][k], abs_tol=1e-9, rel_tol=0) for k in ('wall_s', 'cpu_s')))
    check('overlay_no_formal_authorization_or_execution', budget['formal_execution_budget_approved'] is False and budget['formal_completed'] == budget['new_scientific_executions'] == 0 and budget['historical_unmeasured_tails'] == 'UNKNOWN_RETAINED')
    check('overlay_scope_denominators_and_VI_stop', tuple(budget[k] for k in ('original_table_I_trials', 'd080_approved_scope_trials', 'archived_VI_original_trials', 'VI_candidate_cap', 'VI_candidates_consumed', 'VI_remaining')) == (22500, 18000, 4500, 974, 974, 0) and budget['VI_future_execution'] == 'PROHIBITED_BY_D080')
    check('preserve_94_manifest_count', preserve['uncommitted_file_count'] == len(preserve['files']) == 94 and preserve['uncommitted_bytes'] == sum(x['bytes'] for x in preserve['files'].values()) == 1121261 and preserve['verified_all_members'] is True)
    archive = Path(preserve['archive'])
    archive_bytes = archive.read_bytes()
    check('preserve_local_archive_hash_and_size', len(archive_bytes) == preserve['archive_bytes'] and sha_bytes(archive_bytes) == preserve['archive_sha256'])
    with tarfile.open(archive, 'r:gz') as tf:
        members = tf.getmembers()
        check('preserve_archive_exact_members', len(members) == 94 and len({m.name for m in members}) == 94 and {m.name for m in members} == set(preserve['files']) and all(m.isfile() for m in members))
        for name, item in preserve['files'].items():
            data = read(name)
            check('preserve_original_local_file:' + name, len(data) == item['bytes'] and sha_bytes(data) == item['sha256'])
            packed = tf.extractfile(name).read()
            check('preserve_archive_byte_equality:' + name, packed == data and len(packed) == item['bytes'] and sha_bytes(packed) == item['sha256'])
    check('preserve_branch_baseline_and_local_only_policy', preserve['head'] == BASE_COMMIT and preserve['branch'] == 'p4-full-reproduction-pcs-study' and 'Local only' in preserve['archive_delivery_policy'] and preserve['new_science_calls'] == 0)
    tree = ast.parse(source)
    imports = {node.module if isinstance(node, ast.ImportFrom) else alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(name='')])}
    check('generator_stdlib_saved_data_imports', imports <= {'pathlib', 'collections', 'csv', 'hashlib', 'itertools', 'json', 're'})
    check('generator_no_scientific_dispatch_names', not any(isinstance(node, ast.Name) and node.id in {'Popen', 'run', 'exec', 'eval', '__import__'} for node in ast.walk(tree)))
    check('generator_writes_new_outputs_only', "open('x'" in source and 'write_bytes(' not in source and 'unlink(' not in source and 'rmtree(' not in source)
    own_tree = ast.parse(Path(__file__).read_text())
    own_imports = {node.module if isinstance(node, ast.ImportFrom) else alias.name for node in ast.walk(own_tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in (node.names if isinstance(node, ast.Import) else [ast.alias(name='')])}
    check('generator_was_not_imported_by_auditor', not any(name and ('map_scope' in name or 'p4_d080' in name) for name in own_imports))
    failed = [c for c in checks if not c['passed']]
    historical_differences = sum(before.get(k) != after.get(k) for before, after in zip(old, rows) for k in old_fields)
    report = {'schema': 'P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_V1', 'status': 'PASS_D080_SCOPE_SAVED_INDEPENDENT_REVIEW' if not failed else 'FAIL_D080_SCOPE_SAVED_INDEPENDENT_REVIEW',
              'personnel_independent': True, 'saved_data_only': True, 'generator_rerun': False, 'model_imports': 0, 'new_scientific_calls': 0,
              'checks_total': len(checks), 'checks_passed': len(checks)-len(failed), 'checks_failed': len(failed),
              'source_rows': len(old), 'historical_columns': len(old_fields), 'output_columns': len(fields), 'historical_value_differences': historical_differences,
              'archived_VI_rows': 21, 'partial_scope_rows': 30, 'other_retained_rows': 160, 'formal_original_trials': 22500, 'formal_D080_scope_trials': 18000, 'formal_completed': 0,
              'local_preserved_files': 94, 'local_archive_sha256': preserve['archive_sha256'], 'retained_sha256': retained, 'checks': checks,
              'limitations': ['范围与已保存证据审查，不是新增算法、路径或统计资格。', 'PARTIAL只限制VI经验复现，九公式全文数学核对保留。', '18,000条目为未批准的待冻结清单；不构成正式计算预算授权。', '原四条II路径的离散/重建端点/aligned碰撞边界保留，未新增连续碰撞或RSS规划证书。', '仅核对94文件和本地归档原字节；归档含历史作者源码，报告仅发布manifest/hash。']}
    with STEM.with_suffix('.json').open('x') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
    with STEM.with_suffix('.md').open('x') as f:
        f.write('# D080范围与保存证据独立审查\n\n')
        f.write(f"状态：{report['status']}；实际 {report['checks_passed']}/{len(checks)} 检查通过，{len(failed)} 失败。仅使用保存的CSV/JSON/Markdown、Git旧对象和本地tar原字节；未重运行生成器、导入模型或执行科学。\n\n")
        f.write('211行保留原186列逐值不变，新增10列。VI专属21行仅存档；30跨环境行部分范围；160其余保留行。九公式全文核对、Fig4的I/II歧义、FR3仅适用性分析边界均保留。\n\n')
        f.write('原Table I 45×500=22,500；D080 II–V 36×500=18,000；VI原9×500=4,500存档。18,000个唯一任务均为DRAFT_NOT_AUTHORIZED/NOT_RUN、seed待配对冻结、原1000s上限；正式0/18,000。\n\n')
        f.write('V25原账、原186列表与保全报告和旧Git对象逐字相同，43 execution原SHA保持；32科学/11工程，累计839.3257053759941墙钟秒/771.588923 CPU秒。VI 974/974、0余额；未知尾部保持UNKNOWN。94个原未提交文件及本地tar成员逐字一致。\n\n')
        f.write('本审查不证明新算法资格、连续安全、RSS全局规划或原论文全量复现；正式计算仍须cost pilot与用户预算批准。\n')
        if failed:
            f.write('\n失败检查：\n' + '\n'.join('- ' + c['name'] for c in failed) + '\n')
    print(json.dumps({'status': report['status'], 'checks_total': len(checks), 'checks_failed': len(failed), 'report_json_sha256': sha_bytes(STEM.with_suffix('.json').read_bytes()), 'report_md_sha256': sha_bytes(STEM.with_suffix('.md').read_bytes()), 'script_sha256': sha_bytes(Path(__file__).read_bytes())}))


if __name__ == '__main__':
    main()
