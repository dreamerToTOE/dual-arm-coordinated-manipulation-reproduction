// Unique numerical translation unit; immutable already-Q1-qualified core.
#include "abb_nr_interface_observation_draft.hpp"
#include "physical_nr_abb_cpp_draft.hpp"

namespace p4nr_iface {
std::vector<double> array(const p4nr_draft::Vector& value) {
    return {value.data(), value.data() + value.size()};
}
bool physical_gd(const std::vector<double>& input, double d, double rod_l,
                        bool include_limits, std::vector<double>& solution,
                        int& counter, double& measured_cpu) {
    if (!((environment == "II" && d == 900. && rod_l == 300.) ||
          (environment == "III" && d == 1200. && rod_l == 500.)) || !include_limits)
        throw std::runtime_error("FROZEN_PHYSICAL_NR_ENVIRONMENT_AND_LIMITS_REQUIRED");
    auto id = p4pcs::enter("nr_gd", {{"input_q12", input}});
    ++counter;
    const clock_t begun = clock();
    p4nr_draft::Vector q(input.size());
    for (std::size_t i = 0; i < input.size(); ++i) q[i] = input[i];
    // Identical already-Q1-qualified kernel/options in plain and trace.
    // Wall resource stop is not a new NR iteration/convergence parameter.
    p4nr_draft::Options options;
    options.detailed_trace = false;
    auto answer = p4nr_draft::project_nr(q, environment, options);
    measured_cpu += double(clock() - begun) / CLOCKS_PER_SEC;
    const bool returned = answer.status == "CONVERGED";
    if (returned) solution = array(answer.candidate_q_rad);
    if (p4pcs::enabled) {
        try {
            json row = {{"input_q12", input}, {"status", answer.status},
                {"returned", returned}, {"candidate_is_finite", answer.candidate_is_finite},
                {"candidate_q12", answer.candidate_is_finite ? json(array(answer.candidate_q_rad)) : json(nullptr)},
                {"accepted_updates", answer.accepted_updates}, {"wall_s", answer.wall_s},
                {"metrics", answer.has_metrics ? json({
                    {"translation_max_abs", answer.metrics.translation_max_abs},
                    {"rotation_matrix_max_abs", answer.metrics.rotation_matrix_max_abs},
                    {"rotation_angle_max_rad", answer.metrics.rotation_angle_max_rad},
                    {"position_unit", "mm"}}) : json(nullptr)}};
            gd_completed_candidates.push_back(row);
            leave(id, "nr_gd", row);
        } catch (const std::exception& error) { observer_errors.push_back(error.what()); }
    }
    return returned;
}
} // namespace p4nr_iface
