// [ENGINEERING] 有界离线数学验收：真实 FR3 模型与历史几何记录，不运行物理系统。
#include "model_adapter.hpp"

#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <sstream>
#include <vector>

#include <nlohmann/json.hpp>
#include <yaml-cpp/yaml.h>

namespace
{
using Json = nlohmann::json;
using Model = task03_offline::DualFr3Model;

// 预声明的离线算术精度，不是正式 Benchmark 成功/碰撞门限。
constexpr double FK_LIMIT = 1e-11;
constexpr double POSITION_CLOSURE_LIMIT = 5e-8;
constexpr double ROTATION_CLOSURE_LIMIT = 2e-5;
constexpr double JACOBIAN_LIMIT = 2e-7;
constexpr double GAUGE_LIMIT = 1e-11;
constexpr double FIVE_POINT_STEP = 3e-6;
constexpr std::array<double, 3> CENTRAL_STEPS{1e-5, 3e-6, 1e-6};
constexpr std::array<int, 4> CRITICAL_STATES{0, 135, 196, 292};

std::string readText(const std::string& path)
{
  std::ifstream stream(path);
  if (!stream)
    throw std::invalid_argument("Cannot read input: " + path);
  std::ostringstream output;
  output << stream.rdbuf();
  return output.str();
}

Eigen::Isometry3d pose(const Json& input)
{
  const auto& p = input.at("translation_m");
  const auto& q = input.at("quaternion_xyzw");
  if (p.size() != 3 || q.size() != 4)
    throw std::invalid_argument("Invalid saved pose vector size");
  return common_geometry::fromXyzw(Eigen::Vector3d(p[0], p[1], p[2]),
                                 Eigen::Vector4d(q[0], q[1], q[2], q[3]));
}

Eigen::Isometry3d yamlPose(const YAML::Node& input)
{
  const auto& p = input["translation_m"];
  const auto& q = input["quaternion_xyzw"];
  if (p.size() != 3 || q.size() != 4)
    throw std::invalid_argument("Invalid original grasp pose vector size");
  return common_geometry::fromXyzw(
      Eigen::Vector3d(p[0].as<double>(), p[1].as<double>(), p[2].as<double>()),
      Eigen::Vector4d(q[0].as<double>(), q[1].as<double>(), q[2].as<double>(), q[3].as<double>()));
}

Json poseJson(const Eigen::Isometry3d& input)
{
  const Eigen::Quaterniond q(input.linear());
  const auto& p = input.translation();
  return {{"translation_m", {p.x(), p.y(), p.z()}},
          {"quaternion_xyzw", {q.x(), q.y(), q.z(), q.w()}},
          {"direction", "TCP_to_Object; maps Object coordinates into TCP"}};
}

template<class Derived>
Json matrixJson(const Eigen::MatrixBase<Derived>& input)
{
  Json rows=Json::array();
  for (Eigen::Index row=0; row<input.rows(); ++row)
  {
    Json values=Json::array();
    for (Eigen::Index column=0; column<input.cols(); ++column)
      values.push_back(input(row,column));
    rows.push_back(values);
  }
  return rows;
}

p4::JointVector joints(const Json& row)
{
  p4::JointVector output;
  const auto& left = row.at("left_q_rad");
  const auto& right = row.at("right_q_rad");
  if (left.size() != 7 || right.size() != 7)
    throw std::invalid_argument("Invalid saved 14q");
  for (int joint = 0; joint < 7; ++joint)
  {
    output[joint] = left[joint];
    output[joint + 7] = right[joint];
  }
  if (!output.allFinite())
    throw std::invalid_argument("Non-finite saved 14q");
  return output;
}

double angularError(const Eigen::Isometry3d& first, const Eigen::Isometry3d& second)
{
  return common_geometry::so3Log(first.linear().transpose() * second.linear()).norm();
}

p4::ClosureSample evaluate(Model& model, const p4::JointVector& q,
                           const Eigen::Isometry3d& gl, const Eigen::Isometry3d& gr)
{
  const auto arms = model.sample(q);
  return p4::evaluate(arms.first, arms.second, gl, gr);
}

p4::Residual residual(Model& model, const p4::JointVector& q,
                      const Eigen::Isometry3d& gl, const Eigen::Isometry3d& gr)
{
  const auto arms = model.sample(q);
  return p4::residual(arms.first.world_tcp, arms.second.world_tcp, gl, gr);
}

// 与生产 centralDifference 独立实现的五点导数，只读取 FK，不访问解析 J。
p4::ConstraintJacobian fivePoint(Model& model, const p4::JointVector& q,
                                const Eigen::Isometry3d& gl, const Eigen::Isometry3d& gr)
{
  p4::ConstraintJacobian output;
  for (int joint = 0; joint < 14; ++joint)
  {
    auto qm2 = q, qm1 = q, qp1 = q, qp2 = q;
    qm2[joint] -= 2 * FIVE_POINT_STEP;
    qm1[joint] -= FIVE_POINT_STEP;
    qp1[joint] += FIVE_POINT_STEP;
    qp2[joint] += 2 * FIVE_POINT_STEP;
    output.col(joint) =
        (residual(model, qm2, gl, gr) - 8 * residual(model, qm1, gl, gr) +
         8 * residual(model, qp1, gl, gr) - residual(model, qp2, gl, gr)) /
        (12 * FIVE_POINT_STEP);
  }
  return output;
}

struct DerivativeChecks
{
  std::array<double, 3> central_max{};
  double five_point_max{0.0};
  std::size_t configurations{0};

