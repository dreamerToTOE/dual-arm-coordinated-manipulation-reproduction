# TASK01 — 杯面中心/法向不变的腕部转角

2026-10-06。[ENGINEERING]/[EXPERIMENTAL]，不是P2/P3控制器；TASK01 IN_PROGRESS。

## === PRE-TASK REPORT ===

- Task: TASK01 / BUG017、019。
- Goal: 避开已记录的原Isaac link7深墙实体接触，不移动墙/吸点、不改L结构。
- Paper method understood as: 没有实现论文算法；只做3+2已批准工程接触流程的姿态可行性。
- Scope of this iteration: 前三件side helper在OPEN接近/重抓时绕原杯面法向旋转，之后双吸附X/Y保持该姿态；后两件/原双臂搬运/原物理/ACM/80Nm/几何门限不变。
- Files expected to change: runtime独立include/probe/policy与主程序条件编译参数检查；本仓只读FK/hull审计/单测、报告、六记录/results。
- Validation plan: 原点/法向不变检查→真实RobotModel名义3链IK/FCL/相对姿态→原USD convexHull离线检查→编译/参数负向检查→新鲜普通供料首件scale5/hold0/原门限/同一步接触验证。未通过不得交付为5件PASS。
- Known ambiguities / risks: 原URDF/NVIDIAmesh不同；离线凸包不等于PhysX cooked hull/contact offsets；6.77mm轴向名义余量不是动态跟踪保证；IK RNG未控制；首件不能证明后两件/可靠性/benchmark冻结。
- Need user confirmation: no，只调整工作姿态、保留吸点/法向/场景/模型；若必须改变这些或论文/物理参数则停止另问。

## 只读证据与参数来源

诊断02的精确joint replay排除主要坐标偏移（max FK差0.000872mm），left link7与深墙有实测接触、同姿态MoveIt墙检查自由。原NVIDIA asset是convexHull collider，URDF用另一STL；原数据/模型未改。官方文档说明[Mesh collider approximation](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/dev_guide/rigid_bodies_articulations/collision.html)，但具体资产与接触结果以本机hash/实测记录为准，不从最新版文档推定4.5 cooked参数。

转角worldY=-15deg，杯面TCP+X仍为世界+/-Y，故点和法向不变、四杯阵列只在面内旋转。不是把杯面偏离Cube，也不是改L杆或侧边缘抓取；侧面中心仍是原120mm cube中心。

`nominal01` /0cfdbaf名义3链PASS，stdout/rosout穿插污染记录导致hull分析FAIL，保留。`nominal02` /c13ea40独立不覆盖文件，3/3名义contact/X/Y/释放退出链PASS，1330腕部FK节点、原USD凸包与深墙0重叠，最小X平面余量6.766308mm；relativeTCP约0.003mm/0.001deg。53Python、probe build51.2s PASS。全部无joint/suction/feed/rail/Scene/ACM写，不等于物理PASS。

## Commands

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
CMAKE_BUILD_PARALLEL_LEVEL=2 colcon build --packages-select fr3_dual_palletize --symlink-install --parallel-workers 1 --cmake-target task01_dual_fixture_probe
ros2 run fr3_dual_palletize task01_dual_fixture_probe --ros-args \
  -p side_roll_world_y_deg:=-15.0 \
  -p wrist_audit_path:=/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/results/20261006_TASK01_cup_roll_nominal02/raw/wrist_fk.tsv
```

探针不得覆盖已有TSV，需每次选新run目录。几何与只读重放：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 platforms/isaac_ros2/probes/audit_held_hull.py \
  results/20261006_TASK01_cup_roll_nominal02/raw/wrist_fk.tsv \
  results/20261006_TASK01_held_fixture_diagnostic02/raw/asset_link7.json
# 在ROS2/工程环境已source的终端，只调用服务，无写入：
python3 platforms/isaac_ros2/probes/task01_held_moveit_replay.py \
  results/20261006_TASK01_held_fixture_diagnostic02/raw/held_contact_samples.jsonl \
  --steps 19627 19753 21051 --rail-shift-x 0.1
python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py'
python3 scripts/validate_benchmark_candidate.py
```

## 物理复测准备

执行器尚待引入同一转角函数/参数与编译。仅前三件side helper在OPEN重抓时应用；已吸附后不旋转、不更换grasp。后两件精准单rear与双臂搬运不变。first1/max1/scale5/hold0/zero-preplaced新鲜本机headless结果待填写，无新物理PASS。
