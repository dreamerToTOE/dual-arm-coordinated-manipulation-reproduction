// Thin JSONL transport: call exactly IKproject(q1,q2,active_chain).
// Final physical/branch/collision checks belong to a separately frozen runner.
#include "abb_helper_observation_draft.hpp"
#include "StateValidityCheckerPCS.h"
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <memory>
#include <stdexcept>
namespace {
class Redirect {
    std::streambuf* previous;
public:
    Redirect():previous(std::cout.rdbuf(std::cerr.rdbuf())){}
    ~Redirect(){std::cout.rdbuf(previous);}
};
State q12(const p4helper::json& j) {
    auto q=j.get<State>();
    if(q.size()!=12)throw std::runtime_error("EXPECTED_FINITE_Q12");
    for(auto v:q)if(!std::isfinite(v))throw std::runtime_error("EXPECTED_FINITE_Q12");
    return q;
}
State join(const State& a,const State& b) {State q=a;q.insert(q.end(),b.begin(),b.end());return q;}
}
int main(int argc,char** argv) {
    if(argc!=4)return 64;
    std::string env=argv[1],mode=argv[3];
    if((env!="II"&&env!="III")||(mode!="plain"&&mode!="trace"))return 64;
    std::filesystem::current_path(argv[2]);
    std::unique_ptr<StateValidityChecker> checker;
    {Redirect quiet;checker=std::make_unique<StateValidityChecker>(env=="II"?1:2);}
    checker->initiate_log_parameters();
    p4helper::enabled=(mode=="trace");
    std::string line;
    while(std::getline(std::cin,line)) {
        p4helper::reset();
        p4helper::json out={{"schema","P4_ABB_RANDOM_HELPER_TRANSPORT_DRAFT_V1"},
            {"environment",env},{"mode",mode},{"helper_dispatch_started",0},
            {"helper_dispatch_completed",0},{"srand_calls_completed",0},
            {"rand_started_completed","UNOBSERVED_SOURCE_STDLIB_NOT_INFERRED"},
            {"post_helper_model_calls",0},{"source_counts_observed",p4helper::enabled}};
        try {
            auto req=p4helper::json::parse(line);out["request"]=req;
            if(req.at("operation")!="random_three_argument_helper"||req.at("environment")!=env)
                throw std::runtime_error("REQUEST_OPERATION_OR_ENVIRONMENT_MISMATCH");
            auto input=q12(req.at("q12"));int active=req.at("active_chain").get<int>();
            unsigned int seed=req.at("seed").get<unsigned int>();
            if((active!=0&&active!=1)||(seed!=7&&seed!=17))throw std::runtime_error("FIXED_ROLE_SEED_REQUIRED");
            State a(input.begin(),input.begin()+6),b(input.begin()+6,input.end());
            // The author's unmodified std::random_shuffle consumes the RNG.
            std::srand(seed);out["srand_calls_completed"]=1;
            out["helper_dispatch_started"]=1;
            bool returned;
            {Redirect quiet;returned=checker->IKproject(a,b,active);}
            out["helper_dispatch_completed"]=1;
            out["returned"]=returned;out["q12"]=join(a,b);
            out["candidate_is_finite"]=true;
            for(auto v:join(a,b))if(!std::isfinite(v))out["candidate_is_finite"]=false;
            out["status"]="SOURCE_HELPER_COMPLETED";
        } catch(const std::exception& e) {out["status"]="STOP_RETAINED_PREFIX";out["error"]=e.what();}
        if(p4helper::enabled) {
            out["source_started"]=p4helper::started;out["source_completed"]=p4helper::completed;
            out["trace"]=p4helper::events;
        } else {out["source_started"]=nullptr;out["source_completed"]=nullptr;out["trace"]=nullptr;}
        std::cout<<out.dump()<<std::endl;
        if(out["status"]!="SOURCE_HELPER_COMPLETED")return 2;
    }
}
