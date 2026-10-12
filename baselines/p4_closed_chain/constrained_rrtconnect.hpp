#pragma once
// [ORIGINAL] source-audited P4 NR bidirectional growth order, independently implemented.
// [ADAPTATION] unchanged TASK03/04/05 callbacks; [ENGINEERING] explicit finite guards/evidence.
#include "baselines/p4_closed_chain/local_connection.hpp"
#include <cstdint>

namespace p4
{
struct PlannerOptions
{
  LocalConnectionOptions local_connection;
  std::uint64_t seed;
  double raw_steer_range_rad;
  double candidate_projection_correction_l2_limit_rad;
  double accepted_extension_l2_limit_rad;
  double minimum_progress_rad;
  std::size_t extend_attempts, connect_attempts, max_nodes, max_iterations;
  double max_compute_wall_sec;
};

enum class PlannerStatus
{
  SUCCESS, INVALID_OPTIONS, INVALID_INPUT, START_REJECTED, GOAL_REJECTED,
  ITERATION_LIMIT, NODE_LIMIT, TIME_LIMIT, INTERNAL_ERROR
};
enum class PlannerTree { START, GOAL };
enum class GrowthMode { EXTEND, CONNECT };
enum class AttemptStatus
{
  ACCEPTED, PROJECTION_FAILED, PROJECTION_JUMP, EXTENSION_JUMP, NO_PROGRESS,
  CONNECTION_REJECTED, NODE_LIMIT, TIME_LIMIT, INVALID_CANDIDATE
};
const char* statusName(PlannerStatus);
const char* statusName(PlannerTree);
const char* statusName(GrowthMode);
const char* statusName(AttemptStatus);

struct PlannerNode
{
  JointVector q{JointVector::Zero()};
  // Indices are local to this node's tree; incoming_attempt indexes PlannerResult::attempts.
  std::optional<std::size_t> parent, incoming_attempt;
};
struct PlannerAttempt
{
  PlannerTree tree{PlannerTree::START};
  GrowthMode mode{GrowthMode::EXTEND};
  std::size_t iteration{0}, growth_attempt{0}, nearest_node{0};
  JointVector raw_target{JointVector::Zero()}, raw_steer{JointVector::Zero()};
  bool target_is_existing{false}, raw_target_within_range{false}, reached{false};
  std::optional<JointVector> candidate;
  std::optional<ProjectionResult> projection;
  std::optional<ConnectionResult> connection;
  std::optional<double> projection_correction_l2_rad, accepted_extension_l2_rad;
  std::optional<std::size_t> added_node;
  AttemptStatus status{AttemptStatus::INVALID_CANDIDATE};
  std::string reason;
};
struct PlannerPathEdge
{
  PlannerTree tree;
  std::size_t parent, child, attempt;
  // Goal-tree evidence is stored root->child and traversed child->root in the output.
  bool reversed;
};
struct PlannerPathPoint
{
  JointVector q{JointVector::Zero()};
  PlannerTree tree{PlannerTree::START};
  // No attempt means the exact root evidence for this tree.
  std::optional<std::size_t> attempt;
  std::size_t checked_point{0};
};
struct PlannerCounters
{
  std::size_t iterations{0}, samples{0}, rng_draws{0}, nearest_queries{0};
  std::size_t nearest_distance_evaluations{0}, growth_attempts{0};
  std::size_t candidate_projection_calls{0}, candidate_projection_failures{0};
  std::size_t projection_jump_rejections{0}, extension_jump_rejections{0};
  std::size_t no_progress_rejections{0}, invalid_candidate_rejections{0};
  std::size_t root_connection_calls{0}, tree_edge_connection_calls{0};
  std::size_t local_connection_rejections{0}, rbs_midpoint_projection_calls{0};
  std::size_t rbs_midpoint_projection_failures{0};
  std::size_t collision_queries{0}, collision_positive_queries{0};
  std::size_t collision_unavailable_queries{0}, constraint_evaluations{0}, margin_evaluations{0};
  std::size_t accepted_start_edges{0}, accepted_goal_edges{0};
};
struct PlannerPathMetrics
{
  double joint_path_length_rad{0.}, milestone_path_length_rad{0.};
  double maximum_position_residual_m{0.}, rms_position_residual_m{0.};
  double maximum_rotation_residual_rad{0.}, rms_rotation_residual_rad{0.};
  double minimum_native_joint_margin_rad{0.};
  double maximum_adjacent_l2_rad{0.}, maximum_adjacent_max_abs_rad{0.};
};
struct PlannerResult
{
  PlannerStatus status{PlannerStatus::INVALID_INPUT};
  std::string reason;
  JointVector requested_start{JointVector::Zero()}, requested_goal{JointVector::Zero()};
  JointVector native_lower{JointVector::Zero()}, native_upper{JointVector::Zero()};
  std::uint64_t seed{0};
  std::optional<PlannerOptions> options;
  std::optional<ConnectionResult> start_root, goal_root;
  std::vector<JointVector> sampled_targets;
  std::vector<PlannerNode> start_tree, goal_tree;
  std::vector<PlannerAttempt> attempts;
  std::optional<std::size_t> meeting_start_node, meeting_goal_node;
  std::vector<PlannerPathEdge> path_edges;
  std::vector<JointVector> path_milestones, dense_path;
  std::vector<PlannerPathPoint> dense_path_evidence;
  // Last rejected connector's ordered local prefix. Diagnostic only, never a solution.
  std::optional<std::size_t> failed_prefix_attempt;
  std::vector<JointVector> failed_prefix;
  PlannerCounters counters;
  std::optional<PlannerPathMetrics> path_metrics;
  double compute_wall_time_sec{0.};
  std::string minimum_distance_status{"UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED"};
};

PlannerResult plan(const JointVector& start, const JointVector& goal,
                   const JointVector& native_lower, const JointVector& native_upper,
                   const ConstraintEvaluator& constraint,
                   const JointMarginEvaluator& native_margin,
                   const CollisionEvaluator& collision,
                   const PlannerOptions& options);
} // namespace p4
