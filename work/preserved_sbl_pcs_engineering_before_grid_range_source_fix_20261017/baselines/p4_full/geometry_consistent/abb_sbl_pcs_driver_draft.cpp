// Project-owned SBL engineering transport. Builder never executes this binary.
// Only future separately frozen II/setup is available. solve is refused.
#include "abb_sbl_pcs_observation_draft.hpp"
#include "SBL_PCS.h"
#include <ompl/base/ScopedState.h>
#include <ompl/base/ProblemDefinition.h>
#include <ompl/base/spaces/RealVectorStateProjections.h>
#include <ompl/util/RandomNumbers.h>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <memory>
#include <typeinfo>
namespace ob=ompl::base;
namespace og=ompl::geometric;
namespace fs=std::filesystem;
namespace {
class Redirect {std::streambuf* old;public:Redirect():old(std::cout.rdbuf(std::cerr.rdbuf())){}~Redirect(){std::cout.rdbuf(old);}};
std::vector<double> finite12(const p4sbl::json& value){auto q=value.get<std::vector<double>>();p4sbl::require(q.size()==12,"FINITE12_REQUIRED");for(double x:q)p4sbl::require(std::isfinite(x),"FINITE12_REQUIRED");return q;}
void put(ob::ScopedState<ob::RealVectorStateSpace>& state,const std::vector<double>& q){for(unsigned i=0;i<12;++i)state[i]=q[i];}
class Probe final:public og::SBL {
public:
    Probe(const ob::SpaceInformationPtr& si):og::SBL(si,2.6,1){p4sbl::bind_tree(&tStart_,"start");p4sbl::bind_tree(&tGoal_,"goal");}
    p4sbl::json metadata()const {
        auto p=getProjectionEvaluator();p4sbl::require(bool(p),"ACTUAL_DEFAULT_PROJECTION_REQUIRED");
        const auto& type=typeid(*p);
        p4sbl::require(type==typeid(ob::RealVectorLinearProjectionEvaluator)||type==typeid(ob::RealVectorRandomLinearProjectionEvaluator),"EXACT_EXISTING_LINEAR_TYPE_REQUIRED_NO_REPLACEMENT");
        const unsigned dim=p->getDimension();p4sbl::require(dim>0,"POSITIVE_ACTUAL_PROJECTION_DIMENSION_REQUIRED");
        p4sbl::json observations=p4sbl::json::array(),columns=p4sbl::json::array();
        ob::ScopedState<ob::RealVectorStateSpace> input(si_->getStateSpace());
        for(unsigned sample=0;sample<13;++sample){
            for(unsigned i=0;i<12;++i)input[i]=(sample>0&&sample-1==i)?1.:0.;
            Eigen::VectorXd output(dim);p->project(input.get(),output);
            std::vector<double> values(output.data(),output.data()+dim);
            for(double x:values)p4sbl::require(std::isfinite(x),"FINITE_PUBLIC_LINEAR_ACTION_REQUIRED");
            if(sample==0)for(double x:values)p4sbl::require(x==0.,"PUBLIC_LINEAR_ACTION_ORIGIN_MUST_BE_ZERO");
            else columns.push_back(values);
            observations.push_back({{"input_q12",p4sbl::q12(input.get())},{"input_binary64",p4sbl::binary64(p4sbl::q12(input.get()))},{"output",values},{"output_binary64",p4sbl::binary64(values)}});
        }
        p4sbl::json bounds=nullptr;
        if(p->hasBounds())bounds={{"low",p->getBounds().low},{"high",p->getBounds().high}};
        return {{"projection_dynamic_type",type.name()},{"projection_dimension",dim},{"cell_sizes",p->getCellSizes()},
            {"has_bounds",p->hasBounds()},{"bounds",bounds},{"user_configured",p->userConfigured()},
            {"public_project_observation_count",13},{"fixed_zero_then_basis_observations",observations},
            {"observed_linear_action_matrix_columns",columns},{"matrix_identity_label","OBSERVED_LINEAR_ACTION_MATRIX_NOT_PROTECTED_STORAGE_BYTES"},
            {"projection_observer_RNG_draws",0},{"actual_setup_library_RNG_draws","UNOBSERVED"},
            {"setup_getRange",getRange()},{"original_solve_Range",Range},
            {"sampler",sampler_?p4sbl::json(sampler_->getName()):p4sbl::json(nullptr)},
            {"sampler_allocated_by_observer",false},{"native_tree_sizes",{tStart_.size,tGoal_.size}},
            {"original_solve_entry_available",false},{"historical_connect_a_chain_risk","SOURCE_ONLY_PENDING_SEPARATE_SOLVE_GATE"}};
    }
};
}
int main(int argc,char** argv){
    if(argc!=4||std::string(argv[1])!="II"||std::string(argv[3])!="setup")return 64;
    p4sbl::json result={{"schema","P4_ABB_SBL_PCS_SETUP_TRANSPORT_DRAFT_V1"},{"status","STOP_RETAINED_PREFIX"},{"operation","setup"},{"solve_calls",0},{"formal_table_I_calls",0},{"new_VI_candidate_constructions",0},{"independent_path_qualified",false}};
    try{
        std::string line,extra;p4sbl::require(bool(std::getline(std::cin,line)),"ONE_FROZEN_SETUP_REQUEST_REQUIRED");
        p4sbl::require(!std::getline(std::cin,extra),"EXACT_ONE_REQUEST_THEN_STDIN_EOF_REQUIRED");
        const auto request=p4sbl::json::parse(line);
        p4sbl::require(request.at("operation")=="setup"&&request.at("environment")=="II"&&request.at("seed")==7&&request.at("separately_frozen_setup_qualification")==true,"SEPARATE_SETUP_QUALIFICATION_REQUIRED_NO_SOLVE");
        auto start=finite12(request.at("start_q12")),goal=finite12(request.at("goal_q12"));
        const auto work=fs::absolute(argv[2]);p4sbl::require(fs::is_directory(work/"simulator"),"EXCLUSIVE_FUTURE_MESH_WORK_DIRECTORY_REQUIRED");fs::current_path(work);
        p4sbl::require(!fs::exists("paths")&&!fs::exists("../paths"),"BOTH_ORIGINAL_PATHS_MUST_BE_FRESH");
        p4sbl::require(fs::create_directory("paths")&&fs::create_directory("../paths"),"ISOLATED_ORIGINAL_PATHS_CREATION_REQUIRED");
        p4sbl::enabled=true;p4sbl::reset();ompl::RNG::setSeed(7);std::srand(7);
        auto space=std::make_shared<ob::RealVectorStateSpace>(12);ob::RealVectorBounds bounds(12);
        const std::vector<double> lo={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416},hi={2.88,1.919,1.22,2.79,2.09,3.1416};
        for(unsigned i=0;i<12;++i){bounds.setLow(i,lo[i%6]);bounds.setHigh(i,hi[i%6]);}space->setBounds(bounds);
        auto si=std::make_shared<ob::SpaceInformation>(space);si->setStateValidityChecker([](const ob::State*){return true;});si->setStateValidityCheckingResolution(.02);
        ob::ScopedState<ob::RealVectorStateSpace> a(space),b(space);put(a,start);put(b,goal);
        auto problem=std::make_shared<ob::ProblemDefinition>(si);problem->setStartAndGoalStates(a,b);
        {Redirect quiet;auto planner=std::make_unique<Probe>(si);planner->setProblemDefinition(problem);planner->setup();result["actual_setup_metadata"]=planner->metadata();planner.reset();}
        p4sbl::require(p4sbl::live.empty(),"REGISTRY_MUST_BE_EMPTY_AFTER_DESTRUCTION");result["status"]="SOURCE_SETUP_OBSERVED_NOT_RUNTIME_QUALIFIED";
        result["request"]=request;result["original_default_setup_order_preserved"]=true;
    }catch(const std::exception& e){result["error"]=e.what();}
    result["source_started"]=p4sbl::started;result["source_completed"]=p4sbl::completed;result["trace"]=p4sbl::events;
    result["remaining_live_motions"]=p4sbl::live.size();std::cout<<result.dump()<<std::endl;
    return result["status"]=="SOURCE_SETUP_OBSERVED_NOT_RUNTIME_QUALIFIED"?0:2;
}
