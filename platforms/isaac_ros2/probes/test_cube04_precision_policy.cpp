#include "fr3_dual_palletize/cube04_precision_policy.hpp"
#include <cassert>
#include <cmath>

int main()
{
  using namespace fr3_dual_palletize;
  for (std::size_t index = 0; index < 5; ++index)
  {
    assert(precisionSingleInsert(index) == (index == 3 || index == 4));
    assert(requiresInnerTrim(index) == (index == 2));
    assert(std::abs(stagingGap(index, 0.0015, 0.0005) -
      (index == 3 ? 0.0005 : 0.0015)) < 1e-12);
  }
  assert(!precisionSingleInsert(5));
  assert(!requiresInnerTrim(5));
}
