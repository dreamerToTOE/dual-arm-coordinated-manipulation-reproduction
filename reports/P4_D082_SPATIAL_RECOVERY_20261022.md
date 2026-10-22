# P4 D082 空间路径保存证据恢复（2026-10-22）

本次只读恢复确认：环境II已有 **4条完整合格离散路径**，环境III已有 **1条完整的 reconstructed/aligned 离散路径**。这些结果直接复用，不新增source solve、FK/IK、碰撞或规划调用，不修改历史成功、失败及成本记录。当前D082主对照由独立重建的平面20R实验承担；空间证据用于说明已有完整机器人路径和PCS实际切换。

|环境|规划器/方法|完整节点/叶数|闭链位置最大值/mm|旋转矩阵最大值|全12角最大叶距/rad|人员独立保存证书|
|---|---|---:|---:|---:|---:|---|
|II|RRT/PCS|177/176|3.410605131648481e-13|4.440892098500626e-16|0.04949053472601928|`P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json`，2337/2337|
|II|RRT/NR|393/392|9.793997321594361e-06|3.0701365727470176e-08|0.0478001489336342|`P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json`，24448/24448|
|II|CBiRRT/PCS|413/412|4.547473508864641e-13|6.730727086790012e-16|0.049872908712302065|`P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json`，58152/58152|
|II|CBiRRT/NR|689/688|9.8002665254171e-06|4.6722628137957356e-08|0.04951897373867186|`P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json`，41787/41787|
|III|RRT/PCS|649/648|4.547473508864641e-13|4.468647674116255e-15|0.04995648687917435|`P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json`，16/16|

以上证书均在`reports/`，各证书引用的实际execution字节均与原证书SHA256相同。本次进一步重hash环境II CBiRRT/PCS的3668项、II CBiRRT/NR的11725项、III的3253项保全记录，共18646项引用，均无缺失或变化；这是引用数，跨证书可能重复，不能作为新的实验次数。II两份较早的RRT证书未提供统一retained哈希字典，本次核其execution身份，并以较晚CBiRRT证书中的继承保全链接支持恢复；不声称重新执行其全部历史检查。

III的唯一source结果为seed7、exact=true、approximate=false，保存solve wall为6.177099651s；15个里程点、14条成功局部边、16次回溯尝试及失败均保留。source原main callback为`ORIGINAL_MAIN_ALWAYS_TRUE_NO_FK`，所以source的exact标记本身不是安全证书；649个保存节点的独立物理资格另行保存。保存文件位于`results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/`，source位于对应`...III_RRT_PCS_SOURCE01/parsed_source_result.json`。

本次补查649个队列q12与每个`node_XXXXX.json`、`node_XXXXX_math.json`精确一致，最终node内的collision对象与独立response文件一致，**0个绑定差异**。起终点与原source严格相同。最终路径主动角色依次为`0,0,0,1,0,0,0,1,1,0,0,0,0,0`，实际4次角色切换；这是最终解路径机制见证，不是搜索树切换次数，也不证明PCS性能优于固定划分。

III全部649个aligned TCP通过；原native TCP全部649个不通过，最大位置差0.003570536971253091mm、旋转矩阵差7.347665530579861e-06。历史`independent_path_qualified=false`字段保留，其严格语义不应被新D082简化标签回写覆盖。可接受的表述为`RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY`。原碰撞pair、8mm容差和杆件建模限制仍在；无严格连续CCD、最小净空证书、全部实体杆表面或遗漏pair安全结论。原native等价不成立，不将离散节点安全升级为任意时间连续安全。

未提交的`scripts/p4_d082/audit_iii_saved_path.py`和`audit_saved_virtual_simulation.py`是保存证据审计：只读已有判定，不构成新的独立数值计算。前者缺少逐q12到node/math的显式绑定断言，本次已单独补查且全部一致，不能据这一恢复脚本遗漏反推旧路径无效。旧III第一次D082审计FAIL（7/8）和v2 PASS（8/8）均保留，不覆盖历史失败。

可复核的新恢复结果为`reports/P4_D082_SPATIAL_RECOVERY_20261022.json`。最小后续命令如下，输出路径须为尚不存在的新文件；只做保存数据算术与hash，无任何source或模型调用：

```bash
python3 scripts/p4_d082/audit_spatial_saved_20261022.py --output work/spatial_recovery_repeat.json
```

III无需重跑solve或碰撞。最高优先级的新增数值工作是独立重算平面主实验的闭链、限位、真实碰撞与局部边证据，随后完成公平full/fixed/RSS/NR解释与报告。V5仍是未授权source的工程候选；VI只读归档；本报告不启动其他论文或机器人集成。
