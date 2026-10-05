#include "fr3_dual_palletize/dual_fixture_policy.hpp"
#include <cassert>

int main()
{
  using namespace fr3_dual_palletize;
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
