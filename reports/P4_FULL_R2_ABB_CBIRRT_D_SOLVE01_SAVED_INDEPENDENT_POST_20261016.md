# S01 失败前缀、保全及费用独立POST

科学/transport结论仍为 FAIL_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST；保存审查2688/2688通过，失败0。原STOP/JSONDecodeError、唯一dispatch、源-9/reaped保留。stdout仅55字节原debug行，无完整JSON；stderr原41条prefix完整保存，collision20 entered未返，树/M/回溯/求解结果全部UNKNOWN，不将无观测写成零。

外层原exit1身份和完整费用链可核验，上界1.44s墙钟/1.14s CPU，external_supervision_qualified只限失败费用身份，successful_transport_qualified=false。内部样本保留，以上界替换一次。

静态独立定位：实际绑定libompl的DEBUG logger使用std::cout/ostream_insert/endl，不是printf；driver planner->setup先于Redirect quiet solve作用域，setup调用configurePlannerRange产生原行。可研究版本化接收器精确保留日志sideband后等待唯一JSON；未修改源、未重跑。0科学/模型import/编译/protocol/prior/claim/commit，无路径物理PASS。
