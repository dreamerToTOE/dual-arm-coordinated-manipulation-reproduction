// [ENGINEERING] CollisionObject消息表示校验，不改变任何碰撞/IK/基准验收门限。
// MoveIt Humble planning_scene.h: shapesAndPosesFromCollisionObjectMessage允许
// primitive pose被移入object pose；校验因此使用object * primitive的世界SE3。
#pragma once
#include <moveit_msgs/msg/collision_object.hpp>
#include <rclcpp/serialization.hpp>
#include <rclcpp/serialized_message.hpp>
#include <Eigen/Geometry>
#include <nlohmann/json.hpp>
#include <algorithm>
#include <cmath>
#include <cstring>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace task01_readback {
using Json = nlohmann::json;
using Object = moveit_msgs::msg::CollisionObject;
constexpr double kTranslationLimit = 1e-8;
constexpr double kRotationLimit = 1e-8;
constexpr double kDimensionLimit = 1e-12;
constexpr double kUnitQuaternionRoundoff = 1e-12;

inline std::string hex(const unsigned char* data, std::size_t size) {
  constexpr char digits[] = "0123456789abcdef";
  std::string result; result.reserve(size*2);
  for (std::size_t i=0; i<size; ++i) {
    result.push_back(digits[data[i]>>4]); result.push_back(digits[data[i]&15]);
  }
  return result;
}

template<class T> inline Json number(T value) {
  if (std::isfinite(value)) return static_cast<double>(value);
  // JSON本身不表示NaN/Inf；保留类型和原始位，不能让dump静默变成null。
  unsigned char bytes[sizeof(T)]; std::memcpy(bytes,&value,sizeof(T));
  return {{"nonfinite", std::isnan(value) ? "NaN" : (value>0 ? "+Infinity" : "-Infinity")},
          {"native_ieee754_bytes_hex", hex(bytes,sizeof(T))}, {"byte_count", sizeof(T)}};
}

template<class Point> inline Json pointJson(const Point& point) {
  return {{"x",number(point.x)},{"y",number(point.y)},{"z",number(point.z)}};
}

inline Json poseJson(const geometry_msgs::msg::Pose& pose) {
  const auto& q=pose.orientation;
  return {{"position",pointJson(pose.position)}, {"orientation",{
    {"x",number(q.x)},{"y",number(q.y)},{"z",number(q.z)},{"w",number(q.w)}}}};
}

inline Json posesJson(const std::vector<geometry_msgs::msg::Pose>& poses) {
  Json result=Json::array(); for (const auto& pose:poses) result.push_back(poseJson(pose));
  return result;
}

inline Json allFieldsJson(const Object& object) {
  Json primitives=Json::array(), meshes=Json::array(), planes=Json::array();
  for (const auto& primitive:object.primitives) {
    Json dimensions=Json::array(), points=Json::array();
    for (const auto dimension:primitive.dimensions) dimensions.push_back(number(dimension));
    for (const auto& point:primitive.polygon.points) points.push_back(pointJson(point));
    primitives.push_back({{"type",primitive.type},{"dimensions",dimensions},{"polygon",{{"points",points}}}});
  }
  for (const auto& mesh:object.meshes) {
    Json triangles=Json::array(), vertices=Json::array();
    for (const auto& triangle:mesh.triangles) triangles.push_back({{"vertex_indices",triangle.vertex_indices}});
    for (const auto& vertex:mesh.vertices) vertices.push_back(pointJson(vertex));
    meshes.push_back({{"triangles",triangles},{"vertices",vertices}});
  }
  for (const auto& plane:object.planes) {
    Json coefficients=Json::array(); for (const auto value:plane.coef) coefficients.push_back(number(value));
    planes.push_back({{"coef",coefficients}});
  }
  return {{"header",{{"stamp",{{"sec",object.header.stamp.sec},{"nanosec",object.header.stamp.nanosec}}},
                     {"frame_id",object.header.frame_id}}},
    {"pose",poseJson(object.pose)},{"id",object.id},
    {"type",{{"key",object.type.key},{"db",object.type.db}}},
    {"primitives",primitives},{"primitive_poses",posesJson(object.primitive_poses)},
    {"meshes",meshes},{"mesh_poses",posesJson(object.mesh_poses)},
    {"planes",planes},{"plane_poses",posesJson(object.plane_poses)},
    {"subframe_names",object.subframe_names},{"subframe_poses",posesJson(object.subframe_poses)},
    {"operation",object.operation}};
}

inline Json rawMessage(const Object& object) {
  rclcpp::Serialization<Object> serializer;
  rclcpp::SerializedMessage serialized;
  serializer.serialize_message(&object,&serialized);
  const auto& bytes=serialized.get_rcl_serialized_message();
  return {{"ros_type","moveit_msgs/msg/CollisionObject"},{"encoding","ROS2_CDR_hex"},
    {"byte_count",bytes.buffer_length},{"cdr_hex",hex(bytes.buffer,bytes.buffer_length)},
    {"all_fields",allFieldsJson(object)}};
}

