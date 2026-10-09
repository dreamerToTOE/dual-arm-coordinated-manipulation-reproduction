#pragma once
// [THIN_ADAPTER] 沿用TASK04完整history JSON组织；只记录数学/原生FCL证据。
#include "baselines/p4_closed_chain/local_connection.hpp"
#include <nlohmann/json.hpp>

namespace task05_offline
{
using Json=nlohmann::json;
template<class D> Json vectorJson(const Eigen::MatrixBase<D>& v)
{
  Json j=Json::array(); for(Eigen::Index i=0;i<v.size();++i) j.push_back(v(i)); return j;
}
inline Json residualJson(const p4::Residual& r)
{
  return {{"position_vector_world_m",vectorJson(r.head<3>())},
    {"rotation_log_right_object_rad",vectorJson(r.tail<3>())},
    {"position_norm_m",r.head<3>().norm()},{"rotation_norm_rad",r.tail<3>().norm()}};
}
inline Json projectionJson(const p4::ProjectionResult& p)
{
  Json history=Json::array();
  for(const auto& s:p.history)
  {
    Json row={{"update_index",s.update_index},{"q_before_rad",vectorJson(s.q_before)},
      {"residual_before",residualJson(s.residual_before)},
      {"joint_margin_before_rad",s.joint_margin_before_rad},{"numerical_rank",s.numerical_rank},
      {"singular_values",s.singular_values?vectorJson(*s.singular_values):Json(nullptr)},
      {"singular_cutoff",s.singular_cutoff?Json(*s.singular_cutoff):Json(nullptr)},
      {"proposed_delta_q_rad",s.proposed_delta_q?vectorJson(*s.proposed_delta_q):Json(nullptr)},
      {"proposed_q_rad",s.proposed_q?vectorJson(*s.proposed_q):Json(nullptr)},
      {"candidate_joint_margin_rad",s.candidate_joint_margin_rad?Json(*s.candidate_joint_margin_rad):Json(nullptr)},
      {"residual_after",s.residual_after?residualJson(*s.residual_after):Json(nullptr)},
      {"update_accepted",s.update_accepted},{"note",s.note}};
    history.push_back(std::move(row));
  }
  return {{"status",p4::statusName(p.status)},{"reason",p.reason},
    {"initial_q_rad",vectorJson(p.initial_q)},{"projected_q_rad",vectorJson(p.projected_q)},
    {"initial_residual",p.initial_residual?residualJson(*p.initial_residual):Json(nullptr)},
    {"final_residual",p.final_residual?residualJson(*p.final_residual):Json(nullptr)},
    {"accepted_updates",p.accepted_updates},{"evaluations",p.evaluations},
    {"joint_delta_norm_rad",p.joint_delta_norm_rad?Json(*p.joint_delta_norm_rad):Json(nullptr)},
    {"joint_delta_max_abs_rad",p.joint_delta_max_abs_rad?Json(*p.joint_delta_max_abs_rad):Json(nullptr)},
    {"compute_wall_time_sec",p.compute_wall_time_sec},{"history",history}};
}
inline Json collisionJson(const p4::CollisionEvidence& c)
{
  Json contacts=Json::array();
  for(const auto& p:c.contacts)
    contacts.push_back({{"body_a",p.body_a},{"body_b",p.body_b},{"category",p.category},
      {"position_world_m",vectorJson(p.position_world_m)},
      {"penetration_depth_m",p.penetration_depth_m}});
  return {{"complete",c.complete},{"self_collision",c.self_collision},
    {"world_collision",c.world_collision},{"backend",c.backend},{"reason",c.reason},
    {"acm_identity",c.acm_identity},{"contacts",contacts}};
}
inline Json connectionJson(const p4::ConnectionResult& r)
{
  Json points=Json::array(),edges=Json::array();
  for(const auto& p:r.checked_points)
    points.push_back({{"q_rad",vectorJson(p.q)},{"role",p.role},{"depth",p.depth},
      {"qualified",p.qualified},{"failure",p.failure},
      {"native_joint_margin_rad",p.joint_margin_rad?Json(*p.joint_margin_rad):Json(nullptr)},
      {"residual",p.residual?residualJson(*p.residual):Json(nullptr)},
      {"collision",p.collision?collisionJson(*p.collision):Json(nullptr)},
      {"projection",p.projection?projectionJson(*p.projection):Json(nullptr)},
      {"projection_correction_l2_rad",p.projection_correction_l2_rad?Json(*p.projection_correction_l2_rad):Json(nullptr)}});
  for(const auto& e:r.leaf_edges)
    edges.push_back({{"from_checked_index",e.from},{"to_checked_index",e.to},
      {"joint_l2_rad",e.l2_rad},{"joint_max_abs_rad",e.max_abs_rad},{"accepted",e.accepted}});
  return {{"status",p4::statusName(r.status)},{"reason",r.reason},
    {"requested_start_rad",vectorJson(r.requested_start)},{"requested_goal_rad",vectorJson(r.requested_goal)},
    {"checked_points",points},{"verified_prefix_indices",r.verified_prefix},
    {"leaf_edges",edges},{"failed_point_index",r.failed_point?Json(*r.failed_point):Json(nullptr)},
    {"projection_calls",r.projection_calls},{"maximum_depth",r.maximum_depth},
    {"compute_wall_time_sec",r.compute_wall_time_sec},
    {"time_qualification","CPU_COMPUTE_NOT_SIMULATION_OR_EXECUTION"},
    {"continuous_collision_certificate",false},{"physical_grasp_certificate",false}};
}
} // namespace task05_offline
