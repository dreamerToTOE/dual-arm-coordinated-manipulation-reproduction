#pragma once
// [ORIGINAL] P4 II-C RBS；[ENGINEERING] 有界离散证据，不是执行轨迹/连续安全证明。
#include "baselines/p4_closed_chain/projection.hpp"

namespace p4
{
struct CollisionContact
{
  std::string body_a, body_b, category;
  double penetration_depth_m{0.};
  Eigen::Vector3d position_world_m{Eigen::Vector3d::Zero()};
};
struct CollisionEvidence
{
  bool complete{false};
  bool self_collision{false}; // 包含同臂与跨臂；原生检查，不使用旧过滤器。
  bool world_collision{false}; // 包含持件与环境。
  std::string backend, reason, acm_identity;
  std::vector<CollisionContact> contacts;
};
using CollisionEvaluator=std::function<CollisionEvidence(const JointVector&)>;

struct LocalConnectionOptions
{
  ProjectionOptions projection;
  double leaf_resolution_rad;
  double adjacent_l2_limit_rad;
  double adjacent_max_abs_limit_rad;
  double projection_correction_limit_rad;
  std::size_t max_depth, max_projections, max_path_points;
};
enum class ConnectionStatus
{
  CONNECTED, INVALID_OPTIONS, INVALID_INPUT, JOINT_LIMIT, CLOSURE,
  EVALUATION_ERROR, COLLISION_UNAVAILABLE, COLLISION, PROJECTION_FAILED,
  PROJECTION_JUMP, CONTINUITY, DEPTH_LIMIT, PROJECTION_BUDGET, PATH_BUDGET
};
const char* statusName(ConnectionStatus status);

struct ConnectionPoint
{
  JointVector q{JointVector::Zero()};
  std::string role;
  std::size_t depth{0};
  bool qualified{false};
  std::optional<double> joint_margin_rad;
  std::optional<Residual> residual;
  std::optional<CollisionEvidence> collision;
  std::optional<ProjectionResult> projection;
  std::optional<double> projection_correction_l2_rad;
  std::string failure;
};
struct ConnectionEdge
{
  std::size_t from, to;
  double l2_rad, max_abs_rad;
  bool accepted;
};
struct ConnectionResult
{
  ConnectionStatus status{ConnectionStatus::INVALID_INPUT};
  std::string reason;
  JointVector requested_start{JointVector::Zero()}, requested_goal{JointVector::Zero()};
  std::vector<ConnectionPoint> checked_points;
  // 失败时仅已完成连接的有序左前缀，不把提前检查的终点/中点冒充可达点。
  std::vector<std::size_t> verified_prefix;
  std::vector<ConnectionEdge> leaf_edges;
  std::optional<std::size_t> failed_point;
  std::size_t projection_calls{0}, maximum_depth{0};
  double compute_wall_time_sec{0.};
};

ConnectionResult connect(const JointVector& start, const JointVector& goal,
                         const ConstraintEvaluator& constraint,
                         const JointMarginEvaluator& native_margin,
                         const CollisionEvaluator& collision,
                         const LocalConnectionOptions& options);
} // namespace p4
