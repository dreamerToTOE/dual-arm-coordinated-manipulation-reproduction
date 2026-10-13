# P4 三策略真实比较图表

原始结果：`results/20261013_P4_three_methods_round3/`。所有统计行与 gzip 原件及 SHA256 核对。

10幅PNG/SVG包含原创理论流程、登记机构、全部成功/失败统计和真实合格路径。图08来自原日志的逐点关节/闭链/GEOS记录；图09严格区分RSS单元桥接与全局规划。

选例规则：各方法按seed升序、登记环境顺序、预算升序选择首条SUCCESS，未成功的方法不画路径。全部60次统计见CSV；确定性重复不进入成功率分母。

复建命令：`python scripts/build_p4_three_assets.py --run-id 20261013_P4_three_methods_round3`。该脚本只读保存数据，不运行规划、IK、碰撞查询或仿真。
