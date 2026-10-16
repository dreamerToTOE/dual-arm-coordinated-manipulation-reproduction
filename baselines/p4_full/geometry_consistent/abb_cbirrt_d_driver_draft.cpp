// Project-owned transport to the actual author CBiRRT and SVC bodies.
// argv: II|III MESH_WORK_DIRECTORY distance|local|solve plain|trace
// No mode is executed by the engineering builder. Science requires new freezes.
#include "abb_cbirrt_d_observation_draft.hpp"
#include "CBiRRT_PCS.h"
#include <ompl/base/ScopedState.h>
#include <ompl/base/ProblemDefinition.h>
#include <ompl/base/PlannerData.h>
#include <ompl/base/PlannerTerminationCondition.h>
#include <ompl/geometric/PathGeometric.h>
#include <ompl/util/RandomNumbers.h>
#include <cmath>
#include <chrono>
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
std::vector<double> finite12(const p4cb::json& value) {
    auto q=value.get<std::vector<double>>();
    if(q.size()!=12)throw std::runtime_error("FINITE_Q12_REQUIRED");
    for(double x:q)if(!std::isfinite(x))throw std::runtime_error("FINITE_Q12_REQUIRED");
    return q;
}
void put(ob::ScopedState<ob::RealVectorStateSpace>& state,const std::vector<double>& q) {
    for(unsigned i=0;i<12;++i)state[i]=q[i];
}
class Probe final:public og::CBiRRT {
public:
    Probe(const ob::SpaceInformationPtr& si,double range,int env):og::CBiRRT(si,range,env){}
    double distance(const ob::State* a,const ob::State* b,int role) {
        // Borrow two real ScopedState allocations. Motion destructor is empty;
        // these motions never enter the search trees or own the borrowed state.
        Motion ma,mb;ma.state=const_cast<ob::State*>(a);mb.state=const_cast<ob::State*>(b);
        active_chain=role;
        return activeDistance(&ma,&mb);
    }
    p4cb::json snapshot() const {
        p4cb::json nodes=p4cb::json::array();std::map<const ob::State*,unsigned long> state_to_motion;
        for(const auto& side:{tStart_,tGoal_})if(side) {
            std::vector<Motion*> motions;side->list(motions);
            for(auto* m:motions)state_to_motion[m->state]=p4cb::identity(m);
        }
        unsigned side_index=0;
        for(const auto& side:{tStart_,tGoal_}) {
            if(side) {
                std::vector<Motion*> motions;side->list(motions);
                for(auto* m:motions)nodes.push_back({{"motion_id",p4cb::identity(m)},
                    {"tree",side_index==0?"start":"goal"},{"state_id",p4cb::identity(m->state)},
                    {"parent_motion_id",p4cb::identity(m->parent)},
                    {"root_state_id",p4cb::identity(m->root)},
                    {"root_motion_id",state_to_motion.at(m->root)},
                    {"q12",p4cb::q12(m->state)},{"root_q12",p4cb::q12(m->root)},
                    {"ik_q1_active",m->ik_q1_active},{"ik_q2_active",m->ik_q2_active},{"a_chain",m->a_chain}});
            }
            ++side_index;
        }
        auto connected=[&](const ob::State* state)->p4cb::json {
            if(!state)return nullptr;
            auto found=state_to_motion.find(state);
            return {{"state_id",p4cb::identity(state)},
                {"motion_id",found==state_to_motion.end()?p4cb::json(nullptr):p4cb::json(found->second)},
                {"q12",p4cb::q12(state)}};
        };
        return {{"nodes",nodes},{"connection_start",connected(connectionPoint_.first)},
            {"connection_goal",connected(connectionPoint_.second)},
            {"node_identity_policy","Actual Motion/state identities; equal q never merged."}};
    }
};
void attach_observation(p4cb::json& result) {
    result["source_counts_observed"]=p4cb::enabled;
    result["source_started"]=p4cb::enabled?p4cb::json(p4cb::started):p4cb::json(nullptr);
    result["source_completed"]=p4cb::enabled?p4cb::json(p4cb::completed):p4cb::json(nullptr);
    result["trace"]=p4cb::enabled?p4cb::events:p4cb::json(nullptr);
}
}
int main(int argc,char** argv) {
    if(argc!=5)return 64;
    const std::string env=argv[1],operation=argv[3],mode=argv[4];
    if((env!="II"&&env!="III")||(operation!="distance"&&operation!="local"&&operation!="solve")
            ||(mode!="plain"&&mode!="trace")||(operation=="solve"&&(env!="II"||mode!="trace")))return 64;
    try {
        const fs::path work=fs::absolute(argv[2]);
        if(!fs::is_directory(work/"simulator"))throw std::runtime_error("MESH_WORK_DIRECTORY_REQUIRED");
        fs::current_path(work);
        if(operation=="solve") {
            // Runner must make this an exclusive child of a new run. Both
            // author's original relative outputs then stay inside that run.
            if(fs::exists("paths")||fs::exists("../paths"))throw std::runtime_error("BOTH_ORIGINAL_PATHS_MUST_BE_ABSENT");
            if(!fs::create_directory("paths")||!fs::create_directory("../paths"))throw std::runtime_error("FRESH_PATHS_CREATION_FAILED");
        }
        p4cb::enabled=(mode=="trace");p4cb::reset();
        if(operation!="local")ompl::RNG::setSeed(7);
        if(operation=="solve")std::srand(7);
        auto space=std::make_shared<ob::RealVectorStateSpace>(12);
        ob::RealVectorBounds bounds(12);
        const std::vector<double> lo={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416},
            hi={2.88,1.919,1.22,2.79,2.09,3.1416};
        for(unsigned i=0;i<12;++i){bounds.setLow(i,lo[i%6]);bounds.setHigh(i,hi[i%6]);}
        space->setBounds(bounds);auto si=std::make_shared<ob::SpaceInformation>(space);
        std::unique_ptr<Probe> planner;std::unique_ptr<StateValidityChecker> checker;
        {Redirect quiet;
            if(operation=="local") {checker=std::make_unique<StateValidityChecker>(si,env=="II"?1:2);checker->defaultSettings();checker->initiate_log_parameters();}
            else planner=std::make_unique<Probe>(si,env=="II"?2.6:1.,env=="II"?1:2);
        }
        p4cb::json construction={{"cbirrt_constructor_dispatch_completed",planner?1:0},
            {"svc_only_constructor_dispatch_completed",checker?1:0},
            {"ompl_setSeed_calls_completed",operation=="local"?0:1},
            {"srand_calls_completed",operation=="solve"?1:0},
            {"source_direct_rng_member_initializations_structural",planner?1:0},
            {"source_direct_rng_member_true_started_completed","UNOBSERVED_LIBRARY_NOT_HOOKED"},
            {"library_internal_seed_draws","UNOBSERVED_NOT_REPORTED_ZERO"}};
        attach_observation(construction);
        unsigned requests=0;std::string line;
        while(std::getline(std::cin,line)) {
            if(++requests>(operation=="solve"?1u:8u))throw std::runtime_error("TRANSPORT_REQUEST_CAP_NO_RETRY");
            p4cb::reset();
            p4cb::json out={{"schema","P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1"},
                {"environment",env},{"mode",mode},{"operation",operation},{"construction",construction},
                {"status","STOP_RETAINED_PREFIX"},{"source_dispatch_started",0},{"source_dispatch_completed",0},
                {"solve_calls",0},{"formal_table_I_calls",0},{"independent_path_qualified",false}};
            try {
                auto request=p4cb::json::parse(line);out["request"]=request;
                if(request.at("environment")!=env||request.at("operation")!=operation)throw std::runtime_error("REQUEST_MODE_ENVIRONMENT_MISMATCH");
                if(operation=="distance"||operation=="local") {
                    auto qa=finite12(request.at("qa12")),qb=finite12(request.at("qb12"));
                    const int role=request.at("active_chain").get<int>();
                    if(role!=0&&role!=1)throw std::runtime_error("ROLE_0_OR_1_REQUIRED");
                    int branch=-1;std::string call;
                    if(operation=="local") {
                        branch=request.at("branch").get<int>();call=request.at("local_call").get<std::string>();
                        if(branch<0||branch>7)throw std::runtime_error("ORIGINAL_BRANCH_0_TO_7_REQUIRED");
                        if(call!="rbs"&&call!="reconstruct")throw std::runtime_error("EXACT_LOCAL_CALL_REQUIRED");
                    }
                    ob::ScopedState<ob::RealVectorStateSpace> a(space),b(space);put(a,qa);put(b,qb);
                    out["source_dispatch_started"]=1;
                    {Redirect quiet;
                        if(operation=="distance")out["distance"]=planner->distance(a.get(),b.get(),role);
                        else {
                            Matrix path;
                            if(call=="rbs")out["returned"]=checker->checkMotionRBS(a.get(),b.get(),role,branch);
                            else if(call=="reconstruct") {out["returned"]=checker->reconstructRBS(a.get(),b.get(),path,role,branch);out["path_q12"]=path;}
                        }
                    }
                    out["source_dispatch_completed"]=1;
                    out["qa12_after"]=p4cb::q12(a.get());out["qb12_after"]=p4cb::q12(b.get());
                    out["qa12_binary64_after"]=p4cb::binary64(p4cb::q12(a.get()));
                    out["qb12_binary64_after"]=p4cb::binary64(p4cb::q12(b.get()));
                    out["status"]="SOURCE_INTERFACE_COMPLETED_NOT_QUALIFIED";
                } else {
                    if(request.at("seed")!=7||request.at("range_rad")!=2.6||request.at("solve_seconds")!=10.)
                        throw std::runtime_error("II_SEED7_RANGE26_SOLVE10_REQUIRED");
                    auto start=finite12(request.at("start_q12")),goal=finite12(request.at("goal_q12"));
                    si->setStateValidityChecker([](const ob::State*){return true;});
                    si->setStateValidityCheckingResolution(.02);si->setup();
                    ob::ScopedState<ob::RealVectorStateSpace> a(space),b(space);put(a,start);put(b,goal);
                    auto problem=std::make_shared<ob::ProblemDefinition>(si);problem->setStartAndGoalStates(a,b);
                    planner->setProblemDefinition(problem);planner->setup();
                    out["source_dispatch_started"]=1;out["solve_calls"]=1;
                    const auto solve_begun=std::chrono::steady_clock::now();
                    {Redirect quiet;
                        const auto status=planner->solve(ob::timedPlannerTerminationCondition(10.));
                        out["planner_status"]=status.asString();
                        out["planner_status_code"]=static_cast<int>(static_cast<ob::PlannerStatus::StatusType>(status));
                    }
                    out["solve_wall_s"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-solve_begun).count();
                    out["solve_wall_scope"]="Whole original solve including original save2file and observation I/O; not a paper timing sample.";
                    out["source_dispatch_completed"]=1;out["exact"]=problem->hasExactSolution();
                    out["has_solution"]=problem->hasSolution();out["approximate"]=problem->hasApproximateSolution();
                    out["solution_count"]=problem->getSolutionCount();
                    out["solution_difference"]=problem->hasSolution()?p4cb::json(problem->getSolutionDifference()):p4cb::json(nullptr);
                    out["trees"]=planner->snapshot();out["milestones_q12"]=p4cb::json::array();
                    if(problem->hasSolution()) {
                        auto path=std::dynamic_pointer_cast<og::PathGeometric>(problem->getSolutionPath());
                        if(!path)throw std::runtime_error("GEOMETRIC_PATH_REQUIRED");
                        for(auto* state:path->getStates())out["milestones_q12"].push_back(p4cb::q12(state));
                    }
                    // Author getPlannerData unconditionally adds its bridge;
                    // call only when a genuine exact solution supplies it.
                    if(problem->hasExactSolution()) {
                        ob::PlannerData data(si);{Redirect quiet;planner->getPlannerData(data);}
                        p4cb::json vertices=p4cb::json::array(),edges=p4cb::json::array();
                        for(unsigned i=0;i<data.numVertices();++i) {
                            vertices.push_back({{"index",i},{"q12",p4cb::q12(data.getVertex(i).getState())},
                                {"state_id",p4cb::identity(data.getVertex(i).getState())},
                                {"tag",data.getVertex(i).getTag()},{"start",data.isStartVertex(i)},{"goal",data.isGoalVertex(i)}});
                            std::vector<unsigned> children;data.getEdges(i,children);for(auto child:children)edges.push_back({i,child});
                        }
                        out["planner_data"]={{"vertices",vertices},{"edges",edges}};
                    } else out["planner_data"]=nullptr;
                    out["status"]=problem->hasExactSolution()?"SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT":"SOURCE_NONEXACT_RETAINED_PREFIX";
                }
            } catch(const std::exception& error) {out["error"]=error.what();}
            attach_observation(out);std::cout<<out.dump()<<std::endl;
            if(out["status"]=="STOP_RETAINED_PREFIX")return 2;
        }
        return 0;
    } catch(const std::exception& error) {std::cerr<<"P4_CBIRRT_D_TRANSPORT_ERROR "<<error.what()<<std::endl;return 3;}
}
