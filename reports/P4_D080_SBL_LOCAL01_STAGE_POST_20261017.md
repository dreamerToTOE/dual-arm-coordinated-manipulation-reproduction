# D080 SBL 原生 lazy/RBS 局部资格结果（2026-10-17）

固定正负两条重建树夹具、各trace/plain四进程已经实际完成并独立验收。原isPathValid、递归RBS及removeMotion正文未改变；不重复原setup13点或II四条全程路径。冻结提交7a470dbe，协议f678405e0f520eedba276fcd7860a748d473758b48a4737d740168ff03f6ce80。

正例保存node0→108，原role0/branch3：实际true，107次固定分支投影、215次vector RBS和108叶，子节点valid=true。107次投影输出逐binary64全等于旧edge0的107个内部节点；全部109原节点SHA与独立合格证书复用，108相邻叶严格小于原.05，不新算模型、不用近似相等冒充证书。负例保存node0→359→360、真实branch[3,0]→[0,3]：实际false、零RBS、两次递归remove，parent置null后的真实退役被核对，根保留。四进程plain/trace树、分支、角色、返回与副作用一致，全部stdout/stderr EOF、exit0、进程组空、live registry为0。未实际地址复用的性质仍UNKNOWN。

独立报告 `P4_FULL_R2_ABB_SBL_PCS_LOCAL01_SAVED_INDEPENDENT_POST_20261017.json` SHA47c32c8a9c97816e2c56a44206447649853a0741ad2714172bf44df5639bddf3。此局部夹具分类RECONSTRUCTED_TREE_FIXTURE，不是原作者原生起终点或SBL全局成功。local未触发connect/save/reconstruct，writer无attempt且原五文件缺失均真实保存；sidecar仅证明我方持久化，不证明原fstream内部成功。

命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_sbl_pcs_local_shadow_v2_draft.py --protocol configs/p4_full/r2_abb_sbl_pcs_local_shadow_v2_v1.json
```

实际上界8.19墙钟/2.89CPU秒。V27共45execution=33科学账+12工程，累计869.885705375994墙钟/811.528923CPU秒；余额仅上界2730.114294624006/6388.471077，历史未测尾UNKNOWN保留。source solve仍5，本次0；正式0/18000。新表211×204保留前200列，VI原历史/974和旧失败不变。

下一项是另冻单次SBL solve：II/A01/seed7/.8，原10秒、总20墙钟/40CPU秒。自然观察checkSolution、lazy删除、未知connect与原save/RBS回溯；EXACT只是候选，必须独立全路径检查。失败/非exact不换seed、不追加同claim。本轮未授权正式18k、没有VI新运行、不P2/Isaac。
