// [ENGINEERING] D039单件fixed handoff薄入口。仅到INSERT_READY，不执行TARGET。
// rear候选/排序/FCL/同步提交复用固定631b1f Task26原语（见同目录抽取头）。
// 不运行旧main/Task27、推进/force监督；不继承旧摩擦/drive/.12速度/3x时标。
#include "task26_reused_primitives.hpp"
#include <moveit/robot_trajectory/robot_trajectory.h>
#include <moveit/trajectory_processing/iterative_time_parameterization.h>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <std_msgs/msg/string.hpp>
#include <yaml-cpp/yaml.h>
#include <nlohmann/json.hpp>
#include <fstream>

using Json = nlohmann::json;
using namespace task26_reuse;

namespace {
class SnapshotBuffer {
public:
  SnapshotBuffer(const rclcpp::Node::SharedPtr& node, const std::string& topic) {
    subscription_ = node->create_subscription<std_msgs::msg::String>(topic, 10,
      [this](const std_msgs::msg::String::SharedPtr message) {
        std::lock_guard<std::mutex> lock(mutex_);
        try {
          auto value = Json::parse(message->data);
          if (value.at("frame_id") != "world" || value.at("physics_step").get<long long>() < 1)
            throw std::runtime_error("Invalid post-step snapshot frame/step");
          for (const auto& side : {"left", "right"}) {
            if (value.at("joints").at(side).size() != 7 ||
                value.at("bases").at(side).size() != 7 ||
                value.at("tcp_poses").at(side).size() != 7)
              throw std::runtime_error("Invalid snapshot joint/pose dimensions");
          }
          if (value.at("cube_pose_xyzw").size() != 7)
            throw std::runtime_error("Invalid Cube snapshot dimensions");
          latest_ = std::move(value);
        } catch (const std::exception& error) { error_ = error.what(); }
      });
  }
  Json get() const {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!error_.empty()) throw std::runtime_error("Snapshot protocol: " + error_);
    return latest_;
  }
private:
  mutable std::mutex mutex_;
  Json latest_;
  std::string error_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

std::vector<double> vector3(const YAML::Node& value) {
  if (!value.IsSequence() || value.size() != 3) throw std::runtime_error("Missing YAML XYZ");
  std::vector<double> result;
  for (const auto& item : value) result.push_back(item.as<double>());
  return result;
}

geometry_msgs::msg::Pose identityPose(double x, double y, double z) {
  geometry_msgs::msg::Pose result;
  result.position.x = x; result.position.y = y; result.position.z = z;
  result.orientation.w = 1.;
  return result;
}

geometry_msgs::msg::Pose sidePose(double x, double y, double z, bool left, double shift) {
  // Task26 :230–254；仅world_shift作为显式输入，姿态不重新设计。
  auto result = identityPose(x - shift, y, z);
  result.orientation.w = 0.; result.orientation.x = std::sqrt(.5);
  result.orientation.y = left ? std::sqrt(.5) : -std::sqrt(.5);
  return result;
}

geometry_msgs::msg::Pose rearPose(const Json& snapshot, double shift) {
  // Task26 pushPose :257；rear面中心偏置 = half Cube .060 +既有1mm空气隙。
  const auto& c = snapshot.at("cube_pose_xyzw");
  auto result = identityPose(c.at(0).get<double>() - .061 - shift,
    c.at(1).get<double>(), c.at(2).get<double>());
  result.orientation.w = 0.; result.orientation.x = 1.;
  return result;
}

moveit_msgs::msg::CollisionObject collisionBox(const std::string& id,
    const std::vector<double>& center, const std::vector<double>& size, double shift) {
  moveit_msgs::msg::CollisionObject result;
  result.header.frame_id = "world"; result.id = id; result.operation = result.ADD;
  shape_msgs::msg::SolidPrimitive shape;
  shape.type = shape.BOX; shape.dimensions = {size.at(0), size.at(1), size.at(2)};
  result.primitives.push_back(shape);
  result.primitive_poses.push_back(identityPose(center.at(0) - shift, center.at(1), center.at(2)));
  return result;
}

const std::vector<std::string> kWorldIds{
  "task01_table", "task01_carriage_deep_wall", "task01_carriage_minus_y_wall",
  "task01_carriage_plus_y_wall", "task01_cube"};

std::vector<moveit_msgs::msg::CollisionObject> worldObjects(
    const YAML::Node& config, const Json& snapshot, double shift) {
  std::vector<moveit_msgs::msg::CollisionObject> objects;
  objects.push_back(collisionBox(kWorldIds[0], vector3(config["table"]["center_world_m"]),
    vector3(config["table"]["size_m"]), shift));
  const auto carriage = config["carriage"];
  const double x0 = carriage["interior_x_world_m"][0].as<double>();
  const double x1 = carriage["interior_x_world_m"][1].as<double>();
  const double y0 = carriage["interior_y_world_m"][0].as<double>();
  const double y1 = carriage["interior_y_world_m"][1].as<double>();
  const double thickness = carriage["wall_thickness_m"].as<double>();
  const double height = carriage["wall_height_m"].as<double>();
  const double z = config["table"]["top_world_z_m"].as<double>() + height / 2.;
  objects.push_back(collisionBox(kWorldIds[1], {x1+thickness/2., (y0+y1)/2., z},
    {thickness, y1-y0+2*thickness, height}, shift));
  objects.push_back(collisionBox(kWorldIds[2], {(x0+x1)/2., y0-thickness/2., z},
    {x1-x0+2*thickness, thickness, height}, shift));
  objects.push_back(collisionBox(kWorldIds[3], {(x0+x1)/2., y1+thickness/2., z},
    {x1-x0+2*thickness, thickness, height}, shift));
  const auto cube = snapshot.at("cube_pose_xyzw").get<std::vector<double>>();
  auto object = collisionBox(kWorldIds[4], {cube[0], cube[1], cube[2]},
    vector3(config["cube"]["size_m"]), shift);
  auto& q = object.primitive_poses[0].orientation;
  q.x=cube[3]; q.y=cube[4]; q.z=cube[5]; q.w=cube[6];
  objects.push_back(object);
  return objects;
}

trajectory_msgs::msg::JointTrajectory referenceTrajectory(
    const moveit::core::RobotModelConstPtr& model, const std::string& group, const Json& q) {
  trajectory_msgs::msg::JointTrajectory result;
  const auto* joints = model->getJointModelGroup(group);
  if (!joints) throw std::runtime_error("Missing planning group " + group);
  result.joint_names = joints->getVariableNames();
  trajectory_msgs::msg::JointTrajectoryPoint point;
  point.positions = q.get<std::vector<double>>();
  result.points.push_back(point);
  return result;
}

double cubeDrift(const Json& a, const Json& b) {
  double squared = 0.;
  for (int i=0; i<3; ++i) squared += std::pow(
    a.at("cube_pose_xyzw").at(i).get<double>() - b.at("cube_pose_xyzw").at(i).get<double>(), 2);
  return std::sqrt(squared);
}

void verifyRails(const Json& state, double requested) {
  for (const auto& side : {"left", "right"}) {
    const double measured = state.at("rails").at(side).at("measured_x_m").get<double>();
    const double base = state.at("bases").at(side).at(0).get<double>();
    if (!std::isfinite(measured) || std::abs(measured-requested) > 1e-5 ||
        std::abs(base-measured) > 1e-5)
      throw std::runtime_error(std::string(side) + " measured rail/base inconsistent");
  }
  if (std::abs(state.at("world_shift_x_m").get<double>() - (requested-.650)) > 1e-5)
    throw std::runtime_error("Measured common world shift mismatch");
}
}

