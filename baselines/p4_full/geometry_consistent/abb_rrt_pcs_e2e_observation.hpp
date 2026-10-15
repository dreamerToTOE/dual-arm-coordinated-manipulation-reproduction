// Project-owned I/O observation only. No FK/IK/collision or algorithm repair.
#pragma once
#include <nlohmann/json.hpp>
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <cerrno>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <system_error>
#include <unistd.h>
#include <vector>

namespace p4e2e {
using json=nlohmann::json;
inline int reconstruction_fd=-1;
inline int identify_fd=-1;
inline std::size_t identify_count=0;
inline std::vector<json> reconstruction_attempts;
inline int exclusive(const std::string& filename) {
    int fd=::open(filename.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC,0644);
    if(fd<0)throw std::system_error(errno,std::generic_category(),"EXCLUSIVE_OUTPUT "+filename);
    return fd;
}
inline void append(int fd,const std::string& text) {
    std::size_t at=0;
    while(at<text.size()) {
        auto n=::write(fd,text.data()+at,text.size()-at);
        if(n<0&&errno==EINTR)continue;
        if(n<=0)throw std::system_error(n<0?errno:EIO,std::generic_category(),"EVIDENCE_WRITE");
        at+=static_cast<std::size_t>(n);
    }
}
inline void write_new_json(const std::string& filename,const json& value) {
    int fd=exclusive(filename);
    try { append(fd,value.dump(2)+"\n");if(::fsync(fd))throw std::system_error(errno,std::generic_category(),"EVIDENCE_SYNC"); }
    catch(...) {::close(fd);throw;}
    ::close(fd);
}
inline std::vector<double> q12(const ompl::base::State* state) {
    const auto* s=state->as<ompl::base::RealVectorStateSpace::StateType>();
    return {s->values,s->values+12};
}
inline void observe_reconstruction(const ompl::base::State* a,const ompl::base::State* b,
        int role,int branch,const std::vector<std::vector<double>>& confs,bool returned) {
    json row={{"schema","P4_ABB_RRT_PCS_RECONSTRUCTION_V1"},
        {"attempt_index",reconstruction_attempts.size()},
        {"observation","ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN"},
        {"qa12",q12(a)},{"qb12",q12(b)},{"active_chain",role},{"branch",branch},
        {"returned",returned},{"path_q12",confs}};
    // nlohmann emits round-trip binary64 precision (up to max_digits10=17).
    // Record only after the complete original state-level call has returned.
    if(reconstruction_fd<0)throw std::runtime_error("RECONSTRUCTION_LOG_NOT_OPEN");
    append(reconstruction_fd,row.dump()+"\n");
    reconstruction_attempts.push_back(std::move(row));
}
inline void observe_identify(const std::vector<double>& a,const std::vector<double>& b,
        const std::vector<double>& input_ik,const std::vector<double>& returned_ik) {
    std::vector<double> q=a;q.insert(q.end(),b.begin(),b.end());
    json row={{"schema","P4_ABB_RRT_PCS_IDENTIFY_V1"},{"call_index",identify_count},
        {"observation","ORIGINAL_VECTOR_IDENTIFY_CALL_COMPLETED_POST_RETURN"},
        {"q12",q},{"input_ik",input_ik},{"returned_ik",returned_ik}};
    if(identify_fd<0)throw std::runtime_error("IDENTIFY_LOG_NOT_OPEN");
    append(identify_fd,row.dump()+"\n");++identify_count;
}
}
