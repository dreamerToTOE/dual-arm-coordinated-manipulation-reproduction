// Project-owned CBiRRT_NR observations. No model evaluation or RNG draws.
// The immutable previously qualified physical GD translation unit is reused.
#pragma once
#include "abb_nr_interface_observation_draft.hpp"
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <map>
#include <sstream>
namespace p4cbnr {
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
inline unsigned long identity(const void* value) {
    if(!value)return 0;
    auto found=identities.find(value);
    if(found!=identities.end())return found->second;
    auto id=identities.size()+1;identities[value]=id;return id;
}
inline std::string binary64(const std::vector<double>& q) {
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(double v:q){std::uint64_t u;std::memcpy(&u,&v,sizeof u);out<<std::setw(16)<<u;}
    return out.str();
}
inline void reset(){serial=0;started.clear();completed.clear();identities.clear();events=json::array();}
inline void emit(const json& value) {
    if(enabled){events.push_back(value);std::cerr<<"P4_CBIRRT_NR_TRACE "<<value.dump()<<std::endl;}
}
inline unsigned long enter(const std::string& kind,const json& args) {
    if(!enabled)return 0;
    auto id=++serial;++started[kind];emit({{"event","entered"},{"id",id},{"kind",kind},{"args",args}});return id;
}
inline void leave(unsigned long id,const std::string& kind,const json& result) {
    if(enabled){++completed[kind];emit({{"event","completed"},{"id",id},{"kind",kind},{"result",result}});}
}
inline void mark(const std::string& kind,const json& args) {
    if(enabled)emit({{"event","observed"},{"id",++serial},{"kind",kind},{"args",args}});
}
} // namespace p4cbnr
