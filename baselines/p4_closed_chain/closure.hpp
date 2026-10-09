#pragma once
// [ADAPTATION] P4 刚性闭链要求到 dual-FR3 的六维局部 SO(3) chart。
// 原文 II-A 式(1)/(2)不给出本文件的特定残差；见 README 的逐项归属。
#include "common/geometry/se3.hpp"
#include <functional>

namespace p4
{
using JointVector=Eigen::Matrix<double,14,1>;
using ArmJacobian=Eigen::Matrix<double,6,7>;
using Residual=Eigen::Matrix<double,6,1>;
using ConstraintJacobian=Eigen::Matrix<double,6,14>;

struct ArmSample
{
  Eigen::Isometry3d world_tcp;
  // 世界系 geometric Jacobian，前3行为 TCP 原点线速度，后3行为角速度。
  ArmJacobian world_tcp_jacobian;
};

struct ClosureSample
{
  Eigen::Isometry3d left_object;
  Eigen::Isometry3d right_object;
  Residual residual;
  ConstraintJacobian jacobian;
};

// T^A_B 把 B 坐标映到 A。grasp 参数必须是 T^TCP_Object，不是其逆。
Residual residual(const Eigen::Isometry3d& world_left_tcp,
                  const Eigen::Isometry3d& world_right_tcp,
                  const Eigen::Isometry3d& left_tcp_to_object,
                  const Eigen::Isometry3d& right_tcp_to_object);

ClosureSample evaluate(const ArmSample& left,const ArmSample& right,
                       const Eigen::Isometry3d& left_tcp_to_object,
                       const Eigen::Isometry3d& right_tcp_to_object);

// [ENGINEERING] 独立 FK 中央有限差分，仅验证导数，不做 Newton/投影/更新 q。
ConstraintJacobian centralDifference(
  const JointVector& q,const std::function<Residual(const JointVector&)>& evaluate_residual,
  double step_rad);
}  // namespace p4
