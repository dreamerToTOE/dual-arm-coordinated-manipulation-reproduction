#pragma once

#include <array>
#include <memory>
#include <string>
#include <utility>

#include <moveit/robot_model/robot_model.h>
#include <moveit/robot_state/robot_state.h>

#include "baselines/p4_closed_chain/closure.hpp"

namespace task03_offline
{

// [THIN_ADAPTER] 同一展开 URDF/SRDF + 旧工程 RobotState FK/Jacobian；无执行接口。
class DualFr3Model
{
public:
  // frame_gauge 仅用于明确标记的离线坐标规范测试。默认恒等；不写模型文件。
  DualFr3Model(const std::string& urdf_xml, const std::string& srdf_xml,
              const Eigen::Isometry3d& frame_gauge = Eigen::Isometry3d::Identity());

  std::pair<p4::ArmSample, p4::ArmSample> sample(const p4::JointVector& q);
  double minimumJointMargin(const p4::JointVector& q) const;
  std::array<std::string, 14> jointNames() const;
  Eigen::Isometry3d linkPose(const p4::JointVector& q, const std::string& link);

private:
  void update(const p4::JointVector& q);
  p4::ArmSample armSample(std::size_t side);

  moveit::core::RobotModelPtr model_;
  std::unique_ptr<moveit::core::RobotState> state_;
  std::array<const moveit::core::JointModelGroup*, 2> groups_{};
  std::array<const moveit::core::LinkModel*, 2> tcp_links_{};
  std::array<const moveit::core::LinkModel*, 2> jacobian_reference_links_{};
};

}  // namespace task03_offline
