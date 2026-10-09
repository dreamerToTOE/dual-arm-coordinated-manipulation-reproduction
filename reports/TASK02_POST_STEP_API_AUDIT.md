# TASK02-D — 本机 Isaac Sim 4.5 post-step API 审计

2026-10-09 · 软件基线 `36c95ab` · **PARTIAL / DEFERRED**

本轮仅静态读取安装包源码、头文件、绑定声明和测试源码。未启动 Isaac、ROS、
MoveIt、原 Task26；未 import simulator；未实现 Observer、未改旧 callback。
TASK02 保持 IN_PROGRESS，Benchmark DRAFT / NOT FROZEN。用户批准关闭此审计线，
缺口归属后续 Isaac 正式测量适配，不阻塞离线数学与规划算法复现。

## 本机版本与证据

安装根 `/home/ubuntu2004/isaacsim-4.5.0`，VERSION 为
`4.5.0-rc.36+release.19112.f59b3005.gl`，PhysX 扩展 `106.5.7`。
以下路径均相对安装根，行号以本轮本机文件为准；读取测试源码不等于运行测试。

| 接口/行为 | 本机证据 |
|---|---|
| 无 `IsaacEvents.POST_PHYSICS_STEP` | `exts/isaacsim.core.simulation_manager/isaacsim/core/simulation_manager/impl/isaac_events.py:15` |
| Manager `register_callback(callback, event)` 的 PHYSICS_STEP 注册旧接口 | 同扩展 `impl/simulation_manager.py:468,497` |
| 明确 `pre_step=False` 为步后回调 | `extsPhysics/omni.physx/omni/physx/bindings/_physx.pyi:1845` |
| explicit pre/post 顺序的安装包测试 | `extsPhysics/omni.physx.tests/omni/physxtests/tests/PhysxInterfaceSimulationEvents.py:101,157` |
| actual q → native DOF positions | `exts/isaacsim.core.prims/isaacsim/core/prims/impl/articulation.py:1518` |
| valid Cube handle → native transforms；invalid 会 fallback | 同扩展 `impl/rigid_prim.py:368` |
| native articulation root/base transforms；invalid 会 fallback | 同扩展 `impl/articulation.py:1887` |
| native link transform；直接设 q 后可能尚未更新 | `extsPhysics/omni.physics.tensors/omni/physics/tensors/impl/api.py:1185` |
| native simulation clock/count 声明 | `exts/isaacsim.core.nodes/include/CoreNodes.h:36` |
| 秒/Stop reset 语义 | 同扩展 `docs/ogn/OgnIsaacReadSimulationTime.rst:38` |
| native count 与 STOP 清零测试 | 同扩展 `isaacsim/core/nodes/tests/test_core_nodes.py:55` |
| USD transformation 写回是独立、受设置影响的步骤 | `_physx.pyi:1245,1907`；Manager `enable_fabric:338` |

## 能力与签名

```python
omni.physx.get_physx_interface() -> PhysX
PhysX.subscribe_physics_on_step_events(
    self, fn: Callable[[float], None], pre_step: bool, order: int
) -> carb.Subscription
```

`pre_step=False` 的 API 合同明确为 physics step 后；较小 order 先调用。
Manager PHYSICS_STEP 则只调用 `subscribe_physics_step_events(callback)`，其 phase
在安装包 Core 文档与旧 demo 注释中互相矛盾。不能声称旧 Task26 callback 已被认证
为 post-step，也不能反向断言它一定 pre-step。安装包 explicit-order 测试只检查旧
callback 被调用，没有证明它相对 explicit post callback 的位置。

```python
SingleArticulation.get_joint_positions(joint_indices=None)
RigidBodyView.get_transforms()
ArticulationView.get_root_transforms()
ArticulationView.get_link_transforms()
_isaacsim_core_nodes.acquire_interface().get_sim_time()
_isaacsim_core_nodes.acquire_interface().get_sim_time_monotonic()
_isaacsim_core_nodes.acquire_interface().get_physics_num_steps()
```

现有 Task26 已持有 initialized articulation 与 Cube rigid handles，可以原地复用。
q 必须按真实 joint identity 选择7+7，不能用 command target。Cube/base 只接受有效
physics-handle native 分支，拒绝 USD/Fabric fallback。native tensor quaternion为xyzw，
Core wrapper world pose转为wxyz，接 TASK02 xyzw 契约时须明确转换。

TCP 是非独立 rigid child；候选只能是 native link8 pose × 已有固定 link8→TCP
外参，标记派生来源，不冒充独立 native TCP measurement 或以 command FK代替。

## 仍不可认证

1. native CoreNodes clock/count 确实存在，不是 Python 累计dt；但本机分发没有提供
   其相对 explicit post callback 的更新实现/顺序证明。不能认证读数精确标识刚结束
   的同一个 solver step，不自行+dt或+1。SimulationContext current_time/step本身是
   累计dt/计数（simulation_context.py:1360），不得替代原生时间证据。
2. 未找到原生唯一 session/reset epoch。STOP/stage事件只能支持软件管理分段；
   若旧流程直接 teleport/reset 未发这些事件，不能默认覆盖全部reset。
3. post-step 不保证所有 USD world transforms 已写回。旧 `_pose()` 的 USD取数和
   ROS `get_clock().now()` 不能靠统一标签升级为原生同步样本。
4. 有效 native getter 能力不等于旧控制 callback中的setter与观察时序已认证。
   同次回调读完字段或前后count不变，也不是clock更新相位的证明。

因此：**API AVAILABILITY VERIFIED；科学同步采样资格 PARTIAL / DEFERRED**。
这些缺口不否定原 Task26 工程执行证据；它们限制正式测量资格。

## 最小独立 Observer 方案（仅候选，不实现）

独立 `pre_step=False` 订阅，不替换/重排原 callback；复用现有有效 native handles，
复制q、Cube/base/link，明确固定外参派生TCP，读取native clock/count；拒绝无效handle、
USDfallback、未知reset和未证明的时间绑定。软件session元数据诚实标注为管理身份。
在当前证据下只能保持诊断/未认证资格，不可接入正式科研时间序列。

本用户授权止于记录并 DEFER：不实现Observer，不运行新同步探针，不继续此工程线。

## 文件身份（SHA256）

```text
isaac_events.py
396eca28dd30aaaed2c82c9f30fa9754c92e65110157402fcef41f610ab8af44
simulation_manager.py
97d1ef88202f370eac00281b193581ba02b5c95ed64131f153c006e3ab104357
_physx.pyi
b75b94176c7e6b766bf6f36058d2115016eaabc0d45d8b36a28c64cbf29f4dd9
CoreNodes.h
9fe6adfa653bb657741a5aa6dabc3538307e82ea96bc3dee4af285807b70b1e1
```

## POST-TASK REPORT

Task: TASK02-D local post-step API audit

Status: PARTIAL / DEFERRED; TASK02 IN_PROGRESS; Benchmark DRAFT / NOT FROZEN.
Minimum sufficient evidence: yes for API availability, no for native synchronized snapshot.
Attempt budget: one authorized local availability audit; implementation/runtime0.
TASK-BLOCKING for TASK03 offline math: none.
DEFERRED: native stamp/step phase binding, reset identity and actual adapter qualification.
KNOWN LIMITATION: explicit callback contract does not certify USD export or old callback order.
LEGACY: asynchronous Task26 diagnostics remain unchanged.
Paper fidelity: [ENGINEERING] API audit only; no paper algorithm/physics change.
Next: user separately authorizes TASK03 math; stop this engineering research line.
