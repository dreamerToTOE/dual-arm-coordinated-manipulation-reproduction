// PROJECT-OWNED DRAFT. NOT BUILT, EXECUTED, QUALIFIED, OR A SPEED BASELINE.
// PRE: reports/P4_FULL_R2_NR_THIN_INTERFACE_SOURCE_AUDIT_PRE_DRAFT_20261015.md
// Port target: immutable physical_nr.py + abb_independent_oracle.py.
// This is reconstructed physical full-Jacobian NR, NOT author-native KDL.
// Only environments II/III are implemented here. No planner/RBS/collision,
// random sampling, IPC, or author-source mutation is performed by this header.
#pragma once

#include <Eigen/Core>
#include <Eigen/Geometry>
#include <Eigen/SVD>
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace p4nr_draft {
using Vector = Eigen::VectorXd;
using Matrix = Eigen::MatrixXd;
using Vec3 = Eigen::Vector3d;
using Mat3 = Eigen::Matrix3d;
using Mat4 = Eigen::Matrix4d;
using Jacobian6 = Eigen::Matrix<double, 6, 6>;
constexpr double author_pi = 3.1416;

struct Options {
    double wall_limit_s = 120.;
    int max_iterations = 10000;
    double position_gate = 1e-5;
    double rotation_gate = 1e-5;
    double svd_relative = 1e-12;
    bool detailed_trace = false;
};

struct Metrics {
    double translation_max_abs = 0.;  // millimetres
    double rotation_matrix_max_abs = 0.;
    double rotation_angle_max_rad = 0.;
    const char* position_unit = "mm";
};

struct Step {
    int iteration = 0;
    Vector q_before;
    Vector g;
    Matrix j;
    Metrics metrics;
    Vector singular_values;  // Empty when no update is attempted.
    double cutoff = 0.;
    int numerical_rank = 0;
    Vector delta_q;  // Actual proposal q_next - q_before, without clipping.
    Vector q_next;
};

struct Result {
    std::string status = "ITERATION_LIMIT";
    Vector input_q_rad;
    Vector candidate_q_rad;
    bool candidate_is_finite = false;
    bool has_metrics = false;
    Metrics metrics;
    std::vector<Step> trace;
    int accepted_updates = 0;
    double wall_s = 0.;
    const char* method = "Paper full-Jacobian pseudoinverse NR, Eigen C++ DRAFT";
    bool collision_checked = false;
};

inline void require_environment(const std::string& env) {
    if (env != "II" && env != "III")
        throw std::invalid_argument("DRAFT_ONLY_ENVIRONMENT_II_III");
}

inline Mat4 translation(const Vec3& p) {
    Mat4 t = Mat4::Identity();
    t.topRightCorner<3, 1>() = p;
    return t;
}

inline Mat4 rotation(char axis, double angle) {
    const double c = std::cos(angle), s = std::sin(angle);
    Mat4 r = Mat4::Identity();
    if (axis == 'x') {
        r(1, 1) = c; r(1, 2) = -s; r(2, 1) = s; r(2, 2) = c;
    } else if (axis == 'y') {
        r(0, 0) = c; r(0, 2) = s; r(2, 0) = -s; r(2, 2) = c;
    } else if (axis == 'z') {
        r(0, 0) = c; r(0, 1) = -s; r(1, 0) = s; r(1, 1) = c;
    } else {
        throw std::invalid_argument("UNKNOWN_REVOLUTE_AXIS");
    }
    return r;
}

inline Mat3 skew(const Vec3& v) {
    Mat3 k;
    k << 0., -v.z(), v.y(), v.z(), 0., -v.x(), -v.y(), v.x(), 0.;
    return k;
}

inline Vec3 log_so3(const Mat3& r) {
    const Vec3 axial((r(2, 1) - r(1, 2)) / 2.,
                     (r(0, 2) - r(2, 0)) / 2.,
                     (r(1, 0) - r(0, 1)) / 2.);
    const double s = axial.norm(), c = (r.trace() - 1.) / 2.;
    const double theta = std::atan2(s, c);
    const double true_pi = std::acos(-1.);
    if (true_pi - theta < 1e-7)
        throw std::invalid_argument("SO3_PRINCIPAL_CHART_NEAR_PI");
    return theta < 1e-7 ? (axial * (1. + theta * theta / 6.)).eval()
                         : (axial * (theta / s)).eval();
}

inline Mat3 left_jacobian_inverse(const Vec3& phi) {
    const double theta = phi.norm();
    const Mat3 k = skew(phi);
    const double theta2 = theta * theta;
    const double coef = theta < 1e-4 ? 1. / 12. + theta2 / 720.
        : 1. / theta2 - (1. + std::cos(theta)) /
          (2. * theta * std::sin(theta));
    return (Mat3::Identity() - k / 2. + coef * (k * k)).eval();
}

struct ArmSample {
    Mat4 pose;
    Jacobian6 jacobian;
};

// Exact axes/offset order of the qualified independent ABB oracle.
// Inputs are radians; base = [x_mm,y_mm,yaw_rad]. No exact-pi substitution.
inline ArmSample abb_fk_and_jacobian(const Vector& q, const Vec3& base) {
    if (q.size() != 6 || !q.allFinite() || !base.allFinite())
        throw std::invalid_argument("EXPECTED_FINITE_ABB_Q6_BASE3");
    constexpr std::array<char, 6> axes = {'z', 'y', 'y', 'x', 'y', 'x'};
    const std::array<Vec3, 6> offsets = {Vec3(0., 0., 124.),
        Vec3(0., 0., 270.), Vec3(149.6, 0., 70.), Vec3(152.4, 0., 0.),
        Vec3(65.5, 0., 0.), Vec3(66.5, 0., 0.)};
    Mat4 t = (translation(Vec3(base.x(), base.y(), 166.)) *
              rotation('z', base.z())).eval();
    std::array<Vec3, 6> origins, directions;
    for (int i = 0; i < 6; ++i) {
        const Vec3 local_axis = axes[i] == 'x' ? Vec3(1., 0., 0.)
            : axes[i] == 'y' ? Vec3(0., 1., 0.) : Vec3(0., 0., 1.);
        origins[i] = t.topRightCorner<3, 1>();
        directions[i] = t.topLeftCorner<3, 3>() * local_axis;
        t = (t * rotation(axes[i], q[i])).eval();
        t = (t * translation(offsets[i])).eval();
    }
    ArmSample out;
    out.pose = t;
    const Vec3 endpoint = t.topRightCorner<3, 1>();
    for (int i = 0; i < 6; ++i) {
        out.jacobian.topRows<3>().col(i) =
            directions[i].cross(endpoint - origins[i]);
        out.jacobian.bottomRows<3>().col(i) = directions[i];
    }
    return out;
}

inline std::pair<ArmSample, ArmSample> arm_samples(const Vector& q,
                                                 const std::string& env) {
    require_environment(env);
    if (q.size() != 12)
        throw std::invalid_argument("WRONG_NUMBER_OF_PHYSICAL_COORDINATES");
    if (!q.allFinite())
        throw std::invalid_argument("NONFINITE_CONFIGURATION");
    const double d = env == "II" ? 900. : 1200.;
    return {abb_fk_and_jacobian(q.head(6), Vec3(-d / 2., 0., 0.)),
            abb_fk_and_jacobian(q.tail(6), Vec3(d / 2., 0., author_pi))};
}

inline Mat4 grasp(const std::string& env) {
    require_environment(env);
    return translation(Vec3(env == "II" ? 300. : 500., 0., 0.));
}

inline Mat4 flip() {
    Mat4 s = Mat4::Identity();
    s(0, 0) = -1.; s(1, 1) = -1.;
    return s;
}

inline Mat4 target_pose(const Mat4& first_pose, const std::string& env) {
    const Mat4 with_grasp = (first_pose * grasp(env)).eval();
    return (with_grasp * flip()).eval();
}

// Dynamic matrix permits Eigen's thin U/V. The intended shape is 6x12.
inline std::pair<Vector, Matrix> closure_vector_jacobian(
        const Vector& q, const std::string& env) {
    const auto samples = arm_samples(q, env);
    const auto& a = samples.first;
    const auto& b = samples.second;
    const Mat4 target = target_pose(a.pose, env);
    const Mat3 e = (b.pose.topLeftCorner<3, 3>() *
                   target.topLeftCorner<3, 3>().transpose()).eval();
    const Vec3 phi = log_so3(e);
    Vector g(6);
    g.head<3>() = b.pose.topRightCorner<3, 1>() - target.topRightCorner<3, 1>();
    g.tail<3>() = phi;
    Matrix j = Matrix::Zero(6, 12);
    const Vec3 offset = (a.pose.topLeftCorner<3, 3>() *
                         grasp(env).topRightCorner<3, 1>()).eval();
    j.block<3, 6>(0, 0) = (-a.jacobian.topRows<3>() +
        skew(offset) * a.jacobian.bottomRows<3>()).eval();
    j.block<3, 6>(0, 6) = b.jacobian.topRows<3>();
    const Mat3 log_j = left_jacobian_inverse(phi);
    const Mat3 negative_log_e = ((-log_j) * e).eval();
    j.block<3, 6>(3, 0) = (negative_log_e * a.jacobian.bottomRows<3>()).eval();
    j.block<3, 6>(3, 6) = (log_j * b.jacobian.bottomRows<3>()).eval();
    return {std::move(g), std::move(j)};
}

inline Metrics residual_metrics(const Vector& q, const std::string& env) {
    // Re-evaluate as in the immutable Python reference. Do not infer a pass
    // merely from the logarithm g: the acceptance gate is matrix-entry error.
    const auto samples = arm_samples(q, env);
    const Mat4 target = target_pose(samples.first.pose, env);
    const Mat4 error = (samples.second.pose - target).eval();
    const Mat3 e = (samples.second.pose.topLeftCorner<3, 3>() *
                   target.topLeftCorner<3, 3>().transpose()).eval();
    Metrics out;
    out.translation_max_abs = error.topRightCorner<3, 1>().cwiseAbs().maxCoeff();
    out.rotation_matrix_max_abs = error.topLeftCorner<3, 3>().cwiseAbs().maxCoeff();
    out.rotation_angle_max_rad = log_so3(e).norm();
    return out;
}

inline Matrix source_limits(const std::string& env) {
    require_environment(env);
    constexpr double degrees[6][2] = {{-165., 165.}, {-110., 110.},
        {-110., 70.}, {-160., 160.}, {-120., 120.}, {-400., 400.}};
    Matrix bounds(12, 2);
    for (int i = 0; i < 12; ++i)
        for (int k = 0; k < 2; ++k)
            bounds(i, k) = degrees[i % 6][k] * author_pi / 180.;
    return bounds;
}

inline Vector periodic_chart(const Vector& input, const std::string& env) {
    require_environment(env);
    Vector q = input;
    for (Eigen::Index i = 0; i < q.size(); ++i)
        q[i] = std::atan2(std::sin(q[i]), std::cos(q[i]));
    return q;
}

inline bool passes(const Metrics& m, const Options& options) {
    return m.translation_max_abs <= options.position_gate &&
           m.rotation_matrix_max_abs <= options.rotation_gate;
}

inline Result project_nr(const Vector& input, const std::string& env,
                         const Options& options = Options{}) {
    const auto started = std::chrono::steady_clock::now();
    const auto elapsed = [&]() {
        return std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started).count();
    };
    Result out;
    out.input_q_rad = input;
    Vector q = input;
    try {
        const Matrix bounds = source_limits(env);
        if (q.size() != 12)
            throw std::invalid_argument("WRONG_NUMBER_OF_PHYSICAL_COORDINATES");
        for (int iteration = 0; iteration <= options.max_iterations; ++iteration) {
            if (elapsed() >= options.wall_limit_s) {
                out.status = "WALL_LIMIT";
                break;
            }
            const auto gj = closure_vector_jacobian(q, env);
            const Vector& g = gj.first;
            const Matrix& j = gj.second;
            out.metrics = residual_metrics(q, env);
            out.has_metrics = true;
            if (options.detailed_trace) {
                Step step;
                step.iteration = iteration;
                step.q_before = q;
                step.g = g;
                step.j = j;
                step.metrics = out.metrics;
                out.trace.push_back(std::move(step));
            }
            if (passes(out.metrics, options)) {
                q = periodic_chart(q, env);
                out.metrics = residual_metrics(q, env);
                const bool legal = (q.array() >= bounds.col(0).array()).all() &&
                                   (q.array() <= bounds.col(1).array()).all();
                out.status = !passes(out.metrics, options)
                    ? "POST_CHART_RESIDUAL_REJECTED"
                    : legal ? "CONVERGED" : "CLOSED_BUT_JOINT_LIMIT_REJECTED";
                break;
            }
            if (iteration == options.max_iterations)
                break;
            const Eigen::JacobiSVD<Matrix> svd(j, Eigen::ComputeThinU | Eigen::ComputeThinV);
            if (svd.info() != Eigen::Success)
                throw std::runtime_error("EIGEN_SVD_DID_NOT_CONVERGE");
            const Vector s = svd.singularValues();
            const double cutoff = s[0] * options.svd_relative;
            Vector inv = Vector::Zero(s.size());
            int rank = 0;
            for (Eigen::Index i = 0; i < s.size(); ++i) {
                if (s[i] > cutoff) {
                    inv[i] = 1. / s[i];
                    ++rank;
                }
            }
            const Vector inner = (svd.matrixU().transpose() * g).eval();
            const Vector weighted = (inv.array() * inner.array()).matrix();
            const Vector correction = (svd.matrixV() * weighted).eval();
            q -= correction;
            ++out.accepted_updates;
            if (options.detailed_trace) {
                Step& step = out.trace.back();
                step.singular_values = s;
                step.cutoff = cutoff;
                step.numerical_rank = rank;
                step.delta_q = -correction;
                step.q_next = q;
            }
            if (!q.allFinite()) {
                out.status = "NONFINITE";
                break;
            }
        }
    } catch (const std::exception& error) {
        out.status = error.what();
    }
    out.candidate_is_finite = q.allFinite();
    if (out.candidate_is_finite)
        out.candidate_q_rad = q;
    out.wall_s = elapsed();
    return out;
}
}  // namespace p4nr_draft
