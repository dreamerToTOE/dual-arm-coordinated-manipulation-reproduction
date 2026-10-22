# 第二篇P2物体位姿与内部作用力控制论文复现汇总：构造器与提纲

2026-10-14；第二阶段输入基线834bcc，实际动力学源码身份另从每次run的metadata读取，不能把输入基线冒充新科学源码commit。

构造器现已只读实际结束的动力学失败run，生成“动力学资格阶段”Word初稿与真实前缀图；完整闭环报告未完成，没有四组图。正式结果必须来自带summary与SHA清单的真实run。系统python3缺python-docx；持久报告环境为`/home/ubuntu2004/lmy/.venv-p2-report`，python-docx1.2.0，使用系统NumPy／Matplotlib。构造器薄适配既有P4的Report和原生OMML，不修改P4或任何旧源文件。

## 第一部分：原论文数学模型与核心方法

1. 直接讲双臂标定／时延导致的位姿与内部应力冲突、论文贡献和闭环计算图；本人科研叙述，不写对话要求或编写说明。
2. SE(3)变换、线性优先twist/wrench、右扰动、完整伴随与作用点、Log平移区别；对应原式1–6。
3. D的共同base变换链、弹性hK、原Rbar阻尼、H的tight/pivot/sliding接触拓扑、W的逆转置wrench映射；原式7–12及单位、有限形变局限。
4. 印刷原式15正号完整保留；自由滑动反例独立列为公式审计。展示已批准G演化Ng、Ac、VG、Jr及自由Log不变量与零功；标[DEVIATION／已批准]，不是作者勘误。说明标准模式可逆域、非零自由初值不卸载、固定时刻切换预载拒绝与原阻尼近似。
5. 独立式16COM惯性／重力／body动力学、原A质量尺寸、均质惯量及理想Cartesian适配；力推动物体，不能用desired pose或解析式24产生实验响应。
6. 六个SE(3)＋ℝ6的42维右扰动IESEKF、原式17弹性触觉与动态视觉维度、式18噪声尺度、多率新样本、迭代更新、状态注入与协方差坐标重置、运输C冻结、因果held input和GT隔离。解释论文机制与实际实施状态分别标明。
7. 原式20传递子空间内力投影与H提升、21零内力控制；零内部wrench不是零握力。
8. 原式22印刷形式、直接微分的有限形变争议、式24局部稳定性范围；只理论解释，不用于生成plant力曲线。
9. 原式25当前body位姿误差／前馈转换、19叠加、26约化运动学与J=I适配；exp2仅KP=0保留前馈，exp4仅估计模型K失配。原表II与原图6／7／9含义、卡尺<0.1mm删失界明确为论文结果。

## 第二部分：真实运行及原文对照

- 只读本轮`metadata.json`、`cases.jsonl`、`summary.json`、`termination.json`、`config_snapshot.json`和`*.jsonl.gz`；验证`artifact_sha256.json`绑定、冻结protocol SHA、case计数、唯一run身份、原始样本字段与时钟。没有相应数据则不出相应图。
- 科学commit与各源SHA从运行时metadata读取；当前工作区文件不能替代当时科学版本。重复或修正版保留为不同记录，不能当新增独立主样本。
- 构造器当前仅接受`INDEPENDENT_DYNAMICS_QUALIFICATION_NO_CONTROL`，不猜将来闭环日志格式，不运行任何实验或加载mechanics／controller／observer。
- 对真实保存动力学画COM位移、body速度、分单位力／力矩平衡残差、两侧总接触力／力矩。图题明确固定EE、无估计器、无反馈；横轴只到实际落盘样本，不能补成95s运输图。
- case表显示真实通过／失败、数值和来源；终止last_integrated_state与末个保存样本分别解释，不以采样末帧冒充终止状态。
- 若动力学门失败：明确“只取得无控制动力学响应；42维滤波、主20与代表控制实验未执行；完整P2部分完成”。不给exp1–4空图、伪RMS、力矩80%或估计收敛。
- 原图6／7／8／9与本机实测分列。原文约1.5N、10mm／4.5°、0.42°、80%和卡尺分辨率仅为论文参照；无主20时写尚未复现、不可作性能数值对比。
- 如后续全部门通过，须按真实闭环schema扩展只读构造器：5配对seed及主20分母、每侧／stack N与单独Nm、GT及估计位姿误差、真实vs估计内力、发布／model／施加输入、时延／高力矩／切换独立代表例。扩展前不提前生成。

## 最后独立应用差距

双FR3／侧吸／Cube／受限车厢仅在最后独立章讨论接触拓扑、吸盘柔性与释放、6D力观测、COM/TCP标定、多率时延、7DoF约化运动学、真空重力保持和Isaac物理证据。原P2最小数值资格不能称真实机器人可执行、摩擦安全或完整装配完成；不开展改进、P3或Isaac。

