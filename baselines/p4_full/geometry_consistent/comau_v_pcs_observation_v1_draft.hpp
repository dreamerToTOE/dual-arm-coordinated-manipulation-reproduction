// Project-owned V local-PCS observation. DRAFT, unbuilt and unqualified.
// Both binaries enforce the same counters/caps and retain the same JSON data.
// P4V_TRACE_MODE changes stderr events only. No observer FK/IK/RNG calls.
#pragma once
#include <PQP.h>
#include <nlohmann/json.hpp>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

#ifndef P4V_TRACE_MODE
#error P4V_TRACE_MODE_must_be_explicitly_frozen_as_zero_or_one
#endif
static_assert(P4V_TRACE_MODE == 0 || P4V_TRACE_MODE == 1);

namespace p4vpcs {
using json = nlohmann::json;
using Count = std::uint64_t;
inline std::map<std::string, Count> caps, counts;
inline Count serial = 0;
inline bool configured = false;
inline json records = json::array(), poses = json::array(), pairs = json::array();
inline json box_pose = nullptr;

inline void event(const json& value) {
    if constexpr (P4V_TRACE_MODE == 1)
        std::cerr << "P4_V_PCS_TRACE " << value.dump() << '\n';
}
inline void configure(const json& values) {
    if (configured) throw std::runtime_error("CAPS_ALREADY_FROZEN");
    const std::vector<std::string> required = {
        "public_request", "project_fixed", "identify", "is_valid_rbs", "rbs",
        "reconstruct", "native_fk", "native_ik", "specific_ik", "limits",
        "collision", "pqp", "mesh_load", "records"};
    if (!values.is_object() || values.size() != required.size())
        throw std::runtime_error("EXACT_CAP_KEY_SET_REQUIRED");
    for (const auto& name : required) {
        if (!values.contains(name) || !values.at(name).is_number_unsigned())
            throw std::runtime_error("UNSIGNED_FROZEN_CAP_REQUIRED_" + name);
        auto cap = values.at(name).get<Count>();
        if (!cap || cap > 1000000) throw std::runtime_error("INVALID_CAP_" + name);
        caps[name] = cap;
    }
    configured = true;
}
inline Count enter(const std::string& kind, const json& args) {
    if (!configured || !caps.count(kind))
        throw std::runtime_error("UNCONFIGURED_SOURCE_COUNTER_" + kind);
    if (counts[kind] >= caps.at(kind) || counts["records"] >= caps.at("records")) {
        event({{"event", "cap_reached"}, {"kind", kind}, {"counts", counts}});
        throw std::runtime_error("SOURCE_CALL_CAP_" + kind);
    }
    ++counts[kind];
    // Reserve one retained record BEFORE the scientific entry. A throw inside
    // an author call leaves this entered record intact in the retained prefix.
    ++counts["records"];
    auto id = ++serial;
    json row = {{"event", "entered"}, {"id", id}, {"kind", kind}, {"args", args}};
    records.push_back(row); event(row); return id;
}
inline void leave(Count id, const std::string& kind, const json& result) {
    if (!id || id > records.size() || records.at(id - 1).at("kind") != kind)
        throw std::runtime_error("OBSERVATION_LIFETIME_MISMATCH");
    records.at(id - 1)["event"] = "completed";
    records.at(id - 1)["result"] = result;
    event({{"event", "completed"}, {"id", id}, {"kind", kind}, {"result", result}});
}
inline void aborted(Count id, const std::string& kind, const json& prefix) {
    if (!id || id > records.size() || records.at(id - 1).at("kind") != kind)
        throw std::runtime_error("OBSERVATION_ABORT_LIFETIME_MISMATCH");
    records.at(id - 1)["event"] = "aborted_retained_prefix";
    records.at(id - 1)["retained_prefix"] = prefix;
    event({{"event", "aborted_retained_prefix"}, {"id", id}, {"kind", kind}, {"retained_prefix", prefix}});
}
inline json joined(const std::vector<double>& a, const std::vector<double>& b) {
    auto q = a; q.insert(q.end(), b.begin(), b.end()); return q;
}
inline json pose(PQP_REAL r[3][3], PQP_REAL t[3], double local_x = 0) {
    json matrix = json::array();
    for (int i = 0; i < 3; ++i)
        matrix.push_back({r[i][0], r[i][1], r[i][2], t[i] + local_x * r[i][0]});
    matrix.push_back({0, 0, 0, 1}); return matrix;
}
inline void begin_collision() {
    poses = json::array(); pairs = json::array(); box_pose = nullptr;
}
inline void capture_box(PQP_REAL r[3][3], PQP_REAL t[3]) { box_pose = pose(r, t); }
inline json collision_result(int returned) {
    return {{"returned", returned}, {"physical_tcp_poses", poses},
            {"source_box_pose", box_pose}, {"active_pairs", pairs},
            {"policy", "V_ALIGNED_V3_SOURCE_87_PAIRS_8MM"},
            {"continuous_collision_checked", false}};
}
}  // namespace p4vpcs

// Existing collision-v3 observation ABI. These are arithmetic copies only.
inline void p4_pose(PQP_REAL r[3][3], PQP_REAL t[3], double local_x) {
    p4vpcs::poses.push_back(p4vpcs::pose(r, t, local_x));
}
inline int p4_query_named(const char* first, const char* second,
                         PQP_ToleranceResult* result,
                         PQP_REAL r1[3][3], PQP_REAL t1[3], PQP_Model* a,
                         PQP_REAL r2[3][3], PQP_REAL t2[3], PQP_Model* b,
                         PQP_REAL tolerance, int queue_size = 2) {
    auto id = p4vpcs::enter("pqp", {{"first", first}, {"second", second},
        {"pair_index", p4vpcs::pairs.size()}, {"tolerance_mm", tolerance},
        {"queue_size", queue_size}});
    const int code = PQP_Tolerance(result, r1, t1, a, r2, t2, b, tolerance, queue_size);
    // API return code zero does not mean collision clear. Keep the actual
    // predicate used by the original author's aggregate collision decision.
    const bool closer = result->CloserThanTolerance();
    p4vpcs::json row = {{"first", first}, {"second", second},
        {"pair_index", p4vpcs::pairs.size()}, {"tolerance_mm", tolerance},
        {"queue_size", queue_size}, {"api_code", code},
        {"closer_than_tolerance", closer}};
    p4vpcs::pairs.push_back(row); p4vpcs::leave(id, "pqp", row); return code;
}