  Json check(Model& model, const p4::JointVector& q,
             const Eigen::Isometry3d& gl, const Eigen::Isometry3d& gr)
  {
    const auto analytic = evaluate(model, q, gl, gr).jacobian;
    const auto function = [&](const p4::JointVector& value) {
      return residual(model, value, gl, gr);
    };
    Json errors = Json::array();
    for (std::size_t index = 0; index < CENTRAL_STEPS.size(); ++index)
    {
      const auto numerical = p4::centralDifference(q, function, CENTRAL_STEPS[index]);
      const double error = (analytic - numerical).cwiseAbs().maxCoeff();
      central_max[index] = std::max(central_max[index], error);
      errors.push_back({{"step_rad", CENTRAL_STEPS[index]}, {"max_abs_entry_error", error}});
    }
    const double five_error = (analytic - fivePoint(model, q, gl, gr)).cwiseAbs().maxCoeff();
    five_point_max = std::max(five_point_max, five_error);
    ++configurations;
    return {{"central", errors}, {"five_point_step_rad", FIVE_POINT_STEP},
            {"five_point_max_abs_entry_error", five_error}};
  }

  Json summary() const
  {
    Json central = Json::array();
    for (std::size_t index = 0; index < CENTRAL_STEPS.size(); ++index)
      central.push_back({{"step_rad", CENTRAL_STEPS[index]}, {"max_abs_entry_error", central_max[index]}});
    return {{"configurations", configurations}, {"central", central},
            {"five_point_step_rad", FIVE_POINT_STEP}, {"five_point_max_abs_entry_error", five_point_max},
            {"limit", JACOBIAN_LIMIT}, {"passed", passed()}};
  }

