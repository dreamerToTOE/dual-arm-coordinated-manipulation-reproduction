// Project-owned JSONL transport for original ABB NR SVC/RBS/reconstruction.
// Link original RRT_NR, but this local driver never allocates or solves it.
// argv: ENVIRONMENT MODE NEW_RUNTIME_WITH_BOUND_SIMULATOR
#include "abb_nr_interface_observation_draft.hpp"
#include "StateValidityCheckerNR.h"
#include <filesystem>
#include <cmath>
#include <memory>

namespace {
class Redirect {
    std::streambuf* old;
public:
    Redirect() : old(std::cout.rdbuf(std::cerr.rdbuf())) {}
    ~Redirect() { std::cout.rdbuf(old); }
};
State finite12(const p4pcs::json& value) {
    State q = value.get<State>();
    if (q.size() != 12) throw std::runtime_error("EXPECTED_Q12");
    for (double v : q) if (!std::isfinite(v)) throw std::runtime_error("NONFINITE_Q12");
    return q;
}
}
int main(int argc, char** argv) {
    if (argc != 4) return 64;
    const std::string env = argv[1], mode = argv[2];
    if ((env != "II" && env != "III") || (mode != "plain" && mode != "trace")) return 64;
    const auto runtime = std::filesystem::absolute(argv[3]);
    if (!std::filesystem::is_directory(runtime / "simulator") || std::filesystem::exists(runtime / "paths"))
        return 64;
    std::filesystem::current_path(runtime);
    p4nr_iface::environment = env;
    std::unique_ptr<StateValidityChecker> checker;
    { Redirect redirect; checker = std::make_unique<StateValidityChecker>(env == "II" ? 1 : 2); }
    checker->initiate_log_parameters();
    p4pcs::enabled = mode == "trace";
    // Per-request external observation caps. They stop with UNKNOWN, not false.
    // The source .05 tolerance, max depth 150, recursion order are unchanged.
    p4pcs::caps = {{"nr_gd", 1024}, {"nr_project", 1}, {"nr_valid_midpoint", 1024},
        {"nr_rbs", 2049}, {"nr_reconstruct", 2049}, {"collision", 1024}, {"pqp", 131072}};
    std::string line;
    while (std::getline(std::cin, line)) {
        p4nr_iface::reset();
        checker->initiate_log_parameters();
        p4pcs::json result = {{"schema", "P4_ABB_NR_THIN_V1"}, {"environment", env},
            {"mode", mode}, {"solve_calls", 0}, {"rng_calls", 0}};
        State retained_q;
        Matrix retained_path;
        bool project_seen = false, reconstruct_seen = false;
        try {
            const auto request = p4pcs::json::parse(line);
            result["request"] = request; result["id"] = request.at("id");
            const auto op = request.at("op").get<std::string>(); result["op"] = op;
            { Redirect redirect;
                if (op == "project_q12") {
                    retained_q = finite12(request.at("q12")); project_seen = true;
                    result["returned"] = checker->IKproject(retained_q, true);
                } else if (op == "rbs" || op == "reconstruct") {
                    const auto qa = finite12(request.at("qa12")), qb = finite12(request.at("qb12"));
                    if (op == "rbs") result["returned"] = checker->checkMotionRBS(qa, qb, 0, 0);
                    else {
                        retained_path = {qa, qb}; reconstruct_seen = true;
                        result["returned"] = checker->reconstructRBS(qa, qb, retained_path, 0, 1, 1);
                    }
                } else throw std::runtime_error("UNKNOWN_LOCAL_OPERATION_NO_SOLVE_ENTRY");
            }
            result["status"] = "SOURCE_CALL_COMPLETED";
        } catch (const std::exception& error) {
            result["status"] = "STOP_RETAINED_PREFIX"; result["error"] = error.what();
        }
        if (project_seen) result["q12"] = retained_q;
        if (reconstruct_seen) result["path_q12"] = retained_path;
        result["observed_counts"] = p4pcs::counts;
        result["gd_completed_candidates"] = p4nr_iface::gd_completed_candidates;
        result["observer_errors"] = p4nr_iface::observer_errors;
        result["source_log_counters"] = {{"IK_counter", checker->get_IK_counter()},
            {"IK_time_cpu_s", checker->get_IK_time()}, {"isValid_counter", checker->get_isValid_counter()},
            {"collisionCheck_counter", checker->get_collisionCheck_counter()},
            {"collisionCheck_time_cpu_s", checker->get_collisionCheck_time()}};
        if (!p4nr_iface::observer_errors.empty()) result["status"] = "STOP_OBSERVER_ERROR_AFTER_SOURCE_RETURN";
        std::cout << "P4_NR_RESPONSE " << result.dump() << std::endl;
        if (result["status"] != "SOURCE_CALL_COMPLETED") return 2;
    }
}
