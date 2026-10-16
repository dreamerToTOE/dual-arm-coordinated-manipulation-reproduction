# CBiRRT_NR BUILD01 工程失败独立根因

STOP：compiler exit0、reaped且组空，仍不授予build资格。六TU共用一次-MD -o，只剩output-derived p4_abb_cbirrt_nr.d且仅含末个CBiRRT_NR.cpp；五TU依赖缺失。我们的构建设计与独立静态审查错误地推广了通用aux命名规则，不是作者程序或论文理论错误。原V4、claim、binary、源码与所有失败字节保全。

[GCC的MD专门规则](https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html)说明-o决定.d默认名，MF可显式指定。新版本应使用六次独立-c -MD -MF与唯一object输出，再一次link；先冻结新stage/claim/命令和实际费用，保持科学条件与45/90及累计帽，不重试旧claim。

费用独立资格=True；实际GNUtime ['33.95', '44.43', '11.03', '1']，上界33.96wall/55.48CPU。本次审查0compile/binary/science。
