# D080 V PCS fixed-local 冻结字段接缝草案

2026-10-18。仅从当前已审DRAFT、local runner/supervisor和既有`L.preload_state`读取字段合同，未生成协议、冻结、导入runner或执行模型。新BUILD02组合POST实际ADDENDUM已独审；local仍待最终门独审、最新实际账及root冻结。

顶层schema为`P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1`。以下是当前源码真正读取的必需键；无需新增框架或helper。

| 键 | 冻结值或来源 |
|---|---|
| `schema` | `P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1` |
| `frozen` | true，仅在独审及root批准完成后 |
| `environment` / `method` | `V` / `PCS` |
| `run_id` | `20261018_R2_D080_V_PCS_LOCAL01` |
| `classification` | `CORRECTED_COMAU_APC_ALIGNED_V3_ORIGINAL_FIXED_PCS_RBS_CONTROL_RECONSTRUCTED_A02` |
| `budget` | `{"wall_s":30,"cpu_s":60}`，两source合计；原R2总3600/7200不扩 |
| `independent_review_passed` | true，仅最终组合资产门的独审后 |
| `scientific_execution_authorized` | true，仅本固定local来源调用 |
| `formal_execution_authorized` | false |
| `fixture_sha256` | 当前`configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json`原字节SHA，不改请求 |
| `schedule_modes` | `["trace","plain"]` |
| `driver_protocol` | 下表；原18命名请求与原caps逐值相同 |
| `maxima` | 原fixture的`global_maxima_proposal`完整副本：public36/project512/independent_unique_nodes256/source2/setup2/solve0/formal0 |
| `build_assets` | 真实BUILD02 tail execution/SHA、真实组合独立POST/SHA、plain/trace两个binary与SHA；见下表 |
| `runtime_meshes_sha256` | 原`collision_adapter_v3/manifest.json`中V/aligned的27个mesh；key为`V_aligned/simulator/<name>`绝对路径 |
| `prior` | tail独审且唯一入账后的最新V32（或确有新execution时更新到更晚实际账）的`ledger`相对路径、`ledger_sha256`、`wall_s`、`cpu_s`；不得预用V31或跳过未入账attempt |
| `bound_files_sha256` | 绝对路径键→当前SHA；完整union规则见后 |
| `system_preload_state` | 冻结时按既有`L.preload_state()`原函数取得，结构`{"path":"/etc/ld.so.preload","exists":bool,"sha256":SHA或null}`；只有不存在或空白普通文件允许；不得预填一个历史值 |
| `external_supervision` | 下表原GNUtime/路径/工具SHA合同 |

`driver_protocol`必需键：`schema=P4_D080_V_PCS_LOCAL_FROZEN_V1`、`environment=V`、`method=PCS`、`frozen=true`、`api_local_only=true`、`scientific_execution_authorized=true`、`independent_review_passed=true`、`requests=fixture.requests`、`caps=fixture.caps_per_binary_proposal`。这是真正传入binary argv[2]的完整固定JSON；每binary实际输出1条setup+18条请求=19行，trace/plain合计38行与36public，不发送stdin请求。

`build_assets`必需键：`execution=results/p4_full/20261018_R2_D080_V_PCS_BUILD02_TAIL/execution.json`、`execution_sha256=真实tail SHA`、`personnel_independent_POST=reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json`、`post_sha256=3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8`、`targets={"plain":{"binary":旧plain ELF绝对路径,"binary_sha256":原/当前SHA},"trace":{"binary":新build02/trace ELF绝对路径,"binary_sha256":真实SHA}}`。binary模式和实际source target相同；旧plain status=REUSED_BUILT_NOT_QUERIED、新trace=BUILT_NOT_QUERIED。最终source常量`BUILD_COMPOSITE_POST_SHA`已绑定实际ADDENDUM SHA`3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8`，首版FAIL仍保留。

`external_supervision`必需键：`sibling_path=results/p4_full/<run_id>.supervision.time.txt`、`metadata_path=results/p4_full/<run_id>.supervision.jsonl`、`stderr_path=results/p4_full/<run_id>.supervision.stderr.log`、`charge_path=results/p4_full/<run_id>.supervision.charge.json`、`format="%e %U %S %x"`、`time_binary_sha256=当前/usr/bin/time SHA`、`python_binary_sha256=当前/usr/bin/python3 SHA`。可以保留已审的required、.01wall/.02CPU padding与final_POST说明；首次外charge仍采用原三观测Decimal最大包络，不是rawtime单独计费。

`bound_files_sha256`沿已审冻结证据做stdlib union即可：真实BUILD02 frozen manifest全部输入、BUILD02实际新staged/dependency输出、真实组合POST及其retained资产（两ELF、旧first-collected17资产和各source/依赖）、旧failure POST3dca、tail execution/外charge/内部receipt/time/metadata/stderr、当前local OWN六原项+compat PRE、最终local独审证书、fixture/两个A02原中心、原27mesh、scope/overlay和最新实际账及其每条execution/外POST/charge/内部receipt/time/metadata/stderr。合并遇到同一路径不同历史SHA必须区分历史证据引用与当前冻结输入，不覆盖旧记录；当前输入只接受已证当前字节。

当前local OWN为：local runner、local supervisor、fixed fixture、local PRE、已审SBL setup基础设施源码、已审V build原源码、固定compat PRE。所有OWN和最终协议必须在唯一执行前commit，执行时原git字节门仍必需。额外union不改变source环境或loaded symbol观察边界：V无stdin等待门，模型前实际符号观察仍UNOBSERVED_NOT_CLAIMED。

本项只保存固定来源调用/trace/plain一致性/完整原始流与成功节点待验队列。任何source true或组合工程资格都不能替代后续另冻的Comau闭链、真实分支、原限位、原87pair碰撞及叶距离独立资格；不得借ABB oracle或启动规划。