  bool passed() const
  {
    return five_point_max <= JACOBIAN_LIMIT &&
           std::all_of(central_max.begin(), central_max.end(), [](double value) { return value <= JACOBIAN_LIMIT; });
  }
};

void check(bool condition, const std::string& label, std::vector<std::string>& failures)
{
  if (!condition)
    failures.push_back(label);
}

Json run(const std::map<std::string, std::string>& paths)
{
  const std::string urdf_xml = readText(paths.at("--urdf"));
  const std::string srdf_xml = readText(paths.at("--srdf"));
  Model model(urdf_xml, srdf_xml);
  const Json rows = Json::parse(readText(paths.at("--fixture")));
  const YAML::Node original = YAML::Load(readText(paths.at("--config")));
  // 输入是归档时的配置，不读取、更改或冻结当前 Benchmark。
  const Eigen::Isometry3d original_gl =
      yamlPose(original["shared_grasp"]["object_to_left_tcp_candidate"]).inverse();
  const Eigen::Isometry3d original_gr =
      yamlPose(original["shared_grasp"]["object_to_right_tcp_candidate"]).inverse();
  if (!rows.is_array() || rows.size() != 293)
    throw std::invalid_argument("Expected unchanged historical 293-record dense fixture");

  std::vector<std::string> failures;
  DerivativeChecks historical_derivatives;
  double max_fk_position = 0, max_fk_rotation = 0, max_position_closure = 0, max_rotation_closure = 0;
  double min_margin = std::numeric_limits<double>::infinity();
  int position_worst_state = -1, rotation_worst_state = -1;
  std::size_t above_position = 0, above_rotation = 0;
  std::set<std::vector<double>> unique_q;
  Json historical_results = Json::array();
  for (std::size_t index = 0; index < rows.size(); ++index)
  {
    const auto& row = rows[index];
    const auto q = joints(row);
    check(row.at("state_index").get<std::size_t>() == index, "historical state index order", failures);
    unique_q.insert(std::vector<double>(q.data(), q.data() + q.size()));
    const auto arms = model.sample(q);
    for (const auto& item : {
             std::make_pair(arms.first.world_tcp, std::string("left_fr3_side_suction_tcp")),
             std::make_pair(arms.second.world_tcp, std::string("right_fr3_side_suction_tcp"))})
    {
      const auto saved = pose(row.at("link_world_poses").at(item.second));
      max_fk_position = std::max(max_fk_position, (item.first.translation() - saved.translation()).norm());
      max_fk_rotation = std::max(max_fk_rotation, angularError(item.first, saved));
    }
    const auto value = p4::evaluate(arms.first, arms.second, original_gl, original_gr);
    const double position = value.residual.head<3>().norm();
    const double rotation = value.residual.tail<3>().norm();
    if (position > max_position_closure)
    {
      max_position_closure = position;
      position_worst_state = static_cast<int>(index);
    }
    if (rotation > max_rotation_closure)
    {
      max_rotation_closure = rotation;
      rotation_worst_state = static_cast<int>(index);
    }
    above_position += position > POSITION_CLOSURE_LIMIT;
    above_rotation += rotation > ROTATION_CLOSURE_LIMIT;
    min_margin = std::min(min_margin, model.minimumJointMargin(q));
    historical_results.push_back({{"state_index", index}, {"position_closure_m", position},
                                 {"rotation_closure_rad", rotation},
                                 {"jacobian_validation", historical_derivatives.check(model, q, original_gl, original_gr)}});
  }
  check(max_fk_position <= FK_LIMIT && max_fk_rotation <= FK_LIMIT, "historical TCP FK oracle equality", failures);
  check(min_margin >= 0, "historical actual URDF joint bounds", failures);
  check(historical_derivatives.passed(), "historical actual-model Jacobian finite differences", failures);

  // 明确独立的真实模型代数抓取样例：q0来自原START，无IK/投影；O固定为归档START。
  // 仅在这里各构造一次 G=FK(q0)^-1 O，此后对所有扰动固定G，不能伪称物理校准。
  const auto q0 = joints(rows[0]);
  const auto start_arms = model.sample(q0);
  const auto original_start = p4::evaluate(start_arms.first, start_arms.second, original_gl, original_gr);
  const auto& center = rows[0].at("cube_center_world_m");
  const auto& orientation = rows[0].at("cube_orientation_xyzw");
  const auto object = common_geometry::fromXyzw(Eigen::Vector3d(center[0], center[1], center[2]),
      Eigen::Vector4d(orientation[0], orientation[1], orientation[2], orientation[3]));
  const Eigen::Isometry3d algebraic_gl = start_arms.first.world_tcp.inverse() * object;
  const Eigen::Isometry3d algebraic_gr = start_arms.second.world_tcp.inverse() * object;
  const auto exact = p4::evaluate(start_arms.first, start_arms.second, algebraic_gl, algebraic_gr);
  check(exact.residual.head<3>().norm() <= POSITION_CLOSURE_LIMIT &&
        exact.residual.tail<3>().norm() <= ROTATION_CLOSURE_LIMIT,
        "real FR3 algebraic fixed-grasp fixture closure", failures);
  check(model.minimumJointMargin(q0) >= 0, "algebraic q0 actual joint bounds", failures);
  DerivativeChecks algebraic_derivatives;
  Json perturbations = Json::array();
  algebraic_derivatives.check(model, q0, algebraic_gl, algebraic_gr);
  double minimum_perturbed_position = std::numeric_limits<double>::infinity();
  double minimum_perturbed_rotation = std::numeric_limits<double>::infinity();
  for (int joint = 0; joint < 14; ++joint)
    for (double sign : {-1., 1.})
    {
      auto altered = q0;
      altered[joint] += sign * 0.01;
      const auto value = evaluate(model, altered, algebraic_gl, algebraic_gr);
      const double position = value.residual.head<3>().norm(), rotation = value.residual.tail<3>().norm();
      minimum_perturbed_position = std::min(minimum_perturbed_position, position);
      minimum_perturbed_rotation = std::min(minimum_perturbed_rotation, rotation);
      check(position > 1e-6 || rotation > 1e-6, "fixed algebraic grasp single-joint disturbance detection", failures);
      check(model.minimumJointMargin(altered) >= 0, "perturbed q0 actual joint bounds", failures);
      perturbations.push_back({{"joint_index", joint}, {"delta_rad", sign * 0.01},
                             {"position_closure_m", position}, {"rotation_closure_rad", rotation},
                             {"jacobian_validation", algebraic_derivatives.check(model, altered, algebraic_gl, algebraic_gr)}});
    }
  // 原固定历史抓取也在规定关键 q 上逐关节验证离流形导数，不重新生成抓取。
  for (int state : CRITICAL_STATES)
    for (int joint = 0; joint < 14; ++joint)
      for (double sign : {-1., 1.})
      {
        auto altered = joints(rows[state]);
        altered[joint] += sign * 0.01;
        check(model.minimumJointMargin(altered) >= 0, "historical critical perturbed actual joint bounds", failures);
        historical_derivatives.check(model, altered, original_gl, original_gr);
      }
  check(algebraic_derivatives.passed(), "real FR3 algebraic fixed-grasp Jacobian finite differences", failures);
  check(historical_derivatives.passed(), "off-manifold historical Jacobian finite differences", failures);

  // O(delta^2) 检验：固定G；分别记录位置和旋转余项，不合成物理成功评分。
  p4::JointVector direction;
  for (int joint = 0; joint < 14; ++joint)
    direction[joint] = std::sin(0.7 * static_cast<double>(joint + 1));
  direction.normalize();
  Json linearization = Json::array();
  std::array<Eigen::Vector2d, 3> remainders;
  const std::array<double, 3> deltas{1e-3, 5e-4, 2.5e-4};
  for (std::size_t index = 0; index < deltas.size(); ++index)
  {
    const p4::JointVector dq = deltas[index] * direction;
    const p4::Residual remainder = residual(model, q0 + dq, algebraic_gl, algebraic_gr) -
                                  exact.residual - exact.jacobian * dq;
    remainders[index] = {remainder.head<3>().norm(), remainder.tail<3>().norm()};
    linearization.push_back({{"delta_norm_rad", deltas[index]},
                             {"position_remainder_m", remainders[index][0]},
                             {"rotation_remainder_rad", remainders[index][1]}});
  }
  Json ratios = Json::array();
  for (std::size_t index = 1; index < remainders.size(); ++index)
  {
    const Eigen::Vector2d ratio = remainders[index - 1].cwiseQuotient(remainders[index]);
    check(ratio.allFinite() && (ratio.array() >= 3.8).all() && (ratio.array() <= 4.2).all(),
          "actual-model linearization quadratic remainder scaling", failures);
    ratios.push_back({{"position_ratio", ratio[0]}, {"rotation_ratio", ratio[1]}});
  }

  // 在内存中施加同一旋转/平移坐标规范，确保非恒等 base 的Jacobian参考系处理正确。
  Eigen::Isometry3d gauge = Eigen::Isometry3d::Identity();
  gauge.linear() = (Eigen::AngleAxisd(0.47, Eigen::Vector3d::UnitZ()) *
                    Eigen::AngleAxisd(-0.31, Eigen::Vector3d::UnitY()) *
                    Eigen::AngleAxisd(0.22, Eigen::Vector3d::UnitX())).toRotationMatrix();
  gauge.translation() = Eigen::Vector3d(0.21, -0.17, 0.08);
  Model gauged(urdf_xml, srdf_xml, gauge);
  auto gauge_q = q0;
  gauge_q[3] += .03;
  gauge_q[8] -= .02;
  const auto regular = evaluate(model, gauge_q, algebraic_gl, algebraic_gr);
  const auto transformed = evaluate(gauged, gauge_q, algebraic_gl, algebraic_gr);
  Eigen::Matrix<double, 6, 6> change = Eigen::Matrix<double, 6, 6>::Identity();
  change.topLeftCorner<3, 3>() = gauge.linear();
  const double gauge_residual_error = (transformed.residual - change * regular.residual).norm();
  const double gauge_jacobian_error = (transformed.jacobian - change * regular.jacobian).cwiseAbs().maxCoeff();
  const double gauge_object_position_error =
      (transformed.left_object.translation() - (gauge * regular.left_object).translation()).norm();
  check(gauge_residual_error <= GAUGE_LIMIT && gauge_jacobian_error <= GAUGE_LIMIT &&
        gauge_object_position_error <= GAUGE_LIMIT, "synthetic frame gauge of real FR3 model", failures);
  DerivativeChecks gauge_derivatives;
  gauge_derivatives.check(gauged, gauge_q, algebraic_gl, algebraic_gr);
  check(gauge_derivatives.passed(), "rotated-base actual-model Jacobian finite differences", failures);

  const auto graspDifference = [](const Eigen::Isometry3d& first, const Eigen::Isometry3d& second) -> Json {
    return {{"translation_delta_m", (first.translation() - second.translation()).norm()},
            {"rotation_delta_rad", angularError(first, second)}};
  };
  return {{"schema_version", 1}, {"task", "TASK03_OFFLINE_REAL_FR3_CLOSURE"},
          {"status", failures.empty() ? "PASS_OFFLINE_MATH_ONLY" : "FAIL_OFFLINE_CHECK"},
          {"task03_status", failures.empty() && above_position==0 && above_rotation==0 ?
            "PASS_CANDIDATE" : "PARTIAL"},
          {"original_fixed_grasp_acceptance", {
            {"position_limit_m", POSITION_CLOSURE_LIMIT},
            {"rotation_limit_rad", ROTATION_CLOSURE_LIMIT},
            {"passed", above_position==0 && above_rotation==0},
            {"algebraic_fixture_is_not_a_substitute", true}}},
          {"scientific_qualification", "OFFLINE_MATH_NOT_PHYSICAL_SHARED_GRASP_PROOF"},
          {"benchmark_frozen", false}, {"simulation_started", false},
          {"ros_context_initialized", false}, {"command_publishers", 0},
          {"ik_calls", 0}, {"projection_calls", 0}, {"fcl_queries", 0},
          {"input_paths", paths}, {"joint_names", model.jointNames()},
          {"example_original_START", {
             {"qualification", "HISTORICAL_FK_MATH_ONLY_NOT_MEASURED_PHYSICS"},
             {"q_rad", matrixJson(q0.transpose())},
             {"C_position_m_rotation_rad", matrixJson(original_start.residual.transpose())},
             {"Jc_6_by_14", matrixJson(original_start.jacobian)}}},
          {"declared_engineering_precision", {{"fk_oracle_m_and_rad", FK_LIMIT},
             {"position_closure_m", POSITION_CLOSURE_LIMIT}, {"rotation_closure_rad", ROTATION_CLOSURE_LIMIT},
             {"jacobian_max_abs_entry", JACOBIAN_LIMIT}, {"frame_gauge", GAUGE_LIMIT},
             {"linearization_halving_ratio_interval", {3.8, 4.2}}}},
          {"historical_fixed_grasp", {{"classification", "APPROXIMATE_HISTORICAL_IK_DIAGNOSTIC"},
             {"records", rows.size()}, {"unique_joint_configurations", unique_q.size()},
             {"exact_closure_claim", false}, {"max_position_closure_m", max_position_closure},
             {"max_position_state", position_worst_state}, {"max_rotation_closure_rad", max_rotation_closure},
             {"max_rotation_state", rotation_worst_state}, {"position_over_declared_limit_records", above_position},
             {"rotation_over_declared_limit_records", above_rotation},
             {"left_tcp_to_object", poseJson(original_gl)}, {"right_tcp_to_object", poseJson(original_gr)},
             {"minimum_joint_margin_rad", min_margin}, {"max_fk_oracle_translation_m", max_fk_position},
             {"max_fk_oracle_rotation_rad", max_fk_rotation}, {"jacobian_validation", historical_derivatives.summary()},
             {"per_state", historical_results}}},
          {"algebraic_fixed_grasp", {{"classification", "REAL_FR3_MODEL_ALGEBRAIC_GRASP_FIXTURE"},
             {"origin", "ONE_TIME_G=FK(q0)^-1*ARCHIVED_START_OBJECT; q0 from archived START; no IK"},
             {"benchmark_or_suction_calibration", false}, {"grasp_recomputed_after_q0", false},
             {"left_tcp_to_object", poseJson(algebraic_gl)}, {"right_tcp_to_object", poseJson(algebraic_gr)},
             {"left_difference_from_archived_fixed_grasp", graspDifference(algebraic_gl, original_gl)},
             {"right_difference_from_archived_fixed_grasp", graspDifference(algebraic_gr, original_gr)},
             {"q0_position_closure_m", exact.residual.head<3>().norm()},
             {"q0_rotation_closure_rad", exact.residual.tail<3>().norm()},
             {"joint_perturbations", perturbations}, {"minimum_perturbed_position_closure_m", minimum_perturbed_position},
             {"minimum_perturbed_rotation_closure_rad", minimum_perturbed_rotation},
             {"jacobian_validation", algebraic_derivatives.summary()},
             {"linearization", linearization}, {"halving_ratios", ratios}}},
          {"synthetic_rotated_frame_gauge", {{"classification", "SYNTHETIC_COORDINATE_CHANGE_ON_REAL_FR3_MODEL"},
             {"source_assets_written", false}, {"residual_error", gauge_residual_error},
             {"jacobian_max_abs_entry_error", gauge_jacobian_error},
             {"left_object_position_error_m", gauge_object_position_error},
             {"jacobian_validation", gauge_derivatives.summary()}}},
          {"failures", failures}};
}

}  // namespace

