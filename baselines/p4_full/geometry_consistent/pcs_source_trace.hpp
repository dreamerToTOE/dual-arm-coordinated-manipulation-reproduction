// Project-owned observation and finite-call guards; no author algorithm body.
#pragma once
#include <nlohmann/json.hpp>
#include <PQP.h>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>
namespace p4pcs {
using json=nlohmann::json;
inline bool enabled=false;
inline std::map<std::string,int> counts;
inline std::map<std::string,int> caps={{"project_fixed",64},{"rbs",128},
    {"reconstruct",128},{"native_fk",256},{"native_ik",64},
    {"collision",64},{"pqp",8192}};
inline std::vector<std::vector<double>> projected;
inline unsigned long serial=0;
inline void emit(const json& event) { if(enabled) std::cerr<<"P4_PCS_TRACE "<<event.dump()<<std::endl; }
inline void reset() { counts.clear();projected.clear();serial=0; }
inline unsigned long enter(const std::string& kind,const json& args) {
    if(!enabled)return 0;
    if(caps.count(kind)&&counts[kind]>=caps.at(kind)) {
        emit({{"event","cap_reached"},{"kind",kind},{"counts",counts}});
        throw std::runtime_error("P4_SOURCE_CALL_CAP_"+kind);
    }
    ++counts[kind];auto id=++serial;
    emit({{"event","entered"},{"kind",kind},{"id",id},{"args",args}});return id;
}
inline void leave(unsigned long id,const std::string& kind,const json& result) {
    if(!enabled)return;
    emit({{"event","completed"},{"kind",kind},{"id",id},{"result",result}});
    if(kind=="project_fixed"&&result.at("returned").get<bool>()) {
        auto q=result.at("q1").get<std::vector<double>>();
        auto b=result.at("q2").get<std::vector<double>>();q.insert(q.end(),b.begin(),b.end());
        projected.push_back(q);
    }
}
inline int query(PQP_ToleranceResult* result,PQP_REAL r1[3][3],PQP_REAL t1[3],
                 PQP_Model* a,PQP_REAL r2[3][3],PQP_REAL t2[3],PQP_Model* b,
                 PQP_REAL tolerance,int queue_size=2) {
    auto id=enter("pqp",{{"tolerance",tolerance},{"queue_size",queue_size}});
    int code=PQP_Tolerance(result,r1,t1,a,r2,t2,b,tolerance,queue_size);
    leave(id,"pqp",{{"code",code}});return code;
}
}
