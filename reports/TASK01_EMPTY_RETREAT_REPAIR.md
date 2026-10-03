# TASK01 — 空载退出构型连续性修复

2026-10-03；状态：PARTIAL，工程实现/编译通过，物理验证待运行。

## PRE-TASK REPORT

- Task: TASK01 / Cube04 precision variant, Cube05 empty retreat reliability.
- Goal: 修复释放后 Cartesian IK 换支 / 命令终点非实测起点的问题，不改接触协议。
- Paper method understood as: TASK01 仍是基准准备；P2/P3 方法尚未开始。原 D004 前三件协议仍未实现，第四件例外已由用户批准。
- Scope: 实测空载起点、局部 seed 延拓备用路径、包含已释放 Cube 的完整同步 FCL、只读回归、真实 PhysX 试验。
- Files expected to change: 旧工程共享执行器的独立宏分支/新增策略头/只读探针/CMake；本仓测试探针、报告、六份记录和结果。
- Validation plan: 策略单测 → colcon 完成 → 真 RobotModel 只读 FK/FCL → 独立 Cube05 → Cube04/05 连续实测。
- Known risks: IK 极限/起点真实碰撞可能无法工程修复；旧 Bridge 姿态/时序缺陷仍存在；Cube04 单次 PASS 非稳定性。
- Need user confirmation: no，当前只是 ENGINEERING；如需要改模型/物理/接触/门限则停止。

## 实现与边界

上游用户工程 https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，修改前 `7be3659`，分支 `task01-runtime-fixes`；根未声明统一许可证。继续使用独立 `task01_cube04_precision_insert`，旧 Task26/27 默认路线不变。

已释放后，确认双杯 OPEN，读取同一 MoveIt RobotState 的左右实测关节，等待新 Cube Ground Truth。退出仍使用原目标；普通 Cartesian 候选失真时，在每个 ≤2 mm 小段上复用已有精细数值 IK，以上一段构型作下一段 seed。原局部 4 mm / 0.08 rad / 5 µm 求解界限不变；不将全部内部 0.1 mm 迭代点作为 30 ms 命令点，避免人为放慢20倍。

候选仍需原 5 mm FK 直线门限、关节极限、同步完整 FCL。当前已释放 Cube 以最新原 Bridge pose 加入校验世界，不扩大 ACM、不去除当前 Cube。不声称旧 scaled-USD quaternion 已成为正确动态物理姿态。

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
