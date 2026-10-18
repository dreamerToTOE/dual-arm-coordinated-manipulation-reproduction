// Project-owned fixed-input V PCS local transport. DRAFT, never built/run.
// Link the author's byte-identical RRT source, but never instantiate a planner.
#include "comau_v_pcs_observation_v1_draft.hpp"
#include "StateValidityCheckerPCS.h"
#include <cmath>
#include <filesystem>
#include <fstream>
#include <memory>
#include <set>

namespace {
class Redirect {
    std::streambuf* old;
public:
    Redirect() : old(std::cout.rdbuf(std::cerr.rdbuf())) {}
    ~Redirect() { std::cout.rdbuf(old); }
};
State state(const p4vpcs::json& value) {
    auto q = value.get<State>();
    if (q.size() != 12) throw std::runtime_error("EXPECTED_Q12");
    for (double x : q) if (!std::isfinite(x)) throw std::runtime_error("NONFINITE_Q");
    return q;
}
std::pair<State, State> split(const State& q) {
    return {{q.begin(), q.begin() + 6}, {q.begin() + 6, q.end()}};
}
State joined(const State& a, const State& b) {
    State q = a; q.insert(q.end(), b.begin(), b.end()); return q;
}
int integer(const p4vpcs::json& value, const char* field, int high) {
    if (!value.at(field).is_number_integer()) throw std::runtime_error("INTEGER_IDENTITY_REQUIRED");
    int v = value.at(field).get<int>();
    if (v < 0 || v > high) throw std::runtime_error("INVALID_FIXED_IDENTITY");
    return v;
}
struct DependencyFailure : std::runtime_error { using std::runtime_error::runtime_error; };
using Rows = std::map<std::string, p4vpcs::json>;
void validate_branch(const p4vpcs::json& request, const Rows& definitions) {
    const auto& branch = request.at("branch");
    if (branch.is_number_integer()) { integer(request, "branch", 7); return; }
    if (!branch.is_object() || branch.size() != 1 || !branch.contains("from_identify"))
        throw std::runtime_error("FIXED_BRANCH_OR_NAMED_IDENTIFY_REQUIRED");
    auto name = branch.at("from_identify").get<std::string>();
    if (!definitions.count(name) || definitions.at(name).at("op") != "identify")
        throw std::runtime_error("ONLY_PRIOR_NAMED_CENTER_IDENTIFY_ALLOWED");
}
int resolved_branch(const p4vpcs::json& request, const Rows& completed) {
    if (request.at("branch").is_number_integer()) return integer(request, "branch", 7);
    auto name = request.at("branch").at("from_identify").get<std::string>();
    const auto& row = completed.at(name);
    if (!row.contains("returned_ik")) throw DependencyFailure("CENTER_IDENTIFY_NOT_COMPLETED_" + name);
    auto indices = row.at("returned_ik").get<State>();
    int active = integer(request, "active_chain", 1);
    if (indices.size() != 2 || !std::isfinite(indices.at(active)) ||
        indices.at(active) < 0 || indices.at(active) > 7 || std::floor(indices.at(active)) != indices.at(active))
        throw DependencyFailure("CENTER_ROLE_IDENTIFY_FAILED_" + name);
    return static_cast<int>(indices.at(active));
}
State projected_endpoint(const p4vpcs::json& request, const char* field, const Rows& completed) {
    auto name = request.at(field).get<std::string>();
    const auto& row = completed.at(name);
    if (!row.contains("returned") || row.at("returned") != true)
        throw DependencyFailure("FROZEN_PROJECT_DEPENDENCY_FAILED_" + name);
    return state(row.at("q12"));
}
}  // namespace

