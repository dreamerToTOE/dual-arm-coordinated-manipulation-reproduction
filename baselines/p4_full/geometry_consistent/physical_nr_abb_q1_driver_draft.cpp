// PROJECT-OWNED DRAFT: NOT BUILT, EXECUTED, OR QUALIFIED.
// Single binary, runtime argv[1]=plain|trace. JSONL in/out, no planner/collision.
// Both modes call exactly the same project_nr; detailed_trace only observes it.
#include "physical_nr_abb_cpp_draft.hpp"
#include <nlohmann/json.hpp>
#include <iostream>
#include <string>

using json = nlohmann::json;
namespace nr = p4nr_draft;
json vec(const nr::Vector& v) {
    json a=json::array();for(Eigen::Index i=0;i<v.size();++i)a.push_back(v[i]);return a;
}
json mat(const nr::Matrix& m) {
    json a=json::array();for(Eigen::Index i=0;i<m.rows();++i){json row=json::array();
        for(Eigen::Index j=0;j<m.cols();++j)row.push_back(m(i,j));a.push_back(row);}return a;
}
json metrics(const nr::Metrics& m) {
    return {{"translation_max_abs",m.translation_max_abs},
        {"rotation_matrix_max_abs",m.rotation_matrix_max_abs},
        {"rotation_angle_max_rad",m.rotation_angle_max_rad},{"position_unit",m.position_unit}};
}
json result_json(const nr::Result& r) {
    json trace=json::array();
    for(const auto& s:r.trace) {
      nr::Vector observed_delta;
      if(s.q_next.size()) observed_delta=(s.q_next-s.q_before).eval();
      trace.push_back({{"iteration",s.iteration},
        {"q_before",vec(s.q_before)},{"g",vec(s.g)},{"j",mat(s.j)},
        {"metrics",metrics(s.metrics)},{"singular_values",vec(s.singular_values)},
        {"cutoff",s.cutoff},{"numerical_rank",s.numerical_rank},
        {"proposed_delta_q",vec(s.delta_q)},
        {"observed_delta_q",vec(observed_delta)},{"q_next",vec(s.q_next)}});
    }
    return {{"status",r.status},{"input_q_rad",vec(r.input_q_rad)},
        {"candidate_q_rad",r.candidate_is_finite?vec(r.candidate_q_rad):json(nullptr)},
        {"candidate_is_finite",r.candidate_is_finite},{"metrics",r.has_metrics?metrics(r.metrics):json(nullptr)},
        {"trace",trace},{"accepted_updates",r.accepted_updates},{"wall_s",r.wall_s},
        {"method",r.method},{"collision_checked",r.collision_checked}};
}
int main(int argc,char** argv) {
    if(argc!=2||(std::string(argv[1])!="plain"&&std::string(argv[1])!="trace"))return 64;
    const bool detailed=std::string(argv[1])=="trace";
    std::string line;unsigned index=0;
    while(std::getline(std::cin,line)) {
        try {
            auto req=json::parse(line);
            if(req.size()!=3||!req.contains("case_id")||!req.contains("environment")||!req.contains("q12"))
                throw std::invalid_argument("EXACT_REQUEST_KEYS_REQUIRED");
            const std::string env=req.at("environment");nr::require_environment(env);
            const auto qdata=req.at("q12").get<std::vector<double>>();
            if(qdata.size()!=12)throw std::invalid_argument("EXPECTED_Q12");
            nr::Vector q(12);for(int i=0;i<12;++i){q[i]=qdata[i];
                if(!std::isfinite(q[i]))throw std::invalid_argument("FINITE_Q12_REQUIRED");}
            nr::Options options;options.detailed_trace=detailed;
            // Preserve Python defaults: 120s/call,10000 updates,1e-5/1e-5,1e-12.
            const auto result=nr::project_nr(q,env,options);
            std::cout<<json({{"schema","P4_NR_ABB_CPP_Q1_DRAFT_V1"},
                {"request_index",index},{"request",req},{"mode",argv[1]},
                {"completed_top_level_nr",true},{"result",result_json(result)}}).dump()<<std::endl;
            ++index;
        } catch(const std::exception& e) {
            std::cout<<json({{"schema","P4_NR_ABB_CPP_Q1_DRAFT_V1"},
                {"request_index",index},{"mode",argv[1]},
                {"transport_error",e.what()},{"completed_top_level_nr",false}}).dump()<<std::endl;
            return 2; // Keep the full stdout prefix; no retry or fallback.
        }
    }
    return 0;
}
