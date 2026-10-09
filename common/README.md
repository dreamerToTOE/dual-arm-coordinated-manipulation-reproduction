# common

Platform-independent scientific infrastructure.

TASK02-A 提供 `common/interfaces/state.py` 的草案状态契约：SI 单位、xyzw、
显式 frame/测量来源、按身份绑定的关节、双臂/物体状态，以及禁止把异步旧数据
冒充 post-physics-step 科研状态的时钟校验。不依赖 ROS、Isaac 或 MuJoCo。

已验收 Task26 的原地薄适配器在 `platforms/isaac_ros2/foundation/`。
命令接口、ContactWrench、CollisionDistance、BenchmarkResult、统一 logger/metrics
仍属于后续 TASK02 切片；当前不是完整 TASK02 PASS，不冻结 Benchmark。

离线测试（仓库根目录）：

```bash
python3 -m unittest discover -s tests -p 'test_task02_foundation_interface.py' -v
```
