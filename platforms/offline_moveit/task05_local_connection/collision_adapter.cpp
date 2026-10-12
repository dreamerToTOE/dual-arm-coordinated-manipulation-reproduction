#include "collision_adapter.hpp"

#include <array>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <set>
#include <sstream>
#include <stdexcept>

#include <geometric_shapes/shapes.h>
#include <moveit/collision_detection_fcl/collision_detector_allocator_fcl.h>
#include <moveit/planning_scene/planning_scene.h>
#include <moveit/robot_state/robot_state.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <srdfdom/model.h>
#include <urdf_parser/urdf_parser.h>
#include <yaml-cpp/yaml.h>

namespace task05_offline
{
namespace
{
using Json = nlohmann::json;
using State = moveit::core::RobotState;
constexpr const char* LEFT_TCP = "left_fr3_side_suction_tcp";
constexpr const char* CUBE = "task05_shared_cube";
constexpr const char* NEGATIVE_BOX = "task05_negative_tcp_box";
constexpr const char* BACKEND = "EXISTING_MOVEIT_PLANNING_SCENE_FCL";
constexpr const char* ACM_IDENTITY = "ORIGINAL_SRDF_UNCHANGED_NO_ADDED_ENTRIES";
constexpr std::size_t CONTACT_CAP = 10000;
constexpr std::size_t PAIR_CONTACT_CAP = 1000;

Json xyz(const Eigen::Vector3d& value)
{
  return Json::array({value.x(), value.y(), value.z()});
}

Json rigidJson(const Eigen::Isometry3d& value)
{
  const Eigen::Quaterniond q(value.linear());
  return {{"translation_m", xyz(value.translation())},
          {"quaternion_xyzw", Json::array({q.x(), q.y(), q.z(), q.w()})}};
}

Eigen::Vector3d vector3(const YAML::Node& input)
{
  if (!input.IsSequence() || input.size() != 3)
    throw std::invalid_argument("Expected archived XYZ vector");
  Eigen::Vector3d value(input[0].as<double>(), input[1].as<double>(), input[2].as<double>());
  if (!value.allFinite()) throw std::invalid_argument("Nonfinite archived XYZ vector");
  return value;
}

Eigen::Isometry3d urdfPose(const urdf::Pose& input)
{
  return common_geometry::fromXyzw(
      Eigen::Vector3d(input.position.x, input.position.y, input.position.z),
      Eigen::Vector4d(input.rotation.x, input.rotation.y, input.rotation.z, input.rotation.w));
}

// 使用原 package:// URI 和标准 ament prefix；缺失资源直接失败，不创建替代几何。
std::filesystem::path resourcePath(const std::string& uri)
{
  std::filesystem::path path;
  const std::string prefix = "package://";
  if (uri.rfind(prefix, 0) == 0)
  {
    const auto slash = uri.find('/', prefix.size());
    if (slash == std::string::npos) throw std::invalid_argument("Invalid original mesh URI: " + uri);
    const auto package = uri.substr(prefix.size(), slash - prefix.size());
    const auto relative = uri.substr(slash + 1);
    const char* environment = std::getenv("AMENT_PREFIX_PATH");
    std::istringstream prefixes(environment ? environment : "");
    std::string candidate;
    while (std::getline(prefixes, candidate, ':'))
    {
      if (candidate.empty()) continue;
      const std::filesystem::path root(candidate);
      if (std::filesystem::is_regular_file(root / "share/ament_index/resource_index/packages" / package))
      {
        path = root / "share" / package / relative;
        break;
      }
    }
    if (path.empty()) throw std::runtime_error("Original mesh package unavailable: " + uri);
  }
  else if (uri.rfind("file://", 0) == 0) path = uri.substr(7);
  else if (std::filesystem::path(uri).is_absolute()) path = uri;
  else throw std::invalid_argument("Unsupported original mesh resource: " + uri);
  if (!std::filesystem::is_regular_file(path) || std::filesystem::file_size(path) == 0)
    throw std::runtime_error("Original mesh resource missing or empty: " + uri);
  return std::filesystem::canonical(path);
}

Json acmJson(const moveit_msgs::msg::AllowedCollisionMatrix& input)
{
  Json values = Json::array();
  for (const auto& row : input.entry_values) values.push_back(row.enabled);
  return {{"entry_names", input.entry_names}, {"entry_values", values},
          {"default_entry_names", input.default_entry_names},
          {"default_entry_values", input.default_entry_values}};
}

void verifyShape(const urdf::Geometry& original, const shapes::Shape& loaded, Json& evidence)
{
  switch (original.type)
  {
    case urdf::Geometry::MESH:
    {
      if (loaded.type != shapes::MESH) throw std::runtime_error("Original mesh replaced by another shape");
      const auto& mesh = static_cast<const urdf::Mesh&>(original);
      const auto& shape = static_cast<const shapes::Mesh&>(loaded);
      const Eigen::Vector3d scale(mesh.scale.x, mesh.scale.y, mesh.scale.z);
      if (!scale.allFinite() || (scale.array() <= 0.).any() || !shape.vertices || !shape.triangles ||
          shape.vertex_count == 0 || shape.triangle_count == 0)
        throw std::runtime_error("Invalid or unloaded original mesh");
      for (std::size_t i = 0; i < 3ULL * shape.vertex_count; ++i)
        if (!std::isfinite(shape.vertices[i])) throw std::runtime_error("Nonfinite original mesh vertex");
      for (std::size_t i = 0; i < 3ULL * shape.triangle_count; ++i)
        if (shape.triangles[i] >= shape.vertex_count) throw std::runtime_error("Invalid original mesh triangle");
      evidence = {{"type", "MESH"}, {"original_uri", mesh.filename},
                  {"resolved_resource", resourcePath(mesh.filename).string()},
                  {"urdf_scale", xyz(scale)}, {"vertices", shape.vertex_count},
                  {"triangles", shape.triangle_count}};
      break;
    }
    case urdf::Geometry::BOX:
    {
      if (loaded.type != shapes::BOX) throw std::runtime_error("Original box shape type mismatch");
      const auto& box = static_cast<const urdf::Box&>(original);
      const auto& shape = static_cast<const shapes::Box&>(loaded);
      const Eigen::Vector3d expected(box.dim.x, box.dim.y, box.dim.z);
      if (!expected.allFinite() || (expected.array() <= 0.).any() ||
          shape.size[0] != expected.x() || shape.size[1] != expected.y() || shape.size[2] != expected.z())
        throw std::runtime_error("Original box dimensions changed");
      evidence = {{"type", "BOX"}, {"size_m", xyz(expected)}};
      break;
    }
    case urdf::Geometry::CYLINDER:
    {
      if (loaded.type != shapes::CYLINDER) throw std::runtime_error("Original cylinder type mismatch");
      const auto& cylinder = static_cast<const urdf::Cylinder&>(original);
      const auto& shape = static_cast<const shapes::Cylinder&>(loaded);
      if (!std::isfinite(cylinder.radius) || !std::isfinite(cylinder.length) || cylinder.radius <= 0. ||
          cylinder.length <= 0. || shape.radius != cylinder.radius || shape.length != cylinder.length)
        throw std::runtime_error("Original cylinder dimensions changed");
      evidence = {{"type", "CYLINDER"}, {"radius_m", cylinder.radius}, {"length_m", cylinder.length}};
      break;
    }
    case urdf::Geometry::SPHERE:
    {
      if (loaded.type != shapes::SPHERE) throw std::runtime_error("Original sphere type mismatch");
      const auto& sphere = static_cast<const urdf::Sphere&>(original);
      if (!std::isfinite(sphere.radius) || sphere.radius <= 0. ||
          static_cast<const shapes::Sphere&>(loaded).radius != sphere.radius)
        throw std::runtime_error("Original sphere radius changed");
      evidence = {{"type", "SPHERE"}, {"radius_m", sphere.radius}};
      break;
    }
    default: throw std::runtime_error("Unsupported original URDF collision geometry");
  }
}
}  // namespace

struct CollisionAdapter::Impl
{
  moveit::core::RobotModelPtr model;
  planning_scene::PlanningScenePtr scene;
  std::array<const moveit::core::JointModelGroup*, 2> groups{};
  Eigen::Isometry3d left_tcp_to_object;
  Eigen::Vector3d cube_size;
  moveit_msgs::msg::AllowedCollisionMatrix original_acm;
  Json evidence;

