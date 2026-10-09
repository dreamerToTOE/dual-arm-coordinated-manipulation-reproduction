// [ENGINEERING] 一次有界、确定性、离线的真实 FR3 投影验收；没有执行或碰撞接口。
#include "platforms/offline_moveit/task03_closure/model_adapter.hpp"
#include "baselines/p4_closed_chain/projection.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include <yaml-cpp/yaml.h>

namespace
{
using Json = nlohmann::json;
using Model = task03_offline::DualFr3Model;

// 仅保留 TASK03 已声明历史精度；不改数据、不改门限、不回写投影后的 q。
constexpr double TASK03_POSITION_LIMIT_M = 5e-8;
constexpr double TASK03_ROTATION_LIMIT_RAD = 2e-5;

std::string readText(const std::string& path)
{
  std::ifstream stream(path);
  if (!stream)
    throw std::invalid_argument("Cannot read unchanged input: " + path);
  std::ostringstream output;
  output << stream.rdbuf();
  return output.str();
}

Json expectedProtocol()
{
  // D048 运行前锁定的工程协议。拒绝额外/缺失/修改字段，而不是事后调参。
  return {{"schema", "task04.offline_projection_test.v1"},
          {"classification", "PREDECLARED_ENGINEERING_TEST_NOT_BENCHMARK"},
          {"position_tolerance_m", 1e-8}, {"rotation_tolerance_rad", 1e-8},
          {"max_iterations", 40}, {"svd_absolute_cutoff", 1e-12},
          {"svd_relative_cutoff", 1e-10}, {"stagnation_step_rad", 1e-14},
          {"required_rank_for_correction", 6}, {"row_weighting", "NONE_FIXED_SI_M_RAD"},
          {"damping", false}, {"line_search", false},
          {"joint_limit_policy", "REJECT_FULL_UPDATE_NO_CLAMP"},
          {"perturbation_magnitudes_rad", {0.001, 0.01, 0.03}},
          {"coupled_directions", 4}, {"neighborhood_cases", 97},
          {"neighborhood_repeats", 2}, {"repeat_joint_max_abs_tolerance_rad", 1e-12},
          {"historical_diagnostic_records", 293}, {"random_seed", nullptr},
          {"random_sampling_used", false}, {"physics_or_collision_claim", false},
          {"benchmark_frozen", false}};
}

template<class Derived>
Json vectorJson(const Eigen::MatrixBase<Derived>& value)
{
  Json output = Json::array();
  for (Eigen::Index index = 0; index < value.size(); ++index)
    output.push_back(value(index));
  return output;
}

Json residualJson(const p4::Residual& value)
{
  return {{"position_vector_world_m", vectorJson(value.head<3>())},
          {"rotation_log_right_object_rad", vectorJson(value.tail<3>())},
          {"position_norm_m", value.head<3>().norm()},
          {"rotation_norm_rad", value.tail<3>().norm()},
          {"mixed_unit_norm_not_used_for_acceptance", true}};
}

Json optionalResidual(const std::optional<p4::Residual>& value)
{
  return value ? residualJson(*value) : Json(nullptr);
}

Json poseJson(const Eigen::Isometry3d& value,
              const std::string& direction = "T^TCP_Object maps Object coordinates into TCP")
{
  const Eigen::Quaterniond quaternion(value.linear());
  return {{"translation_m", vectorJson(value.translation())},
          {"quaternion_xyzw", {quaternion.x(), quaternion.y(), quaternion.z(), quaternion.w()}},
          {"direction", direction}};
}

p4::JointVector joints(const Json& row)
{
  const auto& left = row.at("left_q_rad");
  const auto& right = row.at("right_q_rad");
  if (!left.is_array() || !right.is_array() || left.size() != 7 || right.size() != 7)
    throw std::invalid_argument("Historical row does not contain unchanged 14q");
  p4::JointVector output;
  for (int joint = 0; joint < 7; ++joint)
  {
    output[joint] = left[joint].get<double>();
    output[joint + 7] = right[joint].get<double>();
  }
  if (!output.allFinite())
    throw std::invalid_argument("Historical 14q is nonfinite");
  return output;
}

Eigen::Isometry3d originalGrasp(const YAML::Node& value)
{
  const auto p = value["translation_m"], q = value["quaternion_xyzw"];
  if (p.size() != 3 || q.size() != 4)
    throw std::invalid_argument("Original archived grasp representation is invalid");
  return common_geometry::fromXyzw(
      Eigen::Vector3d(p[0].as<double>(), p[1].as<double>(), p[2].as<double>()),
      Eigen::Vector4d(q[0].as<double>(), q[1].as<double>(), q[2].as<double>(), q[3].as<double>()));
}

Eigen::Isometry3d startObject(const Json& row)
{
  const auto& p = row.at("cube_center_world_m");
  const auto& q = row.at("cube_orientation_xyzw");
  if (p.size() != 3 || q.size() != 4)
    throw std::invalid_argument("Original archived START Object pose is invalid");
  return common_geometry::fromXyzw(
      Eigen::Vector3d(p[0], p[1], p[2]), Eigen::Vector4d(q[0], q[1], q[2], q[3]));
}

p4::ClosureSample evaluate(Model& model, const p4::JointVector& q,
                           const Eigen::Isometry3d& gl, const Eigen::Isometry3d& gr)
{
  const auto arms = model.sample(q);
  return p4::evaluate(arms.first, arms.second, gl, gr);
}

void requireCheck(bool condition, const std::string& message, std::vector<std::string>& failures)
{
  if (!condition)
    failures.push_back(message);
}

bool converged(const p4::ProjectionResult& value, const p4::ProjectionOptions& options)
{
  return value.status == p4::ProjectionStatus::CONVERGED && value.final_residual &&
         value.final_residual->allFinite() &&
         value.final_residual->head<3>().norm() <= options.position_tolerance_m &&
         value.final_residual->tail<3>().norm() <= options.rotation_tolerance_rad;
}

Json projectionJson(const p4::ProjectionResult& value, Model& model,
                    const p4::ProjectionOptions& options)
{
  Json history = Json::array();
  for (const auto& step : value.history)
  {
    Json record = {{"update_index", step.update_index},
                   {"q_before_rad", vectorJson(step.q_before)},
                   {"residual_before", residualJson(step.residual_before)},
                   {"joint_margin_before_rad", step.joint_margin_before_rad},
                   {"numerical_rank", step.numerical_rank},
                   {"update_accepted", step.update_accepted}, {"note", step.note},
                   {"singular_values", nullptr}, {"singular_cutoff", nullptr},
                   {"proposed_delta_q_rad", nullptr}, {"proposed_q_rad", nullptr},
                   {"candidate_joint_margin_rad", nullptr}, {"residual_after", nullptr}};
    if (step.singular_values) record["singular_values"] = vectorJson(*step.singular_values);
    if (step.singular_cutoff) record["singular_cutoff"] = *step.singular_cutoff;
    if (step.proposed_delta_q) record["proposed_delta_q_rad"] = vectorJson(*step.proposed_delta_q);
    if (step.proposed_q) record["proposed_q_rad"] = vectorJson(*step.proposed_q);
    if (step.candidate_joint_margin_rad) record["candidate_joint_margin_rad"] = *step.candidate_joint_margin_rad;
    if (step.residual_after) record["residual_after"] = residualJson(*step.residual_after);
    history.push_back(std::move(record));
  }
  Json output = {{"status", p4::statusName(value.status)}, {"reason", value.reason},
                 {"converged_under_declared_separate_tests", converged(value, options)},
                 {"initial_q_rad", vectorJson(value.initial_q)},
                 {"projected_q_rad", vectorJson(value.projected_q)},
                 {"initial_residual", optionalResidual(value.initial_residual)},
                 {"final_residual", optionalResidual(value.final_residual)},
                 {"joint_delta_norm_rad", value.joint_delta_norm_rad ? Json(*value.joint_delta_norm_rad) : Json(nullptr)},
                 {"joint_delta_max_abs_rad", value.joint_delta_max_abs_rad ? Json(*value.joint_delta_max_abs_rad) : Json(nullptr)},
                 {"accepted_updates", value.accepted_updates}, {"constraint_evaluations", value.evaluations},
                 {"compute_wall_time_sec", value.compute_wall_time_sec},
                 {"time_qualification", "CPU_COMPUTE_WALL_TIME_NOT_SIMULATION_OR_PHYSICAL_EXECUTION"},
                 {"initial_native_joint_margin_rad", model.minimumJointMargin(value.initial_q)},
                 {"final_native_joint_margin_rad", model.minimumJointMargin(value.projected_q)},
                 {"history", history}};
  return output;
}

// 独立检查输出契约，不重写 C/Jc/FK 或投影算法；不因此改变收敛标准。
void auditResult(const p4::ProjectionResult& value, const p4::JointVector& input,
                 Model& model, const p4::ProjectionOptions& options,
                 const std::string& name, std::vector<std::string>& failures)
{
  requireCheck(value.initial_q.allFinite() && value.projected_q.allFinite(), name + ": finite q", failures);
  requireCheck((value.initial_q - input).cwiseAbs().maxCoeff() == 0., name + ": initial q preserved", failures);
  requireCheck(value.accepted_updates <= options.max_iterations, name + ": bounded iteration count", failures);
  requireCheck(std::isfinite(value.compute_wall_time_sec) && value.compute_wall_time_sec >= 0.,
               name + ": qualified compute wall time", failures);
  requireCheck(model.minimumJointMargin(value.projected_q) >= 0., name + ": original joint limits", failures);
  requireCheck(value.initial_residual && value.initial_residual->allFinite() &&
               value.final_residual && value.final_residual->allFinite(), name + ": residuals preserved", failures);
  const p4::JointVector delta = value.projected_q - input;
  requireCheck(value.joint_delta_norm_rad && value.joint_delta_max_abs_rad &&
               *value.joint_delta_norm_rad == delta.norm() &&
               *value.joint_delta_max_abs_rad == delta.cwiseAbs().maxCoeff(), name + ": actual q change metadata", failures);
  std::size_t accepted = 0;
  for (const auto& step : value.history)
  {
    requireCheck(step.q_before.allFinite() && step.residual_before.allFinite() &&
                 step.joint_margin_before_rad >= 0., name + ": valid history before update", failures);
    if (step.update_accepted)
    {
      ++accepted;
      requireCheck(step.proposed_q && step.proposed_q->allFinite() && step.proposed_delta_q &&
                   step.proposed_delta_q->allFinite() && step.candidate_joint_margin_rad &&
                   *step.candidate_joint_margin_rad >= 0. && step.residual_after &&
                   step.residual_after->allFinite() && step.numerical_rank == 6,
                   name + ": accepted full update invariant", failures);
    }
  }
  requireCheck(accepted == value.accepted_updates, name + ": history update count", failures);
}

struct Trial
{
  std::string id;
  std::string kind;
  p4::JointVector input;
  double amplitude_rad;
  int joint_index{-1};
  int sign{0};
  int direction_index{-1};
  p4::JointVector direction{p4::JointVector::Zero()};
};

void run(const std::map<std::string, std::string>& paths, Json& output)
{
  const Json protocol = Json::parse(readText(paths.at("--protocol")));
  output["raw_protocol"] = protocol;
  if (protocol != expectedProtocol())
    throw std::invalid_argument("Protocol differs from the predeclared D048 v1; stop without tuning");
  const p4::ProjectionOptions options{
      protocol.at("position_tolerance_m"), protocol.at("rotation_tolerance_rad"),
      protocol.at("max_iterations"), protocol.at("svd_absolute_cutoff"),
      protocol.at("svd_relative_cutoff"), protocol.at("stagnation_step_rad")};
  const std::string urdf_path = "tests/fixtures/task03/robot.urdf";
  const std::string srdf_path = "tests/fixtures/task03/robot.srdf";
  const std::string rows_path = "results/20261007_TASK01_full_single_cube_geometry01/state_records.json";
  const std::string config_path = "results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml";
  output["input_paths"] = {{"urdf", urdf_path}, {"srdf", srdf_path},
                           {"historical_states", rows_path}, {"historical_config", config_path},
                           {"protocol", paths.at("--protocol")}};
  Model model(readText(urdf_path), readText(srdf_path));
  const Json rows = Json::parse(readText(rows_path));
  const YAML::Node original = YAML::Load(readText(config_path));
  if (!rows.is_array() || rows.size() != protocol.at("historical_diagnostic_records").get<std::size_t>())
    throw std::invalid_argument("Expected unchanged 293 historical records");
  for (std::size_t index = 0; index < rows.size(); ++index)
    if (rows[index].at("state_index").get<std::size_t>() != index)
      throw std::invalid_argument("Original historical state indices are not ordered");

  const Eigen::Isometry3d original_gl = originalGrasp(original["shared_grasp"]["object_to_left_tcp_candidate"]).inverse();
  const Eigen::Isometry3d original_gr = originalGrasp(original["shared_grasp"]["object_to_right_tcp_candidate"]).inverse();
  const p4::JointVector q0 = joints(rows[0]);
  const auto start_arms = model.sample(q0);
  const Eigen::Isometry3d object = startObject(rows[0]);
  // 仅此一次构造代数测试 G*；后续194+293调用中的抓取变换固定不重拟合。
  const Eigen::Isometry3d algebraic_gl = start_arms.first.world_tcp.inverse() * object;
  const Eigen::Isometry3d algebraic_gr = start_arms.second.world_tcp.inverse() * object;
  const auto margin = [&](const p4::JointVector& q) { return model.minimumJointMargin(q); };
  const auto algebraic_evaluate = [&](const p4::JointVector& q) {
    return evaluate(model, q, algebraic_gl, algebraic_gr);
  };
  const auto historical_evaluate = [&](const p4::JointVector& q) {
    return evaluate(model, q, original_gl, original_gr);
  };
  output["joint_names"] = model.jointNames();
  output["grasp_fixtures"] = {
      {"algebraic_once_fixed", {{"classification", "REAL_FR3_MODEL_ALGEBRAIC_FIXTURE_NOT_PHYSICAL_GRASP"},
         {"formula", "G*_i = FK_TCP_i(q0)^-1 * archived_START_Object; compute once then fixed"},
         {"q0_source_state_index", 0}, {"q0_rad", vectorJson(q0)},
         {"object_world_pose", poseJson(object, "T^World_Object maps Object coordinates into World")},
         {"left_tcp_to_object", poseJson(algebraic_gl)},
         {"right_tcp_to_object", poseJson(algebraic_gr)}, {"refit_during_trials", false},
         {"benchmark_or_suction_calibration", false}}},
      {"historical_original_fixed", {{"classification", "INDEPENDENT_ORIGINAL_GRASP_DIAGNOSTIC"},
         {"source", config_path}, {"direction_conversion", "invert archived T^Object_TCP to T^TCP_Object"},
         {"left_tcp_to_object", poseJson(original_gl)}, {"right_tcp_to_object", poseJson(original_gr)},
         {"refit_during_trials", false}, {"historical_q_or_results_written", false}}}};

  std::vector<Trial> trials;
  trials.push_back({"zero", "ZERO_PERTURBATION", q0, 0.});
  const std::array<double, 3> amplitudes{0.001, 0.01, 0.03};
  for (int joint = 0; joint < 14; ++joint)
    for (int sign : {-1, 1})
      for (std::size_t index = 0; index < amplitudes.size(); ++index)
      {
        p4::JointVector direction = p4::JointVector::Zero();
        direction[joint] = sign;
        Trial trial{"joint_" + std::to_string(joint) + "_sign_" + std::to_string(sign) +
                      "_amplitude_" + std::to_string(index), "SINGLE_JOINT", q0 + amplitudes[index] * direction,
                      amplitudes[index], joint, sign};
        trial.direction = direction;
        trials.push_back(std::move(trial));
      }
  for (int direction_index = 0; direction_index < 4; ++direction_index)
  {
    p4::JointVector direction;
    for (int joint = 0; joint < 14; ++joint)
      direction[joint] = std::sin(0.7 * static_cast<double>((direction_index + 1) * (joint + 1)));
    direction.normalize();
    for (std::size_t index = 0; index < amplitudes.size(); ++index)
    {
      Trial trial{"coupled_" + std::to_string(direction_index) + "_amplitude_" + std::to_string(index),
                  "COUPLED_SIN_DIRECTION", q0 + amplitudes[index] * direction, amplitudes[index]};
      trial.direction_index = direction_index;
      trial.direction = direction;
      trials.push_back(std::move(trial));
    }
  }
  if (trials.size() != protocol.at("neighborhood_cases").get<std::size_t>())
    throw std::logic_error("Bounded neighborhood count mismatch");

  std::vector<std::string> failures;
  std::map<std::string, std::size_t> neighborhood_statuses;
  std::map<std::string, std::size_t> historical_statuses;
  std::vector<p4::ProjectionResult> first_results;
  output["neighborhood_trials"] = Json::array();
  output["historical_diagnostic_trials"] = Json::array();
  std::size_t neighborhood_converged = 0, historical_converged = 0, projection_calls = 0;
  double maximum_repeat_q_delta = 0., max_final_position = 0., max_final_rotation = 0.;
  double minimum_output_margin = std::numeric_limits<double>::infinity();
  double total_compute_wall = 0.;
  std::size_t maximum_accepted_updates = 0;
  for (std::size_t repeat = 0; repeat < protocol.at("neighborhood_repeats").get<std::size_t>(); ++repeat)
    for (std::size_t index = 0; index < trials.size(); ++index)
    {
      const auto& trial = trials[index];
      const auto value = p4::project(trial.input, algebraic_evaluate, margin, options);
      ++projection_calls;
      const std::string name = trial.id + " repeat=" + std::to_string(repeat);
      ++neighborhood_statuses[p4::statusName(value.status)];
      neighborhood_converged += converged(value, options);
      requireCheck(converged(value, options), name + ": declared position/rotation convergence", failures);
      auditResult(value, trial.input, model, options, name, failures);
      bool repeat_equal = true;
      double repeat_delta = 0.;
      if (repeat == 0)
        first_results.push_back(value);
      else
      {
        const auto& first = first_results[index];
        repeat_delta = (value.projected_q - first.projected_q).cwiseAbs().maxCoeff();
        maximum_repeat_q_delta = std::max(maximum_repeat_q_delta, repeat_delta);
        repeat_equal = repeat_delta <= protocol.at("repeat_joint_max_abs_tolerance_rad").get<double>() &&
                       value.status == first.status && value.accepted_updates == first.accepted_updates &&
                       value.evaluations == first.evaluations;
        requireCheck(repeat_equal, name + ": deterministic q/status/update/evaluation repeat", failures);
      }
      if (index == 0)
        requireCheck(value.accepted_updates == 0 &&
                     (value.projected_q - q0).cwiseAbs().maxCoeff() == 0., name + ": zero identity", failures);
      if (value.final_residual)
      {
        max_final_position = std::max(max_final_position, value.final_residual->head<3>().norm());
        max_final_rotation = std::max(max_final_rotation, value.final_residual->tail<3>().norm());
      }
      minimum_output_margin = std::min(minimum_output_margin, model.minimumJointMargin(value.projected_q));
      total_compute_wall += value.compute_wall_time_sec;
      maximum_accepted_updates = std::max(maximum_accepted_updates, value.accepted_updates);
      Json record = projectionJson(value, model, options);
      record["trial_id"] = trial.id;
      record["repeat_index"] = repeat;
      record["kind"] = trial.kind;
      record["amplitude_rad"] = trial.amplitude_rad;
      record["perturbation_direction_14q"] = vectorJson(trial.direction);
      record["joint_index"] = trial.joint_index;
      record["sign"] = trial.sign;
      record["coupled_direction_index"] = trial.direction_index;
      record["repeat_check"] = {{"available", repeat != 0}, {"matched", repeat_equal},
                                {"max_abs_output_q_difference_rad", repeat_delta},
                                {"compute_wall_time_compared", false}};
      output["neighborhood_trials"].push_back(std::move(record));
    }

  // 独立历史诊断：不以新的投影输出替换原始 precision FAIL、原始 q 或抓取变换。
  std::size_t historical_input_position_fail = 0, historical_input_rotation_fail = 0;
  double original_max_position = 0., original_max_rotation = 0.;
  int original_worst_position_state = -1, original_worst_rotation_state = -1;
  for (std::size_t index = 0; index < rows.size(); ++index)
  {
    const p4::JointVector input = joints(rows[index]);
    const auto original_value = historical_evaluate(input);
    const double position = original_value.residual.head<3>().norm();
    const double rotation = original_value.residual.tail<3>().norm();
    historical_input_position_fail += position > TASK03_POSITION_LIMIT_M;
    historical_input_rotation_fail += rotation > TASK03_ROTATION_LIMIT_RAD;
    if (position > original_max_position)
    {
      original_max_position = position;
      original_worst_position_state = static_cast<int>(index);
    }
    if (rotation > original_max_rotation)
    {
      original_max_rotation = rotation;
      original_worst_rotation_state = static_cast<int>(index);
    }
    const auto value = p4::project(input, historical_evaluate, margin, options);
    ++projection_calls;
    historical_converged += converged(value, options);
    ++historical_statuses[p4::statusName(value.status)];
    auditResult(value, input, model, options, "original state=" + std::to_string(index), failures);
    Json record = projectionJson(value, model, options);
    record["source_state_index"] = index;
    record["qualification"] = "OFFLINE_ORIGINAL_GRASP_DIAGNOSTIC_NOT_REPLACEMENT_HISTORICAL_DATA";
    record["unprojected_original_residual"] = residualJson(original_value.residual);
    record["original_TASK03_position_precision_pass"] = position <= TASK03_POSITION_LIMIT_M;
    record["original_TASK03_rotation_precision_pass"] = rotation <= TASK03_ROTATION_LIMIT_RAD;
    output["historical_diagnostic_trials"].push_back(std::move(record));
  }
  requireCheck(projection_calls == 487, "Exact finite experiment budget 194+293 projection calls", failures);
  const bool required_passed = failures.empty() && neighborhood_converged == 194;
  output["required_neighborhood_summary"] = {
      {"cases", trials.size()}, {"repeats", 2}, {"projection_calls", 194},
      {"converged", neighborhood_converged}, {"status_counts", neighborhood_statuses},
      {"passed", required_passed}, {"maximum_final_position_residual_m", max_final_position},
      {"maximum_final_rotation_residual_rad", max_final_rotation},
      {"minimum_final_native_joint_margin_rad", minimum_output_margin},
      {"maximum_accepted_updates", maximum_accepted_updates},
      {"maximum_repeat_output_q_difference_rad", maximum_repeat_q_delta},
      {"total_projection_compute_wall_time_sec", total_compute_wall},
      {"coupled_direction_formula", "normalize_L2(sin(0.7*(direction_index+1)*(joint_index+1))); indices 0..3/0..13"}};
  output["historical_original_summary"] = {
      {"records", rows.size()}, {"projection_calls", rows.size()},
      {"projection_converged", historical_converged}, {"status_counts", historical_statuses},
      {"projection_failure_is_independent_diagnostic_not_required_neighborhood_failure", true},
      {"unprojected_TASK03_acceptance", {
          {"position_limit_m_unchanged", TASK03_POSITION_LIMIT_M},
          {"rotation_limit_rad_unchanged", TASK03_ROTATION_LIMIT_RAD},
          {"maximum_original_position_residual_m", original_max_position},
          {"maximum_original_rotation_residual_rad", original_max_rotation},
          {"worst_position_state", original_worst_position_state},
          {"worst_rotation_state", original_worst_rotation_state},
          {"position_fail_records", historical_input_position_fail},
          {"rotation_fail_records", historical_input_rotation_fail},
          {"status", historical_input_position_fail == 0 && historical_input_rotation_fail == 0 ? "PASS" : "FAIL"},
          {"original_data_and_grasps_unchanged", true},
          {"new_projection_outputs_do_not_replace_original_FAIL", true}}}};
  output["pipeline_counts"] = {{"projection_calls", projection_calls},
                                {"required_neighborhood_calls", 194}, {"independent_diagnostic_calls", 293},
                                {"ik_calls", 0}, {"fcl_queries", 0}, {"execution_commands", 0},
                                {"original_grasp_refits", 0}, {"algebraic_fixture_construction_count", 1}};
  output["failures"] = failures;
  output["status"] = required_passed ? "PASS_OFFLINE_PROJECTION_ONLY" : "FAIL_OFFLINE_CHECK";
  output["task04_status"] = required_passed ? "PASS_CANDIDATE" : "PARTIAL";
}

}  // namespace

