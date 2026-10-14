# 工程修正01：Comau资格驱动名称冲突

原源码970ac34已保存。真实build01的IV/V/VI均编译失败，科学调用0；错误为本项目JSON输出函数vector与作者using namespace std导入的std::vector冲突，以及作者def.h的RR宏进入后包含的标准库。证据 results/p4_full/20261014T1540_R1_COMAU01/*_build.log。

唯一修正：本项目JSON函数更名write_state_json；标准库头放在作者宏之前。作者APC/KDL/def.h字节不改，模型、端点、算法、seed、次数、门值均不改。

这是我方编译接口问题，归OUR-IMPLEMENTATION/ENGINEERING，按D079不消耗科学修正次数；所有成本保留。第二次构建在新run_id、同既定总1800s内，不覆盖首失败；若再失败先据具体编译证据处理，不重抽科学输入。
