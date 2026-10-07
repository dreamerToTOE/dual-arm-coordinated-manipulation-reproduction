#pragma once
// [ENGINEERING] 单 Cube 几何探针：无 Isaac/Arm/MoveGroupInterface、无执行接口。
// 只读原 URDF/SRDF 和候选 YAML，在进程内检查，绝不编辑远程 Scene 或 ACM。
#include <rclcpp/rclcpp.hpp>
#include <moveit/robot_model_loader/robot_model_loader.h>
#include <moveit/planning_scene/planning_scene.h>
#include <moveit/collision_detection/collision_env.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <yaml-cpp/yaml.h>
#include <nlohmann/json.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <optional>
#include <sstream>
#include <algorithm>
#include <cmath>
#include <limits>
#include <map>
#include <vector>

using Json = nlohmann::json;
using State = moveit::core::RobotState;
using Group = moveit::core::JointModelGroup;

std::string readText(const std::string& path)
{
  std::ifstream file(path);
  if (!file) throw std::runtime_error("Cannot read " + path);
  std::ostringstream text; text << file.rdbuf(); return text.str();
}
Eigen::Vector3d vec(const YAML::Node& value)
{
  if (!value.IsSequence() || value.size()!=3) throw std::runtime_error("Undefined XYZ in candidate");
  Eigen::Vector3d v(value[0].as<double>(),value[1].as<double>(),value[2].as<double>());
  if (!v.allFinite()) throw std::runtime_error("Nonfinite XYZ");
  return v;
}
Eigen::Isometry3d transform(const YAML::Node& t)
{
  Eigen::Isometry3d out=Eigen::Isometry3d::Identity();
  out.translation()=vec(t["translation_m"]);
  auto q=t["quaternion_xyzw"];
  Eigen::Quaterniond quat(q[3].as<double>(),q[0].as<double>(),q[1].as<double>(),q[2].as<double>());
  if (!quat.coeffs().allFinite() || std::abs(quat.norm()-1.)>1e-9)
    throw std::runtime_error("Invalid candidate quaternion");
  out.linear()=quat.toRotationMatrix(); return out;
}
geometry_msgs::msg::Pose pose(const Eigen::Isometry3d& t)
{
  geometry_msgs::msg::Pose p;
  p.position.x=t.translation().x(); p.position.y=t.translation().y(); p.position.z=t.translation().z();
  Eigen::Quaterniond q(t.linear());
  p.orientation.x=q.x(); p.orientation.y=q.y(); p.orientation.z=q.z(); p.orientation.w=q.w(); return p;
}
Json xyz(const Eigen::Vector3d& v) { return Json::array({v.x(),v.y(),v.z()}); }
void box(planning_scene::PlanningScene& scene,const std::string& id,
         const Eigen::Vector3d& center,const Eigen::Vector3d& size)
{
  moveit_msgs::msg::CollisionObject object;
  object.header.frame_id="world"; object.id=id; object.operation=object.ADD;
  shape_msgs::msg::SolidPrimitive s; s.type=s.BOX; s.dimensions={size.x(),size.y(),size.z()};
  Eigen::Isometry3d t=Eigen::Isometry3d::Identity(); t.translation()=center;
  object.primitives.push_back(s); object.primitive_poses.push_back(pose(t));
  if (!scene.processCollisionObjectMsg(object)) throw std::runtime_error("Cannot add local box " + id);
}
Json residual(const State& state,const std::string& tip,const Eigen::Isometry3d& target)
{
  const auto& actual=state.getGlobalLinkTransform(tip);
  return {{"translation_m",(actual.translation()-target.translation()).norm()},
          {"rotation_rad",Eigen::AngleAxisd(target.linear().transpose()*actual.linear()).angle()}};
}
double margin(const State& state,const Group* group)
{
  double result=std::numeric_limits<double>::infinity();
  for (const auto& name:group->getVariableNames())
  {
    const auto& b=state.getRobotModel()->getVariableBounds(name);
    if (b.position_bounded_) result=std::min(result,std::min(
      state.getVariablePosition(name)-b.min_position_,b.max_position_-state.getVariablePosition(name)));
  }
  return result;
}
std::vector<State> solutions(const State& origin,const Group* group,
                            const std::string& tip,const Eigen::Isometry3d& target,
                            int attempt_cap=64,std::size_t retained_cap=12,Json* diagnostics=nullptr)
{
  // 有限、显式 seed；使用插件单次 getPositionIK，禁止 searchPositionIK 隐式随机重试。
  // 无候选仅表示本探针未找到，不能宣称全局无解。
  std::vector<State> found;
  const auto solver=group->getSolverInstance();
  if (!solver || solver->getJointNames()!=group->getVariableNames())
    throw std::runtime_error("Missing IK or unexpected joint ordering");
  if (solver->getTipFrames()!=std::vector<std::string>{tip})
    throw std::runtime_error("Configured solver tip differs from requested TCP");
  if (diagnostics) *diagnostics=Json::array();
  for (int attempt=0;attempt<attempt_cap && found.size()<retained_cap;++attempt)
  {
    State trial(origin);
    std::vector<double> seed; trial.copyJointGroupPositions(group,seed);
    if (attempt) for (std::size_t j=0;j<seed.size();++j)
    {
      const auto& b=origin.getRobotModel()->getVariableBounds(group->getVariableNames()[j]);
      const double f=.01+.98*((attempt*17+static_cast<int>(j)*7)%101)/100.;
      seed[j]=b.min_position_+f*(b.max_position_-b.min_position_);
    }
    // 插件使用其 base frame 表达目标；world 系目标不直接误传入插件。
    const auto base=trial.getGlobalLinkTransform(solver->getBaseFrame());
    std::vector<double> q; moveit_msgs::msg::MoveItErrorCodes error;
    const bool solved=solver->getPositionIK(pose(base.inverse()*target),seed,q,error);
    Json diagnostic={{"arm_group",group->getName()},{"tip_link",tip},
      {"solver_base_frame",solver->getBaseFrame()},{"attempt",attempt},
      {"seed_q_rad",seed},{"raw_q_rad",q},{"solver_return",solved},
      {"moveit_error_code",error.val},{"solution_size",q.size()},
      {"target_world_pose",{{"translation_m",xyz(target.translation())},
        {"rotation_matrix",Json::array({target.linear()(0,0),target.linear()(0,1),target.linear()(0,2),
          target.linear()(1,0),target.linear()(1,1),target.linear()(1,2),
          target.linear()(2,0),target.linear()(2,1),target.linear()(2,2)})}}},
      {"acceptance_translation_limit_m",1e-5},{"acceptance_rotation_limit_rad",1e-4}};
    const auto reject=[&](const std::string& reason) {
      diagnostic["disposition"]=reason;
      if (diagnostics) diagnostics->push_back(diagnostic);
    };
    if (!solved || error.val!=error.SUCCESS) { reject("SOLVER_FAILURE"); continue; }
    if (q.size()!=seed.size()) { reject("JOINT_COUNT_MISMATCH"); continue; }
    if (!std::all_of(q.begin(),q.end(),[](double value) { return std::isfinite(value); }))
      { reject("NONFINITE_SOLUTION"); continue; }
    trial.setJointGroupPositions(group,q); trial.update();
    const auto r=residual(trial,tip,target);
    diagnostic["bounds_satisfied"]=trial.satisfiesBounds(group);
    diagnostic["minimum_joint_margin_rad"]=margin(trial,group);
    diagnostic["residual"]=r;
    if (!trial.satisfiesBounds(group)) { reject("JOINT_BOUNDS_REJECTED"); continue; }
    if (r["translation_m"].get<double>()>1e-5) { reject("TRANSLATION_RESIDUAL_REJECTED"); continue; }
    if (r["rotation_rad"].get<double>()>1e-4) { reject("ROTATION_RESIDUAL_REJECTED"); continue; }
    bool duplicate=false;
    for (const auto& old:found) if (old.distance(trial,group)<1e-5) duplicate=true;
    if (duplicate) { reject("DUPLICATE"); continue; }
    found.push_back(trial); reject("ACCEPTED");
  }
  return found;
}
