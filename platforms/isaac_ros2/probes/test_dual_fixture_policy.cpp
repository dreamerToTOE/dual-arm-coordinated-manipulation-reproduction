#include "fr3_dual_palletize/dual_fixture_policy.hpp"
#include <cassert>
#include <limits>

int main()
{
  using namespace fr3_dual_palletize;
  assert(validRearFixtureRoll(0.) && validRearFixtureRoll(45.) && validRearFixtureRoll(60.));
  assert(!validRearFixtureRoll(-.001) && !validRearFixtureRoll(60.001));
  assert(!validRearFixtureRoll(std::numeric_limits<double>::quiet_NaN()));
  assert(validFixturePose({1, 2, 3, 0, 0, 0, 1}));
  assert(!validFixturePose({1, 2, 3, 0, 0, 0, 0}));
  assert(!validFixturePose({std::numeric_limits<double>::quiet_NaN(), 2, 3, 0, 0, 0, 1}));
  assert(validFixtureStamp(2, 1));
  assert(!validFixtureStamp(1, 1) && !validFixtureStamp(0, -1) && !validFixtureStamp(1, 2));
  assert(freshFixtureReceipt(0) && freshFixtureReceipt(.25));
  assert(!freshFixtureReceipt(.250001) && !freshFixtureReceipt(-.001));
  assert(!freshFixtureReceipt(std::numeric_limits<double>::quiet_NaN()));
  double elapsed = -1.;
  assert(fixturePlaybackElapsed(1000000000LL, 1000000000LL, 1000000000LL, &elapsed));
  assert(elapsed == 0.);  // 重复读取同一步不推进，更不能按现实秒追赶。
  assert(fixturePlaybackElapsed(1000000000LL, 1000000000LL, 1016666667LL, &elapsed));
  assert(std::abs(elapsed - .016666667) < 1e-12);
  assert(fixturePlaybackElapsed(1000000000LL, 1016666667LL, 2000000000LL, &elapsed));
  assert(elapsed == 1.);  // 现实时间无论多久，只有1个物理秒才推进1个规划秒。
  assert(!fixturePlaybackElapsed(0, 0, 1, &elapsed));
  assert(!fixturePlaybackElapsed(2, 1, 3, &elapsed));
  assert(!fixturePlaybackElapsed(1, 3, 2, &elapsed));  // reset/回退拒绝。
  assert(!fixturePlaybackElapsed(1, 1, 2, nullptr));
  assert(validSideFixtureRoll(-15.0));
  assert(validSideFixtureRoll(0.0));
  assert(validSideFixtureRoll(-30.0) && validSideFixtureRoll(30.0));
  assert(!validSideFixtureRoll(30.000001));
  assert(!validSideFixtureRoll(-30.000001));
  assert(!validSideFixtureRoll(std::numeric_limits<double>::infinity()));
  assert(!validSideFixtureRoll(std::numeric_limits<double>::quiet_NaN()));
  for (std::size_t index = 0; index < 8; ++index)
  {
    assert(dualFixtureRequired(index) == (index < 3));
    assert(preciseSingleFixtureRequired(index) == (index == 3 || index == 4));
    assert(!validDualFixtureContactState(index, false, false));
    assert(!validDualFixtureContactState(index, true, false));
    assert(!validDualFixtureContactState(index, false, true));
    assert(validDualFixtureContactState(index, true, true) == (index < 3));
    assert(!(dualFixtureRequired(index) && preciseSingleFixtureRequired(index)));
  }
}
