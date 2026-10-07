// [ENGINEERING] 完整单 Cube 离散几何链：START→PRE_PUSH→TARGET。
// 不发 ROS 控制命令、不运行 Isaac；不是带时间的运动轨迹或连续碰撞证书。
#include "geometry_common.hpp"

namespace
{
constexpr double kStep = .002;
constexpr double kEpsilon = 1e-7;
constexpr double kOrientationWeight = .01;
constexpr double kTranslationAcceptance = 1e-5;
constexpr double kRotationAcceptance = 1e-4;

struct EnvironmentBox
{
  std::string name;
  Eigen::Vector3d center;
  Eigen::Vector3d size;
};

Json rigidPose(const Eigen::Isometry3d& t)
{
  const Eigen::Quaterniond q(t.linear());
  return {{"translation_m",xyz(t.translation())},
          {"quaternion_xyzw",Json::array({q.x(),q.y(),q.z(),q.w()})}};
}

void requireIdentity(const YAML::Node& q,const std::string& field)
{
  if (!q.IsSequence() || q.size()!=4 || q[0].as<double>()!=0. ||
      q[1].as<double>()!=0. || q[2].as<double>()!=0. || q[3].as<double>()!=1.)
    throw std::runtime_error("This approved probe requires identity orientation: "+field);
}

Json cubeEnvironment(const Eigen::Vector3d& center,const Eigen::Vector3d& size,
                     const std::vector<EnvironmentBox>& environment)
{
  // 名义 Cube 和四个环境盒均轴对齐，此处补齐 FCL 未覆盖的 world/world 几何。
  // 1e-12 仅吸收浮点舍入；不放宽机器人碰撞/IK 验收，不把相交当净空。
  Json checks=Json::array(); bool penetration=false;
  for (const auto& env:environment)
  {
    const Eigen::Vector3d overlap=.5*(size+env.size)-(center-env.center).cwiseAbs();
    const bool volume=(overlap.array()>1e-12).all();
    const bool touching=!volume && (overlap.array()>=-1e-12).all();
    const Eigen::Vector3d gaps=(-overlap).cwiseMax(0.);
    double distance=volume ? -overlap.minCoeff():gaps.norm();
    if (touching) distance=0.;
    checks.push_back({{"body1","shared_cube"},{"body2",env.name},
      {"signed_axis_aligned_distance_m",distance},{"overlap_xyz_m",xyz(overlap)},
      {"volumetric_penetration",volume},{"classification",volume ? "PENETRATION":touching ? "TOUCH":"FREE"}});
    penetration=penetration || volume;
  }
  return {{"status",penetration ? "FAIL":"PASS"},{"method","identity-oriented exact nominal box AABB"},
          {"floating_roundoff_m",1e-12},{"checks",checks}};
}

std::string pairClass(const std::string& a,const std::string& b,const bool self)
{
  const auto is_world=[](const std::string& name) {
    return name=="table" || name=="shared_cube" || name.rfind("carriage_",0)==0;
  };
  if (is_world(a) || is_world(b)) return "ROBOT_WORLD";
  if ((a.rfind("left_",0)==0 && b.rfind("right_",0)==0) ||
      (a.rfind("right_",0)==0 && b.rfind("left_",0)==0)) return "INTER_ARM";
  if (!self && a.rfind("left_",0)!=0 && a.rfind("right_",0)!=0 &&
      b.rfind("left_",0)!=0 && b.rfind("right_",0)!=0) return "ROBOT_WORLD";
  return "SELF";
}

Json contactList(const collision_detection::CollisionResult& result,const bool self)
{
  Json pairs=Json::array();
  for (const auto& entry:result.contacts) for (const auto& hit:entry.second)
    pairs.push_back({{"body1",entry.first.first},{"body2",entry.first.second},
      {"type",pairClass(entry.first.first,entry.first.second,self ||
        (hit.body_type_1==collision_detection::BodyType::ROBOT_LINK &&
         hit.body_type_2==collision_detection::BodyType::ROBOT_LINK))},
      {"depth_m",hit.depth},{"position_world_m",xyz(hit.pos)}});
  return pairs;
}

Json distanceData(const collision_detection::DistanceResultsData& d,const bool self)
{
  if (!std::isfinite(d.distance) || d.link_names[0].empty() || d.link_names[1].empty() ||
      !d.nearest_points[0].allFinite() || !d.nearest_points[1].allFinite())
    throw std::runtime_error("FCL did not return a finite distance/pair");
  return {{"signed_distance_m",d.distance},{"body1",d.link_names[0]},{"body2",d.link_names[1]},
    {"type",pairClass(d.link_names[0],d.link_names[1],self)},
    {"nearest_point_1_world_m",xyz(d.nearest_points[0])},
    {"nearest_point_2_world_m",xyz(d.nearest_points[1])}};
}

bool criticalLink(const std::string& name)
{
  return name.find("link7")!=std::string::npos || name.find("link8")!=std::string::npos ||
         name.find("side_suction")!=std::string::npos;
}

bool nominalEnvironment(const std::string& name)
{
  return name=="table" || name.rfind("carriage_",0)==0;
}

Json checkState(const State& state,planning_scene::PlanningScene& scene,
                const Group* left,const Group* right,const std::string& lt,const std::string& rt,
                const Eigen::Isometry3d& object,const Eigen::Isometry3d& gl,const Eigen::Isometry3d& gr,
                const std::vector<EnvironmentBox>& environment,const Eigen::Vector3d& cube_size,Json& row)
{
  // 调用者预先保存 state 上下文，本函数逐项写入；distance 错误不能丢失碰撞证据。
  std::vector<double> lq,rq;
  state.copyJointGroupPositions(left,lq); state.copyJointGroupPositions(right,rq);
  row["left_q_rad"]=lq; row["right_q_rad"]=rq;
  row["joint_limit"]=state.satisfiesBounds() ? "PASS":"FAIL";
  row["min_joint_margin_rad"]=std::min(margin(state,left),margin(state,right));
  row["joint_margins"]=Json::array();
  for (const auto* group:{left,right}) for (const auto& name:group->getVariableNames())
  {
    const auto& bound=state.getRobotModel()->getVariableBounds(name);
    const double q=state.getVariablePosition(name);
    row["joint_margins"].push_back({{"joint",name},{"position_rad",q},
      {"lower_rad",bound.min_position_},{"upper_rad",bound.max_position_},
      {"margin_rad",std::min(q-bound.min_position_,bound.max_position_-q)}});
  }
  row["left_relative_grasp_error"]=residual(state,lt,object*gl);
  row["right_relative_grasp_error"]=residual(state,rt,object*gr);
  const Eigen::Isometry3d relative_actual=state.getGlobalLinkTransform(lt).inverse()*state.getGlobalLinkTransform(rt);
  const Eigen::Isometry3d relative_target=gl.inverse()*gr;
  row["inter_tcp_closure_error"]={{"translation_m",(relative_actual.translation()-relative_target.translation()).norm()},
    {"rotation_rad",Eigen::AngleAxisd(relative_target.linear().transpose()*relative_actual.linear()).angle()}};
  row["link_world_poses"]=Json::object();
  for (const auto* link:state.getRobotModel()->getLinkModels())
    row["link_world_poses"][link->getName()]=rigidPose(state.getGlobalLinkTransform(link));

  collision_detection::CollisionRequest request;
  request.contacts=true; request.max_contacts=1000; request.max_contacts_per_pair=3;
  collision_detection::CollisionResult self,world;
  scene.getCollisionEnv()->checkSelfCollision(request,self,state,scene.getAllowedCollisionMatrix());
  scene.getCollisionEnv()->checkRobotCollision(request,world,state,scene.getAllowedCollisionMatrix());
  row["self_and_inter_arm_collision_pairs"]=contactList(self,true);
  row["robot_world_collision_pairs"]=contactList(world,false);
  row["collision_pairs"]=row["self_and_inter_arm_collision_pairs"];
  for (const auto& hit:row["robot_world_collision_pairs"]) row["collision_pairs"].push_back(hit);
  row["self_and_inter_arm_fcl"]=self.collision ? "FAIL":"PASS";
  row["robot_world_fcl"]=world.collision ? "FAIL":"PASS";
  row["fcl"]=(self.collision || world.collision) ? "FAIL":"PASS";

  // SINGLE 保存每个 body-pair 的最小距离；完整有效 ACM 原样用于 self 和 world。
  collision_detection::DistanceRequest dr;
  dr.type=collision_detection::DistanceRequestType::SINGLE;
  dr.enable_signed_distance=true; dr.enable_nearest_points=true;
  dr.acm=&scene.getAllowedCollisionMatrix();
  collision_detection::DistanceResult sd,wd;
  scene.getCollisionEnv()->distanceSelf(dr,sd,state);
  scene.getCollisionEnv()->distanceRobot(dr,wd,state);
  row["minimum_self_and_inter_arm_fcl_distance"]=distanceData(sd.minimum_distance,true);
  row["minimum_robot_world_fcl_distance"]=distanceData(wd.minimum_distance,false);
  row["minimum_fcl_distance"] = sd.minimum_distance.distance<=wd.minimum_distance.distance ?
    row["minimum_self_and_inter_arm_fcl_distance"]:row["minimum_robot_world_fcl_distance"];
  row["fcl_distance_collision_consistency"]={{"self_check_collision",self.collision},
    {"self_distance_collision",sd.collision},{"world_check_collision",world.collision},
    {"world_distance_collision",wd.collision},{"status","PASS"}};
  if (sd.collision!=self.collision || wd.collision!=world.collision ||
      (sd.minimum_distance.distance<0. && !self.collision) ||
      (wd.minimum_distance.distance<0. && !world.collision) ||
      (self.collision && sd.minimum_distance.distance>0.) ||
      (world.collision && wd.minimum_distance.distance>0.))
  {
    row["fcl_distance_collision_consistency"]["status"]="ERROR";
    throw std::runtime_error("FCL distance/checkCollision contradiction; rejected without tolerance");
  }
  row["wrist_tool_environment_distances"]=Json::array();
  std::optional<Json> environment_min,critical_min,inter_arm_min;
  for (const auto& entry:wd.distances) for (const auto& d:entry.second)
  {
    const bool environment_pair=nominalEnvironment(d.link_names[0]) || nominalEnvironment(d.link_names[1]);
    if (!environment_pair) continue;
    const auto item=distanceData(d,false);
    if (!environment_min || d.distance<(*environment_min)["signed_distance_m"].get<double>()) environment_min=item;
    if (criticalLink(d.link_names[0]) || criticalLink(d.link_names[1]))
    {
      row["wrist_tool_environment_distances"].push_back(item);
      if (!critical_min || d.distance<(*critical_min)["signed_distance_m"].get<double>()) critical_min=item;
    }
  }
  for (const auto& entry:sd.distances) for (const auto& d:entry.second)
    if (pairClass(d.link_names[0],d.link_names[1],true)=="INTER_ARM" &&
        (!inter_arm_min || d.distance<(*inter_arm_min)["signed_distance_m"].get<double>()))
      inter_arm_min=distanceData(d,true);
  if (!environment_min || !critical_min || !inter_arm_min)
    throw std::runtime_error("Missing full-pair FCL distance coverage");
  row["minimum_robot_environment_excluding_cube_fcl_distance"]=*environment_min;
  row["minimum_wrist_tool_environment_fcl_distance"]=*critical_min;
  row["minimum_inter_arm_fcl_distance"]=*inter_arm_min;
  row["cube_environment_geometry"]=cubeEnvironment(object.translation(),cube_size,environment);
  bool grasp=true;
  for (const auto arm:{"left","right"})
  {
    const auto& error=row[std::string(arm)+"_relative_grasp_error"];
    grasp=grasp && error["translation_m"].get<double>()<=kTranslationAcceptance &&
      error["rotation_rad"].get<double>()<=kRotationAcceptance;
  }
  row["shared_grasp_acceptance"]=grasp ? "PASS":"FAIL";
  row["status"]=(row["joint_limit"]=="PASS" && grasp && !self.collision && !world.collision &&
    row["cube_environment_geometry"]["status"]=="PASS") ? "PASS_DISCRETE_GEOMETRY":"FAIL_STOP";
  return row;
}

Json summarize(const Json& rows,const std::string& segment,const int planned,const bool overall_error)
{
  Json s={{"segment",segment},{"states_checked",0},{"states_passed",0},
    {"planned_states",planned},{"complete_segment_checked",false},
    {"status","NOT_RUN"},{"minimum_joint_margin_rad",nullptr},
    {"max_grasp_translation_m",0.},{"max_grasp_rotation_rad",0.},
    {"minimum_fcl_distance",nullptr},{"minimum_wrist_tool_environment_fcl_distance",nullptr},
    {"cube_environment_checks",0},{"cube_environment_penetrations",0},{"collision_pairs",Json::array()}};
  bool failed=false;
  for (const auto& row:rows)
  {
    if (row["segment"]!=segment) continue;
    s["states_checked"]=s["states_checked"].get<int>()+1;
    if (row["status"]=="PASS_DISCRETE_GEOMETRY") s["states_passed"]=s["states_passed"].get<int>()+1;
    else failed=true;
    if (row.contains("min_joint_margin_rad") && (s["minimum_joint_margin_rad"].is_null() ||
        row["min_joint_margin_rad"].get<double>()<s["minimum_joint_margin_rad"].get<double>()))
      s["minimum_joint_margin_rad"]=row["min_joint_margin_rad"];
    for (const auto arm:{"left","right"})
    {
      const auto key=std::string(arm)+"_relative_grasp_error";
      if (!row.contains(key)) continue;
      s["max_grasp_translation_m"]=std::max(s["max_grasp_translation_m"].get<double>(),row[key]["translation_m"].get<double>());
      s["max_grasp_rotation_rad"]=std::max(s["max_grasp_rotation_rad"].get<double>(),row[key]["rotation_rad"].get<double>());
    }
    for (const auto key:{"minimum_fcl_distance","minimum_wrist_tool_environment_fcl_distance"})
      if (row.contains(key) && (s[key].is_null() || row[key]["signed_distance_m"].get<double>()<s[key]["signed_distance_m"].get<double>()))
      {
        s[key]=row[key]; s[key]["state_index"]=row["state_index"];
        s[key]["segment_index"]=row["segment_index"];
        s[key]["cube_center_world_m"]=row["cube_center_world_m"];
      }
    if (row.contains("cube_environment_geometry")) for (const auto& check:row["cube_environment_geometry"]["checks"])
    {
      s["cube_environment_checks"]=s["cube_environment_checks"].get<int>()+1;
      if (check["volumetric_penetration"].get<bool>())
        s["cube_environment_penetrations"]=s["cube_environment_penetrations"].get<int>()+1;
    }
    if (row.contains("collision_pairs")) for (const auto& pair:row["collision_pairs"]) s["collision_pairs"].push_back(pair);
  }
  const int checked=s["states_checked"].get<int>();
  s["complete_segment_checked"]=planned>0 && checked==planned;
  if (checked>0)
  {
    if (overall_error && checked<planned) s["status"]="INCOMPLETE_ERROR_STOP";
    else if (failed) s["status"]=overall_error ? "ERROR_STOP":"FAIL_STOP";
    else if (planned>0 && checked==planned) s["status"]="PASS_SAMPLED_SEGMENT";
    else s["status"]="INCOMPLETE_STOP";
  }
  return s;
}
} // namespace

