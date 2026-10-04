// [ENGINEERING] 使用真实控制器 header，避免在测试中另写一套纠偏算法。
#include <fr3_dual_palletize/preclose_alignment.hpp>
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>

int main()
{
  using fr3_dual_palletize::precloseAlignmentDelta;
  const auto near = [](double a, double b) { return std::abs(a - b) < 1e-12; };
  assert(near(precloseAlignmentDelta(0.001, true), 0));
  assert(near(precloseAlignmentDelta(0.001, false), 0));
  assert(near(precloseAlignmentDelta(0.001153, true), 0.000153));
  assert(near(precloseAlignmentDelta(0.001468, false), -0.000468));
  assert(near(precloseAlignmentDelta(0.00101, false), -0.00001));
  assert(near(precloseAlignmentDelta(0.0025, false), -0.001));
  assert(near(precloseAlignmentDelta(-0.001, true), -0.001));
  double left = 0.001153, right = 0.002122;
  left -= precloseAlignmentDelta(left, true);
  right += precloseAlignmentDelta(right, false);
  assert(std::abs(left - right) <= 0.0003);
  bool rejected = false;
  try { precloseAlignmentDelta(std::numeric_limits<double>::quiet_NaN(), true); }
  catch (const std::invalid_argument&) { rejected = true; }
  assert(rejected);
  using fr3_dual_palletize::PrecloseVector3;
  using fr3_dual_palletize::precloseAlignmentDeltaXYZ;
  const auto norm = [](const PrecloseVector3& v)
  { return std::hypot(std::hypot(v[0], v[1]), v[2]); };
  const PrecloseVector3 zero{0, 0, 0};
  assert(norm(precloseAlignmentDeltaXYZ(zero, zero)) == 0);
  const auto small = precloseAlignmentDeltaXYZ({.0001, -.0002, .0003}, zero);
  assert(near(small[0], .0001) && near(small[1], -.0002) && near(small[2], .0003));
  const auto diagonal = precloseAlignmentDeltaXYZ({.01, .02, -.03}, zero);
  assert(norm(diagonal) <= .001 + 1e-15);
  assert(near(diagonal[1], 2*diagonal[0]) && near(diagonal[2], -3*diagonal[0]));
  assert(near(precloseAlignmentDeltaXYZ({0, .000153, 0}, zero)[1],
              precloseAlignmentDelta(.001153, true)));
  for (std::size_t axis = 0; axis < 3; ++axis)
  {
    for (const double invalid : {std::numeric_limits<double>::quiet_NaN(),
                                std::numeric_limits<double>::infinity()})
    {
      auto bad = zero; bad[axis] = invalid;
      rejected = false;
      try { precloseAlignmentDeltaXYZ(bad, zero); }
      catch (const std::invalid_argument&) { rejected = true; }
      assert(rejected);
    }
  }
  // 前轮静止失败读数的数学重放，不是实际物理跟踪证明。
  const PrecloseVector3 desired_left{.349998832, -.061001499, .259999990};
  const PrecloseVector3 desired_right{.349998832, .060998501, .259999990};
  PrecloseVector3 actual_left{.348959131, -.060998930, .258775326};
  PrecloseVector3 actual_right{.352108885, .060996765, .258479024};
  for (int attempt = 0; attempt < 2; ++attempt)
  {
    const auto dl = precloseAlignmentDeltaXYZ(desired_left, actual_left);
    const auto dr = precloseAlignmentDeltaXYZ(desired_right, actual_right);
    assert(norm(dl) <= .001 + 1e-15 && norm(dr) <= .001 + 1e-15);
    for (std::size_t axis = 0; axis < 3; ++axis)
    { actual_left[axis] += dl[axis]; actual_right[axis] += dr[axis]; }
  }
  assert(std::abs(actual_left[0] - actual_right[0]) < .0025);
  assert(norm(precloseAlignmentDeltaXYZ(desired_left, actual_left)) < 1e-12);
  std::cout << "PASS: nominal, signs, tiny step, bounds, prior failed state, NaN guards\n";
  std::cout << "PASS: combined XYZ direction, total1mm bound, finite guards, static negative-state replay\n";
}
