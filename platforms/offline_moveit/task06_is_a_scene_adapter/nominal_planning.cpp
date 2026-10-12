// [THIN_ADAPTER] 同一URDF/KDL-LMA端点构造 + 已有TASK03–06；无ROS Node/服务/执行。
#include "platforms/offline_moveit/task03_closure/model_adapter.hpp"
#include "platforms/offline_moveit/task05_local_connection/collision_adapter.hpp"
#include "platforms/offline_moveit/task06_constrained_rrtconnect/evidence.hpp"
#include <kdl/chainiksolverpos_lma.hpp>
#include <kdl/chainfksolverpos_recursive.hpp>
#include <kdl_parser/kdl_parser.hpp>
#include <srdfdom/model.h>
#include <urdf_parser/urdf_parser.h>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <set>
#include <sstream>

namespace
{
using Json=nlohmann::json;
using namespace task05_offline;
using Clock=std::chrono::steady_clock;
std::string read(const std::string& path)
{
  std::ifstream f(path); if(!f) throw std::runtime_error("Missing input: "+path);
  std::ostringstream s; s<<f.rdbuf(); return s.str();
}
void write(const std::filesystem::path& path,const Json& j)
{
  if(std::filesystem::exists(path)) throw std::runtime_error("Never overwrite evidence: "+path.string());
  std::ofstream f(path); f<<j.dump(2)<<'\n'; f.flush();
  if(!f) throw std::runtime_error("Evidence write failed");
}
Eigen::Vector3d xyz(const Json& p)
{
  if(p.size()!=3) throw std::invalid_argument("Expected3D");
  return {p.at(0).get<double>(),p.at(1).get<double>(),p.at(2).get<double>()};
}
Eigen::Isometry3d pose(const Json& p)
{
  const auto r=p.at("quaternion_xyzw");
  return common_geometry::fromXyzw(xyz(p.at("translation_m")),Eigen::Vector4d(r.at(0),r.at(1),r.at(2),r.at(3)));
}
Json poseJson(const Eigen::Isometry3d& p)
{
  Eigen::Quaterniond r(p.linear());
  return {{"translation_m",vectorJson(p.translation())},{"quaternion_xyzw",{r.x(),r.y(),r.z(),r.w()}}};
}
KDL::Frame kdlFrame(const Eigen::Isometry3d& p)
{
  return {KDL::Rotation(p(0,0),p(0,1),p(0,2),p(1,0),p(1,1),p(1,2),p(2,0),p(2,1),p(2,2)),
          KDL::Vector(p(0,3),p(1,3),p(2,3))};
}
Eigen::Isometry3d eigenFrame(const KDL::Frame& p)
{
  Eigen::Isometry3d r=Eigen::Isometry3d::Identity();
  for(int i=0;i<3;++i) {r(i,3)=p.p(i);for(int j=0;j<3;++j) r(i,j)=p.M(i,j);}
  return r;
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
p4::JointVector home(const std::string& urdf,const std::string& srdf,
                     const std::array<std::string,14>& names)
{
  auto u=urdf::parseURDF(urdf); srdf::Model s;
  if(!u||!s.initString(*u,srdf)) throw std::runtime_error("Original SRDF unavailable");
  p4::JointVector q; std::set<int> found;
  for(const auto& state:s.getGroupStates())
    for(int side=0;side<2;++side)
      if(state.name_=="home" && state.group_==(side?"right_arm":"left_arm"))
        for(int i=0;i<7;++i)
        {const int k=7*side+i;const auto& v=state.joint_values_.at(names[k]);
         if(v.size()!=1 || !found.insert(k).second) throw std::runtime_error("HOME seed ambiguous");
         q[k]=v[0];}
  if(found.size()!=14||!q.allFinite()) throw std::runtime_error("Complete original HOME seed absent");
  return q;
}
void verifyWorld(CollisionAdapter& fcl,const Json& scene,const Json& config)
{
  const auto readback=fcl.worldReadback(); const auto expected=scene.at("adapter_world_objects");
  if(readback.size()!=expected.size() || readback.size()!=config.at("scene_world_object_count"))
    throw std::runtime_error("Native world count mismatch");
  for(const auto& e:expected)
  {
    const Json* observed=nullptr;
    for(const auto& r:readback) if(r.at("id")==e.at("id")) observed=&r;
    if(!observed || observed->at("frame_id")!="world" || observed->at("primitive_count")!=1 ||
       observed->at("primitive_type")!="BOX") throw std::runtime_error("Native world identity/type mismatch");
    Json p={{"translation_m",e.at("center_world_m")},{"quaternion_xyzw",e.at("quaternion_xyzw")}};
    const double eps=config.at("static_message_equivalence_epsilon");
    if((xyz(e.at("size_m"))-xyz(observed->at("size_m"))).cwiseAbs().maxCoeff()>eps ||
       (pose(p).matrix()-pose(observed->at("composed_shape_pose_world")).matrix()).cwiseAbs().maxCoeff()>eps)
      throw std::runtime_error("Composed native world geometry differs: "+e.at("id").get<std::string>());
  }
  if(fcl.manifest().at("attachment").at("id")!=config.at("attached_object_id"))
    throw std::runtime_error("Attached object ID mismatch");
}
class Endpoints
{
public:
  Endpoints(task03_offline::DualFr3Model& model,CollisionAdapter& fcl,const std::string& urdf,
            const Json& config,const p4::LocalConnectionOptions& l,
            const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr,
            const std::filesystem::path& output)
    :model_(model),fcl_(fcl),ik_(config.at("ik")),local_(l),gl_(gl),gr_(gr),output_(output)
  {
    if(!kdl_parser::treeFromString(urdf,tree_)) throw std::runtime_error("Original KDL tree parse failed");
    for(int side=0;side<2;++side)
    {
      const auto name=std::string(side?"right":"left")+"_fr3_side_suction_tcp";
      if(!tree_.getChain("world",name,chains_[side]) || chains_[side].getNrOfJoints()!=7)
        throw std::runtime_error("Original world-to-TCP chain mismatch");
      const auto names=model_.jointNames(); int j=7*side;
      for(const auto& segment:chains_[side].segments)
        if(segment.getJoint().getType()!=KDL::Joint::Fixed && segment.getJoint().getName()!=names[j++])
          throw std::runtime_error("Original KDL movable-joint order mismatch");
      Eigen::Matrix<double,6,1> weights;
      weights<<1.,1.,1.,ik_.at("orientation_vs_position").get<double>(),
                           ik_.at("orientation_vs_position").get<double>(),ik_.at("orientation_vs_position").get<double>();
      solvers_[side]=std::make_unique<KDL::ChainIkSolverPos_LMA>(chains_[side],weights,
        ik_.at("epsilon"),ik_.at("max_iterations_per_arm"),ik_.at("joint_increment_epsilon"));
    }
  }
  p4::ClosureSample evaluate(const p4::JointVector& q)
  {const auto a=model_.sample(q);return p4::evaluate(a.first,a.second,gl_,gr_);}
  std::optional<p4::JointVector> construct(const std::string& name,const Json& target,const p4::JointVector& first)
  {
    const auto object=pose(target); const auto bounds=model_.positionBounds();
    const std::uint64_t seed=ik_.at(name+"_rng_seed"); std::mt19937_64 rng(seed);
    const auto begin=Clock::now();std::size_t draws=0;
    const auto file=output_/(name+"_candidates.jsonl");
    if(std::filesystem::exists(file)) throw std::runtime_error("Candidate evidence exists");
    std::ofstream log(file); Json summary={{"rng_seed",seed},{"candidates",0},{"rng_draws",0},
      {"qualified",false},{"actual_physical_measurement",false}};
    for(int index=0;index<ik_.at("max_candidate_pairs_per_endpoint").get<int>();++index)
    {
      const double elapsed=std::chrono::duration<double>(Clock::now()-begin).count();
      if(elapsed>=ik_.at("max_compute_wall_sec_per_endpoint").get<double>())
      {summary["termination"]="ENDPOINT_TIME_BUDGET";break;}
      p4::JointVector initial=first;
      if(index) for(int j=0;j<14;++j)
      {const double u=static_cast<double>(rng()>>11)*0x1.0p-53; ++draws;
       initial[j]=bounds.first[j]+u*(bounds.second[j]-bounds.first[j]);}
      Json row={{"candidate_index",index},{"rng_seed",seed},{"rng_draws",draws},
        {"seed_q_rad",vectorJson(initial)},{"seed_source",index?"FIXED_RNG_NATIVE14D":(name=="start"?"SRDF_HOME_SEED_ONLY":"ACCEPTED_START_SEED_ONLY")},
        {"target_cube_world",target},{"kdl",Json::array()},{"qualified",false}};
      p4::JointVector raw; bool solved=true;
      for(int side=0;side<2;++side)
      {
        KDL::JntArray in(7),out(7);for(int j=0;j<7;++j) in(j)=initial[side*7+j];
        const Eigen::Isometry3d desired=object*(side?gr_:gl_).inverse();
        const int code=solvers_[side]->CartToJnt(in,kdlFrame(desired),out);
        for(int j=0;j<7;++j) raw[side*7+j]=out(j);
        row["kdl"].push_back({{"side",side?"right":"left"},{"return_code",code},
          {"iterations",solvers_[side]->lastNrOfIter},{"position_difference_m",solvers_[side]->lastTransDiff},
          {"rotation_difference_rad",solvers_[side]->lastRotDiff},{"desired_tcp_world",poseJson(desired)}});
        solved=solved&&code==0;
      }
      row["raw_q_rad"]=vectorJson(raw); row["reason"]="IK_FAILURE";
      if(solved && raw.allFinite())
      {
        row["raw_native_joint_margin_rad"]=model_.minimumJointMargin(raw);
        row["raw_closure"]=residualJson(evaluate(raw).residual);
        if(model_.minimumJointMargin(raw)<0.) row["reason"]="RAW_NATIVE_JOINT_LIMIT";
        else
        {
          const auto projection=p4::project(raw,[&](const auto& q){return evaluate(q);},
            [&](const auto& q){return model_.minimumJointMargin(q);},local_.projection);
          row["projection"]=projectionJson(projection);
          if(projection.status!=p4::ProjectionStatus::CONVERGED) row["reason"]="PROJECTION_FAILURE";
          else if((projection.projected_q-raw).norm()>ik_.at("endpoint_projection_correction_l2_limit_rad").get<double>() ||
            (projection.projected_q-raw).cwiseAbs().maxCoeff()>ik_.at("endpoint_projection_correction_linf_limit_rad").get<double>())
            row["reason"]="ENDPOINT_PROJECTION_JUMP";
          else
          {
            const auto q=projection.projected_q;const auto c=evaluate(q);const auto a=model_.sample(q);
            Json checks=Json::array();bool target_ok=true;
            for(int side=0;side<2;++side)
            {
              const Eigen::Isometry3d tcp=side?a.second.world_tcp:a.first.world_tcp;
              const Eigen::Isometry3d cube=side?c.right_object:c.left_object;
              const Eigen::Isometry3d desired=object*(side?gr_:gl_).inverse();
              KDL::JntArray joints(7);for(int j=0;j<7;++j) joints(j)=q[side*7+j];
              KDL::Frame native;KDL::ChainFkSolverPos_recursive fk(chains_[side]);
              if(fk.JntToCart(joints,native)!=0 ||
                (eigenFrame(native).matrix()-tcp.matrix()).cwiseAbs().maxCoeff()>ik_.at("model_fk_crosscheck_max_abs").get<double>() ||
                (fcl_.linkPose(q,std::string(side?"right":"left")+"_fr3_side_suction_tcp").matrix()-tcp.matrix()).cwiseAbs().maxCoeff()>1e-12)
                throw std::runtime_error("Original KDL/MoveIt/FCL FK mismatch; STOP");
              const auto error=[&](const Eigen::Isometry3d& p,const Eigen::Isometry3d& d){
                return Json{{"position_m",(p.translation()-d.translation()).norm()},
                  {"rotation_rad",common_geometry::so3Log(d.linear().transpose()*p.linear()).norm()}};};
              const auto te=error(tcp,desired),oe=error(cube,object);
              checks.push_back({{"side",side?"right":"left"},{"tcp_world",poseJson(tcp)},
                {"predicted_cube_world",poseJson(cube)},{"tcp_target_error",te},{"cube_target_error",oe}});
              for(const auto& e:{te,oe}) target_ok=target_ok&&e.at("position_m").get<double>()<=ik_.at("endpoint_pose_tolerance_m").get<double>() &&
                e.at("rotation_rad").get<double>()<=ik_.at("endpoint_pose_tolerance_rad").get<double>();
            }
            row["actual14q_offline_rad"]=vectorJson(q);row["target_checks"]=checks;
            row["closure"]=residualJson(c.residual); row["minimum_native_joint_margin_rad"]=model_.minimumJointMargin(q);
            const auto collision=fcl_.check(q);row["collision"]=collisionJson(collision);
            const bool valid=target_ok&&model_.minimumJointMargin(q)>=0. &&
              c.residual.head<3>().norm()<=local_.projection.position_tolerance_m &&
              c.residual.tail<3>().norm()<=local_.projection.rotation_tolerance_rad &&
              collision.complete&&!collision.self_collision&&!collision.world_collision&&collision.contacts.empty();
            row["qualified"]=valid; row["reason"]=valid?"FULLY_QUALIFIED_NOMINAL_OFFLINE_ENDPOINT":
              (!target_ok?"ABSOLUTE_TARGET_REJECTED":(!collision.complete?"FCL_INCOMPLETE":
                (collision.self_collision||collision.world_collision?"NATIVE_FCL_COLLISION":"CLOSURE_OR_LIMIT_REJECTED")));
          }
        }
      }
      row["compute_wall_time_sec"]=std::chrono::duration<double>(Clock::now()-begin).count();
      // 超时返回候选也拒绝，不能靠循环入口检查越过端点预算。
      if(row["compute_wall_time_sec"].get<double>()>ik_.at("max_compute_wall_sec_per_endpoint").get<double>())
      {row["qualified"]=false;row["reason"]="ENDPOINT_TIME_BUDGET";}
      log<<row.dump()<<'\n';log.flush();if(!log) throw std::runtime_error("Candidate logging failed");
      summary["candidates"]=index+1;summary["rng_draws"]=draws;
      if(row.at("qualified").get<bool>())
      {
        const auto values=row.at("actual14q_offline_rad").get<std::vector<double>>();
        const p4::JointVector q=Eigen::Map<const p4::JointVector>(values.data());
        row["joint_names"]=model_.jointNames();row["left7q_rad"]=vectorJson(q.head<7>());
        row["right7q_rad"]=vectorJson(q.tail<7>());row["qualification"]="OFFLINE_CONSTRUCTED_NOT_HISTORICAL_PHYSICAL_MEASUREMENT";
        write(output_/(name+"_endpoint.json"),row);
        summary["qualified"]=true;summary["termination"]="FIRST_QUALIFIED_PAIR";
        summary["compute_wall_time_sec"]=std::chrono::duration<double>(Clock::now()-begin).count();
        write(output_/(name+"_summary.json"),summary);return q;
      }
      if(row.at("reason")=="ENDPOINT_TIME_BUDGET") {summary["termination"]="ENDPOINT_TIME_BUDGET";break;}
    }
    if(!summary.contains("termination")) summary["termination"]="CANDIDATE_PAIR_BUDGET_EXHAUSTED";
    summary["compute_wall_time_sec"]=std::chrono::duration<double>(Clock::now()-begin).count();
    write(output_/(name+"_summary.json"),summary);return std::nullopt;
  }
private:
  task03_offline::DualFr3Model& model_;CollisionAdapter& fcl_;Json ik_;
  p4::LocalConnectionOptions local_;Eigen::Isometry3d gl_,gr_;std::filesystem::path output_;
  KDL::Tree tree_;std::array<KDL::Chain,2> chains_;
  std::array<std::unique_ptr<KDL::ChainIkSolverPos_LMA>,2> solvers_;
};
void run(const std::string& protocol,const std::filesystem::path& output,Json& report)
{
  const auto config=Json::parse(read(protocol)),audit=Json::parse(read((output/"source_audit.json").string()));
  if(!audit.at("model_checks").at("urdf").at("xml_structure_and_all_numeric_fields_equal").get<bool>() ||
     !audit.at("model_checks").at("srdf").at("xml_structure_and_all_numeric_fields_equal").get<bool>() ||
     audit.at("source_scenario")!=config.at("source_scenario")) throw std::runtime_error("Source gate failed");
  const auto scene=audit.at("scene_input");const auto urdf=read(config.at("urdf")),srdf=read(config.at("srdf"));
  const Eigen::Isometry3d gl=pose(audit.at("nominal_object_to_tcp").at("left")).inverse();
  const Eigen::Isometry3d gr=pose(audit.at("nominal_object_to_tcp").at("right")).inverse();
  task03_offline::DualFr3Model model(urdf,srdf);CollisionAdapter fcl(urdf,srdf,config.at("geometry_archive"),gl);
  if(Json(model.jointNames())!=audit.at("joint_names")) throw std::runtime_error("Joint order differs");
  const auto bounds=model.positionBounds();
  for(int i=0;i<14;++i)
  {
    const auto lim=audit.at("constants").at("FR3_OFFICIAL_JOINT_LIMITS_RAD").at(std::to_string(i%7+1));
    if(bounds.first[i]!=lim.at(0).get<double>()||bounds.second[i]!=lim.at(1).get<double>())
      throw std::runtime_error("Native bounds differ");
  }
  write(output/"native_world_readback.json",fcl.worldReadback());write(output/"native_manifest.json",fcl.manifest());
  verifyWorld(fcl,scene,config);report["world_source_readback_gate"]="PASS";
  // 同一次软件回归核对可选输入没有改写历史默认四对象/原附着身份。不查历史端点。
  CollisionAdapter legacy(urdf,srdf,"results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml",gl);
  std::set<std::string> old_ids;for(const auto& r:legacy.worldReadback()) old_ids.insert(r.at("id").get<std::string>());
  if(old_ids!=std::set<std::string>{"table","carriage_deep_wall","carriage_minus_y_wall","carriage_plus_y_wall"} ||
     legacy.manifest().at("attachment").at("id")!="task05_shared_cube") throw std::runtime_error("Legacy defaults changed");
  write(output/"legacy_default_world_regression.json",{{"status","PASS"},{"manifest",legacy.manifest()},
    {"readback",legacy.worldReadback()},{"collision_queries",0}});
  const auto l=local(Json::parse(read(config.at("local_protocol"))));Endpoints endpoints(model,fcl,urdf,config,l,gl,gr,output);
  report["failure_stage"]="START_ENDPOINT_CONSTRUCTION";
  const auto start=endpoints.construct("start",scene.at("nominal_endpoints").at("start"),home(urdf,srdf,model.jointNames()));
  if(!start) {report["reason"]="Bounded nominal START construction failed; no goal/search dispatched";return;}
  report["failure_stage"]="GOAL_ENDPOINT_CONSTRUCTION";
  const auto goal=endpoints.construct("goal",scene.at("nominal_endpoints").at("goal"),*start);
  if(!goal) {report["reason"]="Bounded nominal GOAL construction failed; no search dispatched";return;}
  report["endpoint_gate"]="PASS";report["failure_stage"]="P4_SEARCH";
  const auto evaluate=[&](const auto& q){return endpoints.evaluate(q);};
  const auto margin=[&](const auto& q){return model.minimumJointMargin(q);};
  const auto collision=[&](const auto& q){return fcl.check(q);};
  const auto planner=Json::parse(read(config.at("planner_protocol")));
  for(const auto& seed_json:config.at("planner_seeds"))
  {
    const std::uint64_t seed=seed_json; report["planning_calls"]=report.at("planning_calls").get<int>()+1;
    const auto result=p4::plan(*start,*goal,bounds.first,bounds.second,evaluate,margin,collision,options(planner,l,seed));
    const auto file="planner_seed"+std::to_string(seed)+".json";write(output/file,task06_offline::plannerJson(result));
    report["trials"].push_back({{"seed",seed},{"artifact",file},{"status",p4::statusName(result.status)},
      {"reason",result.reason},{"nodes",result.start_tree.size()+result.goal_tree.size()},
      {"path_edges",result.path_edges.size()},{"path_points",result.dense_path.size()},
      {"wall_sec",result.compute_wall_time_sec},{"counters",task06_offline::countersJson(result.counters)},
      {"metrics",result.path_metrics?task06_offline::pathMetricsJson(*result.path_metrics):Json(nullptr)}});
    std::cout<<"seed="<<seed<<" status="<<p4::statusName(result.status)<<" nodes="<<result.start_tree.size()+result.goal_tree.size()<<std::endl;
    if(result.status!=p4::PlannerStatus::SUCCESS) continue;
    report["failure_stage"]="INDEPENDENT_PATH_VALIDATION";Json checks=Json::array();
    bool valid=!result.dense_path.empty() && (result.dense_path.front()-*start).norm()==0. && (result.dense_path.back()-*goal).norm()==0.;
    for(std::size_t i=0;i<result.dense_path.size();++i)
    {
      const auto& q=result.dense_path[i];const auto c=evaluate(q);const auto hit=collision(q);
      const double step=i?(q-result.dense_path[i-1]).norm():0.,maxstep=i?(q-result.dense_path[i-1]).cwiseAbs().maxCoeff():0.;
      const bool ok=c.residual.head<3>().norm()<=l.projection.position_tolerance_m &&
        c.residual.tail<3>().norm()<=l.projection.rotation_tolerance_rad && margin(q)>=0. && hit.complete&&
        !hit.self_collision&&!hit.world_collision&&hit.contacts.empty() && step<=l.adjacent_l2_limit_rad && maxstep<=l.adjacent_max_abs_limit_rad;
      valid=valid&&ok;checks.push_back({{"index",i},{"q_rad",vectorJson(q)},{"closure",residualJson(c.residual)},
        {"native_joint_margin_rad",margin(q)},{"adjacent_l2_rad",step},{"adjacent_max_abs_rad",maxstep},
        {"collision",collisionJson(hit)},{"qualified",ok}});
    }
    // 解路径每条树边的来源必须是原 TASK05 CONNECTED；不只复核节点。
    for(const auto& edge:result.path_edges)
    {const auto& attempt=result.attempts.at(edge.attempt);
     valid=valid&&attempt.status==p4::AttemptStatus::ACCEPTED && attempt.connection && attempt.connection->status==p4::ConnectionStatus::CONNECTED;}
    write(output/"independent_path_validation.json",{{"qualified",valid},{"states",checks},
      {"path_edges",task06_offline::pathEdgesJson(result.path_edges)},{"continuous_collision_certificate",false}});
    if(!valid) {report["reason"]="Returned path failed independent qualification; STOP";return;}
    write(output/"qualified_joint_path.json",{{"joint_names",model.jointNames()},{"q_rad",task06_offline::jointArrayJson(result.dense_path)},
      {"qualification","OFFLINE_DISCRETE_KINEMATIC_PATH_NOT_TIME_TRAJECTORY_OR_PHYSICAL_CERTIFICATE"}});
    report["qualified_path_count"]=1;report["task06_is_a_status"]="PASS_CANDIDATE_OFFLINE_ADAPTATION_ONLY";
    report["failure_stage"]=nullptr;report["reason"]="First source-consistent qualified nominal path; STOP";return;
  }
  report["reason"]="Fixed planner seed budget exhausted; endpoints not reselected";
}
}
int main(int argc,char** argv)
{
  Json report={{"schema","task06_is_a.nominal_stage2.v2"},{"task06_is_a_status","PARTIAL"},
    {"planning_calls",0},{"qualified_path_count",0},{"trials",Json::array()},
    {"simulation_time",nullptr},{"physics_step",nullptr},{"execution_commands",0},
    {"physical_measurement",false},{"minimum_collision_distance_m",nullptr},
    {"minimum_collision_distance_status","UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED"},
    {"benchmark_frozen",false},{"continuous_collision_certificate",false}};
  if(argc!=3) {std::cerr<<"Usage: nominal_planning PROTOCOL EXISTING_RUN_DIRECTORY\n";return 2;}
  try {run(argv[1],argv[2],report);}
  catch(const std::exception& e) {report["error"]=e.what();report["reason"]="Engineering failure; STOP without scientific retry";}
  try {write(std::filesystem::path(argv[2])/"planning_summary.json",report);}
  catch(const std::exception& e) {std::cerr<<e.what()<<std::endl;return 2;}
  std::cout<<report.dump(2)<<std::endl;
  return report.contains("error")?2:(report.at("qualified_path_count")==1?0:1);
}
