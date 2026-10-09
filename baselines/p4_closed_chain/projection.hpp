#pragma once
// [ORIGINAL] NR 伪逆更新；[ENGINEERING] 有界、只读FK回调、明确失败与日志。
#include "baselines/p4_closed_chain/closure.hpp"
#include <cstddef>
#include <optional>
#include <string>
#include <vector>

namespace p4
{
// 数值必须由调用者显式提供。不是正式 Benchmark 默认成功阈值。
struct ProjectionOptions
{
  double position_tolerance_m;
  double rotation_tolerance_rad;
  std::size_t max_iterations;
  double svd_absolute_cutoff;
  double svd_relative_cutoff;
  double stagnation_step_rad;
};

enum class ProjectionStatus
{
  CONVERGED, INVALID_OPTIONS, INVALID_INPUT, INITIAL_JOINT_LIMIT,
  ITERATION_LIMIT, RANK_DEFICIENT, UPDATE_JOINT_LIMIT, NONFINITE_EVALUATION,
  EVALUATION_ERROR, BOUNDS_ERROR, NONFINITE_UPDATE, STAGNATION
};
const char* statusName(ProjectionStatus status);

struct ProjectionIteration
{
  std::size_t update_index;
  JointVector q_before;
  Residual residual_before;
  double joint_margin_before_rad;
  std::optional<Eigen::Matrix<double,6,1>> singular_values;
  std::optional<double> singular_cutoff;
  int numerical_rank{-1};
  std::optional<JointVector> proposed_delta_q;
  std::optional<JointVector> proposed_q;
  std::optional<double> candidate_joint_margin_rad;
  std::optional<Residual> residual_after;
  bool update_accepted{false};
  std::string note;
};

struct ProjectionResult
{
  ProjectionStatus status{ProjectionStatus::INVALID_INPUT};
  std::string reason;
  JointVector initial_q;
  // 初始q通过验证后：失败保留最后接受的有限、限位合法且可评估q。
  // 若初始输入本就不合格，仍返回原输入；调用者必须检查status，不直接执行。
  JointVector projected_q;
  std::optional<Residual> initial_residual;
  std::optional<Residual> final_residual;
  std::optional<double> joint_delta_norm_rad;
  std::optional<double> joint_delta_max_abs_rad;
  std::size_t accepted_updates{0};
  std::size_t evaluations{0};
  double compute_wall_time_sec{0.};
  std::vector<ProjectionIteration> history;
};

using ConstraintEvaluator=std::function<ClosureSample(const JointVector&)>;
// 返回原模型最小关节余量(rad)；负数为越界，不允许epsilon放宽或clamp。
using JointMarginEvaluator=std::function<double(const JointVector&)>;

ProjectionResult project(const JointVector& initial_q,
                         const ConstraintEvaluator& evaluate_constraint,
                         const JointMarginEvaluator& native_joint_margin,
                         const ProjectionOptions& options);
}  // namespace p4
