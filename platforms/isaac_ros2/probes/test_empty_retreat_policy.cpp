#include "fr3_dual_palletize/empty_retreat_policy.hpp"
#include <cassert>
#include <limits>

int main()
{
  using namespace fr3_dual_palletize;
  assert(emptyRetreatSegmentCount(0.0, 0.0) == 1);
  assert(emptyRetreatSegmentCount(0.02, 0.0) == 10);
  assert(emptyRetreatSegmentCount(0.6, 0.0) == 300);
  assert(emptyRetreatSegmentCount(0.01, 0.1) == 10);
  assert(emptyRetreatSegmentCount(0.60001, 0.0) == 0);
  assert(emptyRetreatSegmentCount(-0.1, 0.0) == 0);
  assert(emptyRetreatSegmentCount(0.1, 3.15) == 0);
  assert(emptyRetreatSegmentCount(std::numeric_limits<double>::quiet_NaN(), 0.0) == 0);
  const std::vector<double> q(7, 0.0);
  assert(validEmptyRetreatSeed(false, false, q, q, 7, 7));
  assert(!validEmptyRetreatSeed(true, false, q, q, 7, 7));
  assert(!validEmptyRetreatSeed(false, true, q, q, 7, 7));
  assert(!validEmptyRetreatSeed(false, false, {}, q, 7, 7));
  assert(!validEmptyRetreatSeed(false, false, q, q, 6, 7));
  auto invalid = q;
  invalid[2] = std::numeric_limits<double>::infinity();
  assert(!validEmptyRetreatSeed(false, false, invalid, q, 7, 7));
}