inline Json rawObjects(const std::vector<Object>& objects) {
  Json result=Json::array(); for (const auto& object:objects) result.push_back(rawMessage(object));
  return result;
}
inline Json rawObjects(const std::map<std::string,Object>& objects) {
  Json result=Json::array();
  for (const auto& [key,object]:objects) result.push_back({{"map_key",key},{"message",rawMessage(object)}});
  return result;
}

struct Transform { Eigen::Vector3d p; Eigen::Quaterniond q; bool empty_root_quaternion=false; };

inline Transform transform(const geometry_msgs::msg::Pose& pose, bool object_root) {
  const auto& p=pose.position; const auto& q=pose.orientation;
  for (const double value:{p.x,p.y,p.z,q.x,q.y,q.z,q.w})
    if (!std::isfinite(value)) throw std::runtime_error("nonfinite pose");
  Transform result{Eigen::Vector3d(p.x,p.y,p.z),Eigen::Quaterniond(q.w,q.x,q.y,q.z),false};
  if (q.x==0. && q.y==0. && q.z==0. && q.w==0.) {
    if (!object_root || p.x!=0. || p.y!=0. || p.z!=0.)
      throw std::runtime_error("zero quaternion outside completely empty object root");
    result.q=Eigen::Quaterniond::Identity(); result.empty_root_quaternion=true;
  } else {
    const double norm=result.q.norm();
    if (!std::isfinite(norm) || std::abs(norm-1.)>kUnitQuaternionRoundoff)
      throw std::runtime_error("malformed non-unit quaternion");
    result.q.normalize();
  }
  return result;
}

inline Transform compose(const Transform& object, const Transform& primitive) {
  Transform result{object.p+object.q*primitive.p,object.q*primitive.q,false};
  result.q.normalize(); return result;
}

inline Json transformJson(const Transform& t) {
  return {{"translation_xyz_m",{number(t.p.x()),number(t.p.y()),number(t.p.z())}},
          {"quaternion_xyzw",{number(t.q.x()),number(t.q.y()),number(t.q.z()),number(t.q.w())}}};
}

inline double rotationError(const Eigen::Quaterniond& expected, const Eigen::Quaterniond& observed) {
  Eigen::Quaterniond relative=expected.conjugate()*observed; relative.normalize();
  // acos会把1e-8rad量级舍入为0；atan2同时处理q/-q的同一姿态。
  return 2.*std::atan2(relative.vec().norm(),std::abs(relative.w()));
}

