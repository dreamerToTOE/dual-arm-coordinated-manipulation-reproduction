// Project-owned batch interface; link only the separately staged author APC.
// Compile with P4_MODEL=0 (ABB), 4, 5, or 6.  No KDL or planner is used.
// Usage: spatial_batch_driver NEW_OUTPUT_FILE [--env II|III]
// The --env argument is required for ABB and may appear before the filename.
// stdin: F arm q1 q2 q3 q4 q5 q6
//        K arm branch T00 T01 ... T33   (16 row-major entries)
// stdout and NEW_OUTPUT_FILE: exactly one JSON object per input line.
// Matrices in the JSON are nested row-major 4x4 arrays.  Original targets are
// echoed unchanged: no rounding, orthogonalization, projection or NR fallback.

#include <cerrno>
#include <cmath>
#include <fcntl.h>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <unistd.h>

#include "apc_class.h"

#ifndef P4_MODEL
#error Compile with P4_MODEL=0, 4, 5, or 6.
#endif
#if P4_MODEL != 0 && P4_MODEL != 4 && P4_MODEL != 5 && P4_MODEL != 6
#error Unsupported P4_MODEL.
#endif

namespace {
constexpr int p4_arm_count = P4_MODEL == 6 ? 3 : 2;
constexpr const char* p4_schema = "P4_SPATIAL_BATCH_V1";

void write_number(std::ostream& out, double value) {
    if (std::isfinite(value)) out << std::setprecision(17) << value;
    else if (std::isnan(value)) out << "\"NaN\"";
    else out << (value < 0 ? "\"-Infinity\"" : "\"Infinity\"");
}

void write_string(std::ostream& out, const std::string& value) {
    static constexpr char hex[] = "0123456789abcdef";
    out << '"';
    for (const unsigned char ch : value) {
        switch (ch) {
        case '"': out << "\\\""; break;
        case '\\': out << "\\\\"; break;
        case '\b': out << "\\b"; break;
        case '\f': out << "\\f"; break;
        case '\n': out << "\\n"; break;
        case '\r': out << "\\r"; break;
        case '\t': out << "\\t"; break;
        default:
            if (ch < 0x20) out << "\\u00" << hex[ch >> 4] << hex[ch & 15];
            else out << static_cast<char>(ch);
        }
    }
    out << '"';
}

void write_state(std::ostream& out, const State& q) {
    out << '[';
    for (std::size_t i = 0; i < q.size(); ++i) {
        if (i) out << ',';
        write_number(out, q[i]);
    }
    out << ']';
}

void write_matrix(std::ostream& out, const Matrix& matrix) {
    out << '[';
    for (std::size_t row = 0; row < matrix.size(); ++row) {
        if (row) out << ',';
        write_state(out, matrix[row]);
    }
    out << ']';
}

bool finite_state(const State& q) {
    for (const double value : q) if (!std::isfinite(value)) return false;
    return true;
}

bool finite_matrix(const Matrix& matrix) {
    for (const State& row : matrix) if (!finite_state(row)) return false;
    return true;
}

// Author constructors print a status line.  Author diagnostics are routed to
// stderr so they cannot corrupt the one-request/one-JSON stdout contract.
class AuthorStdoutToStderr {
public:
    AuthorStdoutToStderr() : saved_(std::cout.rdbuf(std::cerr.rdbuf())) {}
    ~AuthorStdoutToStderr() { std::cout.rdbuf(saved_); }
    AuthorStdoutToStderr(const AuthorStdoutToStderr&) = delete;
    AuthorStdoutToStderr& operator=(const AuthorStdoutToStderr&) = delete;
private:
    std::streambuf* saved_;
};

// POSIX O_EXCL makes non-overwrite atomic, including an existing symlink.
// A failed or interrupted output is retained; this class never removes it.
class ExclusiveOutput {
public:
    explicit ExclusiveOutput(const std::string& filename) {
        descriptor_ = ::open(filename.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0644);
        if (descriptor_ < 0)
            throw std::system_error(errno, std::generic_category(), "cannot create NEW_OUTPUT_FILE");
    }
    ~ExclusiveOutput() { if (descriptor_ >= 0) ::close(descriptor_); }
    void append(const std::string& value) {
        std::size_t written = 0;
        while (written < value.size()) {
            const ssize_t n = ::write(descriptor_, value.data() + written, value.size() - written);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0)
                throw std::system_error(n < 0 ? errno : EIO, std::generic_category(), "cannot append JSON evidence");
            written += static_cast<std::size_t>(n);
        }
    }
    void finish() {
        if (::fsync(descriptor_) != 0)
            throw std::system_error(errno, std::generic_category(), "cannot sync JSON evidence");
    }
    ExclusiveOutput(const ExclusiveOutput&) = delete;
    ExclusiveOutput& operator=(const ExclusiveOutput&) = delete;
private:
    int descriptor_ = -1;
};

