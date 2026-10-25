#!/usr/bin/env python3
"""Append D083 evidence to all211 historical rows without changing old cells.

Read-only source/result mapping. No numerical/robot/planning libraries imported.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'reports/P4_D082_ORIGINAL_VS_APPROVED_VS_ACTUAL.csv'
NEW=ROOT/'reports/P4_D083_ORIGINAL_VS_APPROVED_VS_ACTUAL.csv'
MD=ROOT/'reports/P4_D083_ORIGINAL_VS_APPROVED_VS_ACTUAL.md'
VERIFY=ROOT/'reports/P4_D083_COVERAGE_PRESERVATION_20261022.json'
A='results/20261022_D083_spatial_visualization01/manifest.json'
B='results/20261022_D083_fig3_controlled02/summary.json'
C='results/20261022_D083_difficult02/summary.json'
AF='reports/p4_d083_spatial_assets_20261022/'
BF='results/20261022_D083_fig3_controlled02/'
CF='results/20261022_D083_difficult02/'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with OLD.open(newline='',encoding='utf-8-sig') as f:
 reader=csv.DictReader(f);old_fields=list(reader.fieldnames);old=list(reader)
assert len(old)==211 and len(old_fields)==257
assert all(len(r)==257 for r in old)
assert len({r['item_id'] for r in old})==211
for x in [A,B,C]:assert (ROOT/x).exists()
new_fields=['d083_scope','d083_actual_status','d083_stage_A_evidence','d083_stage_B_evidence',
 'd083_stage_C_evidence','d083_evidence_files','d083_limitations_and_missing',
 'd083_population_and_denominator','d083_new_original_Table_I_trials',
 'd083_original_Table_I_denominator','d083_cancelled_historical_target',
 'd083_spatial_qualification_boundary','d083_original_vs_reconstruction',
 'd083_after_delivery_action','d083_record_date']
AL='空间II/III仅RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY；native TCP仍不合格；离散source碰撞策略，无CCD、实体杆/省略pair安全或最小间隙证书。'
BL='96端点条件于13条历史成功轨迹；180非自对共享端点，非全流形均匀样本，距离仅0.0103–2.7035rad；不赋总体置信区间；非原m20/NR曲线或Bi-RRT时间。'
CL='三条件为旧PCS轨迹端点诊断；均无候选路线实际受阻证据，NOT_ESTABLISHED_HARD；PCS首调用artifact UNKNOWN保留且未重跑，不计方法失败；无性能优势主张。'
AD='复用II RRT PCS177/NR393和III PCS649节点，真实网格/FK及杆/障碍三维图；III14边角色[0,0,0,1,0,0,0,1,1,0,0,0,0,0]，4次转换；零新空间规划。'
BD='先冻同一96合法端点/180非自对及bins；2880单图表候选+900实际共享512中点策略；m1=176/180，m2/3/7/16=180/180；并集单调性零违反；97,577成功局部离散点引用独立合格。'
CD='3条件×4方法×3配对种子=36已执行；35完整/1artifact UNKNOWN；PCS8合格+1未知、兼容fixed-0 9/9、NR9/9、RSS3/9；成功解partition切换均0。'
new=[]

def put(r,status,ae='',be='',ce='',files='',limit='',pop=''):
 r.update(d083_actual_status=status,d083_stage_A_evidence=ae,d083_stage_B_evidence=be,
          d083_stage_C_evidence=ce,d083_evidence_files=files,
          d083_limitations_and_missing=limit,d083_population_and_denominator=pop)

for original in old:
 r=dict(original);i=r['item_id'];parent='-'.join(i.split('-')[:2]);model=r['original_model_platform']
 r.update({k:'' for k in new_fields})
 r.update(d083_scope='PARTIAL_SCOPE_I_II_III_ONLY',
   d083_actual_status='PRESERVED_D082_EVIDENCE_NO_NEW_ROW_SPECIFIC_TEST',
   d083_evidence_files=r['d082_evidence_files'],
   d083_limitations_and_missing='D082旧状态及缺口原样保留；D083未扩展为原论文FULL。'+r['d082_limitations'],
   d083_population_and_denominator='旧分母见原257列；D083诊断不并入原TableI或旧D081分母。',
   d083_new_original_Table_I_trials='0',d083_original_Table_I_denominator='22500',
   d083_cancelled_historical_target='18000_CANCELLED_NOT_RESTARTED',
   d083_spatial_qualification_boundary=AL,
   d083_original_vs_reconstruction='原论文义务不删；批准范围为20R重建+ABB II/III保存证据与限定新诊断，非全部原实验FULL。',
   d083_after_delivery_action='STOP_AWAIT_USER_REVIEW_NO_NEXT_PAPER_OR_NEW_CAMPAIGN',d083_record_date='2026-10-22')
 if original['d080_scope']=='ARCHIVED_OUT_OF_APPROVED_SCOPE':
  r['d083_scope']='ARCHIVED_VI_NO_NEW_EXECUTION'
  put(r,'ARCHIVED_HISTORICAL_VI_IMMUTABLE',files=r['d082_evidence_files'],
      limit='VI只读归档，不追加数学/规划/修补或预算；旧974/974及失败不改，原4500统计义务保留历史。',pop='D083新增VI调用0；原TableI VI4500保留历史。')
 elif i in ('P4-T13','P4-T14') or model in ('IV','V'):
  r['d083_scope']='HISTORICAL_IV_V_NO_NEW_EXECUTION'
  put(r,'OUT_OF_D083_SCOPE_PRESERVED_FAILURE_AND_INCOMPLETE',files=r['d082_evidence_files'],
      limit='D083明确禁止新增IV/V；保留旧不完整/失败及V native/aligned/TCP问题，未修复、不改判。')
 else:
  if i in ('P4-T01','P4-T05','P4-T08','P4-T16','P4-T26'):
   put(r,'RECONSTRUCTED_MECHANISMS_AND_DISCRETE_EVIDENCE_PARTIAL',AD,BD,CD,
       ';'.join([A,B,C]),AL+' '+BL+' '+CL,'A旧保存路径；B180同配对；C36诊断调用，35完整/1未知。')
  elif i=='P4-T02' or i=='P4-T02-I':
   put(r,'PLANAR_ANALYTIC_CHART_IDENTITIES_CONTROLLED_LOCAL_PARTIAL',be=BD,
       files=BF+'candidate_outcomes.csv;'+BF+'frozen_pool.json',limit=BL+' 不证明全可行IK分支分布或原空间50万投影。',pop='2880逐分划真实候选；158端点分支不兼容，364RBS解析中点不可达。')
  elif i=='P4-T06':
   put(r,'NESTED_EXISTENTIAL_UNION_VERIFIED_NOT_GLOBAL_THEORY_PROOF',be=BD,files=B,
       limit=BL+' 并集单调性是同一候选集合逻辑检查，不证明等分支测度/独立性假设或式7–9普遍统计界。',pop='180固定点对，m1/2/3/7/16同总体。')
  elif i in ('P4-T07','P4-T07-RSS_I'):
   put(r,'HISTORICAL_RSS_FAILURE_RETAINED_NEW_LOCAL_TASK_SUCCESSES_LIMITED',ce=CD,
       files=CF+'method_summary.csv;reports/P4_D082_ALGORITHM_FINDINGS_20261022.md',
       limit=CL+' 新C3的3次RSS路径成功不等于随机奇异桥成功；旧72请求/2304不可达构造和原E0/E1零RSS规划成功保留。',pop='新RSS3/9；旧D081 RSS0/10独立分母，不合并。')
  elif i in ('P4-T09','P4-T17','P4-T23','P4-T28','P4-T08-I_ABLATION','P4-T23-I'):
   put(r,'BOUNDED_DIAGNOSTIC_COMPLETE_NO_PCS_SUPERIORITY_HARDNESS_UNESTABLISHED',ce=CD,
       files=C+';'+CF+'method_summary.csv;'+CF+'condition_diagnostics.json',limit=CL+(' 未做同任务移除障碍的原始消融。' if i in ('P4-T23','P4-T23-I') else '')+(' 本次仅独立共同树规划栈，不是原三规划器完整矩阵。' if i=='P4-T17' else ''),
       pop='3预注册条件×4方法×种子[7,23,41]；36执行/35完整/1未知，不合并旧50call。')
  elif i=='P4-T10' or i=='P4-T16-I':
   put(r,'RECONSTRUCTED_PLANAR_TASK_REUSED_CONTROLLED_SUPPLEMENT',be=BD,ce=CD,files=B+';'+C,
       limit=BL+' '+CL+' 原Fig2a精确输入仍缺，不能称原环境I逐参数等价。',pop='B180同配对；C36诊断，旧轨迹保留。')
  elif i in ('P4-T11','P4-T12','P4-T02-II','P4-T03-II','P4-T16-II','P4-T02-III','P4-T16-III',
              'P4-T05-II_PCS','P4-T05-II_NR','P4-T05-III_PCS'):
   put(r,'SAVED_SPATIAL_PATH_REUSE_AND_SOURCE_BOUND_3D_VISUALIZATION',ae=AD,files=A,
       limit=AL+' 无新规划/碰撞资格，II另外413/689及SBL证据沿用旧交付；III仅PCS。',pop='主要渲染II177+393点，III649点；旧证书非新增成功率样本。')
  elif i=='P4-T19' or i in ('P4-T19-VIS_M1','P4-T19-VIS_M2','P4-T19-VIS_M3','P4-T19-VIS_M7'):
   put(r,'FIG3_CONTROLLED_SHARED_POPULATION_DIAGNOSTIC_COMPLETE_ORIGINAL_PARTIAL',be=BD,files=B+';'+BF+'pair_by_m_outcomes.csv',
       limit=BL+' m≥3没有额外可用性增益；实际局部cost不冒称规划cost。',pop='各m同180非自对；m1=176、m2/3/7/16=180；无UNKNOWN/超时/耗尽。')
  elif i=='P4-T19-VIS_M20':
   put(r,'ORIGINAL_M20_UNAVAILABLE_RECONSTRUCTED_CHARTS_NOT_INVENTED',be='重建模型仅非零连续3R起点0..16；受控最大m16是p0..15。',
       files='configs/p4_d083/fig3_controlled_v1.json',limit='未执行m20，不复制图表填充；原论文m20义务保持未覆盖。')
  elif i=='P4-T19-VIS_NR':
   put(r,'MATCHED_FIG3_NR_NOT_PERFORMED',files=B,limit='本次仅纠正PCS的m因果总体；原NR同合法池曲线未做，旧Fig4代理NR不能代替。')
  elif i.startswith('P4-T19-TIME_'):
   put(r,'ORIGINAL_FIG3_BIRRT_RUNTIME_NOT_PERFORMED',be='新增m局部检查成本与枚举成本分开保存。',files=BF+'summary_by_m.csv',
       limit='该行原指标是Bi-RRT规划时间；本次未跑每m规划，不以局部wall填原规划runtime。')
  elif i=='P4-T19-PLANAR_PROJECTION':
   put(r,'ORIGINAL_PLANAR_40X_COST_CLAIM_UNVERIFIED',files=r['d082_evidence_files'],limit='本次无新增APC/NR投影成本对照，不从局部总成本推导原40倍单投影结论。')
  elif i.startswith('P4-T18'):
   ae=AD if i in ('P4-T18-II_RRT_PCS','P4-T18-II_RRT_NR','P4-T18-III_RRT_PCS') else ''
   put(r,'ORIGINAL_FORMAL_SCALE_CANCELLED_NOT_RUN',ae=ae,files=A if ae else r['d082_evidence_files'],
       limit='原每格500次/1000秒、原22500均为历史对照；18k已取消；D083没有正式TableI调用。保存单路径/平面诊断不填入空间500分母。',pop='新增正式TableI=0；原22500、取消18000均保留。')
  elif i in ('P4-T08-II_ABLATION','P4-T08-III_ABLATION'):
   put(r,'SPATIAL_PARTITION_ABLATION_NOT_PERFORMED_SWITCH_MECHANISM_ONLY',ae=AD,files=A,
       limit=AL+' II两次/III四次角色转换只是保存解机制，不是full/fixed/NR/RSS同条件性能比较。')
  elif i=='P4-T03-III' or i=='P4-T05-III_NR':
   put(r,'NO_QUALIFIED_SPATIAL_III_NR_PATH_NO_NEW_SOLVE',files=r['d082_evidence_files'],limit='III本次复用PCS路径；不以II NR或平面NR替代III NR路径资格。')
  elif i in ('P4-T07-RSS_II','P4-T07-RSS_III','P4-T05-II_RSS','P4-T05-III_RSS'):
   put(r,'NO_QUALIFIED_SPATIAL_RSS_PATH_HISTORICAL_FAILURE_PRESERVED',files=r['d082_evidence_files'],limit='D083没有新空间RSS求解；平面C3三条任务路径不能代替空间RSS/随机跨奇异成功。')
  elif i in ('P4-T05-I_PCS','P4-T05-I_NR','P4-T05-I_RSS'):
   put(r,'PLANAR_LOCAL_DISCRETE_QUALIFICATION_SUPPLEMENT_PARTIAL',be=BD if i.endswith('PCS') else '',ce=CD,files=B+';'+C,
       limit=BL+' '+CL+' 成功路径有限离散资格，不作CCD/全局分布结论。')
  elif i in ('P4-T24','P4-T24-GAMMA') or i.startswith('P4-T24-STEP_'):
   put(r,'COMMON_FROZEN_PARAMETERS_NO_NEW_TUNING',ce=CD if i in ('P4-T24','P4-T24-GAMMA','P4-T24-STEP_I') else '',
       files='configs/p4_d083/difficult_v1.json;'+C,
       limit='保留原gamma0.2与冻结统一设置；没有重调种子/几何/阈值或原方法独立profiling，不宣称调优复现。')
  elif i=='P4-T25':
   put(r,'SOURCE_HASH_BOUND_VERSIONED_REPRODUCIBLE_RECONSTRUCTION',ae=AD,be=BD,ce=CD,
       files=A+';'+BF+'run_metadata.json;'+CF+'run_metadata.json',
       limit=AL+' '+BL+' '+CL+' 机器/语言/库与作者原论文不同，不冒称原机器秒数。')
  elif i=='P4-T29':
   r['d083_scope']='CONCEPTUAL_TRANSFER_ANALYSIS_ONLY_NO_FR3_ADAPTATION'
   put(r,'CONCEPTUAL_FUTURE_TRANSFER_ONLY',files='reports/P4_D082_ALGORITHM_FINDINGS_20261022.md;scripts/p4_d083/build_chinese_report.py',
       limit='仅讨论NR/RBS/PCS/RSS迁移前提、接口与限制；没有FR3、Isaac、ROS、硬件或下一篇执行。')
  elif parent in ('P4-T04','P4-T20','P4-T21','P4-T22','P4-T27','P4-T30') or i.startswith('P4-T06-EQ'):
   r['d083_limitations_and_missing']='无该原指标的新专项实验；沿用D082代理/理论/UNKNOWN界限。'+r['d082_limitations']
 new.append(r)
assert len(new)==211
with NEW.open('x',newline='',encoding='utf-8') as f:
 writer=csv.DictWriter(f,fieldnames=old_fields+new_fields);writer.writeheader();writer.writerows(new)
with NEW.open(newline='',encoding='utf-8') as f:
 reader=csv.DictReader(f);new_loaded=list(reader);loaded_fields=reader.fieldnames
assert loaded_fields[:257]==old_fields
mismatches=[(n,k) for n,(a,b) in enumerate(zip(old,new_loaded)) for k in old_fields if a[k]!=b[k]]
assert not mismatches
vi=[r['item_id'] for r in new if r['d083_scope']=='ARCHIVED_VI_NO_NEW_EXECUTION']
assert len(vi)==21
assert all(any(r['item_id']==f'P4-T{i:02}' for r in new) for i in range(1,31))
summary=collections.Counter(r['d083_actual_status'] for r in new)
lines=['# D083 原文—批准范围—实际证据覆盖表','',
 '本表完整继承D082的211行、257个历史字段；所有历史单元值逐一相同，只追加15个D083字段。旧失败/未知、原22,500与取消18,000、21个VI只读行全部保留。完整原文要求和所有历史信息见同名CSV；以下逐行列D083增量，不能把这些局部标签解释为原论文FULL。','',
 '## D083实际增量','',
 '- A：原保存II PCS177/NR393、III PCS649轨迹，真实3D图、轨迹图、III四切换帧/时间线/GIF；零新空间规划。II另外413/689/SBL沿旧证书，未重做。',
 '- B：同96合法端点/180非自对；2880候选+900实际策略，m1 176/180、m≥2 180/180；原混杂已消除，条件总体和原m20/NR/Bi-RRT时间缺口保留。',
 '- C：36预注册调用，35完整/1artifact UNKNOWN；PCS8合格+1未知、fixed0与NR各9/9、RSS3/9。三条件均NOT_ESTABLISHED_HARD；没有证明PCS性能优越，未升级/换种子。',
 '- 所有空间证据限aligned、source collision policy和离散点；native TCP及CCD缺口保留。IV/V/VI新增实验0；交付后停止等用户审核。','',
 '## 逐行增量映射','',
 '| 项目 | 原文要求 | D083范围 | D083实际状态 | 新证据 | 限制/缺失 |','|---|---|---|---|---|---|']
def cell(s):return s.replace('|','/').replace('\n',' ')
for r in new:
 evidence='；'.join(x for x in [r['d083_stage_A_evidence'],r['d083_stage_B_evidence'],r['d083_stage_C_evidence']] if x)
 lines.append('| '+' | '.join(cell(x) for x in [r['item_id'],r['original_requirement'],r['d083_scope'],r['d083_actual_status'],evidence or 'D082历史结果保留；无新专项计算',r['d083_limitations_and_missing']])+' |')
with MD.open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
verify={'schema':'P4_D083_COVERAGE_PRESERVATION_V1','source':str(OLD.relative_to(ROOT)),
 'source_sha256':sha(OLD),'output_csv':str(NEW.relative_to(ROOT)),'output_csv_sha256':sha(NEW),
 'output_md':str(MD.relative_to(ROOT)),'output_md_sha256':sha(MD),'historical_rows':211,
 'historical_columns':257,'appended_d083_columns':15,'total_columns':272,
 'historical_cell_comparisons':211*257,'historical_cell_mismatches':mismatches,
 'all_parent_T01_T30_preserved':True,'VI_only_archived_rows':vi,'VI_only_count':len(vi),
 'status_counts':dict(summary),'new_scientific_calls_from_this_mapping':0,
 'evidence_inputs_sha256':{x:sha(ROOT/x) for x in [A,B,C]}}
with VERIFY.open('x',encoding='utf-8') as f:json.dump(verify,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:verify[k] for k in ['historical_rows','historical_columns','total_columns','historical_cell_comparisons','historical_cell_mismatches','VI_only_count']}))
