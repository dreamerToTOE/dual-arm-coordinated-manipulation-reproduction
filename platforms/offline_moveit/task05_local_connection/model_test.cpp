// [ENGINEERING] 固定次数真实FR3/原生FCL验收。仅私有内存，无ROS初始化/服务/执行。
#include "platforms/offline_moveit/task03_closure/model_adapter.hpp"
#include "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp"
#include "platforms/offline_moveit/task05_local_connection/evidence.hpp"
#include <fstream>
#include <iostream>
#include <sstream>

namespace
{
using namespace task05_offline;
using Model=task03_offline::DualFr3Model;
std::string read(const std::string& p)
{
  std::ifstream s(p); if(!s) throw std::runtime_error("Missing immutable input: "+p);
  std::ostringstream b; b<<s.rdbuf(); return b.str();
}
p4::JointVector joints(const Json& j)
{
  if(j.size()!=14) throw std::runtime_error("Expected exact stored 14q");
  p4::JointVector q; for(int i=0;i<14;++i) q[i]=j.at(i).get<double>();
  if(!q.allFinite()) throw std::runtime_error("Nonfinite stored q"); return q;
}
Eigen::Isometry3d pose(const Json& j)
{
  const auto p=j.at("translation_m"),q=j.at("quaternion_xyzw");
  return common_geometry::fromXyzw(Eigen::Vector3d(p.at(0),p.at(1),p.at(2)),
    Eigen::Vector4d(q.at(0),q.at(1),q.at(2),q.at(3)));
}
p4::LocalConnectionOptions options(const Json& j)
{
  // 协议文件由runner的预声明hash锁定，这里只构造显式选项，不寻找可通过的值。
  return {{j.at("position_tolerance_m"),j.at("rotation_tolerance_rad"),
    j.at("max_iterations"),j.at("svd_absolute_cutoff"),j.at("svd_relative_cutoff"),
    j.at("stagnation_step_rad")},j.at("leaf_joint_l2_resolution_rad"),
    j.at("adjacent_joint_l2_limit_rad"),j.at("adjacent_joint_max_abs_limit_rad"),
    j.at("midpoint_projection_l2_correction_limit_rad"),j.at("max_recursion_depth"),
    j.at("max_midpoint_projections"),j.at("max_path_points")};
}
void run(const std::string& protocol,Json& out)
{
  const std::string urdf_path="tests/fixtures/task03/robot.urdf",srdf_path="tests/fixtures/task03/robot.srdf";
  const std::string archive="results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml";
  const std::string projected="results/20261009_TASK04_projection03/projection_metrics.json";
  const auto config=Json::parse(read(protocol)),prior=Json::parse(read(projected));
  const auto o=options(config);
  Model model(read(urdf_path),read(srdf_path));
  const auto margin=[&](const p4::JointVector& q){return model.minimumJointMargin(q);};
  Json failures=Json::array(),cases=Json::array(),manifests=Json::array();
  std::size_t positives=0,negatives=0;
  double max_position=0.,max_rotation=0.,min_margin=1e100,max_l2=0.,max_abs=0.,wall=0.;
  std::size_t projections=0,native_checks=0,path_points=0;
  const auto require=[&](bool ok,const std::string& message){if(!ok) failures.push_back(message);};
  out["protocol"]=config; out["prior_projection_source"]=projected;
  out["fixed_grasp_sources"]=prior.at("grasp_fixtures");
  for(const bool algebraic:{false,true})
  {
    const auto& f=prior.at("grasp_fixtures").at(algebraic?"algebraic_once_fixed":"historical_original_fixed");
    const auto gl=pose(f.at("left_tcp_to_object")),gr=pose(f.at("right_tcp_to_object"));
    CollisionAdapter backend(read(urdf_path),read(srdf_path),archive,gl);
    const auto original_manifest=backend.manifest();
    const auto evaluate=[&](const p4::JointVector& q) {
      const auto arms=model.sample(q); return p4::evaluate(arms.first,arms.second,gl,gr);
    };
    const auto oracle=[&](const p4::JointVector& q) {
      ++native_checks;
      for(const auto& link:{"left_fr3_side_suction_tcp","right_fr3_side_suction_tcp"})
      {
        const auto a=model.linkPose(q,link),b=backend.linkPose(q,link);
        if((a.matrix()-b.matrix()).cwiseAbs().maxCoeff()>1e-12)
          throw std::runtime_error("Unchanged model FK/collision model mismatch");
      }
      return backend.check(q);
    };
    std::vector<std::pair<std::string,p4::JointVector>> endpoints;
    if(algebraic)
    {
      for(const auto& row:prior.at("neighborhood_trials"))
      {
        if(row.at("repeat_index")!=0) continue;
        const int joint=row.at("joint_index");
        if(row.at("trial_id")=="zero" || ((joint==0 || joint==7) && row.at("amplitude_rad")==0.03))
        {
          require(row.at("status")=="CONVERGED","Stored algebraic endpoint status");
          endpoints.push_back({row.at("trial_id"),joints(row.at("projected_q_rad"))});
        }
      }
      require(endpoints.size()==5,"Exactly five fixed algebraic endpoints, no post-result selection");
    }
    else
    {
      for(const int index:{0,1,4})
      {
        const auto& row=prior.at("historical_diagnostic_trials").at(index);
        require(row.at("source_state_index")==index && row.at("status")=="CONVERGED",
          "Stored original endpoint identity/status");
        endpoints.push_back({"state"+std::to_string(index),joints(row.at("projected_q_rad"))});
      }
    }
    if(endpoints.empty()) throw std::runtime_error("No exact input endpoints");
    const auto q0=endpoints.front().second;
    const auto trial=[&](const std::string& name,const p4::JointVector& a,const p4::JointVector& b,
                         p4::ConnectionStatus expected) {
      const auto result=p4::connect(a,b,evaluate,margin,oracle,o);
      const bool positive=expected==p4::ConnectionStatus::CONNECTED;
      positive?++positives:++negatives;
      require(result.status==expected,name+": expected "+p4::statusName(expected)+", got "+p4::statusName(result.status));
      require((result.requested_start-a).norm()==0. && (result.requested_goal-b).norm()==0.,name+": caller endpoints preserved");
      if(positive && result.status==expected)
      {
        require(!result.verified_prefix.empty(),name+": nonempty complete path");
        if(!result.verified_prefix.empty())
          require((result.checked_points.at(result.verified_prefix.back()).q-b).norm()==0.,name+": exact goal reached, no snap");
        for(const auto i:result.verified_prefix)
        {
          const auto& p=result.checked_points.at(i);
          require(p.qualified && p.residual && p.collision && p.collision->complete &&
            !p.collision->self_collision && !p.collision->world_collision,name+": independently qualified path evidence");
          max_position=std::max(max_position,p.residual->head<3>().norm());
          max_rotation=std::max(max_rotation,p.residual->tail<3>().norm());
          min_margin=std::min(min_margin,*p.joint_margin_rad);
        }
        for(const auto& e:result.leaf_edges)
        {
          require(e.accepted && e.l2_rad<=o.adjacent_l2_limit_rad && e.max_abs_rad<=o.adjacent_max_abs_limit_rad,
            name+": continuity evidence");
          max_l2=std::max(max_l2,e.l2_rad);max_abs=std::max(max_abs,e.max_abs_rad);
        }
        path_points+=result.verified_prefix.size();
      }
      projections+=result.projection_calls;wall+=result.compute_wall_time_sec;
      Json record=connectionJson(result);
      record["case_id"]=name;record["grasp_fixture"]=algebraic?"G_STAR_ALGEBRAIC_TEST_ONLY":"ORIGINAL_ARCHIVED_FIXED";
      record["expected_status"]=p4::statusName(expected);record["passed"]=result.status==expected;
      record["native_backend_manifest"]=backend.manifest();cases.push_back(std::move(record));
      std::cout<<name<<": "<<p4::statusName(result.status)<<" points="<<result.verified_prefix.size()
        <<" projected="<<result.projection_calls<<'\n';
    };
    const std::string prefix=algebraic?"algebraic/":"original/";
    trial(prefix+"same",q0,q0,p4::ConnectionStatus::CONNECTED);
    for(std::size_t i=1;i<endpoints.size();++i)
    {
      trial(prefix+"q0_to_"+endpoints[i].first,q0,endpoints[i].second,p4::ConnectionStatus::CONNECTED);
      if(!algebraic) trial(prefix+endpoints[i].first+"_to_q0",endpoints[i].second,q0,p4::ConnectionStatus::CONNECTED);
    }
    require(backend.manifest()==original_manifest,"Private ACM/world unchanged throughout positive suite");
    if(!algebraic)
    {
      auto bad=q0;bad[0]=10.;trial("native_bounds_negative",q0,bad,p4::ConnectionStatus::JOINT_LIMIT);
      bad=q0;bad[0]+=0.001;trial("invalid_exact_closure_negative",q0,bad,p4::ConnectionStatus::CLOSURE);
      backend.addNegativeWorldBox(q0);
      trial("real_fcl_box_at_tcp_negative",q0,endpoints.at(1).second,p4::ConnectionStatus::COLLISION);
      const auto& last=cases.back();
      require(last.at("verified_prefix_indices").empty(),"Real FCL collision endpoint not added to verified prefix");
      require(!last.at("checked_points").at(0).at("collision").at("contacts").empty(),
        "Real FCL exact pair/depth evidence retained");
    }
    manifests.push_back({{"fixture",prefix},{"before",original_manifest},{"after",backend.manifest()}});
  }
  require(positives==10 && negatives==3,"Predeclared finite case counts");
  out["cases"]=cases;out["native_manifests"]=manifests;out["failures"]=failures;
  out["summary"]={{"positive_connections",positives},{"negative_connections",negatives},
    {"positive_path_points",path_points},{"connector_projection_calls",projections},{"native_collision_checks",native_checks},
    {"max_position_residual_m",max_position},{"max_rotation_residual_rad",max_rotation},
    {"min_native_joint_margin_rad",min_margin},{"max_adjacent_l2_rad",max_l2},{"max_adjacent_max_abs_rad",max_abs},
    {"total_connector_compute_wall_sec",wall}};
  out["task05_status"]=failures.empty()?"PASS_CANDIDATE":"PARTIAL";
}
}
int main(int argc,char** argv)
{
  Json output={{"task","TASK05"},{"scope","OFFLINE_DISCRETE_RBS_REAL_FR3_AND_NATIVE_FCL_ONLY"},
    {"task05_status","PARTIAL"},{"simulation_step",nullptr},{"simulation_time",nullptr},
    {"seed",nullptr},{"random_sampling",false},{"ros_context_initialized",false},
    {"isaac_or_controller_started",false},{"benchmark_status","DRAFT_NOT_FROZEN"},
    {"task02_d","DEFERRED"},{"continuous_collision_certificate",false}};
  if(argc!=5 || std::string(argv[1])!="--protocol" || std::string(argv[3])!="--output")
    {std::cerr<<"Use --protocol PATH --output NEW_JSON_PATH\n";return 2;}
  if(std::ifstream(argv[4]).good()) {std::cerr<<"Refuse evidence overwrite\n";return 2;}
  try {run(argv[2],output);}
  catch(const std::exception& e) {output["error"]=e.what();output["task05_status"]="PARTIAL";}
  std::ofstream stream(argv[4]);stream<<output.dump(2)<<'\n';stream.close();
  std::cout<<"TASK05="<<output.at("task05_status")<<'\n';
  return stream.fail()?2:(output.at("task05_status")=="PASS_CANDIDATE"?0:1);
}
