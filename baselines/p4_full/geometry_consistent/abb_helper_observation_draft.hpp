// Project-owned observations for the actual author three-argument helper.
// No guards, RNG, FK/IK calls, collision queries, or algorithm substitutes.
#pragma once
#include <nlohmann/json.hpp>
#include <iostream>
#include <map>
#include <string>
#include <vector>
namespace p4helper {
using json=nlohmann::json;
inline bool enabled=false;
inline unsigned long serial=0;
inline std::map<std::string,unsigned long> started,completed;
inline json events=json::array();
inline void reset() { serial=0;started.clear();completed.clear();events=json::array(); }
inline void emit(json e) {
    if(!enabled)return;
    events.push_back(e);
    // Preserve the last observed source entry even if the source never returns.
    std::cerr<<"P4_HELPER_TRACE "<<e.dump()<<std::endl;
}
inline unsigned long enter(const std::string& kind,const json& args) {
    if(!enabled)return 0;
    auto id=++serial;++started[kind];
    emit({{"event","entered"},{"id",id},{"kind",kind},{"args",args}});return id;
}
inline void leave(unsigned long id,const std::string& kind,const json& value) {
    if(!enabled)return;
    ++completed[kind];
    emit({{"event","completed"},{"id",id},{"kind",kind},{"result",value}});
}
inline void mark(const std::string& kind,const json& args) {
    if(enabled)emit({{"event","observed"},{"id",++serial},{"kind",kind},{"args",args}});
}
}
