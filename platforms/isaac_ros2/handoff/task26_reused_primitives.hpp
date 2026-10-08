#pragma once
// [ENGINEERING] 从用户旧项目Task26机械抽取，非新SG/重抓/推进算法。
// source: dreamerToTOE/dual-arm-embodied-palletizing
// ref: side-suction-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a
// file: ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp
// SHA256: a844529af73a77b8e52aa7be8eb879a4a86d317148a3ded49ea76e714a72e840
// Git blob: dc436a52cb31c34c4dc656e200923ea81ec0e3dd
// ranges: 398–514, 833–1670（仅当前handoff需要的方法；删unused task/home/single-execute）。
// patches: /task01 topics + global joint_states prefix filtering; bounded outer guard;
// current1.0 scaling/time_scale; remove legacy residual-success fallback;
// same-stamp execute follows MoveIt retimed phase (empty arms only).
// 不包含五Cube、推入TARGET、摩擦、drive、80Nm或3mm终点门限。
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdint>
#include <functional>
#include <iomanip>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <stdexcept>
#include <thread>
#include <unordered_map>
#include <vector>
#include <builtin_interfaces/msg/time.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <moveit/collision_detection/collision_common.h>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene/planning_scene.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit/robot_state/robot_state.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit_msgs/msg/robot_trajectory.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_msgs/msg/bool.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>

