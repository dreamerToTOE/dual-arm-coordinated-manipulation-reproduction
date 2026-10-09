#include "baselines/p4_closed_chain/projection.hpp"
#include <Eigen/SVD>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <exception>

namespace p4
{
const char* statusName(ProjectionStatus status)
{
  switch(status)
  {
    case ProjectionStatus::CONVERGED: return "CONVERGED";
    case ProjectionStatus::INVALID_OPTIONS: return "INVALID_OPTIONS";
    case ProjectionStatus::INVALID_INPUT: return "INVALID_INPUT";
    case ProjectionStatus::INITIAL_JOINT_LIMIT: return "INITIAL_JOINT_LIMIT";
    case ProjectionStatus::ITERATION_LIMIT: return "ITERATION_LIMIT";
    case ProjectionStatus::RANK_DEFICIENT: return "RANK_DEFICIENT";
    case ProjectionStatus::UPDATE_JOINT_LIMIT: return "UPDATE_JOINT_LIMIT";
    case ProjectionStatus::NONFINITE_EVALUATION: return "NONFINITE_EVALUATION";
    case ProjectionStatus::EVALUATION_ERROR: return "EVALUATION_ERROR";
    case ProjectionStatus::BOUNDS_ERROR: return "BOUNDS_ERROR";
    case ProjectionStatus::NONFINITE_UPDATE: return "NONFINITE_UPDATE";
    case ProjectionStatus::STAGNATION: return "STAGNATION";
  }
  return "UNKNOWN";
}

ProjectionResult project(const JointVector& initial_q,
                         const ConstraintEvaluator& evaluate_constraint,
                         const JointMarginEvaluator& native_joint_margin,
                         const ProjectionOptions& options)
{
  // walltime仅用于离线算法计算成本，不是物理时间/运动执行时间。
  const auto begin=std::chrono::steady_clock::now();
  ProjectionResult out;
  out.initial_q=initial_q;
  out.projected_q=initial_q;
  const auto finish=[&](ProjectionStatus status,const std::string& reason) {
    out.status=status;
    out.reason=reason;
    if (out.initial_q.allFinite() && out.projected_q.allFinite())
    {
      const JointVector delta=out.projected_q-out.initial_q;
      out.joint_delta_norm_rad=delta.norm();
      out.joint_delta_max_abs_rad=delta.cwiseAbs().maxCoeff();
    }
    out.compute_wall_time_sec=std::chrono::duration<double>(
      std::chrono::steady_clock::now()-begin).count();
    return out;
  };
  const auto positive=[](double value){return std::isfinite(value) && value>0.;};
  if (!positive(options.position_tolerance_m) || !positive(options.rotation_tolerance_rad) ||
      !std::isfinite(options.svd_absolute_cutoff) || options.svd_absolute_cutoff<0. ||
      !positive(options.svd_relative_cutoff) || options.svd_relative_cutoff>=1. ||
      !std::isfinite(options.stagnation_step_rad) || options.stagnation_step_rad<0.)
    return finish(ProjectionStatus::INVALID_OPTIONS,"Invalid explicitly supplied engineering options");
  if (!initial_q.allFinite() || !evaluate_constraint || !native_joint_margin)
    return finish(ProjectionStatus::INVALID_INPUT,"Finite input q and both read-only callbacks required");

  double margin;
  try { margin=native_joint_margin(initial_q); }
  catch(const std::exception& e) {return finish(ProjectionStatus::BOUNDS_ERROR,e.what());}
  if (!std::isfinite(margin))
    return finish(ProjectionStatus::BOUNDS_ERROR,"Native joint margin is not finite");
  if (margin<0.)
    return finish(ProjectionStatus::INITIAL_JOINT_LIMIT,"Initial q outside original native joint limits");

  ClosureSample current;
  try {++out.evaluations; current=evaluate_constraint(initial_q);}
  catch(const std::exception& e) {return finish(ProjectionStatus::EVALUATION_ERROR,e.what());}
  if (!current.residual.allFinite() || !current.jacobian.allFinite())
    return finish(ProjectionStatus::NONFINITE_EVALUATION,"Initial C or Jc is not finite");
  out.initial_residual=current.residual;
  out.final_residual=current.residual;

  for(;;)
  {
    // 分别判m和rad；不用混合单位的6-vector norm作成功判据。
    if (current.residual.head<3>().norm()<=options.position_tolerance_m &&
        current.residual.tail<3>().norm()<=options.rotation_tolerance_rad)
      return finish(ProjectionStatus::CONVERGED,"Separate position and rotation criteria satisfied");
    // 初始max0和接受第40步后都先做上述最终收敛判断，没有off-by-one。
    if (out.accepted_updates>=options.max_iterations)
      return finish(ProjectionStatus::ITERATION_LIMIT,"Accepted Newton update budget exhausted");

    ProjectionIteration step;
    step.update_index=out.accepted_updates+1;
    step.q_before=out.projected_q;
    step.residual_before=current.residual;
    step.joint_margin_before_rad=margin;
    const auto reject=[&](ProjectionStatus status,const std::string& reason) {
      step.note=reason;
      out.history.push_back(step);
      return finish(status,reason);
    };

    // [ENGINEERING] SVD产生Moore–Penrose最小范数修正，无阻尼、行权重或步缩放。
    const Eigen::JacobiSVD<ConstraintJacobian> svd(current.jacobian,
      Eigen::ComputeFullU|Eigen::ComputeFullV);
    const Eigen::Matrix<double,6,1> sigma=svd.singularValues();
    if (!sigma.allFinite())
      return reject(ProjectionStatus::NONFINITE_EVALUATION,"SVD singular spectrum is not finite");
    step.singular_values=sigma;
    const double cutoff=std::max(options.svd_absolute_cutoff,
                                options.svd_relative_cutoff*sigma.maxCoeff());
    step.singular_cutoff=cutoff;
    Eigen::Matrix<double,6,1> inverse=Eigen::Matrix<double,6,1>::Zero();
    step.numerical_rank=0;
    for(int i=0;i<6;++i)
      if (sigma(i)>cutoff)
      {
        inverse(i)=1./sigma(i);
        ++step.numerical_rank;
      }
    // 保守局部验收策略：不是声称P4规定rank<6一律不可投影。
    if (step.numerical_rank<6)
      return reject(ProjectionStatus::RANK_DEFICIENT,
                    "Correction rejected by declared full-row-rank qualification policy");
    const JointVector delta=-(svd.matrixV().leftCols<6>()*inverse.asDiagonal()*
                             svd.matrixU().transpose()*current.residual).eval();
    const JointVector candidate=out.projected_q+delta;
    step.proposed_delta_q=delta;
    step.proposed_q=candidate;
    if (!delta.allFinite() || !candidate.allFinite())
      return reject(ProjectionStatus::NONFINITE_UPDATE,"Newton proposal is not finite");
    if (delta.norm()<=options.stagnation_step_rad ||
        (candidate.array()==out.projected_q.array()).all())
      return reject(ProjectionStatus::STAGNATION,"No qualified representable progress before convergence");
    double candidate_margin;
    try {candidate_margin=native_joint_margin(candidate);}
    catch(const std::exception& e){return reject(ProjectionStatus::BOUNDS_ERROR,e.what());}
    if (!std::isfinite(candidate_margin))
      return reject(ProjectionStatus::BOUNDS_ERROR,"Candidate native joint margin is not finite");
    step.candidate_joint_margin_rad=candidate_margin;
    if (candidate_margin<0.)
      return reject(ProjectionStatus::UPDATE_JOINT_LIMIT,
                    "Full Newton update outside original native limits; rejected without clamp");

    // 候选的C/Jc可评估且有限后才正式accept；π分支/回调错误不覆盖最后有效q。
    ClosureSample next;
    try {++out.evaluations; next=evaluate_constraint(candidate);}
    catch(const std::exception& e){return reject(ProjectionStatus::EVALUATION_ERROR,e.what());}
    if (!next.residual.allFinite() || !next.jacobian.allFinite())
      return reject(ProjectionStatus::NONFINITE_EVALUATION,"Candidate C or Jc is not finite");
    step.residual_after=next.residual;
    step.update_accepted=true;
    step.note="ACCEPTED_FULL_NEWTON_STEP";
    out.history.push_back(step);
    out.projected_q=candidate;
    out.final_residual=next.residual;
    ++out.accepted_updates;
    current=next;
    margin=candidate_margin;
  }
}
}  // namespace p4
