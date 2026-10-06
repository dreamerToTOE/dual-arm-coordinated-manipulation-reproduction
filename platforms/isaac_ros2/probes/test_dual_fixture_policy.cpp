#include "fr3_dual_palletize/dual_fixture_policy.hpp"
#include <cassert>
#include <limits>

int main()
{
  using namespace fr3_dual_palletize;
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
