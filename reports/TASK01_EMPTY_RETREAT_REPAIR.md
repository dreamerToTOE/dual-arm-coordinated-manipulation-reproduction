# TASK01 — 空载退出构型连续性修复

2026-10-03；状态：**PARTIAL（工程回归 PASS；TASK01 基准仍 IN_PROGRESS）**。独立第五件与第四→第五连续实测通过；不是完整五件/稳定性/论文方法/冻结证明。

## PRE-TASK REPORT

- Task: TASK01 / Cube04 precision variant, Cube05 empty retreat reliability.
- Goal: 修复释放后 Cartesian IK 换支 / 命令终点非实测起点的问题，不改接触协议。
- Paper method understood as: TASK01 仍是基准准备；P2/P3 方法尚未开始。原 D004 前三件协议仍未实现，第四件例外已由用户批准。
- Scope: 实测空载起点、局部 seed 延拓备用路径、包含已释放 Cube 的完整同步 FCL、只读回归、真实 PhysX 试验。
- Files expected to change: 旧工程共享执行器的独立宏分支/新增策略头/只读探针/CMake；本仓测试探针、报告、六份记录和结果。
- Validation plan: 策略单测 → colcon 完成 → 真 RobotModel 只读 FK/FCL → 独立 Cube05 → Cube04/05 连续实测。
- Known risks: IK 极限/起点真实碰撞可能无法工程修复；旧 USD 回调时序问题仍存在；Task27 旋转修复已在前轮完成，本轮保留；Cube04 单次 PASS 非稳定性。
- Need user confirmation: no，当前只是 ENGINEERING；如需要改模型/物理/接触/门限则停止。

## 实现与边界

上游用户工程 https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，修改前 `7be3659`，分支 `task01-runtime-fixes`；根未声明统一许可证。继续使用独立 `task01_cube04_precision_insert`，旧 Task26/27 默认路线不变。

已释放后，确认双杯 OPEN，读取同一 MoveIt RobotState 的左右实测关节，等待新 Cube Ground Truth。退出仍使用原目标；普通 Cartesian 候选失真时，在每个 ≤2 mm 小段上复用已有精细数值 IK，以上一段构型作下一段 seed。原局部 4 mm / 0.08 rad / 5 µm 求解界限不变；不将全部内部 0.1 mm 迭代点作为 30 ms 命令点，避免人为放慢20倍。

候选仍需原 5 mm FK 直线门限、关节极限、同步完整 FCL。当前已释放 Cube 以最新原 Bridge pose 加入校验世界，不扩大 ACM、不去除当前 Cube。Task27分支前轮已用 `Gf.Transform(transform).GetRotation().GetQuat()` 消除scale旋转错误，本轮保持；但USD回调发布时刻不等于同一步PhysX采样，不声称已建立正确的动态同步测量合同。

测试夹具新增可选 `--preplaced-count=4`，默认仍3，仅用于快速复测第五件；预置件不得算作执行成功。

## 检查点

- colcon 最终完成 57.2 s，旧 rosidl deprecation warning 非编译失败。
- 独立 C++ 策略测试：OPEN/有限7关节/步数上限/非有限输入/越界拒绝 PASS。
- Python 19/19 PASS；语法/diff PASS。
- benchmark YAML 原 SHA `a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8` 未改，36 null；TASK01 IN_PROGRESS / TASK02 TODO。
- 真 RobotModel 只读最终探针 exit0：左右20mm连续seed路径/FCL通过；已释放 Cube 挡住路径时 FCL 正确拒绝；超范围/全零 quaternion 拒绝；零位移输出有效保持。首轮探针将 Quaternion{} 误当全零（ROS默认w=1），仅修正测试输入，原失败日志保留。控制器门限未改。
- 当前独立第五件物理测试运行；二进制 SHA `77b4f4993c0a5a0cecc82e03c7a671182f384d60576e42e14443d80c78b0866f`，legacy `4f88c68`（运行控制器同 `e25de24`），repro `9098faf`。前三/四件预置只用于隔离，不能称完整五件交付 PASS。

## Fidelity

[ORIGINAL] 未开始论文方法；[ADAPTATION] 沿用已批准第四件协议；[ENGINEERING] 空载实测起点/连续 seed/FCL/单测；[DEVIATION] 不新增第四件已记录例外以外的协议差异；[EXPERIMENTAL] 前3或4件预置的物理夹具，非完整五件证明。

## 独立第五件真实 PhysX 结果

