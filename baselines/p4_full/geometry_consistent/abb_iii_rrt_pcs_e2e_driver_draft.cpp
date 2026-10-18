// Project-owned environment III thin entry; derived from qualified II driver, source unchanged.
// argv: NEW_RUN_DIRECTORY; stdin: one frozen request JSON; no fallback/retry.
#include "abb_rrt_pcs_e2e_observation.hpp"
#include "RRT_PCS.h"
#include <ompl/base/PlannerData.h>
#include <ompl/base/PlannerTerminationCondition.h>
#include <ompl/base/ProblemDefinition.h>
#include <ompl/base/ScopedState.h>
#include <ompl/geometric/PathGeometric.h>
#include <ompl/util/RandomNumbers.h>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <memory>
#include <sstream>

namespace ob=ompl::base;
namespace og=ompl::geometric;
namespace fs=std::filesystem;
namespace {
std::vector<double> finite12(const p4e2e::json& value) {
    auto q=value.get<std::vector<double>>();
    if(q.size()!=12)throw std::runtime_error("EXPECTED_Q12");
    for(double x:q)if(!std::isfinite(x))throw std::runtime_error("NONFINITE_Q12");
    return q;
}
double elapsed(std::chrono::steady_clock::time_point start) {
    return std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
}
}
int main(int argc,char** argv) {
    if(argc!=2)return 64;
    const fs::path run=fs::absolute(argv[1]);
    p4e2e::json result={{"schema","P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1"},
        {"status","STOP_RETAINED_PREFIX"},{"solve_calls",0},
        {"formal_table_I_calls",0},{"independent_path_qualified",false},
        {"full_physical_geometry_or_CCD_qualified",false}};
    try {
        if(!fs::is_directory(run)||!fs::is_directory(run/"simulator")||fs::exists(run/"paths"))
            throw std::runtime_error("FRESH_RUN_SIMULATOR_AND_ABSENT_PATHS_REQUIRED");
        // paths is a new empty output directory, never a copied author path.
        fs::create_directory(run/"paths");fs::current_path(run);
        p4e2e::reconstruction_fd=p4e2e::exclusive("reconstruction_attempts.jsonl");
        p4e2e::identify_fd=p4e2e::exclusive("identify_observations.jsonl");
        std::string input;std::getline(std::cin,input);std::string extra;
        while(std::getline(std::cin,extra))if(!extra.empty())throw std::runtime_error("EXACTLY_ONE_REQUEST_REQUIRED");
        auto request=p4e2e::json::parse(input);
        const auto start=finite12(request.at("start_q12")),goal=finite12(request.at("goal_q12"));
        if(request.at("environment")!="III"||request.at("seed")!=7||request.at("range_rad")!=.8
                ||request.at("goal_bias")!=.05||request.at("solve_seconds")!=10.)
            throw std::runtime_error("FROZEN_III_SEED7_RANGE08_GOAL005_SOLVE10_REQUIRED");
        // Original plan_PCS.cpp sampler box, including its restricted q6.
        const std::vector<double> arm_low={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416};
        const std::vector<double> arm_high={2.88,1.919,1.22,2.79,2.09,3.1416};
        std::vector<double> low=arm_low,high=arm_high;
        low.insert(low.end(),arm_low.begin(),arm_low.end());
        high.insert(high.end(),arm_high.begin(),arm_high.end());
        if(request.at("bounds_low_rad")!=low||request.at("bounds_high_rad")!=high)
            throw std::runtime_error("FROZEN_ORIGINAL_MAIN_SAMPLER_BOUNDS_REQUIRED");
        result.update({{"request",request},{"environment","III"},{"seed",7},
            {"start_q12",start},{"goal_q12",goal},{"range_rad",.8},{"goal_bias",.05},
            {"bounds_low_rad",low},{"bounds_high_rad",high},
            {"state_validity_callback","ORIGINAL_MAIN_ALWAYS_TRUE_NO_FK"},
            {"solution_path_simplification",false}});
        p4e2e::write_new_json("request_observed.json",request);
        ompl::RNG::setSeed(7);std::srand(7);
        auto space=std::make_shared<ob::RealVectorStateSpace>(12);
        ob::RealVectorBounds bounds(12);
        for(int i=0;i<12;++i){bounds.setLow(i,low[i]);bounds.setHigh(i,high[i]);}
        space->setBounds(bounds);
        auto si=std::make_shared<ob::SpaceInformation>(space);
        si->setStateValidityChecker([](const ob::State*){return true;});
        si->setStateValidityCheckingResolution(.02);si->setup();
        ob::ScopedState<ob::RealVectorStateSpace> s(space),g(space);
        for(int i=0;i<12;++i){s[i]=start[i];g[i]=goal[i];}
        auto pdef=std::make_shared<ob::ProblemDefinition>(si);pdef->setStartAndGoalStates(s,g);
        auto planner=std::make_shared<og::RRT>(si,.8,2);
        planner->setGoalBias(.05);planner->setProblemDefinition(pdef);planner->setup();
        auto begun=std::chrono::steady_clock::now();result["solve_calls"]=1;
        auto status=planner->solve(ob::timedPlannerTerminationCondition(10.));
        result["solve_wall_s"]=elapsed(begun);
        result["planner_status"]=status.asString();
        result["planner_status_code"]=static_cast<int>(static_cast<ob::PlannerStatus::StatusType>(status));
        result["exact"]=pdef->hasExactSolution();result["approximate"]=pdef->hasApproximateSolution();
        result["has_solution"]=pdef->hasSolution();result["solution_count"]=pdef->getSolutionCount();
        result["solution_difference"]=pdef->hasSolution()?p4e2e::json(pdef->getSolutionDifference()):p4e2e::json(nullptr);
        result["milestones_q12"]=p4e2e::json::array();
        if(pdef->hasSolution()) {
            auto path=std::dynamic_pointer_cast<og::PathGeometric>(pdef->getSolutionPath());
            if(!path)throw std::runtime_error("NON_GEOMETRIC_SOLUTION_PATH");
            for(auto* state:path->getStates())result["milestones_q12"].push_back(p4e2e::q12(state));
        }
        ob::PlannerData data(si);planner->getPlannerData(data);
        p4e2e::json vertices=p4e2e::json::array(),edges=p4e2e::json::array();
        for(unsigned i=0;i<data.numVertices();++i) {
            vertices.push_back({{"index",i},{"q12",p4e2e::q12(data.getVertex(i).getState())},
                {"start",data.isStartVertex(i)},{"goal",data.isGoalVertex(i)}});
            std::vector<unsigned> children;data.getEdges(i,children);
            for(unsigned child:children)edges.push_back({i,child});
        }
        result["planner_data"]={{"vertices",vertices},{"edges",edges},
            {"num_vertices",data.numVertices()},{"num_edges",data.numEdges()}};
        result["status"]="SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT";
    } catch(const std::exception& error) {result["error"]=error.what();}
    result["reconstruction_attempts"]=p4e2e::reconstruction_attempts;
    result["identify_observation_count"]=p4e2e::identify_count;
    result["reconstruction_calls_completed_observed"]=p4e2e::reconstruction_attempts.size();
    result["identify_calls_completed_observed"]=p4e2e::identify_count;
    result["reconstruction_true_started"]="UNOBSERVED_NO_START_HOOK";
    result["identify_true_started"]="UNOBSERVED_NO_START_HOOK";
    try {
        if(p4e2e::reconstruction_fd>=0) {::fsync(p4e2e::reconstruction_fd);::close(p4e2e::reconstruction_fd);}
        if(p4e2e::identify_fd>=0) {::fsync(p4e2e::identify_fd);::close(p4e2e::identify_fd);}
        p4e2e::write_new_json((run/"result.json").string(),result);
        std::cout<<result.dump()<<std::endl;
    } catch(const std::exception& error) {std::cerr<<"P4_RESULT_EVIDENCE_ERROR "<<error.what()<<std::endl;return 3;}
    return result["status"]=="SOURCE_SOLVE_RETURNED_PENDING_INDEPENDENT_PATH_AUDIT"?0:2;
}
