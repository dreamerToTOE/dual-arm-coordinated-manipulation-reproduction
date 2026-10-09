# TASK02-C — 平台无关指标草案

纯 Python 标准库；不安装、不导入、不调用 Isaac、MuJoCo、ROS、MoveIt 或 FCL。
只计算指标，不产生命令、不判断 SUCCESS、不冻结 Benchmark。

## 复用定义

数学基准是旧仓库 `631b1f65656d025c1bb2173e874192f3fe4d355a` 的
`ros_ws/src/fr3_dual_palletize/src/task14_shared_box_geometry_monitor.cpp`：
位置定义见224–237行，max/RMS见148–151行，四元数角度见50–66行。
对应旧 TASK14 文档的连续几何目的保持不变；旧3mm、5mm、2°、30ms只属历史验收，
**不是本模块默认值**。Task16的显式seed/trial/文件证据组织通过已存在TASK02-B复用。

对同一frame中的实际物体和双TCP，令首个有效样本为0：

```text
r(t) = p_right(t) - p_left(t)
d(t) = p_object(t) - (p_left(t) + p_right(t))/2
relative_tcp_error(t) = norm(r(t) - r(0))
box_to_tcp_midpoint_error(t) = norm(d(t) - d(0))
orientation_error(t) = 2 acos(clamp(abs(dot(q(t),q(0)))/(norm(q(t))*norm(q(0))),0,1))
maximum = max(e_i)
RMS = sqrt(sum(e_i^2)/N)
```

Task14基线是**初始关系漂移**。固定的初始中点偏移/姿态偏移不会被此定义判为误差；
它不是物体坐标系中的SE(3)闭链残差、TCP相对姿态误差或姿态目标跟踪。
`q`和`-q`等价；输入无效四元数先拒绝，只有有效单位四元数的消息舍入参与角度计算。
max/RMS对有效样本等权，不是时间积分；不同采样密度对一般运动可改变RMS。

Benchmark A新增的**位置跟踪RMSE**独立定义为：

```text
e_position(t) = norm(p_actual(t) - p_desired(t))
object_position_rmse = sqrt(sum(e_position(t)^2)/N)
```

desired pose由调用者明确与测量对应；本模块不按索引擅自对齐轨迹时间、不插值、不重采样。
这项基础数学扩展不是旧Task14已实现的指标，也不是P1–P5控制律。

## Benchmark B

调用者显式给同frame中的轴原点`p0`、目标`p_target`和单位插入方向`a`。
目标沿轴的投影长度必须为正；横向基准线是`p0 + s*a`，不自动从目标推断轴。

```text
cube_target_position_error = norm(p_actual - p_target)
axial_displacement = dot(p_actual - p0, a)                 # m，有符号
axial_progress = axial_displacement / dot(p_target-p0,a)  # 无单位，不截断
lateral_deviation = norm((p_actual-p0) - axial_displacement*a)
orientation_deviation = quaternion_angle(q_actual,q_target)
```

回退可出现progress<0，超调可>1，均不自动宣告完成。末输入样本无效/缺失时，
`final_cube_target_position_error_m=null`，不能用之前幸存样本冒充最终目标误差。

`insertion_time_sec`只取**调用者明确截取的插入窗口**首末post-step仿真stamp之差；
不推断TARGET跨越、SUCTION事件或成功。FORMAL模式、同session、两个合格端点才能计算。
窗口端点缺失/无效/被拒绝时为null并给原因。内部缺样仍显式计数，不补零。
SYNTHETIC模式永远返回null；轨迹相对时间、wall time、旧异步快照均不能产生正式耗时。

## 时间、质量与接口

- `MetricContext`必须显式给frame、object、simulation_session、mode和`max_stamp_skew_ns`；
  没有默认30ms。后者只是数据对齐策略，不是Benchmark成功阈值。
- `EvaluationMode.FORMAL`要求声明SYNCHRONIZED_POST_STEP；SYNTHETIC模式只接受SYNTHETIC。
  两者不得混用。资格声明并非native真实性认证；本轮没有采集真实post-step数据。
- frame、钟域、session、资格或实体身份不一致拒绝整组输入并抛出带原因异常；
  时间/step倒退也拒绝，不能拼接reset后的序列。
- 缺失、invalid、post-step信息缺失、三通道stamp/step偏差、重复钟值逐样本记录原因。
  一个输入行最多计一次拒绝；`input_samples = valid_samples + rejected_samples`。
- 双TCP及Cube必须同physics_step；每个通道的stamp和step独立检查单调性。
  缺失/无效参考目标也明确拒绝。畸形数值、向量长度、四元数等在数据构造时抛错。
- 无有效样本时参考和汇总为null，不用0伪装零误差。
- 初始参考使用首个有效样本；完整参考pose、时间、输入索引随结果保存。
  不重新创建旧Task14的CLOSED窗口监听器；输入窗口由调用者负责。
- `TransportMetrics`/`InsertionMetrics`复用TASK02-B严格JSON envelope编解码。
  输出单位为m/rad/s；无`status`、`success`或默认评分门限。

```python
from common.metrics import evaluate_transport, evaluate_insertion

# samples/context均为显式数据；函数不会查询平台或执行命令。
a = evaluate_transport(transport_samples, context=context)
b = evaluate_insertion(object_samples, context=context,
                       axis_origin=origin, target=target, unit_axis=(1.0, 0.0, 0.0))
encoded = a.to_json()
```

完整可运行合成构造例子见[双适配器测试输入](../../tests/task02c_synthetic_inputs.py)。
dict/xyzw/ns和array/wxyz/sec两个独立解码器是test doubles，不是实时平台适配器。

## 测量草案

`common/interfaces/measurement.py`复用A的`Pose`及B的资格/时间/wire契约：

- `MeasurementInfo`：source、qualification、session/stamp/step、post-step标记、valid、
  invalid_reason、evidence_refs。合法格式不等于测量资格；已标legacy/synthetic来源不能升级。
- `PoseMeasurement`：实体身份、可用pose或None、测量信息。
- `ContactWrench`：on/by body、表达frame、force_N、torque_Nm、application_point_m。
  **力矩关于此显式作用点，所有向量与点均在同frame**；不默认TCP/COM，不做moment shift、
  力估计或重力惯性补偿。单位固定N、N*m、m。
- `CollisionDistance`：body pair、表达frame、signed_distance_m、两个最近/witness点。
  正/零/负表示间隙/边界/穿透，不判断失败；负距离的点遵循来源后端语义，不假定唯一
  或强制点距等于穿透深度。未查询时valid=false并保留None，不能补0。

两种契约只描述数据，无FCL查询器、PhysX传感器、力控器、后台采集或实时日志服务。

## 离线复现

```bash
python3 -m unittest discover -s tests -p 'test_task02*.py' -v
# 输出路径必须是尚不存在的文件，不覆盖已有证据：
PYTHONPATH=. python3 tests/task02c_synthetic_inputs.py --output /path/to/new_metrics.json
```

本轮实际输出见[报告](../../reports/TASK02_METRICS_MEASUREMENTS01.md)。
资格分支单测中的“declared post-step TEST_DOUBLE”只是合成代码分支覆盖，不能当科研测量。
TASK02-C PASS CANDIDATE，TASK02 IN_PROGRESS，BENCHMARK DRAFT / NOT FROZEN。
