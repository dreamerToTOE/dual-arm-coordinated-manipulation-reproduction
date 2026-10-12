#pragma once
// [THIN_ADAPTER / ENGINEERING] 原 MoveIt PlanningScene/FCL；无 ROS context 或执行接口。
#include "baselines/p4_closed_chain/local_connection.hpp"

#include <memory>
#include <string>
#include <nlohmann/json.hpp>

namespace task05_offline
{
class CollisionAdapter
{
public:
  CollisionAdapter(const std::string& urdf_xml, const std::string& srdf_xml,
                   const std::string& archive_yaml_path,
                   const Eigen::Isometry3d& left_tcp_to_object);
  ~CollisionAdapter();
  CollisionAdapter(const CollisionAdapter&) = delete;
  CollisionAdapter& operator=(const CollisionAdapter&) = delete;

  p4::CollisionEvidence check(const p4::JointVector& q) const;
  nlohmann::json manifest() const;
  // [TASK06-IS-A] 原生 World 的只读组合 world-shape readback；不查询新碰撞后端。
  nlohmann::json worldReadback() const;
  Eigen::Isometry3d linkPose(const p4::JointVector& q, const std::string& name) const;

  // 只在独立负例实例中添加同尺寸盒；不移动/删除归档 table 或三面墙。
  void addNegativeWorldBox(const p4::JointVector& q);
  // [ENGINEERING TASK06] 独立离线fixture，沿用原生box插入；禁止覆盖旧环境。
  void addPrivateWorldBox(const std::string& id, const Eigen::Isometry3d& pose_world,
                          const Eigen::Vector3d& size_m);

private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};
}  // namespace task05_offline
