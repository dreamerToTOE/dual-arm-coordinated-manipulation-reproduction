# P2-T01 环境、依赖与缺口登记

**结论**：科学路径（plant / estimator / control / qualification）只依赖 `numpy + scipy + 标准库`，可在本机复现；
**报告生成路径**存在两个可复现性缺口（缺 `python-docx`、缺 P4 的 `build_p4_paper_report`），以及
`PATH` 上的 `python3` 与运行所需解释器不一致的陷阱。三者都不影响 T02–T09 的科学计算，但会影响 T10 的报告产出，
必须先记录再决定修法。

---

## 1. 解释器与依赖版本

| 项 | 值 | 来源 |
|---|---|---|
| 必需解释器 | `/usr/bin/python3.10`（**3.10.12**） | 直接探测 |
| `PATH` 上的 `python3` | `/home/ubuntu2004/.workbuddy/binaries/python/versions/3.13.12/bin/python3`（**3.13.12，无 numpy**） | `which -a python3` |
| numpy | 1.24.4 | `import numpy` |
| scipy | 1.8.0 | `import scipy` |
| pytest | 6.2.5 | `import pytest` |
| matplotlib | 3.5.1 | 仅报告脚本用 |
| python-docx | **缺失** | `import docx` → ModuleNotFoundError |
| g++ | 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3) | `g++ --version` |
| Eigen | 3.4.0（`/usr/include/eigen3`） | `Macros.h` |
| Boost | 1.74.0（仅头文件，`cpp_dec_float_50` 用） | `boost/version.hpp` |
| native 二进制 | `/home/ubuntu2004/lmy/.p2_native_build_v3/p2_native.so`，SHA256 `a3ff7b1b…b94949` | 构建缓存命中，本轮未重编译 |
| git | 2.34.1 | — |

**固定运行命令**（写进后续所有 PRE）：

```bash
cd /home/ubuntu2004/lmy/p2-num-sim-20261018
/usr/bin/python3.10 scripts/<script>.py ...
```

**陷阱**：直接写 `python3` 会命中 3.13（无 numpy/scipy），报 `ModuleNotFoundError`。
这不是环境损坏，是 PATH 顺序问题；三种解法（择一，T01 后统一）：显式绝对路径、在仓库内建 venv、或在命令前 `PATH=/usr/bin:$PATH`。
本轮采用**显式绝对路径**，不改系统环境。

## 2. 导入依赖审计

| 范围 | 依赖 | 结论 |
|---|---|---|
| `baselines/p2_pose_force/*.py` | numpy、scipy（`linalg`、`spatial.transform`）、ctypes、heapq、hashlib、json、pathlib、dataclasses、subprocess | **无 P4 / ROS / Isaac 依赖**，可独立复现 |
| `tests/test_p2_*.py` | numpy、scipy、pytest、`baselines.p2_pose_force` | 同上 |
| 科学脚本（`qualify_p2_*`、`run_p2_closed_loop`、`audit_p2_*`） | numpy、scipy、标准库、`baselines.p2_pose_force` | 同上；`run_p2_closed_loop` 通过 `ctypes` 调 native |
| 报告脚本（`build_p2_*_review.py`、`build_p2_stage2_report.py`） | `matplotlib`、`docx`、`build_p4_paper_report`、`build_p2_stage2_report` | **缺口见 §3** |

## 3. 三个可复现性缺口（登记，不在本轮修复）

1. **`python-docx` 未安装**：所有生成 `.docx` 的脚本无法运行。影响 T10 报告，不影响科学计算。
2. **`build_p4_paper_report` 不在本分支**：`scripts/build_p2_stage2_report.py` 顶部 `from build_p4_paper_report import Report, brackets, ...`。该模块属 P4，本分支按规则未导入 → 脚本不可用。
   受连带影响：`build_p2_implicit_review.py`、`build_p2_closed_loop_review.py`（均 `import build_p2_stage2_report`）。
3. **`common/metrics/README.md` 未导入**（T00 已记）：指标定义（`r(t)`、`d(t)`、四元数角、max/RMS）缺文档，代码在。

处置建议（待批准，不在本轮做）：为报告路径新建 **P2 自有的最小渲染器**（不引用 P4 模块），或把这三个脚本标为 `LEGACY_REPORT_PATH_UNUSABLE`
并在 T10 另写报告生成器。**不得**为了修报告去修改 P4 分支。

## 4. 未导入的历史排版资产（111 项，逐条在册）

