#!/usr/bin/env python3
"""Append D082 evidence without changing any of the 211 x 248 history cells."""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'reports/P4_D080_III_RRT_PCS_PHYSICAL01_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261019.csv'
OUT = 'reports/P4_D082_ORIGINAL_VS_APPROVED_VS_ACTUAL'
NUM = 'results/20261019_D081_numeric_pilot'
PAIRED = 'results/20261019_D081_stability_pilot'
ORACLE = 'results/20261022_D082_independent_planar01/summary.json'
FINDINGS = 'reports/P4_D082_ALGORITHM_FINDINGS_20261022.md'
ANALYSIS = 'results/20261022_D082_saved_analysis01/summary.json'
SPATIAL = 'reports/P4_D082_SPATIAL_RECOVERY_20261022.json'
FIGURES = 'reports/p4_d082_research_assets_20261022/manifest.json'
COMMON = '独立重建平面20R；有限离散验证，无连续CCD；不等同原论文空间I–VI或全部原生软件/统计。'
DESIGN = '50 paired pilot calls=5 methods x2 scenes x5 seeds[7,23,41,59,73]; 20 exploratory numeric calls separate; formal Table I=0'

# status, concrete actual evidence, limitations, evidence files
MAIN = {
 '01': ('algorithm_partial','闭链定义、20R几何/限位/障碍及独立数值oracle均有实现。','定义和重建数值证据不覆盖原论文全部模型与理论证明。', ORACLE),
 '02': ('algorithm_partial','重建APC解析3R、双IK分支及投影真实成功/失败；原空间II/III已有解析分支资格。','平面只实现17个连续正长3R划分，不能替代原20划分。', f'{NUM}/projection_trials.csv;{SPATIAL}'),
 '03': ('algorithm_partial','768条NR投影成功768条；保留迭代、残差、耗时和独立FD数学检查。','不是原50万样本/全部空间NR栈的完整重复。', f'{NUM}/projection_trials.csv;{NUM}/summary.json'),
 '04': ('reduced_scale_proxy','APC/NR各768投影，共1536条原始记录。','原500000随机样本未执行；模型和采样分布有差异。', f'{NUM}/projection_trials.csv'),
 '05': ('verified_discrete_reconstructed','50次paired pilot中26条成功全路径经独立oracle：2142保存点+6348策略中点，2116叶全通过。','只验证离散点与固定策略加密，未证明连续扫掠安全。', ORACLE),
 '06': ('theory_and_proxy_partial','局部可见性有RSS/PCS/NR各240对真实RBS数值。','有限抽样不证明原文可见域概率界；可比性与假设必须逐项保留。', f'{NUM}/fig4_visibility_pairs.csv'),
 '07': ('algorithm_partial_rss_planning_failed','RSS paired规划0/10；72奇异请求、2304构造全IK_UNREACHABLE；另有rank2和两侧分支桥数学正例。','无接受闭合奇异目标；根因UNKNOWN，不以手工桥替代RSS规划成功。', f'{FINDINGS};results/20261022_D082_saved_analysis01/saved_rank_and_bridge_evidence.json'),
 '08': ('algorithm_partial_no_pcs_advantage','fullPCS6/10、fixed0 10/10、fixed16 0/10；仅失败树1条真实0→16父子切换；6条成功PCS最终路径切换0。','fixed16端点分支不兼容，仅作结构性负对照；fullPCS未优于公平fixed0。', f'{ANALYSIS};{FINDINGS}'),
 '09': ('matched_proxy_pilot_only','同重建场景/种子/公共预算：NR10/10、PCS6/10、fixed0 10/10、fixed16 0/10、RSS0/10。','计时为重建Python/GEOS；不同方法随机消耗和计算成本不同；未复现全部原生栈。', f'{PAIRED}/planner_trials.csv;{ANALYSIS}'),
 '10': ('verified_reconstructed_virtual_task','平面20R E0/E1完整起终点任务及26条独立合格路径，真实障碍和限位，保留24次TIME_LIMIT。','属于重建平面任务，不冒称原环境I端点/障碍完全相同。', f'{ORACLE};{FIGURES}'),
 '11': ('reused_qualified_spatial_discrete','环境II四条完整路径：RRT/PCS177、RRT/NR393、CBiRRT/PCS413、CBiRRT/NR689节点。','A01重建端点、aligned原离散策略，native TCP/杆件/省略pair等限制保留。', SPATIAL),
 '12': ('reused_qualified_spatial_discrete','环境III RRT/PCS649节点、15里程点、14边、4次最终路径角色切换；绑定/hash恢复通过。','aligned重建离散证据；649个native TCP均不一致，无连续CCD。', SPATIAL),
 '13': ('preserved_incomplete_not_required_full_env','保留环境IV原模型、端点/腕部资格与失败；D082未新增完整规划。','原IV完整任务未复现，不把组件资格当完整路径。', SOURCE),
 '14': ('preserved_failure_v5_engineering_only','保留V source/碰撞失败；V4残缺前缀无完整目标路径；V5仅工程候选。','V5新source未授权且未执行；不将stdout solved当独立合格轨迹。', 'reports/P4_D081_V_SOURCE01_V5_GUARD_SCOPE_ADDENDUM_20261019.md'),
 '15': ('archived','VI所有数学、失败和974/974历史预算只读保全。','D082不执行VI，不能报六环境完整复现。', SOURCE),
 '16': ('partial_endpoint_and_path_witnesses','II四条及III一条保存空间路径；平面任务26条独立合格路径。','原六环境/原始端点跨奇异结论未全部核实，IV/V不补成功、VI归档。', f'{SPATIAL};{ORACLE}'),
 '17': ('reduced_planner_comparison','平面重建单套双树规划栈完成50次paired pilot；空间II有RRT/CBiRRT已有路径。','未执行所有RRT/Bi-RRT/SBL×三方法×全环境，不能按完整组合解释。', f'{PAIRED}/planner_trials.csv;{SPATIAL}'),
 '18': ('formal_scale_cancelled_proxy_pilot','原TableI分母22500保留；D080历史18000已D081取消；本次比较为50次paired pilot。','正式原TableI试验仍0；20次探索pilot单列，不能合并为500/单元。', f'{PAIRED}/planner_summary.json;{NUM}/summary.json'),
 '19': ('fig3_population_confounded_partial','m=1,2,3,7,16各180对保存RBS记录。','m组重新生成状态池，m1有19/180自配对、m16无；不可因果归因于m；原m20缺失。', f'{NUM}/fig3_pairs.csv;{FINDINGS}'),
 '20': ('table_ii_proxy_metrics_partial','paired50记录samples、失败/超时、树节点、局部调用、投影数、路径长度与耗时。','这些是平面proxy；无原空间II原TableII各算法调优/完整成本口径。', f'{PAIRED}/planner_trials.csv;{ANALYSIS}'),
 '21': ('reduced_visibility_proxy','RSS/PCS/NR各240对，共720行真实局部连接记录，距离分箱可复核。','原50000合法点对未执行；图注I/正文II与重建模型差异单列。', f'{NUM}/fig4_visibility_pairs.csv'),
 '22': ('fig5_proxy_partial','APC/NR各384行投影前后距离变化，共768行。','扰动/参照邻点定义与原图条件不完全一致；不能原样同条件比较。', f'{NUM}/fig5_distance_change.csv'),
 '23': ('obstacle_ablation_proxy_negative','E0稀疏/E1杂障使用相同端点与paired种子；成功率相同，无PCS优势。','不是原空间各环境逐个移除障碍实验；现路径指标高度相似，不能宣称复杂窄通道优势。', f'{PAIRED}/planner_summary.json;{FINDINGS}'),
 '24': ('common_budget_not_original_tuning','保存统一pilot预算/分辨率/随机种子，RSS奇异概率0.2。','未逐方法调优步长；不是论文最优参数性能排名。', f'{NUM}/config_snapshot.json;{PAIRED}/config_snapshot.json'),
 '25': ('traceable_reconstruction_partial','源码、配置、raw gzip、50-artifact manifest、独立数值与历史空间hash链接完整。','保留Python/GEOS与原OMPL/KDL/PQP、几何及作者条件的差异；作者raw到论文统计仍未全闭合。', f'{ORACLE};{SPATIAL};{FINDINGS}'),
 '26': ('discrete_safety_and_cost_partial','真实约束/碰撞与RBS、局部调用、投影成本、净空和路径曲线均可核。','无连续CCD、动力学/时间参数化或空间复杂场景完整统计。', f'{ORACLE};{ANALYSIS};{FIGURES}'),
 '27': ('model_applicability_partial','区分平面17划分与空间双臂角色切换；III最终路径4次角色切换。','三臂独立/依赖多闭环限制未解决，VI归档；不能从平面划分数推广空间。', f'{SPATIAL};{FINDINGS}'),
 '28': ('negative_findings_no_original_advantage_claim','当前pilot NR与兼容fixed0全成功，PCS6/10，RSS0/10，明确报告负面发现。','样本小、场景弱、fixed16不兼容；不证明原PCS障碍优势或RSS方法本身失效。', f'{ANALYSIS};{FINDINGS}'),
 '29': ('conceptual_future_application_only','D082报告最后章讨论双FR3接口、约束/Jacobian/IK/碰撞前置与未来研究。','本阶段不实现FR3适配，不声称机器人/Isaac实证；完整性以最终报告为准。', 'docs/tasks/P4_D082_VIRTUAL_SIMULATION_EXECUTION_20261019.md'),
 '30': ('original_distribution_claim_unverified','有限投影成功率/距离记录保存。','未建立全部环境APC/NR输出分布近似相同或流形覆盖的统计证据。', f'{NUM}/projection_trials.csv'),
}


