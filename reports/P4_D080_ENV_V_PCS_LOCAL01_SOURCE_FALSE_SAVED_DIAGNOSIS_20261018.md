# V LOCAL01 来源false的只读因果诊断

最早失败为`start_role0_minus`：public22 → fixed project23 → specific24 → 被动arm2、branch3的native IK26返回false（trace stderr第49/50行）。没有collision或全12角`check_angle_limits`调用；内部IK未记录具体return位置，workspace/被动界/其他解析门之间保留UNKNOWN。其role0 RBS与回溯均按固定依赖门未执行，没有换点或分支。

其余三条实际RBS与三条回溯全部因**成功投影后的原碰撞安全带拒绝**返回false，未出现内部project失败。原最深探索仅4，失败不是depth150或资源帽。下表pair_index从0开始；每pair均API code0而`CloserThanTolerance=true`，原阈值8mm，不能解释成API错误，也不等于已经证明实体网格交叠。

|原固定边|主动role / branch|首个拒绝深度|isValid / collision / PQP事件ID|原pair|回溯对应事件|
|---|---|---|---|---|---|
|start_role1|1 / 3|2（先探索到4）|1186 / 1191 / 1278|86 conveyor–box|2421 / 2426 / 2513，同一q|
|goal_role0|0 / 1|1|2640 / 2645 / 2719|73 chassis–box|2829 / 2834 / 2908，同一q|
|goal_role1|1 / 3|1|3028 / 3033 / 3106|72 chassis–EE2|3217 / 3222 / 3295，同一q|

`process0_stderr.bin`原始行定位：三RBS true-pair完成行2551、5434、6208；对应collision完成2552、5461、6237及isValid false完成2553、5462、6238。JSON附每个拒绝q12、实际分支、全部true pair、对应回溯及原始entry/completion行。`trace/parsed_rows.json`零基8/9、13/14、17/18可直接定位六次请求。

固定四参project本体只调用所选被动IK并写回，被动IK内部`include_joint_limits=true`，但它**不调用collision_state，也不调用全12角check_angle_limits**。`isValidRBS`在project之后调用collision，仍未显式调用全12角limits；本run limits事件确为0。故7次public project true既不是独立碰撞合格，也不是独立全12角限位/闭链/branch证书；不能笼统说“完全没有任何限位检查”。源branch参数也不能取代独立branch识别。

trace34个collision查询为17个唯一节点各在RBS/回溯出现两次：28次clear、6次安全带拒绝，对应14个唯一clear和3个唯一拒绝。24个待验节点中另7个是只有投影输出、没有source collision查询；因此“17个被查询节点”不应写作“17个碰撞节点”。失败中点也因成功project被保存在待验队列，不能删去。

来源execution SHA `a0549cd8207b0a4c16e5adb71aab0f063859458a803916ba72db287e419d7985`，source commit`7bf8afb784de429e87e2a4bef9abbcd0361d6409`。仅保存raw算术/事件因果定位；既有194/194独立来源后审不重做。本诊断没有新模型、FK/J、IK、PQP、RBS、编译、重跑、费用或阈值变更，不是物理后审，也不提升为论文理论/方法错误。
