# 工程修正02：VI作者PI宏与KDL头的隔离

第二次构建bce960c：IV/V已经编译并完成原生组件读数；VI仍编译失败，没有VI科学调用。实际证据VI_build.log显示def.h的PI宏进入后包含的KDL常数，不能以此判三臂算法错误。第一份工程记录将宏初判写为RR，现按真实编译日志纠正为PI；首记录与首失败完整保留。

唯一改动：本项目driver先包含kdl_class.h，再包含apc_class.h；KDL头在作者宏定义之前解析。所有作者源字节、模型、种子、端点与协议门值不改。OUR-IMPLEMENTATION/ENGINEERING，不计科学修正轮，耗时累加原1800s额度，第三次构建只针对VI，不重复IV/V读数。
