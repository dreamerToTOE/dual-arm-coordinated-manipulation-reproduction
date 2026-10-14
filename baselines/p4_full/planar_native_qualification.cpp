// Project-owned driver; the original author solvers are external unchanged dependencies.
// CLI: planar_native_qualification I output.json
// Every completed case is also flushed to output.json.partial.jsonl.
// No planner is invoked. Units are source_link_length_unit and rad.
#include "apc_class.h"
#include "kdl_class.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <limits>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int n = 20, fk_count = 100, nr_count = 10;
constexpr std::uint64_t seed = 20261014;
constexpr double author_pi = 3.1416;
constexpr double fk_translation_gate = 1e-7, fk_rotation_gate = 1e-10;
constexpr double projection_translation_gate = 1e-5, projection_rotation_gate = 1e-5;
using Clock = std::chrono::steady_clock;
using SE2 = std::array<std::array<long double,3>,3>;
const State start = {1.6581,.17453,.17453,.17453,-.034907,-.17453,-.17453,
    -.5236,-.69813,-.5236,-.87266,-.17453,.087266,.34907,.17453,.17453,
    .17453,.18147,-.80904,2.4791};
const State goal = {-2.1293,.34907,.5236,.5236,.69813,.61087,.61087,-.17453,
    -.7854,-.5236,-.34907,.5236,.7854,.7854,.2618,.43633,-.17453,
    -1.2474,1.2172,5.0836};

std::string number(double x) {
    if (!std::isfinite(x)) return "null";
    std::ostringstream s; s << std::setprecision(17) << x; return s.str();
}
std::string vector_json(const State &v) {
    std::ostringstream s; s << '[';
    for (std::size_t i=0; i<v.size(); ++i) { if(i) s << ','; s << number(v[i]); }
    s << ']'; return s.str();
}
bool finite(const State &v) {
    for (double x:v) if (!std::isfinite(x)) return false; return true;
}
SE2 identity() { return {{{1,0,0},{0,1,0},{0,0,1}}}; }
SE2 multiply(const SE2 &a,const SE2 &b) {
    SE2 c{};
    for(int i=0;i<3;++i) for(int j=0;j<3;++j) for(int k=0;k<3;++k)
        c[i][j]+=a[i][k]*b[k][j];
    return c;
}
SE2 joint(long double q,long double length) {
    const auto c=std::cos(q),s=std::sin(q);
    return {{{c,-s,length*c},{s,c,length*s},{0,0,1}}};
}
SE2 independent_left(const State &q) {
    if(q.size()!=n || !finite(q)) throw std::runtime_error("Invalid FK input");
    SE2 t=identity();
    for(int j=0;j<n-1;++j) t=multiply(t,joint(q[j],1));
    return t;
}
SE2 independent_full(const State &q) {
    // The author's last encoder stays in [0,2*PI_]. It is a reversed terminal
    // angle: a temporary KDL joint is PI_-q[19], with zero link length.
    return multiply(independent_left(q),joint((long double)author_pi-q[19],0));
}
State flatten(const SE2 &t) {
    State v; for(const auto &row:t) for(auto x:row) v.push_back((double)x); return v;
}
State flatten(const Matrix &t) {
    State v; for(const auto &row:t) for(auto x:row) v.push_back(x); return v;
}
struct Error {
    double position=std::numeric_limits<double>::infinity();
    double rotation=std::numeric_limits<double>::infinity();
};
Error compare(const Matrix &a,const SE2 &b) {
    if(a.size()!=4) return {};
    for(const auto &row:a) if(row.size()!=4) return {};
    if(!finite(flatten(a))) return {};
    Error e{std::fabs(a[2][3]),0};
    e.position=std::max(e.position,std::fabs(a[0][3]-(double)b[0][2]));
    e.position=std::max(e.position,std::fabs(a[1][3]-(double)b[1][2]));
    for(int i=0;i<3;++i) for(int j=0;j<3;++j) {
        const double expected=i<2 && j<2 ? (double)b[i][j] : double(i==j);
        e.rotation=std::max(e.rotation,std::fabs(a[i][j]-expected));
    }
    return e;
}
Error closure(const State &q) {
    if(q.size()!=n || !finite(q)) return {};
    const auto t=independent_full(q);
    Error e{std::max(std::fabs((double)t[0][2]-7),
                     std::fabs((double)t[1][2]-4)),0};
    for(int i=0;i<2;++i) for(int j=0;j<2;++j)
        e.rotation=std::max(e.rotation,std::fabs((double)t[i][j]-double(i==j)));
    return e;
}
bool within(const Error &e,double pg,double rg) {
    return std::isfinite(e.position) && std::isfinite(e.rotation)
        && e.position<=pg && e.rotation<=rg;
}
bool chart_bounds(const State &q) {
    if(q.size()!=n || !finite(q)) return false;
    for(int j=0;j<n-1;++j) if(q[j]<-author_pi || q[j]>author_pi) return false;
    return q.back()>=0 && q.back()<=2*author_pi;
}
std::string error_json(const Error &e) {
    return "\"translation_error_source_units\":"+number(e.position)
        +",\"rotation_matrix_error\":"+number(e.rotation)
        +",\"finite_errors\":"+(std::isfinite(e.position)&&std::isfinite(e.rotation)?"true":"false");
}
double elapsed(Clock::time_point t) {
    return std::chrono::duration<double>(Clock::now()-t).count();
}
std::string boolean(bool x) { return x?"true":"false"; }
class Recorder {
    std::ofstream partial;
    std::vector<std::string> records;
    std::string path;
public:
    explicit Recorder(const std::string &p):partial(p+".partial.jsonl"),path(p) {
        if(!partial) throw std::runtime_error("Cannot open prefix evidence");
    }
    void add(const std::string &row) {
        records.push_back(row); partial<<row<<'\n'; partial.flush();
        if(!partial) throw std::runtime_error("Cannot save prefix evidence");
    }
    void finish(int fk_fail,int nr_fail,int apc_fail,double wall) {
        std::ofstream out(path);
        if(!out) throw std::runtime_error("Cannot open final evidence");
        out<<"{\"schema\":\"P4_PLANAR_NATIVE_QUALIFICATION_V1\",\"environment\":\"I\","
            <<"\"source_commit\":\"e5edcb58e151b78baca43dd4922bfe27a48388cd\","
            <<"\"classification\":\"COMPONENT_DIAGNOSTICS_NOT_PLANNING\","
            <<"\"units\":\"source_link_length_unit / rad\",\"seed\":"<<seed<<','
            <<"\"joints\":20,\"fk_count\":100,\"nr_count\":10,\"apc_count\":40,"
            <<"\"formal_planning_calls\":0,\"endpoint_policy\":\"RAW_UNCHANGED_DIAGNOSTIC\","
            <<"\"oracle\":\"long_double_SE2_19_RotZ_unit_links_then_zero_length_PI_minus_q19\","
            <<"\"apc_wrapped_scalar_orientation_policy\":\"SECONDARY_REPRESENTATION_DIAGNOSTIC_NO_ERROR_SUPPRESSION\","
            <<"\"fk_translation_gate_source_units\":"<<number(fk_translation_gate)<<','
            <<"\"fk_rotation_gate\":"<<number(fk_rotation_gate)<<','
            <<"\"projection_translation_gate_source_units\":"<<number(projection_translation_gate)<<','
            <<"\"projection_rotation_gate\":"<<number(projection_rotation_gate)<<','
            <<"\"source_author_PI\":"<<number(author_pi)<<','
            <<"\"fk_failures\":"<<fk_fail<<",\"nr_failures\":"<<nr_fail
            <<",\"apc_reject_or_residual_failures\":"<<apc_fail
            <<",\"wall_s\":"<<number(wall)<<",\"records\":[";
        for(std::size_t i=0;i<records.size();++i) { if(i) out<<','; out<<records[i]; }
        out<<"]}\n";
        if(!out) throw std::runtime_error("Cannot save final evidence");
    }
};
}