def map_row(row):
    item = row['item_id']
    number = re.match(r'P4-T(\d\d)', item).group(1)
    status, actual, limitations, evidence = MAIN[number]
    scope = 'D082核心算法/重建虚拟任务；原论文该义务保留历史层级'
    env_match = re.search(r'(?:^|[-_])(VI|III|II|IV|V|I)(?:$|[_-])', item)
    env = env_match.group(1) if env_match else None
    if env == 'VI' or number == '15':
        return 'D082排除新执行；VI只读归档', 'archived', '沿用历史VI数学/失败/预算记录，新增调用0。', SOURCE, '原实验未完成部分保持；974/974预算及UNKNOWN不改判。'
    if item == f'P4-T{number}':
        return scope, status, actual, evidence, limitations
    if number == '01':
        if 'FIG1c' in item:
            return scope, 'mathematical_bridge_only', '保存rank2及两侧RSS分支桥正例；完整RSS规划仍失败。', f'{FINDINGS};results/20261022_D082_saved_analysis01/saved_rank_and_bridge_evidence.json', '桥数学正例不替代随机RSS全路径成功或原Fig1图像完全复现。'
        return scope, 'definition_and_reconstructed_illustration', actual, f'{ORACLE};{FIGURES}', '方程/示意解释覆盖此项，未将理论图示当实验统计。'
    if number == '06':
        return scope, 'theory_explained_not_fully_numerically_proved', '原公式适用条件与独立/依赖链解释；有限局部记录作为机制证据。', f'{NUM}/fig4_visibility_pairs.csv;{FINDINGS}', '有限pilot不能证明此条概率界或全部原数学假设。'
    if env in ('IV','V') and number in ('02','03','05','07','08','16','17','18','23','24','30'):
        return f'D082保留环境{env}历史结果，非本次主任务完整通过前提', 'preserved_incomplete', f'此环境{env}原模型、数学/碰撞诊断与失败原样保留；无本次完整合格路径。', SOURCE, '不得以其他环境/平面proxy成功替代此原环境对应项。V5仅工程候选、无新source授权。' if env == 'V' else '不得以其他环境/平面proxy成功替代此原环境对应项。'
    if number == '08' and env in ('II','III'):
        return scope, 'not_performed_spatial_partition_ablation', f'环境{env}已有空间PCS路径及角色切换见证，未执行此环境full/fixed公平消融。', SPATIAL, '平面fixed0/fixed16结果单独报告，不能填作该空间环境划分消融。'
    if number == '07' and env in ('II','III'):
        return scope, 'no_qualified_spatial_rss_path', f'环境{env}没有已独立合格的RSS完整路径；保留原RSS失败。', SOURCE, '平面72请求/2304候选失败是另一重建模型证据，不代替此空间环境RSS执行。'
    if number == '18':
        known = {'P4-T18-II_RRT_PCS':'II RRT/PCS177节点','P4-T18-II_RRT_NR':'II RRT/NR393节点','P4-T18-II_Bi-RRT_PCS':'II CBiRRT/PCS413节点','P4-T18-II_Bi-RRT_NR':'II CBiRRT/NR689节点','P4-T18-III_RRT_PCS':'III RRT/PCS649节点'}
        if item in known:
            return 'D082复用个案；原500次/单元不再要求', 'single_spatial_path_reused_no_formal_statistics', known[item]+'完整离散保存证据。', SPATIAL, '此行正式TableI次数0/500；保存个案不替代原统计，CBiRRT与论文Bi-RRT实现差异保留。'
        return 'D082不要求原正式全组合规模', 'not_executed_original_cell', '该原空间planner×method单元无完整D082正式统计；原失败和未知保留。', SOURCE, '正式次数0/500；平面paired50不填入空间表格此行。'
    if number == '19':
        if 'M20' in item:
            return scope, 'not_available_original_m20', '本重建机制仅17个连续正长3R划分，未合成m20。', f'{NUM}/summary.json;{FINDINGS}', '原m20曲线/耗时缺失；不能把m16改名m20。'
        if item.endswith('_NR'):
            return scope, 'not_performed_matched_fig3_nr', 'NR局部连接数据位于另一个Fig4-like池，未形成Fig3同池控制NR曲线。', f'{NUM}/fig4_visibility_pairs.csv', '不能挪用不匹配池当原Fig3 NR基线。'
        if item.endswith('PLANAR_PROJECTION'):
            return scope, 'reduced_scale_proxy', 'APC/NR各768投影记录。', f'{NUM}/projection_trials.csv', '原50万投影未执行，17划分/重建采样差异保留。'
        match = re.search(r'_M(\d+)$', item)
        if match and int(match.group(1)) not in (1,2,3,7,16):
            return scope, 'not_performed_original_chain_count', '此原m值未列入D081重建pilot。', f'{NUM}/config_snapshot.json', '不插值、不用理论曲线补运行数据。'
        return scope, 'fig3_population_confounded_partial', '对应m保存180条局部连接及wall数据。', f'{NUM}/fig3_pairs.csv;{FINDINGS}', '各m重建状态池不同，m1自配对19/180；无可控因果m趋势，原完整运行时间曲线未复现。'
    if number in ('02','03','16') and env in ('II','III'):
        return scope, 'reused_spatial_math_or_path', f'原环境{env}重建模型/端点已有数学与完整离散路径证据；逐项不重跑。', SPATIAL, '原始舍入端点失败及native TCP不一致保持；不升级为全分支/全空间/CCD覆盖。'
    if number == '16' and env == 'I':
        return scope, 'verified_reconstructed_endpoints_not_original_I', '重建E0/E1具有合法起终点、关节界及26条独立合格完整路径。', ORACLE, '不声称原环境I的原始端点/奇异跨分支任务完全一致。'
    if number == '23' and env in ('II','III'):
        return scope, 'not_performed_spatial_obstacle_removal', f'原环境{env}保存完整路径；未执行该环境配对移除障碍消融。', SPATIAL, '平面E0/E1不能替代此空间环境原消融。'
    if number == '30':
        return scope, 'original_distribution_claim_unverified', actual, evidence, limitations
    if number == '07':
        return scope, 'algorithm_partial_rss_planning_failed', actual, evidence, limitations
    if number == '05' and env in ('II','III'):
        if item.endswith('_RSS'):
            return scope, 'no_qualified_spatial_rss_path', '保留RSS失败；该空间RSS完整路径未通过。', SOURCE, 'PCS/NR路径不替代RSS方法；原RSS分布/RBS问题独立保留。'
        if env == 'III' and item.endswith('_NR'):
            return scope, 'no_qualified_spatial_nr_path', '环境III未获得已独立合格的NR完整路径。', SOURCE, '环境III PCS路径不替代该NR项；旧失败/未知保留。'
        return scope, 'reused_spatial_discrete_rbs', f'环境{env}对应方法完整已保存RBS路径证据。', SPATIAL, '原离散碰撞限制保留；不证明连续CCD或全部局部对。'
    if number == '17' and env == 'I':
        return scope, 'single_proxy_planner_not_original_combination', '仅重建双树pilot真实运行，方法/规划器差异明确。', f'{PAIRED}/planner_trials.csv', '不能把同一重建planner改名为原RRT/SBL所有独立组合。'
    if number == '20':
        if item.endswith('NN_COST'):
            return scope, 'nearest_neighbor_cost_not_isolated', '保存树规模、总采样与局部投影调用成本。', f'{PAIRED}/planner_trials.csv', '未独立测最近邻耗时随树增大的原趋势，不将全wall差当NN成本。'
        return scope, 'table_ii_proxy_metrics_partial', actual, evidence, limitations+' 具体指标以原CSV实际列为准，无列值则未完成。'
    if item.endswith('AUTHOR_RAW_LINEAGE'):
        return scope, 'author_raw_to_paper_lineage_incomplete', '作者版本和本地重建运行来源分开保留。', SOURCE, '未完整闭合作者raw数据、筛选与最终论文所有数字的统计来源链。'
    if number == '24':
        return scope, 'common_budget_not_original_tuning', actual, evidence, limitations
    return scope, status, actual, evidence, limitations