int main(int argc, char** argv) {
    // No stdin/seed/solve/random or open-ended request loop. The independently
    // frozen local protocol contains the complete ordered request list.
    if (argc != 3) return 64;
    p4vpcs::json output = {{"schema", "P4_D080_V_PCS_LOCAL_DRAFT_V1"},
        {"environment", "V"}, {"trace_enabled", P4V_TRACE_MODE == 1},
        {"solve_calls", 0}, {"rng_calls", 0}, {"continuous_collision_checked", false},
        {"status", "NOT_STARTED"}};
    std::size_t emitted_records = 0;
    try {
        std::ifstream stream(argv[2]);
        if (!stream) throw std::runtime_error("LOCAL_PROTOCOL_REQUIRED");
        p4vpcs::json protocol; stream >> protocol;
        if (protocol.at("schema") != "P4_D080_V_PCS_LOCAL_FROZEN_V1" ||
            protocol.at("environment") != "V" || protocol.at("method") != "PCS" ||
            protocol.at("frozen") != true || protocol.at("scientific_execution_authorized") != true ||
            protocol.at("independent_review_passed") != true || protocol.at("api_local_only") != true)
            throw std::runtime_error("FROZEN_INDEPENDENTLY_REVIEWED_LOCAL_AUTHORIZATION_REQUIRED");
        const auto& requests = protocol.at("requests");
        if (!requests.is_array() || requests.empty()) throw std::runtime_error("COMPLETE_FIXED_REQUESTS_REQUIRED");
        p4vpcs::configure(protocol.at("caps"));
        if (requests.size() > p4vpcs::caps.at("public_request"))
            throw std::runtime_error("REQUESTS_EXCEED_FROZEN_CAP");
        // Validate ALL shapes/operations/identities before constructor loading
        // and before any science call; reject malformed late rows in advance.
        std::set<std::string> ids; Rows definitions;
        for (const auto& request : requests) {
            const auto id = request.at("id").get<std::string>();
            if (id.empty() || !ids.insert(id).second) throw std::runtime_error("UNIQUE_NONEMPTY_REQUEST_ID_REQUIRED");
            const auto op = request.at("op").get<std::string>();
            if (op == "identify" || op == "limits") state(request.at("q12"));
            else if (op == "project" || op == "rbs" || op == "reconstruct") {
                integer(request, "active_chain", 1); validate_branch(request, definitions);
                if (op == "project") state(request.at("q12"));
                else for (const auto field : {"qa_from_project", "qb_from_project"}) {
                    auto name = request.at(field).get<std::string>();
                    if (!definitions.count(name) || definitions.at(name).at("op") != "project" ||
                        definitions.at(name).at("active_chain") != request.at("active_chain") ||
                        definitions.at(name).at("branch") != request.at("branch"))
                        throw std::runtime_error("ONLY_PRIOR_FROZEN_SAME_ROLE_BRANCH_PROJECT_ENDPOINTS_ALLOWED");
                }
            } else throw std::runtime_error("UNSUPPORTED_LOCAL_OPERATION");
            definitions.emplace(id, request);
        }
        std::filesystem::current_path(argv[1]);
        std::unique_ptr<StateValidityChecker> checker;
        { Redirect redirect; checker = std::make_unique<StateValidityChecker>(1); }
        checker->initiate_log_parameters();
        output["status"] = "SETUP_COMPLETED";
        output["observed_records"] = p4vpcs::records;
        output["observed_counts_cumulative"] = p4vpcs::counts;
        std::cout << output.dump() << std::endl;
        emitted_records = p4vpcs::records.size();
        Rows completed;
        for (const auto& request : requests) {
            output.erase("observed_records"); output["request"] = request;
            output["status"] = "SOURCE_CALL_ENTERED";
            auto token = p4vpcs::enter("public_request", request);
            const auto op = request.at("op").get<std::string>();
            p4vpcs::json result;
            try {
            if (op == "limits") result["source_limits_legal"] = checker->check_angle_limits(state(request.at("q12")));
            else if (op == "identify") {
                auto [a, b] = split(state(request.at("q12")));
                result["returned_ik"] = checker->identify_state_ik(a, b, {-1, -1});
            } else {
                int active = integer(request, "active_chain", 1), branch = resolved_branch(request, completed);
                result["resolved_branch"] = branch;
                if (op == "project") {
                    auto [a, b] = split(state(request.at("q12")));
                    result["returned"] = checker->IKproject(a, b, active, branch);
                    result["q12"] = joined(a, b);
                } else {
                    auto qa = projected_endpoint(request, "qa_from_project", completed);
                    auto qb = projected_endpoint(request, "qb_from_project", completed);
                    result["resolved_qa12"] = qa; result["resolved_qb12"] = qb;
                    auto [a, b] = split(qa); auto [c, d] = split(qb);
                    Matrix path = {qa, qb};
                    if (op == "rbs") result["returned"] = checker->checkMotionRBS(a, b, c, d, active, branch, 0, 0);
                    else {
                        result["returned"] = checker->reconstructRBS(a, b, c, d, active, branch, path, 0, 1, 1);
                        result["path_q12"] = path;
                    }
                }
            }
            } catch (const DependencyFailure& failure) {
                result["status"] = "NOT_EXECUTED_DEPENDENCY_FAILED";
                result["reason"] = failure.what(); result["source_call_started"] = false;
            }
            p4vpcs::leave(token, "public_request", result);
            completed.emplace(request.at("id").get<std::string>(), result);
            output["result"] = result;
            output["status"] = result.value("status", std::string("SOURCE_CALL_COMPLETED"));
            output["observed_records"] = p4vpcs::json::array();
            for (; emitted_records < p4vpcs::records.size(); ++emitted_records)
                output["observed_records"].push_back(p4vpcs::records.at(emitted_records));
            output["observed_counts_cumulative"] = p4vpcs::counts;
            std::cout << output.dump() << std::endl;
        }
        return 0;
    } catch (const std::exception& error) {
        output.erase("result"); output["status"] = "STOP_RETAINED_PREFIX"; output["error"] = error.what();
        output["observed_records"] = p4vpcs::json::array();
        for (; emitted_records < p4vpcs::records.size(); ++emitted_records)
            output["observed_records"].push_back(p4vpcs::records.at(emitted_records));
        output["observed_counts_cumulative"] = p4vpcs::counts;
        std::cout << output.dump() << std::endl; return 2;
    }
}
