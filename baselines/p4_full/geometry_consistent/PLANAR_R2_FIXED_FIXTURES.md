# R2 平面固定资格输入声明

本文件与 qualify_planar.py 在首次运行前一并冻结；当前仅已写源码，未执行。先前 PLANAR_QUALIFICATION_PROPOSAL.json 的 328 条是未获冻结的建议，本轮不采用。

根协议为 configs/p4_full/r2_geometry_consistent_qualification_v1.json。实际固定任务为 100 个 R1 FK、80 个 APC 请求、2 个原端点 Jacobian、8 个解析 fixture，共 190 项。两原端点另作不施加闭合成功门的诊断，重复利用相同输入，不增加独立任务。原 start 的 40 个 APC 既是 R1 重放又是 R2 两端点 80 请求的一半，保存双 lineage 但只计 40；goal 40 为固定扩展。所有 chart lifts 保留，候选数量不当作独立样本。

FK 直接读取 results/p4_full/20261014T1555_R1_PLANAR01/I_native.json 的 100 个 q_author_chart，不新增随机数。比较的是 endpoint H=F*T(7,4) 的位置、姿态与已保存 oracle_SE2；一般未闭合状态下 F 的平移不等于 endpoint_position-(7,4)，不能直接相减制造失败。另用累计角求和与 physical_nr 的独立约束作交叉核验，不调用 NR 求解器。

Jacobian 仅在原 start、goal 两点，用 ε=10^-6 中央差分，平移门 5×10^-6 source unit、角门 5×10^-7。不是 20 个新采样点。

八个解析 fixture 全部明写在源码 ALGEBRA_FIXTURES，不搜索、不筛选：

| ID | 实际 factor 类型 | 固定目标 | 分支符号 | 预声明类型 |
|---|---|---|---|---|
| equal_regular_positive | [0,1,2]，长度 [1,1,1] | 标准 θ=[0.3,0.7,-0.2] 正向积 | + | REGULAR |
| equal_regular_negative | [0,1,2] | θ=[0.3,-0.7,-0.2] 正向积 | - | REGULAR |
| ground_first_regular_positive | [19,0,1]，长度 [√65,1,1] | θ=[0.3,0.7,-0.2] 后乘实际 γ_c | + | REGULAR |
| ground_middle_regular_negative | [18,19,0]，长度 [1,√65,1] | θ=[0.3,-0.7,-0.2] 后乘实际 γ_c | - | REGULAR |
| far_unreachable_positive | [0,1,2] | (x,y,ψ)=(10^8,0,0) | + | UNREACHABLE |
| far_unreachable_negative | [0,1,2] | (-10^8,0,0) | - | UNREACHABLE |
| straight_coalesced_both_signs | [0,1,2] | (3,0,0)，腕点长度 2 | +、- | SINGULAR_BOUNDARY |
| folded_infinite_both_signs | [0,1,2] | (1,0,0)，腕点 0 | +、- | DEGENERATE_INFINITE |

后两项各在同一固定目标上检查两个会合标签，因此八 fixture 合计 10 次底层 solve_three_r 调用；并不是 10 个独立目标。非正则项必须保持 source_regular_eligible=false，不能将边界解当作 PCS 正则成功。没有改动物理连杆、ground 或原端点。

source chart 与 source 机械限位分别保存。PCS/GD 原 check_angles(f=1) 对 q0…18 使用 ±179.9/180×3.1416、对 q19 只要求非负；运行 chart 另要求 q19≤2×3.1416。kdl_class.cpp 的另一个 check_angle_limits helper 对全部20维做对称绝对值限制，runner 单列这个不同诊断，不将其替代规划 validity 策略。chart 合法不保证机械限位合法。每个原端点、每个被动标签的两分支合并后必须至少有一个 source-limit 合法候选；任何不合法分支和所有数值残差继续保留。

输出接口为 run_planar_suite(root,out,protocol)，out 是目录；输出文件 I_geometry_consistent_raw.jsonl 与 I_geometry_consistent_summary.json 只使用排他新建，禁止覆写。每条原始记录完成即 flush；失败、不有限、超时或异常写入日志并停止受影响模型。没有 main、没有导入即运行、没有规划调用。所有统计来自真实执行后产生的文件，本文不先填 PASS。