## 构造器使用

真实run结束后先只读检查：

```bash
/home/ubuntu2004/lmy/.venv-p2-report/bin/python scripts/build_p2_stage2_report.py \
  --run-dir results/<completed_run> --audit-only
```

确认身份后可生成正式Word；多个实际run用重复`--run-dir`保留失败，不覆盖旧Word／图目录：

```bash
/home/ubuntu2004/lmy/.venv-p2-report/bin/python scripts/build_p2_stage2_report.py \
  --run-dir results/<completed_run> \
  --output-docx reports/第二篇P2物体位姿与内部作用力控制论文复现汇总_动力学资格阶段.docx \
  --assets-dir reports/p2_stage2_report_assets
```

生成后需实际打开Word／PDF逐页检查中文、公式、表格与图。私有原PDF与提取全文不上传；只保存引用、SHA、原创图、真实源码／日志与报告。当前提纲不宣称任何后续实验已执行。

## 实际阶段稿（2026-10-14）

- 来源`results/20261014_P2_stage2_dynamics01`，科学commit9194f9f；四个science source SHA、冻结protocol及完整artifact索引核验一致。
- 状态`FAIL_STOP`；壁钟120.050960746s、终止tick9972对应积分3.324s；831个保存样本为0–3.32s，不能混为5s资格已完成。
- 11项已完成代数／单步检查通过；5ssettle尚未完成，半步／其他初态／IESEKF／控制和主20＋其他10run未执行，完整P2部分完成。
- 初稿`第二篇P2物体位姿与内部作用力控制论文复现汇总_动力学资格阶段.docx`含29原生OMML和3嵌图。理论闭环图说明论文计算关系，另两图只取真实无控制动力学前缀，中文字体已目视检查。
- 首次Matplotlib自动字体族识别失败，编辑预览保留为`preview01_font_issue`；显式注册既有NotoCJK后重新生成，无科学run、参数或数据修改，科学小修预算仍剩2。
- 尚待主代理Word／PDF逐页检查及独立显式中点步长风险审计结果；不得把未执行的C初态写成已跑失败。

## 阶段性审查变体（2026-10-14）

前稿Word／PDF和图目录保留。新稿为`第二篇P2物体位姿与内部作用力控制论文复现汇总_阶段性审查.docx`、`p2_stage2_review_assets/`，副标题明确“阶段性审查／完整P2部分完成”。构造器用Heading1.page_break_before替代空分页段，移除继承表格后的空段，避免前稿第7页分页溢出；不修改P4 helper。

- 可选`--delivery-audit-dir`绑定交付审计index、原source metadata和run index；将独立prefix统计逐字段与保存原始样本复核。正文加实际下沉0.594756249mm、每侧支撑3.35502N；新增真实hI每侧N／N·m图，约10⁻¹³N对称数值残差不能当作内力反馈成果。
- 可选`--numerical-audit-dir`只读固定数学诊断完整index、source SHA及4个fixture。诊断源码385d08d和真实动力学9194f9f分别标记，二者mechanics／contact_geometry SHA一致；未篡改被metadata引用的原诊断声明。
- A快连续λ约−2183.07s⁻¹、C约−9335.81s⁻¹；主／半步线性中点快支倍率、实际FD one-step谱和4ms Euler无更新风险分表。C主步2.73014非中性模式与半步0.65455快支、约1中性方向分别解释。
- 明示名义点并非重力平衡、解析平衡点仅独立诊断副本；C没运行trajectory、IESEKF尚未实现／未执行／未资格。该诊断不证明实际C失败或完整滤波发散，不新增ODE trajectory、控制run或验收阈值。
- 新稿30原生OMML、4嵌图；原始动力学、交付审计和数学诊断的全部artifact SHA在生成后复核仍相同。尚待主代理实际PDF逐页确认分页修正效果，完整P2保持部分完成。

阶段性审查变体的实际只读构造命令：

```bash
/home/ubuntu2004/lmy/.venv-p2-report/bin/python -B scripts/build_p2_stage2_report.py \
  --run-dir results/20261014_P2_stage2_dynamics01 \
  --delivery-audit-dir results/20261014_P2_stage2_delivery_audit01 \
  --numerical-audit-dir results/20261014_P2_stage2_numerical_audit01 \
  --output-docx reports/第二篇P2物体位姿与内部作用力控制论文复现汇总_阶段性审查.docx \
  --assets-dir reports/p2_stage2_review_assets
```

默认禁止覆盖已有Word和图目录；复核输入可在同一命令末追加`--audit-only`，不写报告。`report_data.json`保存报告构造器／继承helper SHA、六资料SHA、实际run、交付统计和数学诊断身份。
