# D080 环境 V：固定24节点独立诊断完成

冻结提交 `7a40f67e710738b0bc4f3bb6a6066b8256e63682`；协议 `configs/p4_d080/v_pcs_physical01_v1.json` SHA `b00774bf8592b541bed7ed143db01a017494c6eea7fc6a062e2a077b17b8667f`。唯一执行命令为：

```sh
/usr/bin/python3 scripts/p4_d080/supervise_v_pcs_physical01_v1_draft.py --protocol configs/p4_d080/v_pcs_physical01_v1.json
```

本次完整消费 LOCAL01 保存的原24个唯一节点，既未新增样本或投影，也未重跑局部/规划器。两碰撞worker正常退出、已reap、组空、EOF完整，所有固定调用完成：独立arm FK48、branch48、adapter24、adapter内部FK/J96、双variant PQP4176。原execution SHA `ae553ae764753ecfc0cfba294902ecac2641c8b0784e8dae0c74d8bb62953450`、所有原失败和false字段保持。

24/24闭链、原关节限位和全部被动分支关联通过；闭链位置最大误差1.4779288903810084e-12 mm、旋转矩阵最大误差3.8510861166685117e-16。aligned source-policy下15个节点合格、9个碰撞拒绝，拒绝ID为0/2/15/16/17/19/20/21/23；全部拒绝均非数学错误。native同样9拒绝，但24个节点native TCP全部不一致，不能将其当原native几何资格通过。未改变原8mm安全带或1e-5验收门。

人员独立保存POST 430/430，证书 `reports/P4_D080_ENV_V_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json` SHA `0a9cdde6f9cee4d625861d4bf2180c315b07b1e253804522a30b9bc8be1a38a9`，仅确认固定24节点诊断、完整保存与费用；`independent_local_qualified/independent_path_qualified/continuous_collision_certificate`均false。LOCAL01三条实际公有RBS与三条回溯false、另一对依赖未执行保持；false根中的true叶或回溯前缀不升为路径成功。

原17唯一source collision点的TCP、箱体姿态、87pair身份/API/CloserThanTolerance聚合与新独立aggregate碰撞响应另作纯保存核对；本阶段POST明确保留该项PENDING，不预设其结果。独立adapter未保存逐pair closer，所以不能以aggregate一致冒称逐pair独立几何重算。7个source未做碰撞的public project输出另列。

费用按原raw GNUtime、外单调/reaped CPU、内部receipt三观测Decimal最大包络一次入账，9.466394254997576wall /3.7087890000000003CPU，低于本项60/120及工作50/100。V34共52execution（38科学账、14工程账），累计1113.4602605769917wall/927.6919419999999CPU；R2总3600/7200不变，余额仅上界2486.5397394230083wall/6272.308058CPU，历史未测持久化尾UNKNOWN保留。POST两数相加与账本math.fsum的最后浮点位差别不修改原文件。

最新211行232列对照表 `reports/P4_D080_V_PCS_PHYSICAL01_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261018.csv/.md` 保持前228列逐值不变。source solve累计6、本次新增0；正式0/18,000，原22500历史与VI974/974只读保持，II五条合格路径未重跑。

下一门：完成source17保存对照后，保留真实碰撞负例，准备V原RRT+PCS一次完整入口的最薄工程与单次资格；具体新入口尚未冻结或执行。原RRT直接指定IK分支，三参随机helper缺break不在该调用链，暂不混入修复。III窄通道原range .8单目标工程并行准备，IV与RSS独立推进；端到端通过后真实cost pilot，再申请正式18k。禁止P2、Isaac、FR3新实验及提前结题。