struct Arguments {
    std::string filename;
    std::string environment;
};

Arguments parse_arguments(int argc, char** argv) {
    Arguments result;
    for (int i = 1; i < argc; ++i) {
        const std::string token = argv[i];
        if (token == "--env") {
            if (!result.environment.empty() || ++i >= argc)
                throw std::runtime_error("--env must occur once with an environment value");
            result.environment = argv[i];
        } else if (token.rfind("--", 0) == 0) {
            throw std::runtime_error("unknown argument: " + token);
        } else if (result.filename.empty()) {
            result.filename = token;
        } else {
            throw std::runtime_error("only one NEW_OUTPUT_FILE is accepted");
        }
    }
    if (result.filename.empty())
        throw std::runtime_error("usage: spatial_batch_driver NEW_OUTPUT_FILE [--env II|III]");
#if P4_MODEL == 0
    if (result.environment != "II" && result.environment != "III")
        throw std::runtime_error("ABB requires --env II or --env III");
#else
#if P4_MODEL == 4
    const std::string expected = "IV";
#elif P4_MODEL == 5
    const std::string expected = "V";
#else
    const std::string expected = "VI";
#endif
    if (!result.environment.empty() && result.environment != expected)
        throw std::runtime_error("--env does not match compiled Comau model");
    result.environment = expected;
#endif
    return result;
}

std::unique_ptr<two_robots> make_model(const std::string& environment) {
    AuthorStdoutToStderr redirect;
#if P4_MODEL == 0
    // Exact initialization from baselines/p4_full/abb_native_qualification.cpp.
    // The physical base yaw deliberately remains the author's literal 3.1416.
    const bool ii = environment == "II";
    const double distance = ii ? 900.0 : 1200.0;
    const double rod_length = ii ? 300.0 : 500.0;
    const State base1 = {-distance / 2.0, 0.0, 0.0};
    const State base2 = {distance / 2.0, 0.0, 3.1416};
    auto result = std::make_unique<two_robots>(base1, base2, rod_length);
#else
    (void)environment;
    auto result = std::make_unique<two_robots>();
#endif
    result->IK_counter = 0;
    result->IK_time = 0.0;
    return result;
}

Matrix native_fk(two_robots& model, const State& q, int arm) {
    model.FKsolve_rob(q, arm);
    if (arm == 1) return model.get_FK_solution_T1();
    if (arm == 2) return model.get_FK_solution_T2();
#if P4_MODEL == 6
    if (arm == 3) return model.get_FK_solution_T3();
#endif
    throw std::runtime_error("invalid FK arm");
}

State native_ik_result(two_robots& model, int arm) {
    if (arm == 1) return model.get_IK_solution_q1();
    if (arm == 2) return model.get_IK_solution_q2();
#if P4_MODEL == 6
    if (arm == 3) return model.get_IK_solution_q3();
#endif
    throw std::runtime_error("invalid IK arm");
}