  State state(const p4::JointVector& q, bool attach) const
  {
    if (!q.allFinite()) throw std::invalid_argument("Nonfinite collision-query joint configuration");
    State result(model);
    result.setToDefaultValues();
    result.setJointGroupPositions(groups[0], q.head<7>());
    result.setJointGroupPositions(groups[1], q.tail<7>());
    if (attach)
    {
      const std::vector<shapes::ShapeConstPtr> shapes{
          std::make_shared<shapes::Box>(cube_size.x(), cube_size.y(), cube_size.z())};
      const EigenSTL::vector_Isometry3d poses{Eigen::Isometry3d::Identity()};
      result.attachBody(CUBE, left_tcp_to_object, shapes, poses, std::set<std::string>{}, LEFT_TCP);
      const auto* body = result.getAttachedBody(CUBE);
      if (!body || !body->getTouchLinks().empty() || body->getAttachedLinkName() != LEFT_TCP)
        throw std::runtime_error("Native attachment differs from empty-touch-links contract");
    }
    result.update();
    return result;
  }

  void integrity() const
  {
    moveit_msgs::msg::AllowedCollisionMatrix current;
    scene->getAllowedCollisionMatrix().getMessage(current);
    if (current != original_acm) throw std::runtime_error("Original SRDF ACM changed");
    if (scene->getCollisionDetectorName() != collision_detection::CollisionDetectorAllocatorFCL::NAME ||
        !dynamic_cast<const collision_detection::CollisionEnvFCL*>(scene->getCollisionEnv().get()))
      throw std::runtime_error("Original native FCL backend unavailable");
    for (const auto* link : model->getLinkModelsWithCollisionGeometry())
    {
      if (scene->getCollisionEnv()->getLinkPadding(link->getName()) != 0. ||
          scene->getCollisionEnv()->getLinkScale(link->getName()) != 1. ||
          scene->getCollisionEnvUnpadded()->getLinkPadding(link->getName()) != 0. ||
          scene->getCollisionEnvUnpadded()->getLinkScale(link->getName()) != 1.)
        throw std::runtime_error("Original native collision padding or scale changed");
    }
  }

