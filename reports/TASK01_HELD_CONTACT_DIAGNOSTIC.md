# TASK01 — 持件双吸附推压诊断

日期：2026-10-06。Status: IN_PROGRESS；BUG-017仍OPEN，不是新版五件通过。

## 网络恢复后的第二次启动（进行中）

同日后续S3直连/代理HEAD均HTTP200，原资产Content-Length17462793；runtime正常push已成功。保留下面startup01失败，不将瞬时网络故障视为永久阻塞。新鲜原场景 `results/20261006_TASK01_held_fixture_diagnostic02/` 重新启动，真实采样与首件结果待验证；尚未替换资产或发送controller命令。下方startup01的POST是该失败尝试的checkpoint，不是第二次启动的结果。

## PRE-TASK REPORT

- Task: TASK01，诊断新3+2协议首件Y15保护停止。
- Goal: 同一PhysX post-step记录Cube/工具/机器人状态、接触对、raw DOF effort，区分接触/跟踪/闭环负载。
- Paper method understood as: [ENGINEERING] 数据采集/[EXPERIMENTAL] 原场景首件复测；P2内部力/P3力位混合未实现，不将本轮视为论文控制器。
- Scope: 独立新节点阶段标签+可选持件只读诊断；旧场景/工具/质量/摩擦/吸盘/ACM/80Nm/几何门限和后两件逻辑不变。
- Files expected to change: runtime task01_dual_fixture_impl.inc；本仓release_diagnostics接口、held_fixture_diagnostics、contact sampler压缩选项、headless runner、测试、分析器、六记录及结果。
- Validation plan: 无Isaac依赖负向单测→编译→诊断启动有效句柄/DOF映射→本机headless首件普通供料→同一步记录完整性/接触对/原门限检查→证据决定工程修正或停工申请范围。
- Known ambiguities / risks: 阶段标签异步到达；raw projected DOF force不是TCP wrench；碰撞接触不含D6约束；采样必须保持同一步/单位/路径映射；非固定OMPL种子。诊断不改变控制律，且不能用释放后FCL回推触发瞬间。
- Need user confirmation: no，用户继续定位已记录问题；若需改物理/基准/力控算法则另行请求。

## 实施与软件验证

[ENGINEERING] runtime `d35cc0c769fe51832dd0717ba0fcf71b873e2cef` 只增加 `/task01/fixture_phase` 标签：CONTACT、X_1..16、ROLE_SWAP、Y_1..16、ABORT/COMPLETE；不改运动律/轨迹目标/80Nm。新binary SHA256 `d6b53269077746b454b2e16203e5bb0fd095fab93af4d1530ea6c1c9287fff60`，colcon build103s PASS。

可选 `--record-held-diagnostics`：同一post-step复用原Cube/工具pose与contact sampler，新增各机器人link的contact view、DOF names/positions/targets/velocity/projected effort。只压缩完全零接触对，不设接触力阈值。启动检查API/句柄/DOF映射，失败不得发运动命令。阶段标签异步接收；行内physics pose/contact字段必须同一步，不能声称ROS guard与physics事件已严格对齐。raw revolute投影effort单位Nm、finger prismatic单位N；没有TCP wrench估计，也没有把D6约束力称为碰撞力。

44项离线测试PASS，包括空流/丢步/混步/非有限/DOF个数不符安全拒绝、phase范围、保留微小接触/默认旧记录行为。live tensor API在本轮**没有完成启动验证**，不能将离线PASS视为可用物理测量。

## 启动负结果与连接排查

20261006_TASK01_held_fixture_diagnostic01 使用原官方URL/first1/max1/scale5/hold0/零预置；实际在原场景 `_asset_url()` 报 `RuntimeError: 找不到官方 FR3 USD。`，机器人命令0/控制器未启动。Kit cleanup返回0但failure.json存在，严格判 **FAIL_STARTUP**，不是首件运动FAIL或首件PASS。

