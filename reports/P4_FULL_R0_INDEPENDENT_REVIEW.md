# 00ef300 完整矩阵与 R1 协议的独立只读复核

2026-10-14。被审查版本00ef3000e372ea360faaf6e053ab93c7eef4ab95，读取完整169行CSV与R1 v1配置、预算报告、作者原source和公开raw基数。本复核未改矩阵/旧配置/旧数据，不编译，不运行新科学case。另行编写的原创planar驱动尚未执行。

## 已覆盖且未缩减

30父义务（原29＋T30）均保留；TableI的45cell全部500、1000s预算；Fig3上图五m/NR、下图m1…20/NR均独立展开；TableII十指标、Fig5两投影、六环境原端点、去障/分布与各fixed消融均有入口。未以旧E0/E1或作者data代填新结果。v1许可、source/final版本链与大额预算均显示待裁决，无R2正式授权，科学run=0。

## 具体问题及修订建议

| ID | 被审位置 | 发现 | 审查要求 |
|---|---|---|---|
| M01 | CSV T02-I..VI、T03-I..VI、T16-I..VI | original_repeats分别100/10/2，实际为我们R1 FK/near-NR/endpoint资格数，论文未给该资格计数 | 原栏UNKNOWN或not-applicable；将100/10/2移到明确的ours_planned_count列，不能使原作者被归属我们的测试设计。Root已同意归档v1并新增修订，尚未声称完成。 |
| M02 | CSV T20-visibility | original_repeats=500，duration却写独立50k | Pv来源与TableI的planning500分离：visibility目标50k；其他九指标只在相同cell/version/config才reuse500，TableII未独立给repeat数须注明推定复用方案。 |
| P01 | R1 v1 translation_gate_mm、singular_value_units | 空间source用mm，而planar L1是未给物理尺度的source-length unit；统一/1000会伪造planar米单位 | 保留v1，对planar补pre-execution单位说明：source_link_length_unit、数值门1e−7/1e−5不改、planarJac不/1000；空间仍mm→m。Root已同意单独addendum，尚未执行。 |
| P02 | 原planar输入映射 | 末q是相对基座的反向terminal encoder，q19∈[0,2PI_]，KDL末joint=PI_−q19；不能按20个q直接累计orientation | 独立FK为19个单位杆+末零长逆向joint；source_chart输入不改到[-π,π]。作者PI_=3.1416和APC fmod2PI_造成的物理matrix差独立保存，不能清零或用同源wrap盖掉。 |
| P03 | R1 v1 spatial ik_branch_indices=0..7 | 这并非planar的二分支索引；planar全部20partition枚举也未显式出现在v1字段 | 新addendum明确40固定原start的20×2 APC数学diagnostic，100FK/10NR、seed映射、扰动joint模式和整体1800/单120预算；不修改正式calls=0。Root已同意。 |
| C01 | T05父项、T07父项、T27父项 | 原子目录未逐env展开RBS正负/奇异桥；T07除了Fig1四杆示例缺独立六环境RSS生成/三模式/branch桥入口 | 现有父项保留，新增稳定子ID用于各env实际Jac秩、合法目标、跨branch RBS/最终path证据；不能因ABB资格成功就标Comau/VI已RSS资格。可属后续R1/R2，但R0必须登记。 |
| C02 | T06-EQ3..9 | CSV展开了式号，但继承相同概率摘要；Eq3实际是valid_edge的可见集合，不是式4–9的概率界 | 补每式具体变量/量纲/等测度/独立/依赖/碰撞分母/VI非适用；尤其Eq7条件语义与pair-union语义分开。保留式号，不默改公式。 |
| C03 | T24父项/T17父项 | 分法profiling、RSSγ=.2、three planner仅综合入口，尚无冻结grid/training seeds/独立formal seeds；I的RRT/SBL另有author代码但不在TableI空间45cell | 拆科学计划训练与正式日志；I的additional planner验证如果要求执行须单列original-known/未报道N，不自动500。完整scope不能等只有BiRRT结果才填FULL。 |
| C04 | T19-PLANAR_PROJECTION / T07解释 | 40倍投影成本已有独立义务；RSS大树NN成本机制仍仅discussion | 建议T07-NN独立解释性子ID：记录真实NN耗时随tree size；原文无NN曲线则标PAPER-CLAIM-NOT-DIRECTLY-TESTED，不凭低成功率单独推出该根因。 |
| C05 | Source final-data lineage | public source/raw次数和原文counts不一，plotting脚本含人工点改动；矩阵现泛称lineage pending | 将原data→原Fig3/4/5/TableI/II逐file/脚本hash/变换/列定义单列；新图从新raw独立画，作者raw为reference，原刊图另列。没有一一链不能claimedORIGINAL-EXACT。 |

## 原作者已有raw进一步约束

- planar benchmark_PCS_obs_range2.txt15002行：m1/2各751，其余750；NR1000。当前source mode4为1000/m；不能把任一版本次数当final-paper明确N。
- pcs_m_analysis.txt112684行，gd_rbs_verification.txt57965行；current source目标200000/50000仅成功时递增，真尝试量未封顶。正式有限采样必须预登记总请求/接受pair/有效RBS三个分母。
- ABB apc_kdl_proj.txt500000行，APC成功flag39632；raw输入q缺失，不能从flag重新独立验证原500000个q的闭合/碰撞。
- ABB三visibility候选raw108435/444392/77488行，NR/RSS使用comma分隔；当前源env/接受分布也不同。不可将这三文件简单接到“统一II50000pair”的标签。
- 这些基数只是AUTHOR_REFERENCE文件审查，没有变成我们的scientific试次；记录文件SHA在P4_AUTHOR_REFERENCE_DATA_CARDINALITY.json。

## 本次原创planar数学驱动的接口和未覆盖边界

baselines/p4_full/planar_native_qualification.cpp仅调用外部未修改的planar_ckc ckc/kdl类，CLI为 binary I output.json；final单JSON，每个完成case另flush到output.json.partial.jsonl防止超时丢前缀。seed20261014；100均匀source-chart FK样本；原start/goal各5个single-joint±.01的NR输入；固定原start20p×2branch APC；两个原endpoint只诊断、一个0.1rad闭合负例及两branch不可达目标。

long-double矩阵相乘SE2是项目原创oracle，不复制作者源码；另有只读Python direct cumulative/math.fsum核验器verify_planar_native_qualification.py input.json output.json，从原source-input manifest核验原endpoint与固定扰动。两种独立FK表示分别为矩阵乘积、累计角和，均保留末q chart。

155条预注册记录不是155条全部必须成功的投影：合法不可达IK branch须保留source reject而非runtime error；返回true的projection必须真实符合既定残差门。源拒绝的具体原因、所有reachable branch完整性、collision、RBS、planning、人工奇异秩仍未由该驱动验证，不允许将它写成P4环境I完整通过。程序return0只表示保存完成，不是scientificPASS。

本文件全部结论属于文档/来源审查或执行前约定。没有科学运行；当前正式计数、模型、原论文公式、旧记录和科学门数值均未修改。