  void box(const std::string& id, const Eigen::Isometry3d& pose, const Eigen::Vector3d& size,
           bool negative = false)
  {
    common_geometry::requireRigid(pose);
    if (!size.allFinite() || (size.array() <= 0.).any()) throw std::invalid_argument("Invalid archived box size");
    moveit_msgs::msg::CollisionObject object;
    object.id = id; object.header.frame_id = "world"; object.operation = object.ADD;
    shape_msgs::msg::SolidPrimitive shape;
    shape.type = shape.BOX; shape.dimensions = {size.x(), size.y(), size.z()};
    geometry_msgs::msg::Pose p;
    const Eigen::Quaterniond q(pose.linear());
    p.position.x = pose.translation().x(); p.position.y = pose.translation().y(); p.position.z = pose.translation().z();
    p.orientation.x = q.x(); p.orientation.y = q.y(); p.orientation.z = q.z(); p.orientation.w = q.w();
    object.primitives.push_back(shape); object.primitive_poses.push_back(p);
    if (!scene->processCollisionObjectMsg(object)) throw std::runtime_error("Cannot load original private-world box: " + id);
    evidence["world_objects"].push_back({{"id", id}, {"pose_world", rigidJson(pose)},
                                        {"size_m", xyz(size)}, {"negative_test_only", negative}});
  }

