#include "geometry_common.hpp"

int main(int argc,char** argv)
{
  if (argc<6 || argc%2!=0) { std::cerr<<"usage: probe benchmark.yaml robot.urdf robot.srdf kinematics.yaml output-dir [--ik-epsilon value] [--replay-step dense-results.json]\n"; return 2; }
  std::optional<double> solver_epsilon;
  std::optional<std::string> replay_path;
  for (int i=6;i<argc;i+=2)
  {
    if (std::string(argv[i])=="--ik-epsilon")
    {
      try { solver_epsilon=std::stod(argv[i+1]); } catch (...) { return 2; }
      // 仅收紧求解精度；不允许借此放宽原来的残差验收。
      if (!std::isfinite(*solver_epsilon) || *solver_epsilon<=0. || *solver_epsilon>1e-5) return 2;
    }
    else if (std::string(argv[i])=="--replay-step") replay_path=argv[i+1];
    else return 2;
  }
  const std::filesystem::path output(argv[5]);
  if (std::filesystem::exists(output/"sample_results.json") || std::filesystem::exists(output/"replay_step_results.json"))
    { std::cerr<<"Refusing to overwrite prior run\n"; return 2; }
  std::filesystem::create_directories(output);
  Json samples=Json::array();
  Json dense=Json::array();
  Json numeric;
  int exit_code=2;
  rclcpp::init(argc,argv);
  try
  {
    const auto config=YAML::LoadFile(argv[1]);
    const auto kin=YAML::LoadFile(argv[4]);
    if (config["cube"]["count"].as<int>()!=1 || config["frames"]["world"].as<std::string>()!="world")
      throw std::runtime_error("Not a one-Cube world-frame candidate");
    std::vector<rclcpp::Parameter> params={rclcpp::Parameter("robot_description",readText(argv[2])),
      rclcpp::Parameter("robot_description_semantic",readText(argv[3]))};
    for (const std::string arm:{"left_arm","right_arm"})
      for (const auto entry:kin[arm])
      {
        const auto key=entry.first.as<std::string>();
        for (const auto& prefix:{arm+".","robot_description_kinematics."+arm+"."})
          if (key=="kinematics_solver") params.emplace_back(prefix+key,entry.second.as<std::string>());
          else if (key=="max_solver_iterations") params.emplace_back(prefix+key,entry.second.as<int>());
          else if (key=="position_only_ik") params.emplace_back(prefix+key,entry.second.as<bool>());
          else params.emplace_back(prefix+key,entry.second.as<double>());
      }
    for (const std::string arm:{"left_arm","right_arm"})
    {
      if (solver_epsilon) params.emplace_back(arm+".epsilon",*solver_epsilon);
      numeric[arm]={{"plugin",kin[arm]["kinematics_solver"].as<std::string>()},
        {"epsilon",solver_epsilon.value_or(kin[arm]["epsilon"] ? kin[arm]["epsilon"].as<double>():1e-5)},
        {"orientation_vs_position",kin[arm]["orientation_vs_position"] ? kin[arm]["orientation_vs_position"].as<double>():.01},
        {"epsilon_override_namespace",solver_epsilon ? arm+".epsilon":"none; YAML or plugin default"}};
    }
    auto node=std::make_shared<rclcpp::Node>("task01_single_cube_geometry",
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
    State state(model); state.setToDefaultValues();
    state.setToDefaultValues(left,"home"); state.setToDefaultValues(right,"home"); state.update();
    for (const auto arm:{"left","right"})
      if ((state.getGlobalLinkTransform(std::string(arm)+"_fr3_link0").translation()-
           vec(config["robots"][arm]["base_at_rest_world_m"])).norm()>1e-9)
        throw std::runtime_error("Model base differs from candidate; no hidden rail shift permitted");
    planning_scene::PlanningScene scene(model);
    const auto acm_before=scene.getAllowedCollisionMatrix().getSize();
    box(scene,"table",vec(config["table"]["center_world_m"]),vec(config["table"]["size_m"]));
    const auto c=config["carriage"];
    const double x0=c["interior_x_world_m"][0].as<double>(),x1=c["interior_x_world_m"][1].as<double>();
    const double y0=c["interior_y_world_m"][0].as<double>(),y1=c["interior_y_world_m"][1].as<double>();
    const double t=c["wall_thickness_m"].as<double>(),h=c["wall_height_m"].as<double>();
    const double z=c["wall_top_world_z_m"].as<double>()-h/2.;
    box(scene,"carriage_deep_wall",{x1+t/2.,(y0+y1)/2.,z},{t,y1-y0+2*t,h});
    box(scene,"carriage_minus_y_wall",{(x0+x1)/2.,y0-t/2.,z},{x1-x0+2*t,t,h});
    box(scene,"carriage_plus_y_wall",{(x0+x1)/2.,y1+t/2.,z},{x1-x0+2*t,t,h});
    const auto grasp_l=transform(config["shared_grasp"]["object_to_left_tcp_candidate"]);
    const auto grasp_r=transform(config["shared_grasp"]["object_to_right_tcp_candidate"]);
    const auto size=vec(config["cube"]["size_m"]);
    const auto b=config["benchmarks"]["B_constrained_insertion"];
    const auto pre=vec(b["start_cube_center_world_m"]),goal=vec(b["target_cube_center_world_m"]);
    if (replay_path)
    {
      // 同一记录的精确14q/同一目标做数值A/B，只检查一个步骤，不选择新的吸点或构型。
      const auto recorded=Json::parse(readText(*replay_path));
      if (!recorded.is_array() || recorded.size()!=2 || recorded[0]["status"]!="PASS" || recorded[1]["status"]!="FAIL_STOP")
        throw std::runtime_error("Replay expects prior two-row PASS/FAIL record");
      const auto lq=recorded[0]["left_q_rad"].get<std::vector<double>>();
      const auto rq=recorded[0]["right_q_rad"].get<std::vector<double>>();
      if (lq.size()!=left->getVariableCount() || rq.size()!=right->getVariableCount())
        throw std::runtime_error("Replay joint count mismatch");
      state.setJointGroupPositions(left,lq); state.setJointGroupPositions(right,rq); state.update();
      if (!state.satisfiesBounds()) throw std::runtime_error("Replay seed exceeds original limits");
      Eigen::Isometry3d object=Eigen::Isometry3d::Identity();
      const auto p=recorded[1]["cube_center_world_m"].get<std::vector<double>>();
      if (p.size()!=3) throw std::runtime_error("Replay Cube XYZ mismatch");
      object.translation()=Eigen::Vector3d(p[0],p[1],p[2]);
      box(scene,"shared_cube",object.translation(),size);
      Json ld,rd;
      const auto ls=solutions(state,left,lt,object*grasp_l,1,1,&ld),rs=solutions(state,right,rt,object*grasp_r,1,1,&rd);
      Json record={{"scope","single_cube_core_benchmark"},{"replay_input",*replay_path},
        {"effective_ik_numeric",numeric},{"original_seed_left_q_rad",lq},{"original_seed_right_q_rad",rq},
        {"cube_center_world_m",xyz(object.translation())},{"left_ik_diagnostics",ld},{"right_ik_diagnostics",rd},
        {"robot_commands",0},{"suction_commands",0},{"physics_started",false},{"acm_modified",false},
        {"full_chain_verified",false},{"fcl","NOT_RUN_NO_ACCEPTED_DUAL_IK"},{"status","FAIL_STOP"}};
      if (!ls.empty() && !rs.empty())
      {
        State pair(state); std::vector<double> new_lq,new_rq;
        ls.front().copyJointGroupPositions(left,new_lq); rs.front().copyJointGroupPositions(right,new_rq);
        pair.setJointGroupPositions(left,new_lq); pair.setJointGroupPositions(right,new_rq); pair.update();
        collision_detection::CollisionRequest request; request.contacts=true;
        request.max_contacts=200; request.max_contacts_per_pair=1;
        collision_detection::CollisionResult result; scene.checkCollision(request,result,pair);
        record["collision_pairs"]=Json::array();
        for (const auto& entry:result.contacts) for (const auto& hit:entry.second)
          record["collision_pairs"].push_back({{"body1",entry.first.first},{"body2",entry.first.second},{"depth_m",hit.depth}});
        record["fcl"]=result.collision ? "FAIL":"PASS";
        if (!result.collision && pair.satisfiesBounds()) record["status"]="PASS_RECORDED_STEP_ONLY";
      }
      std::ofstream file(output/"replay_step_results.json"); file<<record.dump(2)<<'\n';
      std::cout<<record.dump()<<std::endl;
      rclcpp::shutdown(); return record["status"]=="PASS_RECORDED_STEP_ONLY" ? 3:1;
    }
    // START 缺定义就记录缺失；不私自继承 Task27 供料位或选一个更好到达的位置。
    const auto start=config["benchmarks"]["A_tight_transport"]["initial_cube_center_world_m"];
    const bool start_defined=start.IsSequence();
    const std::vector<std::pair<std::string,double>> names={{"PRE_PUSH",0.},{"INSERT_10",.1},
      {"INSERT_30",.3},{"INSERT_50",.5},{"INSERT_70",.7},{"INSERT_100",1.}};
    samples.push_back({{"sample","START"},{"status","NOT_RUN_UNDEFINED_START"}});
    if (start_defined) throw std::runtime_error("START now defined: extend explicit start handling before run");
    std::ofstream contacts(output/"collision_pairs.csv"),margins(output/"joint_margin.csv"),errors(output/"relative_grasp_error.csv");
    contacts<<"sample,candidate,body1,body2,depth_m,x_m,y_m,z_m\n";
    margins<<"sample,joint,position_rad,lower_rad,upper_rad,margin_rad\n";
    errors<<"sample,arm,translation_m,rotation_rad\n";
    contacts<<std::setprecision(17); margins<<std::setprecision(17); errors<<std::setprecision(17);
    bool stopped=false;
    std::optional<State> pre_state;
    for (const auto& [name,fraction]:names)
    {
      if (stopped) { samples.push_back({{"sample",name},{"status","NOT_RUN_STOP_ON_FAILURE"}}); continue; }
      Eigen::Isometry3d object=Eigen::Isometry3d::Identity(); object.translation()=pre+fraction*(goal-pre);
      box(scene,"shared_cube",object.translation(),size);
      auto ls=solutions(state,left,lt,object*grasp_l),rs=solutions(state,right,rt,object*grasp_r);
      Json record={{"sample",name},{"cube_center_world_m",xyz(object.translation())},
        {"left_ik_count",ls.size()},{"right_ik_count",rs.size()},
        {"seed_attempt_cap_per_arm",64},{"retained_solution_cap_per_arm",12},
        {"all_candidates_failed_is_not_global_infeasibility_proof",true}};
      std::optional<State> selected;
      Json best_contacts=Json::array(); std::size_t least=std::numeric_limits<std::size_t>::max(); int candidate=0;
      bool selected_collision=true;
      for (const auto& l:ls) for (const auto& r:rs)
      {
        State paired(state); std::vector<double> lq,rq;
        l.copyJointGroupPositions(left,lq); r.copyJointGroupPositions(right,rq);
        paired.setJointGroupPositions(left,lq); paired.setJointGroupPositions(right,rq); paired.update();
        collision_detection::CollisionRequest request; request.contacts=true;
        request.max_contacts=200; request.max_contacts_per_pair=1; // 空 group = 全机器人。
        collision_detection::CollisionResult result; scene.checkCollision(request,result,paired);
        Json pairs=Json::array();
        for (const auto& entry:result.contacts) for (const auto& hit:entry.second)
        {
          pairs.push_back({{"body1",entry.first.first},{"body2",entry.first.second},
                           {"depth_m",hit.depth},{"position_world_m",xyz(hit.pos)}});
          contacts<<name<<','<<candidate<<','<<entry.first.first<<','<<entry.first.second<<','<<hit.depth<<','
                  <<hit.pos.x()<<','<<hit.pos.y()<<','<<hit.pos.z()<<'\n';
        }
        if (!result.collision || result.contacts.size()<least)
          { least=result.contacts.size(); best_contacts=pairs; selected=paired; selected_collision=result.collision; }
        ++candidate;
        if (!result.collision) goto candidate_selected;
      }
candidate_selected:
      record["joint_candidates_checked"]=candidate;
      record["collision_pairs"]=best_contacts;
      bool valid=selected.has_value() && !selected_collision;
      record["fcl"]=selected ? (!selected_collision ? "PASS":"FAIL"):"NOT_CHECKED_NO_IK";
      if (selected)
      {
        record["joint_limit"]=selected->satisfiesBounds() ? "PASS":"FAIL";
        record["min_joint_margin_rad"]=std::min(margin(*selected,left),margin(*selected,right));
        std::vector<double> lq,rq; selected->copyJointGroupPositions(left,lq); selected->copyJointGroupPositions(right,rq);
        record["left_q_rad"]=lq; record["right_q_rad"]=rq;
        record["left_relative_grasp_error"]=residual(*selected,lt,object*grasp_l);
        record["right_relative_grasp_error"]=residual(*selected,rt,object*grasp_r);
        for (const auto* group:{left,right}) for (const auto& joint:group->getVariableNames())
        {
          const auto& bound=model->getVariableBounds(joint); const double q=selected->getVariablePosition(joint);
          margins<<name<<','<<joint<<','<<q<<','<<bound.min_position_<<','<<bound.max_position_<<','
                 <<std::min(q-bound.min_position_,bound.max_position_-q)<<'\n';
        }
        for (const auto arm:{"left","right"}) errors<<name<<','<<arm<<','
          <<record[std::string(arm)+"_relative_grasp_error"]["translation_m"]<<','
          <<record[std::string(arm)+"_relative_grasp_error"]["rotation_rad"]<<'\n';
        collision_detection::DistanceRequest request;
        request.type=collision_detection::DistanceRequestType::ALL;
        request.enable_signed_distance=true; request.enable_nearest_points=true;
        request.acm=&scene.getAllowedCollisionMatrix();
        collision_detection::DistanceResult distances;
        scene.getCollisionEnv()->distanceRobot(request,distances,*selected);
        record["wrist_tool_wall_distances_m"]=Json::array();
        for (const auto& entry:distances.distances) for (const auto& d:entry.second)
          if ((entry.first.first.find("carriage_")==0 || entry.first.second.find("carriage_")==0) &&
              (entry.first.first.find("side_suction")!=std::string::npos || entry.first.second.find("side_suction")!=std::string::npos ||
               entry.first.first.find("link7")!=std::string::npos || entry.first.second.find("link7")!=std::string::npos ||
               entry.first.first.find("link8")!=std::string::npos || entry.first.second.find("link8")!=std::string::npos))
            record["wrist_tool_wall_distances_m"].push_back({{"body1",entry.first.first},
              {"body2",entry.first.second},{"signed_distance_m",d.distance}});
        valid=valid && selected->satisfiesBounds();
        state=*selected;
        if (name=="PRE_PUSH" && valid) pre_state=state;
      }
      record["status"]=valid ? "PASS_SAMPLED_ENDPOINT":"FAIL_STOP";
      std::cout<<name<<": "<<record["status"]<<", dual IK="<<ls.size()<<'/'<<rs.size()
               <<", paired candidates="<<candidate<<", contacts="<<best_contacts.dump()<<std::endl;
      samples.push_back(record);
      if (!valid) stopped=true;
    }
    // [ENGINEERING] 额外验证插入段同一 IK 分支延续，每不超过 2 mm 检查闭链和全 FCL。
    // 这是离散几何检查，不是 P4 投影规划或连续碰撞证明；第一次失败立即停止。
    if (!stopped && pre_state)
    {
      State previous=*pre_state;
      const int steps=static_cast<int>(std::ceil((goal-pre).norm()/.002));
      for (int index=0;index<=steps;++index)
      {
        const double fraction=static_cast<double>(index)/steps;
        Eigen::Isometry3d object=Eigen::Isometry3d::Identity(); object.translation()=pre+fraction*(goal-pre);
        Json ldiagnostic,rdiagnostic;
        auto ls=solutions(previous,left,lt,object*grasp_l,1,1,&ldiagnostic);
        auto rs=solutions(previous,right,rt,object*grasp_r,1,1,&rdiagnostic);
        Json row={{"index",index},{"insertion_fraction",fraction},{"cube_center_world_m",xyz(object.translation())},
                  {"status","FAIL_STOP"},{"dual_ik",!ls.empty() && !rs.empty()},
                  {"left_ik_diagnostics",ldiagnostic},{"right_ik_diagnostics",rdiagnostic}};
        if (!ls.empty() && !rs.empty())
        {
          State paired(previous); std::vector<double> lq,rq;
          ls.front().copyJointGroupPositions(left,lq); rs.front().copyJointGroupPositions(right,rq);
          paired.setJointGroupPositions(left,lq); paired.setJointGroupPositions(right,rq); paired.update();
          box(scene,"shared_cube",object.translation(),size);
          collision_detection::CollisionRequest request; request.contacts=true;
          request.max_contacts=200; request.max_contacts_per_pair=1;
          collision_detection::CollisionResult result; scene.checkCollision(request,result,paired);
          row["collision_pairs"]=Json::array();
          for (const auto& entry:result.contacts) for (const auto& hit:entry.second)
          {
            row["collision_pairs"].push_back({{"body1",entry.first.first},{"body2",entry.first.second},
                                             {"depth_m",hit.depth},{"position_world_m",xyz(hit.pos)}});
            contacts<<"DENSE_"<<index<<",0,"<<entry.first.first<<','<<entry.first.second<<','<<hit.depth<<','
                    <<hit.pos.x()<<','<<hit.pos.y()<<','<<hit.pos.z()<<'\n';
          }
          row["joint_limit"]=paired.satisfiesBounds();
          row["min_joint_margin_rad"]=std::min(margin(paired,left),margin(paired,right));
          row["left_relative_grasp_error"]=residual(paired,lt,object*grasp_l);
          row["right_relative_grasp_error"]=residual(paired,rt,object*grasp_r);
          row["max_joint_step_rad"]=0.;
          for (const auto& joint:model->getVariableNames()) row["max_joint_step_rad"]=std::max(
            row["max_joint_step_rad"].get<double>(),std::abs(paired.getVariablePosition(joint)-previous.getVariablePosition(joint)));
          row["left_q_rad"]=lq; row["right_q_rad"]=rq;
          for (const auto link:{"left_fr3_link7","right_fr3_link7"})
          {
            const auto& t=paired.getGlobalLinkTransform(link); const Eigen::Quaterniond q(t.linear());
            row[std::string(link)+"_world_pose"]={{"translation_m",xyz(t.translation())},
              {"quaternion_xyzw",Json::array({q.x(),q.y(),q.z(),q.w()})}};
          }
          if (!result.collision && paired.satisfiesBounds()) { row["status"]="PASS"; previous=paired; }
        }
        dense.push_back(row);
        if (row["status"]!="PASS") { stopped=true; std::cout<<"DENSE FAIL: "<<row.dump()<<std::endl; break; }
      }
      std::cout<<"Dense insertion states checked="<<dense.size()<<", stop="<<stopped<<std::endl;
    }
    if (scene.getAllowedCollisionMatrix().getSize()!=acm_before) throw std::runtime_error("ACM changed");
    exit_code=stopped ? 1:3; // START 缺失不能用插入离散点 PASS 宣称整链通过。
  }
  catch (const std::exception& e) { samples.push_back({{"status","ERROR"},{"reason",e.what()}}); std::cerr<<e.what()<<std::endl; }
  std::ofstream file(output/"sample_results.json");
  file<<Json({{"scope","single_cube_core_benchmark"},{"status",exit_code==1 ? "FAIL_STOP":exit_code==3 ? "PARTIAL_UNDEFINED_START":"ERROR"},
    {"physics_started",false},{"robot_commands",0},{"suction_commands",0},{"acm_modified",false},
    {"continuous_path_verified",false},{"effective_ik_numeric",numeric},
    {"dense_step_cap_m",.002},{"dense_states_checked",dense.size()},
    {"samples",samples}}).dump(2)<<'\n';
  std::ofstream dense_file(output/"dense_insertion_results.json"); dense_file<<dense.dump(2)<<'\n';
  rclcpp::shutdown(); return exit_code;
}