std::string process_line(two_robots& model, const std::string& line,
                         std::size_t line_number, const std::string& environment) {
    std::string operation;
    int arm = 0, branch = -1;
    State input_q;
    Matrix target, fk_result;
    State solution;
    bool parsed_q = false, parsed_target = false;
    bool success = false, finite = false, have_solution = false, have_fk = false;
    std::string error;
    try {
        std::istringstream input(line);
        if (!(input >> operation >> arm)) throw std::runtime_error("expected operation and arm");
        if (arm < 1 || arm > p4_arm_count) throw std::runtime_error("arm outside compiled model");
        if (operation == "F") {
            input_q.resize(6);
            for (double& value : input_q)
                if (!(input >> value)) throw std::runtime_error("F requires exactly six numeric joint angles");
            parsed_q = true;
            if (!finite_state(input_q)) throw std::runtime_error("nonfinite F input");
        } else if (operation == "K") {
            if (!(input >> branch) || branch < 0 || branch >= NUM_IK_SOLUTIONS)
                throw std::runtime_error("K branch must be one of 0..7");
            target.assign(4, State(4));
            for (State& row : target)
                for (double& value : row)
                    if (!(input >> value)) throw std::runtime_error("K requires exactly sixteen row-major target entries");
            parsed_target = true;
            if (!finite_matrix(target)) throw std::runtime_error("nonfinite K target");
        } else {
            throw std::runtime_error("unknown operation; expected F or K");
        }
        std::string extra;
        if (input >> extra) throw std::runtime_error("unexpected trailing input token");

        AuthorStdoutToStderr redirect;
        if (operation == "F") {
            fk_result = native_fk(model, input_q, arm);
            have_fk = true;
            finite = finite_matrix(fk_result);
            success = finite;
        } else {
            // success is the source IK bool, kept independent of finite checks.
            success = model.IKsolve_rob(target, arm, branch);
            if (success) {
                solution = native_ik_result(model, arm);
                have_solution = true;
                if (solution.size() != 6) throw std::runtime_error("source returned non-six-dimensional IK state");
                fk_result = native_fk(model, solution, arm);
                have_fk = true;
                finite = finite_state(solution) && finite_matrix(fk_result);
            }
        }
    } catch (const std::exception& exception) {
        error = exception.what();
    }

    const bool canonical = operation == "K" && success && have_solution
                           && solution.size() == 6 && solution[4] == 0.0;
    std::ostringstream out;
    out << "{\"schema\":\"" << p4_schema << "\",\"input_line\":" << line_number
        << ",\"model\":" << P4_MODEL << ",\"environment\":";
    write_string(out, environment);
    out << ",\"op\":"; write_string(out, operation);
    out << ",\"arm\":" << arm << ",\"branch\":";
    if (operation == "K") out << branch; else out << "null";
    out << ",\"q\":";
    if (parsed_q) write_state(out, input_q); else out << "null";
    out << ",\"target\":";
    if (parsed_target) write_matrix(out, target); else out << "null";
    out << ",\"success\":" << (success ? "true" : "false")
        << ",\"finite\":" << (finite ? "true" : "false") << ",\"solution\":";
    if (have_solution) write_state(out, solution); else out << "null";
    out << ",\"T\":";
    if (have_fk) write_matrix(out, fk_result); else out << "null";
    out << ",\"canonical_wrist\":" << (canonical ? "true" : "false")
        << ",\"canonical_wrist_note\":";
    if (canonical) write_string(out, "q5=0 canonical representative; complete singular family is not enumerated");
    else out << "null";
    out << ",\"error\":";
    if (error.empty()) out << "null"; else write_string(out, error);
    out << ",\"raw_input\":"; write_string(out, line);
    out << "}\n";
    return out.str();
}
}  // namespace

int main(int argc, char** argv) {
    try {
        const Arguments arguments = parse_arguments(argc, argv);
        ExclusiveOutput evidence(arguments.filename);
        auto model = make_model(arguments.environment);
        std::string line;
        std::size_t line_number = 0;
        while (std::getline(std::cin, line)) {
            const std::string json = process_line(*model, line, ++line_number, arguments.environment);
            evidence.append(json);
            std::cout << json << std::flush;
            if (!std::cout) throw std::runtime_error("stdout write failed; prior rows retained in NEW_OUTPUT_FILE");
        }
        if (std::cin.bad()) throw std::runtime_error("stdin read failed");
        evidence.finish();
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "spatial_batch_driver: " << exception.what() << '\n';
        return 2;
    }
}
