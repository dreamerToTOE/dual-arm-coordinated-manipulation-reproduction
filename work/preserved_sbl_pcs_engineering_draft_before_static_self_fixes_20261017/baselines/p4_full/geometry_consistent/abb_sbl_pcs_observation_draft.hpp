// Project-owned SBL observations. No model evaluation or RNG draws.
#pragma once
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <nlohmann/json.hpp>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
namespace p4sbl {
using json=nlohmann::json;
inline bool enabled=false;
inline unsigned long serial=0,next_lifetime=0,next_state=0,connection_scope=0;
inline std::map<std::string,unsigned long> started,completed;
inline json events=json::array();
struct Lifetime {unsigned long id,generation,state_id;const void* state;bool a_chain_initialized;std::string origin;};
inline std::map<const void*,Lifetime> live;
inline std::map<const void*,unsigned long> generations;
inline std::map<const void*,unsigned long> state_to_motion;
inline std::map<const void*,std::string> tree_names;
inline void require(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
inline std::vector<double> q12(const ompl::base::State* state) {
    const auto* s=state->as<ompl::base::RealVectorStateSpace::StateType>();
    return std::vector<double>(s->values,s->values+12);
}
inline std::vector<double> joined(const std::vector<double>& a,const std::vector<double>& b){auto q=a;q.insert(q.end(),b.begin(),b.end());return q;}
inline std::string binary64(const std::vector<double>& q){std::ostringstream o;o<<std::hex<<std::setfill('0');for(double x:q){std::uint64_t u;std::memcpy(&u,&x,sizeof u);o<<std::setw(16)<<u;}return o.str();}
inline void emit(const json& e){if(enabled){events.push_back(e);std::cerr<<"P4_SBL_PCS_TRACE "<<e.dump()<<std::endl;}}
inline unsigned long enter(const std::string& kind,const json& args){if(!enabled)return 0;auto id=++serial;++started[kind];emit({{"event","entered"},{"id",id},{"kind",kind},{"args",args}});return id;}
inline void leave(unsigned long id,const std::string& kind,const json& value){if(enabled){++completed[kind];emit({{"event","completed"},{"id",id},{"kind",kind},{"result",value}});}}
inline void mark(const std::string& kind,const json& value){if(enabled)emit({{"event","observed"},{"id",++serial},{"kind",kind},{"args",value}});}
inline void reset(){require(live.empty()&&connection_scope==0,"NO_RESET_WHILE_SBL_OBJECTS_LIVE");serial=0;next_lifetime=0;next_state=0;started.clear();completed.clear();events=json::array();generations.clear();state_to_motion.clear();tree_names.clear();}
inline void bind_tree(const void* tree,const std::string& name){require(!tree_names.count(tree),"TREE_ALREADY_BOUND");tree_names.emplace(tree,name);}
inline unsigned long identity(const void* p){if(!p)return 0;auto it=live.find(p);require(it!=live.end(),"LIVE_MOTION_ID_REQUIRED_NO_IMPLICIT_CREATION");return it->second.id;}
struct ConnectionScope {ConnectionScope(){++connection_scope;}~ConnectionScope(){--connection_scope;}ConnectionScope(const ConnectionScope&)=delete;};
template<class Motion> json snapshot(Motion* m) {
    if(!m)return nullptr;
    const auto& x=live.at(m);
    auto root=state_to_motion.find(m->root);require(root!=state_to_motion.end(),"LIVE_ROOT_STATE_REQUIRED");
    return {{"motion_id",x.id},{"address_generation",x.generation},{"state_id",x.state_id},
        {"parent_motion_id",identity(m->parent)},{"root_motion_id",root->second},{"q12",q12(m->state)},
        {"ik_q1_active",m->ik_q1_active},{"ik_q2_active",m->ik_q2_active},{"valid",m->valid},
        {"a_chain",x.a_chain_initialized?json(m->a_chain):json(nullptr)},
        {"a_chain_provenance",x.a_chain_initialized?x.origin:"UNINITIALIZED_NOT_READ"}};
}
template<class Motion> json register_motion(const void* tree,Motion* m) {
    require(!live.count(m)&&!state_to_motion.count(m->state),"MOTION_OR_STATE_ALREADY_LIVE");
    require(tree_names.count(tree),"BIND_BOTH_ORIGINAL_SBL_TREES_BEFORE_SOLVE");
    const bool connect=connection_scope!=0;
    Lifetime x{++next_lifetime,++generations[m],++next_state,m->state,!connect,connect?"CHECKSOLUTION_CONNECT":(m->parent?"GROW_ASSIGNED":"ROOT_ASSIGNED")};
    live.emplace(m,x);state_to_motion.emplace(m->state,x.id);
    auto value=snapshot(m);value["tree"]=tree_names.at(tree);mark("motion_lifetime_registered",value);return value;
}
struct Retirement {const void* address;const void* state;unsigned long id;json before;};
template<class Motion> Retirement prepare_retirement(Motion* m) {
    const auto& x=live.at(m);auto before=snapshot(m);json children=json::array();
    for(auto* child:m->children)children.push_back(snapshot(child));
    before["original_children_before_parent_null"]=children;
    mark("motion_before_native_retirement",before);return {m,x.state,x.id,before};
}
inline void retire(const Retirement& item){auto it=live.find(item.address);require(it!=live.end()&&it->second.id==item.id,"RETIRE_EXACT_LIFETIME_TOKEN");mark("motion_lifetime_retired",item.before);state_to_motion.erase(item.state);live.erase(it);}
template<class Grid> std::vector<Retirement> prepare_grid(Grid& grid){std::vector<Retirement> tokens;for(auto it=grid.begin();it!=grid.end();++it)for(unsigned i=0;i<it->second->data.size();++i)tokens.push_back(prepare_retirement(it->second->data[i]));return tokens;}
inline void retire_grid(const std::vector<Retirement>& tokens){for(const auto& item:tokens)retire(item);}
template<class Paths> json paths_snapshot(const Paths& first,const Paths& second){json result=json::array();for(const auto& side:{first,second}){json out=json::array();for(auto* m:side)out.push_back(snapshot(m));result.push_back(out);}return result;}
} // namespace p4sbl
