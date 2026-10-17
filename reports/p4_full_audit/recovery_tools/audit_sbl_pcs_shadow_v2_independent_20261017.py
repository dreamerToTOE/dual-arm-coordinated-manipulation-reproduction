#!/usr/bin/python3
# One authorized in-memory text-transform engineering check; no C++ or model execution.
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
TEMPLATE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain')
BASE=ROOT/'baselines/p4_full/geometry_consistent'
STEM='P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_20261017'
OUT=ROOT/'reports'/STEM
# Exclusive outputs prohibit accidentally repeating the two in-memory transform calls.
jhandle=OUT.with_suffix('.json').open('x',encoding='utf-8')
mhandle=OUT.with_suffix('.md').open('x',encoding='utf-8')
checks=[]
def ck(name,passed,detail=None):
    checks.append(dict(name=name,passed=bool(passed),detail=detail))
def sha(data):return hashlib.sha256(data).hexdigest()
def source_mask(text):
    # Independent small C++ lexical mask, separate from the transform's body_span.
    out=list(text);i=0;state='code';quote=''
    while i<len(text):
        c=text[i];n=text[i+1] if i+1<len(text) else ''
        if state=='code':
            if c=='/' and n in ('/','*'):
                out[i]=out[i+1]=' ';state='line' if n=='/' else 'block';i+=2;continue
            if c in ('"',"'"):
                quote=c;out[i]=' ';state='quoted';i+=1;continue
        elif state=='line':
            if c=='\n':state='code'
            else:out[i]=' '
        elif state=='block':
            if c=='*' and n=='/':out[i]=out[i+1]=' ';state='code';i+=2;continue
            if c!='\n':out[i]=' '
        elif state=='quoted':
            if c=='\\':
                out[i]=' '
                if i+1<len(text):out[i+1]=' ' if n!='\n' else '\n'
                i+=2;continue
            if c==quote:state='code'
            if c!='\n':out[i]=' '
        i+=1
    if state not in ('code','line'):raise ValueError('INDEPENDENT_LEXER_UNTERMINATED')
    return ''.join(out)
def pair(mask,opening):
    if mask[opening]!='{':raise ValueError('OPEN_BRACE_REQUIRED')
    depth=1;i=opening+1
    while depth:
        if i>=len(mask):raise ValueError('INDEPENDENT_BRACE_BALANCE')
        depth+=(mask[i]=='{')-(mask[i]=='}');i+=1
    return opening+1,i-1
def span(text,signature):
    if text.count(signature)!=1:raise ValueError('INDEPENDENT_SIGNATURE_CARDINALITY')
    mask=source_mask(text);return pair(mask,mask.index('{',text.index(signature)))
def unwrap(output,manifest,original,label):
    restored=dict(output)
    entries=[x for x in manifest['changes'] if x['kind'].startswith('OBSERVE_')]
    ck(label+'_exact16_wrappers',len(entries)==16,len(entries))
    for item in entries:
        f=item['file'];sig=item['signature'];text=restored[f].decode();a,b=span(text,sig);wrapped=text[a:b]
        hit=re.search(r'\[&\]\(\) -> (?:void|bool|State) \{',wrapped)
        if hit is None:raise ValueError('INDEPENDENT_RETURNING_LAMBDA_REQUIRED')
        wa,wb=pair(source_mask(wrapped),hit.end()-1);body=wrapped[wa:wb]
        oa,ob=span(original[f].decode(),sig);expected=original[f].decode()[oa:ob]
        if label=='v2' and sig==SAVE:
            for before,after in EDITS:expected=expected.replace(before,after,1)
        ck(label+'_body_'+item['observation_kind'],body==expected,dict(file=f,sha256=sha(body.encode())))
        restored[f]=(text[:a]+body+text[b:]).encode()
    if label=='v2':
        text=restored[SBL].decode();a,b=span(text,SAVE);body=text[a:b]
        for before,after in EDITS:
            ck('independent_inverse_writer_'+before,body.count(after)==1)
            body=body.replace(after,before,1)
        restored[SBL]=(text[:a]+body+text[b:]).encode()
    for f in sorted(original):ck(label+'_whole_file_inverse_'+f,restored[f]==original[f],sha(restored[f]))
    return restored
