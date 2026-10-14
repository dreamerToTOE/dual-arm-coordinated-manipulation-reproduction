// Original project qualification harness; author kernels remain external and unchanged.
// Build separately for P4_COMAU_MODEL=4, 5, 6 against each pinned model's headers.
// Author literal endpoints: ckcComau2@80089340 run/plan_PCS.cpp:252-253;
// ckcComau/industrialScene@ef6e9c4d run/plan_PCS.cpp:262-263;
// ckcComau3@25488a86 run/plan_PCS.cpp:264-265. No endpoint is projected here.

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>

#include "apc_class.h"
#include "kdl_class.h"

#ifndef P4_COMAU_MODEL
#error Compile with P4_COMAU_MODEL=4, 5, or 6.
#endif
#if P4_COMAU_MODEL != 4 && P4_COMAU_MODEL != 5 && P4_COMAU_MODEL != 6
#error Unsupported Comau model.
#endif

namespace {
constexpr int arms = P4_COMAU_MODEL == 6 ? 3 : 2;
constexpr double author_pi = 3.1416;
using Clock = std::chrono::steady_clock;

void number(std::ostream& out, double x) {
    if (std::isfinite(x)) out << std::setprecision(17) << x;
    else if (std::isnan(x)) out << "\"NaN\"";
    else out << (x < 0 ? "\"-Infinity\"" : "\"Infinity\"");
}
void write_state_json(std::ostream& out, const State& x) {
    out << '[';
    for (std::size_t i = 0; i < x.size(); ++i) { if (i) out << ','; number(out, x[i]); }
    out << ']';
}
void matrix(std::ostream& out, const Matrix& x) {
    out << '[';
    for (std::size_t i = 0; i < x.size(); ++i) { if (i) out << ','; write_state_json(out, x[i]); }
    out << ']';
}
State split(const State& q, int arm) {
    return State(q.begin() + 6 * (arm - 1), q.begin() + 6 * arm);
}
Matrix fk(two_robots& model, const State& q, int arm) {
    model.FKsolve_rob(q, arm);
    if (arm == 1) return model.get_FK_solution_T1();
    if (arm == 2) return model.get_FK_solution_T2();
#if P4_COMAU_MODEL == 6
    if (arm == 3) return model.get_FK_solution_T3();
#endif
    throw std::runtime_error("invalid_arm");
}
State ik_result(two_robots& model, int arm) {
    if (arm == 1) return model.get_IK_solution_q1();
    if (arm == 2) return model.get_IK_solution_q2();
#if P4_COMAU_MODEL == 6
    if (arm == 3) return model.get_IK_solution_q3();
#endif
    throw std::runtime_error("invalid_arm");
}
void all_fk(std::ostream& out, two_robots& model, const State& q) {
    out << '[';
    for (int arm = 1; arm <= arms; ++arm) {
        if (arm > 1) out << ',';
        matrix(out, fk(model, split(q, arm), arm));
    }
    out << ']';
}
void passive_fd(std::ostream& out, two_robots& model, const State& q, int arm, double sign) {
    out << '[';
    for (int joint=0;joint<6;++joint) {
        if (joint) out << ',';
        State shifted=q; shifted[joint]+=sign*1e-6;
        matrix(out,fk(model,shifted,arm));
    }
    out << ']';
}
void closure_fd_record(std::ostream& out, two_robots& model, const char* name, const State& q) {
    out << "{\"type\":\"closure_fd_fixture\",\"name\":\"" << name
        << "\",\"q_rad\":"; write_state_json(out,q);
    out << ",\"epsilon_rad\":1e-6,\"author_fk_reference\":"; all_fk(out,model,q);
    for (int sign : {1,-1}) {
        out << (sign==1?",\"author_fk_plus\":[":",\"author_fk_minus\":[");
        for (std::size_t joint=0;joint<q.size();++joint) {
            if (joint) out << ',';
            State shifted=q; shifted[joint]+=sign*1e-6;
            all_fk(out,model,shifted);
        }
        out << ']';
    }
    out << '}' << std::endl;
}
std::pair<State, State> endpoints() {
#if P4_COMAU_MODEL == 4
    return {{-0.59,1.48,-1.57,-1.36,-0.4,0,1.0144,0.504505,-0.149664,1.6056,-1.17541,0.157832},
            {0.56,0.83,-0.55,-1.36,0.5,0,-0.786965,0.642824,0.316891,2.37455,1.48212,-1.18054}};
#elif P4_COMAU_MODEL == 5
    return {{-0.03,0.33,-0.05,0,1.2908,-1.5808,0.0183141,1.06015,-1.25727,-0.193255,0.200755,0.189466},
            {1.57,0.55,0.73,0,0.2908,0.0092,-1.12171,0.868895,-0.0134552,-1.21367,-1.2759,0.661756}};
#else
    return {{0.01,0.66,-0.92,0,0.29,0,0.26018,-0.106253,0.0485152,1.73479,-0.253422,-1.76992,-0.274494,-0.0556799,0.00153614,-1.70184,-0.286787,1.73772},
            {0.38,0.65,0.21,0,-0.85,0,-0.527848,-0.0288182,1.16444,-0.952929,-1.31305,0.342119,-0.272648,1.22228,-0.804083,-1.07655,-0.761231,0.943446}};
#endif
}
Matrix bases() {
#if P4_COMAU_MODEL == 6
    return {{ROBOT1_X,ROBOT1_Y,ROBOT1_Z,ROBOT1_ROT},
            {ROBOT2_X,ROBOT2_Y,ROBOT2_Z,ROBOT2_ROT},
            {ROBOT3_X,ROBOT3_Y,ROBOT3_Z,ROBOT3_ROT}};
#else
    return {{-ROBOTS_DISTANCE_X/2.0,0,ROBOT1_HEIGHT,0},
            {ROBOTS_DISTANCE_X/2.0,ROBOTS_DISTANCE_Y,ROBOT2_HEIGHT,ROBOT2_ROT}};
#endif
}
const char* source_commit() {
#if P4_COMAU_MODEL == 4
    return "80089340f0f1f6822e5b2821a63c998b6ae0413f";
#elif P4_COMAU_MODEL == 5
    return "ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca";
#else
    return "25488a86947cd07377cc62c43850df719a70d9ee";
#endif
}
void state_record(std::ostream& out, two_robots& model, const char* type,
                  const char* name, const State& q) {
    out << "{\"type\":\"" << type << "\",\"name\":\"" << name << "\",\"q_rad\":";
    write_state_json(out, q); out << ",\"author_fk\":"; all_fk(out, model, q);
    out << '}' << std::endl;
}
}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: comau_qualification NEW_RAW_JSONL SEED\n";
        return 2;
    }
    if (std::filesystem::exists(argv[1])) {
        std::cerr << "refusing_to_overwrite_existing_raw_file\n";
        return 2;
    }
    std::ofstream out(argv[1]);
    if (!out) { std::cerr << "cannot_open_raw_file\n"; return 2; }
    const auto started = Clock::now();
    std::string stage = "constructors";
    auto elapsed = [&]() { return std::chrono::duration<double>(Clock::now() - started).count(); };
    auto budget = [&]() { if (elapsed() >= 120.0) throw std::runtime_error("DIAGNOSTIC_WALL_LIMIT"); };
    try {
        const auto seed = std::stoull(argv[2]);
        // R1 requires a distinct fixed stream per model; argv carries base seed.
        const std::uint64_t effective_seed=seed+1000ULL*P4_COMAU_MODEL;
        std::mt19937_64 rng(effective_seed);
        two_robots apc;
        kdl nr;
        apc.IK_counter = 0; apc.IK_time = 0;
        nr.IK_counter = 0; nr.IK_time = 0;
        const auto raw = endpoints();
        // Distribution uses original author's joint-coordinate limits; no retries.
        const State low = {-author_pi, -60*author_pi/180, -90*author_pi/180,
                           -2700*author_pi/180, -120*author_pi/180, -400*author_pi/180};
        const State high = {author_pi,125*author_pi/180,75*author_pi/180,
                            2700*author_pi/180,120*author_pi/180,400*author_pi/180};
        out << "{\"type\":\"metadata\",\"schema\":\"P4_COMAU_QUALIFICATION_RAW_V1\","
            << "\"classification\":\"INDEPENDENT_QUALIFICATION_NOT_FORMAL_PAPER_TRIALS\","
            << "\"model\":" << P4_COMAU_MODEL << ",\"arms\":" << arms
            << ",\"source_commit\":\"" << source_commit() << "\",\"seed\":" << seed
            << ",\"effective_seed\":" << effective_seed
            << ",\"seed_mapping\":\"base_seed+1000*model\",\"rng\":\"std::mt19937_64\",\"distribution\":\"uniform within declared author joint limits; no rejection or success selection\","
            << "\"fk_count\":100,\"ik_target_count\":10,\"ik_branch_count\":8,\"nr_near_count\":10,"
            << "\"joint_low_rad\":"; write_state_json(out,low);
        out << ",\"joint_high_rad\":"; write_state_json(out,high);
        out << ",\"author_properties_mm\":"; write_state_json(out,apc.get_robots_properties());
        out << ",\"kdl_properties_mm\":"; write_state_json(out,nr.get_robots_properties());
        out << ",\"base_xyz_yaw_mm_rad\":"; matrix(out,bases());
        out << ",\"grasp_transforms\":[";
#if P4_COMAU_MODEL == 6
        matrix(out,apc.getQ12()); out << ','; matrix(out,apc.getQ13());
#else
        matrix(out,apc.getQ());
#endif
        out << "],\"diagnostic_wall_limit_s\":120,\"literal_endpoint_policy\":\"unchanged diagnostics\"}" << std::endl;

        stage = "raw_endpoints";
        state_record(out,apc,"raw_endpoint","start",raw.first);
        state_record(out,apc,"raw_endpoint","goal",raw.second);

        std::vector<State> fixed_samples;
        stage = "fk_samples";
        for (int i = 0; i < 100; ++i) {
            budget(); State q(6*arms);
            for (int arm = 0; arm < arms; ++arm)
                for (int j = 0; j < 6; ++j)
                    q[6*arm+j] = std::uniform_real_distribution<double>(low[j],high[j])(rng);
            fixed_samples.push_back(q);
            out << "{\"type\":\"fk_sample\",\"sample\":" << i << ",\"q_rad\":";
            write_state_json(out,q); out << ",\"author_fk\":"; all_fk(out,apc,q);
            out << '}' << std::endl;
        }

        stage = "ik_roundtrip";
        for (int i = 0; i < 10; ++i) {
            const int arm = i%arms+1;
            const State q_source = split(fixed_samples.at(i),arm);
            const Matrix target = fk(apc,q_source,arm);
            for (int branch = 0; branch < 8; ++branch) {
                budget(); const auto t0 = Clock::now();
                const bool accepted = apc.IKsolve_rob(target,arm,branch);
                const double call_s = std::chrono::duration<double>(Clock::now()-t0).count();
                out << "{\"type\":\"ik_roundtrip\",\"sample\":" << i << ",\"arm\":" << arm
                    << ",\"branch\":" << branch << ",\"source_q_rad\":";
                write_state_json(out,q_source); out << ",\"target\":"; matrix(out,target);
                out << ",\"accepted\":" << (accepted?"true":"false") << ",\"wall_s\":"; number(out,call_s);
                out << ",\"q_result_rad\":";
                if (accepted) { const State result=ik_result(apc,arm); write_state_json(out,result);
                    out << ",\"author_result_fk\":"; matrix(out,fk(apc,result,arm)); }
                else out << "null,\"author_result_fk\":null";
                out << '}' << std::endl;
            }
        }

        stage = "nr_near_endpoints";
        for (int i = 0; i < 10; ++i) {
            budget(); const State& original = i%2 ? raw.second : raw.first;
            State input=original,offset(input.size());
            for (std::size_t j=0;j<input.size();++j) {
                offset[j] = (rng() & 1ULL) ? 0.01 : -0.01;
                input[j] += offset[j];
            }
            const auto t0=Clock::now(); const bool accepted=nr.GD(input);
            const double call_s=std::chrono::duration<double>(Clock::now()-t0).count();
            out << "{\"type\":\"nr_near_endpoint\",\"sample\":" << i << ",\"anchor\":\""
                << (i%2?"goal":"start") << "\",\"anchor_q_rad\":";
            write_state_json(out,original); out << ",\"offset_rad\":"; write_state_json(out,offset);
            out << ",\"input_q_rad\":"; write_state_json(out,input);
            out << ",\"accepted\":" << (accepted?"true":"false") << ",\"wall_s\":"; number(out,call_s);
            out << ",\"q_result_rad\":";
            if (accepted) { const State result=nr.get_GD_result(); write_state_json(out,result);
                out << ",\"author_result_fk\":"; all_fk(out,apc,result); }
            else out << "null,\"author_result_fk\":null";
            out << '}' << std::endl;
        }

        stage = "negative_cases";
        State perturbed=raw.first; perturbed[0]+=0.1;
        state_record(out,apc,"negative_state","closure_perturbation_first_joint_0.1_rad",perturbed);
        Matrix far=fk(apc,split(raw.first,2),2); far[0][3]=100000000.0;
        for (int branch=0;branch<8;++branch) {
            budget(); const bool accepted=apc.IKsolve_rob(far,2,branch);
            out << "{\"type\":\"far_unreachable_ik\",\"arm\":2,\"branch\":" << branch
                << ",\"target\":"; matrix(out,far);
            out << ",\"accepted\":" << (accepted?"true":"false") << '}' << std::endl;
        }
        // R1 fixtures: save actual author FK central differences at frozen epsilon.
        // Separate Python computes native/independent SVD, never from IK labels.
        const State regular={0.37,0.21,-1.5708,0.48,0.71,-0.31};
        for (int arm=1;arm<=arms;++arm) {
            for (int mode=0;mode<3;++mode) {
                budget(); State q=regular;
                if (mode==1) q[4]=0;
                if (mode==2) q[2]=-author_pi/2.0;
                const char* name=mode==0?"regular_passive_jacobian_positive_control":
                    mode==1?"wrist_singular_q5_zero":"author_elbow_only_q3_minus_PI_over_2";
                out << "{\"type\":\"passive_fixture\",\"name\":\"" << name
                    << "\",\"arm\":" << arm << ",\"q_rad\":"; write_state_json(out,q);
                out << ",\"author_fk\":"; matrix(out,fk(apc,q,arm));
                out << ",\"epsilon_rad\":1e-6,\"author_fk_plus\":"; passive_fd(out,apc,q,arm,1);
                out << ",\"author_fk_minus\":"; passive_fd(out,apc,q,arm,-1);
                out << '}' << std::endl;
            }
        }
        stage = "native_closure_jacobians";
        budget(); closure_fd_record(out,apc,"start",raw.first);
        budget(); closure_fd_record(out,apc,"goal",raw.second);
        out << "{\"type\":\"completion\",\"status\":\"RAW_DIAGNOSTICS_COMPLETED_NOT_QUALIFIED\",\"wall_s\":";
        number(out,elapsed()); out << '}' << std::endl;
        return 0;
    } catch (const std::exception& error) {
        out << "{\"type\":\"failure\",\"status\":\"FAIL_STOP\",\"stage\":\""
            << stage << "\",\"reason\":\"" << error.what() << "\",\"wall_s\":";
        number(out,elapsed()); out << '}' << std::endl;
        return 1;
    }
}
