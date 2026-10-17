// New project-owned transport: versioned writer metadata, original SBL control.
// Engineering BUILD02 never executes this binary. Runtime requires separate freeze.
#include "abb_sbl_pcs_observation_shadow_v2_draft.hpp"
#include "SBL_PCS.h"
#include <ompl/base/ScopedState.h>
#include <ompl/base/ProblemDefinition.h>
#include <ompl/base/PlannerTerminationCondition.h>
#include <ompl/geometric/PathGeometric.h>
#include <ompl/util/RandomNumbers.h>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <fcntl.h>
#include <iterator>
#include <memory>
#include <set>
#include <sstream>
#include <system_error>
#include <unistd.h>
namespace ob=ompl::base;
namespace og=ompl::geometric;
namespace fs=std::filesystem;
using json=p4sbl::json;
namespace {
class Redirect {std::streambuf* prior;public:Redirect():prior(std::cout.rdbuf(std::cerr.rdbuf())){}~Redirect(){std::cout.rdbuf(prior);}};
const std::vector<double> START={.5236,1.7453,-1.8326,-1.4835,1.5708,0.,1.0042713284452618,.2729059574498862,.9485892867539307,-1.1501189067527977,1.8100179182011582,-1.977396290726386};
const std::vector<double> GOAL={.5236,.34907,.69813,-1.3963,1.5708,0.,.7096069035980488,1.8033460368176983,-1.7064142899195036,-1.6286748910337208,1.914257188961649,-2.015718262850188};
const std::vector<double> LOW={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416},HIGH={2.88,1.919,1.22,2.79,2.09,3.1416};
std::vector<double> finite12(const json& value){auto q=value.get<std::vector<double>>();p4sbl::require(q.size()==12,"FINITE12_REQUIRED");for(double x:q)p4sbl::require(std::isfinite(x),"FINITE12_REQUIRED");return q;}
void put(ob::ScopedState<ob::RealVectorStateSpace>& state,const std::vector<double>& q){for(unsigned i=0;i<12;++i)state[i]=q[i];}
void local_preflight(const json& fixture){
    p4sbl::require(fixture.is_object()&&fixture.at("separately_frozen_local_fixture")==true,"FROZEN_LOCAL_FIXTURE_REQUIRED_BEFORE_MODEL");
    const auto kind=fixture.at("kind").get<std::string>();p4sbl::require(kind=="lazy_chain"||kind=="connect_pair","EXACT_LOCAL_FIXTURE_KIND_REQUIRED_BEFORE_MODEL");
    p4sbl::require(!fixture.at("fixture_id").get<std::string>().empty()&&fixture.at("saved_input_references").is_array()&&!fixture.at("saved_input_references").empty(),"SAVED_LOCAL_INPUT_PROVENANCE_REQUIRED_BEFORE_MODEL");
    auto chain=[&](const json& values){p4sbl::require(values.is_array()&&values.size()>=1&&values.size()<=3,"BOUNDED_LOCAL_CHAIN_REQUIRED_BEFORE_MODEL");for(std::size_t i=0;i<values.size();++i){const auto& node=values.at(i);finite12(node.at("q12"));const auto& ik=node.at("ik");p4sbl::require(ik.is_array()&&ik.size()==2,"TWO_LOCAL_BRANCH_IDS_REQUIRED_BEFORE_MODEL");for(const auto& value:ik){p4sbl::require(value.is_number_integer(),"INTEGER_LOCAL_BRANCH_ID_REQUIRED_BEFORE_MODEL");const int branch=value.get<int>();p4sbl::require(branch>=-1&&branch<8,"LOCAL_BRANCH_RANGE_REQUIRED_BEFORE_MODEL");}p4sbl::require(node.at("assigned_active_role").is_number_integer(),"INTEGER_LOCAL_ROLE_REQUIRED_BEFORE_MODEL");const int role=node.at("assigned_active_role").get<int>();p4sbl::require((role==0||role==1)&&(i>0||role==0),"LOCAL_ROOT_ZERO_OR_GROW_ROLE_REQUIRED_BEFORE_MODEL");}};
    chain(fixture.at("start_chain"));if(kind=="lazy_chain")p4sbl::require(fixture.at("start_chain").size()>=2,"NONROOT_LOCAL_LAZY_CHAIN_REQUIRED_BEFORE_MODEL");else chain(fixture.at("goal_chain"));
}
std::string hexbytes(const std::string& value){static const char* digits="0123456789abcdef";std::string result;result.reserve(value.size()*2);for(unsigned char c:value){result.push_back(digits[c>>4]);result.push_back(digits[c&15]);}return result;}
std::string readbytes(const fs::path& path){std::ifstream stream(path,std::ios::binary);p4sbl::require(stream.is_open(),"EVIDENCE_READ_OPEN_REQUIRED");std::string bytes((std::istreambuf_iterator<char>(stream)),{});p4sbl::require(!stream.bad(),"EVIDENCE_READ_BADBIT");return bytes;}
void syncdir(const fs::path& path){int fd=::open(path.c_str(),O_RDONLY|O_DIRECTORY|O_CLOEXEC);if(fd<0)throw std::system_error(errno,std::generic_category(),"EVIDENCE_DIRECTORY_OPEN");const int rc=::fsync(fd),saved=errno;::close(fd);if(rc)throw std::system_error(saved,std::generic_category(),"EVIDENCE_DIRECTORY_FSYNC");}
void durable_new(const fs::path& path,const std::string& bytes){
    int fd=::open(path.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0600);if(fd<0)throw std::system_error(errno,std::generic_category(),"EXCLUSIVE_EVIDENCE_OPEN");
    try{std::size_t done=0;while(done<bytes.size()){ssize_t n=::write(fd,bytes.data()+done,bytes.size()-done);if(n<0&&errno==EINTR)continue;if(n<=0)throw std::system_error(errno,std::generic_category(),"EVIDENCE_WRITE");done+=static_cast<std::size_t>(n);}if(::fsync(fd))throw std::system_error(errno,std::generic_category(),"EVIDENCE_FSYNC");if(::close(fd)){fd=-1;throw std::system_error(errno,std::generic_category(),"EVIDENCE_CLOSE");}fd=-1;syncdir(path.parent_path());p4sbl::require(readbytes(path)==bytes,"EVIDENCE_READBACK_BYTES_MUST_MATCH");}
    catch(...){if(fd>=0)::close(fd);throw;}
}
class Probe final:public og::SBL {
    Motion* fixture_node(TreeData& tree,const json& spec,Motion* parent){
        auto q=finite12(spec.at("q12"));auto ik=spec.at("ik").get<std::vector<int>>();p4sbl::require(ik.size()==2,"FROZEN_TWO_BRANCH_IDS_REQUIRED");
        for(int x:ik)p4sbl::require(x>=-1&&x<8,"FROZEN_ANALYTIC_BRANCH_RANGE_REQUIRED");
        const int role=spec.at("assigned_active_role").get<int>();p4sbl::require((role==0||role==1)&&(parent||role==0),"FIXTURE_ROOT_ZERO_OR_ASSIGNED_GROW_ROLE_REQUIRED");
        auto release_unregistered=[&](Motion* m){if(m){if(m->state)si_->freeState(m->state);delete m;}};std::unique_ptr<Motion,decltype(release_unregistered)> owned(new Motion(si_),release_unregistered);auto* m=owned.get();
        auto* state=m->state->as<ob::RealVectorStateSpace::StateType>();for(unsigned i=0;i<12;++i)state->values[i]=q[i];
        m->ik_q1_active=ik[0];m->ik_q2_active=ik[1];m->parent=parent;m->root=parent?parent->root:m->state;
        // Explicit fixture adapter matches the original root/grow assigned fields.
        // It never fabricates checkSolution connect and never writes a connect role.
        m->a_chain=role;m->valid=parent?false:true;if(parent)parent->children.push_back(m);
        addMotion(tree,m);owned.release();return m;
    }
public:
    Probe(const ob::SpaceInformationPtr& si):og::SBL(si,.8,1){p4sbl::bind_tree(&tStart_,"start");p4sbl::bind_tree(&tGoal_,"goal");}
    json metadata()const{auto p=getProjectionEvaluator();p4sbl::require(bool(p),"ACTUAL_DEFAULT_PROJECTION_REQUIRED");const auto dim=p->getDimension();p4sbl::require(dim>0&&tStart_.grid.getDimension()==dim&&tGoal_.grid.getDimension()==dim,"ACTUAL_PROJECTION_GRID_DIMENSIONS_REQUIRED");return {{"projection_dynamic_type",typeid(*p).name()},{"projection_dimension",dim},{"cell_sizes",p->getCellSizes()},{"user_configured",p->userConfigured()},{"native_grid_dimensions",{tStart_.grid.getDimension(),tGoal_.grid.getDimension()}},{"setup_getRange",getRange()},{"original_solve_Range",Range},{"additional_public_project_observations",0},{"observer_rng_draws",0},{"setup_internal_rng_draws","UNOBSERVED"}};}
    json trees()const{json nodes=json::array();unsigned side=0;for(const auto* tree:{&tStart_,&tGoal_}){for(auto it=tree->grid.begin();it!=tree->grid.end();++it)for(unsigned i=0;i<it->second->data.size();++i){auto row=p4sbl::snapshot(it->second->data[i]);row["tree"]=side==0?"start":"goal";nodes.push_back(row);}++side;}return {{"nodes",nodes},{"native_tree_sizes",{tStart_.size,tGoal_.size}},{"identity_policy","LIVE_MOTION_LIFETIME_GENERATION_NO_Q_MERGE"}};}
    json local(const json& fixture){
        p4sbl::require(fixture.at("separately_frozen_local_fixture")==true,"FROZEN_LOCAL_FIXTURE_REQUIRED");
        const std::string kind=fixture.at("kind"),id=fixture.at("fixture_id");p4sbl::require(!id.empty()&&fixture.at("saved_input_references").is_array()&&!fixture.at("saved_input_references").empty(),"SAVED_INPUT_PROVENANCE_REQUIRED");
        initiate_log_parameters();startTime=clock();json result={{"kind",kind},{"fixture_id",id},{"fixture_adapter","RECONSTRUCTED_TREE_FIXTURE_ORIGINAL_SBL_METHOD_BODIES"},{"saved_input_references",fixture.at("saved_input_references")}};
        auto* start=fixture_node(tStart_,fixture.at("start_chain").at(0),nullptr);
        auto* last=start;const auto& chain=fixture.at("start_chain");p4sbl::require(chain.size()>=1&&chain.size()<=3,"BOUNDED_START_CHAIN_ONE_TO_THREE_REQUIRED");for(std::size_t i=1;i<chain.size();++i)last=fixture_node(tStart_,chain[i],last);
        result["before"]=trees();
        if(kind=="lazy_chain"){
            p4sbl::require(chain.size()>=2,"NONROOT_LAZY_FIXTURE_REQUIRED");result["source_isPathValid_returned"]=isPathValid(tStart_,last);
        }else if(kind=="connect_pair"){
            const auto& other=fixture.at("goal_chain");p4sbl::require(other.size()>=1&&other.size()<=3,"BOUNDED_GOAL_CHAIN_ONE_TO_THREE_REQUIRED");auto* target=fixture_node(tGoal_,other.at(0),nullptr);for(std::size_t i=1;i<other.size();++i)target=fixture_node(tGoal_,other[i],target);
            result["before_connect"]=trees();std::vector<Motion*> solution;
            result["source_checkSolution_returned"]=checkSolution(true,tStart_,tGoal_,last,solution);result["source_solution_motion_ids"]=json::array();for(auto* m:solution)result["source_solution_motion_ids"].push_back(p4sbl::identity(m));
            result["source_checkSolution_dispatches"]=1;result["original_same_cell_selection_rng_may_run"]=true;
        }else throw std::runtime_error("ONLY_PREDECLARED_LAZY_OR_CONNECT_FIXTURE_REQUIRED");
        result["after"]=trees();result["no_retry_or_fixture_replacement"]=true;return result;
    }
};
json native_files(const fs::path& work,const fs::path& evidence){
    const std::vector<std::pair<std::string,fs::path>> expected={{"parent/path_milestones.txt",work.parent_path()/"paths/path_milestones.txt"},{"parent/ik_path.txt",work.parent_path()/"paths/ik_path.txt"},{"work/path.txt",work/"paths/path.txt"},{"work/temp.txt",work/"paths/temp.txt"},{"work/perf_log.txt",work/"paths/perf_log.txt"}};
    json rows=json::array();std::set<fs::path> known;for(const auto& item:expected)known.insert(item.second.lexically_normal());
    auto capture=[&](const std::string& name,const fs::path& path){json row={{"name",name},{"original_path",path.string()},{"exists",fs::exists(path)},{"original_stream_open_write_flush_flags","UNOBSERVED"},{"readback_bytes_saved",false}};try{if(fs::exists(path)){p4sbl::require(fs::is_regular_file(path)&&!fs::is_symlink(path),"NATIVE_OUTPUT_REGULAR_NONLINK_REQUIRED");const auto bytes=readbytes(path);const auto saved=evidence/"native"/name;fs::create_directories(saved.parent_path());durable_new(saved,bytes);row["readback_bytes_saved"]=true;row["saved_path"]=saved.string();row["bytes"]=bytes.size();row["bytes_hex"]=hexbytes(bytes);row["original_final_bytes_readable"]=true;}else row["absence_retained"]=true;}catch(const std::exception& error){row["error"]=error.what();}rows.push_back(row);};
    for(const auto& item:expected)capture(item.first,item.second);
    for(const auto& dir:{work/"paths",work.parent_path()/"paths"})if(fs::is_directory(dir))for(const auto& entry:fs::directory_iterator(dir))if(!known.count(entry.path().lexically_normal()))capture("unexpected/"+std::string(dir==work/"paths"?"work/":"parent/")+entry.path().filename().string(),entry.path());
    return rows;
}
json shadow_audit(const fs::path& work,const json& attempts,const json& tree){
    json result={{"schema","P4_R2_ABB_SBL_PCS_IK_PATH_SHADOW_PERSISTED_V2"},{"classification","RECONSTRUCTED_OUTPUT_METADATA_ONLY"},{"attempts",attempts},{"attempt_count",attempts.size()},{"final_text_readback_matches_attempts",false},{"original_fstream_open_write_flush_flags","UNOBSERVED"},{"scope","ONE_SEPARATELY_FROZEN_LOCAL_OR_SOLVE_REQUEST_AT_MOST_ONE_ORIGINAL_SAVE"}};
    const auto path=work.parent_path()/"paths/ik_path.txt";
    try{
        if(attempts.empty()){result["no_writer_attempts_observed"]=true;result["ik_path_exists"]=fs::exists(path);result["empty_attempts_do_not_prove_write_success"]=true;return result;}
        p4sbl::require(fs::is_regular_file(path),"IK_PATH_PRESENT_FOR_ATTEMPTS_REQUIRED");std::istringstream input(readbytes(path));std::string line;std::size_t index=0;unsigned prior_side=1;long prior_source=-1;json rows=json::array();
        while(std::getline(input,line)){
            p4sbl::require(index<attempts.size(),"NO_EXTRA_IK_PATH_LINES_ALLOWED");const auto& attempt=attempts.at(index);std::istringstream fields(line);long role,ik0,ik1;std::string extra;p4sbl::require(bool(fields>>role>>ik0>>ik1)&&!(fields>>extra),"EXACT_THREE_INTEGER_IK_PATH_COLUMNS_REQUIRED");
            p4sbl::require(attempt.at("attempt_row_1based")==index+1,"ATTEMPT_ROW_SEQUENCE_REQUIRED");const auto id=attempt.at("motion_id").get<unsigned long>();const json* node=nullptr;for(const auto& value:tree.at("nodes"))if(value.at("motion_id")==id){p4sbl::require(node==nullptr,"UNIQUE_LIVE_MOTION_ID_REQUIRED");node=&value;}
            p4sbl::require(node!=nullptr,"WRITER_ATTEMPT_LIVE_NODE_REQUIRED");p4sbl::require(role==attempt.at("text_first_column").get<long>()&&ik0==node->at("ik_q1_active").get<long>()&&ik1==node->at("ik_q2_active").get<long>(),"FINAL_IK_PATH_COLUMNS_MUST_MATCH_SHADOW_AND_LIVE_BRANCHES");
            p4sbl::require(attempt.at("a_chain")==node->at("a_chain")&&attempt.at("address_generation")==node->at("address_generation")&&attempt.at("state_id")==node->at("state_id"),"ATTEMPT_LIFETIME_SHADOW_IDENTITY_REQUIRED");
            const unsigned side=attempt.at("source_side").get<unsigned>();const long source=attempt.at("source_index_0based").get<long>();p4sbl::require(side>=prior_side&&(side==1||side==2),"ORIGINAL_SIDE_ORDER_REQUIRED");if(index&&side==prior_side)p4sbl::require(source==prior_source+(side==1?-1:1),"ORIGINAL_SIDE_SOURCE_INDEX_SEQUENCE_REQUIRED");else if(side==2){p4sbl::require(source==0,"SECOND_SIDE_START_INDEX_ZERO_REQUIRED");if(index)p4sbl::require(prior_source==0,"FIRST_SIDE_MUST_REACH_INDEX_ZERO");}
            prior_side=side;prior_source=source;rows.push_back({{"line_1based",index+1},{"actual_three_columns",{role,ik0,ik1}},{"matches",true}});++index;
        }
        p4sbl::require(index==attempts.size(),"ALL_ATTEMPTS_REQUIRE_FINAL_IK_PATH_ROWS");result["final_rows"]=rows;result["final_text_readback_matches_attempts"]=true;result["final_byte_certificate_not_internal_stream_flags"]=true;
    }catch(const std::exception& error){result["error"]=error.what();}return result;
}
}
int main(int argc,char** argv){
    if(argc!=5)return 64;const std::string environment=argv[1],operation=argv[3],mode=argv[4];if(environment!="II"||(operation!="local"&&operation!="solve")||(mode!="plain"&&mode!="trace"))return 64;
    json out={{"schema","P4_ABB_SBL_PCS_SHADOW_V2_RUNTIME_DRAFT"},{"status","STOP_RETAINED_PREFIX"},{"operation",operation},{"mode",mode},{"setup_dispatches",0},{"public_project_observations",0},{"solve_calls",0},{"source_dispatch_started",0},{"source_dispatch_completed",0},{"formal_table_I_calls",0},{"new_VI_candidate_constructions",0},{"independent_path_qualified",false},{"continuous_collision_certificate",false}};
    fs::path work,evidence;bool isolated=false;
    try{
        std::string line,extra;p4sbl::require(bool(std::getline(std::cin,line))&&!std::getline(std::cin,extra),"ONE_REQUEST_THEN_STDIN_EOF_REQUIRED");const auto request=json::parse(line);out["request"]=request;
        p4sbl::require(request.at("operation")==operation&&request.at("environment")=="II"&&request.at("seed")==7&&request.at("range_rad")==.8&&request.at("separately_frozen_runtime_qualification")==true,"SEPARATELY_FROZEN_II_SEED7_RANGE08_REQUEST_REQUIRED");
        p4sbl::require(finite12(request.at("start_q12"))==START&&finite12(request.at("goal_q12"))==GOAL,"EXACT_SAVED_A01_RECONSTRUCTED_ENDPOINTS_REQUIRED");if(operation=="solve")p4sbl::require(request.at("solve_seconds")==10.,"ONE_NATIVE_TEN_SECOND_SOLVE_REQUIRED");if(operation=="local")local_preflight(request.at("fixture"));
        work=fs::absolute(argv[2]);p4sbl::require(fs::is_directory(work/"simulator"),"FRESH_MESH_WORK_DIRECTORY_REQUIRED");p4sbl::require(!fs::exists(work/"paths")&&!fs::exists(work.parent_path()/"paths")&&!fs::exists(work/"writer_evidence"),"ISOLATED_ORIGINAL_AND_VERSIONED_OUTPUTS_MUST_BE_ABSENT");fs::current_path(work);p4sbl::require(fs::create_directory(work/"paths")&&fs::create_directory(work.parent_path()/"paths")&&fs::create_directory(work/"writer_evidence"),"FRESH_OUTPUT_DIRECTORIES_REQUIRED");evidence=work/"writer_evidence";isolated=true;
        p4sbl::enabled=mode=="trace";p4sbl::reset();ompl::RNG::setSeed(7);std::srand(7);auto space=std::make_shared<ob::RealVectorStateSpace>(12);ob::RealVectorBounds bounds(12);for(unsigned i=0;i<12;++i){bounds.setLow(i,LOW[i%6]);bounds.setHigh(i,HIGH[i%6]);}space->setBounds(bounds);
        auto si=std::make_shared<ob::SpaceInformation>(space);si->setStateValidityChecker([](const ob::State*){return true;});si->setStateValidityCheckingResolution(.02);ob::ScopedState<ob::RealVectorStateSpace> a(space),b(space);put(a,START);put(b,GOAL);auto problem=std::make_shared<ob::ProblemDefinition>(si);problem->setStartAndGoalStates(a,b);
        {Redirect quiet;auto planner=std::make_unique<Probe>(si);planner->setProblemDefinition(problem);planner->setup();out["setup_dispatches"]=1;out["setup_metadata"]=planner->metadata();out["setup_scope"]="NECESSARY_RUNTIME_SETUP_NOT_REPEATED_PUBLIC13_QUALIFICATION";
            out["source_dispatch_started"]=1;if(operation=="local"){out["local"]=planner->local(request.at("fixture"));out["status"]="SOURCE_LOCAL_OBSERVED_PENDING_INDEPENDENT_QUALIFICATION";}else{
                out["solve_calls"]=1;const auto begun=std::chrono::steady_clock::now();const auto status=planner->solve(ob::timedPlannerTerminationCondition(10.));out["solve_wall_s"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-begun).count();out["planner_status"]=status.asString();out["exact"]=problem->hasExactSolution();out["solution_count"]=problem->getSolutionCount();out["milestones_q12"]=json::array();if(problem->hasSolution()){auto path=std::dynamic_pointer_cast<og::PathGeometric>(problem->getSolutionPath());p4sbl::require(bool(path),"NATIVE_GEOMETRIC_PATH_REQUIRED");for(auto* state:path->getStates())out["milestones_q12"].push_back(p4sbl::q12(state));}out["status"]=problem->hasExactSolution()?"SOURCE_EXACT_PENDING_INDEPENDENT_PATH_QUALIFICATION":"SOURCE_NONEXACT_RETAINED";
            }out["source_dispatch_completed"]=1;out["trees_before_destruction"]=planner->trees();planner.reset();}
        p4sbl::require(p4sbl::live.empty(),"REGISTRY_EMPTY_AFTER_NATIVE_DESTRUCTION_REQUIRED");
    }catch(const std::exception& error){out["error"]=error.what();out["status"]="STOP_RETAINED_PREFIX";}
    out["remaining_live_motions"]=p4sbl::live.size();out["source_counts_observed"]=p4sbl::enabled;out["source_started"]=p4sbl::enabled?json(p4sbl::started):json(nullptr);out["source_completed"]=p4sbl::enabled?json(p4sbl::completed):json(nullptr);out["trace"]=p4sbl::enabled?p4sbl::events:json(nullptr);out["writer_metadata_attempts"]=p4sbl::writer_metadata_attempt_buffer();
    if(isolated){try{out["native_file_evidence"]=native_files(work,evidence);bool all_native_retained=true;for(const auto& row:out["native_file_evidence"])if(row.contains("error")||(row.at("exists")==true&&row.at("readback_bytes_saved")!=true))all_native_retained=false;out["native_output_capture_complete"]=all_native_retained;const json tree=out.contains("trees_before_destruction")?out.at("trees_before_destruction"):json{{"nodes",json::array()}};auto sidecar=shadow_audit(work,p4sbl::writer_metadata_attempt_buffer(),tree);sidecar["native_file_evidence"]=out["native_file_evidence"];durable_new(evidence/"ik_path_shadow_v2.json",sidecar.dump(2)+"\n");out["shadow_sidecar_saved_and_readback_equal"]=true;out["shadow_sidecar_path"]=(evidence/"ik_path_shadow_v2.json").string();out["shadow_final_text_readback_matches_attempts"]=sidecar.at("final_text_readback_matches_attempts");durable_new(evidence/"transport_prefix_and_io_evidence.json",out.dump(2)+"\n");out["transport_evidence_saved_and_readback_equal"]=true;if(!all_native_retained)out["status"]="STOP_EVIDENCE_PERSISTENCE_ERROR";}catch(const std::exception& error){out["artifact_persistence_error"]=error.what();out["status"]="STOP_EVIDENCE_PERSISTENCE_ERROR";}}
    out["original_fstream_internal_flags"]="UNOBSERVED_FINAL_READBACK_CERTIFICATE_ONLY";out["solve_timing_scope"]="ORIGINAL_SOLVE_AND_OBSERVATIONS_NOT_FORMAL_PAPER_TIMING";std::cout<<out.dump()<<std::endl;return out["status"]=="STOP_RETAINED_PREFIX"||out["status"]=="STOP_EVIDENCE_PERSISTENCE_ERROR"?2:0;
}
