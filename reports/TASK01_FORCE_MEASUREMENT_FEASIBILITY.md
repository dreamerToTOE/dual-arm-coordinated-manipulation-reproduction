# TASK01 力测量可行性与独立校准（2026-10-03）

状态：**碰撞接触测量与独立安装座反力校准通过；FR3 TCP 接触 wrench 尚未完成标定。TASK01 仍为 IN_PROGRESS。**

## 本轮范围

- [ENGINEERING] 同一物理步读取碰撞法向冲量、摩擦冲量、接触点，并重建指定刚体原点处的 wrench；8 个离线单元测试。
- [ADAPTATION] Isaac 4.5 PhysX 的接触冲量按真实物理步长转换成 N，世界坐标、Nm、仿真时间和步号显式记录。
- [EXPERIMENTAL] 已知质量/外力/外力矩的独立校准场景，以及一个独立关节安装座。均不是论文方法。
- 未改旧 Task27 控制、质量/几何/ACM、Surface Gripper 参数或 benchmark 草案；未新增 FR3 测力关节，也未实现力控。

## 必须区分的三种信号

| 信号 | 本轮证据 | 可以说明什么 | 不能说明什么 |
|---|---|---|---|
| PhysX 碰撞接触 wrench | 支撑、摩擦、已知力矩、旋转墙面校准 PASS | 指定 Cube 与桌面/墙/其他 Cube 的碰撞法向和摩擦作用 | Surface Gripper D6 吸附约束反力、左右内力 |
| Articulation 六维 incoming joint reaction | 独立安装座悬挂 0.8 kg 校准 PASS | 安装关节反力能包含吸盘传回的载荷 | 未补偿的 FR3 读数就是 TCP 接触力 |
| 旧 ROS JointState.effort | 仍为原接口 | 各自由度驱动/反力矩诊断 | 完整的末端六维 wrench |

双吸盘实际悬空保持 Cube 高度 0.500 m、两约束 CLOSED，但碰撞接口读数为 **0 N**。这不是吸盘没有力，而是普通碰撞接口不包含 D6 约束作用。不能用这种零信号证明 P2 的 internal wrench 为零。

## 接触重建及独立校准

接口为本机 Isaac 4.5 `omni.physics.tensors` 的 `create_rigid_contact_view`、`get_contact_data(dt)`、`get_friction_data(dt)`。法向 force matrix **不包含摩擦**；必须单独读取摩擦锚点。两次调用可能复用 count/start 缓冲，立即复制后再计算。

```text
F_world = Σ(normal_scalar × normal_direction) + Σ(friction_vector)
τ_world_about_body_origin = Σ((contact_point - body_origin) × contact_force)
力 = 接触冲量 / 实际 physics_dt；不是默认 dt=1 的冲量数值
```

参考点明确是采样刚体原点，不暗中假设任意模型的原点等于质心/TCP。采样器拒绝失效 view、非有限数据、错误路径顺序、缺少同一步原点和越界缓冲。

校准体边长 0.12 m、质量 0.8 kg、重力 9.81 m/s²。静/动摩擦 0.8/0.6，仅用于已知载荷校准，不改 Task27。校准 gate 在试验前固定：力平衡误差 ≤0.05 N、已知力矩平衡误差 ≤0.001 Nm，另检验零接触、同一步时间、CLOSED、悬空高度和 stabilization 不被测量接口更改。

| 项目 | 60 Hz 物理、墙 yaw=0° | 120 Hz 物理、墙 yaw=30° |
|---|---:|---:|
| 桌面平均支撑 Z 力 | 7.84800024 N | 7.84799969 N |
| 抵消外加 +X 2 N 的摩擦 X 力 | −1.99999991 N | −2.00000003 N |
| 抵消外加 +Z 0.04 Nm 的力矩 Z | −0.03996668 Nm | −0.03998334 Nm |
| 已知触墙 4 N 的平均力 `(Fx,Fy)` | `(−4.000000, 0)` N | `(−3.464101, −2.000000)` N |
| 双吸盘承重时碰撞力 | 0 N | 0 N |
| 各主测量阶段样本 | 60 | 120 |
| 所有 13 项校准检查 | PASS | PASS |

