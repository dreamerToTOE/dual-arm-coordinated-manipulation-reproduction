# TASK01 旧工程修补来源

- Upstream: https://github.com/dreamerToTOE/dual-arm-embodied-palletizing
- Branch: `task01-runtime-fixes`
- Base: `631b1f65656d025c1bb2173e874192f3fe4d355a`
- 修预吸附/Task27 quaternion：`d80b6b63d21065ff67ed2fd3f45bf09c9440cd53`
- 静载校验可选 hold：`76408c8`（默认 0，普通流程不启用）
- `fr3_dual_palletize/package.xml` declares Apache-2.0; the legacy repository
  root/Isaac scripts have no separately identified license file. These are
  user-owned project patches, not imported paper implementations; retain this
  qualification instead of inventing a blanket upstream license.

`task01_runtime_fixes.patch` 仅记录第一个修复 commit 的四文件 diff。不要盲目
apply 到有用户修改的工作树，也不要编辑生成的 install 文件。第二个可选 hold
commit 的完整差异在 upstream；其受控实验记录单独保存。

修补没有变更几何、质量、摩擦、ACM、0.300 mm 预吸附门限或三次失败停机。
Task26 默认行为保持原样。精细微 IK 是未吸附时的 [ENGINEERING] 修正，不是
论文规划/闭链算法。普通五件流程通过，也不能代替 D004 接触协议验收或数值冻结。