int main(int argc,char **argv) {
    if(argc!=3 || std::string(argv[1])!="I") {
        std::cerr<<"Usage: planar_native_qualification I output.json\n"; return 2;
    }
    const auto whole=Clock::now();
    try {
        Recorder log(argv[2]);
        ckc apc(n,.3); kdl nr(n,.3);
        // Initialize only public performance counters, not kinematic states.
        apc.IK_counter=0; apc.IK_time=0; nr.IK_counter=0; nr.IK_time=0;
        for(int endpoint=0;endpoint<2;++endpoint) {
            const State &q=endpoint==0?start:goal;
            log.add("{\"kind\":\"raw_endpoint\",\"endpoint\":"+std::to_string(endpoint)
                +",\"q\":"+vector_json(q)+",\"oracle_SE2\":"+vector_json(flatten(independent_full(q)))
                +",\"apc_constraint_raw\":"+vector_json(apc.constraint(q))
                +",\"kdl_constraint_raw\":"+vector_json(nr.constraint(q))
                +","+error_json(closure(q))
                +",\"source_run_chart_bounds\":"+boolean(chart_bounds(q))+",\"gate_applied\":false}");
        }
        std::mt19937_64 rng(seed);
        std::uniform_real_distribution<double> regular(-author_pi,author_pi),last(0,2*author_pi);
        int fk_fail=0,nr_fail=0,apc_fail=0;
        for(int i=0;i<fk_count;++i) {
            State q(n);
            for(int j=0;j<n-1;++j) q[j]=regular(rng);
            q.back()=last(rng);
            const auto before=Clock::now();
            State physical=q; physical.back()=author_pi-q.back();
            nr.FK(physical);
            const auto native=nr.get_FK_solution();
            const auto oracle=independent_full(q);
            const auto e=compare(native,oracle);
            const bool ok=within(e,fk_translation_gate,fk_rotation_gate);
            if(!ok) ++fk_fail;
            apc.FK_left(q,n-1);
            const auto left=apc.get_FK_sol_left();
            const auto left_oracle=independent_left(q);
            double lp=std::numeric_limits<double>::infinity(),lr=lp;
            if(left.size()==3 && finite(left)) {
                lp=std::max(std::fabs(left[0]-(double)left_oracle[0][2]),
                            std::fabs(left[1]-(double)left_oracle[1][2]));
                lr=std::max(std::fabs(std::cos(left[2])-(double)left_oracle[0][0]),
                            std::fabs(std::sin(left[2])-(double)left_oracle[1][0]));
            }
            log.add("{\"kind\":\"fk\",\"index\":"+std::to_string(i)
                +",\"q_author_chart\":"+vector_json(q)+",\"q_temporary_KDL\":"+vector_json(physical)
                +",\"author_KDL_matrix4\":"+vector_json(flatten(native))
                +",\"oracle_SE2\":"+vector_json(flatten(oracle))
                +",\"apc_left_raw\":"+vector_json(left)
                +",\"apc_left_position_error_source_units\":"+number(lp)
                +",\"apc_left_physical_matrix_error_diagnostic\":"+number(lr)
                +","+error_json(e)+",\"qualified_kdl_fk\":"+boolean(ok)
                +",\"elapsed_wall_s\":"+number(elapsed(before))+"}");
        }
        for(int i=0;i<nr_count;++i) {
            const int endpoint=i<5?0:1,joint_index=i%5;
            const double offset=i%2?.01:-.01;
            State input=endpoint==0?start:goal; input[joint_index]+=offset;
            const auto before=Clock::now();
            const bool source_return=nr.GD(input);
            const double wall=elapsed(before);
            State output; if(source_return) output=nr.get_GD_result();
            const auto e=source_return?closure(output):Error{};
            const bool ok=source_return && within(e,projection_translation_gate,projection_rotation_gate);
            if(!ok) ++nr_fail;
            log.add("{\"kind\":\"nr_projection\",\"index\":"+std::to_string(i)
                +",\"endpoint\":"+std::to_string(endpoint)+",\"perturbed_joint\":"+std::to_string(joint_index)
                +",\"offset_rad\":"+number(offset)+",\"q_input\":"+vector_json(input)
                +",\"source_return\":"+boolean(source_return)
                +",\"q_output\":"+(source_return?vector_json(output):"null")
                +","+error_json(e)+",\"source_run_chart_bounds\":"+boolean(chart_bounds(output))
                +",\"qualified_closure\":"+boolean(ok)+",\"elapsed_wall_s\":"+number(wall)+"}");
        }
        for(int partition=0;partition<n;++partition) for(int branch=0;branch<2;++branch) {
            State candidate=start;
            const auto before=Clock::now();
            const bool source_return=apc.project(candidate,partition,branch);
            const double wall=elapsed(before);
            const auto e=closure(candidate);
            const bool ok=source_return && within(e,projection_translation_gate,projection_rotation_gate);
            if(!ok) ++apc_fail;
            log.add("{\"kind\":\"apc_projection\",\"partition\":"+std::to_string(partition)
                +",\"branch\":"+std::to_string(branch)+",\"q_input\":"+vector_json(start)
                +",\"source_return\":"+boolean(source_return)
                +",\"q_candidate_diagnostic\":"+vector_json(candidate)
                +","+error_json(e)+",\"source_run_chart_bounds\":"+boolean(chart_bounds(candidate))
                +",\"qualified_closure\":"+boolean(ok)+",\"collision_checked\":false"
                +",\"elapsed_wall_s\":"+number(wall)+"}");
        }
        State bad=start; bad.front()+=.1;
        log.add("{\"kind\":\"negative_closure\",\"q_input\":"+vector_json(bad)+","+error_json(closure(bad))+"}");
        for(int branch=0;branch<2;++branch) {
            const State target{100000000,0,0};
            const auto before=Clock::now();
            const bool result=apc.IKp(target,branch,1);
            log.add("{\"kind\":\"negative_unreachable_IK\",\"branch\":"+std::to_string(branch)
                +",\"target_source_units_rad\":"+vector_json(target)+",\"source_return\":"+boolean(result)
                +",\"elapsed_wall_s\":"+number(elapsed(before))+"}");
        }
        log.finish(fk_fail,nr_fail,apc_fail,elapsed(whole));
        // Return code describes completed evidence delivery, never scientific PASS.
        // Legitimate unreachable IK branches are recorded, not executable errors.
        return 0;
    } catch(const std::exception &e) {
        std::cerr<<"Planar diagnostic stopped: "<<e.what()<<'\n'; return 3;
    }
}
