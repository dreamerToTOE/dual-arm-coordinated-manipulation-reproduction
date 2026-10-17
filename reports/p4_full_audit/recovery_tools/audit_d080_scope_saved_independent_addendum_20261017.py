"""Correct one auditor JSON selector; reuse unchanged saved-data checks."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OLD = 'reports/P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_20261017.json'
OLD_MD = 'reports/P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_20261017.md'
OLD_SCRIPT = 'reports/p4_full_audit/recovery_tools/audit_d080_scope_saved_independent_20261017.py'
LEDGER = 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json'
STEM = ROOT/'reports/P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_ADDENDUM_20261017'
checks = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(name, ok):
    checks.append({'name': name, 'passed': bool(ok)})


def main():
    old_bytes = (ROOT/OLD).read_bytes()
    old = json.loads(old_bytes)
    check('original_failed_review_retained', sha(old_bytes) == '874e568d4c4f7522a4ed3b41d74df2ebd7400ef03d0d227718ca9937bca4af14')
    check('original_md_retained', sha((ROOT/OLD_MD).read_bytes()) == '0f6787039772e6b0c066a400c928db0f6b30e162cdec6c787636c181bb409694')
    check('original_auditor_retained', sha((ROOT/OLD_SCRIPT).read_bytes()) == 'a4e5c4a238d8d6c7e973c453c6b7d371a2c2366c3ca15c4a8844dbfdb00f495c')
    failed_before = [c for c in old['checks'] if not c['passed']]
    check('only_original_selector_failed', old['checks_total'] == 1028 and old['checks_passed'] == 1027 and old['checks_failed'] == 1 and len(failed_before) == 1 and failed_before[0]['name'] == 'v25_vi_original_budget_retained')
    for name, digest in old['retained_sha256'].items():
        check('unchanged_saved_evidence:' + name, sha((ROOT/name).read_bytes()) == digest)
    ledger = json.loads((ROOT/LEDGER).read_bytes())
    check('correct_nested_vi_candidate_cap', ledger['vi_B_candidate_cap'] == 974)
    check('correct_nested_vi_candidate_consumed', ledger['vi_B_consumed']['candidate_constructions'] == 974)
    check('correct_nested_vi_candidate_remaining', ledger['vi_B_remaining']['candidate_constructions'] == 0)
    preserve = json.loads((ROOT/'reports/P4_D080_PRE_SWITCH_LOCAL_PRESERVATION_20261017.json').read_bytes())
    archive = Path(preserve['archive']).read_bytes()
    check('same_local_preservation_archive', sha(archive) == preserve['archive_sha256'] == old['local_archive_sha256'])
    check('original_scientific_bytes_and_budget_were_not_changed', old['new_scientific_calls'] == 0 and old['generator_rerun'] is False and old['historical_value_differences'] == 0 and old['local_preserved_files'] == 94)
    failed = [c for c in checks if not c['passed']]
    result = {'schema': 'P4_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_ADDENDUM_V1',
              'status': 'PASS_D080_SCOPE_SAVED_INDEPENDENT_REVIEW' if not failed else 'FAIL_D080_SCOPE_SAVED_INDEPENDENT_REVIEW_ADDENDUM',
              'personnel_independent': True, 'saved_data_only': True, 'generator_rerun': False, 'model_imports': 0, 'new_scientific_calls': 0,
              'original_report': OLD, 'original_report_sha256': sha(old_bytes),
              'original_failed_auditor_retained': True,
              'correction': '审查器原把V25 vi_B_consumed/remaining嵌套对象与974/0标量比较；本addendum读取其中candidate_constructions，未修改账本、范围表、manifest、raw或科学实现。',
              'checks_total': len(checks), 'checks_passed': len(checks)-len(failed), 'checks_failed': len(failed),
              'prior_passed_checks_reused_with_unchanged_evidence': 1027,
              'original_failed_selector_now_qualified': not failed,
              'scope_rows': 211, 'historical_columns_preserved': 186, 'total_columns': 196,
              'historical_value_differences': 0, 'archived_VI_rows': 21, 'partial_scope_rows': 30, 'other_retained_rows': 160,
              'original_table_I_trials': 22500, 'D080_approved_scope_trials': 18000, 'archived_VI_trials': 4500, 'formal_trials_completed': 0,
              'formal_execution_budget_approved': False, 'VI_candidates_consumed': 974, 'VI_remaining': 0, 'local_files_preserved': 94,
              'retained_sha256': old['retained_sha256'], 'checks': checks,
              'limits': old['limitations']}
    with STEM.with_suffix('.json').open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, allow_nan=False); f.write('\n')
    with STEM.with_suffix('.md').open('x') as f:
        f.write('# D080范围独立审查补记\n\n')
        f.write(f"状态：{result['status']}。本次实际{result['checks_passed']}/{len(checks)}检查通过，失败{len(failed)}；原审查1027项通过检查在全部保存证据SHA保持后复用。\n\n")
        f.write('原1028项审查唯一失败来自审查器的JSON嵌套选择器错误：V25 vi_B_consumed/remaining是含candidate_constructions的对象。本次正确读取974/0；原失败报告及脚本原字节保留。账本、范围产物、作者源码和科学运行未改变。\n\n')
        f.write('211×196表完整保留原186列；21行VI归档、30行跨环境部分范围、160行其余保留。九公式全文数学核对、Fig4的I/II歧义及FR3仅分析边界保留。原Table I 22,500、D080批准范围18,000、VI存档4,500分别报告；18,000条清单均待审批、未运行，正式0/18,000。\n\n')
        f.write('V25原账/表/保全与旧Git对象原字节相同，43execution原SHA保持，累计839.3257053759941墙钟秒/771.588923 CPU秒；VI 974/974、剩余0。94个原未提交文件及本地tar已逐字核验且此次SHA仍保持。未重运行生成器、导入模型或增加科学调用。\n\n')
        f.write('此证书只审核范围与保存证据，不证明新路径/连续碰撞/RSS规划/全量论文复现，也不批准正式计算。\n')
    print(json.dumps({'status': result['status'], 'checks_total': len(checks), 'checks_failed': len(failed), 'prior_passed_checks_reused': 1027,
                      'json_sha256': sha(STEM.with_suffix('.json').read_bytes()), 'md_sha256': sha(STEM.with_suffix('.md').read_bytes()), 'script_sha256': sha(Path(__file__).read_bytes())}))


if __name__ == '__main__':
    main()