namespace task26_reuse {
using namespace std::chrono_literals;
constexpr const char* kTaskLabel = "task01";
inline std::string taskTopic(const std::string& suffix) { return "/task01" + suffix; }
constexpr double kPi = 3.14159265358979323846;
constexpr int kRrtCandidateCount = 8;
constexpr int kRetries = 3;
constexpr double kCartesianStep = .002;
constexpr double kCartesianJumpThreshold = 0.0;
constexpr double kMinCartesianFraction = .999;
constexpr double kMaxCartesianLineDeviation = .005;
constexpr double kFclSamplePeriod = .010;
constexpr auto kDualCommandPeriod = 10ms;
// 100ms final submission; actualsettle由明确engineering参数及post-step值决定。
constexpr int kFinalCommandHold = 10;
inline double g_joint_settle_limit_rad = .01;
inline std::function<void()> g_operation_guard = [] {};
inline std::function<double()> g_seconds_remaining = [] { return 120.; };
inline std::function<void(trajectory_msgs::msg::JointTrajectory&)> g_retime_untimed;

double pointTime(const trajectory_msgs::msg::JointTrajectoryPoint& point)
{
  return static_cast<double>(point.time_from_start.sec) +
         static_cast<double>(point.time_from_start.nanosec) * 1e-9;
}

void setPointTime(trajectory_msgs::msg::JointTrajectoryPoint& point, double seconds)
{
  point.time_from_start.sec = static_cast<std::int32_t>(std::floor(seconds));
  point.time_from_start.nanosec = static_cast<std::uint32_t>(std::llround(
    (seconds - std::floor(seconds)) * 1e9));
}

void ensureTiming(trajectory_msgs::msg::JointTrajectory& trajectory)
{
  if (trajectory.points.empty())
  {
    return;
  }
  // computeCartesianPath() 在目标与起点完全重合（例如已经对准目标 Y 的
  // COMMON_Y_ALIGN）时会合法地返回仅含一个、t=0 的点。它不是规划失败，
  // 而是零位移保持；补出一个相同的 30 ms 终点，才能与另一臂同步并继续做
  // FCL 采样和原子双臂命令。不能把该阶段跳过，否则左右时序会失去统一接口。
  if (trajectory.points.size() == 1)
  {
    auto endpoint = trajectory.points.front();
    setPointTime(endpoint, 0.03);
    trajectory.points.push_back(std::move(endpoint));
    return;
  }
  if (pointTime(trajectory.points.back()) > 1e-6)
  {
    return;
  }
  // [ENGINEERING] 不继承旧30ms/point速度；无时间轨迹用当前MoveIt限位做IPTP。
  if (!g_retime_untimed) throw std::runtime_error("Current-limit retimer not installed");
  g_retime_untimed(trajectory);
}

std::vector<double> finalPositions(const trajectory_msgs::msg::JointTrajectory& trajectory)
{
  return trajectory.points.empty() ? std::vector<double>{} : trajectory.points.back().positions;
}

std::string formatJointPositions(const std::vector<double>& positions)
{
  std::ostringstream stream;
  stream << std::fixed << std::setprecision(4) << "[";
  for (std::size_t index = 0; index < positions.size(); ++index)
  {
    if (index > 0)
    {
      stream << ", ";
    }
    stream << positions[index];
  }
  stream << "]";
  return stream.str();
}

// 侧面双吸盘的最终 CONTACT 必须两臂都到位，但两条从 PRE_CONTACT 到 CONTACT
// 的短 Cartesian 进给若严格同一时刻开始，局部肘部扫掠会偶发相交。这里使用
// 可验证的微时序：左臂先进入，右臂保持 PRE_CONTACT；随后右臂进入，左臂保持
// CONTACT。两杯均接触后仍同步 ON，并从 COMMON_LIFT 开始执行真正的紧协调。
// 这不是等待区或长距离串行搬运，只是接触建立阶段的安全时序。
trajectory_msgs::msg::JointTrajectory holdTrajectory(
  const trajectory_msgs::msg::JointTrajectory& reference,
  const std::vector<double>& positions, double duration)
{
  trajectory_msgs::msg::JointTrajectory hold;
  hold.joint_names = reference.joint_names;
  trajectory_msgs::msg::JointTrajectoryPoint begin;
  begin.positions = positions;
  setPointTime(begin, 0.0);
  trajectory_msgs::msg::JointTrajectoryPoint end = begin;
  setPointTime(end, std::max(0.05, duration));
  hold.points = {begin, end};
  return hold;
}

std::vector<double> interpolate(
  const trajectory_msgs::msg::JointTrajectory& trajectory, double time_sec)
{
  if (trajectory.points.empty())
  {
    return {};
  }
  if (time_sec <= pointTime(trajectory.points.front()))
  {
    return trajectory.points.front().positions;
  }
  if (time_sec >= pointTime(trajectory.points.back()))
  {
    return trajectory.points.back().positions;
  }
  for (std::size_t index = 1; index < trajectory.points.size(); ++index)
  {
    const auto& first = trajectory.points[index - 1];
    const auto& second = trajectory.points[index];
    if (time_sec > pointTime(second))
    {
      continue;
    }
    const double denominator = pointTime(second) - pointTime(first);
    const double alpha = denominator > 1e-9 ?
      std::clamp((time_sec - pointTime(first)) / denominator, 0.0, 1.0) : 0.0;
    std::vector<double> positions(first.positions.size());
    for (std::size_t joint = 0; joint < positions.size(); ++joint)
    {
      positions[joint] = first.positions[joint] +
        alpha * (second.positions[joint] - first.positions[joint]);
    }
    return positions;
  }
  return trajectory.points.back().positions;
}
class Arm
{
public:
  Arm(const rclcpp::Node::SharedPtr& node, bool left, double time_scale)
    : node_(node), left_(left), side_(left ? "left" : "right"),
      group_(left ? "left_arm" : "right_arm"),
      eef_(left ? "left_fr3_side_suction_tcp" : "right_fr3_side_suction_tcp"),
      prefix_(left ? "left_" : "right_"), time_scale_(time_scale)
  {
    joint_pub_ = node_->create_publisher<sensor_msgs::msg::JointState>("/" + side_ + "/joint_command", 10);
    suction_pub_ = node_->create_publisher<std_msgs::msg::Bool>(
      taskTopic("/" + side_ + "/suction_command"), 10);
    state_sub_ = node_->create_subscription<std_msgs::msg::Bool>(
      taskTopic("/" + side_ + "/suction_state"), 10,
      [this](const std_msgs::msg::Bool::SharedPtr state)
      {
        seen_state_.store(true);
        closed_.store(state->data);
      });
    joint_state_sub_ = node_->create_subscription<sensor_msgs::msg::JointState>(
      "/joint_states", 10,
      [this](const sensor_msgs::msg::JointState::SharedPtr state)
      {
        std::lock_guard<std::mutex> lock(joint_mutex_);
        joint_positions_.clear();
        const std::size_t count = std::min(state->name.size(), state->position.size());
        for (std::size_t index = 0; index < count; ++index)
        {
          if (state->name[index].rfind(prefix_, 0) == 0)
            joint_positions_[state->name[index].substr(prefix_.size())] = state->position[index];
        }
        // 速度只服务于超时诊断：用来区分"被挡住"（速度≈0）与"还在追"（速度非零）。
        joint_velocities_.clear();
        const std::size_t velocity_count = std::min(state->name.size(), state->velocity.size());
        for (std::size_t index = 0; index < velocity_count; ++index)
        {
          if (state->name[index].rfind(prefix_, 0) == 0)
            joint_velocities_[state->name[index].substr(prefix_.size())] = state->velocity[index];
        }
        seen_joint_state_.store(true);
        joint_condition_.notify_all();
      });
  }

