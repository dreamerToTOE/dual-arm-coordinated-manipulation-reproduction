# SBL_PCS 首次 setup 与公有13点资格

唯一SETUP01在冻结提交 `ff25dc60` 后执行，独立后审 **9534/9534、零失败**。本阶段确认原 SBL setup、公有投影作用及完整进程证据；SBL solve 和完整路径仍待资格。

执行命令：

```bash
/usr/bin/python3 scripts/supervise_p4_full_r2_abb_sbl_pcs_setup_draft.py --protocol configs/p4_full/r2_abb_sbl_pcs_setup_v1.json
```

固定II/native1、既有A01 RECONSTRUCTED端点、seed7。协议SHA256 `ef7432f1b577e072dc531dc234a3817aeca1aab61dd94f60603e449570d47a77`；execution `107b8fe30b5e2f02c0a2ad035a2cee62d42f5b604c39d8de4bcd1952505b56e4`；独立POST `1c3ac4aef9f08917d33af7302f0b003f1d7960a557ddef4c1fad28f6caec8415`。原SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST及external=false等字段留原字节；独立证书另载通过。

实际一个source、一个请求、setup一次、固定零点与12基向量公有project共13次、solve零次。真实默认类型RealVectorRandomLinearProjectionEvaluator，projection维数3、两grid[3,3]/空树[0,0]，cell sizes [0.09401987353262707,0.0731507039721386,0.07248321696072735]；sampler null、userConfigured false。setup自动range3.4158286519086403与原solveRange .8分别保留，公有作用矩阵列及binary64完整保存。它不证明protected存储字节或setup内部RNG次数，后者仍UNOBSERVED。

完整raw stdout8413B/stderr669B、mesh_load1/freeGridMotions2共六entry/exit事件、单次write/stdin关闭/双EOF/exit0/reaped/空组及九映射文件身份均独立通过。20个作者mesh运行前后hash一致，文件保留本地；本次仅提交来源与hash。请求前loaded symbol scope结合已审libompl静态证据，不冒称直接读取运行时GOT。未产生规划文件。

GNUtime `1.94 1.46 0.20 0`；完整child上界1.95wall/1.68CPU，在原10/20内。内部样本1.8024732929998208wall/1.612739CPU保留、不重复相加。V25真实43execution=32科学账+11工程，累计839.3257053759941wall/771.588923CPU，R2余额仅上界2760.674294624006/6428.411077。历史未测尾UNKNOWN保持，source solve累计5、本项新增0。supervisor自身持久化不在该child费用内；预检计费但此前未安装内部hard timer，此限制保留。

完整覆盖表211×186、前182历史列逐值保持；仅T02/T05/T08/T11/T17/T25附setup观察证据。V25保全passed=true、七组mismatch全空：旧1028科学文件、57崩溃文件8482891B及tar、另5工作树13未提交、V24账/表/保全均保持。账SHA256 `ce612e7c9706666a338aae6deda581274f1aadb229e2be999cd6ee836499e64a`；保全 `b3a0ab365ef415673f2e0ab7a5fb45365d5a86e33ec7c0584b5bf875c15c07d5`；CSV `2b34a55a39f3678d1d5a7ec1ca1d1c0bf13c828fad9ec6f2f4cfe7461604a491`。

独立POST执行前发现审查器错误：初始prefix与最终mutable状态直接比较，以及journal空行后final事件数量假设错误。旧稿SHA327f4c61前缀版本已保全，修后只比immutable身份并分别核初值/终态、按实际两个final事件核行位置；仅一次实际POST，无科学重跑、无raw修改。

下一项处理原connect Motion的a_chain未初始化输出读取，先做最小writer/shadow版本化设计和独立审查，不初始化Motion或改采样/控制/RBS。RSS固定32数学资格的完整外层监督另线审查，未执行；新解碰撞资格仍UNKNOWN。原失败、源码和所有UNKNOWN保留。

本阶段不认证SBL完整路径、连续无碰撞、RSS或PCS优势；VI974/974余0，正式0/22500、全部211义务及原统计规模保持。端到端后先可重复cost pilot，再申请正式资源，不P2、Isaac或提前结题Word/PDF。