  std::string category(const collision_detection::Contact& contact) const
  {
    const auto& a = contact.body_name_1;
    const auto& b = contact.body_name_2;
    const auto native_type = [&](const std::string& name) {
      if (name == CUBE) return collision_detection::BodyTypes::ROBOT_ATTACHED;
      if (model->hasLinkModel(name)) return collision_detection::BodyTypes::ROBOT_LINK;
      return collision_detection::BodyTypes::WORLD_OBJECT;
    };
    if (contact.body_type_1 != native_type(a) || contact.body_type_2 != native_type(b)) return "UNKNOWN";
    if (a == CUBE || b == CUBE)
    {
      const auto& other = a == CUBE ? b : a;
      if (other == "left_fr3_side_suction" || other == "right_fr3_side_suction") return "TOOL_CUBE";
      if (model->hasLinkModel(other)) return "ROBOT_CUBE";
      return scene->getWorld()->hasObject(other) ? "CUBE_ENV" : "UNKNOWN";
    }
    if (model->hasLinkModel(a) && model->hasLinkModel(b))
    {
      const bool opposite = (a.rfind("left_", 0) == 0 && b.rfind("right_", 0) == 0) ||
                            (a.rfind("right_", 0) == 0 && b.rfind("left_", 0) == 0);
      return opposite ? "INTER_ARM" : "SELF";
    }
    if ((model->hasLinkModel(a) && scene->getWorld()->hasObject(b)) ||
        (model->hasLinkModel(b) && scene->getWorld()->hasObject(a))) return "ROBOT_ENV";
    return "UNKNOWN";
  }
};

CollisionAdapter::CollisionAdapter(const std::string& urdf_xml, const std::string& srdf_xml,
                                   const std::string& archive_yaml_path,
                                   const Eigen::Isometry3d& left_tcp_to_object)
  : impl_(std::make_unique<Impl>())
{
  common_geometry::requireRigid(left_tcp_to_object);
  const auto urdf_model = urdf::parseURDF(urdf_xml);
  if (!urdf_model || urdf_model->getRoot()->name != "world")
    throw std::invalid_argument("Expected original world-root dual FR3 URDF");
  auto srdf_model = std::make_shared<srdf::Model>();
  if (!srdf_model->initString(*urdf_model, srdf_xml)) throw std::invalid_argument("Cannot parse original SRDF");
  // 验证 URI 在模型加载前可解；RobotModel 仍自行用原标准加载器加载未改写的 URI。
  for (const auto& entry : urdf_model->links_)
    for (const auto& collision : entry.second->collision_array)
      if (collision && collision->geometry && collision->geometry->type == urdf::Geometry::MESH)
        static_cast<void>(resourcePath(static_cast<const urdf::Mesh&>(*collision->geometry).filename));
  impl_->model = std::make_shared<moveit::core::RobotModel>(urdf_model, srdf_model);
  if (impl_->model->getModelFrame() != "world" || impl_->model->getVariableCount() != 14 ||
      impl_->model->getName() != "dual_fr3_side_suction")
    throw std::invalid_argument("Original world-frame 14-DoF dual FR3 model unavailable");
  impl_->left_tcp_to_object = left_tcp_to_object;
  for (std::size_t side = 0; side < 2; ++side)
  {
    const std::string prefix = side ? "right" : "left";
    impl_->groups[side] = impl_->model->getJointModelGroup(prefix + "_arm");
    if (!impl_->groups[side] || !impl_->groups[side]->isChain() || impl_->groups[side]->getVariableCount() != 7)
      throw std::invalid_argument("Original arm chain unavailable");
    for (std::size_t joint = 0; joint < 7; ++joint)
      if (impl_->groups[side]->getVariableNames()[joint] != prefix + "_fr3_joint" + std::to_string(joint + 1))
        throw std::invalid_argument("Original 14q ordering changed");
  }
  if (!impl_->model->getLinkModel(LEFT_TCP) || !impl_->model->getLinkModel(LEFT_TCP)->getShapes().empty())
    throw std::invalid_argument("Original attachment TCP must have no collision geometry");
  impl_->scene = std::make_shared<planning_scene::PlanningScene>(impl_->model);
  impl_->scene->allocateCollisionDetector(collision_detection::CollisionDetectorAllocatorFCL::create());
  impl_->scene->getAllowedCollisionMatrix().getMessage(impl_->original_acm);
  collision_detection::AllowedCollisionMatrix expected_acm(*srdf_model);
  moveit_msgs::msg::AllowedCollisionMatrix expected_message;
  expected_acm.getMessage(expected_message);
  if (expected_message != impl_->original_acm) throw std::runtime_error("Private scene ACM differs from original SRDF");
  impl_->integrity();
  impl_->evidence = {{"backend", BACKEND}, {"detector_name", impl_->scene->getCollisionDetectorName()},
      {"ros_context_initialized", false}, {"ros_services_used", false}, {"execution_commands", 0},
      {"archive_yaml_path", archive_yaml_path}, {"acm_identity", ACM_IDENTITY},
      {"acm", acmJson(impl_->original_acm)}, {"acm_added_entries", 0},
      {"srdf_disabled_pairs", Json::array()}, {"legal_installation_contacts", Json::array()},
      {"links", Json::array()}, {"world_objects", Json::array()},
      {"contact_cap", CONTACT_CAP}, {"contact_cap_per_pair", PAIR_CONTACT_CAP},
      {"contact_cap_policy", "AT_OR_ABOVE_CAP_IS_INCOMPLETE_AND_REJECTED"},
      {"raw_contact_policy", "NO_PAIR_FILTER_NO_DEPTH_TOLERANCE_ALL_COLLISIONS_REJECTED"},
      {"queries", Json::array({"checkSelfCollision", "checkRobotCollision"})},
      {"continuous_collision_certificate", false}};
  for (const auto& pair : srdf_model->getDisabledCollisionPairs())
  {
    const Json item{{"body_a", pair.link1_}, {"body_b", pair.link2_}, {"reason", pair.reason_}};
    impl_->evidence["srdf_disabled_pairs"].push_back(item);
    if ((pair.link1_ == "left_fr3_link8" && pair.link2_ == "left_fr3_side_suction") ||
        (pair.link1_ == "right_fr3_link8" && pair.link2_ == "right_fr3_side_suction"))
      impl_->evidence["legal_installation_contacts"].push_back(item);
  }
  std::size_t shape_count = 0, mesh_count = 0;
  for (const auto& entry : urdf_model->links_)
  {
    const auto* link = impl_->model->getLinkModel(entry.first);
    if (!link || link->getShapes().size() != entry.second->collision_array.size() ||
        link->getCollisionOriginTransforms().size() != entry.second->collision_array.size())
      throw std::runtime_error("Original URDF collision shape count mismatch: " + entry.first);
    Json record{{"name", entry.first}, {"expected_collision_shapes", entry.second->collision_array.size()},
                {"loaded_collision_shapes", link->getShapes().size()}, {"shapes", Json::array()},
                {"native_padding_m", 0.}, {"native_scale", 1.}};
    for (std::size_t i = 0; i < link->getShapes().size(); ++i)
    {
      const auto& original = entry.second->collision_array[i];
      if (!original || !original->geometry || !link->getShapes()[i]) throw std::runtime_error("Missing original collision shape");
      Json shape;
      verifyShape(*original->geometry, *link->getShapes()[i], shape);
      const auto expected = urdfPose(original->origin);
      // 固定格式/FK 数值一致性检查；不用于接触、padding 或安全门限。
      if ((expected.matrix() - link->getCollisionOriginTransforms()[i].matrix()).norm() > 1e-12)
        throw std::runtime_error("Original collision origin changed");
      shape["origin_link"] = rigidJson(link->getCollisionOriginTransforms()[i]);
      record["shapes"].push_back(shape); ++shape_count;
      if (original->geometry->type == urdf::Geometry::MESH) ++mesh_count;
    }
    impl_->evidence["links"].push_back(record);
  }
  impl_->evidence["collision_shape_count"] = shape_count;
  impl_->evidence["collision_mesh_count"] = mesh_count;
  const auto archive = YAML::LoadFile(archive_yaml_path);
  if (archive["frames"]["world"].as<std::string>() != "world" || archive["cube"]["count"].as<int>() != 1)
    throw std::invalid_argument("Expected unchanged one-Cube world-frame archive");
  const State initial = impl_->state(p4::JointVector::Zero(), false);
  for (const auto& side : {std::string("left"), std::string("right")})
    if ((initial.getGlobalLinkTransform(side + "_fr3_link0").translation() -
         vector3(archive["robots"][side]["base_at_rest_world_m"])).norm() > 1e-12)
      throw std::invalid_argument("Original URDF base differs from archive");
  impl_->cube_size = vector3(archive["cube"]["size_m"]);
  if ((impl_->cube_size.array() != .120).any()) throw std::invalid_argument("Expected original 0.120 m Cube");
  impl_->evidence["attachment"] = {{"id", CUBE}, {"parent_link", LEFT_TCP},
      {"parent_collision_shapes", 0}, {"tcp_to_object", rigidJson(left_tcp_to_object)},
      {"size_m", xyz(impl_->cube_size)}, {"touch_links", Json::array()},
      {"tool_cube_exempt", false}, {"cube_world_covered_by_native_FCL", true}};
  const auto add = [&](const std::string& id, const Eigen::Vector3d& center, const Eigen::Vector3d& size) {
    Eigen::Isometry3d pose = Eigen::Isometry3d::Identity(); pose.translation() = center;
    impl_->box(id, pose, size);
  };
  add("table", vector3(archive["table"]["center_world_m"]), vector3(archive["table"]["size_m"]));
  const auto carriage = archive["carriage"];
  const double x0 = carriage["interior_x_world_m"][0].as<double>(), x1 = carriage["interior_x_world_m"][1].as<double>();
  const double y0 = carriage["interior_y_world_m"][0].as<double>(), y1 = carriage["interior_y_world_m"][1].as<double>();
  const double t = carriage["wall_thickness_m"].as<double>(), h = carriage["wall_height_m"].as<double>();
  const double z = carriage["wall_top_world_z_m"].as<double>() - h / 2.;
  if (!std::isfinite(x0) || !std::isfinite(x1) || !std::isfinite(y0) || !std::isfinite(y1) ||
      !std::isfinite(t) || !std::isfinite(h) || !std::isfinite(z) || x1 <= x0 || y1 <= y0 || t <= 0. || h <= 0.)
    throw std::invalid_argument("Invalid original carriage dimensions");
  add("carriage_deep_wall", {x1+t/2., (y0+y1)/2., z}, {t, y1-y0+2*t, h});
  add("carriage_minus_y_wall", {(x0+x1)/2., y0-t/2., z}, {x1-x0+2*t, t, h});
  add("carriage_plus_y_wall", {(x0+x1)/2., y1+t/2., z}, {x1-x0+2*t, t, h});
  impl_->integrity();
}

CollisionAdapter::~CollisionAdapter() = default;

p4::CollisionEvidence CollisionAdapter::check(const p4::JointVector& q) const
{
  p4::CollisionEvidence output;
  output.backend = BACKEND; output.acm_identity = ACM_IDENTITY;
  try
  {
    impl_->integrity();
    const State state = impl_->state(q, true);
    if (!state.satisfiesBounds()) throw std::invalid_argument("Native joint bounds violated in collision query");
    collision_detection::CollisionRequest request;
    request.contacts = true; request.max_contacts = CONTACT_CAP; request.max_contacts_per_pair = PAIR_CONTACT_CAP;
    collision_detection::CollisionResult self, world;
    impl_->scene->getCollisionEnv()->checkSelfCollision(request, self, state, impl_->scene->getAllowedCollisionMatrix());
    impl_->scene->getCollisionEnv()->checkRobotCollision(request, world, state, impl_->scene->getAllowedCollisionMatrix());
    output.self_collision = self.collision; output.world_collision = world.collision;
    for (const auto* result : {&self, &world})
    {
      std::size_t count = 0;
      for (const auto& entry : result->contacts)
      {
        if (entry.second.empty() || entry.second.size() >= PAIR_CONTACT_CAP)
          throw std::runtime_error("Incomplete native contact pair evidence or per-pair cap reached");
        for (const auto& hit : entry.second)
        {
          ++count;
          if (hit.body_name_1.empty() || hit.body_name_2.empty() || !hit.pos.allFinite() ||
              !hit.normal.allFinite() || !std::isfinite(hit.depth) || hit.depth < 0. ||
              !((hit.body_name_1 == entry.first.first && hit.body_name_2 == entry.first.second) ||
                (hit.body_name_2 == entry.first.first && hit.body_name_1 == entry.first.second)))
            throw std::runtime_error("Invalid native FCL contact evidence");
          const auto category = impl_->category(hit);
          if (category == "UNKNOWN") throw std::runtime_error("Unclassified native FCL body pair");
          output.contacts.push_back({hit.body_name_1, hit.body_name_2, category, hit.depth, hit.pos});
        }
      }
      if (count != result->contact_count || count >= CONTACT_CAP ||
          (result->collision && count == 0) || (!result->collision && count != 0))
        throw std::runtime_error("Incomplete native FCL result or global contact cap reached");
    }
    impl_->integrity();
    output.complete = true;
    output.reason = (self.collision || world.collision) ? "NATIVE_FCL_COLLISION_REJECTED" : "NATIVE_FCL_DISCRETE_STATE_CLEAR";
  }
  catch (const std::exception& error)
  {
    output.complete = false; output.reason = error.what();
  }
  return output;
}

Json CollisionAdapter::manifest() const
{
  impl_->integrity();
  Json output = impl_->evidence;
  output["acm_unchanged_verified"] = true;
  output["original_padding_and_scales_verified"] = true;
  output["original_collision_shape_counts_verified"] = true;
  return output;
}

Eigen::Isometry3d CollisionAdapter::linkPose(const p4::JointVector& q, const std::string& name) const
{
  if (!impl_->model->getLinkModel(name)) throw std::invalid_argument("Link absent from original native model: " + name);
  const State state = impl_->state(q, false);
  const auto pose = state.getGlobalLinkTransform(name);
  common_geometry::requireRigid(pose);
  return pose;
}

void CollisionAdapter::addNegativeWorldBox(const p4::JointVector& q)
{
  impl_->integrity();
  if (impl_->scene->getWorld()->hasObject(NEGATIVE_BOX)) throw std::invalid_argument("Negative world box already exists");
  impl_->box(NEGATIVE_BOX, linkPose(q, LEFT_TCP), impl_->cube_size, true);
  impl_->integrity();
}

void CollisionAdapter::addPrivateWorldBox(const std::string& id,
                                         const Eigen::Isometry3d& pose_world,
                                         const Eigen::Vector3d& size_m)
{
  impl_->integrity();
  if (id.rfind("task06_private_", 0) != 0 || id.size() <= 15 ||
      impl_->model->hasLinkModel(id) || impl_->scene->getWorld()->hasObject(id) || id == CUBE)
    throw std::invalid_argument("Private fixture must have a new task06_private_ ID");
  impl_->box(id, pose_world, size_m);
  impl_->evidence["world_objects"].back()["classification"] = "PRIVATE_ENGINEERING_FIXTURE_ONLY";
  impl_->integrity();
}
}  // namespace task05_offline
