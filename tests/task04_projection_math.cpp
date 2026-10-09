// [ENGINEERING] 纯合成投影单元；不是FR3物理、碰撞或执行证据。
// 数值是已预声明TASK04工程测试；负向toy配置只用于失败分支覆盖。
#include "baselines/p4_closed_chain/projection.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace
{
int checks=0;
void check(bool condition,const char* name)
{
  if (!condition) throw std::runtime_error(name);
  ++checks;
}
p4::ProjectionOptions protocol()
{
  return {1e-8,1e-8,40,1e-12,1e-10,1e-14};
}
p4::ClosureSample sample(const p4::Residual& c,const p4::ConstraintJacobian& j)
{
  p4::ClosureSample s;
  s.left_object=Eigen::Isometry3d::Identity();
  s.right_object=Eigen::Isometry3d::Identity();
  s.residual=c;
  s.jacobian=j;
  return s;
}
p4::ConstraintJacobian identityRows()
{
  p4::ConstraintJacobian a=p4::ConstraintJacobian::Zero();
  a.leftCols<6>().setIdentity();
  return a;
}
p4::JointMarginEvaluator unrestricted()
{
  return [](const p4::JointVector& q) {return 10.-q.cwiseAbs().maxCoeff();};
}
p4::ConstraintEvaluator linear(const p4::ConstraintJacobian& a)
{
  return [a](const p4::JointVector& q) {return sample(a*q,a);};
}
void unchanged(const p4::ProjectionResult& r,const p4::JointVector& q,const char* name)
{
  check((r.projected_q-q).cwiseAbs().maxCoeff()==0.,name);
  check(r.accepted_updates==0,"rejected update not accepted");
}
void finiteReport(const p4::ProjectionResult& r)
{
  check(std::isfinite(r.compute_wall_time_sec)&&r.compute_wall_time_sec>=0.,
    "engineering compute walltime finite/nonnegative");
  check(r.joint_delta_norm_rad.has_value()&&std::isfinite(*r.joint_delta_norm_rad),
    "finite joint-change norm recorded");
  check(r.joint_delta_max_abs_rad.has_value()&&std::isfinite(*r.joint_delta_max_abs_rad),
    "finite joint-change maximum recorded");
}
}