  const std::string& groupName() const { return group_; }
  const std::string& eefLink() const { return eef_; }
  bool isLeft() const { return left_; }
  bool isClosed() const { return closed_.load(); }

  bool waitBridge() const
  {
    for (int attempt = 0; attempt < 100; ++attempt)
    {
      if (joint_pub_->get_subscription_count() > 0 && suction_pub_->get_subscription_count() > 0 &&
          seen_state_.load() && seen_joint_state_.load())
      {
        return true;
      }
      std::this_thread::sleep_for(100ms);
    }
    return false;
  }

  bool planPoseCandidatesFrom(
    moveit::planning_interface::MoveGroupInterface& group,
    const std::vector<double>& start, const geometry_msgs::msg::Pose& target,
    const std::string& label,
    std::vector<trajectory_msgs::msg::JointTrajectory>* outputs) const
  {
    configure(group);
    const auto* joint_model_group = group.getRobotModel()->getJointModelGroup(group_);
    auto state = group.getCurrentState(2.0);
    if (!joint_model_group || !state || start.size() != joint_model_group->getVariableCount())
    {
      return false;
    }
    state->setJointGroupPositions(joint_model_group, start);
    state->update();
    group.clearPoseTargets();
    if (!group.setPoseTarget(target, eef_))
    {
      return false;
    }
    std::vector<std::pair<double, trajectory_msgs::msg::JointTrajectory>> candidates;
    for (int attempt = 1; attempt <= kRrtCandidateCount; ++attempt)
    {
      g_operation_guard();
      group.setPlanningTime(std::max(.05, std::min(3.0, g_seconds_remaining())));
      group.setStartState(*state);
      moveit::planning_interface::MoveGroupInterface::Plan plan;
      if (group.plan(plan) != moveit::core::MoveItErrorCode::SUCCESS ||
          plan.trajectory_.joint_trajectory.points.empty())
      {
        RCLCPP_WARN(node_->get_logger(), "%s %s RRTConnect candidate failed=%d/%d.",
          side_.c_str(), label.c_str(), attempt, kRrtCandidateCount);
        continue;
      }
      auto candidate = plan.trajectory_.joint_trajectory;
      ensureTiming(candidate);
      double travel = 0.0;
      for (std::size_t point = 1; point < candidate.points.size(); ++point)
      {
        for (std::size_t joint = 0; joint < candidate.points[point].positions.size(); ++joint)
        {
          travel += std::abs(candidate.points[point].positions[joint] -
            candidate.points[point - 1].positions[joint]);
        }
      }
      candidates.emplace_back(travel, std::move(candidate));
    }
    if (candidates.empty())
    {
      return false;
    }
    std::sort(candidates.begin(), candidates.end(),
      [](const auto& first, const auto& second) { return first.first < second.first; });
    outputs->clear();
    for (auto& [travel, candidate] : candidates)
    {
      (void)travel;
      outputs->push_back(std::move(candidate));
    }
    RCLCPP_INFO(node_->get_logger(), "%s %s candidates=%zu, shortest_joint_travel=%.3f.",
      side_.c_str(), label.c_str(), outputs->size(), candidates.front().first);
    return true;
  }

