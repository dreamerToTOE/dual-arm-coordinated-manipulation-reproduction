#pragma once
// [THIN_ADAPTER] Reuse TASK05's complete NR/RBS/FCL evidence serializers unchanged.
#include "baselines/p4_closed_chain/constrained_rrtconnect.hpp"
#include "platforms/offline_moveit/task05_local_connection/evidence.hpp"

namespace task06_offline
{
using Json=nlohmann::json;
using task05_offline::vectorJson;
using task05_offline::projectionJson;
using task05_offline::connectionJson;

inline Json jointArrayJson(const std::vector<p4::JointVector>& points)
{
  Json result=Json::array(); for(const auto& q:points) result.push_back(vectorJson(q)); return result;
}
inline Json countersJson(const p4::PlannerCounters& c)
{
  return {{"iterations",c.iterations},{"samples",c.samples},{"rng_draws",c.rng_draws},
    {"nearest_queries",c.nearest_queries},{"nearest_distance_evaluations",c.nearest_distance_evaluations},
    {"growth_attempts",c.growth_attempts},{"candidate_projection_calls",c.candidate_projection_calls},
    {"candidate_projection_failures",c.candidate_projection_failures},
    {"projection_jump_rejections",c.projection_jump_rejections},
    {"extension_jump_rejections",c.extension_jump_rejections},{"no_progress_rejections",c.no_progress_rejections},
    {"invalid_candidate_rejections",c.invalid_candidate_rejections},
    {"root_connection_calls",c.root_connection_calls},{"tree_edge_connection_calls",c.tree_edge_connection_calls},
    {"local_connection_rejections",c.local_connection_rejections},
    {"rbs_midpoint_projection_calls",c.rbs_midpoint_projection_calls},
    {"rbs_midpoint_projection_failures",c.rbs_midpoint_projection_failures},
    {"collision_queries",c.collision_queries},{"collision_positive_queries",c.collision_positive_queries},
    {"collision_unavailable_queries",c.collision_unavailable_queries},
    {"constraint_evaluations",c.constraint_evaluations},{"margin_evaluations",c.margin_evaluations},
    {"accepted_start_edges",c.accepted_start_edges},{"accepted_goal_edges",c.accepted_goal_edges}};
}
inline Json optionsJson(const p4::PlannerOptions& o)
{
  const auto& l=o.local_connection; const auto& p=l.projection;
  return {{"seed",o.seed},{"raw_steer_range_rad",o.raw_steer_range_rad},
    {"candidate_projection_correction_l2_limit_rad",o.candidate_projection_correction_l2_limit_rad},
    {"accepted_extension_l2_limit_rad",o.accepted_extension_l2_limit_rad},
    {"minimum_progress_rad",o.minimum_progress_rad},{"extend_attempts",o.extend_attempts},
    {"connect_attempts",o.connect_attempts},{"max_nodes",o.max_nodes},{"max_iterations",o.max_iterations},
    {"max_compute_wall_sec",o.max_compute_wall_sec},
    {"local_connection",{{"leaf_resolution_rad",l.leaf_resolution_rad},
      {"adjacent_l2_limit_rad",l.adjacent_l2_limit_rad},
      {"adjacent_max_abs_limit_rad",l.adjacent_max_abs_limit_rad},
      {"projection_correction_limit_rad",l.projection_correction_limit_rad},
      {"max_depth",l.max_depth},{"max_projections",l.max_projections},{"max_path_points",l.max_path_points},
      {"projection",{{"position_tolerance_m",p.position_tolerance_m},
        {"rotation_tolerance_rad",p.rotation_tolerance_rad},{"max_iterations",p.max_iterations},
        {"svd_absolute_cutoff",p.svd_absolute_cutoff},{"svd_relative_cutoff",p.svd_relative_cutoff},
        {"stagnation_step_rad",p.stagnation_step_rad}}}}}};
}
inline Json nodesJson(const std::vector<p4::PlannerNode>& nodes)
{
  Json result=Json::array();
  for(std::size_t k=0;k<nodes.size();++k)
  {
    const auto& n=nodes[k];
    result.push_back({{"node_index",k},{"q_rad",vectorJson(n.q)},
      {"parent",n.parent?Json(*n.parent):Json(nullptr)},
      {"incoming_attempt",n.incoming_attempt?Json(*n.incoming_attempt):Json(nullptr)}});
  }
  return result;
}
inline Json pathEdgesJson(const std::vector<p4::PlannerPathEdge>& edges)
{
  Json result=Json::array();
  for(const auto& e:edges)
    result.push_back({{"tree",p4::statusName(e.tree)},{"parent",e.parent},{"child",e.child},
      {"attempt",e.attempt},{"reversed",e.reversed}});
  return result;
}
inline Json pathMetricsJson(const p4::PlannerPathMetrics& m)
{
  return {{"joint_path_length_rad",m.joint_path_length_rad},
    {"milestone_path_length_rad",m.milestone_path_length_rad},
    {"maximum_position_residual_m",m.maximum_position_residual_m},
    {"rms_position_residual_m",m.rms_position_residual_m},
    {"maximum_rotation_residual_rad",m.maximum_rotation_residual_rad},
    {"rms_rotation_residual_rad",m.rms_rotation_residual_rad},
    {"minimum_native_joint_margin_rad",m.minimum_native_joint_margin_rad},
    {"maximum_adjacent_l2_rad",m.maximum_adjacent_l2_rad},
    {"maximum_adjacent_max_abs_rad",m.maximum_adjacent_max_abs_rad},
    {"minimum_collision_distance_m",nullptr},
    {"minimum_collision_distance_status","UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED"}};
}
inline Json attemptDecisionsJson(const p4::PlannerAttempt& a)
{
  return {{"tree",p4::statusName(a.tree)},{"mode",p4::statusName(a.mode)},
    {"iteration",a.iteration},{"growth_attempt",a.growth_attempt},{"nearest_node",a.nearest_node},
    {"raw_target_rad",vectorJson(a.raw_target)},{"raw_steer_rad",vectorJson(a.raw_steer)},
    {"target_is_existing",a.target_is_existing},{"raw_target_within_range",a.raw_target_within_range},
    {"reached",a.reached},{"candidate_rad",a.candidate?vectorJson(*a.candidate):Json(nullptr)},
    {"projection_correction_l2_rad",a.projection_correction_l2_rad?Json(*a.projection_correction_l2_rad):Json(nullptr)},
    {"accepted_extension_l2_rad",a.accepted_extension_l2_rad?Json(*a.accepted_extension_l2_rad):Json(nullptr)},
    {"added_node",a.added_node?Json(*a.added_node):Json(nullptr)},
    {"status",p4::statusName(a.status)},{"reason",a.reason}};
}
inline Json plannerJson(const p4::PlannerResult& r)
{
  Json attempts=Json::array(),dense_evidence=Json::array();
  for(std::size_t k=0;k<r.attempts.size();++k)
  {
    const auto& a=r.attempts[k]; Json row=attemptDecisionsJson(a); row["attempt_index"]=k;
    row["projection"]=a.projection?projectionJson(*a.projection):Json(nullptr);
    row["connection"]=a.connection?connectionJson(*a.connection):Json(nullptr);
    attempts.push_back(std::move(row));
  }
  for(const auto& p:r.dense_path_evidence)
    dense_evidence.push_back({{"q_rad",vectorJson(p.q)},{"tree",p4::statusName(p.tree)},
      {"attempt",p.attempt?Json(*p.attempt):Json(nullptr)},{"checked_point",p.checked_point}});
  return {{"schema","task06.offline_constrained_rrtconnect.v1"},
    {"status",p4::statusName(r.status)},{"reason",r.reason},{"seed",r.seed},
    {"requested_start_rad",vectorJson(r.requested_start)},{"requested_goal_rad",vectorJson(r.requested_goal)},
    {"native_lower_rad",vectorJson(r.native_lower)},{"native_upper_rad",vectorJson(r.native_upper)},
    {"options",r.options?optionsJson(*r.options):Json(nullptr)},
    {"start_root",r.start_root?connectionJson(*r.start_root):Json(nullptr)},
    {"goal_root",r.goal_root?connectionJson(*r.goal_root):Json(nullptr)},
    {"sampled_targets_rad",jointArrayJson(r.sampled_targets)},
    {"start_tree",nodesJson(r.start_tree)},{"goal_tree",nodesJson(r.goal_tree)},{"attempts",attempts},
    {"meeting_start_node",r.meeting_start_node?Json(*r.meeting_start_node):Json(nullptr)},
    {"meeting_goal_node",r.meeting_goal_node?Json(*r.meeting_goal_node):Json(nullptr)},
    {"path_edges",pathEdgesJson(r.path_edges)},{"path_milestones_rad",jointArrayJson(r.path_milestones)},
    {"dense_path_rad",jointArrayJson(r.dense_path)},{"dense_path_evidence",dense_evidence},
    {"failed_prefix_attempt",r.failed_prefix_attempt?Json(*r.failed_prefix_attempt):Json(nullptr)},
    {"failed_prefix_rad",jointArrayJson(r.failed_prefix)},
    {"failed_prefix_qualification","DIAGNOSTIC_LOCAL_PREFIX_NOT_A_SOLUTION_OR_EXECUTABLE_TRAJECTORY"},
    {"counters",countersJson(r.counters)},
    {"path_metrics",r.path_metrics?pathMetricsJson(*r.path_metrics):Json(nullptr)},
    {"compute_wall_time_sec",r.compute_wall_time_sec},
    {"time_qualification","CPU_COMPUTE_NOT_SIMULATION_OR_EXECUTION"},
    {"minimum_distance_status",r.minimum_distance_status},{"minimum_collision_distance_m",nullptr},
    {"simulation_time",nullptr},{"simulation_step",nullptr},
    {"continuous_collision_certificate",false},{"physical_grasp_certificate",false},
    {"benchmark_frozen",false},{"distance_queries_performed",false}};
}

inline Json deterministicProjectionJson(const p4::ProjectionResult& p)
{
  return {{"status",p4::statusName(p.status)},{"reason",p.reason},
    {"initial_q_rad",vectorJson(p.initial_q)},{"projected_q_rad",vectorJson(p.projected_q)},
    {"accepted_updates",p.accepted_updates},{"evaluations",p.evaluations}};
}
inline Json deterministicConnectionJson(const p4::ConnectionResult& c)
{
  Json points=Json::array(),edges=Json::array();
  for(const auto& p:c.checked_points)
    points.push_back({{"q_rad",vectorJson(p.q)},{"role",p.role},{"depth",p.depth},
      {"qualified",p.qualified},{"failure",p.failure},
      {"native_joint_margin_rad",p.joint_margin_rad?Json(*p.joint_margin_rad):Json(nullptr)},
      {"residual",p.residual?task05_offline::residualJson(*p.residual):Json(nullptr)},
      {"projection",p.projection?deterministicProjectionJson(*p.projection):Json(nullptr)},
      {"collision_complete",p.collision?Json(p.collision->complete):Json(nullptr)},
      {"self_collision",p.collision?Json(p.collision->self_collision):Json(nullptr)},
      {"world_collision",p.collision?Json(p.collision->world_collision):Json(nullptr)}});
  for(const auto& e:c.leaf_edges)
    edges.push_back({{"from",e.from},{"to",e.to},{"l2_rad",e.l2_rad},
      {"max_abs_rad",e.max_abs_rad},{"accepted",e.accepted}});
  return {{"status",p4::statusName(c.status)},{"reason",c.reason},
    {"requested_start_rad",vectorJson(c.requested_start)},{"requested_goal_rad",vectorJson(c.requested_goal)},
    {"checked_points",points},{"verified_prefix",c.verified_prefix},{"leaf_edges",edges},
    {"failed_point",c.failed_point?Json(*c.failed_point):Json(nullptr)},
    {"projection_calls",c.projection_calls},{"maximum_depth",c.maximum_depth}};
}
inline Json deterministicJson(const p4::PlannerResult& r)
{
  Json attempts=Json::array();
  for(const auto& a:r.attempts)
  {
    Json row=attemptDecisionsJson(a);
    row["projection"]=a.projection?deterministicProjectionJson(*a.projection):Json(nullptr);
    row["connection"]=a.connection?deterministicConnectionJson(*a.connection):Json(nullptr);
    attempts.push_back(std::move(row));
  }
  // No wall costs or raw contact arrays: search decisions and all q/qualified edges are retained.
  return {{"schema","task06.deterministic_search.v1"},{"status",p4::statusName(r.status)},
    {"reason",r.reason},{"seed",r.seed},
    {"requested_start_rad",vectorJson(r.requested_start)},{"requested_goal_rad",vectorJson(r.requested_goal)},
    {"native_lower_rad",vectorJson(r.native_lower)},{"native_upper_rad",vectorJson(r.native_upper)},
    {"options",r.options?optionsJson(*r.options):Json(nullptr)},
    {"start_root",r.start_root?deterministicConnectionJson(*r.start_root):Json(nullptr)},
    {"goal_root",r.goal_root?deterministicConnectionJson(*r.goal_root):Json(nullptr)},
    {"sampled_targets_rad",jointArrayJson(r.sampled_targets)},
    {"start_tree",nodesJson(r.start_tree)},{"goal_tree",nodesJson(r.goal_tree)},
    {"attempts",attempts},{"counters",countersJson(r.counters)},
    {"meeting_start_node",r.meeting_start_node?Json(*r.meeting_start_node):Json(nullptr)},
    {"meeting_goal_node",r.meeting_goal_node?Json(*r.meeting_goal_node):Json(nullptr)},
    {"path_edges",pathEdgesJson(r.path_edges)},{"path_milestones_rad",jointArrayJson(r.path_milestones)},
    {"dense_path_rad",jointArrayJson(r.dense_path)},
    {"failed_prefix_attempt",r.failed_prefix_attempt?Json(*r.failed_prefix_attempt):Json(nullptr)},
    {"failed_prefix_rad",jointArrayJson(r.failed_prefix)},
    {"path_metrics",r.path_metrics?pathMetricsJson(*r.path_metrics):Json(nullptr)}};
}
} // namespace task06_offline
