# III RRT+PCS 完整原路径物理资格 PRE 草案

2026-10-18。用户已授权 III SOURCE01 一次原10秒 solve，并将实际候选交独立物理门；root 指定本项外120秒墙钟/240秒CPU、work100/200、max2048，仍扣原R2总3600/7200。未执行本物理项。DRAFT 所有冻结/执行/审查标志仍 false，最新 prior 由 root 按运行前真实版本重绑后冻结。

SOURCE01 已实际 exact、非 approximate，一次 solve，原15里程点、16回溯（14 true、2 false），原false及全部原始材料保留。源码/输入/判据没有变化，不重跑source或旧局部。保存独审25/25：`reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_SAVED_INDEPENDENT_POST_20261018.json`，SHA256 `be8a4f2d3ec4b095f34c409d980e6c7d511a5f417594b3d29893e6607e941418`。source execution SHA256 `f9229c0c2b768f76f540e4667545b09d2b1c425957817cb0a284f696760f39b0`，它的 `independent_path_qualified=false` 永久保留。

纯保存物化已唯一完成：`configs/p4_d080/iii_rrt_pcs_source01_complete_saved_queue_v1.DRAFT.json`，SHA256 `037b754847718d5bc2a929c7600d354c61b785d249eeacd31548c52f84fdf1d9`。独立保存检查7/7：`reports/P4_D080_ENV_III_RRT_PCS_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_20261018.json`，SHA256 `8318b25ac39cfe6a6f69df71e95a118381ef42ff9b9e88013683719c423f9f73`。原14边的 first true 原M完整连通，binary64去重649节点、648叶，原16尝试均按原顺序消耗。两次false不改判、不截断日志、不补点；逐边完整M以原引用保留。

本项采用已通过 II PCS 原科学核：每个原节点两个独立FK、原闭链矩阵残差、原机械限位、每条所引用边的被动解析分支成员身份及原aligned离散碰撞策略。唯一环境替换是显式 `'II'`→`'III'`，不改变公式/门限/点序。位置maxabs≤1e-5mm、旋转矩阵maxabs≤1e-5、分支零判别64×机器epsilon、full12叶L2严格小于.05rad。649节点全部检查，2048是资源停止门；不截尾、不更换节点/分支、无新IK/NR/投影/RBS/solve/RNG。

| 字段 | III真实设置 | 来源及范围 |
|---|---|---|
| 独立机器人 | ABB两臂，基距1200mm，基座(-600,0,0)/(600,0,3.1416) | 既有 `oracle.arm_fk(...,'III',arm)` 与 `physical_nr.model_geometry('III')` |
| 抓持闭链 | rod500mm，既有FLIP，原毫米/弧度 | 既有 `grasps_for('III')`；不能误用II的900/300 |
| 原规划环境 | 内部 env2 | 已建III ELF直接复用，不编译/规划 |
| 碰撞worker | 既有 v3 manifest的abb/native与abb/aligned二进制，实际argv envIII | adapter保留原III障碍、原20mesh和8mm tolerance |
| 碰撞调用上界 | 每节点两variant，各最多103条原PQP调用 | III原env2先0..76；若TCP高于800mm直接原拒绝，否则77..102；manifest query_count=0仅build元数据不能用作真实次数 |
| 合格策略 | 完整独立闭链/限位/被动branch + aligned离散collision false | native与aligned完整原响应分开保留；不把native TCP不一致改判为通过 |
| 生命周期 | V PHYSICAL01已审注册、mask、中央kill/reap/空组/真实EOF | 只身份及120/240帽适配；D080真实argv互斥薄复用 |
| 写入 | NR393已审即时close JSON，原散文件保留；最终完整tar逐成员逐字核对后fsync文件+目录 | 不逐node fsync，禁止补造记录；FinalIOGuard沿原绝对work帽监督，超时留原prefix/partial archive |
| 成本 | 真实GNUtime独占inode/父链/argv，三观测Decimal max envelope | 与最新已实际账本一次替换，不双计，历史UNKNOWN保留 |

原科学loop的计数wrapper与循环从已审SBL TAIL02/II PCS版本提取，只做环境字符串与节点写入器适配；监督与worker清理从V PHYSICAL01提取；`FinalIOGuard`/`durable_saved_snapshot`从已审CBiRRT_NR PATH提取。后者完整body保持。差异需要独立增量静审后才可冻结。

执行源码是 `scripts/p4_d080/qualify_iii_rrt_pcs_physical01_v1_draft.py`，监督源码 `scripts/p4_d080/supervise_iii_rrt_pcs_physical01_v1_draft.py`。物理协议 `configs/p4_d080/iii_rrt_pcs_physical01_v1.DRAFT.json` 只绑定完整649队列、真实SOURCE/POST、旧碰撞二进制/实际instrumented源码/20mesh、全部自身及独立数学源码、D080和最新prior。root在独立审查后逐字提交并另存frozen协议，唯一运行。

离散物理门通过也不证明CCD、实体rod表面、作者省略碰撞pair安全、全局成功率、PCS复杂场景优势或原论文完整复现。正式仍0/18,000，VI继续只读，不P2/Isaac Sim/FR3新实验。

冻结前发现另一个 V BUILD01 在 commit 门之前退出、原execution/receipt不存在的已发生监督尝试。原四DRAFT已逐字保全至 `results/p4_d080/20261018_III_PHYSICAL_PRIOR_ADAPTER_PRESERVATION/old_drafts.tar`，逐成员核对通过。本项仅将 `current_prior` 切到纯stdlib `validate_prior_preflight_recovery_v1.validate_prior(spec,RUN,run_dir)` 并纳入OWN/hash。正常费用分支逐字复用原B body；唯一固定V BUILD01单例承认独立审计的保存恢复记录和两观测Decimal费用，不将原external_supervision=false、缺receipt、null hash、exit1或原envelope=false升级。原算法/物理循环与上述科学判据不变；最新包含该成本的账仍由root终绑。