int main(int argc, char** argv) {
  // 纯消息/坐标/原语检查：在rclcpp::init之前，不创建ROS/IK/仿真或执行接口。
  if (argc == 3 && std::string(argv[1]) == "--self-test") {
    try {
      const auto config = YAML::LoadFile(argv[2]);
      const Json snapshot = {{"cube_pose_xyzw", {.790,0.,.260,0.,0.,0.,1.}}};
      const auto before = worldObjects(config,snapshot,0.);
      const auto after = worldObjects(config,snapshot,.100);
      if (before.size()!=5 || after.size()!=5 || before[0].primitives[0].dimensions[0]!=1.5)
        throw std::runtime_error("Single-Cube/current table geometry mismatch");
      for (std::size_t i=0; i<before.size(); ++i) {
        if (before[i].id!=kWorldIds[i] || before[i].primitives!=after[i].primitives ||
            std::abs(before[i].primitive_poses[0].position.x-
              after[i].primitive_poses[0].position.x-.100)>1e-12)
          throw std::runtime_error("Fixed shifted-world projection mismatch");
      }
      if (std::abs(rearPose(snapshot,.100).position.x-.629)>1e-12)
        throw std::runtime_error("Original rear transform mismatch");
      trajectory_msgs::msg::JointTrajectory trajectory;
      trajectory.joint_names={"left_fr3_joint1"};
      trajectory_msgs::msg::JointTrajectoryPoint first,last;
      first.positions={0.}; last.positions={.2}; setPointTime(last,1.);
      trajectory.points={first,last};
      if (std::abs(interpolate(trajectory,.5)[0]-.1)>1e-12 ||
          interpolate(trajectory,-1.)[0]!=0. || interpolate(trajectory,2.)[0]!=.2)
        throw std::runtime_error("Task26 interpolation regression");
      std::cout << "PURE SELF TEST PASS: 5 current objects, fixed .100 projection, rear pose, Task26 interpolation; no ROS/IK/Isaac\n";
      return 0;
    } catch (const std::exception& error) {
      std::cerr << "PURE SELF TEST FAIL: " << error.what() << '\n'; return 2;
    }
  }
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("task01_rear_handoff",
    rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));
  const auto parameter = [&](const std::string& name, auto value) {
    using T = decltype(value);
    return node->has_parameter(name) ? node->get_parameter(name).get_value<T>() :
      node->declare_parameter<T>(name, value);
  };
  const std::string config_path = parameter("benchmark_config", std::string(""));
  const std::string snapshot_topic = parameter("snapshot_topic", std::string("/task01/ready_snapshot"));
  const double deadline_sec = parameter("deadline_sec", 120.0);
  const double cube_drift_guard_m = parameter("cube_drift_guard_m", .005);
  g_joint_settle_limit_rad = parameter("joint_settle_limit_rad", .01);
  SnapshotBuffer snapshots(node, snapshot_topic);
  auto rail_pub = node->create_publisher<std_msgs::msg::String>("/task01/rail_command", 10);
  auto ack_pub = node->create_publisher<std_msgs::msg::String>("/task01/planning_world_ack", 10);
  auto capture_pub = node->create_publisher<std_msgs::msg::Bool>("/task01/capture_insert_ready", 10);
  Arm left(node, true, 1.0), right(node, false, 1.0);
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  std::thread spin([&] { executor.spin(); });
  int exit_code = 1;
  const auto deadline = std::chrono::steady_clock::now() + std::chrono::duration<double>(deadline_sec);
  g_seconds_remaining = [&] { return std::chrono::duration<double>(deadline-
    std::chrono::steady_clock::now()).count(); };
  g_operation_guard = [&] {
    if (!rclcpp::ok() || g_seconds_remaining() <= 0.)
      throw std::runtime_error("One bounded handoff wall deadline reached");
    auto state = snapshots.get();
    if (state.is_object()) {
      if (state.contains("halted") && state.at("halted").get<bool>())
        throw std::runtime_error("Isaac reported HALTED; no retry permitted");
      if (state.contains("error") && !state.at("error").is_null() &&
          state.at("error") != "") throw std::runtime_error("Isaac error: " + state.at("error").dump());
    }
  };
  const auto wait = [&](const std::string& label, const std::function<bool(const Json&)>& predicate,
                        double timeout) {
    const auto end = std::chrono::steady_clock::now() + std::chrono::duration<double>(
      std::min(timeout, std::max(0., g_seconds_remaining())));
    while (std::chrono::steady_clock::now() < end) {
      g_operation_guard();
      const auto state = snapshots.get();
      if (state.is_object() && predicate(state)) return state;
      std::this_thread::sleep_for(20ms);
    }
    throw std::runtime_error(label + " timeout; STOP without fallback");
  };
  try {
    if (config_path.empty()) throw std::runtime_error("benchmark_config required");
    const auto config = YAML::LoadFile(config_path);
    if (config["cube"]["count"].as<int>() != 1 || config["status"].as<std::string>() != "DRAFT")
      throw std::runtime_error("Only current DRAFT single-Cube candidate is authorized");
    const auto initial = wait("bilateral-held PRE_PUSH", [](const Json& s) {
      return s.value("handoff_initial_ready", false) &&
        s.at("suction").at("left_closed").get<bool>() &&
        s.at("suction").at("right_closed").get<bool>();
    }, 15.);
    verifyRails(initial, .650);
    if (!left.waitBridge() || !right.waitBridge()) throw std::runtime_error("Existing bridge not ready");
    moveit::planning_interface::MoveGroupInterface left_group(node, left.groupName());
    moveit::planning_interface::MoveGroupInterface right_group(node, right.groupName());
    for (auto* group : {&left_group, &right_group}) {
      group->setPlannerId("RRTConnectkConfigDefault");
      group->setMaxVelocityScalingFactor(1.0); group->setMaxAccelerationScalingFactor(1.0);
      group->setPoseReferenceFrame("world");
    }
    left_group.setEndEffectorLink(left.eefLink()); right_group.setEndEffectorLink(right.eefLink());
    const auto model = left_group.getRobotModel();
    g_retime_untimed = [&](trajectory_msgs::msg::JointTrajectory& input) {
      moveit::core::RobotState state(model); state.setToDefaultValues();
      const auto current = snapshots.get();
      state.setJointGroupPositions("left_arm", current.at("joints").at("left").get<std::vector<double>>());
      state.setJointGroupPositions("right_arm", current.at("joints").at("right").get<std::vector<double>>());
      state.update();
      const std::string own = input.joint_names.front().rfind("left_", 0) == 0 ? "left_arm" : "right_arm";
      robot_trajectory::RobotTrajectory trajectory(model, own);
      moveit_msgs::msg::RobotTrajectory message; message.joint_trajectory = input;
      trajectory.setRobotTrajectoryMsg(state, message);
      trajectory_processing::IterativeParabolicTimeParameterization retimer;
      if (!retimer.computeTimeStamps(trajectory, 1.0, 1.0))
        throw std::runtime_error("Current-limit MoveIt retiming failed");
      trajectory.getRobotTrajectoryMsg(message); input = message.joint_trajectory;
      if (pointTime(input.points.back()) <= 0.) throw std::runtime_error("Nonpositive retimed duration");
    };
    moveit::planning_interface::PlanningSceneInterface scene;
    int generation = 0;
    const auto refresh = [&](const Json& measured, double shift, const std::string& helper_label) {
      g_operation_guard();
      verifyRails(measured, shift + .650);
      const auto expected = worldObjects(config, measured, shift);
      const auto previous = scene.getObjects();
      for (const auto& [id, unused] : previous) {
        (void)unused;
        if (std::find(kWorldIds.begin(), kWorldIds.end(), id) == kWorldIds.end())
          throw std::runtime_error("Foreign/stale collision object: " + id);
      }
      scene.removeCollisionObjects(kWorldIds);
      if (!scene.applyCollisionObjects(expected)) throw std::runtime_error("Planning world refresh failed");
      const auto actual = scene.getObjects(kWorldIds);
      if (actual.size() != expected.size()) throw std::runtime_error("Missing refreshed world objects");
      for (const auto& object : expected) {
        const auto& observed = actual.at(object.id);
        if (observed.primitives.size() != 1 || observed.primitive_poses.size() != 1 ||
            observed.primitives[0].dimensions != object.primitives[0].dimensions ||
            observed.primitive_poses[0] != object.primitive_poses[0])
          throw std::runtime_error("Planning object differs after shift: " + object.id);
      }
      const long long prior_step = measured.at("physics_step");
      Json ack = {{"refreshed", true}, {"generation", ++generation}, {"world_shift_x_m", shift},
        {"measured_rail_x_m", {
          {"left", measured.at("rails").at("left").at("measured_x_m")},
          {"right", measured.at("rails").at("right").at("measured_x_m")}}},
        {"required_objects", kWorldIds}, {"helper_park_label", helper_label}};
      std_msgs::msg::String message; message.data = ack.dump(); ack_pub->publish(message);
      const auto acknowledged = wait("post-step planning world ACK", [&](const Json& s) {
        return s.at("physics_step").get<long long>() > prior_step && s.contains("planning_world") &&
          s.at("planning_world").value("refreshed", false) &&
          s.at("planning_world").value("generation", -1) == generation &&
          std::abs(s.at("planning_world").at("world_shift_x_m").get<double>()-shift) < 1e-9;
      }, 5.);
      verifyRails(acknowledged, shift+.650);
      // 新建每次FCL场景并从刚确认的world取得，绝不使用移动前FCL缓存。
      return staticWorld(scene);
    };
    // Open必须真实确认；不能消费旧缓存CLOSED/OPEN标记就开始动轨。
    const long long open_step = initial.at("physics_step");
    std::thread left_off([&] { left.suction(false); });
    right.suction(false); left_off.join();
    const auto opened = wait("bilateral OPEN confirmed", [&](const Json& s) {
      return s.at("physics_step").get<long long>() > open_step &&
        !s.at("suction").at("left_closed").get<bool>() &&
        !s.at("suction").at("right_closed").get<bool>();
    }, 6.);
    auto world = refresh(opened, 0., "PRE_PUSH_OPEN");
    trajectory_msgs::msg::JointTrajectory left_safe, right_safe;
    if (!planAndCheckCommon(node, left_group, right_group, left, right,
        opened.at("joints").at("left").get<std::vector<double>>(),
        opened.at("joints").at("right").get<std::vector<double>>(),
        sidePose(.690,-.320,.560,true,0.), sidePose(.790,.061,.560,false,0.),
        world, "REUSED_SAFE_HELPER_PUSHER_TRANSITION", &left_safe, &right_safe))
      throw std::runtime_error("Old safe helper/pusher transition geometry rejected");
    if (!executeSync(left,left_safe,right,right_safe)) throw std::runtime_error("Safe transition did not settle");
    const auto safe = snapshots.get();
    if (cubeDrift(opened, safe) > cube_drift_guard_m)
      throw std::runtime_error("Cube drifted during empty safe transition");
    // 既有rail互锁要求both OPEN且joint命令静默>=1s。
    const auto quiet_end = std::chrono::steady_clock::now() + 1100ms;
    while (std::chrono::steady_clock::now() < quiet_end) { g_operation_guard(); std::this_thread::sleep_for(20ms); }
    std_msgs::msg::String rail_message;
    rail_message.data = Json({{"left_x", .750}, {"right_x", .750}}).dump();
    rail_pub->publish(rail_message);
    const auto shifted = wait("both measured rails .750", [&](const Json& s) {
      return s.at("physics_step").get<long long>() > safe.at("physics_step").get<long long>() &&
        std::abs(s.at("rails").at("left").at("measured_x_m").get<double>()-.750) < 1e-5 &&
        std::abs(s.at("rails").at("right").at("measured_x_m").get<double>()-.750) < 1e-5;
    }, 15.);
    verifyRails(shifted, .750);
    if (cubeDrift(opened, shifted) > cube_drift_guard_m)
      throw std::runtime_error("Cube drifted during reused rail movement");
    world = refresh(shifted,.100,"LEFT_HELPER_PARK_AFTER_FIXED_RAIL_ADVANCE");
    // Task26 preplanPush的rear候选筛选，仅执行/捕获rear部分；B整链留下一阶段。
    const auto reference = snapshots.get();
    const auto left_reference = referenceTrajectory(model,"left_arm",reference.at("joints").at("left"));
    std::vector<trajectory_msgs::msg::JointTrajectory> candidates;
    if (!right.planPoseCandidatesFrom(right_group,
        reference.at("joints").at("right").get<std::vector<double>>(),
        rearPose(reference,.100),"REUSED_RIGHT_REAR_NEG_X",&candidates))
      throw std::runtime_error("Bounded reused rear RRT candidate pool exhausted");
    trajectory_msgs::msg::JointTrajectory chosen, chosen_hold;
    for (const auto& candidate : candidates) {
      g_operation_guard();
      auto hold = holdTrajectory(left_reference, finalPositions(left_reference), pointTime(candidate.points.back()));
      if (validateSync(node,model,world,hold,candidate,"REUSED_REAR_CANDIDATE")) {
        chosen=candidate; chosen_hold=std::move(hold); break;
      }
    }
    if (chosen.points.empty()) throw std::runtime_error("No reused rear candidate passed complete RobotState FCL");
    if (!executeSync(left,chosen_hold,right,chosen)) throw std::runtime_error("Rear approach did not settle");
    const auto before_close = snapshots.get();
    if (cubeDrift(reference,before_close) > cube_drift_guard_m)
      throw std::runtime_error("Cube drifted during rear regrasp approach");
    right.suction(true);
    const auto closed = wait("right rear CLOSED", [&](const Json& s) {
      return s.at("physics_step").get<long long>() > before_close.at("physics_step").get<long long>() &&
        !s.at("suction").at("left_closed").get<bool>() &&
        s.at("suction").at("right_closed").get<bool>();
    }, 6.);
    verifyRails(closed,.750);
    if (cubeDrift(reference,closed) > cube_drift_guard_m)
      throw std::runtime_error("Cube drifted while rear attachment CLOSED");
    std_msgs::msg::Bool request; request.data=true; capture_pub->publish(request);
    const auto captured = wait("atomic INSERT_READY capture", [&](const Json& s) {
      return s.at("physics_step").get<long long>() > closed.at("physics_step").get<long long>() &&
        s.value("insert_ready_captured",false);
    }, 6.);
    RCLCPP_INFO(node->get_logger(),
      "INSERT_READY CAPTURED: step=%lld sim_stamp_ns=%lld rails=.750/.750; no TARGET command. TASK01 remains PARTIAL.",
      captured.at("physics_step").get<long long>(), captured.at("simulation_stamp_ns").get<long long>());
    exit_code=0;
  } catch (const std::exception& error) {
    RCLCPP_ERROR(node->get_logger(),"BOUNDED HANDOFF STOP: %s. No second station/path experiment.",error.what());
    // 单件由桌面支撑；停止入口，不发布任何进一步joint/rail/push命令。
    try { left.suction(false); right.suction(false); } catch (...) {}
  }
  executor.cancel(); if (spin.joinable()) spin.join();
  rclcpp::shutdown(); return exit_code;
}
