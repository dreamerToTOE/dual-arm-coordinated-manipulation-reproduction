#!/usr/bin/env python3
"""Versioned D083 Chinese research report; requires completed source-bound data.

Use the bundled artifact Python. D082 formatting/OMML helpers are reused without
executing its main routine or altering any predecessor deliverable.
"""
from pathlib import Path
import argparse
import importlib.util
import json
from docx import Document
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('d082_docx_helpers', ROOT/'scripts/p4_d082/build_chinese_research_report.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
p,h,eq,page,table = d.p,d.h,d.eq,d.page,d.table
sub,sup,frac,large = d.sub,d.sup,d.frac,d.large


def load(rel):
    return json.loads((ROOT/rel).read_text())


def figure(path, caption, width=16.2):
    path = Path(path)
    d.ASSETS = ROOT/path.parent
    d.figure(path.name, caption, width)


def code(text):
    para=p(text)
    para.paragraph_format.space_after=Pt(3)
    for run in para.runs:
        run.font.name='DejaVu Sans Mono'
        run.font.size=Pt(8)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'reports/P4_D083闭链规划受控实验与双ABB空间仿真研究报告_20261022.docx')
    parser.add_argument('--spatial-manifest',type=Path,default=ROOT/'results/20261022_D083_spatial_visualization01/manifest.json')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    b=load('results/20261022_D083_fig3_controlled02/summary.json')
    c=load('results/20261022_D083_difficult02/summary.json')
    if b['status']!='COMPLETE' or c['status']!='COMPLETED_FROZEN_BATCH_WITH_ONE_ARTIFACT_UNKNOWN':
        raise RuntimeError('report requires actual complete bounded data; do not assume success')
    spatial=json.loads(args.spatial_manifest.read_text())
    # The figure names are supplied by the source-bound spatial renderer.
    figs=spatial['report_figures']
    old='reports/p4_d082_research_assets_20261022/'
    bf='results/20261022_D083_fig3_controlled02/plots_v2/'
    d.DOC=Document();d.setup()
    d.DOC.core_properties.title='P4闭链规划受控实验与双ABB空间仿真研究报告'
    d.DOC.add_paragraph('P4闭链规划受控实验与双ABB空间仿真研究报告','Title')
    p('RSS PCS NR 与递归局部连接的数值复现\nD083 版本  2026年10月22日')
    h('研究结果概述')
    p('我研究全驱动转动关节闭链的采样规划，分别用20R平面机构与双ABB IRB120展示算法、约束和真实关节路径。闭链约束、关节界和碰撞必须同时满足；人工被动链分支的可连接性与完整机构的实际运动能力需要分开解释。')
    rates='、'.join(f"m={r['m']}时{r['existential_success_count']}/180" for r in b['by_m'])
    p('本次受控可见性实验对全部分划数量使用同一组96个合法构型、180个非自配对。逐图册候选并集的成功数为'+rates+'。这些是固定有限总体上的描述结果，反映本次离散连接规则；不把相关轨迹端点视为均匀流形样本，也不以局部检查成本替代原图的Bi RRT规划时间。')
    cs={r['registered_method']:r for r in c['method_summary']}
    p('三组预定归档端点条件各用三个配对种子比较四种策略，共'+str(c['executed_calls'])+'次新规划。独立合格结果为PCS '+str(cs['PCS']['independent_success'])+'/8（另1次保存失败、资格未知）、兼容固定分划 '+str(cs['COMPATIBLE_FIXED']['independent_success'])+'/9、NR '+str(cs['NR']['independent_success'])+'/9、RSS '+str(cs['RSS']['independent_success'])+'/9。困难程度及是否存在性能优势须结合后文的路线阻挡与失败记录判断。三组条件均未建立候选路线的障碍阻挡，困难性未成立，不能估计一般窄通道问题的成功率。')
    p('空间部分直接复用已保存的合格轨迹，未重新规划。环境II比较PCS与NR的实际路径；环境III的649个离散状态形成14条最终解边，主动臂角色确实切换4次。全部空间证据保留aligned碰撞位姿与原生TCP不一致、原碰撞对及杆件模型限制；没有连续CCD、动力学或实际机器人执行结论。')
    h('原论文身份',2)
    p('Sintov A, Borum A, Bretl T. Motion Planning of Fully Actuated Closed Kinematic Chains With Revolute Joints A Comparative Analysis. IEEE Robotics and Automation Letters, 2018, 3(4):2886–2893. DOI 10.1109/LRA.2018.2846806。已阅读全文8页作者稿；原文SHA256为193710e5a9d4284cf62b30ff189a1df038a9d5c5ce3f1545525dc2f78bea08c6。原论文全范围仍为PARTIAL。')

    page('1 闭链约束与牛顿投影')
    p('原文式1至2定义闭链集合与合法空间。令q为n维关节角，C(q)为平面3维或空间6维约束残差。规划目标是寻找由合法起点到合法终点的连续几何路径；本次实际取得的数值证书是有限离散状态与局部叶，不等于连续路径已严格认证。')
    eq([sub('C','cl'),'={q∈',sup('R','n'),': C(q)=0},  ',sub('C','o'),'=',sub('C','cl'),'∩',sub('C','free')],1)
    eq(['α:[0,1]→',sub('C','o'),',  α(0)=',sub('q','s'),',  α(1)=',sub('q','g')],2)
    p('20R独立重建机构由19根等长移动杆和一个零长度末端转动法兰构成，地杆连接相距1 m的基座。令θ_i为前i个相对关节角之和，ℓ=sin(π/38) m，则末端位置与角度为')
    eq([sub('θ','i'),'=',large('∑','j=1','i',sub('q','j')),';  x=',large('∑','i=1','19',[sub('ℓ','i'),'cos ',sub('θ','i')]),';  y=',large('∑','i=1','19',[sub('ℓ','i'),'sin ',sub('θ','i')])],3)
    eq(['C(q)=',sup(['[x−1, y, wrap(',large('∑','i=1','20',sub('q','i')),')]'],'T')],4)
    p('对第j个关节的偏导累加该关节后方连杆的切向位移；角度残差导数为1。第20个零长度关节仍参与姿态闭合。空间ABB使用各侧完整刚体变换形成闭链，毫米位置与旋转矩阵残差分别记录，不与平面米制门限混用。')
    eq([sub('J','xj'),'=−',large('∑','i=j','19',[sub('ℓ','i'),'sin ',sub('θ','i')]),';  ',sub('J','yj'),'=',large('∑','i=j','19',[sub('ℓ','i'),'cos ',sub('θ','i')]),';  ',sub('J','θj'),'=1'],5)
    h('SVD伪逆更新',2)
    p('在当前构型线性化C(q+Δq)≈C(q)+JΔq，求最小范数校正Δq=−J†C。写J=UΣVᵀ，以max(10⁻¹²,10⁻¹⁰σ_max)为截断，低于门限的奇异值不取倒数。')
    eq([sub('q','k+1'),'=wrap(',sub('q','k'),'−V',sup('Σ','†'),sup('U','T'),'C(',sub('q','k'),'))'],6)
    p('平面生产实现为全更新、无阻尼、无线搜索、无随机重启的NR，最多100次更新，分别用10⁻⁸ m和10⁻⁸ rad验收。旧投影数据的平均trace长度8.447包含初始及终止评估，实际Newton更新均值是7.447，二者没有混写。原文使用KDL，不能把本次Python绝对耗时当作原软件的性能复现。')

    page('2 解析被动链与分划可见性')
    p('APC保持主动变量，用非冗余被动链的闭式逆解闭合其余角。被动是求解角色，机构全部关节仍有驱动。分解整链T_prefix T_p T_suffix=T_target后，可把目标变换到该连续3R链的局部坐标。')
    eq([sub('T','p'),'=',sup(sub('T','prefix'),'−1'),sub('T','target'),sup(sub('T','suffix'),'−1')],7)
    p('从被动目标(x_p,y_p,φ)减去第三杆位移得到腕点(u,v)。余弦定理给出肘角，两符号对应两条IK分支；随后解第一角与末角。')
    eq(['u=',sub('x','p'),'−',sub('ℓ','3'),'cosφ;  v=',sub('y','p'),'−',sub('ℓ','3'),'sinφ'])
    eq([sub('c','2'),'=',frac([sup('u','2'),'+',sup('v','2'),'−',sup(sub('ℓ','1'),'2'),'−',sup(sub('ℓ','2'),'2')],['2',sub('ℓ','1'),sub('ℓ','2')]),';  ',sub('q','2'),'=±acos(',sub('c','2'),')'],8)
    eq([sub('q','1'),'=atan2(v,u)−atan2(',sub('ℓ','2'),'sin',sub('q','2'),',',sub('ℓ','1'),'+',sub('ℓ','2'),'cos',sub('q','2'),')'],9)
    eq([sub('q','3'),'=φ−',sub('q','1'),'−',sub('q','2')])
    p('主动构型并不总能闭合。|c₂|>1时拒绝，只容许既有10⁻¹²浮点边界舍入，随后重新验闭链和关节界。模型提供p0至p16共17个连续非零3R分划，不能复制分划补造m20。主规划仍使用p0和p16；Fig.3补充另暴露其余合法分划。')
    h('PCS的连接机制与上界',2)
    p('同一构型在不同分划中具有不同人工奇异集。若两端在某分划具有共同的非奇异肘支，可在该分划内递归投影。另一分划能绕开原分划的人为分支障碍，树的不同边可选择不同被动链。最终解的相邻边分划变化才算解上的切换。')
    eq([sub('V','m'),'(q)=',large('⋃','i=1','m',[sub('V','i'),'(q)'])],10)
    eq([sub('P','v'),'=1−',large('∏','k=1','m',['(1−',frac('1',sub('ξ','k')),')']),';  μ(',sub('V','m'),')≤',sub('P','v'),'μ(',sub('C','cl'),')'],11)
    p('式11对应原文式6至9中独立、等测度分支的假设上界；真实障碍、限位、可达性及被动链依赖会降低连接率。式10则说明同一总体与同一确定候选规则下，嵌套集合的已知成功并集不能减少。有限总预算策略可能因顺序和额外开销产生不同结果，需分别实测。')

    page('3 RSS与递归二分局部连接')
    p('固定被动链的人工奇异性由J_p=∂C/∂q_p秩下降定义。对连续3R平面链，det J_p与ℓ₁ℓ₂ sin q₂成比例，q₂=0或π是两条肘支可能相接的位置；这不等于整个闭链约束雅可比也奇异。')
    eq(['rank(',sub('J','p'),')<3;  γ=0.2'],12)
    p('RSS以概率γ请求奇异目标，仍须满足完整闭合、机械界、碰撞可行和局部连接。既有72次奇异请求包含2304次构造，全部IK_UNREACHABLE；人工rank2正例及其两侧桥只支持局部机制，不能计入随机全局规划的成功分子。本次没有改奇异采样器、γ或原失败。')
    p('RBS先检查端点，再把环境关节空间中点投影回流形。中点须同时通过闭链、限位和几何碰撞；任一拒绝均保留原因。以投影点分成左右子段，递归至叶长≤0.05 rad，深度或中点预算耗尽则停止。')
    eq([sub('q','m'),'=Π(',frac([sub('q','a'),'+',sub('q','b')],'2'),'),  ',sub('q','m'),'∈',sub('C','o')],13)
    p('规划调用沿用每连接256个总投影与深度12；受控局部实验沿用旧Fig.3局部配置512个总投影与深度16。这两类预算没有混成同一性能指标。已成功局部路径的全部保存点由独立几何程序复核，但有限叶和增密点都不能证明任意时间的连续无碰撞。')
    figure(old+'07_algorithm_flow.png','图1 复现算法流程  投影  状态检查  RBS与双树搜索',15.4)

    page('4 平面机构与既有完整路径')
    figure(old+'01_complete_trajectory.png','图2 既有E1 PCS seed7的真实完整轨迹  背景为保存构型',14.0)
    p('20R移动杆与地杆为半径0.002 m胶囊体，仅排除共享转动关节的相邻杆对。障碍使用真实线段至圆心距离判定。E0圆心(0.45,0.72) m、半径0.045 m；E1另含(0.50,0.18,0.065)与(0.72,0.60,0.050) m两圆。所有新平面实验保留该几何与[-π,π]关节界。')
    p('D082的50次既有规划使用5方法×2环境×5种子，每次1秒、120外循环、300节点。26条成功记录对应13条不同关节轨迹在两个环境重复取得资格，24条TIME_LIMIT。独立程序以累积变换与解析线段距离复算8490个离散状态，最大位置9.040×10⁻⁹ m、角度2.220×10⁻¹⁵ rad，最小净距0.053965 m。')
    table(['方法','每环境成功','重要解释'],[['PCS full','3/5','成功解分划均为p0'],['fixed p0','5/5','端点分支兼容的公平基线'],['fixed p16','0/5','原端点分支不兼容的结构负对照'],['NR','5/5','本任务路径与耗时更好'],['RSS','0/5','随机奇异构造失败保留']],[3,2.7,11.1])
    p('13对跨环境成功q路径逐值相同，旧E1未迫使这些解改变路线；旧数据不能证明复杂障碍优势。本次新增受控局部实验和三个冻结端点诊断，既有50次不重复执行、不与新诊断合并成一个总体。')

    page('5 双ABB环境II的真实空间几何')
    figure(figs['ii_scene'],'图3 环境II的实际基座 连杆 杆件与障碍  关节构型来自保存路径',16.4)
    p('环境II由两台ABB IRB120共同持杆。三维图使用原模型的基座变换、刚性杆与障碍坐标，并把保存关节角输入原几何一致FK。绘图所做的FK只确定显示位置，不产生新的规划或碰撞资格；来源q、源配置与独立证书SHA在图表manifest逐项绑定。')
    p('已保存的RRT PCS路径有177点、176叶，NR有393点、392叶；CBiRRT PCS为413点，NR为689点。RRT PCS的3条最终解边还记录2次角色转换；此处与环境III的4次分别计数。本次图例标注路径点与方法，无同条件重复统计，因此轨迹可行性比较不推出PCS或NR的成功率与速度优势。')
    p('图中机器人实体来自原始CAD网格的运动学变换；TCP轨迹和离散点由保存数据直接给出。杆件显示不能替代碰撞模型的完整实体表面。基座、物体与机器人姿态没有为了画面效果改变科研几何。')

    page('6 环境II的轨迹与数值资格')
    figure(figs['ii_paths'],'图4 环境II PCS与NR的已保存轨迹  路径参数为离散点序号',16.4)
    table(['环境II方法','点数','最大位置残差 mm','最大旋转矩阵差','最大叶距 rad'],[
      ['RRT PCS',177,'3.411e−13','4.441e−16','0.049491'],['RRT NR',393,'9.794e−6','3.070e−8','0.047800'],
      ['CBiRRT PCS',413,'4.547e−13','6.731e−16','0.049873'],['CBiRRT NR',689,'9.800e−6','4.672e−8','0.049519']],[3.3,1.4,4.0,4.2,3.9])
    p('表中指标来自原独立证书与其绑定记录，不是图像反推测量。PCS解析闭合与NR容差终止导致残差水平不同，较小残差不自动表示整体方法更优。空间路径采用重建端点及aligned源碰撞策略，原native位姿差异保留。')
    p('离散碰撞判定只覆盖原模型的已检查碰撞对及8 mm政策，不能升级为全部实体、遗漏碰撞对或连续扫掠安全。未经时间参数化的路径也不具备真实速度、加速度、力矩与抓持载荷资格。动画仅按保存构型播放，播放帧率没有物理时间含义。')

    page('7 环境III窄通道与完整路径')
    figure(figs['iii_scene'],'图5 环境III的真实保存路径  障碍几何与649点离散轨迹',16.4)
    p('原环境III要求双ABB持杆通过狭窄通道。既有RRT PCS唯一source结果为exact=true、approximate=false，保存求解墙钟6.177099651 s；15里程点、14条最终接受边、649点、648叶。原source主callback为恒真，因此exact标记本身不是安全证书，649点物理资格在另一份独立证据中给出。')
    p('最大闭链位置分量4.547×10⁻¹³ mm、最大旋转矩阵差4.469×10⁻¹⁵、最大相邻全12角距离0.04995649 rad。仅RECONSTRUCTED ALIGNED DISCRETE SOURCE COLLISION POLICY ONLY成立。全部649点保留native TCP mismatch，最大位置0.00357054 mm、旋转矩阵7.34767×10⁻⁶；未将原记录的independent_path_qualified=false回写为全原生通过。')
    p('这条空间结果证明已保存模型中存在完整离散路径和实际角色切换机制，未比较同任务固定被动臂与NR，不能单独支持窄通道性能优势或严格连续可行性。')

    page('8 环境III的四次主动被动角色转换')
    figure(figs['iii_switches'],'图6 最终路径四次角色切换的相邻边与姿态  0和1是主动臂角色索引',16.4)
    p('14条最终解边的主动角色序列为[0,0,0,1,0,0,0,1,1,0,0,0,0,0]。零起始边索引的转换为2→3、3→4、6→7、8→9；使用一基编号即第3至4、第4至5、第7至8、第9至10条边。每次切换前后帧引用相邻真实边的公共里程点及邻近离散姿态，不能把动画插值伪装为新解。')
    p('主动和被动只描述某条边的IK计算角色，两个机械臂仍都运动且都驱动。换角色不是放开抓持，也不是物理控制器主从切换。本图与时间线从最终回溯边提取，未以搜索尝试的时间相邻变化替代解中切换。')
    p('20R既有成功PCS解最终切换为0，III最终角色切换为4，两者属于不同环境、不同划分的独立机制证据。切换发生并不证明该切换为所有可行解所必需，也没有建立性能因果效应。')

    page('环境III角色时间线与资格边界')
    figure(figs['iii_timeline'],'图7 环境III保存路径的角色与离散资格  横轴为路径序号而非物理时间',16.5)
    p('图中角色台阶由最终接受边逐段生成；四条竖线对应零基路径序号179、248、392和492。aligned通过与native不通过分别显示，二者没有合并。')

    page('9 同一合法点对的受控可见性实验')
    p('旧Fig.3代理数据对每个m重新生成构型池，距离和自配对比例同时变化，不能识别增加分划的作用。我从既有13条独立合格E0轨迹中逐字节去重，以预定PCG64种子抽96点，再在4560个无序非自对中无放回抽180对，朝向按端点索引固定。所有m共用q、配对、0.3 rad距离bin、几何与验收门。')
    p('端点由独立NumPy几何及生产GEOS共同复核；选点失败不替换。随后冻结池、点对、来源SHA，才进行连接。嵌套集合为p0至p(m−1)，m=1、2、3、7、16；最大集合为p0至p15，另一个数学合法p16没有补入m16以改变旧prefix定义。')
    eq([sub('A','m'),'(a,b)=',large('⋁','p=0','m−1',['success(RBS(',sub('q','a'),',',sub('q','b'),';p))'])],14)
    p('每对的16个单分划候选独立执行既有512中点规则并缓存；所有m从完全相同候选取并集。再为每个m实际运行一次共享512投影总预算的PCS升序策略，分别记录尝试分划、分支、失败、时间及调用数。出现耗尽或未执行时存在性只报告下上界，不把UNKNOWN当作无连接。')
    figure(bf+'fig3_controlled_visibility_by_distance.png','图8 相同180点对随距离的局部可见率  空bin不连线  每bin分母见图与CSV',15.4)

    page('10 受控分划数量与局部成本')
    figure(bf+'fig3_controlled_visibility_and_local_cost_by_m.png','图9 同一有限总体的可见率与局部检查代价  不是Bi RRT规划耗时',16.5)
    table(['m','候选并集成功','存在性未知','有限策略成功','平均局部 ms'],[
      [r['m'],str(r['existential_success_count'])+'/180',r['existential_unknown_count'],str(r['bounded_success_count'])+'/'+str(r['bounded_executed_count']),f"{r['mean_bounded_wall_sec']*1000:.3f}"] for r in b['by_m']],[1.2,4.1,2.9,4.1,4.5])
    p('实际单分划候选'+str(b['candidate_calls'])+'次、有限策略'+str(b['bounded_calls'])+'次；候选成功'+str(b['candidate_success_count'])+'次。已知成功并集单调性违规为'+str(len(b['existential_monotonicity_violations']))+'。这是对同一嵌套候选规则的可复查比较，不是原理论无预算连通性的证明。')
    p('本总体条件于既有成功路径，点对共享端点，且成功路径点分布不均匀。因此图中为固定180对的精确描述率，没有把独立Bernoulli区间误作全流形置信区间。样本不确定性及跨任务外推不能由这180对消除；时间受机器负载与Python实现影响，不能据此复现论文平面投影快40倍或m20规划时间。')
    p('存在性随着可用分划增加与有限搜索是否变快是两个问题。即使成功率增大，穷尽更多图册可能增加成本；有限策略的早停可节省工作。全部候选、pair×m结果、真实失败及分箱分母保存在独立CSV/JSON与gzip记录中。')

    page('11 一次有预算界的困难条件诊断')
    p('我在不改变障碍、半径、机械界或算法的前提下，从旧E1 PCS seed7、23、41密集路径按floor((N−1)/2)固定抽取三个中间状态，组成C1=(7,23)、C2=(23,41)、C3=(41,7)。每个可行见证为第一来源前缀倒序至公共START，再接第二来源前缀；端点、公共根和全部离散见证逐值及几何核验。')
    p('这些条件来自PCS成功轨迹，明确属于归档端点诊断，不是无偏困难场景总体。固定基线从真实p0、p16的两端肘支判断兼容性，取第一个兼容分划；不兼容则NOT COMPARABLE，不计为方法失败。先对兼容分划与NR独立构造深度8的投影路线，闭合且限位合法的碰撞状态才算特定路线被挡；环境直线未闭合不能当作障碍。')
    for row in c['conditions']:
        p(row['id']+'：端点及可行见证'+('通过' if row['valid_condition'] else '未通过')+'，固定p'+str(row['fixed_partition'])+'，路线困难状态 '+row['hard_scenario_status']+'。')
    figure('results/20261022_D083_difficult02/difficult_diagnostic.png','图10 冻结归档端点条件的配对结果与独立候选路线净距  x表示投影失败',15.8)
    p('只有特定候选碰撞也不足以证明拓扑窄通道。没有建立真正困难性时，本批只能提供负或未定证据，不追加挪障碍、换端点或择种子运行。该停止规则在新结果出现前已冻结。')

    page('12 配对规划结果与方法边界')
    table(['方法','调用/可评估','源成功','独立成功','平均观察耗时 s','最终解切换'],[
      [r['registered_method'],str(r['executed'])+'/'+str(r['evaluable_complete_artifacts']),r['source_success'],r['independent_success'],f"{r['mean_wall_sec']:.4f}",r['solution_switches']] for r in c['method_summary']],[3.9,1.8,1.8,1.8,4.2,3.3])
    p('首个C1 PCS seed7调用完成后，gzip JSON写入遇到NumPy布尔标量类型错误。截断前缀虽记录SUCCESS及0.142819 s，但不含完整可验证路径，故资格为UNKNOWN，不计算法失败、不补跑。原失败目录和源程序保持不变；仅修复保存器后继续剩余35次，原180 s墙钟和240 s CPU阶段上限共同累计。PCS分母为8个完整结果，另1个未知；其余方法各9个结果，PCS配对比较至多8组。')
    p('每条件三个种子7、23、41，四法具有共同1 s墙钟、120外循环、300节点及相同RBS/NR参数。相同PCG64初始种子并不保证算法消耗相同数量的随机向量。超时按实际TIME LIMIT保留，不证明问题无解；平均耗时包含失败，不能转换成无条件求解速度比。')
    p('所有SUCCESS须通过独立端点、双树祖先、接受边与局部叶拓扑核验，保存点及每叶两层新增中点再验闭链、限位、碰撞与分支。原生产FK/GEOS不进入独立几何计算。树父子边分划变化与最终解变化分别保存，不能混计。')
    p('RSS在新端点条件中3/9成功、6/9超时，与旧任务0/10分别报告；这些成功不代表随机奇异桥生成已修复。RSS沿用原随机采样器，没有人工奇异夹具替代。当前证据不能建立PCS在一般困难问题上优于兼容固定分划与NR；正负结果均只适用于这三组预定端点、当前重建几何与有限预算。没有再开展第二轮困难搜索。')
    p('29个完整成功结果的独立验证覆盖3111个保存点及12357个两层增密点，最大增密位置残差9.933×10⁻⁹ m、角度2.665×10⁻¹⁵ rad，最小关节余量0.068994 rad、最小净距0.001720 m；全部最终解切换为0。有限增密仍不等于连续CCD。')
    p('本批规划计算墙钟累计'+f"{c['planner_compute_wall_sec']:.4f}"+' s；含独立诊断、资格、序列化与绘图的总阶段耗时见原始summary和外层GNUtime。历史50调用、旧投影统计和本批36调用分开保留，没有合并成原论文500次每格。')
    h('RSS失败归因',2)
    p('历史2304次奇异构造全因IK不可达拒绝；本批新增53次请求、1696次奇异构造也全部IK_UNREACHABLE。C3的3次RSS成功只沿p16同一肘支的普通连接，没有成功奇异桥。固定夹具却能给出rank2与合法两侧桥。这些证据支持随机构造的闭合可达性是当前障碍，仍不能区分采样支持、重建几何与具体实现中的全部因素，根因维持UNKNOWN。缺失原20R精确输入属于PAPER RESOURCE差异，没有归因为论文错误，也没有重置旧修正3/3。')

    page('13 原文数字与本次证据的对应关系')
    table(['原文项目','原论文结果或规模','本次实际证据与差异'],[
      ['投影试验','空间500000样本；APC7.92% NR100%；APC快3至6倍','旧20R每法768输入；APC51/768 NR768/768；分布与软件不同'],
      ['Fig3上图','20R m1/2/3/7/20；bin0.3 rad','新同一180对、m1/2/3/7/16；相关成功轨迹总体'],
      ['Fig3下图','Bi RRT规划时间随m','只交局部检查代价；m20与各m规划时间未做'],
      ['Fig4与TableII','II可见率RSS0.85% PCS1.31% NR23.74%','旧240共享平面点对；与空间总体不同'],
      ['TableII局部耗时','RSS4.97 PCS0.32 NR1.40 ms','新局部成本定义及机构不同；不算同机加速比'],
      ['TableI环境II RRT','RSS90.86 PCS0.33 NR0.60 s','重用单路径证书；无500重复同条件统计'],
      ['TableI环境III RRT','RSS75.94 PCS2.91 NR1.53 s','既有PCS单次6.1771 s；不能直接比较机器/端点'],
      ['全空间统计','II至VI 22500次','当前未执行正式统计；18000历史计划已取消'],
      ['空间换链与安全','原作者模型和碰撞设置','III四次真实角色切换；native差异与离散证据限制保留']],[3.5,5.2,8.1])
    p('原文Fig.4图注写环境I，正文及Table II讨论环境II，这一原文口径差异保留；本次不利用它将平面代理冒称空间统计。原文表I本身也不支持任一方法在所有场景和规划器上绝对占优，结论应对照具体任务、可见性与投影成本。')
    p('完整覆盖表继承211个原文义务行与257个D082历史列，再追加D083状态、实际证据和限制。环境IV/V/VI没有新增实验，旧失败和VI974/974只读保留；完整原论文仍为PARTIAL。')

    page('14 数据来源与复现入口')
    p('所有脚本拒绝覆盖已发布科学目录。Fig.3分prepare与execute两阶段，先冻结池再运行连接；重放必须同时指定同一个新的输出目录。困难诊断只有一次执行授权，以下入口供审查源程序，不能覆盖本批结果或自动扩展预算。空间渲染只读取既有路径，不重新求解。')
    code('python3 scripts/p4_d083/controlled_fig3.py prepare --output results/user_fig3_replay01')
    code('python3 scripts/p4_d083/controlled_fig3.py execute --output results/user_fig3_replay01')
    code('python3 scripts/p4_d083/render_fig3_saved.py --help')
    code('python3 scripts/p4_d083/bounded_difficulty_resume.py --help')
    p('困难脚本固定本次唯一目录并拒绝覆盖；另一次科学批次须先制定新协议及新目录，不能为重跑而删除原数据。科学环境沿用系统Python3.10、NumPy1.24.4和Shapely2.1.2；报告使用捆绑文档Python，与科学依赖分开。')
    p('主要原始数据为results/20261022_D083_fig3_controlled02、results/20261022_D083_difficult01与02、results/20261022_D083_spatial_visualization01。失败的Fig.3准备01在任何数值查询前由私有符号链接路径键触发，失败字节与修复提交均保留；没有覆盖该目录。')
    p('README提供空间完整渲染参数、输入私有网格SHA、报告构建与捆绑LibreOffice渲染命令。私有论文和作者网格不公开转载；原始q和证据来源、渲染图、脚本、CSV与来源manifest随版本交付，便于区分本次新增与复用结果。')
    h('证据的适用范围',2)
    p('有限构型资格并非连续CCD；平面与空间度量和单位分开；aligned不等于native；几何路径不等于动力学或实际执行。可见性增加不能自动推出规划速度优势，单条换链路径不能自动推出换链不可替代性。原样本规模、其他空间方法对照、m20、原始完整杆件碰撞及硬件执行仍缺失。')

    page('15 面向双FR3的可迁移机制与先决条件')
    p('本节只讨论未来研究，没有FR3、Isaac、ROS或硬件实现。对刚性共同抓持，令G_L、G_R为TCP到物体的固定标定变换，由两侧运动学得到同一物体位姿。')
    eq([sup(sub('T','WO'),'L'),'(',sub('q','L'),')=',sub('T','WL'),'(',sub('q','L'),')',sub('G','L'),';  ',sup(sub('T','WO'),'R'),'(',sub('q','R'),')=',sub('T','WR'),'(',sub('q','R'),')',sub('G','R')],15)
    eq([sub('C','FR3'),'(q)=Log(',sup(['(',sup(sub('T','WO'),'L'),')'],'−1'),sup(sub('T','WO'),'R'),')=0'],16)
    p('NR可把14维关节向量、独立FK/Jacobian与抓持变换映射为6维闭链残差和校正。它不要求7R单臂闭式IK，是优先考虑的通用机制；前提是坐标扰动、米/弧度、机械界与标定一致，并独立验证Jacobian、投影漂移与奇异邻域。未来阻尼或限步版本属于PROPOSED，当前没有性能证明。')
    p('RBS可将两端闭链构型、投影器和统一碰撞接口变成带拒绝原因的离散局部路径。未来MoveIt/FCL接口须包含实际机器人、吸盘、物体与障碍；执行前还要时间参数化、速度加速度界、连续或保守扫掠验证，以及实时闭链误差监测。当前ABB离散证书不能迁移为FR3碰撞证书。')
    p('PCS要求被动子链具有可求且可连续跟踪的有限IK分支。FR3单臂7R冗余，不能直接照搬ABB6R或本次连续3R；若固定冗余参数形成6关节问题，需证明覆盖、分支连续与奇异集合。只改数值初值不是原论文PCS。III四次切换是机制见证，对FR3的性能收益仍未证实。')
    p('RSS还需推导对应被动子链的真实秩亏集合，构造闭合、合法、碰撞可行的随机奇异样本。当前采样失败说明代数奇异条件不够，尚不建议将RSS直接作为双FR3共同搬运主规划器。')
    h('接触与单臂推进的边界',2)
    p('侧吸盘可能柔性变形、滑移与吸附失效。刚性C(q)=0不能保证力闭合、吸力容量或内部应力安全；需要可信关节/物体观测、吸附状态及力或接触信息，传感读数与仿真真值分离。不能简单扩大几何容差掩盖柔性误差。')
    p('单臂后侧推进时，共同物体的双臂闭链已不存在。可借鉴NR/RBS表达实际末端姿态或导向约束，但单边接触、摩擦、卡滞与力位控制属于另外的数学模型。未来应先冻结独立可行路径与完整几何，再比较NR、兼容固定分划和真实PCS，最后由控制研究检验跟踪、内部力与失效恢复。')
    h('参考文献与代码',2)
    p('[1] Sintov A, Borum A, Bretl T. IEEE RA L, 2018, 3(4):2886–2893. DOI 10.1109/LRA.2018.2846806。')
    p('[2] 作者CKCplanning快照909bd72fff778aca8682c96f9eb86ae4eb75557b，https://github.com/avishais/CKCplanning；源码许可与本地差异见既有来源清单。')
    p('[3] 复现仓库 https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction ，分支p4-full-reproduction-pcs-study；D083原始数据、SHA与命令见版本化README。')
    for border in list(d.DOC.element.iter(d.qn('w:pBdr'))):border.getparent().remove(border)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    d.DOC.save(args.output)
    print(args.output)


if __name__=='__main__':main()