def main():
    with (ROOT/SOURCE).open(newline='') as stream:
        original = list(csv.reader(stream))
    header, records = original[0], original[1:]
    assert len(header) == 248 and len(records) == 211
    oracle = json.loads((ROOT/ORACLE).read_text())
    assert str(oracle['status']).startswith('PASS'), 'Do not mark virtual task verified before independent PASS'
    extra = ['d082_scope','d082_actual_status','d082_actual_evidence_description','d082_evidence_files','d082_limitations','d082_original_table_I_denominator','d082_cancelled_historical_d080_target','d082_actual_paired_pilot_design','d082_record_date']
    output = []
    main_records = []
    for cells in records:
        row = dict(zip(header,cells))
        scope,status,actual,evidence,limits = map_row(row)
        appended=[scope,status,actual,evidence,limits+' '+COMMON,'22500','18000_CANCELLED_BY_D081',DESIGN,'2026-10-22']
        output.append(cells+appended)
        if re.fullmatch(r'P4-T\d\d',row['item_id']):
            main_records.append((row['item_id'],row['original_requirement'],status,actual,limits))
    csv_path=ROOT/(OUT+'.csv')
    with csv_path.open('x',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(header+extra);writer.writerows(output)
    with csv_path.open(newline='') as stream:
        written=list(csv.reader(stream))
    assert written[0][:248] == header
    assert all(a[:248] == b for a,b in zip(written[1:],records))
    assert len(written) == len(original)
    assert len(main_records) == 30
    counts=Counter(row[249] for row in output)
    source_sha=hashlib.sha256((ROOT/SOURCE).read_bytes()).hexdigest()
    oracle_sha=hashlib.sha256((ROOT/ORACLE).read_bytes()).hexdigest()
    lines=['# P4：原论文范围、D082批准范围与实际证据（2026-10-22）','',
        '本表继承211行原论文义务，原248列逐单元格保持；追加9列D082范围、状态、实际证据、限制及统计口径。原始矩阵有P4-T01–T30共30条主义务，全部保留（不是29条）。CSV读取回验确认211×248个历史值与列名/次序完全相同。', '',
        f'继承来源：`{SOURCE}`；SHA256 `{source_sha}`。独立主任务oracle：`{ORACLE}`；SHA256 `{oracle_sha}`；状态`{oracle["status"]}`。', '',
        '当前批准要求是核心算法与一套真实端到端虚拟任务。平面20R主任务50次paired pilot中26条成功路径已独立核闭链、界、碰撞、分支及加密策略中点；24次TIME_LIMIT保留。NR10/10、兼容fixed0 10/10、fullPCS6/10、fixed16 0/10、RSS0/10。完整任务的离散数值证据通过，不等于RSS规划已成功、原论文全部曲线相同或六环境完整复现。', '',
        '原TableI为22500次；D080历史目标18000次由D081取消；当前正式原TableI次数0。当前比较为50次预注册paired pilot（5方法×2场景×5种子），此前20次探索pilot单列，不能合并成500次/单元的正式统计，也不把重验已有路径计为新规划。', '',
        '空间II四条完整路径与III一条aligned离散路径只读复用；III最终路径4次角色切换。平面6条成功PCS路径的最终划分切换全部0，失败树仅1条真实父子切换。fixed16起终点分支不兼容，仅属结构性负对照，兼容fixed0才是公平的固定划分基线。未观察到PCS优于fixed0。', '',
        'RSS真实失败：72奇异请求/2304候选全部IK_UNREACHABLE，尚无接受的闭合奇异目标；根因UNKNOWN，保留rank2与两侧分支桥的数学正例，但不把正例代作RSS规划成功。Fig3各m使用不同状态池且含不同自配对比例，当前曲线不支持划分数的因果优势。原m20、500000投影和50000合法点对未做。', '',
        'VI只读归档，不新增科学调用；V5只是未授权source的工程候选。所有路径均为有限离散安全范围，无连续CCD；空间原碰撞pair/8mm容差/杆件模型和native TCP不一致继续保留。', '',
        '## 30条主义务', '', '|ID|原义务|D082当前状态|实际结果与限制|','|---|---|---|---|']
    for item,req,status,actual,limits in main_records:
        lines.append('|'+ '|'.join(x.replace('|','/').replace('\n',' ') for x in (item,req,status,actual+' '+limits))+'|')
    lines += ['', '## 211行状态分布', '', '|状态|行数|','|---|---:|']
    lines += [f'|{status}|{count}|' for status,count in sorted(counts.items())]
    lines += ['',f'合计{sum(counts.values())}行。各状态是本轮D082实际映射，不回写历史列的成功/失败；`partial`、`not_performed`、`archived`均不算原论文FULL。', '', '## 可复核入口', '',
        f'- 主任务独立数值资格：`{ORACLE}`。',f'- 空间保全与q12绑定：`{SPATIAL}`。',f'- 机制/失败根因与可比性：`{FINDINGS}`。',f'- 真正父子切换及最终路径统计：`{ANALYSIS}`。',f'- 七幅真实中文图与原数据：`{FIGURES}`。', '',
        '生成命令：`python3 scripts/p4_d082/build_coverage_20261022.py`。为保全已有交付，脚本以排他新建方式写入；再次生成须先指定/版本化新的输出文件名，不能覆盖旧矩阵。']
    with (ROOT/(OUT+'.md')).open('x') as stream:
        stream.write('\n'.join(lines)+'\n')
    print(json.dumps({'historical_rows':211,'historical_columns':248,'appended_columns':len(extra),'history_cells_preserved':True,'main_obligations':len(main_records),'statuses':dict(counts)},ensure_ascii=False))


if __name__ == '__main__':
    main()
