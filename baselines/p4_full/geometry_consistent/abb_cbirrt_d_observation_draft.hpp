// Project-owned read-only observations. No model evaluation or RNG draws.
#pragma once
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <nlohmann/json.hpp>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <sstream>
#include <iomanip>
#include <vector>
namespace p4cb {
using json=nlohmann::json;
inline bool enabled=false;
inline unsigned long serial=0;
inline std::map<std::string,unsigned long> started,completed;
inline std::map<const void*,unsigned long> identities;
inline json events=json::array();
inline std::vector<double> q12(const ompl::base::State* state) {
    const auto* s=state->as<ompl::base::RealVectorStateSpace::StateType>();
    return std::vector<double>(s->values,s->values+12);
}
inline std::vector<double> joined(const std::vector<double>& a,const std::vector<double>& b) {
    auto q=a;q.insert(q.end(),b.begin(),b.end());return q;
}
inline std::string binary64(const std::vector<double>& q) {
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(double v:q) {std::uint64_t u;std::memcpy(&u,&v,sizeof u);out<<std::setw(16)<<u;}
    return out.str();
}
inline unsigned long identity(const void* value) {
    if(!value)return 0;
    auto found=identities.find(value);
    if(found!=identities.end())return found->second;
    auto id=identities.size()+1;identities[value]=id;return id;
}
inline void reset() {serial=0;started.clear();completed.clear();identities.clear();events=json::array();}
inline void emit(const json& e) {
    if(!enabled)return;
    events.push_back(e);std::cerr<<"P4_CBIRRT_D_TRACE "<<e.dump()<<std::endl;
}
inline unsigned long enter(const std::string& kind,const json& args) {
    if(!enabled)return 0;
    auto id=++serial;++started[kind];emit({{"event","entered"},{"id",id},{"kind",kind},{"args",args}});return id;
}
inline void leave(unsigned long id,const std::string& kind,const json& value) {
    if(!enabled)return;
    ++completed[kind];emit({{"event","completed"},{"id",id},{"kind",kind},{"result",value}});
}
inline void mark(const std::string& kind,const json& value) {
    if(enabled)emit({{"event","observed"},{"id",++serial},{"kind",kind},{"args",value}});
}
}
