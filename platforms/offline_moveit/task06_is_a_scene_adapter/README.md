# TASK06-IS-A 只读场景薄适配器

## 第二阶段当前交付（D058/D059）

**无执行规划适配初步验收通过，停止待审查**；
见[报告/完整端点/路径](../../../reports/TASK06_IS_A_NOMINAL_SCENE02.md)。
新独立v2世界读取旧Task26 .628m原六对象，未覆盖.606m历史归档。
`nominal_inputs.py`复用原source audit核对静态来源、完整模型和持件名义阶段；
`nominal_planning.cpp`直接原KDL-LMA后端构造两个完整14q，再调用原C/Jc/NR/RBS/P4。
TASK05包装器仅增加可选来源world对象/附着ID与native World readback，默认行为回归通过。
`scripts/run_task06_is_a_nominal_offline.py`锁定20fe06d协议，用原TASK02日志保留失败与全证据。
唯一科学进程seed7成功、1869点独立合格；不是时间轨迹/实际持件/物理执行。
原软件/原阈值/原scene/bridge/控制器/Benchmark不改，无ROS Node或执行接口。
15接口测试、72TASK02、4/4数学目标通过；提交后不自动运行B/C/TASK07或重跑科学实验。

## 第一阶段历史交付（保留，不回判）

当前状态：**部分完成，停止等待审查**。源码/归档 Y 不匹配且实际持件端点缺失。
新接口已编译，8项数据测试通过；不能用于机器人执行，不代表已有合格路径。
完整来源/坐标/限制与证据见 [交付报告](../../../reports/TASK06_IS_A_SCENE_ADAPTER01.md)。

- `source_audit.py`：读取固定 Task26 文本和原快照，不导入/运行旧 Isaac 文件。
  旧世界/模型一致门禁先于任何 native 模型加载或规划。
- `native_audit.cpp`：直接复用 TASK03 模型、TASK05 FCL 和 TASK06 搜索接口。
  当前完整端点未批准，规划 wrapper 只编译不调用。来源运行提前停止，native
  程序本轮未执行。编译时使用原 CMake 目标，不拷贝算法。
- `scripts/run_task06_is_a_offline.py` 锁定先提交的工程协议，拒绝事后修改；
  缺少端点不求 IK、不修构型、不装载其他世界或通过扩大 ACM 获得路径。

原 TASK03–06 核心、模型、原结果、旧 Task26、Benchmark 都没有修改。
不新增 ROS 节点/MoveGroup、scene/bridge/Surface Gripper/导轨/执行器。
没有碰撞结果、路径、时间轨迹或物理安全结论可供下发。

已完成的软件检查命令（仅用于复现源码构建/合成检查，不授权重新做科学运行）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
timeout 60s cmake -S platforms/offline_moveit/task06_is_a_scene_adapter \
  -B build/task06_is_a_scene_adapter -DCMAKE_BUILD_TYPE=Release
timeout 240s cmake --build build/task06_is_a_scene_adapter --parallel 2
PYTHONPATH="${PWD}:${PYTHONPATH}" timeout 60s /usr/bin/python3 -m unittest discover \
  -s tests -p 'test_task06_is_a_scene_adapter.py' -v
PYTHONPATH="${PWD}:${PYTHONPATH}" timeout 60s /usr/bin/python3 -m unittest discover \
  -s tests -p 'test_task02*.py' -v
timeout 60s ctest --test-dir build/task06_is_a_scene_adapter --output-on-failure
```

本輪科学源门禁已有一次失败证据；不要重新运行它或 native_audit 来绕过停止。
来源输入/端点补充需要用户审查，不自动进入 TASK06-IS-B/C 或 TASK07。