int main(int argc, char** argv)
{
  Json output;
  std::string output_path;
  try
  {
    if (argc != 11)
      throw std::invalid_argument("Usage: --urdf PATH --srdf PATH --fixture PATH --config PATH --output NEW_JSON_PATH");
    std::map<std::string, std::string> paths;
    for (int index = 1; index < argc; index += 2)
      if (!paths.emplace(argv[index], argv[index + 1]).second)
        throw std::invalid_argument("Duplicate option");
    for (const auto& key : {"--urdf", "--srdf", "--fixture", "--config", "--output"})
      if (!paths.count(key))
        throw std::invalid_argument("Missing required option " + std::string(key));
    output_path = paths.at("--output");
    if (std::filesystem::exists(output_path))
      throw std::invalid_argument("Refusing to overwrite existing evidence file");
    output = run(paths);
  }
  catch (const std::exception& error)
  {
    output = {{"task", "TASK03_OFFLINE_REAL_FR3_CLOSURE"}, {"status", "ERROR"},
              {"reason", error.what()}, {"simulation_started", false}, {"benchmark_frozen", false}};
  }
  if (!output_path.empty() && !std::filesystem::exists(output_path))
  {
    const auto parent = std::filesystem::path(output_path).parent_path();
    if (!parent.empty())
      std::filesystem::create_directories(parent);
    std::ofstream stream(output_path);
    if (!stream)
    {
      std::cerr << "Cannot save new offline result file\n";
      return 2;
    }
    stream << output.dump(2) << '\n';
  }
  std::cout << output.at("status").get<std::string>() << '\n';
  if (output.contains("reason"))
    std::cout << output["reason"].get<std::string>() << '\n';
  if (output.contains("failures"))
    for (const auto& failure : output["failures"])
      std::cout << failure.get<std::string>() << '\n';
  return output.at("status") == "PASS_OFFLINE_MATH_ONLY" ? 0 : 1;
}
