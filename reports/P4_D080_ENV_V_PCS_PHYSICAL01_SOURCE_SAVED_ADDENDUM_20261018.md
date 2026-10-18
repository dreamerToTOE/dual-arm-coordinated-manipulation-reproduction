# V PHYSICAL01：原source TCP、箱体与碰撞记录保存核对补记

只归约已有数据，不重跑24节点或原LOCAL01。source侧stdlib脚本唯一执行634/634，人员独立薄审8/8；复用原430项物理/生命周期/费用证书，不重复检查或入账。原PHYSICAL01主POST中PENDING字段按原字节保留，本补记补充后续真实证据。

|保存分组|节点数|aligned清晰|aligned碰撞拒绝|
|---|---:|---:|---:|
|原source实际查询collision的唯一节点|17|14|3|
|仅public project输出，原source未查询collision|7|1|6|
|完整原队列|24|15|9|

68条source碰撞记录（trace34、plain34）按完整12角binary64映射：87个pair的顺序/身份、8mm门、API=0、returned等于any(CloserThanTolerance)均自一致，且aggregate与保存独立aligned响应一致。source TCP与保存独立FK位置最大差9.094947017729282e-13mm、旋转2.220446049250313e-16；按原Rtcp*Ry(-3.1416/2)、ptcp+Rtcp*[435,0,300]所得箱体位置/旋转差最大9.094947017729282e-13mm/1.1102230246251565e-16，均在原1e-5门内。

三条原RBS及回溯拒绝对应的source pair86 conveyor–box、73 chassis–box、72 chassis–EE2保持；这些点独立aggregate也拒绝。独立adapter没有保存逐pair closer结果，所以逐pair独立几何归因仍UNKNOWN，不宣称已独立复算每个碰撞pair，也不将安全带拒绝等同实体穿透。7个纯project输出的6拒绝说明闭链成功不能代替碰撞资格，不回写原project返回值或挑选正例重跑。

source report `reports/P4_D080_ENV_V_PCS_PHYSICAL01_SOURCE_SAVED_CROSSCHECK_20261018.json` SHA `1788b0a11a04702dd36621e8418d4b94df9405e06f4d8e88385f52dedf2c6309`；其personnel_independent=false如实保留。人员独立补证 `reports/P4_D080_ENV_V_PCS_PHYSICAL01_SOURCE_SAVED_INCREMENTAL_INDEPENDENT_POST_20261018.json` SHA `6f96a32b0e6bbc3d33a749a87d48b7f7ea1a0375cacb72bbdd1a13b55cb04235`。脚本 SHA `94313116c78fc0e781944858da0e6019f904ef40738abd47e52e35b9d41b6d51`。

本项不改变V34费用、211×232表、24节点结果、原失败、native TCP mismatch、local/path/CCD=false或正式0/18000。对原接受/拒绝和坐标系的本次独立诊断已完整，保留负例后可以准备原V RRT有限完整入口；该入口尚无编译/科学协议或路径资格，不更改原几何/阈值。III工程独立推进，不增加VI或进入P2/Isaac/FR3。