`results/20261003_TASK01_empty_retreat_center_01/`：controller exit0，batch5 PASS。最终原 GT 位置误差0.540mm / 深墙间隙0.514mm / 两侧间隙1.335与1.665mm；后吸推入最大原始关节力矩35.52Nm（不是TCP力）。实测关节起点与旧命令终点最大差左0.000809rad、右0.001186rad；普通 Cartesian 得到左0.002mm、右0.001mm直线偏差，包含已释放 Cube 的同步 FCL 290采样通过，物理退出执行通过。**这轮未触发备用数值 IK，不能只凭本轮声称备用已做真实运动验证或修复的因果已隔离**。

4,691稀疏PhysX采样，完整性/采样异常0；物理终态 yaw0.062808°。前四件预置，不能算完整五件通过。停止时 MoveIt 再次 -11，单独保留原 teardown缺陷。

备用长路径另做只读重放：从本轮落桌日志四位小数 seed 出发，左404.716mm/203段、右301.601mm/151段，备用求解通过（日志直线偏差均0.000mm），含释放Cube的FCL610采样通过；**没有发布机器人命令**。原测试失败日志保留，最终长重放exit0。源码 `3ee42d2`（执行器未改，仅探针扩展）。

下一步：全新干净场景，实际Cube04→Cube05连续测试（前三件预置），不是改既有场景或追加横向控制。

## 第四→第五连续真实 PhysX 结果

`results/20261003_TASK01_empty_retreat_pair_01/`，前三件预置落稳，其余真实供料/抓取/搬运/后吸推进，控制器 exit0、batch4和5 PASS。没有跳过第四件，也没有将前三件预置记作执行成功。

| 指标 | 第四件 | 第五件 |
|---|---:|---:|
| 最终旧GT中心误差 | 1.151 mm | 0.530 mm |
| 深墙间隙 | 0.244 mm | 0.476 mm |
| 邻件/两侧间隙 | 0.375 mm | 1.829 / 2.295 mm |
| 空载退出含释放Cube同步FCL采样 | 540 | 287 |

两段实际空载退出原直线偏差门限均通过（最大打印0.002mm）；没有触发备用数值IK。第四件后吸前Y误差0.079mm/投影余隙0.421mm；不做侧压，辅助杯保持OPEN。连续物理采样7,778条，时间/有限值/单位quaternion校验异常0；实际第四件后推段Y范围0.045866mm、yaw最大0.076537°，后来物理邻件轴向gap0.375402mm/旋转投影gap0.331231mm。投影gap不是PhysX穿透深度；采样约10Hz不能证明全频无碰撞/连续力控。最高原始关节推入力矩34.21Nm，不称TCP接触力。

批间保留旧短清障→RRT到下一件预吸点，无中途HOME；最终完成后两臂HOME。控制器时间约616.398s（time_scale=5）；该慢速可行性试验不声称码垛效率优化。独立探针墙钟801.351s包含准备/等待/末尾采样，不能与控制器时间混用。

实际质量0.800000012kg、有效摩擦0.5/0.5保持不变；旧场景源码SHA仍 `43aa7c2eb6a5667da5e94eaaef347229fe6178ec58d6a10d12dddf14ba2aa9e7`。所有本轮拥有的Isaac/MoveIt/控制器进程已停止；MoveIt退出仍-11，未冒充全生命周期无崩溃。

实际日志（原始完整日志在各run的raw/controller.log，本地保留）：

```text
[INFO] [1791032864.115957879] [task01_cube04_precision_insert]: task27_minus_inner PREPLANNED_COMMON_RETREAT RELEASED_CUBE_INCLUDED synchronized FCL PASS, samples=540.
[INFO] [1791032987.623401295] [task01_cube04_precision_insert]: task27_minus_inner final Ground Truth: expected=(1.100, -0.122, 0.260), actual=(1.100, -0.123, 0.260), cell_error=1.151 mm, +X deep wall_gap=+0.244 mm, -Y outer cube_gap=+0.375 mm.
[INFO] [1791033026.383731582] [task01_cube04_precision_insert]: Task27 batch 4 PASS: Cube 已落稳；双臂从短清障位经 RRTConnect 到下一件上方待命位，未执行长距离原路退出或批间 HOME。
[INFO] [1791033145.000105970] [task01_cube04_precision_insert]: task27_center_insert PREPLANNED_COMMON_RETREAT RELEASED_CUBE_INCLUDED synchronized FCL PASS, samples=287.
[INFO] [1791033272.442806196] [task01_cube04_precision_insert]: task27_center_insert center Ground Truth: expected=(1.100, -0.001, 0.260), actual=(1.100, -0.000, 0.260), cell_error=0.530 mm, +X_gap=+0.476 mm, +Y_inner_gap=+1.829 mm, -Y_inner_gap=+2.295 mm, total=+4.125 mm.
[INFO] [1791033306.698871744] [task01_cube04_precision_insert]: Task27 batch 5 PASS: 当前批 1 件已落稳入垛，双臂已回到共同 HOME。
```