inline Json validateObject(const Object& expected, const Object& observed) {
  Json errors=Json::array(), primitives=Json::array();
  const auto fail=[&](const std::string& reason) { errors.push_back(reason); };
  if (expected.id!=observed.id) fail("id mismatch");
  if (expected.header.frame_id!="world" || observed.header.frame_id!="world") fail("frame must be world");
  const auto counts=[](const Object& object) -> Json { return {
    {"primitives",object.primitives.size()},{"primitive_poses",object.primitive_poses.size()},
    {"meshes",object.meshes.size()},{"mesh_poses",object.mesh_poses.size()},
    {"planes",object.planes.size()},{"plane_poses",object.plane_poses.size()},
    {"subframe_names",object.subframe_names.size()},{"subframe_poses",object.subframe_poses.size()}}; };
  if (counts(expected)!=counts(observed)) fail("geometry/pose count mismatch");
  for (const auto* object:{&expected,&observed}) {
    if (object->primitives.size()!=object->primitive_poses.size() ||
        object->meshes.size()!=object->mesh_poses.size() || object->planes.size()!=object->plane_poses.size() ||
        object->subframe_names.size()!=object->subframe_poses.size()) fail("geometry/pose counts internally inconsistent");
    // 当前授权世界只有box；不能把新增mesh/plane/subframe默默视为已验证。
    if (!object->meshes.empty() || !object->planes.empty() || !object->subframe_names.empty())
      fail("unsupported geometry in fixed box-only world");
  }
  Json roots={{"expected_raw",poseJson(expected.pose)},{"observed_raw",poseJson(observed.pose)}};
  const auto norm=[](const geometry_msgs::msg::Pose& pose) {
    const auto& q=pose.orientation; return Eigen::Quaterniond(q.w,q.x,q.y,q.z).norm();
  };
  roots["expected_raw_quaternion_norm"]=number(norm(expected.pose));
  roots["observed_raw_quaternion_norm"]=number(norm(observed.pose));
  roots["unit_quaternion_roundoff_limit"]=kUnitQuaternionRoundoff;
  Transform expected_root,observed_root; bool roots_valid=false;
  try {
    expected_root=transform(expected.pose,true); observed_root=transform(observed.pose,true); roots_valid=true;
    roots["expected_empty_quaternion_as_identity"]=expected_root.empty_root_quaternion;
    roots["observed_empty_quaternion_as_identity"]=observed_root.empty_root_quaternion;
    roots["expected_interpreted"]=transformJson(expected_root); roots["observed_interpreted"]=transformJson(observed_root);
  } catch (const std::exception& error) { fail(std::string("invalid object root: ")+error.what()); }
  const auto count=std::min(expected.primitives.size(),observed.primitives.size());
  for (std::size_t i=0;i<count;++i) {
    const auto& a=expected.primitives[i]; const auto& b=observed.primitives[i];
    Json entry={{"index",i},{"expected_type",a.type},{"observed_type",b.type},{"dimension_errors_m",Json::array()}};
    if (a.type!=b.type) fail("primitive "+std::to_string(i)+" type mismatch");
    if (a.type!=a.BOX || b.type!=b.BOX || a.dimensions.size()!=3 || b.dimensions.size()!=3)
      fail("malformed box primitive dimensions/type");
    if (a.dimensions.size()!=b.dimensions.size()) fail("primitive dimension count mismatch");
    for (std::size_t j=0;j<std::min(a.dimensions.size(),b.dimensions.size());++j) {
      const double delta=std::abs(a.dimensions[j]-b.dimensions[j]);
      entry["dimension_errors_m"].push_back(number(delta));
      if (!std::isfinite(a.dimensions[j]) || !std::isfinite(b.dimensions[j]) ||
          a.dimensions[j]<=0. || b.dimensions[j]<=0. || delta>kDimensionLimit) fail("primitive dimension mismatch/nonfinite");
    }
    if (a.polygon!=b.polygon || !a.polygon.points.empty()) fail("unexpected box polygon");
    if (i<expected.primitive_poses.size() && i<observed.primitive_poses.size()) {
      entry["expected_primitive_raw"]=poseJson(expected.primitive_poses[i]);
      entry["observed_primitive_raw"]=poseJson(observed.primitive_poses[i]);
      entry["expected_raw_quaternion_norm"]=number(norm(expected.primitive_poses[i]));
      entry["observed_raw_quaternion_norm"]=number(norm(observed.primitive_poses[i]));
      try {
        const auto a_shape=transform(expected.primitive_poses[i],false);
        const auto b_shape=transform(observed.primitive_poses[i],false);
        if (roots_valid) {
          const auto a_world=compose(expected_root,a_shape), b_world=compose(observed_root,b_shape);
          const Eigen::Vector3d delta=b_world.p-a_world.p;
          const double position=delta.norm(), angle=rotationError(a_world.q,b_world.q);
          entry["expected_composed_world"]=transformJson(a_world); entry["observed_composed_world"]=transformJson(b_world);
          entry["translation_error_xyz_m"]={number(delta.x()),number(delta.y()),number(delta.z())};
          entry["translation_error_norm_m"]=number(position); entry["rotation_error_rad"]=number(angle);
          if (!std::isfinite(position) || position>kTranslationLimit) fail("composed world translation mismatch");
          if (!std::isfinite(angle) || angle>kRotationLimit) fail("composed world rotation mismatch");
        }
      } catch (const std::exception& error) { fail(std::string("invalid primitive pose: ")+error.what()); }
    }
    primitives.push_back(entry);
  }
  return {{"id",expected.id},{"pass",errors.empty()},{"errors",errors},
    {"expected_counts",counts(expected)},{"observed_counts",counts(observed)},
    {"object_roots",roots},{"primitives",primitives}};
}

inline Json validateWorld(const std::vector<Object>& expected, const std::map<std::string,Object>& observed) {
  Json checks=Json::array(), errors=Json::array(); bool pass=expected.size()==observed.size();
  if (!pass) errors.push_back("world object count mismatch");
  for (const auto& object:expected) {
    const auto found=observed.find(object.id);
    if (found==observed.end()) { pass=false; errors.push_back("missing object: "+object.id); continue; }
    auto check=validateObject(object,found->second);
    if (!check.at("pass").get<bool>()) pass=false;
    checks.push_back(std::move(check));
  }
  for (const auto& [key,object]:observed) {
    if (key!=object.id) { pass=false; errors.push_back("map key/id mismatch: "+key); }
    if (std::none_of(expected.begin(),expected.end(),[&](const auto& item) { return item.id==key; })) {
      pass=false; errors.push_back("unexpected object: "+key);
    }
  }
  return {{"pass",pass},{"errors",errors},{"objects",checks},
    {"limits",{{"translation_norm_m",kTranslationLimit},{"rotation_angle_rad",kRotationLimit},
               {"dimension_absolute_m",kDimensionLimit}}}};
}
} // namespace task01_readback
