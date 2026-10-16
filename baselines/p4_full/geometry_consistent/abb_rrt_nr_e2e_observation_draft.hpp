// Project-owned NR complete-path I/O observation only. DRAFT, never run.
// Reuses the existing exclusive/append/round-trip writer; no model query.
#pragma once
#include "abb_nr_interface_observation_draft.hpp"
#include "abb_rrt_pcs_e2e_observation.hpp"

namespace p4e2e {
inline void observe_nr_reconstruction(const ompl::base::State* a,
        const ompl::base::State* b,
        const std::vector<std::vector<double>>& confs, bool returned) {
    json row = {{"schema", "P4_ABB_RRT_NR_RECONSTRUCTION_DRAFT_V1"},
        {"attempt_index", reconstruction_attempts.size()},
        {"observation", "ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN"},
        {"qa12", q12(a)}, {"qb12", q12(b)},
        {"returned", returned}, {"path_q12", confs}};
    if (reconstruction_fd < 0) throw std::runtime_error("RECONSTRUCTION_LOG_NOT_OPEN");
    append(reconstruction_fd, row.dump() + "\n");
    reconstruction_attempts.push_back(std::move(row));
}
} // namespace p4e2e