官方S3直连/本地HTTP CONNECT代理curl均报SSL unexpected EOF（exit35）；另一S3域名和HTTP尝试也未恢复。GitHub SSH早期banner timeout(exit255)，随后带nc连接超时的正常runtime push已成功，不能声称GitHub一直不可用。源码已上传runtime分支。SDK `open_cached_file(original_url,download=False)` 返回ERROR_CONNECTION；Sdf只读发现一个cached FR3（无external layer/asset依赖），但URL→cache来源映射未证实，未替换模型/缓存/原场景。

原scene/bridge/YAML SHA256分别43aa7c2e…、0f712365…、a49d60a4…不变。自有Isaac与MoveIt已经结束；MoveIt teardown-11/bridge1历史问题重复，与无机器人动作的startup结果分开。raw本地ignored，精选trace与metadata入git。

## Commands

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
CMAKE_BUILD_PARALLEL_LEVEL=2 colcon build --packages-select fr3_dual_palletize --symlink-install --parallel-workers 1
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description moveit_dual_side_suction.launch.py use_rviz:=false
```

本轮后台Isaac（在reproduction根目录）：

```bash
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --preplaced-count 0 --duration-sec 1200 \
  --record-release-diagnostics --record-held-diagnostics \
  --output-dir results/20261006_TASK01_held_fixture_diagnostic01/raw
python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py'
python3 scripts/validate_benchmark_candidate.py
```

未执行的controller命令（必须先有READY/held_topology且没有failure/sampler error）：

```bash
ros2 run fr3_dual_palletize task01_dual_suction_fixture --ros-args \
  -p first_batch:=1 -p max_batches:=1 -p execution_time_scale:=5.0
```

下一步有真实数据后才运行 `python3 platforms/isaac_ros2/probes/analyze_held_fixture.py <held_contact_samples.jsonl>`，空流会拒绝汇总。

## === POST-TASK REPORT ===

- Task: TASK01 / BUG-017持件诊断；Status: **PARTIAL**。
- Completed: 专用持件阶段/同物理步诊断/全机器人contact拓扑/流式完整性与峰值分析器；44软件测试/编译通过；记录启动FAIL与连接排查。
- Files changed: runtime `ros_ws/src/fr3_dual_palletize/src/task01_dual_fixture_impl.inc`；本仓held_fixture_diagnostics.py、release_diagnostics.py可选接口、physics_contact_sampler.py压缩选项、task01_cube04_headless.py、analyze_held_fixture.py与三项测试文件；六记录、本报告、TASK01任务卡及run metadata/startup_evidence.log。
- Commands run: 上述colcon/MoveIt/headless/unittest/analytic/py_compile/diff --check；curl直连/代理、SSH、SDK cache/Sdf只读探针。物理controller **未运行**。
- Tests / experiment results: 软件44PASS/build PASS/analytic PASS only；真实启动FAIL，live held sampler验证与采样未开展。
- Key metrics: robot commands0、held samples0、failure.json1、headless exit0不当PASS；MoveIt teardown-11/bridge1；36nulls/hash不变。之前Cube01Y15 86.975Nm失败仍为最新物理结果，非本轮测得。
- Paper fidelity: [ORIGINAL] 无新论文算法；[ADAPTATION] 沿用已批准3+2；[ENGINEERING] 只读采样/映射/完整性/phase；[DEVIATION] 未改场景或提高门限，不叫忠实论文复现；[EXPERIMENTAL] 一次原场景startup尝试/联网与缓存探针。
- Records updated: STATUS、WORKLOG、EXPERIMENT_LOG、BUGS（017/018 OPEN）、DECISIONS D020、USER_FEEDBACK，另TASK01卡/results/report。
- Open risks: 官方资产访问未恢复；held live sampler尚未验证；phase时钟、D6反力/跟踪/接触根因待区分；旧teardown与36数值审查仍OPEN。
- Recommended next step: 恢复同一官方资产连接或验证原资产完整离线映射 → 正常首件启动/readout验证 → 真实推压同一步诊断 → 原门限内工程修正；需要模型/物理/算法范围改变时另行询问。
- Git branch / commit / dirty files: runtime task01-runtime-fixes/d35cc0c正常push成功；reproduction task01-benchmark-draft诊断/记录最后commit见Git历史。raw本地ignored、原runtime未跟踪目录保留；保护目录未访问。GitHub各push最终结果随六记录更新，不以本地commit冒充上传。