## 完整复测命令

终端1，不source系统ROS，运行独立物理夹具：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --duration-sec 1400 \
  --output-dir results/20261003_TASK01_empty_retreat_pair_01/raw
```

终端2：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

看到夹具READY后，终端3：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_cube04_precision_insert --ros-args \
  -p first_batch:=4 -p max_batches:=2 \
  -p center_pusher_arm:=right -p execution_time_scale:=5.0
```

只读回归在MoveIt已启动时运行，不发布机器人命令：

```bash
ros2 run fr3_dual_palletize task01_empty_retreat_probe
```

旧结果目录仅列出已执行命令。复跑请用新的run-id，不能覆盖已有原始证据；普通GUI未放好前三件时也不能直接跳到first_batch=4。

## 明天前的停止边界

本轮工程问题已有通过证据，不再增加接触控制、模型/摩擦修改或放宽门限来“保证成功”。仍需用户确认基准冻结清单：实际有效摩擦0.5/0.5与旧文档0.90/0.75不一致；隐藏旧手爪质量影响接触力；原D004前三件双吸盘后推/侧向约束协议仍不能由旧串行demo证明。需要模型/接触方法改变时必须另开明确批准的迭代。36 nulls/YAML原hash不变，TASK01不PASS/FROZEN，TASK02不开始。

先前较快第四件漂移FAIL、慢速第五件IK安全停机、只读探针错误输入FAIL均保留。不同随机构型/速度的少量PASS不能证明可靠性或“测得关节起点”是唯一因果；备用物理触发也尚未覆盖。

## POST-TASK REPORT

- Task: TASK01, approved Cube04 variant / released empty retreat reliability.
- Status: PARTIAL overall; engineering basic/long FK-FCL + isolated fifth + fourth/fifth continuous physical PASS.
- Completed: live measured dual-arm start, fresh released-Cube strict FCL, bounded continuous-seed fallback reusing fine IK, guard tests/real-model negative regression, two fresh physical fixtures, complete records/source pins.
- Files changed: legacy `task26_truck_box_push_in.cpp` macro branch, `empty_retreat_policy.hpp`, `task01_empty_retreat_probe.cpp`, CMake; reproduction generalized physical fixture/analyzer/unit test, report/six records/three run metadata+physical summaries. No old scene/model/ACM/material or protected-directory modification.
- Commands/tests: colcon57.2s final all-target build PASS; probe-only rebuild PASS; pure C++ guard PASS; Python19/19 PASS; real-model basic/long replay exit0; actual isolated and continuous controllers exit0. Draft analytic PASS/36nulls/unchangedhash, syntax/diff PASS.
- Key metrics: fourth0.375mm neighbor/0.244mm deepgap, fifth0.530mm error/0.476mm deepgap; isolated fifth0.540mm error. 7,778+4,691 valid sparse samples; no sampler errors; MoveIt teardown-11 separately retained.
- [ORIGINAL]: no paper algorithm begun. [ADAPTATION]: user-approved fourth rear-only precision contact protocol inherited unchanged. [ENGINEERING]: live seeds/local IK/FCL/tests/logging. [DEVIATION]: no new exception beyond recorded D014 fourth change; legacy first-three D004 mismatch remains unresolved. [EXPERIMENTAL]: preplaced shortened fixtures, rounded-seed read-only replay, uncontrolled OMPL trials.
- Records: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK all updated.
- Open risks: small unseeded sample, USD motion-time channel (Task27 rotation fix already retained), material/mass/contact-wrench ambiguity, first-three D004, teardown, numerical freeze review. Fallback physically not triggered. No full-five-new-variant/reliability/force-control claim.
- Recommended next: user model/freeze/contact review before paper methods; any next engineering repeat must retain separate fresh-scene raw evidence and old gates.
- Git: legacy `task01-runtime-fixes` / `3ee42d2`; reproduced records `task01-benchmark-draft` (final commit in branch history). Raw ignored/local; summaries tracked. All owned runtimes stopped; pre-existing untracked legacy files preserved.
