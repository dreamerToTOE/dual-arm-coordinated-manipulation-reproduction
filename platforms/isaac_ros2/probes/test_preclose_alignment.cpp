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
  std::cout << "PASS: nominal, signs, tiny step, bounds, prior failed state, NaN guards\n";
}
