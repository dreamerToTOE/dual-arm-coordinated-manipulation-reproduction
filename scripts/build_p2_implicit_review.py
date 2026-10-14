#!/usr/bin/env python3
"""Saved-evidence-only Word review; does not import/evaluate physical algorithms."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import build_p2_stage2_report as prior
ROOT=prior.ROOT
TITLE=prior.TITLE
ASSETS=ROOT/'reports/p2_implicit_review_assets'
OUTPUT=ROOT/'reports'/(TITLE+'_隐式资格审查.docx')

def read(p):return json.loads(Path(p).read_text())
def indexed(p):
 h=read(p/'artifact_sha256.json')
 for name,value in h.items():
  assert prior.sha(p/name)==value,(p,name)
 return h

def main():
 if ASSETS.exists() or OUTPUT.exists():raise FileExistsError('Preserve prior reports and assets')
 qual=ROOT/'results/20261014_P2_implicit_qualification01';diag=ROOT/'results/20261014_P2_implicit_FD_diagnosis01';qh=indexed(qual);dh=indexed(diag)
 q=read(qual/'summary.json');d=read(diag/'summary.json');meta=read(qual/'metadata.json')
 assert q['completed_checks']==46 and q['passed_checks']==45 and q['status']=='FAIL_STOP'
 assert d['status']=='DIAGNOSTIC_ONLY_ORIGINAL_FAIL_STOP_RETAINED'
 cases=[json.loads(s) for s in (qual/'cases.jsonl').read_text().splitlines()]
 assert len(cases)==q['completed_checks'] and sum(c['pass'] for c in cases)==q['passed_checks']
 old=prior.load_bundle(ROOT/'results/20261014_P2_stage2_dynamics01');cfg=prior.read_json(prior.PROTOCOL)
 assert prior.sha(prior.PROTOCOL)==prior.PROTOCOL_SHA and prior.sha(ROOT/prior.MATERIALS[-1])==prior.PDF_SHA
 ASSETS.mkdir();prior.setup_plots();r=prior.P2Report();prior.theory(r,cfg,ASSETS,review=True)
 r.doc.paragraphs[1].text='隐式数值资格审查 · 原模型、状态估计与联合控制 · 完整P2部分完成'
 r.page('第二部分  实际执行证据与数值资格停点')
 r.h('9 当前实现与实际验证范围')
 r.p('我在eb2600a之后实施已批准的隐式耦合Lie中点plant，并增加与原Python模型等价的C++计算核。原接触几何、式(9)–(12)/(16)以及控制式(19)–(21)/(25)保持；v2只版本化积分解释与授权/来源元数据。原式(18)估计均值仍作右Euler预测，没有因plant获批而自动更换。')
 r.table(['层次','已实现内容','实际资格'],[
 ['接触几何','此前已批准有限形变约束；源码保持','历史68/68沿用'],
 ['独立动力学','原式9–12/16及新的24未知隐式Newton','本次核等价45通过/1失败；隐式轨迹未执行'],
 ['42维IESEKF','右误差、固定prior/五次迭代、C Schmidt、Joseph及right reset','源码存在；未运行组件测试/滤波轨迹'],
 ['模拟视觉触觉','独立随机流、采样/到达戳、75对静态标定、观测初始化','源码存在；未运行组件资格'],
 ['位姿与内力控制','独立UF/UP、同坐标前馈/反馈、H选择与命令界','源码存在；未运行组件资格'],
 ['时序与四组实验','固定条件和已登记30case保留','集成runner尚未完成；30项NOT_EXECUTED']],[3.2,7.2,6],size=8)
 r.p('新source冻结37ccba0后执行N/D首跑，保存46项检查：45通过、1失败，实际状态FAIL_STOP。36项只核对原有限输入上的τ和G body twist，是新backend等价检查；A的9项H组合另比较完整接触力/合wrench/内力和连续field。它们不是新的68项模型审查，不代表隐式物理积分或闭环已经合格。')
 r.h('9.1 隐式数值实现及原文区别')
 r.eq(['δ = Δt f(X_old ⊞ δ/2, U_held),   X_new = X_old ⊞ δ'],'本次批准数值实现；非原文新控制公式')
 r.p('E1/E2的已知增量为ΔtU，C增量为0；联合求解O、Vo、G1、G2共24未知。初值为原field的Euler增量，最多12次完整Newton修正；各残差分量≤10⁻¹²才接受。没有线搜索、隐式失败显式兜底、substep、状态投影或抓点重锚。未通过资格前，不以编译成功宣称收敛或稳定。')
 r.p('计算核使用本机g++11.4.0、Eigen3.4.0和Boost1.74.0，前向AD产生右扰动连续Jacobian；Boost50位仅作为中央差分资格计算。C++与Python解析Jacobian独立实现，50位差分与C++共享primal field，所以先前原Python力/速度等价检查不可省略。快速Log覆盖协议soft-pad域，不能宣称全部π图域等价。')
 r.p('沿用原120s/单case、7200s/总套、5个种子、时刻、观测噪声、gain/刚度及评分；控制run仍0。原失败不覆盖，未执行的85–95s位置/角度RMS和13–76s内力RMS均为空缺，而不是0。')
 r.page('10 固定中央差分资格失败与实际诊断')
 row=d['rows'][0];r.p('首跑停在native_Jac_transport_tight_tight。完整42×42矩阵在原目录保存；零基行9/列27为物体body角加速度ω̇x对C右旋转扰动δθx的偏导，单位(rad/s²)/rad=s⁻²。以下只比较这个具有统一单位的分量，不把力、力矩和位姿混成范数。')
 r.table(['计算/门限','值 / s⁻²','含义'],[
 ['native前向AD',format(row['AD_row9_col27'],'.15g'),'待审查导数'],
 ['ε=10⁻⁶中央差分',format(row['FD_row9_col27'],'.15g'),'实际资格oracle'],
 ['绝对差异',format(row['error_row9_col27'],'.15g'),'超过门限，FAIL保持'],
 ['逐分量门限','1e−7','原值保持']],[5,5.6,5.8],size=9)
 r.p('native AD与独立Python解析链在完整矩阵中逐分量差异最大6.522213880089112×10⁻¹⁰，各块仍保留自身单位；field逐分量最大差4.547473508864641×10⁻¹³。解析一致尚不能替代原差分资格。首门停止后，隐式单步、六条五秒积分、半步、滤波和控制均未执行；尚无隐式物体响应曲线，也不能称滤波已发散。')
 r.h('10.1 一轮固定规模差分诊断')
 r.eq(['D₂(h) = f′(0) + ',prior.fraction('h²','6'),' f‴(0) + O(h⁴)'],'二阶中央差分Taylor误差')
 r.table(['ε / rad','同一偏导误差 / s⁻²','对原ε的误差比','用途'],[[format(x['epsilon'],'.1e'),format(x['error_row9_col27'],'.10g'),format(x['error_row9_col27']/row['error_row9_col27'],'.9g'),'原资格FAIL' if x['qualifying_epsilon'] else '只作诊断'] for x in d['rows']],[3.0,5.1,4.2,4.1],size=9)
 eps=np.array([x['epsilon'] for x in d['rows']]);err=np.array([abs(x['error_row9_col27']) for x in d['rows']]);order=np.argsort(eps)
 fig,ax=plt.subplots(figsize=(8.8,4.7));ax.loglog(eps[order],err[order],'o-',label='已保存三点误差');ax.loglog(eps[order],row['error_row9_col27']*(eps[order]/1e-6)**2,'--',label='以原点为锚的 h² 比例参考');ax.axhline(1e-7,color='#b43c31',linestyle=':',label='原逐分量门限');ax.set_xlabel('差分角扰动 h / rad');ax.set_ylabel(r'同一偏导绝对差 / $s^{-2}$');ax.set_title('固定数学点：差分截断诊断；没有状态积分或控制');ax.grid(alpha=.25,which='both');ax.legend();fig.tight_layout();figpath=ASSETS/'05_fixed_FD_truncation.png';prior.save_figure(fig,figpath);r.picture(figpath,'图5 固定三点中央差分诊断。数据来自同一已保存矩阵；比例参考不是控制曲线，也不解除原FAIL_STOP。')
 r.p('步长加倍/减半时误差约3.999/0.250，支持二阶截断项为主要来源。高精度减少舍入，却不消除h²截断。只诊断这一个固定A点，不能扩展为所有模式/状态/控制均已正确。原ε=10⁻⁶及10⁻⁷门限不变，未以诊断小步长替代资格。')
 r.h('10.2 停点、修正和后续资格')
 r.p('诊断首跑在保存三份矩阵后，summary写入遇到numpy.int64的JSON类型错误。累计小修2仅将索引转Python int，并从已有NPZ只读恢复归档；没有重算矩阵或追加仿真。缺失的脚本自身墙钟记null，外部工具的进程墙钟另标0.145563236s。累计预算2/3，余1，原资格失败原样保留。')
 r.eq(['D₄(h) = ',prior.fraction('−f(2h)+8f(h)−8f(−h)+f(−2h)','12h')],'四阶差分候选；尚未批准/执行')
 r.p('若要采用四阶差分，只改变native continuous-field的资格oracle，保留h=10⁻⁶、绝对门10⁻⁷及所有物理/估计/控制条件。由于本次已经冻结为二阶中央差分，不能由我用候选式改判已有结果或越过门继续实验。这一问题需要新的明确数值资格裁决；本次先停止并完整保存证据。原观察器预测也仍需后续真实资格，未获任何变更授权。')
 r.page('11 先前真实无控制动力学与原论文比较边界')
 r.p('以下三图只重绘9194f9f旧首跑的原始状态/接触日志，831个250Hz样本至3.32s；实际最后积分3.324s，120秒限制停止。它们属于隐式路线前的显式中点失败前缀，不是本次implicit结果或四组联合控制结果。原记录和阶段Word保持。')
 figs,_=prior.dynamics_assets(old,ASSETS,2)
 for p,c in figs:r.picture(p,c)
 r.table(['原论文描述性结果','本机当前证据','比较结论'],[
 ['exp2约10mm / 4.5°','20主实验均未执行','无法对照控制误差'],
 ['exp1多数阶段约1.5N内部力','仅对称无控制真实前缀，内力约数值零','不能据此宣称反馈有效'],
 ['平移低于0.1mm卡尺分辨率；角0.42°','没有85–95s目标窗口','原文删失界不作为本机精确数据'],
 ['exp4失配瞬态变差/稳态近似','仅原model K条件已编码','无控制对照证据'],
 ['高力矩约80%末端降幅；非稳态','高力矩控制未执行','不能报告已复现80%']],[6.3,5.1,5],size=8)
 r.p('P2仍部分完成。运动学68项、旧动力学11项与本次native 45项分别来自不同层次，不相加成联合控制通过次数。20主和10代表/诊断继续标NOT_EXECUTED，不能把尚未运行写成30次控制失败。原图6–9所需的物体误差、两侧真实内力/内力矩、估计误差、四组定量统计仍未获得。')
 r.h('11.1 来源和可核查文件')
 r.table(['来源','身份及实际范围'],[['科学source','37ccba0；N/D46项，45通过/1失败'],['诊断source','c66496e；固定三点，零积分/零控制'],['归档小修source','ee97134；恢复已有矩阵，零重算'],['v1 SHA256',prior.PROTOCOL_SHA],['v2 SHA256',meta['protocol_sha256']],['旧真实plant','results/20261014_P2_stage2_dynamics01'],['本次qualification','results/20261014_P2_implicit_qualification01'],['固定diagnosis','results/20261014_P2_implicit_FD_diagnosis01']],[4.1,12.3],size=8)
 prior.application(r);r.doc.save(OUTPUT)
 data={'title':TITLE,'report_builder_sha256':prior.sha(Path(__file__)),'inherited_builder_sha256':prior.sha(ROOT/'scripts/build_p2_stage2_report.py'),'qualification_artifact_sha256':qh,'diagnostic_artifact_sha256':dh,'old_true_dynamics_index_sha256':prior.sha(old.path/'artifact_sha256.json'),'report_docx_sha256':prior.sha(OUTPUT),'assets_sha256':{p.name:prior.sha(p) for p in sorted(ASSETS.glob('*.png'))},'closed_loop_runs':0,'implicit_plant_trajectories':0,'corrections_used':2,'experiment_execution_by_report':False}
 (ASSETS/'report_data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'docx':str(OUTPUT),'figures':len(data['assets_sha256']),'status':'PARTIAL_FAIL_STOP'},ensure_ascii=False))
if __name__=='__main__':main()
