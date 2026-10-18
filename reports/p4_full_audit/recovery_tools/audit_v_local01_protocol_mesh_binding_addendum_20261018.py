#!/usr/bin/env python3
"""Correct only an overstrict duplicate mesh-map assertion; no experiment."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL01_PROTOCOL_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
DRAFT = ROOT / 'configs/p4_d080/v_pcs_local01_v1.DRAFT.json'
RUNNER = ROOT / 'scripts/p4_d080/qualify_v_pcs_local_v1_draft.py'
OUT = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL01_PROTOCOL_INCREMENTAL_INDEPENDENT_PRE_ADDENDUM_20261018'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
base, d = load(BASE), load(DRAFT)
manifest = load('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json')
model, = [r for r in manifest['entries'] if r['model'] == 'V' and r['variant'] == 'aligned']
expected = {str(Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/V_aligned/simulator') / n): h
            for n, h in model['mesh_sha256'].items()}
failed = [r for r in base['checks'] if not r['passed']]
checks = [
    {'check': 'Exact base8 successful checks reused and sole overstrict duplicate-map failure retained',
     'passed': sha(BASE) == '57b1656652aade5b985ddf5a76c727898311a4529379e30a0561ee31b4713fc8'
       and base['checks_total'] == 9 and base['checks_passed'] == 8 and base['checks_failed'] == 1
       and failed == [{'check': 'Original V27 mesh identity map and87pair policy reused without model calls', 'passed': False}]},
    {'check': 'Original runtime27 map87pairv3 and all current mesh bytes match; separate runtime map is sufficient',
     'passed': d['runtime_meshes_sha256'] == expected and len(expected) == 27
       and model['active_call_statement_count'] == 87 and model['tcp_observation_version'] == 3
       and all(sha(p) == h for p, h in expected.items())},
    {'check': 'Unchanged runner uses exact frozen runtime map and verifies copied bytes before each source launch',
     'passed': sha(RUNNER) == 'aafb13d2bfb1932c478e110206677280ce0e476eead8959715818d8d3ecd3b7f'
       and "spec['runtime_meshes_sha256'] == expected_meshes" in RUNNER.read_text()
       and "require(sha(filename) == digest, 'RUNTIME_MESH_BYTES_CHANGED')" in RUNNER.read_text()
       and RUNNER.read_text().index("require(sha(filename) == digest, 'RUNTIME_MESH_BYTES_CHANGED')")
           < RUNNER.read_text().index('sessions.append(session); session.start()')},
    {'check': 'Draft and all nonmesh metadata remain exact; allowed freeze transformation unchanged',
     'passed': sha(DRAFT) == base['draft_protocol_sha256'] == '01ce5307a9283506dee8478dc8d2d808b5fa9e4bbfd75bc94d676868cc48ffd3'
       and base['allowed_final_freeze_transform']['formal_execution_authorized_must_remain_false'] is True},
]
result = {k: v for k, v in base.items() if k not in ['checks', 'checks_total', 'checks_passed', 'checks_failed', 'status']}
result.update(schema='P4_D080_V_PCS_LOCAL01_PROTOCOL_INCREMENTAL_PERSONNEL_INDEPENDENT_PRE_ADDENDUM_V1',
    status='PASS_INCREMENTAL_PROTOCOL_SEAM_STATIC_ONLY' if all(r['passed'] for r in checks) else 'FAIL_ADDENDUM_RETAINED',
    reused_base_saved_PRE=str(BASE.relative_to(ROOT)), reused_base_saved_PRE_sha256=sha(BASE),
    base_passed_checks_reused_without_rerun=8, base_failed_check_preserved=failed[0],
    addendum_reason='Initial reviewer required runtime27 mesh inputs to be duplicated in bound_files_sha256. Exact runtime_meshes_sha256 plus unchanged per-copy SHA guard before launch is the actual reviewed source contract. No source, draft or input changed; all27 current mesh bytes match.',
    checks=checks, checks_total=len(checks), checks_passed=sum(r['passed'] for r in checks),
    checks_failed=sum(not r['passed'] for r in checks))
for suffix, content in [('.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n'),
                        ('.md', '# V local01协议接缝独审补记\n\n' + result['status']
                         + f"；{result['checks_passed']}/{len(checks)}，复用原8项通过。原9项审查中唯一FAIL保留：审查器额外要求27网格在bound map重复绑定，超出源码真实合同。现独立核原runtime map、27当前字节及每次source前逐拷贝SHA守门，原DRAFT/runner未改。\n\n"
                         + '适用冻结变换：root在新正式文件仅将顶层及driver的frozen/review/scientific_authorization六flag置true，追加本补记与13项组合门证书的精确binding/reference；原DRAFT保留，formal=false及其余字段/现有binding不变。V32、两ELF、36public/38stdout、30wall/60CPU结论复用原8项；仅source-local，独立物理资格另冻。\n\n'
                         + '本审者是早期V源码/草案作者，人员独立性仅针对root协议metadata。无模型/import/describe/编译/科学/冻结/入账。\n')]:
    with Path(str(OUT) + suffix).open('x') as f:
        f.write(content)
print(json.dumps({'status': result['status'], 'checks_passed': result['checks_passed'], 'checks_total': len(checks),
                  'outputs_sha256': {s: sha(str(OUT) + s) for s in ['.json', '.md']}}, ensure_ascii=False))