两个物理步长下测得同样的 N/Nm 量级，旋转墙面的 XY 分量符合世界坐标解析方向。不是只在一个默认步长上碰巧读对。

对应原始数据和 summary：

- `results/20261003_TASK01_contact_force_60hz_torque/`
- `results/20261003_TASK01_contact_force_120hz_yaw30/`
- 较早 60 Hz 不带非零力矩阶段的成功试验保留为 `contact_force_60hz_v3`，不把它计成力矩标定证据。

## 安装座反力、方向和参考点识别

独立试验用固定基座 + 一自由度高刚度安装座 + 侧吸 D6，不改 FR3。先空载采样，再打开载荷重力、悬挂 0.8 kg，比较相同静止位姿下的加载增量。载荷中心距安装座原点 0.160 m，解析增量为世界 `Fz=7.848 N, τy=−1.255680 Nm`。

- 安装座 roll=0°：加载增量 Z 力 `7.848000407 N`，Y 力矩 `−1.255679830 Nm`。
- roll=90°：加载增量局部 Y 力 `7.848002005 N`，局部 Z 力矩 `1.255679846 Nm`。这排除了“原始分量始终在 world”的解释。
- 前两个试验中 link 原点、质心、joint anchor 以及 link/joint axes 重合，**不能据此分辨坐标和力矩参考点**。早期非零 COM 的缩放刚体试验也存在已知模型错误：body scale 同时缩放了 authored COM/joint anchor；该试验的原点识别结论作废，原始数据保留。
- 最终使用**无刚体缩放**夹具（Cube 的 `size` 定义尺寸），明确验证 physics view 的 COM 确为 **5 mm**，主惯性轴 roll **45°**，joint child anchor X **3 mm**、joint frame roll **30°**。九种解释中仅 **joint axes / about joint anchor** 满足相同 gate；力/力矩误差约 `3.436e−6 N / 4.430e−7 Nm`。错误用 link 原点会差 `0.023544 Nm`，错误用 COM 会差 `0.015696 Nm`；错误用 link axes 会差约 `4.0624 N`。

**因此必须用 inbound joint 的坐标和 anchor，不可直接使用 link 坐标和 link 原点。** 最终夹具中的 joint axes 为父/子端对齐的轴，单个固定安装座已验证；并不自动验证每一种转动关节的 native-axis 约定。FR3 link8 的固定入关节仍需读取其实际 localRot/localPos 和空载补偿。

这提供的是本机该 API 的静态参考点/方向识别，不是运动中 FR3 的补偿算法验证。独立安装座的 stiffness/damping 是校准夹具设置，不会写入 benchmark。

运行记录：`results/20261003_TASK01_mount_reaction_identity/`、`mount_reaction_roll90/`、`mount_joint_reference_unscaled/`。`mount_reference_identity` 与 `mount_joint_reference` 的刚体缩放混淆保留在 metadata 中，不能计为参考点识别成功。

## 实际 FR3 接口审计与仍缺的工作

新只读五件探针读取真实 physics articulation 拓扑，确认两臂都有 `fr3_link8`（index=8）可供采样；六维反力与 Cube/碰撞数据共享物理步快照。TCP 由实际 PhysX link8 位姿和旧场景固定工具变换计算，车厢入口暂存为候选坐标定义，不宣称已发布/冻结 ROS TF。

一个重要的现有模型事实：隐藏原 hand/finger 的 visual/collision 后，相关刚体质量**并没有消失**。当前 link8 及其后续 hand/finger/hand_tcp 支路的总质量约 **1.946277 kg**，解析静态支撑约 **19.092980 N**。首个未加载快照按 link 姿态作临时旋转的读数约 19.10 N，仅为量级诊断：实际 joint frame/anchor 尚未核验，不能称已校准 world wrench。直接把 link8 反力当吸盘载荷会严重误报；本轮没有删除这些质量或改模型。