int main()
{
  try
  {
    const auto opt=protocol();
    const auto bounds=unrestricted();
    const auto eye=identityRows();
    const p4::JointVector zero=p4::JointVector::Zero();

    // 非方阵满行秩，显式最小范数结果；不依赖kernel的SVD作oracle。
    auto a=eye;
    for(int i=0;i<6;++i) a(i,7+i)=.25*(i+1);
    p4::JointVector q;
    for(int i=0;i<14;++i) q(i)=.03*(i-6);
    p4::JointVector expected=q;
    for(int i=0;i<6;++i)
    {
      const double w=a(i,7+i);
      const double c=q(i)+w*q(7+i);
      expected(i)-=c/(1.+w*w);
      expected(7+i)-=w*c/(1.+w*w);
    }
    auto one=opt; one.max_iterations=1;
    auto r=p4::project(q,linear(a),bounds,one);
    check(r.status==p4::ProjectionStatus::CONVERGED,"linear minnorm converges in final allowed update");
    check(r.accepted_updates==1&&r.history.size()==1,"one full update logged");
    check((r.projected_q-expected).cwiseAbs().maxCoeff()<1e-14,"undamped pseudoinverse sign and minnorm");
    check(r.projected_q(6)==q(6)&&r.projected_q(13)==q(13),"uncoupled nullspace unchanged");
    for(int i=0;i<6;++i)
      check(std::abs((-a(i,7+i)*r.projected_q(i)+r.projected_q(7+i))-
        (-a(i,7+i)*q(i)+q(7+i)))<1e-14,"coupled nullspace component unchanged");
    check(r.initial_residual.has_value()&&r.final_residual.has_value(),"initial/final residual recorded");
    check(r.final_residual->head<3>().norm()<=opt.position_tolerance_m&&
      r.final_residual->tail<3>().norm()<=opt.rotation_tolerance_rad,"independent residuals converge");
    check(r.history[0].numerical_rank==6&&r.history[0].singular_values.has_value()&&
      r.history[0].singular_cutoff.has_value(),"SVD spectrum/cutoff/rank logged");
    check(r.history[0].proposed_q.has_value()&&r.history[0].proposed_delta_q.has_value()&&
      r.history[0].update_accepted,"proposal/acceptance recorded");
    finiteReport(r);

    // 独立米/弧度门限：一项越线不能被另一项的零误差掩盖。
    auto no_updates=opt; no_updates.max_iterations=0;
    for(int row:{0,3})
    {
      auto v=zero; v(row)=1.1e-8;
      r=p4::project(v,linear(eye),bounds,no_updates);
      check(r.status==p4::ProjectionStatus::ITERATION_LIMIT,"each residual independently rejects beyond tolerance");
      unchanged(r,v,"max0 no unresolved update");
    }
    auto near=zero; near(0)=.9e-8; near(3)=.9e-8;
    r=p4::project(near,linear(eye),bounds,no_updates);
    check(r.status==p4::ProjectionStatus::CONVERGED&&r.accepted_updates==0,
      "both independently under tolerance accepted at max0");

    const auto deficient=[](const p4::JointVector& v) {
      p4::ConstraintJacobian j=p4::ConstraintJacobian::Zero();
      return sample(v.head<6>(),j);
    };
    r=p4::project(zero,deficient,bounds,opt);
    check(r.status==p4::ProjectionStatus::CONVERGED&&r.accepted_updates==0,
      "already closed rank-deficient sample needs no update");
    auto nonzero=zero; nonzero(0)=.2;
    r=p4::project(nonzero,deficient,bounds,opt);
    check(r.status==p4::ProjectionStatus::RANK_DEFICIENT,"unclosed rank deficiency rejected");
    unchanged(r,nonzero,"rank failure preserves last accepted q");
    check(!r.history.empty()&&r.history[0].numerical_rank==0,"rank0 diagnostic preserved");

    // 两个截断各自触发；不修改真实实验配置。
    for(bool relative:{false,true})
    {
      auto toy_opt=opt;
      toy_opt.svd_absolute_cutoff=relative?0.:1e-12;
      toy_opt.svd_relative_cutoff=relative?1e-10:1e-20;
      auto j=eye; j(5,5)=relative?5e-11:5e-13;
      const auto fn=[j](const p4::JointVector&)->p4::ClosureSample {
        p4::Residual c=p4::Residual::Zero(); c(0)=.1;
        return sample(c,j);
      };
      r=p4::project(zero,fn,bounds,toy_opt);
      check(r.status==p4::ProjectionStatus::RANK_DEFICIENT,"absolute/relative singular cutoff applied");
      check(r.history.size()==1&&r.history[0].numerical_rank==5,"truncated rank5 recorded");
      const double cutoff=relative?1e-10:1e-12;
      check(r.history[0].singular_cutoff.has_value()&&
        std::abs(*r.history[0].singular_cutoff-cutoff)<1e-24,"exact effective cutoff recorded");
      unchanged(r,zero,"truncated solve not applied");
    }
    {
      auto equality_opt=opt; equality_opt.svd_relative_cutoff=1e-20;
      auto j=eye; j(5,5)=equality_opt.svd_absolute_cutoff;
      const auto exact_cutoff=[j](const p4::JointVector&) {
        p4::Residual c=p4::Residual::Zero();c(0)=.1;return sample(c,j);
      };
      r=p4::project(zero,exact_cutoff,bounds,equality_opt);
      check(r.status==p4::ProjectionStatus::RANK_DEFICIENT&&r.history[0].numerical_rank==5,
        "singular value equal to cutoff is truncated");
    }

    int eval_count=0;
    const auto counted=[&](const p4::JointVector& v) {++eval_count;return sample(eye*v,eye);};
    const p4::JointMarginEvaluator unit_bounds=[](const p4::JointVector& v) {
      return 1.-v.cwiseAbs().maxCoeff();
    };
    auto outside=zero; outside(0)=1.01;
    r=p4::project(outside,counted,unit_bounds,opt);
    check(r.status==p4::ProjectionStatus::INITIAL_JOINT_LIMIT&&eval_count==0,
      "out-of-bounds initial q rejected before C/J");
    unchanged(r,outside,"invalid initial not silently clamped");
    const auto target_outside=[eye](const p4::JointVector& v) {
      p4::Residual c=eye*v; c(0)+=2.; return sample(c,eye);
    };
    auto initial=zero; initial(0)=.5;
    r=p4::project(initial,target_outside,unit_bounds,opt);
    check(r.status==p4::ProjectionStatus::UPDATE_JOINT_LIMIT,"out-of-bounds full proposal rejected");
    unchanged(r,initial,"rejected proposal not clamped/not returned");
    check(r.history.size()==1&&r.history[0].proposed_q.has_value()&&
      r.history[0].candidate_joint_margin_rad.has_value()&&
      *r.history[0].candidate_joint_margin_rad<0.&&!r.history[0].update_accepted,
      "rejected bound proposal/margin logged");

    const auto nonlinear=[eye](const p4::JointVector& v) {
      p4::Residual c=eye*v; auto j=eye;
      c(0)=std::exp(v(0))-1.;j(0,0)=std::exp(v(0));return sample(c,j);
    };
    initial=zero;initial(0)=1.;
    r=p4::project(initial,nonlinear,bounds,one);
    check(r.status==p4::ProjectionStatus::ITERATION_LIMIT&&r.accepted_updates==1,
      "nonconverged max1 not claimed success");
    check(std::abs(r.projected_q(0)-(1.-(std::exp(1.)-1.)/std::exp(1.)))<1e-14,
      "iteration failure returns last accepted q");
    check(r.final_residual.has_value()&&r.final_residual->head<3>().norm()>opt.position_tolerance_m,
      "iteration failure residual retained");
    finiteReport(r);

    const double nan=std::numeric_limits<double>::quiet_NaN();
    const double inf=std::numeric_limits<double>::infinity();
    for(double bad:{nan,inf})
    {
      auto invalid=zero;invalid(2)=bad;eval_count=0;
      r=p4::project(invalid,counted,bounds,opt);
      check(r.status==p4::ProjectionStatus::INVALID_INPUT&&eval_count==0,
        "nonfinite q never evaluated");
      for(bool bad_j:{false,true})
      {
        const auto bad_eval=[eye,bad,bad_j](const p4::JointVector&) {
          p4::Residual c=p4::Residual::Zero();auto j=eye;
          if(bad_j)j(0,0)=bad;else c(0)=bad;
          return sample(c,j);
        };
        r=p4::project(zero,bad_eval,bounds,opt);
        check(r.status==p4::ProjectionStatus::NONFINITE_EVALUATION,
          "nonfinite C or J explicitly rejected");
        unchanged(r,zero,"invalid evaluation not accepted");
      }
    }
    r=p4::project(zero,p4::ConstraintEvaluator{},bounds,opt);
    check(r.status==p4::ProjectionStatus::INVALID_INPUT,"empty C/J callback rejected");
    r=p4::project(zero,linear(eye),p4::JointMarginEvaluator{},opt);
    check(r.status==p4::ProjectionStatus::INVALID_INPUT,"empty bounds callback rejected");
    const auto throwing=[](const p4::JointVector&)->p4::ClosureSample {
      throw std::runtime_error("intentional toy evaluator failure");
    };
    r=p4::project(zero,throwing,bounds,opt);
    check(r.status==p4::ProjectionStatus::EVALUATION_ERROR,"initial evaluator exception is explicit failure");
    const auto chart_failure=[](const p4::JointVector&)->p4::ClosureSample {
      common_geometry::so3LeftJacobianInverse({common_geometry::pi,0.,0.});
      throw std::runtime_error("unreachable pi chart accepted");
    };
    r=p4::project(zero,chart_failure,bounds,opt);
    check(r.status==p4::ProjectionStatus::EVALUATION_ERROR,"pi chart exception not ignored");

    // Candidate需要可评估才能接受；失败后不能泄露被拒proposal为finalq。
    for(bool invalid_number:{false,true})
    {
      const auto candidate_bad=[eye,nan,invalid_number](const p4::JointVector& v) {
        if(v.norm()<.1)
        {
          if(!invalid_number)throw std::runtime_error("intentional candidate failure");
          p4::Residual c=p4::Residual::Zero();c(0)=nan;return sample(c,eye);
        }
        return sample(eye*v,eye);
      };
      initial=zero;initial(0)=.2;
      r=p4::project(initial,candidate_bad,bounds,opt);
      check(r.status==(invalid_number?p4::ProjectionStatus::NONFINITE_EVALUATION:
        p4::ProjectionStatus::EVALUATION_ERROR),"candidate bad evaluation explicit failure");
      unchanged(r,initial,"failed candidate rejected preserves q");
      check(r.history.size()==1&&!r.history[0].update_accepted,
        "failed candidate recorded rejected");
      check(r.final_residual.has_value()&&std::abs((*r.final_residual)(0)-.2)<1e-14,
        "failed candidate retains last valid residual");
    }
    for(bool throws:{false,true})
    {
      const p4::JointMarginEvaluator bad_margin=[throws,nan](const p4::JointVector&) {
        if(throws)throw std::runtime_error("intentional bounds failure");
        return nan;
      };
      r=p4::project(zero,linear(eye),bad_margin,opt);
      check(r.status==p4::ProjectionStatus::BOUNDS_ERROR,"bounds exception/nonfinite rejected");
      unchanged(r,zero,"bounds evaluation no accepted update");
      const p4::JointMarginEvaluator candidate_margin=[throws,nan](const p4::JointVector& v) {
        if(v.norm()>=.1)return 1.;
        if(throws)throw std::runtime_error("intentional candidate bounds failure");
        return nan;
      };
      initial=zero;initial(0)=.2;
      r=p4::project(initial,linear(eye),candidate_margin,opt);
      check(r.status==p4::ProjectionStatus::BOUNDS_ERROR,"candidate bounds exception/nonfinite rejected");
      unchanged(r,initial,"candidate invalid bounds cannot mutate final q");
    }
    const auto fail_after_one=[nonlinear](const p4::JointVector& v) {
      if(v(0)<.2)throw std::runtime_error("intentional later candidate failure");
      return nonlinear(v);
    };
    initial=zero;initial(0)=1.;
    r=p4::project(initial,fail_after_one,bounds,opt);
    check(r.status==p4::ProjectionStatus::EVALUATION_ERROR&&r.accepted_updates==1,
      "later bad candidate does not erase prior accepted update");
    check(std::abs(r.projected_q(0)-(1.-(std::exp(1.)-1.)/std::exp(1.)))<1e-14,
      "later candidate failure preserves last accepted q not initial/proposal");
    check(r.history.size()==2&&r.history[0].update_accepted&&!r.history[1].update_accepted,
      "accepted then rejected history explicit");
    const auto tiny_correction=[eye](const p4::JointVector&) {
      p4::Residual c=p4::Residual::Zero();c(0)=1.;
      return sample(c,1e16*eye);
    };
    r=p4::project(zero,tiny_correction,bounds,opt);
    check(r.status==p4::ProjectionStatus::STAGNATION,"numerically tiny unresolved update rejected");
    unchanged(r,zero,"stagnation not convergence/update");
    auto overflow_opt=opt;overflow_opt.svd_absolute_cutoff=0.;
    const auto overflow_update=[eye](const p4::JointVector&) {
      p4::Residual c=p4::Residual::Zero();c(0)=1e308;return sample(c,1e-300*eye);
    };
    r=p4::project(zero,overflow_update,bounds,overflow_opt);
    check(r.status==p4::ProjectionStatus::NONFINITE_UPDATE,"finite inputs overflowing pseudoinverse correction rejected");
    unchanged(r,zero,"nonfinite proposal cannot mutate accepted q");

    // 无限、负值或零精度不是有效protocol；零iterations已独立测试为合法。
    for(int field=0;field<6;++field)
    {
      auto invalid_opt=opt;
      if(field==0)invalid_opt.position_tolerance_m=0.;
      if(field==1)invalid_opt.rotation_tolerance_rad=-1.;
      if(field==2)invalid_opt.svd_absolute_cutoff=-1.;
      if(field==3)invalid_opt.svd_relative_cutoff=nan;
      if(field==4)invalid_opt.stagnation_step_rad=-1.;
      if(field==5)invalid_opt.position_tolerance_m=inf;
      eval_count=0;
      r=p4::project(zero,counted,bounds,invalid_opt);
      check(r.status==p4::ProjectionStatus::INVALID_OPTIONS&&eval_count==0,
        "invalid options rejected before callbacks");
    }
    std::cout<<"TASK04 SYNTHETIC PROJECTION PASS checks="<<checks
      <<" full-step undamped SVD; no physics/control backend\n";
    return 0;
  }
  catch(const std::exception& e)
  {
    std::cerr<<"TASK04 SYNTHETIC PROJECTION FAIL after checks="<<checks<<": "<<e.what()<<'\n';
    return 1;
  }
}
