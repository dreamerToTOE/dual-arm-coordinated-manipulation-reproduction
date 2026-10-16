# ABB NR 原GD/SVC/RBS接口局部资格 POST

2026-10-16接续记录；原固定输入、源码冻结与科学运行日期为2026-10-15，不重跑。

**固定局部资格通过：FIXED_LOCAL_ABB_NR_QUALIFIED。** II/III全部4端点投影、II保存的全部3条边各原RBS/原回溯，在同binary plain/trace共20顶层全部返回true，10逻辑对的原布尔值、q/path binary64及非计时计数一致。环境II下一有限planner资格门通过；这不是全局NR规划或原论文性能通过。

来源7ee551a，命令：

```bash
python3 scripts/qualify_p4_full_r2_abb_nr_local_draft.py --protocol configs/p4_full/r2_abb_nr_local_qualification_v1.json
```

4输入为A01 RECONSTRUCTED端点；3条边为第一条已保存PCS路径的全部连续milestone边，没有换样本/端点/边、补点、修路径或更改门限。数值为RECONSTRUCTED_PHYSICAL_FULL_NR_CPP，显式替换原kdl::GD body；原SVC/RBS控制流和原0.05/depth150保持，原GD完整源码与原失败保留。普通NR允许全12角改变，无PCS主动链/branch门。

147/147唯一节点、全部refs/原路径及尾部完成独立数学/原机械界/v3 aligned原离散碰撞检查。最大闭链位置9.887878832159913e-6mm、旋转矩阵2.5558390071012127e-8，均在原1e-5门内；最小原限位余量0.08726666666666683rad。三条完整原回溯节点65/65/17，对应最大full12叶距0.041259710686189305/0.04380115273344425/0.04769340858982442rad，均严格<0.05。没有RBStrue/reconstructfalse、超时、异常或未检查尾部。

trace实际GD286、原collision286、PQP33150、RBS285、回溯285、中点282；plain内部计数UNOBSERVED，不按trace倍增。数学逐臂FK/J294次、adapter内部逐臂FK/J588次、独立collision147次、native/aligned各17026 PQP，共34052，均由实际事件/原始返回统计。原native TCP最大位置差0.003531732927598341mm，147节点的既有不一致保留；selected aligned TCP最大位置差2.2737367544323206e-13mm、旋转差3.3306690738754696e-16，全部合格。不能将保留native失败冒充已修通过。

运行actual wall3.6995257820017287秒/CPU4.245554秒；单项60/120帽保持。22次execution逐自身一次累计wall385.7659771849949秒/CPU345.13823秒，工程也保守纳R2，原3600/7200帽保持；VI974/974余0，正式TableI0/22500。原作者网格本地保留及hash提交，runtime多模式网格不公开转载；原始日志、每个数学/碰撞结果及失败记录均入77f0334。

独立保存审计：runner作者另写stdlib审计117258/117258，明确personnel_independent=false；另一未写runner代理单独事件树重放、保存矩阵算术及资产审计218766/218766，0新科学。根代理核实两份PASS、原执行与前后1203绑定SHA、完整尾部及源冻结后接受本局部资格。对应JSON/MD均保留，不以重复科学运行替代审查。

下一项另冻工程与单次II seed7原RRT_NR solve10秒、外帽30wall/60CPU，随后完整路径独立资格；原source Exact与独立路径PASS分列。三planner/六环境、500000投影、约50000点对、全部Fig3–5/TableI–II/窄通道/消融和211项全文义务保持。RSS分布/原RBS/入口独立诊断，不新增VI构造。原离散pair/8mm PQP/共线杆几何限制保留，不声称CCD、完整实体几何或论文完成，不P2/Isaac。
