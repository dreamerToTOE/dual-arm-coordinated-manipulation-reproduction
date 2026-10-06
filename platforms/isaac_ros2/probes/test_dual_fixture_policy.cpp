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