APC='proj_classes/apc_class.cpp';SVC='validity_checkers/StateValidityCheckerPCS.cpp';COL='validity_checkers/collisionDetection.cpp';SBL='planners/SBL_PCS.cpp';HDR='planners/SBL_PCS.h'
SAVE='void ompl::geometric::SBL::save2file(vector<Motion*> mpath1, vector<Motion*> mpath2)'
EDITS=(('mpath1[i]->a_chain','p4sbl::writer_a_chain(mpath1[i],1,i)'),('mpath2[i]->a_chain','p4sbl::writer_a_chain(mpath2[i],2,i)'))
paths={f'TEMPLATE/{k}':TEMPLATE/k for k in (APC,SVC,COL)}
paths.update({f'AUTHOR/{k}':AUTHOR/k for k in (SBL,HDR)})
for name in ('abb_pcs_source_corrections_draft.py','abb_sbl_pcs_instrumentation_draft.py','abb_sbl_pcs_observation_draft.hpp','abb_sbl_pcs_instrumentation_shadow_v2_draft.py','abb_sbl_pcs_observation_shadow_v2_draft.hpp'):paths[name]=BASE/name
for name in ('P4_FULL_R2_ABB_SBL_PCS_A_CHAIN_OUTPUT_MINIMAL_FIX_STATIC_DESIGN_20261017.md','P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_IMPLEMENTATION_STATIC_DRAFT_20261017.md'):paths[name]=ROOT/'reports'/name
before={k:p.read_bytes() for k,p in paths.items()}
inputs_sha={k:sha(v) for k,v in before.items()}
report=dict(schema='P4_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_V1',classification='PURE_TEXT_ENGINEERING_REVIEW_ONLY_NOT_BUILT_NOT_RUN',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='sbl_shadow_independent',personnel_independent=True,source_head_at_read='dc810b78f490950bf11f609a8dbf1a60b688dece',scientific_calls=0,compile_calls=0,model_calls=0,setup_calls=0,solve_calls=0,stage_writes=0,original_or_candidate_mutations=0,pure_text_transform_calls={'v1':0,'v2':0},inputs_sha256=inputs_sha,checks=checks)
try:
    pins={'abb_sbl_pcs_observation_shadow_v2_draft.hpp':'3c0d3031d53532bb077e7eabb3911aa9f911f771bb34216406cf0a71fb9108c3','abb_sbl_pcs_instrumentation_shadow_v2_draft.py':'926592eb43ef8ad90a6434a30aa613c2c6c41416e9f9120c734b76adc3a39209','P4_FULL_R2_ABB_SBL_PCS_A_CHAIN_OUTPUT_MINIMAL_FIX_STATIC_DESIGN_20261017.md':'0e84c42cba0e82fc3b30cedbf1301f76225acbb353a9805f8253617602e69642','P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_IMPLEMENTATION_STATIC_DRAFT_20261017.md':'dc71819a3d3d85c5cb5e04548a4843b8ea2be570df2366947bb4c036e97c97f8'}
    for k,v in pins.items():ck('pinned_'+k,inputs_sha[k]==v,inputs_sha[k])
    original={k:before[f'TEMPLATE/{k}'] for k in (APC,SVC,COL)}
    original.update({k:before[f'AUTHOR/{k}'] for k in (SBL,HDR)})
    cpp=original[SBL].decode();hdr=original[HDR].decode();header=before['abb_sbl_pcs_observation_shadow_v2_draft.hpp'].decode();cppmask=source_mask(cpp);hmask=source_mask(header)
    assignments=re.findall(r'\b(?:motion|connect|mpath\w*\[i\])->a_chain\s*=\s*([^;]+);',cppmask)
    ck('author_exact_three_assignments',assignments==['0','0','active_chain'],assignments)
    allrefs=re.findall(r'\ba_chain\b',cppmask)
    ck('author_exact_five_member_occurrences',len(allrefs)==5,len(allrefs))
    ck('author_exact_two_writer_reads',all(cpp.count(a)==1 for a,b in EDITS))
    calls=re.findall(r'(?m)^\s*addMotion\(([^;]+)\);',cppmask)
    ck('author_exact_four_addMotion_calls',calls==['tStart_, motion','tGoal_, motion','tree, motion','tree, connect'],calls)
    ck('author_two_ctors_do_not_initialize_a_chain',hdr.count('Motion(')==2 and not re.search(r'\ba_chain\s*\(',source_mask(hdr)))
    for sig in ('bool ompl::geometric::SBL::isPathValid(TreeData &tree, Motion *motion)',SAVE):
        a,b=span(cpp,sig);ck('no_algorithm_a_chain_read_'+sig.split('::')[-1].split('(')[0],('a_chain' not in source_mask(cpp[a:b])) if sig!=SAVE else all(cpp[a:b].count(a)==1 for a,z in EDITS))
    csa,csb=span(cpp,'bool ompl::geometric::SBL::checkSolution(bool start, TreeData &tree, TreeData &otherTree, Motion *motion, std::vector<Motion*> &solution)')
    cs=cpp[csa:csb]
    ck('connect_never_assigned',not re.search(r'connect->a_chain\s*=',source_mask(cs)))
    ck('historical_connect_can_survive_other_tree_failure','if (isPathValid(tree, connect) && isPathValid(otherTree, connectOther))' in cs and 'removeMotion' not in cs)
    ck('future_parent_and_path_can_include_old_connect','motion->parent = existing;' in cpp and 'motion = motion->parent;' in cs and 'connectOther = connectOther->parent;' in cs)
    ck('shadow_only_member_read_guarded_nonconnect',hmask.count('m->a_chain')==1 and 'if(!connect){const int assigned=m->a_chain;' in header)
    ck('no_added_Motion_member_write',not re.search(r'\bm->\w+\s*(?:=(?!=)|\+=|-=|\+\+|--)',hmask))
    ck('optional_unknown_initialized_empty','std::optional<int> shadow;' in header and 'std::optional<int> a_chain_shadow;' in header)
    ck('connection_origin_pinned','connect?"CHECKSOLUTION_CONNECT":(m->parent?"GROW_ASSIGNED":"ROOT_ASSIGNED")' in header)
    ck('known_roles_checked_0_or_1','require(assigned==0||assigned==1,' in header)
    ck('generation_increment_and_lifetime_increment','++next_lifetime,++generations[m],++next_state' in header)
    ck('duplicate_live_pointer_and_state_rejected','require(!live.count(m)&&!state_to_motion.count(m->state)' in header)
    ck('live_map_record_only_inserted_then_erased',hmask.count('live.emplace(')==1 and hmask.count('live.erase(')==1 and not re.search(r'live\s*\[',hmask))
    ck('exact_token_retirement','it->second.id==item.id' in header)
    for sig in ('template<class Motion> json snapshot(Motion* m)','template<class Motion> int writer_a_chain(Motion* m,unsigned side,std::size_t source_index)'):
        a,b=span(header,sig);ck('shadow_only_'+sig.split('> ')[-1].split('(')[0],'m->a_chain' not in header[a:b] and 'const auto& x=live.at(m);' in header[a:b])
    wa,wb=span(header,'template<class Motion> int writer_a_chain(Motion* m,unsigned side,std::size_t source_index)');writer=header[wa:wb]
    ck('plain_trace_both_collect_attempts','if(enabled)' not in writer and 'writer_metadata_attempts.push_back(row);' in writer)
    ck('unknown_text_sentinel_minus1','const int column=x.a_chain_shadow?*x.a_chain_shadow:-1;' in writer)
    ck('unknown_json_null_and_provenance','json(nullptr)' in writer and 'UNINITIALIZED_NOT_READ' in writer)
    ck('attempt_write_success_unknown','{"text_write_success_observed",nullptr}' in writer)
    ck('buffer_getter_const','inline const json& writer_metadata_attempt_buffer(){return writer_metadata_attempts;}' in header)
    ck('header_does_not_open_file',not re.search(r'\b(?:ofstream|fopen|open|fwrite)\s*\(',hmask))
    ck('buffer_is_cleared_on_reset','writer_metadata_attempts=json::array();generations.clear();' in header)
    ck('new_cpp17_optional_explicit','#include <optional>' in header)
    helper_ast=ast.parse(before['abb_pcs_source_corrections_draft.py'].decode())
    helper_fn=next(n for n in helper_ast.body if isinstance(n,ast.FunctionDef) and n.name=='body_span')
    helper_ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[helper_fn],type_ignores=[])),'saved_body_span_ast','exec'),helper_ns)
    def load_transform(name):
        tree=ast.parse(before[name].decode(),filename=name)
        tree.body=[n for n in tree.body if not isinstance(n,ast.ImportFrom) or not n.level]
        ns={'body_span':helper_ns['body_span']}
        exec(compile(ast.fix_missing_locations(tree),name,'exec'),ns)
        return ns
    v1=load_transform('abb_sbl_pcs_instrumentation_draft.py');v2=load_transform('abb_sbl_pcs_instrumentation_shadow_v2_draft.py')
    ck('v2_literal_two_writer_edits',v2['WRITER_EDITS']==EDITS)
    report['pure_text_transform_calls']['v1']+=1
    out1,manifest1=v1['instrument_sources'](original)
    report['pure_text_transform_calls']['v2']+=1
    out2,manifest2=v2['instrument_sources'](original)
    ck('input_dictionary_not_mutated',original=={**{k:before[f'TEMPLATE/{k}'] for k in (APC,SVC,COL)},**{k:before[f'AUTHOR/{k}'] for k in (SBL,HDR)}})
    unwrap(out1,manifest1,original,'v1');unwrap(out2,manifest2,original,'v2')
    for f in (APC,SVC,COL,HDR):ck('v1_v2_output_equal_'+f,out1[f]==out2[f])
    expected=out1[SBL].decode()
    for before_expr,after_expr in EDITS:expected=expected.replace(before_expr,after_expr,1)
    old='{"original_save_may_read_uninitialized_historical_connect_a_chain",true}'
    new='{"original_writer_uninitialized_read_risk_retained_as_source_evidence",true},{"candidate_writer_uses_versioned_shadow",true}'
    ck('v1_source_mark_exactly_once',expected.count(old)==1)
    expected=expected.replace(old,new,1)
    ck('v1_v2_SBL_only_two_IO_expressions_and_source_mark',expected.encode()==out2[SBL])
    ck('v2_manifest_no_false_verbatim_save',manifest2['save_body_verbatim_original'] is False)
    ck('v2_manifest_two_IO_edits',manifest2['writer_expression_replacements']==2 and len([c for c in manifest2['changes'] if c['kind']=='RECONSTRUCTED_OUTPUT_METADATA_ONLY'])==2)
    ck('v2_manifest_Motion_unchanged',manifest2['Motion_storage_writes_added']==0 and manifest2['Motion_layout_or_constructor_changes']==0)
    ck('v2_manifest_requires_v2_header',manifest2['required_header_variant']=='abb_sbl_pcs_observation_shadow_v2_draft.hpp')
    ck('v2_manifest_no_H_D_NR',manifest2['H_or_D_or_NR_correction_present'] is False)
    report['transform_output_sha256']={'v1':{k:sha(v) for k,v in out1.items()},'v2':{k:sha(v) for k,v in out2.items()}}
    report['v2_manifest']=manifest2
