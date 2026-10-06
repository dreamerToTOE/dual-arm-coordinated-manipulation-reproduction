# TASK01 — 正常播放倍率与可见GUI运行

2026-10-06。运行设置/软件检查完成；正常倍率物理验收未完成。

## === PRE-TASK REPORT ===

- Task: TASK01运行配置与用户工作流要求。
- Goal: 恢复按规划时间正常播放，后续让用户看到Isaac场景。
- Paper method understood as: 不实现P2/P3，不改变已批准前三双吸主从/后两精准单推协议。
- Scope: 只改新独立节点默认播放倍率，保存GUI-only要求及上一轮最终负结果。
- Files expected to change: runtime共享源码的Task01条件分支、README、STARTUP_GUIDE；本仓库六记录、AGENTS、Task01状态、报告及结果metadata。
- Validation plan: 当前执行节点串行build；61Python与两组C++策略检查；错误倍率无命令拒绝；原场景/Bridge/YAML hash不变。
- Known ambiguities / risks: 正常倍率不是100%关节上限；原反馈新鲜度故障仍OPEN；慢速PASS不可替代新倍率物理验收。
- Need user confirmation: no（按用户新请求调整播放与GUI方式）；若需100%关节上限或改原物理/门限则另行确认。

## 速度核对及实际修改

执行器路径时间为`wall_elapsed / execution_time_scale`。因此`1.0`是100%规划轨迹
播放，`2.0`是50%，此前实际`5.0`是20%；此前代码默认`3.0`约33.3%。
当前`task01_dual_suction_fixture`默认改为`1.0`，启动日志明确输出百分比，并在
任何Arm/命令前拒绝非有限或小于1的倍率。旧Task26/27节点的默认3.0保持。

MoveIt RRT速度/加速度限制仍为`0.12`，这是规划时间参数化的另一个设置。
Cartesian/接触轨迹还有其既有计时规则，因此不能把所有动作统一称为12%关节
极限速度，也不能把正常播放称为100%硬件速度。本轮没有把它们改成1.0。
显式历史`-p execution_time_scale:=5.0`会覆盖新默认值，后续命令使用1.0。

## GUI加载步骤（不要省略）

后续只用可见Isaac Sim 4.5 GUI，不再启动headless。新开GUI后，停止Timeline，
在Script Editor执行原场景入口：

```python
exec(open('/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/isaac/scripts/task27_five_cube_center_insert_scene.py', encoding='utf-8').read())
```

点击Play，等待机器人初始化，再加载原物理Bridge：

```python
exec(open('/home/ubuntu2004/lmy/dual-arm-embodied-palletizing/isaac/scripts/task27_five_cube_center_insert_bridge.py', encoding='utf-8').read())
```

然后加载新Task01需要的同物理步Cube+双TCP反馈：

```python
exec(open('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/probes/task01_fixture_geometry_bridge.py', encoding='utf-8').read())
```

正常倍率参数为`-p execution_time_scale:=1.0`。本轮没有自动启动物理任务；先前
反馈过期/无效缺陷仍存在，下一轮应在GUI中观察、记录并诊断，不能宣称已交付
完整五件稳定版。GUI的场景/Bridge与ROS终端应沿用同一ROS域及localhost设置。

## 上一轮最终结果（不篡改历史速度）

`results/20261006_TASK01_empty_handoff_full01`，源码f237cff，production SHA
812c71eeab695c02d992ce4c16569c951e390a296b8429d655ef40bdc1ab9ef3。
第一件X1–15双CLOSED通过；X16在执行中互锁反馈`STALE_OR_INVALID`，raw关节
峰值20.627/30.965Nm低于80Nm。安全双OPEN、controller1、completed[]，后续件
没有命令。自有headless受控SIGINT后正常exit0，用户新要求后没有重启它。

17条日志几何精确匹配物理stamp，舍入差最大0.000491944mm/deg；5862held、
21398atomic、3566sparse记录完整性零错误。记录完整并不能证明ROS消费及时；
缺陷来源未隔离，原250ms门禁不放宽。新空载handoff代码未实际触发，不叫物理PASS。

## === POST-TASK REPORT ===

- Task: TASK01正常播放/GUI-only。
- Status: PASS（设置与软件检查）；PARTIAL（Task01整体及新速度物理验收）。
- Completed: 新节点默认1.0、速度语义日志与输入守卫；GUI工作流和历史FAIL终局归档。
- Files changed: runtime三个文件；本仓库AGENTS/README、六记录、Task01任务、两报告、结果metadata与三份已生成诊断summary。
- Commands run:
  - `colcon build --packages-select fr3_dual_palletize --symlink-install --parallel-workers 1 --cmake-target task01_dual_suction_fixture`
  - `python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py'`
  - `g++ -std=c++17 -Wall -Wextra -Werror -I /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_palletize/include`分别编译`test_dual_fixture_policy.cpp`和`test_empty_retreat_policy.cpp`并执行。
  - 在source ROS/workspace后：`ros2 run fr3_dual_palletize task01_dual_suction_fixture --ros-args -p execution_time_scale:=0.5`。
  - `python3 scripts/validate_benchmark_candidate.py configs/benchmark/benchmark_v1.yaml`；`sha256sum`及`git diff --check`。
- Tests / experiment results: build57.3s/exit0；61Python和两组C++ PASS；倍率0.5在模型/Arm/命令前按预期exit1；无新GUI/headless物理动作。分析检查器初次误传`--help`导致路径不存在exit1，改传实际YAML后exit0，保留错误说明而不算物理故障。
- Key metrics: 默认100%规划播放；生产binary SHA `08f3060ac4d710b5580fad5023ba16bb718df0bfc5505de175bdbcc7a49bd31e`；新倍率物理误差/成功率未测。
- Paper fidelity: [ORIGINAL]无；[ADAPTATION]既有3+2协议不变；[ENGINEERING]播放默认/日志/守卫/GUI工作流；[DEVIATION]无论文方法改动；[EXPERIMENTAL]新速度待GUI验收，不借旧慢速数据证明。
- Records updated: STATUS、WORKLOG、EXPERIMENT_LOG、BUGS（BUG023 OPEN）、DECISIONS（D028）、USER_FEEDBACK。
- Open risks: 原子反馈过期/无效根因未隔离；原USD/URDF碰撞模型差异与接触问题；高速跟踪/保护可能触发；GUI下完整五件未通过。
- Recommended next step: 只在可见GUI中首先诊断反馈及时性，保留原所有保护；确认后重新测正常倍率单件/完整五件。TASK01仍IN_PROGRESS/DRAFT/36nulls，TASK02 TODO。
- Git branch / commit / dirty files: runtime `task01-runtime-fixes` / `6bc24ec`；记录在`task01-benchmark-draft`提交，未纳入generated build/install/raw或用户无关文件。

未修改的原场景SHA43aa7c2e…，原Bridge SHA0f712365…；benchmark SHA
a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8，36nulls保持。
