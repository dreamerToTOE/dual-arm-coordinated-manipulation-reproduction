// Project-owned thin JSONL transport. Link the external author's three PCS
// searchers for interface/build qualification; never allocate or solve a planner.
#include "pcs_source_trace.hpp"
#include "StateValidityCheckerPCS.h"
#include <filesystem>
#include <cmath>
#include <memory>
#include <sstream>

namespace {
class Redirect {
    std::streambuf* old;
public: Redirect():old(std::cout.rdbuf(std::cerr.rdbuf())){}
    ~Redirect(){std::cout.rdbuf(old);}
};
State state(const p4pcs::json& j) {
    State q=j.get<State>();
    if(q.size()!=12)throw std::runtime_error("EXPECTED_Q12");
    for(double x:q)if(!std::isfinite(x))throw std::runtime_error("NONFINITE_Q");
    return q;
}
std::pair<State,State> split(const State& q){return {{q.begin(),q.begin()+6},{q.begin()+6,q.end()}};}
State join(const State& a,const State& b){State q=a;q.insert(q.end(),b.begin(),b.end());return q;}
}
int main(int argc,char** argv) {
    if(argc!=4)return 64;
    const std::string env=argv[1];
    if(env!="II"&&env!="III")return 64;
    const bool trace=std::string(argv[3])=="trace";
    if(!trace&&std::string(argv[3])!="plain")return 64;
    std::filesystem::current_path(argv[2]);
    std::unique_ptr<StateValidityChecker> checker;
    {Redirect redirect;checker=std::make_unique<StateValidityChecker>(env=="II"?1:2);}
    checker->initiate_log_parameters();
    p4pcs::enabled=trace;
    std::string line;
    while(std::getline(std::cin,line)) {
        p4pcs::reset();
        p4pcs::json result={{"schema","P4_ABB_PCS_THIN_V1"},{"environment",env},
            {"trace_enabled",trace},{"solve_calls",0},{"rng_calls",0}};
        try {
            auto request=p4pcs::json::parse(line);result["request"]=request;
            const auto op=request.at("op").get<std::string>();
            if(op=="limits") {
                auto q=state(request.at("q12"));result["source_limits_legal"]=checker->check_angle_limits(q);
            } else {
                int active=request.at("active_chain"),branch=request.at("branch");
                if(active<0||active>1||branch<0||branch>7)throw std::runtime_error("INVALID_FIXED_IDENTITY");
                if(op=="project") {
                    auto q=state(request.at("q12"));auto [a,b]=split(q);
                    bool ok=checker->IKproject(a,b,active,branch);
                    result["returned"]=ok;result["q12"]=join(a,b);
                } else if(op=="rbs"||op=="reconstruct") {
                    auto qa=state(request.at("qa12")),qb=state(request.at("qb12"));
                    auto [a,b]=split(qa);auto [c,d]=split(qb);
                    Matrix path={qa,qb};
                    result["returned"]=(op=="rbs" ? checker->checkMotionRBS(a,b,c,d,active,branch,0,0)
                        :checker->reconstructRBS(a,b,c,d,active,branch,path,0,1,1));
                    if(op=="reconstruct")result["path_q12"]=path;
                } else throw std::runtime_error("UNKNOWN_OPERATION");
            }
            // FK observation happens AFTER the top-level source call, so no
            // extra FK mutates author's T1/T2 inside its recursive algorithm.
            auto candidates=p4pcs::projected;
            if(!trace&&op=="project"&&result.at("returned").get<bool>())
                candidates.push_back(result.at("q12").get<State>());
            result["native_checks"]=p4pcs::json::array();
            for(const auto& q:candidates) {
                auto [a,b]=split(q);checker->FKsolve_rob(a,1);auto ta=checker->get_FK_solution_T1();
                checker->FKsolve_rob(b,2);auto tb=checker->get_FK_solution_T2();
                result["native_checks"].push_back({{"q12",q},{"poses",{ta,tb}},
                    {"source_limits_legal",checker->check_angle_limits(q)}});
            }
            result["status"]="SOURCE_CALL_COMPLETED";
        } catch(const std::exception& error) {
            result["status"]="STOP_RETAINED_PREFIX";result["error"]=error.what();
        }
        result["observed_counts"]=p4pcs::counts;
        std::cout<<result.dump()<<std::endl;
        if(result["status"]!="SOURCE_CALL_COMPLETED")return 2;
    }
}
