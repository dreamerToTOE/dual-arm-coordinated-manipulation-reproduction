// Versioned RECONSTRUCTED SBL writer metadata; independent new header, NOT built.
// Shadow values never initialize or write original Motion::a_chain storage.
// Unknown text sentinel -1 is paired with JSON null/provenance in an in-memory
// attempt buffer. No file writer or driver is supplied by this header.
#pragma once
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <nlohmann/json.hpp>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
namespace p4sbl {
using json=nlohmann::json;
inline bool enabled=false;
inline unsigned long serial=0,next_lifetime=0,next_state=0,connection_scope=0;
inline std::map<std::string,unsigned long> started,completed;
inline json events=json::array(),writer_metadata_attempts=json::array();
struct Lifetime {unsigned long id,generation,state_id;const void* state;std::optional<int> a_chain_shadow;std::string origin;};
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
inline void reset(){require(live.empty()&&connection_scope==0,"NO_RESET_WHILE_SBL_OBJECTS_LIVE");serial=0;next_lifetime=0;next_state=0;started.clear();completed.clear();events=json::array();writer_metadata_attempts=json::array();generations.clear();state_to_motion.clear();tree_names.clear();}
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
        {"a_chain",x.a_chain_shadow?json(*x.a_chain_shadow):json(nullptr)},
        {"a_chain_provenance",x.a_chain_shadow?x.origin:"UNINITIALIZED_NOT_READ"}};
}
template<class Motion> json register_motion(const void* tree,Motion* m) {
    require(!live.count(m)&&!state_to_motion.count(m->state),"MOTION_OR_STATE_ALREADY_LIVE");
    require(tree_names.count(tree),"BIND_BOTH_ORIGINAL_SBL_TREES_BEFORE_SOLVE");
    const bool connect=connection_scope!=0;
    // Fixed author addMotion sites: two roots and grow assign before this
    // observer; checkSolution connect never assigns, so never read its member.
    std::optional<int> shadow;
    if(!connect){const int assigned=m->a_chain;require(assigned==0||assigned==1,"AUTHOR_ASSIGNED_ACTIVE_ROLE_0_OR_1_REQUIRED");shadow=assigned;}
    Lifetime x{++next_lifetime,++generations[m],++next_state,m->state,shadow,connect?"CHECKSOLUTION_CONNECT":(m->parent?"GROW_ASSIGNED":"ROOT_ASSIGNED")};
    live.emplace(m,x);state_to_motion.emplace(m->state,x.id);
    auto value=snapshot(m);value["tree"]=tree_names.at(tree);mark("motion_lifetime_registered",value);return value;
}
template<class Motion> int writer_a_chain(Motion* m,unsigned side,std::size_t source_index) {
    require(side==1||side==2,"ORIGINAL_IK_PATH_SIDE_1_OR_2_REQUIRED");
    const auto& x=live.at(m);
    require((x.a_chain_shadow&&(x.origin=="ROOT_ASSIGNED"||x.origin=="GROW_ASSIGNED"))||(!x.a_chain_shadow&&x.origin=="CHECKSOLUTION_CONNECT"),"EXACT_LIFETIME_A_CHAIN_PROVENANCE_REQUIRED");
    const int column=x.a_chain_shadow?*x.a_chain_shadow:-1;
    const json row={{"schema","P4_R2_ABB_SBL_PCS_IK_PATH_METADATA_SHADOW_V2"},
        {"classification","RECONSTRUCTED_OUTPUT_METADATA_ONLY"},
        {"writer_file","../paths/ik_path.txt"},{"attempt_row_1based",writer_metadata_attempts.size()+1},
        {"source_side",side},{"source_index_0based",source_index},
        {"motion_id",x.id},{"address_generation",x.generation},{"state_id",x.state_id},
        {"a_chain",x.a_chain_shadow?json(*x.a_chain_shadow):json(nullptr)},
        {"a_chain_provenance",x.a_chain_shadow?x.origin:"UNINITIALIZED_NOT_READ"},
        {"motion_origin",x.origin},{"text_first_column",column},{"unknown_sentinel",-1},
        {"text_write_success_observed",nullptr}};
    // Always collect in plain and trace modes. This is an expression attempt,
    // not proof of ofstream open/write/flush success or on-disk sidecar saving.
    writer_metadata_attempts.push_back(row);mark("ik_path_metadata_attempt",row);
    return column;
}
inline const json& writer_metadata_attempt_buffer(){return writer_metadata_attempts;}
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