`p2/reviews/LEGACY_BLOB_CHECK.json::sha256_freeze_manifest_crosscheck::missing_paths` 列出全部 111 条，分布：

| 目录 | 数量 | 性质 |
|---|---:|---|
| `reports/p2_closed_loop_layout_review01/` | 20 | Word 分页预览 png |
| `reports/p2_stage2_layout_review02/` | 18 | 同上 |
| `reports/p2_implicit_layout_review01/` | 16 | 同上 |
| `reports/p2_stage2_layout_review01/` | 16 | 同上 |
| `reports/p2_closed_loop_review_assets/` | 7 png + 4 文件 | `report_data.json`、`report_text.txt`、`final_delivery_qa.json`、`runtime_readiness.json` |
| `reports/p2_implicit_review_assets/` | 5 png + 4 文件 | 同上族 |
| `reports/p2_implicit_font_preview01/` | 5 png + 2 文件 | 字体预览 |
| `reports/p2_stage2_review_assets/` | 4 png + 2 文件 | 同上 |
| `reports/p2_stage2_report_assets*/` | 6 png + 2 文件 | 同上 |

**口径**：这些是 Word/PDF 的**排版与渲染资产**（分页图、报告数据、交付 QA），不含任何运行日志、`summary.json`、
`cases.jsonl`、轨迹或矩阵。因此可以说"**科学证据无遗漏**"，**不可以**说"所有资产零遗漏"。
其中 `report_data.json` 是报告数值的来源快照；若 T10 需要复算报告数字，应直接从 `results/` 重算，而不是依赖这些未导入文件。

## 5. 缺失参数（论文未给）

来自 `p2/configs/paper_reference_v1.json::unknown_or_unreported`：

- 物体惯量张量（论文只说刚性；实现用均质长方体对角阵，`ADAPTATION`）
- 各物体上的抓取点坐标
- 机器人基座相对变换 `T^{b1}_{b2}`
- 路点绝对位姿与 23 s / 55 s 分段时刻
- **式(18) 的离散传播方式**（Euler / 指数 / 隐式未说明）→ T01 裁决对象
- 抓力控制器 [23] 与摩擦系数（Fig.9 必需）
- 软垫几何、预载、形变限
- ArUco marker 到 COM 的偏移与字典 id
- 标定样本数与滤波初始化细节
- 附加视频内容与 IESEKF/标准 EKF 的数值对比

以上均已标 `UNKNOWN`，未填猜测值；实现侧的替代选择在协议中已标 `ADAPTATION`。

## 6. Fig.9 与四物体装配的建模缺口

**Fig.9（T08）**
- 论文时间基 0–250 s，事件约 50 s 抬升、130 s 抓力降至 0.3 N、150 s 起滑移、200 s 结束；旧协议为 **30 s 替代**（5 s 开始滑移、25 s 恢复、目标下移 200 mm）。二者不可直接对标。
- 缺**抓力伺服**与**摩擦模型**：论文 Fig.9 的 0.3 N 抓力、≤0.3 N 切向力来自低层抓握控制器 [23]，当前代码没有该层，只有 `H` 选择矩阵。
- 缺软垫在滑移中的真实形变/摩擦状态，`mode_switch_guard` 以静态预载阈值为准（1e-6 m / 6e-3 N / 2e-6 Nm），属工程发明。

**四物体装配（T09）**
- 协议 `model.objects` 只有 A 与 C，**缺 B1/B2**（论文 Fig.5(d)：各 0.280 kg、75×140×40 mm，本轮已录入 `paper_reference_v1.json`）。
- Fig.5(b) 的最终装配布局只有图像、**无坐标**；任何布局都必须标 `ESTIMATED_FROM_FIGURE` 并做敏感性。
- 缺"支承板/接触检测"：旧协议明确 `after_76: no plate contact`，而论文的最终放置靠外力估计触发接触检测（附加视频 + §IV-A 末段）。
- 缺 5 次重复的初值扰动定义（论文"by hand 粗略摆放"），需自行给出并声明。

以上四项构成 T08/T09 的**准入门槛**；本轮只登记，不实现。

## 7. 结论

- 科学路径环境**可用**且可复现（固定 `/usr/bin/python3.10`）。
- 报告路径**不可用**（两个依赖缺失），已登记，不影响 T02–T09。
- 参数与场景缺口已分类：`UNKNOWN`（论文未给）/ `ADAPTATION`（实现自选）/ `MISSING`（尚未实现）。
- 没有把任何 `UNKNOWN` 静默填入协议。