  // 批间退出：共同回到官方空载准备姿态。空载 RRTConnect 到固定关节目标即可，
  // 但仍必须整段通过同步 FCL 门禁；这里不执行任何负载段。
  void publishAt(const trajectory_msgs::msg::JointTrajectory& input, double logical_time,
                 const builtin_interfaces::msg::Time& stamp) const
  {
    std::vector<std::string> names;
    names.reserve(input.joint_names.size());
    for (const auto& name : input.joint_names)
    {
      names.push_back(name.rfind(prefix_, 0) == 0 ? name.substr(prefix_.size()) : name);
    }
    sensor_msgs::msg::JointState command;
    command.header.stamp = stamp;
    command.header.frame_id = std::string(kTaskLabel) + "_dual_sync";
    command.name = std::move(names);
    command.position = interpolate(input, logical_time);
    joint_pub_->publish(command);
  }

  builtin_interfaces::msg::Time nowMsg() const
  {
    const auto nanoseconds = node_->now().nanoseconds();
    builtin_interfaces::msg::Time stamp;
    stamp.sec = static_cast<std::int32_t>(nanoseconds / 1000000000LL);
    stamp.nanosec = static_cast<std::uint32_t>(nanoseconds % 1000000000LL);
    return stamp;
  }

  double timeScale() const
  {
    return time_scale_;
  }

  double simulationSeconds() const { return node_->now().seconds(); }

  bool waitAtTarget(const trajectory_msgs::msg::JointTrajectory& trajectory,
                    double tolerance_rad, double timeout_sec) const
  {
    if (trajectory.joint_names.empty() || trajectory.points.empty() ||
        trajectory.joint_names.size() != trajectory.points.back().positions.size())
    {
      return false;
    }
    const auto& target = trajectory.points.back().positions;
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::duration<double>(timeout_sec);
    double last_max_error = std::numeric_limits<double>::infinity();
    while (std::chrono::steady_clock::now() < deadline)
    {
      g_operation_guard();
      {
        std::unique_lock<std::mutex> lock(joint_mutex_);
        bool complete = true;
        last_max_error = 0.0;
        for (std::size_t index = 0; index < trajectory.joint_names.size(); ++index)
        {
          const auto& full_name = trajectory.joint_names[index];
          const std::string name = full_name.rfind(prefix_, 0) == 0
            ? full_name.substr(prefix_.size()) : full_name;
          const auto found = joint_positions_.find(name);
          if (found == joint_positions_.end())
          {
            complete = false;
            last_max_error = std::numeric_limits<double>::infinity();
            break;
          }
          last_max_error = std::max(last_max_error, std::abs(found->second - target[index]));
        }
        if (complete && last_max_error <= tolerance_rad)
        {
          RCLCPP_INFO(node_->get_logger(), "%s final joint-state settled: max_error=%.3f deg.",
            side_.c_str(), last_max_error * 180.0 / kPi);
          return true;
        }
        joint_condition_.wait_for(lock, 50ms);
      }
    }
    const std::string max_error_text = std::isfinite(last_max_error)
      ? std::to_string(last_max_error * 180.0 / kPi) + " deg"
      : "missing joint state";
    RCLCPP_ERROR(node_->get_logger(), "%s final joint-state did not settle within %.1f s: max_error=%s.",
      side_.c_str(), timeout_sec, max_error_text.c_str());
    // 超时诊断：逐关节残差 + 实测速度。速度≈0 = 被挡住；速度非零 = 还在追（给时间即可）。
    {
      std::unique_lock<std::mutex> lock(joint_mutex_);
      std::ostringstream detail;
      for (std::size_t index = 0; index < trajectory.joint_names.size(); ++index)
      {
        const auto& full_name = trajectory.joint_names[index];
        const std::string name = full_name.rfind(prefix_, 0) == 0
          ? full_name.substr(prefix_.size()) : full_name;
        const auto position = joint_positions_.find(name);
        if (position == joint_positions_.end())
        {
          continue;
        }
        detail << " " << name << " " << std::fixed << std::setprecision(2)
               << (position->second - target[index]) * 180.0 / kPi << "deg";
        const auto velocity = joint_velocities_.find(name);
        if (velocity != joint_velocities_.end())
        {
          detail << "/" << std::setprecision(3) << velocity->second << "rad_s";
        }
      }
      RCLCPP_ERROR(node_->get_logger(), "%s 超时细节（残差deg / 速度rad_s）：%s",
        side_.c_str(), detail.str().c_str());
    }
    return false;
  }