int main(int argc, char** argv)
{
  Json output = {{"schema_version", 1}, {"task", "TASK04_OFFLINE_REAL_FR3_PROJECTION"},
                 {"status", "ERROR"}, {"task04_status", "PARTIAL"},
                 {"scientific_qualification", "OFFLINE_PROJECTION_MATHEMATICS_ONLY"},
                 {"benchmark_frozen", false}, {"physics_or_collision_claim", false},
                 {"simulation_started", false}, {"simulation_time", nullptr}, {"physics_step", nullptr},
                 {"ros_context_initialized", false}, {"seed", nullptr},
                 {"seed_status", "UNSET_NO_RANDOM_SAMPLING"},
                 {"historical_data_written", false}, {"source_model_written", false},
                 {"full_P4_reproduction_claim", false}};
  std::string output_path;
  try
  {
    if (argc != 5)
      throw std::invalid_argument("Usage from repository root: --protocol PATH --output NEW_JSON_PATH");
    std::map<std::string, std::string> paths;
    for (int index = 1; index < argc; index += 2)
      if (!paths.emplace(argv[index], argv[index + 1]).second)
        throw std::invalid_argument("Duplicate option");
    if (paths.size() != 2 || !paths.count("--protocol") || !paths.count("--output"))
      throw std::invalid_argument("Only --protocol PATH and --output NEW_JSON_PATH are accepted");
    output_path = paths.at("--output");
    if (std::filesystem::exists(output_path))
      throw std::invalid_argument("Refusing to overwrite existing evidence");
    output["command_inputs"] = paths;
    run(paths, output);
  }
  catch (const std::exception& error)
  {
    output["status"] = "ERROR";
    output["task04_status"] = "PARTIAL";
    output["reason"] = error.what();
  }
  if (!output_path.empty() && !std::filesystem::exists(output_path))
  {
    const auto parent = std::filesystem::path(output_path).parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
    // exclusive create，失败运行仍保留已完成诊断，绝不覆盖旧证据。
    std::FILE* stream = std::fopen(output_path.c_str(), "wx");
    if (!stream)
    {
      std::cerr << "Cannot exclusively save new offline evidence file\n";
      return 2;
    }
    const std::string serialized = output.dump(2) + '\n';
    const bool saved = std::fwrite(serialized.data(), 1, serialized.size(), stream) == serialized.size();
    const bool closed = std::fclose(stream) == 0;
    if (!saved || !closed)
    {
      std::cerr << "Offline evidence file write failure\n";
      return 2;
    }
  }
  std::cout << output.at("status").get<std::string>() << '\n';
  if (output.contains("reason")) std::cout << output["reason"].get<std::string>() << '\n';
  if (output.contains("required_neighborhood_summary"))
    std::cout << "Required neighborhood converged=" << output["required_neighborhood_summary"]["converged"]
              << "/194, original diagnostic converged=" << output["historical_original_summary"]["projection_converged"]
              << "/293; no physics or collision claim\n";
  if (output.contains("failures"))
    for (const auto& failure : output["failures"]) std::cout << failure.get<std::string>() << '\n';
  return output.at("status") == "PASS_OFFLINE_PROJECTION_ONLY" ? 0 : 1;
}
