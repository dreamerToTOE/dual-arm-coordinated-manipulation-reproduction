// [THIN_ADAPTER] 原 TASK03 模型、TASK05 FCL、TASK06 搜索；无机器人执行接口。
#include "platforms/offline_moveit/task03_closure/model_adapter.hpp"
#include "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp"
#include "platforms/offline_moveit/task06_constrained_rrtconnect/evidence.hpp"
#include <fstream>
#include <iostream>
#include <sstream>

namespace
{
using Json=nlohmann::json;
std::string read(const std::string& path)
{
  std::ifstream file(path); if(!file) throw std::runtime_error("Missing source input: "+path);
  std::ostringstream out; out<<file.rdbuf(); return out.str();
}
Eigen::Isometry3d pose(const Json& p)
{
  const auto t=p.at("translation_m"),r=p.at("quaternion_xyzw");
  return common_geometry::fromXyzw(Eigen::Vector3d(t.at(0).get<double>(),t.at(1).get<double>(),t.at(2).get<double>()),
    Eigen::Vector4d(r.at(0).get<double>(),r.at(1).get<double>(),r.at(2).get<double>(),r.at(3).get<double>()));
}

// 薄函数只连接已有接口；合法起终点的来源资格由独立来源门禁负责。
// 当前协议没有已批准端点，所以 main 不调用它；不宣称已集成验收成功。
[[maybe_unused]] p4::PlannerResult planQualifiedEndpoints(
  task03_offline::DualFr3Model& model,task05_offline::CollisionAdapter& fcl,
  const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr,
  const p4::JointVector& start,const p4::JointVector& goal,const p4::PlannerOptions& options)
{
  const auto bounds=model.positionBounds();
  return p4::plan(start,goal,bounds.first,bounds.second,
    [&](const p4::JointVector& q){const auto arms=model.sample(q);return p4::evaluate(arms.first,arms.second,gl,gr);},
    [&](const p4::JointVector& q){return model.minimumJointMargin(q);},
    [&](const p4::JointVector& q){return fcl.check(q);},options);
}
}
int main(int argc,char** argv)
{
  Json out;
  try
  {
    if(argc!=3) throw std::invalid_argument("Usage: native_audit PROTOCOL SOURCE_AUDIT_JSON");
    const auto config=Json::parse(read(argv[1])),audit=Json::parse(read(argv[2]));
    if(audit.at("source_scenario")!=config.at("source_scenario") ||
       !audit.at("model_checks").at("urdf").at("xml_structure_and_all_numeric_fields_equal").get<bool>() ||
       !audit.at("model_checks").at("srdf").at("xml_structure_and_all_numeric_fields_equal").get<bool>())
      throw std::runtime_error("Pinned model source audit is incomplete");
    const auto urdf=read(config.at("urdf")),srdf=read(config.at("srdf"));
    task03_offline::DualFr3Model model(urdf,srdf);
    const Eigen::Isometry3d gl=pose(audit.at("nominal_object_to_tcp").at("left")).inverse();
    // 采用来源已核对的名义抓取，只构造原生离线几何；不是实测 D6 attachment。
    task05_offline::CollisionAdapter fcl(urdf,srdf,config.at("geometry_archive"),gl);
    const auto names=model.jointNames();
    if(Json(names)!=audit.at("joint_names")) throw std::runtime_error("Native joint order mismatch");
    const auto bounds=model.positionBounds();
    for(int i=0;i<14;++i)
    {
      const auto limits=audit.at("constants").at("FR3_OFFICIAL_JOINT_LIMITS_RAD").at(std::to_string(i%7+1));
      if(bounds.first[i]!=limits.at(0).get<double>() || bounds.second[i]!=limits.at(1).get<double>())
        throw std::runtime_error("Native limits differ from source scene official override");
    }
    // q=0 仅检查两个原模型相同，不作为合法构型/端点，不执行碰撞查询。
    const p4::JointVector identity_check=p4::JointVector::Zero();
    for(const auto* link:{"left_fr3_link0","right_fr3_link0","left_fr3_link8","right_fr3_link8",
                         "left_fr3_side_suction_tcp","right_fr3_side_suction_tcp"})
      if((model.linkPose(identity_check,link).matrix()-fcl.linkPose(identity_check,link).matrix()).cwiseAbs().maxCoeff()>1e-12)
        throw std::runtime_error("Native FK/FCL models disagree");
    out={{"native_model_loaded",true},{"joint_names",names},
      {"native_lower_rad",task05_offline::vectorJson(bounds.first)},
      {"native_upper_rad",task05_offline::vectorJson(bounds.second)},
      {"native_collision_manifest",fcl.manifest()},
      {"manifest_scope","STATIC_TABLE_WALLS_AND_ONE_CARRIED_CUBE_TEMPLATE_NOT_COMPLETE_TASK26_BATCH"},
      {"other_task26_cubes_loaded",false},{"native_state_collision_queries",0},
      {"endpoint_gate",audit.at("endpoint_gate")},{"planning_calls",0},{"rng_draws",0},
      {"path",nullptr},{"path_metrics",nullptr},{"simulation_time",nullptr},{"physics_step",nullptr},
      {"execution_commands",0},{"continuous_collision_certificate",false},
      {"task06_is_a_status","PARTIAL"}};
    if(!config.at("endpoints").at("start").is_null() || !config.at("endpoints").at("goal").is_null())
      throw std::runtime_error("New endpoint input is outside current audited protocol; review required");
    out["reason"]="Actual shared-held START/PRE_PUSH 14q not confirmed; no search dispatched";
    std::cout<<out.dump(2)<<'\n'; return 0; // 软件审计完成 != 科学路径验收通过。
  }
  catch(const std::exception& e)
  {
    out["task06_is_a_status"]="PARTIAL";out["error"]=e.what();
    std::cout<<out.dump(2)<<'\n';return 1;
  }
}