int main(int argc,char** argv)
{
  if (argc!=6)
  {
    std::cerr<<"usage: full_chain_probe benchmark.yaml robot.urdf robot.srdf kinematics.yaml output-dir\n";
    return 2;
  }
  const std::filesystem::path output(argv[5]);
  if (std::filesystem::exists(output/"full_chain_results.json") || std::filesystem::exists(output/"state_records.json"))
  { std::cerr<<"Refusing to overwrite prior run\n"; return 2; }
  std::filesystem::create_directories(output);
  Json rows=Json::array();
  Json current_state_context;
  bool current_state_pending=false;
  Json summary={{"scope","single_cube_core_benchmark"},{"status","ERROR"},
    {"scientific_classification","ENGINEERING"},{"physics_started",false},{"robot_commands",0},
    {"suction_commands",0},{"acm_modified",false},{"kinematic_timed_trajectory",false},
    {"continuous_collision_certificate",false},{"benchmark_frozen",false},
    {"state_timestamp_policy","geometry_index_only_not_simulation_time"},
    {"max_cube_translation_step_m",kStep},{"start_joint_state_is_candidate_not_frozen",true},
    {"seed_policy","original deterministic64 per-arm,retain12; then previous-q one-shot continuation"}};
  int exit_code=2;
  std::ofstream distance_csv(output/"per_state_minimum_fcl_distance.csv");
  distance_csv<<"state_index,segment,segment_index,cube_x_m,cube_y_m,cube_z_m,category,signed_distance_m,body1,body2\n";
  distance_csv<<std::setprecision(17);
  rclcpp::init(argc,argv);
  try
  {
    const auto config=YAML::LoadFile(argv[1]),kin=YAML::LoadFile(argv[4]);
    if (config["cube"]["count"].as<int>()!=1 || config["frames"]["world"].as<std::string>()!="world")
      throw std::runtime_error("Not a one-Cube world-frame candidate");
    const auto numeric=config["task01_validation"]["geometry_probe_numeric"];
    for (const auto& value:std::vector<std::pair<std::string,double>>{
      {"lma_epsilon",kEpsilon},{"orientation_vs_position",kOrientationWeight},
      {"translation_acceptance_m",kTranslationAcceptance},{"rotation_acceptance_rad",kRotationAcceptance},
      {"max_cube_translation_step_m",kStep}})
      if (!numeric[value.first] || numeric[value.first].as<double>()!=value.second)
        throw std::runtime_error("Unapproved probe numerical value: "+value.first);
    const auto a=config["benchmarks"]["A_tight_transport"],b=config["benchmarks"]["B_constrained_insertion"];
    requireIdentity(a["initial_orientation_xyzw"],"A.initial_orientation_xyzw");
    requireIdentity(a["target_orientation_xyzw"],"A.target_orientation_xyzw");
    requireIdentity(b["start_orientation_xyzw"],"B.start_orientation_xyzw");
    requireIdentity(b["target_orientation_xyzw"],"B.target_orientation_xyzw");
    const auto start=vec(a["initial_cube_center_world_m"]),pre=vec(a["target_cube_center_world_m"]),goal=vec(b["target_cube_center_world_m"]);
    if ((pre-vec(b["start_cube_center_world_m"])).norm()>1e-12)
      throw std::runtime_error("A/B PRE_PUSH mismatch");
    if ((start-Eigen::Vector3d(.55,0.,.38)).norm()>1e-12 ||
        (pre-Eigen::Vector3d(.79,0.,.26)).norm()>1e-12 || (goal-Eigen::Vector3d(1.1,0.,.26)).norm()>1e-12)
      throw std::runtime_error("Pose differs from user-approved single-Cube candidate");
    std::vector<rclcpp::Parameter> params={rclcpp::Parameter("robot_description",readText(argv[2])),
      rclcpp::Parameter("robot_description_semantic",readText(argv[3]))};
    for (const std::string arm:{"left_arm","right_arm"})
    {
      if (kin[arm]["kinematics_solver"].as<std::string>()!="lma_kinematics_plugin/LMAKinematicsPlugin")
        throw std::runtime_error("Full-chain probe requires the approved LMA plugin");
      for (const auto entry:kin[arm])
      {
        const auto key=entry.first.as<std::string>();
        if (key=="epsilon" || key=="orientation_vs_position") continue;
        for (const auto& prefix:{arm+".","robot_description_kinematics."+arm+"."})
          if (key=="kinematics_solver") params.emplace_back(prefix+key,entry.second.as<std::string>());
          else if (key=="max_solver_iterations") params.emplace_back(prefix+key,entry.second.as<int>());
          else if (key=="position_only_ik") params.emplace_back(prefix+key,entry.second.as<bool>());
          else params.emplace_back(prefix+key,entry.second.as<double>());
      }
      for (const auto& prefix:{arm+".","robot_description_kinematics."+arm+"."})
      {
        params.emplace_back(prefix+"epsilon",kEpsilon);
        params.emplace_back(prefix+"orientation_vs_position",kOrientationWeight);
      }
      summary["effective_ik_numeric"][arm]={{"plugin","lma_kinematics_plugin/LMAKinematicsPlugin"},
        {"epsilon",kEpsilon},{"orientation_vs_position",kOrientationWeight},
        {"max_solver_iterations",kin[arm]["max_solver_iterations"] ? kin[arm]["max_solver_iterations"].as<int>():500},
        {"position_only_ik",kin[arm]["position_only_ik"] ? kin[arm]["position_only_ik"].as<bool>():false},
        {"acceptance_translation_m",kTranslationAcceptance},{"acceptance_rotation_rad",kRotationAcceptance}};
      if (summary["effective_ik_numeric"][arm]["position_only_ik"].get<bool>())
        throw std::runtime_error("Position-only IK is forbidden for the fixed shared-grasp check");
    }
    auto node=std::make_shared<rclcpp::Node>("task01_full_single_cube_geometry",
      rclcpp::NodeOptions().parameter_overrides(params).automatically_declare_parameters_from_overrides(true)
      .enable_rosout(false).start_parameter_services(false).start_parameter_event_publisher(false));
    robot_model_loader::RobotModelLoader loader(node);
    const auto model=loader.getModel();
    if (!model) throw std::runtime_error("Robot model absent");
    const auto* left=model->getJointModelGroup("left_arm");
    const auto* right=model->getJointModelGroup("right_arm");
    if (!left || !right) throw std::runtime_error("Arm group absent");
    const auto lt=config["robots"]["left"]["tcp_link"].as<std::string>();
    const auto rt=config["robots"]["right"]["tcp_link"].as<std::string>();
    State previous(model); previous.setToDefaultValues();
    previous.setToDefaultValues(left,"home"); previous.setToDefaultValues(right,"home"); previous.update();
    for (const auto arm:{"left","right"})
      if ((previous.getGlobalLinkTransform(std::string(arm)+"_fr3_link0").translation()-
           vec(config["robots"][arm]["base_at_rest_world_m"])).norm()>1e-9)
        throw std::runtime_error("Model base differs from candidate; no hidden rail shift permitted");
    planning_scene::PlanningScene scene(model);
    moveit_msgs::msg::AllowedCollisionMatrix original_acm;
    scene.getAllowedCollisionMatrix().getMessage(original_acm);
    std::vector<EnvironmentBox> environment={{"table",vec(config["table"]["center_world_m"]),vec(config["table"]["size_m"])}};
    const auto c=config["carriage"];
    const double x0=c["interior_x_world_m"][0].as<double>(),x1=c["interior_x_world_m"][1].as<double>();
    const double y0=c["interior_y_world_m"][0].as<double>(),y1=c["interior_y_world_m"][1].as<double>();
    const double t=c["wall_thickness_m"].as<double>(),h=c["wall_height_m"].as<double>();
    const double z=c["wall_top_world_z_m"].as<double>()-h/2.;
    environment.push_back({"carriage_deep_wall",{x1+t/2.,(y0+y1)/2.,z},{t,y1-y0+2*t,h}});
    environment.push_back({"carriage_minus_y_wall",{(x0+x1)/2.,y0-t/2.,z},{x1-x0+2*t,t,h}});
    environment.push_back({"carriage_plus_y_wall",{(x0+x1)/2.,y1+t/2.,z},{x1-x0+2*t,t,h}});
    for (const auto& env:environment) box(scene,env.name,env.center,env.size);
    const auto gl=transform(config["shared_grasp"]["object_to_left_tcp_candidate"]);
    const auto gr=transform(config["shared_grasp"]["object_to_right_tcp_candidate"]);
    const auto cube_size=vec(config["cube"]["size_m"]);
    const int transport_steps=static_cast<int>(std::ceil((pre-start).norm()/kStep));
    const int insertion_steps=static_cast<int>(std::ceil((goal-pre).norm()/kStep));
    summary["planned_state_counts"]={{"A_tight_transport",transport_steps+1},{"B_constrained_insertion",insertion_steps+1},
      {"unique_chain_states",transport_steps+insertion_steps+1},{"shared_pre_push_duplicate_records",1}};
    summary["translation_step_m"]={{"A",(pre-start).norm()/transport_steps},{"B",(goal-pre).norm()/insertion_steps}};
    bool failed=false;
    const auto begin_state=[&](const std::string& segment,const int index,const double fraction,
                               const Eigen::Isometry3d& object,const State& state,const bool accepted_ik)
    {
      std::vector<double> lq,rq;
      state.copyJointGroupPositions(left,lq); state.copyJointGroupPositions(right,rq);
      current_state_context={{"state_index",rows.size()},{"segment",segment},{"segment_index",index},
        {"segment_fraction",fraction},{"cube_center_world_m",xyz(object.translation())},
        {"cube_orientation_xyzw",Json::array({0.,0.,0.,1.})},{"left_q_rad",lq},{"right_q_rad",rq},
        {"q_context_role",accepted_ik ? "ACCEPTED_IK_STATE_TO_BE_CHECKED":"PREVIOUS_Q_OR_START_SEED_NOT_YET_ACCEPTED"}};
      current_state_pending=true;
    };
    const auto append=[&](Json row,const std::string& segment,const int index,const double fraction,
                          const Eigen::Isometry3d& object)
    {
      row["state_index"]=rows.size(); row["segment"]=segment; row["segment_index"]=index;
      row["segment_fraction"]=fraction; row["cube_center_world_m"]=xyz(object.translation());
      row["cube_orientation_xyzw"]=Json::array({0.,0.,0.,1.});
      for (const auto key:{"minimum_fcl_distance","minimum_self_and_inter_arm_fcl_distance",
        "minimum_inter_arm_fcl_distance","minimum_robot_world_fcl_distance",
        "minimum_robot_environment_excluding_cube_fcl_distance","minimum_wrist_tool_environment_fcl_distance"})
        if (row.contains(key))
        {
          const auto& d=row[key];
          distance_csv<<row["state_index"]<<','<<segment<<','<<index<<','<<object.translation().x()<<','
            <<object.translation().y()<<','<<object.translation().z()<<','<<key<<','
            <<d["signed_distance_m"]<<','<<d["body1"].get<std::string>()<<','<<d["body2"].get<std::string>()<<'\n';
        }
      rows.push_back(row);
      current_state_pending=false;
      std::cout<<segment<<" state="<<index<<" fraction="<<fraction<<" "<<row["status"]<<std::endl;
      if (row["status"]!="PASS_DISCRETE_GEOMETRY") { failed=true; std::cout<<row.dump()<<std::endl; }
    };

    // START 的有限候选枚举只选第一个完整 FCL 合法的双臂状态；随后不换构型。
    Eigen::Isometry3d object=Eigen::Isometry3d::Identity(); object.translation()=start;
    begin_state("A_tight_transport",0,0.,object,previous,false);
    box(scene,"shared_cube",start,cube_size);
    Json ld,rd,start_row;
    const auto ls=solutions(previous,left,lt,object*gl,64,12,&ld);
    const auto rs=solutions(previous,right,rt,object*gr,64,12,&rd);
    summary["start_ik_seed_diagnostics"]={{"left",ld},{"right",rd}};
    summary["start_paired_candidates"]=Json::array();
    bool selected=false;
    for (const auto& l:ls)
    {
      if (selected) break;
      for (const auto& r:rs)
      {
        State candidate(previous); std::vector<double> lq,rq;
        l.copyJointGroupPositions(left,lq); r.copyJointGroupPositions(right,rq);
        candidate.setJointGroupPositions(left,lq); candidate.setJointGroupPositions(right,rq); candidate.update();
        collision_detection::CollisionRequest request; request.contacts=true;
        request.max_contacts=1000; request.max_contacts_per_pair=3;
        collision_detection::CollisionResult result; scene.checkCollision(request,result,candidate);
        Json pair={{"candidate_index",summary["start_paired_candidates"].size()},
          {"left_q_rad",lq},{"right_q_rad",rq},{"collision",result.collision},
          {"collision_pairs",contactList(result,false)}};
        summary["start_paired_candidates"].push_back(pair);
        if (result.collision || !candidate.satisfiesBounds()) continue;
        previous=candidate; selected=true;
        begin_state("A_tight_transport",0,0.,object,previous,true);
        current_state_context["left_ik_diagnostics"]=ld; current_state_context["right_ik_diagnostics"]=rd;
        current_state_context["selected_pair_index"]=pair["candidate_index"];
        start_row=checkState(previous,scene,left,right,lt,rt,object,gl,gr,environment,cube_size,current_state_context);
        start_row["left_ik_diagnostics"]=ld; start_row["right_ik_diagnostics"]=rd;
        start_row["selected_pair_index"]=pair["candidate_index"];
        break;
      }
    }
    if (!selected)
      start_row={{"status","FAIL_STOP"},{"reason","NO_ACCEPTED_START_DUAL_IK_FCL_PAIR_WITHIN_FINITE_POOL"},
        {"left_ik_diagnostics",ld},{"right_ik_diagnostics",rd},{"fcl","NO_SELECTED_START_PAIR"},
        {"all_candidates_failed_is_not_global_infeasibility_proof",true}};
    append(start_row,"A_tight_transport",0,0.,object);
    if (!failed)
    {
      Json joints={{"status","START_JOINT_STATE_CANDIDATE_NOT_FROZEN"},
        {"benchmark_a_start_joint_state_rad",{{"left",start_row["left_q_rad"]},{"right",start_row["right_q_rad"]}}},
        {"cube_pose_world",rigidPose(object)},{"is_task27_feed_pose",false},{"random_re_ik_on_reset",false}};
      std::ofstream file(output/"start_joint_state_candidate.json"); file<<joints.dump(2)<<'\n';
    }
    const auto continue_segment=[&](const std::string& segment,const Eigen::Vector3d& from,
                                    const Eigen::Vector3d& to,const int steps,const int first)
    {
      for (int index=first;index<=steps && !failed;++index)
      {
        const double fraction=static_cast<double>(index)/steps;
        Eigen::Isometry3d object=Eigen::Isometry3d::Identity(); object.translation()=from+fraction*(to-from);
        begin_state(segment,index,fraction,object,previous,false);
        box(scene,"shared_cube",object.translation(),cube_size);
        Json left_diagnostics,right_diagnostics;
        const auto l=solutions(previous,left,lt,object*gl,1,1,&left_diagnostics);
        const auto r=solutions(previous,right,rt,object*gr,1,1,&right_diagnostics);
        Json row={{"status","FAIL_STOP"},{"left_ik_diagnostics",left_diagnostics},{"right_ik_diagnostics",right_diagnostics},
          {"reason","NO_ACCEPTED_PREVIOUS_Q_ONE_SHOT_DUAL_IK"},{"fcl","NOT_RUN_NO_ACCEPTED_DUAL_IK"},
          {"cube_environment_geometry",cubeEnvironment(object.translation(),cube_size,environment)}};
        if (!l.empty() && !r.empty())
        {
          State candidate(previous); std::vector<double> lq,rq;
          l.front().copyJointGroupPositions(left,lq); r.front().copyJointGroupPositions(right,rq);
          candidate.setJointGroupPositions(left,lq); candidate.setJointGroupPositions(right,rq); candidate.update();
          begin_state(segment,index,fraction,object,candidate,true);
          current_state_context["left_ik_diagnostics"]=left_diagnostics;
          current_state_context["right_ik_diagnostics"]=right_diagnostics;
          row=checkState(candidate,scene,left,right,lt,rt,object,gl,gr,environment,cube_size,current_state_context);
          row["left_ik_diagnostics"]=left_diagnostics; row["right_ik_diagnostics"]=right_diagnostics;
          row["max_joint_step_rad"]=0.;
          for (const auto* group:{left,right}) for (const auto& name:group->getVariableNames())
            row["max_joint_step_rad"]=std::max(row["max_joint_step_rad"].get<double>(),
              std::abs(candidate.getVariablePosition(name)-previous.getVariablePosition(name)));
          if (row["status"]=="PASS_DISCRETE_GEOMETRY") previous=candidate;
        }
        append(row,segment,index,fraction,object);
      }
    };
    continue_segment("A_tight_transport",start,pre,transport_steps,1);
    if (!failed)
    {
      // 接缝保留 A 实際 PRE_PUSH 的精确 14q，B 第零状态不重新 IK。
      object.translation()=pre;
      begin_state("B_constrained_insertion",0,0.,object,previous,true);
      current_state_context["ik_disposition"]="REUSED_EXACT_A_PRE_PUSH_Q_NO_RE_IK";
      current_state_context["seam_source_state_index"]=rows.size()-1;
      Json seam=checkState(previous,scene,left,right,lt,rt,object,gl,gr,environment,cube_size,current_state_context);
      seam["left_ik_diagnostics"]=Json::array(); seam["right_ik_diagnostics"]=Json::array();
      seam["ik_disposition"]="REUSED_EXACT_A_PRE_PUSH_Q_NO_RE_IK";
      seam["seam_source_state_index"]=rows.size()-1;
      append(seam,"B_constrained_insertion",0,0.,object);
      continue_segment("B_constrained_insertion",pre,goal,insertion_steps,1);
    }
    moveit_msgs::msg::AllowedCollisionMatrix final_acm;
    scene.getAllowedCollisionMatrix().getMessage(final_acm);
    if (final_acm!=original_acm) throw std::runtime_error("ACM changed");
    summary["acm_unchanged_verified"]=true;
    summary["status"]=failed ? "FAIL_STOP":"PASS_DISCRETE_FULL_CHAIN_ONLY";
    exit_code=failed ? 1:0;
  }
  catch (const std::exception& error)
  {
    summary["status"]="ERROR_STOP"; summary["error"]=error.what();
    if (current_state_pending)
    {
      current_state_context["status"]="ERROR_STOP";
      current_state_context["reason"]=error.what();
      summary["error_state_context"]=current_state_context;
      // 保留出错状态精确 pose/q 和此前取得的 contacts，而不把成功前缀冒称整段通过。
      rows.push_back(current_state_context);
    }
    std::cerr<<error.what()<<std::endl;
  }
  const auto planned=summary.contains("planned_state_counts") ? summary["planned_state_counts"]:Json::object();
  const bool overall_error=summary["status"]=="ERROR_STOP";
  summary["segments"]={{"A",summarize(rows,"A_tight_transport",planned.value("A_tight_transport",0),overall_error)},
    {"B",summarize(rows,"B_constrained_insertion",planned.value("B_constrained_insertion",0),overall_error)}};
  summary["recorded_states"]=rows.size();
  std::ofstream state_file(output/"state_records.json"); state_file<<rows.dump(2)<<'\n';
  std::ofstream result_file(output/"full_chain_results.json"); result_file<<summary.dump(2)<<'\n';
  std::cout<<summary["status"]<<" states="<<rows.size()<<std::endl;
  rclcpp::shutdown(); return exit_code;
}