后续 FR3 接触估计器需要：

1. 明确支路所有质量/质心/惯性与实际关节拓扑（含 inbound fixed joint frame），去除空载重力及运动惯性贡献。
2. 从关节反力转换作用方向，并将力矩由 incoming joint anchor 平移到 TCP；平移不能只旋转六维分量。
3. 做已知单侧载荷/双侧载荷/不同姿态/运动状态校准，确认实际误差和带宽。
4. 再定义左右 contact wrench、external/internal 分解和 benchmark force gates。

独立夹具空载相减只解决一个静态姿态，不能冒充这四项已经完成。也不能从“总支撑正确”推出双吸盘分担一定各半。

官方 [PhysX Joint Force Reporting](https://nvidia-omniverse.github.io/PhysX/physx/5.4.0/docs/Joints.html) 提供 C++ 约束反力读取概念，但本机 4.5 Surface_Gripper Python 对象公开方法只有 `initialize/close/open/update/is_closed/is_attempting_close`，没有直接 wrench getter；C++ API 存在不等于当前 Isaac Python 桥已暴露。另直接核查本机 tensor 源码及 SingleArticulation 测量实现，没有套用 Isaac 6.0 文档接口。

## 失败与边界

- 首次用了不存在的 `PhysicsContext.get_physics_scene_prim()`，后改为 4.5 的 `get_current_physics_scene_prim()`。异常后的慢关闭还出现段错误，保留失败摘要与日志，不计成功。
- 第二次把 RigidPrim 的 `reset_xform_properties` 参数误传给 SingleRigidPrim；修正真实构造器后才运行成功。
- 完整场景只读探针先后因不存在的 `STATE_READY`、将场景字典覆盖后读取场景常量失败；两次均在机器人命令前停止。分别修复为原 Bridge 的 ARRIVED 与保存独立场景参数字典。
- Isaac fast shutdown 在部分异常路径仍返回 0：必须看 `failure.json`/完整 checks，不以退出码单独判 PASS。
- 非零 COM 的早期安装座使用 `scale=0.02`，真实 COM/anchor 随刚体缩放，不能与未经缩放的预期位置比较；又因 joint/link frame 重合，不能识别 joint frame。最终改独立夹具尺寸表达、核验真实 COM 并同时区分九种解释，才获得上面的 joint-frame/anchor 结论。没有改 benchmark 刚体或放宽任何 gate。
- 独立安装座没有 FR3 的惯性/重力补偿、实际控制延迟、左右相互内力或论文算法。碰撞校准也不代表所有实际接触条件/冲击峰值已标定。

## 完整复现命令

60 Hz 接触校准（终端无需 source ROS；launcher 清除继承的系统 ROS 路径）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_contact_force_probe.py \
  --output-dir results/manual_TASK01_force_60hz/raw
```

120 Hz + 旋转墙面校准：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_contact_force_probe.py \
  --physics-dt 0.008333333333333333 --wall-yaw-deg 30 \
  --output-dir results/manual_TASK01_force_120hz/raw
```

安装座方向与参考点识别：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_mount_reaction_probe.py \
  --roll-deg 90 --tool-com-x 0.005 --principal-roll-deg 45 \
  --joint-child-anchor-x 0.003 --joint-roll-deg 30 \
  --output-dir results/manual_TASK01_mount_reference/raw

python3 platforms/isaac_ros2/probes/test_physics_contact_sampler.py
```

不要在有用户 GUI 仿真运行时额外启动大量 Isaac 实例；本次测试使用独立 headless 小场景，运行结束退出。

完整五件物理探针在第二件吸附前 FAIL，结果单独记录在 `reports/TASK01_FULL_FIXTURE_CONTACT_PROBE.md`，不与此处的测量校准 PASS 合并成 TASK01/论文 PASS。
