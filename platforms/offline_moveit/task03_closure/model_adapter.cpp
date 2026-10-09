#include "model_adapter.hpp"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

#include <srdfdom/model.h>
#include <urdf_parser/urdf_parser.h>

namespace task03_offline
{
namespace
{

Eigen::Isometry3d pose(const urdf::Pose& input)
{
  Eigen::Isometry3d output = Eigen::Isometry3d::Identity();
  output.translation() = Eigen::Vector3d(input.position.x, input.position.y, input.position.z);
  output.linear() = Eigen::Quaterniond(input.rotation.w, input.rotation.x,
                                      input.rotation.y, input.rotation.z).toRotationMatrix();
  return output;
}

void setPose(urdf::Pose& output, const Eigen::Isometry3d& input)
{
  const Eigen::Quaterniond quaternion(input.linear());
  output.position = urdf::Vector3(input.translation().x(), input.translation().y(), input.translation().z());
  output.rotation.setFromQuaternion(quaternion.x(), quaternion.y(), quaternion.z(), quaternion.w());
}

}  // namespace

DualFr3Model::DualFr3Model(const std::string& urdf_xml, const std::string& srdf_xml,
                         const Eigen::Isometry3d& frame_gauge)
{
  auto urdf_model = urdf::parseURDF(urdf_xml);
  if (!urdf_model || urdf_model->getRoot()->name != "world")
    throw std::invalid_argument("Expected unchanged dual FR3 URDF with world root");
  common_geometry::requireRigid(frame_gauge);

  // 只读输入文件，内存里对两条 world→base 固定边施加同一个坐标规范变换。
  // 此测试不是更改 Benchmark 基座位置，也不是新的机器人几何模型。
  for (const auto& side : {std::string("left"), std::string("right")})
  {
    auto found = urdf_model->joints_.find("world_to_" + side + "_fr3");
    if (found == urdf_model->joints_.end() || found->second->type != urdf::Joint::FIXED)
      throw std::invalid_argument("Missing existing fixed world-to-base joint");
    auto& origin = found->second->parent_to_joint_origin_transform;
    setPose(origin, frame_gauge * pose(origin));
  }

  auto srdf_model = std::make_shared<srdf::Model>();
  if (!srdf_model->initString(*urdf_model, srdf_xml))
    throw std::invalid_argument("Cannot parse supplied SRDF");
  model_ = std::make_shared<moveit::core::RobotModel>(urdf_model, srdf_model);
  if (model_->getModelFrame() != "world" || model_->getVariableCount() != 14)
    throw std::invalid_argument("Expected existing world-frame 14-DoF model");
  state_ = std::make_unique<moveit::core::RobotState>(model_);
  state_->setToDefaultValues();

  for (std::size_t side = 0; side < 2; ++side)
  {
    const std::string prefix = side == 0 ? "left" : "right";
    groups_[side] = model_->getJointModelGroup(prefix + "_arm");
    tcp_links_[side] = model_->getLinkModel(prefix + "_fr3_side_suction_tcp");
    if (!groups_[side] || !groups_[side]->isChain() ||
        groups_[side]->getVariableCount() != 7 || !tcp_links_[side])
      throw std::invalid_argument("Existing arm chain/TCP does not match expected model");
    for (std::size_t joint = 0; joint < 7; ++joint)
      if (groups_[side]->getVariableNames()[joint] != prefix + "_fr3_joint" + std::to_string(joint + 1))
        throw std::invalid_argument("Unexpected actual URDF joint order");

    // MoveIt 2.5.9 getJacobian 的参考系是组首 joint 的 parent，而不是默认 world。
    // 对两个 3-row block 旋转到 world；不需要空间 twist 的额外平移 adjoint。
    jacobian_reference_links_[side] = groups_[side]->getJointModels().front()->getParentLinkModel();
    if (!jacobian_reference_links_[side])
      throw std::invalid_argument("Missing existing Jacobian root-parent reference");
  }
}

void DualFr3Model::update(const p4::JointVector& q)
{
  if (!q.allFinite())
    throw std::invalid_argument("Non-finite actual joint configuration");
  state_->setJointGroupPositions(groups_[0], q.head<7>());
  state_->setJointGroupPositions(groups_[1], q.tail<7>());
  state_->update();
}

p4::ArmSample DualFr3Model::armSample(std::size_t side)
{
  p4::ArmSample output;
  output.world_tcp = state_->getGlobalLinkTransform(tcp_links_[side]);
  Eigen::MatrixXd local;
  if (!state_->getJacobian(groups_[side], tcp_links_[side], Eigen::Vector3d::Zero(), local, false) ||
      local.rows() != 6 || local.cols() != 7)
    throw std::runtime_error("Existing MoveIt geometric Jacobian unavailable");
  const Eigen::Matrix3d world_reference =
      state_->getGlobalLinkTransform(jacobian_reference_links_[side]).linear();
  output.world_tcp_jacobian.topRows<3>() = world_reference * local.topRows<3>();
  output.world_tcp_jacobian.bottomRows<3>() = world_reference * local.bottomRows<3>();
  if (!output.world_tcp.matrix().allFinite() || !output.world_tcp_jacobian.allFinite())
    throw std::runtime_error("Existing model produced invalid FK/Jacobian");
  return output;
}

std::pair<p4::ArmSample, p4::ArmSample> DualFr3Model::sample(const p4::JointVector& q)
{
  update(q);
  return {armSample(0), armSample(1)};
}

double DualFr3Model::minimumJointMargin(const p4::JointVector& q) const
{
  if (!q.allFinite())
    throw std::invalid_argument("Non-finite actual joint configuration");
  double result = std::numeric_limits<double>::infinity();
  const auto names = jointNames();
  for (std::size_t joint = 0; joint < names.size(); ++joint)
  {
    const auto& bounds = model_->getVariableBounds(names[joint]);
    if (!bounds.position_bounded_)
      throw std::runtime_error("Expected existing FR3 bounded revolute joints");
    result = std::min(result, std::min(q[joint] - bounds.min_position_, bounds.max_position_ - q[joint]));
  }
  return result;
}

std::array<std::string, 14> DualFr3Model::jointNames() const
{
  std::array<std::string, 14> output;
  for (std::size_t side = 0; side < 2; ++side)
    for (std::size_t joint = 0; joint < 7; ++joint)
      output[side * 7 + joint] = groups_[side]->getVariableNames()[joint];
  return output;
}

Eigen::Isometry3d DualFr3Model::linkPose(const p4::JointVector& q, const std::string& link)
{
  update(q);
  if (!model_->getLinkModel(link))
    throw std::invalid_argument("Requested link not in unchanged URDF");
  return state_->getGlobalLinkTransform(link);
}

}  // namespace task03_offline
