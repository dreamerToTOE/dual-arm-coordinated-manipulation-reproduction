# H 科学资格草案：漏计工程 own-cost 的元数据修正

**PASS_SCIENCE_PRIOR26_SAVED_METADATA**，12/12项保存元数据检查通过。0科学、0编译、0helper派发。

原science调用builder.prior()，该函数为工程排除自身build RUN，因而漏计刚完成H工程。修正仅在未冻结science runner加入专用science_prior()并改一个调用点，排除science自身RUN、纳入H工程。冻结builder/PRE及原25笔工程协议完全未改，runner修前原字节另存work/h_science_prior_recovery_20261016。

新science账26笔：墙钟443.9257601529946秒、CPU418.516481秒；原25笔419.40566987399438/385.449026，新增恰为工程own-cost 24.520090279000215/33.067454999999995，只计一次。两个实际工程binary已ready，270项绑定资产哈希复核一致。

新runner SHA `3c6784a896a853fb21c9e553cfa4518a3a61059421460cce425008c58d32abdf`。尚未保存/冻结科学候选或启动科学；root应由当前runner重新describe、复核并提交26笔实际账协议。本修正不改任何数值、branch、collision、64点清单、预算帽或原失败。
