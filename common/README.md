# common

Platform-independent scientific infrastructure.

TASK02-A 提供 `common/interfaces/state.py` 的草案状态契约：SI 单位、xyzw、
显式 frame/测量来源、按身份绑定的关节、双臂/物体状态，以及禁止把异步旧数据
冒充 post-physics-step 科研状态的时钟校验。不依赖 ROS、Isaac 或 MuJoCo。

已验收 Task26 的原地薄适配器在 `platforms/isaac_ros2/foundation/`。
TASK02-B 提供 `common/interfaces/exchange.py` 数据命令、事件、结果和运行元数据，
`wire.py` 严格确定性 JSON 编解码，以及 `common/logging/run.py` 文件日志。
当前 TASK02-B PASS CANDIDATE、TASK02 IN_PROGRESS；不冻结 Benchmark。

## 数据契约和时间

- `BaselineCommand` 只有数据，无 execute/send/publish：JOINT_TARGET（rad）、TASK_POSE
  （m + quaternion xyzw）、HOLD、SUCTION_ON/OFF。显式机器人/对象、frame、deadline、
  配置/来源；issue/deadline 必须同一时钟域，关节身份和目标机器人必须匹配。
- `TaskEvent` 延用旧 SUCTION_ON/ATTACH/SUCTION_OFF/DETACH。PLANNED 使用轨迹ID及
  相对ns；OBSERVED/CONFIRMED 使用仿真session及实际 post-step ns/step。不同域不比较
  大小，也不自动换算。FAILED必须保留原因/证据；物理失败也要实际step。
- `EventLedger` 只检查记录顺序/因果，不驱动机器人。CONFIRMED必须引用独立先前
  OBSERVED，匹配命令/对象/link/attachment；ATTACH观测必须有attachment身份/原始证据。
  字符串身份不等于 native D6已验真，SUCTION_ON和SG CLOSED都不会自动生成ATTACH。
- `TaskStageMarker` 保留轨迹相对 start/end。旧事件薄适配仅生成PLANNED，见foundation。
- `BenchmarkResult` 草案区分SUCCESS/FAILURE/ABORTED/INCOMPLETE，记录scope、失败阶段、
  原因、证据/配置/来源和measurement qualification；不计算或冻结科学成功阈值。

## 轻量日志

`RunMetadata` 必须显式给run/task/baseline/platform/git/trial/seed、原命令argv、配置ID及
路径、SourceRef文件hash。seed=None写UNSET，不调用任何RNG。`source_ref()`可计算本地
文件SHA256，但不是原生测量真实性认证。可使用现有 TASK02-A StateRecord字典记可选状态。

```python
# 这些对象均为数据，不会执行命令；实际构造例子见离线 tests/。
with RunLogger(output_root, metadata) as log:
    log.append_command(command)
    log.append_event(planned_event)
    # 有独立证据时才记录 observed_event，再引用它进行确认。
    log.append_state(historical_record, MeasurementQualification.LEGACY_ASYNCHRONOUS)
    log.finish(explicit_result)
```

独占run目录，已存在则拒绝覆盖。metadata.json内`run_metadata`保存完整typed envelope，
旁边列seed_status/status/计数/配置路径/最终artifact hashes。commands/events/states使用JSONL，
result.json原子写入。正常未finish退出为INCOMPLETE；Python异常退出为ABORTED，保留traceback
并向调用方传播异常。单进程单写者；不承诺SIGKILL、磁盘故障、跨文件事务或并发恢复。
摘要/hashes在创建和finish更新，不是每条append后刷新。不会引入数据库或日志服务。

实际文件读回：

```python
import json
from pathlib import Path
from common.interfaces import RunMetadata, TaskEvent, BenchmarkResult

folder = Path("results/20261009_TASK02_exchange_logging01/retained_failure")
metadata = RunMetadata.from_dict(json.loads((folder / "metadata.json").read_text())["run_metadata"])
events = [TaskEvent.from_dict(json.loads(line)["event"])
          for line in (folder / "events.jsonl").read_text().splitlines()]
result = BenchmarkResult.from_json((folder / "result.json").read_text())
```

示例是故意失败的合成测试，**不是物理失败/成功证据**。历史旧状态缺少同步时间，不能靠
补字段或删标签升级；日志的SYNCHRONIZED_POST_STEP结果需非空且全部同资格的状态记录。
这仍是格式/来源声明校验，不能防止伪造所有字段。ContactWrench/CollisionDistance、科学
metrics、执行RNG控制和native数据绑定留给后续有界切片；当前不执行实时测试或TASK03。

离线测试（仓库根目录）：

```bash
python3 -m unittest discover -s tests -p 'test_task02*.py' -v
```
