// [ENGINEERING] 固定协议真实FR3离线搜索；没有ROS初始化/服务/物理执行。
#include "baselines/p4_closed_chain/constrained_rrtconnect.hpp"
#include "platforms/offline_moveit/task06_constrained_rrtconnect/evidence.hpp"
#include "platforms/offline_moveit/task03_closure/model_adapter.hpp"
#include "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <filesystem>

namespace
{
using Json=nlohmann::json;
using namespace task05_offline;
std::string read(const std::string& path)
{
  std::ifstream file(path); if(!file) throw std::runtime_error("Missing fixed input: "+path);
  std::ostringstream text; text<<file.rdbuf(); return text.str();
}
void write(const std::filesystem::path& path,const Json& value)
{
  if(std::filesystem::exists(path)) throw std::runtime_error("Never overwrite evidence: "+path.string());
  std::ofstream stream(path); if(!stream) throw std::runtime_error("Cannot open evidence");
  stream<<value.dump(2)<<'\n'; if(!stream) throw std::runtime_error("Cannot save complete evidence");
}
p4::JointVector q(const Json& row)
{
  if(row.size()!=14) throw std::runtime_error("Expected actual stored14q");
  p4::JointVector result; for(int i=0;i<14;++i) result[i]=row.at(i).get<double>();
  if(!result.allFinite()) throw std::runtime_error("Nonfinite stored14q");
  return result;
}
Eigen::Vector3d xyz(const Json& v) {return {v.at(0),v.at(1),v.at(2)};}
Eigen::Isometry3d pose(const Json& p)
{
  auto v=p.at("quaternion_xyzw"); return common_geometry::fromXyzw(xyz(p.at("translation_m")),
    Eigen::Vector4d(v.at(0),v.at(1),v.at(2),v.at(3)));
}
p4::LocalConnectionOptions local(const Json& j)
{
  return {{j.at("position_tolerance_m"),j.at("rotation_tolerance_rad"),j.at("max_iterations"),
    j.at("svd_absolute_cutoff"),j.at("svd_relative_cutoff"),j.at("stagnation_step_rad")},
    j.at("leaf_joint_l2_resolution_rad"),j.at("adjacent_joint_l2_limit_rad"),
    j.at("adjacent_joint_max_abs_limit_rad"),j.at("midpoint_projection_l2_correction_limit_rad"),
    j.at("max_recursion_depth"),j.at("max_midpoint_projections"),j.at("max_path_points")};
}
p4::PlannerOptions options(const Json& j,const p4::LocalConnectionOptions& l,std::uint64_t seed)
{
  return {l,seed,j.at("raw_steer_range_rad"),j.at("candidate_projection_correction_l2_limit_rad"),
    j.at("accepted_extension_l2_limit_rad"),j.at("minimum_progress_rad"),j.at("extend_attempts"),
    j.at("connect_attempts"),j.at("max_nodes"),j.at("max_iterations"),j.at("max_compute_wall_sec")};
}
void run(const std::string& protocol,const std::filesystem::path& output,Json& report)
{
  const auto config=Json::parse(read(protocol));
  const auto l=local(Json::parse(read(config.at("local_connection_protocol"))));
  const auto fixture=Json::parse(read(config.at("fixture")));
  const auto& grasps=fixture.at("grasp_fixtures").at(config.at("grasp_fixture"));
  const auto gl=pose(grasps.at("left_tcp_to_object")),gr=pose(grasps.at("right_tcp_to_object"));
  const auto urdf=read("tests/fixtures/task03/robot.urdf"),srdf=read("tests/fixtures/task03/robot.srdf");
  const std::string archive="results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml";
  task03_offline::DualFr3Model model(urdf,srdf);
  const auto bounds=model.positionBounds();
  const auto margin=[&](const p4::JointVector& value){return model.minimumJointMargin(value);};
  const auto evaluate=[&](const p4::JointVector& value){const auto arms=model.sample(value);
    return p4::evaluate(arms.first,arms.second,gl,gr);};
  const auto endpoint=[&](int index){const auto& trial=fixture.at("historical_diagnostic_trials").at(index);
    if(trial.at("source_state_index")!=index || trial.at("status")!="CONVERGED")
      throw std::runtime_error("Stored projected endpoint identity/status mismatch");
    return q(trial.at("projected_q_rad"));};
  report["protocol"]=config; report["grasp_fixture"]=grasps;
  report["native_joint_names"]=model.jointNames();
  report["native_lower_rad"]=vectorJson(bounds.first); report["native_upper_rad"]=vectorJson(bounds.second);
  report["cases"]=Json::array(); report["negative_cases"]=Json::array();
  report["failures"]=Json::array();
  const auto require=[&](bool ok,const std::string& reason){if(!ok) report["failures"].push_back(reason);};
  for(const std::string name:{"simple","nontrivial","obstacle"})
  {
    const auto specification=config.at("case_"+name);
    const auto start=endpoint(specification.at("source_start_index"));
    const auto goal=endpoint(specification.at("source_goal_index"));
    CollisionAdapter backend(urdf,srdf,archive,gl);
    if(name=="obstacle")
    {
      const auto b=config.at("private_obstacle"); Eigen::Isometry3d p=Eigen::Isometry3d::Identity();
      const auto v=b.at("quaternion_xyzw");
      p=common_geometry::fromXyzw(xyz(b.at("translation_world_m")),Eigen::Vector4d(v.at(0),v.at(1),v.at(2),v.at(3)));
      backend.addPrivateWorldBox(b.at("id"),p,xyz(b.at("size_m")));
    }
    const auto collision=[&](const p4::JointVector& value){
      // 两个适配器均读取未修改RobotModel；防止规划FK与碰撞FK不一致。
      for(const auto* link:{"left_fr3_side_suction_tcp","right_fr3_side_suction_tcp"})
        if((model.linkPose(value,link).matrix()-backend.linkPose(value,link).matrix()).cwiseAbs().maxCoeff()>1e-12)
          throw std::runtime_error("Unchanged FK/FCL model mismatch");
      return backend.check(value);
    };
    const auto direct=p4::connect(start,goal,evaluate,margin,collision,l);
    const auto direct_file="direct_"+name+".json"; write(output/direct_file,connectionJson(direct));
    Json scene={{"case",name},{"direct_connection_status",p4::statusName(direct.status)},
      {"direct_connection_artifact",direct_file},{"manifest",backend.manifest()},
      {"exact_start_rad",vectorJson(start)},{"exact_goal_rad",vectorJson(goal)},
      {"ambient_endpoint_distance_rad",(start-goal).norm()},{"trials",Json::array()}};
    if(name=="obstacle") require(direct.status==p4::ConnectionStatus::COLLISION,
      "Fixed private obstacle did not reject direct TASK05 connector specifically for collision");
    std::size_t qualified_seeds=0;
    for(const auto& seed_json:config.at("seeds"))
    {
      const std::uint64_t seed=seed_json;
      Json deterministic_before;
      bool seed_qualified=true;
      const int repeats=config.at("repeats_per_case_seed");
      for(int repeat=0;repeat<repeats;++repeat)
      {
        auto result=p4::plan(start,goal,bounds.first,bounds.second,evaluate,margin,collision,options(config,l,seed));
        Json full=task06_offline::plannerJson(result);
        const std::string id=name+"_seed"+std::to_string(seed)+"_repeat"+std::to_string(repeat);
        full["trial_id"]=id; full["classification"]="OFFLINE_REAL_FR3_NATIVE_FCL_DISCRETE_ONLY";
        full["native_backend_manifest"]=backend.manifest();
        write(output/(id+".json"),full);
        const auto stable=task06_offline::deterministicJson(result);
        if(repeat==0) deterministic_before=stable;
        else require(stable==deterministic_before,id+": deterministic path/termination/counters differ");
        const bool success=result.status==p4::PlannerStatus::SUCCESS;
        const bool nontrivial=result.counters.accepted_start_edges>0 && result.counters.accepted_goal_edges>0 && result.path_edges.size()>=3;
        seed_qualified=seed_qualified&&success&&(name=="simple"||nontrivial);
        if(name=="simple") require(success,id+": fixed simple planning failed");
        // 独立核对所有插入边；拒绝边的prefix从不出现在返回solution中。
        for(const auto* tree:{&result.start_tree,&result.goal_tree})
          for(std::size_t i=1;i<tree->size();++i)
          {
            const auto& node=tree->at(i);
            require(node.parent && node.incoming_attempt,id+": missing tree edge source");
            if(!node.parent||!node.incoming_attempt) continue;
            const auto& attempt=result.attempts.at(*node.incoming_attempt);
            require(attempt.status==p4::AttemptStatus::ACCEPTED && attempt.connection &&
              attempt.connection->status==p4::ConnectionStatus::CONNECTED,id+": tree edge not RBS qualified");
            if(attempt.connection)
              require((attempt.connection->requested_start-tree->at(*node.parent).q).norm()==0. &&
                (attempt.connection->requested_goal-node.q).norm()==0.,id+": inserted edge endpoint mismatch");
          }
        if(success)
        {
          require(result.path_metrics.has_value()&&!result.dense_path.empty(),id+": missing successful path evidence");
          require((result.dense_path.front()-start).norm()==0. && (result.dense_path.back()-goal).norm()==0.,id+": exact endpoints altered");
          for(std::size_t i=0;i<result.dense_path.size();++i)
          {
            const auto c=evaluate(result.dense_path[i]); const auto hit=collision(result.dense_path[i]);
            require(c.residual.head<3>().norm()<=l.projection.position_tolerance_m &&
              c.residual.tail<3>().norm()<=l.projection.rotation_tolerance_rad &&
              margin(result.dense_path[i])>=0. && hit.complete && !hit.self_collision && !hit.world_collision && hit.contacts.empty(),
              id+": independent dense output validation failed");
            if(i) require((result.dense_path[i]-result.dense_path[i-1]).norm()<=l.adjacent_l2_limit_rad &&
              (result.dense_path[i]-result.dense_path[i-1]).cwiseAbs().maxCoeff()<=l.adjacent_max_abs_limit_rad,
              id+": independent dense continuity failed");
          }
        }
        scene["trials"].push_back({{"trial_id",id},{"artifact",id+".json"},{"seed",seed},{"repeat",repeat},
          {"status",p4::statusName(result.status)},{"reason",result.reason},{"nontrivial",nontrivial},
          {"node_count",result.start_tree.size()+result.goal_tree.size()},{"path_tree_edges",result.path_edges.size()},
          {"path_points",result.dense_path.size()},{"compute_wall_time_sec",result.compute_wall_time_sec},
          {"summary",full.at("counters")},{"path_metrics",full.at("path_metrics")}});
        std::cout<<id<<": "<<p4::statusName(result.status)<<" nodes="<<result.start_tree.size()+result.goal_tree.size()
          <<" path_edges="<<result.path_edges.size()<<" wall="<<result.compute_wall_time_sec<<std::endl;
      }
      if(seed_qualified) ++qualified_seeds;
    }
    scene["qualified_seeds"]=qualified_seeds;
    if(name!="simple") require(qualified_seeds>0,name+": no fixed seed met nontrivial dual-tree acceptance");
    report["cases"].push_back(std::move(scene));
  }
  // 真实原模型负例，不使用合成碰撞替代nativeFCL。
  CollisionAdapter native_negative(urdf,srdf,archive,gl);
  const auto start=endpoint(0),goal=endpoint(1);
  auto outside=start; outside[0]=bounds.first[0]-1e-6;
  const auto bounds_failure=p4::plan(outside,goal,bounds.first,bounds.second,evaluate,margin,
    [&](const p4::JointVector& v){return native_negative.check(v);},options(config,l,7));
  require(bounds_failure.status==p4::PlannerStatus::START_REJECTED,"Native bound negative not rejected");
  report["negative_cases"].push_back({{"case","NATIVE_JOINT_BOUND"},{"status",p4::statusName(bounds_failure.status)}});
  write(output/"negative_native_bounds.json",task06_offline::plannerJson(bounds_failure));
  native_negative.addNegativeWorldBox(start);
  const auto native_failure=p4::plan(start,goal,bounds.first,bounds.second,evaluate,margin,
    [&](const p4::JointVector& v){return native_negative.check(v);},options(config,l,7));
  require(native_failure.status==p4::PlannerStatus::START_REJECTED && native_failure.start_root &&
    native_failure.start_root->status==p4::ConnectionStatus::COLLISION,"Actual native collision not rejected at root");
  report["negative_cases"].push_back({{"case","NATIVE_FCL_BOX_AT_TCP"},{"status",p4::statusName(native_failure.status)}});
  write(output/"negative_native_collision.json",task06_offline::plannerJson(native_failure));
  report["task06_status"]=report["failures"].empty()?"PASS_CANDIDATE":"PARTIAL";
  report["minimum_collision_distance"]="UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED";
  report["simulation_time"]=nullptr;report["physics_step"]=nullptr;report["physical_commands"]=0;
  report["qualification"]="OFFLINE_DISCRETE_SEARCH_NOT_PHYSICAL_OR_CONTINUOUS_CERTIFICATE";
}
}
int main(int argc,char** argv)
{
  std::string protocol; std::filesystem::path output;
  for(int i=1;i+1<argc;i+=2)
  {if(std::string(argv[i])=="--protocol") protocol=argv[i+1]; else if(std::string(argv[i])=="--output-dir") output=argv[i+1];}
  Json report;
  try
  {
    if(protocol.empty() || output.empty() || !std::filesystem::is_directory(output)) throw std::runtime_error("Required protocol/output directory absent");
    run(protocol,output,report); write(output/"planning_metrics.json",report);
    std::cout<<"TASK06="<<report.at("task06_status")<<std::endl;
    return report.at("task06_status")=="PASS_CANDIDATE"?0:1;
  }
  catch(const std::exception& e)
  {
    report["task06_status"]="PARTIAL";report["error"]=e.what();
    if(!output.empty()&&!std::filesystem::exists(output/"planning_metrics.json")) write(output/"planning_metrics.json",report);
    std::cerr<<e.what()<<std::endl;return 1;
  }
}
