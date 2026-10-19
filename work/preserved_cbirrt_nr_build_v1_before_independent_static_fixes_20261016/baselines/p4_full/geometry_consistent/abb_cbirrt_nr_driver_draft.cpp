// Project-owned single-request transport. Engineering build never executes it.
// argv: II FRESH_MESH_WORK_DIRECTORY solve plain|trace
#include "abb_cbirrt_nr_observation_draft.hpp"
#include "CBiRRT_NR.h"
#include <ompl/base/ScopedState.h>
#include <ompl/base/ProblemDefinition.h>
#include <ompl/base/PlannerData.h>
#include <ompl/base/PlannerTerminationCondition.h>
#include <ompl/geometric/PathGeometric.h>
#include <ompl/util/RandomNumbers.h>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <memory>
#include <stdexcept>
namespace ob=ompl::base;
namespace og=ompl::geometric;
namespace fs=std::filesystem;
namespace {
class Redirect {
    std::streambuf* prior;
public:
    Redirect():prior(std::cout.rdbuf(std::cerr.rdbuf())){}
    ~Redirect(){std::cout.rdbuf(prior);}
};
std::vector<double> finite12(const p4cbnr::json& value) {
    auto q=value.get<std::vector<double>>();
    if(q.size()!=12)throw std::runtime_error("FINITE_Q12_REQUIRED");
    for(double x:q)if(!std::isfinite(x))throw std::runtime_error("FINITE_Q12_REQUIRED");
    return q;
}
class Probe final:public og::CBiRRT {
public:
    Probe(const ob::SpaceInformationPtr& si):og::CBiRRT(si,2.6,1){}
    p4cbnr::json snapshot() const {
        p4cbnr::json nodes=p4cbnr::json::array();std::map<const ob::State*,unsigned long> state_to_motion;
        for(const auto& tree:{tStart_,tGoal_})if(tree){std::vector<Motion*> motions;tree->list(motions);for(auto* m:motions)state_to_motion[m->state]=p4cbnr::identity(m);}
        unsigned side=0;
        for(const auto& tree:{tStart_,tGoal_}){
            if(tree){
                std::vector<Motion*> motions;tree->list(motions);
                for(auto* m:motions)nodes.push_back({{"motion_id",p4cbnr::identity(m)},{"tree",side==0?"start":"goal"},
                    {"state_id",p4cbnr::identity(m->state)},{"parent_motion_id",p4cbnr::identity(m->parent)},
                    {"root_state_id",p4cbnr::identity(m->root)},{"root_motion_id",state_to_motion.at(m->root)},
                    {"q12",p4cbnr::q12(m->state)},{"root_q12",p4cbnr::q12(m->root)}});
            }
            ++side;
        }
        auto connection=[&](const ob::State* s)->p4cbnr::json{
            if(!s)return nullptr;
            auto found=state_to_motion.find(s);
            return {{"state_id",p4cbnr::identity(s)},{"motion_id",found==state_to_motion.end()?p4cbnr::json(nullptr):p4cbnr::json(found->second)},{"q12",p4cbnr::q12(s)}};
        };
        return {{"nodes",nodes},{"connection_start",connection(connectionPoint_.first)},
            {"connection_goal",connection(connectionPoint_.second)},
            {"node_identity_policy","Actual live Motion/state identities; equal q never merged. Original CBiNR never deletes tree motions before snapshot."}};
    }
};
void observation(p4cbnr::json& result){
    result["source_counts_observed"]=p4cbnr::enabled;
    result["source_started"]=p4cbnr::enabled?p4cbnr::json(p4cbnr::started):p4cbnr::json(nullptr);
    result["source_completed"]=p4cbnr::enabled?p4cbnr::json(p4cbnr::completed):p4cbnr::json(nullptr);
    result["trace"]=p4cbnr::enabled?p4cbnr::events:p4cbnr::json(nullptr);
}
}
int main(int argc,char** argv){
    if(argc!=5)return 64;
    const std::string env=argv[1],operation=argv[3],mode=argv[4];
    if(env!="II"||operation!="solve"||(mode!="plain"&&mode!="trace"))return 64;
    p4cbnr::json out={{"schema","P4_ABB_CBIRRT_NR_TRANSPORT_DRAFT_V1"},{"status","STOP_RETAINED_PREFIX"},
        {"environment",env},{"operation",operation},{"mode",mode},{"source_dispatch_started",0},
        {"source_dispatch_completed",0},{"solve_calls",0},{"formal_table_I_calls",0},
        {"independent_path_qualified",false},{"continuous_collision_certificate",false}};
    try{
        const fs::path work=fs::absolute(argv[2]);
        if(!fs::is_directory(work/"simulator"))throw std::runtime_error("MESH_WORK_DIRECTORY_REQUIRED");
        fs::current_path(work);
        if(fs::exists("paths")||!fs::create_directory("paths"))throw std::runtime_error("FRESH_ABSENT_PATHS_REQUIRED");
        std::string line,extra;if(!std::getline(std::cin,line))throw std::runtime_error("ONE_REQUEST_REQUIRED");
        while(std::getline(std::cin,extra))if(!extra.empty())throw std::runtime_error("EXACTLY_ONE_REQUEST_REQUIRED");
        auto request=p4cbnr::json::parse(line);out["request"]=request;
        if(request.at("environment")!=env||request.at("operation")!=operation||request.at("seed")!=7||request.at("range_rad")!=2.6||request.at("solve_seconds")!=10.)
            throw std::runtime_error("FROZEN_II_SEED7_RANGE26_SOLVE10_REQUIRED");
        auto start=finite12(request.at("start_q12")),goal=finite12(request.at("goal_q12"));
        const std::vector<double> arm_low={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416},arm_high={2.88,1.919,1.22,2.79,2.09,3.1416};
        std::vector<double> low=arm_low,high=arm_high;low.insert(low.end(),arm_low.begin(),arm_low.end());high.insert(high.end(),arm_high.begin(),arm_high.end());
        if(request.at("bounds_low_rad")!=low||request.at("bounds_high_rad")!=high)throw std::runtime_error("ORIGINAL_MAIN_SAMPLER_BOX_REQUIRED");
        p4cbnr::enabled=(mode=="trace");p4cbnr::reset();
        p4pcs::enabled=false;p4nr_iface::environment="II";
        ompl::RNG::setSeed(7);std::srand(7);
        auto space=std::make_shared<ob::RealVectorStateSpace>(12);ob::RealVectorBounds bounds(12);
        for(unsigned i=0;i<12;++i){bounds.setLow(i,low[i]);bounds.setHigh(i,high[i]);}space->setBounds(bounds);
        auto si=std::make_shared<ob::SpaceInformation>(space);
        si->setStateValidityChecker([](const ob::State*){return true;});si->setStateValidityCheckingResolution(.1);
        std::unique_ptr<Probe> planner;
        {Redirect quiet;si->setup();planner=std::make_unique<Probe>(si);}
        out["construction"]={{"cbirrt_constructor_dispatch_completed",1},{"ompl_setSeed_calls_completed",1},{"srand_calls_completed",1},
            {"source_direct_rng_member_initializations_structural",1},{"source_direct_rng_member_true_started_completed","UNOBSERVED_LIBRARY_NOT_HOOKED"},
            {"library_internal_seed_draws","UNOBSERVED_NOT_REPORTED_ZERO"}};
        observation(out["construction"]);p4cbnr::reset();
        ob::ScopedState<ob::RealVectorStateSpace> a(space),b(space);for(unsigned i=0;i<12;++i){a[i]=start[i];b[i]=goal[i];}
        auto problem=std::make_shared<ob::ProblemDefinition>(si);problem->setStartAndGoalStates(a,b);
        {Redirect quiet;planner->setProblemDefinition(problem);planner->setup();}
        out["state_validity_callback"]="ORIGINAL_MAIN_ALWAYS_TRUE_NO_FK";
        out["resolution"]=.1;out["distance_policy"]="ORIGINAL_FULL12_SI_DISTANCE_NO_ACTIVE_ROLE_OR_ANALYTIC_BRANCH";
        out["solution_path_simplification"]=false;out["source_dispatch_started"]=1;out["solve_calls"]=1;
        const auto begun=std::chrono::steady_clock::now();
        {Redirect quiet;const auto status=planner->solve(ob::timedPlannerTerminationCondition(10.));
            out["planner_status"]=status.asString();out["planner_status_code"]=static_cast<int>(static_cast<ob::PlannerStatus::StatusType>(status));}
        out["solve_wall_s"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count();
        out["solve_wall_scope"]="Whole original solve including save2file and observation I/O; not a paper timing sample.";
        out["source_dispatch_completed"]=1;out["exact"]=problem->hasExactSolution();out["has_solution"]=problem->hasSolution();
        out["approximate"]=problem->hasApproximateSolution();out["solution_count"]=problem->getSolutionCount();
        out["solution_difference"]=problem->hasSolution()?p4cbnr::json(problem->getSolutionDifference()):p4cbnr::json(nullptr);
        out["trees"]=planner->snapshot();out["milestones_q12"]=p4cbnr::json::array();
        if(problem->hasSolution()){
            auto path=std::dynamic_pointer_cast<og::PathGeometric>(problem->getSolutionPath());if(!path)throw std::runtime_error("GEOMETRIC_PATH_REQUIRED");
            for(auto* s:path->getStates())out["milestones_q12"].push_back(p4cbnr::q12(s));
        }
        if(problem->hasExactSolution()){
            ob::PlannerData data(si);{Redirect quiet;planner->getPlannerData(data);}
            p4cbnr::json vertices=p4cbnr::json::array(),edges=p4cbnr::json::array();
            for(unsigned i=0;i<data.numVertices();++i){
                vertices.push_back({{"index",i},{"q12",p4cbnr::q12(data.getVertex(i).getState())},{"state_id",p4cbnr::identity(data.getVertex(i).getState())},
                    {"tag",data.getVertex(i).getTag()},{"start",data.isStartVertex(i)},{"goal",data.isGoalVertex(i)}});
                std::vector<unsigned> children;data.getEdges(i,children);for(auto child:children)edges.push_back({i,child});
            }
            out["planner_data"]={{"vertices",vertices},{"edges",edges}};
        }else out["planner_data"]=nullptr;
        out["status"]=problem->hasExactSolution()?"SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT":"SOURCE_NONEXACT_RETAINED_PREFIX";
    }catch(const std::exception& error){out["error"]=error.what();}
    observation(out);std::cout<<out.dump()<<std::endl;
    return out["status"]=="STOP_RETAINED_PREFIX"?2:0;
}