except BaseException as exc:
    report['exception']=dict(type=type(exc).__name__,message=str(exc))
    ck('review_exception_free',False,report['exception'])
finally:
    for k,p in paths.items():ck('input_bytes_unchanged_'+k,p.read_bytes()==before[k])
    report['checks_total']=len(checks);report['checks_passed']=sum(x['passed'] for x in checks);report['checks_failed']=report['checks_total']-report['checks_passed']
    report['status']='PASS_INDEPENDENT_STATIC_AND_ONCE_IN_MEMORY_TEXT_TRANSFORM_ONLY' if report['checks_failed']==0 else 'FAIL_RETAINED_INDEPENDENT_STATIC_REVIEW'
    report['D080']='I-V approved scope; VI archived, no new VI work; original 211/22500 facts retained; future formal D080 18000 requires pilot and separate approval.'
    report['limitations']=['No C++ compilation or execution; no runtime shadow fixture or actual historical connect UB occurrence observed.','No sidecar exists: header records in-memory expression attempts only; file write success remains unknown.','Not a SBL local/solve/path certificate; future builder/driver/protocol must explicitly select v2 and independently persist/check actual writer outputs.','Scientific control bytes unchanged outside two documented writer expressions; no equivalence claim for undefined original output or timing/allocation effects.']
    json.dump(report,jhandle,ensure_ascii=False,indent=2);jhandle.write('\n');jhandle.close()
    lines=['# SBL writer/shadow v2 独立静审与一次内存文本核验','',f"状态：`{report['status']}`。真实检查 {report['checks_passed']}/{report['checks_total']}，失败 {report['checks_failed']}。",'','本项真实执行一次系统 Python 工程审查进程，保存源码 AST 中的 v1 与 v2 instrument_sources 各调用一次，只在内存变换五份字节；未 import 项目包、编译 C++、创建 stage、调用模型、setup、solve、RBS、IK、采样或碰撞。两份报告使用独占 x 创建，禁止重复执行以替代原结果。','', '固定原作者三处 a_chain 赋值、两处 writer 读取及四个 addMotion 来源均核对；ConnectionScope 只覆盖 checkSolution 的 connect 登记。历史 connect 可存活并成为未来父节点，registry 保留其 CHECKSOLUTION_CONNECT/unknown 来源，不因 parent 改变或地址复用而补值。候选仅在非 connect 且已有原赋值时读取一次 Motion::a_chain，此后 snapshot/writer 均读 optional shadow；无 Motion 字段写回。','', '独立词法掩码与括号扫描逆剥 v1/v2 各 16 个 returning-lambda wrappers；v2 另逆回两处 I/O 表达式。核对所有五文件逐字恢复。v1/v2 的 APC、SVC、collision、HDR 输出相等；SBL 输出差异严格为两个 writer 表达式与来源观察标签。原 save 完整原 body 声明已明确不适用 v2，两 I/O edits 单列，其他原科学 body 保留。','', '已知 0/1 由 optional 的是否持值判断（值 0 仍为有值）；unknown 输出 -1，JSON 记录 null、来源和 lifetime/代际/state ID。plain/trace 均收集内存 attempt buffer。header 未落盘 sidecar，text_write_success_observed=null；不能声称文本写成功、sidecar 已保存、完整路径或 SBL 端到端合格。','', 'D080 已读并采用：I-V 为批准范围；VI 只读存档且本项新增 VI 运行 0。原 211 行和 22500 事实保留，D080 正式目标 18000 须 pilot 后单独批准。不重跑 II 四条成功路径，不进 P2/Isaac。','', '下一步可接入新版本工程候选并单独冻结；实际 C++ header、driver 保存、plain/trace 和 solve 资格仍未由本项证明。所有候选/原作者/旧证据字节检查保持，未改共享治理或预算账。','',f"机器可核验结果：`reports/{STEM}.json`。",'']
    mhandle.write('\n'.join(lines));mhandle.close()
print(json.dumps({'status':report['status'],'checks_passed':report['checks_passed'],'checks_total':report['checks_total'],'checks_failed':report['checks_failed'],'pure_text_transform_calls':report['pure_text_transform_calls'],'json_sha256':sha(OUT.with_suffix('.json').read_bytes()),'md_sha256':sha(OUT.with_suffix('.md').read_bytes())},ensure_ascii=False))