  void suction(bool enabled) const
  {
    std_msgs::msg::Bool message;
    message.data = enabled;
    for (int repeat = 0; repeat < 20; ++repeat)
    {
      suction_pub_->publish(message);
      std::this_thread::sleep_for(10ms);
    }
  }

  bool waitSuction(bool expected, double timeout_sec) const
  {
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::duration<double>(timeout_sec);
    while (std::chrono::steady_clock::now() < deadline)
    {
      if (seen_state_.load() && closed_.load() == expected)
      {
        return true;
      }
      std::this_thread::sleep_for(20ms);
    }
    return false;
  }

private:
  void configure(moveit::planning_interface::MoveGroupInterface& group) const
  {
    group.setPlannerId("RRTConnectkConfigDefault");
    // [ENGINEERING] 原有限RRT池，单候选最多3s且总handoff deadline仍生效。
    group.setPlanningTime(std::max(.05, std::min(3.0, g_seconds_remaining())));
    group.setNumPlanningAttempts(1);
    group.setMaxVelocityScalingFactor(1.0);
    group.setMaxAccelerationScalingFactor(1.0);
    group.setPoseReferenceFrame("world");
    group.setEndEffectorLink(eef_);
  }

  rclcpp::Node::SharedPtr node_;
  bool left_;
  std::string side_;
  std::string group_;
  std::string eef_;
  std::string prefix_;
  double time_scale_;
  rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_pub_;
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr suction_pub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr state_sub_;
  rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
  std::atomic_bool seen_state_{false};
  std::atomic_bool seen_joint_state_{false};
  std::atomic_bool closed_{false};
  mutable std::mutex joint_mutex_;
  mutable std::condition_variable joint_condition_;
  std::unordered_map<std::string, double> joint_positions_;
  std::unordered_map<std::string, double> joint_velocities_;
};

bool executeSync(const Arm& left, const trajectory_msgs::msg::JointTrajectory& left_trajectory,
                 const Arm& right, const trajectory_msgs::msg::JointTrajectory& right_trajectory)
{
  auto left_command = left_trajectory;
  auto right_command = right_trajectory;
  ensureTiming(left_command);
  ensureTiming(right_command);
  if (left_command.points.empty() || right_command.points.empty() ||
      left_command.joint_names.empty() || right_command.joint_names.empty())
  {
    return false;
  }

  const double left_duration = pointTime(left_command.points.back());
  const double right_duration = pointTime(right_command.points.back());
  const double common_duration = std::max(left_duration, right_duration);
  if (common_duration <= 1e-6 || std::abs(left.timeScale() - right.timeScale()) > 1e-9)
  {
    return false;
  }

  const auto start = std::chrono::steady_clock::now();
  const double simulation_start = left.simulationSeconds();

  // 同一phase/stamp机制来自Task26。本入口是空载handoff，time_scale固定1.0，
  // 直接跟随当前MoveIt限速轨迹，不继承旧持件S曲线的额外时间重映射。
  const double physical_duration = common_duration * left.timeScale();
  std::size_t tick = 0;
  while (true)
  {
    // [ENGINEERING] phase由同源post-step /clock推进，wall只做发送节拍与硬deadline。
    const double elapsed = std::max(0., left.simulationSeconds() - simulation_start);
    const double linear_phase = std::clamp(elapsed / physical_duration, 0.0, 1.0);
    const auto stamp = left.nowMsg();
    g_operation_guard();
    // [ENGINEERING] 本入口只有空载handoff，不叠加旧持件S曲线时间重映射；
    // 直接跟随MoveIt已限速的轨迹，共享phase/stamp，time_scale固定1.0。
    left.publishAt(left_command, linear_phase * left_duration, stamp);
    right.publishAt(right_command, linear_phase * right_duration, stamp);
    if (linear_phase >= 1.0)
    {
      break;
    }
    ++tick;
    std::this_thread::sleep_until(start + tick * kDualCommandPeriod);
  }

  for (int repeat = 0; repeat < kFinalCommandHold; ++repeat)
  {
    g_operation_guard();
    const auto stamp = left.nowMsg();
    left.publishAt(left_command, left_duration, stamp);
    right.publishAt(right_command, right_duration, stamp);
    std::this_thread::sleep_for(kDualCommandPeriod);
  }
  return left.waitAtTarget(left_command, g_joint_settle_limit_rad, std::min(10.0, g_seconds_remaining())) &&
    right.waitAtTarget(right_command, g_joint_settle_limit_rad, std::min(10.0, g_seconds_remaining()));
}

bool synchronize(trajectory_msgs::msg::JointTrajectory* first, trajectory_msgs::msg::JointTrajectory* second)
{
  ensureTiming(*first);
  ensureTiming(*second);
  if (first->points.empty() || second->points.empty())
  {
    return false;
  }
  const double duration = std::max(pointTime(first->points.back()), pointTime(second->points.back()));
  for (auto* trajectory : {first, second})
  {
    if (trajectory->points.empty())
    {
      return false;
    }

    const double original = pointTime(trajectory->points.back());
    if (original <= 1e-9)
    {
      return false;
    }
    for (auto& point : trajectory->points)
    {
      setPointTime(point, pointTime(point) * duration / original);
    }
  }
  return true;
}

bool validateSync(
  const rclcpp::Node::SharedPtr& node, const moveit::core::RobotModelConstPtr& model,
  const std::vector<moveit_msgs::msg::CollisionObject>& world,
  const trajectory_msgs::msg::JointTrajectory& left, const trajectory_msgs::msg::JointTrajectory& right,
  const std::string& label)
{
  auto scene = std::make_shared<planning_scene::PlanningScene>(model);
  for (const auto& object : world)
  {
    if (!scene->processCollisionObjectMsg(object))
    {
      RCLCPP_ERROR(node->get_logger(), "%s cannot load world object %s into FCL.", label.c_str(), object.id.c_str());
      return false;
    }
  }
  const double duration = std::max(pointTime(left.points.back()), pointTime(right.points.back()));
  const std::size_t samples = static_cast<std::size_t>(std::ceil(duration / kFclSamplePeriod));
  for (std::size_t index = 0; index <= samples; ++index)
  {
    const auto left_q = interpolate(left, std::min(duration, index * kFclSamplePeriod));
    const auto right_q = interpolate(right, std::min(duration, index * kFclSamplePeriod));
    moveit::core::RobotState state(model);
    state.setToDefaultValues();
    state.setVariablePositions(left.joint_names, left_q);
    state.setVariablePositions(right.joint_names, right_q);
    state.update();
    collision_detection::CollisionRequest request;
    request.contacts = true;
    request.max_contacts = 1;
    collision_detection::CollisionResult result;
    scene->checkCollision(request, result, state);
    if (result.collision)
    {
      const double collision_time = std::min(duration, index * kFclSamplePeriod);
      RCLCPP_ERROR(node->get_logger(), "%s FCL collision at t=%.3f s.",
        label.c_str(), collision_time);
      for (const auto& [pair, contacts] : result.contacts)
      {
        RCLCPP_ERROR(node->get_logger(), "%s FCL pair: %s <-> %s.",
          label.c_str(), pair.first.c_str(), pair.second.c_str());
        for (const auto& contact : contacts)
        {
          RCLCPP_ERROR(node->get_logger(),
            "%s FCL contact: pos=(%.3f, %.3f, %.3f) depth=%.3f mm.",
            label.c_str(), contact.pos.x(), contact.pos.y(), contact.pos.z(),
            contact.depth * 1000.0);
        }
        // 记录碰撞采样点的 link 原点，区分“目标姿态本身过低”和“Cartesian
        // IK 分支在中途下探”。这只是诊断，不放宽任何碰撞规则。
        for (const auto& name : {pair.first, pair.second})
        {
          if (model->hasLinkModel(name))
          {
            const auto& p = state.getGlobalLinkTransform(name).translation();
            RCLCPP_ERROR(node->get_logger(), "%s FCL link %s origin=(%.3f, %.3f, %.3f).",
              label.c_str(), name.c_str(), p.x(), p.y(), p.z());
            // Task26 侧吸盘的 collision 依次是：竖杆、横杆、面板、四个 Cup。
            // 输出各 primitive 的世界原点，以便定位真实擦碰实体；不据此放宽 ACM。
            const auto* link = model->getLinkModel(name);
            const auto& local_origins = link->getCollisionOriginTransforms();
            for (std::size_t collision_index = 0; collision_index < local_origins.size(); ++collision_index)
            {
              const auto world = state.getGlobalLinkTransform(name) * local_origins[collision_index];
              const auto& origin = world.translation();
              RCLCPP_ERROR(node->get_logger(),
                "%s FCL collision_primitive=%zu world_origin=(%.3f, %.3f, %.3f).",
                label.c_str(), collision_index, origin.x(), origin.y(), origin.z());
            }
          }
        }
      }
      return false;
    }
  }
  RCLCPP_INFO(node->get_logger(), "%s synchronized FCL PASS, samples=%zu.", label.c_str(), samples + 1);
  return true;
}

// 用 FK 检查一条笛卡尔轨迹的中间状态是否真的贴着命令直线。
// MoveIt 的 computeCartesianPath 在个别路径点 IK 失败时仍会报出 1.0000 的 fraction，
// 但中间状态可能离直线极远（实测左臂 COMMON_Y_ALIGN 的 TCP 从 y=0.02 甩到 y=-1.2 m
// 再绕回来，且中途扫过桌面）。这类轨迹既不是真实碰撞也不是可用构型，必须整体拒绝并
// 换一个采样步长重规划，而不是等同步 FCL 在最后一段才发现。
double cartesianLineDeviation(
  const moveit::core::RobotModelConstPtr& model, const std::string& eef_link,
  const trajectory_msgs::msg::JointTrajectory& trajectory,
  const geometry_msgs::msg::Pose& target)
{
  if (trajectory.points.empty() || trajectory.joint_names.empty())
  {
    return std::numeric_limits<double>::infinity();
  }
  const auto poseAt = [&](const std::vector<double>& positions) {
    moveit::core::RobotState state(model);
    state.setToDefaultValues();
    state.setVariablePositions(trajectory.joint_names, positions);
    state.update();
    return state.getGlobalLinkTransform(eef_link).translation();
  };
  const Eigen::Vector3d start = poseAt(trajectory.points.front().positions);
  const Eigen::Vector3d goal(
    target.position.x, target.position.y, target.position.z);
  const Eigen::Vector3d delta = goal - start;
  const double span = delta.norm();
  if (span <= 1e-9)
  {
    return 0.0;
  }
  const Eigen::Vector3d direction = delta / span;
  double worst = 0.0;
  for (const auto& point : trajectory.points)
  {
    const Eigen::Vector3d actual = poseAt(point.positions);
    const double alpha = std::clamp(
      (actual - start).dot(direction) / span, 0.0, 1.0);
    worst = std::max(worst, (actual - (start + alpha * delta)).norm());
  }
  return worst;
}

bool planCommonCartesian(
  const rclcpp::Node::SharedPtr& node, moveit::planning_interface::MoveGroupInterface& group,
  const std::string& own_group, const std::string& partner_group,
  const std::vector<double>& own_start, const std::vector<double>& partner_start,
  const geometry_msgs::msg::Pose& target, const std::string& label,
  trajectory_msgs::msg::JointTrajectory* output,
  const std::string& eef_link, bool avoid_collisions = false)
{
  const auto model = group.getRobotModel();
  const auto* own = model->getJointModelGroup(own_group);
  const auto* partner = model->getJointModelGroup(partner_group);
  if (!own || !partner || own_start.empty() || partner_start.empty())
  {
    return false;
  }
  // 同一个起点可能因为 IK 采样序列不同而产生贴线或离线的轨迹。先按默认步长试，
  // 只有在轨迹离线时才换步长重试；不接受任何不贴线的轨迹。
  const std::array<double, 4> steps{kCartesianStep, 0.0015, 0.003, 0.001};
  for (const double step : steps)
  {
    for (int attempt = 1; attempt <= kRetries; ++attempt)
    {
      g_operation_guard();
      auto state = group.getCurrentState(2.0);
      if (!state)
      {
        return false;
      }
      state->setJointGroupPositions(own, own_start);
      state->setJointGroupPositions(partner, partner_start);
      state->update();
      group.setStartState(*state);
      moveit_msgs::msg::RobotTrajectory candidate;
      moveit_msgs::msg::MoveItErrorCodes error;
      // 共同搬运阶段的完整双臂 FCL 在候选同步后进行；不能把搭档臂冻结在阶段
      // 起点而误判。但空载接触阶段必须同时避开桌面，故由调用点显式开启。
      const double fraction = group.computeCartesianPath(
        {target}, step, kCartesianJumpThreshold, candidate, avoid_collisions, &error);
      if (fraction < kMinCartesianFraction || candidate.joint_trajectory.points.empty())
      {
        RCLCPP_INFO(node->get_logger(), "%s Cartesian fraction=%.4f error=%d step=%.4f attempt=%d/%d.",
          label.c_str(), fraction, error.val, step, attempt, kRetries);
        continue;
      }
      const double deviation = cartesianLineDeviation(
        model, eef_link, candidate.joint_trajectory, target);
      RCLCPP_INFO(node->get_logger(),
        "%s Cartesian fraction=%.4f error=%d step=%.4f attempt=%d/%d line_deviation=%.3f mm.",
        label.c_str(), fraction, error.val, step, attempt, kRetries, deviation * 1000.0);
      if (deviation > kMaxCartesianLineDeviation)
      {
        RCLCPP_WARN(node->get_logger(),
          "%s rejected: 中间状态离线 %.1f mm（超过 %.1f mm）；换步长重规划。",
          label.c_str(), deviation * 1000.0, kMaxCartesianLineDeviation * 1000.0);
        break;
      }
      *output = candidate.joint_trajectory;
      ensureTiming(*output);
      return true;
    }
  }
  return false;
}

std::vector<moveit_msgs::msg::CollisionObject> staticWorld(
  moveit::planning_interface::PlanningSceneInterface& scene)
{
  std::vector<moveit_msgs::msg::CollisionObject> objects;
  for (const auto& [id, object] : scene.getObjects())
  {
    (void)id;
    objects.push_back(object);
  }
  return objects;
}

bool planAndCheckCommon(
  const rclcpp::Node::SharedPtr& node, moveit::planning_interface::MoveGroupInterface& left_group,
  moveit::planning_interface::MoveGroupInterface& right_group, const Arm& left, const Arm& right,
  const std::vector<double>& left_start, const std::vector<double>& right_start,
  const geometry_msgs::msg::Pose& left_target, const geometry_msgs::msg::Pose& right_target,
  const std::vector<moveit_msgs::msg::CollisionObject>& world, const std::string& stage,
  trajectory_msgs::msg::JointTrajectory* left_output, trajectory_msgs::msg::JointTrajectory* right_output)
{
  // 共同负载段：两臂在同一 phase 下同步运动，但 computeCartesianPath 只能一次
  // 规划一条单臂路径，并且会把搭档臂冻结在该段起点。Task26 的 COMMON_Y_ALIGN 需要
  // 把 Cube 从 y=-0.070 搬到目标行的 y=±0.120，两臂要一起走 +190 mm；此时“冻结的
  // 搭档臂”会被真实运动的另一臂扫到，MoveIt 会把 Cartesian 路径截断在约 63.5%
  // （实测截断点接触对为 left_fr3_side_suction <-> right_fr3_side_suction）。
  // 那是冻结假设造成的假阳性，不是真实碰撞。
  //
  // 因此共同段的两条单臂路径不做“对冻结搭档”的碰撞判断，真正的门禁是紧随其后的
  // validateSync：它按同一时间参数采样左右两条轨迹，对完整双臂 RobotState 做
  // robot--robot 与 robot--world 的 FCL 检查。ACM 没有扩大，世界障碍物也没有移除，
  // 任何真实碰撞仍会在 validateSync 处以具体碰撞对和接触点被拒绝。
  if (!planCommonCartesian(node, left_group, left.groupName(), right.groupName(), left_start, right_start,
                           left_target, stage + " left", left_output, left.eefLink(), false) ||
      !planCommonCartesian(node, right_group, right.groupName(), left.groupName(), right_start, left_start,
                           right_target, stage + " right", right_output, right.eefLink(), false) ||
      !synchronize(left_output, right_output) ||
      !validateSync(node, left_group.getRobotModel(), world, *left_output, *right_output, stage))
  {
    return false;
  }
  return true;
}


}  // namespace task26_reuse
