// Project-owned thin GD seam and observation. No author algorithm body.
// Only the isolated build recipe may insert the seam into kdl::GD.
#pragma once
#include "pcs_source_trace.hpp"
#include <ctime>

namespace p4nr_iface {
using json = p4pcs::json;
inline std::string environment;
inline json gd_completed_candidates = json::array();
inline std::vector<std::string> observer_errors;
inline void reset() {
    p4pcs::reset(); gd_completed_candidates = json::array(); observer_errors.clear();
}
inline void leave(unsigned long id, const std::string& kind, const json& result) {
    try { p4pcs::leave(id, kind, result); }
    catch (const std::exception& error) { observer_errors.push_back(error.what()); }
}
bool physical_gd(const std::vector<double>& input, double d, double rod_l,
                 bool include_limits, std::vector<double>& solution,
                 int& counter, double& measured_cpu);
} // namespace p4nr_iface
