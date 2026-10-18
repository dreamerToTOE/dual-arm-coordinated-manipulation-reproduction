# D080 SBL 原生单次规划与回溯观察（2026-10-18）

10月17日冻结并实际执行的唯一 SBL_PCS solve 已完成保存证据独立验收，现于18日接续入V28账。执行冻结提交59a68e3a；环境II/A01重建端点、seed7、原Range=.8、原10秒solve，20墙钟/40CPU单项帽不变。没有第二次solve、额外local或重复四条II合格路径。

作者搜索返回Exact solution，6个里程碑；实际5条边的原成功回溯M长度35/41/185/65/65，合并387节点/386叶。第5边原role0回溯false、M2节点，原代码随后role1回溯true65；这次失败原样保留，不隐藏或另选路径。此为原搜索和原回溯的候选，**完整独立闭链/分支/限位/碰撞资格尚未运行，不能写成第五条合格路径**。source EXACT不证明CCD、500次成功率或PCS优势。

原调用实际50个Motion lifetime、34次checkSolution、27次remove、1次save；14个connect lifetime的a_chain未知，从未读取其未初始化storage。最终writer6项均来自known root/grow，没有未知connect进入writer，不能据此声称原未初始化风险消失。最终原文件、元数据三列/行序、sidecar字节读回通过；原fstream内部open/write/flush flags仍UNKNOWN。

独立证书 `P4_FULL_R2_ABB_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_20261017.json` SHAfea6f01839a041430d10da796a0c7a59bd65dbf4bcf7487dc8c27a7c15358066，111项记录仅为transport/来源/保存字节和费用的完整性检查，不当作规划成功率。原source实际solve观察0.227167777秒包含观察/输出，与正式性能计时分开。

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_sbl_pcs_solve_shadow_v2_draft.py --protocol configs/p4_full/r2_abb_sbl_pcs_solve_shadow_v2_v1.json
```

实际外费7.05墙钟/5.01CPU秒。V28共46execution=34科学账+12工程，charged876.935705375994墙钟/816.538923CPU；原R2余额上界2723.064294624006/6383.461077，历史未测尾UNKNOWN保留。source solve累计6，本次新增1；正式0/18000。211新表208列继承全部204历史列和D080范围，原22500历史分母/VI974记录不改。

下一项只从已保存原trace提取完整387节点和全部尝试，复用已审物理检查循环；不再次调用源solve或reconstruct。资格前冻结真实输入、同原门限和独立120墙钟/240CPU上限，仍扣R2余额；若未验证全程，不以局部前缀给PASS。环境V PCS工程门并行补齐，V两个后续合格重建端点复用，RSS独立线、VI存档，不P2/Isaac/FR3新实验。
