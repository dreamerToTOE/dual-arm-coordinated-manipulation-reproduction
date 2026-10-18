#!/usr/bin/env python3
"""Final review from saved implicit trajectories and stopped actual estimated loop."""
import gzip,json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import build_p2_stage2_report as base
ROOT=base.ROOT;TITLE=base.TITLE;ASSETS=ROOT/'reports/p2_closed_loop_review_assets';OUTPUT=ROOT/'reports'/(TITLE+'_闭环资格审查.docx')
def loadlog(p):
 with gzip.open(p,'rt') as f:return [json.loads(s) for s in f]
def indexed(p):
 d=json.loads((p/'artifact_sha256.json').read_text())
 for k,v in d.items():assert base.sha(p/k)==v,(p,k)
 return d

def main():
 if ASSETS.exists() or OUTPUT.exists():raise FileExistsError('Preserve all earlier reports')
 qdir=ROOT/'results/20261014_P2_implicit_qualification_v3_01';suite=ROOT/'results/20261014_P2_closed_loop_suite02';adir=ROOT/'results/20261014_P2_closed_loop_analysis01';run=suite/'case_11_exp3_7'
 sources={str(p.relative_to(ROOT)):indexed(p) for p in (qdir,suite,adir)};q=json.loads((qdir/'summary.json').read_text());s=json.loads((suite/'summary.json').read_text());a=json.loads((adir/'actual_prefix_metrics.json').read_text());cs=json.loads((run/'summary.json').read_text());ledger=json.loads((suite/'case_ledger.json').read_text());qc=[json.loads(x) for x in (qdir/'cases.jsonl').read_text().splitlines()];plant=loadlog(run/'plant.jsonl.gz');commands=loadlog(run/'commands.jsonl.gz');est=loadlog(run/'estimator.jsonl.gz');paired=np.load(adir/'actual_paired_curves.npz')
 assert q['passed_checks']==70 and s['executed_cases']==1 and cs['reason']=='ESTIMATOR_MODEL_PAD_DOMAIN_INVALID' and cs['GT_control_state_reads']==0
 ASSETS.mkdir();base.setup_plots();r=base.P2Report();cfg=json.loads((ROOT/'configs/p2_closed_loop_protocol_v3.json').read_text());base.theory(r,cfg,ASSETS,review=True);r.doc.paragraphs[1].text='独立动力学与真实视觉触觉闭环资格 · 完整P2部分完成'
 r.page('第二部分  真实动力学、状态估计与闭环资格结果')
 r.h('9 已实现方法及实际执行范围')
 r.p('我以原式(9)–(12)/(16)构建独立COM刚体与双侧软接触，使用已批准的几何一致G演化。物体位姿和接触载荷由实际受力积分产生，没有把期望位姿赋给物体，也没有按控制命令生成内力曲线。独立trueplant、按原R生成的传感器、42维估计和控制命令各自保存。主控制接口只读取观测初始化的滤波状态及旧已发布输入。')
 r.table(['资格层次','实际结果','含义'],[['有限接触几何','此前68/68通过','原批准模型与历史证据保持'],['本次隐式N/D','70/70，约11.25s','等价/Jacobian/残差/六条五秒/三组半步均通过'],['观测/IESEKF/控制组件','35/35','物理Jacobian、右重置、固定prior/Schmidt、时戳和原控制验证'],['因果端点时序','2/2','旧published与延迟actual分离，粗/半步物理时刻一致'],['完整闭环ID11','exp3/seed7，3.948s停止','估计pad域越界；95s与完整半步未获资格'],['20主/10其他账目','主1条失败、19未运行；其他10未运行','未取得四组反馈对照，不能填0值窗口RMS']],[4.2,5.3,6.9],size=8)
 r.h('9.1 数值协议及原文保真边界')
 r.eq(['δ = Δt f(X_old ⊞ δ/2,U_old),   X_new = X_old ⊞ δ'],'已批准implicit plant；不是修改原控制式')
 r.p('O、Vo与G1/G2共24未知用完整Newton耦合求解，E增量ΔtU、C增量0为已知；最多12次修正，逐分量残差≤10⁻¹²。原接触力、Rbar阻尼近似、质量/均质惯量、gain、观测频率和参考均保持。原观察器式(18)仍在真实测量/heartbeat事件间做右Euler，不采用plant的implicit步，也没有隐藏内部substep。')
 r.p('v2的两点中央差分资格原失败保留：ε=10⁻⁶时一个偏导差6.38×10⁻⁷>10⁻⁷，固定三点显示二阶截断比例。经明确批准，v3只将native continuous-field资格oracle改为50位五点四阶差分，仍ε=10⁻⁶/逐分量门10⁻⁷。它不改变动力学或估计公式，不把旧FAIL改判；原测量H和离散F资格保持。')
 r.p('g++11.4/Eigen3.4/Boost1.74数值核与canonical Python通过固定输入对照。AD、独立解析与高精度FD分别验证；不以共享primal的FD代替原Python模型对照。快速核只在原soft-pad域获资格，不宣称全π图域或真实机器人关节执行已复现。')
 r.page('10 六条真实五秒动力学与时间步资格')
 trials=[x for x in qc if x['name'].startswith('five_seconds_')]
 r.table(['真实无控制fixture/步长','壁钟 / s','终态max力残差 / N','max力矩残差 / N·m','线速度max / m/s','角速度max / rad/s'],[[x['name'].replace('five_seconds_',''),format(x['evidence']['wall_s'],'.5g'),format(max(abs(z) for z in x['evidence']['terminal_force_N']),'.4g'),format(max(abs(z) for z in x['evidence']['terminal_moment_Nm']),'.4g'),format(max(abs(z) for z in x['evidence']['terminal_linear_speed_m_s']),'.4g'),format(max(abs(z) for z in x['evidence']['terminal_angular_speed_rad_s']),'.4g')] for x in trials],[4.2,2,2.55,2.55,2.55,2.55],size=7)
 r.p('这些终态来自固定5s积分，不是解析平衡赋值。A、高力矩A和C均从原声明初态分别以1/3000s及1/6000s积分；锁EE、重力开启、控制关闭。每条1251个250Hz保存样本、完整状态和真实接触hK/hB保留。三个对象的half-step门分别判定，不能用对称无控制的近零内力推断联合控制有效。')
 fig,axes=plt.subplots(2,2,figsize=(10,6),sharex=True)
 for variant,color in zip(('transport','high_moment','sliding'),('#245d91','#a56a11','#348759')):
  for scale,style in (('coarse','-'),('fine','--')):
   rows=loadlog(qdir/(variant+'_'+scale+'.jsonl.gz'));t=np.array([z['time_s'] for z in rows]);O=np.array([z['state']['O'] for z in rows]);V=np.array([z['state']['V'] for z in rows]);bal=np.array([z['force_balance_N'] for z in rows]);mbal=np.array([z['moment_balance_Nm'] for z in rows]);label=variant+'/'+scale
   axes[0,0].plot(t,1000*(O[:,2,3]-O[0,2,3]),style,color=color,label=label);axes[0,1].plot(t,np.linalg.norm(V[:,:3],axis=1),style,color=color,label=label);axes[1,0].plot(t,np.linalg.norm(bal,axis=1),style,color=color,label=label);axes[1,1].plot(t,np.linalg.norm(mbal,axis=1),style,color=color,label=label)
 for ax,title,unit in zip(axes.ravel(),('真实world-z位移','真实线速度','接触加重力残差','真实力矩平衡残差'),('mm','m/s','N','N·m')):ax.set_title(title);ax.set_ylabel(unit);ax.grid(alpha=.25);ax.legend(fontsize=6)
 for ax in axes[1]:ax.set_xlabel('实际仿真时间 / s')
 fig.suptitle('六条固定EE五秒积分；未开启反馈');fig.tight_layout();p=ASSETS/'02_six_real_dynamics.png';base.save_figure(fig,p);r.picture(p,'图2 六条原始日志的真实重力支撑响应；粗/半步采用相同物理输出时刻，A两姿态在本对称重力fixture中曲线重叠。')
 steps=[x for x in qc if x['name'].startswith('step_refinement_')]
 r.table(['fixture','位置差 / m','角差 / rad','raw力差 / N','raw力矩差 / N·m','内力差 / N','内力矩差 / N·m'],[[x['name'].replace('step_refinement_',''),*[format(x['evidence'][k],'.5g') for k in ('position_m','angle_rad','raw_force_N','raw_moment_Nm','internal_force_N','internal_moment_Nm')]] for x in steps],[3.2,2.2,2.2,2.2,2.2,2.2,2.2],size=7)
 r.p('比较门保持位置50µm、角5×10⁻⁴rad、每force0.05N、每moment0.002N·m。无控制资格70项通过之后才进入原ID11；它们不能替代完整95s控制的粗/半步对照。旧120s仅积分至3.324s的显式失败仍另存，没有删除。')
 r.page('11 真实多率闭环与状态估计停点')
 r.p('首次正式名额为ID11、exp3、seed7、主步1/3000s。先用75对静止带噪视觉标定C，再执行5s锁EE真实settle，再以t=0全新EE/视觉观测初始化O/E、V=0、G为声明几何；已消费packet不重复更新。单case包含全部阶段，壁钟24.939s，没有重置case计时绕过120s。')
 r.p('端点按200/50Hz发布、触觉100Hz、视觉15Hz，控制及滤波heartbeat250Hz；事件都按整数tick。旧actualU驱动物体，观测仅由真实state生成，filter预测使用旧publishedU，更新后controller计算新命令，再发布并施加下一物理区间。主控制读取GT状态次数为0；传感/评分使用真值有明确标签。')
 r.p(f"该case在t={a['actual_stopping_time_s']:.6g}s发生{a['failure']}。控制日志有{a['transport_samples']}个样本至{a['last_control_log_time_s']:.6g}s；滤波实际1619次预测、829次更新，终态及完整P/F/Qd/最后prior/H/K/reset/Panchor保存。其余29名额未执行，其中主19、代表/诊断/完整半步10。不是20或30次控制失败。")
 r.table(['最后接受真state与最后估计state','实际值','含义'],[['估计位置误差',f"{a['terminal_estimation_position_error_m']:.10g}m",'同戳真/估计world COM位置差'],['估计姿态误差',f"{a['terminal_estimation_angle_error_rad']:.10g}rad",'SO(3)测地角'],['真实角速度范数',f"{a['terminal_true_angular_speed_rad_s']:.10g}rad/s",'真实plant仍近静止'],['估计角速度范数',f"{a['terminal_estimated_angular_speed_rad_s']:.10g}rad/s",'估计速度显著增大，非实际转速'],['侧1估计rho-x',f"{a['terminal_contact_tau_reconstructed_from_saved_state']['estimated'][0][0]:.10g}m",'超出原±.005m域'],['侧2估计rho-x',f"{a['terminal_contact_tau_reconstructed_from_saved_state']['estimated'][1][0]:.10g}m",'超出原±.005m域'],['真实rho-x（侧1）',f"{a['terminal_contact_tau_reconstructed_from_saved_state']['true'][0][0]:.10g}m",'真实pad仍在原域']],[6,5,5.4],size=8)
 r.p('失败发生在3–13s的零命令保持段，尚未到7s内力或13s位姿反馈开启时刻。记录的UF和UP均为0；0–3s只有原声明的10mm手动lift命令。不能把这条前缀说成已经验证联合反馈，也不能借低内力说明原KF有效。失败时估计超域与真实pad超域是不同事件，最后真实接触仍符合冻结有效域。')
 t=np.array([p['time_s'] for p in plant]);O=np.array([p['state']['O'] for p in plant]);h=np.array([p['h_N_Nm'] for p in plant]);hi=np.array([p['internal_N_Nm'] for p in plant])
 fig,axes=plt.subplots(2,1,figsize=(9.4,5.5),sharex=True)
 for k,label in enumerate('xyz'):axes[0].plot(t,1000*(O[:,k,3]-O[0,k,3]),label=label)
 for side,style in ((0,'-'),(1,'--')):axes[1].plot(t,np.linalg.norm(h[:,side,:3],axis=1),style,label=f'侧{side+1}总真实接触力')
 axes[0].set_ylabel('真实COM相对t0位移 / mm');axes[1].set_ylabel('力 / N');axes[1].set_xlabel('运输相位时间 / s')
 for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8);ax.axvline(3,color='gray',linestyle=':')
 fig.suptitle('实际10mm手动lift及保持；内力/位姿反馈尚未开启');fig.tight_layout();p=ASSETS/'03_actual_motion_contact.png';base.save_figure(fig,p);r.picture(p,'图3 实际物体响应和两侧总接触力；竖线为原3s手动lift结束，不是7/13s反馈事件。')
 fig,axes=plt.subplots(2,1,figsize=(9.4,5.5),sharex=True)
 for side,style in ((0,'-'),(1,'--')):
  axes[0].plot(t,np.linalg.norm(hi[:,side,:3],axis=1),style,label=f'侧{side+1}真实投影内力');axes[1].plot(t,np.linalg.norm(hi[:,side,3:],axis=1),style,label=f'侧{side+1}真实投影内力矩')
 axes[0].set_ylabel('内力 / N');axes[1].set_ylabel('内力矩 / (N·m)');axes[1].set_xlabel('运输相位时间 / s')
 for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('原式20投影真实hK+hB；反馈仍关闭');fig.tight_layout();p=ASSETS/'04_actual_internal_force_moment.png';base.save_figure(fig,p);r.picture(p,'图4 真实两侧内力与内力矩。每侧峰值约0.00202018N/2.89285e−6N·m，来自实际微小端点相对运动；不与原运输阶段1.5N直接作性能对照。')
 r.page('12 真实估计误差、速度及协方差')
 pt=paired['paired_time_s'];pos=paired['estimated_minus_true_position_m'];phi=paired['estimated_minus_true_Log_rho_m_theta_rad'][:,3:]
 fig,axes=plt.subplots(2,1,figsize=(9.4,5.5),sharex=True)
 axes[0].plot(pt,1000*np.linalg.norm(pos,axis=1),label='估计位置误差');axes[1].plot(pt,np.linalg.norm(phi,axis=1),label='估计姿态误差')
 axes[0].set_ylabel('欧氏位置误差 / mm');axes[1].set_ylabel('SO(3)角误差 / rad');axes[1].set_xlabel('运输相位时间 / s')
 for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('同时间真实/估计state；末点来自3.948s终止记录');fig.tight_layout();p=ASSETS/'05_actual_pose_estimation_error.png';base.save_figure(fig,p);r.picture(p,'图5 真实状态与滤波估计的误差。0–3.944s逐控制时刻直接配对；3.948s末点由终止文件的最后接受true state和同戳估计得到，无插值或延长。')
 fig,axes=plt.subplots(2,1,figsize=(9.4,5.5),sharex=True)
 for label,key,style in (('真实','true_V_m_s_rad_s','--'),('估计','estimated_V_m_s_rad_s','-')):
  v=paired[key];axes[0].plot(pt,np.linalg.norm(v[:,:3],axis=1),style,label=label);axes[1].plot(pt,np.linalg.norm(v[:,3:],axis=1),style,label=label)
 axes[0].set_ylabel('线速度范数 / (m/s)');axes[1].set_ylabel('角速度范数 / (rad/s)');axes[1].set_xlabel('运输相位时间 / s')
 for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('估计速度增大与真实plant响应分开');fig.tight_layout();p=ASSETS/'06_actual_velocity_estimation.png';base.save_figure(fig,p);r.picture(p,'图6 保存的真/估计速度。估计角速度末值约260.0205rad/s，真实末值约8.10e−8rad/s，不将估计速度当实际动作。')
 r.table(['实际滤波证据','值','限定'],[['未收敛更新',f"{a['nonconverged_updates']}/{a['update_count']}",'最多连续1次，未触发原连续3次停门'],['最终P数值最小特征值',format(a['terminal_covariance_min_eigenvalue'],'.10g'),'未触发负特征值退出'],['最终P最大非对称',format(a['terminal_covariance_max_asymmetry'],'.10g'),'对称检查仍通过'],['ωx方差',format(a['terminal_angular_velocity_covariance_diagonal_rad2_s2'][0],'.10g')+' (rad/s)²','明显增大；不混不同state单位求范数'],['末次预测间隔',format(a['last_prediction_interval_s'],'.10g')+'s','3ms且无新测量'],['保存F单次未校正谱半径',format(a['last_saved_prediction_F_spectral_radius'],'.10g'),'约5.547；不是完整闭环稳定性定理']],[5.8,5.0,5.6],size=8)
 r.p('实际停门是估计接触域越界，并非真实物体数值失稳、非有限或协方差负值。最后3ms没有新测量，原Euler传播的保存F有大于1的局部倍率；这与已知刚性模型预测风险相符。但没有更换预测或受控消融，不能把所有估计异常唯一归因给Euler。冻结的有偏C、有限形变/原阻尼近似、均质惯量等适配也须与原作者未公开实现区别。')
 r.page('13 控制命令、四组账目与原论文比较')
 ct=np.array([c['time_s'] for c in commands]);u=np.array([c['U_cmd'] for c in commands]);UF=np.array([c['U_F'] for c in commands]);UP=np.array([c['U_P'] for c in commands]);fig,axes=plt.subplots(2,1,figsize=(9.4,5.5),sharex=True)
 for side,style in ((0,'-'),(1,'--')):
  axes[0].plot(ct,np.linalg.norm(u[:,side,:3],axis=1),style,label=f'侧{side+1}命令线速度');axes[1].plot(ct,np.linalg.norm(u[:,side,3:],axis=1),style,label=f'侧{side+1}命令角速度')
 axes[0].plot(ct,np.linalg.norm(UF[:,:, :3].reshape(len(ct),-1),axis=1),':',label='UF线速度（均0）');axes[0].plot(ct,np.linalg.norm(UP[:,:,:3].reshape(len(ct),-1),axis=1),'-.',label='UP线速度（均0）')
 axes[0].set_ylabel('线速度命令 / (m/s)');axes[1].set_ylabel('角速度命令 / (rad/s)');axes[1].set_xlabel('运输相位时间 / s')
 for ax in axes:ax.grid(alpha=.25);ax.legend(fontsize=8)
 fig.suptitle('实际记录的原时序命令；7s/13s反馈事件尚未到达');fig.tight_layout();p=ASSETS/'07_actual_commands.png';base.save_figure(fig,p);r.picture(p,'图7 原始commands日志的真实命令；手动lift与UF/UP分别记录。零反馈是该时间段原定开关所致，不能推断反馈收敛。')
 r.table(['条件/诊断','实际完成/失败/未执行','85–95s位置RMS / m','85–95s角RMS / rad','13–76s内力RMS / N'],[['exp1','0完成/0失败/5未执行','未取得','未取得','未取得'],['exp2','0完成/0失败/5未执行','未取得','未取得','未取得'],['exp3','0完成/1失败/4未执行','未取得','未取得','未取得'],['exp4','0完成/0失败/5未执行','未取得','未取得','未取得'],['其他10名额','高力矩2/时延2/滑动1/GT4/半步1均未执行','不纳入主统计','不纳入主统计','不纳入主统计']],[3.0,5.1,2.77,2.77,2.76],size=7)
 r.p('当前只有一条seed7资格失败前缀，不能进行五种子均值/标准差、改善百分比或全五seed三条优越性判定。原冻结窗口指标为null，不按3.948s前缀另建窗口。完整半步ID30和其他名额都未运行；没有把GT代替正式估计以绕过资格，也没有改变7/13/76s事件、噪声或gain。')
 r.table(['原论文描述','本机对应证据','当前比较结论'],[['exp2约10mm/4.5°','尚无exp2或95s运输','不能判原位姿改进'],['exp1多数运输约1.5N内力','只有早期手动lift下约.00202N真内力','不同时间/激励/组别，不能报告改进百分比'],['平移<.1mm卡尺分辨率/角.42°','当前.1469mm/约.1185rad是估计误差','定义不同，不冒称最终定位误差'],['高力矩约80%末端降低','代表例未执行','尚无复现证据'],['exp4瞬态变差/稳态相近','真实K保持名义；失配条件已编码但未执行','尚无对照结论']],[5.9,5.8,4.7],size=8)
 r.page('14 失败边界、修正预算与复现结论')
 r.p('独立物体动力学已经通过本次资格，42维IESEKF和原控制的数学组件也获得测试证据；首次完整多率闭环在估计状态域失效前得到真实观测/控制/物体日志。P2仍部分完成，尚未运行位姿和内力反馈有效时段，原论文联合控制实验结果未复现。不能由本次适配模型失败断言原作者方法或真实机器人实验无效。')
 r.p('累计小修已用3/3：此前接触资格符号/覆盖修正1；本轮诊断JSON索引归档修正2；闭环入口relative/absolute路径修正3。修正2/3只涉及归档和启动，完整前后源码和失败保存。明确批准的接触几何、plant隐式和五点资格各为独立裁决，不重开三轮预算。后续没有进行第四轮程序修正、调参或额外控制实验。')
 r.p('保留三个停止来源：原显式首跑120s超时、v2固定差分资格FAIL以及suite01零case入口失败。v3来源45a547c，组件来源5bfcafd，clock来源d90f32f，实际闭环来源513c36a。suite02完整原始gzip、metadata、配置、events、失败终态和滤波NPZ按SHA归档。源码/原始数据身份与文档排版检查分开，不将Word通过说成科学闭环通过。')
 r.p('如果要继续取得原论文7–95s的联合控制结果，需要先裁决原式(18)在本刚性模型/多率事件中的数值预测含义，并核对原作者实际惯量、预测/更新细节与代码。改预测器、内部substep、惯量、R/Q或退出界都是本轮冻结条件之外的变化；我没有自行实施。当前预算内以实际失败及差距收尾，不自动进入P3或现有FR3改进。')
 r.h('14.1 来源与参数快照')
 r.table(['证据','文件/身份'],[['协议v1/v2/v3','configs/p2_closed_loop_protocol_v1/v2/v3.json；原物理/条件参数一致'],['本次六条动力学及70case','results/20261014_P2_implicit_qualification_v3_01'],['35组件/2clock','results/20261014_P2_components_qualification01、P2_clock_qualification01'],['真实case及29未执行','results/20261014_P2_closed_loop_suite02/case_11_exp3_7、case_ledger.json'],['只读曲线与末态分析','results/20261014_P2_closed_loop_analysis01'],['源码与旧失败/Word','reproduce-p2-paper-audit全部历史保持']],[5.3,11.1],size=8)
 base.application(r);r.doc.save(OUTPUT)
 identity={'title':TITLE,'builder_SHA':base.sha(Path(__file__)),'inherited_theory_builder_SHA':base.sha(ROOT/'scripts/build_p2_stage2_report.py'),'sources':sources,'docx_SHA':base.sha(OUTPUT),'asset_SHA':{p.name:base.sha(p) for p in sorted(ASSETS.glob('*.png'))},'closed_loop_cases_used':1,'closed_loop_complete_cases':0,'implicit_dynamics_trajectories_used':6,'corrections_used':3,'remaining_corrections':0,'no_experiment_execution_by_report':True}
 (ASSETS/'report_data.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'output':str(OUTPUT),'figures':len(identity['asset_SHA']),'status':'P2_PARTIAL_FULL_LOOP_FAIL_STOP'},ensure_ascii=False))
if __name__=='__main__':main()
